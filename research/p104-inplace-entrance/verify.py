#!/usr/bin/env python3
"""Replay the source-bound P104 in-place entrance contract and budget screen.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
Normal replay authenticates and consumes committed artifacts without writing.
"""

import argparse
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/p104-rounded-collector/inputs/WORD.json'
OLD_NATIVE = 'research/p104-rounded-collector/inputs/NATIVE.json.gz'
COMPLETION = 'research/p104-omitted-completion/CERTIFICATE.json'
ADAPTERS = 'research/p104-omitted-frame-adapters/ADAPTERS.json'
COMPILER = ('research/gmx-t74-borrow43-handoff/new/fastnative/vendor/native/new/code/'
            'borrow/vendor/clifford/clifford_exact.py')
KERNEL = 'research/p104-omitted-frame-adapters/inputs/PR3416_verify.py'
OWN = ('primary.py', 'native.py', 'physical.py', 'invoice.py', 'controls.py',
       'verify.py', 'README.md', 'PROOF.md', 'COSTS.md', 'TASK.json', 'VERIFY.json')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key ' + key)
            result[key] = value
        return result

    def invalid(token):
        raise ValueError('noninteger JSON token ' + token)
    return json.loads(raw, object_pairs_hook=pairs, parse_float=invalid, parse_constant=invalid)


def same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def read(path):
    need(not any(p.is_symlink() for p in (path, *path.parents)), 'symbolic link in source ' + str(path))
    need(path.is_file(), 'missing regular source ' + str(path))
    with path.open('rb') as stream:
        raw = stream.read(32*1024*1024+1)
    need(len(raw) <= 32*1024*1024, 'source size limit')
    return raw


def module(raw, path, name):
    value = ModuleType(name)
    value.__file__ = str(path)
    sys.modules[name] = value
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def capture():
    manifest_bytes = read(HERE/'SOURCES.json')
    manifest = strict_json(manifest_bytes)
    need(type(manifest.get('schema_version')) is int and manifest['schema_version'] == 1,
         'source schema')
    raw = {}
    for pin in manifest['files']:
        if pin['usage'] != 'input':
            continue
        path = pin['path']
        need(type(path) is str and not path.startswith('/')
             and all(part not in ('', '.', '..') for part in path.split('/')), 'input path')
        need(path not in raw, 'duplicate scientific input')
        raw[path] = read(ROOT/path)
        need(sha(raw[path]) == pin['sha256'], 'source hash mismatch ' + path)
    need({WORD, OLD_NATIVE, COMPLETION, ADAPTERS, COMPILER, KERNEL} <= set(raw),
         'required scientific inputs missing')
    own = {name: read(HERE/name) for name in OWN}
    return manifest_bytes, raw, own


def artifact(name, expected, regenerate):
    path = HERE/name
    if regenerate:
        need(not path.is_symlink(), 'linked artifact destination')
        path.write_text(json.dumps(expected, indent=2, sort_keys=True)+'\n', encoding='utf8')
    raw = read(path)
    actual = strict_json(raw)
    need(same(actual, expected), 'typed serialized artifact mismatch ' + name)
    return actual, raw


