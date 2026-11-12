#!/usr/bin/env python3
"""Derive parent/child Task alternatives from the existing three synthetic R4 bundles.
This is a modelling comparison, not a clinical or HL7 conformance assertion.
"""
import copy
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "fixtures"
OUT.mkdir(parents=True, exist_ok=True)
NAMESPACE = uuid.UUID("e3844cb1-fc13-4081-bbb8-e88cc12cde35")

for original in sorted((ROOT / "fixtures").glob("case*.json")):
    case = original.stem
    bundle = json.loads(original.read_text())
    entries = bundle["entry"]
    parents = [e for e in entries if e["resource"]["resourceType"] == "Task"]
    assert len(parents) == 1, case
    parent = parents[0]
    parent_resource = parent["resource"]
    old_output = copy.deepcopy(parent_resource.get("output", []))
    parent_resource.pop("basedOn", None)
    parent_resource.pop("output", None)
    parent_resource["description"] = (
        "Reported aggregate Task status; does not establish an exhaustive request "
        "or child Task set, complete evidence, placer acceptance, or clinical adequacy."
    )
    requests = [e for e in entries if e["resource"]["resourceType"] == "ServiceRequest"]
    reports = [e for e in entries if e["resource"]["resourceType"] == "DiagnosticReport"]
    new_children = []
    for request in requests:
        sr_ref = request["fullUrl"]
        tag = request["resource"]["identifier"][0]["value"]
        child_id = str(uuid.uuid5(NAMESPACE, case + ":" + tag))
        matching_reports = [entry for entry in reports if
                            any(link["reference"] == sr_ref
                                for link in entry["resource"].get("basedOn", []))]
        linked_output = [
            output for output in old_output
            if any(output.get("valueReference", {}).get("reference") == report["fullUrl"]
                   for report in matching_reports)
        ]
        child = {
            "resourceType": "Task",
            "id": child_id,
            "status": "completed",
            "intent": "order",
            "description": "Synthetic filler-reported completion for " + tag,
            "partOf": [{"reference": parent["fullUrl"]}],
            "focus": {"reference": sr_ref},
            "for": copy.deepcopy(parent_resource["for"]),
            "requester": copy.deepcopy(parent_resource["requester"]),
            "owner": copy.deepcopy(parent_resource["owner"]),
            "authoredOn": parent_resource["authoredOn"],
            "lastModified": parent_resource["lastModified"],
        }
        if linked_output:
            child["output"] = linked_output
        new_children.append({"fullUrl": "urn:uuid:" + child_id, "resource": child})
    entries.extend(new_children)
    (OUT / original.name).write_text(json.dumps(bundle, indent=2) + "\n")
    print(case, "requests", len(requests), "child Tasks", len(new_children),
          "reports", len(reports))
