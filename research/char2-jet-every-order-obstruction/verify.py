"""Integer flow certificates: the char-2 jet obstruction of jf0, jf1, jf2 holds at every order.

For each harmonic line h of the three no-wild configurations of research/char2-jets that is
immovable at first order, this script finds and checks an integer relation

    m_h * prod_{e in Z} m_e^{c_e} = 1,    c_e in {+1, -1},

between Laurent monomials m_e = P_i(t) Q_i(s) / (P_j(t) Q_j(s)), where e = (t, s) runs over
incidences of the full pattern and {i, j} = pi(t) & sigma(s), i < j.  See README.md for the
theorem this identity proves.

Default mode recomputes every certificate from the pinned configurations, compares it with
CERTIFICATE.json and runs the controls.  `--write` regenerates CERTIFICATE.json.
Standard library only.
"""
import json
import os
import random
import sys
from fractions import Fraction

PKG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(PKG))
DATA = os.path.join(ROOT, "research", "char2-jets", "data")
CERT = os.path.join(PKG, "CERTIFICATE.json")
NAMES = ("jf0", "jf1", "jf2")
# Immovable lines reported by research/char2-jets README section 5.
EXPECTED_IMMOVABLE = {"jf0": [0], "jf1": [7], "jf2": [0, 2]}
SERIES_ORDER = 24          # truncation of F2[[eps]] in the valuation control
RANDOM_TRIALS = 200


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def load(name):
    with open(os.path.join(DATA, name + ".json")) as f:
        d = json.load(f)
    P, Q = d[0], d[1]
    assert len(P) == len(Q) and all(len(x) == 3 for x in P + Q)
    return P, Q


class Config:
    """Supports, incidences, harmonic lines and exponent vectors of one configuration."""

    def __init__(self, P, Q):
        self.P, self.Q, self.v = P, Q, len(P)
        v = self.v
        self.pi = [frozenset(j for j in range(3) if P[t][j]) for t in range(v)]
        self.sg = [frozenset(j for j in range(3) if Q[t][j]) for t in range(v)]
        for t in range(v):
            assert dot(P[t], Q[t]) != 0, "diagonal must be nonzero"
        self.inc = [(t, s) for t in range(v) for s in range(v)
                    if t != s and dot(P[t], Q[s]) == 0 and self.pi[t] & self.sg[s]]
        for t, s in self.inc:
            assert len(self.pi[t] & self.sg[s]) == 2, "wild incidence: outside the no-wild scope"
        self.harm = [t for t in range(v) if self._harmonic(t)]
        self.var = {}
        for t in range(v):
            for j in sorted(self.pi[t]):
                self.var[("p", t, j)] = len(self.var)
            for j in sorted(self.sg[t]):
                self.var[("q", t, j)] = len(self.var)

    def _harmonic(self, t):
        D = self.pi[t] & self.sg[t]
        if len(D) != 2:
            return False
        i, j = sorted(D)
        return self.P[t][i] * self.Q[t][i] == self.P[t][j] * self.Q[t][j]

    def pair(self, t, s):
        i, j = sorted(self.pi[t] & self.sg[s])
        return i, j

    def vec(self, t, s):
        """Exponent vector of m_(t,s) = P_i(t) Q_i(s) / (P_j(t) Q_j(s))."""
        i, j = self.pair(t, s)
        x = [0] * len(self.var)
        x[self.var[("p", t, i)]] += 1
        x[self.var[("p", t, j)]] -= 1
        x[self.var[("q", s, i)]] += 1
        x[self.var[("q", s, j)]] -= 1
        return x


def f2_member(cols, target):
    """Is target in the F2-span of cols?  (Lemma F's first-order immovability test.)"""
    piv = []
    for c in cols:
        x = sum((a & 1) << i for i, a in enumerate(c))
        for p in piv:
            x = min(x, x ^ p)
        if x:
            piv.append(x)
            piv.sort(reverse=True)
    y = sum((a & 1) << i for i, a in enumerate(target))
    for p in piv:
        y = min(y, y ^ p)
    return y == 0


def val2(x):
    """2-adic valuation of a nonzero rational."""
    n, d, k = x.numerator, x.denominator, 0
    while n % 2 == 0:
        n //= 2
        k += 1
    while d % 2 == 0:
        d //= 2
        k -= 1
    return k


