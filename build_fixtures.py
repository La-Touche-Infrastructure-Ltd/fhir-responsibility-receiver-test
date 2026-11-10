#!/usr/bin/env python3
"""Generate deterministic, entirely synthetic FHIR R4 (4.0.1) Bundle/collection fixtures.
Not a clinical implementation, and not validated against a published implementation guide profile.
"""
import copy, json, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent
NAMESPACE=uuid.UUID('343db20e-5a38-4bdc-a383-4c43fc323aca')
def uid(case,kind):return str(uuid.uuid5(NAMESPACE,f'{case}-{kind}'))
def ref(case,kind):return {'reference':'urn:uuid:'+uid(case,kind)}
def code(text):return {'text':text}
def item(case,kind,r):
    r['id']=uid(case,kind)
    return {'fullUrl':'urn:uuid:'+uid(case,kind),'resource':r}
def sr(case,label,group):
    return {'resourceType':'ServiceRequest','status':'active','intent':'order','identifier':[{'system':'https://example.invalid/orders','value':f'{case}-{label}'}], 'requisition':{'system':'https://example.invalid/requisitions','value':group},'code':code(f'Synthetic diagnostic examination {label}'), 'subject':ref(case,'patient'),'requester':ref(case,'requester'),'performer':[ref(case,'performer')], 'authoredOn':'2026-11-09T09:00:00Z'}
def dr(case,label):
    return {'resourceType':'DiagnosticReport','status':'final','identifier':[{'system':'https://example.invalid/reports','value':f'{case}-{label}'}], 'code':code(f'Synthetic diagnostic report {label}'), 'basedOn':[ref(case,'sr-'+label)], 'subject':ref(case,'patient'), 'performer':[ref(case,'performer')], 'effectiveDateTime':'2026-11-09T11:30:00Z','issued':'2026-11-09T11:45:00Z', 'conclusion':f'Synthetic normal report {label}; no real patient or clinical finding.'}
def bundle(case,orders,arrived):
    group=f'SYNTH-{case}-REQUISITION'
    entries=[item(case,'patient',{'resourceType':'Patient','name':[{'family':'Synthetic','given':['Example']}]}),item(case,'requester',{'resourceType':'Organization','name':'Synthetic Referral Hospital'}),item(case,'performer',{'resourceType':'Organization','name':'Synthetic Diagnostic Provider'})]
    for label in orders:entries.append(item(case,'sr-'+label,sr(case,label,group)))
    t={'resourceType':'Task','status':'completed','intent':'order', 'description':'Sender reports diagnostic workflow complete; this does not prove receiver-side evidence completeness.', 'groupIdentifier':{'system':'https://example.invalid/requisitions','value':group}, 'basedOn':[ref(case,'sr-'+v) for v in orders],'for':ref(case,'patient'),'requester':ref(case,'requester'),'owner':ref(case,'performer'),'authoredOn':'2026-11-09T09:00:00Z','lastModified':'2026-11-09T12:00:00Z', 'output':[{'type':code(f'Synthetic diagnostic report {v}'),'valueReference':ref(case,'report-'+v)} for v in arrived]}
    entries.append(item(case,'task',t))
    for v in arrived:entries.append(item(case,'report-'+v,dr(case,v)))
    return {'resourceType':'Bundle','id':uid(case,'bundle'),'type':'collection','timestamp':'2026-11-10T12:00:00Z','entry':entries}
cases={
 'case1_missing_B':{'orders':['A','B'],'received':['A'],'expected_scope_authoritative':True,'description':'Two independently ordered examinations are agreed to exhaust this synthetic group, but B report is unavailable to the receiver.'},
 'case2_both_received':{'orders':['A','B'],'received':['A','B'],'expected_scope_authoritative':True,'description':'Two independently ordered examinations are agreed to exhaust this synthetic group, and both report resources are present.'},
 'case3_only_A_known':{'orders':['A'],'received':['A'],'expected_scope_authoritative':False,'description':'Only examination A is in receiver-visible requests; no evidence establishes that the receiver knows the full obligation set.'}}
for name,meta in cases.items():
    obj=bundle(name,meta['orders'],meta['received'])
    (ROOT/'fixtures'/f'{name}.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
policy={'title':'Receiver reliance assumptions (outside FHIR)','warning':'The complete expectation boundary is an external agreement/receiver policy, not an HL7 FHIR R4 primitive or claim made by this example. Never infer all external obligations merely from Bundle contents.','cases':{k:{'expected_service_requests':[f'{k}-{v}' for v in x['orders']], 'expected_scope_authoritative':x['expected_scope_authoritative'],'description':x['description']} for k,x in cases.items()}}
(ROOT/'receiver-policy.json').write_text(json.dumps(policy,indent=2)+'\n')
print('Generated',len(cases),'FHIR R4 synthetic bundles and receiver-policy.json')
