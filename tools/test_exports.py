"""Export compatibility checks; run with python3 -m unittest discover -s tools -p 'test_*.py'."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import openpyxl

import possibilities


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.output = Path(self.scratch.name) / "result"
        self.doc = {
            "name": "export-check", "request": {"requirement": "Inspect a construction."},
            "sheets": [
                {"name": "Steps", "header_row": 3, "columns": possibilities.STEP_COLS,
                 "rows": [{"Step ID": "S-0001", "Depth": 0, "Kind": "Construction",
                           "Name": "Example", "State": "Decision"}]},
                {"name": "Links", "header_row": 3, "columns": possibilities.LINK_COLS, "rows": []},
                {"name": "Routes", "header_row": 3, "columns": possibilities.ROUTE_COLS, "rows": []},
            ],
        }

    def assert_workbook(self):
        workbook = openpyxl.load_workbook(self.output / "possibilities.xlsx")
        self.addCleanup(workbook.close)
        self.assertEqual(workbook.sheetnames, ["Steps", "Links", "Routes"])
        self.assertEqual(workbook["Steps"]["A4"].value, "S-0001")
        self.assertEqual(workbook["Steps"]["E4"].value, "Example")
        self.assertEqual(workbook["Steps"]["F4"].value, "Decision")
        self.assertEqual(workbook["Steps"].freeze_panes, "C4")

    def test_default_delivery_still_has_workbook_json_and_summary(self):
        original = copy.deepcopy(self.doc)
        possibilities.write(self.doc, self.output)
        self.assertEqual(json.loads((self.output / "possibilities.json").read_text()), original)
        self.assertEqual(self.doc, original)
        self.assert_workbook()
        self.assertIn("possibilities.xlsx (one tab per sheet, for reading)", (self.output / "summary.md").read_text())

    def test_json_only_refresh_removes_stale_workbook_and_retains_routes(self):
        self.output.mkdir()
        (self.output / "possibilities.xlsx").write_bytes(b"old export")
        (self.output / "routes.json").write_text("[]\n")
        possibilities.write(self.doc, self.output, xlsx=False)
        self.assertFalse((self.output / "possibilities.xlsx").exists())
        self.assertEqual((self.output / "routes.json").read_text(), "[]\n")
        self.assertEqual(json.loads((self.output / "possibilities.json").read_text()), self.doc)
        self.assertNotIn("possibilities.xlsx (", (self.output / "summary.md").read_text())

    def test_later_export_preserves_canonical_json_and_composed_routes(self):
        possibilities.write(self.doc, self.output, xlsx=False)
        (self.output / "routes.json").write_text("[]\n")
        before = {name: (self.output / name).read_bytes() for name in ("possibilities.json", "routes.json")}
        self.assertIsNone(possibilities.main(["export-xlsx", str(self.output)]))
        self.assert_workbook()
        for name, data in before.items():
            self.assertEqual((self.output / name).read_bytes(), data)
        self.assertIn("possibilities.xlsx (", (self.output / "summary.md").read_text())

    def test_json_only_cli_works_without_third_party_packages(self):
        source = Path(possibilities.__file__).resolve()
        request = Path(self.scratch.name) / "request.json"
        request.write_text(json.dumps({"name": "stdlib", "requirement": "Inspect decision content.",
                                      "anchors": {"states": ["Decision"], "audiences": ["Prospect buyer"]}}))
        done = subprocess.run([sys.executable, "-S", str(source), "resolve", str(request),
                               "--out", str(self.output), "--no-xlsx"], text=True, capture_output=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertFalse((self.output / "possibilities.xlsx").exists())
        result = json.loads((self.output / "possibilities.json").read_text())
        self.assertGreater(len(possibilities.sheet(result, "Steps")["rows"]), 0)
        self.assertEqual((self.output / "request.json").read_bytes(), request.read_bytes())

    def test_invalid_route_keeps_failure_exit_and_finding_without_workbook(self):
        possibilities.write(self.doc, self.output, xlsx=False)
        (self.output / "routes.json").write_text(json.dumps([{"id": "R-unknown", "steps": ["S-999999"]}]))
        self.assertEqual(possibilities.main(["check", str(self.output), "--no-xlsx"]), 1)
        result = json.loads((self.output / "possibilities.json").read_text())
        self.assertEqual(possibilities.sheet(result, "Routes")["rows"][0]["Check"], "unknown Step ID")
        self.assertFalse((self.output / "possibilities.xlsx").exists())


if __name__ == "__main__":
    unittest.main()
