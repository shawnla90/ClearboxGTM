# Enrichment waterfall

The full path from a classified Clearbox op to a sequence-ready contact. Every step is optional and degrades gracefully — the waterfall runs whatever stages have API keys configured and skips the rest.

## The flow

```mermaid
graph TD
  A[Clearbox inbox<br/>classified ops] --> B{Kind?}
  B -->|lead| C[Disclosure gate<br/>unmask.py]
  B -->|engage| D[Reply queue<br/>human drafts reply]
  B -->|competitor| E[Competitor intel<br/>share of voice]
  C -->|direct Reddit-profile disclosure| F[Freckle workflow<br/>company + ICP + contacts]
  C -->|search/thread/handle candidate| P[Manual review]
  C -->|no public evidence| D
  C -->|lookup error| Q[Retry queue]
  F --> G{Has LinkedIn URL?}
  G -->|yes| H[Apollo: people/match<br/>email + title + seniority]
  G -->|no| I[Apollo: org search<br/>find people at company]
  H --> J[MoltSets: email grade<br/>A through F]
  I --> J
  J --> K{Grade?}
  K -->|A or B| L[T1_send<br/>sequence-ready]
  K -->|C| M[T2_catchall<br/>review queue]
  K -->|D or F| N[SUPPRESS<br/>bad deliverability]
  L --> O[CRM + sequence]
  M --> P[Manual review sheet]
```

## What each step does

| Step | Tool | Input | Output | Without it |
|------|------|-------|--------|-----------|
| Classify | Clearbox | Subreddit config | Ops with `kind` and `summary` | Use RapidAPI keyword matching (noisier) |
| Disclosure gate | `unmask.py` | Reddit profile evidence + op text | Verdict, eligibility, evidence URL, candidate domain | No enrichment path |
| Company enrich | Freckle CLI | Domain | Company name, ICP tier, contacts | Swap for Clay or Apollo org search |
| People match | Apollo API | LinkedIn URL or company name | Email, title, seniority | No email enrichment |
| Email grade | MoltSets API | Email address | Grade A-F, catchall flag | Send without grading |
| Classify result | `coverage_waterfall.py` | Email + grade + domain | T1/T2/HOLD/SUPPRESS | Manual review of every lead |

## The disclosure gate

The gate is the critical step. It runs before any enrichment and separates four states:

1. **Direct disclosure** — a company domain appears on the author's own Reddit profile, with the exact profile URL and excerpt
2. **Plausible candidate** — search, thread-domain, or brand-handle evidence needs human verification
3. **No public evidence** — a Reddit-profile check completed without a match
4. **Lookup error** — no Reddit-profile check completed and the lookup must be retried

Only the first state is eligible for automatic company enrichment. Candidates stay in manual review; absence stays a Reddit conversation; errors stay unknown.

## The pluggable seam

The `enrich_domain()` function in `engine/unmask.py` is the one function to swap. Replace it with:

- **Clay** — HTTP Request to a Clay table that returns enrichment
- **Apollo** — Direct API call to `people/match` or `organizations/enrich`
- **Your own waterfall** — Any sequence of enrichment calls

The gate stays the same regardless of the enrichment backend.

## Related

- [`../../engine/unmask.py`](../../engine/unmask.py) — the review gate and pluggable enrichment seam
- [`../../playbooks/orchestrate-freckle.md`](../../playbooks/orchestrate-freckle.md) — the full pipeline
- [`../integrations/clay.md`](../integrations/clay.md) — Clay HTTP column integration
- [`../integrations/n8n.md`](../integrations/n8n.md) — n8n flow with enrichment branch
