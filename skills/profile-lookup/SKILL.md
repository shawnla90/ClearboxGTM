# Profile Lookup

> Version 1.0.0

Given a Reddit username, check whether the person's public presence discloses a company, website, or social profile. The waterfall starts with the person's own Reddit profile — that is where disclosure is most likely — then escalates to web search if the profile does not reveal anything.

## When to use

After classifying opportunities, before enrichment. The disclosure gate in `unmask.py` calls this automatically when you pass `--profile`. Use this skill standalone when you want to check a specific username without running the full pipeline.

## What it checks (in order)

| Tier | Method | Cost | What it finds |
|------|--------|------|---------------|
| 1 | Reddit profile (JSON API) | Free | Bio text, website link, social links in their profile |
| 2 | Exa search | ~$0.01/query | Company blogs, LinkedIn profiles, personal sites tied to the username |
| 3 | DuckDuckGo HTML search | Free | Same signals, coarser results, no API key needed |
| 4 | Playwright browser scrape | Free | Rendered profile page via an existing Chrome session |

The waterfall stops at the first tier that finds a company domain or professional link. Tier 1 (Reddit JSON API) returns 403 since mid-2025 but costs nothing to try. Tier 4 requires Chrome launched with `--remote-debugging-port=9222`.

## What it returns

```json
{
  "disclosed": true,
  "domains": ["mpiresolutions.com"],
  "links": ["https://mpiresolutions.com/blog/..."],
  "bio": "Founder at MPI Resolutions...",
  "source": "exa",
  "signal": "company domain found via web search: mpiresolutions.com"
}
```

When no identity signals are found across all tiers:

```json
{
  "disclosed": false,
  "domains": [],
  "links": [],
  "bio": null,
  "source": "none",
  "signal": "no identity signals found across 4 tiers"
}
```

## How to run

### Standalone CLI

```bash
cd engine
python3 -m lib.profile_lookup twot0n3 Squared_Bear --verbose
```

### As part of the unmask pipeline

```bash
python3 unmask.py --ops data/ops_classified.json --profile --out data/unmasked.json
```

### In your own code

```python
from lib.profile_lookup import lookup_profile

result = lookup_profile("twot0n3")
if result["disclosed"]:
    print(f"Found: {result['domains']} via {result['source']}")
```

## Prerequisites

- `pip install requests` (for tiers 1-3)
- Exa API key in `EXA_API_KEY` env var (for tier 2)
- `pip install playwright && playwright install chromium` (for tier 4, optional)

## What this is and is not

This reads what the author chose to publish — a bio, a website link, a blog post under their username. It does not infer identity from posting patterns, writing style, or timezone analysis. If the person did not leave public breadcrumbs tying their username to a company, the lookup correctly returns `disclosed: false` and the lead stays a Reddit conversation.

## Real test results

Tested against 8 lead usernames from a live client corpus:
- **1 of 8 disclosed** — `twot0n3` → `mpiresolutions.com` via Exa (company blog found linking to the username)
- **7 of 8 genuinely pseudonymous** — no identity signals across any tier
- The in-thread domain scan alone had found **0 of 8** — the profile lookup added one real lead the thread check missed entirely

The 12.5% hit rate on this corpus is higher than the ~1.25% baseline from in-thread scanning alone. The profile lookup catches a different class of disclosure: people who keep their Reddit username separate from their posts but link it to their company elsewhere on the web.
