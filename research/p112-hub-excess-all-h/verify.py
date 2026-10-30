#!/usr/bin/env python3
"""Hub-excess equality 4h(h+1) for every hub count.

Part 1 checks the finite core of PROOF.md: the circuits through E in the
seven-vector reduced configuration, the excluded three-query hub, the source
functional cases and every explicit cost-one evaluator.
Part 2 is a control: a brute-force subset census of the h-hub star for
h = 1..H (default H = 4), compared with the closed-form table, and its
minimum charge computed by exhaustive paid-set search.

Exact rational arithmetic only. Usage: verify.py [--hmax H]
"""
import argparse
import itertools
from fractions import Fraction

PASS = "PASS_HUB_EXCESS_ALL_H"

# Reduced configuration, coordinates (E, F, G).
CORE = {
    "g": (0, 0, 1),
    "d": (1, 1, 0),
    "t": (1, 1, 1),
    "a": (1, 0, 1),   # {v_j, x_j}: x_j + v_j = E + G
    "b": (0, 1, 1),   # {v_j, y_j}: y_j + v_j = F + G
    "c": (1, -1, 0),  # {x_j, y_j}: x_j - y_j = E - F
}
E3 = (1, 0, 0)
HUB_TYPES = ("a", "b", "c")
EXPECTED_CIRCUITS = {
    frozenset(s) for s in (
        "ga", "dta", "gdb", "tb", "dc", "gtc", "dab", "tac", "gbc",
    )
}
FAMILY_CIRCUITS = {frozenset("dc"), frozenset("gtc"), frozenset("dab")}


def solve(columns, target):
    """Unique coefficients expressing target in independent columns, or None.

    Returns "dependent" if the columns are linearly dependent.
    """
    rows = len(target)
    width = len(columns)
    matrix = [[Fraction(columns[j][i]) for j in range(width)] + [Fraction(target[i])]
              for i in range(rows)]
    pivots = []
    r = 0
    for col in range(width + 1):
        pivot = next((i for i in range(r, rows) if matrix[i][col] != 0), None)
        if pivot is None:
            continue
        if col == width:
            return None  # target outside span
        matrix[r], matrix[pivot] = matrix[pivot], matrix[r]
        scale = matrix[r][col]
        matrix[r] = [value / scale for value in matrix[r]]
        for i in range(rows):
            if i != r and matrix[i][col] != 0:
                factor = matrix[i][col]
                matrix[i] = [x - factor * y for x, y in zip(matrix[i], matrix[r])]
        pivots.append(col)
        r += 1
    if len(pivots) < width:
        return "dependent"
    return [matrix[i][width] for i in range(width)]


def core_circuits():
    """Independent T subset of CORE with E in span(T), all coefficients nonzero."""
    found = {}
    names = sorted(CORE)
    for size in range(1, len(names) + 1):
        for subset in itertools.combinations(names, size):
            coeffs = solve([CORE[n] for n in subset], E3)
            if coeffs is None or coeffs == "dependent":
                continue
            if all(c != 0 for c in coeffs):
                found[frozenset(subset)] = dict(zip(subset, coeffs))
    return found


def check_core():
    circuits = core_circuits()
    if set(circuits) != EXPECTED_CIRCUITS:
        raise AssertionError(f"core circuits {sorted(map(sorted, circuits))}")
    for t in circuits:
        if set(HUB_TYPES) <= t:
            raise AssertionError("a, b and c are dependent; cannot share a circuit")
    # Lemma 2: a hub using all of v, x, y contributes the plane <E+G, F+G>;
    # with one core query q the representation needs lambda_x, lambda_y,
    # lambda_x + lambda_y (the v coefficient) and mu all nonzero.
    for q in ("g", "d", "t"):
        coeffs = solve([CORE["a"], CORE["b"], CORE[q]], E3)
        if coeffs is None or coeffs == "dependent":
            continue
        lx, ly, mu = coeffs
        if lx != 0 and ly != 0 and lx + ly != 0 and mu != 0:
            raise AssertionError(f"three-query hub survives with {q}")
    # No core query lies in the plane <E+G, F+G>, so at most one can be added.
    for q in ("g", "d", "t"):
        if solve([CORE["a"], CORE["b"]], CORE[q]) is not None:
            raise AssertionError(f"{q} in hub plane")
    single = sum(1 for t in circuits if len(t & set(HUB_TYPES)) == 1)
    double = sum(1 for t in circuits if len(t & set(HUB_TYPES)) == 2)
    if (single, double) != (6, 3):
        raise AssertionError((single, double))
    return circuits


