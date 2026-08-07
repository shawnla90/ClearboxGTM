#!/usr/bin/env python3
"""Create a per-client doc page in Notion from a markdown file.

Takes --file and --title so one script serves every client deliverable: the
onboarding doc, the command center, the operator handbook. Re-publish with
--inplace to keep a shared URL stable across rebuilds.

Reads the integration token from the NOTION_API_TOKEN env var (or ~/.env.notion),
converts the markdown to Notion blocks (headings, code, COLORED callouts, to-do
checkboxes, bookmark cards, external images, uploaded images, bullets, dividers,
inline bold/code/links), and creates the page under a parent the integration can
access. Prints the URL.

Markdown conventions beyond standard:
  > 💸 text                     -> callout, color inferred from the leading emoji
  - [ ] text / - [x]            -> to-do checkbox (unchecked / checked)
  ::: bookmark <url>            -> bookmark card
  ::: image <url> | caption     -> external image (GIF/PNG) with optional caption
  ::: image_upload <path> | cap -> upload a local file, embed it (optional caption)

Usage:
  python3 push_notion.py --file doc.md --title "Acme - Reddit" --parent <page_id>
  python3 push_notion.py --file doc.md --inplace <page_id>   # keep URL
  python3 push_notion.py --file doc.md --replace <old_id> --parent <page_id>
  python3 push_notion.py --file doc.md --update <id>

The integration must be shared into the parent page (Notion UI: page -> ... ->
Connections) or the API returns 401/404. Share-to-web is a manual UI toggle; the
API cannot publish a page publicly.
"""
from __future__ import annotations
import json, mimetypes, re, sys, urllib.request, urllib.error
from pathlib import Path

API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
HERE = Path(__file__).resolve().parent
MD = HERE / "doc.md"          # override with --file
TITLE = "Client Doc"          # override with --title

EMOJI_COLOR = {
    "💸": "green_background", "⚡": "blue_background", "🤖": "purple_background",
    "🔥": "orange_background", "✅": "green_background", "📦": "purple_background",
    "🛠️": "gray_background", "🚀": "orange_background", "⏱️": "blue_background",
    "🎯": "pink_background", "💡": "gray_background", "📈": "green_background",
    "🟧": "orange_background", "🔴": "red_background", "🟢": "green_background",
}
KNOWN_EMOJI = list(EMOJI_COLOR.keys())
CODE_LANGS = {"bash": "bash", "sh": "shell", "shell": "shell", "python": "python",
              "py": "python", "json": "json", "js": "javascript", "sql": "sql", "": "plain text"}


def load_token() -> str:
    import os
    if os.environ.get("NOTION_API_TOKEN"):
        return os.environ["NOTION_API_TOKEN"].strip()
    env_file = Path.home() / ".env.notion"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("NOTION_API_TOKEN"):
                return line.split("=", 1)[1].strip()
    raise SystemExit("set NOTION_API_TOKEN (env var or ~/.env.notion)")


TOKEN = load_token()


def _headers():
    return {"Authorization": f"Bearer {TOKEN}", "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json"}


def _req(method: str, path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Notion API {method} {path} -> {e.code}\n{e.read().decode()}")


def upload_file(path: Path) -> str:
    """Two-step Notion file upload; returns the file_upload id to attach to a block."""
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    created = _req("POST", "/file_uploads", {"filename": path.name, "content_type": mime})
    fid, send_url = created["id"], created["upload_url"]
    boundary = "----notionuploadboundary7e3f2a"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
            f"filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n").encode()
    body += path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(send_url, data=body, method="POST", headers={
        "Authorization": f"Bearer {TOKEN}", "Notion-Version": NOTION_VERSION,
        "Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req) as r:
            r.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"file upload send -> {e.code}\n{e.read().decode()}")
    print("  uploaded", path.name, "->", fid)
    return fid


# ---- inline markdown -> rich_text ----
INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def _rt(content: str, bold=False, code=False, link=None) -> dict:
    rt = {"type": "text", "text": {"content": content}}
    if link:
        rt["text"]["link"] = {"url": link}
    ann = {}
    if bold:
        ann["bold"] = True
    if code:
        ann["code"] = True
    if ann:
        rt["annotations"] = ann
    return rt


def inline(text: str) -> list:
    out, pos = [], 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            out.append(_rt(text[pos:m.start()]))
        tok = m.group(0)
        if tok.startswith("**"):
            out.append(_rt(tok[2:-2], bold=True))
        elif tok.startswith("`"):
            out.append(_rt(tok[1:-1], code=True))
        else:
            lm = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok)
            out.append(_rt(lm.group(1), link=lm.group(2)))
        pos = m.end()
    if pos < len(text):
        out.append(_rt(text[pos:]))
    return out or [_rt("")]


def _hdr(level: int, text: str) -> dict:
    key = f"heading_{level}"
    return {"object": "block", "type": key, key: {"rich_text": inline(text)}}


def _image_block(img_data: dict, caption: str) -> dict:
    if caption.strip():
        img_data["caption"] = inline(caption.strip())
    return {"object": "block", "type": "image", "image": img_data}


