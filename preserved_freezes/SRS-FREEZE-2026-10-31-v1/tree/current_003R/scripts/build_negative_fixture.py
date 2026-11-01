#!/usr/bin/env python3
"""Create deterministic negative-control fixture data from the current 003 catalog."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dataset/v1'
OUT=ROOT/'fixtures/conflict_missing_evidence'
OUT.mkdir(parents=True,exist_ok=True)
def rows(name): return [json.loads(x) for x in (DATA/(name+'.jsonl')).read_text().splitlines() if x.strip()]
parts=['software_types','engineering_practices','sdlc_stages','architecture_patterns','prompt_patterns','roadmap_patterns','verification_gates','reference_projects']
records={r['id']:r for p in parts for r in rows(p)}
sources={r['id']:r for r in rows('sources')}
rels=[r for r in rows('relationships') if r.get('status','active')!='superseded']
edges={(e['source_endpoint'],e['target_endpoint'],e['predicate']):e for e in rels}
fixture='conflict_missing_evidence'
root_type='software_type.apis'
selected_ids=[root_type,'arch.minimal_viable_structure','gate.unit_integration_execution','gate.release_readiness']
brief={
 'fixture_id':fixture,
 'description':'Negative controls for source-scope mismatch, standard-edition currency, missing candidate-bound test evidence, apparently conflicting architecture guidance, and unknown requirements. This is not a product recommendation. No tests, CI, or release were executed.',
 'software_type_ids':[root_type],
 'attributes':{'authenticated_api':True,'mobile_application':False,'current_standard_verified':True,'organization_standard_adoption_known':False,'candidate_identity_available':False,'test_execution_artifact_available':False,'source_guidance_conflicts':True},
 'available_inputs':{'target_category':'authenticated API','catalog_record':'ISO/IEC/IEEE 12207:2026 status and abstract','pinned_test_source':'FastAPI test source and workflow configuration'},
 'missing_inputs':['organization standard adoption','normative clauses reviewed','candidate identity','actual test execution artifact','project-specific architecture workload and team evidence','project-specific workload and organization evidence'],
 'prohibited_features':['assert 12207-2017 is current','claim tests passed from source/configuration presence','apply mobile-only evidence to an API','select a universal architecture winner','auto-map unknown requirements'],
 'evidence':{'candidate_id':None,'test_execution_artifact':None,'approval_record':None},
 'acceptance_boundary':'Expected output is conditional selection and INCOMPLETE gate states; no compliance, test-pass, release, or universal architecture conclusion is allowed.'
}
selected=[]
for rid in selected_ids:
 status='RECOMMENDED' if rid==root_type else ('CONDITIONAL' if rid=='arch.minimal_viable_structure' else 'INCOMPLETE')
 unresolved=[]
 if rid=='arch.minimal_viable_structure': unresolved=['project-specific workload and organization evidence']
 if rid.startswith('gate.'): unresolved=['candidate identity','actual test execution artifact']
 selected.append({'record_id':rid,'status':status,'reason':{'software_type.apis':'The target is an authenticated network API; this category does not resolve feature or architecture choices.','arch.minimal_viable_structure':'AWS workload-segmentation advice and Twelve-Factor process-state guidance have different scopes; choose only with project evidence.','gate.unit_integration_execution':'The test file and workflow exist, but no candidate-bound run record is supplied.','gate.release_readiness':'No candidate identity, completed gate evidence, or release approval is supplied.'}[rid],'branch_condition':{'all_true':[],'all_false':[]},'unresolved_inputs':unresolved})

def path_for(rid,sid):
 if rid==root_type: return [root_type,sid],['supported_by']
 pred='exemplified_by' if records[rid]['knowledge_category']=='reference_projects' else 'applies_to'
 key=(root_type,rid,pred)
 if key not in edges: raise SystemExit(f'missing applicability edge {key}')
 if (rid,sid,'supported_by') not in edges: raise SystemExit(f'missing provenance edge {(rid,sid,"supported_by")}')
 return [root_type,rid,sid],[pred,'supported_by']
traces=[]
for rid in selected_ids:
 r=records[rid]
 sid=next((s for s in r['source_ids'] if s in sources),None)
 if not sid: raise SystemExit('no source for '+rid)
 src=sources[sid]
 path,preds=path_for(rid,sid)
 cls='observed_repository_file' if 'repository' in src.get('source_type','').lower() or 'test source' in src.get('source_type','').lower() or 'workflow' in src.get('source_type','').lower() else ('synthesis' if 'synthesis' in r.get('evidence_classification','').lower() else 'documented_guidance')
 traces.append({'knowledge_record_id':rid,'source_id':sid,'path':path,'predicates':preds,'claim_locator':src['claim_locator'],'evidence_classification':cls})
neg_cases={
 'fixture_id':fixture,
 'cases':[
  {'case_id':'mobile_source_cannot_support_api_claim','case_type':'stack_mismatch','expected_status':'INAPPLICABLE','evidence_source_ids':['source.mobile_applications.01'],'details':{'target_software_type_id':root_type,'source_claimed_scope':'Android/native mobile-app guidance','selection_policy':'Do not infer API behavior from a different software stack.'}},
  {'case_id':'superseded_edition_without_adoption','case_type':'superseded_standard','expected_status':'INCOMPLETE','evidence_source_ids':['source.iso.12207.2026.summary'],'details':{'claimed_current_edition':'ISO/IEC/IEEE 12207:2017','catalogued_current_edition':'ISO/IEC/IEEE 12207:2026','organization_adoption_known':False,'full_normative_text_reviewed':False}},
  {'case_id':'repository_test_source_without_run','case_type':'missing_test_execution','expected_status':'INCOMPLETE','evidence_source_ids':['source.fastapi.tests','source.fastapi.ci'],'details':{'gate_id':'gate.unit_integration_execution','candidate_id':None,'test_execution_artifact':None,'workflow_configuration_is_execution':False,'expected_gate_outcome':'INCOMPLETE'}},
  {'case_id':'source_specific_guidance_is_not_a_universal_default','case_type':'source_tension','expected_status':'CONDITIONAL','evidence_source_ids':['source.aws.segment_workload','source.12factor.processes'],'details':{'architecture_record_id':'arch.minimal_viable_structure','decision_policy':'context_specific_options_only','rule':'Keep AWS workload segmentation and Twelve-Factor process-state guidance within their own scopes; neither independently proves a universal architecture choice.'}},
  {'case_id':'unknown_requirement_abstains','case_type':'unknown_requirement','expected_status':'INCOMPLETE','evidence_source_ids':['source.github.copilot_task_practices'],'details':{'unknown_requirement_id':'requirement.unknown_telemetry_target','no_catalog_match':True,'selection_policy':'abstain','rationale':'No stable record or source maps this requirement; clarify it or extend the reviewed catalog before recommending.'}}
 ]
}
files={
 'brief.json':brief,
 'expected_selection.json':{'fixture_id':fixture,'selected_records':selected,'gate_outcomes':{'gate.unit_integration_execution':'INCOMPLETE','gate.release_readiness':'INCOMPLETE'}},
 'expected_rejections.json':{'fixture_id':fixture,'rejected_requirements':[{'requirement_id':'apply_mobile_source_to_api','reason':'The source is stack-specific and is not evidence for the API target.','source_record_ids':['source.mobile_applications.01']},{'requirement_id':'claim_tests_passed_from_repository_presence','reason':'A source file and workflow configuration are not a candidate-bound execution record.','source_record_ids':['source.fastapi.tests','source.fastapi.ci']},{'requirement_id':'requirement.unknown_telemetry_target','reason':'No stable catalog match exists; abstain rather than infer an unsupported requirement.','source_record_ids':['source.github.copilot_task_practices']}],'rejected_records':[]},
 'expected_deliverables.json':{'fixture_id':fixture,'deliverables':[{'deliverable_id':'negative-control-abstention','phase':'verification','name':'Scoped evidence disposition','status':'INCOMPLETE','acceptance_criteria':['Keep every evidence claim within source scope.','Resolve the organization’s standard adoption and review the relevant normative text before asserting conformance.','Do not mark a test gate PASS without a candidate-bound execution record.','Keep architecture selection conditional on project-specific workload and operational evidence.'],'record_ids':selected_ids,'evidence_ids':['source.mobile_applications.01','source.iso.12207.2026.summary','source.fastapi.tests','source.fastapi.ci','source.aws.segment_workload','source.12factor.processes']}]},
 'evidence_trace.json':{'fixture_id':fixture,'traces':traces},
 'negative_cases.json':neg_cases
}
for name,obj in files.items(): (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'fixture_id':fixture,'selected_records':selected_ids,'negative_cases':[x['case_id'] for x in neg_cases['cases']],'traces':len(traces)},indent=2))
