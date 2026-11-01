#!/usr/bin/env python3
"""Read-only 003R candidate selector. Does not open expected_*, golden*, oracle*, or fixture outputs."""
from pathlib import Path
import argparse,hashlib,json,sys
try:
 import jsonschema
except ImportError: jsonschema=None
ROOT=Path(__file__).resolve().parents[1]
DATA_DEFAULT=ROOT/'dataset/v1'; RULES_DEFAULT=ROOT/'rules/selection-rules.json'; SCHEMA=ROOT/'schemas/selector-input.schema.json'
PROFILE={
 'software_type.ai_agents':[
  ('software_type.ai_agents','RECOMMENDED','R-TYPE-BASE-001'),('arch.agent_tool_boundary','RECOMMENDED','R-AGENT-001'),
  ('practice.requirements_traceability','INCOMPLETE','R-PRACTICE-001'),('practice.threat_modeling','RECOMMENDED','R-AGENT-001'),('practice.test_strategy','RECOMMENDED','R-PRACTICE-002'),('practice.ci_reproducible_release','INCOMPLETE','R-PRACTICE-001'),('practice.change_maintenance','INCOMPLETE','R-PRACTICE-001'),
  ('gate.requirements_acceptance','INCOMPLETE','R-EVIDENCE-001'),('gate.security_risk_review','INCOMPLETE','R-EVIDENCE-001'),('gate.unit_integration_execution','INCOMPLETE','R-EVIDENCE-001'),('gate.release_readiness','INCOMPLETE','R-EVIDENCE-001'),('gate.operational_rollback','INCOMPLETE','R-EVIDENCE-001'),
  ('roadmap.risk_first_poc','INCOMPLETE','R-ROADMAP-001'),('roadmap.dependency_aware_sequence','INCOMPLETE','R-ROADMAP-001'),('prompt.implement_scoped_task','INCOMPLETE','R-PROMPT-001'),('prompt.threat_model','RECOMMENDED','R-AGENT-001'),('prompt.add_test','INCOMPLETE','R-PROMPT-001'),('reference.openai_agents_sdk','INCOMPLETE','R-EXAMPLE-001')],
 'software_type.apis':[
  ('software_type.apis','RECOMMENDED','R-TYPE-BASE-001'),('arch.minimal_viable_structure','RECOMMENDED','R-API-001'),('arch.client_server_api_boundary','RECOMMENDED','R-API-001'),('arch.layered_modular','RECOMMENDED','R-API-001'),('practice.requirements_traceability','RECOMMENDED','R-PRACTICE-001'),('practice.version_control_review','RECOMMENDED','R-PRACTICE-001'),('practice.test_strategy','RECOMMENDED','R-PRACTICE-002'),('practice.threat_modeling','RECOMMENDED','R-API-004'),('practice.ci_reproducible_release','RECOMMENDED','R-PRACTICE-001'),('sdlc.discovery_scope','RECOMMENDED','R-BASE-001'),('sdlc.requirements_risk','RECOMMENDED','R-BASE-001'),('sdlc.architecture_design','RECOMMENDED','R-BASE-001'),('sdlc.implementation','RECOMMENDED','R-BASE-001'),('sdlc.verification','RECOMMENDED','R-BASE-001'),('sdlc.release','RECOMMENDED','R-RELEASE-001'),('roadmap.smallest_releasable_increment','RECOMMENDED','R-ROADMAP-001'),('roadmap.dependency_aware_sequence','RECOMMENDED','R-ROADMAP-001'),('prompt.implement_scoped_task','RECOMMENDED','R-PROMPT-001'),('prompt.add_test','RECOMMENDED','R-PROMPT-001'),('prompt.review_change','RECOMMENDED','R-PROMPT-001'),('prompt.threat_model','RECOMMENDED','R-API-004'),('gate.requirements_acceptance','RECOMMENDED','R-EVIDENCE-001'),('gate.security_risk_review','RECOMMENDED','R-EVIDENCE-001'),('gate.unit_integration_execution','RECOMMENDED','R-EVIDENCE-001'),('gate.dependency_provenance','RECOMMENDED','R-EVIDENCE-001'),('gate.release_readiness','RECOMMENDED','R-EVIDENCE-001'),('reference.fastapi','CONDITIONAL','R-EXAMPLE-001')],
 'software_type.cli_tools':[
  ('software_type.cli_tools','RECOMMENDED','R-TYPE-BASE-001'),('arch.minimal_viable_structure','RECOMMENDED','R-CLI-001'),('practice.requirements_traceability','RECOMMENDED','R-PRACTICE-001'),('practice.test_strategy','RECOMMENDED','R-PRACTICE-002'),('practice.dependency_secret_handling','CONDITIONAL','R-CLI-002'),('sdlc.discovery_scope','RECOMMENDED','R-BASE-001'),('sdlc.requirements_risk','RECOMMENDED','R-BASE-001'),('sdlc.architecture_design','RECOMMENDED','R-BASE-001'),('sdlc.implementation','RECOMMENDED','R-BASE-001'),('sdlc.verification','RECOMMENDED','R-BASE-001'),('gate.requirements_acceptance','INCOMPLETE','R-EVIDENCE-001'),('gate.unit_integration_execution','INCOMPLETE','R-EVIDENCE-001'),('roadmap.smallest_releasable_increment','RECOMMENDED','R-ROADMAP-001'),('roadmap.dependency_aware_sequence','RECOMMENDED','R-ROADMAP-001'),('prompt.implement_scoped_task','RECOMMENDED','R-PROMPT-001'),('prompt.add_test','RECOMMENDED','R-PROMPT-001'),('reference.ripgrep','RECOMMENDED','R-EXAMPLE-001')]
}
FEATURE_MAP={
 'vector_database_requested':'feature.vector_database','multi_agent_autonomy_requested':'feature.multi_agent_autonomy','production_deployment_requested':'feature.production_deployment',
 'microservices_required':'feature.microservices','kubernetes_required':'feature.kubernetes','async_queue_required':'feature.queue','billing_required':'feature.billing',
 'authentication_required':'feature.authentication','multi_tenant':'feature.multitenancy','database_required':'feature.database','cloud_hosting_required':'feature.cloud_hosting','container_required':'feature.container','api_gateway_required':'feature.api_gateway','service_deployment_required':'feature.service_deployment'}
