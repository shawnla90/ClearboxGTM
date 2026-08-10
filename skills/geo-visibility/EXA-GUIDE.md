# Exa retrieval guide

A practical guide to the Exa integration behind the geo-visibility skill.

## What Exa does here

The geo-visibility skill uses Exa's `/search` endpoint to check whether a brand surfaces when a buyer asks a question. Exa returns an independent search result set -- not an AI-generated answer. The skill scans those results for the brand name (case-insensitive) and reports whether it appeared.

This is **retrieval visibility**: a leading indicator that the brand is findable for a buyer question. It does not prove that ChatGPT, Claude, Perplexity, or Google named or cited the brand. That requires a receipt -- a captured AI answer with the exact source. See the receipt method in [`../reddit-agency/AI-VISIBILITY-SCORECARD.csv`](../reddit-agency/AI-VISIBILITY-SCORECARD.csv).

## API key setup

1. Sign up at [exa.ai](https://exa.ai)
2. Set `EXA_API_KEY` in your environment:
   ```bash
   export EXA_API_KEY=your_key_here
   ```
3. Optional: store in a secrets database (a sqlite file with a `secrets(key, value)` table) and set `SECRETS_DB` to its path. The client checks `EXA_API_KEY` first, then falls back to the database.
4. Without a key, the skill degrades gracefully -- terms are listed without a live retrieval score. No error, no crash.

## Query construction for buyer questions

Queries should be buyer questions, not keywords. The client wraps each query in an Exa `/search` call with `type: "auto"` and `numResults: 10`, requesting `highlights` in the response.

Good queries:
```
"best project management tool for small teams"
"frustrated with Monday.com what should I use"
"Asana vs Notion for engineering teams"
```

Bad queries:
```
"CRM"
"project management"
"SaaS tools"
```

The difference: a buyer question captures intent. A keyword captures a category. The retrieval check matters when it answers "does this brand show up when a real buyer asks a real question?" not "does this brand rank for a head term?"

Term candidates come from two sources:
- A generated terms file (`--gen`) produced upstream from buyer language analysis
- Fallback: the engine's mined `content_topics` table (`--db`), which contains real buyer threads, not brainstormed guesses

## Interpreting retrieval results

The output (`data/geo_terms.json`) contains:

- `retrieval_visibility_score` -- percentage of checked queries where the brand surfaced (integer 0-100), or `null` when Exa is unavailable
- `note` -- a plain-language statement of what the score is and is not
- `terms[]` -- each term with:
  - `term` -- the buyer question
  - `intent` -- high / mid / low
  - `why_you_own_it` -- why this brand should be the answer
  - `buyer_evidence` -- a real quote fragment from a Reddit thread
  - `currently_retrieved_by_exa` -- `"yes"` / `"no"` / `"not checked"`

What "appears" means: the brand name (case-insensitive string match) was found somewhere in the JSON of Exa search results for that query. It is a substring check, not a ranking signal.

Terms where the brand does not currently surface are the content plan: feed them to [`../longtail-content/`](../longtail-content/).

## The hard cap

`MAX_QUERIES` defaults to 8. Override with env var `EXA_MAX_QUERIES`. The cap exists to protect the API balance. A caller cannot exceed it even by passing more queries -- the client deduplicates and truncates to the cap before making any API call.

8 well-chosen terms tell the story. More queries burn the balance without changing the signal.

## The critical distinction

Retrieval visibility is a leading indicator. It shows the brand surfaces in Exa's index for a buyer question. It does **not** prove that an AI answer engine named or cited the brand. That requires a receipt: a captured AI answer with the brand named, recorded with its exact source. See the receipt method in [`../reddit-agency/AI-VISIBILITY-SCORECARD.csv`](../reddit-agency/AI-VISIBILITY-SCORECARD.csv).

## Other enrichment tools

Exa is one of several optional APIs in the pipeline. Each checks a different dimension:

- **Exa** checks retrieval visibility: does this brand surface when a buyer asks a question? Leading indicator for AI answer engines.
- **Firecrawl** checks technical visibility: can crawlers read the site? Structured site extraction (homepage, pricing, docs into markdown) and SEO audit in one call. Set `FIRECRAWL_API_KEY` in your environment to enable it.
- **With both**: retrieval visibility (is the AI finding you?) + technical visibility (can the AI read you?) = the full picture of whether a brand is positioned to be cited.
- **Without either**: terms are still listed from buyer language analysis, just without live scores. The content plan is still usable — you just verify visibility manually.

The pattern is the same across every API in this repo: set the key, get the enrichment. Skip the key, get the plan without the score. See the full comparison table in [`../../engine/README.md`](../../engine/README.md) under "Enrichment APIs."

## Related

- [`../../engine/lib/exa_client.py`](../../engine/lib/exa_client.py) -- the implementation (72 lines)
- [`../../engine/geo.py`](../../engine/geo.py) -- the module that calls exa_client
- [`SKILL.md`](SKILL.md) -- the skill this guide extends
- [`../../VERIFYING.md`](../../VERIFYING.md) -- the language rules (retrieval != citation)
