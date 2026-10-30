"""Read-only exact receipt comparison; finite tests are not a full theorem."""
import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--suite',required=True,choices=('boundary','routes','handoff','controls'))
    parser.add_argument('--emit',action='store_true')
    args=parser.parse_args()
    module=importlib.import_module({'boundary':'boundary_checks','routes':'route_checks',
                                   'handoff':'handoff_checks','controls':'controls'}[args.suite])
    result=module.run()
    if args.emit:print(canonical(result))
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())[args.suite]
        if canonical(result)!=canonical(expected):raise ValueError('complete typed receipt differs')
        print(canonical(dict(suite=args.suite,sha256=sha256(canonical(result).encode()).hexdigest())))
    print('PASS_RECURSIVE_OUTPUT_'+args.suite.upper())


if __name__=='__main__':main()
