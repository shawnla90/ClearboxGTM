import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


replies = load_module("clearbox_replies", ENGINE / "replies.py")


OPS = [
    {"op_id": "op_1", "lane": "engage_now", "subreddit": "projectmanagement", "summary": "Asana vs Monday"},
    {"op_id": "op_2", "lane": "lead_enrich", "subreddit": "sales", "summary": "follow-up falling through"},
    {"op_id": "op_3", "lane": "competitor_intel", "subreddit": "saas", "summary": "RivalPM shipped dashboards"},
    {"op_id": "op_4", "lane": "reply_now", "subreddit": "startups", "summary": "tool feedback thread"},
]


def contract(replies_map, overrides=None):
    return {"rules": replies.DEFAULT_RULES, "replies": replies_map, "gate_overrides": overrides or {}}


class GateTests(unittest.TestCase):
    def test_lane_mapping_both_vocabularies(self):
        cases = {
            "engage_now": "GO", "reply_now": "GO",
            "competitor_intel": "NO-REPLY", "competitor_watch": "NO-REPLY",
            "lead_enrich": "REVIEW", "lead_review": "REVIEW",
            "engage_selective": "REVIEW", "": "REVIEW", "unknown_lane": "REVIEW",
        }
        for lane, want in cases.items():
            gate, note = replies.gate_for({"op_id": "x", "lane": lane}, {})
            self.assertEqual(gate, want, lane)
            self.assertTrue(note)

    def test_action_lane_field_accepted(self):
        gate, _ = replies.gate_for({"op_id": "x", "action_lane": "competitor_watch"}, {})
        self.assertEqual(gate, "NO-REPLY")

    def test_override_beats_lane(self):
        ov = {"op_1": ["NO-REPLY", "Founder self-promo. Flag for partnership outreach instead."]}
        gate, note = replies.gate_for(OPS[0], ov)
        self.assertEqual(gate, "NO-REPLY")
        self.assertIn("partnership", note)

    def test_invalid_override_gate_raises(self):
        with self.assertRaises(ValueError):
            replies.gate_for(OPS[0], {"op_1": ["MAYBE", "note"]})

    def test_malformed_override_shape_raises_not_crashes(self):
        for bad in ({"gate": "GO"}, "GO", []):
            with self.assertRaises(ValueError):
                replies.gate_for(OPS[0], {"op_1": bad})


class WordCountTests(unittest.TestCase):
    def assert_matches_wc(self, text):
        wc = int(subprocess.run(["wc", "-w"], input=text, capture_output=True, text=True).stdout.split()[0])
        self.assertEqual(replies.word_count(text), wc, repr(text))

    def test_matches_wc_w(self):
        for text in [
            "one two  three",
            "punctuation-attached words, still two",
            "Un solo tablero, no cinco chats.",
            "  leading and trailing  ",
        ]:
            self.assert_matches_wc(text)


class CheckTests(unittest.TestCase):
    def flags(self, replies_map, overrides=None, ops=OPS):
        return replies.check_contract(contract(replies_map, overrides), ops, replies.MAX_WORDS)

    def test_eighteen_words_pass_nineteen_fail(self):
        ok18 = " ".join(["word"] * 18)
        bad19 = " ".join(["word"] * 19)
        base = {"op_2": "Assign every follow-up one owner and one date.", "op_4": ok18}
        self.assertEqual(self.flags({**base, "op_1": ok18}), [])
        flagged = self.flags({**base, "op_1": bad19})
        self.assertTrue(any("19/18" in fl for _, fl in flagged))

    def test_link_fails(self):
        flagged = self.flags({"op_1": "See https://example.com for the answer.",
                              "op_2": "x", "op_4": "x"})
        self.assertTrue(any("link in reply" in fl for _, fl in flagged))

    def test_reply_on_noreply_op_fails(self):
        flagged = self.flags({"op_1": "x", "op_2": "x", "op_3": "A perfectly good reply.", "op_4": "x"})
        self.assertTrue(any(oid == "op_3" and "NO-REPLY" in fl for oid, fl in flagged))

    def test_banned_word_fails_via_shared_slop_gate(self):
        flagged = self.flags({"op_1": "This is a game-changer for your team.", "op_2": "x", "op_4": "x"})
        self.assertTrue(any("game-changer" in fl for _, fl in flagged))

    def test_empty_slot_fails(self):
        flagged = self.flags({"op_1": "", "op_2": "x", "op_4": "x"})
        self.assertTrue(any("empty" in fl for _, fl in flagged))

    def test_op_missing_from_replies_fails(self):
        flagged = self.flags({"op_1": "x", "op_2": "x"})  # op_4 (reply_now) has no slot at all
        self.assertTrue(any(oid == "op_4" and "no reply slot" in fl for oid, fl in flagged))

    def test_malformed_override_flags_without_crash(self):
        flagged = self.flags({"op_1": "x", "op_2": "x", "op_4": "x"},
                             overrides={"op_1": {"gate": "GO"}})
        self.assertTrue(any(oid == "op_1" for oid, fl in flagged))


