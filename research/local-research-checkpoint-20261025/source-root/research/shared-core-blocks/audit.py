"""Block-label shared-core ledger and exact direct-sum controls.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
No new local characteristic-dependent core or assembled supplier is asserted.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('block_power_tools',
    HERE.parent/'higher-rank-sixteenth/screen.py')
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)
require, encode = H.require, H.encode


def power(x, s):
    p = 1-s
    return H.power_interval(Q(x), p.numerator, p.denominator)


def shared_profile(d, r, v, R, loss, internal, source, target, gauges=None):
    gauges = gauges or {}
    require(0 < r < d and v > 0 and R >= 0 and loss >= 0, 'profile parameters')
    require(all(0 < a < d and count >= 0 for a, count in gauges.items()), 'proper gauges')
    require(sum(gauges.values()) <= R, 'gauge stock')
    def mass(rows):
        require(all(0 < k <= d and count >= 0 for k, count in rows.items()), 'local widths')
        return sum(k*count for k, count in rows.items())
    gauge_mass = sum(a*count for a, count in gauges.items())
    require(mass(internal) == R*d-gauge_mass+loss, 'complete auxiliary local mass')
    source_mass, target_mass = mass(source), mass(target)
    require(min(source_mass, target_mass) >= v*(d-r), 'data endpoint rank floor')
    data_excess = source_mass+target_mass-2*v*(d-r)
    children = Counter()
    for rows in (internal, source, target):
        for width, count in rows.items():
            children[width] += 3*count
    children[2*r] += 2*v
    for a, count in gauges.items():
        children[3*a] += count
    W, m = 2*v+R, 3*d
    total = sum(t*c for t, c in children.items())
    require(W*m-total == 2*v*r-3*(loss+data_excess), 'block deficit identity')
    require(all(0 < t < m for t in children), 'strict child widths')
    return dict(d=d, label_rank=r, v=v, R=R, auxiliary_loss=loss,
                data_excess=data_excess, loss=loss+data_excess, m=m, W=W,
                rank=total, deficit=W*m-total, child_histogram=dict(sorted(children.items())))


def moment(hist, m, W, saving):
    return H.moment(hist, m, W, saving)


def ideal_budget(d, r, saving, rho=Q(1), loss_ratio=Q(0)):
    """Lower bound for the stipulated zero-gauge compiler; not an attained profile.

    rho=R/v; loss_ratio=L_aux/(v*d). Data paths retain their minimum rank
    and are ideally single children; auxiliary rank is packed fractionally
    into width d. Zero gauge only. Data excess needs its actual histogram.
    """
    require(0 < r < d and rho >= 0 and loss_ratio >= 0, 'budget domain')
    m = 3*d
    rows = Counter()
    rows[d-r] += 6
    rows[2*r] += 2
    rows[d] += 3*(rho+loss_ratio)
    lo, hi = moment(rows, m, 2+rho, saving)
    bare = moment(Counter({d-r: 6, 2*r: 2}) if d-r != 2*r
                  else Counter({d-r: 8}), m, 2, saving)
    aux = power(Q(1, 3), saving)
    A = (3*aux[0], 3*aux[1])  # 3**saving, cost per ungauged role
    require(A[0] > 1, 'positive source-role cost excess')
    residual = (2-2*bare[1]-rho*(A[1]-1)-A[1]*loss_ratio,
                2-2*bare[0]-rho*(A[0]-1)-A[0]*loss_ratio)
    return dict(d=d, r=r, rank_ratio=Q(r, d), saving=saving, rho=rho,
                loss_ratio=loss_ratio, moment_interval=[lo, hi],
                bare_moment_interval=list(bare), auxiliary_cost_interval=list(A),
                residual_interval=list(residual),
                maximum_zero_loss_rho_interval=[(2-2*bare[1])/(A[1]-1),
                                                (2-2*bare[0])/(A[0]-1)],
                status='optimistic pass' if hi < 1 else 'excluded' if lo > 1 else 'undecided',
                scope='Zero entrance gauges; full local histogram still required.')


def compose(a, b):
    return tuple(a[b[i]] for i in range(len(a)))


def swap_perm(n, left, right):
    p = list(range(n))
    for a, b in zip(left, right):
        p[a], p[b] = p[b], p[a]
    return tuple(p)


def image(p, subset):
    return frozenset(p[i] for i in subset)


def geometry_control(scale=1):
    # Six cells: U, V=A-U, B, C, Z1, Z2; each cell has `scale` coordinates.
    # d=2*scale, r=scale, m=6*scale. This is a direct sum, not new geometry.
    cells = [frozenset(range(i*scale, (i+1)*scale)) for i in range(6)]
    U, V, B, C, Z1, Z2 = cells
    A, E, Z = U|V, U|V|B|C, Z1|Z2
    P = (A, B|Z1, C|Z2)
    r12 = swap_perm(6*scale, sorted(V), sorted(B))
    r23 = swap_perm(6*scale, sorted(V), sorted(C))
    Hs = (tuple(range(6*scale)), swap_perm(6*scale, sorted(A), sorted(P[1])),
          swap_perm(6*scale, sorted(A), sorted(P[2])))
    require(image(r12, A) == U|B and image(r23, A) == U|C, 'active exchanges')
    require(image(r23, V|B) == B|C, 'port-independent third offset')
    active = (U|B, A, U|C)
    for i in range(3):
        for j in range(i):
            require(active[i]&active[j] == U, 'common block intersection')
    require(set.union(*(set(p) for p in P)) == set(range(6*scale)), 'bank coverage')
    require(sum(map(len, P)) == 6*scale, 'disjoint full bank coverage')
    # Exact finite subgroup control. It is NOT the full generic routing group
    # used for an all-size supplier or a certificate of its rare-class bound.
    G = [tuple(p[i]*scale+j for i in range(6) for j in range(scale))
         for p in permutations(range(6))]
    group = set(G)
    for R in (r12, r23, *Hs):
        require({compose(g, R) for g in G} == group, 'incidence bijection')
    for g in G:
        for R in (r12, r23):
            require(image(compose(g, R), U) == image(g, U), 'same source block')
        for Hs_j, P_j in zip(Hs, P):
            require(image(compose(g, Hs_j), A) == image(g, P_j), 'paid bank routing')
    return dict(scale=scale, d=2*scale, r=scale, m=6*scale, data_cover_dimension=4*scale,
                group_size=len(G), data_ports=len(G), independent_roles=3*len(G),
                r12=r12, r23=r23, bank_maps=Hs,
                all_incidence_bijections=True, source_block_consistent=True,
                no_simultaneous_bank_use=True,
                scope='Explicit coordinate-subgroup control; no generic routing/prime theorem.')


# Sparse operator expressions in commuting coordinate transforms C_j.
# Complex C_j have exact order four; bit partial swaps have order two.
# Keeping exponent two for C_j is essential: C_j**2 is a Pauli, not identity.
def clean(expr, modulus):
    return {k: (c % 2 if modulus == 2 else c) for k, c in expr.items()
            if (c % 2 if modulus == 2 else c)}


def plus(a, b, coefficient, modulus):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0)+coefficient*value
    return clean(out, modulus)


def move(expr, delta, modulus):
    out = {}
    for (role, exponents), coefficient in expr.items():
        key = (role, tuple((a+b) % modulus for a, b in zip(exponents, delta)))
        out[key] = out.get(key, 0)+coefficient
    return clean(out, modulus)


def unit(role, dim):
    return {(role, (0,)*dim): 1}


def local_control(scale, modulus):
    d, r = 2*scale, scale
    U = (1,)*r+(0,)*(d-r)
    I = (1,)*d
    cap = tuple(1-u for u in U)
    values = [unit(i, d) for i in range(3)]
    original = [dict(x) for x in values]
    operations = [
        ('add', 1, 2, -1, (0,)*d, 0),  # initial arbitrary dirty response
        ('move', 2, None, 1, U, r),
        ('add', 2, 0, 1, (0,)*d, 0),
        ('add', 1, 2, 1, tuple(-u for u in U), r),  # paid copied-center read
        ('move', 0, None, 1, cap, d-r),
        ('move', 2, None, 1, cap, d-r),
        ('add', 2, 0, -1, (0,)*d, 0),
        ('move', 1, None, 1, cap, d-r),
    ]
    def execute(ops):
        for kind, target, control, coeff, delta, cost in ops:
            if kind == 'move':
                values[target] = move(values[target], delta, modulus)
            else:
                values[target] = plus(values[target], move(values[control], delta, modulus), coeff, modulus)
    execute(operations)
    expected = [move(original[0], cap, modulus),
                plus(move(original[1], cap, modulus),
                     move(original[0], tuple(a-b for a, b in zip(cap, U)), modulus), 1, modulus),
                move(original[2], I, modulus)]
    require(values == expected, 'complete local source/target/dirty endpoint')
    inverse = [(kind, t, c, (-coeff if kind == 'add' else coeff),
                tuple(-a for a in delta) if kind == 'move' else delta, cost)
               for kind, t, c, coeff, delta, cost in reversed(operations)]
    execute(inverse)
    require(values == original, 'literal inverse including copied read')
    internal = Counter({r: 2})
    internal[d-r] += 1
    source, target = Counter({d-r: 1}), Counter({d-r: 1})
    profile = shared_profile(d, r, 1, 1, r, internal, source, target)
    require(profile['deficit'] == -r, 'negative control deficit')
    # Exact global data endpoint, with every phase power retained.
    m = 3*d
    u = (1,)*r+(0,)*(m-r)
    e = (1,)*(3*d-2*r)+(0,)*(2*r)
    tail = tuple(1-a for a in e)
    def data_output(include_pauli):
        x, y = unit(0, m), unit(1, m)
        if include_pauli:
            x = move(x, tuple(2*a for a in u), modulus)
        x = move(x, tuple(-a for a in u), modulus)  # logical entrance T_U^-1
        y = plus(y, x, 1, modulus)
        x = plus(x, y, -1, modulus)
        y = plus(y, x, 1, modulus)
        x = move(x, e, modulus)
        y = move(y, tuple(a-b for a, b in zip(e, u)), modulus)
        x, y = move(x, tail, modulus), move(y, tail, modulus)
        x = plus({}, x, -1, modulus)
        return y, x  # actual output bank exchange
    expected_global = (move(unit(0, m), (1,)*m, modulus),
                       move(unit(1, m), (1,)*m, modulus))
    require(data_output(True) == expected_global, 'global data endpoint')
    require((data_output(False) == expected_global) == (modulus == 2), 'complex Pauli necessity')
    # A zero-gauge completed dirty core acts as the full active transform.
    # The middle stage is its exact inverse, with its square Pauli paid.
    z = unit(2, m)
    for j in range(3):
        block = tuple(int(j*d <= i < (j+1)*d) for i in range(m))
        z = move(z, tuple((-1 if j == 1 else 1)*a for a in block), modulus)
        if j == 1:
            z = move(z, tuple(2*a for a in block), modulus)
    require(z == move(unit(2, m), (1,)*m, modulus), 'completed auxiliary bank endpoint')
    return dict(scale=scale, operator_order=modulus, local_word=operations,
                exact_arbitrary_inputs=True, literal_inverse=True,
                composed_global_data_and_dirty_endpoints=True,
                omitted_complex_pauli_rejected=modulus == 4,
                profile=profile)


def frozen_lift():
    sys.set_int_max_str_digits(0)
    path = ROOT/'research/coordinated-frames-and-entrance-banks/certificate.json'
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() ==
            '59b20818af6f850f40d18fd8206b136da504d9cbc57dbbefcba232c62f3384e6',
            'selected certificate pin')
    c = json.loads(raw)
    # Locate the unique normalized complex profile by its exact scalar data.
    found = []
    def visit(x):
        if isinstance(x, dict):
            if x.get('m') == 66 and x.get('W_per_vertex') == 13326 and 'child_histogram' in x:
                found.append(x)
            for y in x.values():visit(y)
        elif isinstance(x, list):
            for y in x:visit(y)
    visit(c)
    require(found, 'selected profile exists')
    p = found[0]
    hist = {int(t): n for t, n in p['child_histogram'].items()}
    require(sum(t*n for t, n in hist.items()) == 878196, 'selected complex mass')
    lifted = {2*t: n for t, n in hist.items()}
    require(sum(t*n for t, n in lifted.items()) == 2*878196, 'lifted mass')
    controls = {}
    for s in (Q(2, 25), Q(3, 40)):
        before, after = moment(hist, 66, 13326, s), moment(lifted, 132, 13326, s)
        require(before == after, 'exact direct-sum moment invariance')
        controls[str(s)] = before
    return dict(source_sha256=hashlib.sha256(raw).hexdigest(), role_count=13326,
                original=dict(d=22, r=1, m=66, loss=440, rank=878196, deficit=1320),
                rank_two=dict(d=44, r=2, m=132, loss=880, rank=1756392, deficit=2640),
                lifted_histogram=lifted, moment_controls=controls,
                invariance='Every width and ambient dimension doubles; all ratios t/m and W stay fixed.',
                scope='Lift of the finite address geometry and scalar identities only. '
                      'No new generic bases, prime certificate, group stock or all-size bridge claimed.')


def complex_phase_control():
    def add(a, b):return (a[0]+b[0], a[1]+b[1])
    def mul(a, b):return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
    def matmul(a, b):
        return [[add(mul(a[i][0], b[0][j]), mul(a[i][1], b[1][j]))
                 for j in range(2)] for i in range(2)]
    alpha, beta = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
    C = [[alpha, beta], [beta, alpha]]
    z, o = (Q(0), Q(0)), (Q(1), Q(0))
    X, I = [[z, o], [o, z]], [[o, z], [z, o]]
    square = matmul(C, C)
    require(square == X and square != I, 'exact Gaussian-dyadic square')
    require(matmul(square, square) == I, 'exact fourth power')
    return dict(C=C, square=square, fourth_power=I,
                justification='The coordinate operator algebra used in the controls specializes to this exact C.')


def fano_screen():
    # Seven lines on F_2^3 minus zero, any two meeting in one point.
    lines = sorted({tuple(sorted((a, b, a^b))) for a in range(1, 8)
                    for b in range(a+1, 8)})
    require(len(lines) == 7 and all(len(set(a)&set(b)) == 1 for i, a in enumerate(lines)
                                   for b in lines[:i]), 'Fano clique')
    # If these labels must mutually annihilate, 7r<=d. The bare moment is
    # concave in t=r/d, so its minimum on [0,1/7] is at an endpoint.
    s = Q(1, 15)  # Weaker than the necessary coarse bit target for kappa=1/16.
    zero = power(Q(1, 3), s)
    endpoints = [(3*zero[0], 3*zero[1]),
                 ideal_budget(7, 1, s, rho=Q(0))['bare_moment_interval']]
    require(all(lo > 1 for lo, hi in endpoints), 'uniform Fano capped rejection')
    return dict(lines=lines, necessary_rank_ratio_upper=Q(1, 7), saving=s,
                endpoint_moments=endpoints,
                scope='Full intersection-one triple annihilation graph, shared-core data paths '
                      'and padding tails, each extra auxiliary paying at least its full rank capacity. '
                      'Does not assert that every future scalar circuit requires these edges.')


def audit():
    controls = [local_control(k, order) for k in (1, 2) for order in (2, 4)]
    a, b = controls[0]['profile'], controls[2]['profile']
    require(b['child_histogram'] == {2*t: c for t, c in a['child_histogram'].items()}, 'small direct-sum histogram')
    cases = [ideal_budget(d, r, s) for d, r in ((7, 1), (3, 1), (5, 2),
             (11, 5), (15, 7), (19, 9), (2, 1)) for s in (Q(2, 25), Q(3, 40))]
    # A rational hypothetical local bill with integral child multiplicities.
    # It passes arithmetically, but no label family or scalar producer supplies it.
    target = shared_profile(19, 9, 250, 250, 19, {19: 251}, {10: 250}, {10: 250})
    target['moments'] = {str(s): moment(target['child_histogram'], target['m'], target['W'], s)
                         for s in (Q(2, 25), Q(3, 40))}
    require(all(x[1] < 1 for x in target['moments'].values()), 'hypothetical budget pass')
    target['status'] = 'UNIMPLEMENTED BUDGET; no geometry, local circuit or finite supplier'
    sources = ['notes/paired-cube-sharing.tex', 'notes/three-stage-cover-complex.tex',
               'notes/three-stage-cover-bit.tex', 'notes/general-clifford-frames.tex',
               'scripts/paired_cube/frames.py', 'scripts/paired_cube/gauges.py',
               'research/higher-rank-sixteenth/screen.py']
    return dict(status='BLOCK GEOMETRY/LEDGER DERIVED CONDITIONALLY; DIRECT SUM VERIFIED; NO NEW KAPPA',
                source_pins={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
                geometry_controls=[geometry_control(1), geometry_control(2)],
                local_controls=controls, exact_complex_operator=complex_phase_control(),
                selected_direct_sum=frozen_lift(), full_triple_graph_screen=fano_screen(),
                optimistic_budgets=cases, hypothetical_profile=target,
                missing=['competitive block-label family and compatible complete local word',
                         'actual loss and split histogram, entrance gauges and all physical rewrites',
                         'complex isometry types and exact representatives for new labels',
                         'bit fallback, generic bases, primes, group stock, wrapper and analytic domain'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    result = encode(audit())
    if args.check:
        require(result == json.loads(args.check.read_text()), 'receipt mismatch')
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS block cover, full local/inverse controls, selected direct-sum invariance and target budget')
