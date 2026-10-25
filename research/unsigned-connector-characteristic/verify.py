#!/usr/bin/env python3
"""Verify the unsigned dirty-connector optimum in every characteristic.

Default mode regenerates CERTIFICATE.json in memory and requires byte
equality. ``--emit`` prints the regenerated certificate instead.
"""
import hashlib
import itertools
import json
import pathlib
import sys

PKG = pathlib.Path(__file__).resolve().parent
ROOT = PKG.parent.parent
READ_CAP = 128 * 1024
MARKER = "PASS_UNSIGNED_CONNECTOR_CHARACTERISTIC"
# Explicit five-source walks for the two characteristics below five.
WALKS = {
    3: [0, 4, 4, 0, 0, 1, 3, 2, 2, 1, 3, 3, 4, 2, 1],
    4: [0, 2, 3, 4, 3, 2, 1, 0, 0, 2, 1, 0, 1, 3, 3, 4, 4, 2, 1, 4],
}
RUN_DOMAIN = [(c, k) for c in range(2, 10) for k in range(1, min(c, 7) + 1)]
PACKAGE_FILES = ["README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py"]


class CheckError(Exception):
    pass


def require(ok, message):
    if not ok:
        raise CheckError(message)


def read_bytes(path):
    data = path.read_bytes()
    require(len(data) <= READ_CAP, f"file too large: {path}")
    return data


def prefixes(walk, c, k):
    q = [0] * k
    out = [tuple(q)]
    for s in walk:
        require(0 <= s < k, "source label out of range")
        q[s] = (q[s] + 1) % c
        out.append(tuple(q))
    return out


def masks(k):
    return [tuple((m >> j) & 1 for j in range(k)) for m in range(1, 2 ** k)]


def search_readouts(walk, c, k):
    """Lexicographically first multiset of c boundaries for each mask."""
    pre = prefixes(walk, c, k)
    found = {}
    for combo in itertools.combinations_with_replacement(range(len(pre)), c):
        total = tuple(sum(pre[t][i] for t in combo) % c for i in range(k))
        found.setdefault(total, list(combo))
    readouts = []
    for target in masks(k):
        require(target in found, f"c={c} k={k}: mask {target} uncovered")
        readouts.append(found[target])
    return readouts


def run_walk(c, k):
    return [j for j in range(k) for _ in range(c)]


def run_readouts(c, k):
    """Boundary c*j+1 holds e_j; boundary 0 holds the zero prefix."""
    require(k <= c, "run walk needs k <= c")
    out = []
    for target in masks(k):
        chosen = [c * j + 1 for j in range(k) if target[j]]
        out.append([0] * (c - len(chosen)) + chosen)
    return out


def literal_word(walk, readouts):
    """Interleave readouts A_m at their boundaries, ascending mask order."""
    word = []
    for t in range(len(walk) + 1):
        for m, chosen in enumerate(readouts, start=1):
            word.extend(["A", m] for b in chosen if b == t)
        if t < len(walk):
            word.append(["B", walk[t]])
    return word


def generic_run(word, c, k, n_out):
    """Track coefficients of z0 and B_j x_j in z and in every A_m image."""
    z = [1] + [0] * k
    y = [[0] * (k + 1) for _ in range(n_out + 1)]
    for kind, idx in word:
        if kind == "B":
            z[idx + 1] = (z[idx + 1] + 1) % c
        else:
            y[idx] = [(a + b) % c for a, b in zip(y[idx], z)]
    return z, y


def check_generic(word, c, k):
    targets = masks(k)
    z, y = generic_run(word, c, k, len(targets))
    require(z == [1] + [0] * k, f"c={c} k={k}: connector not restored")
    for m, target in enumerate(targets, start=1):
        require(y[m] == [0] + list(target), f"c={c} k={k}: row {m} wrong")


def check_counts(word, c, k):
    counts = {}
    for kind, idx in word:
        counts[(kind, idx)] = counts.get((kind, idx), 0) + 1
    expected = [("B", j) for j in range(k)]
    expected += [("A", m) for m in range(1, 2 ** k)]
    require(sorted(counts) == sorted(expected), "operator set differs")
    require(all(v == c for v in counts.values()), "an operator count is not c")
    require(len(word) == c * (k + 2 ** k - 1), "word length differs")


def lcg(seed):
    state = seed
    while True:
        state = (state * 6364136223846793005 + 1442695040888963407) % 2 ** 64
        yield state >> 33


def matrix(gen, c, size):
    return [[next(gen) % c for _ in range(size)] for _ in range(size)]


def matvec(mat, vec, c):
    return [sum(a * b for a, b in zip(row, vec)) % c for row in mat]


def vadd(u, v, c):
    return [(a + b) % c for a, b in zip(u, v)]