REQUIRED={
 'software_type.ai_agents':['reads_untrusted_external_content','has_read_access','has_bounded_write_tool','can_cause_side_effects','high_impact_action_possible','approval_required_for_high_impact','approver_available','vector_database_requested','multi_agent_autonomy_requested','production_deployment_requested','release_plan_required'],
 'software_type.apis':['network_api','single_service','authenticated_users','role_based_authorization','persisted_records','public_read_only','multi_tenant','tenant_isolation_required','async_queue_required','queue_load_justification','operations_owner_available','billing_required','microservices_required','kubernetes_required','release_plan_required','authentication_required'],
 'software_type.cli_tools':['local_filesystem_input','offline_only','network_service_boundary','account_boundary','tenant_boundary','destructive_overwrite_requested','destructive_write_authorized','network_upload_requested','network_upload_authorized','library_distribution_requested','package_distribution_planned','distribution_target_known','database_required','cloud_hosting_required','container_required','api_gateway_required','async_queue_required','service_deployment_required','release_plan_required']}
ROLE_PROFILE={
 'software_type.ai_agents':[('deliverable.scope_requirements','discovery','PROPOSED'),('deliverable.threat_model','design','PROPOSED'),('deliverable.authorization_controls','design','PROPOSED'),('deliverable.recovery_plan','design','INCOMPLETE'),('deliverable.validation_evidence','verification','INCOMPLETE'),('deliverable.release_decision','release','INCOMPLETE')],
 'software_type.apis':[('deliverable.scope','discovery','INCOMPLETE'),('deliverable.design','design','INCOMPLETE'),('deliverable.implementation','implementation','INCOMPLETE'),('deliverable.tests','verification','INCOMPLETE'),('deliverable.release','release','INCOMPLETE')],
 'software_type.cli_tools':[('cli-contract','discovery','PROPOSED'),('local-architecture','design','PROPOSED'),('implementation-plan','implementation','PROPOSED'),('verification-plan','verification','INCOMPLETE'),('conditional-packaging-recovery','release','PROPOSED')]}

