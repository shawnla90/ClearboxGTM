# What a client market read looks like

This is the sanitized structure of a real deliverable built from a Clearbox inbox. The data is redacted; the pattern is exact. Every client engagement produces this document, and it pushes to Notion as a shareable page with a stable URL.

## The pattern

A market read triages every opportunity in the inbox into four buckets: strike now, secondary plays, competitor watch, and skip. Each bucket follows a consistent format.

### Strike now (3-5 ops)

The highest-intent signals where the client's product is the direct answer. Each entry follows the **signal / win / enter** triad:

```
### 1. "[The buyer's exact question or pain point]"

**Signal:** A buyer in [r/subreddit](permalink) is [what they said].
The thread context is [why this matters right now].

**Where [client] wins:** [One sentence: why the client's product is
the answer to this specific question, not a generic pitch.]

**How to enter:** Reply as [named person]. [Exact tactical advice:
what to say, what to link, what to disclose.] No pitch deck.

[Op N · r/subreddit · date](permalink)
```

The signal is a quote or paraphrase from the actual Reddit thread. The win is specific to the client's product, not a category claim. The entry instructions name a person and give them one paragraph to post.

### Secondary plays (5-8 ops)

Lower intent or less direct fit, but still actionable. Same format, briefer. These are threads where the client can add value by answering a question, sharing expertise, or offering a comparison — without selling.

### Competitor watch (1-3 ops)

Threads where a competitor was named or recommended. Each entry includes the direct quote, the competitor's positioning in the thread, and the counter-positioning for the client. The client never argues with the commenter; the competitive insight feeds content strategy.

### What to skip

A table of every op explicitly excluded, with the reason:

```
| Op | Why skip |
|----|----------|
| Op N (engage) | Author already chose a tool — not shopping |
| Op M (engage) | Peer, not prospect — building their own solution |
```

Skips are documented so the operator does not re-evaluate them. Explicit skips prevent the inbox from becoming a guilt pile.

## The standard sections

Every market read ends with the same five sections:

### The operating rule

Five engagement principles:

1. Value first — every reply answers the question. Product link comes last, if at all.
2. Disclose — "[I work at Company]" in every reply.
3. Write for the silent readers — the 50 people who read the thread without commenting are the real audience.
4. Pace it — two replies per day across all threads.
5. Mark done only after action — reading is not done.

### Who should own what

Names a day-to-day operator (the person who posts) and an executive sponsor (the person who approves the voice). Real names, not roles.

### The first move

One sentence naming the single highest-priority action: which thread, which reply, right now.

### Closing tagline

> The inbox reads. [Client] decides. The voice stays human.

## What produces each section

| Section | Produced by | Data source |
|---------|-------------|-------------|
| Strike now / Secondary | Manual triage of classified ops | Clearbox inbox (`GET /a/{token}/inbox`) |
| Competitor watch | `engine/competitor.py` + manual review | Clearbox `kind: competitor` ops |
| What to skip | Manual decision, documented | All ops not in the other buckets |
| Operating rule | Template (same for every client) | `playbooks/how-to-win-on-reddit.md` |
| Who should own what | Client briefing | Intake call or onboarding |

## How it reaches the client

The markdown pushes to Notion via `notion_audit.py` (or `push_notion.py` for full command centers). The resulting page has a stable public URL on `notion.site` that the client bookmarks. Updates rebuild the page in place — same URL, fresh data.

## Related

- [`../playbooks/orchestrate-freckle.md`](../playbooks/orchestrate-freckle.md) — the full pipeline that produces the ops
- [`../playbooks/win-an-agency-client.md`](../playbooks/win-an-agency-client.md) — how this deliverable wins the client in the first place
- [`../skills/reddit-proposal/`](../skills/reddit-proposal/) — the automated version (BRIEF.md)
- [`../skills/competitor-intel/`](../skills/competitor-intel/) — the competitor watch data source