class ScaffoldTests(unittest.TestCase):
    def test_slots_only_for_gated_in_ops(self):
        with tempfile.TemporaryDirectory() as td:
            ops_path = Path(td) / "ops.json"
            out_path = Path(td) / "suggested_replies.json"
            ops_path.write_text(json.dumps(OPS))
            args = type("A", (), {"ops": str(ops_path), "out": str(out_path), "force": False})
            self.assertEqual(replies.scaffold(args), 0)
            data = json.loads(out_path.read_text())
            self.assertEqual(sorted(data["replies"]), ["op_1", "op_2", "op_4"])
            self.assertEqual(data["rules"], replies.DEFAULT_RULES)
            self.assertEqual(data["gate_overrides"], {})

    def test_refuses_to_overwrite_drafts_without_force(self):
        with tempfile.TemporaryDirectory() as td:
            ops_path = Path(td) / "ops.json"
            out_path = Path(td) / "suggested_replies.json"
            ops_path.write_text(json.dumps(OPS))
            out_path.write_text(json.dumps(contract({"op_1": "A drafted reply survives."})))
            args = type("A", (), {"ops": str(ops_path), "out": str(out_path), "force": False})
            self.assertEqual(replies.scaffold(args), 1)
            self.assertIn("drafted reply survives", out_path.read_text())


class AnglesTests(unittest.TestCase):
    def test_digest_compatible_output(self):
        with tempfile.TemporaryDirectory() as td:
            ops_path = Path(td) / "ops.json"
            rep_path = Path(td) / "replies.json"
            out_path = Path(td) / "angles.json"
            ops_path.write_text(json.dumps(OPS))
            rep_path.write_text(json.dumps(contract(
                {"op_1": "A drafted GO reply.", "op_2": "A drafted REVIEW reply.", "op_4": ""},
                overrides={"op_4": ["NO-REPLY", "Founder self-promo. Log it."]},
            )))
            args = type("A", (), {"ops": str(ops_path), "replies": str(rep_path),
                                  "out": str(out_path), "max_words": replies.MAX_WORDS})
            self.assertEqual(replies.angles(args), 0)
            data = json.loads(out_path.read_text())
            self.assertIsInstance(data, list)
            by_id = {a["op_id"]: a for a in data}
            self.assertEqual(by_id["op_1"]["priority"], "high")
            self.assertEqual(by_id["op_2"]["priority"], "med")
            self.assertNotIn("op_3", by_id)  # NO-REPLY lane skipped
            self.assertNotIn("op_4", by_id)  # overridden to NO-REPLY, empty slot skipped
            for a in data:  # exactly the digest.py loader shape
                self.assertEqual(sorted(a), ["angle", "op_id", "priority"])

    def test_angles_refuses_unchecked_contract(self):
        with tempfile.TemporaryDirectory() as td:
            ops_path = Path(td) / "ops.json"
            rep_path = Path(td) / "replies.json"
            out_path = Path(td) / "angles.json"
            ops_path.write_text(json.dumps(OPS))
            rep_path.write_text(json.dumps(contract({
                "op_1": " ".join(["word"] * 19), "op_2": "x", "op_4": "x",
            })))
            args = type("A", (), {"ops": str(ops_path), "replies": str(rep_path),
                                  "out": str(out_path), "max_words": replies.MAX_WORDS})
            self.assertEqual(replies.angles(args), 1)
            self.assertFalse(out_path.exists())


class SheetValuesTests(unittest.TestCase):
    def test_rules_header_and_gate_sort(self):
        values = replies.sheet_values(OPS, contract({"op_1": "r1", "op_2": "r2", "op_4": "r4"}))
        self.assertEqual(values[0][0], replies.DEFAULT_RULES)
        self.assertEqual(values[1], replies.HEADERS)
        gates = [row[3] for row in values[2:]]
        self.assertEqual(gates, sorted(gates, key=lambda g: {"GO": 0, "REVIEW": 1, "NO-REPLY": 2}[g]))


if __name__ == "__main__":
    unittest.main()
