#!/usr/bin/env python3
"""proof-sheet engine - parameterized gspread color-coded Google Sheet builder.

Canonical home for the "Duve-style" interactive proof sheet that Shawn ships:
score gradient (red→yellow→green), categorical TEXT_EQ color maps, banding,
frozen headers, basic filters, sized columns, a styled dashboard, and
anyone-with-link sharing - rebuildable IN PLACE by sheet-id so a linked doc
stays valid.

This module is pure (no file I/O, no argv): callers pass pandas DataFrames + a
config dict and get back (url, tab_titles). Projects vendor a copy into
scripts/lib/sheet_engine.py and write a thin per-project builder that loads the
data, defines the config, and calls build(). See SKILL.md for the config schema.
"""
from pathlib import Path

import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread

DEFAULT_TOKEN = Path.home() / ".config" / "gspread" / "token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# shared palette (hex without #)
NAVY = "1F3A56"
GREEN = "57BB8A"
GREEN_DK = "16653A"
GREEN_LT = "B7E1CD"
BLUE = "C9DAF8"
YELLOW = "FCE8B2"
AMBER = "FFF2CC"
GREY = "EFEFEF"
GREY_LT = "F3F3F3"
ORANGE = "FCE5CD"
RED = "E67C73"

# Clearbox client-pack palette. The generic sheet builder above intentionally
# keeps its original navy/green treatment for backwards compatibility; the
# eleven-view client dashboard uses the public Clearbox dark/purple system.
CLEARBOX_INK = "0D0D12"
CLEARBOX_CARD = "17171F"
CLEARBOX_CARD_ALT = "201C30"
CLEARBOX_PURPLE = "6D5EE9"
CLEARBOX_PURPLE_LT = "D8D3FF"
CLEARBOX_WHITE = "FFFFFF"
CLEARBOX_MUTED = "AAA7B4"
CLEARBOX_LINE = "35313F"


def rgb(h: str) -> dict:
    h = h.lstrip("#")
    return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}


def num(v):
    try:
        f = float(v)
        return int(f) if f == int(f) else f
    except (ValueError, TypeError):
        return None


def creds(token=DEFAULT_TOKEN):
    c = Credentials.from_authorized_user_file(str(token), SCOPES)
    if not c.valid:
        c.refresh(Request())
        Path(token).write_text(c.to_json())
    return c


# ── request builders (semantics proven on the Duve build) ──
def r_header(sid, ncols):
    return [{"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": ncols},
             "cell": {"userEnteredFormat": {"backgroundColor": rgb(NAVY),
                      "textFormat": {"foregroundColor": rgb("FFFFFF"), "bold": True, "fontSize": 10},
                      "verticalAlignment": "MIDDLE"}},
             "fields": "userEnteredFormat(backgroundColor,textFormat,verticalAlignment)"}},
            {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}}]


def r_band(sid, nrows, ncols):
    return {"addBanding": {"bandedRange": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": nrows, "startColumnIndex": 0, "endColumnIndex": ncols},
            "rowProperties": {"headerColor": rgb(NAVY), "firstBandColor": rgb("FFFFFF"), "secondBandColor": rgb("EEF3F8")}}}}


def r_filter(sid, nrows, ncols):
    return {"setBasicFilter": {"filter": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": nrows, "startColumnIndex": 0, "endColumnIndex": ncols}}}}


def r_width(sid, col, px):
    return {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": col, "endIndex": col + 1}, "properties": {"pixelSize": px}, "fields": "pixelSize"}}


def r_validation(sid, start_row, end_row, start_col, end_col, values):
    """Dropdown validation request. Row/column indexes are zero-based and end-exclusive."""
    return {"setDataValidation": {
        "range": {"sheetId": sid, "startRowIndex": start_row, "endRowIndex": end_row,
                  "startColumnIndex": start_col, "endColumnIndex": end_col},
        "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
            {"userEnteredValue": str(value)} for value in values
        ]}, "strict": True, "showCustomUi": True},
    }}