def local_solve(cols, target):
    """Solve sum_k c_k cols[k] = target with c in Z_(2) (odd denominators), or return None.

    Column elimination over the discrete valuation ring Z_(2): the pivot in each row has minimal
    2-adic valuation, so every elimination factor stays in Z_(2).
    """
    n, m = len(target), len(cols)
    A = [[Fraction(cols[k][r]) for k in range(m)] for r in range(n)]
    T = [[Fraction(int(i == k)) for k in range(m)] for i in range(m)]
    remaining, pivot_of_row = list(range(m)), {}
    for r in range(n):
        cand = [k for k in remaining if A[r][k] != 0]
        if not cand:
            continue
        c = min(cand, key=lambda k: val2(A[r][k]))
        remaining.remove(c)
        pivot_of_row[r] = c
        for k in cand:
            if k == c:
                continue
            f = A[r][k] / A[r][c]
            assert val2(f) >= 0
            for rr in range(n):
                A[rr][k] -= f * A[rr][c]
            for i in range(m):
                T[i][k] -= f * T[i][c]
    x, coef = [Fraction(a) for a in target], [Fraction(0)] * m
    for r in range(n):
        if r in pivot_of_row:
            c = pivot_of_row[r]
            f = x[r] / A[r][c]
            if f != 0 and val2(f) < 0:
                return None
            coef[c] += f
            for rr in range(n):
                x[rr] -= f * A[rr][c]
        elif x[r] != 0:
            return None
    return [sum(T[i][k] * coef[k] for k in range(m)) for i in range(m)]


def find_certificates(name):
    cfg = Config(*load(name))
    cols = [cfg.vec(t, s) for t, s in cfg.inc]
    out, movable = [], []
    for h in cfg.harm:
        vh = cfg.vec(h, h)
        if not f2_member(cols, vh):
            movable.append(h)
            continue
        sol = local_solve(cols, [-a for a in vh])
        assert sol is not None, "%s line %d: immovable mod 2 but no 2-local integer lift" % (name, h)
        assert all(c.denominator == 1 and c in (-1, 0, 1) for c in sol), "non-unit lift"
        edges = [{"t": t, "s": s, "pair": list(cfg.pair(t, s)), "c": int(c)}
                 for (t, s), c in zip(cfg.inc, sol) if c]
        out.append({"line": h, "pair": list(cfg.pair(h, h)), "edges": edges})
    return cfg, out, movable


def check_identity(cfg, cert):
    """Exact integer check: v_h + sum c_e v_e = 0, every edge a genuine binomial incidence."""
    h = cert["line"]
    assert h in cfg.harm
    total = cfg.vec(h, h)
    assert list(cfg.pair(h, h)) == cert["pair"]
    inc = set(cfg.inc)
    for e in cert["edges"]:
        t, s, c = e["t"], e["s"], e["c"]
        assert (t, s) in inc and c in (-1, 1) and list(cfg.pair(t, s)) == e["pair"]
        total = [a + c * b for a, b in zip(total, cfg.vec(t, s))]
    return all(a == 0 for a in total)


# ---- truncated power series over F2: an int bitmask, bit k = coefficient of eps^k ----

MASK = (1 << SERIES_ORDER) - 1


def smul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = (a << 1) & MASK
        b >>= 1
    return r


def sval(a):
    return (a & -a).bit_length() - 1 if a else SERIES_ORDER


def sinv(a):
    """Inverse of a unit (constant term 1) modulo eps^SERIES_ORDER."""
    assert a & 1
    x = 1
    for _ in range(SERIES_ORDER.bit_length() + 1):
        x = smul(x, smul(a, x))  # Newton step x <- x(2 - a x) = x * a * x in char 2
    assert smul(a, x) == 1
    return x


def monomial_ratio(cfg, P, Q, t, s):
    """(a, b) with a = P_i(t) Q_i(s), b = P_j(t) Q_j(s) as series."""
    i, j = cfg.pair(t, s)
    return smul(P[t][i], Q[s][i]), smul(P[t][j], Q[s][j])


