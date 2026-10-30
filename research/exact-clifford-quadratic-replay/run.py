"""Run the complete pinned source proof with one explicit state engine."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from pins import authenticate, load


def run(engine):
    authenticate()
    if engine == 'literal':
        verifier = load('source_verifier', ROOT / 'source/verify.py')
        result = verifier.run()
    else:
        import verify_source
        if engine == 'quadratic':
            result = verify_source.run()
        elif engine == 'tables':
            table = load('credited_table_engine', ROOT / 'tables/fast_state.py')
            def equal(left, right):
                return (left.n == right.n and left.tab == right.tab and
                        table.zero_state(left) == table.zero_state(right))
            result = verify_source.run(equal)
        else:
            raise ValueError('Unknown state engine')
    expected = json.loads((ROOT / 'source/RESULT.json').read_text())
    if result != expected:
        raise ValueError('The complete source result changed')
    payload = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
    print('PASS_COMPLETE_SOURCE_RESULT', sha256(payload).hexdigest(), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=['literal', 'tables', 'quadratic'], default='quadratic')
    run(parser.parse_args().engine)
