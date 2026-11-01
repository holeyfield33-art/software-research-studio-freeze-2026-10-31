"""Independently verify recovered archival bytes; do not execute archived code."""
from pathlib import Path, PurePosixPath
from io import BytesIO
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'preserved_freezes/SRS-FREEZE-2026-10-31-v1'
ARCHIVE = BASE / 'SOFTWARE_RESEARCH_STUDIO_FREEZE_2026-10-31_v1.zip'
TREE = BASE / 'tree'
sha = lambda b: hashlib.sha256(b).hexdigest()


def verify():
    assert sha(ARCHIVE.read_bytes()) == 'a39b30fee3304e843b0291770efe7a42e993d733c3c09d5321ea5f2d53e6ad04'
    scanned = 0
    nested_zips = 0
    key_patterns = [rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b', rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}\b', rb'\bAKIA[A-Z0-9]{16}\b']
    def scan(data):
        nonlocal scanned, nested_zips
        scanned += 1
        assert not any(re.search(p, data) for p in key_patterns), 'Potential credential pattern; publication requires review'
        if zipfile.is_zipfile(BytesIO(data)):
            nested_zips += 1
            with zipfile.ZipFile(BytesIO(data)) as nested:
                assert nested.testzip() is None
                for item in nested.infolist():
                    if not item.is_dir():
                        scan(nested.read(item))
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        names = z.namelist()
        assert len(names) == len(set(names)) == 177
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n and ':' not in n for n in names)
        for n in names:
            assert not z.getinfo(n).is_dir()
            data = z.read(n)
            assert (TREE / n).read_bytes() == data, n
            scan(data)
        assert sorted(p.relative_to(TREE).as_posix() for p in TREE.rglob('*') if p.is_file()) == sorted(names)
        inventory = json.loads(z.read('INVENTORY.json'))['files']
        for row in inventory:
            data = z.read(row['path'])
            assert len(data) == row['size_bytes'] and sha(data) == row['sha256'], row['path']
        assert z.read('SHA256SUMS.txt').decode().splitlines() == [f"{r['sha256']}  {r['path']}" for r in inventory]
        m = json.loads(z.read('current_003R/manifest.json'))
        for n, digest in m['sha256'].items():
            assert sha(z.read('current_003R/' + n)) == digest, n
        manifest_digest = z.read('current_003R/manifest.sha256').decode().split()[0]
        assert sha(z.read('current_003R/manifest.json')) == manifest_digest
        rzip = z.read('original_checkpoints/STUDIO_KNOWLEDGE_003R_checkpoint.zip')
        assert sha(rzip) == '5fea1fe5e8f19064df7ee9af4386aeb85046003c99ee83f9b4569432f0992aa8'
        assert z.read('original_checkpoints/STUDIO_KNOWLEDGE_003R_checkpoint.zip.sha256').decode().split()[0] == sha(rzip)
        with zipfile.ZipFile(BytesIO(rzip)) as r:
            assert r.testzip() is None
            for n in r.namelist():
                if not r.getinfo(n).is_dir():
                    assert r.read(n) == z.read('current_003R/' + n), n
        for n in ['STUDIO_KNOWLEDGE_001_initial_checkpoint.zip', 'STUDIO_KNOWLEDGE_002_checkpoint.zip', 'STUDIO_KNOWLEDGE_003_checkpoint.zip']:
            assert z.read('original_checkpoints/' + n) == (ROOT / 'original_checkpoints' / n).read_bytes(), n
        with zipfile.ZipFile(BytesIO(z.read('original_checkpoints/STUDIO_KNOWLEDGE_003_checkpoint.zip'))) as three:
            total = 0
            relationships = 0
            partitions = [n for n in three.namelist() if n.startswith('dataset/v1/') and n.endswith('.jsonl')]
            assert len(partitions) == 10
            for n in partitions:
                data = z.read('current_003R/' + n)
                assert data == three.read(n), n
                rows = [json.loads(line) for line in data.decode().splitlines() if line.strip()]
                total += len(rows)
                if n.endswith('/relationships.jsonl'):
                    relationships = len(rows)
        state = json.loads(z.read('FROZEN_STATE.json'))
        assert state['freeze_id'] == 'SRS-FREEZE-2026-10-31-v1'
        assert state['authoritative_checkpoint'] == 'STUDIO-KNOWLEDGE-003R'
    return dict(status='PASS', archive_sha256=sha(ARCHIVE.read_bytes()), archive_size_bytes=ARCHIVE.stat().st_size,
                extracted_files_byte_identical=177, inventory_files_verified=len(inventory),
                manifest_003R_hashes_verified=len(m['sha256']), original_001_002_003_archives_identical=True,
                original_003R_archive_sha256=sha(rzip), dataset_003_to_003R_partitions_identical=10,
                parsed_records=total, relationships=relationships, nested_zip_crc_checks=nested_zips,
                common_credential_pattern_scan=dict(files_scanned=scanned, findings=0, scope='Common key patterns only; not exhaustive privacy review'),
                behavioral_validation='NOT RERUN; archival verification only', gemini_round_2='Not contained in recovered freeze')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
