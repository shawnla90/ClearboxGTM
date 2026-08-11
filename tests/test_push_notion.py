import importlib.util
import os
from pathlib import Path
import unittest


os.environ.setdefault("NOTION_API_TOKEN", "test-token")
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "push_notion.py"
SPEC = importlib.util.spec_from_file_location("push_notion", SCRIPT)
push_notion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(push_notion)


class NotionMarkdownTests(unittest.TestCase):
    def test_toggle_block_keeps_title_and_children(self):
        blocks = push_notion.md_to_blocks(
            "::: toggle Dashboard — the answer first\n"
            "Start here.\n"
            "- Review the recommendation.\n"
            ":::"
        )

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["type"], "toggle")
        self.assertEqual(
            blocks[0]["toggle"]["rich_text"][0]["text"]["content"],
            "Dashboard — the answer first",
        )
        self.assertEqual(
            [child["type"] for child in blocks[0]["toggle"]["children"]],
            ["paragraph", "bulleted_list_item"],
        )


if __name__ == "__main__":
    unittest.main()
