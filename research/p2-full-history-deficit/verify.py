#!/usr/bin/env python3
"""Classify all diagonal target columns in the frozen p2 history.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The D-left algebra and phase interpreter are unchanged credited inputs.
"""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / 'inputs' / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def reduced(word):
    out = []
    for x in word:
        if out and (out[-1] == -x or x in (2, 3) and out[-1] == x):
            out.pop()
        else:
            out.append(x)
    return tuple(out)


class Right:
    """D-right normal form, checked against the credited D-left algebra."""
    def __init__(self):
        self.one = {((), (0, 0)): Q(1)}
        self.q, self.qi, self.c, self.e = [{((x,), (0, 0)): Q(1)} for x in (1, -1, 2, 3)]
        self.d, self.f = [{((), ds): Q(1)} for ds in ((1, 0), (0, 1))]

    @staticmethod
    def add(*polys):
        out = defaultdict(Q)
        for p in polys:
            for key, value in p.items():
                out[key] += value
        return {key: v for key, v in out.items() if v}

    @staticmethod
    def neg(p):
        return {key: -v for key, v in p.items()}

    def mul(self, *polys):
        out = self.one
        for p in polys:
            acc = defaultdict(Q)
            for (u, ds), a in out.items():
                for (v, es), b in p.items():
                    letters = list(u)
                    for x in v:
                        n = ds[x - 2] if x in (2, 3) else 0
                        letters += [-1] * n + [x] + [1] * n
                    acc[reduced(letters), tuple(x + y for x, y in zip(ds, es))] += a * b
            out = {key: v for key, v in acc.items() if v}
        return out


def observations(a, omit_minus_bridge=False):
    rows = [[a.one if i == j else {} for j in range(4)] for i in range(4)]
    obs = []

    def plus(i, j, z):
        rows[i] = [a.add(x, a.mul(z, y)) for x, y in zip(rows[i], rows[j])]

    def left(i, z):
        rows[i] = [a.mul(z, x) for x in rows[i]]

    def snap(label):
        obs.extend((label + ':' + str(i), list(row)) for i, row in enumerate(rows))

    def thin(pair, before, after, label):
        response = [a.mul(before, x) for x in rows[2 * pair]]
        obs.append((label, response))
        rows[2 * pair + 1] = [a.add(x, a.mul(after, y))
                              for x, y in zip(rows[2 * pair + 1], response)]

    def full(pair, c, d):
        plus(2 * pair, 2 * pair + 1, a.neg(a.mul(a.q, c)))
        left(2 * pair, d)
        left(2 * pair + 1, d)

    def bridge(dst, src, sign):
        plus(2 * dst, 2 * src, a.one if sign == 1 else a.neg(a.one))
        plus(2 * src + 1, 2 * dst + 1, a.neg(a.one) if sign == 1 else a.one)

    plus(0, 2, a.neg(a.one))
    plus(3, 1, a.one)
    snap('cut0_after_right_boundary')
    thin(0, a.qi, a.c, 'paid_response0_Qinv_x')
    snap('cut1_after_thin0')
    full(0, a.c, a.d)
    snap('cut2_after_FULL1')
    left(2, a.d)
    left(3, a.d)
    snap('cut3_after_IDLE')
    bridge(0, 1, 1)
    thin(0, a.mul(a.qi, a.c), a.one, 'paid_response2_Qinv_C1_x')
    snap('cut4_after_bridge_plus_and_thin2')
    if not omit_minus_bridge:
        bridge(0, 1, -1)
    snap('cut5_after_bridge_minus')
    full(1, a.e, a.f)
    snap('cut6_after_FULL3')
    thin(1, a.mul(a.qi, a.e), a.one, 'paid_response4_Qinv_C3_x')
    snap('cut7_after_thin4')
    bridge(1, 0, 1)
    for pair in range(2):
        x, y = 2 * pair, 2 * pair + 1
        rows[x], rows[y] = rows[y], [a.neg(z) for z in rows[x]]
    plus(0, 2, a.one)
    plus(3, 1, a.neg(a.one))
    snap('cut8_after_final_standard_boundary')
    return obs


