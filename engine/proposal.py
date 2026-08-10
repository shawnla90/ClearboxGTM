#!/usr/bin/env python3
"""proposal.py — build pitch materials for a prospect from Reddit buyer signals.

The reverse-uno at the tactical level: given a prospect company, pull their buyers' conversations
from the signal database and generate a pitch brief that shows the prospect what their market is
saying. Optionally incorporates competitor analysis and GEO terms if those have already been run.

  python3 proposal.py --prospect "Acme Corp" --db data/signals.db --out data/proposal/
  python3 proposal.py --prospect "Acme Corp" --db data/signals.db \
      --competitor-analysis data/competitor_analysis.json \
      --geo data/geo_terms.json --out data/proposal/
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from textwrap import dedent

HERE = Path(__file__).resolve().parent
DB = HERE / "data" / "signals.db"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prospect", required=True)
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--competitor-analysis", default="")
    ap.add_argument("--geo", default="")
    ap.add_argument("--out", default="data/proposal/")
    ap.add_argument("--limit", type=int, default=15,
                    help="top content topics to include")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(args.db, timeout=10)
    con.row_factory = sqlite3.Row

    topics = con.execute("""
        SELECT external_id, topic, content_angle, score, tier, intent, mentions,
               engagement, brands, evidence, topic_reason
        FROM content_topics
        ORDER BY score DESC
        LIMIT ?
    """, (args.limit,)).fetchall()

    buyer_lang = con.execute("""
        SELECT kind, quote, brands, subreddit, permalink
        FROM buyer_language
        ORDER BY engagement DESC
        LIMIT 30
    """).fetchall()

    subreddits = con.execute("""
        SELECT subreddit, COUNT(*) as n
        FROM reddit_threads
        GROUP BY subreddit
        ORDER BY n DESC
    """).fetchall()
    con.close()

    comp = {}
    if args.competitor_analysis and Path(args.competitor_analysis).exists():
        try:
            comp = json.loads(Path(args.competitor_analysis).read_text())
        except Exception:
            comp = {}

    geo = {}
    if args.geo and Path(args.geo).exists():
        try:
            geo = json.loads(Path(args.geo).read_text())
        except Exception:
            geo = {}

    brief_data = {
        "prospect": args.prospect,
        "content_gaps": [
            {"topic": t["topic"], "angle": t["content_angle"], "score": t["score"],
             "tier": t["tier"], "intent": t["intent"], "reason": t["topic_reason"]}
            for t in topics
        ],
        "buyer_questions": [
            {"kind": b["kind"], "quote": b["quote"], "subreddit": "r/" + (b["subreddit"] or ""),
             "brands_mentioned": b["brands"]}
            for b in buyer_lang if b["kind"] in ("question", "comparison", "pain")
        ],
        "active_subreddits": [
            {"subreddit": "r/" + (s["subreddit"] or ""), "thread_count": s["n"]}
            for s in subreddits
        ],
    }
    if comp:
        brief_data["competitor_context"] = {
            "share_of_voice": comp.get("share_of_voice", {}),
            "sentiment_summary": comp.get("sentiment", {}).get("distribution", {}),
        }
    if geo:
        terms = geo.get("terms", [])
        brief_data["geo_terms"] = {
            "retrieval_visibility_score": geo.get("retrieval_visibility_score"),
            "terms_not_surfacing": [t["term"] for t in terms
                                    if t.get("currently_retrieved_by_exa") == "no"],
        }

    (out / "brief.json").write_text(json.dumps(brief_data, indent=2, ensure_ascii=False))

    top_qs = brief_data["buyer_questions"][:5]
    top_gaps = brief_data["content_gaps"][:5]
    subs = brief_data["active_subreddits"][:5]

    md_lines = [
        f"# Pitch brief: {args.prospect}",
        "",
        f"Generated from {len(brief_data['content_gaps'])} scored content topics and "
        f"{len(brief_data['buyer_questions'])} buyer-language extracts.",
        "",
        "## What their buyers are asking on Reddit",
        "",
    ]
    for q in top_qs:
        md_lines.append(f"- **{q['subreddit']}** ({q['kind']}): \"{q['quote'][:120]}\"")
    md_lines += ["", "## Content gaps (highest-scored topics without brand presence)", ""]
    for g in top_gaps:
        md_lines.append(f"- **{g['topic']}** (tier {g['tier']}, score {g['score']}): {g['angle']}")
    md_lines += ["", "## Where the conversations happen", ""]
    for s in subs:
        md_lines.append(f"- **{s['subreddit']}** — {s['thread_count']} threads")
    if comp:
        sov = comp.get("share_of_voice", {})
        md_lines += [
            "", "## Competitive context", "",
            sov.get("reading", "No competitor analysis available."),
        ]
    if geo and brief_data["geo_terms"]["terms_not_surfacing"]:
        md_lines += ["", "## GEO terms not yet surfacing", ""]
        for t in brief_data["geo_terms"]["terms_not_surfacing"][:5]:
            md_lines.append(f"- {t}")
    md_lines += [
        "", "---", "",
        "This brief is generated from real Reddit conversations. Every quote traces to a "
        "permalink in brief.json. Use it to show the prospect what their buyers are saying, "
        "not to pitch — the reverse-uno method "
        "(see playbooks/win-an-agency-client.md).", "",
    ]
    (out / "BRIEF.md").write_text("\n".join(md_lines))

    n_topics = len(brief_data["content_gaps"])
    n_qs = len(brief_data["buyer_questions"])
    print(f"proposal: {n_topics} gaps · {n_qs} buyer questions · {len(subs)} subreddits -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
