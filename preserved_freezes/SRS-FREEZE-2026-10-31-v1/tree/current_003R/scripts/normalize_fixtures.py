#!/usr/bin/env python3
"""Rebuild fixture evidence traces from selected records and active graph edges."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'dataset/v1'; FIX=ROOT/'fixtures'
parts=['software_types','engineering_practices','sdlc_stages','architecture_patterns','prompt_patterns','roadmap_patterns','verification_gates','reference_projects']
records={r['id']:r for p in parts for l in (DATA/(p+'.jsonl')).read_text().splitlines() if l.strip() for r in [json.loads(l)]}
sources={r['id']:r for l in (DATA/'sources.jsonl').read_text().splitlines() if l.strip() for r in [json.loads(l)]}
edges={(e['source_endpoint'],e['target_endpoint'],e['predicate']):e for l in (DATA/'relationships.jsonl').read_text().splitlines() if l.strip() for e in [json.loads(l)] if e.get('status','active')!='superseded'}
def class_for(source,record):
 st=source.get('source_type','').lower()
 if any(x in st for x in ['repository','workflow','test source','ci configuration','pinned']): return 'observed_repository_file'
 if 'synthesis' in record.get('evidence_classification','').lower() or 'conditional' in record.get('evidence_classification','').lower(): return 'synthesis'
 return 'documented_guidance'
changed=[]
for directory in sorted(p for p in FIX.iterdir() if p.is_dir()):
 selection_path=directory/'expected_selection.json'; trace_path=directory/'evidence_trace.json'
 if not selection_path.exists() or not trace_path.exists(): continue
 brief=json.loads((directory/'brief.json').read_text()); selection=json.loads(selection_path.read_text()); trace_doc=json.loads(trace_path.read_text())
 traces=[]
 for sel in selection['selected_records']:
  rid=sel['record_id']; rec=records[rid]
  for sid in rec.get('source_ids',[]):
   src=sources[sid]
   if rec.get('knowledge_category')=='software_types':
    if (rid,sid,'supported_by') not in edges: raise SystemExit(f'missing source edge {rid}->{sid}')
    path=[rid,sid]; predicates=['supported_by']
   else:
    pred='exemplified_by' if rec.get('knowledge_category')=='reference_projects' else 'applies_to'
    type_id=next((t for t in brief.get('software_type_ids',[]) if t in rec.get('applicable_software_types',[]) and (t,rid,pred) in edges),None)
    if not type_id: raise SystemExit(f'missing applicability edge for {rid} in {directory.name}')
    if (rid,sid,'supported_by') not in edges: raise SystemExit(f'missing source edge {rid}->{sid}')
    path=[type_id,rid,sid]; predicates=[pred,'supported_by']
   traces.append({'knowledge_record_id':rid,'source_id':sid,'path':path,'predicates':predicates,'claim_locator':src['claim_locator'],'evidence_classification':class_for(src,rec)})
 if directory.name=='conflict_missing_evidence':
  # Scope-only supporting records are intentionally not selected as project recommendations.
  extras=[('software_type.mobile_applications','source.mobile_applications.01'),('sdlc.discovery_scope','source.iso.12207.2026.summary'),('reference.fastapi','source.fastapi.tests'),('reference.fastapi','source.fastapi.ci'),('prompt.review_change','source.github.copilot_task_practices')]
  existing={(x['knowledge_record_id'],x['source_id']) for x in traces}
  for rid,sid in extras:
   if (rid,sid) in existing: continue
   rec=records[rid]; src=sources[sid]
   if sid not in rec.get('source_ids',[]): raise SystemExit(f'{sid} is not scoped to supplemental record {rid}')
   if rec.get('knowledge_category')=='software_types':
    if (rid,sid,'supported_by') not in edges: raise SystemExit(f'missing source edge {rid}->{sid}')
    path=[rid,sid]; predicates=['supported_by']
   else:
    pred='exemplified_by' if rec.get('knowledge_category')=='reference_projects' else 'applies_to'
    type_id=next((t for t in json.loads((directory/'brief.json').read_text()).get('software_type_ids',[]) if t in rec.get('applicable_software_types',[]) and (t,rid,pred) in edges),None)
    if not type_id or (rid,sid,'supported_by') not in edges: raise SystemExit(f'missing active graph path for supplemental {rid}->{sid}')
    path=[type_id,rid,sid];predicates=[pred,'supported_by']
   traces.append({'knowledge_record_id':rid,'source_id':sid,'path':path,'predicates':predicates,'claim_locator':src['claim_locator'],'evidence_classification':class_for(src,rec)})
 trace_doc={'fixture_id':brief['fixture_id'],'traces':traces}
 selection['fixture_id']=brief['fixture_id']
 for name,obj in [('expected_selection.json',selection),('evidence_trace.json',trace_doc)]:
  (directory/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 changed.append({'fixture':directory.name,'traces':len(traces)})
print(json.dumps({'normalized':changed},indent=2))
