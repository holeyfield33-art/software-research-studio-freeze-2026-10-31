#!/usr/bin/env python3
"""Build a stable-ID preservation and version-change map from stored checkpoint indexes."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'dataset/v1'; RESEARCH=ROOT/'research'; REPORTS=ROOT/'reports'
def load_index(label): return json.loads((RESEARCH/f'record-index-{label}.json').read_text(encoding='utf-8'))
def digest(record): return hashlib.sha256(json.dumps(record,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
def load_current():
 out={}
 for path in DATA.glob('*.jsonl'):
  out[path.name]={r['id']:r for line in path.read_text(encoding='utf-8').splitlines() if line.strip() for r in [json.loads(line)]}
 return out
old1,old2,current=load_index('001'),load_index('002'),load_current()
ids=lambda idx:{name:{x['id'] for x in rows} for name,rows in idx.items()}
cur_ids={name:set(rows) for name,rows in current.items()}
old2_ids=ids(old2); old1_ids=ids(old1)
missing_001={f:{x['id'] for x in rows}-cur_ids.get(f,set()) for f,rows in old1.items() if {x['id'] for x in rows}-cur_ids.get(f,set())}
missing_002={f:{x['id'] for x in rows}-cur_ids.get(f,set()) for f,rows in old2.items() if {x['id'] for x in rows}-cur_ids.get(f,set())}
changed=[]; added=[]
for part,rows in current.items():
 base={x['id']:x for x in old2.get(part,[])}
 for rid,r in rows.items():
  now=digest(r)
  if rid not in base: added.append({'partition':part,'id':rid,'version':r.get('version'),'current_sha256':now})
  elif now!=base[rid]['canonical_sha256']:
   changed.append({'partition':part,'id':rid,'from_version':base[rid].get('version'),'to_version':r.get('version'),'from_sha256':base[rid]['canonical_sha256'],'to_sha256':now})
hashes=json.loads((RESEARCH/'immutable-input-digests.json').read_text())
edge_rows=[r for l in (DATA/'relationships.jsonl').read_text().splitlines() if l.strip() for r in [json.loads(l)]]
report={'dataset_version':'1.2.0','schema_version':'1.1.0','inputs':{'001_sha256':hashes['001'],'002_sha256':hashes['002'],'original_archives_embedded':False},'preservation':{'001_record_count':sum(len(x) for x in old1.values()),'002_record_count':sum(len(x) for x in old2.values()),'current_record_count':sum(len(x) for x in current.values()),'001_missing_ids_by_partition':{k:sorted(v) for k,v in missing_001.items()},'002_missing_ids_by_partition':{k:sorted(v) for k,v in missing_002.items()},'all_001_ids_preserved':not missing_001,'all_002_ids_preserved':not missing_002},'changes_from_002':{'changed_existing_records':changed,'added_records':added,'changed_count':len(changed),'added_count':len(added),'relationship_status_counts':{'active':sum(e.get('status','active')!='superseded' for e in edge_rows),'superseded':sum(e.get('status')=='superseded' for e in edge_rows),'superseded_ids':sorted(e['id'] for e in edge_rows if e.get('status')=='superseded')}},'notes':['Stable record IDs were preserved; corrected content uses record versions and the change log.','Three out-of-scope repository applicability edges remain as superseded history rather than active candidates.','Added source and relationship records are enumerated by stable ID below.','No original 001/002 checkpoint ZIP is included in this package.']}
REPORTS.mkdir(exist_ok=True)
path=REPORTS/'version-map.json';path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'path':str(path),'missing_001':sum(map(len,missing_001.values())),'missing_002':sum(map(len,missing_002.values())),'changed':len(changed),'added':len(added)},indent=2))