def calculate(regenerate=False):
    manifest, raw, own = capture()
    engines = {name: module(own[name+'.py'], HERE/(name+'.py'), 'p104_inplace_'+name)
               for name in ('primary', 'native', 'physical', 'invoice', 'controls')}
    compiler = module(raw[COMPILER], ROOT/COMPILER, 'p104_inplace_retained_compiler')
    kernel = module(raw[KERNEL], ROOT/KERNEL, 'p104_inplace_retained_kernel')
    word, completion, adapters = (strict_json(raw[name]) for name in (WORD, COMPLETION, ADAPTERS))
    expanded = gzip.decompress(raw[OLD_NATIVE])
    need(len(expanded) <= 8*1024*1024, 'native expansion limit')
    old_native = strict_json(expanded)
    primary, native = engines['primary'], engines['native']
    generated = {'schema_version': 1, 'program': primary.program_for(word, completion, adapters),
                 'retained_original_event_indices': primary.projection(word)}
    program, program_bytes = artifact('PROGRAM.json', generated, regenerate)
    x_maps, full_map, native_receipt = native.synthesize(word, compiler.__dict__, kernel.__dict__)
    need(set(x_maps) == set(completion['factor']['C']), 'new native output keys differ from source factor')
    records, native_bytes = artifact('NATIVE.json', {'schema_version': 1, 'x_to_empty': x_maps,
                                      'empty_to_full': full_map}, regenerate)
    old_full = next(r for r in adapters['recipes'] if r['old'] == [])
    current_full = native_receipt['certificates']['empty_to_full']
    for key in ('signed_pauli_sha256', 'exact_anchor_sha256'):
        need(current_full[key] == old_full['certificate'][key], 'retained common exit certificate')
    altered = deepcopy(records['empty_to_full'])
    altered['recipe']['left']['phase'] = (altered['recipe']['left']['phase']+1) % 4
    try:
        native.certify_record(altered, kernel.__dict__)
    except ValueError as error:
        need(str(error) == 'exact global phase mismatch', 'wrong native phase control reason')
    else:
        raise ValueError('wrong global phase was admitted')
    matrix = primary.analyze(word, old_native, completion, adapters, program['program'])
    invoice = engines['invoice'].analyze(word, old_native, completion, adapters,
                                         program['retained_original_event_indices'])
    dirty = engines['controls'].scalar_controls(program['program'], completion['factor']['C'],
                                                 completion['factor']['A'])
    physical = engines['physical'].verify_physical(word, completion, records['x_to_empty'],
                   records['empty_to_full'], program=program['program'])
    need(physical['actual_fields'] == physical['expected_fields'], 'full independent physical arrays')
    need(physical['actual_frames'] == physical['expected_frames'], 'full independent physical frames')
    p = physical['receipt']
    need(p['program_sha256'] == matrix['new_program_sha256'], 'independent executed schedule digest')
    need(p['native_counts']['native_rank_mass'] == invoice['entrance_completion']['native_rank_mass']
         == native_receipt['proposed_native_rank_mass'], 'three independent native invoices')
    need(p['native_counts']['completed_floor_pairs'] == native_receipt['proposed_native_pair_count'],
         'literal complete-pair inventory')
    need(not same({'count': True}, {'count': 1}), 'Boolean/integer receipt distinction')
    for path, before in raw.items():
        need(read(ROOT/path) == before, 'source changed during replay '+path)
    for path, before in own.items():
        need(read(HERE/path) == before, 'implementation changed during replay '+path)
    need(read(HERE/'SOURCES.json') == manifest, 'source manifest changed during replay')
    need(read(HERE/'PROGRAM.json') == program_bytes and read(HERE/'NATIVE.json') == native_bytes,
         'serialized artifact changed during replay')
    result = {'schema_version': 1, 'status': 'PASS_P104_INPLACE_ENTRANCE',
              'SOURCES_sha256': sha(manifest), 'input_sha256': {p: sha(b) for p, b in raw.items()},
              'implementation_and_proof_sha256': {p: sha(b) for p, b in own.items()},
              'artifact_sha256': {'PROGRAM.json': sha(program_bytes), 'NATIVE.json': sha(native_bytes)},
              'primary': matrix, 'native': native_receipt, 'physical': p,
              'invoice': invoice, 'dirty_controls': dirty,
              'global_phase_control': 'Altered scalar i rejected by exact global-phase anchor.',
              'typed_receipt_control': 'Boolean true is distinct from integer1.',
              'scope': 'An actual local in-place entrance completion, a source-bound all358 endpoint/module implication, one independent dense literal prefix, and a conditional rejected consumer budget. No global owner, full physical bill, all-size supplier, or new selected saving.'}
    return strict_json(canonical(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-artifacts', action='store_true',
                        help='Explicitly regenerate only this package PROGRAM, NATIVE, and RECEIPT artifacts.')
    args = parser.parse_args()
    result = calculate(args.write_artifacts)
    path = HERE/'RECEIPT.json'
    if args.write_artifacts:
        need(not path.is_symlink(), 'linked receipt destination')
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf8')
    else:
        need(same(result, strict_json(read(path))), 'typed deterministic receipt mismatch')
    print('PASS_P104_INPLACE_ENTRANCE receipt='+sha(read(path)))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as error:
        print('FAIL_P104_INPLACE_ENTRANCE: '+str(error), file=sys.stderr)
        raise SystemExit(1) from error
