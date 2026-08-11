#!/usr/bin/env python3
"""Build a client Sheet dashboard and Notion-ready brief from Clearbox ops.

The default run writes local JSON and Markdown only. Add --publish-sheet to
create or rebuild a Google Sheet, and --publish-notion with an existing page id
or parent id to publish the generated brief. No Reddit action is performed.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from lib.client_pack import (  # noqa: E402
    build_pack,
    load_payload,
    merge_rows,
    normalize_analysis,
    normalize_clearbox,
    render_notion_markdown,
)


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"


def pull_account(base_url: str, status: str) -> dict:
    """Read the account-scoped inbox. Never writes opportunity state."""
    base = base_url.strip().rstrip("/")
    if base.endswith("/inbox"):
        base = base[:-6]
    url = f"{base}/inbox?{urllib.parse.urlencode({'status': status})}"
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:300]
        raise SystemExit(f"Clearbox inbox returned HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Clearbox inbox request failed: {exc.reason}") from exc


def _frame(rows: list[dict], columns: list[str]):
    import pandas as pd

    return pd.DataFrame(rows, columns=columns).fillna("")


def sheet_config(pack: dict, key: Optional[str], share: bool) -> dict:
    """Return the eleven-view Google Sheet config without making an API call."""
    GREEN, BLUE, AMBER, GREY, ORANGE = "57BB8A", "C9DAF8", "FFF2CC", "EFEFEF", "FCE5CD"
    tabs = pack["tabs"]
    dispositions = {"lead": GREEN, "engage": BLUE, "competitor": ORANGE}
    tiers = {"A": GREEN, "B": BLUE, "C": AMBER, "D": GREY, "UNSCORED": GREY}
    reviews = {
        "not_started": GREY,
        "reviewing": AMBER,
        "approved": GREEN,
        "held": ORANGE,
        "complete": BLUE,
    }

    data_tabs = []
    for title in [
        "Plan Setup", "Operator Console", "Signals", "Buyer Language", "Content Topics",
        "Competitor Sentiment", "GEO Terms", "Disclosure Audit", "Research Workflow",
    ]:
        rows = tabs[title]
        columns = list(rows[0]) if rows else {
            "Competitor Sentiment": ["op_id", "competitor_name", "competitor_sentiment", "analysis_reason", "source_url"],
            "Disclosure Audit": ["op_id", "author", "disclosure_status", "profile_review_verdict", "enrichment_eligibility", "disclosure_evidence", "profile_evidence_urls", "source_url"],
        }.get(title, ["status"])
        spec = {
            "title": title,
            "df": _frame(rows, columns),
            "cols": columns,
            "widths": {column: (420 if column in {"summary", "snippet", "analysis_reason", "helpful_reply_angle", "operator_action", "outreach_safety", "guidance"} else 240 if "url" in column else 160) for column in columns},
            "numeric": [column for column in columns if column.endswith("_score") or column in {"rank", "priority_score", "total_score"}],
            "cf": [],
            "validations": [],
        }
        if "source_disposition" in columns:
            spec["cf"].append({"col": "source_disposition", "type": "map", "map": dispositions})
        if "tier" in columns:
            spec["cf"].append({"col": "tier", "type": "map", "map": tiers})
        if "review_status" in columns:
            spec["cf"].append({"col": "review_status", "type": "map", "map": reviews})
            spec["validations"].append({
                "col": "review_status", "start_row": 1, "end_row": len(rows) + 1,
                "values": list(reviews),
            })
        if title == "Plan Setup":
            spec["validations"] += [
                {"col": "selection", "start_row": 1, "end_row": 2, "values": [
                    "Keep current offer", "Add a separate client offer", "Upgrade capacity and add a client",
                ]},
                {"col": "selection", "start_row": 2, "end_row": 3, "values": [
                    "Agency pays", "Client pays", "Decision together",
                ]},
                {"col": "selection", "start_row": 3, "end_row": 4, "values": [
                    "Reviewing", "Ready to configure", "Need guidance",
                ]},
            ]
        data_tabs.append(spec)

    metrics = pack["metrics"]
    disposition = metrics["dispositions"]
    tier = metrics["tiers"]
    dashboard_entries = [
        {"kind": "section", "label": "CURRENT VALUE"},
        {"kind": "kpi", "label": "Current opportunities", "value": str(metrics["total"])},
        {"kind": "kpi", "label": "Lead", "value": str(disposition.get("lead", 0))},
        {"kind": "kpi", "label": "Engage", "value": str(disposition.get("engage", 0))},
        {"kind": "kpi", "label": "Competitor", "value": str(disposition.get("competitor", 0))},
        {"kind": "kpi", "label": "Tier A", "value": str(tier.get("A", 0))},
        {"kind": "blank", "label": ""},
        {"kind": "section", "label": "HOW TO USE IT"},
        {"kind": "bullet", "label": "Start with Plan Setup, then work Tier A rows in Operator Console and update Review Status."},
        {"kind": "bullet", "label": "Signals preserves every Clearbox disposition and exact Reddit permalink. Optional analysis never replaces that source record."},
        {"kind": "bullet", "label": "GEO Terms separates search discovery, observed AI answers, exact citations, and business outcomes."},
    ]
    return {
        "title": f"{pack['brand']} x Clearbox: Client Value Pack",
        "key": key,
        "share": "anyone_reader" if share else None,
        "dashboard": {
            "title": "Dashboard",
            "subtitle": {
                "title": f"{pack['brand'].upper()} X CLEARBOX: CLIENT VALUE PACK",
                "sub": "Generated from Clearbox dispositions and exact Reddit permalinks",
            },
            "entries": dashboard_entries,
        },
        "tabs": data_tabs,
        "raw_tabs": [{
            "title": "Action Legend",
            "values": [["field", "meaning"]] + [[row["field"], row["meaning"]] for row in tabs["Action Legend"]],
            "widths": {0: 190, 1: 720},
        }],
    }


def publish_sheet(pack: dict, key: Optional[str], share: bool) -> str:
    """Render the eleven canonical views with dropdowns and stable titles."""
    from lib.sheet_engine import build

    url, titles = build(sheet_config(pack, key, share))
    expected = ["Dashboard", "Plan Setup", "Operator Console", "Signals", "Buyer Language", "Content Topics", "Competitor Sentiment", "GEO Terms", "Disclosure Audit", "Research Workflow", "Action Legend"]
    if titles != expected:
        raise RuntimeError(f"unexpected Sheet tab order: {titles}")
    return url


def publish_notion(markdown_path: Path, title: str, page_id: Optional[str], parent_id: Optional[str]) -> None:
    command = [sys.executable, str(ROOT / "scripts" / "push_notion.py"), "--file", str(markdown_path), "--title", title]
    if page_id:
        command += ["--inplace", page_id]
    elif parent_id:
        command += ["--parent", parent_id]
    else:
        raise SystemExit("--publish-notion requires --notion-page-id or --notion-parent-id")
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--ops", help="Clearbox inbox JSON export")
    source.add_argument("--account-url", help="Account-scoped Clearbox base URL; prefer CLEARBOX_ACCOUNT_URL")
    parser.add_argument("--status", choices=["todo", "done", "all"], default="all")
    parser.add_argument("--analysis", help="Freckle/Base Loop JSON or Clay JSON/CSV export")
    parser.add_argument("--backend", choices=["freckle", "baseloop", "clay"], help="Analysis backend")
    parser.add_argument("--brand", required=True)
    parser.add_argument("--existing-offer")
    parser.add_argument("--plan-path", default="Keep current offer")
    parser.add_argument("--payer", default="Decision together")
    parser.add_argument("--readiness", default="Reviewing")
    parser.add_argument("--out", default="data/client_pack")
    parser.add_argument("--allow-truncated", action="store_true", help="Build a clearly partial pack when the API says truncated")
    parser.add_argument("--publish-sheet", action="store_true")
    parser.add_argument("--sheet-id", help="Existing Google Sheet id to rebuild in place")
    parser.add_argument("--sheet-url", help="Existing Sheet URL to place in the brief without rebuilding it")
    parser.add_argument("--share-sheet", action="store_true", help="Share a newly created Sheet as anyone-with-link reader")
    parser.add_argument("--publish-notion", action="store_true")
    parser.add_argument("--notion-page-id", help="Existing Notion page id to rebuild in place")
    parser.add_argument("--notion-parent-id", help="Parent for a new Notion page")
    parser.add_argument("--notion-title")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    account_url = args.account_url or os.environ.get("CLEARBOX_ACCOUNT_URL", "")
    if args.ops:
        source_payload = load_payload(args.ops)
        source_name = "export"
    elif account_url:
        source_payload = pull_account(account_url, args.status)
        source_name = "clearbox_api"
    else:
        raise SystemExit("pass --ops or set CLEARBOX_ACCOUNT_URL")

    clearbox_rows, api_meta = normalize_clearbox(source_payload)
    expected = (api_meta.get("counts") or {}).get("total") if args.status == "all" else None
    if expected and expected > api_meta["returned"]:
        api_meta["truncated"] = True
    if api_meta["truncated"] and not args.allow_truncated:
        raise SystemExit(
            f"Clearbox returned {api_meta['returned']} rows but reported a larger or truncated inbox. "
            "Refusing to publish an incomplete client pack; rerun with a complete export or --allow-truncated."
        )

    if args.analysis and not args.backend:
        raise SystemExit("--analysis requires --backend freckle|baseloop|clay")
    analysis = normalize_analysis(load_payload(args.analysis), args.backend) if args.analysis else {}
    merged, merge_meta = merge_rows(clearbox_rows, analysis)
    pack = build_pack(
        args.brand,
        merged,
        api_meta=api_meta,
        merge_meta=merge_meta,
        existing_offer=args.existing_offer,
        plan_path=args.plan_path,
        payer=args.payer,
        readiness=args.readiness,
    )

    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    pack_path = out / "client_pack.json"
    brief_path = out / "client_brief.md"

    sheet_url = args.sheet_url or ""
    if args.publish_sheet:
        sheet_url = publish_sheet(pack, args.sheet_id, args.share_sheet)
    pack["delivery"] = {"sheet_url": sheet_url, "source": source_name}
    pack_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n")
    brief_path.write_text(render_notion_markdown(pack, sheet_url))

    print(f"PACK: {pack_path}")
    print(f"BRIEF: {brief_path}")
    print(f"ROWS: {len(merged)}")
    print(f"DISPOSITIONS: {pack['metrics']['dispositions']}")
    print(f"BACKENDS: {pack['metrics']['analysis_backends']}")
    if sheet_url:
        print(f"SHEET: {sheet_url}")

    if args.publish_notion:
        publish_notion(
            brief_path,
            args.notion_title or f"{args.brand} x Clearbox: GTM Value Brief",
            args.notion_page_id,
            args.notion_parent_id,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
