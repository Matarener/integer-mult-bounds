#!/usr/bin/env python3
"""Replay the depth-three chain connector law; print a source-bound receipt.

Letters 1..k name the complete calls z_l += B_l z_{l-1} (z_0 = x immutable,
z_k = y). Over characteristic m a word restores z_1..z_{k-1} and adds
c B_k...B_1 x to y exactly when its interval subword counts satisfy
N[i..j] = 0 mod m for every interval except N[1..k] = c (PROOF.md, Lemma 1).
The script writes no files.
"""

import hashlib
import itertools
import json
import sys
from collections import deque
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
BFS_DEPTH3_MAX = 8          # exact UT4(Z/m) breadth-first search, m <= 8
CONSTRUCTION_MAX = 256      # explicit 3m family, m <= 256
DENSE_MAX = 32              # literal noncommuting dirty replay, m <= 32
DEPTH4_DEFAULT = (2, 3, 4)  # exact UT5(Z/m) search; m = 5 is opt-in
EXCEPTIONS = {(2, 1): "12321232", (3, 2): "112113211323",
              (4, 3): "1112111321213233"}
SPORADIC = {(6, 5): "111122133232123233"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def intervals(depth: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(1, depth + 1) for j in range(i, depth + 1)]


def signature(word: str, depth: int, modulus: int) -> dict:
    """Interval subword counts N[i..j] mod m, by one chronological pass."""
    require(2 <= modulus and 1 <= depth <= 4, "signature domain")
    count = {iv: 0 for iv in intervals(depth)}
    for event in word:
        letter = int(event)
        require(1 <= letter <= depth, "unknown letter")
        for i in range(1, letter + 1):
            gain = 1 if i == letter else count[(i, letter - 1)]
            count[(i, letter)] = (count[(i, letter)] + gain) % modulus
    return count


def is_target(word: str, depth: int, modulus: int, coefficient: int) -> bool:
    count = signature(word, depth, modulus)
    return all(v == (coefficient % modulus if iv == (1, depth) else 0)
               for iv, v in count.items())


def construction(modulus: int, coefficient: int) -> str:
    """PROOF.md, Lemma 3: 1^a 2 3^t 1^(m-2a) 2 1^a 2^(m-t-2) 3 2^t 3^(m-t-1)."""
    require(5 <= modulus <= CONSTRUCTION_MAX, "construction domain")
    require(1 <= coefficient < modulus, "coefficient domain")
    if (modulus, coefficient) in SPORADIC:
        return SPORADIC[(modulus, coefficient)]
    if coefficient <= modulus - 2:
        a, t = 1, coefficient
    else:
        a = next(u for u in range(2, modulus // 2 + 1) if _unit(u, modulus))
        t = (-pow(a, -1, modulus)) % modulus
    require(1 <= t <= modulus - 2 and 1 <= a <= modulus // 2, "parameters")
    m = modulus
    return ("1" * a + "2" + "3" * t + "1" * (m - 2 * a) + "2" + "1" * a
            + "2" * (m - t - 2) + "3" + "2" * t + "3" * (m - t - 1))


def _unit(u: int, modulus: int) -> bool:
    a, b = u, modulus
    while b:
        a, b = b, a % b
    return a == 1


def bfs_minima(depth: int, modulus: int) -> dict[int, int]:
    """Exact shortest positive words to every central target in UT_{k+1}(Z/m)."""
    ivs = intervals(depth)
    slot = {iv: n for n, iv in enumerate(ivs)}
    size = len(ivs)
    require(modulus ** size <= 10_000_000, "search exceeds state bound")
    weight = [modulus ** n for n in range(size)]

    def step(code: int, letter: int) -> int:
        for i in range(1, letter + 1):
            gain = 1 if i == letter else (code // weight[slot[(i, letter - 1)]]) % modulus
            w = weight[slot[(i, letter)]]
            old = (code // w) % modulus
            code += (((old + gain) % modulus) - old) * w
        return code

    dist = bytearray([255]) * (modulus ** size)
    dist[0] = 0
    queue = deque([0])
    while queue:
        code = queue.popleft()
        for letter in range(1, depth + 1):
            nxt = step(code, letter)
            if dist[nxt] == 255:
                dist[nxt] = dist[code] + 1
                queue.append(nxt)
    top = weight[slot[(1, depth)]]
    return {c: dist[c * top] for c in range(1, modulus)}


def balanced_census(modulus: int) -> list[int]:
    """All words with exactly m copies of each letter; attainable c, independent of BFS."""
    require(2 <= modulus <= 4, "census domain")
    found = set()
    n = 3 * modulus
    for ones in itertools.combinations(range(n), modulus):
        rest = [p for p in range(n) if p not in ones]
        for twos in itertools.combinations(rest, modulus):
            word = ["3"] * n
            for p in ones:
                word[p] = "1"
            for p in twos:
                word[p] = "2"
            count = signature("".join(word), 3, modulus)
            if all(v == 0 for iv, v in count.items() if iv != (1, 3)):
                found.add(count[(1, 3)])
    return sorted(found)


def depth3_checks() -> dict:
    table = {}
    for m in range(2, BFS_DEPTH3_MAX + 1):
        minima = bfs_minima(3, m)
        for c, value in minima.items():
            expect = 4 * m if (m, c) in EXCEPTIONS else 3 * m
            require(value == expect, f"depth-3 minimum mismatch m={m} c={c}")
        table[str(m)] = [minima[c] for c in range(1, m)]
    census = {}
    for m in (2, 3, 4):
        attained = balanced_census(m)
        expect = [0] + [c for c in range(1, m) if (m, c) not in EXCEPTIONS]
        require(attained == expect, f"balanced census mismatch m={m}")
        census[str(m)] = attained
    for (m, c), word in EXCEPTIONS.items():
        require(len(word) == 4 * m and is_target(word, 3, m, c), "exception witness")
    built = 0
    for m in range(5, CONSTRUCTION_MAX + 1):
        for c in range(1, m):
            word = construction(m, c)
            require(len(word) == 3 * m and all(word.count(s) == m for s in "123"),
                    "construction letter counts")
            require(is_target(word, 3, m, c), f"construction failed m={m} c={c}")
            built += 1
    return {"bfs_minima": table, "balanced_census_c_values": census,
            "constructed_words": built}


def matmul(a, b, m):
    return tuple(tuple(sum(a[i][t] * b[t][j] for t in range(2)) % m for j in range(2))
                 for i in range(2))


def matvec(a, v, m):
    return tuple(sum(a[i][t] * v[t] for t in range(2)) % m for i in range(2))


def replay(word: str, maps, regs, m):
    regs = list(regs)
    for event in word:
        l = int(event)
        regs[l] = tuple((regs[l][i] + matvec(maps[l - 1], regs[l - 1], m)[i]) % m
                        for i in range(2))
    return tuple(regs)


DENSE_MAPS = (((1, 1), (0, 1)), ((0, 1), (1, 1)), ((1, 0), (1, 1)))


def dense_checks() -> dict:
    """Literal dirty registers x, z1, z2, y with noncommuting 2x2 maps."""
    b1, b2, b3 = DENSE_MAPS
    cases = 0
    words = [(m, c, construction(m, c)) for m in range(5, DENSE_MAX + 1)
             for c in range(1, m)]
    words += [(m, c, w) for (m, c), w in EXCEPTIONS.items()]
    for m, c, word in words:
        prod = matmul(b3, matmul(b2, b1, m), m)
        for seed in range(4):
            vals = [((seed + 1) * (i + 3) + seed * i * i) % m for i in range(8)]
            regs = tuple(tuple(vals[2 * r:2 * r + 2]) for r in range(4))
            out = replay(word, DENSE_MAPS, regs, m)
            want_y = tuple((regs[3][i] + c * matvec(prod, regs[0], m)[i]) % m
                           for i in range(2))
            require(out[:3] == regs[:3] and out[3] == want_y, "dense endpoint")
            cases += 1
    return {"dense_cases": cases}


def controls() -> list[str]:
    done = []
    word = construction(7, 3)
    require(not is_target(word.replace("3", "", 1), 3, 7, 3), "missing call")
    done.append("one omitted readout call")
    swap = word.index("12")
    swapped = word[:swap] + "21" + word[swap + 2:]
    require(not is_target(swapped, 3, 7, 3), "adjacent swap")
    done.append("first adjacent 12 transposed (N[1..2] moves by one)")
    require(not is_target(word, 3, 7, 4), "wrong coefficient")
    done.append("wrong target coefficient")
    require(not is_target(construction(7, 6).replace("2", "", 1) + "2", 3, 7, 6),
            "moved restoring call")
    done.append("one middle call moved to the end")
    b1, b2, b3 = DENSE_MAPS
    regs = ((1, 0), (0, 0), (0, 0), (0, 0))
    out = replay(construction(5, 1), DENSE_MAPS, regs, 5)
    wrong = matvec(matmul(b1, matmul(b2, b3, 5), 5), (1, 0), 5)
    require(out[3] != wrong, "factor order undetected")
    done.append("noncommuting factor order reversed")
    for bad in ((4, 1), (257, 1), (7, 0), (7, 7)):
        try:
            construction(*bad)
        except ValueError:
            continue
        raise ValueError("construction domain not enforced")
    done.append("construction domain enforced")
    return done


def source_hashes() -> dict:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    result = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            path = PACKAGE.parent.parent / row["path"]
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            require(actual == row["sha256"], f"input hash mismatch: {row['path']}")
            result[row["path"]] = actual
    files = sorted(PACKAGE.iterdir())
    require(len(files) <= 10, "unexpected package file count")
    for path in files:
        require(path.is_file() and not path.is_symlink(), "unexpected package entry")
        result[f"package/{path.name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main() -> None:
    extra = sys.argv[1:]
    require(extra in ([], ["--depth4-m5"]), "usage: verify.py [--depth4-m5]")
    depth4_moduli = DEPTH4_DEFAULT + ((5,) if extra else ())
    depth4 = {}
    for m in depth4_moduli:
        depth4[str(m)] = [bfs_minima(4, m)[c] for c in range(1, m)]
    require(depth4["2"] == [12] and depth4["3"] == [18, 18]
            and depth4["4"] == [20, 20, 20], "depth-4 table mismatch")
    if extra:
        require(depth4["5"] == [25] * 4, "depth-4 m=5 mismatch")
    receipt = {"claim_type": "scoped proof with finite certificate",
               "depth3": depth3_checks(), "depth4_bfs_minima": depth4,
               "dense": dense_checks(), "controls": controls(),
               "sha256": source_hashes()}
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    print(encoded)
    print(f"PASS_DEPTH3_CHAIN_CONNECTOR depth4_moduli={len(depth4_moduli)} "
          f"constructed={receipt['depth3']['constructed_words']} "
          f"receipt_sha256={digest}")


if __name__ == "__main__":
    main()
