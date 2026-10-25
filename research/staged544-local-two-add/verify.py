#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only exact replay; --emit explicitly regenerates an external receipt."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import types

P = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def module(name, path):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value

def authenticate(raw, row):
    require(len(raw) == row['bytes'], 'source length: ' + row['local'])
    require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['local'])
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == row['git_blob'], 'source Git blob: ' + row['local'])

def setup():
    sources = json.loads((P / 'SOURCES.json').read_text())
    for row in sources['snapshots']:
        authenticate((P / row['local']).read_bytes(), row)
    return (module('owned_search', P / 'search.py'),
            module('retained_auditor', P / 'vendor/audit_core.py'),
            module('retained_semantics', P / 'vendor/audit_verify.py'))

def load(tag):
    return json.loads(gzip.decompress((P / 'inputs' / f'BORROW-WORD-43{tag}.json.gz').read_bytes()))

def calculate(tag, progress=False):
    S, C, A = setup()
    word = load(tag)
    C.hygiene(word)
    bill, inventory, *_ = C.frame_bill(word)
    require(bill == {int(r): n for r, n in word['report']['local_profile'].items()}, 'source declared invoice')
    require(S.R.tracing(word)[2] == bill, 'source trace disagreement')
    require(C.derive_cleanup(word) == word['cleanup'], 'source inverse cleanup')
    baseline = S.R.census(word)
    expected = json.loads((P / 'inputs/SINGLE-CENSUS.json').read_text())[tag]
    require(json.loads(json.dumps(baseline)) == expected, 'predecessor single-move census differs')
    require(all(row['certificate'] for row in baseline['deltas']), 'single-move premise failed')
    result = S.compute(word, C, progress)
    return {'schema_version': 1, 'provider': tag, 'source_canonical': S.digest(word),
            'source_profile': bill, 'width_inventory': inventory,
            'single_move_candidates': baseline['candidates'],
            'single_census_digest': S.digest(baseline),
            'source_semantics': A.semantics(C, word), 'pair_census': result}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=('base', 'extra'), required=True)
    parser.add_argument('--emit', type=Path)
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    result = calculate(args.provider, args.progress)
    if args.emit:
        require(not args.emit.resolve().is_relative_to(P), 'write regenerated receipt outside the package')
        args.emit.write_text(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n')
    else:
        expected = json.loads((P / f'RESULT-{args.provider}.json').read_text())
        require(json.loads(json.dumps(result)) == expected, 'complete pair receipt differs')
    print(json.dumps({'status': 'PASS_STAGED544_LOCAL_TWO_ADD', 'provider': args.provider,
                      'first_counts': result['pair_census']['first_counts'],
                      'result_sha256': hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                      'new_supplier': False}, sort_keys=True))

if __name__ == '__main__':
    main()
