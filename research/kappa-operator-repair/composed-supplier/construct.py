#!/usr/bin/env python3
"""Compose the PR3945 terminal refit with the admitted receiver-sharing word.

PR3945/Dugongue supplies the actual changed terminal/owner construction;
dataisfire supplies staged544. The independent receiver identity is retained
from the adaptive continuation, transposing Nick Petalas's shared covector
mechanism. This file claims only its checked finite composition and price;
fresh native, owner and conditional integration are separate obligations.
Apache-2.0. Substantial OpenAI assistance.
"""
import argparse
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
REPO = SCOPE.parents[1]
OLD = REPO / 'research/kappa-adaptive-continuation/native-alternatives'
P3945 = SCOPE / 'sources/PR3945/research/staged544-terminal-gap-fill'
sys.path.insert(0, str(OLD))
import fanout_search as F
import construct as C


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=HERE / 'candidate')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(REPO / 'research/kappa-1745-continuation/complex-birth'))
    exact = load(REPO / 'research/kappa-1745-continuation/complex-birth/exact_rows.py', 'composition_exact_rows')
    expected_profile = {1:2482, 2:712, 3:218, 4:109, 5:20, 8:8}
    new_profile = {1:2481, 2:711, 3:219, 4:109, 5:20, 8:8}
    providers = {}
    for tag in ['base', 'extra']:
        source = P3945 / 'owner/inputs' / ('WORD-' + tag + '.json.gz')
        word = F.read(source)
        if word['B'][692:694] != C.OLD:
            raise ValueError('Receiver preimage differs from the exact admitted identity')
        if {int(r):n for r,n in word['report']['local_profile'].items()} != expected_profile:
            raise ValueError('Unexpected terminal-refit local profile')
        changed = deepcopy(word)
        changed['B'][692:694] = deepcopy(C.NEW)
        for warp in changed['warps']:
            if warp[0] >= 694:
                warp[0] += 1
        F.derive_cleanup(changed)
        changed['report']['local_profile'] = {str(r):n for r,n in new_profile.items()}
        before = F.trace(word, F.expand(word))
        after = F.trace(changed, F.expand(changed))
        if before[:2] != after[:2]:
            raise ValueError('Changed external frames')
        deltas = {}
        for r in before[5]:
            delta = after[5][r].copy()
            delta.subtract(before[5][r])
            delta = {k:n for k,n in delta.items() if n}
            if delta:
                deltas[r] = delta
        if deltas != {672:C.DELTA}:
            raise ValueError(('Unexpected path delta', deltas))
        old_rows, old_captures = exact.replay(word)
        new_rows, new_captures = exact.replay(changed)
        if new_rows != old_rows or new_rows != exact.expected(changed):
            raise ValueError('Complete signed arbitrary-input operator failure')
        if old_captures != new_captures:
            raise ValueError('SOURCE/dirty center capture changed')
        if word['initial_corrections'] != changed['initial_corrections']:
            raise ValueError('Unpriced initial correction')
        payload = json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()
        target = args.out / ('BORROW-WORD-43' + tag + '.json.gz')
        target.write_bytes(gzip.compress(payload, mtime=0))
        providers[tag] = {'source': str(source.relative_to(REPO)),
                          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                          'word': target.name, 'word_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                          'word_payload_sha256': hashlib.sha256(payload).hexdigest(),
                          'local_profile': new_profile, 'per_register_delta': deltas,
                          'helper_widths': changed['report']['width_inventory'],
                          'exact_free_warp_all_inputs': True, 'center_captures_unchanged': True,
                          'all_632_live_columns': True, 'all_91_zero_buffers_restored': True,
                          'new_initial_corrections': 0}
        print('PASS_COMPOSED_WORD', tag, new_profile, flush=True)
    profile = {1:8041680,2:2306880,3:729648,4:353160,5:69120,8:25920,48:137952}
    for rank, delta in C.DELTA.items():
        profile[rank] += 3240 * delta
    engine = load(REPO / 'research/native-complex-moment552/engines/moment.py', 'composition_moment')
    root = engine.certify(profile, 73, 322560)
    report = {'status': 'PASS_COMPOSED_FINITE_WORD_AND_PROVISIONAL_COMPLETE_PROFILE',
              'native_and_owner_admission_complete': False, 'providers': providers,
              'profile': profile, 'local_profile': new_profile,
              'replicas': 360, 'calls': 3240, 'productive_families': 322560,
              'root': root,
              'scope': 'Exact arbitrary-dirty finite composition; full owner recount, fresh native phase/word replay and inherited conditional resource/outer ledgers remain required.',
              'source_pins': {str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [Path(__file__), OLD/'construct.py', OLD/'fanout_search.py',
                                REPO/'research/kappa-1745-continuation/complex-birth/exact_rows.py',
                                REPO/'research/native-complex-moment552/engines/moment.py']}}
    (args.out / 'CONSTRUCTION.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('PROVISIONAL_COMPOSED_ROOT', [root['lower'], root['upper']], flush=True)


if __name__ == '__main__':
    main()
