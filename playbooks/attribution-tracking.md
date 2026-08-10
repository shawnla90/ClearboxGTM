# Attribution tracking — the journey materialization pattern

How to know where your users came from, without cookies, without third-party tracking, on your own infrastructure.

## Why this pattern

Attribution is the question that shapes every GTM decision: which channel produced the user? The typical answer involves cookie-based analytics, third-party tracking pixels, and a vendor that owns your data. The pattern here does none of that. It materializes journeys from an events table in a local SQLite database, produces first-touch and last-touch channel attribution, and runs on your own machine. No one else sees the data.

This is how the proof pipeline in this repo (`proof/generate_proof.py --with-logpose`) generates the signup-attribution tables. It is also how the `skills/dataviz/examples/ChannelBars.tsx` chart gets its data.

## The architecture

```
sources (CRM, product, outbound, content)
    ↓ adapters (one per source, idempotent, keyed by source_ref)
events table (person_id, ts, kind, channel, direction, source, source_ref)
    ↓ journey materialization query
journeys table (person_id, first_touch_channel, last_touch_channel, touch_count, signup_at)
    ↓ read-only dashboard
ChannelBars chart / proof pipeline / Slack digest
```

### The identity spine

Events from different sources need to resolve to one person. The identity table uses a `UNIQUE(kind, value)` constraint:

```sql
CREATE TABLE identities (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES persons(id),
    kind TEXT NOT NULL,  -- email, linkedin_url, x_handle, reddit_username, ...
    value TEXT NOT NULL,
    UNIQUE(kind, value)
);
```

One person can have multiple identities (their email, their LinkedIn URL, their Reddit username). The constraint ensures each identity value maps to exactly one person. When a new source event comes in, the adapter looks up the identity, finds or creates the person, and writes the event against that person_id.

### The events table

The single timeline:

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES persons(id),
    ts TEXT NOT NULL,           -- ISO 8601
    kind TEXT NOT NULL,         -- signup, page_view, reply, meeting_booked, deal_created, ...
    channel TEXT,               -- reddit, linkedin, email, web, referral, search, x, ...
    direction TEXT,             -- inbound, outbound, internal
    source TEXT NOT NULL,       -- adapter name that wrote this
    source_ref TEXT NOT NULL,   -- dedup key within the source
    UNIQUE(source, source_ref, kind)
);
```

The `UNIQUE(source, source_ref, kind)` constraint makes adapters idempotent — re-running the same adapter produces the same events, no duplicates.

### The journey materialization

The query that produces attribution:

```sql
-- First-touch: the channel of the earliest event for each person
-- Last-touch: the channel of the latest event before signup
INSERT OR REPLACE INTO journeys (person_id, first_touch_channel, last_touch_channel, touch_count, signup_at)
SELECT
    p.id,
    (SELECT e.channel FROM events e WHERE e.person_id = p.id ORDER BY e.ts ASC LIMIT 1) AS first_touch,
    (SELECT e.channel FROM events e WHERE e.person_id = p.id AND e.ts <= COALESCE(
        (SELECT e2.ts FROM events e2 WHERE e2.person_id = p.id AND e2.kind = 'signup' LIMIT 1),
        datetime('now')
    ) ORDER BY e.ts DESC LIMIT 1) AS last_touch,
    (SELECT COUNT(*) FROM events e WHERE e.person_id = p.id) AS touch_count,
    (SELECT e.ts FROM events e WHERE e.person_id = p.id AND e.kind = 'signup' LIMIT 1) AS signup_at
FROM persons p;
```

This is a full rebuild — idempotent, runs on every sync. The journey table is a materialized view, not a primary data source.

## What you get

The journeys table answers the attribution question directly:

```sql
-- Signups by first-touch channel
SELECT first_touch_channel, COUNT(*) AS n
FROM journeys
WHERE signup_at IS NOT NULL
GROUP BY first_touch_channel
ORDER BY n DESC;

-- Signups by last-touch (what pushed them over the edge)
SELECT last_touch_channel, COUNT(*) AS n
FROM journeys
WHERE signup_at IS NOT NULL
GROUP BY last_touch_channel
ORDER BY n DESC;
```

Feed these into `ChannelBars.tsx` from `skills/dataviz/` and you have the chart.

## Your data stays yours

This pattern runs entirely on your infrastructure. The databases are local SQLite files. The adapters read your CRM, product analytics, and outbound tools via their APIs, but the data lands in a file on your disk. No third-party analytics vendor sees it. No cookies track your visitors. No pixel fires.

The engine scripts in this repo follow the same principle: every database connection is read-only (or writes only to an explicit `--out` file). The dashboard reads the data; it never writes to the source. A crashed dashboard cannot corrupt your event stream.

This is not just a privacy stance — it is an architecture that makes attribution reliable. When you own the data, you can join sources that a SaaS analytics tool cannot: Reddit usernames to CRM emails to signup events to deal outcomes. The identity spine makes that join possible without a vendor in the middle.

## How this connects to the proof pipeline

`proof/generate_proof.py --with-logpose` reads the journeys table to produce the "signups by first-touch channel" table in `proof/README.md`. The same data, the same queries, verified by the scan gate.

## Related

- [`../proof/generate_proof.py`](../proof/generate_proof.py) — where this data feeds
- [`skills/dataviz/`](../skills/dataviz/) — the Recharts components that visualize it
- [`transparency/what-actually-worked.md`](../transparency/what-actually-worked.md) — the attribution findings this pattern produced
- [`SECURITY.md`](../SECURITY.md) — the broader data-protection model
