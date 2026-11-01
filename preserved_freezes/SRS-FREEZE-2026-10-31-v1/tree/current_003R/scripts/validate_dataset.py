#!/usr/bin/env python3
"""Validate the complete STUDIO_KNOWLEDGE_003 dataset and its typed graph."""
from pathlib import Path
import argparse, json, sys
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'dataset' / 'v1'
SCHEMAS = ROOT / 'schemas'
PARTITIONS = ['software_types','engineering_practices','sdlc_stages','architecture_patterns','prompt_patterns','roadmap_patterns','verification_gates','reference_projects','sources','relationships']
KNOWLEDGE = set(PARTITIONS) - {'sources','relationships'}


def read_jsonl(path):
    out=[]
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip(): continue
        try: out.append((number, json.loads(line)))
        except Exception as exc: raise ValueError(f'{path}:{number}: invalid JSON: {exc}')
    return out

def load_schema(name): return json.loads((SCHEMAS/name).read_text(encoding='utf-8'))
def add(errors, file, line, rid, message): errors.append({'file':file,'line':line,'record_id':rid,'message':message})

def check_roadmap(rows, errors):
    for line, obj in rows['roadmap_patterns']:
        tasks=obj.get('category_specific',{}).get('example_tasks',[])
        tids=[t.get('task_id') for t in tasks]
        if len(tids)!=len(set(tids)): add(errors,'dataset/v1/roadmap_patterns.jsonl',line,obj.get('id'),'duplicate example task_id')
        graph={t.get('task_id'):t.get('depends_on',[]) for t in tasks}
        for task_id, deps in graph.items():
            for dep in deps:
                if dep not in graph: add(errors,'dataset/v1/roadmap_patterns.jsonl',line,obj.get('id'),f'unknown task dependency {dep} in {task_id}')
        visiting=set(); visited=set(); cyclic=False
        def visit(node):
            nonlocal cyclic
            if node in visiting: cyclic=True; return
            if node in visited: return
            visiting.add(node)
            for dep in graph.get(node,[]):
                if dep in graph: visit(dep)
            visiting.remove(node); visited.add(node)
        for node in graph: visit(node)
        if cyclic: add(errors,'dataset/v1/roadmap_patterns.jsonl',line,obj.get('id'),'cyclic example task dependency')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--report',default=str(ROOT/'reports'/'validation-report.json'))
    args=ap.parse_args()
    schema_files={'knowledge':'knowledge-record.schema.json','source':'source-record.schema.json','relationship':'relationship.schema.json'}
    schemas={k:load_schema(filename) for k,filename in schema_files.items()}
    validators={k:Draft202012Validator(s,format_checker=FormatChecker()) for k,s in schemas.items()}
    errors=[]; rows={}; counts={}; all_ids={}; id_location={}
    for part in PARTITIONS:
        path=DATA/(part+'.jsonl')
        if not path.exists():
            rows[part]=[]; counts[part]=0
            if part in KNOWLEDGE: add(errors,str(path.relative_to(ROOT)),0,None,'required partition missing')
            continue
        entries=read_jsonl(path); rows[part]=entries; counts[part]=len(entries)
        validator=validators['source' if part=='sources' else 'relationship' if part=='relationships' else 'knowledge']
        seen=set()
        for line,obj in entries:
            relpath=str(path.relative_to(ROOT)); rid=obj.get('id')
            for err in validator.iter_errors(obj):
                add(errors,relpath,line,rid,err.message+' at /'+'/'.join(map(str,err.absolute_path)))
            if not rid: continue
            if rid in seen: add(errors,relpath,line,rid,'duplicate ID within partition')
            seen.add(rid)
            if rid in all_ids: add(errors,relpath,line,rid,f'ID reused in {part}; first seen in {all_ids[rid]}')
            else: all_ids[rid]=part; id_location[rid]=(part,line,obj)
    source_ids={r.get('id') for _,r in rows['sources']}
    software_ids={r.get('id') for _,r in rows['software_types']}
    for part in KNOWLEDGE:
        for line,obj in rows[part]:
            for tid in obj.get('applicable_software_types',[]):
                if tid not in software_ids: add(errors,f'dataset/v1/{part}.jsonl',line,obj.get('id'),f'unknown applicable software type: {tid}')
            for sid in obj.get('source_ids',[]):
                if sid not in source_ids: add(errors,f'dataset/v1/{part}.jsonl',line,obj.get('id'),f'unknown source_id: {sid}')
            for rid in obj.get('related_record_ids',[]):
                if rid not in all_ids: add(errors,f'dataset/v1/{part}.jsonl',line,obj.get('id'),f'unknown related_record_id: {rid}')
    # Source IDs on graph edges must resolve, and typed predicates must agree with endpoint categories.
    endpoint={rid:part for rid,part in all_ids.items()}
    allowed={
      'applies_to':({'software_types'},KNOWLEDGE-{'software_types'}),
      'requires':(KNOWLEDGE,KNOWLEDGE),
      'verified_by':({'engineering_practices','sdlc_stages','architecture_patterns','prompt_patterns'},{'verification_gates'}),
      'implemented_with':(KNOWLEDGE,{'reference_projects'}),
      'informs':(KNOWLEDGE,KNOWLEDGE),
      'produces':(KNOWLEDGE,KNOWLEDGE),
      'exemplified_by':({'software_types','reference_projects'},{'reference_projects','sources'}),
      'supported_by':(KNOWLEDGE,{'sources'})
    }
    edge_sets=set(); edges_by_key={}; all_edge_keys=set(); superseded_count=0
    for line,e in rows['relationships']:
        key=(e.get('source_endpoint'),e.get('target_endpoint'),e.get('predicate'))
        if key in all_edge_keys and e.get('status','active')=='active': add(errors,'dataset/v1/relationships.jsonl',line,e.get('id'),'duplicate active typed relationship edge')
        all_edge_keys.add(key)
        if e.get('status','active')=='superseded': superseded_count+=1
        else: edge_sets.add(key); edges_by_key[key]=e
        for field in ['source_endpoint','target_endpoint']:
            if e.get(field) not in endpoint: add(errors,'dataset/v1/relationships.jsonl',line,e.get('id'),f'dangling {field}: {e.get(field)}')
        for sid in e.get('source_ids',[]):
            if sid not in source_ids: add(errors,'dataset/v1/relationships.jsonl',line,e.get('id'),f'dangling source_id: {sid}')
        pred=e.get('predicate'); pair=allowed.get(pred)
        if pair:
            left=endpoint.get(e.get('source_endpoint')); right=endpoint.get(e.get('target_endpoint'))
            if left not in pair[0] or right not in pair[1]: add(errors,'dataset/v1/relationships.jsonl',line,e.get('id'),f'predicate {pred} does not allow endpoint types {left}->{right}')
    for part in KNOWLEDGE | {'relationships'}:
        for line,obj in rows[part]:
            for sid in obj.get('source_ids',[]):
                if sid not in source_ids: add(errors,f'dataset/v1/{part}.jsonl',line,obj.get('id'),f'dangling source_id: {sid}')
    # Candidate applicability arrays are declarations, not proof of category coverage; graph edges must mirror them exactly.
    for part in KNOWLEDGE-{'software_types'}:
        predicate='exemplified_by' if part=='reference_projects' else 'applies_to'
        for line,obj in rows[part]:
            expected={(tid,obj.get('id'),predicate) for tid in obj.get('applicable_software_types',[])}
            actual={k for k in edge_sets if k[1]==obj.get('id') and k[2]==predicate and endpoint.get(k[0])=='software_types'}
            for key in sorted(expected-actual): add(errors,f'dataset/v1/{part}.jsonl',line,obj.get('id'),f'applicability relationship missing for {key[0]}')
            for key in sorted(actual-expected): add(errors,f'dataset/v1/{part}.jsonl',line,obj.get('id'),f'graph applicability conflicts with applicable_software_types for {key[0]}')
    # Knowledge record source provenance is represented by a typed supported_by edge with the same source ID.
    for part in KNOWLEDGE:
        for line,obj in rows[part]:
            for sid in obj.get('source_ids',[]):
                edge=edges_by_key.get((obj.get('id'),sid,'supported_by'))
                if edge is None: add(errors,f'dataset/v1/{part}.jsonl',line,obj.get('id'),f'missing supported_by graph edge to {sid}')
                elif sid not in edge.get('source_ids',[]): add(errors,'dataset/v1/relationships.jsonl',0,edge.get('id'),f'supported_by edge lacks its target source as evidence: {sid}')
    # Repository citations remain commit-pinned to the exact file path; test/config source is never a run result.
    for line,source in rows['sources']:
        commit=source.get('repo_commit','not_applicable'); path=source.get('file_path','not_applicable')
        if commit!='not_applicable' and path not in ('not_applicable','repository tree inventory'):
            token=f'/{commit}/{path}'
            if token not in source.get('canonical_url',''): add(errors,'dataset/v1/sources.jsonl',line,source.get('id'),f'canonical_url is not pinned to repo_commit plus file_path ({token})')
    check_roadmap(rows,errors)
    arch_ids=set()
    for line,obj in rows['architecture_patterns']:
        ids=[o.get('option_id') for o in obj.get('category_specific',{}).get('options',[])]
        if len(ids)!=len(set(ids)): add(errors,'dataset/v1/architecture_patterns.jsonl',line,obj.get('id'),'duplicate architecture option_id')
        record_sources=set(obj.get('source_ids',[]))
        for option in obj.get('category_specific',{}).get('options',[]):
            for sid in option.get('evidence_source_ids',[]):
                if sid not in record_sources: add(errors,'dataset/v1/architecture_patterns.jsonl',line,obj.get('id'),f'option source {sid} is not in record source_ids')
    # Gate outcomes are a tri-state contract, and a PASS always needs candidate-bound executed evidence.
    for line,obj in rows['verification_gates']:
        cs=obj.get('category_specific',{})
        if cs.get('outcomes')!=['PASS','FAIL','INCOMPLETE']: add(errors,'dataset/v1/verification_gates.jsonl',line,obj.get('id'),'gate outcomes must be PASS/FAIL/INCOMPLETE')
        if cs.get('candidate_binding',{}).get('required_for_pass') is not True or cs.get('candidate_binding',{}).get('execution_record_required') is not True:
            add(errors,'dataset/v1/verification_gates.jsonl',line,obj.get('id'),'gate PASS must require candidate identity and an execution record')
    counts['source_count']=len(rows['sources']); counts['relationship_count']=len(rows['relationships'])
    counts['active_relationship_count']=len(edge_sets); counts['superseded_relationship_count']=superseded_count
    report={'dataset_version':'1.2.0','schema_version':'1.1.0','counts':counts,'record_count':sum(counts[p] for p in PARTITIONS),'error_count':len(errors),'errors':errors,'status':'PASS' if not errors else 'FAIL'}
    out=Path(args.report); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False)); return 0 if not errors else 1

if __name__=='__main__': sys.exit(main())