def dense_case(word, c, k, size, seed, reverse_factors=False):
    """Execute the literal word on dirty rows with random maps over Z/c."""
    gen = lcg(seed)
    n_out = 2 ** k - 1
    bmaps = [matrix(gen, c, size) for _ in range(k)]
    amaps = [matrix(gen, c, size) for _ in range(n_out + 1)]
    xs = [[next(gen) % c for _ in range(size)] for _ in range(k)]
    z0 = [next(gen) % c for _ in range(size)]
    y0 = [[next(gen) % c for _ in range(size)] for _ in range(n_out + 1)]
    z, ys = list(z0), [list(row) for row in y0]
    for kind, idx in word:
        if kind == "B":
            z = vadd(z, matvec(bmaps[idx], xs[idx], c), c)
        else:
            ys[idx] = vadd(ys[idx], matvec(amaps[idx], z, c), c)
    ok = z == z0
    for m, target in enumerate(masks(k), start=1):
        want = list(y0[m])
        for j in range(k):
            if target[j]:
                inner = matvec(amaps[m] if reverse_factors else bmaps[j],
                               xs[j], c)
                outer = bmaps[j] if reverse_factors else amaps[m]
                want = vadd(want, matvec(outer, inner, c), c)
        ok = ok and ys[m] == want
    return ok


def fails(fn):
    try:
        fn()
    except CheckError:
        return True
    return False


def explicit_case(c):
    walk = WALKS[c]
    k = 5
    require(all(walk.count(j) == c for j in range(k)), "walk counts differ")
    require(prefixes(walk, c, k)[-1] == (0,) * k, "walk does not close")
    readouts = search_readouts(walk, c, k)
    word = literal_word(walk, readouts)
    check_counts(word, c, k)
    check_generic(word, c, k)
    for size in (1, 2, 3):
        for seed in (11, 23, 37):
            require(dense_case(word, c, k, size, 1000 * c + 10 * size + seed),
                    f"c={c}: dense case failed")
    return {"characteristic": c, "sources": k, "walk": walk,
            "readout_boundaries": readouts, "calls": len(word), "word": word}


def run_case(c, k):
    word = literal_word(run_walk(c, k), run_readouts(c, k))
    check_counts(word, c, k)
    check_generic(word, c, k)
    require(dense_case(word, c, k, 2, 7919 * c + k), f"run c={c} k={k} dense")
    return [c, k, len(word)]


def controls():
    """Each mutation must be rejected; returns the number of controls."""
    walk, c, k = WALKS[4], 4, 5
    good = search_readouts(walk, c, k)
    word = literal_word(walk, good)
    dropped = word[:]
    dropped.remove(["A", 31])
    moved = [list(r) for r in good]
    moved[30] = [b + 1 if i == len(moved[30]) - 1 else b
                 for i, b in enumerate(moved[30])]
    relabeled = [1] + walk[1:]
    checks = [
        fails(lambda: check_generic(dropped, c, k)),
        fails(lambda: check_generic(literal_word(walk, moved), c, k)),
        fails(lambda: check_generic(literal_word(relabeled, good), c, k)),
        fails(lambda: check_generic(word, 8, k)),
        fails(lambda: search_readouts(run_walk(4, 5), 4, 5)),
        fails(lambda: search_readouts(run_walk(2, 3), 2, 3)),
        not dense_case(word, c, k, 2, 5, reverse_factors=True),
        not dense_case(literal_word(WALKS[3], search_readouts(WALKS[3], 3, 5)),
                       3, 5, 3, 6, reverse_factors=True),
    ]
    require(all(checks), f"a semantic control was not rejected: {checks}")
    return len(checks)


def check_sources():
    sources = json.loads(read_bytes(PKG / "SOURCES.json"))
    for entry in sources["files"]:
        digest = hashlib.sha256(read_bytes(ROOT / entry["path"])).hexdigest()
        require(digest == entry["sha256"], f"source hash differs: {entry['path']}")
    return len(sources["files"])


def certificate():
    return {
        "schema_version": 1,
        "claim": "Unsigned five-source dirty connector: 36c calls in every "
                 "characteristic c >= 3; c(k + 2^k - 1) whenever c >= k.",
        "explicit_cases": [explicit_case(3), explicit_case(4)],
        "run_walk_cases": [run_case(c, k) for c, k in RUN_DOMAIN],
    }


def render(cert):
    return json.dumps(cert, separators=(",", ":"), sort_keys=True) + "\n"


def main(argv):
    require(argv in ([], ["--emit"]), "usage: verify.py [--emit]")
    text = render(certificate())
    if argv == ["--emit"]:
        sys.stdout.write(text)
        return 0
    require(read_bytes(PKG / "CERTIFICATE.json").decode() == text,
            "CERTIFICATE.json differs from the regenerated certificate")
    n_sources = check_sources()
    n_controls = controls()
    files = {name: hashlib.sha256(read_bytes(PKG / name)).hexdigest()
             for name in PACKAGE_FILES}
    print(json.dumps({"package_sha256": files, "sources_checked": n_sources,
                      "controls_rejected": n_controls}, sort_keys=True))
    print(f"{MARKER} c3_calls=108 c4_calls=144 run_cases={len(RUN_DOMAIN)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except CheckError as err:
        print(f"FAIL: {err}", file=sys.stderr)
        sys.exit(1)
