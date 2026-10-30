"""Even-part rank tracker for Laurent controllers: paid odd shears versus twisted outputs.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.

Model (one central port).  Bank i starts with the formal symbol b_i.  Contents are elements of
R = K[Q, Q^-1] (x) K[stage markers]; a term is keyed by (bank, Q-exponent, stage tuple).  The controller alphabet
(research/p104-productive-controller/caller.py) is replayed with the literal rational coefficients:

  free  : ADD with a scalar, SWAP, SIGNED_SWAP, Q_POWER +-2, IDLE (multiplies both banks of a pair by stage markers),
          the stage marker of a LOCAL;
  paid  : the odd shear of a LOCAL (y += Q^{-1} x, or x += -Q y backward) and of a QUERY_SHEAR.

Even part E of a bank = its terms with even Q-exponent, odd part O = the others.  Each free operation is an
invertible row operation of the matrix whose rows are the banks; it maps the even parts among themselves (even Q
powers and markers are even), so it preserves rank E.  A paid shear adds Q^{+-1} x to y: E_y += Q^{+-1} O_x, a
change of one row, so rank E drops by at most one; before the first paid shear every O_x is zero, so the first
paid shear does not change rank E at all.  The outputs are the rows of L.M (L the constant left boundary); a
twisted output row l_i.M has zero even part, so l_i lies in the left kernel of E, and the twisted outputs being
independent monomials, these l_i are independent (L need not be invertible).  Hence with s paid shears and n_odd
twisted outputs,

    n_odd  <=  32 - rank E_final  <=  s - 1 .

The tracker evaluates rank over K after the homomorphism markers -> 1, Q^2 -> theta (nonzero scalar); the three
properties above (free operations preserve rank, a paid shear changes one row, twisted rows vanish) hold verbatim
in this image, so the per-event rank trace is a complete check of the argument on the given word.
"""
from fractions import Fraction as Q
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def plus(dst, src, c):
    for k, v in src.items():
        x = dst.get(k, 0) + c * v
        if x:
            dst[k] = x
        else:
            dst.pop(k, None)


def shiftq(vec, dq):
    return {(b, q + dq, m): v for (b, q, m), v in vec.items()}


def shiftm(vec, stages):
    out = {}
    for (b, q, m), v in vec.items():
        key = (b, q, tuple(sorted(set(m) | set(stages))))
        out[key] = out.get(key, 0) + v
    return {k: v for k, v in out.items() if v}


