#!/usr/bin/env python3
"""Rebuild the pinned literal invoice; compare complete typed evidence."""
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
    represented = json.loads(json.dumps(value, ensure_ascii=True, allow_nan=False))
    return json.dumps(represented, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def module(name):
    spec = importlib.util.spec_from_file_location('_bit_invoice_' + name, PACKAGE/(name+'.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def authenticate():
    count = 0
    for row in json.loads((PACKAGE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT/row['path']
        require(path.is_file() and not path.is_symlink(), 'regular pinned input')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'input SHA256')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw,
                             usedforsecurity=False).hexdigest() == row['git_blob'], 'input Git blob')
        count += 1
    require(count == 17, 'complete source inventory')
    return count


def run():
    inputs = authenticate()
    local = module('engine').run()
    require(digest(local) == digest(json.loads((PACKAGE/'EXPECTED-LOCAL.json').read_text())),
            'complete fresh typed local payload')
    parent = module('owners').run(local['helper_widths'], local['local_profile'])
    require(digest(parent) == digest(json.loads((PACKAGE/'EXPECTED-PARENT.json').read_text())),
            'complete fresh typed parent payload')
    oracle = module('oracle').check(local)
    require(digest(oracle) == digest(json.loads((PACKAGE/'EXPECTED-ORACLE.json').read_text())),
            'complete fresh typed independent rational oracle')
    # These controls protect complete evidence equality, beyond summary totals.
    bad = copy.deepcopy(local)
    bad['orientations']['forward']['paid_transition_records'][0]['derived_paid_rank'] += 1
    require(digest(bad) != digest(local), 'altered literal paid rank rejected')
    bad = copy.deepcopy(parent)
    bad['full_profile']['1' if '1' in bad['full_profile'] else 1] += 1
    require(digest(bad) != digest(parent), 'altered parent invoice rejected')
    bad = copy.deepcopy(parent)
    bad['all_call_owners_checked'] = 1
    require(digest(bad) != digest(parent), 'integer cannot replace Boolean evidence')
    return {'status': 'PASS_LITERAL_BIT_PROFILE_REBUILD', 'exact_inputs': inputs,
            'local_QUERYs': local['local_QUERYs'], 'local_rankmass': local['local_rankmass'],
            'frames_rebuilt': local['frames_rebuilt'],
            'records_per_orientation': local['orientations']['forward']['records_checked'],
            'local_profile': local['local_profile'], 'full_profile': parent['full_profile'],
            'calls': parent['calls'], 'helper_occurrences': parent['helper_occurrences'],
            'QUERYs': parent['QUERYs'], 'rankmass': parent['rankmass'],
            'W': parent['W'], 'private_families': parent['private_families'],
            'semantic_controls_rejected': len(local['negative_controls'])+len(parent['negative_controls']),
            'stored_payload_corruptions_rejected': 3,
            'local_payload_sha256': digest(local), 'parent_payload_sha256': digest(parent),
            'oracle_payload_sha256': digest(oracle),
            'scope': 'finite Q-frame/owner invoice only; no numeric ERASE/SOURCE/native/physical/outer or new kappa'}


if __name__ == '__main__':
    require(len(sys.argv) == 1, 'no arguments')
    print(json.dumps(run(), sort_keys=True, separators=(',', ':')))
