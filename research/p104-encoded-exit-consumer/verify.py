#!/usr/bin/env python3
"""Standard-Y consumer of the PR #3943 encoded exit. No new kappa. Apache-2.0."""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FIXTURE = REPO / "research/p104-native-channel/inputs/P104-FIXTURE.json"
FIXTURE_SHA256 = "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"
J = [0, 1, 3, 6, 22, 31, 93, 103]
ENCODED_MASS = 2576
LEGACY_MASS = 2768
PROGRESS = 2312
LEGACY_SLOPE = 352
LEGACY_INTERCEPT = 104
ENCODED_SLOPE = 160


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ports_from_fixture(data):
    removed = {tuple(v) for v in data["F0"] + data["C"]}
    roots = set()
    for a, b in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            vector = [0] * 8
            vector[a], vector[b] = 2, 2 * sign
            roots.add(tuple(vector))
    for signs in itertools.product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1,) + signs)
    need(len(roots) == 120 and len(removed) == 16 and removed <= roots, "geometry domain")
    return sorted(roots - removed)


def gram(ports):
    return [[F(sum(a * b for a, b in zip(u, v)), 8) for v in ports] for u in ports]


def blocks(A):
    pivots = set(J)
    N = [i for i in range(104) if i not in pivots]
    B = [[A[j][n] for n in N] for j in J]
    need(all(A[j][k] == (j == k) for j in J for k in J), "pivot frame")
    need(all(A[n][m] == sum(B[t][a] * B[t][b] for t in range(8))
             for a, n in enumerate(N) for b, m in enumerate(N)), "Gram block")
    need(sum(x != 0 for row in B for x in row) == 384, "B support")
    need(all(x in (0, F(1, 2), F(-1, 2)) for row in B for x in row), "B coefficients")
    return N, B


def matvec(rows, vector):
    return [sum(c * x for c, x in zip(row, vector)) for row in rows]


def rank(rows):
    matrix = [list(row) for row in rows]
    height, width = len(matrix), len(matrix[0])
    row = col = 0
    while row < height and col < width:
        pivot = next((i for i in range(row, height) if matrix[i][col] != 0), None)
        if pivot is None:
            col += 1
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        scale = matrix[row][col]
        matrix[row] = [entry / scale for entry in matrix[row]]
        for other in range(height):
            if other != row and matrix[other][col] != 0:
                factor = matrix[other][col]
                matrix[other] = [entry - factor * matrix[row][k] for k, entry in enumerate(matrix[other])]
        row += 1
        col += 1
    return row


def difference_matrix(B, N):
    """Rows are coefficients of (x_J, x_N) in v_N - w_N, y cancelled."""
    width = 8 + len(N)
    rows = []
    for a in range(len(N)):
        row = [B[t][a] for t in range(8)]
        row.extend(sum(B[t][a] * B[t][b] for t in range(8)) - (a == b) for b in range(len(N)))
        need(len(row) == width, "difference width")
        rows.append(row)
    return rows


def encode(A, B, N, x, y):
    w = [x[i] + y[i] for i in range(104)]
    ax = matvec(A, x)
    v = [y[i] + ax[i] for i in range(104)]
    q = [x[J[t]] + sum(B[t][a] * x[N[a]] for a in range(len(N))) for t in range(8)]
    return w, v, q


def inverse(B, N, w, q, v):
    x = [F(0)] * 104
    for a, n in enumerate(N):
        x[n] = w[n] - v[n] + sum(B[t][a] * q[t] for t in range(8))
    for t, j in enumerate(J):
        x[j] = q[t] - sum(B[t][a] * x[N[a]] for a in range(len(N)))
    y = [w[i] - x[i] for i in range(104)]
    return x, y


def product_ops(B, N):
    """Move N-products onto Y. This is the legacy adapter without the X_J repair."""
    ops = [("up", f"X{n}", n) for n in N]
    for t, j in enumerate(J):
        ops.append(("scale", f"X{j}", "1/2"))
        for a, n in enumerate(N):
            if B[t][a]:
                ops.append(("add", f"Y{n}", f"X{j}", -int(2 * B[t][a])))
        ops.append(("scale", f"X{j}", "2"))
    for n in N:
        ops.extend((("add", f"X{n}", f"Y{n}", -1), ("add", f"Y{n}", f"X{n}", 1)))
    ops.extend(("down", f"Y{n}", n) for n in N)
    return ops


