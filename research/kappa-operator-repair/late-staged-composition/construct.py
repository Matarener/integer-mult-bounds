#!/usr/bin/env python3
"""Compose PR4076's three staged entries with the retained receiver identity.

PR4076/Rohan Arun supplies the staged entries, exact frames and owner fill;
PR3945/Dugongue supplies the terminal refits. The receiver identity is the
adaptive continuation's transpose of Nick Petalas's shared-covector rewrite.
The retained exact interpreters are credited to PR3687/3693. Apache-2.0.
Substantial OpenAI assistance. This finite candidate is not native admission.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
REPO = SCOPE.parents[1]
P4076 = SCOPE / 'sources/PR4076/research/staged544-triple-entry-fill'
P3945 = SCOPE / 'sources/PR3945/research/staged544-terminal-gap-fill'
OLD = [['add', 672, 544, 1, 2, [414, 51]],
       ['add', 676, 544, -1, 2, [414, 51]]]
NEW = [['add', 672, 676, 1, 1, [51]], OLD[1],
       ['add', 672, 676, -1, 1, [413, 72, 48, 3]]]
OLD_PROFILE = {1:2488, 2:714, 3:223, 4:102, 5:20, 8:8}
PROFILE = {1:2487, 2:713, 3:224, 4:102, 5:20, 8:8}
WIDTHS = {5:28, 6:18, 7:56, 8:93, 9:213}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE / 'candidate')
    args = ap.parse_args()
    need(__debug__, 'assertions enabled')
    args.out.mkdir(parents=True, exist_ok=False)
    source = read(SCOPE / 'sources/PR4076/SOURCE.json')
    need(source['head'] == '9744f9df268590295a9872b1952c695a678192b9', 'exact PR4076 head')
    for row in source['files']:
        p = SCOPE / 'sources/PR4076' / row['path']
        need(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'retrieved source authentication')
    sys.path.insert(0, str(P4076 / 'vendor'))
    C = module(P4076 / 'vendor/audit_core.py', 'late_exact_core')
    V = module(P4076 / 'vendor/audit_verify.py', 'late_exact_semantics')
    A = module(P4076 / 'recipe/staged_entries_applier.py', 'late_staged_applier')
    L = module(P4076 / 'checks/independent_frames.py', 'late_independent_frames')
    pins = [Path(__file__), SCOPE / 'sources/PR4076/SOURCE.json',
            P4076 / 'vendor/audit_core.py', P4076 / 'vendor/audit_verify.py',
            P4076 / 'vendor/staged_pair.py', P4076 / 'recipe/staged_entries_applier.py',
            P4076 / 'checks/independent_frames.py', P4076 / 'INPUTS.json',
            REPO / 'research/kappa-adaptive-continuation/native-alternatives/construct.py']
    providers = {}
    for tag in ('base', 'extra'):
        parent_path = P4076 / 'inputs' / ('OLD-' + tag + '.json.gz')
        source_path = P4076 / 'inputs' / ('NEW-' + tag + '.json.gz')
        record_path = P4076 / 'recipe' / ('RECORD-' + tag + '.json')
        pr3945_path = P3945 / 'owner/inputs' / ('WORD-' + tag + '.json.gz')
        parent, source_word = read(parent_path), read(source_path)
        need(parent == read(pr3945_path), 'staged predecessor is the exact PR3945 word')
        need(A.apply(parent, read(record_path)) == source_word, 'literal staged recipe reconstructs source')
        need(source_word['B'][683:685] == OLD, 'exact receiver preimage')
        need({int(r):n for r,n in source_word['report']['local_profile'].items()} == OLD_PROFILE,
             'exact source local profile')
        changed = deepcopy(source_word)
        changed['B'][683:685] = deepcopy(NEW)
        for warp in changed['warps']:
            if warp[0] >= 685:
                warp[0] += 1
        changed['cleanup'] = C.derive_cleanup(changed)
        changed['report']['local_profile'] = {str(r):n for r,n in PROFILE.items()}
        for word in (source_word, changed):
            C.hygiene(word)
            bill, widths, _, _, _ = C.frame_bill(word, lagrangian=True)
            need(bill == {int(r):n for r,n in word['report']['local_profile'].items()}, 'exact Lagrangian bill')
            need(widths == WIDTHS, 'actual helper width inventory')
            independent_bill, independent_widths = L.ledger(word)
            need(dict(independent_bill) == bill and dict(independent_widths) == widths,
                 'independent GF2 frame ledger agrees')
        before = C.frame_bill(source_word)[2]
        after = C.frame_bill(changed)[2]
        deltas = {}
        for r in set(before) | set(after):
            old_bill = Counter(d for _, d, _ in before.get(r, []) if type(d) is int and d > 0)
            new_bill = Counter(d for _, d, _ in after.get(r, []) if type(d) is int and d > 0)
            delta = {k:new_bill[k]-old_bill[k] for k in set(old_bill)|set(new_bill) if new_bill[k]!=old_bill[k]}
            if delta:
                deltas[r] = delta
        need(deltas == {672:{1:-1, 2:-1, 3:1}}, 'only the exact receiver tariff changes')
        kept = [k for k in source_word if k not in ('B','warps','cleanup','report')]
        need(all(source_word[k] == changed[k] for k in kept), 'all other caller fields unchanged')
        need([w[1:] for w in source_word['warps']] == [w[1:] for w in changed['warps']],
             'native warp identities, lenders, maps and frames unchanged')
        print('CHECK_COMPLETE_DIRTY_OPERATOR', tag, flush=True)
        semantics = V.semantics(C, changed)
        controls = []
        for label, index in [('flip_opening_receiver', 683), ('flip_closing_receiver', 685)]:
            mutant = deepcopy(changed)
            mutant['B'][index][3] *= -1
            mutant['cleanup'] = C.derive_cleanup(mutant)
            try:
                rows = C.forward_rows(mutant, symbolic_buffers=True)
                bad, dirty, leaks, identity = C.endpoint_defects(mutant, rows)
                need(not bad and not dirty and not leaks and identity, 'exact endpoint rejection')
            except (ValueError, C.AuditFailure):
                controls.append(label)
            else:
                raise ValueError('accepted mutation ' + label)
        payload = json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()
        target = args.out / ('BORROW-WORD-43' + tag + '.json.gz')
        target.write_bytes(gzip.compress(payload, mtime=0))
        providers[tag] = {'word':target.name, 'word_sha256':sha(target),
            'canonical_sha256':hashlib.sha256(payload).hexdigest(),
            'source_word_sha256':sha(source_path), 'source_record_sha256':sha(record_path),
            'receiver_preimage':[683,685], 'new_receiver_events':NEW,
            'per_register_delta':deltas, 'local_profile':PROFILE, 'width_inventory':WIDTHS,
            'semantics':semantics, 'controls_rejected':controls,
            'unchanged_fields':kept, 'all_632_live_and_91_dirty_buffer_inputs':True,
            'center_captures_unchanged_from_PR4076':True,
            'center_capture_reason':'A, precondition, compensation, cut and every pre-capture field are identical; the receiver edit occurs inside B.',
            'fresh_native_admission':False}
        pins += [parent_path, source_path, record_path, pr3945_path, target]
        print('PASS_LATE_COMPOSED_WORD', tag, PROFILE, flush=True)
    result = {'status':'PASS_FINITE_STAGED_RECEIVER_COMPOSITION_NATIVE_PENDING',
        'source_pr':4076, 'source_head':source['head'], 'providers':providers,
        'local_profile':PROFILE, 'width_inventory':WIDTHS,
        'native_completed':False, 'full_release_completed':False, 'new_admitted_kappa':False,
        'scope':'Literal source reconstruction, independent complete 632+91 signed semantics and frame bills. New native provider execution, actual owner invoice and full conditional release remain separate.',
        'input_files':{p.resolve().relative_to(REPO).as_posix():sha(p) for p in sorted(set(pins))}}
    (args.out / 'CONSTRUCTION.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