def to_right(left, r):
    out = {}
    for (ds, word), value in left.items():
        p = r.one
        for g, count in zip((r.d, r.f), ds):
            for _ in range(count):
                p = r.mul(p, g)
        for x in word:
            p = r.mul(p, {1: r.q, -1: r.qi, 2: r.c, 3: r.e}[x])
        out = r.add(out, {key: value * v for key, v in p.items()})
    return out


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            bit = v.bit_length() - 1
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit] = v
                break
    return len(pivots)


def linear(rows, v):
    return sum(((a & v).bit_count() % 2) << i for i, a in enumerate(rows))


def inverse(rows):
    n = len(rows)
    aug = [x | (1 << (n + i)) for i, x in enumerate(rows)]
    for j in range(n):
        k = next(k for k in range(j, n) if aug[k] >> j & 1)
        aug[j], aug[k] = aug[k], aug[j]
        for i in range(n):
            if i != j and aug[i] >> j & 1:
                aug[i] ^= aug[j]
    return [v >> n for v in aug]


def physical_grades(code, normal):
    """Compute ranks from native binary maps without the source rank routine."""
    ce = load('p2_phase_source', 'clifford_exact.py')
    ks, matrices = [], []
    for record in normal['ports']:
        op = ce.ident(9)
        for e in record['K_word']:
            if e[0] == 'P':
                op = op.then(ce.perm(9, e[1]))
            elif e[0] == 'D':
                need(not any(e[1]) and all(x % 2 == 0 for x in e[2]), 'Pauli phase only')
                op = op.then(ce.diag(9, e[1], e[2]))
            else:
                raise ValueError('Unexpected normalizer gate')
        need(len(record['K_word']) == 2 and record['K_word'][0][0] == 'P', 'Normalizer form')
        g = record['K_word'][0][1]
        need(all(((x & y).bit_count() % 2) == (i == j)
                 for i, x in enumerate(g) for j, y in enumerate(g)), 'Orthogonal source G')
        gaussian = ce.fourier(9)
        a, b = op.then(gaussian), gaussian.then(op)
        need(a.tab == b.tab and a.zero_state() == b.zero_state(), 'Signed Gaussian commutation')
        matrices.append(g)
        ks.append(op)
    invs = [inverse(g) for g in matrices]
    per_column, pairs = [], []
    d = ce.fourier(9, range(1, 9))
    qi = ce.cgate(9, 1).adjoint()
    for j in range(112):
        grades = set()
        for i in range(112):
            if not code[i][j]:
                continue
            # Q^-1 K_i^-1 K_j D: track the X part of every Z image.
            gcol = [linear(invs[i], linear(matrices[j], 1 << k)) for k in range(9)]
            xcols = [(gcol[k] if k else 0) ^ (gcol[k] & 1) for k in range(9)]
            value = rank(xcols)
            source_op = d.then(ks[j]).then(ks[i].adjoint()).then(qi)
            need(value == rank([x for x, _, _ in source_op.tab[9:]]), 'Independent physical grade')
            grades.add(value)
            pairs.append([i, j, str(code[i][j]), value])
        per_column.append(grades)
    return per_column, pairs


def grades_for(term, j, late):
    word, ds = term
    weight = 8 * sum(ds)
    if word in ((), (3, 2)):
        return {weight}
    if word in ((-1,), (2, -1)) and ds == (0, 0):
        return {1}
    if word in ((2, 1), (3, 1)):
        return {weight + 1}
    if word == (-1, 2) and ds in ((1, 0), (1, 1)):
        return {g + 8 * ds[1] for g in late[j]}
    if word == (-1, 3) and ds == (1, 1):
        return {g + 8 for g in late[j]}
    raise ValueError('Unclassified physical term ' + str(term))


def encode(obs):
    return [{'label': label, 'columns': [[{'word': list(w), 'fresh': list(ds),
             'coefficient': str(v)} for (w, ds), v in sorted(p.items())] for p in row]}
            for label, row in obs]


def coset_witnesses(code, gs):
    columns = [linear(g, 1) for g in gs]
    need(len(set(columns)) == 112, 'Distinct left monomial cosets')
    zero = [j for j in range(112) if not code[j][j]]
    witnesses = [next((j for j in zero if code[i][j]), None) for i in range(112)]
    need(all(j is not None for j in witnesses), 'Every row meets a zero-diagonal column')
    # A fixed j has distinct u=G_j^-1 G_i e0. The rank-one matrices u*u^T
    # distinguish the left cosets. The diagonal of u*u^T recovers u.
    for j in zero:
        gi = inverse(gs[j])
        us = [linear(gi, columns[i]) for i in range(112) if code[i][j]]
        need(len(us) == len(set(us)) and 1 not in us, 'Distinct off-diagonal coset signatures')
    return witnesses


