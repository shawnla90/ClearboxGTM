#!/usr/bin/env python3
"""unmask.py - the lead-unmasking pass over a client's classified Reddit opportunities.

Three-step disclosure gate, then enrichment. Reddit is pseudonymous, so you enrich the COMPANY, never
the person, and only when the author tied themselves to a company. Pseudonymous threads stay Reddit
conversations. This is the honest version of "unmasking": it reads what the author volunteered in
public, it does not de-anonymize anyone.

The gate checks three things, in order:
  1. Profile lookup (--profile)  check the author's own Reddit profile and web presence first,
                                 because that is where disclosure is most likely
  2. In-thread domain scan       regex for company domains in post/comment text
  3. Brand-handle heuristic      username patterns that look like a company handle

  # gate only (default, no external calls): who disclosed a company, and the domain
  python3 unmask.py --ops data/ops_classified.json --out data/unmasked.json

  # gate with profile lookup (adds web search for the author's public identity)
  python3 unmask.py --ops data/ops_classified.json --profile --out data/unmasked.json

  # gate + live enrich each disclosed domain through your enrichment backend
  python3 unmask.py --ops data/ops_classified.json --profile --enrich --out data/unmasked.json

Enrichment backend is pluggable. The default shells the Freckle CLI (saved workflow
"enrich-domain-score-icp-contacts-omnibound", org clearbox): invoke -> poll -> inspect, returning the
company, the ICP tier, and the buying-role contacts. Swap enrich_domain() for Clay, Base Loop, Apollo,
Deepline, or any waterfall a client already runs. Never enriches without --enrich.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

# The saved Freckle workflow: domain -> company + ICP tier + buying-role contacts.
# Set both to YOUR workflow id and org slug (freckle workflow saved list): no defaults ship here.
FRECKLE_WORKFLOW = os.environ.get("FRECKLE_WORKFLOW_ID", "")
FRECKLE_ORG = os.environ.get("FRECKLE_ORG_ID", "")

DOMAIN_RE = re.compile(r"\b([a-z0-9][a-z0-9-]{1,}\.(?:com|io|ai|co|team|app|dev|net|org))\b", re.I)
BRAND_HANDLE_RE = re.compile(
    r"(technolog|labs?|systems|software|agency|studio|solutions|-ai|-io|-hq|-inc)$", re.I)
# domains that appear in threads but are never the author's own company
IGNORE_DOMAINS = {"reddit.com", "redd.it", "google.com", "youtube.com", "github.com",
                  "linkedin.com", "twitter.com", "x.com", "notion.so", "medium.com",
                  "substack.com", "loom.com", "imgur.com"}


def disclose(op: dict, use_profile: bool = False) -> dict:
    """The three-step disclosure gate.

    Step 1 (--profile): check the author's own profile and web presence — this is where
    disclosure is most likely. Requires an Exa key for the web search tier.
    Step 2: scan the thread text for company domains.
    Step 3: check if the username looks like a brand handle.
    """
    author = op.get("author") or ""

    # Step 1: profile lookup (opt-in)
    if use_profile and author:
        try:
            from lib.profile_lookup import lookup_profile
            result = lookup_profile(author)
            if result.get("disclosed") and result.get("domains"):
                return {"disclosed": True,
                        "signal": f"profile lookup ({result['source']}): {result['signal']}",
                        "domain": result["domains"][0],
                        "action": "reply first, then enrich the company"}
        except ImportError:
            pass

    # Step 2: in-thread domain scan
    text = f"{op.get('summary', '')} {op.get('snippet', '')}"
    for m in DOMAIN_RE.finditer(text):
        dom = m.group(1).lower()
        root = ".".join(dom.split(".")[-2:])
        if root in IGNORE_DOMAINS:
            continue
        return {"disclosed": True, "signal": "company domain in thread", "domain": dom,
                "action": "reply first, then enrich the company"}

    # Step 3: brand-handle heuristic
    if BRAND_HANDLE_RE.search(author):
        return {"disclosed": True, "signal": "author handle looks like a brand", "domain": None,
                "action": "check the handle, it may name a company"}

    return {"disclosed": False, "signal": "no company disclosed", "domain": None,
            "action": "stays a Reddit conversation, reply on the thread"}


def is_lead(op: dict) -> bool:
    """A lead-classified op, in either the raw Clearbox shape (kind) or the classified shape (lane)."""
    return (op.get("kind") or "").lower() == "lead" or op.get("lane") == "lead_enrich"


def enrich_domain(domain: str, timeout_s: int = 240) -> dict:
    """Invoke the enrichment backend for one domain and return its result (or a plain error dict).

    Pluggable seam: this is the one function to replace with your orchestration tool. The default
    shells the Freckle CLI. Swap it for Clay, Base Loop, Deepline, Apollo, or your own waterfall.
    """
    if not shutil.which("freckle"):
        return {"domain": domain, "error": "freckle CLI not found; plug your enrichment backend into "
                                            "enrich_domain() (Clay, Base Loop, Deepline, Apollo, or your own waterfall)"}
    if not FRECKLE_WORKFLOW or not FRECKLE_ORG:
        return {"domain": domain, "error": "set FRECKLE_WORKFLOW_ID and FRECKLE_ORG_ID to your saved "
                                            "workflow (freckle workflow saved list)"}
    try:
        inv = subprocess.run(
            ["freckle", "workflow", "saved", "invoke", FRECKLE_WORKFLOW,
             "--org", FRECKLE_ORG, "--json", json.dumps({"domain": domain})],
            capture_output=True, text=True, timeout=90)
        out = (inv.stdout or "") + "\n" + (inv.stderr or "")
        m = re.search(r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", out)
        if not m:
            return {"domain": domain, "error": "no runId returned from invoke", "raw": out.strip()[:800]}
        run_id = m.group(1)
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            insp = subprocess.run(
                ["freckle", "workflow", "runs", "inspect", run_id, "--org", FRECKLE_ORG],
                capture_output=True, text=True, timeout=60)
            body = insp.stdout or ""
            if re.search(r"\bstatus:\s*completed\b", body) or '"status": "completed"' in body:
                return {"domain": domain, "run_id": run_id, "status": "completed", "result": body.strip()}
            if re.search(r"\bstatus:\s*(failed|errored)\b", body):
                return {"domain": domain, "run_id": run_id, "status": "failed", "result": body.strip()}
            time.sleep(8)
        return {"domain": domain, "run_id": run_id, "status": "timeout"}
    except subprocess.TimeoutExpired:
        return {"domain": domain, "error": "freckle CLI timed out"}
    except Exception as e:  # noqa: BLE001 - the backend is external, report and continue
        return {"domain": domain, "error": f"{type(e).__name__}: {e}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ops", default="data/ops_classified.json")
    ap.add_argument("--out", default="data/unmasked.json")
    ap.add_argument("--profile", action="store_true",
                    help="run profile lookup (web search for the author's public identity)")
    ap.add_argument("--enrich", action="store_true", help="live-enrich each disclosed domain")
    ap.add_argument("--limit", type=int, default=25, help="max domains to enrich in one run")
    args = ap.parse_args()

    ops = json.loads(Path(args.ops).read_text())
    leads = [o for o in ops if is_lead(o)]

    rows = []
    for o in leads:
        d = disclose(o, use_profile=args.profile)
        rows.append({
            "op_id": o.get("op_id") or o.get("id"),
            "subreddit": "r/" + (o.get("subreddit") or ""),
            "author": o.get("author"),
            "summary": (o.get("summary") or "")[:160],
            "permalink": o.get("permalink") or o.get("url"),
            **d,
        })

    disclosed = [r for r in rows if r["disclosed"] and r["domain"]]
    stays = [r for r in rows if not r["disclosed"]]
    maybe = [r for r in rows if r["disclosed"] and not r["domain"]]

    enrichment = []
    if args.enrich:
        seen = set()
        for r in disclosed:
            dom = r["domain"]
            if dom in seen:
                continue
            seen.add(dom)
            if len(seen) > args.limit:
                print(f"  reached --limit {args.limit}; {len(disclosed) - len(seen) + 1} domains left")
                break
            print(f"  enriching {dom} ...")
            enrichment.append(enrich_domain(dom))

    result = {
        "leads_total": len(leads),
        "disclosed_company": len(disclosed),
        "handle_looks_like_brand": len(maybe),
        "stays_on_reddit": len(stays),
        "profile_lookup": args.profile,
        "gate": ("enrich the company, not the person, and only when the author tied themselves to a "
                 "company — in their profile, in the thread, or via a brand handle"),
        "rows": rows,
        "enrichment": enrichment,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"unmask: {len(leads)} leads -> {len(disclosed)} disclosed a company, "
          f"{len(maybe)} brand-like handles, {len(stays)} stay on Reddit"
          f"{' (profile lookup on)' if args.profile else ''}"
          f"{' · enriched ' + str(len(enrichment)) if args.enrich else ''} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
