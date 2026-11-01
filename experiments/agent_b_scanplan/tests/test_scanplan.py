"""Independent contract/negative-control checks for offline ScanPlan."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scanplan.core import IntakeError, build_plan, canonical, parse_input

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "examples" / "demo.json").read_text())

class ScanPlanTests(unittest.TestCase):
    def test_all_kinds_have_positive_negative_and_oracle(self):
        x = build_plan(BASE)
        self.assertEqual(len(x["checks"]), 4)
        for c in x["checks"]:
            self.assertTrue(c["positive_control"] and c["negative_control"] and c["independent_oracle"])
            self.assertEqual((c["execution"], c["result"], c["evidence"]), ("NOT_RUN", "UNKNOWN", "NONE"))
    def test_never_claims_execution_or_authorization(self):
        x = build_plan(BASE)
        self.assertEqual(x["execution_authority"], "UNVERIFIED")
        self.assertEqual(x["release_disposition"], "HOLD")
        self.assertEqual(x["coverage"]["executed"], 0)
    def test_deterministic_output(self):
        self.assertEqual(canonical(build_plan(BASE)), canonical(build_plan(copy.deepcopy(BASE))))
    def test_threat_order_normalized(self):
        x = copy.deepcopy(BASE); x["threats"].reverse()
        self.assertEqual(build_plan(BASE)["checks"], build_plan(x)["checks"])
    def test_unknown_kind_rejected(self):
        x = copy.deepcopy(BASE); x["threats"][0]["kind"] = "remote_shell"
        with self.assertRaises(IntakeError): build_plan(x)
    def test_duplicate_id_rejected(self):
        x = copy.deepcopy(BASE); x["threats"][0]["id"] = x["threats"][1]["id"]
        with self.assertRaises(IntakeError): build_plan(x)
    def test_scope_network_true_rejected(self):
        x = copy.deepcopy(BASE); x["scope"]["network_allowed"] = True
        with self.assertRaises(IntakeError): build_plan(x)
    def test_scope_fixture_false_rejected(self):
        x = copy.deepcopy(BASE); x["scope"]["fixture_only"] = False
        with self.assertRaises(IntakeError): build_plan(x)
    def test_extra_authority_field_rejected(self):
        x = copy.deepcopy(BASE); x["scope"]["is_admin"] = True
        with self.assertRaises(IntakeError): build_plan(x)
    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(IntakeError): parse_input(b'{"version":"0.1.0","version":"0.1.0"}')
    def test_nonfinite_json_rejected(self):
        with self.assertRaises(IntakeError): parse_input(b'{"value":NaN}')
    def test_excessive_size_rejected(self):
        with self.assertRaises(IntakeError): parse_input(b" " * 1048577)
    def test_missing_claim_rejected(self):
        x = copy.deepcopy(BASE); x["threats"][0]["observation"] = ""
        with self.assertRaises(IntakeError): build_plan(x)
    def test_empty_list_rejected(self):
        x = copy.deepcopy(BASE); x["threats"] = []
        with self.assertRaises(IntakeError): build_plan(x)
    def test_cli_stdout_and_new_file(self):
        with tempfile.TemporaryDirectory() as td:
            env = dict(__import__("os").environ, PYTHONPATH=str(ROOT))
            args = [sys.executable, "-m", "scanplan", "plan", str(ROOT / "examples" / "demo.json")]
            p = subprocess.run(args, capture_output=True, env=env)
            self.assertEqual(p.returncode, 0, p.stderr.decode())
            self.assertEqual(json.loads(p.stdout)["coverage"]["planned"], 4)
            out = Path(td) / "out.json"
            p2 = subprocess.run(args + ["--output", str(out)], capture_output=True, env=env)
            self.assertEqual(p2.returncode, 0, p2.stderr.decode())
            self.assertEqual(out.read_bytes(), p.stdout)
            # Existing output may not be silently overwritten.
            p3 = subprocess.run(args + ["--output", str(out)], capture_output=True, env=env)
            self.assertEqual(p3.returncode, 1)
            self.assertEqual(out.read_bytes(), p.stdout)
    def test_cli_does_not_touch_existing_file(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.json"; out.write_text("CANARY")
            env = dict(__import__("os").environ, PYTHONPATH=str(ROOT))
            p = subprocess.run([sys.executable,"-m","scanplan","plan",str(ROOT/"examples"/"demo.json"),"--output",str(out)],capture_output=True,env=env)
            self.assertEqual(p.returncode, 1)
            self.assertEqual(out.read_text(), "CANARY")
    def test_cli_rejects_symlink_input(self):
        with tempfile.TemporaryDirectory() as td:
            inp = Path(td) / "link.json"; inp.symlink_to(ROOT / "examples" / "demo.json")
            env = dict(__import__("os").environ, PYTHONPATH=str(ROOT))
            p = subprocess.run([sys.executable,"-m","scanplan","plan",str(inp)],capture_output=True,env=env)
            self.assertEqual(p.returncode, 1)
    def test_no_network_or_exec_implementation(self):
        import scanplan.core as module
        s = Path(module.__file__).read_text()
        for v in ["subprocess", "socket.", "urllib", "requests", "os.system", "eval("]:
            self.assertNotIn(v, s)

if __name__ == "__main__": unittest.main()
