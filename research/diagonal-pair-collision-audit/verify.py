#!/usr/bin/env python3
"""Independent re-check of PR6097's five-call diagonal-pair refutation, and its
extension from F2 to F3 (width two).

Standard library only; imports no repository code and does not read PR6097's
verifier. The relaxation is restated over F_p: a node per chronological subset
U of call positions plus nodes A, B for the targets a, b; an equivalence
relation closed under common-prefix/common-suffix cancellation (every prefix
or suffix length, both directions); forbidden equalities (g_i != e, a != b,
a, b not products of at most two labels); and, in each of the four matrix-entry
equations of sum_U [g_U] P_U = diag([a],[b]) over F_p[G], every class has
total weight 0 mod p. A refutation of the relaxation refutes every group
realization (README.md, "Soundness over F_p").

Usage:
    verify.py              F2 lengths 0..5, F3 lengths 0..4, controls
    verify.py --f3-full [--jobs N]
                           also F3 length 5 with this search. Not registered:
                           single tuples need up to ~10^5 nodes and the run
                           takes hours; the F3 length-5 row is the local SAT
                           result of sat_crosscheck.py instead (README.md).
"""
import itertools
import json
import sys

NODE_CAP = 10 ** 6


def require(cond, msg):
    if not cond:
        raise SystemExit("FAIL " + msg)


def mat_mul(X, Y, p):
    a, b, c, d = X
    e, f, g, h = Y
    return ((a * e + b * g) % p, (a * f + b * h) % p,
            (c * e + d * g) % p, (c * f + d * h) % p)


IDENTITY = (1, 0, 0, 1)


def projectors(p):
    """Rank-one idempotent 2x2 matrices over F_p (row-major a, b, c, d)."""
    out = []
    for N in itertools.product(range(p), repeat=4):
        a, b, c, d = N
        if mat_mul(N, N, p) == N and N != (0, 0, 0, 0) and N != IDENTITY:
            out.append(N)
    return tuple(out)


def outer_products(p):
    """Independent inventory: u v^T with v.u = 1."""
    out = set()
    for u in itertools.product(range(p), repeat=2):
        for v in itertools.product(range(p), repeat=2):
            if (u[0] * v[0] + u[1] * v[1]) % p == 1:
                out.add((u[0] * v[0] % p, u[0] * v[1] % p, u[1] * v[0] % p, u[1] * v[1] % p))
    return out


def subset_coefficients(tup, p):
    """P_U = prod_i (N_i if i in U else I - N_i), chronological order."""
    k = len(tup)
    out = {}
    for U in range(1 << k):
        M = IDENTITY
        for i, N in enumerate(tup):
            F = N if (U >> i) & 1 else tuple((x - y) % p for x, y in zip(IDENTITY, N))
            M = mat_mul(M, F, p)
        out[U] = M
    return out


def free_word_product(tup, word, p):
    """Independent expansion: multiply D_N(g) = (I-N) + [g]N in the free monoid
    algebra, keyed by label strings. Used only as a control."""
    poly = {"": IDENTITY}
    for N, g in zip(tup, word):
        IN = tuple((x - y) % p for x, y in zip(IDENTITY, N))
        new = {}
        for w, M in poly.items():
            for w2, F in ((w, IN), (w + g, N)):
                prod = mat_mul(M, F, p)
                old = new.get(w2, (0, 0, 0, 0))
                new[w2] = tuple((x + y) % p for x, y in zip(old, prod))
        poly = {w: M for w, M in new.items() if M != (0, 0, 0, 0)}
    return poly


def bits(U, k):
    return [i for i in range(k) if (U >> i) & 1]


def cancellation_rules(k, suffixes=True):
    """(U, V, U', V'): g_U = g_V <=> g_U' = g_V', where U, V share a common
    nonempty prefix (or suffix) of positions that is removed. Every common
    prefix/suffix length is emitted."""
    rules = []
    for U in range(1 << k):
        pu = bits(U, k)
        for V in range(U + 1, 1 << k):
            pv = bits(V, k)
            m = 0
            while m < min(len(pu), len(pv)) and pu[m] == pv[m]:
                m += 1
                cut = sum(1 << i for i in pu[:m])
                rules.append((U, V, U & ~cut, V & ~cut))
            m = 0
            while suffixes and m < min(len(pu), len(pv)) and pu[-1 - m] == pv[-1 - m]:
                m += 1
                cut = sum(1 << i for i in pu[len(pu) - m:])
                rules.append((U, V, U & ~cut, V & ~cut))
    return rules


