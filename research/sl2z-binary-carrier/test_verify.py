#!/usr/bin/env python3
"""Separate AI review: independent finite semantics and damaged-input controls.

The core checks do not import verify.py or call its matrix/group algorithms.
This is executable finite evidence, not independent human or kernel review.
"""

import ast
from collections import Counter, deque
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def constants():
    names = {"X", "Y", "B", "U", "V", "TARGET", "BASIS", "U_GATES", "V_GATES", "B_GATES"}
    found = {}
    for node in ast.parse((ROOT / "verify.py").read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in names:
                need(target.id not in found, "duplicate declared constant")
                found[target.id] = ast.literal_eval(node.value)
    need(set(found) == names, "missing declared constants")
    return found


def compose(p, q):
    """Truth-table composition; q acts first."""
    return tuple(p[q[x]] for x in range(len(p)))


def perm_power(p, count):
    value = tuple(range(len(p)))
    for _ in range(count):
        value = compose(p, value)
    return value


def inverse(p):
    return tuple(p.index(x) for x in range(len(p)))


def linear_table(matrix, width):
    masks = tuple(sum(matrix[width * i + j] << j for j in range(width))
                  for i in range(width))
    return tuple(sum(((mask & x).bit_count() % 2) << i
                     for i, mask in enumerate(masks)) for x in range(1 << width))


def gate_table(gates, width):
    table = []
    for x in range(1 << width):
        for destination, source in gates:
            need(destination != source and min(destination, source) >= 0
                 and max(destination, source) < width, "invalid declared gate")
            x ^= ((x >> source) & 1) << destination
        table.append(x)
    return tuple(table)


def projective_and_basis(c):
    # Projective points are sets of two nonzero scalar multiples, avoiding
    # the production verifier's normalization and coordinate algorithms.
    representatives = ((1, 0), (0, 1), (1, 1), (1, 2))
    points = tuple(frozenset(((x, y), (2 * x % 3, 2 * y % 3)))
                   for x, y in representatives)
    masks = (0b1010, 0b1111, 0b0110)
    need(c["BASIS"] == tuple(tuple((m >> j) & 1 for j in range(4)) for m in masks),
         "declared basis changed")
    coordinate = {}
    for bits in range(8):
        z = 0
        for i, mask in enumerate(masks):
            if (bits >> i) & 1:
                z ^= mask
        need(z not in coordinate, "dependent basis")
        coordinate[z] = bits
    need(set(coordinate) == {x for x in range(16) if x.bit_count() % 2 == 0},
         "basis is not all of W")
    actions = []
    for label, expected in (("X", (0, 2, 3, 1)), ("Y", (2, 1, 3, 0))):
        a, b, d, e = c[label]
        permutation = tuple(next(j for j, point in enumerate(points)
                                 if ((a * x + b * y) % 3, (d * x + e * y) % 3) in point)
                            for x, y in representatives)
        need(permutation == expected, label + " projective action differs")
        action = []
        for z, bits in coordinate.items():
            image = sum(((z >> i) & 1) << permutation[i] for i in range(4))
            action.append((bits, coordinate[image]))
        actions.append(tuple(dict(action)[i] for i in range(8)))
    u, v = actions
    need(u == linear_table(c["U"], 3) and v == linear_table(c["V"], 3),
         "declared matrices differ from independently constructed action")
    target = compose(perm_power(u, 2), perm_power(v, 2))
    need(target == tuple(x ^ (((x >> 2) & 1) << 1) for x in range(8)),
         "projective target is not b ^= c")
    need(target == linear_table(c["TARGET"], 3), "declared target changed")
    need(compose(u, v) != compose(v, u), "image is commutative")
    need(perm_power(u, 3) == perm_power(v, 3) == tuple(range(8)), "generator order changed")
    return u, v, target


def dimension_two_control():
    # GL2(F2) acts faithfully on its three nonzero vectors. Work directly
    # in S3 rather than enumerate 2x2 matrices as the production verifier does.
    group = tuple(permutations(range(3)))
    unit = (0, 1, 2)
    order = {p: next(k for k in range(1, 7) if perm_power(p, k) == unit) for p in group}
    need(Counter(order.values()) == {1: 1, 2: 3, 3: 2}, "S3 order classification failed")
    admitted = []
    for u, v in product(group, repeat=2):
        vi = inverse(v)
        braid = compose(compose(u, vi), u) == compose(compose(vi, u), vi)
        conjugate = any(compose(compose(s, u), inverse(s)) == vi for s in group)
        if braid and conjugate:
            need(compose(perm_power(u, 2), perm_power(v, 2)) == unit,
                 "a two-dimensional necessary-relation image detects B")
            admitted.append((u, v))
    need(len(admitted) == 12, "unexpected S3 relation-pair count")
    return len(admitted)


def native_bfs_and_dirty(c, u, v, target):
    # BFS through truth tables under all six directed CNOTs certifies the
    # complete 168-element GL3 metric independently of changed-row bounds.
    elementary = tuple(gate_table(((i, j),), 3) for i in range(3) for j in range(3) if i != j)
    unit = tuple(range(8))
    distances = {unit: 0}
    queue = deque((unit,))
    while queue:
        current = queue.popleft()
        for gate in elementary:
            following = compose(gate, current)
            if following not in distances:
                distances[following] = distances[current] + 1
                queue.append(following)
    need(len(distances) == 168, "CNOT closure is not GL3(F2)")
    need((distances[u], distances[v], distances[target]) == (2, 3, 1), "native minima differ")
    ug, vg, tg = c["U_GATES"], c["V_GATES"], c["B_GATES"]
    need(gate_table(ug, 3) == u and gate_table(vg, 3) == v and gate_table(tg, 3) == target,
         "declared chronological programs differ from genuine action")
    four = vg + vg + ug + ug
    two = tuple(reversed(vg)) + tuple(reversed(ug))
    need((len(four), len(two), len(tg)) == (10, 5, 1), "raw gate invoice differs")
    for gates in (four, two, tg):
        table6 = gate_table(gates, 6)
        need(table6 == tuple((x & 0b111000) | target[x & 7] for x in range(64)),
             "six-bit dirty endpoint or spectator preservation failed")
        # Column-major triples represent arbitrary 3x3 matrices. Audit all
        # 2^18 dirty inputs after calculating each nine-bit gate truth table.
        lifted = tuple((destination + 3 * column, source + 3 * column)
                       for column in range(3) for destination, source in gates)
        table9 = gate_table(lifted, 9)
        desired9 = tuple(sum(target[(x >> (3 * column)) & 7] << (3 * column)
                             for column in range(3)) for x in range(512))
        need(table9 == desired9, "arbitrary matrix left-action failed")
        need(all((x & ~511) | table9[x & 511] == (x & ~511) | desired9[x & 511]
                 for x in range(1 << 18)), "eighteen-bit dirty endpoint failed")
    return dict(sorted(Counter(distances.values()).items()))


def vector_rank(columns):
    # Enumerate the binary span, independent of production elimination.
    span = {0}
    for column in columns:
        span |= {x ^ column for x in tuple(span)}
    return len(span).bit_length() - 1


def paid_factors_and_free_roles(u, v, target):
    role_maps = []
    frames = []
    for a, b, c, d in product((0, 1), repeat=4):
        columns = (a | (c << 1), b | (d << 1))
        rank = vector_rank(columns)
        table = tuple((a * (x & 1) ^ b * (x >> 1)) |
                      ((c * (x & 1) ^ d * (x >> 1)) << 1) for x in range(4))
        if rank == 2:
            role_maps.append(table)
        if rank == 1 and compose(table, table) == table:
            frames.append(table)
    need(len(frames) == 6 and len(role_maps) == 6, "role classifications differ")
    target6 = tuple((x & 0b111000) | target[x & 7] for x in range(64))
    factors = []
    for frame, label in product(frames, (u, inverse(u), v, inverse(v))):
        table = []
        for x in range(64):
            active, spectator = x & 7, x >> 3
            displacements = (label[active] ^ active, label[spectator] ^ spectator)
            correction = [0, 0]
            for coordinate in range(3):
                role_pair = ((displacements[0] >> coordinate) & 1) | (((displacements[1] >> coordinate) & 1) << 1)
                changed = frame[role_pair]
                correction[0] |= (changed & 1) << coordinate
                correction[1] |= (changed >> 1) << coordinate
            table.append(x ^ correction[0] ^ (correction[1] << 3))
        table = tuple(table)
        need(vector_rank(tuple(table[1 << j] ^ (1 << j) for j in range(6))) == 2,
             "one represented call has wrong displacement rank")
        need(table != target6, "one represented call attains target")
        factors.append(table)
    need(len(set(factors)) == 24 and target6 != tuple(range(64)), "paid alphabet changed")
    need(any(compose(a, b) == target6 for a, b in product(factors, repeat=2)),
         "two represented calls do not attain target")
    ranks = []
    for role in role_maps:
        columns = []
        for j in range(6):
            x = 1 << j
            value = 0
            for coordinate in range(3):
                bits = ((x >> coordinate) & 1) | (((x >> (coordinate + 3)) & 1) << 1)
                mapped = role[bits]
                value |= (mapped & 1) << coordinate
                value |= (mapped >> 1) << (coordinate + 3)
            columns.append(target6[x] ^ value)
        ranks.append(vector_rank(columns))
    need(sorted(ranks) == [1, 3, 3, 4, 6, 6], "free-role residual rank certificate differs")
    return len(factors)


def run_verifier(folder, optimized):
    command = [sys.executable, "-I", "-B"]
    if optimized:
        command.append("-O")
    command.append(str(folder / "verify.py"))
    return subprocess.run(command, cwd=folder, capture_output=True, text=True, timeout=15)


def replace_once(path, old, new):
    source = path.read_text()
    need(source.count(old) == 1, "mutation change point is ambiguous")
    path.write_text(source.replace(old, new))


def damaged_input_controls():
    source = (ROOT / "verify.py").read_text()
    mutations = (
        ("target", "TARGET = (1, 0, 0, 0, 1, 1, 0, 0, 1)", "TARGET = (1, 0, 0, 0, 1, 0, 0, 0, 1)"),
        ("generator", "U = (0, 0, 1, 0, 1, 0, 1, 0, 1)", "U = (1, 0, 1, 0, 1, 0, 1, 0, 1)"),
        ("gate_chronology", "V_GATES = ((0, 2), (2, 0), (1, 2))", "V_GATES = ((1, 2), (2, 0), (0, 2))"),
        ("label_chronology", "four = V_GATES + V_GATES + U_GATES + U_GATES", "four = U_GATES + U_GATES + V_GATES + V_GATES"),
        ("spectator_clobber", "        result[destination] ^= result[source]", "        result[destination] ^= result[source]\n        if len(result) == 6:\n            result[3] ^= 1"),
        ("rank", "    return rank\n", "    return rank + 1\n"),
        ("idempotent", "if binary_rank(n, 2) == 1 and mul(n, n, 2) == n)", "if binary_rank(n, 2) == 1)"),
    )
    names = [row[0] for row in mutations] + ["source_pin", "source_bytes"]
    with tempfile.TemporaryDirectory(prefix="sl2z-binary-controls-") as temporary:
        base = Path(temporary)
        for name in names:
            folder = base / name
            folder.mkdir()
            (folder / "verify.py").write_text(source)
            shutil.copyfile(ROOT / "SOURCE-ORIGINS.json", folder / "SOURCE-ORIGINS.json")
            shutil.copytree(ROOT / "source", folder / "source", copy_function=shutil.copyfile)
            if name == "source_pin":
                path = folder / "SOURCE-ORIGINS.json"
                manifest = json.loads(path.read_text())
                manifest["files"][0]["upstream_commit"] = "0" * 40
                path.write_text(json.dumps(manifest))
            elif name == "source_bytes":
                path = folder / "source/sl2z-README.md"
                path.write_bytes(path.read_bytes() + b"\n")
            else:
                _, before, after = next(row for row in mutations if row[0] == name)
                replace_once(folder / "verify.py", before, after)
            for optimized in (False, True):
                result = run_verifier(folder, optimized)
                need(result.returncode != 0 and "RuntimeError" in result.stderr,
                     "damaged-input control was not rejected: " + name + "/" + str(optimized))
    return len(names)


def main():
    started = time.monotonic()
    c = constants()
    u, v, target = projective_and_basis(c)
    admitted = dimension_two_control()
    histogram = native_bfs_and_dirty(c, u, v, target)
    factors = paid_factors_and_free_roles(u, v, target)
    for optimized in (False, True):
        result = run_verifier(ROOT, optimized)
        need(result.returncode == 0 and "PASS_SL2Z_BINARY_CARRIER" in result.stdout,
             "production verifier did not pass: " + result.stderr)
    damaged = damaged_input_controls()
    sha = hashlib.sha256((ROOT / "verify.py").read_bytes()).hexdigest()
    print("PASS_SL2Z_BINARY_INDEPENDENT_REVIEW gl2_permutations=6 relation_pairs=" + str(admitted)
          + " gl3_bfs=168 distances=" + json.dumps(histogram, separators=(",", ":"))
          + " native_minima=2,3,1 paid_factors=" + str(factors)
          + " minimum_paid_labels=2 dirty_six_bit=64 dirty_matrix_bits=18 matrix_inputs=262144"
          + " free_role_rank_certificate=PASS mutation_cases=" + str(damaged)
          + " mutation_runs=" + str(2 * damaged) + " normal_and_optimized=PASS verifier_sha256=" + sha
          + " elapsed_seconds=" + format(time.monotonic() - started, ".3f"))


if __name__ == "__main__":
    main()