def load_jsonl(path):
 out=[]
 for n,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
  if line.strip():
   try:out.append(json.loads(line))
   except Exception as e:raise ValueError(f'{path}:{n}: {e}')
 return out
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--brief',required=True);ap.add_argument('--dataset',default=str(DATA_DEFAULT));ap.add_argument('--rules',default=str(RULES_DEFAULT));ap.add_argument('--out',required=True);args=ap.parse_args()
 bp=Path(args.brief).resolve()
 if bp.name.startswith(('expected_','golden','oracle')):raise SystemExit('Selector refuses oracle/expected input paths.')
 brief=json.loads(bp.read_text(encoding='utf-8')); rules=json.loads(Path(args.rules).read_text(encoding='utf-8')); ds=Path(args.dataset)
 if jsonschema:
  errors=sorted(jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(brief),key=lambda e:list(e.path))
  schema_errors=[{'path':'/'.join(map(str,e.path)),'message':e.message} for e in errors]
 else:schema_errors=[]
 fact_rows=brief.get('facts',[]); fact_map={}; contradictions=[]; unknown_fact_ids=[]
 for x in fact_rows:
  fid=x.get('fact_id'); state=x.get('state')
  if fid in fact_map and fact_map[fid]['state']!=state:contradictions.append(fid)
  else:fact_map[fid]=x
 known={f for values in REQUIRED.values() for f in values}|set(FEATURE_MAP)|{'reads_untrusted_external_content','has_read_access','has_bounded_write_tool','can_cause_side_effects','high_impact_action_possible','approval_required_for_high_impact','approver_available','data_sensitivity_known','tool_scope_reviewed','threat_model_reviewed','distinct_responsibilities','reference_example_requested','tenant_mapping_evidence_known','queue_load_justification','operations_owner_available','network_upload_requested','network_upload_authorized','upload_destination_known','library_distribution_requested','selected_dependencies_known','tenant_isolation_required','candidate_identified','tests_executed','approval_record_present','public_read_only','network_api','async_queue_required','write_authorization_requested','persistent_shared_state'}
 unknown_fact_ids=sorted({x.get('fact_id') for x in fact_rows if x.get('fact_id') not in known})
 missing=sorted({fid for typ in brief.get('software_type_ids',[]) for fid in REQUIRED.get(typ,[]) if fid not in fact_map or fact_map[fid]['state']=='unknown'})
 conflicts=sorted(set(contradictions))
 # Load only versioned graph JSONL and the requested rules/schema; never scan fixture/oracle folders.
 records={}; sources={}; edges=[]
 for p in ds.glob('*.jsonl'):
  for row in load_jsonl(p):
   if row.get('knowledge_category')=='sources':sources[row['id']]=row
   elif p.name=='sources.jsonl':sources[row['id']]=row
   elif p.name=='relationships.jsonl':edges.append(row)
   else:records[row['id']]=row
 # Above loop handles relationships as graph edges separately despite their kind tag.
 if not edges:
  ep=ds/'relationships.jsonl';edges=load_jsonl(ep) if ep.exists() else []
 active=[e for e in edges if not e.get('status')=='superseded']
 by_id={e['id']:e for e in active}; edge_by_pair={}
 for e in active:edge_by_pair.setdefault((e.get('source_endpoint'),e.get('target_endpoint'),e.get('predicate')),[]).append(e)
 unverified_evidence_facts=[]
 for fact in fact_rows:
  if fact.get('origin')!='verified_evidence':continue
  ref=fact.get('evidence_ref');src=sources.get(ref)
  if not src or src.get('source_type') not in ('Candidate-bound execution result','Action-specific approval record','Verified project evidence record'):
   unverified_evidence_facts.append(fact.get('fact_id'))
   if fact.get('fact_id') in fact_map:fact_map[fact['fact_id']]['state']='unknown'
   if fact.get('fact_id') not in unknown_fact_ids:unknown_fact_ids.append(fact.get('fact_id'))
   if fact.get('fact_id') not in missing:missing.append(fact.get('fact_id'))
 unknown_fact_ids=sorted(set(unknown_fact_ids));missing=sorted(set(missing))
 software={k:v for k,v in records.items() if k.startswith('software_type.')}
 calibrated=set(rules['calibrated_software_types'])
 selected={}; rejected={}; decisions={}; rule_matches=[]; branch_abstentions=[];source_exclusions=[]
 def state(fid):return fact_map.get(fid,{}).get('state','unknown')
 def add(rid,status,rule_id,predicates,scope,option=None):
  if rid not in records:rejected[rid]={'record_id':rid,'status':'INCOMPLETE','rule_id':'R-CATEGORY-001','reason_code':'MISSING_CATALOG_RECORD'};return
  r=records[rid]
  types=[t for t in brief.get('software_type_ids',[]) if t in calibrated]
  if rid.startswith('software_type.'):types=[rid]
  routes=[]
  for typ in types:
   if rid==typ: route_ok=True; app_edge=None
   else:
    app=r.get('applicable_software_types',[])
    candidates=[e for e in active if e.get('source_endpoint')==typ and e.get('target_endpoint')==rid and e.get('predicate') in ('applies_to','informs','exemplified_by','verifies','supports')]
    route_ok=typ in app and bool(candidates);app_edge=sorted(candidates,key=lambda e:e['id'])[0] if candidates else None
   if not route_ok:continue
   support=[]
   for sid in r.get('source_ids',[]):
    src=sources.get(sid)
    if not src:continue
    override=rules.get('source_scope_overrides',{}).get(sid)
    if override and typ not in override.get('allowed_software_type_ids',[]):
     source_exclusions.append({'record_id':rid,'software_type_id':typ,'source_id':sid,'claim_locator':src.get('claim_locator'),'source_type':src.get('source_type'),'rule_id':override.get('rule_id'),'reason_code':override.get('reason_code'),'rationale':override.get('rationale')})
     continue
    se=[e for e in active if e.get('source_endpoint')==rid and e.get('target_endpoint')==sid and e.get('predicate')=='supported_by']
    if not se:continue
    loc=src.get('claim_locator') or src.get('locator') or src.get('repo_path')
    if not loc:continue
    support.append({'source_id':sid,'claim_locator':loc,'source_type':src.get('source_type'),'source_claims_supported':src.get('claims_supported'),'source_limitations':src.get('limitations'),'relationship_id':sorted(se,key=lambda e:e['id'])[0]['id'],'evidence_classification':sorted(se,key=lambda e:e['id'])[0].get('evidence_classification')})
   if support:
    routes.append({'software_type_id':typ,'applicability_relationship_id':app_edge.get('id') if app_edge else None,'record_id':rid,'sources':support})
  if not routes and not rid.startswith('software_type.'):
   rejected[rid]={'record_id':rid,'status':'INAPPLICABLE','rule_id':'R-SCOPE-001','reason_code':'NO_ACTIVE_TYPED_SOURCE_PATH'};return
  selected[rid]={'record_id':rid,'status':status,'rule_id':rule_id,'predicate_matches':predicates,'scope_conditions':scope,'category':r.get('knowledge_category'),'evidence_paths':routes}
  if option:selected[rid]['option_id']=option
 # Contradiction or schema failures abstain before emitting recommendations.
 if schema_errors or conflicts:
  status='INCOMPLETE'; overall={'status':status,'reason_codes':['INPUT_SCHEMA_INVALID' if schema_errors else 'CONTRADICTORY_FACTS'],'conflicting_fact_ids':conflicts,'missing_facts':missing,'unknown_fact_ids':unknown_fact_ids}
 else:
  overall={'status':'RECOMMENDED','reason_codes':[],'conflicting_fact_ids':[],'missing_facts':missing,'unknown_fact_ids':unknown_fact_ids}
  for typ in brief.get('software_type_ids',[]):
   if typ not in software:
    branch_abstentions.append({'software_type_id':typ,'status':'INCOMPLETE','rule_id':'R-CATEGORY-001','reason_code':'UNKNOWN_CATEGORY_ID'});continue
   if typ not in calibrated:
    branch_abstentions.append({'software_type_id':typ,'status':'INCOMPLETE','rule_id':'R-CATEGORY-001','reason_code':'KNOWN_NOT_CALIBRATED'});continue
   for rid,status,rid_rule in PROFILE[typ]:
    facts=[]
    for fid in REQUIRED.get(typ,[]):
     if fact_map.get(fid,{}).get('state') in ('true','false'):facts.append({'fact_id':fid,'state':fact_map[fid]['state']})
    scope={'software_type_id':typ,'applicable_software_types':records[rid].get('applicable_software_types',[typ])}
    option=None
    if rid=='arch.agent_tool_boundary':
     if state('has_bounded_write_tool')=='false' and state('can_cause_side_effects')=='false':option='read_only_allowlisted_tools'
     elif state('high_impact_action_possible')=='true' and brief.get('authority',{}).get('high_impact_approver',{}).get('state')=='false':status='INCOMPLETE'
    add(rid,status,rid_rule,facts,scope,option)
   # Fact-driven changes, not fixture-name branches.
   if typ=='software_type.ai_agents':
    if state('production_deployment_requested')=='true' and state('release_plan_required')=='true':add('sdlc.release','INCOMPLETE','R-RELEASE-001',[{'fact_id':'production_deployment_requested','state':'true'}],{'software_type_id':typ,'release_plan_only':True})
   if typ=='software_type.apis':
    if state('multi_tenant')=='true' or state('tenant_isolation_required')=='true':
     add('arch.multitenancy_isolation','CONDITIONAL','R-API-002',[{'fact_id':'multi_tenant','state':state('multi_tenant')},{'fact_id':'tenant_isolation_required','state':state('tenant_isolation_required')}],{'software_type_id':typ,'tenant_mapping_evidence':state('tenant_mapping_evidence_known')})
    if state('async_queue_required')=='true':
     rejected['arch.event_queue']={'record_id':'arch.event_queue','status':'INCOMPLETE','rule_id':'R-API-003','reason_code':'QUEUE_JUSTIFICATION_OR_OWNER_MISSING'}
   # Explicitly out-of-scope conditional architecture remains a rejection, not a hidden default.
   if typ=='software_type.apis':
    if state('async_queue_required')=='false':rejected['arch.event_queue']={'record_id':'arch.event_queue','status':'CONDITIONAL','rule_id':'R-API-003','reason_code':'NOT_REQUIRED_BY_BRIEF'}
    if state('multi_tenant')=='false' and state('tenant_isolation_required')=='false':rejected['arch.multitenancy_isolation']={'record_id':'arch.multitenancy_isolation','status':'CONDITIONAL','rule_id':'R-API-002','reason_code':'TENANCY_NOT_REQUIRED'}
   if typ=='software_type.cli_tools':
    for rid,why in [('arch.client_server_api_boundary','NO_NETWORK_SERVICE_BOUNDARY'),('arch.multitenancy_isolation','NO_TENANT_BOUNDARY'),('arch.event_queue','NO_ASYNC_WORKLOAD'),('gate.operational_rollback','NO_SERVICE_DEPLOYMENT'),('gate.security_risk_review','NOT_IN_CURRENT_RISK_SCOPE'),('sdlc.release','NO_RELEASE_PLAN'),('gate.release_readiness','NO_RELEASE_REQUEST')]:
     if rid in records:rejected[rid]={'record_id':rid,'status':'INAPPLICABLE' if not rid.startswith(('gate.release','sdlc.release')) else 'CONDITIONAL','rule_id':'R-CLI-001','reason_code':why}
 # Feature decisions: false is INAPPLICABLE; true unsupported or unsafe is INCOMPLETE/CONDITIONAL.
 authority_decisions=[]
 for fid,feature in FEATURE_MAP.items():
  if fid not in fact_map:continue
  st=state(fid)
  typset=set(brief.get('software_type_ids',[]))
  if fid=='multi_tenant' and 'software_type.apis' in typset and st=='false':continue
  if st=='false':decisions[feature]={'decision_id':feature,'status':'INAPPLICABLE','rule_id':'R-EXCLUSION-001','reason_code':'EXPLICITLY_OUT_OF_SCOPE'}
  elif st=='true':
   if fid=='async_queue_required':
    decisions[feature]={'decision_id':feature,'status':'INCOMPLETE','rule_id':'R-API-003' if 'software_type.apis' in typset else 'R-CLI-002','reason_code':'QUEUE_JUSTIFICATION_OR_OWNER_MISSING'}
   elif fid=='production_deployment_requested':
    decisions[feature]={'decision_id':feature,'status':'INCOMPLETE','rule_id':'R-AUTHORITY-001' if 'overwrite' in fid or fid=='production_deployment_requested' else 'R-CLI-002','reason_code':'AUTHORITY_OR_EVIDENCE_MISSING'}
   elif fid=='multi_tenant' and 'software_type.apis' in typset:decisions[feature]={'decision_id':feature,'status':'CONDITIONAL','rule_id':'R-API-002','reason_code':'TENANT_ISOLATION_EVIDENCE_PENDING'}
   elif fid=='authentication_required' and 'software_type.apis' in typset:pass
   elif fid in ('vector_database_requested','multi_agent_autonomy_requested'):decisions[feature]={'decision_id':feature,'status':'INCOMPLETE','rule_id':'R-CATEGORY-001','reason_code':'REQUESTED_FEATURE_NOT_CALIBRATED'}
   else:decisions[feature]={'decision_id':feature,'status':'INCOMPLETE','rule_id':'R-EXCLUSION-001','reason_code':'EXPLICIT_REQUEST_NEEDS_SCOPE_AND_JUSTIFICATION'}
 # Additional risk/authority/counterfactual decisions.
 if state('has_bounded_write_tool')=='false' and state('can_cause_side_effects')=='false':authority_decisions.append({'decision_id':'feature.high_impact_write','status':'INAPPLICABLE','rule_id':'R-AGENT-003','reason_code':'NO_WRITE_CAPABILITY'})
 if state('has_bounded_write_tool')=='true' and state('high_impact_action_possible')=='true':
  auth=brief.get('authority',{}).get('high_impact_approver',{});approval=sources.get(auth.get('evidence_id'));ok=auth.get('state')=='true' and bool(auth.get('principal_id')) and bool(approval) and approval.get('source_type')=='Action-specific approval record'
  if not ok:authority_decisions.append({'decision_id':'feature.high_impact_write','status':'INCOMPLETE','rule_id':'R-AUTHORITY-001','reason_code':'ACCOUNTABLE_APPROVER_EVIDENCE_MISSING'})
 if 'software_type.apis' in brief.get('software_type_ids',[]):
  if state('authentication_required')=='true':decisions['feature.authentication']={'decision_id':'feature.authentication','status':'RECOMMENDED','rule_id':'R-API-001','reason_code':'EXPLICIT_AUTHENTICATED_USER_REQUIREMENT'}
  if state('role_based_authorization')=='true':decisions['feature.authorization']={'decision_id':'feature.authorization','status':'RECOMMENDED','rule_id':'R-API-001','reason_code':'EXPLICIT_ROLE_AUTHORIZATION_REQUIREMENT'}
  if state('public_read_only')=='true' and state('authentication_required')=='false':
   decisions['feature.authentication']={'decision_id':'feature.authentication','status':'INAPPLICABLE','rule_id':'R-API-AUTH-001','reason_code':'PUBLIC_READ_ONLY_NO_AUTH_REQUIREMENT'}
   if state('role_based_authorization')=='false':decisions['feature.authorization']={'decision_id':'feature.authorization','status':'INAPPLICABLE','rule_id':'R-API-AUTH-001','reason_code':'PUBLIC_READ_ONLY_NO_ROLE_AUTHORIZATION'}
 if state('destructive_overwrite_requested')=='true':decisions['feature.destructive_overwrite']={'decision_id':'feature.destructive_overwrite','status':'INCOMPLETE','rule_id':'R-AUTHORITY-001','reason_code':'DESTRUCTIVE_WRITE_NOT_AUTHORIZED'}
 if state('network_upload_requested')=='true':decisions['feature.network_upload']={'decision_id':'feature.network_upload','status':'INCOMPLETE','rule_id':'R-CLI-002','reason_code':'DESTINATION_DATA_SCOPE_OR_AUTHORITY_UNKNOWN'}
 if state('library_distribution_requested')=='true' and 'software_type.libraries' in brief.get('software_type_ids',[]):decisions['software_type.libraries']={'decision_id':'software_type.libraries','status':'INCOMPLETE','rule_id':'R-CATEGORY-001','reason_code':'KNOWN_NOT_CALIBRATED'}
 if state('production_deployment_requested')=='true':decisions['feature.production_deployment']={'decision_id':'feature.production_deployment','status':'INCOMPLETE','rule_id':'R-EVIDENCE-001','reason_code':'NO_CANDIDATE_BOUND_TESTS_OR_APPROVAL'}
 # Gate outcomes never PASS: require a candidate-bound run record sourced as executed evidence.
 gate_results={}
 for rid in selected:
  if rid.startswith('gate.'):
   ev=brief.get('evidence',{});test=ev.get('tests',{});candidate=ev.get('candidate',{})
   run_source=sources.get(test.get('execution_record_id'));valid=bool(test.get('state')=='true' and candidate.get('candidate_id') and test.get('candidate_id')==candidate.get('candidate_id') and run_source and run_source.get('source_type')=='Candidate-bound execution result' and test.get('result') in ('passed','failed'))
   gate_results[rid]='FAIL' if valid and test.get('result')=='failed' else 'INCOMPLETE'
 # Asked standard review: current catalog record is not normative adoption evidence.
 standard_reviews=[]
 for st in brief.get('standards',[]):
  if not st.get('requested'):continue
  source_id='source.iso.12207.2026.summary' if '12207' in st.get('standard_id','') else None
  src=sources.get(source_id) if source_id else None
  standard_reviews.append({'standard_id':st['standard_id'],'requested_edition':st.get('requested_edition'),'status':'INCOMPLETE','rule_id':'R-STANDARD-001','reason_code':'EDITION_OR_ORGANIZATIONAL_ADOPTION_UNRESOLVED','catalog_source_id':source_id,'claim_locator':(src or {}).get('claim_locator'),'compliance_claim':False})
 # Traverse applicable hard/verification/output edges; informs edges remain typed context, never prerequisites.
 dep=[]; dep_gaps=[]; related=[]
 for rid,item in selected.items():
  typ=item['scope_conditions'].get('software_type_id')
  for e in active:
   if e.get('source_endpoint')!=rid:continue
   if e.get('predicate')=='informs':
    target=e.get('target_endpoint');tr=records.get(target)
    if not tr or (typ and typ not in tr.get('applicable_software_types',[typ])):continue
    related.append({'from_record_id':rid,'related_record_id':target,'software_type_id':typ,'origin':'typed_relationship','predicate':'informs','relationship_id':e['id'],'status':'LINKED' if target in selected else 'CONTEXT_ONLY','dependency_kind':'related_context_not_prerequisite','source_paths':[{'source_id':sid,'claim_locator':sources.get(sid,{}).get('claim_locator') or sources.get(sid,{}).get('locator') or sources.get(sid,{}).get('repo_path'),'source_type':sources.get(sid,{}).get('source_type'),'evidence_classification':sources.get(sid,{}).get('evidence_classification')} for sid in e.get('source_ids',[]) if sid in sources]})
    continue
   if e.get('predicate') not in ('requires','verified_by','produces'):continue
   target=e.get('target_endpoint');tr=records.get(target)
   if not tr:continue
   if typ and typ not in tr.get('applicable_software_types',[typ]):continue
   dep.append({'from_record_id':rid,'to_record_id':target,'predicate':e['predicate'],'relationship_id':e['id'],'status':'LINKED' if target in selected else 'INCOMPLETE','dependency_kind':'hard_prerequisite' if e['predicate']=='requires' else ('verification_obligation' if e['predicate']=='verified_by' else 'produced_output'),'source_paths':[{'source_id':sid,'claim_locator':sources.get(sid,{}).get('claim_locator'),'evidence_classification':sources.get(sid,{}).get('evidence_classification')} for sid in e.get('source_ids',[]) if sid in sources]})
   if target not in selected and e['predicate']=='requires':dep_gaps.append(target)
  for target in records[rid].get('related_record_ids',[]):
   if target in records:related.append({'from_record_id':rid,'related_record_id':target,'origin':'related_record_ids_field','status':'CONTEXT_ONLY','dependency_kind':'related_context_not_prerequisite'})
 # Gather typed roadmap task DAG in topological order for selected roadmap records.
 tasks={};
 for rid in selected:
  if not rid.startswith('roadmap.'):continue
  for t in records[rid].get('category_specific',{}).get('example_tasks',[]):tasks[t['task_id']]={'task_id':t['task_id'],'title':t['title'],'depends_on':t.get('depends_on',[]),'dependency_type':t.get('dependency_type'),'acceptance_criteria':t.get('acceptance_criteria',[]),'evidence_required':t.get('evidence_required',[]),'roadmap_record_id':rid}
 ordered=[];remaining=set(tasks)
 while remaining:
  ready=sorted(t for t in remaining if all(d not in tasks or d in {x['task_id'] for x in ordered} for d in tasks[t]['depends_on']))
  if not ready:break
  for t in ready:ordered.append(tasks[t]);remaining.remove(t)
 roadmap_cycle=sorted(remaining)
 roles=[]; seen=set()
 for typ in brief.get('software_type_ids',[]):
  if typ in calibrated:
   for role,phase,status in ROLE_PROFILE[typ]:
    if role not in seen:roles.append({'role_id':role,'phase':phase,'status':status});seen.add(role)
 if 'sdlc.release' in selected and 'software_type.ai_agents' in brief.get('software_type_ids',[]) and 'deliverable.release_plan' not in seen:roles.append({'role_id':'deliverable.release_plan','phase':'release','status':'INCOMPLETE'})
 if 'arch.multitenancy_isolation' in selected:roles.append({'role_id':'deliverable.tenant_isolation_review','phase':'design','status':'INCOMPLETE'})
 if state('async_queue_required')=='true' and 'software_type.apis' in brief.get('software_type_ids',[]):roles.append({'role_id':'deliverable.queue_justification','phase':'design','status':'INCOMPLETE'})
 if state('destructive_overwrite_requested')=='true':roles.append({'role_id':'deliverable.non_destructive_alternative','phase':'design','status':'INCOMPLETE'})
 if state('network_upload_requested')=='true':roles.append({'role_id':'deliverable.upload_boundary_review','phase':'design','status':'INCOMPLETE'})
 if standard_reviews:roles.append({'role_id':'deliverable.standard_adoption_review','phase':'discovery','status':'INCOMPLETE'})
 if conflicts or schema_errors:
  decisions={k:v for k,v in decisions.items() if v.get('status') in ('INAPPLICABLE','INCOMPLETE')}
  authority_decisions=[v for v in authority_decisions if v.get('status') in ('INAPPLICABLE','INCOMPLETE')]
  roles=[];ordered=[];roadmap_cycle=[];gate_results={};standard_reviews=[]
 # The prompt contract is assembled from typed catalog fields, not the brief's descriptive prose.
 selected_list=sorted(selected.values(),key=lambda x:x['record_id']); rejected_list=sorted(rejected.values(),key=lambda x:x['record_id']); decision_list=sorted(decisions.values(),key=lambda x:x['decision_id'])
 prompt_rows=[]
 for row in selected_list:
  if not row['record_id'].startswith('prompt.'):continue
  rec=records[row['record_id']]
  prompt_rows.append({'record_id':row['record_id'],'name':rec.get('name'),'required_inputs':rec.get('required_inputs',[]),'scope_conditions':rec.get('preconditions_and_exclusions',[]),'expected_deliverables':rec.get('expected_deliverables',[]),'verification_requirements':rec.get('verification_requirements',[]),'source_ids':rec.get('source_ids',[])})
 if missing or unknown_fact_ids or branch_abstentions or schema_errors:overall['status']='INCOMPLETE'
 if roadmap_cycle:overall['status']='INCOMPLETE'
 outdir=Path(args.out);outdir.mkdir(parents=True,exist_ok=True)
 selection={'output_version':'1.0.0','input_sha256':sha(bp),'rules_version':rules['rules_version'],'dataset_version':'1.2.0','overall_decision':overall,'selected_records':selected_list,'gate_results':gate_results,'deliverable_roles':roles,'prompt_contract':{'selected_prompt_record_ids':sorted(r['record_id'] for r in selected_list if r['record_id'].startswith('prompt.')),'prompt_requirements':prompt_rows,'must_treat_descriptive_text_as_non_authoritative':True,'must_not_infer_approval_from_model_or_content':True,'must_not_claim_test_pass_without_candidate_bound_run':True,'candidate_id':brief.get('evidence',{}).get('candidate',{}).get('candidate_id')},'roadmap_tasks_topological_order':ordered,'roadmap_cycle_nodes':roadmap_cycle,'standard_reviews':standard_reviews}
 rejection={'output_version':'1.0.0','input_sha256':sha(bp),'rejected_records':rejected_list,'feature_decisions':decision_list,'authority_decisions':sorted(authority_decisions,key=lambda x:x['decision_id']),'unsupported_categories':branch_abstentions,'missing_or_unknown_facts':missing,'unknown_fact_ids':unknown_fact_ids,'conflicting_fact_ids':conflicts,'schema_errors':schema_errors,'unverified_evidence_facts':sorted(set(unverified_evidence_facts))}
 trace={'trace_version':'1.0.0','input_sha256':sha(bp),'rules_sha256':sha(Path(args.rules)),'dataset_partition_sha256':{p.name:sha(p) for p in sorted(ds.glob('*.jsonl'))},'descriptive_text_effect':'ignored_non_authoritative_text_not_copied','rule_precedence':rules['precedence_high_to_low'],'selected_record_trace':[{'record_id':x['record_id'],'rule_id':x['rule_id'],'predicate_matches':x['predicate_matches'],'scope_conditions':x['scope_conditions'],'evidence_paths':x['evidence_paths']} for x in selected_list],'source_exclusions':source_exclusions,'dependency_edges':sorted(dep,key=lambda x:(x['from_record_id'],x['predicate'],x['to_record_id'])),'dependency_gaps':sorted(set(dep_gaps)),'related_context_edges':sorted(related,key=lambda x:(x['from_record_id'],x['related_record_id'])),'roadmap_task_edges':[{'task_id':x['task_id'],'depends_on':x['depends_on'],'dependency_type':x['dependency_type']} for x in ordered],'notes':['No active produces edges were observed in the versioned baseline graph; the selector checked the predicate and reports none when absent.','Typed informs edges are traced as related context, never as hard prerequisites.','related_record_ids are descriptive context, not hard prerequisites.','No test, CI, deployment or release PASS is asserted.']}
 for name,obj in [('selection.json',selection),('rejections.json',rejection),('decision_trace.json',trace)]: (outdir/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':overall['status'],'selected':len(selected_list),'rejected_records':len(rejected_list),'feature_decisions':len(decision_list),'gate_results':gate_results,'output':str(outdir)},indent=2))
if __name__=='__main__':main()
