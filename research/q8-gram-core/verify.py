"""Bounded exact checks for the written Gram normal-form theorem.

Nick Petalas, Apache-2.0. Finite checks do not replace the uniform proof.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gram
from linear import apply, basis, column, coordinates, identity, multiply, parity, rank, require
import model
import oracle
import system

ROOT = Path(__file__).resolve().parent


def formal_output(formal, vector):
    rows = []
    for row in formal:
        value = 0
        for j, coefficient in enumerate(row):
            if vector & (1 << j):
                value ^= coefficient
        rows.append(value)
    return tuple(sum(((value >> g) & 1) << j for j, value in enumerate(rows)) for g in range(8))


def check_word(gates, roles, counts):
    m = model.gram(gates, roles)
    labels = tuple(g.label for g in gates)
    core, reduced = gram.normal_form(m, labels)
    require(model.gram(core, reduced) == m, "Gram roundtrip")
    require(reduced == rank(m), "core dimension")
    original, smaller = model.endpoint(gates, roles), model.endpoint(core, reduced)
    require(original == oracle.endpoint(gates, roles), "Hamilton endpoint")
    for j in range(8 * roles):
        expected = tuple(model.ring_product(original[a][j // 8], 1 << (j % 8)) for a in range(roles))
        require(oracle.action(gates, roles, j) == expected, "faithful dirty column")
        counts["dirty_columns"] += 1
    u_basis = basis(tuple(g.u for g in gates), roles)
    m_basis = basis(tuple(column(m, j) for j in range(len(m))), len(m))
    y = tuple(g.v for g in gates)
    for vector in u_basis:
        projected = coordinates(m_basis, apply(y, vector), len(m))
        for gate, image in zip(gates, core, strict=True):
            old = gate.u if parity(gate.v & vector) else 0
            left = coordinates(m_basis, apply(y, old), len(m))
            right = image.u if parity(image.v & projected) else 0
            require(left == right, "intertwining each ordered call")
            counts["call_intertwining"] += 1
        left = tuple(coordinates(m_basis, apply(y, value), len(m))
                     for value in formal_output(original, vector))
        require(left == formal_output(smaller, projected), "full coefficient quotient")
        counts["coefficient_quotients"] += 8
    counts["words"] += 1


def short_words(counts):
    for roles, depth in ((2, 3), (3, 2)):
        alphabet = tuple(model.Gate(label, u, v) for label in (2, 4)
                         for u in range(1, 1 << roles) for v in range(1, 1 << roles)
                         if parity(u & v))
        for length in range(depth + 1):
            for gates in itertools.product(alphabet, repeat=length):
                check_word(gates, roles, counts)


def varied_words(counts):
    rng = random.Random(10483487)
    for sample in range(192):
        roles, length = 1 + sample % 8, 1 + sample % 12
        gates = []
        for _ in range(length):
            u, v = rng.randrange(1, 1 << roles), rng.randrange(1 << roles)
            if not parity(u & v):
                v ^= u & -u
            gates.append(model.Gate(rng.choice((2, 4)), u, v))
        check_word(tuple(gates), roles, counts)
    # A diagonal identity endpoint where the simultaneous reduction is strict.
    gates = (model.Gate(2, 1, 3), model.Gate(2, 2, 7)) * 4
    require(model.endpoint(gates, 3) == ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "identity fixture")
    require(rank(tuple(g.u for g in gates)) == rank(tuple(g.v for g in gates)) == 2, "old reductions")
    require(rank(model.gram(gates, 3)) == 1, "strict core reduction")
    check_word(gates, 3, counts)


def direct_fixtures(counts):
    for roles in (3, 4, 7):
        active = (0, 1, roles - 1)
        for labels in itertools.product((2, 4), repeat=3):
            for corrections in itertools.product((2, 4), repeat=3):
                gates = []
                for role, label, correction in zip(active, labels, corrections, strict=True):
                    gates.extend((model.Gate(label, 1 << role, 1 << role),
                                  model.Gate(correction, 1 << role, 1 << role),
                                  model.Gate(correction, 1 << role, 1 << role)))
                m, ordered = model.gram(gates, roles), tuple(g.label for g in gates)
                si, sj = labels.count(2), labels.count(4)
                require(gram.negative_target(m, ordered, si, sj), "direct Gram positive control")
                require(system.build(9, si, sj).evaluate(m, ordered), "direct symbolic positive control")
                square = multiply(m, m)
                require(multiply(square, m) == square and rank(square) == 3, "spectral identity")
                require(rank(m) == 3, "no essential spectator in direct word")
                check_word(tuple(gates), roles, counts)
                counts["direct_endpoints"] += 1


def matrices(size, diagonal):
    positions = tuple((a, b) for a in range(size) for b in range(size) if not diagonal or a != b)
    for mask in range(1 << len(positions)):
        rows = list(identity(size)) if diagonal else [0] * size
        for j, (a, b) in enumerate(positions):
            if mask & (1 << j):
                rows[a] |= 1 << b
        yield tuple(rows)


def exhaustive_criterion(counts):
    for n in range(1, 4):
        systems = {(a, b): system.build(n, a, b) for a in range(n + 1) for b in range(n + 1)}
        for rows in matrices(n, True):
            for labels in itertools.product((2, 4), repeat=n):
                core, roles = gram.normal_form(rows, labels)
                require(model.gram(core, roles) == rows, "candidate reconstruction")
                expected = oracle.eigen_counts(oracle.endpoint(core, roles))
                for target, circuit in systems.items():
                    actual = gram.negative_target(rows, labels, *target)
                    require(actual == (expected == target), "independent binary eigenspaces")
                    require(circuit.evaluate(rows, labels) == actual, "symbolic criterion")
                    counts["criterion_valuations"] += 1
                counts["gram_candidates"] += 1


def exhaustive_rank(counts):
    for n in range(1, 4):
        circuits = []
        for wanted in range(n + 1):
            c = system.Circuit(n)
            rows = tuple(c.node("row", a) for a in range(n))
            c.equal((c.rank(rows),), (c.const(wanted),))
            circuits.append(c)
        for rows in matrices(n, False):
            span = {0}
            for row in rows:
                span |= {value ^ row for value in tuple(span)}
            expected = len(span).bit_length() - 1
            for wanted, c in enumerate(circuits):
                require(c.evaluate(rows, (2,) * n) == (wanted == expected), "rank circuit")
                counts["rank_valuations"] += 1


def source_hashes():
    names = ("linear.py", "model.py", "gram.py", "oracle.py", "system.py", "verify.py",
             "test_package.py", "PROOF.md", "README.md", "VALIDATION.md", "inputs/RETENTION.json",
             "inputs/pr3487-PROOF.md")
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}


def replay():
    retention = json.loads((ROOT / "inputs/RETENTION.json").read_text())
    require(hashlib.sha256((ROOT / "inputs/pr3487-PROOF.md").read_bytes()).hexdigest()
            == retention["sha256"], "retained predecessor bytes")
    require(all(model.group_product(a, b) == oracle.product(a, b)
                for a in range(8) for b in range(8)), "independent group table")
    counts = dict.fromkeys(("words", "dirty_columns", "call_intertwining", "coefficient_quotients",
                           "direct_endpoints", "gram_candidates", "criterion_valuations", "rank_valuations"), 0)
    short_words(counts)
    varied_words(counts)
    direct_fixtures(counts)
    exhaustive_criterion(counts)
    exhaustive_rank(counts)
    exports = {}
    for target in ((3, 0), (2, 1)):
        circuit = system.build(7, *target)
        raw = circuit.smt(60_000).encode()
        exports[str(target)] = {"nodes": len(circuit.nodes), "equations": len(circuit.assertions),
                                "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return {"status": "PASS_GRAM_CORE_FINITE_CHECKS", "scope": "Written uniform theorem plus bounded exact controls; no seven-call exclusion.",
            "counts": counts, "seven_call_exports": exports, "source_sha256": source_hashes()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = replay()
    if args.write_result is not None:
        with args.write_result.open("x", encoding="utf-8") as stream:
            require(stream.write(json.dumps(result, indent=2) + "\n") > 0, "receipt write")
    else:
        require(result == json.loads((ROOT / "RESULT.json").read_text()), "published receipt mismatch")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}))


if __name__ == "__main__":
    main()
