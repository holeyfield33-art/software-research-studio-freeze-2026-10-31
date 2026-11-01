#!/usr/bin/env python3
"""Freeze 003R oracle from the immutable 003 fixtures plus separately authored CF decisions.
This script never reads selector outputs; run before selector implementation.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; FIX=ROOT/'fixtures'; OUT=ROOT/'oracles'; DATA=ROOT/'dataset/v1'
OUT.mkdir(exist_ok=True)
FAMILY_RULE={
 'sdlc_stages':'R-BASE-001','engineering_practices':'R-PRACTICE-001','verification_gates':'R-EVIDENCE-001',
 'roadmap_patterns':'R-ROADMAP-001','prompt_patterns':'R-PROMPT-001','reference_projects':'R-EXAMPLE-001',
 'software_types':'R-TYPE-BASE-001','architecture_patterns':'R-ARCH-001'}
def part_for(rid):
 if rid.startswith('software_type.'):return 'software_types'
 if rid.startswith('arch.'):return 'architecture_patterns'
 if rid.startswith('practice.'):return 'engineering_practices'
 if rid.startswith('sdlc.'):return 'sdlc_stages'
 if rid.startswith('gate.'):return 'verification_gates'
 if rid.startswith('roadmap.'):return 'roadmap_patterns'
 if rid.startswith('prompt.'):return 'prompt_patterns'
 if rid.startswith('reference.'):return 'reference_projects'
 raise ValueError(rid)
def rule_for(rid,typ):
 if rid=='arch.agent_tool_boundary':return 'R-AGENT-001'
 if rid in ('arch.minimal_viable_structure',):return 'R-CLI-001' if typ.endswith('cli_tools') else 'R-API-001'
 if rid.startswith('arch.client_server') or rid=='arch.layered_modular':return 'R-API-001'
 if rid=='practice.threat_modeling':return 'R-AGENT-001' if typ.endswith('ai_agents') else 'R-API-004'
 if rid=='practice.test_strategy':return 'R-PRACTICE-002'
 if rid=='practice.dependency_secret_handling':return 'R-CLI-002'
 if rid=='practice.version_control_review':return 'R-PRACTICE-001'
 if rid=='practice.requirements_traceability':return 'R-PRACTICE-001'
 if rid=='practice.ci_reproducible_release':return 'R-PRACTICE-001'
 if rid.startswith('prompt.threat_model'):return 'R-AGENT-001' if typ.endswith('ai_agents') else 'R-API-004'
 if rid=='sdlc.release':return 'R-RELEASE-001'
 return FAMILY_RULE[part_for(rid)]
def record_index():
 result={}
 for p in DATA.glob('*.jsonl'):
  for line in p.read_text().splitlines():
   if line.strip():
    r=json.loads(line);result[r['id']]=r
 return result
RECS=record_index()
def source_task_ids(rid):
 tasks=RECS[rid].get('category_specific',{}).get('example_tasks',[])
 return [t['task_id'] for t in tasks]
def topological_task_ids(items):
 tasks={}
 for item in items:
  rid=item['record_id']
  if rid.startswith('roadmap.'):
   for task in RECS[rid].get('category_specific',{}).get('example_tasks',[]):tasks[task['task_id']]=task
 ordered=[];remaining=set(tasks)
 while remaining:
  ready=sorted(t for t in remaining if all(d not in tasks or d in {x['task_id'] for x in ordered} for d in tasks[t].get('depends_on',[])))
  if not ready:raise ValueError('cycle in expected roadmap tasks')
  for t in ready:ordered.append({'task_id':t});remaining.remove(t)
 return [x['task_id'] for x in ordered]
def make_base(folder,typ):
 f=FIX/folder
 selected=json.loads((f/'expected_selection.json').read_text())['selected_records']
 rejects=json.loads((f/'expected_rejections.json').read_text())
 deliver=json.loads((f/'expected_deliverables.json').read_text())
 items=[{'record_id':x['record_id'],'status':x['status'],'rule_id':rule_for(x['record_id'],typ)} for x in selected]
 rejected=[]
 for x in rejects.get('rejected_records',[]):
  r=x.get('status','CONDITIONAL')
  if typ.endswith('cli_tools'):rule='R-CLI-001'
  elif x['record_id']=='arch.event_queue':rule='R-API-003'
  elif x['record_id']=='arch.multitenancy_isolation':rule='R-API-002'
  elif x['record_id'].startswith('gate.') or x['record_id'].startswith('sdlc.release'):rule='R-CLI-001'
  else:rule='R-SCOPE-001'
  if typ.endswith('cli_tools'):reason={'arch.event_queue':'NO_ASYNC_WORKLOAD','arch.multitenancy_isolation':'NO_TENANT_BOUNDARY','arch.client_server_api_boundary':'NO_NETWORK_SERVICE_BOUNDARY','gate.operational_rollback':'NO_SERVICE_DEPLOYMENT','gate.security_risk_review':'NOT_IN_CURRENT_RISK_SCOPE','sdlc.release':'NO_RELEASE_PLAN','gate.release_readiness':'NO_RELEASE_REQUEST'}.get(x['record_id'],'INAPPLICABLE_BY_SCOPE')
  else:reason={'arch.event_queue':'NOT_REQUIRED_BY_BRIEF','arch.multitenancy_isolation':'TENANCY_NOT_REQUIRED'}.get(x['record_id'],'INAPPLICABLE_BY_SCOPE')
  rejected.append({'record_id':x['record_id'],'status':r,'rule_id':rule,'reason_code':reason})
 features=[]
 for x in rejects.get('rejected_requirements',[]):
  features.append({'decision_id':x['requirement_id'],'status':'INAPPLICABLE','rule_id':'R-EXCLUSION-001','reason_code':'EXPLICITLY_OUT_OF_SCOPE'})
 if typ=='software_type.apis':
  features.extend([{'decision_id':'feature.authentication','status':'RECOMMENDED','rule_id':'R-API-001','reason_code':'EXPLICIT_AUTHENTICATED_USER_REQUIREMENT'},{'decision_id':'feature.authorization','status':'RECOMMENDED','rule_id':'R-API-001','reason_code':'EXPLICIT_ROLE_AUTHORIZATION_REQUIREMENT'}])
 gates={g:'INCOMPLETE' for g in json.loads((f/'expected_selection.json').read_text()).get('gate_outcomes',{})}
 roles=[{'role_id':x['deliverable_id'],'phase':x['phase'],'status':x['status']} for x in deliver['deliverables']]
 roadmap=topological_task_ids(items)
 authority=[]
 if typ=='software_type.ai_agents':authority=[{'decision_id':'feature.high_impact_write','status':'INCOMPLETE','rule_id':'R-AUTHORITY-001','reason_code':'ACCOUNTABLE_APPROVER_EVIDENCE_MISSING'}]
 return {'case_path':f'selection_cases/base_{folder}/brief.json','software_type_ids':[typ],'selected_records':sorted(items,key=lambda x:x['record_id']),'rejected_records':sorted(rejected,key=lambda x:x['record_id']),'feature_decisions':sorted(features,key=lambda x:x['decision_id']),'authority_decisions':authority,'standard_reviews':[],'gate_results':gates,'deliverable_roles':roles,'roadmap_task_ids':roadmap,'prompt_record_ids':sorted(x['record_id'] for x in items if x['record_id'].startswith('prompt.')),'descriptive_text_effect':'ignored'}
base={
 'base_ai_agent':make_base('ai_agent','software_type.ai_agents'),
 'base_authenticated_api':make_base('authenticated_api','software_type.apis'),
 'base_offline_cli':make_base('offline_cli','software_type.cli_tools')}
# Independently specified counterfactual contract: exact inherited sets plus explicit deltas.
cf={
 'agent_no_write_tool':{'base':'base_ai_agent','selected_add':[],'selected_remove':[],'selected_status':{'arch.agent_tool_boundary':'RECOMMENDED'},'rejected_add':[],'rejected_remove':[],'feature_set':{},'feature_rule':'','authority_set':{'feature.high_impact_write':'INAPPLICABLE'},'roles_add':[],'task_roles_add':[]},
 'agent_write_no_approver':{'base':'base_ai_agent','selected_add':[],'selected_remove':[],'selected_status':{'arch.agent_tool_boundary':'INCOMPLETE'},'rejected_add':[],'rejected_remove':[],'feature_set':{},'feature_rule':'','authority_set':{'feature.high_impact_write':'INCOMPLETE'},'roles_add':[],'task_roles_add':[]},
 'agent_production_without_candidate_tests':{'base':'base_ai_agent','selected_add':[{'record_id':'sdlc.release','status':'INCOMPLETE','rule_id':'R-RELEASE-001'}],'selected_remove':[],'selected_status':{},'rejected_add':[],'rejected_remove':[],'feature_set':{'feature.production_deployment':'INCOMPLETE'},'feature_rule':'R-EVIDENCE-001','authority_set':{},'standard_reviews_add':[],'roles_add':[{'role_id':'deliverable.release_plan','phase':'release','status':'INCOMPLETE'}],'task_roles_add':[]},
 'api_public_read_only':{'base':'base_authenticated_api','selected_add':[],'selected_remove':[],'selected_status':{},'rejected_add':[],'rejected_remove':[],'feature_set':{'feature.authentication':'INAPPLICABLE','feature.authorization':'INAPPLICABLE'},'feature_rules':{'feature.authentication':'R-API-AUTH-001','feature.authorization':'R-API-AUTH-001'},'feature_reasons':{'feature.authentication':'PUBLIC_READ_ONLY_NO_AUTH_REQUIREMENT','feature.authorization':'PUBLIC_READ_ONLY_NO_ROLE_AUTHORIZATION'},'roles_add':[],'task_roles_add':[]},
 'api_explicit_multitenant':{'base':'base_authenticated_api','selected_add':[{'record_id':'arch.multitenancy_isolation','status':'CONDITIONAL','rule_id':'R-API-002'}],'selected_remove':[],'selected_status':{},'rejected_add':[],'rejected_remove':['arch.multitenancy_isolation'],'feature_set':{'feature.multitenancy':'CONDITIONAL'},'feature_rule':'R-API-002','roles_add':[{'role_id':'deliverable.tenant_isolation_review','phase':'design','status':'INCOMPLETE'}],'task_roles_add':[]},
 'api_queue_without_justification':{'base':'base_authenticated_api','selected_add':[],'selected_remove':[],'selected_status':{},'rejected_add':[{'record_id':'arch.event_queue','status':'INCOMPLETE','rule_id':'R-API-003','reason_code':'QUEUE_JUSTIFICATION_OR_OWNER_MISSING'}],'rejected_remove':['arch.event_queue'],'feature_set':{'feature.queue':'INCOMPLETE'},'feature_rule':'R-API-003','roles_add':[{'role_id':'deliverable.queue_justification','phase':'design','status':'INCOMPLETE'}],'task_roles_add':[]},
 'api_changed_standard_edition':{'base':'base_authenticated_api','selected_add':[],'selected_remove':[],'selected_status':{},'rejected_add':[],'rejected_remove':[],'feature_set':{},'feature_rule':'','authority_set':{},'standard_reviews_add':[{'standard_id':'ISO/IEC/IEEE 12207','requested_edition':'2017','status':'INCOMPLETE','rule_id':'R-STANDARD-001','reason_code':'EDITION_OR_ORGANIZATIONAL_ADOPTION_UNRESOLVED','catalog_source_id':'source.iso.12207.2026.summary','compliance_claim':False}],'roles_add':[{'role_id':'deliverable.standard_adoption_review','phase':'discovery','status':'INCOMPLETE'}],'task_roles_add':[]},
 'cli_destructive_overwrite_unauthorized':{'base':'base_offline_cli','selected_add':[],'selected_remove':[],'selected_status':{},'rejected_add':[],'rejected_remove':[],'feature_set':{'feature.destructive_overwrite':'INCOMPLETE'},'feature_rule':'R-AUTHORITY-001','roles_add':[{'role_id':'deliverable.non_destructive_alternative','phase':'design','status':'INCOMPLETE'}],'task_roles_add':[]},
 'cli_network_upload_unknown_scope':{'base':'base_offline_cli','selected_add':[],'selected_remove':[],'selected_status':{},'rejected_add':[],'rejected_remove':[],'feature_set':{'feature.network_upload':'INCOMPLETE'},'feature_rule':'R-CLI-002','roles_add':[{'role_id':'deliverable.upload_boundary_review','phase':'design','status':'INCOMPLETE'}],'task_roles_add':[]},
 'cli_library_distribution_no_service':{'base':'base_offline_cli','selected_add':[],'selected_remove':[],'selected_status':{},'rejected_add':[],'rejected_remove':[],'feature_set':{'software_type.libraries':'INCOMPLETE','feature.service_deployment':'INAPPLICABLE'},'feature_rules':{'software_type.libraries':'R-CATEGORY-001','feature.service_deployment':'R-EXCLUSION-001'},'authority_set':{},'standard_reviews_add':[],'roles_add':[],'task_roles_add':[]}
}
for name,delta in cf.items():
 b=base[delta['base']]; sel={x['record_id']:dict(x) for x in b['selected_records']};rej={x['record_id']:dict(x) for x in b['rejected_records']}
 for rid in delta['selected_remove']:sel.pop(rid,None)
 for x in delta['selected_add']:sel[x['record_id']]=dict(x)
 for rid,status in delta['selected_status'].items():
  if rid not in sel:raise ValueError((name,'status target absent',rid))
  sel[rid]['status']=status
 for rid in delta['rejected_remove']:rej.pop(rid,None)
 for x in delta['rejected_add']:rej[x['record_id']]=dict(x)
 features={x['decision_id']:dict(x) for x in b['feature_decisions']}
 for did,status in delta.get('feature_set',{}).items():
  rule=delta.get('feature_rules',{}).get(did,delta.get('feature_rule',''))
  defaults={('feature.multitenancy','CONDITIONAL'):'TENANT_ISOLATION_EVIDENCE_PENDING',('feature.queue','INCOMPLETE'):'QUEUE_JUSTIFICATION_OR_OWNER_MISSING',('feature.production_deployment','INCOMPLETE'):'NO_CANDIDATE_BOUND_TESTS_OR_APPROVAL',('feature.destructive_overwrite','INCOMPLETE'):'DESTRUCTIVE_WRITE_NOT_AUTHORIZED',('feature.network_upload','INCOMPLETE'):'DESTINATION_DATA_SCOPE_OR_AUTHORITY_UNKNOWN',('software_type.libraries','INCOMPLETE'):'KNOWN_NOT_CALIBRATED',('feature.service_deployment','INAPPLICABLE'):'EXPLICITLY_OUT_OF_SCOPE'}
  reason=delta.get('feature_reasons',{}).get(did,defaults.get((did,status),status))
  features[did]={'decision_id':did,'status':status,'rule_id':rule,'reason_code':reason}
 authority={x['decision_id']:dict(x) for x in b.get('authority_decisions',[])}
 for did,status in delta.get('authority_set',{}).items():authority[did]={'decision_id':did,'status':status,'rule_id':'R-AGENT-003' if status=='INAPPLICABLE' else 'R-AUTHORITY-001','reason_code':'NO_WRITE_CAPABILITY' if status=='INAPPLICABLE' else 'ACCOUNTABLE_APPROVER_EVIDENCE_MISSING'}
 standards=list(b.get('standard_reviews',[]))+delta.get('standard_reviews_add',[])
 for review in standards:
  sid=review.get('catalog_source_id')
  if sid in RECS:review.setdefault('claim_locator',RECS[sid].get('claim_locator'))
 gates=dict(b['gate_results'])
 roles=list(b['deliverable_roles'])+delta['roles_add']
 tasks=list(b['roadmap_task_ids'])
 base[name]={'case_path':f'selection_cases/{name}/brief.json','software_type_ids':json.loads((ROOT/'selection_cases'/name/'brief.json').read_text())['software_type_ids'],'selected_records':sorted(sel.values(),key=lambda x:x['record_id']),'rejected_records':sorted(rej.values(),key=lambda x:x['record_id']),'feature_decisions':sorted(features.values(),key=lambda x:x['decision_id']),'authority_decisions':sorted(authority.values(),key=lambda x:x['decision_id']),'standard_reviews':standards,'gate_results':gates,'deliverable_roles':roles,'roadmap_task_ids':tasks,'prompt_record_ids':sorted(x['record_id'] for x in sel.values() if x['record_id'].startswith('prompt.')),'descriptive_text_effect':'ignored'}
negative=json.loads((FIX/'conflict_missing_evidence'/'negative_cases.json').read_text())
obj={'oracle_version':'1.0.0','frozen_before_selector_implementation':True,'independent_basis':'Base selections copied from immutable 003 fixture contracts, then assigned stable 003R rule IDs; ten counterfactuals manually specified from structured facts and directive acceptance criteria. No selector outputs were read.','base_and_counterfactual_cases':base,'inherited_negative_controls':negative['cases'],'mutation_controls':['flip_recommended_status','reverse_typed_rejection_reason','inject_fake_test_or_deployment_pass','contradict_descriptive_text_with_authoritative_facts']}
(OUT/'frozen-oracle.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'frozen':True,'cases':len(base),'base':3,'counterfactual':len(cf),'negative_controls':len(negative['cases'])},indent=2))
