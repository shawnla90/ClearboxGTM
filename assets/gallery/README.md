# Gallery

Screenshots of real ClearboxGTM outputs, generated from the offline pipeline and public Notion pages.

## Images

### `sheet-scored-signals.png`

The Google Sheet produced by `engine/build_sheet.py` after running the offline pipeline (`bash run.sh --offline`). Shows the Dashboard tab with signal summary, 5 tabs (Dashboard, Content Plan, Buyer Language, Buyer Threads, Scoring Model), and "View only" sharing. Data is from the bundled "Acme PM" sample.

### `notion-multi-account-guide.png`

The public Notion page at `fierce-camelotia-1fa.notion.site`. Shows the multi-account operating guide for agencies running multiple Reddit accounts for clients.

## How these were generated

```bash
# 1. Run the offline pipeline to create the Google Sheet
cd engine && bash run.sh --offline

# 2. Screenshot the sheet (URL from engine/data/sheet_url.txt)
python3 scripts/screenshot.py --url "<sheet_url>" --out assets/gallery/sheet-scored-signals.png --delay 5

# 3. Screenshot the Notion page
python3 scripts/screenshot.py --url "https://fierce-camelotia-1fa.notion.site/..." --out assets/gallery/notion-multi-account-guide.png --full-page
```

Requires `pip install playwright && playwright install chromium`.

## Rules

- No client names, email addresses, or PII in any image
- Filenames are ASCII-only (no emoji, no unicode)
- Every image traces to a reproducible source (offline pipeline or public URL)
