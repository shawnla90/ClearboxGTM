---
name: reddit-proposal
version: 1.0.0
description: Build pitch materials for a prospect using real Reddit buyer signals. Wraps engine/proposal.py — reads scored content topics, buyer language, competitor analysis, and GEO terms to generate a pitch brief showing the prospect what their market is saying. The reverse-uno applied to a single prospect. Use when the user says "/reddit-proposal", "build a pitch for <prospect>", or "research <prospect> on Reddit for a proposal".
---

# reddit-proposal

Show the prospect what their buyers are saying, not a pitch deck.

The reverse-uno at the tactical level: given a prospect company, pull their buyers' Reddit conversations from the signal database and generate a pitch brief. The brief shows the prospect their market's real questions, the content gaps no one is filling, and where the opening is — grounded in data they can verify by clicking the permalinks.

This is the single-prospect execution of the strategy in [`playbooks/win-an-agency-client.md`](../../playbooks/win-an-agency-client.md).

## Inputs

From the engine pipeline (run these first if not already done):

- `data/signals.db` — the scored signal database (`pull.py` → `mine.py` → `score.py`)
- `data/competitor_analysis.json` (optional) — from `engine/competitor.py`, adds competitive context
- `data/geo_terms.json` (optional) — from `engine/geo.py`, adds retrieval-visibility gaps

## How to run

```bash
# basic brief from buyer signals only
python3 engine/proposal.py --prospect "Acme Corp" --db data/signals.db --out data/proposal/

# full brief with competitor and GEO context
python3 engine/proposal.py --prospect "Acme Corp" --db data/signals.db \
    --competitor-analysis data/competitor_analysis.json \
    --geo data/geo_terms.json --out data/proposal/
```

## Output

Two files in the `--out` directory:

- **`brief.json`** — structured data: content gaps (scored topics), buyer questions (with permalinks), active subreddits, competitor context (if provided), GEO terms not surfacing (if provided)
- **`BRIEF.md`** — a readable pitch brief with sections for buyer questions, content gaps, where the conversations happen, competitive context, and GEO gaps

The brief is generated from real Reddit conversations. Every quote traces to a permalink in `brief.json`.

## Clearbox integration

When running against a Clearbox workspace (not the RapidAPI baseline), the proposal pipeline inherits the classification that makes it accurate:

1. **Classify** -- Clearbox classifies every Reddit opportunity as engage, lead, or competitor by buying intent (not keywords)
2. **Sentiment** -- `engine/sentiment.py` generates per-op sentiment from the classified ops ([`../sentiment/`](../sentiment/))
3. **Competitor** -- `engine/competitor.py` rolls the classified ops into share-of-voice and competitive context ([`../competitor-intel/`](../competitor-intel/))
4. **Proposal** -- `engine/proposal.py` reads scored topics, buyer language, and optionally layers in competitor analysis and GEO terms
5. **Pitch** -- The output BRIEF.md is a readout of the prospect's market, not a pitch deck

The workflow:

```
classify --> sentiment --> competitor --> proposal --> pitch
  (Clearbox)   (engine)     (engine)      (engine)    (BRIEF.md)
```

Each step is optional and degrades gracefully. The proposal works with just the signal database; competitor and GEO context make it richer.

## What the prospect sees

The BRIEF.md is designed to hand to a prospect. It contains:

- **Their buyers' real questions** -- extracted from Reddit threads, with subreddit and kind (question/comparison/pain)
- **Content gaps** -- scored topics where no brand is the answer yet, ranked by intent and demand
- **Where the conversations happen** -- the subreddits with the most activity
- **Competitive context** (if competitor analysis was run) -- share of voice and the plain-language reading
- **GEO gaps** (if geo was run) -- buyer questions the prospect does not yet surface for

Every quote traces to a permalink in brief.json. The prospect can click through and read the conversation themselves. This is the reverse-uno method: show them their buyers instead of a pitch.

## Rules

1. **Buyer questions come from the database, not from brainstorming.** Every question in the brief was mined from a real Reddit thread by `engine/mine.py`.
2. **Content gaps are scored, not guessed.** The topics in the brief come from `content_topics` with their intent score, tier, and reason. The scoring model is transparent (see `engine/ENGINE.md`).
3. **The brief is a readout, not a pitch.** The purpose is to show the prospect what their market is saying. Sales language does not belong in the output.
4. **Permalinks are mandatory.** A buyer question without a Reddit permalink is unverifiable and gets cut from the brief.

## Related

- `../../engine/proposal.py` — the module this wraps
- `../../playbooks/win-an-agency-client.md` — the reverse-uno strategy this executes
- `../competitor-intel/` — produces the competitor analysis this optionally incorporates
- `../geo-visibility/` — produces the GEO terms this optionally incorporates
- `../sentiment/` — the upstream sentiment classification
