#!/usr/bin/env python3
"""Validate all deterministic fixtures against schemas, graph paths and safety controls."""
from pathlib import Path
import argparse, json, sys
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dataset/v1'; FIX=ROOT/'fixtures'; SCHEMA=json.loads((ROOT/'schemas/fixture.schema.json').read_text())
PARTS=['software_types','engineering_practices','sdlc_stages','architecture_patterns','prompt_patterns','roadmap_patterns','verification_gates','reference_projects']
FIXTURE_DEFS={'brief.json':'brief','expected_selection.json':'expectedSelection','expected_rejections.json':'expectedRejections','expected_deliverables.json':'expectedDeliverables','evidence_trace.json':'evidenceTrace'}
def read_rows(name): return [json.loads(x) for x in (DATA/(name+'.jsonl')).read_text().splitlines() if x.strip()]
def load_catalog():
 records={r['id']:r for p in PARTS for r in read_rows(p)}
 sources={r['id']:r for r in read_rows('sources')}
 edges={(e['source_endpoint'],e['target_endpoint'],e['predicate']):e for e in read_rows('relationships') if e.get('status','active')!='superseded'}
 return records,sources,edges
def truth(v): return bool(v)
def check_condition(condition, attrs):
 for key in condition.get('all_true',[]):
  path=key.removeprefix('attributes.')
  if path not in attrs or not truth(attrs[path]): return False,f'{key} must be true and present'
 for key in condition.get('all_false',[]):
  path=key.removeprefix('attributes.')
  if path not in attrs or truth(attrs[path]): return False,f'{key} must be false and present'
 return True,''
def trace_path(record_id,source_id,software_ids,records,edges):
 if record_id in software_ids or (record_id in records and records[record_id].get('knowledge_category')=='software_types'):
  k=(record_id,source_id,'supported_by')
  return ([record_id,source_id],['supported_by']) if k in edges else (None,None)
 if record_id not in records: return None,None
 record=records[record_id]
 if source_id not in record.get('source_ids',[]): return None,None
 candidates=[]
 for tid in software_ids:
  if tid not in record.get('applicable_software_types',[]): continue
  pred='exemplified_by' if record.get('knowledge_category')=='reference_projects' else 'applies_to'
  if (tid,record_id,pred) in edges and (record_id,source_id,'supported_by') in edges:
   candidates.append(([tid,record_id,source_id],[pred,'supported_by']))
 return candidates[0] if candidates else (None,None)
def negative_case_status(case,records,sources,fixture_docs):
 typ=case['case_type']; details=case['details']
 if typ=='stack_mismatch':
  sid=case['evidence_source_ids'][0]; target=records.get(details.get('target_software_type_id'))
  if not target: return 'ERROR','Unknown target software type.'
  src=sources.get(sid,{})
  mobile=records.get('software_type.mobile_applications',{})
  if sid in mobile.get('source_ids',[]) and sid not in target.get('source_ids',[]) and 'mobile' in (sid+' '+src.get('title','')).lower(): return 'INAPPLICABLE','Source is attached to the mobile-app software-type record, not the API record, and is scoped to another stack.'
  return 'ERROR','Stack mismatch control no longer holds: source may support the target or its scope was not explicit.'
 if typ=='superseded_standard':
  sid=case['evidence_source_ids'][0]; src=sources.get(sid,{})
  supported=src.get('claims_supported','').lower(); limits=src.get('limitations','').lower()
  if '2026' in supported and 'supersedes 12207-2017' in supported.lower() and 'not inspected' in limits and details.get('organization_adoption_known') is False and details.get('full_normative_text_reviewed') is False:
   return 'INCOMPLETE','Catalog currency is established, but adoption and normative applicability remain unresolved.'
  return 'ERROR','Edition/adoption abstention evidence is insufficient or inconsistent with the pinned catalog.'
 if typ=='missing_test_execution':
  ref=records.get('reference.fastapi',{}); gates=fixture_docs['expected_selection.json'].get('gate_outcomes',{})
  no_run=ref.get('category_specific',{}).get('test_execution_status')=='not_run' and ref.get('category_specific',{}).get('ci_execution_status')=='not_run'
  no_artifacts=details.get('candidate_id') is None and details.get('test_execution_artifact') is None
  if no_run and no_artifacts and details.get('workflow_configuration_is_execution') is False and gates.get(details.get('gate_id'))=='INCOMPLETE':
   return 'INCOMPLETE','Pinned test and workflow sources are configuration only; no candidate-bound run result exists.'
  return 'ERROR','Missing-execution control failed or a gate was promoted without an actual run record.'
 if typ=='source_tension':
  arch=records.get(details.get('architecture_record_id'),{}).get('category_specific',{})
  aws=sources.get('source.aws.segment_workload',{}).get('claims_supported','').lower()
  twelve=sources.get('source.12factor.processes',{}).get('claims_supported','').lower()
  limits=sources.get('source.12factor.processes',{}).get('limitations','').lower()
  if arch.get('decision_policy')=='context_specific_options_only' and 'support them' in aws and 'stateless' in twelve and 'does not by itself choose' in limits:
   return 'CONDITIONAL','Different source scopes remain attributed; no universal architecture winner is inferred.'
  return 'ERROR','Source-tension control failed: conditional option policy or scope limits are missing.'
 if typ=='unknown_requirement':
  unknown=details.get('unknown_requirement_id')
  selected={x.get('record_id') for x in fixture_docs['expected_selection.json'].get('selected_records',[])}
  if unknown and unknown not in records and unknown not in sources and unknown not in selected and details.get('no_catalog_match') is True and details.get('selection_policy')=='abstain':
   return 'INCOMPLETE','No stable catalog match exists; the unknown requirement is not silently mapped to a recommendation.'
  return 'ERROR','Unknown-requirement control failed: the request was mapped or did not explicitly abstain.'
 return 'ERROR','Unknown negative case type.'

