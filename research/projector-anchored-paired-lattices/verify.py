"""Exact corroboration of projector-anchored paired-lattice completeness.

Produced by Nick Petalas. Apache-2.0. No predecessor executable is imported.
"""

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from check import check  # noqa: E402
from lattice import solve, validate  # noqa: E402
from linear import (block_at, identity, inverse, multiply, paired, power_two,
                    require, upper, valuation, zero)  # noqa: E402


def projectors(size):
    return tuple(tuple(tuple(Fraction(r == i == c) for c in range(size))
                       for r in range(size)) for i in range(size))


def conjugate(value, basis):
    return multiply(multiply(basis, value), inverse(basis))


def problem(basis, blocks):
    size = len(basis)
    anchors = tuple(conjugate(p, basis) for p in projectors(size))
    applied = tuple(upper(p) for p in anchors) + tuple(
        upper(conjugate(a, basis)) for a in blocks)
    return validate(anchors, applied)


def graph_oracle(weights):
    # Independent min-plus closure on the originally specified graph.
    size = len(weights)
    distance = [[0 if i == j else None for j in range(size)] for i in range(size)]
    for target in range(size):
        for source in range(size):
            weight = weights[target][source]
            if weight is not None:
                old = distance[source][target]
                distance[source][target] = weight if old is None else min(old, weight)
    for middle in range(size):
        for source in range(size):
            for target in range(size):
                left, right = distance[source][middle], distance[middle][target]
                if left is not None and right is not None:
                    old = distance[source][target]
                    distance[source][target] = left + right if old is None else min(old, left + right)
    return all(distance[i][i] >= 0 for i in range(size))


def placements(block):
    size = len(block)
    values = [upper(block)]
    values.append(tuple(tuple(Fraction(i == j) + (block[i - size][j]
                        if j < size <= i else 0)
                        for j in range(2 * size)) for i in range(2 * size)))
    if block[0][0] * block[1][1] != block[0][1] * block[1][0]:
        for half in range(2):
            values.append(tuple(tuple(block[i % size][j % size]
                          if i // size == j // size == half else Fraction(i == j)
                          for j in range(2 * size)) for i in range(2 * size)))
    return values


def graph_corpus():
    charts = (identity(2), ((1, 1), (1, -1)),
              ((1, Fraction(1, 2)), (0, 1)),
              ((Fraction(1, 3), 1), (1, Fraction(2, 5))))
    counts = {"graphs": 0, "chart_problems": 0, "feasible": 0, "infeasible": 0}
    for entries in product((None, -1, 0, 1), repeat=4):
        weights = (entries[:2], entries[2:])
        expected = graph_oracle(weights)
        bounded = any(all(weights[i][j] is None or a[i] - a[j] <= weights[i][j]
                          for i in range(2) for j in range(2))
                      for a in ((0, -1), (0, 0), (0, 1)))
        require(expected == bounded, "closure disagrees with complete normalized potentials")
        block = tuple(tuple(Fraction(0) if x is None else power_two(x) for x in row)
                      for row in weights)
        counts["graphs"] += 1
        for chart in charts:
            anchors, base = problem(chart, ())
            for placement in placements(block):
                applied = base + (conjugate(placement, paired(chart)),)
                certificate = solve(anchors, applied)
                observed = check(anchors, applied, certificate)
                require(observed == expected, "anchored test disagrees with graph oracle")
                counts["chart_problems"] += 1
                counts["feasible" if observed else "infeasible"] += 1
    return counts


def walsh(size):
    return tuple(tuple(Fraction(-1 if (i & j).bit_count() % 2 else 1)
                       for j in range(size)) for i in range(size))


def walsh_separation():
    rows = []
    for size in (2, 4, 8):
        basis = walsh(size)
        anchors, applied = problem(basis, ())
        require(all(p[i][i] == Fraction(1, size) for p in anchors for i in range(size)),
                "Walsh diagonal formula")
        require(all(valuation(p[i][i]) < 0 for p in anchors for i in range(size)),
                "standard diagonal-gauge self-loop obstruction")
        certificate = solve(anchors, applied)
        require(check(anchors, applied, certificate), "non-diagonal lattice rejected")
        endpoint = identity(2 * size)
        for gate in applied:
            endpoint = multiply(gate, endpoint)
        require(endpoint == upper(identity(size)), "complete paid label is not n_I")
        change = paired(basis)
        require(multiply(multiply(inverse(change), endpoint), change) == endpoint,
                "paired basis changed unit target")
        rows.append({"dimension": size, "paid_rank": size,
                     "diagonal_obstruction_valuation": -((size - 1).bit_length()),
                     "certificate_exponents": certificate["exponents"]})
    return rows