def cf_text(sid, col, nrows, value, color):
    return {"addConditionalFormatRule": {"rule": {"ranges": [{"sheetId": sid, "startRowIndex": 1, "endRowIndex": nrows, "startColumnIndex": col, "endColumnIndex": col + 1}],
            "booleanRule": {"condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": value}]}, "format": {"backgroundColor": rgb(color)}}}, "index": 0}}


def cf_grad(sid, col, nrows, stops=(1, 3, 5)):
    lo, mid, hi = stops
    return {"addConditionalFormatRule": {"rule": {"ranges": [{"sheetId": sid, "startRowIndex": 1, "endRowIndex": nrows, "startColumnIndex": col, "endColumnIndex": col + 1}],
            "gradientRule": {"minpoint": {"color": rgb(RED), "type": "NUMBER", "value": str(lo)},
                             "midpoint": {"color": rgb("FFD666"), "type": "NUMBER", "value": str(mid)},
                             "maxpoint": {"color": rgb(GREEN), "type": "NUMBER", "value": str(hi)}}}, "index": 0}}


def _values(df, cols, numeric):
    out = [cols]
    for _, r in df.iterrows():
        row = []
        for c in cols:
            v = r.get(c, "")
            if c in numeric:
                n = num(v)
                row.append(n if n is not None else "")
            else:
                s = str(v)
                row.append("'" + s if s.startswith("=") else s)
        out.append(row)
    return out


def data_tab(sh, reqs, title, df, cols, widths, cf, numeric, validations=None):
    ws = sh.add_worksheet(title=title, rows=len(df) + 10, cols=len(cols) + 2)
    ws.append_rows(_values(df, cols, numeric), value_input_option="USER_ENTERED")
    sid, nrows, ncols = ws.id, len(df) + 1, len(cols)
    reqs += r_header(sid, ncols)
    reqs.append(r_band(sid, nrows, ncols))
    reqs.append(r_filter(sid, nrows, ncols))
    for cname, px in widths.items():
        if cname in cols:
            reqs.append(r_width(sid, cols.index(cname), px))
    for spec in cf:
        if spec["col"] not in cols:
            continue
        col = cols.index(spec["col"])
        if spec["type"] == "grad":
            reqs.append(cf_grad(sid, col, nrows, spec.get("stops", (1, 3, 5))))
        else:
            for val, color in spec["map"].items():
                reqs.append(cf_text(sid, col, nrows, val, color))
    for spec in validations or []:
        if spec.get("col") not in cols:
            continue
        col = cols.index(spec["col"])
        start_row = int(spec.get("start_row", 1))
        end_row = int(spec.get("end_row", nrows))
        reqs.append(r_validation(sid, start_row, end_row, col, col + 1, spec["values"]))
    return ws


def raw_tab(sh, reqs, title, values, widths=None, header=True):
    """A simple value grid (scoring model, manifest, import log). values = list of rows."""
    ws = sh.add_worksheet(title=title, rows=len(values) + 6, cols=max(len(r) for r in values) + 1)
    ws.append_rows(values, value_input_option="USER_ENTERED")
    if header:
        reqs += r_header(ws.id, len(values[0]))
    for col, px in (widths or {}).items():
        reqs.append(r_width(ws.id, col, px))
    return ws


def _sheet_range(sid, start_row, end_row, start_col, end_col):
    return {
        "sheetId": sid,
        "startRowIndex": start_row,
        "endRowIndex": end_row,
        "startColumnIndex": start_col,
        "endColumnIndex": end_col,
    }


def _merge(reqs, sid, row, start_col, end_col):
    reqs.append({"mergeCells": {
        "range": _sheet_range(sid, row, row + 1, start_col, end_col),
        "mergeType": "MERGE_ALL",
    }})


