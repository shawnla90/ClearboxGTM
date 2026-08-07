# The Notion command center

Every client engagement ships as real, shared, linked documents — not attachments, not "see the playbook" references to files that don't exist. One command center page links everything: the research brief, the offer and 30/60/90 plan, the internal playbook, the client case, the sheet, the deck. The client starts there and never asks "where is X".

## The mechanic

`../scripts/push_notion.py` converts a markdown file into a real Notion page:

```bash
python3 scripts/push_notion.py --file doc.md --title "Acme · Reddit" --parent <page_id>
```

What it handles: headings, fenced code, **colored callouts** (`> 🎯 text` — color inferred from the emoji), `- [ ]` checkboxes, `::: bookmark <url>` cards, external images, **uploaded local images** (`::: image_upload path | caption`), columns, bullets, dividers, inline bold/code/links.

## The rules that keep links stable

- **Reuse page ids.** Re-publish with `--inplace <page_id>`: it deletes the page's blocks and re-appends, so a shared URL never breaks. A rebuilt doc with a new URL is a broken promise.
- **Verify every link resolves** to a real, shared page before the command center ships. Phantom references are the fastest way to lose trust.
- **The integration must be shared into the parent page** (Notion UI → page → Connections) or the API 401s.
- **Share-to-web is a manual UI toggle.** The API cannot publish a page publicly. Flip it yourself, then send.

## Doc conventions

- The command center is plain reading: what each doc is, why to read it, in what order.
- Client-facing docs never reference scripts, filenames, or commands. The doc is the instruction; the data "can be re-queried and rebuilt on demand."
- Callout colors carry meaning consistently: 🎯 the point, ⚡ the mechanism, 🔴 the warning, 💸 the money.
