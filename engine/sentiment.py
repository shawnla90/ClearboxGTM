#!/usr/bin/env python3
"""sentiment.py — thread-level sentiment classification from classified ops.

Reddit opportunities carry no sentiment field. This generates a per-op sentiment read — positive,
neutral, or negative — with a 1-5 score and a reason. Two layers, same pattern as mine.py:
  1. HEURISTIC (always runs): keyword signals in the op summary.
  2. RICH (--cli, optional): shell out to `claude -p` for nuanced three-class scoring.

The output shape matches what competitor.py reads at its --gen input (gen.get("sentiment", [])),
so the two scripts chain directly.

  python3 sentiment.py --ops data/ops_classified.json --out data/sentiment.json
  python3 sentiment.py --ops data/ops_classified.json --out data/sentiment.json --cli
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

CLI_TIMEOUT = 90

POSITIVE_SIGNALS = re.compile(
    r"\b(love|great|amazing|excellent|perfect|solved|helped|recommend|switched to|happy with|"
    r"game.changer|life.?saver|exactly what|glad I found|been using .* for)\b", re.I)
NEGATIVE_SIGNALS = re.compile(
    r"\b(hate|terrible|worst|awful|broken|useless|waste|regret|frustrat|disappointing|"
    r"deal.?breaker|never again|rip.?off|unsubscrib|cancel|gave up)\b", re.I)
NEUTRAL_SIGNALS = re.compile(
    r"\b(looking for|anyone used|what do you think|compared to|thoughts on|considering|"
    r"alternative|vs\.?|options|which one)\b", re.I)


def heuristic_sentiment(text: str) -> tuple[str, int, str]:
    pos = len(POSITIVE_SIGNALS.findall(text))
    neg = len(NEGATIVE_SIGNALS.findall(text))
    neu = len(NEUTRAL_SIGNALS.findall(text))
    if pos > neg and pos > neu:
        score = min(5, 3 + pos)
        return "positive", score, f"{pos} positive signal(s)"
    if neg > pos and neg > neu:
        score = max(1, 3 - neg)
        return "negative", score, f"{neg} negative signal(s)"
    return "neutral", 3, "no strong signal or mixed"


def enrich_with_cli(ops: list[dict]) -> list[dict]:
    summaries = [{"op_id": o.get("op_id", ""), "summary": (o.get("summary") or "")[:300]}
                 for o in ops[:40]]
    system = ("You are a sentiment analyst. For each Reddit opportunity, classify sentiment as "
              "positive, neutral, or negative with a score 1-5 (1=very negative, 5=very positive) "
              "and a one-sentence reason. Return ONLY a JSON array of "
              '{op_id, sentiment, sentiment_score, reason}.')
    user = "Classify sentiment:\n\n" + json.dumps(summaries, indent=2)
    cmd = ["claude", "-p", "--model", "opus", "--dangerously-skip-permissions",
           "--no-session-persistence", "--append-system-prompt", system, user]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=CLI_TIMEOUT)
        if res.returncode != 0 or not res.stdout.strip():
            return []
        text = res.stdout.strip()
        m = re.search(r"\[.*\]", text, re.DOTALL)
        return json.loads(m.group(0) if m else text)
    except Exception as e:
        print(f"  (claude CLI skipped: {e}); using heuristic sentiment")
        return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ops", default="data/ops_classified.json")
    ap.add_argument("--out", default="data/sentiment.json")
    ap.add_argument("--cli", action="store_true", help="use claude -p for richer classification")
    args = ap.parse_args()

    ops = json.loads(Path(args.ops).read_text())

    if args.cli:
        enriched = enrich_with_cli(ops)
        if enriched:
            by_id = {e["op_id"]: e for e in enriched if e.get("op_id")}
            sentiment = []
            for o in ops:
                oid = o.get("op_id", "")
                if oid in by_id:
                    sentiment.append(by_id[oid])
                else:
                    s, sc, r = heuristic_sentiment(o.get("summary") or o.get("title") or "")
                    sentiment.append({"op_id": oid, "sentiment": s, "sentiment_score": sc, "reason": r})
        else:
            sentiment = [{"op_id": o.get("op_id", ""),
                          **(dict(zip(("sentiment", "sentiment_score", "reason"),
                                      heuristic_sentiment(o.get("summary") or o.get("title") or ""))))}
                         for o in ops]
    else:
        sentiment = [{"op_id": o.get("op_id", ""),
                      **(dict(zip(("sentiment", "sentiment_score", "reason"),
                                  heuristic_sentiment(o.get("summary") or o.get("title") or ""))))}
                     for o in ops]

    result = {
        "generated": True,
        "note": "Reddit opportunities carry no sentiment field; this is an LLM read (--cli) "
                "or keyword heuristic over the op summaries, labeled as generated",
        "sentiment": sentiment,
    }
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    from collections import Counter
    dist = Counter(s["sentiment"] for s in sentiment)
    print(f"sentiment: {len(sentiment)} ops · {dict(dist)} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
