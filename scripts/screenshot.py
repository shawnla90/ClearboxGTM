#!/usr/bin/env python3
"""Headless screenshot of a URL for documentation and proof assets.

Takes --url and --out, waits for the page to settle, and saves a PNG.
Designed for Google Sheets, Notion pages, and any public URL that needs
a visual proof capture for the repo gallery.

Requires: pip install playwright && playwright install chromium

Usage:
  python3 screenshot.py --url "<sheet_url>" --out assets/gallery/sheet.png
  python3 screenshot.py --url "<notion_url>" --out assets/gallery/notion.png --full-page
  python3 screenshot.py --url "<url>" --out <path> --width 1440 --height 900 --wait ".selector"
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright not installed — run: pip install playwright && playwright install chromium")


def capture(url: str, out: Path, width: int, height: int,
            wait_selector: str | None, full_page: bool, delay: float,
            nav_timeout: int = 60_000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url, wait_until="load", timeout=nav_timeout)
        if wait_selector:
            page.wait_for_selector(wait_selector, timeout=30_000)
        if delay > 0:
            time.sleep(delay)
        out.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(out), full_page=full_page)
        browser.close()
    print(f"saved {out} ({out.stat().st_size // 1024} KB)")


def main():
    ap = argparse.ArgumentParser(description="Headless screenshot for documentation")
    ap.add_argument("--url", required=True, help="URL to screenshot")
    ap.add_argument("--out", required=True, help="Output PNG path")
    ap.add_argument("--width", type=int, default=1280, help="Viewport width (default 1280)")
    ap.add_argument("--height", type=int, default=900, help="Viewport height (default 900)")
    ap.add_argument("--wait", dest="wait_selector", help="CSS selector to wait for before capture")
    ap.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    ap.add_argument("--delay", type=float, default=2.0, help="Extra seconds to wait after load (default 2)")
    args = ap.parse_args()
    capture(args.url, Path(args.out), args.width, args.height,
            args.wait_selector, args.full_page, args.delay)


if __name__ == "__main__":
    main()
