"""Exact finite corroboration. Produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def connected(n, edges):
    seen = {0}
    for _ in range(n):
        for source, target in edges:
            if source in seen or target in seen:
                seen.update((source, target))
    return len(seen) == n


def vertex_gauges(n, p, edges, labels):
    """Return root-normalized gauges, or None for inconsistent labels."""
    require(2 <= n <= 4 and p in (3, 5), "unsupported finite domain")
    require(len(edges) == len(labels) <= n*(n-1), "edge count")
    require(len(set(edges)) == len(edges), "duplicate edge")
    require(all(0 <= a < n and 0 <= b < n and a != b for a, b in edges),
            "invalid directed edge")
    require(all(1 <= b < p for b in labels), "invalid label")
    require(connected(n, edges), "disconnected graph")
    weights = [None] * n
    weights[0] = 1
    for _ in range(n):
        for (source, target), b in zip(edges, labels):
            if weights[source] is not None:
                candidate = b * weights[source] % p
                if weights[target] is not None and weights[target] != candidate:
                    return None
                weights[target] = candidate
            elif weights[target] is not None:
                weights[source] = pow(b, -1, p) * weights[target] % p
    require(all(w is not None for w in weights), "propagation incomplete")
    require(all(weights[t] == b * weights[s] % p
                for (s, t), b in zip(edges, labels)), "bad gauge output")
    return tuple(weights)


def additive(table, addition):
    q = len(table)
    return all(table[addition[x][y]] == addition[table[x]][table[y]]
               for x in range(q) for y in range(q))


def gate_table(p, maps):
    # Exhaust the literal equation independently of graph propagation.
    return tuple(tuple(tuple(all(target[(x+y) % p]
                                 == (target[x]+b*source[y]) % p
                                 for x in range(p) for y in range(p))
                             for b in range(1, p)) for source in maps)
                 for target in maps)


def graph_census(p, graphs):
    maps = tuple((0,) + tail for tail in permutations(range(1, p)))
    addition = tuple(tuple((x+y) % p for y in range(p)) for x in range(p))
    is_additive = tuple(additive(f, addition) for f in maps)
    gates = gate_table(p, maps)
    counts = {"graphs": 0, "cases": 0, "compatible": 0}
    for edges in graphs:
        candidates = tuple((labels, vertex_gauges(3, p, edges, labels))
                           for labels in product(range(1, p), repeat=len(edges)))
        successes = 0
        for ids in product(range(len(maps)), repeat=3):
            chosen = tuple(maps[k] for k in ids)
            h = chosen[0]
            for labels, weights in candidates:
                actual = all(gates[ids[t]][ids[s]][b-1]
                             for (s, t), b in zip(edges, labels))
                predicted = weights is not None and is_additive[ids[0]] and all(
                    chosen[v][x] == weights[v]*h[x] % p
                    for v in range(3) for x in range(p))
                require(actual == predicted, "graph classification mismatch")
                counts["cases"] += 1
                successes += actual
        require(successes == (p-1)**3, "unexpected compatible count")
        counts["graphs"] += 1
        counts["compatible"] += successes
    return counts


def f9_tables():
    # a+3b denotes a+b*i, i^2=-1 over F3.
    add = tuple(tuple((x % 3+y % 3) % 3 + 3*((x//3+y//3) % 3)
                      for y in range(9)) for x in range(9))
    mul = tuple(tuple(((x % 3)*(y % 3)-(x//3)*(y//3)) % 3
                      + 3*(((x % 3)*(y//3)+(x//3)*(y % 3)) % 3)
                      for y in range(9)) for x in range(9))
    return add, mul


def extension_census():
    add, mul = f9_tables()
    counts = {"permutations": 0, "additive": 0, "phase": 0, "both": 0}
    phase_only = None
    for tail in permutations(range(1, 9)):
        f = (0,) + tail
        a = additive(f, add)
        phase = all(f[mul[3][x]] == mul[3][f[x]] for x in range(9))
        counts["permutations"] += 1
        counts["additive"] += a
        counts["phase"] += phase
        counts["both"] += a and phase
        if a and phase:
            require(all(f[x] == mul[f[1]][x] for x in range(9)),
                    "phase-compatible additive map is not scalar")
        if phase and not a:
            phase_only = f
    require(tuple(counts.values()) == (40320, 48, 32, 8), "F9 census")
    require(phase_only is not None, "missing phase-only witness")
    frobenius = tuple(mul[mul[x][x]][x] for x in range(9))
    require(additive(frobenius, add), "Frobenius not additive")
    require(frobenius[3] != mul[3][frobenius[1]], "missing phase counterexample")
    return counts, phase_only, frobenius


def q(a=0, b=0, c=0, d=0):
    """Exact a+b*i+c*sqrt(2)+d*i*sqrt(2)."""
    return tuple(F(x) for x in (a, b, c, d))


def plus(x, y):
    return tuple(a+b for a, b in zip(x, y))


def times(x, y):
    a, b, c, d = x
    e, f, g, h = y
    return (a*e-b*f+2*(c*g-d*h), a*f+b*e+2*(c*h+d*g),
            a*g-b*h+c*e-d*f, a*h+b*g+c*f+d*e)


def common_h(x):
    return x[0], x[1], -x[2], -x[3]


def algebra_controls():
    # Independent monomial multiplication modulo i^2+1 and sqrt(2)^2-2.
    basis = ((0, 0), (1, 0), (0, 1), (1, 1))
    values = (q(), q(1), q(0, 1), q(c=1), q(d=1), q(1, 1),
              q(F(1, 2), F(-1, 2)), q(2, -3, 5, -7), q(F(1, 3), 0, F(-2, 5)))
    pairs = 0
    for x, y in product(values, repeat=2):
        expected = [F(0)] * 4
        for a, (i, r) in enumerate(basis):
            for b, (j, s) in enumerate(basis):
                at = basis.index(((i+j) % 2, (r+s) % 2))
                expected[at] += x[a]*y[b]*(-1)**((i+j)//2)*2**((r+s)//2)
        require(times(x, y) == tuple(expected), "extension multiplication")
        pairs += 1
    return pairs


def recode(state, inverse=False, nonlinear=True):
    weights = (q(1, 1), q(2), q(0, -1))
    inverses = (q(F(1, 2), F(-1, 2)), q(F(1, 2)), q(0, 1))
    out = []
    for v in range(3):
        row = []
        for x in state[v]:
            value = times(inverses[v], x) if inverse else x
            if nonlinear:
                value = common_h(value)
            row.append(value if inverse else times(weights[v], value))
        out.append(tuple(row))
    return tuple(out)


def run_word(state, changed_coefficients=False):
    weights = (q(1, 1), q(2), q(0, -1))
    inverses = (q(F(1, 2), F(-1, 2)), q(F(1, 2)), q(0, 1))
    c = q(F(1, 2), F(-1, 2))
    zero = q()
    word = (("add", 0, 1), ("native", 1, ((c, c), (c, times(q(-1), c)))),
            ("add", 1, 2), ("native", 0, ((q(1), zero), (zero, q(0, 1)))),
            ("add", 2, 0), ("native", 2, ((q(1), zero), (zero, q(F(1, 2))))),
            ("add", 0, 1))
    current = list(state)
    for kind, source, target in word:
        if kind == "add":
            b = times(weights[target], inverses[source]) if changed_coefficients else q(1)
            current[target] = tuple(plus(x, times(b, y))
                                    for x, y in zip(current[target], current[source]))
        else:
            old = current[source]
            current[source] = tuple(plus(times(row[0], old[0]), times(row[1], old[1]))
                                    for row in target)
    return tuple(current)


def exact_native_census():
    require(common_h(q(1)) == q(1) and common_h(q(c=1)) == q(c=-1),
            "non-scalar additive fixture")
    fixtures = []
    for position in range(6):
        for component in range(4):
            state = [q()] * 6
            basis = [0] * 4
            basis[component] = 1
            state[position] = q(*basis)
            fixtures.append(tuple((state[2*v], state[2*v+1]) for v in range(3)))
    for k in range(24):
        row = tuple(q(F(k-j, j+1), F(k+j, 3), F(j-2*k, 5), F(k*j-1, 7))
                    for j in range(6))
        fixtures.append(tuple((row[2*v], row[2*v+1]) for v in range(3)))
    for state in fixtures:
        nonlinear = recode(run_word(recode(state, inverse=True)))
        scalar = recode(run_word(recode(state, inverse=True, nonlinear=False)),
                        nonlinear=False)
        direct = run_word(state, changed_coefficients=True)
        require(nonlinear == scalar == direct, "native conjugacy mismatch")
        require(recode(recode(state), inverse=True) == state, "inverse recoding")
    return {"fixtures": len(fixtures), "output_scalars": 6*len(fixtures),
            "rational_components": 24*len(fixtures), "events_per_fixture": 7}


def controls():
    cases = ((3, 5, (), ()), (3, 5, ((0, 0),), (1,)),
             (2, 5, ((0, 1),), (0,)), (2, 5, ((0, 1), (0, 1)), (1, 1)))
    count = 0
    for args in cases:
        try:
            vertex_gauges(*args)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid graph accepted")
    cycle = ((0, 1), (1, 2), (2, 0))
    require(vertex_gauges(3, 5, cycle, (1, 1, 2)) is None, "cycle obstruction")
    count += 1
    # Removing zero preservation permits a translation on a sink.
    require(all((x+y+1) % 5 == ((x+1) % 5+y) % 5
                for x in range(5) for y in range(5)), "sink translation")
    count += 1
    nonadditive = (0, 2, 1, 3, 4)
    add = tuple(tuple((x+y) % 5 for y in range(5)) for x in range(5))
    require(not connected(3, ((0, 1),)) and not additive(nonadditive, add),
            "disconnected nonadditive fixture")
    count += 1
    maps = ((0, 1, 2, 3, 4), (0, 2, 4, 1, 3))
    require(not gate_table(5, maps)[1][0][2], "reversed edge ratio accepted")
    count += 1
    # A non-pointwise address swap does not commute with diag(1,2).
    x = (1, 2)
    left = (2*x[1], x[0])
    right = (x[1], 2*x[0])
    require(left != right, "block-map boundary control")
    count += 1
    return count


def main():
    require(len(sys.argv) == 1, "no command-line arguments are supported")
    arcs = tuple((s, t) for s in range(3) for t in range(3) if s != t)
    graphs = tuple(tuple(arcs[j] for j in range(6) if mask >> j & 1)
                   for mask in range(64))
    graphs = tuple(g for g in graphs if connected(3, g))
    f3 = graph_census(3, graphs)
    f5 = graph_census(5, (((0, 1), (1, 2)), ((0, 1), (1, 2), (2, 0))))
    f9, phase_only, frobenius = extension_census()
    arithmetic_pairs = algebra_controls()
    exact = exact_native_census()
    boundary_controls = controls()
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    root = Path(__file__).resolve().parent
    receipt = {"status": "PASS_NONLINEAR_ROLE_RECODING", "F3": f3, "F5": f5,
               "F9": f9, "phase_only_witness": phase_only, "frobenius": frobenius,
               "arithmetic_pairs": arithmetic_pairs,
               "exact_native": exact, "boundary_controls": boundary_controls,
               "sha256": {name: sha256((root/name).read_bytes()).hexdigest() for name in files}}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
