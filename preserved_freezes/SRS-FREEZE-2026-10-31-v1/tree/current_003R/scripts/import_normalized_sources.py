#!/usr/bin/env python3
"""Import verified source normalization from the completed research output.
Versions existing source records in place, preserving stable IDs. Safe/idempotent.
"""
import json
import hashlib
import argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dataset/v1'
parser=argparse.ArgumentParser();parser.add_argument('--research-output',default=str(ROOT/'research'/'source-normalization.json'));parser.add_argument('--inherited-sources',default=str(ROOT/'research'/'inherited-sources-v1.jsonl'));args=parser.parse_args()
obj=json.loads(Path(args.research_output).read_text(encoding='utf-8'))
normalized={s['id']:s for group in obj['results'] for s in group.get('sources',[])}
assert len(normalized)==35, f'expected 35 unique source IDs, found {len(normalized)}'
path=DATA/'sources.jsonl'
rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
inherited_path=Path(args.inherited_sources)
legacy_rows=[json.loads(x) for x in inherited_path.read_text(encoding='utf-8').splitlines() if x.strip()]
legacy_by_id={r['id']:r for r in legacy_rows}; legacy_ids=set(legacy_by_id)
missing=legacy_ids-normalized.keys(); assert not missing, f'missing normalization: {sorted(missing)}'
def digest(record): return hashlib.sha256(json.dumps(record,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
new=[]
for row in rows:
 if row['id'] in normalized and row.get('version')=='1.0.0':
  if digest(row)!=digest(legacy_by_id[row['id']]): raise SystemExit(f"Refusing to overwrite non-baseline/enriched source record {row['id']}; version the record or review manually.")
  new.append({**row,**normalized[row['id']]})
 else: new.append(row)
# The category overview self-identifiers become stable foreign keys; preserve record IDs and bump record version.
p=DATA/'software_types.jsonl'; records=[]
category_index_path=ROOT/'research'/'record-index-001.json'
if not category_index_path.exists() and any(json.loads(line).get('version')=='1.0.0' for line in p.read_text(encoding='utf-8').splitlines() if line.strip()): raise SystemExit('Refusing to migrate legacy software types without research/record-index-001.json.')
category_index={x['id']:x for x in json.loads(category_index_path.read_text(encoding='utf-8')).get('software_types.jsonl',[])} if category_index_path.exists() else {}
for line in p.read_text(encoding='utf-8').splitlines():
 if not line.strip(): continue
 r=json.loads(line)
 if r.get('version')=='1.0.0':
  baseline=category_index.get(r['id'])
  if not baseline or digest(r)!=baseline.get('canonical_sha256'): raise SystemExit(f"Refusing to overwrite non-baseline/enriched software type {r['id']}.")
  r['applicable_software_types']=[r['id']]; r['version']='1.1.0'
 records.append(r)
path.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in new),encoding='utf-8')
p.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in records),encoding='utf-8')
# Add claim-level category-to-source provenance edges with stable next sequence; never replace existing edges.
p=DATA/'relationships.jsonl'; edges=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
existing={e['id'] for e in edges}; nextid=max([int(e['id'].split('.')[-1]) for e in edges if e['id'].startswith('edge.')]+[0])+1
source_map={r['id']:r for r in new}
for cat in records:
 for sid in cat.get('source_ids',[]):
  src=source_map.get(sid)
  if not src: continue
  # Reuse matching edge if this exact claim mapping already exists.
  if any(e.get('source_endpoint')==cat['id'] and e.get('target_endpoint')==sid for e in edges): continue
  edgeid=f'edge.{nextid:04d}'; nextid+=1
  edges.append({'id':edgeid,'version':'1.0.0','source_endpoint':cat['id'],'target_endpoint':sid,'predicate':'exemplified_by','scope_qualifier':src['claim_locator'],'source_ids':[sid],'evidence_classification':'observed_implementation' if src.get('repo_commit') not in ('not_applicable','pending') else 'documented_guidance'})
p.write_text(''.join(json.dumps(e,ensure_ascii=False,sort_keys=True)+'\n' for e in edges),encoding='utf-8')
print(json.dumps({'normalized_inherited_sources':35,'category_records_versioned':len(records),'category_source_edges':len(edges)-len(existing)},indent=2))
