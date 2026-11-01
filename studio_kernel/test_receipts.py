import copy
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
import json
import subprocess
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .acceptance import accept_task
from .canonical import canonical, digest, reference
from .receipts import Receipts
from .test_kernel import fixtures, CANDIDATE
from .validate import validate
from .evidence import verify_import, retain_bundle, saved_receipts
from .store import Store

NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'output.txt').write_bytes(b'expected\n')
        self.records = fixtures()
        self.private = Ed25519PrivateKey.generate()
        self.trust = {'trust_version': '0.1.0', 'max_age_seconds': 3600, 'revoked_record_sha256': [],
            'required_gate_ids': ['gate.unit_integration_execution'], 'keys': {'synthetic-host': {
                'public_key_hex': self.private.public_key().public_bytes_raw().hex(),
                'purposes': ['authority', 'run', 'review', 'release'], 'projects': ['example'],
                'subjects': ['operator', 'synthetic-host', 'owner', 'independent-reviewer'],
                'scopes': ['component/cli']}}}
        self.receipts = []
        for row in self.records:
            purpose = {'Authority': 'authority', 'EvidenceRun': 'run', 'DesignDecision': 'review', 'ReleaseDecision': 'release'}.get(row['kind'])
            if purpose:
                self.receipts.append(self.sign(row, purpose))

    def sign(self, row, purpose, **overrides):
        payload = {'receipt_version': '0.1.0', 'purpose': purpose, 'issuer': 'synthetic-host',
                   'project_id': row['project_id'], 'record_sha256': digest(row),
                   'issued_at': '2026-11-01T00:00:00Z', 'expires_at': '2026-11-01T00:30:00Z', **overrides}
        return {'payload': payload, 'signature_hex': self.private.sign(canonical(payload)).hex()}

    def verifier(self):
        return Receipts(self.trust, self.receipts, now=NOW)

    def row(self, kind, suffix=None):
        return next(r for r in self.records if r['kind'] == kind and (suffix is None or r['id'].endswith(suffix)))

    def validate(self):
        verifier = self.verifier()
        return validate(self.records, project_id='example', candidate=CANDIDATE,
                        artifact_root=self.root, now=NOW, **verifier.callbacks(self.records))

    def acceptance(self):
        return accept_task(self.records, reference(self.row('TaskPacket')), project_id='example', candidate=CANDIDATE,
            gate_id='gate.unit_integration_execution', policy_ref=reference(self.records[0]),
            review_ref=reference(self.row('DesignDecision', 'task-review')),
            created_at='2026-11-01T00:00:00Z', receipt_verifier=self.verifier(), artifact_root=self.root)

    def test_valid_signatures_support_verification(self):
        report = self.validate()
        self.assertEqual(report['status'], 'PASS', report)
        self.assertEqual(report['release_disposition'], 'APPROVE')

    def test_changed_record_rejects_old_receipt(self):
        row = copy.deepcopy(self.row('EvidenceRun'))
        row['body']['producer'] = 'other'
        self.assertFalse(self.verifier().verify(row, 'run'))

    def test_forged_signature(self):
        target = digest(self.row('Authority'))
        next(r for r in self.receipts if r['payload']['record_sha256'] == target)['signature_hex'] = '0' * 128
        self.assertFalse(self.verifier().verify(self.row('Authority'), 'authority'))

    def test_wrong_public_key(self):
        self.trust['keys']['synthetic-host']['public_key_hex'] = Ed25519PrivateKey.generate().public_key().public_bytes_raw().hex()
        self.assertEqual(self.validate()['status'], 'INCOMPLETE')

    def test_untrusted_issuer(self):
        self.receipts = [self.sign(self.row('EvidenceRun'), 'run', issuer='unknown')]
        self.assertFalse(self.verifier().verify(self.row('EvidenceRun'), 'run'))

    def test_wrong_project(self):
        self.trust['keys']['synthetic-host']['projects'] = ['other']
        self.assertFalse(self.verifier().verify(self.row('EvidenceRun'), 'run'))

    def test_wrong_purpose(self):
        self.trust['keys']['synthetic-host']['purposes'] = ['release']
        self.assertFalse(self.verifier().verify(self.row('EvidenceRun'), 'run'))

    def test_wrong_subject_and_scope(self):
        self.trust['keys']['synthetic-host']['subjects'] = ['unrelated']
        self.assertFalse(self.verifier().verify(self.row('EvidenceRun'), 'run'))
        self.trust['keys']['synthetic-host']['subjects'] = ['synthetic-host']
        self.trust['keys']['synthetic-host']['scopes'] = ['component/other']
        self.assertFalse(self.verifier().verify(self.row('EvidenceRun'), 'run'))

    def test_expired_future_and_oversized_lifetime(self):
        for overrides in [dict(expires_at='2026-11-01T00:00:00Z'), dict(issued_at='2026-11-01T01:00:00Z', expires_at='2026-11-01T01:30:00Z'), dict(expires_at='2026-11-02T00:00:00Z')]:
            with self.subTest(overrides=overrides):
                run = self.row('EvidenceRun')
                self.receipts = [self.sign(run, 'run', **overrides)]
                self.assertFalse(self.verifier().verify(run, 'run'))

    def test_revoked_record(self):
        self.trust['revoked_record_sha256'] = [digest(self.row('EvidenceRun'))]
        self.assertFalse(self.verifier().verify(self.row('EvidenceRun'), 'run'))

    def test_missing_operator_required_gate_holds_release(self):
        self.trust['required_gate_ids'].append('gate.operational_rollback')
        self.assertEqual(self.validate()['release_disposition'], 'HOLD')

    def test_unsigned_review_cannot_pass_gate(self):
        self.receipts = [r for r in self.receipts if r['payload']['purpose'] != 'review']
        report = self.validate()
        self.assertEqual(report['release_disposition'], 'HOLD')
        self.assertIn('GATE_REVIEW_RECEIPT', {f['code'] for f in report['findings']})

    def test_accept_task_proposes_canonical_passing_gate(self):
        output = self.acceptance()
        self.assertEqual(output['status'], 'PASS', output)
        self.assertEqual(output['gate']['body']['status'], 'PASS')
        self.assertEqual(output['gate']['derived_from'], [reference(self.row('TaskPacket'))])

    def test_corrupt_artifact_cannot_pass_acceptance(self):
        (self.root / 'output.txt').write_bytes(b'wrong')
        output = self.acceptance()
        self.assertEqual(output['status'], 'FAIL', output)
        self.assertIsNone(output['gate'])

    def test_no_run_receipt_means_no_acceptance(self):
        self.receipts = [r for r in self.receipts if r['payload']['purpose'] != 'run']
        self.assertEqual(self.acceptance()['status'], 'INCOMPLETE')

    def test_unbound_review_not_accepted(self):
        review = self.row('DesignDecision', 'task-review')
        review['derived_from'] = []
        # Drop old gate/release referring to the original review hash for this proposal.
        self.records = [r for r in self.records if r['kind'] not in ('GateDecision', 'ReleaseDecision')]
        self.receipts.append(self.sign(review, 'review'))
        self.assertEqual(self.acceptance()['status'], 'INCOMPLETE')

    def test_verified_failure_can_be_imported_without_becoming_pass(self):
        run = self.row('EvidenceRun')
        run['body']['status'] = 'FAIL'
        self.receipts.append(self.sign(run, 'run'))
        existing = [r for r in self.records if r['kind'] not in ('EvidenceRun', 'GateDecision', 'ReleaseDecision') and not r['id'].endswith('task-review')]
        report = verify_import(existing, [run], project_id='example', candidate=CANDIDATE,
                               verifier=self.verifier(), artifact_root=self.root)
        self.assertEqual(report['status'], 'PASS', report)
        review = self.row('DesignDecision', 'task-review')
        review['derived_from'] = [reference(self.row('TaskPacket')), reference(run)]
        self.receipts.append(self.sign(review, 'review'))
        self.records = existing + [run, review]
        accepted = self.acceptance()
        self.assertEqual(accepted['status'], 'FAIL', accepted)
        self.assertEqual(accepted['gate']['body']['status'], 'FAIL')

    def test_unsigned_run_cannot_be_imported(self):
        run = self.row('EvidenceRun')
        existing = [r for r in self.records if r['kind'] not in ('EvidenceRun', 'GateDecision', 'ReleaseDecision') and not r['id'].endswith('task-review')]
        self.receipts = []
        output = verify_import(existing, [run], project_id='example', candidate=CANDIDATE,
                               verifier=self.verifier(), artifact_root=self.root)
        self.assertEqual(output['status'], 'INCOMPLETE')

    def test_retained_proof_survives_history_reopen_and_detects_corruption(self):
        path = self.root / 'history.sqlite'
        store = Store(path, 'example')
        sha = retain_bundle(path, self.receipts)
        store.commit(self.records, expected_revision=0, candidate=CANDIDATE, actor='operator',
                     reason='receipt_bundle_sha256=' + sha + '; synthetic proof retention test')
        recovered = saved_receipts(path, Store(path, 'example').read()['events'])
        self.assertEqual({digest(r) for r in recovered}, {digest(r) for r in self.receipts})
        proof = Path(str(path) + '.receipts') / (sha + '.json')
        proof.write_text('[]', encoding='utf-8')
        with self.assertRaises(ValueError):
            saved_receipts(path, store.read()['events'])

    def test_malformed_acceptance_reference_is_reported(self):
        output = accept_task(self.records, {'id': [], 'revision': {}, 'sha256': 'x'},
            project_id='example', candidate=CANDIDATE, gate_id='gate.unit_integration_execution',
            policy_ref=reference(self.records[0]), review_ref=reference(self.row('DesignDecision', 'task-review')),
            created_at='2026-11-01T00:00:00Z', receipt_verifier=self.verifier(), artifact_root=self.root)
        self.assertEqual(output['status'], 'FAIL')

    def test_cli_signed_import_and_acceptance(self):
        # CLI uses wall clock; create short-lived test receipts for the actual run.
        from datetime import timedelta
        clock = datetime.now(timezone.utc)
        issued = (clock - timedelta(seconds=5)).isoformat()
        expires = (clock + timedelta(minutes=10)).isoformat()
        proofs = []
        for row in self.records:
            purpose = {'Authority': 'authority', 'EvidenceRun': 'run', 'DesignDecision': 'review'}.get(row['kind'])
            if purpose:
                proofs.append(self.sign(row, purpose, issued_at=issued, expires_at=expires))
        path = self.root / 'cli.sqlite'
        seed = [r for r in self.records if r['kind'] not in ('EvidenceRun', 'GateDecision', 'ReleaseDecision') and not r['id'].endswith('task-review')]
        Store(path, 'example').commit(seed, expected_revision=0, candidate=CANDIDATE, actor='operator', reason='Synthetic initial task')
        def write(name, value):
            target = self.root / name
            target.write_bytes(canonical(value))
            return str(target)
        trust = write('trust.json', self.trust)
        receipts = write('receipts.json', proofs)
        candidate = write('candidate.json', CANDIDATE)
        run_file = write('runs.json', [self.row('EvidenceRun')])
        command = [sys.executable, '-m', 'studio_kernel', 'import-evidence', run_file, '--project', 'example', '--store', str(path), '--expected', '1', '--candidate', candidate, '--actor', 'operator', '--trust-config', trust, '--receipts', receipts, '--artifacts', str(self.root)]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['status'], 'RECORDED')
        self.assertEqual(Store(path, 'example').read()['revision'], 2)
        Store(path, 'example').commit([self.row('DesignDecision', 'task-review')], expected_revision=2,
            candidate=CANDIDATE, actor='independent-reviewer', reason='Record the signed exact-run review')

        command = [sys.executable, '-m', 'studio_kernel', 'accept', '--project', 'example', '--store', str(path), '--candidate', candidate,
            '--task-ref', write('task-ref.json', reference(self.row('TaskPacket'))), '--policy-ref', write('policy-ref.json', reference(self.records[0])),
            '--review-ref', write('review-ref.json', reference(self.row('DesignDecision', 'task-review'))), '--gate-id', 'gate.unit_integration_execution',
            '--created-at', clock.isoformat(), '--trust-config', trust, '--artifacts', str(self.root)]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report['gate']['body']['status'], 'PASS')
        # Acceptance is a proposal; it does not mutate history or authorize release.
        self.assertEqual(Store(path, 'example').read()['revision'], 3)

    def test_pre_execution_review_cannot_approve_later_outputs(self):
        review = self.row('DesignDecision', 'task-review')
        review['derived_from'] = [reference(self.row('TaskPacket'))]
        self.records = [r for r in self.records if r['kind'] not in ('GateDecision', 'ReleaseDecision')]
        self.receipts.append(self.sign(review, 'review'))
        output = self.acceptance()
        self.assertEqual(output['status'], 'INCOMPLETE')
        self.assertEqual(output['findings'][0]['code'], 'ACCEPTANCE_RUN_REVIEW')

    def test_latest_release_decision_supersedes_historical_hold(self):
        release = self.row('ReleaseDecision')
        newer = copy.deepcopy(release)
        newer['revision'] = 2
        release['body']['decision'] = 'HOLD'
        self.records.append(newer)
        self.receipts.append(self.sign(newer, 'release'))
        report = self.validate()
        self.assertEqual(report['release_disposition'], 'APPROVE', report)

if __name__ == '__main__':
    unittest.main()