def rejection(call, message):
    try:
        call()
    except (ValueError, TypeError):
        return 1
    raise ValueError("accepted invalid control: " + message)


def controls():
    anchors, applied = problem(identity(2), (((0, Fraction(1, 2)), (0, 0)),))
    positive = solve(anchors, applied)
    require(check(anchors, applied, positive), "positive control")
    cases = []
    bad = deepcopy(positive)
    bad["exponents"] = [0, 0]
    cases.append((lambda: check(anchors, applied, bad), "omitted precision shift"))
    bad_basis = deepcopy(positive)
    bad_basis["basis"] = ((1, 1), (1, 2))
    cases.append((lambda: check(anchors, applied, bad_basis), "wrong eigenbasis"))
    bad_type = deepcopy(positive)
    bad_type["exponents"] = [False, 1]
    cases.append((lambda: check(anchors, applied, bad_type), "Boolean exponent"))
    cyclic = applied + (upper(((0, 0), (Fraction(1, 2), 0))),)
    negative = solve(anchors, cyclic)
    require(not check(anchors, cyclic, negative), "negative-cycle control")
    bad_cycle = deepcopy(negative)
    bad_cycle["entries"] = [[0, 0, 0]]
    cases.append((lambda: check(anchors, cyclic, bad_cycle), "nonnegative cycle"))
    disconnected = deepcopy(negative)
    disconnected["entries"] = disconnected["entries"][:1]
    cases.append((lambda: check(anchors, cyclic, disconnected), "unclosed cycle"))
    cases.append((lambda: solve(anchors, applied[:1]), "unapplied anchor"))
    cases.append((lambda: check(anchors, applied[:1], positive), "checker unapplied anchor"))
    cases.append((lambda: solve((anchors[0], anchors[0]), applied), "duplicate anchors"))
    cases.append((lambda: solve((identity(2), zero(2)), applied), "higher-rank anchor"))
    cases.append((lambda: solve(anchors[:1], applied), "incomplete anchor family"))
    cases.append((lambda: solve(anchors, (upper(((0, 0.5), (0, 0))),)), "float input"))
    cases.append((lambda: solve(anchors * 5, applied), "dimension limit"))
    cases.append((lambda: solve(anchors, applied * 22), "applied-matrix limit"))
    count = sum(rejection(call, message) for call, message in cases)
    # Dropping the offending applied inverse changes the problem, not the theorem.
    free = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 2, 0), (0, 0, 0, 1))
    require(check(anchors, applied + (free,), solve(anchors, applied + (free,))),
            "singular reduction must remain allowed")
    with_inverse = applied + (free, inverse(free))
    require(not check(anchors, with_inverse, solve(anchors, with_inverse)),
            "applied inverse omitted")
    even_hd = block_at(upper(((2, 0), (0, 2))), 0, 1, 2)
    require(all(not x or valuation(x) > 0 for row in even_hd for x in row),
            "even target has nonzero mod-two HD block")
    return {"rejected": count, "scope_controls": 3}


def source_hashes():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    root = PACKAGE.parents[1]
    for row in manifest["files"]:
        if row["usage"] == "input":
            require(sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "changed predecessor text")
    return {p.name: sha256(p.read_bytes()).hexdigest()
            for p in sorted(PACKAGE.iterdir()) if p.is_file()}


def main():
    require(len(sys.argv) == 1, "this verifier accepts no arguments")
    hashes = source_hashes()
    report = {"status": "PASS_PROJECTOR_ANCHORED_PAIRED_LATTICES",
              "claim_type": "scoped proof with finite corroboration",
              "graphs": graph_corpus(), "walsh_separation": walsh_separation(),
              "controls": controls(), "package_sha256": hashes,
              "python": sys.version.split()[0]}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
