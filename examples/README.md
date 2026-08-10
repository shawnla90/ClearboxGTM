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

## The files

- [`exa-retrieval-visibility.json`](exa-retrieval-visibility.json) — Exa retrieval check for "Clearbox" across 8 buyer questions. Score: 0/8 (a new brand before the content strategy lands).
- [`firecrawl-site-scrape.json`](firecrawl-site-scrape.json) — Firecrawl scrape of clearbox.to into structured markdown. 13,902 chars from one API call.
- [`apollo-people-match.json`](apollo-people-match.json) — Apollo people/match from a LinkedIn URL. Returns verified email, title, company, seniority.
- [`moltsets-email-grade.json`](moltsets-email-grade.json) — MoltSets reverse email lookup. Returns deliverability grade (A = safe to send), company enrichment, confirmation date.

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

The Clearbox API is a pull-only HTTP endpoint — every call is a GET. That means it plugs into any platform that can make an HTTP request:

- **Clay** — Add the Clearbox inbox as an HTTP column. Each row arrives pre-classified (lead / competitor / engage) with intent and sentiment. Clay enriches only the leads worth enriching instead of running blind research on every company.
- **n8n** — HTTP Request node pulls the inbox, a Switch node routes by `kind`. n8n's reasoning nodes can layer Clearbox classification with Firecrawl site data and Exa retrieval scores to build a full prospect brief.
- **Zapier** — Webhooks by Zapier catches the classified ops. Route to Google Sheets, Slack, HubSpot, or a custom webhook.
- **Make** — Same HTTP module pattern. The Clearbox API shape (GET, JSON, token in path) works without custom modules.

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
