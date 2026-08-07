---
name: geo-visibility
version: 1.0.0
description: Turn an offer pack into a GEO term plan with a live retrieval-visibility score. Wraps engine/geo.py — ranks the buyer questions a brand should own, then checks each top term against an independent Exa search pass to see whether the brand currently surfaces for it. Output is retrieval_visibility, never a citation claim. Use when the user says "/geo-visibility", "run the geo check", "which terms should we own", or "are we showing up for buyer questions".
---

# geo-visibility

Which buyer questions should this brand own, and does it currently surface for them?

Buyers increasingly ask an AI instead of a search box, and AI answers are assembled from what's retrievable. This skill wraps [`engine/geo.py`](../../engine/geo.py): it takes the buyer questions a brand should be the answer to, ranks them by intent, and runs a hard-capped independent retrieval check on the top terms. The output is a plan (terms worth owning, with the buyer evidence behind each) plus a leading indicator (a retrieval-visibility score).

## The language rule (binding)

Results are **`retrieval_visibility`** — the share of checked buyer questions where the brand surfaces in an independent Exa result set. That is a leading indicator, not a citation. **A real citation claim requires the receipt method**: a captured AI answer naming the brand, recorded with its exact source — the format in [`../reddit-agency/AI-VISIBILITY-SCORECARD.csv`](../reddit-agency/AI-VISIBILITY-SCORECARD.csv). Never present a retrieval score as "AI recommends us." See [`../../VERIFYING.md`](../../VERIFYING.md).

## Inputs

The canonical input is the offer pack from [`../clearbox-onboard/`](../clearbox-onboard/) — `clearbox-offer.json` supplies:

- `keywords[]` → the seed buyer language the terms are generated from
- `competitorBrands[]` → the alternative-seeking questions worth owning (`<competitor> alternative` forms)
- `ownBrands[]` → the brand string(s) checked for in the retrieval pass (`--brand`)

Term candidates come from a generated terms file (`--gen`), or fall back to the engine's mined `content_topics` table (`--db`) — real buyer threads, not brainstormed guesses.

## How to run

```bash
python3 engine/geo.py --brand "Acme PM" \
  --gen data/geo_terms_gen.json \
  --db reddit-buyer-signals/data/signals.db \
  --out data/geo_terms.json --check 8
```

Read the module before running it. Read-only except the `--out` file. The Exa pass is hard-capped (`--check`, and `lib/exa_client.MAX_QUERIES` behind it); with no Exa key it degrades gracefully to terms without a live score.

## Output shape

`data/geo_terms.json`:

- `retrieval_visibility_score` — share of checked questions where the brand surfaced (or `null` when Exa is unavailable), with a `note` stating exactly what the score is and is not
- `terms[]` — each with `term`, `intent`, `why_you_own_it`, `buyer_evidence` (a real quote fragment), and `currently_retrieved_by_exa` (`yes` / `no` / `not checked`)

Terms the brand doesn't currently surface for are the content plan: feed them to [`../longtail-content/`](../longtail-content/).

## Rules

1. **Retrieval ≠ citation.** The score never appears in client material without its definition attached.
2. **Terms come from buyer evidence** — generated from real threads or mined topics, never brainstormed into the file.
3. **The check is capped.** Don't loop it to inflate coverage; 8 well-chosen terms tell the story.

## Related

- `../../engine/geo.py` — the module this wraps
- `../../playbooks/offer-context-onboarding.md` — where the input pack comes from
- `../longtail-content/` — what to do with the terms you don't yet surface for
- `../reddit-agency/AI-VISIBILITY-SCORECARD.csv` — the receipt method for real citation claims
