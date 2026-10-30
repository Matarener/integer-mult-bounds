#!/usr/bin/env python3
"""Bounded P104 caller-cut audit. Apache-2.0; see README for scope and credit."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = tuple(1 << i for i in range(9))
FIELDS = ([f"X{i}" for i in range(104)] + [f"Y{i}" for i in range(104)]
          + [f"Q{i}" for i in range(8)] + [f"G{i}" for i in range(32)]
          + [f"D{i}" for i in range(32)])


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=unique)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def space(vectors):
    need(all(type(v) is int and 0 < v < 512 for v in vectors), "binary frame vector")
    rows = [v for v in vectors if v]
    pivot = 0
    for bit in range(8, -1, -1):
        found = next((i for i in range(pivot, len(rows)) if (rows[i] >> bit) & 1), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and (rows[i] >> bit) & 1:
                rows[i] ^= rows[pivot]
        pivot += 1
    return tuple(sorted(rows[:pivot]))


def authenticate():
    pins = load(HERE / "PREDECESSORS.json")["files"]
    pins += [row for row in load(HERE / "SOURCES.json")["files"] if row["usage"] == "input"]
    result = {}
    for row in pins:
        path = ROOT / row["path"]
        need(not path.is_symlink(), "source symlink")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        need(blob(raw) == row["git_blob"], "source blob: " + row["path"])
        result[row["path"]] = row["sha256"]
    return result


def geometry():
    fixture = load(ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json")
    g = load(HERE / "inputs/3882-geometry.json")
    section = fixture["section4_explicit_P104"]
    need(section["F0"] == g["F0"] and section["C"] == g["C"], "puncture source")
    roots = set()
    for a, b in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[a], r[b] = 2, 2 * sign
            roots.add(tuple(r))
    for signs in itertools.product((-1, 1), repeat=7):
        if sum(s < 0 for s in signs) % 2 == 0:
            roots.add((1,) + signs)
    ports = sorted(roots - {tuple(r) for r in g["F0"] + g["C"]})
    need(len(roots) == 120 and len(ports) == 104, "root count")
    A = [[F(sum(x*y for x, y in zip(r, s)), 8) for s in ports] for r in ports]
    J = load(HERE / "inputs/3882-result.json")["pivots"]
    N = [i for i in range(104) if i not in J]
    need(J == [0, 1, 3, 6, 22, 31, 93, 103], "pivot order")
    B = [[A[j][i] for i in N] for j in J]
    need(sum(v != 0 for row in B for v in row) == 384, "B support")
    need(all(v in (F(-1, 2), 0, F(1, 2)) for row in B for v in row), "B alphabet")
    need(all(A[j][k] == int(j == k) for j in J for k in J), "pivot block")
    need(all(sum(B[a][i]*B[b][i] for i in range(96)) == 12*int(a == b)
             for a in range(8) for b in range(8)), "B row rank witness")
    for a, i in enumerate(N):
        for b, k in enumerate(N):
            need(A[i][k] == sum(B[t][a]*B[t][b] for t in range(8)), "Schur block")
    return A, J, N, B


def plus(a, b, coefficient=F(1)):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, F(0)) + coefficient * value
        if not out[key]:
            del out[key]
    return out


def source_channel(A):
    word = load(ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    state = {name: {i: F(1)} for i, name in enumerate(FIELDS)}
    frames = {name: tuple(value) for name, value in word["initial_frames"].items()}
    counts, profile = Counter(), Counter()
    for op in word["program"]:
        kind, target = op[:2]
        counts[kind] += 1
        if kind == "transport":
            old, new, rank = tuple(op[2]), tuple(op[3]), op[4]
            need(space(frames[target]) == space(old) and rank == abs(len(new)-len(old)), "source transport")
            need(len(space(old)) == len(old) and len(space(new)) == len(new), "source frame basis")
            frames[target] = new
            profile[rank] += 1
        elif kind == "add":
            source, c, frame = op[2], F(op[3]), tuple(op[4])
            need(space(frames[target]) == space(frames[source]) == space(frame), "source ADD frame")
            state[target] = plus(state[target], state[source], c)
        elif kind == "zero":
            need(target == "C" and target not in state, "owned private creation")
            state[target], frames[target] = {}, tuple(op[2])
        elif kind == "copy":
            need(target == "C" and not state[target], "owned private COPY destination")
            need(space(frames[target]) == space(frames[op[2]]) == space(op[3]), "source COPY frame")
            state[target] = dict(state[op[2]])
        elif kind == "erase":
            # Inherited owned live-copy disposal; deliberately not a zero-erasure assertion.
            need(target == "C" and space(frames[target]) == space(op[2]), "private disposal")
            del state[target], frames[target]
        else:
            raise ValueError("unknown source instruction")
    for i, name in enumerate(FIELDS):
        expected = {i: F(1)}
        if name.startswith("Y"):
            expected.update({j: value for j, value in enumerate(A[int(name[1:])]) if value})
        need(state[name] == expected, "source endpoint: " + name)
        need(space(frames[name]) == space(word["final_frames"][name]), "source final frame")
        if name.startswith("Y"):
            need(len(space(frames[name])) == 8, "channel exit target hyperplane")
        else:
            need(space(frames[name]) == space(FULL), "channel exit source/helper FULL")
    need(len(word["program"]) == 4058 and sum(r*n for r, n in profile.items()) == 2368,
         "source invoice")
    progress = sum(len(word["final_frames"][name])-len(word["initial_frames"][name])
                   for name in FIELDS)
    need(progress == 2312, "persistent source boundary progress")
    return state, frames, {"events": 4058, "operation_counts": dict(counts),
                           "profile": dict(sorted(profile.items())), "mass": 2368,
                           "persistent_progress": progress, "private_copy_mass": 2368-progress}


def seed(A):
    state = [{i: F(1)} for i in range(280)]
    for i, row in enumerate(A):
        state[104+i].update({j: value for j, value in enumerate(row) if value})
    return state


def pivot_stream(J, N, B, restore=False):
    ops = []
    for a, i in enumerate(N):
        ops.append(["half", i])
        for b, j in enumerate(J):
            if B[b][a]:
                sign = int(2*B[b][a])
                ops.append(["add", j, i, -sign if restore else sign])
                if not restore:
                    ops.append(["add", 104+j, i, -sign])
        ops.append(["double", i])
    return ops


def scatter(J, N, B, destination):
    ops = []
    for b, j in enumerate(J):
        ops.append(["half", j])
        for a, i in enumerate(N):
            if B[b][a]:
                ops.append(["add", destination+i, j, -int(2*B[b][a])])
        ops.append(["double", j])
    return ops


def role_tail(J, N, B):
    ops = [["lift", 104+i] for i in range(104)]
    ops += pivot_stream(J, N, B) + scatter(J, N, B, 0)
    ops += [["add", i, 104+i, 1] for i in N]
    ops += [["drop", i] for i in N] + [["drop", 104+j] for j in J]
    return ops


def return_adapter(J, N, B):
    ops = [["lift", i] for i in N] + [["add", 104+i, i, -1] for i in N]
    ops += scatter(J, N, B, 104)
    for a, i in enumerate(N):
        ops.append(["half", 104+i])
        for b, j in enumerate(J):
            if B[b][a]:
                ops.append(["add", j, 104+i, int(2*B[b][a])])
        ops.append(["double", 104+i])
    for i in N:
        ops += [["add", i, 104+i, -1], ["add", 104+i, i, 1], ["add", i, 104+i, -1]]
    return ops + [["drop", 104+i] for i in N]


def inverse_reader():
    return ([["lift", 104+i] for i in range(104)]
            + [["add", i, 104+i, -1] for i in range(104)]
            + [["drop", 104+i] for i in range(104)])


def fused(J, N, B, consume=False):
    ops = [["lift", 104+i] for i in range(104)]
    ops += pivot_stream(J, N, B) + scatter(J, N, B, 104)
    ops += pivot_stream(J, N, B, restore=True)
    ops += [["add", 104+i, i, 1] for i in N]
    if consume:
        ops += [["add", i, 104+i, -1] for i in range(104)]
    return ops + [["drop", 104+i] for i in range(104)]


def direct_baseline(correction, consume=False, retime=False):
    rows, ops = correction["rows"], []
    if retime:
        ops += [["lift", 104+i] for i in range(104)]
        ops += [["half", i] for i in range(104)]
        for row in rows:
            ops += [["add", 104+row["target"], i, int(2*F(c))] for i, c in row["terms"]]
        ops += [["double", i] for i in range(104)]
        if consume:
            ops += [["add", i, 104+i, -1] for i in range(104)]
        return ops + [["drop", 104+i] for i in range(104)]
    for row in rows:
        t = 104 + row["target"]
        ops.append(["lift", t])
        for i, c in row["terms"]:
            ops.append(["scaled_add", t, i, c])
        ops.append(["drop", t])
    return ops + (inverse_reader() if consume else [])


def replay(A, ops, final):
    state, frames = seed(A), [FULL]*104 + [None]*104 + [FULL]*72
    for i in range(104):
        frames[104+i] = tuple(final[f"Y{i}"])
    counts, peak, holds = Counter(), sum(map(len, frames)), 0
    max_den, max_norm = 1, F(0)
    for row in state:
        max_den = max(max_den, *(v.denominator for v in row.values()))
        max_norm = max(max_norm, sum(map(abs, row.values())))
    for op in ops:
        kind, t = op[:2]
        need(type(t) is int and 0 <= t < 208, "public arithmetic target")
        counts[kind] += 1
        if kind == "lift":
            need(len(frames[t]) == 8, "lift entrance")
            frames[t] = FULL
        elif kind == "drop":
            need(frames[t] == FULL, "drop entrance")
            frames[t] = tuple(final[f"Y{t % 104}"])
        else:
            need(frames[t] == FULL, "arithmetic target frame")
            if kind in ("add", "scaled_add"):
                s, coefficient = op[2], F(op[3])
                need(type(s) is int and 0 <= s < 208 and s != t, "arithmetic source")
                need(frames[s] == FULL, "arithmetic source frame")
                need(kind != "add" or coefficient in (-1, 1), "unit ADD")
                state[t] = plus(state[t], state[s], coefficient)
            else:
                need(kind in ("half", "double"), "unknown arithmetic")
                c = F(1, 2) if kind == "half" else F(2)
                state[t] = {k: c*v for k, v in state[t].items()}
            max_den = max(max_den, *(v.denominator for v in state[t].values()))
            max_norm = max(max_norm, sum(map(abs, state[t].values())))
        width = sum(map(len, frames))
        peak, holds = max(peak, width), holds + width
    return state, frames, {"events": len(ops), "operation_counts": dict(sorted(counts.items())),
                           "added_H1": counts["lift"]+counts["drop"],
                           "maximum_coefficient_denominator": max_den,
                           "maximum_row_l1": str(max_norm), "peak_persistent_frame_coordinates": peak,
                           "post_event_persistent_frame_coordinate_holds": holds}


def endpoint(state, frames, final, consume=False):
    for i in range(104):
        want_x = {104+i: F(-1)} if consume else {i: F(1)}
        need(state[i] == want_x and frames[i] == FULL, "X caller endpoint")
        need(state[104+i] == {i: F(1), 104+i: F(1)}, "Y caller endpoint")
        need(frames[104+i] == tuple(final[f"Y{i}"]), "Y caller return frame")
    for i in range(208, 280):
        need(state[i] == {i: F(1)} and frames[i] == FULL, "dirty helper return")


def encode_state(state):
    return [[[k, str(v)] for k, v in sorted(row.items())] for row in state]


def check_baseline(A):
    c = load(HERE / "inputs/3894-correction.json")
    need(len(c["rows"]) == 104, "baseline row count")
    signs = Counter()
    for i, row in enumerate(c["rows"]):
        need(type(row["target"]) is int and row["target"] == i, "baseline target order")
        terms = {j: F(v) for j, v in row["terms"]}
        need(len(terms) == len(row["terms"]) == 48, "baseline row support")
        need(terms == {j: F(i == j)-v for j, v in enumerate(A[i]) if F(i == j)-v},
             "baseline exact correction coefficients")
        signs.update(v for _, v in row["terms"])
    need(signs == {"-1/2": 3376, "1/2": 1616}, "baseline signs")
    word = load(ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    need(c["target_output_frames"] == {str(i): word["final_frames"][f"Y{i}"]
                                      for i in range(104)}, "baseline endpoint frame binding")
    return c


def calculate():
    hashes = authenticate()
    caller = (ROOT / "notes/copied-centers-complex.tex").read_text()
    need("maps $(x,y)$ to $(-y,x+y)$" in caller, "retained caller equation")
    need("Its copy, addition and erasure are paid local work".lower() in caller.lower()
         or "its copy, addition and erasure are paid local work" in caller,
         "retained caller payment clause")
    A, J, N, B = geometry()
    _, _, source = source_channel(A)
    word = load(ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    final = word["final_frames"]
    baseline = check_baseline(A)
    old = role_tail(J, N, B)
    need(digest(old) == load(HERE / "inputs/3882-result.json")["program_sha256"], "PR3882 schedule")
    encoded, encoded_frames, encoded_bill = replay(A, old, final)
    for i in range(104):
        target = 104+i if i in J else i
        need(encoded[target] == {i:F(1),104+i:F(1)} and len(encoded_frames[target]) == 8,
             "PR3882 sum and frame")
    for b, j in enumerate(J):
        q = {j:F(1)}
        q.update({i:B[b][a] for a, i in enumerate(N) if B[b][a]})
        need(encoded[j] == q and encoded_frames[j] == FULL, "PR3882 q boundary")
    entrance = seed(A)
    for i in N:
        need(encoded[104+i] == entrance[104+i] and encoded_frames[104+i] == FULL,
             "PR3882 v_N boundary")
    for i in range(208, 280):
        need(encoded[i] == {i:F(1)} and encoded_frames[i] == FULL, "PR3882 dirty boundary")
    restoration_floor = sum(abs(len(encoded_frames[i])-9) for i in range(104))
    restoration_floor += sum(abs(len(encoded_frames[104+i])-8) for i in range(104))
    programs = {
        "role_then_fixed_return": old + return_adapter(J, N, B),
        "role_return_then_reader": old + return_adapter(J, N, B) + inverse_reader(),
        "fused_return": fused(J, N, B),
        "fused_return_and_reader": fused(J, N, B, True),
        "baseline_3894": direct_baseline(baseline),
        "baseline_3894_then_reader": direct_baseline(baseline, True),
        "retimed_lowered_baseline": direct_baseline(baseline, False, True),
        "retimed_lowered_baseline_and_reader": direct_baseline(baseline, True, True),
    }
    results = {}
    for name, ops in programs.items():
        state, frames, bill = replay(A, ops, final)
        endpoint(state, frames, final, "reader" in name)
        bill["endpoint_sha256"], bill["program_sha256"] = digest(encode_state(state)), digest(ops)
        bill["combined_channel_mass"] = 2368 + bill["added_H1"]
        bill["bare_280_role_M0"] = str(F(bill["combined_channel_mass"], 9*280))
        results[name] = bill
    return {"schema_version": 1, "status": "PASS_P104_ROLE_EXCHANGE_CALLER_AUDIT",
            "sources": hashes, "source_channel": source, "programs": results,
            "encoded_boundary": {"endpoint_sha256":digest(encode_state(encoded)), **encoded_bill},
            "fixed_location_restoration_minimum_added_rank": restoration_floor,
            "restoration_constructed_added_rank": results["role_then_fixed_return"]["added_H1"]-encoded_bill["added_H1"],
            "naive_residual_as_source_error_rank_over_Q": 104,
            "ports": 104, "independent_inputs": 280, "dirty_helpers": 72,
            "scalar_saving_against_retimed_lowered_baseline": 3360,
            "additional_halves_and_doubles_each": 96,
            "unchanged_paired_chain": {"stages": 9, "width": 73, "families": 832,
                "persistent_progress_per_call": 2312, "remaining_coverage": 39096,
                "lower_mass": 9*2576+39096, "capacity": 73*832,
                "M0": str(F(9*2576+39096, 73*832)),
                "scope": "Conditional inherited source-preserving nine-call template only; not a supplied owner embedding."},
            "physical_or_all_size_supplier_admitted": False}, programs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--write", type=Path)
    args = ap.parse_args()
    result, programs = calculate()
    if args.write:
        with args.write.open("xb") as out:
            out.write(canonical(result))
    else:
        expected = load(HERE / "RESULT.json")
        need(type(expected.get("schema_version")) is int, "typed receipt schema")
        need(canonical(result) == canonical(expected), "frozen receipt mismatch")
        need(canonical(programs) == canonical(load(HERE / "PROGRAMS.json.gz")), "frozen programs mismatch")
    print(json.dumps(result, indent=2) if args.emit else result["status"])


if __name__ == "__main__":
    main()
