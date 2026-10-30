#!/usr/bin/env python3
"""Exact P104 changed-boundary experiment. Apache-2.0; see README for scope."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
F0 = [[0,0,0,0,0,0,2,-2],[0,0,0,0,0,0,2,2],
      [0,0,0,0,2,-2,0,0],[0,0,0,0,2,2,0,0],
      [0,0,2,-2,0,0,0,0],[0,0,2,2,0,0,0,0],
      [2,-2,0,0,0,0,0,0],[2,2,0,0,0,0,0,0]]
PUNCTURE_C = [[0,0,0,0,0,2,-2,0],[0,0,0,2,-2,0,0,0],
              [0,2,-2,0,0,0,0,0],[1,-1,-1,-1,-1,-1,-1,1],
              [1,-1,-1,1,1,1,1,1],[1,1,1,-1,-1,1,1,1],
              [1,1,1,1,1,-1,-1,1],[2,0,0,0,0,0,0,-2]]
SOURCE_HASHES = {
    "research/p104-native-channel/inputs/P104-FIXTURE.json":
        "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json":
        "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "research/p104-native-channel/PROOF.md":
        "5d743145d389ffdfaffc66096fa7e32c7155b18f73d74755403151d0435bb94c",
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, f"duplicate JSON key: {key}")
            out[key] = value
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique)


def encoded(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value) -> str:
    return hashlib.sha256(encoded(value)).hexdigest()


def geometry():
    roots = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for tail in itertools.product((-1, 1), repeat=7):
        if sum(t < 0 for t in tail) % 2 == 0:
            roots.add((1,) + tail)
    removed = {tuple(r) for r in F0 + PUNCTURE_C}
    need(len(roots) == 120 and len(removed) == 16 and removed <= roots,
         "root universe or puncture changed")
    ports = sorted(roots - removed)
    R = list(map(list, zip(*ports)))
    need(len(ports) == 104, "wrong port count")
    for a in range(8):
        for b in range(8):
            need(sum(R[a][i] * R[b][i] for i in range(104)) == 104 * (a == b),
                 "RR^t is not 104 I")
    J = []
    for a, b in ((0, 2), (1, 3), (4, 6), (5, 7)):
        for sign in (-1, 1):
            r = [0] * 8
            r[a], r[b] = 2, 2 * sign
            J.append(ports.index(tuple(r)))
    J.sort()
    N = [i for i in range(104) if i not in J]
    A = [[F(sum(x*y for x,y in zip(r,s)), 8) for s in ports] for r in ports]
    need(all(A[i][j] == (i == j) for i in J for j in J), "J not orthogonal")
    B = [[A[j][i] for i in N] for j in J]
    need(all(v in (F(-1,2), 0, F(1,2)) for row in B for v in row), "B alphabet")
    need(sum(v != 0 for row in B for v in row) == 384, "B support")
    for a, i in enumerate(N):
        for b, k in enumerate(N):
            need(A[i][k] == sum(B[j][a] * B[j][b] for j in range(8)),
                 "A_NN != B^t B")
    return R, A, J, N, B


def source_binding(J):
    data = {}
    for path, expected in SOURCE_HASHES.items():
        raw = (REPO / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected, f"source hash: {path}")
        data[path] = raw
    fixture = json.loads(data[next(iter(SOURCE_HASHES))])
    section = fixture["section4_explicit_P104"]
    need(section["F0"] == F0 and section["C"] == PUNCTURE_C, "source extraction")
    word = json.loads(data["research/p104-native-channel/inputs/LOWRANK-WITNESS.json"])
    full = [1 << i for i in range(9)]
    final = word["final_frames"]
    need(all(final[f"X{i}"] == full for i in range(104)), "source exit frame")
    helpers = [f"Q{i}" for i in range(8)] + [f"G{i}" for i in range(32)] + [f"D{i}" for i in range(32)]
    need(all(final[h] == full for h in helpers), "dirty helper exit frames")
    need(all(len(final[f"Y{i}"]) == 8 and binary_rank(final[f"Y{i}"]) == 8
             for i in range(104)), "target exit hyperplane")
    proof = data["research/p104-native-channel/PROOF.md"]
    need(b"y_t + sum_s <r_t,r_s> x_s/2" in proof, "inherited channel statement")
    return {"bound_sources": len(data), "target_frame_digest": digest([final[f"Y{i}"] for i in range(104)]),
            "pivot_input_frames": [word["initial_frames"][f"X{i}"] for i in J]}


def binary_rank(rows):
    pivots = {}
    for row in rows:
        need(type(row) is int and 0 < row < 512, "invalid binary vector")
        while row:
            k = row.bit_length() - 1
            if k in pivots:
                row ^= pivots[k]
            else:
                pivots[k] = row
                break
    return len(pivots)


def program(J, N, B):
    ops = [("lift", 104+i) for i in range(104)]
    for a, i in enumerate(N):
        ops.append(("half", i))
        for b, j in enumerate(J):
            if B[b][a]:
                s = int(2 * B[b][a])
                ops.extend([("add", j, i, s), ("add", 104+j, i, -s)])
        ops.append(("double", i))
    for b, j in enumerate(J):
        ops.append(("half", j))
        for a, i in enumerate(N):
            if B[b][a]:
                ops.append(("add", i, j, -int(2 * B[b][a])))
        ops.append(("double", j))
    ops.extend(("add", i, 104+i, 1) for i in N)
    ops.extend(("drop", i) for i in N)
    ops.extend(("drop", 104+j) for j in J)
    return ops


def execute(A, ops):
    # The 72 arbitrary dirty inputs are explicit independent columns, not zero.
    state = [[F(i == j) for j in range(280)] for i in range(280)]
    for i in range(104):
        state[104+i][:104] = A[i][:]
    frames = [9]*104 + [8]*104 + [9]*72
    max_denominator = max(x.denominator for row in state for x in row)
    peak_row_norm = max(sum(abs(x) for x in row) for row in state)
    for op in ops:
        kind, target = op[:2]
        need(type(target) is int and 0 <= target < 208, "helper mutation or bad register")
        if kind == "lift":
            need(frames[target] == 8, "lift source frame")
            frames[target] = 9
            continue
        if kind == "drop":
            need(frames[target] == 9, "drop source frame")
            frames[target] = 8
            continue
        need(frames[target] == 9, "arithmetic target not FULL")
        if kind == "add":
            source, sign = op[2:]
            need(source != target and 0 <= source < 208 and frames[source] == 9,
                 "arithmetic source or frame")
            need(type(sign) is int and sign in (-1, 1), "ADD coefficient")
            state[target] = [x + sign*y for x,y in zip(state[target], state[source])]
        else:
            need(kind in ("half", "double"), "unknown operation")
            scalar = F(1, 2) if kind == "half" else F(2)
            state[target] = [scalar*x for x in state[target]]
        max_denominator = max(max_denominator, *(x.denominator for x in state[target]))
        peak_row_norm = max(peak_row_norm, sum(abs(x) for x in state[target]))
    return state, frames, max_denominator, peak_row_norm


def mod_rank(matrix, prime=3):
    a = [[int(F(x).numerator * pow(F(x).denominator, -1, prime) % prime)
          for x in row] for row in matrix]
    rank = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inv = pow(a[rank][col], -1, prime)
        a[rank] = [(v*inv) % prime for v in a[rank]]
        for i in range(rank+1, len(a)):
            c = a[i][col]
            if c:
                a[i] = [(x-c*y) % prime for x,y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def verify_endpoint(state, frames, A, J, N, B):
    for i in range(104):
        target = 104+i if i in J else i
        expected = [F(k in (i,104+i)) for k in range(280)]
        need(state[target] == expected and frames[target] == 8, f"sum endpoint {i}")
    for b,j in enumerate(J):
        expected = [F(k == j) for k in range(280)]
        for a,i in enumerate(N):
            expected[i] = B[b][a]
        need(state[j] == expected and frames[j] == 9, f"q residual {j}")
    for i in N:
        expected = [F(k == 104+i) for k in range(280)]
        expected[:104] = A[i][:]
        need(state[104+i] == expected and frames[104+i] == 9, f"v residual {i}")
    for i in range(208,280):
        need(state[i] == [F(i == k) for k in range(280)] and frames[i] == 9,
             f"dirty helper {i}")


def calculate():
    R,A,J,N,B = geometry()
    ops = program(J,N,B)
    state,frames,den,norm = execute(A,ops)
    verify_endpoint(state,frames,A,J,N,B)
    # Separate endpoint formula and explicit inverse, not the gate interpreter.
    xs = []
    for a,i in enumerate(N):
        w = state[i]
        v = state[104+i]
        xs.append([w[k]-v[k]+sum(B[b][a]*state[j][k] for b,j in enumerate(J))
                   for k in range(280)])
    for a,i in enumerate(N):
        need(xs[a] == [F(k == i) for k in range(280)], "inverse x_N")
    for b,j in enumerate(J):
        restored = [state[j][k]-sum(B[b][a]*xs[a][k] for a in range(96))
                    for k in range(280)]
        need(restored == [F(k == j) for k in range(280)], "inverse x_J")
    C = [[F(i == j)-A[i][j] for j in range(104)] for i in range(104)]
    naive = [[F(i == j) for j in range(104)]+[F(i == j) for j in range(104)]
             for i in range(104)]
    naive += [A[i][:]+[F(i == j) for j in range(104)] for i in range(104)]
    need(mod_rank(C) == 96 and mod_rank(naive) == 200, "mod-three obstruction")
    need(mod_rank([r[:208] for r in state[:208]]) == 208, "repaired rank")
    need(mod_rank(R) == 8, "root rank modulo three")
    counts = Counter(op[0] for op in ops)
    need(counts == Counter(add=1248,half=104,double=104,lift=104,drop=104), "invoice")
    need(den == 4, "two-bit transient bound")
    return {
        "schema_version": 1, "base_commit": BASE, "scope": "changed source-consuming boundary; no supplier or kappa",
        "ports": 104, "pivots": J, "nonpivots": N, "root_nonzeros": sum(v != 0 for r in R for v in r),
        "B_nonzeros": 384, "program_sha256": digest(ops), "endpoint_sha256": digest([[str(v) for v in r] for r in state]),
        "operation_counts": dict(sorted(counts.items())), "total_tail_events": len(ops),
        "tail_native_profile": {"1": 208}, "inherited_channel_mass": 2368, "combined_mass": 2576,
        "combined_native_profile": [1282,58,86,104,48,24,8,8],
        "scalar_real_adds_at_512_complex_words": 1248*1024,
        "scalar_real_halves_at_512_complex_words": 104*1024,
        "scalar_real_doubles_at_512_complex_words": 104*1024,
        "maximum_scalar_coefficient_denominator": den, "maximum_scalar_row_l1": str(norm),
        "sum_outputs": 104, "dirty_helpers_restored": 72,
        "rank_C_mod3": 96, "rank_naive_mod3": 200, "rank_repaired_mod3": 208,
        "minimum_replaced_residual_arrays_in_stated_linear_model": 8,
        "det_naive": str(12**8), "native_lowering_replayed": False, "complete_consumer_admitted": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algebra-only", action="store_true", help="Do not claim full-repository source authentication.")
    args = parser.parse_args()
    result = calculate()
    need(encoded(result) == encoded(load(HERE/"RESULT.json")), "typed result mismatch")
    if args.algebra_only:
        marker = "PASS_P104_ROLE_EXCHANGE_ALGEBRA_ONLY"
    else:
        print(json.dumps(source_binding(result["pivots"]), sort_keys=True))
        marker = "PASS_P104_ROLE_EXCHANGE_SOURCE_BOUND"
    print(f"{marker} replaced=8 sums=104 dirt=72 tail_H1=208 result={digest(result)}")


if __name__ == "__main__":
    main()
