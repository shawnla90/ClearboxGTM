---
name: competitor-intel
version: 1.0.0
description: Build a competitor narrative from Reddit signals — share of voice, sentiment, and where the opening is. Wraps engine/competitor.py + engine/sentiment.py. Use when the user says "/competitor-intel", "what are competitors doing on Reddit", "build a competitive analysis", or "share of voice".
---

# competitor-intel

Where is a competitor the answer, and where is the opening yours?

Clearbox classifies every Reddit opportunity as engage, lead, or competitor against the offer's own and competitor brands. That classification is the relevant-mention signal — no literal brand-string counting. This skill rolls those classified ops into a share-of-voice view and a generated sentiment read, then surfaces the conversations where the opening belongs to the client.

## How it works

Two engine scripts, chained:

1. **`engine/sentiment.py`** — generates a per-op sentiment classification (positive / neutral / negative, 1-5 score) from the op summaries. Heuristic by default; `--cli` adds an LLM pass for richer reads. Output labeled as generated.
2. **`engine/competitor.py`** — reads the classified ops and the sentiment output, rolls them into share-of-voice (competitor-is-the-answer vs client-category-is-the-opening), sentiment distribution, and the list of competitor conversations with permalinks.

## Inputs

The canonical input is a classified ops file (`data/ops_classified.json`) — the output of a Clearbox workspace run or a manual classification pass over `engine/pull.py` + `engine/mine.py` output. You also need:

- `--own` — the client's brand name
- `--competitor` — the competitor brand to analyze against

## How to run

```bash
# 1. generate sentiment from classified ops
python3 engine/sentiment.py --ops data/ops_classified.json --out data/sentiment.json
python3 engine/sentiment.py --ops data/ops_classified.json --out data/sentiment.json --cli

# 2. build the competitor narrative, feeding in the sentiment
python3 engine/competitor.py --ops data/ops_classified.json --gen data/sentiment.json \
    --own "Acme PM" --competitor "Rival PM" --out data/competitor_analysis.json
```

## Output shape

`data/competitor_analysis.json`:

- `share_of_voice` — basis (classification, not counting), total opportunities, competitor-is-the-answer count, client-category-is-the-opening count, competitor share %, and a plain-language reading
- `sentiment` — distribution (positive/neutral/negative counts), average score, per-op detail; always marked `generated: true`
- `competitor_conversations` — the actual threads where the competitor was the answer, with subreddit, summary, permalink, and author
- `narrative` — a generated summary (from the `--gen` file, if present)

## Rules

1. **Share of voice is from classification, not literal counting.** Clearbox classifies ops by buying intent, not by how often a brand name appears in text.
2. **Sentiment is LLM-generated and labeled as such.** Reddit opportunities carry no sentiment field. Every sentiment output carries `generated: true` and a note explaining what it is.
3. **Never assert market share from Reddit alone.** Reddit conversations are a signal, not a census. A competitor appearing in 30% of classified ops means 30% of the Reddit conversations Clearbox surfaced, not 30% of the market.

## Related

- `../../engine/competitor.py` — the share-of-voice module
- `../../engine/sentiment.py` — the sentiment classification module
- `../geo-visibility/` — retrieval visibility for the terms the competitor owns
- `../../playbooks/win-an-agency-client.md` — the strategy this analysis feeds
- `../../VERIFYING.md` — the provenance and language rules