def validate_case_structure(case,records,sources,docs,errors):
 actual,reason=negative_case_status(case,records,sources,docs)
 if actual!=case.get('expected_status'): errors.append(f"negative case {case.get('case_id')}: expected {case.get('expected_status')}, derived {actual} ({reason})")
 return actual,reason

def validate_all():
 records,sources,edges=load_catalog(); errors=[]; results=[]; category_counts={}
 golden_path=FIX/'golden-id-map.json'
 golden=json.loads(golden_path.read_text(encoding='utf-8')) if golden_path.exists() else {'branches':{}}
 if not golden_path.exists(): errors.append('missing fixtures/golden-id-map.json')
 branches={p:Draft202012Validator({'$schema':SCHEMA['$schema'],'$defs':SCHEMA['$defs'],'$ref':f"#/$defs/{defn}"},format_checker=FormatChecker()) for p,defn in FIXTURE_DEFS.items()}
 branches['negative_cases.json']=Draft202012Validator({'$schema':SCHEMA['$schema'],'$defs':SCHEMA['$defs'],'$ref':'#/$defs/negativeCases'},format_checker=FormatChecker())
 dirs=sorted(p for p in FIX.iterdir() if p.is_dir())
 if len(dirs)!=4: errors.append(f'expected exactly four fixture branches (three project + negative controls), found {len(dirs)}')
 for directory in dirs:
  docs={}
  active_defs=dict(FIXTURE_DEFS)
  if directory.name=='conflict_missing_evidence': active_defs['negative_cases.json']='negativeCases'
  for filename,definition in active_defs.items():
   path=directory/filename
   if not path.exists(): errors.append(f'{directory.name}: missing {filename}'); continue
   try: docs[filename]=json.loads(path.read_text(encoding='utf-8'))
   except Exception as exc: errors.append(f'{path}: invalid JSON: {exc}'); continue
   for err in branches[filename].iter_errors(docs[filename]): errors.append(f'{path.relative_to(ROOT)}: schema: {err.message} at /{ "/".join(map(str,err.absolute_path)) }')
  if len(docs)<5: continue
  brief=docs['brief.json']; sel=docs['expected_selection.json']; rej=docs['expected_rejections.json']; dels=docs['expected_deliverables.json']; trace_doc=docs['evidence_trace.json']
  fixture_id=brief.get('fixture_id')
  for name,doc in docs.items():
   if doc.get('fixture_id')!=fixture_id: errors.append(f'{directory.name}/{name}: fixture_id mismatch')
  expected=golden.get('branches',{}).get(directory.name)
  if not expected: errors.append(f'{directory.name}: no golden-ID contract entry')
  else:
   actual_selected=sorted(x['record_id'] for x in sel.get('selected_records',[]))
   actual_rejected=sorted(x['record_id'] for x in rej.get('rejected_records',[]))
   actual_requirements=sorted(x['requirement_id'] for x in rej.get('rejected_requirements',[]))
   if actual_selected!=expected.get('selected_record_ids'): errors.append(f'{directory.name}: selected record IDs differ from golden map')
   if actual_rejected!=expected.get('rejected_record_ids'): errors.append(f'{directory.name}: rejected record IDs differ from golden map')
   if actual_requirements!=expected.get('rejected_requirement_ids'): errors.append(f'{directory.name}: rejected requirement IDs differ from golden map')
  if set(sel.get('gate_outcomes',{}).values()) & {'PASS','FAIL'}: errors.append(f'{directory.name}: fixture claims a PASS/FAIL gate outcome despite no execution')
  gates={x['record_id'] for x in sel.get('selected_records',[]) if records.get(x['record_id'],{}).get('knowledge_category')=='verification_gates'}
  if gates!=set(sel.get('gate_outcomes',{})): errors.append(f'{directory.name}: selected verification gates do not exactly match gate_outcomes')
  for gid,outcome in sel.get('gate_outcomes',{}).items():
   if gid not in records or records[gid].get('knowledge_category')!='verification_gates': errors.append(f'{directory.name}: gate_outcomes has unknown/non-gate ID {gid}')
   if outcome!='INCOMPLETE': errors.append(f'{directory.name}: gate {gid} must remain INCOMPLETE without candidate-bound execution evidence')
  selected={}
  for row in sel.get('selected_records',[]):
   rid=row.get('record_id'); rec=records.get(rid)
   if rid in selected: errors.append(f'{directory.name}: duplicate selected record {rid}')
   selected[rid]=row
   if not rec: errors.append(f'{directory.name}: selected unknown record {rid}'); continue
   if rec.get('knowledge_category')=='software_types':
    if rid not in brief.get('software_type_ids',[]): errors.append(f'{directory.name}: selected software type {rid} is not in brief.software_type_ids')
   elif not set(rec.get('applicable_software_types',[])).intersection(brief.get('software_type_ids',[])):
    errors.append(f'{directory.name}: selected record {rid} is inapplicable to the fixture software type')
   ok,why=check_condition(row.get('branch_condition',{}),brief.get('attributes',{}))
   if not ok: errors.append(f'{directory.name}: branch condition for {rid} is not satisfied ({why})')
   for missing in row.get('unresolved_inputs',[]):
    if missing not in brief.get('missing_inputs',[]) and missing not in brief.get('description',''):
     # Preserve a meaningful pending input instead of silently treating it as resolved.
     errors.append(f'{directory.name}: unresolved input {missing!r} for {rid} is not recorded in brief missing_inputs')
  traces=trace_doc.get('traces',[]); trace_by_record={}
  for trace in traces:
   rid=trace.get('knowledge_record_id'); sid=trace.get('source_id'); source=sources.get(sid)
   if not source: errors.append(f'{directory.name}: trace references unknown source {sid}'); continue
   rec=records.get(rid)
   if not rec: errors.append(f'{directory.name}: trace references unknown knowledge record {rid}'); continue
   if sid not in rec.get('source_ids',[]): errors.append(f'{directory.name}: trace source {sid} is not in {rid}.source_ids')
   if trace.get('claim_locator')!=source.get('claim_locator'): errors.append(f'{directory.name}: trace locator for {sid} does not exactly match source record')
   expected_path,expected_predicates=trace_path(rid,sid,brief.get('software_type_ids',[]),records,edges)
   if expected_path is None: errors.append(f'{directory.name}: no active typed graph path for {rid} -> {sid}')
   elif trace.get('path')!=expected_path or trace.get('predicates')!=expected_predicates: errors.append(f'{directory.name}: trace path/predicates for {rid} -> {sid} do not match active graph; expected {expected_path} {expected_predicates}')
   if any(x in source.get('source_type','').lower() for x in ['test source','workflow','repository test','ci configuration']) and trace.get('evidence_classification')=='tested_outcome': errors.append(f'{directory.name}: test/configuration source {sid} misclassified as tested outcome')
   trace_by_record.setdefault(rid,[]).append(trace)
  for rid in selected:
   if not trace_by_record.get(rid): errors.append(f'{directory.name}: selected record {rid} lacks source-claim trace')
  for rr in rej.get('rejected_records',[]):
   rec=records.get(rr.get('record_id'))
   if not rec: errors.append(f'{directory.name}: rejected unknown record {rr.get("record_id")}'); continue
   ok,why=check_condition(rr.get('branch_condition',{}),brief.get('attributes',{}))
   if not ok: errors.append(f'{directory.name}: rejection condition for {rr["record_id"]} not satisfied ({why})')
   applicable=bool(set(rec.get('applicable_software_types',[])).intersection(brief.get('software_type_ids',[])))
   if rr.get('status')=='INAPPLICABLE' and applicable: errors.append(f'{directory.name}: record {rr["record_id"]} marked INAPPLICABLE though it applies to this fixture type')
  for rr in rej.get('rejected_requirements',[]):
   for rid in rr.get('source_record_ids',[]):
    if rid not in records and rid not in sources: errors.append(f'{directory.name}: rejection {rr.get("requirement_id")} uses unknown evidence ID {rid}')
  if directory.name=='offline_cli':
   false_obligations={'feature.authentication','feature.multitenancy','feature.database','feature.cloud_hosting','feature.container','feature.api_gateway','feature.queue','feature.service_deployment'}
   actual_false={x.get('requirement_id') for x in rej.get('rejected_requirements',[])}
   if actual_false!=false_obligations: errors.append(f'{directory.name}: false obligations are not rejected exactly; expected {sorted(false_obligations)}, found {sorted(actual_false)}')
   for attr in ['network_service_boundary','account_boundary','tenant_boundary','persistent_shared_state','database_required','cloud_hosting_required','container_required','api_gateway_required','async_queue_required','service_deployment_required']:
    if brief.get('attributes',{}).get(attr) is not False: errors.append(f'{directory.name}: false obligation attribute {attr} must be explicitly false')
  trace_sources={t['source_id'] for t in traces}
  decisions={x['record_id']:x['status'] for x in sel.get('selected_records',[])}
  decisions.update({x['record_id']:x['status'] for x in rej.get('rejected_records',[])})
  for d in dels.get('deliverables',[]):
   for rid in d.get('record_ids',[]):
    if rid not in records: errors.append(f'{directory.name}: deliverable {d.get("deliverable_id")} references unknown record {rid}')
    if rid not in decisions: errors.append(f'{directory.name}: deliverable {d.get("deliverable_id")} cites undecided record {rid}')
    elif decisions[rid]=='INAPPLICABLE': errors.append(f'{directory.name}: deliverable {d.get("deliverable_id")} requires inapplicable record {rid}')
   for sid in d.get('evidence_ids',[]):
    if sid not in sources: errors.append(f'{directory.name}: deliverable {d.get("deliverable_id")} references unknown source {sid}')
    if sid not in trace_sources: errors.append(f'{directory.name}: deliverable source {sid} is absent from evidence_trace')
  for type_id in brief.get('software_type_ids',[]): category_counts[type_id]=category_counts.get(type_id,0)+1
  negative_results=[]
  if directory.name=='conflict_missing_evidence':
   cases=docs.get('negative_cases.json',{}).get('cases',[])
   types={c.get('case_type') for c in cases}
   required={'stack_mismatch','superseded_standard','missing_test_execution','source_tension','unknown_requirement'}
   if types!=required: errors.append(f'negative fixture must contain exactly the five required case types; found {sorted(types)}')
   for case in cases:
    for sid in case.get('evidence_source_ids',[]):
     if sid not in sources: errors.append(f'{directory.name}: negative case {case.get("case_id")} uses unknown source {sid}')
     elif sid not in trace_sources: errors.append(f'{directory.name}: negative case source {sid} lacks an exact evidence trace')
    actual,reason=validate_case_structure(case,records,sources,docs,errors)
    negative_results.append({'case_id':case['case_id'],'case_type':case['case_type'],'expected_status':case['expected_status'],'derived_status':actual,'reason':reason})
  elif docs.get('negative_cases.json',{}).get('cases'):
   errors.append(f'{directory.name}: project fixture must not contain the shared conflict negative-case suite')
  results.append({'directory':directory.name,'fixture_id':fixture_id,'selected_record_count':len(selected),'trace_count':len(traces),'gate_outcomes':sel.get('gate_outcomes',{}),'negative_cases':negative_results})
 return {'schema_version':'1.1.0','fixture_count':len(results),'results':results,'fixture_category_coverage':category_counts,'error_count':len(errors),'errors':errors,'status':'PASS' if not errors else 'FAIL'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--report',default=str(ROOT/'reports'/'fixture-validation.json'));args=ap.parse_args()
 report=validate_all();out=Path(args.report);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(report,indent=2,ensure_ascii=False));return 0 if not report['error_count'] else 1
if __name__=='__main__':sys.exit(main())
