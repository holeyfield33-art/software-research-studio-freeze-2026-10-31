#!/usr/bin/env python3
"""Correct branch conditions/statuses that conflict with explicit fixture inputs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; FIX=ROOT/'fixtures'
def load(d,f): return json.loads((FIX/d/f).read_text())
def save(d,f,x): (FIX/d/f).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
# AI-agent: no candidate identity means coding/work/verification templates remain incomplete, not ready-to-run recommendations.
d='ai_agent'; b=load(d,'brief.json'); b['attributes']['candidate_identified']=False
s=load(d,'expected_selection.json')
for row in s['selected_records']:
 cond=row['branch_condition']; key=next((k for k in cond.get('all_true',[]) if k.split('.')[-1]=='candidate_identified'),None)
 if key:
  cond['all_true'].remove(key); cond.setdefault('all_false',[]).append(key)
  row['status']='INCOMPLETE'
  if 'candidate identity' not in row['unresolved_inputs']: row['unresolved_inputs'].append('candidate identity')
missing=set(b['missing_inputs'])
for row in s['selected_records']:
 for item in row['unresolved_inputs']: missing.add(item)
b['missing_inputs']=sorted(missing)
save(d,'brief.json',b); save(d,'expected_selection.json',s)
# API: clarify unselected conditional patterns are off for this brief, not universally inapplicable by category.
d='authenticated_api'; b=load(d,'brief.json'); b['missing_inputs']=sorted(set(b['missing_inputs'])|{'language/framework selection'})
save(d,'brief.json',b)
r=load(d,'expected_rejections.json')
for row in r['rejected_records']:
 if row['record_id']=='arch.event_queue':
  row['status']='CONDITIONAL'; row['reason']='Only select asynchronous queue architecture if evidence requires durability, bursts, or independent consumers; the brief says none is required.'; row['branch_condition']={'all_true':[],'all_false':['attributes.async_queue_required']}
 if row['record_id']=='arch.multitenancy_isolation':
  row['status']='CONDITIONAL'; row['reason']='Only select a tenant-isolation design if independent tenant boundaries are required; the brief says the product is not multi-tenant.'; row['branch_condition']={'all_true':[],'all_false':['attributes.multi_tenant']}
save(d,'expected_rejections.json',r)
# CLI: no release requested, so defer release stage/readiness instead of putting them on the active path.
d='offline_cli'; b=load(d,'brief.json'); s=load(d,'expected_selection.json'); r=load(d,'expected_rejections.json')
removed={'sdlc.release','gate.release_readiness'}
s['selected_records']=[x for x in s['selected_records'] if x['record_id'] not in removed]
for rid in removed: s['gate_outcomes'].pop(rid,None)
for rid in ['sdlc.release','gate.release_readiness']:
 r['rejected_records'].append({'record_id':rid,'status':'CONDITIONAL','reason':'A release is not requested in this fixture; only add this stage/gate if distribution is later planned and a candidate exists.','branch_condition':{'all_true':[],'all_false':['attributes.release_requested']}})
missing=set(b['missing_inputs'])
for row in s['selected_records']:
 for item in row['unresolved_inputs']: missing.add(item)
b['missing_inputs']=sorted(missing)
save(d,'brief.json',b); save(d,'expected_selection.json',s); save(d,'expected_rejections.json',r)
print('calibrated ai_agent, authenticated_api, and offline_cli fixtures')
