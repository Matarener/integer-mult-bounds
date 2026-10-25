"""Read-only exact receipt replay, also under isolated optimized Python."""
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
    p=argparse.ArgumentParser()
    p.add_argument('--suite',choices=('primary','independent','controls'),required=True)
    p.add_argument('--emit',action='store_true')
    args=p.parse_args()
    import source
    source.inputs()
    result=importlib.import_module('check' if args.suite=='primary' else args.suite).run()
    if args.emit:print(canonical(result))
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())[args.suite]
        if canonical(result)!=canonical(expected):raise ValueError('complete typed receipt differs')
        print(canonical(dict(suite=args.suite,sha256=sha256(canonical(result).encode()).hexdigest())))
    print('PASS_UNEQUAL_CYCLE_'+args.suite.upper())


if __name__=='__main__':main()
