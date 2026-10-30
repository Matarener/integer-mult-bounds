"""One paid, two-invocation in-place encoding diagnostic. No new supplier.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    'higher_rank_budget', HERE.parent/'higher-rank-sixteenth/screen.py')
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)
require, rank, mm, encode = H.require, H.rank, H.mm, H.encode


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def zero(n):
    return [[Q(0) for _ in range(n)] for _ in range(n)]


def sub(a, b):
    return [[x-y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(c, a):
    return [[c*x for x in row] for row in a]


def add(a, b):
    return [[x+y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def inverse(a):
    n = len(a)
    rows = [list(map(Q, row))+tail for row, tail in zip(a, identity(n))]
    for c in range(n):
        pivot = next((i for i in range(c, n) if rows[i][c]), None)
        require(pivot is not None, 'invertible scalar prefix')
        rows[c], rows[pivot] = rows[pivot], rows[c]
        z = rows[c][c]
        rows[c] = [x/z for x in rows[c]]
        for i in range(n):
            if i != c:
                z = rows[i][c]
                rows[i] = [x-z*y for x, y in zip(rows[i], rows[c])]
    return [row[n:] for row in rows]


def tensor(a, b):
    return [[x*y for x in ra for y in rb] for ra in a for rb in b]


def blockdiag(blocks):
    n = sum(len(b) for b in blocks)
    out, offset = zero(n), 0
    for b in blocks:
        for i, row in enumerate(b):
            out[offset+i][offset:offset+len(b)] = row
        offset += len(b)
    return out


def line(slope):
    v = [Q(1), Q(slope)]
    return [[x*y/(1+slope*slope) for y in v] for x in v]


def labels(large=True):
    if large:
        # Rank-two, noncommuting axis labels in Q^4, then rank-four U in Q^16.
        p = [tensor(line(s), identity(2)) for s in (0, 1, -1)]
        U = [tensor(t, t) for t in p]
        E = [tensor(identity(4), t) for t in p]
    else:
        # Small exact finite-address control; not a target-capable supplier.
        U = [line(s) for s in (0, 1, -1)]
        E = [identity(2) for _ in U]
    m, n = len(U[0]), len(U)
    I = identity(m)
    matrices = {'0': zero(m), 'I': I}
    for i, (u, e) in enumerate(zip(U, E)):
        require(mm(u, u) == u and mm(e, e) == e, 'idempotent cuts')
        require(mm(u, e) == mm(e, u) == u, 'nested interstage cuts')
        matrices.update({f'U{i}': u, f'V{i}': sub(I, u),
                         f'E{i}': e, f'A{i}': sub(e, u)})
    require(mm(U[0], U[1]) != mm(U[1], U[0]), 'noncommuting labels')
    return dict(m=m, n=n, matrices=matrices,
                source=[f'U{i}' for i in range(n)]+['0']*n,
                middle=[f'E{i}' for i in range(n)]+[f'A{i}' for i in range(n)],
                sink=['I']*n+[f'V{i}' for i in range(n)])


def word(n=3, fused=True):
    require(n == 3, 'specified three-label experiment')
    out = []
    def enc(bank, family, inverse=False):
        pairs = [(1, 0), (2, 1)]
        if inverse:
            pairs.reverse()
        for target, control in pairs:
            out.append(dict(kind='gate', target=bank*n+target,
                            control=bank*n+control, sign=-1 if inverse else 1,
                            frame=f'{family}{target}'))
    def shear(second):
        for i in range(n):
            out.append(dict(kind='gate', target=i if second else n+i,
                            control=n+i if second else i,
                            sign=-1 if second else 1,
                            frame=f'{"V" if second else "U"}{i}'))
    enc(0, 'U'); enc(1, 'U'); shear(False)
    if not fused:
        enc(0, 'U', True); enc(1, 'U', True)
        out.append(dict(kind='cut', name='middle'))
        enc(0, 'V'); enc(1, 'V')
    shear(True); enc(0, 'V', True); enc(1, 'V', True)
    out.append(dict(kind='cut', name='sink'))
    return out


def scalar_matrix(ops, n, binary=False):
    A = identity(2*n)
    for op in ops:
        if op['kind'] != 'gate':
            continue
        t, c = op['target'], op['control']
        A[t] = [x+op['sign']*y for x, y in zip(A[t], A[c])]
        if binary:
            A[t] = [Q(int(x) % 2) for x in A[t]]
    return A


def expected_scalar(n, binary=False):
    A = zero(2*n)
    for i in range(n):
        A[i][n+i] = 1 if binary else -1
        A[n+i][i] = A[n+i][n+i] = 1
    return A


def paid_ledger(model, ops):
    current = model['source'].copy()
    hist, edges = Counter(), []
    F, m, n = model['matrices'], model['m'], model['n']
    for event, op in enumerate(ops):
        changes = ([(op['target'], op['frame']), (op['control'], op['frame'])]
                   if op['kind'] == 'gate' else list(enumerate(model[op['name']])))
        for role, dest in changes:
            source = current[role]
            r = rank(sub(F[dest], F[source]))
            if r:
                hist[r] += 1
            edges.append(dict(event=event, role=role, source=source, dest=dest, rank=r))
            current[role] = dest
    require(current == model['sink'], 'sink cut')
    correction = Counter(rank(F[f'U{i}']) for i in range(n))
    corrected = hist+correction
    def favorable_moment(rows, saving):
        # Full-width children are granted contribution one FOR REJECTION.
        # They are not admitted into a strictly reducing production recurrence.
        full = rows.get(m, 0)
        proper = {t: count for t, count in rows.items() if t < m}
        require(all(0 < t <= m for t in rows), 'width range')
        lo, hi = H.moment(proper, m, 2*n, saving)
        return [lo+Q(full, 2*n), hi+Q(full, 2*n)]
    return dict(independent_roles=2*n, dimension=m, edges=edges,
                scalar_gate_count=sum(op['kind'] == 'gate' for op in ops),
                pre_correction_histogram=dict(sorted(hist.items())),
                correction_histogram=dict(sorted(correction.items())),
                full_histogram=dict(sorted(corrected.items())),
                pre_correction_rank=sum(t*c for t, c in hist.items()),
                full_rank=sum(t*c for t, c in corrected.items()), capacity=2*n*m,
                target_bit_moment=favorable_moment(corrected, Q(2, 25)),
                target_complex_moment_arithmetic_only=favorable_moment(corrected, Q(3, 40)))


def discrepancy(model, C):
    F, m = model['matrices'], model['m']
    Min = blockdiag([F[f] for f in model['source']])
    Mout = blockdiag([F[f] for f in model['sink']])
    lift = tensor(C, identity(m))
    D = sub(mm(Mout, lift), mm(lift, Min))
    return D


def telescope_control(model, ops):
    """Replay every edge influence, not only the endpoint rank formula."""
    n, m = model['n'], model['m']
    C = scalar_matrix(ops, n)
    prefix = identity(2*n)
    current = model['source'].copy()
    total = zero(2*n*m)
    ranks, terms = [], 0
    for op in ops:
        changes = ([(op['target'], op['frame']), (op['control'], op['frame'])]
                   if op['kind'] == 'gate' else list(enumerate(model[op['name']])))
        for role, dest in changes:
            diff = sub(model['matrices'][dest], model['matrices'][current[role]])
            r = rank(diff)
            if r:
                suffix = mm(C, inverse(prefix))
                influence = [[suffix[i][role]*prefix[role][j] for j in range(2*n)]
                             for i in range(2*n)]
                term = tensor(influence, diff)
                require(rank(term) <= r, 'edge contribution rank')
                total = add(total, term)
                ranks.append(r)
                terms += 1
            current[role] = dest
        if op['kind'] == 'gate':
            t, c = op['target'], op['control']
            require(current[t] == current[c] == op['frame'], 'common gate frame')
            prefix[t] = [x+op['sign']*y for x, y in zip(prefix[t], prefix[c])]
    require(total == discrepancy(model, C), 'complete edge telescoping identity')
    require(prefix == C, 'prefix scalar replay')
    return dict(edge_terms=terms, edge_rank_sum=sum(ranks),
                discrepancy_rank=rank(total), dimension=2*n*m,
                exact_matrix_identity=True)


def budget_allowance(d, r, saving):
    bare = H.block_budget(d, r, saving, Q(0))
    Mlo, Mhi = bare['moment_interval']
    Alo, Ahi = bare['added_role_moment_interval']
    require(Mhi < 1 and Alo > 1, 'positive preliminary allowance')
    # (2*M + 2*rho*A + E)/(2+2*rho) < 1.
    # E is additional unnormalized moment per data pair.
    return dict(d=d, r=r, saving=saving,
                zero_role_extra_moment_allowance=[2*(1-Mhi), 2*(1-Mlo)],
                maximum_role_ratio_at_zero_extra_cost=[(1-Mhi)/(Ahi-1),
                                                       (1-Mlo)/(Alo-1)],
                tradeoff='2*rho*(A-1)+E < 2*(1-M_bare)',
                status='Necessary budget only; no geometry or compiler supplied.')


def address_matrix(P):
    I = identity(len(P))
    C = sub(I, P)
    return [a+b for a, b in zip(C, P)]+[a+b for a, b in zip(P, C)]


def finite_address_check(ops, correction=True, skip_transition=None):
    model = labels(False)
    m, n, prime = model['m'], model['n'], 3
    addresses = list(product(range(prime), repeat=2*m))
    index = {a: i for i, a in enumerate(addresses)}
    size = len(addresses)
    perms = {}
    for name, P in model['matrices'].items():
        D = address_matrix(P)
        residues = [[int(x.numerator*pow(x.denominator, -1, prime) % prime)
                     for x in row] for row in D]
        perm = [index[tuple(sum(x*y for x, y in zip(row, a)) % prime
                            for row in residues)] for a in addresses]
        require(len(set(perm)) == size, 'invertible finite address frame')
        require(all(perm[perm[i]] == i for i in range(size)), 'frame involution')
        perms[name] = perm
    values = [[1 << (role*size+i) for i in range(size)] for role in range(2*n)]
    initial = [row.copy() for row in values]
    current = model['source'].copy()
    def move(v, frame):
        w = [0]*size
        for i, j in enumerate(perms[frame]):
            w[j] = v[i]
        return w
    transitions = 0
    for op in ops:
        changes = ([(op['target'], op['frame']), (op['control'], op['frame'])]
                   if op['kind'] == 'gate' else list(enumerate(model[op['name']])))
        for role, dest in changes:
            if current[role] != dest:
                if transitions != skip_transition:
                    values[role] = move(move(values[role], current[role]), dest)
                transitions += 1
                current[role] = dest
        if op['kind'] == 'gate':
            t, c = op['target'], op['control']
            values[t] = [x^y for x, y in zip(values[t], values[c])]
    if correction:
        for i in range(n):
            temp = move(values[i], f'U{i}')
            values[n+i] = [x^y for x, y in zip(values[n+i], temp)]
            # temp is a dependent copy; it is discarded, never an input role.
    expected = [move(initial[n+i], 'I') for i in range(n)]
    expected += [move(initial[i], 'I') for i in range(n)]
    wrong = sum(x != y for row, out in zip(values, expected) for x, y in zip(row, out))
    return dict(prime=prime, address_dimension=2*m, addresses=size,
                independent_input_bits=2*n*size, wrong_output_forms=wrong,
                transitions=transitions)


def audit():
    model = labels(True)
    small = labels(False)
    fused, separate = word(fused=True), word(fused=False)
    ledgers = {}
    for name, ops in [('fused', fused), ('separate', separate)]:
        for binary in (True, False):
            require(scalar_matrix(ops, 3, binary) == expected_scalar(3, binary),
                    name+' scalar endpoint')
        paid = paid_ledger(model, ops)
        require(paid['pre_correction_rank'] >= paid['capacity'], 'rank rejection')
        require(paid['target_bit_moment'][0] > 1, 'moment rejection')
        ledgers[name] = paid
        require(finite_address_check(ops)['wrong_output_forms'] == 0, 'physical endpoint')
    flat = [dict(op, frame='0') if op['kind'] == 'gate' else op.copy() for op in fused]
    flat_ledger = paid_ledger(model, flat)
    require(flat_ledger['pre_correction_rank'] == flat_ledger['capacity'],
            'sharp rank lower bound control')
    require(finite_address_check(flat)['wrong_output_forms'] == 0, 'flat frame endpoint')
    ledgers['zero_frame_sharpness_control'] = flat_ledger
    C = expected_scalar(3)
    D = discrepancy(small, C)
    require(rank(D) == 12, 'full nonpermutation endpoint discrepancy')
    for i in range(3):
        R = sub(identity(16), scale(2, model['matrices'][f'U{i}']))
        require(mm(R, R) == identity(16), 'reflection inverse')
    negative = dict(no_correction=finite_address_check(fused, correction=False),
                    missing_transition=finite_address_check(fused, skip_transition=0))
    # Delete a decoder gate, not just an address operation.
    broken = fused.copy()
    del broken[-2]
    negative['missing_decoder_gate'] = finite_address_check(broken)
    require(all(x['wrong_output_forms'] > 0 for x in negative.values()), 'adverse controls')
    sources = ['research/higher-rank-sixteenth/screen.py',
               'research/higher-rank-sixteenth/REPORT.md',
               'research/computation-fusion-nine/REPORT.md',
               'docs/research/stronger-rank-screens.md',
               'references/copied-centers/pr29/two-stage-16-note.tex']
    return dict(status='REJECT MATCHED IN-PLACE ENCODING FAMILY; NO NEW SUPPLIER',
                source_pins={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
                budget_allowances=[budget_allowance(d, r, s) for d, r in ((11, 5), (2, 1))
                                   for s in (Q(2, 25), Q(3, 40))],
                frame_matrices=model['matrices'], fused_word=fused, separate_word=separate,
                paid_comparison=ledgers, small_address_control=finite_address_check(fused),
                adverse_controls=negative,
                small_signed_lift=C, small_endpoint_discrepancy=D,
                small_discrepancy_rank=rank(D),
                telescoping_control=telescope_control(small, fused),
                general_rejection='For any matched reversible encoder with a rational lift, '
                                  'the two-shear word has lift (x,y)->(-y,x+y). '
                                  'At cuts (U,0)->(I,I-U), discrepancy per pair is '
                                  '[[0,-I],[I-2U,I-U]], full rank 2m. '
                                  'Every charged frame-edge rank sum is therefore >=2Nm.',
                scope='Full-volume rational projector-difference edge costs, common gate frames, '
                      'matched in-place encoding and decoding, and the retained outer cuts. '
                      'No exclusion of characteristic-dependent unmatched circuits or changed cuts.',
                complex_status='No complex supplier constructed; bit rejection already stops this model.')


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
    print('PASS paid two-invocation word, exact arbitrary-input endpoint, and rational-lift rejection')
