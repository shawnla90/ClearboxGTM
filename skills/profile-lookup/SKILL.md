# Profile Lookup

> Version 1.1.0

Given a Reddit username, check for an exact company disclosure on the author's own Reddit profile, then collect search-only candidates for human review. The profile is evidence. A search result is only a lead to verify.

## When to use

After classifying opportunities, before enrichment. The disclosure gate in `unmask.py` calls this automatically when you pass `--profile`. Use this skill standalone when you want to check a specific username without running the full pipeline.

## What it checks (in order)

| Tier | Method | Cost | What it finds |
|------|--------|------|---------------|
| 1 | Reddit profile (JSON API) | Free | Company domain as direct disclosure; social link without a company domain as a candidate |
| 2 | Exa search | ~$0.01/query | Possible company pages tied to the username, manual review only |
| 3 | DuckDuckGo HTML search | Free | Possible company pages tied to the username, manual review only |
| 4 | Playwright browser scrape | Free | Same profile rule against the rendered page |

The waterfall returns immediately on direct Reddit-profile evidence. Search candidates are retained while later profile tiers are checked. A blocked or unavailable tier is an error, not proof that no evidence exists. Tier 4 can reuse Chrome launched with `--remote-debugging-port=9222`.

## What it returns

```json
{
  "disclosed": true,
  "lookup_status": "self_disclosed",
  "review_verdict": "direct_disclosure",
  "enrichment_eligibility": "eligible_direct_disclosure",
  "domains": ["acme.com"],
  "source": "reddit_json",
  "evidence": [{
    "url": "https://www.reddit.com/user/acme_author/",
    "kind": "reddit_profile",
    "excerpt": "I run acme.com"
  }]
}
```

A web-search match stays out of enrichment:

```json
{
  "disclosed": false,
  "lookup_status": "candidate_found",
  "review_verdict": "plausible_candidate",
  "enrichment_eligibility": "manual_review",
  "domains": ["possible-company.com"],
  "source": "exa",
  "evidence": [{
    "url": "https://possible-company.com/team/acme_author",
    "kind": "web_search_candidate"
  }]
}
```

The other terminal states are `no_public_evidence`, used only when a Reddit-profile tier completed without a match, and `lookup_error`, used when no profile tier completed. Do not turn a successful search with no match into a negative profile finding when Reddit itself could not be checked.

## How to run

### Standalone CLI

```bash
cd engine
python3 -m lib.profile_lookup example_author another_author --verbose
```

### As part of the unmask pipeline

```bash
python3 unmask.py --ops data/ops_classified.json --profile --out data/unmasked.json
```

### In your own code

```python
from lib.profile_lookup import lookup_profile

result = lookup_profile("example_author")
if result["enrichment_eligibility"] == "eligible_direct_disclosure":
    print(f"Found: {result['domains']} via {result['source']}")
elif result["review_verdict"] == "plausible_candidate":
    print("Manual review required")
```

## Prerequisites

- `pip install requests` (for tiers 1-3)
- Exa API key in `EXA_API_KEY` env var (for tier 2)
- `pip install playwright && playwright install chromium` (for tier 4, optional)

## What this is and is not

This reads exact profile evidence and gathers search candidates. It does not infer identity from posting patterns, writing style, or timezone analysis. It never treats a search result, a domain mentioned in a thread, or a brand-like handle as direct disclosure. Those states require human verification and remain in the Reddit conversation queue.

## Decision rule

- `direct_disclosure` plus an exact Reddit-profile evidence URL and company domain: enrichment eligible.
- `plausible_candidate`: manual review only; never passed to enrichment automatically.
- `no_public_evidence`: a Reddit-profile tier completed without a match.
- `lookup_error`: no Reddit-profile tier completed; retry rather than report a negative.
