#!/usr/bin/env python3
"""Deliberately LIMITED FHIR R4 structural/reference checks, not official HL7 validation."""
import json,re,uuid,unittest
from pathlib import Path
from receiver import inspect,ROOT
UUID_URL=re.compile(r'^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
REQUIRED={'Bundle':('resourceType','type','entry'),'Task':('resourceType','status','intent'),'ServiceRequest':('resourceType','status','intent','subject'),'DiagnosticReport':('resourceType','status','code'),'Patient':('resourceType',),'Organization':('resourceType',)}
class TestSyntheticR4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.policies=json.loads((ROOT/'receiver-policy.json').read_text())['cases']
    def test_json_and_minimum_required_fields(self):
        for file in (ROOT/'fixtures').glob('*.json'):
            b=json.loads(file.read_text());self.assertEqual(b['resourceType'],'Bundle');self.assertEqual(b['type'],'collection')
            for e in b['entry']:
                r=e['resource'];self.assertIn(r['resourceType'],REQUIRED)
                for key in REQUIRED[r['resourceType']]:self.assertIn(key,r)
                if r['resourceType']=='Task':
                    self.assertEqual(r['status'],'completed');self.assertEqual(r['intent'],'order')
                    self.assertTrue(all('type'in v and 'valueReference'in v for v in r['output']))
                if r['resourceType']=='DiagnosticReport':self.assertEqual(r['status'],'final')
                if r['resourceType']=='ServiceRequest':self.assertEqual(r['intent'],'order')
    def test_references_reach_real_resource_in_same_bundle(self):
        for file in (ROOT/'fixtures').glob('*.json'):
            b=json.loads(file.read_text()); items={e['fullUrl']:e['resource'] for e in b['entry']}
            self.assertEqual(len(items),len(b['entry']))
            for url,r in items.items():
                self.assertRegex(url,UUID_URL)
                self.assertEqual(url,'urn:uuid:'+r['id'])
                refs=[]
                for k in ('subject','requester','owner','for'):
                    if isinstance(r.get(k),dict):refs.append(r[k]['reference'])
                for k in ('basedOn','performer'):
                    refs += [ref['reference'] for ref in r.get(k,[])]
                if r['resourceType']=='Task':refs += [o['valueReference']['reference'] for o in r['output']]
                for ref in refs:self.assertIn(ref,items,f'{file.name}: dangling {ref}')
    def test_receiver_expected_states(self):
        expected={'case1_missing_B':('INSUFFICIENT_REPORT_EVIDENCE',1),'case2_both_received':('ALL_AGREED_EXPECTED_REPORTS_PRESENT_IN_SNAPSHOT',0),'case3_only_A_known':('ALL_KNOWN_REPORTS_PRESENT_SCOPE_UNKNOWN',0)}
        for name,p in self.policies.items():
            r=inspect(json.loads((ROOT/'fixtures'/f'{name}.json').read_text()),p)
            self.assertEqual((r['receiver_state'],len(r['requests_without_evidenced_reports'])),expected[name])
            self.assertFalse(r['clinical_completion_proven'])
    def test_mutation_removed_task_output_blocks_B_evidence(self):
        import copy
        b=json.loads((ROOT/'fixtures'/'case2_both_received.json').read_text())
        t=next(e['resource'] for e in b['entry'] if e['resource']['resourceType']=='Task')
        t['output']=t['output'][:1]
        r=inspect(b,self.policies['case2_both_received'])
        self.assertEqual(r['receiver_state'],'INSUFFICIENT_REPORT_EVIDENCE')
        self.assertEqual(len(r['requests_without_evidenced_reports']),1)
    def test_mutation_preliminary_report_not_counted_as_final(self):
        b=json.loads((ROOT/'fixtures'/'case2_both_received.json').read_text())
        d=[e['resource'] for e in b['entry'] if e['resource']['resourceType']=='DiagnosticReport']
        d[-1]['status']='preliminary'
        r=inspect(b,self.policies['case2_both_received'])
        self.assertEqual(r['receiver_state'],'INSUFFICIENT_REPORT_EVIDENCE')
    def test_mutation_wrong_order_link_not_counted(self):
        b=json.loads((ROOT/'fixtures'/'case2_both_received.json').read_text())
        reps=[e['resource'] for e in b['entry'] if e['resource']['resourceType']=='DiagnosticReport']
        reps[-1]['basedOn']=reps[0]['basedOn']
        r=inspect(b,self.policies['case2_both_received'])
        self.assertEqual(r['receiver_state'],'INSUFFICIENT_REPORT_EVIDENCE')
    def test_expected_report_missing_even_when_request_resource_absent(self):
        # Regression: a receiver must not silently redefine an externally agreed
        # expectation set from whichever request records happen to be visible.
        b=json.loads((ROOT/'fixtures'/'case2_both_received.json').read_text())
        policy=self.policies['case2_both_received']
        b['entry']=[e for e in b['entry'] if e['resource']['resourceType'] not in
                    ('ServiceRequest','DiagnosticReport') or
                    not e['resource'].get('identifier',[{}])[0].get('value','').endswith('-B')]
        r=inspect(b,policy)
        self.assertEqual(r['receiver_state'],'INSUFFICIENT_REPORT_EVIDENCE')
        self.assertIn('case2_both_received-B',r['expected_requests_without_visible_request_record'])
        self.assertIn('case2_both_received-B',r['requests_without_evidenced_reports'])
    def test_task_order_link_omission_blocks_report_evidence(self):
        b=json.loads((ROOT/'fixtures'/'case2_both_received.json').read_text())
        task=next(e['resource'] for e in b['entry'] if e['resource']['resourceType']=='Task')
        task['basedOn']=task['basedOn'][:1]
        r=inspect(b,self.policies['case2_both_received'])
        self.assertEqual(r['receiver_state'],'INSUFFICIENT_REPORT_EVIDENCE')
        self.assertIn('case2_both_received-B',r['requests_without_evidenced_reports'])
    def test_case3_never_implies_no_B_elsewhere(self):
        p=self.policies['case3_only_A_known'];self.assertFalse(p['expected_scope_authoritative'])
        r=inspect(json.loads((ROOT/'fixtures'/'case3_only_A_known.json').read_text()),p)
        self.assertIn('SCOPE_UNKNOWN',r['receiver_state'])
    def test_task_completed_not_proof_of_received_report(self):
        b=json.loads((ROOT/'fixtures'/'case1_missing_B.json').read_text());r=inspect(b,self.policies['case1_missing_B'])
        self.assertEqual(r['task_status'],'completed');self.assertEqual(r['receiver_state'],'INSUFFICIENT_REPORT_EVIDENCE')
if __name__=='__main__':unittest.main(verbosity=2)