def check_sources_local():
    """phi(G) in {0,-1} and the per-hub vanishing bundles (PROOF.md Lemma 4)."""
    # Hub values: phi(v)=nu, phi(x)=1+gamma-nu, phi(y)=gamma-nu.
    def zeros(gamma, nu):
        out = set()
        if nu == 0:
            out.add("v")
        if 1 + gamma - nu == 0:
            out.add("x")
        if gamma - nu == 0:
            out.add("y")
        return frozenset(out)
    expected = {0: {frozenset("vy"), frozenset("x")}, -1: {frozenset("vx"), frozenset("y")}}
    for gamma, bundles in expected.items():
        got = {zeros(gamma, nu) for nu in (0, 1 + gamma, gamma)}
        if got != bundles:
            raise AssertionError((gamma, got))
    # For gamma outside {0,-1} the three hub conditions are pairwise exclusive.
    for gamma in (Fraction(1), Fraction(-2), Fraction(1, 2), Fraction(-1, 3)):
        for nu in (0, 1 + gamma, gamma):
            if len(zeros(gamma, nu)) != 1:
                raise AssertionError((gamma, nu))


# ---------------------------------------------------------------- star model


def star(h):
    dim = 3 + h
    def vec(**kw):
        row = [0] * dim
        for key, value in kw.items():
            row[{"E": 0, "F": 1, "G": 2}[key] if key in "EFG" else 3 + int(key[1:])] = value
        return tuple(row)
    names = ["g", "d", "t"]
    vecs = [vec(G=1), vec(E=1, F=1), vec(E=1, F=1, G=1)]
    for j in range(h):
        names += [f"v{j}", f"x{j}", f"y{j}"]
        vecs += [vec(**{f"V{j}": 1}), vec(E=1, G=1, **{f"V{j}": -1}),
                 vec(F=1, G=1, **{f"V{j}": -1})]
    return names, vecs, vec(E=1), vec(F=1)


def closed_form(h):
    """E readers, F readers, E sources, F sources as frozensets of names."""
    def hub(j, kind):
        return {"a": {f"v{j}", f"x{j}"}, "b": {f"v{j}", f"y{j}"}, "c": {f"x{j}", f"y{j}"}}[kind]
    e_readers = set()
    for circuit in EXPECTED_CIRCUITS:
        core = {q for q in circuit if q in "gdt"}
        kinds = sorted(circuit & set(HUB_TYPES))
        for hubs in itertools.permutations(range(h), len(kinds)):
            names = set(core)
            for j, kind in zip(hubs, kinds):
                names |= hub(j, kind)
            e_readers.add(frozenset(names))
    swap = {}
    for j in range(h):
        swap[f"x{j}"], swap[f"y{j}"] = f"y{j}", f"x{j}"
    f_readers = {frozenset(swap.get(n, n) for n in r) for r in e_readers}
    e_sources = set()
    for anchor, options in (("g", ("x", "vy")), ("t", ("vx", "y"))):
        for choice in itertools.product(options, repeat=h):
            names = {anchor}
            for j, letters in enumerate(choice):
                names |= {f"{c}{j}" for c in letters}
            e_sources.add(frozenset(names))
    f_sources = {frozenset(swap.get(n, n) for n in s) for s in e_sources}
    return e_readers, f_readers, e_sources, f_sources