def authenticate_rule(rule, k):
    """Check a rule is a single common-context law on increasing sequences."""
    U, V, U2, V2 = rule
    pu, pv, pu2, pv2 = (bits(x, k) for x in rule)
    for split in range(1, len(pu) + 1):
        ctx = pu[:split]
        if pu == ctx + pu2 and pv == ctx + pv2:
            return True
        ctx = pu[len(pu) - split:]
        if pu == pu2 + ctx and pv == pv2 + ctx:
            return True
    return False


class Contradiction(Exception):
    pass


def root(par, x):
    while par[x] != x:
        x = par[x]
    return x


def merge(par, x, y):
    x, y = root(par, x), root(par, y)
    if x != y:
        par[max(x, y)] = min(x, y)


def close(par, rules, forbidden):
    changed = True
    while changed:
        changed = False
        for U, V, U2, V2 in rules:
            left = root(par, U) == root(par, V)
            right = root(par, U2) == root(par, V2)
            if left != right:
                if left:
                    merge(par, U2, V2)
                else:
                    merge(par, U, V)
                changed = True
    for x, y in forbidden:
        if root(par, x) == root(par, y):
            raise Contradiction


class Problem:
    def __init__(self, k, p, cancellation=True, min_target_labels=3, suffixes=True):
        self.k, self.p = k, p
        self.A, self.B = 1 << k, (1 << k) + 1
        self.rules = cancellation_rules(k, suffixes) if cancellation else []
        forb = [(0, 1 << i) for i in range(k)] + [(self.A, self.B)]
        for U in range(1 << k):
            if bin(U).count("1") < min_target_labels:
                forb += [(self.A, U), (self.B, U)]
        self.forbidden = forb
        self.nodes = 0

    def equations(self, tup):
        P = subset_coefficients(tup, self.p)
        eqs = []
        for entry in range(4):
            E = [(U, P[U][entry]) for U in range(1 << self.k) if P[U][entry]]
            if entry == 0:
                E.append((self.A, self.p - 1))
            if entry == 3:
                E.append((self.B, self.p - 1))
            eqs.append(E)
        return eqs

    def solve(self, tup):
        """Return a surviving partition of the relaxation, or None."""
        require(len(tup) == self.k, "length")
        self.count = 0
        return self._search(list(range((1 << self.k) + 2)), self.equations(tup))

    def _search(self, par, eqs):
        self.count += 1
        self.nodes += 1
        require(self.count <= NODE_CAP, "node cap exceeded (not a rejection)")
        par = list(par)
        p = self.p
        while True:
            try:
                close(par, self.rules, self.forbidden)
            except Contradiction:
                return None
            branch = None
            forced = False
            for E in eqs:
                total = {}
                for node, w in E:
                    r = root(par, node)
                    total[r] = (total.get(r, 0) + w) % p
                live = sorted(r for r, t in total.items() if t)
                if len(live) == 1:
                    return None
                if len(live) == 2:
                    if (total[live[0]] + total[live[1]]) % p:
                        return None
                    merge(par, live[0], live[1])
                    forced = True
                    break
                if live and (branch is None or len(live) < len(branch)):
                    branch = live
            if forced:
                continue
            if branch is None:
                return par
            first = branch[0]
            for partner in branch[1:]:
                child = list(par)
                merge(child, first, partner)
                found = self._search(child, eqs)
                if found is not None:
                    return found
            return None


def census(p, k, first=None):
    Ns = projectors(p)
    prob = Problem(k, p)
    heads = Ns if first is None else (first,)
    tested = survivors = 0
    if k == 0:
        tested, survivors = 1, int(prob.solve(()) is not None)
        return tested, survivors, prob.nodes
    for head in heads:
        for rest in itertools.product(Ns, repeat=k - 1):
            tested += 1
            if prob.solve((head,) + rest) is not None:
                survivors += 1
    return tested, survivors, prob.nodes


def _job(args):
    p, k, head = args
    return census(p, k, head)


def dec(n):
    """PR6097's row-major bit encoding over F2."""
    return (n & 1, (n >> 1) & 1, (n >> 2) & 1, (n >> 3) & 1)


