#!/usr/bin/env python3
"""Reference receiver with explicit limited assumptions; NOT an HL7/FHIR or PCC-57 conformance validator."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def inspect(bundle, policy):
    """Assess only receiver-visible reports against explicitly declared expectations.

    This is a local study rule, not an HL7/FHIR or clinical validation algorithm.
    """
    entries = bundle['entry']
    resources = {e['fullUrl']: e['resource'] for e in entries}
    tasks = [r for r in resources.values() if r['resourceType'] == 'Task']
    assert len(tasks) == 1, 'Synthetic fixtures require exactly one Task'
    task = tasks[0]

    requests = {e['fullUrl']: e['resource'] for e in entries
                if e['resource']['resourceType'] == 'ServiceRequest'}
    reports = {e['fullUrl']: e['resource'] for e in entries
               if e['resource']['resourceType'] == 'DiagnosticReport'}

    # The authoritative *test input* is the policy's expected request identifiers,
    # NOT merely the requests that happen to be present in the Bundle.
    expected_list = policy['expected_service_requests']
    assert expected_list and len(expected_list) == len(set(expected_list)), \
        'Expected request identifiers must be non-empty and unique'
    expected = set(expected_list)
    visible_by_id = {}
    for url, request in requests.items():
        ids = [i['value'] for i in request.get('identifier', []) if 'value' in i]
        assert len(ids) == 1, 'Synthetic fixture requires one ServiceRequest identifier'
        assert ids[0] not in visible_by_id, 'Duplicate visible ServiceRequest identifier'
        visible_by_id[ids[0]] = url

    task_order_refs = {r['reference'] for r in task.get('basedOn', [])}
    task_output_refs = {r['valueReference']['reference'] for r in task.get('output', [])
                        if 'valueReference' in r}
    supported = set()
    unusable = []
    for report_url, report in reports.items():
        based_on = [r['reference'] for r in report.get('basedOn', [])]
        if (report.get('status') == 'final'
                and report_url in task_output_refs
                and len(based_on) == 1
                and based_on[0] in task_order_refs
                and based_on[0] in requests):
            request = requests[based_on[0]]
            req_id = request['identifier'][0]['value']
            if req_id in expected:
                supported.add(req_id)
            else:
                unusable.append(report_url)
        else:
            unusable.append(report_url)

    not_evidenced = expected - supported
    missing_request_records = expected - set(visible_by_id)
    if not_evidenced:
        state = 'INSUFFICIENT_REPORT_EVIDENCE'
    elif policy['expected_scope_authoritative']:
        state = 'ALL_AGREED_EXPECTED_REPORTS_PRESENT_IN_SNAPSHOT'
    else:
        state = 'ALL_KNOWN_REPORTS_PRESENT_SCOPE_UNKNOWN'
    return {
        'task_status': task['status'],
        'expected_scope_authoritative_external': policy['expected_scope_authoritative'],
        'expected_requests': sorted(expected),
        'expected_requests_without_visible_request_record': sorted(missing_request_records),
        'final_linked_reports_evidenced_for': sorted(supported),
        'requests_without_evidenced_reports': sorted(not_evidenced),
        'unusable_report_references': sorted(unusable),
        'receiver_state': state,
        'clinical_completion_proven': False,
        'authority_verified': False,
        'note': 'Snapshot evidence only. Not a clinical, legal, identity, authority, or exhaustive-obligation verification.'
    }

def main():
    policy=json.loads((ROOT/'receiver-policy.json').read_text())['cases'];results={}
    for name,settings in policy.items():
        bundle=json.loads((ROOT/'fixtures'/f'{name}.json').read_text())
        results[name]=inspect(bundle,settings)
    output=ROOT/'results.json'
    output.write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
