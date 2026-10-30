#!/usr/bin/env python3
"""Dense all-column check of four new paid MOVE pairs in the root595 edit.

Three are new signed native maps; 3->529 was already used as helper 731's
endpoint and is retained here as a positive control.

The inventory/lowering comparison follows Matarener's PR5960. It uses the
unchanged Clear1nsight exact Gaussian-dyadic dense interpreter and retained
Clifford/literal compilers, authenticated before import. New contribution:
source-bound delta selection and a reproducible four-map receipt. This is
finite native coverage, not the native_all_columns uniform assumption.
Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent


def need(ok, label):
    if not ok:
        raise ValueError(label)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def import_pinned(root):
    pins = read(HERE / 'NATIVE-SOURCES.json')['files']
    modules = []
    for i, pin in enumerate(pins):
        raw = (root / pin['path']).read_bytes()
        need(len(raw) == pin['size'] and sha256(raw).hexdigest() == pin['sha256']
             and sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'],
             'immutable native source: ' + pin['path'])
        name = f'root595_native_dependency_{i}'
        spec = importlib.util.spec_from_file_location(name, root / pin['path'])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        modules.append(module)
    return modules


def audit(base, candidate, root):
    need(base['frames'] == candidate['frames'], 'unchanged native frames')
    need(all(base[k] == candidate[k] for k in ('initial', 'final', 'live', 'ports')), 'unchanged helper maps and main adapters')
    old = {(e[2], e[3]) for e in base['program'] if e[0] == 'MOVE'}
    new = {(e[2], e[3]) for e in candidate['program'] if e[0] == 'MOVE'}
    tasks = sorted(new - old)
    need(tasks == [(3, 529), (520, 737), (529, 520), (737, 595)], 'complete new paid-MOVE-pair inventory')
    main_roles = set(base['live']) | {r + 112 for r in base['live']}
    old_helpers = {(base['initial'][r], base['final'][r])
                   for r in range(base['public']) if r not in main_roles}
    new_signed = set(tasks) - old_helpers
    need(new_signed == {(520, 737), (529, 520), (737, 595)}, 'three new signed native maps')
    compiler, literal, dense = import_pinned(root)
    frames = candidate['frames']
    receipts = []
    control_recipe = control_expected = None
    for a, b in tasks:
        operator = compiler.canonical_frame(9, tuple(frames[a])).adjoint().then(compiler.canonical_frame(9, tuple(frames[b])))
        recipe, _ = compiler.lower_child(operator)
        rank = abs(len(frames[a]) - len(frames[b]))
        need(recipe['rank'] == rank, 'lowering rank')
        actual = literal.recipe(recipe)
        expected = literal.adjoint(literal.frame(frames[a], 9)) + literal.frame(frames[b], 9)
        ac, ec = dense.compile_circuit(actual), dense.compile_circuit(expected)
        digest = sha256()
        for column in range(512):
            left = dense.dense_column(ac, column)
            right = dense.dense_column(ec, column)
            need(left == right, f'exact column for {a}->{b}, {column}')
            real, imag, exponent = left
            need(sum(v*v for v in real) + sum(v*v for v in imag) == 1 << (2*exponent), 'unit column norm')
            need(sum(bool(x or y) for x, y in zip(real, imag)) == 1 << rank, 'native child support rank')
            digest.update(json.dumps([column, exponent, real, imag], separators=(',', ':')).encode())
        receipts.append({'frames': [a, b], 'rank': rank, 'columns': 512,
                         'role': 'new_signed_map' if (a, b) in new_signed else 'existing_helper_map_positive_control',
                         'matrix_sha256': digest.hexdigest()})
        if control_recipe is None:
            control_recipe, control_expected = actual, expected
    fault = control_recipe + (('phase', 1),)
    need(literal.tableau(fault) == literal.tableau(control_recipe), 'phase-only mutation preserves signed tableau')
    need(dense.first_difference(fault, control_expected) is not None, 'phase-only mutation rejected by dense interpreter')
    flipped = list(control_recipe)
    i = next(i for i, gate in enumerate(flipped) if gate[0] == 'C')
    flipped[i] = ('C', flipped[i][1], -flipped[i][2])
    need(dense.first_difference(tuple(flipped), control_expected) is not None, 'child sign mutation rejected')
    return {'paid_move_delta_maps': receipts, 'new_signed_map_count': len(new_signed),
            'columns_checked': 512*len(tasks), 'complex_entries_compared': 512*512*len(tasks),
            'unchanged_helper_maps_and_main_adapters': True, 'controls': {'absolute_phase_only': 'rejected', 'child_sign': 'rejected'},
            'scope': 'Three new finite 9-qubit signed maps and one existing helper-map positive control; other unchanged maps reuse predecessor evidence; uniform native_all_columns remains assumed.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('base', nargs='?', default=str(HERE / 'inputs/pr6143-WORD.json.gz'))
    parser.add_argument('candidate', nargs='?', default=str(HERE / 'WORD.json.gz'))
    parser.add_argument('--source-root', type=Path, default=HERE.parents[1])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit(read(args.base), read(args.candidate), args.source_root)
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.output:
        args.output.write_text(raw)
    receipt = HERE / 'NATIVE-AUDIT.json'
    if args.write:
        receipt.write_text(raw)
    else:
        need(receipt.read_text() == raw, 'exact dense native receipt')
    print('PASS_ROOT595_NEW_NATIVE_MAPS', result['new_signed_map_count'], 'new signed maps;', result['columns_checked'], 'columns checked')


if __name__ == '__main__':
    main()
