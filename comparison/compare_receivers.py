#!/usr/bin/env python3
"""Source-bounded receiver comparison for the FHIR-native Task hierarchy.
Does not infer request completeness from grouping or parent Task status.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent

def inspect(bundle, policy):
    entries = bundle["entry"]
    resources = {e["fullUrl"]: e["resource"] for e in entries}
    task_entries = [(u, r) for u, r in resources.items() if r["resourceType"] == "Task"]
    parent_candidates = [(u, r) for u, r in task_entries if not r.get("partOf")]
    assert len(parent_candidates) == 1
    parent_url, parent = parent_candidates[0]
    children = [(u, r) for u, r in task_entries
                if any(ref["reference"] == parent_url for ref in r.get("partOf", []))]
    requests = {u: r for u, r in resources.items() if r["resourceType"] == "ServiceRequest"}
    reports = {u: r for u, r in resources.items() if r["resourceType"] == "DiagnosticReport"}
    by_id = {}
    for url, req in requests.items():
        identifier = req["identifier"][0]["value"]
        assert identifier not in by_id
        by_id[identifier] = url

    expected = set(policy["expected_service_requests"])
    assert expected
    report_supported = set()
    task_evidenced = set()
    for request_id in expected:
        if request_id not in by_id:
            continue
        request_url = by_id[request_id]
        request_children = [(u, task) for u, task in children
                            if task.get("focus", {}).get("reference") == request_url]
        if not request_children:
            continue
        task_evidenced.add(request_id)
        for _, task in request_children:
            outputs = {o["valueReference"]["reference"] for o in task.get("output", [])
                       if "valueReference" in o}
            if any(url in outputs and report["status"] == "final"
                   and any(link["reference"] == request_url
                           for link in report.get("basedOn", []))
                   for url, report in reports.items()):
                report_supported.add(request_id)

    not_evidenced = expected - report_supported
    if not_evidenced:
        state = "INSUFFICIENT_REPORT_EVIDENCE"
    elif policy["expected_scope_authoritative"]:
        state = "ALL_AGREED_EXPECTED_REPORTS_PRESENT_IN_SNAPSHOT"
    else:
        state = "ALL_KNOWN_REPORTS_PRESENT_SCOPE_UNKNOWN"

    # Without an attested complete expectation set, a grouped identifier and an
    # aggregate Task cannot establish that no unseen requests or children exist.
    visible_request_ids = set(by_id)
    visible_without_reports = visible_request_ids - report_supported
    fhir_observation = (
        "VISIBLE_REQUESTS_WITHOUT_MATCHED_FINAL_REPORT"
        if visible_without_reports else
        "ALL_VISIBLE_REQUESTS_HAVE_MATCHED_FINAL_REPORT_SCOPE_UNKNOWN"
    )
    return {
        "receiver_state": state,
        "parent_task_status": parent["status"],
        "child_task_count": len(children),
        "expected_request_count_from_external_policy": len(expected),
        "expected_scope_authoritative_external": policy["expected_scope_authoritative"],
        "request_ids_without_visible_request_record": sorted(expected - set(by_id)),
        "request_ids_without_visible_child_task": sorted(expected - task_evidenced),
        "request_ids_without_matched_final_report": sorted(not_evidenced),
        "fhir_only_observation": fhir_observation,
        "authority_verified": False,
        "clinical_completion_proven": False,
        "overall_request_completeness_proven_from_fhir_grouping_alone": False
    }

def main():
    policy = json.loads((ROOT / "receiver-policy.json").read_text())["cases"]
    results = {}
    for case, settings in policy.items():
        data = json.loads((HERE / "fixtures" / (case + ".json")).read_text())
        results[case] = inspect(data, settings)
    (HERE / "comparison-results.json").write_text(json.dumps(results, indent=2) + "\n")
    original = json.loads((ROOT / "results.json").read_text())
    for case in policy:
        assert results[case]["receiver_state"] == original[case]["receiver_state"], case
    print(json.dumps(results, indent=2))
    print("Three case decisions agree with preserved baseline, under the same external expectation assumptions.")

if __name__ == "__main__":
    main()