def legacy_ops(B, N):
    ops = product_ops(B, N)
    # product_ops already descended Y. The X_J repair happens before those downs.
    downs = ops[-len(N):]
    head = ops[:-len(N)]
    for a, n in enumerate(N):
        head.append(("scale", f"X{n}", "1/2"))
        for t, j in enumerate(J):
            if B[t][a]:
                head.append(("add", f"X{j}", f"X{n}", -int(2 * B[t][a])))
        head.append(("scale", f"X{n}", "2"))
    return head + downs


def symbolic_exit(A, B, N):
    """Bank values as coefficient dicts of the 208 source coordinates (x, then y)."""
    state = {}
    for i in range(104):
        state[f"Y{i}"] = {104 + i: F(1), **{j: coeff for j, coeff in enumerate(A[i]) if coeff}}
    for t, j in enumerate(J):
        state[f"X{j}"] = {j: F(1), **{N[a]: B[t][a] for a in range(len(N)) if B[t][a]}}
        state[f"Y{j}"] = {j: F(1), 104 + j: F(1)}
    for n in N:
        state[f"X{n}"] = {n: F(1), 104 + n: F(1)}
    for name, count in (("Q", 8), ("G", 32), ("D", 32)):
        for i in range(count):
            state[f"{name}{i}"] = {}
    frames = {}
    for i in range(104):
        frames[f"X{i}"] = "F" if i in set(J) else "H" + str(i)
        frames[f"Y{i}"] = "H" + str(i) if i in set(J) else "F"
    for name, count in (("Q", 8), ("G", 32), ("D", 32)):
        for i in range(count):
            frames[f"{name}{i}"] = "F"
    return state, frames


def run(state, frames, ops):
    state = {name: value.copy() for name, value in state.items()}
    frames = frames.copy()
    for op in ops:
        kind, target = op[:2]
        need(target in state, "unknown register")
        if kind == "up":
            need(frames[target] == "H" + str(op[2]), "wrong lift")
            frames[target] = "F"
        elif kind == "down":
            need(frames[target] == "F", "wrong descent")
            frames[target] = "H" + str(op[2])
        elif kind == "scale":
            need(frames[target] == "F", "scale outside FULL")
            coeff = F(op[2])
            need(coeff in (F(1, 2), F(2)), "scale alphabet")
            state[target] = {i: coeff * value for i, value in state[target].items()}
        else:
            need(kind == "add", "unknown op")
            source, coeff = op[2], op[3]
            need(target != source and frames[target] == frames[source] == "F", "ADD frame")
            need(type(coeff) is int and coeff in (-1, 1), "unit ADD")
            updated = state[target].copy()
            for i, value in state[source].items():
                updated[i] = updated.get(i, F(0)) + coeff * value
                if updated[i] == 0:
                    del updated[i]
            state[target] = updated
    return state, frames


def counts(ops):
    return {kind: sum(op[0] == kind for op in ops) for kind in ("up", "down", "add", "scale")}


def screen(mass, progress, stages):
    """Actual paired-chain rank gap, and the #3943 linear lower bound."""
    m = 8 * stages + 1
    role = 104 * (stages - 1)
    uncovered = (m - 1) * role - stages * progress
    actual = stages * mass + max(0, uncovered) - m * role
    linear = stages * (mass - progress) - role
    need(actual >= linear, "positive-part gap undercuts the linear bound")
    if uncovered > 0:
        need(actual == linear, "positive uncovered credit changed the gap")
    return actual, linear