def _format(reqs, sid, start_row, end_row, start_col, end_col, fmt, fields=None):
    reqs.append({"repeatCell": {
        "range": _sheet_range(sid, start_row, end_row, start_col, end_col),
        "cell": {"userEnteredFormat": fmt},
        "fields": fields or "userEnteredFormat",
    }})


def _row_height(reqs, sid, start_row, end_row, px):
    reqs.append({"updateDimensionProperties": {
        "range": {
            "sheetId": sid,
            "dimension": "ROWS",
            "startIndex": start_row,
            "endIndex": end_row,
        },
        "properties": {"pixelSize": px},
        "fields": "pixelSize",
    }})


def client_dashboard(sh, reqs, spec):
    """Render the dense, branded dashboard used by the eleven-view client pack.

    The values are deliberately supplied through ``spec`` so this visual layer
    remains reusable and testable. It reports the evidence ladder without ever
    turning search retrieval or an uncaptured AI answer into a claimed result.
    """
    rows, cols = 29, 12
    values = [["" for _ in range(cols)] for _ in range(rows)]

    def put(row, col, value):
        values[row][col] = str(value)

    subtitle = spec.get("subtitle", {})
    put(0, 0, subtitle.get("title", "CLIENT VALUE PACK"))
    put(1, 0, subtitle.get("sub", "Clearbox dispositions, exact Reddit permalinks, and a human-controlled working queue"))
    put(2, 0, subtitle.get("eyebrow", "11 WORKING VIEWS  •  SOURCE-LINKED  •  BUILT FOR CLIENT DELIVERY"))

    section_rows = {
        4: "CURRENT VALUE",
        9: "PRIORITY & COVERAGE",
        14: "FROM SIGNAL TO RECEIPT",
        19: "MEASUREMENT EVIDENCE LADDER",
        24: "WHAT TO DO NEXT",
    }
    for row, label in section_rows.items():
        put(row, 0, label)

    cards = list(spec.get("cards", []))[:4]
    while len(cards) < 4:
        cards.append({"label": "", "value": "", "note": ""})
    for i, card in enumerate(cards):
        col = i * 3
        put(5, col, card.get("label", ""))
        put(6, col, card.get("value", ""))
        put(7, col, card.get("note", ""))

    priority = list(spec.get("priority", []))[:3]
    while len(priority) < 3:
        priority.append({"label": "", "value": "", "note": ""})
    for i, card in enumerate(priority):
        col = i * 4
        put(10, col, card.get("label", ""))
        put(11, col, card.get("value", ""))
        put(12, col, card.get("note", ""))

    workflow = list(spec.get("workflow", []))[:4]
    while len(workflow) < 4:
        workflow.append({"label": "", "value": "", "note": ""})
    for i, card in enumerate(workflow):
        col = i * 3
        put(15, col, card.get("label", ""))
        put(16, col, card.get("value", ""))
        put(17, col, card.get("note", ""))

    evidence = list(spec.get("evidence", []))[:4]
    while len(evidence) < 4:
        evidence.append({"label": "", "value": "", "note": ""})
    for i, card in enumerate(evidence):
        col = i * 3
        put(20, col, card.get("label", ""))
        put(21, col, card.get("value", ""))
        put(22, col, card.get("note", ""))

    start = spec.get("start", {})
    put(25, 0, start.get("left_title", "START HERE"))
    put(26, 0, start.get("left_primary", "1  Choose the offer path in Plan Setup"))
    put(27, 0, start.get("left_secondary", "2  Work Tier A rows in Operator Console"))
    put(28, 0, start.get("left_note", "Human review remains the publishing gate."))
    put(25, 6, start.get("right_title", "OPEN THESE VIEWS"))
    put(26, 6, start.get("right_primary", "Plan Setup  →  Operator Console  →  Signals"))
    put(27, 6, start.get("right_secondary", "GEO Terms  →  Disclosure Audit  →  Action Legend"))
    put(28, 6, start.get("right_note", "The exact Reddit permalink stays attached to every working row."))

    ws = sh.add_worksheet(title=spec["title"], rows=rows + 4, cols=cols)
    ws.append_rows(values, value_input_option="USER_ENTERED")
    sid = ws.id

    reqs.append({"updateSheetProperties": {
        "properties": {
            "sheetId": sid,
            "gridProperties": {"hideGridlines": True, "frozenRowCount": 3},
        },
        "fields": "gridProperties(hideGridlines,frozenRowCount)",
    }})
    for col in range(cols):
        reqs.append(r_width(sid, col, 116 if col not in {0, 11} else 126))

    _format(reqs, sid, 0, rows, 0, cols, {
        "backgroundColor": rgb(CLEARBOX_INK),
        "textFormat": {"foregroundColor": rgb(CLEARBOX_WHITE), "fontFamily": "Arial"},
        "verticalAlignment": "MIDDLE",
    })

    for row in (0, 1, 2, *section_rows.keys()):
        _merge(reqs, sid, row, 0, cols)

    _format(reqs, sid, 0, 1, 0, cols, {
        "backgroundColor": rgb(CLEARBOX_INK),
        "textFormat": {"foregroundColor": rgb(CLEARBOX_WHITE), "bold": True, "fontSize": 20},
        "horizontalAlignment": "LEFT",
        "verticalAlignment": "MIDDLE",
        "padding": {"left": 18},
    })
    _format(reqs, sid, 1, 2, 0, cols, {
        "backgroundColor": rgb(CLEARBOX_INK),
        "textFormat": {"foregroundColor": rgb(CLEARBOX_PURPLE_LT), "fontSize": 11},
        "padding": {"left": 18},
    })
    _format(reqs, sid, 2, 3, 0, cols, {
        "backgroundColor": rgb(CLEARBOX_PURPLE),
        "textFormat": {"foregroundColor": rgb(CLEARBOX_WHITE), "bold": True, "fontSize": 9},
        "padding": {"left": 18},
    })
    for row in section_rows:
        _format(reqs, sid, row, row + 1, 0, cols, {
            "backgroundColor": rgb(CLEARBOX_INK),
            "textFormat": {"foregroundColor": rgb(CLEARBOX_PURPLE_LT), "bold": True, "fontSize": 10},
            "padding": {"left": 2},
        })

    border = {
        edge: {"style": "SOLID", "color": rgb(CLEARBOX_LINE)}
        for edge in ("top", "bottom", "left", "right")
    }

    def style_cards(start_row, count, span, value_size=20, alternate=False):
        for i in range(count):
            c0, c1 = i * span, (i + 1) * span
            for row in range(start_row, start_row + 3):
                _merge(reqs, sid, row, c0, c1)
            bg = CLEARBOX_CARD_ALT if alternate and i % 2 else CLEARBOX_CARD
            _format(reqs, sid, start_row, start_row + 3, c0, c1, {
                "backgroundColor": rgb(bg),
                "borders": border,
                "verticalAlignment": "MIDDLE",
                "wrapStrategy": "WRAP",
                "padding": {"left": 12, "right": 10},
            })
            _format(reqs, sid, start_row, start_row + 1, c0, c1, {
                "textFormat": {"foregroundColor": rgb(CLEARBOX_MUTED), "bold": True, "fontSize": 9},
                "padding": {"left": 12},
            }, "userEnteredFormat(textFormat,padding)")
            _format(reqs, sid, start_row + 1, start_row + 2, c0, c1, {
                "textFormat": {"foregroundColor": rgb(CLEARBOX_WHITE), "bold": True, "fontSize": value_size},
                "horizontalAlignment": "LEFT",
                "padding": {"left": 12},
            }, "userEnteredFormat(textFormat,horizontalAlignment,padding)")
            _format(reqs, sid, start_row + 2, start_row + 3, c0, c1, {
                "textFormat": {"foregroundColor": rgb(CLEARBOX_MUTED), "fontSize": 9},
                "padding": {"left": 12, "right": 10},
            }, "userEnteredFormat(textFormat,padding)")

    style_cards(5, 4, 3, value_size=22)
    style_cards(10, 3, 4, value_size=16, alternate=True)
    style_cards(15, 4, 3, value_size=12, alternate=True)
    style_cards(20, 4, 3, value_size=12)

    for c0, c1 in ((0, 6), (6, 12)):
        for row in range(25, 29):
            _merge(reqs, sid, row, c0, c1)
        _format(reqs, sid, 25, 29, c0, c1, {
            "backgroundColor": rgb(CLEARBOX_CARD_ALT if c0 == 0 else CLEARBOX_CARD),
            "borders": border,
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",
            "padding": {"left": 14, "right": 12},
        })
        _format(reqs, sid, 25, 26, c0, c1, {
            "textFormat": {"foregroundColor": rgb(CLEARBOX_PURPLE_LT), "bold": True, "fontSize": 10},
            "padding": {"left": 14},
        }, "userEnteredFormat(textFormat,padding)")
        _format(reqs, sid, 26, 28, c0, c1, {
            "textFormat": {"foregroundColor": rgb(CLEARBOX_WHITE), "bold": True, "fontSize": 11},
            "padding": {"left": 14, "right": 12},
        }, "userEnteredFormat(textFormat,padding)")
        _format(reqs, sid, 28, 29, c0, c1, {
            "textFormat": {"foregroundColor": rgb(CLEARBOX_MUTED), "italic": True, "fontSize": 9},
            "padding": {"left": 14, "right": 12},
        }, "userEnteredFormat(textFormat,padding)")

    for row, height in {
        0: 46, 1: 30, 2: 24, 3: 14,
        4: 26, 5: 24, 6: 42, 7: 38, 8: 14,
        9: 26, 10: 24, 11: 34, 12: 38, 13: 14,
        14: 26, 15: 24, 16: 32, 17: 42, 18: 14,
        19: 26, 20: 24, 21: 32, 22: 42, 23: 14,
        24: 26, 25: 26, 26: 32, 27: 32, 28: 38,
    }.items():
        _row_height(reqs, sid, row, row + 1, height)
    return ws


