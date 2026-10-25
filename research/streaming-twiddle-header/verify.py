#!/usr/bin/env python3
"""Replay streaming-header evidence. Nick Petalas. Apache-2.0."""

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
    from stream import require
    root = HERE.parents[1]
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    inputs = [r for r in manifest['files'] if r['usage'] == 'input']
    expected = {'research/synthetic-twiddle-circuit/PROOF.md',
                'research/synthetic-twiddle-circuit/circuit.py',
                'upstream/build/sections/06-transforms.tex'}
    require(len(inputs) == 3 and {r['path'] for r in inputs} == expected, 'source inventory differs')
    raw_code = None
    for row in inputs:
        path = root / row['path']
        require(all(not (root.joinpath(*path.relative_to(root).parts[:j])).is_symlink()
                    for j in range(1, len(path.relative_to(root).parts) + 1)),
                'source path contains a symlink')
        require(path.is_file() and not path.is_symlink(), 'missing source input')
        require(path.stat().st_size <= 262144, 'source size limit')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source bytes differ')
        if row['path'].endswith('/circuit.py'):
            raw_code = raw
    require(raw_code is not None, 'missing circuit oracle')
    module = types.ModuleType('streaming_twiddle_source')
    sys.modules[module.__name__] = module
    exec(compile(raw_code, 'authenticated-circuit.py', 'exec'), module.__dict__)
    return module


def result():
    from checks import boundaries, exhaustive, failure_cleanup, residuals, wide
    source = source_module()
    physical = exhaustive(source)
    prefix = residuals()
    wide_cases, examples = wide(source)
    return {'schema_version': 1, 'status': 'PASS_STREAMING_TWIDDLE_HEADER',
            'scope': 'Finite corroboration of the author-written all-size register proof',
            'physical_cases': len(physical),
            'physical_address_evaluations': sum(r['addresses'] for r in physical),
            'residual_cases': len(prefix),
            'residual_address_evaluations': sum(r['addresses'] for r in prefix),
            'wide_address_evaluations': wide_cases, 'boundary_rejections': boundaries(),
            'failure_cleanup_cases': failure_cleanup(),
            'examples': examples, 'physical_rows': physical, 'residual_rows': prefix}


def receipt_text(actual):
    tables = ('physical_rows', 'residual_rows')
    summary = {k: v for k, v in actual.items() if k not in tables}
    text = json.dumps(summary, indent=2)[:-2]
    for key in tables:
        rows = ',\n'.join('    ' + json.dumps(row, separators=(',', ': ')) for row in actual[key])
        text += ',\n  "' + key + '": [\n' + rows + '\n  ]'
    return text + '\n}\n'


def main():
    from stream import require
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true', help='replace finite evidence receipt')
    args = parser.parse_args()
    actual = result()
    if args.record:
        (HERE / 'RESULT.json').write_text(receipt_text(actual))
    else:
        require(actual == json.loads((HERE / 'RESULT.json').read_bytes()), 'evidence receipt differs')
    print(json.dumps({k: v for k, v in actual.items()
                      if k not in ('physical_rows', 'residual_rows', 'examples')}, indent=2))


if __name__ == '__main__':
    main()