def rejected(fn, label):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('Control accepted: ' + label)


def module_extension(code, normal, obs, a):
    """Check the extra source facts used by the complete target-module proof."""
    gs = [r['K_word'][0][1] for r in normal['ports']]
    witnesses = coset_witnesses(code, gs)
    controls = [rejected(lambda: coset_witnesses(code, [gs[0]] * 112), 'homogeneous false frames')]
    bad = [row[:] for row in code]
    for j in range(112):
        if not code[j][j]:
            bad[0][j] = Q(0)
    controls.append(rejected(lambda: coset_witnesses(bad, gs), 'unwitnessed code row'))

    lookup = dict(obs)
    dd = a.mul(a.d, a.f)
    A = a.mul(a.qi, a.e, dd)
    B = a.mul(a.qi, a.c, dd)
    L = a.mul(a.add(a.one, a.neg(a.mul(a.e, a.c))), dd)
    Z = a.neg(a.mul(a.e, a.q, dd))
    need(lookup['cut6_after_FULL3:2'] == [{}, {}, L, Z], 'Literal high-layer C row')
    need(lookup['cut6_after_FULL3:3'] == [{}, {}, B, dd], 'Literal high-layer B row')
    need(lookup['cut7_after_thin4:3'] == [{}, {}, A, {}], 'Literal high-layer A row')
    need(lookup['paid_response4_Qinv_C3_x'] == [{}, {}, a.add(A, a.neg(B)), a.neg(dd)],
         'Paid response is A minus B')
    need(lookup['cut2_after_FULL1:0'] == [{}, a.neg(a.mul(a.c, a.d, a.q)), {}, {}],
         'First positive target has a free code decoder')
    generators = [[A, {}], [B, dd], [L, Z], [a.add(A, a.neg(B)), a.neg(dd)]]
    allowed = [[{}, {}]] + generators + [[a.neg(p) for p in v] for v in generators]
    for _, row in obs:
        high = [{key: value for key, value in p.items() if key[1] == (1, 1)} for p in row]
        need(not high[0] and not high[1] and high[2:] in allowed,
             'Every high-layer observation is in A,B,C')

    def act(g, v, axes):
        local = sum(((v >> k) & 1) << i for i, k in enumerate(axes))
        value = linear(g, local)
        for i, k in enumerate(axes):
            v = (v & ~(1 << k)) | (((value >> i) & 1) << k)
        return v

    first, second = list(range(9)), [0] + list(range(9, 17))
    invs = [inverse(g) for g in gs]
    identity_terms = []
    for k in range(112):
        if not code[0][k] * code[k][0]:
            continue
        cols = []
        for j in range(17):
            v = act(gs[0], 1 << j, first)
            v = act(invs[k], v, first)
            v = act(gs[k], v, second)
            cols.append(act(invs[0], v, second))
        if cols == [1 << j for j in range(17)]:
            identity_terms.append(k)
    need(identity_terms == [0] and code[0][0] == 12, 'Unique identity term in leakage entry')
    # The k=0 word is literally identity, with phase one. Every other
    # supported word has a nonidentity linear part, so cannot be projectively I.
    identity_coefficient = 1 - code[0][0] ** 2
    need(identity_coefficient == -143, 'Nonzero leakage coefficient')
    trace = sum(code[i][i] for i in range(112))
    need(trace == 96, 'Rank-eight minus eigenspace')
    return {'all_negative_columns': 224, 'row_witnesses': witnesses,
            'rejected_module_controls': controls,
            'nonzero_leak_identity_coefficient': str(identity_coefficient),
            'negative_eigenspace_rank': int((112 - trace) / 2),
            'complete_return_lower_bound': 225, 'arbitrary_oracle_upper_bound': 240}


