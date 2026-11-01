"""Narrow evidence-contract verifier for a single Studio pilot; not runtime acceptance."""
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
ID = "0634e209d98fcf29f688f7a294ae73e5cec6b552"
REQUIRED_LIFECYCLE = {"discovery", "requirements", "ux_ui", "architecture", "implementation", "verification", "release", "operations", "maintenance"}
REQUIRED_RISKS = {"severity", "exposure", "reversibility", "data_sensitivity", "privilege", "operational_dependence", "external_side_effects", "novelty", "uncertainty"}


def check(doc):
    errors = []
    if doc.get("report_type") != "UNIVERSAL_PROJECT_ASSESSMENT":
        errors.append("REPORT_MODE_INVALID")
    if doc.get("target", {}).get("relationship") != "temporary_assessment_subject" or doc.get("target", {}).get("permanent_product_link") is not False:
        errors.append("PRODUCT_LINK_FORBIDDEN")
    if doc.get("target", {}).get("commit") != ID:
        errors.append("CANDIDATE_MISMATCH")
    if doc.get("studio", {}).get("selector_generalization") != "NO-GO" or doc.get("studio", {}).get("product_integration") != "NO-GO":
        errors.append("FROZEN_GATE_PROMOTION")
    if set(doc.get("lifecycle", {})) != REQUIRED_LIFECYCLE:
        errors.append("LIFECYCLE_COVERAGE_MISSING")
    if set(doc.get("risk_dimensions", {})) != REQUIRED_RISKS:
        errors.append("RISK_COVERAGE_MISSING")
    evidence = doc.get("evidence", [])
    ids = [r.get("id") for r in evidence]
    if len(ids) != len(set(ids)) or any(not r.get("source") for r in evidence):
        errors.append("EVIDENCE_ID_OR_SOURCE_MISSING")
    valid_ids = set(ids)
    for e in evidence:
        if e.get("kind") == "CI_METADATA":
            if e.get("head_sha") != ID:
                errors.append("CI_CANDIDATE_MISMATCH")
            if e.get("executed_steps") == 0 and e.get("status") in {"PASS", "FAIL"}:
                errors.append("UNEXECUTED_CI_MISATTRIBUTION")
    for v in doc.get("verification", []):
        if v.get("status") in {"PASS", "FAIL"} and not v.get("executed"):
            errors.append("UNEXECUTED_VERIFICATION_MISATTRIBUTION")
        if any(ref not in valid_ids for ref in v.get("evidence_refs", [])):
            errors.append("DANGLING_VERIFICATION_EVIDENCE")
        if v.get("status") == "PASS" and not v.get("evidence_refs"):
            errors.append("PASS_WITHOUT_EVIDENCE")
    for t in doc.get("tasks", []):
        if any(ref not in valid_ids and not any(x.get("id") == ref for x in doc.get("tasks", [])) for ref in t.get("requires", [])):
            errors.append("DANGLING_TASK_INPUT")
        if t.get("state") == "ACCEPTED" and doc.get("execution_authority") != "VERIFIED":
            errors.append("ACCEPTANCE_WITHOUT_AUTHORITY")
    if doc.get("decision") == "GO" and (doc.get("execution_authority") != "VERIFIED" or any(v.get("status") != "PASS" for v in doc.get("verification", []))):
        errors.append("UNSUPPORTED_GO")
    return sorted(set(errors))


class PilotControls(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / "pilot.json").read_text(encoding="utf-8"))

    def test_valid_scoped_pilot(self):
        self.assertEqual(check(self.doc), [])

    def test_mapping_only_report_refused(self):
        d = copy.deepcopy(self.doc)
        d["report_type"] = "CROSS_PROJECT_MAPPING"
        self.assertIn("REPORT_MODE_INVALID", check(d))

    def test_unexecuted_ci_cannot_fail_code(self):
        d = copy.deepcopy(self.doc)
        next(x for x in d["evidence"] if x["id"] == "E4")["status"] = "FAIL"
        self.assertIn("UNEXECUTED_CI_MISATTRIBUTION", check(d))

    def test_false_verification_pass_refused(self):
        d = copy.deepcopy(self.doc)
        next(x for x in d["verification"] if x["id"] == "V2")["status"] = "PASS"
        self.assertIn("UNEXECUTED_VERIFICATION_MISATTRIBUTION", check(d))

    def test_product_link_refused(self):
        d = copy.deepcopy(self.doc)
        d["target"]["permanent_product_link"] = True
        self.assertIn("PRODUCT_LINK_FORBIDDEN", check(d))

    def test_release_claim_refused(self):
        d = copy.deepcopy(self.doc)
        d["decision"] = "GO"
        self.assertIn("UNSUPPORTED_GO", check(d))

    def test_stale_candidate_refused(self):
        d = copy.deepcopy(self.doc)
        d["target"]["commit"] = "0" * 40
        self.assertIn("CANDIDATE_MISMATCH", check(d))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        errors = check(json.loads((ROOT / "pilot.json").read_text(encoding="utf-8")))
        print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors}))
        sys.exit(bool(errors))
    unittest.main()