def controls():
    for p, count in ((2, 6), (3, 12)):
        Ns = projectors(p)
        require(len(Ns) == count == p * (p + 1), "projector count p=%d" % p)
        require(set(Ns) == outer_products(p), "outer-product inventory p=%d" % p)
    require(tuple(sorted(dec(n) for n in (1, 3, 5, 8, 10, 12))) == tuple(sorted(projectors(2))),
            "PR6097 encoding")
    for k in range(7):
        for rule in cancellation_rules(k):
            require(authenticate_rule(rule, k), "rule %r" % (rule,))
    E00, E11 = (1, 0, 0, 0), (0, 0, 0, 1)
    six = (E00, E00, E00, E11, E11, E11)
    for p in (2, 3):
        # exact symbolic endpoint of the direct six-call word
        poly = free_word_product(six, "xyxyxy", p)
        require(poly == {"xyx": (1, 0, 0, 0), "yxy": (0, 0, 0, 1)}, "six-call endpoint p=%d" % p)
        require(Problem(6, p).solve(six) is not None, "six-call construction rejected p=%d" % p)
        # subset expansion agrees with free-word expansion on distinct letters
        for tup in itertools.islice(itertools.product(projectors(p), repeat=4), 0, None, 97):
            free = free_word_product(tup, "abcd", p)
            sub = {}
            for U, M in subset_coefficients(tup, p).items():
                if M != (0, 0, 0, 0):
                    sub["".join("abcd"[i] for i in bits(U, 4))] = M
            require(free == sub, "expansion p=%d %r" % (p, tup))
    # four-call diag([xy],[yx]) (#6038) is accepted when targets need >= 2 labels
    require(Problem(4, 2, min_target_labels=2).solve((E00, E00, E11, E11)) is not None,
            "four-call xy/yx construction")
    require(Problem(4, 3, min_target_labels=2).solve((E00, E00, E11, E11)) is not None,
            "four-call xy/yx construction F3")
    # removing cancellation reopens PR6097's four-call tuple (1,5,1,10)
    t = tuple(map(dec, (1, 5, 1, 10)))
    require(Problem(4, 2, cancellation=False).solve(t) is not None, "no-cancel control F2")
    require(Problem(4, 2).solve(t) is None, "cancel kills (1,5,1,10)")
    # short targets reopen (E00, E11)
    require(Problem(2, 2, min_target_labels=1).solve((E00, E11)) is not None, "short control F2")
    require(Problem(2, 3, min_target_labels=1).solve((E00, E11)) is not None, "short control F3")
    # PR6097's written five-call example is rejected
    require(Problem(5, 2).solve(tuple(map(dec, (1, 5, 5, 3, 10)))) is None, "written example")
    # Without cancellation the relaxation has exact survivor counts (F2: 20 at
    # length four and 938 at length five, the counts of #6048's support-only
    # relaxation; F3: 84 at length four). The local SAT encoding reproduces them.
    for p, k, expected in ((2, 4, 20), (2, 5, 938), (3, 4, 84)):
        relaxed = Problem(k, p, cancellation=False)
        got = sum(relaxed.solve(t) is not None for t in itertools.product(projectors(p), repeat=k))
        require(got == expected, "no-cancel count p=%d k=%d: %d" % (p, k, got))
    # Prefix cancellation alone leaves 30 F2 length-five survivors: suffix
    # rules are needed too.
    prefix_only = Problem(5, 2, suffixes=False)
    got = sum(prefix_only.solve(t) is not None for t in itertools.product(projectors(2), repeat=5))
    require(got == 30, "prefix-only control: %d" % got)


def main(argv):
    full = "--f3-full" in argv
    jobs = 1
    if "--jobs" in argv:
        jobs = int(argv[argv.index("--jobs") + 1])
    controls()
    results = []
    plan = [(2, k) for k in range(6)] + [(3, k) for k in range(5)]
    if full:
        plan.append((3, 5))
    for p, k in plan:
        if jobs > 1 and k >= 4:
            import multiprocessing
            with multiprocessing.Pool(jobs) as pool:
                parts = pool.map(_job, [(p, k, h) for h in projectors(p)])
            tested = sum(x[0] for x in parts)
            surv = sum(x[1] for x in parts)
            nodes = sum(x[2] for x in parts)
        else:
            tested, surv, nodes = census(p, k)
        require(tested == len(projectors(p)) ** k, "incomplete enumeration")
        require(surv == 0, "survivor at p=%d k=%d" % (p, k))
        results.append({"field": p, "calls": k, "tuples": tested, "survivors": surv, "nodes": nodes})
    print("PASS_DIAGONAL_PAIR_COLLISION_AUDIT " + json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
