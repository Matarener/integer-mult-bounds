#!/usr/bin/env python3
"""Exact optimum of the scalar-witness error floor for the partial-cache observer.

The observation rows come from JoyboyBrian's PR5498 replay, imported only after
its bytes match SOURCES.json. The physical norm convention is Ali Romman's
PR5537; the provider basis and target are Dillon Amburgey's PR5402.
New optimization and certificate: Nick Petalas. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ORIGINAL = 632
MODES = 8
FLOOR = F(7, 92)
KERNEL_DIM = 150


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pinned():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    out = {}
    for pin in manifest['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT/pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'source drift '+pin['path'])
        out[pin['path']] = raw
    return out


def observer_module():
    path = ROOT/'research/partial-cache-history-observer/verify.py'
    spec = importlib.util.spec_from_file_location('pr5498_observer', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def constraint_rows(rows):
    """One linear form on the 632 original roles per (observed row, free word)."""
    out = {}
    for row in rows:
        by_word = {}
        for (owner, word), value in row.items():
            need(owner < ORIGINAL, 'observed row carries owned-input dirt')
            by_word.setdefault(word, {})[owner] = value
        for form in by_word.values():
            out[tuple(sorted(form.items()))] = form
    return list(out.values())


def reduce_against(row, pivots):
    while True:
        hit = next((j for j in row if j in pivots), None)
        if hit is None:
            return row
        factor = row[hit]
        for k, v in pivots[hit].items():
            value = row.get(k, F(0)) - factor*v
            if value:
                row[k] = value
            else:
                row.pop(k, None)


def kernel_basis(forms):
    """Exact reduced row echelon form; returns free roles and kernel basis."""
    pivots = {}
    for form in forms:
        row = reduce_against(dict(form), pivots)
        if not row:
            continue
        lead = min(row)
        scale = row[lead]
        row = {k: v/scale for k, v in row.items()}
        for other in pivots.values():
            factor = other.get(lead)
            if factor:
                for k, v in row.items():
                    value = other.get(k, F(0)) - factor*v
                    if value:
                        other[k] = value
                    else:
                        other.pop(k, None)
        pivots[lead] = row
    free = [j for j in range(ORIGINAL) if j not in pivots]
    basis = []
    for f in free:
        vector = [F(0)]*ORIGINAL
        vector[f] = F(1)
        for lead, row in pivots.items():
            vector[lead] = -row.get(f, F(0))
        basis.append(vector)
    return free, basis


def run_basis(ops, vector):
    out = list(vector)
    for op in ops:
        if op[0] == 'add':
            out[op[1]] += F(op[3])*out[op[2]]
        else:
            need(op[0] == 'scale' and F(op[2]) != 0, 'basis operation')
            out[op[1]] *= F(op[2])
    return out


def physical(provider, raw):
    """PR5537 convention: decode the helper basis, then undo the 2Km mode entrance."""
    decoded = run_basis(provider['output_basis_program'], list(raw)+[F(0)]*9)
    for role in provider['mode_owners']:
        decoded[role] /= 2
    return decoded[:ORIGINAL]


def target(mode_columns, raw):
    return [sum(F(a)*b for a, b in zip(row, raw[112:224]))/2 for row in mode_columns]


def dot(u, v):
    return sum(a*b for a, b in zip(u, v))


def solve_spd(gram, rhs):
    """Gauss-Jordan without row swaps; every pivot must be positive (G is SPD)."""
    n = len(gram)
    a = [gram[i][:]+rhs[i][:] for i in range(n)]
    pivots = []
    for c in range(n):
        need(a[c][c] > 0, 'Gram matrix is not positive definite')
        pivots.append(a[c][c])
        inv = 1/a[c][c]
        a[c] = [x*inv for x in a[c]]
        for r in range(n):
            if r != c and a[r][c]:
                f = a[r][c]
                a[r] = [x-f*y for x, y in zip(a[r], a[c])]
    return [row[n:] for row in a], pivots


def integral(vector):
    from math import lcm, gcd
    den = 1
    for x in vector:
        den = lcm(den, x.denominator)
    ints = [int(x*den) for x in vector]
    g = 0
    for x in ints:
        g = gcd(g, x)
    return [F(x, g) for x in ints]


def ratio(provider, mode_columns, k):
    return dot(target(mode_columns, k), target(mode_columns, k)), dot(physical(provider, k), physical(provider, k))


def annihilates(observer, rows, k):
    displacement = {j: x for j, x in enumerate(k) if x}
    return all(not observer.residual(row, displacement) for row in rows)


def verify():
    pinned()
    observer = observer_module()
    data = observer.inputs()
    provider, normal = data['PROVIDER.json'], data['NORMALIZERS.json']
    m = normal['mode_columns']
    histories, rows, frames, touches = observer.replay(
        data['ACTUAL-WORD.json.gz']['canonical'], data['WORD.json.gz']['word'])
    need(len(histories) == 4891, 'PR5498 distinct full-frame history count')
    observed = [row for _, _, row in histories]+[rows[j] for j in range(633, 641)]
    forms = constraint_rows(observed)
    free, basis = kernel_basis(forms)
    need(len(basis) == KERNEL_DIM, 'scalar kernel dimension')
    for vector in basis:
        need(annihilates(observer, observed, vector), 'basis vector leaves the kernel')

    phys = [physical(provider, b) for b in basis]
    gram = [[dot(u, v) for v in phys] for u in phys]
    c = [target(m, b) for b in basis]
    x, gram_pivots = solve_spd(gram, c)
    for i in range(len(basis)):
        need([dot(gram[i], [x[r][a] for r in range(len(basis))]) for a in range(MODES)] == c[i],
             'G X = C')
    s = [[sum(c[i][a]*x[i][b] for i in range(len(basis))) for b in range(MODES)] for a in range(MODES)]
    need(s == [[FLOOR if a == b else F(0) for b in range(MODES)] for a in range(MODES)],
         'C^T G^-1 C = (7/92) I')

    witnesses = []
    for a in range(MODES):
        k = integral([sum(x[i][a]*basis[i][r] for i in range(len(basis))) for r in range(ORIGINAL)])
        need(annihilates(observer, observed, k), 'optimal witness annihilates every observation')
        t = target(m, k)
        need(all(t[b] == 0 for b in range(MODES) if b != a) and t[a] != 0, 'one-mode target')
        top, bottom = ratio(provider, m, k)
        need(top/bottom == FLOOR, 'witness attains 7/92')
        witnesses.append({'mode': a, 'nonzero_raw_roles': sum(1 for v in k if v),
                          'nonzero_physical_roles': sum(1 for v in physical(provider, k) if v),
                          'target_norm_squared': str(top), 'physical_norm_squared': str(bottom),
                          'raw': [[j, str(v)] for j, v in enumerate(k) if v]})

    old = [F(0)]*ORIGINAL
    for j, value in json.loads((ROOT/'research/partial-cache-history-observer/KERNEL.json').read_text())[
            'original_input_displacement']:
        old[j] = F(value)
    need(annihilates(observer, observed, old), 'PR5498 witness lies in the scalar kernel')
    old_top, old_bottom = ratio(provider, m, old)
    need(old_top/old_bottom == F(1, 19) < FLOOR, 'PR5537 floor 1/19 is strictly smaller')
    return {'basis': basis, 'free': free, 'forms': forms, 'gram_pivots': gram_pivots,
            'observed': observed, 'observer': observer, 'provider': provider, 'm': m,
            'witnesses': witnesses, 'touches': touches, 'histories': len(histories),
            'old': (old_top, old_bottom)}


def controls(state):
    """Each mutation must be rejected or must change the computed optimum."""
    out = {}
    observer, observed = state['observer'], state['observed']
    k = [F(0)]*ORIGINAL
    for j, v in state['witnesses'][1]['raw']:
        k[j] = F(v)
    support = [j for j, v in enumerate(k) if v]
    bumped = list(k)
    bumped[support[0]] += 1
    need(not annihilates(observer, observed, bumped), 'perturbed witness accepted')
    out['perturbed_witness_rejected'] = True
    # Without the eight PR5498 caches the scalar kernel is larger and the optimum differs.
    full_only = constraint_rows(observed[:-8])
    free, basis = kernel_basis(full_only)
    need(len(basis) > KERNEL_DIM, 'caches add no constraint')
    out['kernel_dim_without_caches'] = len(basis)
    phys = [physical(state['provider'], b) for b in basis]
    gram = [[dot(u, v) for v in phys] for u in phys]
    c = [target(state['m'], b) for b in basis]
    x, _ = solve_spd(gram, c)
    diag = [sum(c[i][a]*x[i][a] for i in range(len(basis))) for a in range(MODES)]
    need(max(diag) > FLOOR, 'cache-free optimum must exceed the observed-channel optimum')
    out['cache_free_mode_diagonal_max'] = str(max(diag))
    # The raw (non-physical) norm gives a different constant: the basis matters.
    raw_top = dot(target(state['m'], k), target(state['m'], k))
    need(raw_top/dot(k, k) != FLOOR, 'raw norm coincides with physical norm')
    out['raw_norm_ratio_of_mode1_witness'] = str(raw_top/dot(k, k))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    state = verify()
    w1 = state['witnesses'][1]
    result = {
        'status': 'PASS_PARTIAL_CACHE_SCALAR_WITNESS_FLOOR',
        'distinct_full_frame_histories': state['histories'],
        'endpoint_caches': 8,
        'distinct_word_constraints': len(state['forms']),
        'constraint_rank': ORIGINAL-len(state['basis']),
        'scalar_kernel_dimension': len(state['basis']),
        'gram_positive_pivots': len(state['gram_pivots']),
        'optimal_squared_floor': str(FLOOR),
        'optimal_floor_decimal_lower': '0.27583',
        'previous_squared_floor': str(state['old'][0]/state['old'][1]),
        'optimum_matrix': '(7/92) I_8',
        'mode1_witness': w1,
        'per_mode_witness_supports': [[w['nonzero_raw_roles'], w['nonzero_physical_roles']]
                                      for w in state['witnesses']],
        'controls': controls(state),
        'scope': 'exact optimum over scalar witnesses k(x)v in the PR5498 free-word observation '
                 'grammar under PR5537 physical norms; lower bound on ||T restricted to ker O||, '
                 'not that norm; no kappa change',
    }
    need(F(27583, 100000)**2 < FLOOR, 'decimal floor is a lower bound')
    if not args.emit:
        expected = json.loads((HERE/'RESULT.json').read_text())
        need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
             'receipt mismatch')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
