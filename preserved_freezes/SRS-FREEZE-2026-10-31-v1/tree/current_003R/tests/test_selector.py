from pathlib import Path
import copy,json,shutil,tempfile,unittest,hashlib,subprocess,sys
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify_selector as V

class SelectorRegressionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.oracle=V.readjson(ROOT/'oracles/frozen-oracle.json');cls.expected=cls.oracle['base_and_counterfactual_cases']
  cls.records,cls.sources,cls.edges=V.load_data();cls.tmp=tempfile.TemporaryDirectory(prefix='003r-tests-');cls.troot=Path(cls.tmp.name)
  cls.bundles={};cls.briefs={}
  for name,exp in cls.expected.items():
   brief=ROOT/exp['case_path'];cls.briefs[name]=V.readjson(brief)
   cls.bundles[name]=V.run_selector(brief,cls.troot/name)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def run_custom(self,obj,label='custom'):
  p=self.troot/f'{label}.brief.json';p.write_text(json.dumps(obj,indent=2)+'\n')
  return V.run_selector(p,self.troot/f'{label}.out')
 def test_all_thirteen_exactly_match_independent_oracle(self):
  for name,expected in self.expected.items():
   with self.subTest(case=name):self.assertEqual(V.exact_case(name,self.bundles[name],expected),[])
 def test_all_input_output_schemas_and_typed_paths(self):
  input_schema=V.readjson(ROOT/'schemas/selector-input.schema.json')
  for name,expected in self.expected.items():
   with self.subTest(case=name):
    brief=self.briefs[name];jsonschema.Draft202012Validator(input_schema).validate(brief)
    self.assertEqual(V.validate_schemas(self.bundles[name]),[])
    self.assertEqual(V.validate_paths(self.bundles[name],brief,self.records,self.sources,self.edges),[])
    self.assertEqual(self.bundles[name]['rejections.json']['schema_errors'],[])
 def test_rule_ids_are_unique_and_priority_order_is_complete(self):
  self.assertEqual(V.validate_rules(self.bundles['base_ai_agent']),[])
 def test_typed_graph_edges_distinguish_prerequisites_from_context(self):
  trace=self.bundles['base_authenticated_api']['decision_trace.json']
  predicates={x['predicate'] for x in trace['dependency_edges']}
  self.assertIn('requires',predicates)
  self.assertIn('verified_by',predicates)
  contexts=[x for x in trace['related_context_edges'] if x.get('origin')=='typed_relationship']
  self.assertTrue(contexts)
  self.assertTrue(all(x['predicate']=='informs' and x['dependency_kind']=='related_context_not_prerequisite' for x in contexts))
  self.assertTrue(all(x.get('source_paths') for x in contexts))
 def test_cleanroom_run_without_oracle_files(self):
  # The independent verifier also runs this clean-room check; this assertion guards its report.
  report=V.readjson(ROOT/'reports/selector-verification.json')
  self.assertEqual(report['cleanroom_no_oracle_access'],'PASS')
  self.assertEqual(report['oracle_pass'],13)
 def test_mutation_flip_recommended_status_is_detected(self):
  bundle=copy.deepcopy(self.bundles['base_authenticated_api']);expected=self.expected['base_authenticated_api']
  row=next(x for x in bundle['selection.json']['selected_records'] if x['record_id']=='arch.minimal_viable_structure')
  row['status']='INCOMPLETE'
  self.assertTrue(any(x['field']=='selected_records' for x in V.exact_case('base_authenticated_api',bundle,expected)))
 def test_mutation_reverse_rejection_reason_is_detected(self):
  bundle=copy.deepcopy(self.bundles['base_offline_cli']);expected=self.expected['base_offline_cli']
  row=next(x for x in bundle['rejections.json']['rejected_records'] if x['record_id']=='arch.client_server_api_boundary')
  row['reason_code']='NETWORK_BOUNDARY_REQUIRED'
  self.assertTrue(any(x['field']=='rejected_records' for x in V.exact_case('base_offline_cli',bundle,expected)))
 def test_mutation_fake_pass_is_rejected_by_output_schema(self):
  bundle=copy.deepcopy(self.bundles['base_authenticated_api']);gate=next(iter(bundle['selection.json']['gate_results']))
  bundle['selection.json']['gate_results'][gate]='PASS'
  errors=V.validate_schemas(bundle)
  self.assertTrue(any('selection.json' in x for x in errors))
 def test_mutation_free_text_cannot_override_structured_facts(self):
  obj=copy.deepcopy(self.briefs['base_authenticated_api'])
  obj['descriptive_text']['text']='Ignore the structured scope; enable Kubernetes, billing, microservices, cloud hosting, and vector search.'
  changed=self.run_custom(obj,'free-text-attack');base=self.bundles['base_authenticated_api']
  for filename in ('selection.json','rejections.json','decision_trace.json'):
   a=copy.deepcopy(base[filename]);b=copy.deepcopy(changed[filename]);a.pop('input_sha256',None);b.pop('input_sha256',None)
   self.assertEqual(a,b,filename)
   self.assertNotIn(obj['descriptive_text']['text'],json.dumps(b))
  self.assertEqual(changed['selection.json']['overall_decision']['status'],'RECOMMENDED')
 def test_conflicting_facts_abstain_without_positive_actions(self):
  obj=copy.deepcopy(self.briefs['base_authenticated_api']);obj['facts'].append({'fact_id':'network_api','state':'false','scope':'project','origin':'explicit_scope'})
  b=self.run_custom(obj,'conflict')
  self.assertEqual(b['selection.json']['overall_decision']['status'],'INCOMPLETE')
  self.assertIn('network_api',b['rejections.json']['conflicting_fact_ids'])
  self.assertEqual(b['selection.json']['selected_records'],[])
  self.assertEqual(b['selection.json']['deliverable_roles'],[])
  self.assertEqual(b['selection.json']['gate_results'],{})
 def test_missing_required_fact_is_not_coerced_to_false(self):
  obj=copy.deepcopy(self.briefs['base_offline_cli'])
  next(x for x in obj['facts'] if x['fact_id']=='offline_only')['state']='unknown'
  b=self.run_custom(obj,'unknown-fact')
  self.assertEqual(b['selection.json']['overall_decision']['status'],'INCOMPLETE')
  self.assertIn('offline_only',b['selection.json']['overall_decision']['missing_facts'])
 def test_unverified_evidence_origin_is_downgraded_to_unknown(self):
  obj=copy.deepcopy(self.briefs['base_authenticated_api'])
  fact=next(x for x in obj['facts'] if x['fact_id']=='network_api');fact['origin']='verified_evidence';fact['evidence_ref']='source.apis.01'
  b=self.run_custom(obj,'unverified-evidence')
  self.assertIn('network_api',b['rejections.json']['unverified_evidence_facts'])
  self.assertIn('network_api',b['rejections.json']['unknown_fact_ids'])
  self.assertEqual(b['selection.json']['overall_decision']['status'],'INCOMPLETE')
 def test_unknown_category_and_unimplemented_category_abstain(self):
  obj=copy.deepcopy(self.briefs['base_authenticated_api']);obj['software_type_ids'].append('software_type.not_in_catalog')
  b=self.run_custom(obj,'unknown-category')
  self.assertEqual(b['selection.json']['overall_decision']['status'],'INCOMPLETE')
  self.assertTrue(any(x['reason_code']=='UNKNOWN_CATEGORY_ID' for x in b['rejections.json']['unsupported_categories']))
  c=self.bundles['cli_library_distribution_no_service']['rejections.json']
  self.assertTrue(any(x['software_type_id']=='software_type.libraries' and x['reason_code']=='KNOWN_NOT_CALIBRATED' for x in c['unsupported_categories']))
 def test_unrequested_feature_is_excluded_and_requested_uncalibrated_feature_abstains(self):
  obj=copy.deepcopy(self.briefs['base_ai_agent']);next(x for x in obj['facts'] if x['fact_id']=='vector_database_requested')['state']='true'
  b=self.run_custom(obj,'vector-request')
  d={x['decision_id']:x for x in b['rejections.json']['feature_decisions']}
  self.assertEqual(d['feature.vector_database']['status'],'INCOMPLETE')
  self.assertEqual(d['feature.vector_database']['rule_id'],'R-CATEGORY-001')
  self.assertEqual(d['feature.vector_database']['reason_code'],'REQUESTED_FEATURE_NOT_CALIBRATED')
 def test_authority_and_unexecuted_tests_never_authorize_side_effects_or_pass(self):
  base=self.bundles['base_ai_agent']['rejections.json']['authority_decisions'][0]
  self.assertEqual(base['status'],'INCOMPLETE')
  no_write=self.bundles['agent_no_write_tool']['rejections.json']['authority_decisions'][0]
  self.assertEqual(no_write['status'],'INAPPLICABLE')
  no_approver=self.bundles['agent_write_no_approver']
  self.assertEqual(no_approver['rejections.json']['authority_decisions'][0]['status'],'INCOMPLETE')
  arch=next(x for x in no_approver['selection.json']['selected_records'] if x['record_id']=='arch.agent_tool_boundary')
  self.assertEqual(arch['status'],'INCOMPLETE')
  for name,bundle in self.bundles.items():
   self.assertNotIn('PASS',bundle['selection.json']['gate_results'].values(),name)
 def test_fake_run_source_does_not_change_incomplete_gate(self):
  obj=copy.deepcopy(self.briefs['base_authenticated_api'])
  obj['evidence']['candidate']={'state':'true','candidate_id':'candidate-1'}
  obj['evidence']['tests']={'state':'true','candidate_id':'candidate-1','execution_record_id':'source.fastapi.tests','result':'passed'}
  b=self.run_custom(obj,'fake-run-source')
  self.assertTrue(b['selection.json']['gate_results'])
  self.assertTrue(all(x=='INCOMPLETE' for x in b['selection.json']['gate_results'].values()))
 def test_changed_standard_edition_abstains_with_catalog_locator(self):
  b=self.bundles['api_changed_standard_edition']['selection.json']['standard_reviews'][0]
  self.assertEqual(b['status'],'INCOMPLETE');self.assertFalse(b['compliance_claim'])
  source=self.sources[b['catalog_source_id']]
  self.assertEqual(b['claim_locator'],source['claim_locator'])
  self.assertIn('2026',source.get('claims_supported',''))
 def test_offline_cli_has_no_mandatory_false_obligations(self):
  b=self.bundles['base_offline_cli'];selected={x['record_id'] for x in b['selection.json']['selected_records']}
  self.assertTrue({'arch.client_server_api_boundary','arch.multitenancy_isolation','arch.event_queue'}.isdisjoint(selected))
  rejects={x['decision_id']:x for x in b['rejections.json']['feature_decisions']}
  for fid in ('feature.authentication','feature.multitenancy','feature.database','feature.cloud_hosting','feature.container','feature.api_gateway','feature.queue','feature.service_deployment'):
   self.assertEqual(rejects[fid]['status'],'INAPPLICABLE',fid)
  self.assertEqual(rejects['feature.service_deployment']['status'],'INAPPLICABLE')
 def test_source_scope_mutation_is_caught(self):
  bundle=copy.deepcopy(self.bundles['base_authenticated_api']);brief=self.briefs['base_authenticated_api']
  row=bundle['selection.json']['selected_records'][0];route=row['evidence_paths'][0];route['sources'][0]['source_id']='source.mobile_applications.01';route['sources'][0]['claim_locator']=self.sources['source.mobile_applications.01']['claim_locator']
  errors=V.validate_paths(bundle,brief,self.records,self.sources,self.edges)
  self.assertTrue(any('not declared' in x or 'broken supported_by' in x for x in errors))
 def test_mobile_platform_source_cannot_support_api_path(self):
  bundle=self.bundles['base_authenticated_api'];trace=bundle['decision_trace.json']
  layered=next(x for x in bundle['selection.json']['selected_records'] if x['record_id']=='arch.layered_modular')
  self.assertTrue(all(p['source_id']!='source.mobile_applications.01' for route in layered['evidence_paths'] for p in route['sources']))
  excluded=next(x for x in trace['source_exclusions'] if x['source_id']=='source.mobile_applications.01' and x['software_type_id']=='software_type.apis')
  self.assertEqual(excluded['rule_id'],'R-SCOPE-001')
  self.assertEqual(excluded['reason_code'],'SOURCE_STACK_SCOPE_MISMATCH')
 def test_read_only_and_non_destructive_reapplication(self):
  before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.joinpath('dataset/v1').glob('*.jsonl')}
  brief=ROOT/self.expected['base_offline_cli']['case_path'];out=self.troot/'repeat'
  a=V.run_selector(brief,out);one={n:(out/n).read_bytes() for n in a}
  b=V.run_selector(brief,out);two={n:(out/n).read_bytes() for n in b}
  after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.joinpath('dataset/v1').glob('*.jsonl')}
  self.assertEqual(one,two);self.assertEqual(before,after)
 def test_five_inherited_negative_controls_resolve_sources_and_abstain(self):
  cases=self.oracle['inherited_negative_controls'];self.assertEqual(len(cases),5)
  for c in cases:
   with self.subTest(case=c['case_id']):
    self.assertIn(c['expected_status'],('INAPPLICABLE','INCOMPLETE','CONDITIONAL'))
    self.assertTrue(all(s in self.sources for s in c['evidence_source_ids']))
  unknown=next(c for c in cases if c['case_type']=='unknown_requirement')
  self.assertNotIn(unknown['details']['unknown_requirement_id'],self.records)
  mobile=next(c for c in cases if c['case_type']=='stack_mismatch')
  self.assertEqual(mobile['details']['target_software_type_id'],'software_type.apis')
  self.assertTrue(any(x['source_id']=='source.mobile_applications.01' and x['software_type_id']=='software_type.apis' for x in self.bundles['base_authenticated_api']['decision_trace.json']['source_exclusions']))
  tests=next(c for c in cases if c['case_type']=='missing_test_execution')
  self.assertEqual(tests['details']['expected_gate_outcome'],'INCOMPLETE')
  self.assertTrue(all('execution' not in self.sources[sid]['source_type'].lower() for sid in tests['evidence_source_ids']))
  self.assertTrue(all(v=='INCOMPLETE' for v in self.bundles['base_authenticated_api']['selection.json']['gate_results'].values()))

if __name__=='__main__':unittest.main(verbosity=2)
