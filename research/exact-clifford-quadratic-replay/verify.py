"""Verify exact engine checks, preserved source obligations and full replay."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from pins import authenticate
import binding
import checks
import quadratic as Q
import run


def main():
    authenticate()
    bound = binding.run()
    Q.need(bound == json.loads((ROOT / 'BINDING.json').read_text()), 'Complete source integration binding')
    result = checks.run()
    Q.need(result == json.loads((ROOT / 'RESULT.json').read_text()), 'Complete new exact engine evidence')
    run.run('quadratic')
    print('PASS_EXACT_CLIFFORD_QUADRATIC_REPLAY')


if __name__ == '__main__':
    Q.need(not sys.argv[1:], 'No unknown arguments')
    main()