def phi_values(h, gamma, nus):
    """Values of the functional phi(E)=1, phi(F)=0, phi(G)=gamma, phi(V_j)=nu_j."""
    out = {"g": gamma, "d": 1, "t": 1 + gamma}
    for j in range(h):
        nu = nus[j]
        out[f"v{j}"] = nu
        out[f"x{j}"] = 1 + gamma - nu
        out[f"y{j}"] = gamma - nu
    return out


def circuit_of(reader):
    """Core queries plus hub kinds (a={v,x}, b={v,y}, c={x,y}) of an E-reader."""
    hubs = {}
    for name in reader:
        if name[0] in "vxy":
            hubs.setdefault(name[1:], set()).add(name[0])
    kind = {frozenset("vx"): "a", frozenset("vy"): "b", frozenset("xy"): "c"}
    return frozenset({q for q in reader if q in "gdt"} | {kind[frozenset(m)] for m in hubs.values()})


def check_costs_closed_form(h):
    """Every non-family row has an explicit cost-one evaluator (all h)."""
    e_readers, _, e_sources, _ = closed_form(h)
    family = 0
    for reader in e_readers:
        if circuit_of(reader) in FAMILY_CIRCUITS:
            family += 1
            continue
        # PROOF.md Lemma 5: phi(G) = 0 if g is present, else -1; every nu_j = 0.
        values = phi_values(h, 0 if "g" in reader else -1, [0] * h)
        if sum(1 for n in reader if values[n] != 0) != 1:
            raise AssertionError(f"no cost-one witness for {sorted(reader)}")
    for source in e_sources:
        gamma = 0 if "g" in source else -1
        nus = []
        for j in range(h):
            if gamma == 0:
                nus.append(1 if f"x{j}" in source else 0)
            else:
                nus.append(0 if f"x{j}" in source else -1)
        values = phi_values(h, gamma, nus)
        if any(values[n] != 0 for n in source) or values["g" if gamma == -1 else "t"] == 0:
            raise AssertionError(f"source functional wrong for {sorted(source)}")
        reader = {"g", "v0", "x0"} if gamma == 0 else {"t", "v0", "y0"}
        if frozenset(reader) not in e_readers:
            raise AssertionError("anchor reader missing")
        if sum(1 for n in reader if values[n] != 0) != 1:
            raise AssertionError(f"source {sorted(source)} has no cost-one reader")
    if family != h * (h + 1):
        raise AssertionError(f"family readers {family} != h(h+1)")
    return len(e_readers), len(e_sources)


# ---------------------------------------------------------------- census control


class Basis:
    """Reduced row echelon basis over Q, modified in place with undo."""

    def __init__(self):
        self.rows = []  # (pivot, row)
        self.saved = []

    def reduce(self, vec):
        v = list(vec)
        for pivot, row in self.rows:
            if v[pivot] != 0:
                f = v[pivot]
                v = [a - f * b for a, b in zip(v, row)]
        return v

    def insert(self, vec):
        v = self.reduce(vec)
        pivot = next((i for i, x in enumerate(v) if x != 0), None)
        if pivot is None:
            return False
        s = v[pivot]
        v = [Fraction(x) / s for x in v]
        new_rows = []
        for p, row in self.rows:
            if row[pivot] != 0:
                f = row[pivot]
                row = [a - f * b for a, b in zip(row, v)]
            new_rows.append((p, row))
        self.saved.append(self.rows)
        self.rows = new_rows + [(pivot, v)]
        return True

    def undo(self):
        self.rows = self.saved.pop()


def in_span_with(rE, rO):
    """E in span(S, O) given reductions of E and O against the basis of S."""
    if not any(rE):
        return True
    if not any(rO):
        return False
    k = next(i for i, x in enumerate(rO) if x != 0)
    c = Fraction(rE[k]) / rO[k]
    return all(Fraction(a) == c * b for a, b in zip(rE, rO))


