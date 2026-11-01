from pathlib import Path
import hashlib
import json

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / 'architecture/UNIVERSAL-ARCH-001/contracts.schema.json'
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
jsonschema.Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker())


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def reference(record):
    return {'id': record['id'], 'revision': record['revision'], 'sha256': digest(record)}


def load_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Non-finite JSON value: ' + value)
    return json.loads(data, object_pairs_hook=unique, parse_constant=invalid)


def schema_errors(record):
    try:
        canonical(record)
        return [error.message for error in VALIDATOR.iter_errors(record)]
    except (TypeError, ValueError, RecursionError) as exc:
        return [str(exc)]


def references(value):
    if isinstance(value, dict):
        if set(value) == {'id', 'revision', 'sha256'}:
            yield value
        else:
            for child in value.values():
                yield from references(child)
    elif isinstance(value, list):
        for child in value:
            yield from references(child)
