"""Independent audit engine for PR6114's controller income bound.

Written from the event semantics of research/p104-productive-controller/caller.py
without importing it or PR6114's incomebound.py. Standard library only.
Josie Elliston with Claude Code (Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as F
import random

NS = 33  # stage markers D_0 .. D_32 (caller.py: 1 Q exponent + 33 stage exponents)


# ---------------------------------------------------------------- linear algebra
def rank(rows):
    """Exact rank over Q of a list of Fraction vectors."""
    m = [list(r) for r in rows if any(r)]
    rk, col = 0, 0
    ncol = len(m[0]) if m else 0
    while rk < len(m) and col < ncol:
        piv = next((i for i in range(rk, len(m)) if m[i][col]), None)
        if piv is None:
            col += 1
            continue
        m[rk], m[piv] = m[piv], m[rk]
        p = m[rk][col]
        for i in range(rk + 1, len(m)):
            if m[i][col]:
                f = m[i][col] / p
                m[i] = [x - f * y for x, y in zip(m[i], m[rk])]
        rk += 1
        col += 1
    return rk


def run_program(program, n):
    m = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    for e in program:
        if e[0] == 'SWAP':
            m[e[1]], m[e[2]] = m[e[2]], m[e[1]]
        elif e[0] == 'SCALE':
            m[e[1]] = [F(e[2]) * x for x in m[e[1]]]
        elif e[0] == 'ADD':
            m[e[1]] = [x + F(e[3]) * y for x, y in zip(m[e[1]], m[e[2]])]
        else:
            raise ValueError('boundary opcode ' + repr(e[0]))
    return m


# ---------------------------------------------------------------- exact Laurent replay
def padd(dst, src, c, shift):
    for k, v in src.items():
        kk = tuple(a + b for a, b in zip(k, shift))
        w = dst.get(kk, F(0)) + c * v
        if w:
            dst[kk] = w
        else:
            dst.pop(kk, None)


def exact_replay(word):
    """Symbolic replay over Q[Q^{+-1}, D_0..D_32]; returns output matrix and counters."""
    n = 2 * word['pairs']
    zero = (0,) * (1 + NS)
    unit = lambda q=0, stages=(): (q,) + tuple(int(s in stages) for s in range(NS))
    rows = [[({zero: F(x)} if F(x) else {}) for x in r] for r in word['boundaries']['right']]

    def scaled(i, shift, sign=1):
        rows[i] = [{tuple(a + b for a, b in zip(k, shift)): sign * v for k, v in cell.items()} for cell in rows[i]]

    cnt = {'LOCAL': 0, 'QUERY_SHEAR': 0, 'lifts': 0, 'qpower': 0}
    for e in word['physical_events']:
        op = e[0]
        if op in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, back = e
            src, dst = (2 * pair + 1, 2 * pair) if back else (2 * pair, 2 * pair + 1)
            shift, c = (unit(1), F(-1)) if back else (unit(-1), F(1))
            new = [dict(cell) for cell in rows[dst]]
            for d, s in zip(new, rows[src]):
                padd(d, s, c, shift)
            rows[dst] = new
            cnt[op] += 1
            if op == 'LOCAL':
                for r in (2 * pair, 2 * pair + 1):
                    scaled(r, unit(0, (stage,)))
                cnt['lifts'] += 2
        elif op == 'Q_POWER':
            if e[2] not in (-2, 2):
                raise ValueError('odd central power is not free')
            scaled(e[1], unit(e[2]))
            cnt['qpower'] += e[2]
        elif op == 'IDLE':
            # caller.py replay() reads the stage list as a set; its physical() rejects repeats, as here
            if len(set(e[2])) != len(e[2]):
                raise ValueError('repeated idle stage')
            for r in (2 * e[1], 2 * e[1] + 1):
                scaled(r, unit(0, tuple(e[2])))
            cnt['lifts'] += 2 * len(e[2])
        elif op == 'ADD':
            new = [dict(cell) for cell in rows[e[1]]]
            for d, s in zip(new, rows[e[2]]):
                padd(d, s, F(e[3]), zero)
            rows[e[1]] = new
        elif op in ('SWAP', 'SIGNED_SWAP'):
            a, b = e[1], e[2]
            ra, rb = rows[a], rows[b]
            rows[a] = rb
            rows[b] = ra
            if op == 'SIGNED_SWAP':
                scaled(b, zero, -1)
        else:
            raise ValueError('opcode ' + repr(op))
    out = [[{} for _ in range(n)] for _ in range(n)]
    for i, lrow in enumerate(word['boundaries']['left']):
        for k, q in enumerate(lrow):
            if F(q):
                for j in range(n):
                    padd(out[i][j], rows[k][j], F(q), zero)
    return out, cnt


# ---------------------------------------------------------------- specialized even/odd tracker
class Image:
    """Image under Q^2 -> theta, D_s -> r_s: each bank row is a + Q b with a, b in Q^n."""

    def __init__(self, entry_even, entry_odd, theta, r):
        self.a = [list(x) for x in entry_even]
        self.b = [list(x) for x in entry_odd]
        self.t, self.r = F(theta), [F(x) for x in r]

    def even_rank(self):
        return rank(self.a)

    def add(self, y, x, c, qexp=0):
        """row_y += c * Q^qexp * row_x, qexp in {-1, 0, 1}."""
        ax, bx = self.a[x], self.b[x]
        if qexp == 0:
            da, db = ax, bx
        elif qexp == 1:   # Q(a + Qb) = theta b + Q a
            da, db = [self.t * v for v in bx], ax
        elif qexp == -1:  # Q^-1(a + Qb) = b + Q a/theta
            da, db = bx, [v / self.t for v in ax]
        else:
            raise ValueError(qexp)
        self.a[y] = [u + c * v for u, v in zip(self.a[y], da)]
        self.b[y] = [u + c * v for u, v in zip(self.b[y], db)]

    def scale(self, i, s):
        self.a[i] = [s * v for v in self.a[i]]
        self.b[i] = [s * v for v in self.b[i]]

    def times_q(self, i, sign=1):
        """row_i *= sign * Q (a paid odd translation; not in the literal alphabet)."""
        a, b = self.a[i], self.b[i]
        self.a[i] = [sign * self.t * v for v in b]
        self.b[i] = [sign * v for v in a]


def image_trace(word, theta, r):
    """Even-part rank after every event; returns (trace at shears, per-event deltas by kind)."""
    n = 2 * word['pairs']
    R = [[F(x) for x in row] for row in word['boundaries']['right']]
    im = Image(R, [[F(0)] * n for _ in range(n)], theta, r)
    trace = [im.even_rank()]
    free_changes, shear_deltas = 0, []
    for e in word['physical_events']:
        op = e[0]
        before = trace[-1]
        if op in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, back = e
            src, dst = (2 * pair + 1, 2 * pair) if back else (2 * pair, 2 * pair + 1)
            if back:
                im.add(dst, src, F(-1), 1)
            else:
                im.add(dst, src, F(1), -1)
            if op == 'LOCAL':
                for q in (2 * pair, 2 * pair + 1):
                    im.scale(q, im.r[stage])
        elif op == 'Q_POWER':
            im.scale(e[1], im.t if e[2] == 2 else 1 / im.t)
        elif op == 'IDLE':
            s = F(1)
            for st in e[2]:
                s *= im.r[st]
            for q in (2 * e[1], 2 * e[1] + 1):
                im.scale(q, s)
        elif op == 'ADD':
            im.add(e[1], e[2], F(e[3]))
        else:
            a, b = e[1], e[2]
            im.a[a], im.a[b] = im.a[b], im.a[a]
            im.b[a], im.b[b] = im.b[b], im.b[a]
            if op == 'SIGNED_SWAP':
                im.scale(b, F(-1))
        now = im.even_rank()
        if op in ('LOCAL', 'QUERY_SHEAR'):
            shear_deltas.append(now - before)
            trace.append(now)
        elif now != before:
            free_changes += 1
        trace[-1] = now
    L = [[F(x) for x in row] for row in word['boundaries']['left']]
    out_even = [[sum(L[i][k] * im.a[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    return trace, shear_deltas, free_changes, out_even


def random_rationals(rng, k):
    vals = []
    while len(vals) < k:
        v = F(rng.randint(-29, 29), rng.randint(1, 17))
        if v:
            vals.append(v)
    return vals


# ---------------------------------------------------------------- scope controls (small n)
def laurent_entry_control():
    """Entry rows x = e1 - Q e2, y = e2 (a Laurent, non-constant boundary).
    Two shears (y += Q^-1 x, then x += -Q y) give two odd monomial rows."""
    theta = F(7, 3)
    im = Image([[F(1), F(0)], [F(0), F(1)]], [[F(0), F(-1)], [F(0), F(0)]], theta, [])
    r0 = im.even_rank()
    im.add(1, 0, F(1), -1)
    im.add(0, 1, F(-1), 1)
    rows = [(im.a[i], im.b[i]) for i in range(2)]
    odd_monomials = all(not any(a) and sum(1 for v in b if v) == 1 for a, b in rows)
    return {'entry_even_rank': r0, 'paid_shears': 2, 'odd_monomial_rows': 2 if odd_monomials else None,
            'final_rows': [[str(v) for v in a] + [str(v) for v in b] for a, b in rows],
            'exceeds_constant_entry_bound': odd_monomials and 2 > 2 - 1}


def odd_translation_control():
    """One paid odd translation row *= Q from a constant entry twists one output with s = 1."""
    im = Image([[F(1), F(0)], [F(0), F(1)]], [[F(0)] * 2, [F(0)] * 2], F(11, 5), [])
    im.times_q(0)
    return {'paid_jobs': 1, 'odd_rows': sum(1 for i in range(2) if not any(im.a[i]) and any(im.b[i])),
            'final_even_rank': im.even_rank()}


def two_row_job_control():
    """One paid job writing both rows of a pair (the composite of the three Whitehead shears)
    from a constant entry: two odd rows with one paid job."""
    im = Image([[F(1), F(0)], [F(0), F(1)]], [[F(0)] * 2, [F(0)] * 2], F(13, 7), [])
    before = im.even_rank()
    im.add(1, 0, F(1), -1)
    im.add(0, 1, F(-1), 1)
    im.add(1, 0, F(1), -1)
    return {'paid_jobs': 1, 'even_rank_before': before, 'even_rank_after': im.even_rank(),
            'odd_rows': sum(1 for i in range(2) if not any(im.a[i]) and any(im.b[i]))}


def one_destination_random(seed, words, n, length):
    """Random words: free events (constant ADD, swap, even scalings) and paid one-destination jobs
    row_y = u row_y + sum_j f_j row_j with u a nonzero even scalar and f_j = c0 + c1 Q + c2 Q^-1.
    Checks every paid job changes the even rank by at most one, the first by zero, and free events by zero."""
    rng = random.Random(seed)
    worst, jobs_total, drops, tight = None, 0, 0, 0
    for _ in range(words):
        theta = F(rng.choice([2, 3, 5, 7, 11, 13]), rng.choice([1, 3, 5, 7]))
        R = [[F(rng.randint(-3, 3)) for _ in range(n)] for _ in range(n)]
        while rank(R) < n:
            R = [[F(rng.randint(-3, 3)) for _ in range(n)] for _ in range(n)]
        im = Image(R, [[F(0)] * n for _ in range(n)], theta, [])
        rk, paid, first = n, 0, True
        for _ in range(length):
            kind = rng.random()
            if kind < 0.5:
                y = rng.randrange(n)
                if rng.random() < 0.7:  # literal-type shear: one source, coefficient Q^-1 or -Q
                    j = rng.choice([j for j in range(n) if j != y])
                    if rng.random() < 0.5:
                        im.add(y, j, F(1), -1)
                    else:
                        im.add(y, j, F(-1), 1)
                else:
                    srcs = rng.sample([j for j in range(n) if j != y], rng.randint(1, min(3, n - 1)))
                    im.scale(y, F(rng.choice([1, -1, 2, -3])) * (theta ** rng.choice([-1, 0, 1])))
                    # simultaneous update: read sources before writing (sources exclude y)
                    for j in srcs:
                        for qexp in (-1, 0, 1):
                            c = F(rng.randint(-2, 2))
                            if c:
                                im.add(y, j, c, qexp)
                now = im.even_rank()
                if now < rk - 1 or now > rk + 1 or (first and now != rk):
                    raise AssertionError('one-destination job moved even rank by more than allowed')
                drops += rk - now if now < rk else 0
                rk, paid, first = now, paid + 1, False
            else:
                y, x = rng.sample(range(n), 2)
                if kind < 0.8:
                    im.add(y, x, F(rng.choice([1, -1, 2])))
                elif kind < 0.9:
                    im.a[y], im.a[x] = im.a[x], im.a[y]
                    im.b[y], im.b[x] = im.b[x], im.b[y]
                else:
                    im.scale(y, theta if rng.random() < 0.5 else F(rng.choice([2, -1])))
                now = im.even_rank()
                if now != rk:
                    raise AssertionError('free event changed even rank')
        zero_rows = n - rk  # upper bound on odd outputs after any constant left boundary
        if paid and zero_rows > paid - 1:
            raise AssertionError('bound violated')
        if paid:
            worst = zero_rows - (paid - 1) if worst is None else max(worst, zero_rows - (paid - 1))
        tight += int(paid > 0 and zero_rows == paid - 1)
        jobs_total += paid
    return {'words': words, 'banks': n, 'length': length, 'paid_jobs_total': jobs_total,
            'even_rank_drops_total': drops, 'words_even_rank_deficit_equals_bound': tight,
            'max_excess_over_bound': worst}
