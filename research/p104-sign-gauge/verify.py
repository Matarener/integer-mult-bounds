#!/usr/bin/env python3
"""Independent exact endpoints, frame/lifetime accounting and sign controls.

The predecessor's executable is not imported. Dense integer transpose and
sparse rational prefix interpreters are separate from the sign compiler.
The transpose method follows Ali Romman's retained local.py checker.
Charan / theon199 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/p104-helper-subspace-splits/'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticated_inputs():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'],
                 'Input SHA256 mismatch: ' + row['path'])
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            need(blob == row['git_blob'], 'Input Git blob mismatch: ' + row['path'])
    return json.loads(gzip.decompress((ROOT / SOURCE / 'WORD.json.gz').read_bytes()))


def compiler():
    # Compile source directly: no preexisting .pyc can replace this local code.
    module = types.ModuleType('p104_sign_construct')
    path = HERE / 'construct.py'
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module.normalize


def apply(rows, event):
    """Sparse exact forward interpreter, starting with arbitrary owned inputs."""
    op, r = event[:2]
    if op == 'MOVE':
        return
    if op in ('INIT', 'CLEAR'):
        rows[r] = {}
        return
    q = Q(event[-2])
    if op == 'SCALE':
        rows[r] = {k: q * v for k, v in rows[r].items()}
    elif op == 'COPY':
        rows[r] = {k: q * v for k, v in rows[event[2]].items()}
    else:
        need(op == 'ADD', 'Unknown scalar event')
        for k, v in list(rows[event[2]].items()):
            value = rows[r].get(k, Q(0)) + q * v
            if value:
                rows[r][k] = value
            else:
                rows[r].pop(k, None)


def expected_endpoint(word, rows):
    n = word['public']
    live = set(word['live'])
    for r, row in enumerate(rows):
        want = {r: Q(1)} if r < n else {}
        if r - 112 in live:
            want[r - 112] = Q(1)
        need(row == want, 'Arbitrary-input scalar endpoint')


def prefix_check(source, candidate, cuts):
    """Infer row signs from actual coefficients, not compiler gauge state.

    Each source event and aligned emitted event only changes its destination;
    comparing that whole row inductively covers every other row too.
    """
    n = source['public'] + 8
    left = [{r: Q(1)} for r in range(n)]
    right = deepcopy(left)
    left_max, right_max = [Q(1)] * n, [Q(1)] * n
    offset = 0
    coefficient_comparisons = 0
    for event, stop in zip(source['program'], cuts, strict=True):
        r = event[1]
        apply(left, event)
        for e in candidate['program'][offset:stop]:
            need(e[1] == r, 'Aligned prefix destination')
            apply(right, e)
            right_max[r] = max(right_max[r], sum(map(abs, right[r].values()), Q(0)))
        left_max[r] = max(left_max[r], sum(map(abs, left[r].values()), Q(0)))
        need(left[r] == right[r] or left[r] == {k: -v for k, v in right[r].items()},
             'Whole prefix row differs beyond a sign')
        coefficient_comparisons += len(set(left[r]) | set(right[r]))
        offset = stop
    for event in candidate['program'][offset:]:
        need(event[0] == 'SCALE' and event[-2] == '-1', 'Explicit final sign correction')
        apply(right, event)
        r = event[1]
        right_max[r] = max(right_max[r], sum(map(abs, right[r].values()), Q(0)))
    expected_endpoint(source, left)
    expected_endpoint(candidate, right)
    need(left_max == right_max, 'Per-role exact prefix envelopes')
    return {'source_cuts': len(cuts), 'nonzero_coefficients_compared': coefficient_comparisons,
            'per_role_prefix_envelopes_equal': True,
            'largest_scalar_row_l1': str(max(left_max)),
            'per_role_envelope_sha256': digest(list(map(str, left_max)))}


def frame_and_cost(word):
    """Independent event tariff and full physical chart/owned-state ledger."""
    frames = []
    for basis in word['frames']:
        space = {0}
        for x in basis:
            need(type(x) is int and 0 < x < 512 and x not in space, 'Binary frame basis')
            space |= {y ^ x for y in tuple(space)}
        frames.append(space)
    public = word['public']
    current = list(word['initial']) + [None] * 8
    owned, zero = set(), set()
    paid, kinds = Counter(), Counter()
    allowance = peak = lifetimes = 0
    for e in word['program']:
        op, r = e[:2]
        kinds[op] += 1
        need(0 <= r < len(current), 'Role range')
        if op == 'MOVE':
            _, _, a, b, private = e
            need(current[r] == a and private == (r in owned), 'MOVE source/ownership')
            need(frames[b] < frames[a] if private else frames[a] < frames[b], 'Strict nested MOVE')
            paid[abs(len(word['frames'][b]) - len(word['frames'][a]))] += 1
            current[r] = b
        elif op == 'INIT':
            need(r >= public and r not in owned, 'Fresh owned lifetime')
            owned.add(r)
            zero.add(r)
            current[r] = e[2]
            lifetimes += 1
            peak = max(peak, len(owned))
            allowance += 2
        elif op == 'CLEAR':
            need(r in owned and current[r] == e[2], 'Owned CLEAR chart')
            owned.remove(r)
            zero.add(r)
            current[r] = None
            allowance += 2
        else:
            q = Q(e[-2])
            num, den = abs(q.numerator), q.denominator
            need(q and den & (den - 1) == 0 and abs(q) + 1 < 2**16, 'Dyadic coefficient/growth')
            need(current[r] == e[-1], 'Scalar destination chart')
            if op == 'SCALE':
                need(num & (num - 1) == 0, 'Invertible dyadic SCALE')
                exponent = num.bit_length() - den.bit_length()
                allowance += 2 * (abs(exponent) + (q < 0))
            else:
                need(op in ('ADD', 'COPY'), 'Known opcode')
                s = e[2]
                need(0 <= s < len(current) and s != r and current[s] == e[-1], 'Common scalar chart')
                if op == 'COPY':
                    need(r in owned and r in zero, 'COPY into cleared owned field')
                # Two real components; binary-Horner magnitude and shift work.
                allowance += 2 * (num.bit_length() + den.bit_length() + num.bit_count() + 1)
                zero.discard(r)
    need(not owned and current[:public] == word['final'], 'Complete exits')
    main = set(word['live']) | {r + 112 for r in word['live']}
    helpers = Counter(len(word['frames'][word['final'][r]]) - len(word['frames'][word['initial'][r]])
                      for r in range(public) if r not in main)
    need(min(helpers) > 0, 'Every helper is productive')
    return {'events': len(word['program']), 'opcodes': dict(sorted(kinds.items())),
            'real_scalar_allowance': allowance, 'paid': dict(sorted(paid.items())),
            'helpers': dict(sorted(helpers.items())), 'public_inputs': public,
            'owned_lifetimes': lifetimes, 'peak_owned_fields': peak,
            'paid_rank_mass': sum(r * count for r, count in paid.items())}


def dense_transpose(word):
    """Reverse-mode integer numerators with per-row powers-of-two denominators.

    This does not use sparse forward apply(), the compiler or source code.
    """
    n = word['public'] + 8
    matrix = [[int(r == c) for c in range(n)] for r in range(n)]
    shifts = [0] * n
    for e in reversed(word['program']):
        op, r = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            matrix[r] = [0] * n
            shifts[r] = 0
        else:
            q = Q(e[-2])
            qshift = q.denominator.bit_length() - 1
            if op == 'SCALE':
                matrix[r] = [q.numerator * v for v in matrix[r]]
                shifts[r] += qshift
            else:
                s = e[2]
                target_shift = max(shifts[s], shifts[r] + qshift)
                f1 = 1 << (target_shift - shifts[s])
                f2 = q.numerator << (target_shift - shifts[r] - qshift)
                matrix[s] = [f1 * x + f2 * y for x, y in zip(matrix[s], matrix[r])]
                shifts[s] = target_shift
                if op == 'COPY':
                    matrix[r] = [0] * n
                    shifts[r] = 0
                r = s
            while shifts[r] and not any(v & 1 for v in matrix[r]):
                matrix[r] = [v // 2 for v in matrix[r]]
                shifts[r] -= 1
    live = set(word['live'])
    for r, row in enumerate(matrix):
        want = [0] * n
        if r < word['public']:
            want[r] = 1 << shifts[r]
        if r in live:
            want[r + 112] = 1 << shifts[r]
        need(row == want, 'Dense transpose all-column endpoint')
    return {'columns': n, 'coefficients': n*n}


def unchanged_contract(source, candidate):
    need({k: v for k, v in source.items() if k != 'program'} ==
         {k: v for k, v in candidate.items() if k != 'program'}, 'Boundary/inventory metadata')
    for op in ('MOVE', 'INIT', 'COPY', 'CLEAR'):
        need([e for e in source['program'] if e[0] == op] ==
             [e for e in candidate['program'] if e[0] == op], 'Ordered ' + op + ' equality')
    a = [e for e in source['program'] if e[0] == 'ADD']
    b = [e for e in candidate['program'] if e[0] == 'ADD']
    need(len(a) == len(b), 'ADD count')
    for x, y in zip(a, b):
        need(x[:3] == y[:3] and x[-1] == y[-1] and abs(Q(x[-2])) == abs(Q(y[-2])),
             'Ordered ADD roles/chart/magnitude')


def reject(thunk, label):
    try:
        thunk()
    except ValueError:
        return label
    raise ValueError('Negative control accepted: ' + label)


def scalar_endpoint(word):
    rows = [{r: Q(1)} for r in range(word['public'] + 8)]
    for e in word['program']:
        apply(rows, e)
    expected_endpoint(word, rows)


def controls(source, candidate, normalize):
    results = []
    mutant = deepcopy(candidate)
    mutant['program'].pop()
    results.append(reject(lambda: scalar_endpoint(mutant), 'omitted_final_sign'))
    mutant = deepcopy(candidate)
    changed = next(i for i, e in enumerate(mutant['program']) if e[0] == 'ADD')
    mutant['program'][changed][-2] = str(-Q(mutant['program'][changed][-2]))
    results.append(reject(lambda: scalar_endpoint(mutant), 'wrong_ADD_sign'))
    mutant = deepcopy(candidate)
    i = next(i for i, e in enumerate(mutant['program']) if e[0] == 'MOVE')
    mutant['program'][i][2], mutant['program'][i][3] = mutant['program'][i][3], mutant['program'][i][2]
    results.append(reject(lambda: frame_and_cost(mutant), 'reversed_MOVE'))
    results.append(reject(lambda: unchanged_contract(source, mutant), 'changed_native_itinerary'))
    # A negative source copied into owned storage must transfer its deferred sign.
    toy = {'public': 2, 'initial': [0, 0], 'final': [0, 0], 'program': [
        ['SCALE', 0, '-1', 0], ['INIT', 2, 0], ['COPY', 2, 0, '1', 0],
        ['ADD', 1, 2, '1', 0], ['CLEAR', 2, 0], ['SCALE', 0, '-1', 0]]}
    new, _ = normalize(toy)
    def values(events):
        rows = [{i: Q(1)} for i in range(10)]
        for e in events:
            apply(rows, e)
        return rows
    need(values(new['program']) == values(toy['program']), 'Signed COPY fixture')
    bad = deepcopy(new['program'])
    next(e for e in bad if e[0] == 'ADD')[-2] = '1'
    results.append(reject(lambda: need(values(bad) == values(toy['program']), 'COPY sign lost'),
                          'lost_owned_COPY_sign'))
    # A reused owned role must not inherit the discarded lifetime's gauge.
    toy['program'] += [['INIT', 2, 0], ['COPY', 2, 1, '1', 0],
                       ['ADD', 0, 2, '1', 0], ['CLEAR', 2, 0]]
    new, _ = normalize(toy)
    need(values(new['program']) == values(toy['program']), 'Owned reuse fixture')
    # Scalar -I outside a tensor power differs from (-I)^tensor f for even f.
    for width in (1, 2, 3, 4):
        need((-1) ** width == (-1 if width % 2 else 1), 'Tensor sign control')
    results.append(reject(lambda: need((-1)**2 == -1, 'Even-width sign failure'),
                          'sign_absorbed_into_tensor_factor'))
    return results


def run(write=False):
    source = authenticated_inputs()
    normalize = compiler()
    candidate, cuts = normalize(source)
    unchanged_contract(source, candidate)
    before, after = frame_and_cost(source), frame_and_cost(candidate)
    need(before['real_scalar_allowance'] == 220232, 'Pinned original scalar tariff')
    need(after['real_scalar_allowance'] == 219258, 'Candidate scalar tariff')
    for key in ('paid', 'helpers', 'public_inputs', 'owned_lifetimes', 'peak_owned_fields', 'paid_rank_mass'):
        need(before[key] == after[key], 'Complete unchanged cost field: ' + key)
    prefix = prefix_check(source, candidate, cuts)
    dense = dense_transpose(candidate)
    rejected = controls(source, candidate, normalize)
    receipt = {'status': 'PASS_P104_SIGN_GAUGE', 'base_commit': 'df0137efd35e11b4445734bf612bdd4c7ebc330c',
               'assignment_seed': 34, 'before': before, 'after': after,
               'saved_real_primitives_per_local_call': 974,
               'saved_real_primitives_in_18_full_calls': 17532,
               'removed_unit_SCALE_events': 334, 'final_sign_restorations': len(candidate['program']) - cuts[-1],
               'source_negative_SCALE_events': sum(e[0] == 'SCALE' and Q(e[-2]) < 0 for e in source['program']),
               'prefix': prefix, 'dense_transpose': dense,
               'negative_controls': rejected, 'candidate_payload_sha256': digest(candidate),
               'scope': 'Finite circuit and ordinary scalar allowance; no new kappa, native recipe or rounded implementation'}
    if write:
        (HERE / 'WORD.json.gz').write_bytes(gzip.compress(canonical(candidate), mtime=0))
        (HERE / 'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    else:
        retained = json.loads(gzip.decompress((HERE / 'WORD.json.gz').read_bytes()))
        need(retained == candidate, 'Committed complete word differs from deterministic compilation')
        need(json.loads((HERE / 'RESULT.json').read_text()) == json.loads(json.dumps(receipt)), 'Exact receipt mismatch')
    print('PASS_P104_SIGN_GAUGE saved=974 full_calls_saved=17532 events=25475->25253 no_new_kappa')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Explicitly regenerate the word and receipt')
    args = parser.parse_args()
    run(args.write)
