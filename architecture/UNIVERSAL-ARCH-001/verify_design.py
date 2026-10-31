"""Mechanical design checks only; no claim to implement runtime semantic invariants."""
from pathlib import Path
import json, hashlib, re, copy, sys
from urllib.parse import unquote
from datetime import datetime, timezone
import jsonschema
from importlib.metadata import version

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(name):return json.loads((HERE/name).read_text(encoding='utf-8'))
idx=load('evidence-index.json')
schema=load('contracts.schema.json')
jsonschema.Draft202012Validator.check_schema(schema)
validator=jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker())
records={}
for rid,row in idx['records'].items():
    p=ROOT/row['path']
    raw=p.read_bytes().splitlines(keepends=True)[row['line']-1]
    assert sha(raw)==row['raw_line_sha256']
    assert sha(p.read_bytes())==row['partition_sha256']
    r=json.loads(raw)
    assert r['id']==rid and r['version']==row['version']
    records[rid]=r
for path,meta in idx['review_and_ux_files'].items():
    assert sha((ROOT/path).read_bytes())==meta['sha256']
assert len(records)==715
edges={k:v for k,v in records.items() if 'predicate' in v}
assert len(edges)==601
assert sum(e.get('status','active')=='active' for e in edges.values())==598
cov=load('coverage.json')
for concern in cov.values():
    for row in concern['records']:
        assert row['record_id'] in records
        for eid in row['active_edge_ids']:
            e=edges[eid]
            assert e.get('status','active')=='active'
            assert row['record_id'] in (e['source_endpoint'],e['target_endpoint'])
        for src in row['source_refs']:
            assert records[src['id']]==src['original_source_record']

R={'id':'ua.example.ref','revision':1,'sha256':'a'*64}
C={'identity':'example-candidate','sha256':'b'*64}
def entity(kind,body):
    return {'contract_version':'0.1.0','kind':kind,'id':'ua.example.record','revision':1,
            'project_id':'example','scope':'component/cli','owner':'example-owner',
            'created_at':'2026-10-31T12:00:00Z','derived_from':[],'body':body}
examples=[
entity('ProjectProfile',{'goals':['Convert local input predictably'],'users_context':['Local operator; offline terminal'],
    'non_goals':['No upload or hosted service'],'constraints':['Preserve input files'],'mode':'brownfield',
    'baseline':'example-revision','component_scopes':['component/cli'],'success_criteria':['Output matches independently prepared fixture']}),
entity('SelectionDecision',{'policy_sha256':'c'*64,'input_sha256':'d'*64,'rules_version':'candidate-0.1.0','plan_status':'INCOMPLETE',
    'choices':[{'target':'arch.event_queue','status':'INCOMPLETE','obligation':'optional','basis':'research','rule_id':'R-API-003',
        'fact_refs':[R],'registry_refs':[],'reasons':['OWNER_UNKNOWN'],'missing':['operations_owner_available'],'conflicts':[]}]}),
entity('EvidenceRun',{'candidate':C,'packet_ref':R,'oracle_refs':[R],'command':['example-runner','fixture-1'],'tool_version':'example-1',
    'environment_sha256':'e'*64,'started_at':None,'ended_at':None,'executed':False,'status':'NOT_RUN',
    'producer':'example-host','artifacts':[],'limits':['Illustration only; no command executed']}),
entity('GateDecision',{'gate_id':'gate.unit_integration_execution','policy_ref':R,'candidate':C,
    'required_run_refs':[],'status':'INCOMPLETE','reasons':['RUN_NOT_EXECUTED'],'review_refs':[]})]
for ex in examples:validator.validate(ex)
# Adversarial schema examples check consequential local constraints, not implementation internals.
bad=[]
def reject(name,example,mutate):
    x=copy.deepcopy(example);mutate(x);assert list(validator.iter_errors(x)),name;bad.append(name)
reject('malformed_body',examples[1],lambda x:x.update(body='not-an-object'))
reject('unsupported_version',examples[0],lambda x:x.update(contract_version='2.0.0'))
reject('unknown_field',examples[0],lambda x:x['body'].update(unreviewed=True))
reject('invalid_timestamp',examples[0],lambda x:x.update(created_at='yesterday'))
reject('invented_kind',examples[0],lambda x:x.update(kind='ApprovalByModel'))
reject('invalid_fact_vocabulary',entity('Fact',{'predicate':'write_authorized','state':'unknown','value':None,'unit':None,'origin':'unknown','evidence_refs':[]}),lambda x:x['body'].update(state=True))
reject('pass_without_execution',examples[2],lambda x:x['body'].update(status='PASS'))
reject('pass_without_artifacts',examples[2],lambda x:x['body'].update(status='PASS',executed=True,started_at='2026-10-31T12:00:00Z',ended_at='2026-10-31T12:01:00Z'))
reject('not_run_marked_executed',examples[2],lambda x:x['body'].update(executed=True))
reject('gate_pass_without_run_refs',examples[3],lambda x:x['body'].update(status='PASS'))
reject('bad_reference_digest',examples[3],lambda x:x['body']['policy_ref'].update(sha256='wrong'))
grant=entity('Authority',{'principal':'actor','grantor':'owner','action':'local-edit','allowed_scope':['component/cli'],'baseline':C,
    'status':'DECLARED','decision_refs':[],'expires_at':'2026-10-31T23:00:00Z'})
validator.validate(grant)
reject('grant_without_decision_evidence',grant,lambda x:x['body'].update(status='GRANTED'))
release=entity('ReleaseDecision',{'candidate':C,'required_gate_refs':[],'decision':'HOLD','authority_ref':R,
    'support_owner':'owner','recovery_distribution_disposition':'No distribution authorized'})
validator.validate(release)
reject('release_approve_without_gate_refs',release,lambda x:x['body'].update(decision='APPROVE'))
checked_links=0
for p in HERE.glob('*.md'):
    for link in re.findall(r'\]\(([^)\s]+(?:\([^)]*\)[^)]*)?)\)',p.read_text(encoding='utf-8')):
        if '://' in link or link.startswith('#'):continue
        target=unquote(link.split('#')[0])
        assert (p.parent/target).exists(),(p.name,link)
        checked_links+=1
(HERE/'examples.json').write_text(json.dumps({'notice':'Illustrative records only; references intentionally do not resolve to real project records.','examples':examples+[grant,release]},indent=2)+'\n',encoding='utf-8',newline='\n')
result={'status':'PASS','scope':'Mechanical design-package checks only',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],
        'jsonschema_version':version('jsonschema'),'original_records_indexed':715,'original_relationships':601,
        'rfc3339_validator_version':version('rfc3339-validator'),
        'active_relationships':598,'review_ux_file_hashes':len(idx['review_and_ux_files']),
        'schema_kinds_compiled':len(schema['oneOf']),'valid_illustrations':len(examples)+2,
        'rejected_schema_cases':bad,'relative_document_links_checked':checked_links,
        'runtime_semantic_invariants':'NOT IMPLEMENTED / NOT TESTED',
        'independent_architecture_review':'NOT PERFORMED','selector_003R2':'NOT EXECUTED',
        'product_integration':'NO-GO; unchanged frozen disposition'}
(HERE/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,indent=2))
