#!/usr/bin/env python3
"""last24.py — the morning briefing: buyer signals from the last 24 hours.

Filters the signal database for threads created in the last day, ordered by engagement and intent.
The fastest way to see what is live right now. With --refresh, shells out to pull.py first so the
database is current; without it, reads what is already there.

  python3 last24.py --db data/signals.db --out data/last24.json
  python3 last24.py --db data/signals.db --out data/last24.json --refresh --limit 20
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "data" / "signals.db"
INTENT_RANK = {"high": 0, "mid": 1, "low": 2}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--out", default="data/last24.json")
    ap.add_argument("--refresh", action="store_true",
                    help="re-pull with a 1-day window before filtering")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    if args.refresh:
        print("refreshing: pulling latest threads...")
        try:
            subprocess.run(
                ["python3", str(HERE / "pull.py"), "--max", "8"],
                check=False, timeout=120)
        except Exception as e:
            print(f"  pull skipped: {e}")

    cutoff = int(time.time()) - 86400
    con = sqlite3.connect(args.db, timeout=10)
    con.row_factory = sqlite3.Row

    rows = con.execute("""
        SELECT t.external_id, t.title, t.selftext, t.subreddit, t.permalink,
               t.score, t.num_comments, t.created_utc
        FROM reddit_threads t
        WHERE t.created_utc >= ?
        ORDER BY (t.score + t.num_comments) DESC, t.created_utc DESC
        LIMIT ?
    """, (cutoff, args.limit)).fetchall()

    bl_rows = con.execute("""
        SELECT bl.thread_id, bl.kind, bl.quote, bl.brands
        FROM buyer_language bl
        JOIN reddit_threads t ON t.external_id = bl.thread_id
        WHERE t.created_utc >= ?
    """, (cutoff,)).fetchall()
    con.close()

    bl_by_thread: dict[str, list[dict]] = {}
    for r in bl_rows:
        bl_by_thread.setdefault(r["thread_id"], []).append({
            "kind": r["kind"], "quote": r["quote"], "brands": r["brands"],
        })

    items = []
    for r in rows:
        eid = r["external_id"]
        bl = bl_by_thread.get(eid, [])
        best_intent = "low"
        for b in bl:
            k = (b.get("kind") or "").lower()
            if k in ("comparison", "recommendation"):
                best_intent = "high"
                break
            if k in ("pain", "question"):
                best_intent = "mid"
        items.append({
            "external_id": eid,
            "title": r["title"],
            "subreddit": "r/" + (r["subreddit"] or ""),
            "permalink": r["permalink"],
            "engagement": (r["score"] or 0) + (r["num_comments"] or 0),
            "created_utc": r["created_utc"],
            "intent": best_intent,
            "buyer_language": bl[:3],
        })

    items.sort(key=lambda x: (INTENT_RANK.get(x["intent"], 2), -x["engagement"]))

    result = {
        "window": "last 24 hours",
        "cutoff_utc": cutoff,
        "count": len(items),
        "items": items,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"last24: {len(items)} threads in the last 24h -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
