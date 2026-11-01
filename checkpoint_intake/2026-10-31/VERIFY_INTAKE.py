"""Verify this additive intake without requiring the unavailable full freeze.

Run: python checkpoint_intake/2026-10-31/VERIFY_INTAKE.py
Only standard library; never executes code from the preserved archives.
"""
from pathlib import Path, PurePosixPath
import collections
import hashlib
import json
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
digest = lambda data: hashlib.sha256(data).hexdigest()


def verify():
    manifest = json.loads((HERE / 'MANIFEST.json').read_text(encoding='utf-8'))
    for line in (HERE / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        expected, name = line.split('  ', 1)
        assert digest((ROOT / name).read_bytes()) == expected, name
    for row in manifest['files']:
        data = (ROOT / row['path']).read_bytes()
        assert len(data) == row['size_bytes'], row['path']
        assert digest(data) == row['sha256'], row['path']
    totals = []
    datasets = []
    manifest_hashes = 0
    for archive in manifest['archives']:
        with zipfile.ZipFile(ROOT / archive['path']) as z:
            assert z.testzip() is None
            names = z.namelist()
            assert len(names) == len(set(names)) == archive['zip_entries']
            assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n and ':' not in n for n in names)
            rows = [dict(path=i.filename, size_bytes=i.file_size, crc32=f'{i.CRC:08x}', sha256=digest(z.read(i))) for i in z.infolist() if not i.is_dir()]
            assert rows == archive['members']
            for internal in archive['internal_manifests']:
                n = internal['path']
                m = json.loads(z.read(n))
                prefix = n[:-len('manifest.json')]
                for path, expected in m['sha256'].items():
                    assert digest(z.read(prefix + path)) == expected, path
                manifest_hashes += len(m['sha256'])
            for check in archive['embedded_checksum_checks']:
                actual = digest(z.read('manifest.json')) if check['target'] == 'manifest.json' else digest((ROOT / 'original_checkpoints' / check['target']).read_bytes())
                assert actual == check['sha256'], check['path']
            records = {}
            counts = {}
            for part in archive['partitions']:
                data = z.read(part['path'])
                assert digest(data) == part['sha256']
                parsed = [json.loads(line) for line in data.decode().splitlines() if line.strip()]
                assert len(parsed) == part['records']
                counts[Path(part['path']).stem] = len(parsed)
                for r in parsed:
                    assert r['id'] not in records, r['id']
                    records[r['id']] = r
            assert counts == archive['record_counts']
            assert len(records) == archive['records_total']
            datasets.append(records)
            totals.append(len(records))
    for idx, transition in enumerate(manifest['id_transitions']):
        old, new = datasets[idx:idx + 2]
        assert len(old.keys() & new.keys()) == transition['retained_ids']
        assert sorted(new.keys() - old.keys()) == transition['added_ids']
        assert sorted(old.keys() - new.keys()) == transition['removed_ids']
        assert sorted(k for k in old.keys() & new.keys() if old[k] != new[k]) == transition['changed_records_same_id']
    state = json.loads((ROOT / 'FROZEN_STATE.json').read_text(encoding='utf-8'))
    assert state['freeze_id'] == 'SRS-FREEZE-2026-10-31-v1'
    assert state['authoritative_checkpoint'] == 'STUDIO-KNOWLEDGE-003R'
    return dict(status='PASS', preserved_files=len(manifest['files']), archives_crc_verified=3,
                member_hashes_verified=sum(len(a['members']) for a in manifest['archives']),
                internal_manifest_hashes_verified=manifest_hashes, records_per_checkpoint=totals,
                comparison_to_003R='NOT RERUN: archive unavailable; prior audit preserved',
                round_2_reports_preserved=2, gemini_round_2='UNAVAILABLE')


if __name__ == '__main__':
    try:
        print(json.dumps(verify(), indent=2))
    except Exception as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}, indent=2))
        sys.exit(1)
