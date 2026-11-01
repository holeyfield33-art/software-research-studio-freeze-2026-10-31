#!/usr/bin/env python3
"""Run the offline regression suite and save a machine-readable summary."""
from pathlib import Path
import io,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]; TESTS=ROOT/'tests'; OUT=ROOT/'reports/regression-tests.json'
sys.path.insert(0,str(ROOT/'scripts'))
suite=unittest.defaultTestLoader.discover(str(TESTS),pattern='test_*.py',top_level_dir=str(ROOT))
stream=io.StringIO(); result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'failures':[{'test':str(t),'traceback':tb} for t,tb in result.failures],'errors':[{'test':str(t),'traceback':tb} for t,tb in result.errors],'output':stream.getvalue()}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'tests_run':report['tests_run'],'failures':len(report['failures']),'errors':len(report['errors']),'summary':str(OUT)},indent=2))
sys.exit(0 if result.wasSuccessful() else 1)
