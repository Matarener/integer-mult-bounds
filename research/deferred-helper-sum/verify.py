#!/usr/bin/env python3
"""Exact deferred pair-chart test on two pinned dirty-helper words.

Ross Richardson with substantial OpenAI GPT-6.1 Sol assistance. Apache-2.0.
The authenticated PR4076 accountant/interpreters retain their original credit.
This script constructs new words; the separate independent checker imports none
of this script or the source accountant.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import json
import types

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source4096/source4076'
PAIR = (608, 609)
E = [76, 45]
F = [144, 75, 42, 7]
U = [266, 138, 75, 42, 26, 7]
V = [272, 144, 72, 41, 4, 3]
EXPORT_SHA256 = '323edf5ff6415abbb60253f64c548c24d63cee499519787a6ffa334acd74861b'


def need(ok, label):
    if not ok:
        raise ValueError(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def authenticated_core():
    raw = (ROOT / 'SOURCE-EXPORT.json').read_bytes()
    need(sha(raw) == EXPORT_SHA256, 'source export manifest pin')
    manifest = json.loads(raw)
    for item in manifest['files']:
        need(sha((ROOT / item['path']).read_bytes()) == item['sha256'],
             'source bytes: ' + item['path'])
    module = types.ModuleType('authenticated_PR4076_accountant')
    module.__file__ = str(SOURCE / 'vendor/audit_core.py')
    data = (SOURCE / 'vendor/audit_core.py').read_bytes()
    # Execute the actual hashed source, without a bytecode/import-cache path.
    exec(compile(data, module.__file__, 'exec'), module.__dict__)
    return module


def add(dst, src, q, frame):
    q = Q(q)
    return ['add', dst, src, q.numerator, q.denominator, list(frame)]


def common_block():
    """Thirteen F-frame gates; the sum remains encoded at this boundary."""
    return [add(d, s, q, F) for d, s, q in [
        (610, 608, -1), (608, 410, -2), (609, 410, -1),
        (610, 410, 1), (609, 417, -1), (612, 417, -1),
        (608, 419, 1), (610, 419, -1), (612, 419, -1),
        (608, 421, -1), (609, 421, -1),
        (610, 421, 1), (612, 421, -1)]]


def check_preimage(w):
    expected = [add(d, s, q, F) for d, s, q in [
        (610, 608, -1), (608, 410, -1), (610, 609, -1),
        (609, 410, -1), (610, 410, 1), (608, 417, 1),
        (609, 417, -1), (612, 417, -1), (608, 419, 1),
        (610, 419, -1), (612, 419, -1), (609, 421, -1),
        (610, 421, 1), (612, 421, -1)]]
    need(w['B'][948:962] == expected, 'literal fourteen-gate source block')
    need(w['B'][962] == add(608, 278, 1, U), 'first divergent source gate')
    need(w['B'][963] == add(609, 276, 1, V), 'second divergent source gate')
    need(not any(948 < r[0] < 962 for r in w['warps']), 'interior native site')
    need(not any(r[1] in PAIR for r in w['warps']), 'pair native site')
    need(all(str(h) not in w['helper_final'] for h in PAIR), 'pair cleanup boundary')


def delayed(w, core):
    check_preimage(w)
    z = deepcopy(w)
    replacement = [add(608, 609, 1, E)] + common_block() + [add(608, 609, -1, F)]
    z['B'][948:962] = replacement
    for r in z['warps']:
        if r[0] >= 962:
            r[0] += 1
    z['cleanup'] = core.derive_cleanup(z)
    return z


def conjugate(g):
    """S g S^-1 for S=I+e608 e609^T, expanded into commuting ADDs."""
    if g[0] == 'scale':
        need(g[1] not in PAIR, 'pair scale outside declared source alphabet')
        return [deepcopy(g)]
    need(g[0] == 'add', 'suffix scalar alphabet')
    d, s, q, frame = g[1], g[2], Q(g[3], g[4]), g[-1]
    dc = {d: Q(1)}
    sc = {s: Q(1)}
    if d == 609:
        dc[608] = Q(1)
    if s == 608:
        sc[609] = Q(-1)
    need(not (set(dc) & set(sc)), 'noncommuting intra-pair conjugation')
    return [add(t, u, q * a * b, frame)
            for t, a in sorted(dc.items()) for u, b in sorted(sc.items())]


def persistent(w, core):
    """Exact algebraic consumer with undo deferred to literal cleanup.

    This is deliberately returned even though the immutable frame labels reject
    it. Operator equality is checked separately from frame legality.
    """
    check_preimage(w)
    z = deepcopy(w)
    result = list(z['B'][:948]) + [add(608, 609, 1, E)] + common_block()
    locations = {i: i for i in range(949)}
    for i in range(962, len(w['B']) + 1):
        locations[i] = len(result)
        if i < len(w['B']):
            result.extend(conjugate(w['B'][i]))
    for r in z['warps']:
        need(r[0] in locations, 'warp in replaced neighborhood')
        r[0] = locations[r[0]]
    z['B'] = result
    z['restore'] = [v for g in w['restore'] for v in conjugate(g)]
    z['cleanup'] = core.derive_cleanup(z)
    return z, locations


def matrix(gates, regs):
    state = {r: {r: Q(1)} for r in regs}
    for g in gates:
        need(g[0] == 'add', 'local scalar alphabet')
        q = Q(g[3], g[4])
        for j, x in list(state[g[2]].items()):
            value = state[g[1]].get(j, Q(0)) + q * x
            if value:
                state[g[1]][j] = value
            else:
                state[g[1]].pop(j, None)
    return state


def span(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in tuple(out)}
    return out


def positive_chains(chain):
    return {r: [(d, mask) for _, d, mask in values if d == 'warp' or d > 0]
            for r, values in chain.items()}


def endpoint_ok(w, rows, dual=False):
    regs = sorted((set(range(704)) - set(w['removed'])) |
                  {704 + int(h) for h in w['helper_final']})
    need(len(regs) == 723 and len(w['helper_final']) == 91, '723 dirty input domain')
    need(set(rows) == set(regs), 'complete row domain')
    for r in regs:
        expected = {(r, ()): Q(1)}
        if not dual and 112 <= r < 224:
            expected[r - 112, ()] = Q(1)
        if dual and r < 112:
            expected[r + 112, ()] = Q(-1)
        need(rows[r] == expected, 'complete arbitrary-dirty endpoint row ' + str(r))


def rejected(label, fn):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('control unexpectedly accepted: ' + label)


def check_provider(w, core):
    check_preimage(w)
    need(core.same_cleanup(w['cleanup'], core.derive_cleanup(w)), 'original literal cleanup')
    bill = core.frame_bill(w, lagrangian=True)
    need(bill[0] == {int(k): v for k, v in w['report']['local_profile'].items()}, 'original invoice')
    original = core.forward_rows(w, symbolic_buffers=True)
    endpoint_ok(w, original)
    endpoint_ok(w, core.forward_rows(w, dual=True, symbolic_buffers=True), True)
    need(core.transpose(core.reverse_columns(w)) == original, 'original reverse pullback')
    z = delayed(w, core)
    core.hygiene(w)
    core.hygiene(z)
    changed = core.forward_rows(z, symbolic_buffers=True)
    need(changed == original, 'delayed complete operator')
    endpoint_ok(z, changed)
    endpoint_ok(z, core.forward_rows(z, dual=True, symbolic_buffers=True), True)
    need(core.transpose(core.reverse_columns(z)) == changed, 'delayed reverse pullback')
    snapshots = []
    core.forward_rows(w, symbolic_buffers=True, snapshot=lambda s: snapshots.append(deepcopy(s)))
    core.forward_rows(z, symbolic_buffers=True, snapshot=lambda s: snapshots.append(deepcopy(s)))
    need(snapshots[0] == snapshots[1], 'all-input cleanup-boundary equality')
    new_bill = core.frame_bill(z, lagrangian=True)
    need(bill[:2] == new_bill[:2] and bill[3:] == new_bill[3:], 'delayed complete local invoice')
    need(positive_chains(bill[2]) == positive_chains(new_bill[2]), 'ordered paid frame chains')
    q, locations = persistent(w, core)
    endpoint_ok(q, core.forward_rows(q, symbolic_buffers=True))
    endpoint_ok(q, core.forward_rows(q, dual=True, symbolic_buffers=True), True)
    need(core.transpose(core.reverse_columns(q)) == original, 'persistent complete reverse pullback')
    # The first crossed six-frame gate is fixed, rather than an arbitrary
    # later failure from an incomplete replay.
    i = locations[963]
    need(q['B'][i] == add(608, 276, 1, V), 'actual persistent crossing gate')
    frame_failure = None
    try:
        core.frame_bill(q, lagrangian=True)
    except core.AuditFailure as err:
        frame_failure = str(err)
    need(frame_failure is not None and 'frame containment fails' in frame_failure,
         'persistent chart must fail frames')
    controls = []
    bad = deepcopy(z)
    bad['B'][950] = add(608, 410, -1, F)
    bad['cleanup'] = core.derive_cleanup(bad)
    controls.append(rejected('wrong doubled source coefficient with regenerated cleanup',
                             lambda: endpoint_ok(bad, core.forward_rows(bad))))
    bad = deepcopy(z)
    bad['B'][962][3] = 1
    bad['cleanup'] = core.derive_cleanup(bad)
    controls.append(rejected('wrong delayed unmix sign with regenerated cleanup',
                             lambda: endpoint_ok(bad, core.forward_rows(bad))))
    bad = deepcopy(z)
    bad['cleanup'] = deepcopy(w['cleanup'])
    controls.append(rejected('stale literal cleanup',
                             lambda: need(core.same_cleanup(bad['cleanup'], core.derive_cleanup(bad)), 'stale cleanup')))
    bad = deepcopy(q)
    del bad['B'][i]
    for rec in bad['warps']:
        if rec[0] > i:
            rec[0] -= 1
    bad['cleanup'] = core.derive_cleanup(bad)
    controls.append(rejected('omitted actual conjugated source pullback',
                             lambda: endpoint_ok(bad, core.forward_rows(bad))))
    controls.append(rejected('dirty private inputs incorrectly declared clean',
                             lambda: endpoint_ok(z, core.forward_rows(z, symbolic_buffers=False))))
    return {
        'source_word_sha256': sha(canonical(w)),
        'delayed_word_sha256': sha(canonical(z)),
        'persistent_word_sha256': sha(canonical(q)),
        'complete_input_dimension': 723, 'independent_private_buffers': 91,
        'source_profile': bill[0], 'delayed_profile': new_bill[0],
        'width_inventory': bill[1], 'paid_chains_equal': True,
        'forward_add_delta': len(z['B']) - len(w['B']),
        'cleanup_add_delta': len(z['cleanup']) - len(w['cleanup']),
        'cleanup_lengths': [len(w['cleanup']), len(z['cleanup'])],
        'complete_operator_forward_dual_reverse': 'PASS',
        'cleanup_boundary_all_inputs': 'PASS',
        'persistent_operator_forward_dual_reverse': 'PASS',
        'persistent_frame_failure': frame_failure,
        'persistent_crossed_B_index': i,
        'controls_rejected': controls,
    }


def run():
    core = authenticated_core()
    regs = (608, 609, 610, 612, 410, 417, 419, 421)
    old = json.loads(gzip.decompress((SOURCE / 'inputs/NEW-base.json.gz').read_bytes()))
    original = matrix(old['B'][948:962], regs)
    repaired = matrix([add(608, 609, 1, E)] + common_block() + [add(608, 609, -1, F)], regs)
    need(original == repaired, 'complete eight-coordinate delayed block')
    common = matrix([add(608, 609, 1, E)] + common_block(), regs)
    need(common[608] == {j: original[608].get(j, Q(0)) + original[609].get(j, Q(0))
                        for j in set(original[608]) | set(original[609])
                        if original[608].get(j, Q(0)) + original[609].get(j, Q(0))},
         'encoded common-sum boundary')
    source_minor = [[original[h].get(s, Q(0)) for s in (410, 417)] for h in PAIR]
    determinant = source_minor[0][0] * source_minor[1][1] - source_minor[0][1] * source_minor[1][0]
    need(determinant == 2, 'rank-two actual source-update witness')
    ef, ff, uf, vf = map(span, (E, F, U, V))
    need(len(ef) == 4 and len(ff) == 16 and len(uf) == len(vf) == 64, 'actual frame dimensions')
    need(ef <= ff and ff <= uf and ff <= vf, 'shared and divergent frame containment')
    need(len(uf & vf) == 32 and len(span(U + V)) == 128, 'crossed six-frame dimensions')
    dependent = deepcopy(source_minor)
    for row in dependent:
        row[1] = 2 * row[0]
    dependent_det = dependent[0][0] * dependent[1][1] - dependent[0][1] * dependent[1][0]
    need(dependent != source_minor, 'dependent-source control changed its input')
    controls = [rejected('dependent source columns cannot certify rank two',
                         lambda: need(dependent_det != 0, 'dependent determinant zero'))]
    results = {}
    for provider in ('base', 'extra'):
        word = json.loads(gzip.decompress((SOURCE / ('inputs/NEW-' + provider + '.json.gz')).read_bytes()))
        results[provider] = check_provider(word, core)
    return {
        'status': 'PASS_SCOPED_DEFERRED_SUM_OBSTRUCTION',
        'predecessor': '8d1e3b9399a2a7914f1ab538242cf2e6e6c4cd9f',
        'source_word_head': '9744f9df268590295a9872b1952c695a678192b9',
        'source_export_sha256': EXPORT_SHA256,
        'local_source_update_minor': [[str(x) for x in row] for row in source_minor],
        'source_update_determinant': str(determinant),
        'frames': {'E': E, 'F': F, 'U': U, 'V': V,
                   'dimensions': [2, 4, 6, 6], 'intersection_U_V': 5, 'join_U_V': 7,
                   'U_not_in_V_witness': min(uf - vf), 'V_not_in_U_witness': min(vf - uf)},
        'providers': results,
        'controls_rejected': controls,
        'scope': 'Two pinned finite providers; written pair-chart and F-influence consequences require the stated fixed external source/frame/consumer neighborhood. No arbitrary graph, native phase, new owner, physical supplier, formal-kernel proof or kappa improvement.',
    }


def main():
    ap = ArgumentParser()
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    result = run()
    encoded = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.out:
        need(not args.out.exists(), 'output already exists')
        need(args.out.resolve() != (ROOT / 'RESULT.json').resolve(), 'cannot overwrite committed result')
        args.out.write_text(encoded)
    if (ROOT / 'RESULT.json').exists():
        need(json.loads((ROOT / 'RESULT.json').read_text()) == json.loads(encoded), 'committed result differs')
    print(json.dumps({'status': result['status'], 'providers': list(result['providers']),
                      'inputs_per_provider': 723, 'dirty_buffers': 91,
                      'delayed_paid_profile_delta': {}, 'delayed_scalar_add_delta': 2,
                      'persistent': 'operator PASS; immutable frames reject',
                      'source_minor': '2', 'frame_union_dimension': 7}, sort_keys=True))


if __name__ == '__main__':
    main()
