#!/usr/bin/env python3
"""Exact finite controls for a three-bit integer-shear caller representation.

The written dimension proof is universal. These checks construct the genuine
quotient action, verify the finite minimum and audit the declared XOR programs.
No predecessor code is imported or executed here.
"""

import ast
import hashlib
import json
import stat
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parent
IDENTITY = (1, 0, 0, 1)
X = (1, 1, 0, 1)
XI = (1, -1, 0, 1)
Y = (1, 0, 1, 1)
YI = (1, 0, -1, 1)
B = (5, 2, 2, 1)
U = (0, 0, 1, 0, 1, 0, 1, 0, 1)
V = (1, 0, 1, 1, 1, 0, 1, 0, 0)
TARGET = (1, 0, 0, 0, 1, 1, 0, 0, 1)
LINES = ((1, 0), (0, 1), (1, 1), (1, 2))
BASIS = ((0, 1, 0, 1), (1, 1, 1, 1), (0, 1, 1, 0))
# Each gate is (target coordinate, source coordinate), applied left to right.
U_GATES = ((2, 0), (0, 2))
V_GATES = ((0, 2), (2, 0), (1, 2))
B_GATES = ((1, 2),)
PINS = {
    "source/sl2z-README.md": (
        "b27bf4c72a822b21f483e08cb3241ad9d165b66f",
        "research/sl2z-four-call-native-target/README.md",
        "f8c354eeb9cc3b60ed4d0da5a58329517c33cd4d",
        "fb475d7cf4de6df3c258d7a9366ef1b3edc61302370f9081c299353ab59b35b1",
    ),
    "source/sl2z-verify.py": (
        "b27bf4c72a822b21f483e08cb3241ad9d165b66f",
        "research/sl2z-four-call-native-target/verify.py",
        "db16b86750aa558ade71db2efb3a8c2d38853e20",
        "653acaedf1119e232edb681428c707292e717860be01c25801066b10cfd97364",
    ),
    "source/caller-README.md": (
        "5ee1c9cee717e682db01bff4c398b87011a135a2",
        "research/sl2z-commutative-caller-obstruction/README.md",
        "89755de599e9705ff3c9f02d0f81e303005f5608",
        "45d409fc050818145e6ba24bc95e8abb1f11df89835f38cd3e76fa7a05b69c4e",
    ),
    "source/faithfulness-README.md": (
        "cfafdd633cf4e2e534704ec3ddd684cb0c32734f",
        "research/binary-stream-faithfulness/README.md",
        "a471c1ee89c64c8d2eae5fa0f7bfccd8d3d726bb",
        "0b5f45d882980038ced16e66cdd4e7d8869c5ca2032e988a5df636df05cb6b12",
    ),
    "source/faithfulness-PROOF.md": (
        "cfafdd633cf4e2e534704ec3ddd684cb0c32734f",
        "research/binary-stream-faithfulness/PROOF.md",
        "daee560b155a09484e644069272d002f8ae65c82",
        "0d82d13bdcca7953a8f1e6647a78fe6008c407795b363af5be7cd1b7ea8ee2a9",
    ),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def identity(n):
    return tuple(int(i == j) for i in range(n) for j in range(n))


def mul(a, b, n, modulus=2):
    require(len(a) == len(b) == n * n, "matrix dimensions disagree")
    result = tuple(sum(a[n * i + k] * b[n * k + j] for k in range(n))
                   for i in range(n) for j in range(n))
    return result if modulus is None else tuple(x % modulus for x in result)


def power(a, exponent, n, modulus=2):
    result = identity(n)
    for _ in range(exponent):
        result = mul(result, a, n, modulus)
    return result


def apply(a, vector, n, modulus=2):
    require(len(a) == n * n and len(vector) == n, "action dimensions disagree")
    return tuple(sum(a[n * i + j] * vector[j] for j in range(n)) % modulus
                 for i in range(n))


def binary_rank(a, n):
    rows = [list(a[n * i:n * (i + 1)]) for i in range(n)]
    require(len(a) == n * n and all(x in (0, 1) for x in a), "nonbinary rank input")
    rank = 0
    for column in range(n):
        pivot = next((i for i in range(rank, n) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(n):
            if i != rank and rows[i][column]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def add(a, b):
    require(len(a) == len(b), "sum dimensions disagree")
    return tuple(x ^ y for x, y in zip(a, b))


def check_sources():
    manifest_path = ROOT / "SOURCE-ORIGINS.json"
    require(stat.S_ISREG(manifest_path.lstat().st_mode), "source manifest is not regular")
    manifest = json.loads(manifest_path.read_text())
    require(manifest["repository"] == "CrocSwap/integer-mult-bounds", "source repository changed")
    entries = manifest["files"]
    require(len(entries) == len(PINS), "source count changed")
    require({row["path"] for row in entries} == set(PINS), "source paths changed")
    for row in entries:
        pin = PINS[row["path"]]
        require(tuple(row[k] for k in ("upstream_commit", "upstream_path", "git_blob", "sha256")) == pin,
                "source provenance changed: " + row["path"])
        path = ROOT / row["path"]
        require(stat.S_ISREG(path.lstat().st_mode), "retained source is not regular: " + row["path"])
        require(path.resolve().is_relative_to(ROOT), "retained source escapes the package")
        raw = path.read_bytes()
        git_blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        require(hashlib.sha1(git_blob).hexdigest() == pin[2], "source Git blob mismatch: " + row["path"])
        require(hashlib.sha256(raw).hexdigest() == pin[3], "source SHA256 mismatch: " + row["path"])
    expected = {"IDENTITY": IDENTITY, "X": X, "XI": XI, "Y": Y, "YI": YI, "EXPECTED": B}
    constants = {}
    for node in ast.parse((ROOT / "source/sl2z-verify.py").read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = node.targets[0]
            if isinstance(name, ast.Name) and name.id in expected:
                require(name.id not in constants, "duplicate predecessor constant")
                constants[name.id] = ast.literal_eval(node.value)
    require(constants == expected, "predecessor constants disagree with the declared model")


def check_integer_relations():
    integer_mul = lambda a, b: mul(a, b, 2, None)
    require(integer_mul(X, XI) == integer_mul(XI, X) == IDENTITY, "X inverse failed")
    require(integer_mul(Y, YI) == integer_mul(YI, Y) == IDENTITY, "Y inverse failed")
    s = integer_mul(integer_mul(X, YI), X)
    si = (0, -1, 1, 0)
    require(s == integer_mul(integer_mul(YI, X), YI) == (0, 1, -1, 0), "integer braid relation failed")
    require(integer_mul(s, si) == IDENTITY, "S inverse failed")
    require(integer_mul(integer_mul(s, X), si) == YI, "integer conjugacy failed")
    require(power(s, 4, 2, None) == IDENTITY, "S fourth power failed")
    require(integer_mul(power(X, 2, 2, None), power(Y, 2, 2, None)) == B != IDENTITY,
            "integer target changed or became identity")


def projective_action(a):
    result = []
    for line in LINES:
        x, y = apply(a, line, 2, 3)
        require((x, y) != (0, 0), "invertible matrix killed a projective line")
        scale = pow(x or y, -1, 3)
        result.append(LINES.index((x * scale % 3, y * scale % 3)))
    return tuple(result)


def permutation_apply(permutation, vector):
    result = [0] * len(vector)
    for i, image in enumerate(permutation):
        result[image] = vector[i]
    return tuple(result)


def check_quotient_action():
    quotient = tuple(a for a in product(range(3), repeat=4)
                     if (a[0] * a[3] - a[1] * a[2]) % 3 == 1)
    require(len(quotient) == 24, "SL2(F3) size changed")
    require(all(sum(w) % 2 == 0 for w in BASIS), "basis lies outside augmentation subspace")
    coordinates = {}
    for c in product((0, 1), repeat=3):
        w = tuple(sum(c[j] * BASIS[j][i] for j in range(3)) % 2 for i in range(4))
        require(w not in coordinates, "augmentation basis is dependent")
        coordinates[w] = c
    require(set(coordinates) == {w for w in product((0, 1), repeat=4) if sum(w) % 2 == 0},
            "basis does not cover the complete augmentation subspace")
    permutations = {a: projective_action(a) for a in quotient}
    require(all(sorted(p) == list(range(4)) for p in permutations.values()), "invalid projective permutation")
    actions = {}
    for a in quotient:
        columns = [coordinates[permutation_apply(permutations[a], w)] for w in BASIS]
        actions[a] = tuple(columns[j][i] for i in range(3) for j in range(3))
        require(binary_rank(actions[a], 3) == 3, "quotient action is not invertible")
    require(actions[IDENTITY] == identity(3), "action is not unital")
    for a, b in product(quotient, repeat=2):
        ab = mul(a, b, 2, 3)
        require(permutations[ab] == tuple(permutations[a][permutations[b][i]] for i in range(4)),
                "projective action does not preserve quotient multiplication")
        require(actions[ab] == mul(actions[a], actions[b], 3), "augmentation action is not a homomorphism")
    reduce3 = lambda a: tuple(x % 3 for x in a)
    require(permutations[reduce3(X)] == (0, 2, 3, 1), "X projective action changed")
    require(permutations[reduce3(Y)] == (2, 1, 3, 0), "Y projective action changed")
    require(actions[reduce3(X)] == U and actions[reduce3(Y)] == V, "declared generator matrices differ from genuine action")
    require(actions[reduce3(B)] == TARGET, "target differs from genuine quotient image")
    require(len(set(actions.values())) == 12, "quotient image size changed")
    # Reduction is a homomorphism for integer matrices; the complete finite
    # action check above therefore defines a representation of the actual G.
    return actions


def check_dimension_control():
    group = tuple(a for a in product((0, 1), repeat=4)
                  if (a[0] * a[3] - a[1] * a[2]) % 2 == 1)
    require(len(group) == 6, "GL2(F2) size changed")
    inverse = {a: next(b for b in group if mul(a, b, 2) == IDENTITY) for a in group}
    order = {a: next(n for n in range(1, 7) if power(a, n, 2) == IDENTITY) for a in group}
    require(sorted(order.values()) == [1, 2, 2, 2, 3, 3], "GL2 orders changed")
    third_order = tuple(a for a in group if order[a] == 3)
    require(len(third_order) == 2 and mul(*third_order, 2) == IDENTITY, "order-three elements do not form one cyclic subgroup")
    admitted = 0
    for u, v in product(group, repeat=2):
        vi = inverse[v]
        braid = mul(mul(u, vi, 2), u, 2) == mul(mul(vi, u, 2), vi, 2)
        conjugate = any(mul(mul(s, u, 2), inverse[s], 2) == vi for s in group)
        if braid and conjugate:
            admitted += 1
            require(order[u] == order[v], "conjugate elements have different orders")
            require(mul(power(u, 2, 2), power(v, 2, 2), 2) == IDENTITY,
                    "two-dimensional necessary-relation control preserves B")
    require(admitted == 12, "two-dimensional control count changed")
    require(power(U, 3, 3) == power(V, 3, 3) == identity(3), "native generators do not have order three")
    require(U != identity(3) and V != identity(3), "native generators collapsed")
    require(mul(U, V, 3) != mul(V, U, 3), "carrier unexpectedly commutes")
    require(mul(power(U, 2, 3), power(V, 2, 3), 3) == TARGET != identity(3), "target collapsed")
    require(power(TARGET, 2, 3) == identity(3), "target order is not two")
    require(binary_rank(add(TARGET, identity(3)), 3) == 1, "target displacement rank is not one")


def tensor(a, b, na, nb):
    return tuple(a[(i // nb) * na + j // nb] * b[(i % nb) * nb + j % nb]
                 for i in range(na * nb) for j in range(na * nb))


def check_paid_label_minimum():
    frames = tuple(n for n in product((0, 1), repeat=4)
                   if binary_rank(n, 2) == 1 and mul(n, n, 2) == n)
    require(len(frames) == 6, "rank-one idempotent frame count changed")
    labels = (U, power(U, 2, 3), V, power(V, 2, 3))
    require(len(set(labels)) == 4, "paid labels are not distinct")
    target = add(identity(6), tensor((1, 0, 0, 0), add(TARGET, identity(3)), 2, 3))
    require(binary_rank(add(target, identity(6)), 6) == 1, "two-role target displacement rank changed")
    factors = []
    for frame, label in product(frames, labels):
        displacement = tensor(frame, add(label, identity(3)), 2, 3)
        require(binary_rank(add(label, identity(3)), 3) == 2, "label displacement rank changed")
        require(binary_rank(displacement, 6) == 2, "one-call displacement rank changed")
        factor = add(identity(6), displacement)
        require(binary_rank(factor, 6) == 6 and factor != target, "one call reached target or is not reversible")
        factors.append(factor)
    require(len(factors) == 24 and target != identity(6), "zero/one-call bound failed")
    p = (1, 0, 0, 0)
    ui = add(identity(6), tensor(p, add(power(U, 2, 3), identity(3)), 2, 3))
    vi = add(identity(6), tensor(p, add(power(V, 2, 3), identity(3)), 2, 3))
    require(mul(ui, vi, 6) == target, "two paid labels do not reach the complete endpoint")
    # Even arbitrary free invertible binary role maps before/after one call
    # cannot help: target-Q⊗I has rank !=2 for every possible Q=left*right.
    free = tuple(q for q in product((0, 1), repeat=4) if binary_rank(q, 2) == 2)
    residual_ranks = sorted(binary_rank(add(target, tensor(q, identity(3), 2, 3)), 6) for q in free)
    require(residual_ranks == [1, 3, 3, 4, 6, 6], "free-role-map rank certificate failed")
    return target


def run_gates(gates, vector):
    result = list(vector)
    for destination, source in gates:
        require(destination != source and 0 <= destination < len(result) and 0 <= source < len(result),
                "invalid XOR gate")
        result[destination] ^= result[source]
    return tuple(result)


def check_native_programs(target):
    require((len(U_GATES), len(V_GATES), len(B_GATES)) == (2, 3, 1), "native gate counts changed")
    for matrix, gates in ((U, U_GATES), (V, V_GATES), (TARGET, B_GATES)):
        changed_outputs = sum(any(matrix[3 * i + j] != int(i == j) for j in range(3)) for i in range(3))
        require(changed_outputs == len(gates), "changed-output XOR lower bound no longer matches program")
        for vector in product((0, 1), repeat=3):
            result = run_gates(gates, vector)
            require(result == apply(matrix, vector, 3), "native XOR program differs from its matrix")
            require(run_gates(tuple(reversed(gates)), result) == vector, "inverse XOR program failed")
    ui_gates, vi_gates = tuple(reversed(U_GATES)), tuple(reversed(V_GATES))
    four = V_GATES + V_GATES + U_GATES + U_GATES
    two = vi_gates + ui_gates
    require(len(four) == 10 and len(two) == 5, "label-expanded XOR bill changed")
    cancelled = []
    for gate in two:
        if cancelled and gate == cancelled[-1]:
            cancelled.pop()
        else:
            cancelled.append(gate)
    require(tuple(cancelled) == B_GATES, "adjacent inverse-gate cancellation failed")
    moved = 0
    for dirty in product((0, 1), repeat=6):
        desired = apply(target, dirty, 6)
        require(desired[:3] == apply(TARGET, dirty[:3], 3), "active block target changed")
        require(desired[3:] == dirty[3:], "dirty spectator was not restored")
        for program in (four, two, B_GATES):
            require(run_gates(program, dirty) == desired, "dirty six-bit endpoint failed")
        moved += desired != dirty
    require(moved == 32, "nontrivial dirty endpoint count changed")
    require(any(run_gates((), w) != apply(TARGET, w, 3) for w in product((0, 1), repeat=3)),
            "omitted-gate negative control failed")
    require(mul(power(V, 2, 3), power(U, 2, 3), 3) != TARGET, "wrong-order negative control failed")


def main():
    check_sources()
    check_integer_relations()
    check_quotient_action()
    check_dimension_control()
    target = check_paid_label_minimum()
    check_native_programs(target)
    print("PASS_SL2Z_BINARY_CARRIER sources=5 quotient_size=24 products=576 image_size=12 "
          "gl2_pairs=36 gl2_admitted=12 minimum_dimension=3 frames=6 one_call_factors=24 "
          "minimum_paid_labels=2 dirty_inputs=64 native_xors_U=2 native_xors_V=3 "
          "native_xors_B=1 scratch_bits=0 no_new_kappa")


if __name__ == "__main__":
    main()