def md_to_blocks(md: str) -> list:
    blocks, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip().lower()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            blocks.append({"object": "block", "type": "code", "code": {
                "rich_text": [_rt("\n".join(buf))], "language": CODE_LANGS.get(lang, "plain text")}})
            continue
        s = line.strip()
        if not s:
            i += 1; continue
        if s == "::: columns":
            i += 1
            cols_raw, cur = [], None
            while i < len(lines) and lines[i].strip() != ":::":
                ls = lines[i].strip()
                if ls == "::: column":
                    cur = []; cols_raw.append(cur)
                elif cur is not None:
                    cur.append(lines[i])
                i += 1
            i += 1  # skip closing :::
            cols = [{"type": "column", "column": {"children": md_to_blocks("\n".join(cl))}}
                    for cl in cols_raw if cl]
            blocks.append({"object": "block", "type": "column_list",
                           "column_list": {"children": cols}})
            continue
        todo = re.match(r"^- \[([ xX])\]\s+(.*)$", s)
        if s == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        elif s.startswith("::: bookmark "):
            blocks.append({"object": "block", "type": "bookmark",
                           "bookmark": {"url": s[len("::: bookmark "):].strip()}})
        elif s.startswith("::: image_upload "):
            p, _, cap = s[len("::: image_upload "):].partition("|")
            fid = upload_file(Path(p.strip()).expanduser())
            blocks.append(_image_block({"type": "file_upload", "file_upload": {"id": fid}}, cap))
        elif s.startswith("::: image "):
            u, _, cap = s[len("::: image "):].partition("|")
            blocks.append(_image_block({"type": "external", "external": {"url": u.strip()}}, cap))
        elif s.startswith("### "):
            blocks.append(_hdr(3, s[4:]))
        elif s.startswith("## "):
            blocks.append(_hdr(2, s[3:]))
        elif s.startswith("# "):
            blocks.append(_hdr(1, s[2:]))
        elif s.startswith("> "):
            content, emoji, color = s[2:], "💡", "gray_background"
            for e in KNOWN_EMOJI:
                if content.startswith(e):
                    emoji, color, content = e, EMOJI_COLOR[e], content[len(e):].lstrip()
                    break
            blocks.append({"object": "block", "type": "callout", "callout": {
                "rich_text": inline(content), "icon": {"emoji": emoji}, "color": color}})
        elif todo:
            blocks.append({"object": "block", "type": "to_do", "to_do": {
                "rich_text": inline(todo.group(2)), "checked": todo.group(1) in ("x", "X")}})
        elif re.match(r"^[-*] ", s):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": inline(s[2:])}})
        elif re.match(r"^\d+\. ", s):
            blocks.append({"object": "block", "type": "numbered_list_item",
                           "numbered_list_item": {"rich_text": inline(re.sub(r"^\d+\. ", "", s))}})
        else:
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": inline(s)}})
        i += 1
    return blocks


def chunk(seq, n):
    for j in range(0, len(seq), n):
        yield seq[j:j + n]


def main():
    global MD, TITLE
    args = sys.argv[1:]
    if "--file" in args:
        MD = Path(args[args.index("--file") + 1]).expanduser().resolve()
    if "--title" in args:
        TITLE = args[args.index("--title") + 1]
    if not MD.exists():
        sys.exit(f"markdown not found: {MD}\npass --file <path>")
    parent = args[args.index("--parent") + 1] if "--parent" in args else None
    update_id = args[args.index("--update") + 1] if "--update" in args else None
    replace_id = args[args.index("--replace") + 1] if "--replace" in args else None
    inplace_id = args[args.index("--inplace") + 1] if "--inplace" in args else None

    blocks = md_to_blocks(MD.read_text())
    print(f"parsed {len(blocks)} blocks from {MD.name}")

    if update_id:
        for batch in chunk(blocks, 100):
            _req("PATCH", f"/blocks/{update_id}/children", {"children": batch})
        print(f"appended {len(blocks)} blocks to {update_id}")
        return

    if inplace_id:
        # delete existing children, re-append new ones — keeps the page id + published URL
        existing, cur = [], None
        while True:
            q = f"/blocks/{inplace_id}/children?page_size=100" + (f"&start_cursor={cur}" if cur else "")
            d = _req("GET", q)
            existing += d["results"]
            if not d.get("has_more"):
                break
            cur = d["next_cursor"]
        for k in existing:
            _req("DELETE", f"/blocks/{k['id']}")
        print(f"deleted {len(existing)} existing top-level blocks")
        for batch in chunk(blocks, 100):
            _req("PATCH", f"/blocks/{inplace_id}/children", {"children": batch})
        print(f"appended {len(blocks)} blocks in place to {inplace_id} (URL preserved)")
        return

    if not parent:
        sys.exit("pass --parent <page_id> (a page your integration is shared into), "
                 "or --inplace/--update to write to an existing page")
    first, rest = blocks[:100], blocks[100:]
    page = _req("POST", "/pages", {
        "parent": {"page_id": parent},
        "icon": {"emoji": "🛠️"},
        "properties": {"title": {"title": [{"text": {"content": TITLE}}]}},
        "children": first,
    })
    pid = page["id"]
    for batch in chunk(rest, 100):
        _req("PATCH", f"/blocks/{pid}/children", {"children": batch})
    if replace_id:
        _req("PATCH", f"/pages/{replace_id}", {"archived": True})
        print("archived old page", replace_id)
    print("PAGE_ID:", pid)
    print("URL:", page.get("url"))


if __name__ == "__main__":
    main()
