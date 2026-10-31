#!/usr/bin/env python3
"""Verify package manifest/file digests and an optional ZIP plus detached checksum."""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def verify(root,archive=None):
 root=Path(root); errors=[]; mp=root/'manifest.json'
 if not mp.exists(): return {'status':'FAIL','errors':['manifest.json is missing']}
 manifest=json.loads(mp.read_text(encoding='utf-8')); entries=manifest.get('sha256',{})
 for rel,expected in entries.items():
  p=root/rel
  if not p.is_file(): errors.append(f'missing manifest member: {rel}')
  elif sha(p)!=expected: errors.append(f'hash mismatch: {rel}')
 side=root/'manifest.sha256'
 if side.exists() and side.read_text().split()[0]!=sha(mp):errors.append('manifest.sha256 mismatch')
 if archive:
  archive=Path(archive)
  if not archive.is_file():errors.append(f'archive missing: {archive}')
  else:
   zhash=sha(archive); zside=Path(str(archive)+'.sha256')
   if not zside.is_file():errors.append('detached archive checksum sidecar missing')
   elif zside.read_text().split()[0]!=zhash:errors.append('archive SHA-256 sidecar mismatch')
   try:
    with zipfile.ZipFile(archive) as z:
     bad=z.testzip()
     if bad:errors.append(f'ZIP CRC failure: {bad}')
     names=set(z.namelist())
     expected=set(entries)|{'manifest.json','manifest.sha256'}
     if names!=expected:errors.append(f'archive member set mismatch: missing={sorted(expected-names)} extra={sorted(names-expected)}')
     forbidden=[n for n in names if n.endswith('.tmp') or n.endswith('.pyc') or '__pycache__' in n]
     if forbidden:errors.append('forbidden package artifacts: '+', '.join(sorted(forbidden)))
   except Exception as exc:errors.append(f'archive unreadable: {exc}')
 return {'status':'PASS' if not errors else 'FAIL','manifest_build_date_utc':manifest.get('build_date_utc'),'manifest_file_count':len(entries),'errors':errors}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));ap.add_argument('--archive');a=ap.parse_args();r=verify(a.root,a.archive);print(json.dumps(r,indent=2));return 0 if r['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
