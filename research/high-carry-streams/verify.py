"""Read-only registered replay of complete typed receipts."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--suite',required=True,choices=('kernel','routes','catalogue','controls'))
    parser.add_argument('--emit',action='store_true')
    args=parser.parse_args()
    import bindings
    bindings.authenticate()
    # The predecessor loader places its packages first in sys.path. Load our
    # checker by explicit path to keep similarly named frozen checkers distinct.
    spec=importlib.util.spec_from_file_location('carry_check_'+args.suite,HERE/('check_'+args.suite+'.py'))
    check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
    result=check.run()
    digest=sha256(canonical(result).encode()).hexdigest()
    if args.emit:print(canonical(result))
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        if digest!=expected[args.suite]:raise ValueError('complete typed receipt differs: '+args.suite)
        if args.suite!='controls':
            saved=json.loads((HERE/(args.suite.upper()+'.json')).read_text())
            if canonical(result)!=canonical(saved):raise ValueError('saved full receipt differs: '+args.suite)
        print(canonical(dict(suite=args.suite,sha256=digest,cases=len(result))))
    print('PASS_HIGH_CARRY_'+args.suite.upper())


if __name__=='__main__':main()
