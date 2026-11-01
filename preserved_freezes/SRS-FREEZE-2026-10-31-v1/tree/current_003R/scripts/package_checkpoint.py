#!/usr/bin/env python3
"""Build a research-only 003R checkpoint without replacing any parent archive."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
HOME=Path('/home/ubuntu')

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def run(args):
    proc=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
    if proc.returncode:
        raise SystemExit(f"Command failed ({proc.returncode}): {' '.join(map(str,args))}\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout

def verify_parent_archives(parent003):
    parents=[
        (HOME/'STUDIO_KNOWLEDGE_001_initial_checkpoint.zip',HOME/'STUDIO_KNOWLEDGE_001_initial_checkpoint.zip.sha256'),
        (HOME/'STUDIO_KNOWLEDGE_002_checkpoint.zip',HOME/'STUDIO_KNOWLEDGE_002_checkpoint.sha256'),
        (Path(parent003),Path(str(parent003)+'.sha256')),
    ]
    result={}
    for archive,sidecar in parents:
        if not archive.is_file() or not sidecar.is_file():
            raise SystemExit(f'Missing immutable parent or detached checksum: {archive} / {sidecar}')
        expected=sidecar.read_text().split()[0]
        actual=sha(archive)
        if expected!=actual:
            raise SystemExit(f'Immutable parent checksum mismatch: {archive}')
        result[archive.name]={'path':str(archive),'sha256':actual,'sidecar_verified':True}
    parent=Path(parent003)
    with zipfile.ZipFile(parent) as z:
        manifest=json.loads(z.read('manifest.json'))
    dataset_hashes={k:v for k,v in manifest.get('sha256',{}).items() if k.startswith('dataset/v1/')}
    mismatches=[]
    for rel,expected in dataset_hashes.items():
        path=ROOT/rel
        if not path.is_file() or sha(path)!=expected:
            mismatches.append(rel)
    if mismatches:
        raise SystemExit('003 baseline JSONL changed in 003R: '+', '.join(mismatches))
    record={'parent_archive':parent.name,'parent_archive_sha256':result[parent.name]['sha256'],'dataset_member_count':len(dataset_hashes),'all_dataset_members_unchanged':True,'dataset_member_sha256':dataset_hashes}
    (ROOT/'research/parent-003-dataset-hashes.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (ROOT/'research/checkpoint-003.sha256').write_text(result[parent.name]['sha256']+'\n',encoding='utf-8')
    lineage_path=ROOT/'research/immutable-input-digests.json'
    lineage=json.loads(lineage_path.read_text(encoding='utf-8'))
    lineage['003']=result[parent.name]['sha256']
    lineage_path.write_text(json.dumps(lineage,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result,record

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',default=str(HOME/'STUDIO_KNOWLEDGE_003R_checkpoint.zip'))
    parser.add_argument('--parent-003',default=str(HOME/'STUDIO_KNOWLEDGE_003_checkpoint.zip'))
    args=parser.parse_args();archive=Path(args.archive).resolve();sidecar=Path(str(archive)+'.sha256')
    if archive.exists() or sidecar.exists():
        raise SystemExit(f'Refusing to overwrite an existing checkpoint or sidecar: {archive}')
    parents,parent_dataset=verify_parent_archives(args.parent_003)
    run([sys.executable,'scripts/validate_dataset.py','--report','reports/dataset-validation.json'])
    run([sys.executable,'scripts/verify_fixtures.py','--report','reports/fixture-validation.json'])
    run([sys.executable,'scripts/build_version_map.py'])
    run([sys.executable,'scripts/verify_selector.py'])
    run([sys.executable,'scripts/run_regression_tests.py'])
    run([sys.executable,'scripts/build_003r_reports.py'])
    dataset_report=json.loads((ROOT/'reports/dataset-validation.json').read_text())
    fixture_report=json.loads((ROOT/'reports/fixture-validation.json').read_text())
    tests=json.loads((ROOT/'reports/regression-tests.json').read_text())
    selector=json.loads((ROOT/'reports/selector-verification.json').read_text())
    report=json.loads((ROOT/'reports/validation-report-003r.json').read_text())
    if any(x.get('status')!='PASS' for x in (dataset_report,fixture_report,tests,report)):
        raise SystemExit('Refusing to package a non-PASS acceptance report')
    if selector.get('oracle_fail')!=0 or selector.get('oracle_cases')<12 or selector.get('cleanroom_no_oracle_access')!='PASS' or selector.get('negative_controls',{}).get('status')!='PASS':
        raise SystemExit('Refusing to package failed selector/oracle/negative-control validation')
    for tmp in ROOT.rglob('*.tmp'):
        if tmp.is_file():tmp.unlink()
    allowed=['README.md','dataset','schemas','fixtures','selection_cases','oracles','selector_runs','rules','docs','tests','scripts','reports','research']
    files=[]
    for name in allowed:
        path=ROOT/name
        if not path.exists():continue
        candidates=[path] if path.is_file() else [p for p in path.rglob('*') if p.is_file()]
        for item in candidates:
            if '__pycache__' in item.parts or item.suffix in ('.pyc','.tmp') or item.name.endswith('.zip'):continue
            files.append(item)
    files=sorted(set(files),key=lambda p:p.relative_to(ROOT).as_posix())
    if not files:raise SystemExit('No package files found')
    members={p.relative_to(ROOT).as_posix():sha(p) for p in files if p.name not in ('manifest.json','manifest.sha256')}
    preservation=json.loads((ROOT/'reports/version-map.json').read_text())['preservation']
    if not preservation.get('all_001_ids_preserved') or not preservation.get('all_002_ids_preserved'):
        raise SystemExit('Refusing to package missing inherited 001/002 stable IDs')
    manifest={
        'project':'STUDIO-KNOWLEDGE-003R',
        'dataset_version':dataset_report['dataset_version'],
        'schema_version':dataset_report['schema_version'],
        'selector_rules_version':json.loads((ROOT/'rules/selection-rules.json').read_text())['rules_version'],
        'build_date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'research-only deterministic selection prototype; no Stage 004, Studio integration, product code, or hosted systems',
        'validation_status':'PASS','dataset_status':dataset_report['status'],'fixture_status':fixture_report['status'],'regression_status':tests['status'],
        'selector_oracle_cases':selector['oracle_cases'],'selector_oracle_pass':selector['oracle_pass'],'selector_oracle_fail':selector['oracle_fail'],
        'selector_cleanroom_no_oracle_access':selector['cleanroom_no_oracle_access'],'selector_negative_controls':selector['negative_controls']['count'],
        'regression_tests':tests['tests_run'],'parent_checkpoints':parents,'parent_003_dataset_unchanged':parent_dataset['all_dataset_members_unchanged'],
        'stable_id_preservation':preservation,'original_checkpoint_zips_embedded':False,'sha256':members
    }
    manifest_path=ROOT/'manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    manifest_hash=sha(manifest_path);(ROOT/'manifest.sha256').write_text(f'{manifest_hash}  manifest.json\n',encoding='utf-8')
    verifier=[sys.executable,'scripts/verify_manifest.py','--root',str(ROOT)]
    pre=json.loads(run(verifier))
    if pre['status']!='PASS':raise SystemExit('In-tree manifest verification failed: '+json.dumps(pre))
    archive.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel in sorted(set(members)|{'manifest.json','manifest.sha256'}):
            z.write(ROOT/rel,arcname=rel)
    archive_hash=sha(archive);sidecar.write_text(f'{archive_hash}  {archive.name}\n',encoding='utf-8')
    post=json.loads(run(verifier+['--archive',str(archive)]))
    if post['status']!='PASS':raise SystemExit('Archive verification failed: '+json.dumps(post))
    result={'status':'PASS','project':'STUDIO-KNOWLEDGE-003R','archive':str(archive),'archive_sha256':archive_hash,'sidecar':str(sidecar),'archive_size_bytes':archive.stat().st_size,'manifest_sha256':manifest_hash,'manifest_file_count':len(members),'dataset_records':dataset_report['record_count'],'selector_cases':selector['oracle_cases'],'selector_cases_passed':selector['oracle_pass'],'regression_tests':tests['tests_run'],'parent_003_dataset_unchanged':parent_dataset['all_dataset_members_unchanged'],'parent_archives_embedded':False,'verifier':post}
    print(json.dumps(result,indent=2,ensure_ascii=False));return 0

if __name__=='__main__':sys.exit(main())
