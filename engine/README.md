# Reddit Buyer Signals

Turn the Reddit conversations your buyers are having right now into a color-coded, scored content plan, then a deck you can pitch. Connect Google over the CLI, pull recent buyer threads, score every topic 1 to 5, and get a shared Google Sheet plus an editable Google Slides deck. This is the full loop, not a read-only analysis toy. You own all of it.

Part of [ClearboxGTM](../README.md). Also ships as the `reddit-buyer-signals` starter in the [GTM Coding Agent Starter Kit](https://github.com/shawnla90/gtm-coding-agent), documented in its chapters 18 and 19.

## What it does

```
config/ (subreddits + keywords)
        │
        ▼
  recent Reddit pull  ──►  SQLite (local)  ──►  mine buyer language  ──►  score 1-5
   (last 30 days only)                                                        │
        ▲                                                                     ▼
   two sources                                           color-coded Google Sheet  +  Google Slides deck
   rapidapi | clearbox
```

- **`init_db.py`** creates the local SQLite database, idempotent, safe to re-run.
- **`pull.py`** pulls recent buyer threads from Reddit through a recency guardrail (last 30 days) and a relevance filter, from one of two sources (see below).
- **`mine.py`** turns raw threads into real buyer language (questions, comparisons, pains) and clusters it into scored content topics. Optionally polishes the topic titles with `claude -p` on your subscription, no API key.
- **`score.py`** scores every topic 1 to 5 on buyer intent, demand, competitive fit, and how widely the threads are read, and writes a one-line reason you get to keep.
- **`build_sheet.py`** renders it all as a Google Sheet: score gradient red to green, tier colors, a dashboard tab, frozen headers, filters, shared anyone-with-link. Rebuilds in place so the link never changes.
- **`build_deck.py`** (optional) builds a short editable Google Slides deck from the same scored data.

The styling engine is `lib/sheet_engine.py`. It is the real, reusable piece. See [ENGINE.md](ENGINE.md).

### From signal to service

The same classified signal feeds five more modules that turn it into an operated client offer. Each is a single file, reads the pipeline's data, and re-points by argument. [ENGINE.md](ENGINE.md) documents them in full.

- **`geo.py`** the buyer questions to own, each checked for current retrieval visibility through a hard-capped Exa pass. Exa is a leading indicator, not proof that an AI answer named or cited the brand.
- **`competitor.py`** the competitor narrative read straight from Clearbox's opportunity classification (the classification is the relevant-mention signal, not literal brand counting), plus a generated sentiment read and a share-of-voice view.
- **`digest.py`** the daily digest of engage threads with the drafted reply, new leads, and competitor mentions, as a header line plus one block per opportunity ordered by priority. Render-only by default; add `--post --webhook-secret <SECRET_NAME>` to post to an incoming webhook.
- **`unmask.py`** the disclosure gate (enrich the company not the person, and only when the author self-disclosed a company by naming it, linking a site, or posting as a brand handle), then a pluggable enrichment backend (Freckle by default, swap in Clay or Apollo) returning the company, the ICP tier, and buying-role contacts.
- **`content.py`** scaffold a LinkedIn, Reddit, and blog content pack from one buyer question in the brand voice, plus an anti-slop check subcommand.
- **`sentiment.py`** thread-level sentiment classification (positive/neutral/negative, 1-5 score) from classified ops, heuristic by default with optional `--cli` for LLM-powered reads. Output feeds `competitor.py --gen`.
- **`last24.py`** the morning briefing: buyer signals from the last 24 hours, ranked by intent and engagement. Optional `--refresh` pulls fresh data first.
- **`proposal.py`** pitch materials for a prospect from their buyers' Reddit conversations. Outputs a structured `brief.json` + readable `BRIEF.md` for the reverse-uno.

```bash
python3 geo.py --brand "Acme PM" --db data/signals.db --out data/geo_terms.json
python3 competitor.py --own "Acme PM" --competitor "Rival PM" --out data/competitor_analysis.json
python3 digest.py --client "Acme PM" --out data/slack_digest.txt
python3 unmask.py --ops data/ops_classified.json --out data/unmasked.json          # add --enrich to live-enrich
python3 content.py scaffold --client "Acme PM" --topic "how to keep one source of truth across two CRMs" --out content/pack-01
python3 content.py check content/pack-01/linkedin.md
python3 sentiment.py --ops data/ops_classified.json --out data/sentiment.json --cli
python3 last24.py --db data/signals.db --out data/last24.json --refresh
python3 proposal.py --prospect "Acme Corp" --db data/signals.db --out data/proposal/
```

The example throughout is a project-management SaaS for small teams (call it "Acme PM"). Point it at your own market by editing two config files and two Python maps.

## Prerequisites

- Python 3.9+
- A Google account (personal or Workspace) that will own the sheet and deck
- One data source: a reddit34 RapidAPI key for the live pull, or nothing at all for the bundled offline sample

> **First-time setup takes 5 minutes.** You need Python 3.9+, a Google account, and a one-time OAuth connection. The script walks you through it -- no GCP experience required. [Jump to setup](#1-clone-and-enter-the-starter)

## Setup

### 1. Clone and enter the starter

```bash
git clone https://github.com/shawnla90/ClearboxGTM.git
cd ClearboxGTM/engine
```

### 2. Install the dependencies

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 3. Connect Google Workspace (the step many copy-paste guides skip)

The builder writes to Google Sheets and Slides as you, over OAuth. The first build fails without a token, so do this once:

```bash
python3 setup_oauth.py
```

If you have never made a Google OAuth client, the script prints the exact steps: create a Google Cloud project, enable the Sheets and Drive APIs, make a Desktop OAuth client, download the JSON to `~/.config/gspread/client_secret.json`, then re-run. A browser opens, you sign in, and the token lands at `~/.config/gspread/token.json`. That is the connection that makes everything else work.

### 4. Run the pipeline

Try it offline first, no key required. This copies the bundled sample export in and runs the whole loop on it:

```bash
bash run.sh --offline
```

Then run it live against real Reddit with your key:

```bash
export RAPIDAPI_KEY=your_reddit34_key
bash run.sh
```

It prints a Google Sheet URL at the end. Open it. That is your buyer signal, scored and color-coded. For the deck, run the optional sixth step:

```bash
python3 build_deck.py
```

## Use your own niche

The whole engine points at one market. Move it to yours in four edits:

1. **`config/subreddits.txt`** the communities your buyers post in.
2. **`config/keywords.txt`** the "X vs Y" and "best tool for" searches your buyers run.
3. **`lib/relevance.py`** the `BRANDS` (the tools buyers compare you against), `CATEGORY` nouns (so off-topic threads get filtered out), and `TOPIC_KEYWORDS` (how threads auto-tag into topics).
4. **`score.py`** the `CARRIED` tuple (the competitor set a topic can map to for a higher score).

Set your product name so the outputs read as yours:

```bash
BRAND="Your Product" bash run.sh
BRAND="Your Product" python3 build_deck.py
```

The rules are plain Python, not a black box.

## Two data sources

`pull.py` reads from one of two sources, chosen with `REDDIT_SOURCE`. Both feed the exact same pipeline, so the sheet and deck look identical either way. The difference is how good the input is.

- **RapidAPI (`REDDIT_SOURCE=rapidapi`, the default).** A quick baseline. It runs keyword searches and subreddit pulls through the reddit34 RapidAPI, then filters by relevance and recency on the way in. Fast and cheap, good enough to see the gap and build the first version. It matches on keywords, so some noise gets through and some intent gets missed.
- **Clearbox (`REDDIT_SOURCE=clearbox`).** The accurate, context-driven version. Clearbox classifies Reddit by real buying intent (intent, not keywords), off real content consumption, and adds sentiment and competitor context. You export your filtered opportunity inbox to `data/clearbox_export.json` and this reads it through the same recency and relevance gates. Higher signal in, higher signal out. The bundled `data/clearbox_export.sample.json` is a small stand-in so you can run the flow with no key.

This is not a forced upsell. The RapidAPI path is genuinely useful and free to start. Clearbox is the better engine when you want the real high-intent conversations instead of a keyword's best guess.

### Access everything through the API

The Clearbox opportunity inbox is a pull-only HTTP API, so the Clearbox path in this starter is a handful of GET requests you own.

- `GET /inbox` returns the classified opportunities, one row each, and every row carries `kind = lead | competitor | engage`.
- `GET /op/{id}` returns one opportunity in full.
- `GET /op/{id}/done` marks that opportunity handled.

Two things trip people up. The token is a path segment in the URL, not a header, so it rides inside the path itself. And Cloudflare returns 403 to a default urllib User-Agent, so send a browser User-Agent on every request. There are no POST routes. Every call is a read, and the one state change, marking an op done, is itself a GET.

## Enrichment APIs — with and without

Every API in this pipeline is optional. The pipeline runs without any of them; each one makes a specific step better. The cost tradeoff matters: a Clay table burning credits on random company research costs more per row than pulling pre-classified intent from the Clearbox API and only enriching what is worth enriching.

| API | What it does | Without it | With it |
|-----|-------------|-----------|---------|
| **RapidAPI** (reddit34) | Reddit thread pull | Use bundled offline sample or Clearbox | Live keyword-based pull, free tier available |
| **Clearbox** | Classified opportunity inbox | RapidAPI keyword matching (noisier) | Intent-classified, context-driven signal |
| **Exa** | Retrieval visibility check | Terms listed, no live score | Brand-surfaces-for-buyer-question score |
| **Firecrawl** | Site crawl + SEO audit | Manual web fetch in onboarding research | Structured markdown of entire site, SEO baseline |
| **Apollo** | People/email reveal | No email enrichment | Email + title + company from a LinkedIn URL |
| **MoltSets** | Email deliverability grade | Send without grading | A-F grade, catchall detection, freemail flag |

### Key setup

Every key follows the same pattern: set the env var, or store it in a secrets database (sqlite file with a `secrets(key, value)` table, path in `SECRETS_DB`). Without a key, the step degrades — no crash, no error, just a narrower output.

```bash
export EXA_API_KEY=...           # retrieval visibility (geo.py)
export FIRECRAWL_API_KEY=...     # site crawl (onboarding research)
export APOLLO_API_KEY=...        # people reveal (coverage waterfall)
export MOLTSETS_API_KEY=...      # email grading (coverage waterfall)
export RAPIDAPI_KEY=...          # reddit34 pull (pull.py)
```

### Where the API fits in automation platforms

The Clearbox API is a pull-only HTTP endpoint. Every call is a GET. That means it plugs into any platform that can make an HTTP request:

- **Clay** — Add the Clearbox inbox as an HTTP column. Each row arrives pre-classified (lead / competitor / engage) with intent and sentiment. Clay enriches only the leads worth enriching instead of running blind research on every company. The cost difference is the point: one classified API call replaces dozens of speculative Clay credits.
- **n8n** — HTTP Request node pulls the inbox, a Switch node routes by `kind` (lead → enrich → CRM, competitor → alert → Slack, engage → draft → queue). n8n's reasoning nodes can layer Clearbox classification with Firecrawl site data and Exa retrieval scores to build a full prospect brief before a human touches it.
- **Zapier** — Webhooks by Zapier catches the classified ops. Route to Google Sheets, Slack, HubSpot, or a custom webhook. Simpler than n8n but covers the 80% case.
- **Make (Integromat)** — Same HTTP module pattern as n8n. The Clearbox API shape (GET, JSON, no auth header — token in path) works without custom modules.

The integration guides for each platform ship in a future release. The API shape is documented above in ["Access everything through the API"](#access-everything-through-the-api).

## Build vs buy

This is build versus buy, with eyes open. You can stand up the full loop yourself and know exactly what it does. The RapidAPI path is free to start and honest about its limits: it matches keywords, so it finds the conversations a keyword can find. Want the accurate, context-driven version that surfaces the real high-intent conversations for you? That is what [Clearbox](https://clearbox.to) does.

## The recency guardrail

`pull.py` only keeps threads from the **last 30 days**. Nothing older ever enters the database. Widen it if you want a fuller season:

```bash
MAX_AGE_DAYS=60 python3 pull.py
```

This is deliberate, and it is the whole point. Two reasons:

- **Current threads are where participation is still useful.** A live conversation lets the account answer a real buyer while the discussion is active. Search or AI visibility is measured later and is never guaranteed by recency alone.
- **It keeps you sincere.** The useful place to participate is a conversation that is actually happening. Recent-only keeps the queue focused on live discussions. It is not a guarantee against removals or enforcement; community rules and the quality of the contribution still control.

## Rebuild in place

`build_sheet.py` stores the sheet URL in `data/sheet_url.txt`, and `build_deck.py` stores the deck URL in `data/slides_url.txt`. Run either again and it refreshes the same doc, so any link you have shared stays valid:

```bash
python3 build_sheet.py                 # rebuild the stored sheet
python3 build_sheet.py <sheet_id>      # rebuild a specific sheet
python3 build_deck.py                  # rebuild the stored deck
```

## Take it further

- **Schedule it.** Wrap `run.sh` in a cron job so the plan re-scores itself weekly as new threads land, and the plan always reflects whatever your buyers are debating this month.
- **Feed the deck to the meeting.** `build_deck.py` reads the live numbers straight from the database, so a rebuild before a pitch always shows current data.
- **Cloud master.** Mirror the SQLite tables to Supabase so a team or a dashboard reads the same signal. Idempotent upsert with the header `Prefer: resolution=merge-duplicates`.
- **Polish with Claude.** `mine.py --cli` rewrites the top topic titles into clean, searchable, citable headlines using your Claude Code subscription. It falls back silently to the heuristic titles if the CLI is not there, so a run never breaks.

## Troubleshooting

- **`Missing ~/.config/gspread/client_secret.json`**: you have not created your OAuth client yet. Run `setup_oauth.py` and follow the printed steps.
- **`invalid_grant` or token errors**: delete `~/.config/gspread/token.json` and run `setup_oauth.py` again.
- **The app is unverified warning**: it is your own app. Click Advanced, then continue.
- **`no RAPIDAPI_KEY set`**: export your reddit34 key, or run `bash run.sh --offline` to use the bundled sample with no key.
- **Empty topics**: a small pull yields modest scores. Widen `MAX_AGE_DAYS`, add more subreddits and keywords, or switch to the Clearbox source for higher-intent input.

---

> 🟧 **Clearbox** is the engine behind this starter. See your market. Move first. Start a 7-day free trial at [clearbox.to](https://clearbox.to).
