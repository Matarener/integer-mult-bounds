#!/usr/bin/env python3
"""Replay the exact cut-state theorem's finite evidence. Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def source_module():
    from states import require
    root = HERE.parents[1]
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    inputs = [row for row in manifest['files'] if row['usage'] == 'input']
    expected = {'research/synthetic-twiddle-circuit/PROOF.md',
                'research/synthetic-twiddle-circuit/circuit.py',
                'upstream/build/sections/06-transforms.tex'}
    require(len(inputs) == 3 and {row['path'] for row in inputs} == expected,
            'source inventory differs')
    raw_code = None
    for row in inputs:
        path = root / row['path']
        require(path.is_file() and not path.is_symlink(), 'missing source input')
        require(path.stat().st_size <= 262144, 'source size limit')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source bytes differ')
        if row['path'].endswith('/circuit.py'):
            raw_code = raw
    require(raw_code is not None, 'missing layout oracle')
    module = types.ModuleType('cut_state_layout_source')
    sys.modules[module.__name__] = module
    exec(compile(raw_code, 'authenticated-circuit.py', 'exec'), module.__dict__)
    return module


def result():
    from checks import boundary_checks, examples, interval_checks, physical_checks, symbolic_checks
    source = source_module()
    rows = physical_checks(source)
    return {'schema_version': 1, 'status': 'PASS_TWIDDLE_CUT_STATES',
            'scope': 'Finite corroboration of the author-written all-size cut-state proof',
            'physical_cases': len(rows), 'physical_address_evaluations': sum(r['addresses'] for r in rows),
            'constant_sum_cases': interval_checks(), 'symbolic_closed_form_cases': symbolic_checks(),
            'boundary_rejections': boundary_checks(), 'examples': examples(), 'physical_rows': rows}


def receipt_text(actual):
    summary = {key: value for key, value in actual.items() if key != 'physical_rows'}
    rows = [json.dumps(row, separators=(',', ': ')) for row in actual['physical_rows']]
    return (json.dumps(summary, indent=2)[:-2] + ',\n  "physical_rows": [\n'
            + ',\n'.join('    ' + row for row in rows) + '\n  ]\n}\n')


def main():
    from states import require
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true', help='replace the local finite evidence receipt')
    args = parser.parse_args()
    actual = result()
    if args.record:
        (HERE / 'RESULT.json').write_text(receipt_text(actual))
    else:
        require(actual == json.loads((HERE / 'RESULT.json').read_bytes()), 'evidence receipt differs')
    small = {key: value for key, value in actual.items() if key != 'physical_rows'}
    print(json.dumps(small, indent=2))


if __name__ == '__main__':
    main()