def dashboard(sh, reqs, title, subtitle, entries):
    """entries: list of {kind, label, value?}. kind ∈ section|kpi|bullet|link|note|blank."""
    rows, sections, kpis, bullets = [], [], [], []
    for e in entries:
        rows.append([e.get("label", ""), e.get("value", "")])
        i = len(rows) - 1
        k = e.get("kind", "kpi")
        if k == "section":
            sections.append(i)
        elif k == "kpi" and str(e.get("value", "")) != "":
            kpis.append(i)
        elif k == "bullet":
            bullets.append(i)

    ws = sh.add_worksheet(title=title, rows=len(rows) + 8, cols=4)
    # title + subtitle occupy the first two rows above the entries
    head = [[subtitle.get("title", ""), ""], [subtitle.get("sub", ""), ""]]
    ws.append_rows(head + rows, value_input_option="USER_ENTERED")
    sid = ws.id
    reqs.append(r_width(sid, 0, 430))
    reqs.append(r_width(sid, 1, 360))
    reqs.append({"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
    reqs.append({"mergeCells": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 4}, "mergeType": "MERGE_ALL"}})
    reqs.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 4},
                 "cell": {"userEnteredFormat": {"backgroundColor": rgb(NAVY), "textFormat": {"foregroundColor": rgb("FFFFFF"), "bold": True, "fontSize": 16}, "horizontalAlignment": "LEFT", "padding": {"left": 10}}},
                 "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,padding)"}})
    reqs.append({"mergeCells": {"range": {"sheetId": sid, "startRowIndex": 1, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 4}, "mergeType": "MERGE_ALL"}})
    reqs.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 1, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 4},
                 "cell": {"userEnteredFormat": {"textFormat": {"foregroundColor": rgb("5B6B7B"), "italic": True}}}, "fields": "userEnteredFormat(textFormat)"}})
    off = 2  # entries start after title+subtitle
    for i in sections:
        reqs.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": i + off, "endRowIndex": i + off + 1, "startColumnIndex": 0, "endColumnIndex": 4},
                     "cell": {"userEnteredFormat": {"backgroundColor": rgb("DCE6F1"), "textFormat": {"bold": True, "fontSize": 11, "foregroundColor": rgb(NAVY)}}},
                     "fields": "userEnteredFormat(backgroundColor,textFormat)"}})
    for i in kpis:
        reqs.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": i + off, "endRowIndex": i + off + 1, "startColumnIndex": 1, "endColumnIndex": 2},
                     "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": rgb(GREEN_DK)}, "horizontalAlignment": "LEFT"}},
                     "fields": "userEnteredFormat(textFormat,horizontalAlignment)"}})
    for i in bullets:
        reqs.append({"mergeCells": {"range": {"sheetId": sid, "startRowIndex": i + off, "endRowIndex": i + off + 1, "startColumnIndex": 0, "endColumnIndex": 4}, "mergeType": "MERGE_ALL"}})
        reqs.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": i + off, "endRowIndex": i + off + 1, "startColumnIndex": 0, "endColumnIndex": 4},
                     "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "textFormat": {"fontSize": 10}}}, "fields": "userEnteredFormat(wrapStrategy,textFormat)"}})
    return ws


