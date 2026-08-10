---
name: sentiment
version: 1.0.0
description: Generate sentiment classifications for Reddit opportunities. Wraps engine/sentiment.py — three-class (positive/neutral/negative) with a 1-5 score, LLM-powered with heuristic fallback. Output feeds competitor-intel and the daily digest. Use when the user says "/sentiment", "run sentiment on these threads", or "what's the mood".
---

# sentiment

What is the mood in the room? Three-class sentiment on every opportunity, generated and labeled.

Reddit opportunities carry no sentiment field — not in the API, not in the Clearbox export. This skill generates a per-op sentiment classification from the op summaries: positive, neutral, or negative, with a 1-5 score and a reason. Two layers, same pattern as `engine/mine.py`:

1. **Heuristic (always runs):** keyword signals in the summary (recommendation words, frustration words, question/comparison words). Fast, no external calls.
2. **Rich (`--cli`, optional):** shells out to `claude -p` for nuanced three-class scoring with a reason. Falls back silently to heuristic if the CLI is unavailable.

Every output carries `generated: true` and a note explaining what it is. This is not observed sentiment — it is a classification read.

## Inputs

A classified ops file (`data/ops_classified.json`) — the same input `competitor.py` and `digest.py` consume.

## How to run

```bash
# heuristic only (fast, no external calls)
python3 engine/sentiment.py --ops data/ops_classified.json --out data/sentiment.json

# with LLM classification (richer reads, needs claude CLI)
python3 engine/sentiment.py --ops data/ops_classified.json --out data/sentiment.json --cli
```

## Output shape

`data/sentiment.json`:

```json
{
  "generated": true,
  "note": "Reddit opportunities carry no sentiment field; this is an LLM read ...",
  "sentiment": [
    {"op_id": "...", "sentiment": "positive", "sentiment_score": 4, "reason": "..."},
    {"op_id": "...", "sentiment": "neutral", "sentiment_score": 3, "reason": "..."}
  ]
}
```

This is the exact shape `engine/competitor.py` reads at its `--gen` input (`gen.get("sentiment", [])`), so the two scripts chain directly:

```bash
python3 engine/sentiment.py --ops data/ops_classified.json --out data/sentiment.json --cli
python3 engine/competitor.py --ops data/ops_classified.json --gen data/sentiment.json \
    --own "Acme PM" --competitor "Rival PM" --out data/competitor_analysis.json
```

## Rules

1. **Every output is labeled `generated: true`.** No exceptions.
2. **Heuristic is the floor, not the ceiling.** The keyword heuristic runs even when `--cli` succeeds, filling gaps for any ops the LLM did not classify.
3. **Small samples get counts, not percentages.** Under 10 ops, state the raw numbers.

## Related

- `../../engine/sentiment.py` — the module this wraps
- `../competitor-intel/` — the primary consumer of sentiment output
- `../../engine/digest.py` — the daily digest can incorporate sentiment
