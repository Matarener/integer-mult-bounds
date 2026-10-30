"""Exact root bracket of the bit price on a paid child histogram (brief cross-check; cf. PR #3668).

Price equation, as stated by the selected chain's moment engine on main
(research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py), with
the inherited 10^-16 bad-class fallback:
    sum_r (r n_r)/(m W) (m/r)^a + (32 m N)/(10^16 W) m^a = 1,   N = sum_r n_r.
c is the largest 10^-24 grid point below the root.  The bounds below are separate rational
enclosures: atanh series for log with a geometric tail, Taylor series for exp with its tail.
"""
from fractions import Fraction as Q


def ln_bounds(x):
    """Rational lower/upper bounds of ln(x) for rational x >= 1."""
    assert x >= 1
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def atanh2(y):
        z = (y - 1) / (y + 1)
        s, t = Q(0), z
        for j in range(80):
            s += t / (2 * j + 1)
            t *= z * z
        return 2 * s, 2 * (s + t / (161 * (1 - z * z)))
    lo, hi = atanh2(x)
    l2, u2 = atanh2(Q(2))
    return lo + k * l2, hi + k * u2


def exp_bounds(x):
    assert 0 <= x < 1
    s = t = Q(1)
    for j in range(1, 30):
        t = t * x / j
        s += t
    return s, s + t * x / 30 / (1 - x / 31)


def moment(hist, m, W, a):
    lo = hi = Q(0)
    N = sum(hist.values())
    terms = [(Q(r * n, m * W), Q(m, r)) for r, n in hist.items()] + [(Q(32 * m * N, 10**16 * W), Q(m))]
    for p, base in terms:
        l, u = ln_bounds(base)
        lo += p * exp_bounds(a * l)[0]
        hi += p * exp_bounds(a * u)[1]
    return lo, hi


def bracket(hist, m, W, c):
    lo_at_c = moment(hist, m, W, c)
    next_grid = c + Q(1, 10**24)
    at_next = moment(hist, m, W, next_grid)
    return dict(c=str(c), next_grid=str(next_grid), moment_upper_at_c_below_one=lo_at_c[1] < 1,
                moment_lower_at_next_grid_above_one=at_next[0] > 1)


def precision(cf, cb, children, maxchild, R, v=111, K=4, L=9, T=32, m=64, W=28416, local_adds=0):
    """Precision fields of the inherited nine-stage invoice (main: global_k.py prefix bound and
    #510 assemble9.py coefficient formula), as an envelope: every non-prefix term is bounded above
    generously (route factors up to 2^40, ports up to 120, doubled), so the reported bit lengths
    hold for any such values.  The ROW constants 9909 + 252 and the ROW cap 20161 (assemble9.py)
    are inherited, not derived here.  The local payload-prefix cap 64 cf^3 cb^2 < 2^104 is the
    one in the selected chain's columns_h.cpp/columns_k.cpp checkers."""
    prefix = 2 ** (6 * (K - 1)) * cf ** (K + 1) * cb ** K
    depth = 1
    while not 2 * maxchild ** depth < m ** depth:
        depth += 1

    def others(V, route):
        unit = L * T * local_adds + 6 * (K - 1) * V * T
        cee = 9 * L * T
        J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * L * T * R + 2 * cee
        high = 16 * (m * m + 1) ** 2
        selectors = 2 * L * T * ((W - 1) + R * m * (route + 144 + 2 + (m - 1) + m))
        return (unit + J * high + J * (W + 9) + children * (8 * m * m + 8 + 128 * (2 * m) ** 3)
                + 16 * m ** 3 + cee + selectors + 1)
    lo = prefix + others(v, 0)
    hi = prefix + 2 * others(120, 2 ** 40)
    two_lo = (lo + 1) ** depth * (children + 1) ** depth
    two_hi = (hi + 1) ** depth * (children + 1) ** depth
    pb = prefix.bit_length()
    payload = 64 * cf ** 3 * cb ** 2
    row = depth * (m * m + 1) + 9909 + 252
    return dict(payload_prefix_bits=payload.bit_length(), payload_below_2_104=payload < 2 ** 104,
                prefix_bits=pb, charged_prefix_bits=192 if pb <= 192 else 64 * ((pb + 63) // 64),
                coefficient_bits=[lo.bit_length(), hi.bit_length()],
                two_level_bits=[two_lo.bit_length(), two_hi.bit_length()],
                charged_two_level_bits=512 if two_hi.bit_length() <= 512 else None,
                halving_depth=depth, halving_inequality=[2 * maxchild ** depth, m ** depth],
                row_coefficient=row, row_below_inherited_cap_20161=row < 20161)
