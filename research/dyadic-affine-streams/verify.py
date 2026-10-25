"""Read-only replay of complete typed scientific receipts."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fused_sources


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', required=True, choices=('affine', 'routes', 'catalogue', 'controls'))
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    fused_sources.authenticate()
    check = fused_sources.load('affine_check_'+args.suite, 'research/dyadic-affine-streams/check_'+args.suite+'.py')
    result = check.run()
    digest = sha256(canonical(result).encode()).hexdigest()
    if args.emit:
        print(canonical(result))
    else:
        expected = json.loads((HERE/'RESULT.json').read_text())
        if digest != expected[args.suite]:
            raise ValueError('complete typed receipt differs: '+args.suite)
        if args.suite != 'controls':
            saved = json.loads((HERE/(args.suite.upper()+'.json')).read_text())
            if canonical(result) != canonical(saved):
                raise ValueError('saved full receipt differs: '+args.suite)
        print(canonical(dict(suite=args.suite, sha256=digest, cases=len(result))))
    print('PASS_DYADIC_AFFINE_'+args.suite.upper())


if __name__ == '__main__':
    main()