def valuation_control(cfg, cert, rng):
    """Random unit-coordinate jets over F2[[eps]]: nu(N_h) >= min over flow edges of nu(N_e)."""
    tight = 0
    for _ in range(RANDOM_TRIALS):
        P = [[(1 | rng.getrandbits(SERIES_ORDER) & ~1) if cfg.P[t][j] else 0 for j in range(3)]
             for t in range(cfg.v)]
        Q = [[(1 | rng.getrandbits(SERIES_ORDER) & ~1) if cfg.Q[t][j] else 0 for j in range(3)]
             for t in range(cfg.v)]
        lhs = 1
        for e in cert["edges"]:
            a, b = monomial_ratio(cfg, P, Q, e["t"], e["s"])
            r = smul(a, sinv(b))
            lhs = smul(lhs, r if e["c"] == 1 else sinv(r))
        a, b = monomial_ratio(cfg, P, Q, cert["line"], cert["line"])
        rh = smul(a, sinv(b))
        assert smul(rh, lhs) == 1, "multiplicative identity failed on a random jet"
        # Every coordinate is a unit, so nu(u_e) = nu(N_e) with N_e = a_e + b_e in char 2.
        m = min(sval(x ^ y) for x, y in
                (monomial_ratio(cfg, P, Q, e["t"], e["s"]) for e in cert["edges"]))
        nh = sval(a ^ b)
        assert nh >= m, "valuation bound failed"
        tight += nh == m
    return tight


def rational_control(cfg, cert, rng):
    """The monomial identity at random nonzero rationals, and the Q-sign bookkeeping."""
    for _ in range(RANDOM_TRIALS):
        P = [[Fraction(rng.choice([-1, 1]) * rng.randint(1, 97), rng.randint(1, 97)) if cfg.P[t][j] else 0
              for j in range(3)] for t in range(cfg.v)]
        Q = [[Fraction(rng.choice([-1, 1]) * rng.randint(1, 97), rng.randint(1, 97)) if cfg.Q[t][j] else 0
              for j in range(3)] for t in range(cfg.v)]
        prod = Fraction(1)
        for e in cert["edges"] + [{"t": cert["line"], "s": cert["line"], "c": 1}]:
            i, j = cfg.pair(e["t"], e["s"])
            prod *= (P[e["t"]][i] * Q[e["s"]][i] / (P[e["t"]][j] * Q[e["s"]][j])) ** e["c"]
        assert prod == 1
    # On the actual configuration every incidence ratio is -1 and the harmonic ratio is +1.
    prod = 1
    for e in cert["edges"]:
        i, j = cfg.pair(e["t"], e["s"])
        r = Fraction(cfg.P[e["t"]][i] * cfg.Q[e["s"]][i], cfg.P[e["t"]][j] * cfg.Q[e["s"]][j])
        assert r == -1
        prod *= r
    assert prod == 1 and len(cert["edges"]) % 2 == 0


def mutation_controls(cfg, cert):
    killed = 0
    for k in range(len(cert["edges"])):
        flipped = json.loads(json.dumps(cert))
        flipped["edges"][k]["c"] *= -1
        dropped = json.loads(json.dumps(cert))
        del dropped["edges"][k]
        killed += (not check_identity(cfg, flipped)) + (not check_identity(cfg, dropped))
    assert killed == 2 * len(cert["edges"]), "a mutated certificate still passed"
    return killed


def main():
    write = sys.argv[1:] == ["--write"]
    assert sys.argv[1:] in ([], ["--write"]), "usage: verify.py [--write]"
    found = {}
    report = []
    for name in NAMES:
        cfg, certs, movable = find_certificates(name)
        immovable = [c["line"] for c in certs]
        assert immovable == EXPECTED_IMMOVABLE[name], (name, immovable)
        found[name] = {"harmonic": cfg.harm, "movable_first_order": movable, "certificates": certs}
        report.append((name, cfg, certs, movable))
    if write:
        with open(CERT, "w") as f:
            json.dump(found, f, indent=1, sort_keys=True)
            f.write("\n")
        print("WROTE", CERT)
        return
    with open(CERT) as f:
        stored = json.load(f)
    assert stored == found, "CERTIFICATE.json differs from the recomputed certificates"
    rng = random.Random(20261027)
    lines = 0
    for name, cfg, certs, movable in report:
        for cert in certs:
            assert check_identity(cfg, cert)
            rational_control(cfg, cert, rng)
            tight = valuation_control(cfg, cert, rng)
            killed = mutation_controls(cfg, cert)
            lines += 1
            print("%s line %d: identity over %d incidences (pair %s); %d random jets, %d tight; "
                  "%d mutations rejected" % (name, cert["line"], len(cert["edges"]), cert["pair"],
                                             RANDOM_TRIALS, tight, killed))
        print("%s: v=%d incidences=%d harmonic=%s movable_first_order=%s"
              % (name, cfg.v, len(cfg.inc), cfg.harm, movable))
    assert lines == 4
    print("PASS_CHAR2_JET_EVERY_ORDER_OBSTRUCTION lines=4")


if __name__ == "__main__":
    main()
