"""Development helper: regenerate synthetic intake examples, not live plans."""
from pathlib import Path
import json

from .planning import INTAKE_SCHEMA, plan
from .test_planning import intake_fixture


def build():
    root = Path(__file__).with_name('planning_examples')
    root.mkdir(exist_ok=True)
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
              'title': 'Reviewed planning intake 0.1.0 — transport, not record schema', **INTAKE_SCHEMA}
    (root / 'intake.schema.json').write_text(json.dumps(schema, indent=2) + '\n', encoding='utf-8')
    for category in ['cli', 'library', 'api', 'web', 'pipeline']:
        intake = intake_fixture(category)
        (root / (category + '.intake.json')).write_text(json.dumps(intake, indent=2) + '\n', encoding='utf-8')
        output = plan(intake)
        assert output['plan_status'] == 'COMPLETE', output['blockers']
    blocked = intake_fixture('cli')
    del blocked['risk_dimensions']['reversibility']
    (root / 'unknown-risk.intake.json').write_text(json.dumps(blocked, indent=2) + '\n', encoding='utf-8')
    assert plan(blocked)['plan_status'] == 'INCOMPLETE'


if __name__ == '__main__':
    build()
