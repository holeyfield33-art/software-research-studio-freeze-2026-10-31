"""Studio checkpoint 002: independently specified malformed-Unicode acceptance."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scanplan.core import IntakeError, build_plan, canonical, parse_input

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / 'examples/demo.json').read_text())


class UnicodeBoundaryTests(unittest.TestCase):
    def test_all_free_text_reject_surrogate_without_crashing(self):
        for field in ('subject', 'review_owner', 'component', 'observation'):
            with self.subTest(field=field):
                x = copy.deepcopy(BASE)
                target = (x if field == 'subject' else x['scope'] if field == 'review_owner'
                          else x['threats'][0])
                target[field] = 'input ' + chr(0xD800)
                raw = json.dumps(x, ensure_ascii=True).encode('ascii')
                with self.assertRaises(IntakeError):
                    canonical(build_plan(parse_input(raw)))

    def test_cli_invalid_unicode_returns_error_without_output(self):
        with tempfile.TemporaryDirectory() as root:
            x = copy.deepcopy(BASE)
            x['threats'][0]['observation'] = chr(0xDC00)
            inp = Path(root) / 'intake.json'
            output = Path(root) / 'result.json'
            inp.write_text(json.dumps(x, ensure_ascii=True))
            env = dict(os.environ, PYTHONPATH=str(ROOT))
            p = subprocess.run([sys.executable, '-m', 'scanplan', 'plan', str(inp), '--output', str(output)],
                               capture_output=True, text=True, env=env)
            self.assertEqual(p.returncode, 1, p.stderr)
            self.assertFalse(output.exists())
            self.assertIn('scanplan:', p.stderr)
            self.assertNotIn('Traceback', p.stderr)

    def test_valid_unicode_is_deterministic(self):
        x = copy.deepcopy(BASE)
        x['subject'] = 'Local café 🧪'
        x['threats'][0]['observation'] = 'Potential escape — needs review ✅'
        raw = json.dumps(x, ensure_ascii=True).encode()
        p = canonical(build_plan(parse_input(raw)))
        self.assertEqual(p, canonical(build_plan(parse_input(raw))))
        self.assertEqual(json.loads(p)['subject'], 'Local café 🧪')
        self.assertEqual(json.loads(p)['execution_authority'], 'UNVERIFIED')
        self.assertEqual(json.loads(p)['release_disposition'], 'HOLD')

    def test_invalid_utf8_is_already_rejected(self):
        with self.assertRaises(IntakeError):
            parse_input(b'{"subject":"\xff"}')


if __name__ == '__main__':
    unittest.main()
