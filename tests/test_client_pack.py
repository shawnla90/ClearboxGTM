import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
import sys

sys.path.insert(0, str(ENGINE))

from lib.client_pack import (  # noqa: E402
    TAB_GUIDANCE,
    build_pack,
    load_payload,
    merge_rows,
    normalize_analysis,
    normalize_clearbox,
    render_notion_markdown,
)
from lib.sheet_engine import client_dashboard  # noqa: E402

BUILDER_SPEC = importlib.util.spec_from_file_location("client_pack_builder", ENGINE / "build_client_pack.py")
client_pack_builder = importlib.util.module_from_spec(BUILDER_SPEC)
BUILDER_SPEC.loader.exec_module(client_pack_builder)


FIXTURES = ROOT / "examples" / "client-pack"


class ClientPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = load_payload(FIXTURES / "clearbox-opportunities.sample.json")
        cls.clearbox_rows, cls.api_meta = normalize_clearbox(payload)

    def test_clearbox_dispositions_and_permalinks_are_source_record(self):
        self.assertEqual(
            [row["source_disposition"] for row in self.clearbox_rows],
            ["lead", "engage", "competitor"],
        )
        self.assertTrue(all(row["source_url"].startswith("https://www.reddit.com/") for row in self.clearbox_rows))

    def test_each_backend_normalizes_to_same_pack_contract(self):
        files = {
            "freckle": "freckle-analysis.sample.json",
            "baseloop": "baseloop-analysis.sample.json",
            "clay": "clay-analysis.sample.csv",
        }
        for backend, filename in files.items():
            with self.subTest(backend=backend):
                analysis = normalize_analysis(load_payload(FIXTURES / filename), backend)
                rows, meta = merge_rows(self.clearbox_rows, analysis)
                pack = build_pack("Acme Ops", rows, api_meta=self.api_meta, merge_meta=meta)
                self.assertEqual(pack["metrics"]["dispositions"], {"lead": 1, "engage": 1, "competitor": 1})
                self.assertEqual(pack["metrics"]["matched_analysis_rows"], 3)
                self.assertEqual(pack["metrics"]["disposition_conflicts"], 0)
                self.assertEqual({row["analysis_backend"] for row in rows}, {backend})
                self.assertEqual(rows[0]["tier"], "A")

    def test_analysis_cannot_replace_clearbox_disposition(self):
        payload = load_payload(FIXTURES / "freckle-analysis.sample.json")
        changed = copy.deepcopy(payload)
        changed[0]["kind"] = "engage"
        rows, meta = merge_rows(self.clearbox_rows, normalize_analysis(changed, "freckle"))
        by_id = {row["op_id"]: row for row in rows}
        self.assertEqual(by_id["101"]["source_disposition"], "lead")
        self.assertTrue(by_id["101"]["disposition_conflict"])
        self.assertEqual(meta["disposition_conflicts"], 1)

    def test_pack_contains_eleven_guided_views(self):
        rows, meta = merge_rows(
            self.clearbox_rows,
            normalize_analysis(load_payload(FIXTURES / "clay-analysis.sample.csv"), "clay"),
        )
        pack = build_pack("Acme Ops", rows, api_meta=self.api_meta, merge_meta=meta)
        self.assertEqual([title for title, _subtitle, _description in TAB_GUIDANCE], [
            "Dashboard", "Plan Setup", "Operator Console", "Signals", "Buyer Language", "Content Topics",
            "Competitor Sentiment", "GEO Terms", "Disclosure Audit", "Research Workflow", "Action Legend",
        ])
        self.assertEqual(list(pack["tabs"]), [
            "Plan Setup", "Operator Console", "Signals", "Buyer Language", "Content Topics",
            "Competitor Sentiment", "GEO Terms", "Disclosure Audit", "Research Workflow", "Action Legend",
        ])
        self.assertIn("exact_reddit_artifact_cited", pack["tabs"]["GEO Terms"][0])
        self.assertIn("qualified_conversations", pack["tabs"]["GEO Terms"][0])

        config = client_pack_builder.sheet_config(pack, "stable-sheet-id", False)
        dashboard = config["dashboard"]
        self.assertEqual(dashboard["layout"], "client_pack")
        self.assertEqual(len(dashboard["cards"]), 4)
        self.assertEqual([card["value"] for card in dashboard["cards"]], [3, 1, 1, 1])
        self.assertEqual(dashboard["priority"][0]["value"], 2)
        self.assertEqual(dashboard["priority"][1]["value"], "3 OF 3")
        self.assertEqual([card["value"] for card in dashboard["workflow"]], [
            "CLEARBOX", "CLAY", "HUMAN QUEUE", "SHEET + NOTION",
        ])
        self.assertEqual([card["value"] for card in dashboard["evidence"]], [
            "EXACT URL", "QUERY RECEIPT", "CAPTURED PROOF", "SOURCE-LINKED",
        ])

        class FakeWorksheet:
            id = 77

            def __init__(self, title):
                self.title = title
                self.rows = []

            def append_rows(self, rows, value_input_option):
                self.rows = rows
                self.value_input_option = value_input_option

        class FakeSpreadsheet:
            def add_worksheet(self, title, rows, cols):
                self.shape = (rows, cols)
                self.worksheet = FakeWorksheet(title)
                return self.worksheet

        fake_sheet = FakeSpreadsheet()
        requests = []
        rendered = client_dashboard(fake_sheet, requests, dashboard)
        self.assertEqual(rendered.title, "Dashboard")
        self.assertEqual(fake_sheet.shape, (33, 12))
        self.assertEqual(len(rendered.rows), 29)
        self.assertTrue(all(len(row) == 12 for row in rendered.rows))
        self.assertEqual(rendered.rows[6][0], "3")
        self.assertEqual(rendered.rows[11][4], "3 OF 3")
        self.assertGreater(len(requests), 100)
        self.assertTrue(any(
            request.get("updateSheetProperties", {}).get("properties", {}).get("gridProperties", {}).get("hideGridlines")
            for request in requests
        ))
        sheet_titles = [config["dashboard"]["title"]] + [tab["title"] for tab in config["tabs"]] + [tab["title"] for tab in config["raw_tabs"]]
        self.assertEqual(sheet_titles, [title for title, _subtitle, _description in TAB_GUIDANCE])
        plan_setup = next(tab for tab in config["tabs"] if tab["title"] == "Plan Setup")
        operator_console = next(tab for tab in config["tabs"] if tab["title"] == "Operator Console")
        self.assertEqual(len(plan_setup["validations"]), 3)
        self.assertEqual(operator_console["validations"][0]["col"], "review_status")

    def test_api_pull_is_read_only_inbox_get(self):
        payload = json.loads((FIXTURES / "clearbox-opportunities.sample.json").read_text())

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps(payload).encode()

        captured = {}

        def fake_urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return Response()

        with patch.object(client_pack_builder.urllib.request, "urlopen", side_effect=fake_urlopen):
            result = client_pack_builder.pull_account("https://api.clearbox.to/a/sample-token", "all")

        request = captured["request"]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url, "https://api.clearbox.to/a/sample-token/inbox?status=all")
        self.assertIn("Mozilla/5.0", request.get_header("User-agent"))
        self.assertEqual(result["counts"]["total"], 3)

    def test_notion_brief_is_guided_and_client_safe(self):
        rows, meta = merge_rows(
            self.clearbox_rows,
            normalize_analysis(load_payload(FIXTURES / "baseloop-analysis.sample.json"), "baseloop"),
        )
        pack = build_pack("Acme Ops", rows, api_meta=self.api_meta, merge_meta=meta)
        markdown = render_notion_markdown(pack, "https://docs.google.com/spreadsheets/d/sample/edit")
        for expected in (
            "What Acme Ops has now",
            "Highest-priority opportunities to review",
            "::: toggle Plan Setup",
            "How the automated workflow works",
            "Freckle, Base Loop, or Clay",
            "partners@clearbox.to",
            "Exact citation",
        ):
            self.assertIn(expected, markdown)
        for forbidden in (
            "Stripe customer",
            "workflow_run_id",
            "workspace_id",
            "Freckle workbook",
            "Base Loop workspace link",
        ):
            self.assertNotIn(forbidden, markdown)


if __name__ == "__main__":
    unittest.main()
