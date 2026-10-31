#!/usr/bin/env python3
"""Standard-library-only verifier of frozen Studio package (run after extraction)."""
from pathlib import Path
import hashlib,json,zipfile,sys
root=Path(__file__).resolve().parent
inventory=json.loads((root/'INVENTORY.json').read_text(encoding='utf-8'))
errors=[]
for r in inventory['files']:
 p=root/r['path']
 if not p.is_file():
  errors.append(f'MISSING {r["path"]}'); continue
 data=p.read_bytes()
 if len(data)!=r['size_bytes'] or hashlib.sha256(data).hexdigest()!=r['sha256']:
  errors.append(f'HASH MISMATCH {r["path"]}')
 if r['path'].endswith('.zip'):
  try:
   with zipfile.ZipFile(p) as z:
    bad=z.testzip()
    if bad: errors.append(f'CRC MISMATCH {r["path"]}::{bad}')
  except Exception as exc: errors.append(f'ZIP FAIL {r["path"]}: {exc}')
checksums=(root/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
expected=[f"{r['sha256']}  {r['path']}" for r in inventory['files']]
if checksums!=expected: errors.append('SHA256SUMS.txt does not match inventory')
state=json.loads((root/'FROZEN_STATE.json').read_text(encoding='utf-8'))
if state['authoritative_checkpoint']!='STUDIO-KNOWLEDGE-003R': errors.append('freeze scope mismatch')
print(json.dumps({'freeze_id':state['freeze_id'],'status':'PASS' if not errors else 'FAIL','files_verified':len(inventory['files'])-len([x for x in errors if x.startswith('MISSING')]),'errors':errors},indent=2))
sys.exit(0 if not errors else 1)