def main():
    for pin in json.loads((HERE / 'INPUTS.json').read_bytes()):
        need(sha256((HERE / pin['local_path']).read_bytes()).hexdigest() == pin['sha256'], 'Source pin')
    right = Right()
    obs = observations(right)
    left = load('p2_left_source', 'algebra.py')
    other = [(label, [to_right(p, right) for p in row]) for label, row in observations(left)]
    need(obs == other and len(obs) == 39, 'All 156 bank coefficients in both normal forms')
    need(observations(right, True) != obs, 'Omitted bridge control')
    target_terms = [right.mul(right.d, right.qi), right.mul(right.d, right.q),
                    right.mul(right.f, right.d, right.qi), right.mul(right.f, right.d, right.q)]
    # With no code, the declared four targets must be the exact endpoint.
    plain = Right()
    plain.c = plain.e = plain.one
    last = [row for _, row in observations(plain)[-4:]]
    need(last == [[target_terms[i] if i == j else {} for j in range(4)] for i in range(4)],
         'Uncoded full endpoint control')
    raw = json.loads(gzip.decompress((HERE / 'inputs/INVOLUTIVE-WORD.json.gz').read_bytes()))['F']
    code = [[Q(raw[j][i]) for j in range(112)] for i in range(112)]
    need(code[0][1] == Q(-1, 2), 'Literal F transpose entry')
    scale = max(q.denominator for row in code for q in row)
    need(all((q * scale).denominator == 1 for row in code for q in row), 'Exact integer scale')
    ints = [[int(q * scale) for q in row] for row in code]
    need(all(sum(ints[i][k] * ints[k][j] for k in range(112)) == (scale * scale if i == j else 0)
             for i in range(112) for j in range(112)), 'Literal code involution')
    normal = json.loads((HERE / 'inputs/NORMALIZERS.json').read_bytes())
    late, pairs = physical_grades(code, normal)
    zero = [j for j in range(112) if not code[j][j]]
    need(len(zero) == 104 and all(late[j] == {7} for j in zero), 'Complete zero-diagonal source')
    terms = [sorted({key for _, row in obs for key in row[b]}) for b in range(4)]
    targets = [9, 9, 17, 17]
    missing, support = [], []
    for b in range(4):
        column_support = [sorted(set().union(*(grades_for(t, j, late) for t in terms[b])))
                          for j in range(112)]
        absent = [j for j, ranks in enumerate(column_support) if targets[b] not in ranks]
        missing.append(absent)
        support.append(column_support)
    need(missing == [zero, [], zero, []], 'Maximal grade-separated target set')
    extension = module_extension(code, normal, obs, right)
    b = extension['complete_return_lower_bound']
    paid = {1: 4754 + b, 2: 824, 3: 1020, 4: 254, 5: 80, 8: 224}
    target = {4: 56, 7: 14, 8: 94, 9: 876, 17: 224}
    hinges = {str(k): sum(n * min(r, k) for r, n in paid.items()) -
              sum(n * min(r, k) for r, n in target.items())
              for k in sorted(set(paid) | set(target))}
    need(min(hinges.values()) > 0 and hinges['17'] == 129, 'All-concave adverse bill')
    # Selected diagonal terms and both positive banks defeat a larger grade claim.
    need(all(9 in late[j] for j in set(range(112)) - set(zero)), 'Selected positive controls')
    out = {'status': 'PASS_P2_FULL_HISTORY_DEFICIT', 'observations': 39,
           'bank_coefficients': 156, 'original_columns': 448,
           'term_families': [len(t) for t in terms], 'supported_native_pairs': len(pairs),
           'native_pair_sha256': sha256(json.dumps(pairs, separators=(',', ':')).encode()).hexdigest(),
           'missing_per_bank': list(map(len, missing)), 'missing_columns': missing,
           'necessary_returns': b, 'minimum_width': 72, 'module_extension': extension,
           'error_bound_columns': 208,
           'reference_q36_squared_error_width84': str(Q(125, 126) * (1 - Q(36, 208))),
           'any_profitable_q95_squared_error_width84': str(Q(125, 126) * (1 - Q(95, 208))),
           'repair_hinges': hinges, 'grade_support': support, 'new_kappa': None}
    trace = encode(obs)
    for filename, value in [('RESULT.json', out), ('OBSERVATIONS.json', trace)]:
        if '--write' in sys.argv:
            (HERE / filename).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
        else:
            need(value == json.loads((HERE / filename).read_bytes()), 'Exact ' + filename)
    print(json.dumps({k: v for k, v in out.items() if k not in ('grade_support', 'missing_columns')}, sort_keys=True))


if __name__ == '__main__':
    main()
