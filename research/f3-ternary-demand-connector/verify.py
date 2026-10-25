#!/usr/bin/env python3
"""Exact 744-call optimum for full ternary demand on the unsigned F3 connector.

Five immutable sources, all 242 nonzero rows of F3^5, one dirty restored
connector. The 741-call operator-count floor needs a restored 15-event path
whose boundary vectors cover F3^5 by three-term sums. This verifier enumerates
every such path up to source relabeling and finds none; it then checks two
literal 744-call schedules and semantic controls. It writes no files.
"""

from __future__ import annotations

import hashlib
import math
import json
import random
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_READ = 128 * 1024

SOURCES = 5
POW3 = (1, 3, 9, 27, 81)
SIZE = 243
FLOOR_CALLS = 3 * SOURCES + 3 * (SIZE - 1)  # 741
CANONICAL_PATHS = 1_401_400  # 15! / (3!^5 * 5!)
WITNESS_18 = "132004311040023420"
WITNESS_15 = "010210321432434"
BINARY_PATH_4225 = "044001322133421"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL_F3_TERNARY_DEMAND_CONNECTOR: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_bytes(path: Path) -> bytes:
    with path.open("rb") as handle:
        data = handle.read(MAX_READ + 1)
    require(len(data) <= MAX_READ, f"{path} exceeds read cap")
    return data


def check_sources() -> None:
    manifest = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    live = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(live) == 1, "expected one live input")
    for row in live:
        digest = hashlib.sha256(read_bytes(ROOT / row["path"])).hexdigest()
        require(digest == row["sha256"], f"live input drifted: {row['path']}")


