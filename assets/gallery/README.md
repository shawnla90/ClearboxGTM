# Gallery

Real ClearboxGTM outputs generated from the synthetic Acme Ops fixture pack. The current showcase represents the eleven-view API-to-client-pack workflow, not the older five-tab offline sheet.

- [View-only Google Sheet](https://docs.google.com/spreadsheets/d/100Q4e8ZW6xIHHk4GHzFO7ONmK_1MdNhBPi0Y4TngWjc)
- [Public guided Notion brief](https://fierce-camelotia-1fa.notion.site/ClearboxGTM-Client-Value-Pack-Demo-Acme-Ops-3b91fb92bcd7818ca3dad03e0e21cbd0)

## Images

### `client-pack-tour.gif`, `client-pack-tour.mp4`, and `client-pack-tour-poster.png`

The short end-to-end README walkthrough. It uses only the verified captures below and the checked-in HyperFrames composition at `videos/client-value-pack-tour/`.

### `client-pack-sheet.png` and `client-pack-dashboard.png`

The public view-only Acme Ops Sheet open on the redesigned Clearbox dashboard. `client-pack-sheet.png` keeps the browser and eleven visible tabs; `client-pack-dashboard.png` is a clean export of the dashboard itself.

### `client-pack-plan-setup.png`

The client-facing selections for offer path, who pays, and readiness.

### `client-pack-operator-console.png`

The ranked working queue. It preserves the original Clearbox disposition and uses a separate human review state.

### `client-pack-geo-terms.png`

The measurement surface. Exact Reddit source URLs remain visible while search discovery, observed AI answer, exact citation, referral, pipeline, and revenue fields stay separate.

### `client-pack-notion.png`

The public guided Notion brief that explains the value, Sheet views, plan decision, workflow, evidence ladder, and next working session.

### Legacy reference captures

`sheet-scored-signals.png` and `notion-multi-account-guide.png` document the earlier offline five-tab sheet and standalone multi-account guide. They remain for release history but are no longer the README showcase.

## How these were generated

```bash
# 1. Build and publish a sanitized fixture pack
python3 engine/build_client_pack.py \
  --ops examples/client-pack/clearbox-opportunities.sample.json \
  --analysis examples/client-pack/clay-analysis.sample.csv \
  --backend clay --brand "Acme Ops" --publish-sheet --share-sheet

# 2. Capture the Sheet and its working views
python3 scripts/screenshot.py --url "<sheet_url>" \
  --out assets/gallery/client-pack-sheet.png --width 1600 --height 1000 --delay 8

# 3. Publish the generated client_brief.md under the public demo parent, then capture it
python3 scripts/screenshot.py --url "https://fierce-camelotia-1fa.notion.site/..." \
  --out assets/gallery/client-pack-notion.png --width 1440 --height 1000 --delay 8

# 4. Re-render the motion asset
(cd videos/client-value-pack-tour && npm run check && npm run render)
```

Requires `pip install playwright && playwright install chromium`.

## Rules

- No client names, email addresses, or PII in any image
- Filenames are ASCII-only (no emoji, no unicode)
- Every image traces to a reproducible source (offline pipeline or public URL)
- The walkthrough may reframe or animate a verified capture; it may not invent interface states
