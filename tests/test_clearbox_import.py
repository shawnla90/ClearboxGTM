import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pull = load_module("clearbox_pull", ENGINE / "pull.py")
init_db = load_module("clearbox_init_db", ENGINE / "init_db.py")


class ClearboxImportTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript(init_db.SCHEMA)

    def tearDown(self):
        self.con.close()

    def test_import_preserves_id_disposition_and_exact_url(self):
        row = {
            "id": "op-101",
            "kind": "lead",
            "title": "Need a better workflow",
            "url": "https://www.reddit.com/r/ops/comments/abc/need_a_better_workflow/?context=3",
            "created_utc": 2_000_000_000,
        }
        self.assertEqual(pull._upsert_thread(self.con, row, cutoff=0), 1)
        stored = self.con.execute(
            "SELECT external_id, clearbox_kind, permalink, source_type FROM reddit_threads"
        ).fetchone()
        self.assertEqual(stored, (row["id"], row["kind"], row["url"], "clearbox"))

    def test_relative_permalink_is_normalized_without_losing_path(self):
        row = {
            "id": "op-102",
            "kind": "engage",
            "permalink": "/r/ops/comments/xyz/source_thread/",
            "created_utc": 2_000_000_000,
        }
        pull._upsert_thread(self.con, row, cutoff=0)
        stored = self.con.execute("SELECT permalink FROM reddit_threads").fetchone()[0]
        self.assertEqual(stored, "https://www.reddit.com/r/ops/comments/xyz/source_thread/")

    def test_missing_or_invalid_source_fields_are_rejected(self):
        valid = {
            "id": "op-103",
            "kind": "competitor",
            "url": "https://www.reddit.com/r/ops/comments/def/source_thread/",
        }
        for key, value in (("id", ""), ("kind", "unknown"), ("url", "")):
            with self.subTest(key=key):
                row = dict(valid)
                row[key] = value
                with self.assertRaises(ValueError):
                    pull._upsert_thread(self.con, row, cutoff=0)

    def test_truncated_export_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.json"
            path.write_text(json.dumps({"truncated": True, "opportunities": []}))
            with self.assertRaisesRegex(SystemExit, "truncated"):
                pull._items_from_export(path)

    def test_complete_export_shapes_are_accepted(self):
        row = {
            "id": "op-104",
            "kind": "lead",
            "url": "https://www.reddit.com/r/ops/comments/ghi/source_thread/",
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for index, payload in enumerate(([row], {"opportunities": [row]}, {"rows": [row]})):
                path = tmp_path / f"ops-{index}.json"
                path.write_text(json.dumps(payload))
                self.assertEqual(pull._items_from_export(path), [row])


if __name__ == "__main__":
    unittest.main()