def digits(code: int, n: int) -> tuple[int, ...]:
    return tuple((code // POW3[i]) % 3 for i in range(n))


def encode(vec: tuple[int, ...]) -> int:
    return sum((v % 3) * POW3[i] for i, v in enumerate(vec))


def add_table(n: int) -> list[list[int]]:
    size = 3**n
    return [[encode(tuple(x + y for x, y in zip(digits(a, n), digits(b, n))))
             for b in range(size)] for a in range(size)]


ADD = add_table(SOURCES)


def prefixes(path: str, table: list[list[int]]) -> list[int]:
    q = [0]
    for letter in path:
        q.append(table[q[-1]][POW3[int(letter)]])
    return q


def triple_cover(boundaries: list[int], table: list[list[int]]) -> set[int]:
    points = set(boundaries)
    pairs = {table[a][b] for a in points for b in points}
    cover: set[int] = set()
    for c in points:
        row = table[c]
        cover.update([row[p] for p in pairs])
    return cover


def census(n: int, canonical: bool) -> dict[int, int]:
    """Histogram of nonzero triple coverage over closed 3n-event paths.

    canonical=True keeps one path per source-relabeling class: letters first
    appear in increasing order. Every source appears, so each class has
    exactly one such member and the relabeled coverage is the image under a
    coordinate permutation, which fixes the full nonzero demand.
    """
    table = ADD if n == SOURCES else add_table(n)
    length = 3 * n
    counts = [0] * n
    q = [0] * (length + 1)
    hist: dict[int, int] = {}
    gaps: list[int] = []

    def rec(t: int, used: int) -> None:
        if t == length:
            cover = triple_cover(q[:length], table)
            k = len(cover) - 1
            hist[k] = hist.get(k, 0) + 1
            if k == len(table) - 2:
                gaps.extend(v for v in range(1, len(table)) if v not in cover)
            return
        top = min(used + 1, n) if canonical else n
        for s in range(top):
            if counts[s] == 3:
                continue
            counts[s] += 1
            q[t + 1] = table[q[t]][POW3[s]]
            rec(t + 1, max(used, s + 1))
            counts[s] -= 1

    rec(0, 0)
    hist[-1] = len(gaps)
    GAPS[n] = gaps
    return hist


GAPS: dict[int, list[int]] = {}


def check_census() -> dict[str, object]:
    hist = census(SOURCES, canonical=True)
    require(hist.pop(-1) == hist[SIZE - 2], "one gap per maximal path")
    total = sum(hist.values())
    require(total == CANONICAL_PATHS, f"canonical path count {total}")
    best = max(hist)
    require(best == SIZE - 2, f"maximum coverage {best}, expected 241")
    require(SIZE - 1 not in hist, "a fifteen-event path covers every row")
    types = sorted({(digits(g, SOURCES).count(1), digits(g, SOURCES).count(2))
                    for g in GAPS[SOURCES]})
    return {"paths": total, "max_cover": best, "at_max": hist[best],
            "gap_types": types}


def check_small_census_controls() -> None:
    # The canonical reduction must agree with full labeled enumeration.
    for n, labeled in ((2, 20), (3, 1680)):
        full = census(n, canonical=False)
        canon = census(n, canonical=True)
        full.pop(-1)
        canon.pop(-1)
        require(sum(full.values()) == labeled, f"labeled count n={n}")
        require(sum(canon.values()) * math.factorial(n) == labeled, f"canonical count n={n}")
        require(max(full) == max(canon), f"canonical maximum differs n={n}")
        require((3**n - 1 in full) == (3**n - 1 in canon), f"feasibility n={n}")


def check_small_floor() -> list[int]:
    """Full ternary demand attains the 3n + 3(3^n - 1) floor for n <= 4."""
    witnesses = []
    for n, paths in ((1, 1), (2, 10), (3, 280), (4, 15400)):
        hist = census(n, canonical=True)
        hist.pop(-1)
        require(sum(hist.values()) == paths, f"canonical count n={n}")
        require(hist.get(3**n - 1, 0) > 0, f"floor not attained n={n}")
        witnesses.append(hist[3**n - 1])
    return witnesses


def triple_value_cap(n: int) -> int:
    """Distinct 3-sums from at most 3n boundary points, counting 0 once."""
    m = 3 * n
    return math.comb(m, 3) + m * (m - 1) + 1


def check_counting_bound() -> None:
    # The cap is a cubic in n, so cap(n+1)/cap(n) < 3 once n >= 7 and the
    # inequality cap(n) < 3^n persists; the loop checks the stated range.
    require(triple_value_cap(6) >= 3**6, "n=6 should not be excluded by counting")
    for n in range(7, 64):
        require(triple_value_cap(n) < 3**n, f"counting bound fails n={n}")
        require(3 * triple_value_cap(n) > triple_value_cap(n + 1), f"ratio n={n}")


def readouts(boundaries: list[int], size: int) -> dict[int, tuple[int, ...]]:
    """Lexicographically first boundary multiset of size 3 or 6 per row."""
    points = range(len(boundaries))
    triples: dict[int, tuple[int, ...]] = {}
    for a in points:
        for b in range(a, len(boundaries)):
            for c in range(b, len(boundaries)):
                v = ADD[ADD[boundaries[a]][boundaries[b]]][boundaries[c]]
                triples.setdefault(v, (a, b, c))
    plan = {v: triples[v] for v in range(1, size) if v in triples}
    for v in range(1, size):
        if v in plan:
            continue
        for u in sorted(triples):
            w = ADD[v][_neg(u)]
            if u != 0 and w in triples:
                plan[v] = tuple(sorted(triples[u] + triples[w]))
                break
    require(len(plan) == size - 1, "a row has no 3- or 6-readout plan")
    return plan


def _neg(u: int) -> int:
    return encode(tuple(-x for x in digits(u, SOURCES)))


def build_word(path: str, plan: dict[int, tuple[int, ...]]) -> list[tuple[str, int]]:
    """Interleave readouts A_v at their boundaries with source calls B_j."""
    word: list[tuple[str, int]] = []
    for t in range(len(path) + 1):
        for v in sorted(plan):
            word.extend(("A", v) for b in plan[v] if b == t)
        if t < len(path):
            word.append(("B", int(path[t])))
    return word


def generic_ledger(word: list[tuple[str, int]]) -> tuple[list[int], dict[int, list[int]]]:
    """Free coefficients: index 0 is z0, index 1+j is B_j x_j, all in F3."""
    z = [1] + [0] * SOURCES
    y: dict[int, list[int]] = {}
    for kind, index in word:
        if kind == "B":
            z[1 + index] = (z[1 + index] + 1) % 3
        else:
            row = y.setdefault(index, [0] * (SOURCES + 1))
            for i in range(SOURCES + 1):
                row[i] = (row[i] + z[i]) % 3
    return z, y


def check_word(word: list[tuple[str, int]], label: str) -> None:
    z, y = generic_ledger(word)
    require(z == [1] + [0] * SOURCES, f"{label}: connector not restored")
    require(sorted(y) == list(range(1, SIZE)), f"{label}: missing output rows")
    for v, row in y.items():
        require(row[0] == 0, f"{label}: dirt left on row {v}")
        require(tuple(row[1:]) == digits(v, SOURCES), f"{label}: wrong row {v}")


def dense_check(word: list[tuple[str, int]], seed: int, dim: int) -> bool:
    """Execute the word on random F3 matrices; True iff the action is exact."""
    rng = random.Random(seed)

    def mat() -> list[list[int]]:
        return [[rng.randrange(3) for _ in range(dim)] for _ in range(dim)]

    def vec() -> list[int]:
        return [rng.randrange(3) for _ in range(dim)]

    def apply(m: list[list[int]], x: list[int]) -> list[int]:
        return [sum(m[i][k] * x[k] for k in range(dim)) % 3 for i in range(dim)]

    def plus(a: list[int], b: list[int]) -> list[int]:
        return [(u + w) % 3 for u, w in zip(a, b)]

    bmap = [mat() for _ in range(SOURCES)]
    amap = {v: mat() for v in range(1, SIZE)}
    x = [vec() for _ in range(SOURCES)]
    z0 = vec()
    y0 = {v: vec() for v in range(1, SIZE)}
    z, y = list(z0), {v: list(r) for v, r in y0.items()}
    for kind, index in word:
        if kind == "B":
            z = plus(z, apply(bmap[index], x[index]))
        else:
            y[index] = plus(y[index], apply(amap[index], z))
    ok = z == z0
    for v in range(1, SIZE):
        want = y0[v]
        for j, coeff in enumerate(digits(v, SOURCES)):
            for _ in range(coeff):
                want = plus(want, apply(amap[v], apply(bmap[j], x[j])))
        ok = ok and y[v] == want
    return ok


def expect_fail(check, label: str) -> None:
    try:
        check()
    except SystemExit:
        return
    fail(f"control accepted: {label}")


def bill(word: list[tuple[str, int]], source_price: list[int], readout: int) -> int:
    return sum(source_price[i] if k == "B" else readout for k, i in word)


def relabel(path: str, perm: tuple[int, ...]) -> str:
    return "".join(str(perm[int(c)]) for c in path)


def witness_words() -> dict[str, list[tuple[str, int]]]:
    words: dict[str, list[tuple[str, int]]] = {}
    for j in range(SOURCES):
        perm = tuple(j if i == 0 else 0 if i == j else i for i in range(SOURCES))
        path = relabel(WITNESS_18, perm)
        require(path.count(str(j)) == 6, f"source {j} is not doubled")
        q = prefixes(path, ADD)
        require(q[-1] == 0, "eighteen-event path is not restored")
        require(len(triple_cover(q[:-1], ADD)) == SIZE, f"18-path {j} misses a row")
        plan = readouts(q[:-1], SIZE)
        require(all(len(r) == 3 for r in plan.values()), "18-path needs six readouts")
        words[f"double{j}"] = build_word(path, plan)
    q = prefixes(WITNESS_15, ADD)
    require(q[-1] == 0, "fifteen-event path is not restored")
    gaps = [v for v in range(1, SIZE) if v not in triple_cover(q[:-1], ADD)]
    require(len(gaps) == 1, f"fifteen-event witness gaps {gaps}")
    plan = readouts(q[:-1], SIZE)
    require(len(plan[gaps[0]]) == 6, "gap row is not a six-readout row")
    words["gap"] = build_word(WITNESS_15, plan)
    for label, word in words.items():
        require(len(word) == FLOOR_CALLS + 3, f"{label} has {len(word)} calls")
        check_word(word, label)
    return words


def check_controls(words: dict[str, list[tuple[str, int]]]) -> int:
    binary = prefixes(BINARY_PATH_4225, ADD)
    require(binary[-1] == 0, "PR4225 path is not restored")
    binary_cover = len(triple_cover(binary[:-1], ADD)) - 1
    require(binary_cover == 203, f"PR4225 path covers {binary_cover}")
    word = words["double0"]
    first_b = next(i for i, (k, _) in enumerate(word) if k == "B")
    controls = [
        ("drop a source call", word[:first_b] + word[first_b + 1:]),
        ("drop a readout", word[1:]),
        ("move a readout across a source call",
         word[1:first_b + 1] + [word[0]] + word[first_b + 1:]),
        ("change a source port",
         [("B", (i + 1) % SOURCES) if (k, i) == ("B", 0) else (k, i) for k, i in word]),
    ]
    for label, bad in controls:
        expect_fail(lambda bad=bad, label=label: check_word(bad, label), label)
    expect_fail(lambda: require(dense_check(controls[2][1], 2, 3), "x"), "dense move")
    for label, w in words.items():
        for seed, dim in ((1, 2), (2, 3)):
            require(dense_check(w, seed, dim), f"dense action {label} L={dim}")
    return len(controls) + 1


def check_tariffs(words: dict[str, list[tuple[str, int]]]) -> list[int]:
    fixtures = [([1] * 5, 1, 744), ([1, 4, 10, 16, 28], 1, 906),
                ([2, 3, 4, 5, 6], 5, 3696), ([7, 8, 9, 10, 11], 1, 864)]
    out = []
    for prices, alpha, expected in fixtures:
        formula = 3 * sum(prices) + 3 * (SIZE - 1) * alpha + 3 * min(min(prices), alpha)
        attained = min(bill(w, prices, alpha) for w in words.values())
        require(formula == expected == attained, f"tariff {prices} {alpha}")
        out.append(attained)
    return out


def main() -> None:
    check_sources()
    require(FLOOR_CALLS == 741, "floor arithmetic")
    check_small_census_controls()
    small = check_small_floor()
    check_counting_bound()
    words = witness_words()
    controls = check_controls(words)
    tariffs = check_tariffs(words)
    result = check_census()
    print(f"census paths={result['paths']} max_cover={result['max_cover']} "
          f"at_max={result['at_max']} gap_types={result['gap_types']}")
    print(f"floor attained n=1..4 by canonical paths {small}; counting excludes n>=7")
    print(f"witnesses={len(words)} controls={controls} tariffs={tariffs}")
    package = sorted(p for p in PACKAGE.iterdir() if p.is_file() and p.suffix != ".pyc")
    receipt = hashlib.sha256()
    for path in package:
        receipt.update(path.name.encode() + b"\0" + hashlib.sha256(read_bytes(path)).digest())
    print(f"receipt sha256={receipt.hexdigest()} files={len(package)}")
    print(f"PASS_F3_TERNARY_DEMAND_CONNECTOR calls={FLOOR_CALLS + 3} rows={SIZE - 1}")


if __name__ == "__main__":
    main()
