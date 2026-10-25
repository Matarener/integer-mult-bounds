#!/usr/bin/env python3
"""Recompute the required X102 coefficient in Y71 and their direct contact.

The archived fixed-cover cut states that this coefficient is -1/2 and that
the two channel paths do not share a frame. This check does not build the
2,309 compatible edges.
"""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
FIXTURE = ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json"
WITNESS = ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
ARCHIVED = ROOT / "research/p104-pooled-cut-independent/verify.py"
ARCHIVED_RESULT = ROOT / "research/p104-pooled-cut-independent/RESULT.json"
TARGET = 71
SOURCE = 102
MARKER = "PASS_P104_REQUIRED_COEFFICIENT coefficient=-1/2 pairs=4992 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_REQUIRED_COEFFICIENT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def points(basis):
    require(type(basis) is list and len(basis) <= 9, "basis size")
    result = [0]
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512 and vector not in result, "basis vector")
        result += [point ^ vector for point in result]
    return frozenset(result)


def shared(left, right):
    return len(set(left) & set(right))


def chain(word, name):
    frames = [points(word["initial_frames"][name])]
    for event in word["program"]:
        if event[0] != "transport" or event[1] != name:
            continue
        old, new = points(event[2]), points(event[3])
        require(frames[-1] == old and old < new, "monotone data path")
        require(len(new) == len(old) * 2 ** event[4], "transport rank")
        frames.append(new)
    require(frames[-1] == points(word["final_frames"][name]), "final frame")
    return frames


def ports_of(fixture):
    removed = fixture["section4_explicit_P104"]
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *signs) for signs in product((-1, 1), repeat=7) if signs.count(-1) % 2 == 0]
    ports = sorted(set(roots) - {tuple(vector) for vector in removed["F0"] + removed["C"]})
    require(len(roots) == 120 and len(ports) == 104, "P104 roots")
    return ports


def entry(ports, target, source):
    return 8 * int(target == source) - sum(
        left * right for left, right in zip(ports[source], ports[target], strict=True)
    )


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/inputs/P104-FIXTURE.json",
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-pooled-cut-independent/verify.py",
        "research/p104-pooled-cut-independent/RESULT.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    checker = ARCHIVED.read_text(encoding="utf-8")
    require('need(matrix8[71][102] == -4, "C[71,102] = -1/2")' in checker, "the coefficient rule moved")
    require('need(sum(m.bit_count() for m in masks) == 4992, "required pairs")' in checker, "the pair count moved")
    require('set(paths[f"X{s}"]) & set(paths[f"Y{t}"])' in checker, "the direct-contact rule moved")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    word = json.loads(WITNESS.read_text(encoding="utf-8"))
    require(len(word["program"]) == 4058, "word length")
    ports = ports_of(fixture)
    value = entry(ports, TARGET, SOURCE)
    pairs = sum(1 for target in range(104) for source in range(104) if entry(ports, target, source))
    source_frames = chain(word, "X102")
    target_frames = chain(word, "Y71")
    common = shared(source_frames, target_frames)
    archived = json.loads(ARCHIVED_RESULT.read_text(encoding="utf-8"))
    require(archived["coefficient"] == "-1/2", "the archived coefficient moved")
    require(archived["required"] == 4992, "the archived pair count moved")
    require(archived["missing"] == [[71, 102]], "the archived missing pair moved")
    require(value == -4 and pairs == 4992 and common == 0, "the recomputation moved")
    return {
        "target": TARGET,
        "source": SOURCE,
        "entry": str(value),
        "coefficient": str(Fraction(value, 8)),
        "required_pairs": pairs,
        "shared_frames": common,
        "source_frames": len(source_frames),
        "target_frames": len(target_frames),
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
