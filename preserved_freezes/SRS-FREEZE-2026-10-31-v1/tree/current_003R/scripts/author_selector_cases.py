#!/usr/bin/env python3
"""Author structured selector inputs; this generator never reads oracle/expected files."""
from pathlib import Path
import copy,json
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'selection_cases'; FIX=ROOT/'fixtures'

def brief_for(kind):
 src=json.loads((FIX/kind/'brief.json').read_text())
 raw=src.get('attributes',{})
 if kind=='ai_agent':
  values={'reads_untrusted_external_content':True,'has_read_access':True,'has_bounded_write_tool':True,'can_cause_side_effects':True,'high_impact_action_possible':True,'approval_required_for_high_impact':True,'approver_available':False,'vector_database_requested':False,'multi_agent_autonomy_requested':False,'production_deployment_requested':False,'release_plan_required':False,'candidate_identified':False,'tests_executed':False,'approval_record_present':False,'data_sensitivity_known':False,'tool_scope_reviewed':False,'threat_model_reviewed':False,'reference_example_requested':True,'distinct_responsibilities':False}
  typ=['software_type.ai_agents']
 elif kind=='authenticated_api':
  values={'network_api':True,'single_service':True,'authenticated_users':True,'role_based_authorization':True,'persisted_records':True,'public_read_only':False,'multi_tenant':False,'tenant_isolation_required':False,'async_queue_required':False,'queue_load_justification':False,'operations_owner_available':False,'billing_required':False,'microservices_required':False,'kubernetes_required':False,'release_plan_required':True,'candidate_identified':False,'tests_executed':False,'approval_record_present':False,'authentication_required':True,'database_required':None,'cloud_hosting_required':None,'api_gateway_required':None,'reference_example_requested':True,'distinct_responsibilities':True,'tenant_mapping_evidence_known':False}
  typ=['software_type.apis']
 else:
  values={'local_filesystem_input':True,'offline_only':True,'network_service_boundary':False,'account_boundary':False,'tenant_boundary':False,'persistent_shared_state':False,'database_required':False,'cloud_hosting_required':False,'container_required':False,'api_gateway_required':False,'async_queue_required':False,'service_deployment_required':False,'authentication_required':False,'multi_tenant':False,'destructive_overwrite_requested':False,'destructive_write_authorized':False,'network_upload_requested':False,'network_upload_authorized':False,'library_distribution_requested':False,'package_distribution_planned':False,'distribution_target_known':False,'candidate_identified':False,'tests_executed':False,'release_plan_required':False,'selected_dependencies_known':False,'reference_example_requested':True,'distinct_responsibilities':False}
  typ=['software_type.cli_tools']
 facts=[]
 for fid,val in sorted(values.items()):
  state=('unknown' if val is None else ('true' if val else 'false'))
  facts.append({'fact_id':fid,'state':state,'scope':'project','origin':'explicit_scope' if state!='unknown' else 'not_provided'})
 return {'input_contract_version':'1.0.0','software_type_ids':typ,'facts':facts,'authority':{'high_impact_approver':{'state':'unknown','principal_id':None,'evidence_id':None},'write_scope_authorized':{'state':'unknown','principal_id':None,'evidence_id':None}},'evidence':{'candidate':{'state':'unknown','candidate_id':None},'tests':{'state':'false','candidate_id':None,'execution_record_id':None,'result':'not_run'},'approval':{'state':'unknown','approval_record_id':None,'approver_id':None}},'standards':[],'descriptive_text':{'text':src.get('description',''),'authority':'non_authoritative'},'missing_inputs':src.get('missing_inputs',[])}
def setf(b,fid,val,scope='project'):
 row=next((x for x in b['facts'] if x['fact_id']==fid),None)
 if row is None: b['facts'].append({'fact_id':fid,'state':'unknown' if val is None else ('true' if val else 'false'),'scope':scope,'origin':'not_provided' if val is None else 'explicit_requirement'})
 else: row.update(state='unknown' if val is None else ('true' if val else 'false'),scope=scope,origin='not_provided' if val is None else 'explicit_requirement')
def save(name,b):
 p=OUT/name;p.mkdir(parents=True,exist_ok=True);(p/'brief.json').write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
# Freeze the three parent scenarios as structured, explicit inputs.
base={k:brief_for(k) for k in ('ai_agent','authenticated_api','offline_cli')}
for k,b in base.items(): save('base_'+k,b)
# Agent counterfactuals.
b=copy.deepcopy(base['ai_agent']);setf(b,'has_bounded_write_tool',False);setf(b,'can_cause_side_effects',False);setf(b,'high_impact_action_possible',False);b['authority']['high_impact_approver']={'state':'false','principal_id':None,'evidence_id':None};save('agent_no_write_tool',b)
b=copy.deepcopy(base['ai_agent']);setf(b,'approver_available',False);setf(b,'high_impact_action_possible',True);b['authority']['high_impact_approver']={'state':'false','principal_id':None,'evidence_id':None};save('agent_write_no_approver',b)
b=copy.deepcopy(base['ai_agent']);setf(b,'production_deployment_requested',True);setf(b,'release_plan_required',True);save('agent_production_without_candidate_tests',b)
# API counterfactuals.
b=copy.deepcopy(base['authenticated_api']);setf(b,'authenticated_users',False);setf(b,'role_based_authorization',False);setf(b,'authentication_required',False);setf(b,'public_read_only',True);setf(b,'persisted_records',False);save('api_public_read_only',b)
b=copy.deepcopy(base['authenticated_api']);setf(b,'multi_tenant',True);setf(b,'tenant_isolation_required',True);setf(b,'tenant_mapping_evidence_known',False);save('api_explicit_multitenant',b)
b=copy.deepcopy(base['authenticated_api']);setf(b,'async_queue_required',True);setf(b,'queue_load_justification',False);setf(b,'operations_owner_available',False);save('api_queue_without_justification',b)
b=copy.deepcopy(base['authenticated_api']);b['standards']=[{'standard_id':'ISO/IEC/IEEE 12207','requested':True,'requested_edition':'2017','organization_adoption':'unknown','evidence_id':None}];save('api_changed_standard_edition',b)
# CLI counterfactuals.
b=copy.deepcopy(base['offline_cli']);setf(b,'destructive_overwrite_requested',True);setf(b,'destructive_write_authorized',False);b['authority']['write_scope_authorized']={'state':'false','principal_id':None,'evidence_id':None};save('cli_destructive_overwrite_unauthorized',b)
b=copy.deepcopy(base['offline_cli']);setf(b,'offline_only',False);setf(b,'network_service_boundary',True);setf(b,'network_upload_requested',True);setf(b,'network_upload_authorized',None);setf(b,'upload_destination_known',False);setf(b,'data_sensitivity_known',False);save('cli_network_upload_unknown_scope',b)
b=copy.deepcopy(base['offline_cli']);b['software_type_ids']=['software_type.cli_tools','software_type.libraries'];setf(b,'library_distribution_requested',True);setf(b,'package_distribution_planned',True);setf(b,'service_deployment_required',False);setf(b,'distribution_target_known',False);save('cli_library_distribution_no_service',b)
print(json.dumps({'base_cases':len(base),'counterfactuals':9,'files':len(list(OUT.glob('*/brief.json')))},indent=2))
