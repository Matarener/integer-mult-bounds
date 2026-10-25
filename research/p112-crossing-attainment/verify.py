"""Exact ternary energy, attainment criterion and sharp-family replay."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    require((ROOT / "FIXTURES.json").stat().st_size <= 2_000_000, "fixture byte bound")
    raw = (ROOT / "FIXTURES.json").read_bytes()
    require(len(raw) <= 2_000_000, "fixture byte bound")
    data = json.loads(raw)
    require(isinstance(data, list) and 1 <= len(data) <= 256, "fixture count")
    for f in data:
        groups, lines = f["groups"], f["lines"]
        require(3 <= len(groups) <= 9, "cell count")
        require(set(groups) == {0, 1, 2}, "three nonempty groups")
        require(all(type(g) is int and 0 <= g <= 2 for g in groups), "group index")
        require(1 <= len(lines) <= 64, "line count")
        used = set()
        for line in lines:
            require(isinstance(line, list) and 1 <= len(line) <= 3, "line arity")
            require(
                all(type(c) is int and 0 <= c < len(groups) for c in line), "cell index"
            )
            require(
                len({groups[c] for c in line}) == len(line), "one occurrence per group"
            )
            used.update(line)
        require(used == set(range(len(groups))), "nonempty cells")
    return data, hashlib.sha256(raw).hexdigest()


def energy(lines, values):
    result = 0
    for line in lines:
        x = [values[c] for c in line]
        if len(x) == 1:
            result += {1: 0, 0: 1, -1: 2}[x[0]]
        elif all(v == 0 for v in x):
            continue
        else:
            good = all(v != 0 for v in x)
            negatives = x.count(-1)
            good = good and (negatives <= 1 if len(x) == 2 else negatives == 1)
            result += int(not good)
    return result


def cover_attains(groups, lines):
    n = len(groups)
    pins = {line[0] for line in lines if len(line) == 1}
    edges = [set(line) for line in lines if len(line) > 1]
    reached = set(pins)
    for _ in range(n):
        for edge in edges:
            if edge & reached:
                reached.update(edge)
    free = sorted(reached - pins)
    for bits in itertools.product((0, 1), repeat=len(free)):
        negative = {c for c, bit in zip(free, bits, strict=True) if bit}
        if all(
            not edge & reached
            or (
                len(edge & negative) == 1
                if len(edge) == 3
                else len(edge & negative) <= 1
            )
            for edge in edges
        ):
            return True
    return False


def evaluate(f):
    groups, lines = f["groups"], f["lines"]
    counts = [sum(len(line) == k for line in lines) for k in (1, 2, 3)]
    base = counts[0] + 3 * counts[1] + 3 * counts[2]
    hist = {}
    stream = hashlib.sha256()
    best, witness = None, None
    for values in itertools.product((-1, 0, 1), repeat=len(groups)):
        total = base + energy(lines, values)
        stream.update((str(total) + "\n").encode())
        hist[str(total)] = hist.get(str(total), 0) + 1
        if best is None or total < best:
            best, witness = total, list(values)
    require((best == base) == cover_attains(groups, lines), "exact-cover equivalence")
    if "private" in f:
        require(best == base + min(f["common"], 2 * min(f["private"])), "sharp family")
    return {
        "name": f["name"],
        "vvv_min": best,
        "vvv_base": base,
        "mmm_min": 2 * counts[0] + 3 * counts[1] + 3 * counts[2],
        "witness": witness,
        "histogram": hist,
        "stream_sha256": stream.hexdigest(),
        "assignments": 3 ** len(groups),
    }


def main():
    fixtures, digest = load()
    rows = [evaluate(f) for f in fixtures]
    require((ROOT / "RESULT.json").stat().st_size <= 8_000_000, "record byte bound")
    expected = json.loads((ROOT / "RESULT.json").read_text())
    require(expected == {"fixtures_sha256": digest, "rows": rows}, "result mismatch")
    print("PASS_CROSSING_ENERGY", len(rows), sum(r["assignments"] for r in rows))


if __name__ == "__main__":
    main()
