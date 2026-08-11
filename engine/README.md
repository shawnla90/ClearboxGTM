# Reddit Buyer Signals

Turn Clearbox-classified Reddit opportunities into a scored content plan, an eleven-view client Sheet, and a guided Notion brief. Clearbox owns the source disposition and exact permalink. Freckle, Base Loop, and Clay can add analysis after the pull without changing that record.

Part of [ClearboxGTM](../README.md). The same engine ships in the [GTM Coding Agent Starter Kit](https://github.com/shawnla90/gtm-coding-agent).

## The architecture

```text
Clearbox offer
    ↓
complete export or account API
    ↓
id + kind + exact Reddit permalink
    ↓
local analysis ── optional Freckle / Base Loop / Clay enrichment
    ↓
Google Sheet + guided Notion brief + optional deck
```

There is one Reddit opportunity source in this module: Clearbox. The local market-read path imports a complete Clearbox export through `pull.py`. The client-delivery path reads the account API or an export through `build_client_pack.py`. Neither path posts, votes, sends DMs, or marks opportunities complete.

## Source contract

Every opportunity must retain:

- `id`: the stable Clearbox opportunity identifier
- `kind`: `lead`, `engage`, or `competitor`
- `url` or `permalink`: the exact Reddit source URL

The importer refuses a truncated export, a missing identifier, an invalid disposition, or a missing source URL. The bundled offline fixture follows the same contract. Downstream analysis may add fields, but it may not replace the source disposition or permalink.

## What the modules do

- **`init_db.py`** creates or migrates the local SQLite database without dropping data.
- **`pull.py`** imports a complete Clearbox opportunity export and enforces the source contract.
- **`mine.py`** extracts questions, comparisons, pains, and buyer-language themes from the imported text.
- **`score.py`** scores topics from 1 to 5 on intent, demand, competitive fit, and source engagement.
- **`build_sheet.py`** renders the lower-level market-read Sheet.
- **`build_client_pack.py`** builds the canonical agency delivery: eleven Sheet views plus a guided Notion-ready brief.
- **`build_deck.py`** optionally builds an editable Slides deck from the scored data.

The styling engine is `lib/sheet_engine.py`. The complete module contract is in [ENGINE.md](ENGINE.md).

## Run the synthetic offline path

```bash
git clone https://github.com/shawnla90/ClearboxGTM.git
cd ClearboxGTM/engine
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
bash run.sh --offline
```

The offline run reads every row in `data/clearbox_export.sample.json` so the demo remains stable as the fixture ages. It does not copy over `data/clearbox_export.json` or require access to a live account. Live exports still use the recency window.

## Run from a complete Clearbox export

```bash
cd ClearboxGTM/engine
CLEARBOX_EXPORT=/absolute/path/to/clearbox-opportunities.json bash run.sh
```

The default live path is `data/clearbox_export.json`. `MAX_AGE_DAYS` defaults to 30 for the local market-read pipeline:

```bash
MAX_AGE_DAYS=60 CLEARBOX_EXPORT=/absolute/path/to/export.json bash run.sh
```

Run `python3 setup_oauth.py` once before publishing the Sheet or deck. Rebuilds reuse the stored Sheet and Slides identifiers so shared URLs stay stable.

## Build the eleven-view client pack

Use the focused builder for a real account API or a normalized export:

```bash
export CLEARBOX_ACCOUNT_URL="https://api.clearbox.to/a/YOUR_ACCOUNT_TOKEN"

python3 build_client_pack.py \
  --brand "Acme Corp" \
  --publish-sheet \
  --sheet-id EXISTING_GOOGLE_SHEET_ID \
  --publish-notion \
  --notion-page-id EXISTING_NOTION_PAGE_ID
```

Add optional analysis only after the Clearbox pull:

```bash
python3 build_client_pack.py \
  --brand "Acme Corp" \
  --analysis data/clay-analysis.csv \
  --backend clay \
  --publish-sheet
```

Use `freckle`, `baseloop`, or `clay` as the backend. Omit both analysis arguments to build directly from the Clearbox dispositions. The builder stops on a truncated API response and records disposition conflicts rather than silently accepting them. See [CLIENT-VALUE-PACK.md](../skills/reddit-agency/CLIENT-VALUE-PACK.md) for the eleven views, stable-link refresh pattern, and report automation contract.

## Client-service modules

- **`geo.py`** checks retrieval visibility for buyer questions. Retrieval is not proof that an AI answer named or cited the brand.
- **`competitor.py`** turns Clearbox competitor dispositions and generated sentiment into a narrative view.
- **`digest.py`** renders a daily Slack digest. It posts only with an explicit `--post` flag.
- **`unmask.py`** reviews public company disclosure evidence. Only an exact company domain on the author's own Reddit profile is automatically enrichment-eligible.
- **`content.py`** scaffolds LinkedIn, Reddit, and blog drafts and checks them for structural slop.
- **`sentiment.py`** adds a labeled generated sentiment read.
- **`last24.py`** ranks the most recent imported opportunities.
- **`proposal.py`** creates source-linked pitch materials from the local database.

## Optional downstream services

| Service | Purpose | Boundary |
|---|---|---|
| Clearbox | Opportunity classification and exact source URLs | Authoritative source |
| Freckle / Base Loop / Clay | Additional analysis and enrichment | Cannot replace `kind` or permalink |
| Exa | Retrieval visibility check | Leading indicator, not an AI citation receipt |
| Firecrawl | Website research during onboarding | Not a Reddit opportunity source |
| Apollo / MoltSets | Company and deliverability enrichment | Runs only after the disclosure and review gates |

## Automation boundary

The Clearbox API pull, export import, analysis merge, Sheet rebuild, and Notion refresh may be scheduled. Reddit posting, voting, DMs, and marking opportunities complete remain human-authorized actions.

## Troubleshooting

- **Missing Clearbox export:** set `CLEARBOX_EXPORT` to a complete export or run `bash run.sh --offline`.
- **Truncated response:** do not publish it as a full report. Retrieve the complete inbox first.
- **Invalid `kind` or missing URL:** fix the source export. Do not infer or fabricate the source record.
- **Google token errors:** run `python3 setup_oauth.py`; if the token is revoked, reconnect it.
- **Empty topics:** inspect the imported source text and recency window. Do not substitute an unclassified discovery feed.

---

**Powered by [Clearbox](https://clearbox.to)**. See your market, preserve the source, and move first.
