#!/usr/bin/env python3
"""Whole-word cross-check of published RETIMED and DELAYED supplier words.

Reuses Sagar Thakrar's exact PR3687 audit_core, unchanged and authenticated
before execution. This is not a new interpreter. No construction/native checker
is imported. roger-sato with substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
STAGED = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
RETIMED = {1: 2437, 2: 724, 3: 226, 4: 102, 5: 20, 8: 8}
WIDTHS = {4: 26, 5: 2, 6: 18, 7: 52, 8: 97, 9: 213}
MOVES = ((591, 1045, 640, 644, 2, [423, 65, 20, 10]),
         (641, 1085, 656, 660, -1, [427, 96, 24, 6]))
SOURCE_COMMITS = {
    3605: '3efbb5de06a49ffeea6684482f2d3fe48cdca3fb',
    3642: '044d24f12e74f228dd462c07ae2d7f3ea35e2be9',
    3653: '607a09ff441c79b215a8127a81f4cc70021d0d9b',
    3682: '431e6c6023ef352c41696469de7fb614cd4ded8c',
    3687: 'f798838eb8ede4178e94f240e7b7e54b3f80c82d',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_text())['snapshots']
    expected = {(3687, 'vendor/audit_core.py')}
    for provider in ('base', 'extra'):
        expected.update((number, f'inputs/{kind}-{provider}.json.gz') for number, kind in
                        ((3605, 'STAGED'), (3642, 'RETIMED'), (3653, 'RETIMED'), (3682, 'DELAYED')))
    keys = [(row['source_pr'], row['local']) for row in rows]
    need(len(keys) == len(expected) and set(keys) == expected, 'source mapping inventory differs')
    for row in rows:
        need(row['source_commit'] == SOURCE_COMMITS[row['source_pr']], 'source commit differs')
        raw = (HERE / row['local']).read_bytes()
        need(len(raw) == row['bytes'], 'source byte length: ' + row['local'])
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['local'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == row['git_blob'], 'source Git blob: ' + row['local'])
    core = types.ModuleType('retained_audit_core')
    path = HERE / 'vendor/audit_core.py'
    # Execute the authenticated source bytes, without accepting a .pyc cache.
    exec(compile(path.read_bytes(), str(path), 'exec'), core.__dict__)
    return core


def load(kind, provider):
    return json.loads(gzip.decompress((HERE / 'inputs' / f'{kind}-{provider}.json.gz').read_bytes()))


def events(w):
    result = []
    for pos in range(len(w['B']) + 1):
        result += [('warp', k, deepcopy(rec)) for k, rec in enumerate(w['warps']) if rec[0] == pos]
        if pos < len(w['B']):
            result.append(('gate', pos, deepcopy(w['B'][pos])))
    return result


def replace_events(w, seq):
    result = deepcopy(w)
    body, warps = [], [None] * len(w['warps'])
    for kind, label, gate in seq:
        gate = deepcopy(gate)
        if kind == 'gate':
            body.append(gate)
        else:
            gate[0] = len(body)
            warps[label] = gate
    need(all(rec is not None for rec in warps), 'lost warp in reconstruction')
    result['B'], result['warps'] = body, warps
    return result


def reconstruct(C, staged, kind):
    """Literal prose recipes: adjacent shear swap, or move before first producer.

    This repeats the credited local structural arguments as an input control;
    the new evidence is the full word calculation below.
    """
    seq = events(staged)
    for start, stop, donor, pivot, coefficient, frame in MOVES:
        source = next(x for x in seq if x[:2] == ('gate', start))
        need(source[2] == ['add', donor, pivot, coefficient, 1, [429, 30]], 'source release')
        if kind == 'RETIMED':
            target = next(x for x in seq if x[:2] == ('gate', start + 1))
            need(target[2][0] == 'add' and target[2][2] == pivot, 'adjacent same-pivot shear')
            need(not any(rec[0] == start + 1 for rec in staged['warps']), 'unexpected crossed warp')
            where = seq.index(target) + 1
        else:
            target = next(x for x in seq if x[:2] == ('gate', stop))
            writes = [i for i, g in enumerate(staged['B']) if i > start and g[1] == pivot]
            need(writes[0] == stop, 'first producer cut')
            where = seq.index(target)
        changed = deepcopy(source[2])
        changed[-1] = frame
        seq.insert(where, ('gate', -pivot, changed))
        seq.remove(source)
    result = replace_events(staged, seq)
    result['cleanup'] = C.derive_cleanup(result)
    result['report']['local_profile'] = {str(k): v for k, v in RETIMED.items()}
    return result


def semantics(C, w):
    """All live and buffer inputs are symbols, with no zero-buffer assumption."""
    def endpoint(name, result):
        bad_live, dirty_buffers, leaks, buffer_identity = result
        need(not bad_live and not dirty_buffers and not leaks and buffer_identity,
             name + ' endpoint: ' + repr(result))
    boundary = {}
    rows = C.forward_rows(w, symbolic_buffers=True,
                          snapshot=lambda values: boundary.setdefault('defects', C.boundary_defects(w, values)))
    endpoint('forward', C.endpoint_defects(w, rows))
    dual_rows = C.forward_rows(w, dual=True, symbolic_buffers=True)
    endpoint('dual', C.endpoint_defects(w, dual_rows, dual=True))
    need(not boundary['defects'], 'cleanup boundary: ' + repr(boundary['defects']))
    pulled = C.transpose(C.reverse_columns(w))
    need(pulled == {r: row for r, row in rows.items() if row}, 'reverse pull-back differs from forward')
    pre = C.transpose(C.reverse_columns(w, upto_cleanup=True))
    pre = {r: pre.get(r, {}) for r in set(pre) | set(range(C.N))}
    need(not C.boundary_defects(w, pre), 'reverse cleanup-boundary contract')
    live = C.N - len(w['removed'])
    buffers = len(w['helper_final'])
    need((live, buffers, len(rows)) == (632, 91, 723), 'complete symbolic domain')
    # Endpoint expectations are derived by the retained checker: live x,y,h
    # map to x,y+x,h; all private buffer symbols return unchanged.
    return {'live_inputs': live, 'dirty_buffers': buffers, 'matrix_dimension': len(rows),
            'forward': 'PASS', 'dual': 'PASS', 'reverse_pullback_equals_forward': True,
            'cleanup_boundary_forward_and_reverse': 'PASS',
            'buffer_to_live_leaks': 0, 'buffer_self_map': 'identity',
            'nonzero_endpoint_terms': sum(len(row) for row in rows.values())}


def inspect(C, w, profile):
    C.hygiene(w)
    bill, widths, chain, _, _ = C.frame_bill(w)
    need(bill == profile, 'computed profile differs')
    need(w['report']['local_profile'] == {str(k): v for k, v in bill.items()}, 'declared profile differs')
    need(widths == WIDTHS, 'helper widths differ')
    need(w['cleanup'] == C.derive_cleanup(w), 'literal cleanup differs')
    return {'semantics': semantics(C, w), 'profile': bill, 'widths': widths,
            'rank_mass': sum(r * n for r, n in bill.items())}, chain


def expect_rejection(C, fn, phrase):
    try:
        fn()
    except (ValueError, C.AuditFailure) as exc:
        need(phrase in str(exc), 'wrong rejection: ' + str(exc))
        return phrase
    raise ValueError('mutant unexpectedly passed: ' + phrase)


def negative_controls(C, staged, w, kind):
    controls = []
    for _, _, donor, pivot, _, _ in MOVES:
        seq = events(w)
        release = next(x for x in seq if x[0] == 'gate' and x[2][0] == 'add' and x[2][1:3] == [donor, pivot])
        for defect in ('omit', 'flip', 'cross_first_producer'):
            changed = deepcopy(seq)
            index = seq.index(release)
            if defect == 'omit':
                changed.pop(index)
            elif defect == 'flip':
                changed[index][2][3] *= -1
            else:
                producer = next(x for x in changed[index + 1:] if x[0] == 'gate' and x[2][1] == pivot)
                moved = changed.pop(index)
                changed.insert(changed.index(producer) + 1, moved)
            bad = replace_events(w, changed)
            bad['cleanup'] = C.derive_cleanup(bad)
            # Repair the literal inverse so stale cleanup is not the rejection.
            reason = expect_rejection(C, lambda: semantics(C, bad), 'forward endpoint')
            controls.append({'defect': defect, 'pivot': pivot, 'rejected_by': reason})
    old_cleanup = deepcopy(w)
    old_cleanup['cleanup'] = staged['cleanup']
    # The inverse shears commute: this is a format failure, not a wrong operator.
    semantic_control = semantics(C, old_cleanup)
    need(old_cleanup['cleanup'] != C.derive_cleanup(old_cleanup), 'old cleanup unexpectedly literal')
    controls.append({'defect': 'old_cleanup_order', 'semantics': semantic_control,
                     'rejected_by': expect_rejection(C, lambda: inspect(C, old_cleanup, RETIMED), 'literal cleanup differs')})
    old_frames = deepcopy(w)
    for gate in old_frames['B']:
        if gate[0] == 'add' and gate[1:3] in ([640, 644], [656, 660]):
            gate[-1] = [429, 30]
    need(semantics(C, old_frames) == semantic_control, 'frame-only mutation changed operator')
    if kind == 'RETIMED':
        need(C.frame_bill(old_frames)[0] == STAGED, 'old frame control does not restore staged bill')
        controls.append({'defect': 'old_release_frames', 'semantic_operator': 'PASS',
                         'profile': STAGED, 'rejected_by': expect_rejection(C, lambda: inspect(C, old_frames, RETIMED), 'computed profile differs')})
    else:
        # The later release encounters a donor that has already climbed, so
        # the original rank-2 frame is now illegal, despite the same operator.
        controls.append({'defect': 'old_release_frames', 'semantic_operator': 'PASS',
                         'rejected_by': expect_rejection(C, lambda: inspect(C, old_frames, RETIMED), 'frame containment fails')})
    fake_report = deepcopy(w)
    fake_report['report']['local_profile']['1'] += 1
    controls.append({'defect': 'wrong_declared_profile', 'rejected_by':
                     expect_rejection(C, lambda: inspect(C, fake_report, RETIMED), 'declared profile differs')})
    return controls


def run(C):
    results = {}
    for provider in ('base', 'extra'):
        staged = load('STAGED', provider)
        control, old_chain = inspect(C, staged, STAGED)
        records = {'STAGED': control}
        for kind in ('RETIMED', 'DELAYED'):
            w = load(kind, provider)
            need(reconstruct(C, staged, kind) == w, 'prose reconstruction differs: ' + kind)
            record, chain = inspect(C, w, RETIMED)
            deltas = {}
            for register in set(chain) | set(old_chain):
                before = Counter(d for _, d, _ in old_chain.get(register, []) if type(d) is int and d > 0)
                after = Counter(d for _, d, _ in chain.get(register, []) if type(d) is int and d > 0)
                delta = {r: after[r] - before[r] for r in set(after) | set(before) if after[r] != before[r]}
                if delta:
                    deltas[register] = delta
            need(deltas == {640: {1: -1, 2: -1, 3: 1}, 656: {1: -1, 2: -1, 3: 1}}, 'per-register invoice differs')
            record['prose_reconstruction'] = 'exact complete JSON equality'
            record['changed_register_bills'] = deltas
            record['controls'] = negative_controls(C, staged, w, kind)
            records[kind] = record
            print('CHECKED', provider, kind, '723-register forward/dual/pull-back and 9 controls', flush=True)
        results[provider] = records
    return {'status': 'PASS_RETIMED_AND_DELAYED_WHOLE_WORD_AUDIT',
            'scope': 'Reused PR3687 interpreter; finite exact operator/frame audit only. No native Gaussian, owner, root, or complete supplier claim.',
            'providers': results}


if __name__ == '__main__':
    need(sys.argv[1:] in ([], ['--write']), 'usage: verify.py [--write]')
    C = authenticate()
    result = run(C)
    output = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(output)
    else:
        need((HERE / 'RESULT.json').read_text() == output, 'committed result differs')
    print(result['status'])
