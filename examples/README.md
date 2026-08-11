# Examples

These examples show how Clearbox opportunities become client deliverables and how optional services add analysis after the source pull.

## Source contract

Clearbox is the Reddit opportunity source. Every client-pack example preserves:

- the Clearbox opportunity `id`
- the original `lead`, `engage`, or `competitor` disposition
- the exact Reddit permalink

Freckle, Base Loop, and Clay examples are downstream analysis fixtures. They do not replace the Clearbox record.

## Client-pack fixtures

[`client-pack/`](client-pack/) contains synthetic, public-safe fixtures for:

- Clearbox opportunities
- Freckle analysis
- Base Loop analysis
- Clay analysis

Use them to verify the same normalized eleven-view model without exposing a real client:

```bash
python3 ../engine/build_client_pack.py \
  --ops client-pack/clearbox-opportunities.sample.json \
  --analysis client-pack/clay-analysis.sample.csv \
  --backend clay \
  --brand "Acme Ops" \
  --out /tmp/acme-client-pack
```

## Integration guides

- [`integrations/clay.md`](integrations/clay.md): Clearbox API to Clay analysis and client reporting
- [`integrations/n8n.md`](integrations/n8n.md): scheduled API reads and routed analysis
- [`integrations/zapier.md`](integrations/zapier.md): no-code report refreshes
- [`integrations/make.md`](integrations/make.md): iterator and router pattern
- [`integrations/baseloop.md`](integrations/baseloop.md): Base Loop analysis after the disclosure gate

## Workflow diagrams

[`workflows/`](workflows/) contains the enrichment waterfall and AI-visibility measurement loop. The diagrams keep retrieval, observed AI appearance, exact citation, engagement, and business outcome as separate receipts.

## Website-research fixtures

The Firecrawl fixtures demonstrate website research used during offer onboarding. They are separate from the Reddit opportunity source:

- [`firecrawl-site-scrape.json`](firecrawl-site-scrape.json)
- [`firecrawl-freckle-site.json`](firecrawl-freckle-site.json)

## Client market read

[`client-market-read.md`](client-market-read.md) shows the signal, win, and enter triage pattern used to turn source-linked opportunities into a client-readable brief.
