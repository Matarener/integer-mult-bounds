"""Histogram-level counting of the lockstep compiler: widths, leaves, unit instances,
peak simultaneously live units (Lemma B) and the record counts of the pass (Lemma A).

Nothing here enumerates units one by one, so it also runs on the complete p7 and
selected profiles.  On small rules it must agree exactly with the event-level
executor (executor.py) and with the counting compiler of #4691.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from math import gcd, lcm


class HistRule:
    """A rule known only through histograms: target ranks with field counts, paid ranks with
    chronological multiplicities and the pass tags.  Enough for every count in this module;
    the order of the rounds does not enter any count (class sizes depend on the product of
    the paid ranks on a path only)."""

    def __init__(self, name, targets, paid, owned_banks=1, kinds=None, completed_fields=0):
        from math import factorial, prod
        self.name = name
        self.targets = Counter({int(k): int(c) for k, c in targets.items() if c})
        self.paid = Counter({int(r): int(c) for r, c in paid.items() if c})
        self.types = tuple(sorted(self.targets))
        self.W = tuple(self.targets[k] for k in self.types)
        self.m = max(self.types)
        self.roles_count = sum(self.W)
        self.rounds_count = sum(self.paid.values())
        self.owned_count = owned_banks
        self.kind_counts = Counter(kinds) if kinds else Counter({"orig": self.rounds_count})
        self.completed_fields = completed_fields
        assert sum(self.kind_counts.values()) == self.rounds_count
        assert max(self.paid) < min(self.types), "strict hierarchy"
        self._factorial, self._prod = factorial, prod

    @property
    def round_mult(self):
        return self.paid

    def c(self, a):
        return self._prod(k ** e for k, e in zip(self.types, a))

    def u(self, a):
        f = self._factorial
        return f(sum(a)) // self._prod(f(e) for e in a) * self._prod(w ** e for w, e in zip(self.W, a))

    def lattice(self, n, dil):
        bound = n // (self.m * dil)
        out = []

        def rec(i, a, val):
            if i == len(self.types):
                out.append(tuple(a))
                return
            e = 0
            while val <= bound:
                rec(i + 1, a + [e], val)
                e += 1
                val *= self.types[i]
        if bound:
            rec(0, [], 1)
        return out

    def pass_counts(self):
        kc = self.kind_counts
        return {"rounds": self.rounds_count, "orig_rounds": kc["orig"], "piece_rounds": kc["piece"],
                "completion_rounds": kc["completion"], "completed_roles": self.completed_fields,
                "adapters": 2 * self.completed_fields, "relocations": kc["piece"] + kc["completion"],
                "owned_banks": self.owned_count}


def hist_rule_of(rule):
    """HistRule view of an executor Rule (same counts)."""
    return HistRule(rule.name, rule.targets, Counter(r for r, _ in rule.rounds), len(rule.owned),
                    rule.kinds, len(rule.completed))


def passed_hist_rule(name, T, P, J, L, owned_banks=1):
    """HistRule after completion to L and splitting at J, with the pass tags."""
    T2, P2, rec = pass_histograms(T, P, J, L)
    kinds = ["orig"] * rec["orig_jobs"] + ["piece"] * rec["piece_jobs"] + ["completion"] * rec["completion_jobs"]
    return HistRule(name, T2, P2, owned_banks, kinds, rec["completed_fields"])


def _roles_count(R):
    return getattr(R, "roles_count", None) or len(R.roles)


def _owned_count(R):
    return getattr(R, "owned_count", None) or len(R.owned)


def _round_mult(R):
    return R.round_mult if hasattr(R, "round_mult") else Counter(r for r, _ in R.rounds)


class FlowCounts:
    """Class-level flow of one tree copy of `rule` at top rank n (FINITE-PRECOMPILATION s3)."""

    def __init__(self, rule, n):
        self.R, self.n = rule, n
        pts = rule.lattice(n, 1)
        self.G = max(map(sum, pts))
        self.round_mult = _round_mult(rule)                          # distinct paid ranks and multiplicities
        self.sources = Counter()                                    # source rank -> count (one copy)
        self.exits = Counter()                                      # exit rank -> jobs (one copy)
        self.exit_paths = {}                                        # deepest dilation -> max live units on such a path
        self.units_total = 0
        self.classes_total = 0
        self.peak_units = self._cls(0, 1, None, 0)

    @lru_cache(None)
    def _class_points(self, d, dil):
        R = self.R
        return tuple(a for a in R.lattice(self.n, dil) if sum(a) == self.G - d)

    def _cls(self, d, dil, incoming, above):
        """Returns the peak number of simultaneously live units (one copy) on the subtree
        rooted at this class, including this class; accumulates sources/exits/totals.
        `incoming` is a Counter point -> number of parent jobs aimed at that point;
        `above` is the number of live units of the ancestor classes on this path."""
        R = self.R
        pts = self._class_points(d, dil)
        size = sum(R.u(a) for a in pts)
        self.units_total += size
        self.classes_total += 1
        demand = Counter()
        for a in pts:
            ua = R.u(a)
            for i, k in enumerate(R.types):
                p = tuple(x + (j == i) for j, x in enumerate(a))
                demand[p] += ua * R.W[i]
        supply = incoming or Counter()
        assert all(supply[p] <= demand[p] for p in supply), "Pascal matching: supply within demand"
        for p, dm in demand.items():
            missing = dm - supply.get(p, 0)
            if missing:
                self.sources[dil * R.c(p)] += missing
        if size == 0:
            return 0
        own = Counter({a: R.u(a) for a in pts})
        best_child = 0
        for r, mult in sorted(self.round_mult.items()):
            if d < self.G:
                # all `mult` rounds of rank r produce identical child classes
                peak_child = self._cls(d + 1, dil * r, own, above + size)
                for _ in range(mult - 1):
                    self._cls(d + 1, dil * r, own, above + size)
                best_child = max(best_child, peak_child)
            else:
                assert all(x == 0 for a in pts for x in a), "deepest class is the zero point"
                self.exits[r * dil] += mult * size
        if d == self.G:
            # the path's exit ranks r * dil are tied to the units live on this same path
            self.exit_paths[dil] = max(self.exit_paths.get(dil, 0), above + size)
        return size + best_child


class Counts:
    def __init__(self, rule, executed=lambda n, cost: True):
        self.R = rule
        self.executed = executed

    @lru_cache(None)
    def flow(self, n):
        return FlowCounts(self.R, n)

    @lru_cache(None)
    def compile(self, n):
        """(B_n, a, P_n, cost) with the same conventions as #4691's counting compiler."""
        R = self.R
        if n < R.m:
            return (1, 1, n, 0)
        F = self.flow(n)
        S = sum(F.sources.values())
        a = 1
        for e, t in F.exits.items():
            B = self.compile(e)[0]
            a = lcm(a, B // gcd(B, t))
        for s, cnt in F.sources.items():
            if n - s:
                B = self.compile(n - s)[0]
                a = lcm(a, B // gcd(B, cnt))
        width = a * S
        leaves = Fraction(0)
        cost = a * F.units_total * _roles_count(R)
        for e, t in F.exits.items():
            B, _, P, c = self.compile(e)
            leaves += Fraction(a * t * P, B)
            cost += a * t // B * c
        for s, cnt in F.sources.items():
            if n - s:
                B, _, P, c = self.compile(n - s)
                leaves += Fraction(a * cnt * P, B)
                cost += a * cnt // B * c
        assert leaves.denominator == 1
        return (width, a, leaves.numerator, cost)

    def _runs(self, n):
        return n >= self.R.m and self.executed(n, self.compile(n)[3])

    @lru_cache(None)
    def banks(self, n, copies=None):
        """(total bank allocations, peak live banks) of the executed rank-n program,
        with one bank set per unit instance (nb banks) and the LIFO allocator.
        `copies` mirrors the executor's partial mode: only that many lockstep tree copies
        run and every nested program is interface-checked (no banks)."""
        nb = _owned_count(self.R)
        if n < self.R.m or (copies is None and not self._runs(n)):
            return (0, 0)
        F = self.flow(n)
        B, a, P, cost = self.compile(n)
        if copies is not None:
            a = min(a, copies)
            return (a * F.units_total * nb, a * F.peak_units * nb)
        total = a * F.units_total * nb
        peak = 0
        for s, cnt in F.sources.items():
            if n - s:
                Bc = self.compile(n - s)[0]
                tot_c, pk_c = self.banks(n - s)
                total += (a * cnt // Bc) * tot_c
                peak = max(peak, pk_c)
        for e, t in F.exits.items():
            Be = self.compile(e)[0]
            tot_e, _ = self.banks(e)
            total += (a * t // Be) * tot_e
        # a path's exit batches run at its deepest class while that whole path is live; the
        # executor runs exit groups one after another, so the maximum is over compatible
        # (path, exit) pairs: exit ranks r * dil of a path with deepest dilation dil
        peak = max(peak, a * F.peak_units * nb)
        for dil, U in F.exit_paths.items():
            for r in F.round_mult:
                peak = max(peak, a * U * nb + self.banks(r * dil)[1])
        return (total, peak)

    @lru_cache(None)
    def records(self, n, copies=None):
        """Unit instances and pass records of the executed rank-n program, nested programs included
        (`copies`: partial mode as in banks)."""
        pc = self.R.pass_counts()
        if n < self.R.m or (copies is None and not self._runs(n)):
            return Counter()
        F = self.flow(n)
        B, a, P, cost = self.compile(n)
        if copies is not None:
            a = min(a, copies)
        U = a * F.units_total
        out = Counter({"unit_instances": U, "classes": F.classes_total,
                       "orig_jobs": U * pc["orig_rounds"], "piece_jobs": U * pc["piece_rounds"],
                       "completion_jobs": U * pc["completion_rounds"],
                       "adapter_records": U * pc["adapters"], "relocation_records": U * pc["relocations"],
                       "bank_init_scans": U * pc["owned_banks"], "bank_erase_scans": U * pc["owned_banks"]})
        if copies is not None:
            return out
        for s, cnt in F.sources.items():
            if n - s:
                Bc = self.compile(n - s)[0]
                for k, v in self.records(n - s).items():
                    out[k] += (a * cnt // Bc) * v
        for e, t in F.exits.items():
            Be = self.compile(e)[0]
            for k, v in self.records(e).items():
                out[k] += (a * t // Be) * v
        return out


# ------------------------------------------------------------------ histogram algebra (any tensor power)
def product_histograms(T, P, v):
    """Ranks multiply and counts multiply under the chronological product (p7-TENSOR s1)."""
    Tv, Pv = Counter({1: 1}), Counter({1: 1})
    for _ in range(v):
        Tn, Pn = Counter(), Counter()
        for k1, c1 in Tv.items():
            for k2, c2 in T.items():
                Tn[k1 * k2] += c1 * c2
        for r1, c1 in Pv.items():
            for r2, c2 in P.items():
                Pn[r1 * r2] += c1 * c2
        Tv, Pv = Tn, Pn
    return Tv, Pv


def pieces(rank, J):
    q, r = divmod(rank, J)
    return [J] * q + ([r] if r else [])


def pass_histograms(T, P, J, L):
    """Completion to floor L and splitting at cutoff J on histograms.  Returns the new
    target and paid histograms and the record counts of the pass."""
    assert 0 < J < L
    T2, P2 = Counter(), Counter()
    rec = Counter()
    for k, cnt in T.items():
        T2[max(k, L)] += cnt
        if k < L:
            rec["completed_fields"] += cnt
            rec["adapter_records"] += 2 * cnt
            for p in pieces(L - k, J):
                P2[p] += cnt
                rec["completion_jobs"] += cnt
                rec["relocation_records"] += cnt
    for r, cnt in P.items():
        ps = pieces(r, J)
        for i, p in enumerate(ps):
            P2[p] += cnt
            if i:
                rec["piece_jobs"] += cnt
                rec["relocation_records"] += cnt
            else:
                rec["orig_jobs"] += cnt
    return T2, P2, rec


def digest(obj):
    """SHA256 of a JSON rendering with exact integers as strings (for huge counts)."""
    import hashlib
    import json

    def conv(o):
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
        if isinstance(o, (list, tuple)):
            return [conv(v) for v in o]
        if isinstance(o, bool):
            return o
        if isinstance(o, int):
            return str(o)
        return o
    return hashlib.sha256(json.dumps(conv(obj), sort_keys=True).encode()).hexdigest()


def mass(H):
    return sum(k * c for k, c in H.items())


def moment(H, t, prec=60):
    from decimal import Decimal, getcontext
    getcontext().prec = prec
    tt = Decimal(t.numerator) / Decimal(t.denominator)
    return sum(Decimal(c) * (Decimal(k) ** tt) for k, c in H.items())


def split_tax(R, J, t):
    """tau(R) = S_t(R,J) - R^t  (net-tax-rank-compiler PROOF s1)."""
    from decimal import Decimal
    tt = Decimal(t.numerator) / Decimal(t.denominator)
    return sum(Decimal(p) ** tt for p in pieces(R, J)) - Decimal(R) ** tt


def completion_tax(K, L, J, t):
    """E(K) = K^t + S_t(L-K,J) - L^t for K<L."""
    from decimal import Decimal
    tt = Decimal(t.numerator) / Decimal(t.denominator)
    return Decimal(K) ** tt + sum(Decimal(p) ** tt for p in pieces(L - K, J)) - Decimal(L) ** tt


def gap_identity(T, P, J, L, t, prec=60):
    """Checks net-tax identity (1): T'_t - P'_t = T_t - P_t - sum tau(R) - sum E(K).
    Returns (left, right) Decimals."""
    from decimal import getcontext
    getcontext().prec = prec
    T2, P2, _ = pass_histograms(T, P, J, L)
    left = moment(T2, t, prec) - moment(P2, t, prec)
    right = moment(T, t, prec) - moment(P, t, prec)
    for r, cnt in P.items():
        right -= cnt * split_tax(r, J, t)
    for k, cnt in T.items():
        if k < L:
            right -= cnt * completion_tax(k, L, J, t)
    return left, right