def build(config: dict):
    """Build/rebuild a sheet from a config dict. Returns (url, [tab_titles]).

    config keys:
      title    : sheet name (used only when creating fresh)
      key      : existing sheet id to rebuild IN PLACE, or None to create new
      token    : gspread OAuth token path (default ~/.config/gspread/token.json)
      share    : "anyone_reader" to share a freshly created sheet, else None
      dashboard: {title, subtitle:{title,sub}, entries:[{kind,label,value}]}  (optional)
      tabs     : [{title, df, cols, widths?, cf?, numeric?, validations?}]    data tabs
      raw_tabs : [{title, values, widths?, header?}]                         simple grids
    """
    gc = gspread.authorize(creds(config.get("token", DEFAULT_TOKEN)))
    key = config.get("key")
    sh = gc.open_by_key(key) if key else gc.create(config["title"])
    # Clear pre-existing tabs BEFORE adding new ones so titles don't collide on an
    # in-place rebuild. A throwaway placeholder keeps the sheet non-empty (the API
    # forbids deleting the last sheet); it's dropped once the new tabs exist.
    existing = sh.worksheets()
    placeholder = sh.add_worksheet(title="_rebuilding_", rows=1, cols=1)
    for ws in existing:
        sh.del_worksheet(ws)

    reqs: list = []
    if config.get("dashboard"):
        d = config["dashboard"]
        if d.get("layout") == "client_pack":
            client_dashboard(sh, reqs, d)
        else:
            dashboard(sh, reqs, d["title"], d.get("subtitle", {}), d["entries"])
    for t in config.get("tabs", []):
        data_tab(sh, reqs, t["title"], t["df"], t["cols"], t.get("widths", {}), t.get("cf", []),
                 set(t.get("numeric", [])), t.get("validations", []))
    for rt in config.get("raw_tabs", []):
        raw_tab(sh, reqs, rt["title"], rt["values"], rt.get("widths", {}), rt.get("header", True))

    if reqs:
        sh.batch_update({"requests": reqs})
    sh.del_worksheet(placeholder)
    if not key and config.get("share") == "anyone_reader":
        sh.share(None, perm_type="anyone", role="reader")
    return sh.url, [w.title for w in sh.worksheets()]
