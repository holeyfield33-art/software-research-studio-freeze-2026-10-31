#!/usr/bin/env python3
import contextlib, hashlib, io, json, os, shutil, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'scripts'; DATA=ROOT/'dataset/v1'; RESEARCH=ROOT/'research'
sys.path.insert(0,str(SCRIPTS))
import validate_dataset as vd
import validate_fixtures as vf
from verify_manifest import verify as verify_manifest

def read_jsonl(path): return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def write_jsonl(path,rows): path.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in rows),encoding='utf-8')
def copy_tree(src,dst): shutil.copytree(src,dst,dirs_exist_ok=True)

class CheckpointAndFixtureTests(unittest.TestCase):
 def test_001_to_002_to_003_ids_and_parent_digests(self):
  idx1=json.loads((RESEARCH/'record-index-001.json').read_text()); idx2=json.loads((RESEARCH/'record-index-002.json').read_text())
  current={p.name:{r['id'] for r in read_jsonl(p)} for p in DATA.glob('*.jsonl')}
  ids1={part:{x['id'] for x in rows} for part,rows in idx1.items()}; ids2={part:{x['id'] for x in rows} for part,rows in idx2.items()}
  self.assertEqual(sum(map(len,ids1.values())),45); self.assertEqual(sum(map(len,ids2.values())),522)
  for part,ids in ids1.items(): self.assertTrue(ids<=ids2.get(part,set()),f'001 IDs lost before 002: {part}')
  for part,ids in ids2.items(): self.assertTrue(ids<=current.get(part,set()),f'002 IDs lost in 003: {part}')
  hashes=json.loads((RESEARCH/'immutable-input-digests.json').read_text())
  for label in ('001','002'):
   sidecar=RESEARCH/f'checkpoint-{label}.sha256'
   self.assertTrue(sidecar.exists())
   self.assertEqual(sidecar.read_text().split()[0],hashes[label])
  version=json.loads((ROOT/'reports/version-map.json').read_text())
  self.assertTrue(version['preservation']['all_001_ids_preserved']); self.assertTrue(version['preservation']['all_002_ids_preserved'])

 def test_dataset_and_golden_fixtures_validate(self):
  with tempfile.TemporaryDirectory() as td:
   report=Path(td)/'dataset.json'
   p=subprocess.run([sys.executable,str(SCRIPTS/'validate_dataset.py'),'--report',str(report)],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr); self.assertEqual(json.loads(report.read_text())['status'],'PASS')
   report2=Path(td)/'fixtures.json'
   p=subprocess.run([sys.executable,str(SCRIPTS/'verify_fixtures.py'),'--report',str(report2)],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   fixtures=json.loads(report2.read_text()); self.assertEqual(fixtures['fixture_count'],4); self.assertEqual(fixtures['error_count'],0)
   negative=next(x for x in fixtures['results'] if x['directory']=='conflict_missing_evidence')
   self.assertEqual(len(negative['negative_cases']),5)

 def test_negative_controls_detect_tampering(self):
  records,sources,_=vf.load_catalog(); d=ROOT/'fixtures/conflict_missing_evidence'
  docs={n:json.loads((d/n).read_text()) for n in ['brief.json','expected_selection.json','expected_rejections.json','expected_deliverables.json','evidence_trace.json','negative_cases.json']}
  cases={c['case_type']:c for c in docs['negative_cases.json']['cases']}
  mutations=[]
  rec={k:dict(v) for k,v in records.items()}
  rec['software_type.apis']['source_ids']=list(rec['software_type.apis']['source_ids'])+['source.mobile_applications.01']
  c=json.loads(json.dumps(cases['stack_mismatch'])); mutations.append((c,rec))
  c=json.loads(json.dumps(cases['superseded_standard'])); c['details']['organization_adoption_known']=True; mutations.append((c,records))
  c=json.loads(json.dumps(cases['missing_test_execution'])); c['details']['workflow_configuration_is_execution']=True; mutations.append((c,records))
  altered={k:dict(v) for k,v in records.items()}; altered['arch.minimal_viable_structure']['category_specific']=dict(records['arch.minimal_viable_structure']['category_specific']); altered['arch.minimal_viable_structure']['category_specific']['decision_policy']='universal_default'
  c=json.loads(json.dumps(cases['source_tension'])); mutations.append((c,altered))
  c=json.loads(json.dumps(cases['unknown_requirement'])); c['details']['no_catalog_match']=False; mutations.append((c,records))
  for case,catalog in mutations:
   errs=[]; vf.validate_case_structure(case,catalog,sources,docs,errs); self.assertTrue(errs,case['case_id']+' mutation was not caught')

class MutationValidationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root=Path(self.tmp.name)
  self.data=self.root/'dataset/v1'; self.data.mkdir(parents=True)
  self.schemas=self.root/'schemas'; shutil.copytree(ROOT/'schemas',self.schemas)
  for p in DATA.glob('*.jsonl'): shutil.copy2(p,self.data/p.name)
 def run_mutated_validator(self):
  report=self.root/'reports/validation.json'
  with mock.patch.object(vd,'ROOT',self.root),mock.patch.object(vd,'DATA',self.data),mock.patch.object(vd,'SCHEMAS',self.schemas),mock.patch.object(sys,'argv',['validate_dataset.py','--report',str(report)]),contextlib.redirect_stdout(io.StringIO()):
   rc=vd.main()
  return rc,json.loads(report.read_text())
 def test_unknown_category_id_fails(self):
  p=self.data/'engineering_practices.jsonl'; rows=read_jsonl(p); rows[0]['applicable_software_types'].append('software_type.ghost'); write_jsonl(p,rows)
  rc,r=self.run_mutated_validator(); self.assertNotEqual(rc,0); self.assertTrue(any('unknown applicable software type' in e['message'] for e in r['errors']))
 def test_dangling_relationship_fails(self):
  p=self.data/'relationships.jsonl'; rows=read_jsonl(p); rows[0]['target_endpoint']='record.ghost'; write_jsonl(p,rows)
  rc,r=self.run_mutated_validator(); self.assertNotEqual(rc,0); self.assertTrue(any('dangling target_endpoint' in e['message'] for e in r['errors']))
 def test_malformed_category_specific_fails(self):
  p=self.data/'prompt_patterns.jsonl'; rows=read_jsonl(p); rows[0]['category_specific']={}; write_jsonl(p,rows)
  rc,r=self.run_mutated_validator(); self.assertNotEqual(rc,0); self.assertTrue(any('category_specific' in e['message'] or 'required property' in e['message'] for e in r['errors']))
 def test_roadmap_unknown_dependency_and_cycle_fail(self):
  unknown={'roadmap_patterns':[(1,{'id':'roadmap.bad','category_specific':{'example_tasks':[{'task_id':'a','depends_on':['missing']}]}})]}; errors=[]; vd.check_roadmap(unknown,errors)
  self.assertTrue(any('unknown task dependency' in e['message'] for e in errors))
  cycle={'roadmap_patterns':[(1,{'id':'roadmap.cycle','category_specific':{'example_tasks':[{'task_id':'a','depends_on':['b']},{'task_id':'b','depends_on':['a']}]}})]}; errors=[]; vd.check_roadmap(cycle,errors)
  self.assertTrue(any('cyclic example task dependency' in e['message'] for e in errors))

class SafeRepeatTests(unittest.TestCase):
 def test_manifest_hash_verifier_detects_file_tampering(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); f=root/'payload.txt'; f.write_text('original\n')
   manifest={'sha256':{'payload.txt':hashlib.sha256(f.read_bytes()).hexdigest()},'build_date_utc':'2026-10-31T00:00:00Z'}
   m=root/'manifest.json'; m.write_text(json.dumps(manifest)+'\n')
   (root/'manifest.sha256').write_text(hashlib.sha256(m.read_bytes()).hexdigest()+'  manifest.json\n')
   self.assertEqual(verify_manifest(root)['status'],'PASS')
   f.write_text('tampered\n'); self.assertEqual(verify_manifest(root)['status'],'FAIL')

 def test_source_import_idempotent_and_preserves_versioned_enrichment(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); copy_tree(DATA,root/'dataset/v1'); (root/'research').mkdir()
   for n in ('source-normalization.json','inherited-sources-v1.jsonl','record-index-001.json'): shutil.copy2(RESEARCH/n,root/'research'/n)
   (root/'scripts').mkdir(); shutil.copy2(SCRIPTS/'import_normalized_sources.py',root/'scripts/import_normalized_sources.py')
   cmd=[sys.executable,str(root/'scripts/import_normalized_sources.py')]
   # Restore the exact inherited source rows so the test exercises a genuine first-time source import.
   baseline=read_jsonl(root/'research/inherited-sources-v1.jsonl'); baseline_by={x['id']:x for x in baseline}
   sp=root/'dataset/v1/sources.jsonl'; rows=read_jsonl(sp); rows=[baseline_by.get(x['id'],x) for x in rows]; write_jsonl(sp,rows)
   p=subprocess.run(cmd,cwd=root,capture_output=True,text=True); self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   rows=read_jsonl(sp); row=next(x for x in rows if x['id']=='source.apis.01'); row['version']='9.9.0'; row['user_enriched_note']='must survive reruns'; write_jsonl(sp,rows)
   cp=root/'dataset/v1/software_types.jsonl'; cats=read_jsonl(cp); cat=next(x for x in cats if x['id']=='software_type.apis'); cat['version']='9.9.0'; cat['user_enriched_note']='preserve category extension'; write_jsonl(cp,cats)
   before={p.name:p.read_bytes() for p in (root/'dataset/v1').glob('*.jsonl')}
   for _ in range(2):
    p=subprocess.run(cmd,cwd=root,capture_output=True,text=True); self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   for name,data in before.items(): self.assertEqual((root/'dataset/v1'/name).read_bytes(),data,name+' changed after enriched-row import rerun')
   self.assertEqual(next(x for x in read_jsonl(sp) if x['id']=='source.apis.01')['user_enriched_note'],'must survive reruns')

 def test_source_import_refuses_unversioned_user_edit(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); copy_tree(DATA,root/'dataset/v1'); (root/'research').mkdir(); (root/'scripts').mkdir()
   for n in ('source-normalization.json','inherited-sources-v1.jsonl','record-index-001.json'): shutil.copy2(RESEARCH/n,root/'research'/n)
   shutil.copy2(SCRIPTS/'import_normalized_sources.py',root/'scripts/import_normalized_sources.py')
   baseline=read_jsonl(root/'research/inherited-sources-v1.jsonl'); by={x['id']:x for x in baseline}; p=root/'dataset/v1/sources.jsonl'; rows=read_jsonl(p); rows=[by.get(x['id'],x) for x in rows]
   row=next(x for x in rows if x['id']=='source.apis.01'); row['user_enriched_note']='unversioned user work'; write_jsonl(p,rows); before=p.read_bytes()
   result=subprocess.run([sys.executable,str(root/'scripts/import_normalized_sources.py')],cwd=root,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0); self.assertIn('Refusing to overwrite non-baseline/enriched source record',result.stdout+result.stderr); self.assertEqual(p.read_bytes(),before)

 def test_completed_migration_rerun_preserves_user_enrichment(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); copy_tree(DATA,root/'dataset/v1'); copy_tree(RESEARCH,root/'research'); (root/'scripts').mkdir()
   shutil.copy2(SCRIPTS/'migrate_003.py',root/'scripts/migrate_003.py')
   p=root/'dataset/v1/architecture_patterns.jsonl'; rows=read_jsonl(p); row=next(x for x in rows if x['id']=='arch.minimal_viable_structure'); row['category_specific']['user_enriched_option_note']='do not erase'; write_jsonl(p,rows)
   before={p.name:p.read_bytes() for p in (root/'dataset/v1').glob('*.jsonl')}
   result=subprocess.run([sys.executable,str(root/'scripts/migrate_003.py')],cwd=root,capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stdout+result.stderr)
   for name,data in before.items(): self.assertEqual((root/'dataset/v1'/name).read_bytes(),data,name+' changed on completed migration rerun')

 def test_unmarked_migration_refuses_nonbaseline_workspace(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); copy_tree(DATA,root/'dataset/v1'); (root/'research').mkdir(); shutil.copy2(RESEARCH/'record-index-002.json',root/'research/record-index-002.json'); (root/'scripts').mkdir(); shutil.copy2(SCRIPTS/'migrate_003.py',root/'scripts/migrate_003.py')
   p=root/'dataset/v1/sources.jsonl'; before=p.read_bytes()
   result=subprocess.run([sys.executable,str(root/'scripts/migrate_003.py')],cwd=root,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0); self.assertIn('Refusing to overwrite non-baseline/enriched record',result.stderr+result.stdout); self.assertEqual(p.read_bytes(),before)

if __name__=='__main__': unittest.main(verbosity=2)
