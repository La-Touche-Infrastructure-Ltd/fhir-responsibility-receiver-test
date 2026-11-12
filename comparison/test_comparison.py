#!/usr/bin/env python3
"""Small synthetic regression suite; not independent or profile validation."""
import copy
import json
import unittest
from pathlib import Path
from build_parent_child import ROOT, OUT
from compare_receivers import inspect

POLICIES = json.loads((ROOT / "receiver-policy.json").read_text())["cases"]
def sample(case):
    return json.loads((OUT / (case + ".json")).read_text())

class ParentChildComparisonTests(unittest.TestCase):
    def test_all_baseline_states_preserved(self):
        baseline = json.loads((ROOT / "results.json").read_text())
        for case, policy in POLICIES.items():
            with self.subTest(case=case):
                self.assertEqual(inspect(sample(case), policy)["receiver_state"],
                                 baseline[case]["receiver_state"])

    def test_known_missing_report_not_overridden_by_completed_parent(self):
        result = inspect(sample("case1_missing_B"), POLICIES["case1_missing_B"])
        self.assertEqual(result["parent_task_status"], "completed")
        self.assertEqual(result["receiver_state"], "INSUFFICIENT_REPORT_EVIDENCE")

    def test_unknown_outer_scope_remains_indeterminate(self):
        result = inspect(sample("case3_only_A_known"), POLICIES["case3_only_A_known"])
        self.assertEqual(result["receiver_state"], "ALL_KNOWN_REPORTS_PRESENT_SCOPE_UNKNOWN")

    def test_group_id_does_not_prove_exhaustive_expected_set(self):
        policy = dict(POLICIES["case2_both_received"], expected_scope_authoritative=False)
        result = inspect(sample("case2_both_received"), policy)
        self.assertEqual(result["receiver_state"], "ALL_KNOWN_REPORTS_PRESENT_SCOPE_UNKNOWN")
        self.assertFalse(result["overall_request_completeness_proven_from_fhir_grouping_alone"])

    def test_missing_child_for_known_order_must_not_be_inferred_complete(self):
        bundle = sample("case2_both_received")
        child = next(e for e in bundle["entry"] if e["resource"]["resourceType"] == "Task"
                     and e["resource"].get("focus") and
                     "case2_both_received-B" in
                     next(r["resource"]["identifier"][0]["value"]
                          for r in bundle["entry"] if r["fullUrl"] ==
                          e["resource"]["focus"]["reference"]))
        bundle["entry"].remove(child)
        result = inspect(bundle, POLICIES["case2_both_received"])
        self.assertEqual(result["receiver_state"], "INSUFFICIENT_REPORT_EVIDENCE")
        self.assertIn("case2_both_received-B",
                      result["request_ids_without_visible_child_task"])

    def test_missing_report_for_known_order_must_not_be_inferred_complete(self):
        bundle = sample("case2_both_received")
        bundle["entry"] = [e for e in bundle["entry"]
                           if not (e["resource"]["resourceType"] == "DiagnosticReport" and
                                   "B" in e["resource"]["identifier"][0]["value"].split("-")[-1])]
        result = inspect(bundle, POLICIES["case2_both_received"])
        self.assertEqual(result["receiver_state"], "INSUFFICIENT_REPORT_EVIDENCE")

    def test_nonfinal_report_not_sufficient(self):
        bundle = sample("case2_both_received")
        for entry in bundle["entry"]:
            if entry["resource"]["resourceType"] == "DiagnosticReport":
                entry["resource"]["status"] = "preliminary"
                break
        result = inspect(bundle, POLICIES["case2_both_received"])
        self.assertEqual(result["receiver_state"], "INSUFFICIENT_REPORT_EVIDENCE")

    def test_one_child_task_focus_per_visible_service_request(self):
        for case in POLICIES:
            with self.subTest(case=case):
                bundle = sample(case)
                requests = [e["fullUrl"] for e in bundle["entry"]
                            if e["resource"]["resourceType"] == "ServiceRequest"]
                child_focus = [e["resource"]["focus"]["reference"] for e in bundle["entry"]
                               if e["resource"]["resourceType"] == "Task" and
                               e["resource"].get("partOf")]
                self.assertCountEqual(requests, child_focus)

if __name__ == "__main__":
    unittest.main(verbosity=2)