def even_coords(vec, theta):
    """K-coordinates of the even part after markers -> 1, Q^2 -> theta: key = bank."""
    out = {}
    for (b, q, m), v in vec.items():
        if q % 2 == 0:
            out[b] = out.get(b, 0) + v * theta ** (q // 2)
    return {k: v for k, v in out.items() if v}


def rank(rows):
    """Rank over K of a list of sparse vectors (dict key -> Fraction)."""
    basis = []
    for v in rows:
        v = dict(v)
        for key, row in basis:
            if key in v:
                c = v[key]
                for k2, x in row.items():
                    y = v.get(k2, 0) - c * x
                    if y:
                        v[k2] = y
                    else:
                        v.pop(k2, None)
        if v:
            key = min(v)
            c = 1 / v[key]
            basis.append((key, {k: x * c for k, x in v.items()}))
    return len(basis)


def is_odd_monomial(vec):
    """True if the content is a single term with odd Q-exponent."""
    return len(vec) == 1 and next(iter(vec))[1] % 2 == 1


def trace(events, banks_n, theta, boundaries=None, diagonal=None):
    """Replay one port.  Returns the receipt: per paid-shear rank of the even part, counts and the final test.

    boundaries: the controller's constant right/left matrices; the banks start as the rows of the right matrix and
    the left matrix is applied at the end (both free), after which every row must be the declared odd monomial."""
    theta = Q(theta)
    need(theta != 0, 'nonzero central square')
    if boundaries is None:
        banks = [{(i, 0, ()): Q(1)} for i in range(banks_n)]
    else:
        banks = [{(j, 0, ()): Q(x) for j, x in enumerate(row) if Q(x)} for row in boundaries['right']]
    E = lambda: rank([even_coords(b, theta) for b in banks])
    r0 = E()
    need(r0 == banks_n, 'initial even rank')
    ranks, paid, thick, thin = [r0], 0, 0, 0
    idle_stage_mass = 0
    for e in events:
        op = e[0]
        if op in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, back = e
            x, y = 2 * pair, 2 * pair + 1
            if back:
                x, y = y, x
            shear = shiftq(banks[x], 1 if back else -1)
            plus(banks[y], shear, Q(-1 if back else 1))
            paid += 1
            if op == 'LOCAL':
                thick += 1
                for r in (x, y):
                    banks[r] = shiftm(banks[r], [stage])
            else:
                thin += 1
            r = E()
            need(ranks[-1] - 1 <= r <= ranks[-1], 'a paid shear changes the even rank by at most one')
            if paid == 1:
                need(r == r0, 'the first paid shear leaves the even rank unchanged')
            ranks.append(r)
        elif op == 'Q_POWER':
            need(e[2] in (-2, 2), 'only even central powers are free')
            banks[e[1]] = shiftq(banks[e[1]], e[2])
        elif op == 'IDLE':
            for r in (2 * e[1], 2 * e[1] + 1):
                banks[r] = shiftm(banks[r], e[2])
            idle_stage_mass += 2 * len(e[2])
        elif op == 'ADD':
            plus(banks[e[1]], banks[e[2]], Q(e[3]))
        elif op in ('SWAP', 'SIGNED_SWAP'):
            a, b = banks[e[1]], banks[e[2]]
            banks[e[1]], banks[e[2]] = b, ({k: -v for k, v in a.items()} if op == 'SIGNED_SWAP' else a)
        else:
            raise ValueError('controller opcode ' + op)
        if op not in ('LOCAL', 'QUERY_SHEAR'):
            need(E() == ranks[-1], 'free operations preserve the even rank')
    even_zero = [i for i, b in enumerate(banks) if not even_coords(b, theta)]
    if boundaries is not None:
        out = []
        for row in boundaries['left']:
            v = {}
            for j, x in enumerate(row):
                if Q(x):
                    plus(v, banks[j], Q(x))
            out.append(v)
        banks = out
        need(E() == ranks[-1], 'the left boundary preserves the even rank')
    odd = [i for i, b in enumerate(banks) if is_odd_monomial(b)]
    if diagonal is not None:
        for i, b in enumerate(banks):
            (bank, qexp, stages), c = next(iter(b.items()))
            need(len(b) == 1 and c == 1 and bank == i and qexp == diagonal[i][0]
                 and stages == tuple(s for s, yes in enumerate(diagonal[i][1:]) if yes), 'declared diagonal output %d' % i)
    return {'theta': str(theta), 'banks': banks_n, 'paid_shears': paid, 'thick': thick, 'thin': thin,
            'even_rank_trace': ranks, 'final_even_rank': ranks[-1], 'twisted_outputs': len(odd),
            'even_zero_outputs': len(even_zero), 'bound_satisfied': len(odd) <= paid - 1,
            'idle_stage_mass_per_port': idle_stage_mass, 'final_banks': [sorted(str(k) for k in b) for b in banks]}


def income(word, fresh=8):
    """Controller mass surplus per port from the literal word: targets 1 + fresh*|S| minus every paid lift and
    thin request.  Lifts: fresh per bank per LOCAL (two banks) and per idle stage (two banks)."""
    targets = sum(1 + fresh * sum(t[1:]) for t in word['diagonal'])
    locals_ = sum(1 for e in word['physical_events'] if e[0] == 'LOCAL')
    thin = sum(1 for e in word['physical_events'] if e[0] == 'QUERY_SHEAR')
    idle = sum(2 * len(e[2]) for e in word['physical_events'] if e[0] == 'IDLE')
    lifts = fresh * (2 * locals_ + idle)
    # Lift cancellation, stage by stage (the determinant argument of PROOF.md): every row-lift by D_s multiplies
    # det by D_s and nothing else carries markers, so #{outputs containing s} must equal the row-lifts at s;
    # likewise sum of output Q-exponents = net Q_POWER exponent (shears have determinant 1).
    nstages = len(word['diagonal'][0]) - 1
    row_lifts = [0] * nstages
    net_q = 0
    for e in word['physical_events']:
        if e[0] == 'LOCAL':
            row_lifts[e[1]] += 2
        elif e[0] == 'IDLE':
            for s in e[2]:
                row_lifts[s] += 2
        elif e[0] == 'Q_POWER':
            net_q += e[2]
    output_stages = [sum(t[1 + s] for t in word['diagonal']) for s in range(nstages)]
    need(output_stages == row_lifts, 'every output stage is paid exactly once as a lift (stage by stage)')
    need(sum(t[0] for t in word['diagonal']) == net_q, 'sum of output Q-exponents equals the net Q_POWER exponent')
    left_rank = rank([{j: Q(x) for j, x in enumerate(row) if Q(x)} for row in word['boundaries']['left']])
    return {'targets_rank_sum': targets, 'outputs': len(word['diagonal']), 'locals': locals_, 'thin': thin,
            'idle_stage_mass': idle, 'paid_lifts': lifts, 'income': targets - lifts - thin,
            'outputs_minus_thin': len(word['diagonal']) - thin, 'stages': nstages,
            'row_lifts_per_stage': row_lifts, 'row_lifts_total': sum(row_lifts),
            'output_stage_count_equals_lifts': True, 'net_q_power': net_q, 'left_boundary_rank': left_rank}


def read(path):
    return json.loads(open(path).read())
