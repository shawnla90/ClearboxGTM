---
name: last24
version: 1.0.0
description: Surface the freshest buyer signals from the last 24 hours. Wraps engine/last24.py — filters the signal database for threads posted in the last day, ordered by intent and engagement. The morning briefing. Use when the user says "/last24", "what happened today", "fresh signals", or "morning briefing".
---

# last24

The morning briefing — what buyers said in the last 24 hours, sorted by what matters.

When you open your laptop, this is the first thing to run. It filters the signal database for threads posted in the last day, ranks them by intent (comparisons and recommendations first) and engagement, and gives you the list with buyer-language extracts attached. Chain it into the daily digest for the Slack version, or read the JSON directly.

## Inputs

The signal database (`data/signals.db`) — the output of `engine/pull.py` + `engine/mine.py`. With `--refresh`, it re-pulls before filtering.

## How to run

```bash
# read what is already in the database
python3 engine/last24.py --db data/signals.db --out data/last24.json

# refresh first (re-pull with a 1-day window), then filter
python3 engine/last24.py --db data/signals.db --out data/last24.json --refresh

# top 10 only
python3 engine/last24.py --db data/signals.db --out data/last24.json --limit 10
```

## Output shape

`data/last24.json`:

```json
{
  "window": "last 24 hours",
  "cutoff_utc": 1723100000,
  "count": 12,
  "items": [
    {
      "external_id": "...",
      "title": "Looking for an alternative to Monday.com for a 5-person team",
      "subreddit": "r/projectmanagement",
      "permalink": "...",
      "engagement": 47,
      "created_utc": 1723150000,
      "intent": "high",
      "buyer_language": [
        {"kind": "comparison", "quote": "we tried Monday but...", "brands": "monday.com"}
      ]
    }
  ]
}
```

Items are sorted by intent (high → mid → low) then by engagement descending. Each item carries up to 3 buyer-language extracts from the `buyer_language` table for context.

## Chaining into the daily digest

The last24 feed and the Slack digest serve different moments. Last24 is the raw signal for your own morning review. The digest (`engine/digest.py`, wrapped by `skills/slack-digest/`) is the client-facing delivery that includes drafted reply angles. Use last24 to triage, then chain the engage-worthy items into the digest.

## Rules

1. **Recency is a hard gate.** Only threads with `created_utc` in the last 24 hours appear. No stale signals.
2. **`--refresh` is optional, not default.** Without it, the script reads what is already in the database. It never pulls automatically.
3. **Read-only except `--out`.** The database is opened in normal mode but the script only reads; writes go to the JSON output file.

## Related

- `../../engine/last24.py` — the module this wraps
- `../slack-digest/` — the client-facing daily delivery this feeds
- `../../engine/pull.py` — the upstream data pull
- `../../engine/mine.py` — the upstream buyer-language extraction
