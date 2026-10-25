#!/usr/bin/env python3
"""Fresh source-bound replay, separate dense arithmetic, full typed equality."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # JSON object keys are strings, including the engine's integer child keys.
    # Normalize that representation before sorting; retain every value's type.
    represented = json.loads(json.dumps(value, ensure_ascii=True, allow_nan=False))
    return json.dumps(represented, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def equal(actual, expected):
    # JSON distinguishes bool, int and list/object structure in this encoding.
    return canonical(actual) == canonical(expected)


def module(name):
    spec = importlib.util.spec_from_file_location('_mixed_cut_' + name, PACKAGE/(name+'.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def authenticate():
    inventory = json.loads((PACKAGE/'SOURCES.json').read_text())
    count = 0
    for row in inventory['files']:
        if row['usage'] != 'input':
            continue  # Provenance is checked by historical transport, not replay.
        path = ROOT/row['path']
        require(path.is_file() and not path.is_symlink(), 'regular source file')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw,
                             usedforsecurity=False).hexdigest() == row['git_blob'],
                'source Git blob')
        count += row['usage'] == 'input'
    require(count == 19, 'complete declared input inventory')
    return count


def run():
    inputs = authenticate()
    primary = module('engine').run()
    expected_primary = json.loads((PACKAGE/'EXPECTED-ENGINE.json').read_text())
    require(equal(primary, expected_primary), 'complete fresh primary typed payload')
    dense = module('oracle').check(primary)
    expected_dense = json.loads((PACKAGE/'EXPECTED-ORACLE.json').read_text())
    require(equal(dense, expected_dense), 'complete fresh dense typed payload')
    # Meaningful stored-evidence corruptions must not be accepted as the replay.
    bad = copy.deepcopy(expected_primary)
    bad['fixtures'][0]['checks'][0]['actual_columns'][0][0][0] += 1
    require(not equal(primary, bad), 'altered dirty-input matrix entry rejected')
    bad = copy.deepcopy(expected_primary)
    bad['fixtures'][0]['removed_axes'].pop()
    require(not equal(primary, bad), 'missing removed axis rejected')
    bad = copy.deepcopy(expected_primary)
    bad['fixtures'][0]['checks'][0]['matches_input_correction'] = 1
    require(not equal(primary, bad), 'integer cannot replace Boolean acceptance')
    return {'status': 'PASS_SOURCE_BOUND_HALF_CUT_EIGHT_STREAMS',
            'primary_outcome': primary['outcome'], 'exact_inputs': inputs,
            'head_counts': primary['head_counts'],
            'full_rank48_blocks': primary['full_rank48_block_count'],
            'head_fixtures': len(primary['fixtures']),
            'head_characters': primary['checked_head_characters'],
            'dirty_columns_per_character': 8,
            'negative_character': primary['negative_control']['witness_character'],
            'dense_complete_matrices': dense['full_8x8_comparisons'],
            'dense_entries': dense['matrix_entries_compared'],
            'dense_active_phase_cases': dense['active_phase_cases'],
            'stored_payload_corruptions_rejected': 3,
            'primary_payload_sha256': hashlib.sha256(canonical(primary)).hexdigest(),
            'dense_payload_sha256': hashlib.sha256(canonical(dense)).hexdigest(),
            'source_projection': 'shared extraction; separately reviewed, not a second reconstruction',
            'scope': 'identity cover, completed-invocation quotient; no native/outer/kappa admission'}


if __name__ == '__main__':
    require(len(sys.argv) == 1, 'no verifier arguments')
    print(json.dumps(run(), sort_keys=True, separators=(',', ':')))
