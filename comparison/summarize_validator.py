#!/usr/bin/env python3
"""Summarise official validator OperationOutcome JSON with source and severity."""
import json
import sys
from pathlib import Path

files = [Path(arg) for arg in sys.argv[1:]]
if not files:
    raise SystemExit("No validator OperationOutcome files supplied")
bad = 0
summary = {}
for path in files:
    if not path.exists():
        summary[path.name] = {"status": "NO_OUTPUT"}
        bad += 1
        continue
    try:
        obj = json.loads(path.read_text())
    except Exception as exc:
        summary[path.name] = {"status": "UNREADABLE", "detail": str(exc)}
        bad += 1
        continue
    if obj.get("resourceType") != "OperationOutcome":
        summary[path.name] = {"status": "UNEXPECTED_RESPONSE",
                              "resourceType": obj.get("resourceType")}
        bad += 1
        continue
    issues = obj.get("issue", [])
    severity_counts = {name: 0 for name in ("fatal", "error", "warning", "information")}
    for issue in issues:
        severity = issue.get("severity")
        if severity in severity_counts:
            severity_counts[severity] += 1
    if severity_counts["fatal"] or severity_counts["error"]:
        bad += 1
    summary[path.name] = {
        "status": "ERRORS" if (severity_counts["fatal"] or severity_counts["error"])
                  else "NO_ERRORS_REPORTED",
        "severity_counts": severity_counts,
        "issues": [{
            "severity": issue.get("severity"),
            "code": issue.get("code"),
            "details": issue.get("details", {}).get("text"),
            "diagnostics": issue.get("diagnostics"),
            "expression": issue.get("expression")
        } for issue in issues]
    }
out = Path("comparison/validation-summary.json")
out.write_text(json.dumps(summary, indent=2) + "\n")
for name, entry in summary.items():
    print(name + ": " + entry["status"] +
          " " + json.dumps(entry.get("severity_counts", {})))
print("Full report:", out)
sys.exit(1 if bad else 0)
