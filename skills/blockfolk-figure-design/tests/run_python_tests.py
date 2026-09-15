"""Standard-library suite with optional immutable machine-readable evidence."""
import argparse,hashlib,json,sys,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path)
args=parser.parse_args()
suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_*.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'passed':result.wasSuccessful(),'tests_run':result.testsRun,
        'failures':[(str(test),trace) for test,trace in result.failures],
        'errors':[(str(test),trace) for test,trace in result.errors],
        'source_hashes':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [*(root/'tests').glob('*.py'),*(root/'scripts/blockfolk').glob('*.py')]}}
if args.output:
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as output:
        json.dump(report,output,indent=2)
sys.exit(0 if result.wasSuccessful() else 1)