def census(h):
    names, vecs, E, F = star(h)
    n = len(names)
    spans = [bytearray(1 << n), bytearray(1 << n)]       # mark in span(S)
    outside = [bytearray(1 << n), bytearray(1 << n)]     # mark not in span(S, other)
    basis = Basis()

    def walk(i, mask):
        if i == n:
            rE, rF = basis.reduce(E), basis.reduce(F)
            spans[0][mask] = not any(rE)
            spans[1][mask] = not any(rF)
            outside[0][mask] = not in_span_with(rE, rF)
            outside[1][mask] = not in_span_with(rF, rE)
            return
        walk(i + 1, mask)
        inserted = basis.insert(vecs[i])
        walk(i + 1, mask | (1 << i))
        if inserted:
            basis.undo()

    walk(0, 0)
    readers, sources = [set(), set()], [set(), set()]
    for mask in range(1 << n):
        members = [i for i in range(n) if mask >> i & 1]
        for m in (0, 1):
            if spans[m][mask] and mask and all(not spans[m][mask ^ (1 << i)] for i in members):
                readers[m].add(frozenset(names[i] for i in members))
            if outside[m][mask] and all(not outside[m][mask | (1 << i)]
                                        for i in range(n) if not mask >> i & 1):
                sources[m].add(frozenset(names[i] for i in members))
    return names, vecs, E, F, readers, sources


def separated(vecs_by_name, killed, mark, other):
    basis = Basis()
    for name in killed:
        basis.insert(vecs_by_name[name])
    return not in_span_with(basis.reduce(mark), basis.reduce(other))


def min_paid(vecs_by_name, fixed, reader, mark, other):
    reader = sorted(reader)
    for size in range(0, len(reader) + 1):
        for paid in itertools.combinations(reader, size):
            killed = list(fixed) + [q for q in reader if q not in paid]
            if separated(vecs_by_name, killed, mark, other):
                return size
    raise AssertionError("no admissible evaluator")


def census_charge(h):
    names, vecs, E, F, readers, sources = census(h)
    expect = closed_form(h)
    if (readers[0], readers[1], sources[0], sources[1]) != expect:
        raise AssertionError(f"h={h} census differs from the closed-form table")
    by_name = dict(zip(names, vecs))
    total = 0
    two = 0
    for m, (mark, other) in enumerate(((E, F), (F, E))):
        for reader in readers[m]:
            cost = min_paid(by_name, (), reader, mark, other)
            total += cost
            two += cost == 2
            if cost not in (1, 2):
                raise AssertionError(cost)
        for source in sources[m]:
            cost = min(min_paid(by_name, source, r, mark, other) for r in readers[m])
            if cost != 1:
                raise AssertionError(f"h={h} source cost {cost}")
            total += cost
    rows = sum(map(len, readers)) + sum(map(len, sources))
    return rows, 2 * total, two


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hmax", type=int, default=4)
    parser.add_argument("--closed-form-hmax", type=int, default=12)
    args = parser.parse_args()
    check_core()
    check_sources_local()
    for h in range(1, args.closed_form_hmax + 1):
        readers, sources = check_costs_closed_form(h)
        if readers != 3 * h * (h + 1) or sources != 2 ** (h + 1):
            raise AssertionError((h, readers, sources))
    report = []
    for h in range(1, args.hmax + 1):
        rows, charge, two = census_charge(h)
        if rows != 2 * (3 * h * (h + 1) + 2 ** (h + 1)):
            raise AssertionError((h, rows))
        if charge != 16 * h * (h + 1) + 2 ** (h + 3) or charge - 2 * rows != 4 * h * (h + 1):
            raise AssertionError((h, charge))
        if two != 2 * h * (h + 1):
            raise AssertionError((h, two))
        report.append(f"h{h}:rows={rows},charge={charge},excess={charge - 2 * rows}")
    print(PASS, "core_circuits=9", f"closed_form_h<={args.closed_form_hmax}",
          f"census_h<={args.hmax}", *report, "no_new_kappa")


if __name__ == "__main__":
    main()
