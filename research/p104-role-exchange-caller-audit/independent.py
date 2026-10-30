#!/usr/bin/env python3
"""Separate dense quarter-integer replay; no primary/predecessor code imports.

Apache-2.0. Clear1nsight with substantial OpenAI assistance; same-session
checking is not independent human authorship or a proof-kernel certificate.
"""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def code(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sources():
    rows = read(HERE / "PREDECESSORS.json")["files"]
    rows += [r for r in read(HERE / "SOURCES.json")["files"] if r["usage"] == "input"]
    for row in rows:
        raw = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        require(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
                == row["git_blob"], "source Git blob")


def roots():
    # Different enumeration from the primary: sparse ternary eight-tuples.
    universe = []
    for row in itertools.product((0, -2, 2), repeat=8):
        nonzero = [v for v in row if v]
        if len(nonzero) == 2 and nonzero[0] > 0:
            universe.append(row)
    for row in itertools.product((1, -1), repeat=8):
        if row[0] == 1 and row.count(-1) % 2 == 0:
            universe.append(row)
    fixture = read(ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json")
    section = fixture["section4_explicit_P104"]
    excluded = {tuple(r) for r in section["F0"] + section["C"]}
    ports = sorted(set(universe)-excluded)
    require(len(universe) == 120 and len(ports) == 104, "independent E8 enumeration")
    # 4*A = dot(doubled root, doubled root)/2, an integer.
    gram4 = []
    for r in ports:
        row = []
        for s in ports:
            dot = sum(a*b for a, b in zip(r, s))
            require(dot % 2 == 0, "quarter-integer entrance")
            row.append(dot//2)
        gram4.append(row)
    return gram4


def seed(gram4):
    state = [[4*int(i == j) for j in range(280)] for i in range(280)]
    for i in range(104):
        state[104+i][:104] = gram4[i][:]
    return state


def run(gram4, operations, hyperplanes):
    rows = seed(gram4)
    full = [1 << b for b in range(9)]
    frames = [full[:] for _ in range(104)] + [h[:] for h in hyperplanes]
    frames += [full[:] for _ in range(72)]
    bill = Counter()
    for op in operations:
        tag, target = op[:2]
        require(type(target) is int and 0 <= target < 208, "independent target")
        bill[tag] += 1
        if tag == "lift":
            require(frames[target] == hyperplanes[target % 104], "independent lift")
            frames[target] = full[:]
        elif tag == "drop":
            require(frames[target] == full, "independent descent")
            frames[target] = hyperplanes[target % 104][:]
        elif tag == "half":
            require(frames[target] == full, "half frame")
            require(all(v % 2 == 0 for v in rows[target]), "two-bit scalar prefix")
            rows[target] = [v//2 for v in rows[target]]
        elif tag == "double":
            require(frames[target] == full, "double frame")
            rows[target] = [2*v for v in rows[target]]
        elif tag in ("add", "scaled_add"):
            source, c = op[2], Fraction(op[3])
            require(frames[source] == frames[target] == full, "independent ADD frames")
            require(tag != "add" or c in (-1, 1), "independent unit coefficient")
            require(all(v*c.numerator % c.denominator == 0 for v in rows[source]),
                    "quarter scaling is sufficient")
            rows[target] = [a+b*c.numerator//c.denominator
                            for a, b in zip(rows[target], rows[source])]
        else:
            raise ValueError("independent unknown operation")
    return rows, frames, bill


def check(rows, frames, hyperplanes, consume):
    full = [1 << b for b in range(9)]
    for i in range(280):
        if i < 104:
            want = [-4*int(j == 104+i) if consume else 4*int(j == i) for j in range(280)]
        elif i < 208:
            want = [4*int(j in (i, i-104)) for j in range(280)]
        else:
            want = [4*int(i == j) for j in range(280)]
        require(rows[i] == want, "independent arbitrary-input endpoint")
        require(frames[i] == (hyperplanes[i-104] if 104 <= i < 208 else full),
                "independent return frame")


def main():
    sources()
    gram4 = roots()
    word = read(ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    hyperplanes = [word["final_frames"][f"Y{i}"] for i in range(104)]
    programs, expected = read(HERE / "PROGRAMS.json.gz"), read(HERE / "RESULT.json")
    require(type(expected["fixed_location_restoration_minimum_added_rank"]) is int,
            "typed rank receipt")
    checked = 0
    for name, operations in programs.items():
        rows, frames, bill = run(gram4, operations, hyperplanes)
        check(rows, frames, hyperplanes, "reader" in name)
        saved = expected["programs"][name]
        encoded = [[[j, str(Fraction(v, 4))] for j, v in enumerate(row) if v] for row in rows]
        require(hashlib.sha256(code(encoded)).hexdigest() == saved["endpoint_sha256"], "endpoint hash")
        require(hashlib.sha256(code(operations)).hexdigest() == saved["program_sha256"], "program hash")
        require(code(dict(bill)) == code(saved["operation_counts"]), "independent invoice")
        require(bill["lift"]+bill["drop"] == saved["added_H1"], "independent transport bill")
        checked += 280*280
    # Independently derive the fixed physical-location rank gap from output dimensions.
    J = read(HERE / "inputs/3882-result.json")["pivots"]
    N = [i for i in range(104) if i not in J]
    require(all(sum(gram4[j][i]*gram4[k][i] for i in N) == 192*int(j == k)
                for j in J for k in J), "independent B B^t = 12 I")
    input_dimensions = [9 if i in J else 8 for i in range(104)]
    input_dimensions += [8 if i in J else 9 for i in range(104)]
    goal_dimensions = [9]*104+[8]*104
    require(sum(abs(a-b) for a, b in zip(input_dimensions, goal_dimensions)) == 192,
            "independent fixed-location lower bound")
    require(expected["fixed_location_restoration_minimum_added_rank"] == 192,
            "saved fixed-location lower bound")
    require(expected["naive_residual_as_source_error_rank_over_Q"] == 8+96,
            "independent residual-as-source error rank")
    require(9*2576+(72*832-9*2312) == 62280 > 73*832 == 60736,
            "conditional complete coverage stop")
    print("PASS_SEPARATE_QUARTER_INTEGER_CALLER", "coefficients="+str(checked),
          "programs="+str(len(programs)), "fixed_location_rank=192")


if __name__ == "__main__":
    main()
