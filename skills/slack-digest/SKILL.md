---
name: slack-digest
version: 1.0.0
description: Render and optionally post the daily Slack digest of a client's Reddit opportunities. Wraps engine/digest.py — engage threads with drafted replies, new leads, competitor mentions, ordered by priority, capped. Render-only by default; --post sends to Slack via incoming webhook. Use when the user says "/slack-digest", "build the daily digest", "post to Slack", or "morning delivery".
---

# slack-digest

The daily client delivery: what to work today, delivered to Slack.

The operated-service version of the morning briefing. Each day the account's engage threads (with the drafted, value-first reply), new leads, and competitor mentions land in the client's Slack channel. Priority-ordered, capped, with permalinks. Render-only by default — posting requires an explicit `--post` flag and a webhook secret.

## Setup

1. Create a Slack incoming webhook for the target channel
2. Store the webhook URL as an environment variable or in a local secrets database:
   ```bash
   export SLACK_WEBHOOK_YOURCLIENT="https://hooks.slack.com/services/T.../B.../..."
   ```
   Or add it to a SQLite secrets store (a table with `key` and `value` columns) and set `SECRETS_DB` to that file path.

## Inputs

- `data/ops_classified.json` — classified opportunities from a Clearbox workspace run
- `data/engage_angles.json` — drafted reply angles for the engage-lane ops (exported by `replies.py angles`, the engage skill, or manually)
- `--client` — the client name for the digest header

## How to run

```bash
# render to a text file only (inspect before posting)
python3 engine/digest.py --ops data/ops_classified.json --angles data/engage_angles.json \
    --client "Acme PM" --out data/slack_digest.txt

# render + post to Slack
python3 engine/digest.py --ops data/ops_classified.json --angles data/engage_angles.json \
    --client "Acme PM" --out data/slack_digest.txt --post --webhook-secret SLACK_WEBHOOK_YOURCLIENT

# custom date and cap
python3 engine/digest.py --client "Acme PM" --date "Aug 9, 2026" --limit 5 --out data/slack_digest.txt
```

## Output

A formatted Slack message with:

- Header: client name, date, count of engage threads
- Per-opportunity block: priority tag, subreddit, age, summary, why-it-matters, drafted reply angle, permalink
- Overflow note if more ops exist beyond the cap

## Rules

1. **`--post` is never the default.** Without it, the script renders to a text file only. Review before posting.
2. **The webhook URL is a secret.** It comes from an env var or a secrets database, never from a hardcoded string or a committed file.
3. **Reply first, value first.** The digest orders by priority (high → med → low) and surfaces the drafted reply angle. The client acts on the digest by replying to threads, not by liking or voting.

## Related

- `../../engine/digest.py` — the module this wraps
- `../last24/` — the raw signal feed that surfaces fresh threads for the digest
- `../reddit-engage/` — where the reply angles in the digest come from
- `../reply-engine/` — drafts the gated reply templates and exports the angles file this digest renders
- `../../playbooks/automation-boundaries.md` — the rule that digest delivery is automated but thread replies are always human