def main():
    need(sha256(FIXTURE) == FIXTURE_SHA256, "fixture hash")
    section = json.loads(FIXTURE.read_text(encoding="utf-8"))["section4_explicit_P104"]
    ports = ports_from_fixture(section)
    A = gram(ports)
    N, B = blocks(A)
    diff = difference_matrix(B, N)
    need(rank(diff) == 96, "v-w rank")
    need(all(any(entry != 0 for entry in row) for row in diff), "every N port differs")

    for n in N:
        w = [F(n == i) for i in range(104)]
        q = [F(0)] * 8
        v = [F(0)] * 104
        x, y = inverse(B, N, w, q, v)
        got_w, got_v, got_q = encode(A, B, N, x, y)
        need(got_w == w and got_q == q and [got_v[i] for i in N] == [F(0)] * len(N),
             "witness does not realise")
        need(sum(coeff != 0 for coeff in x) + sum(coeff != 0 for coeff in y) > 0, "empty witness")

    x = [F(1)] * 104
    y = [F(i % 3) for i in range(104)]
    w, v, q = encode(A, B, N, x, y)
    back_x, back_y = inverse(B, N, w, q, v)
    need(back_x == x and back_y == y, "inverse round trip")

    state, frames = symbolic_exit(A, B, N)
    original = {name: value.copy() for name, value in state.items()}
    done, done_frames = run(state, frames, product_ops(B, N))
    for i in range(104):
        need(done[f"Y{i}"] == {i: F(1), 104 + i: F(1)}, "Y is not the product")
        need(done_frames[f"Y{i}"] == "H" + str(i), "Y frame")
    for t, j in enumerate(J):
        need(done[f"X{j}"] == original[f"X{j}"], "X_J changed")
        need(done_frames[f"X{j}"] == "F", "X_J frame")
    for n in N:
        need(done[f"X{n}"] == {n: F(1)}, "X_N is not x_n")
        need(done_frames[f"X{n}"] == "F", "X_N frame")
    for name in original:
        if name[0] in "QGD":
            need(done[name] == original[name] and done_frames[name] == "F", "helper changed")

    product = counts(product_ops(B, N))
    legacy = counts(legacy_ops(B, N))
    need(product == {"up": 96, "down": 96, "add": 576, "scale": 16}, "product invoice")
    need(legacy["up"] == 96 and legacy["down"] == 96 and legacy["add"] == 960, "legacy invoice")
    need(product["up"] + product["down"] == legacy["up"] + legacy["down"] == 192, "transport floor")

    legacy_state, legacy_frames = run(state, frames, legacy_ops(B, N))
    for i in range(104):
        need(legacy_state[f"X{i}"] == {i: F(1)}, "legacy X")
        need(legacy_state[f"Y{i}"] == {i: F(1), 104 + i: F(1)}, "legacy Y")
        need(legacy_frames[f"X{i}"] == "F" and legacy_frames[f"Y{i}"] == "H" + str(i), "legacy frames")

    sample = N[0]
    skipped_up = [op for op in product_ops(B, N) if op != ("up", f"X{sample}", sample)]
    try:
        run(state, frames, skipped_up)
    except ValueError:
        pass
    else:
        raise ValueError("skipped lift was accepted")
    skipped_down = [op for op in product_ops(B, N) if op != ("down", f"Y{sample}", sample)]
    partial, partial_frames = run(state, frames, skipped_down)
    need(partial_frames[f"Y{sample}"] == "F", "skipped descent still left the hyperplane")
    need(partial[f"Y{sample}"] == {sample: F(1), 104 + sample: F(1)}, "skipped descent changed the value")

    encoded_dims = 8 * 9 + 96 * 8 + 8 * 8 + 96 * 9 + 72 * 9
    standard_dims = 104 * 9 + 104 * 8 + 72 * 9
    need(encoded_dims == standard_dims == PROGRESS + 104 == 2416, "frame dimension tally")
    mass = ENCODED_MASS + 192
    need(mass == LEGACY_MASS == 2768, "rank mass")
    actual9, linear9 = screen(mass, PROGRESS, 9)
    encoded9, encoded_linear9 = screen(ENCODED_MASS, PROGRESS, 9)
    need(actual9 == linear9 == LEGACY_SLOPE * 9 + LEGACY_INTERCEPT == 3272, "nine-stage deficit")
    need(encoded9 == encoded_linear9 == ENCODED_SLOPE * 9 + LEGACY_INTERCEPT == 1544, "encoded deficit")
    for stages in (1, 3, 5, 9, 11):
        actual, linear = screen(mass, PROGRESS, stages)
        encoded_actual, encoded_linear = screen(ENCODED_MASS, PROGRESS, stages)
        need(linear == LEGACY_SLOPE * stages + LEGACY_INTERCEPT, "legacy shape")
        need(encoded_linear == ENCODED_SLOPE * stages + LEGACY_INTERCEPT, "encoded shape")
        need(actual >= linear > 0 and encoded_actual >= encoded_linear > 0, "both screens stay positive")
        need(actual - encoded_actual == 192 * stages, "each transport stage adds its rank")

    print(
        "PASS_P104_ENCODED_EXIT_CONSUMER"
        f" transports=192 unit_adds=576 legacy_unit_adds=960"
        f" v_minus_w_rank=96 mass=2768 progress=2312"
        f" deficit9=3272 encoded_deficit9=1544 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
