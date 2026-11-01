"""Ed25519 verification of external host attestations using operator-pinned keys.

Only public keys are loaded here. Signing and real host enforcement are external.
"""
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import jsonschema

from .canonical import canonical, digest, schema_errors
from .validate import contains, parse_time

TEXT = {'type': 'string', 'minLength': 1}
TEXTS = {'type': 'array', 'items': TEXT, 'minItems': 1, 'uniqueItems': True}
HEX = {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}
PURPOSES = ['authority', 'run', 'review', 'release']


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


TRUST_SCHEMA = obj({'trust_version': {'const': '0.1.0'},
    'max_age_seconds': {'type': 'integer', 'minimum': 1},
    'revoked_record_sha256': {'type': 'array', 'items': HEX, 'uniqueItems': True},
    'required_gate_ids': TEXTS,
    'keys': {'type': 'object', 'minProperties': 1, 'additionalProperties': obj({
        'public_key_hex': HEX, 'purposes': {'type': 'array', 'items': {'enum': PURPOSES}, 'minItems': 1, 'uniqueItems': True},
        'projects': TEXTS, 'subjects': TEXTS, 'scopes': TEXTS})}})
PAYLOAD_SCHEMA = obj({'receipt_version': {'const': '0.1.0'}, 'purpose': {'enum': PURPOSES},
    'issuer': TEXT, 'project_id': TEXT, 'record_sha256': HEX,
    'issued_at': {'type': 'string', 'format': 'date-time'},
    'expires_at': {'type': 'string', 'format': 'date-time'}})
RECEIPT_SCHEMA = obj({'payload': PAYLOAD_SCHEMA,
    'signature_hex': {'type': 'string', 'pattern': '^[a-f0-9]{128}$'}})
CHECKER = jsonschema.FormatChecker()
KINDS = {'authority': 'Authority', 'run': 'EvidenceRun', 'review': 'DesignDecision', 'release': 'ReleaseDecision'}


class Receipts:
    def __init__(self, trust, receipts, *, now=None):
        # Pin copies; don't let caller mutation alter trust halfway through a check.
        import json
        self.trust = json.loads(canonical(trust))
        self.receipts = json.loads(canonical(receipts))
        jsonschema.Draft202012Validator(TRUST_SCHEMA, format_checker=CHECKER).validate(self.trust)
        if not isinstance(self.receipts, list):
            raise ValueError('Receipts must be an array')
        validator = jsonschema.Draft202012Validator(RECEIPT_SCHEMA, format_checker=CHECKER)
        for receipt in self.receipts:
            validator.validate(receipt)
        self.now = now or datetime.now(timezone.utc)

    def verify(self, record, purpose):
        if schema_errors(record) or purpose not in KINDS or record['kind'] != KINDS[purpose]:
            return False
        sha = digest(record)
        if sha in self.trust['revoked_record_sha256']:
            return False
        body = record['body']
        subject = body['producer'] if purpose == 'run' else body['grantor'] if purpose == 'authority' else record['owner']
        if purpose == 'review' and body['status'] != 'ACCEPTED':
            return False
        for receipt in self.receipts:
            payload = receipt['payload']
            key = self.trust['keys'].get(payload['issuer'])
            if not key or payload['purpose'] != purpose or payload['record_sha256'] != sha or payload['project_id'] != record['project_id']:
                continue
            if purpose not in key['purposes'] or record['project_id'] not in key['projects'] or subject not in key['subjects'] or not any(contains(scope, record['scope']) for scope in key['scopes']):
                continue
            if purpose == 'authority' and not all(any(contains(scope, allowed) for scope in key['scopes']) for allowed in body['allowed_scope']):
                continue
            issued, expires = parse_time(payload['issued_at']), parse_time(payload['expires_at'])
            if issued > self.now or expires <= self.now or expires <= issued or (expires - issued).total_seconds() > self.trust['max_age_seconds']:
                continue
            try:
                public = Ed25519PublicKey.from_public_bytes(bytes.fromhex(key['public_key_hex']))
                public.verify(bytes.fromhex(receipt['signature_hex']), canonical(payload))
                return True
            except (InvalidSignature, ValueError):
                continue
        return False

    def callbacks(self, records):
        records = [r for r in records if not schema_errors(r)] if isinstance(records, list) else []
        index = {(r['id'], r['revision']): r for r in records}
        latest = {}
        for r in records:
            if r['revision'] > latest.get(r['id'], {}).get('revision', 0):
                latest[r['id']] = r
        def release(record):
            if not self.verify(record, 'release'):
                return False
            gates = []
            for ref in record['body']['required_gate_refs']:
                gate = index.get((ref['id'], ref['revision']))
                if not gate or gate['kind'] != 'GateDecision' or digest(gate) != ref['sha256'] or gate != latest[gate['id']]:
                    return False
                gates.append(gate)
            return set(self.trust['required_gate_ids']) <= {g['body']['gate_id'] for g in gates}
        return {'authority_receipt': lambda r: self.verify(r, 'authority'),
                'run_receipt': lambda r: self.verify(r, 'run'),
                'review_receipt': lambda r: self.verify(r, 'review'), 'release_receipt': release}
