"""Build derivative indexes and design schemas; never modify preserved inputs."""
from pathlib import Path
import json, hashlib, collections, sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'architecture/UNIVERSAL-ARCH-001'
FROZEN = ROOT / 'preserved_freezes/SRS-FREEZE-2026-10-31-v1/tree'
DATA = FROZEN / 'current_003R/dataset/v1'
sha = lambda b: hashlib.sha256(b).hexdigest()
def write(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')

index = {}
records = {}
counts = {}
for p in sorted(DATA.glob('*.jsonl')):
    rows = p.read_bytes().splitlines(keepends=True)
    counts[p.stem] = len(rows)
    for line, raw in enumerate(rows, 1):
        r = json.loads(raw)
        assert r['id'] not in index
        records[r['id']] = r
        index[r['id']] = {'path':p.relative_to(ROOT).as_posix(), 'line':line,
                         'raw_line_sha256':sha(raw), 'partition_sha256':sha(p.read_bytes()),
                         'version':r['version'], 'status':r.get('status','active')}
assert len(records)==715 and counts['relationships']==601
edges = [r for r in records.values() if 'predicate' in r]
assert sum(e.get('status','active')=='active' for e in edges)==598
for e in edges:
    assert e['source_endpoint'] in records and e['target_endpoint'] in records
    assert all(s in records for s in e['source_ids'])

concerns = {
 'project_understanding':['sdlc.discovery_scope','sdlc.requirements_risk'],
 'complete_lifecycle':[r for r in records if r.startswith('sdlc.')],
 'risk_adaptation':['practice.threat_modeling','roadmap.risk_first_poc'],
 'research_selection':['arch.minimal_viable_structure','practice.requirements_traceability'],
 'connected_artifacts':['practice.requirements_traceability','gate.requirements_acceptance'],
 'architecture':['arch.minimal_viable_structure','arch.layered_modular','arch.client_server_api_boundary','arch.event_queue','arch.multitenancy_isolation','arch.agent_tool_boundary'],
 'bounded_execution':['prompt.implement_scoped_task','prompt.review_change','arch.agent_tool_boundary'],
 'verification':[r for r in records if r.startswith('gate.')],
 'release':['sdlc.release','practice.ci_reproducible_release','gate.dependency_provenance'],
 'operations':['sdlc.maintenance_feedback','practice.observability_incident','gate.operational_rollback'],
 'evolving_state':['practice.change_maintenance','practice.version_control_review'],
 'quality':['practice.test_strategy','prompt.add_test','prompt.investigate_failure'],
 'broad_types':[r for r in records if r.startswith('software_type.')],
 'uxec':[]
}
coverage = {}
for key, ids in concerns.items():
    rows=[]
    for rid in ids:
        r=records[rid]
        es=[e for e in edges if e.get('status','active')=='active' and (e['source_endpoint']==rid or e['target_endpoint']==rid)]
        rows.append({'record_id':rid,'locator':index[rid],
                     'description':r.get('description'), 'limitations':r.get('limitations'),
                     'evidence_classification':r.get('evidence_classification'),
                     'active_edge_ids':[e['id'] for e in es],
                     'supported_by_edge_ids':[e['id'] for e in es if e['source_endpoint']==rid and e['predicate']=='supported_by'],
                     'source_refs':[{'id':s,'locator':index[s], 'original_source_record':records[s]} for s in r.get('source_ids',[])]})
    coverage[key]={'status':'RESEARCH_SUPPORT_WITH_GAPS' if ids else 'EXTERNAL_UX_REPORTS_ONLY',
                   'implementation':'NOT_IMPLEMENTED', 'records':rows}
evidence_files={}
for base in [FROZEN/'independent_reviews',ROOT/'rounds']:
    for p in sorted(base.rglob('*')):
        if p.is_file() and p.suffix in {'.md','.txt','.json'}:
            evidence_files[p.relative_to(ROOT).as_posix()]={'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
write('evidence-index.json',{'checkpoint':'UNIVERSAL-ARCH-001','base_commit':'62c8381',
      'freeze_sha256':'a39b30fee3304e843b0291770efe7a42e993d733c3c09d5321ea5f2d53e6ad04',
      'counts':counts,'predicate_counts':dict(collections.Counter(e['predicate'] for e in edges)),
      'records':index,'review_and_ux_files':evidence_files,
      'interpretation':'Derived index only; hashes establish bytes, not truth or execution.'})
write('coverage.json',coverage)

# Closed entity schemas. These encode shape, not the documented semantic validator.
S={'type':'string','minLength':1}
def enum(*v): return {'enum':list(v)}
def arr(item=S, minimum=0): return {'type':'array','items':item,'minItems':minimum}
def obj(fields, required=None): return {'type':'object','additionalProperties':False,'properties':fields,'required':list(fields) if required is None else required}
H={'type':'string','pattern':'^[a-f0-9]{64}$'}
ref=obj({'id':S,'revision':{'type':'integer','minimum':1},'sha256':H})
refs=arr(ref)
candidate=obj({'identity':S,'sha256':H})
registry=obj({'checkpoint_sha256':H,'record_id':S,'record_version':S,'partition':S,'line':{'type':'integer','minimum':1},'edge_ids':arr(S),'source_ids':arr(S)})
choice=obj({'target':S,'status':enum('RECOMMENDED','CONDITIONAL','INAPPLICABLE','INCOMPLETE'),
            'obligation':enum('mandatory','optional','omitted'),'basis':enum('research','project_policy','synthesis'),
            'rule_id':S,'fact_refs':refs,'registry_refs':arr(registry),'reasons':arr(S,1),'missing':arr(S),'conflicts':refs})
bodies={
'ProjectProfile':obj({'goals':arr(S,1),'users_context':arr(S,1),'non_goals':arr(S),'constraints':arr(S),'mode':enum('greenfield','brownfield','hybrid'),'baseline':S,'component_scopes':arr(S,1),'success_criteria':arr(S,1)}),
'Fact':obj({'predicate':S,'state':enum('true','false','unknown'),'value':{'type':['string','number','boolean','null']},'unit':{'type':['string','null']},'origin':enum('declared','observed','inferred','unknown'),'evidence_refs':refs}),
'Requirement':obj({'outcome':S,'acceptance':arr(S,1),'priority':enum('required','optional'),'acceptance_owner':S,'oracle_refs':refs}),
'RiskAssessment':obj({'tier':enum('T0','T1','T2','T3'),'dimensions':arr(obj({'name':S,'state':enum('known','unknown'),'consequence':S,'rationale':S,'evidence_refs':refs}),1),'floor_triggers':arr(S),'unresolved':arr(S),'tailoring_refs':refs}),
'SelectionDecision':obj({'policy_sha256':H,'input_sha256':H,'rules_version':S,'plan_status':enum('COMPLETE','INCOMPLETE'),'choices':arr(choice,1)}),
'DesignDecision':obj({'problem':S,'alternatives':arr(obj({'name':S,'conditions':arr(S),'costs':arr(S),'exclusions':arr(S)}),1),'chosen':S,'rationale':S,'status':enum('PROPOSED','ACCEPTED','REJECTED','SUPERSEDED')}),
'DomainContract':obj({'module':S,'module_version':S,'schema_sha256':H,'path':S,'sha256':H,'applicability':S}),
'TaskPacket':obj({'goal':S,'requirement_refs':arr(ref,1),'baseline':candidate,'expected_state_revision':{'type':'integer','minimum':0},'allowed_paths':arr(S,1),'allowed_operations':arr(S,1),'forbidden_operations':arr(S),'budget':obj({'seconds':{'type':'integer','minimum':1},'attempts':{'type':'integer','minimum':1},'tokens':{'type':'integer','minimum':0},'cost_limit':{'type':'number','minimum':0},'currency':S}),'dependencies':arr(obj({'task':ref,'kind':enum('hard','optional','conditional'),'condition':S})),'oracle_refs':arr(ref,1),'grant_refs':refs,'stop_triggers':arr(S,1)}),
'Authority':obj({'principal':S,'grantor':S,'action':S,'allowed_scope':arr(S,1),'baseline':candidate,'status':enum('REQUESTED','DECLARED','GRANTED','DENIED','REVOKED'),'decision_refs':refs,'expires_at':{'type':'string','format':'date-time'}}),
'EvidenceRun':obj({'candidate':candidate,'packet_ref':ref,'oracle_refs':arr(ref,1),'command':arr(S,1),'tool_version':S,'environment_sha256':H,'started_at':{'type':['string','null'],'format':'date-time'},'ended_at':{'type':['string','null'],'format':'date-time'},'executed':{'type':'boolean'},'status':enum('PASS','FAIL','BLOCKED','NOT_RUN'),'producer':S,'artifacts':arr(obj({'path':S,'sha256':H})),'limits':arr(S)}),
'GateDecision':obj({'gate_id':S,'policy_ref':ref,'candidate':candidate,'required_run_refs':refs,'status':enum('PASS','FAIL','INCOMPLETE'),'reasons':arr(S,1),'review_refs':refs}),
'ReleaseDecision':obj({'candidate':candidate,'required_gate_refs':refs,'decision':enum('APPROVE','HOLD'),'authority_ref':ref,'support_owner':S,'recovery_distribution_disposition':S}),
'ChangeEvent':obj({'sequence':{'type':'integer','minimum':1},'expected_state_revision':{'type':'integer','minimum':0},'prior_event_sha256':{'type':['string','null'],'pattern':'^[a-f0-9]{64}$'},'actor':S,'changed_refs':arr(ref,1),'invalidated_refs':refs,'reason':S}),
'StateSnapshot':obj({'state_revision':{'type':'integer','minimum':0},'last_event_ref':{'anyOf':[ref,{'type':'null'}]},'scopes':arr(obj({'scope':S,'status':enum('NOT_STARTED','ACTIVE','BLOCKED','READY_FOR_REVIEW','ACCEPTED','STALE','RETIRED')}),1),'blockers':arr(S),'current_candidate':{'anyOf':[candidate,{'type':'null'}]},'next_task_refs':refs})
}
bodies['EvidenceRun']['allOf']=[{'if':{'properties':{'status':enum('PASS','FAIL')},'required':['status']},'then':{'properties':{'executed':{'const':True},'artifacts':{'minItems':1},'started_at':{'type':'string'},'ended_at':{'type':'string'}}}}, {'if':{'properties':{'status':{'const':'NOT_RUN'}},'required':['status']},'then':{'properties':{'executed':{'const':False}}}}]
bodies['Authority']['allOf']=[{'if':{'properties':{'status':{'const':'GRANTED'}},'required':['status']},'then':{'properties':{'decision_refs':{'minItems':1}}}}]
bodies['GateDecision']['allOf']=[{'if':{'properties':{'status':{'const':'PASS'}},'required':['status']},'then':{'properties':{'required_run_refs':{'minItems':1}}}}]
bodies['ReleaseDecision']['allOf']=[{'if':{'properties':{'decision':{'const':'APPROVE'}},'required':['decision']},'then':{'properties':{'required_gate_refs':{'minItems':1}}}}]
variants=[]
for kind, body in bodies.items():
    variants.append(obj({'contract_version':{'const':'0.1.0'},'kind':{'const':kind},'id':{'type':'string','pattern':'^ua\\.[a-z0-9_.-]+$'},'revision':{'type':'integer','minimum':1},'project_id':S,'scope':S,'owner':S,'created_at':{'type':'string','format':'date-time'},'derived_from':refs,'body':body}))
write('contracts.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:universal-architecture:contracts:0.1.0','title':'Universal development record candidates','oneOf':variants})
print(json.dumps({'records':len(index),'active_edges':598,'schema_kinds':len(variants),'indexed_review_ux_files':len(evidence_files)}))
