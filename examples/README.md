# API examples

Real API responses from real services, generated 2026-08-09. Every file in this directory is an actual API call, not a mock. The `_example_note` field in each file explains what the output means and how it fits the pipeline.

## What each API does — with and without

| API | What it does | Without it | With it |
|-----|-------------|-----------|---------|
| **Exa** | Retrieval visibility check | Terms listed, no live score | Brand-surfaces-for-buyer-question score |
| **Firecrawl** | Site crawl + SEO audit | Manual web fetch in onboarding research | Structured markdown of entire site in one call |
| **Apollo** | People/email reveal | No email enrichment | Verified email + title + company from a LinkedIn URL |
| **MoltSets** | Email deliverability grade | Send without grading | A-F grade, catchall detection, freemail flag |
| **RapidAPI** (reddit34) | Reddit thread pull | Use bundled offline sample or Clearbox | Live keyword-based pull, free tier available |
| **Clearbox** | Classified opportunity inbox | RapidAPI keyword matching (noisier) | Intent-classified, context-driven signal |

Every API is optional. The pipeline runs without any of them; each one makes a specific step better.

## Sanitized client-pack fixtures

[`client-pack/`](client-pack/) contains synthetic, non-client fixtures for the reusable agency builder:

- A Clearbox account API response with lead, engage, competitor, and exact permalink fields.
- Equivalent Freckle JSON, Base Loop native `rows[].cells` JSON, and Clay CSV analysis overlays.

Run any overlay through `engine/build_client_pack.py` to verify that all three processing paths produce the same eleven-view Sheet and guided Notion contract while preserving the original Clearbox dispositions.

## The files

- [`exa-retrieval-visibility.json`](exa-retrieval-visibility.json) — Exa retrieval check for "Clearbox" across 8 buyer questions. Score: 0/8 (a new brand before the content strategy lands).
- [`firecrawl-site-scrape.json`](firecrawl-site-scrape.json) — Firecrawl scrape of clearbox.to into structured markdown. 13,902 chars from one API call.
- [`apollo-people-match.json`](apollo-people-match.json) — Apollo people/match from a LinkedIn URL. Returns verified email, title, company, seniority.
- [`moltsets-email-grade.json`](moltsets-email-grade.json) — MoltSets reverse email lookup. Returns deliverability grade (A = safe to send), company enrichment, confirmation date.
- [`firecrawl-freckle-site.json`](firecrawl-freckle-site.json) — Firecrawl scrape of freckle.io. 120,290 chars of structured markdown from one API call — the kind of output the onboarding research step consumes.

## How these fit the pipeline

```
subreddit config
      |
      v
  pull.py (RapidAPI or Clearbox)
      |
      v
  mine.py --> score.py --> build_sheet.py
      |           |
      v           v
  geo.py -----> Exa (retrieval visibility check)
      |
      v
  clearbox-onboard --> Firecrawl (site crawl for research)
      |
      v
  coverage waterfall --> Apollo (LinkedIn URL to email)
                             |
                             v
                         MoltSets (email to deliverability grade)
                             |
                             v
                         classify: T1_send / T2_catchall / SUPPRESS
```

## Where the API fits in automation platforms

The Clearbox API is a pull-only HTTP endpoint — every call is a GET. That means it plugs into any platform that can make an HTTP request. Each platform has a full step-by-step guide with Mermaid workflow diagrams:

- **Clay** — HTTP column, Filter by kind, enrich only leads. 60-96% fewer credits vs keyword research. [Full guide →](integrations/clay.md)
- **n8n** — HTTP Request → Switch → AI Agent reasoning nodes for prospect briefs. [Full guide →](integrations/n8n.md)
- **Zapier** — Schedule → Webhooks GET → Filter → Sheets/Slack/HubSpot. [Full guide →](integrations/zapier.md)
- **Make** — HTTP module → Iterator → Router. No custom modules needed. [Full guide →](integrations/make.md)

## Workflow diagrams

Visual node graphs showing how the pieces connect:

- [**Enrichment waterfall**](workflows/enrichment-waterfall.md) — disclosure gate → Freckle → Apollo → MoltSets → classify
- [**AEO content loop**](workflows/aeo-content-loop.md) — buyer questions → GEO terms → Exa check → content gaps → publish → re-check

## Client deliverable example

What a real client deliverable looks like — the triage pattern, the signal/win/enter triad, and how it pushes to Notion: [**client-market-read.md**](client-market-read.md)

## Key setup

Every key follows the same pattern: set the env var, or store it in a secrets database (sqlite file with a `secrets(key, value)` table, path in `SECRETS_DB`).

```bash
export EXA_API_KEY=...           # retrieval visibility (geo.py)
export FIRECRAWL_API_KEY=...     # site crawl (onboarding research)
export APOLLO_API_KEY=...        # people reveal (coverage waterfall)
export MOLTSETS_API_KEY=...      # email grading (coverage waterfall)
export RAPIDAPI_KEY=...          # reddit34 pull (pull.py)
```

Without a key, the step degrades — no crash, no error, just a narrower output.
