"""Verify the depth-block floor package for the unsigned connector.

Stdlib only. Checks run with explicit exceptions so they stay active under -O.
"""
import hashlib
import itertools
import json
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py")
BLOCK_MAX_C = 7
COUNT_MAX_C = 9
COUNT_MAX_K = 200


class CheckError(Exception):
    pass


def require(cond, message):
    if not cond:
        raise CheckError(message)


def floor_calls(c, k):
    return c * (k + 2 ** k - 1)


def mask_vector(m, k):
    return tuple((m >> j) & 1 for j in range(k))


def prefixes(path, k, c):
    q = [0] * k
    out = [tuple(q)]
    for j in path:
        q[j] = (q[j] + 1) % c
        out.append(tuple(q))
    return out


def first_readouts(path, k, c):
    """Map each realizable nonzero mask to its first c-multiset of boundaries."""
    qs = prefixes(path, k, c)
    found = {}
    for ts in itertools.combinations_with_replacement(range(len(qs)), c):
        s = tuple(sum(qs[t][i] for t in ts) % c for i in range(k))
        if max(s) <= 1 and any(s):
            m = sum(bit << i for i, bit in enumerate(s))
            found.setdefault(m, ts)
    return found


def build_word(path, readouts):
    """Interleave readouts (mask -> boundary tuple) into the source path."""
    at = {}
    for m, ts in readouts.items():
        for t in ts:
            at.setdefault(t, []).append(m)
    word = []
    for t in range(len(path) + 1):
        word.extend(("A", m) for m in sorted(at.get(t, [])))
        if t < len(path):
            word.append(("B", path[t]))
    return word


def simulate(word, k, c):
    """Generic simulation over Z/c with arbitrary noncommuting maps.

    z is tracked as coefficients of (z0, B_0 x_0, ..., B_{k-1} x_{k-1}); each
    output accumulates A_m applied to that formal sum. Integer coefficients act
    through Z/c, the prime subring of any ring of characteristic c.
    """
    z = [1] + [0] * k
    outs = {}
    for kind, idx in word:
        if kind == "B":
            z[1 + idx] = (z[1 + idx] + 1) % c
        elif kind == "A":
            acc = outs.setdefault(idx, [0] * (k + 1))
            for i in range(k + 1):
                acc[i] = (acc[i] + z[i]) % c
        else:
            raise CheckError(f"unknown call kind {kind}")
    return z, outs


def check_word(word, k, c):
    z, outs = simulate(word, k, c)
    require(z == [1] + [0] * k, "connector not restored")
    require(set(outs) == set(range(1, 2 ** k)), "output set mismatch")
    for m, acc in outs.items():
        require(acc[0] == 0, f"connector dirt left in output {m}")
        require(tuple(acc[1:]) == mask_vector(m, k), f"wrong row for output {m}")
    counts = {}
    for call in word:
        counts[call] = counts.get(call, 0) + 1
    require(set(counts.values()) == {c}, "some operator not called exactly c times")
    require(len(counts) == k + 2 ** k - 1, "operator set mismatch")
    require(len(word) == floor_calls(c, k), "length differs from the floor")


def block_walk(c, k):
    """Concatenate two-source blocks a b a^(c-1) b^(c-1), plus a^c if k is odd.

    Returns the path and, per block, a map from each nonzero block mask to the
    single boundary whose prefix equals it.
    """
    path, blocks = [], []
    for a in range(0, k, 2):
        start = len(path)
        if a + 1 < k:
            b = a + 1
            path += [a, b] + [a] * (c - 1) + [b] * (c - 1)
            hit = {(1, 0): start + 1, (1, 1): start + 2, (0, 1): start + c + 1}
            blocks.append(((a, b), hit))
        else:
            path += [a] * c
            blocks.append(((a,), {(1,): start + 1}))
    return path, blocks


def block_readouts(c, k):
    path, blocks = block_walk(c, k)
    require(len(blocks) <= c, "more blocks than readouts per mask")
    readouts = {}
    for m in range(1, 2 ** k):
        bits = mask_vector(m, k)
        ts = []
        for srcs, hit in blocks:
            key = tuple(bits[j] for j in srcs)
            if any(key):
                ts.append(hit[key])
        ts += [0] * (c - len(ts))
        readouts[m] = tuple(sorted(ts))
    return path, readouts


def check_blocks():
    """Theorem A: the floor is attained for every k <= 2c, here for c <= 7."""
    cases = 0
    for c in range(2, BLOCK_MAX_C + 1):
        for k in range(1, 2 * c + 1):
            path, readouts = block_readouts(c, k)
            qs = prefixes(path, k, c)
            for m, ts in readouts.items():
                s = tuple(sum(qs[t][i] for t in ts) % c for i in range(k))
                require(s == mask_vector(m, k), f"block readout c={c} k={k} m={m}")
            check_word(build_word(path, readouts), k, c)
            cases += 1
    return cases


def check_depth_one(c, k):
    """Count walks (each source c times) whose single prefixes give every mask."""
    def arrangements(left, prefix):
        if not any(left):
            yield list(prefix)
            return
        for j in range(k):
            if left[j]:
                left[j] -= 1
                prefix.append(j)
                yield from arrangements(left, prefix)
                prefix.pop()
                left[j] += 1

    good = total = 0
    for path in arrangements([c] * k, []):
        total += 1
        qs = set(prefixes(path, k, c))
        if all(mask_vector(m, k) in qs for m in range(1, 2 ** k)):
            good += 1
    require(total == math.factorial(c * k) // math.factorial(c) ** k, "arrangement count")
    return good


def check_depth_lemma():
    """Lemma C controls: depth-one blocks exist for two sources, never for three."""
    for c in range(2, BLOCK_MAX_C + 1):
        path, blocks = block_walk(c, 2)
        qs = set(prefixes(path, 2, c))
        require({(1, 0), (1, 1), (0, 1)} <= qs, f"two-source block depth c={c}")
    totals = {}
    for c in (2, 3, 4):
        totals[c] = check_depth_one(c, 3)
        require(totals[c] == 0, f"depth-one three-source walk exists at c={c}")
    return totals


def dense_check(path, readouts, k, c, dim, seed):
    """Run the literal word on random singular noncommuting matrices over Z/c."""
    rng = random.Random(seed)

    def mat():
        return [[rng.randrange(c) for _ in range(dim)] for _ in range(dim)]

    def mul(a, v):
        return [sum(a[i][j] * v[j] for j in range(dim)) % c for i in range(dim)]

    bs = [mat() for _ in range(k)]
    xs = [[rng.randrange(c) for _ in range(dim)] for _ in range(k)]
    a_maps = {m: mat() for m in range(1, 2 ** k)}
    z0 = [rng.randrange(c) for _ in range(dim)]
    z = list(z0)
    ys = {m: [0] * dim for m in a_maps}
    for kind, idx in build_word(path, readouts):
        if kind == "B":
            z = [(u + v) % c for u, v in zip(z, mul(bs[idx], xs[idx]))]
        else:
            ys[idx] = [(u + v) % c for u, v in zip(ys[idx], mul(a_maps[idx], z))]
    require(z == z0, "dense connector not restored")
    for m, y in ys.items():
        want = [0] * dim
        for j in range(k):
            if m >> j & 1:
                want = [(u + v) % c for u, v in zip(want, mul(a_maps[m], mul(bs[j], xs[j])))]
        require(y == want, f"dense output {m} wrong")


def check_walks(cert):
    """Explicit characteristic-four floor walks."""
    c = cert["characteristic"]
    require(c == 4, "certificate characteristic")
    out = {}
    for key, path in sorted(cert["floor_walks"].items(), key=lambda kv: int(kv[0])):
        k = int(key)
        require(sorted(path) == sorted(list(range(k)) * c), f"k={k}: event counts")
        readouts = first_readouts(path, k, c)
        require(len(readouts) == 2 ** k - 1, f"k={k}: covers {len(readouts)} masks")
        check_word(build_word(path, readouts), k, c)
        dense_check(path, readouts, k, c, dim=2, seed=k)
        out[k] = (path, readouts)
    return out


def delete_source(path, j):
    return [i - (i > j) for i in path if i != j]


def check_deletion(walks, c):
    checked = 0
    for k, (path, _) in walks.items():
        for j in range(k):
            smaller = delete_source(path, j)
            require(len(first_readouts(smaller, k - 1, c)) == 2 ** (k - 1) - 1,
                    f"deletion of source {j} from k={k} lost coverage")
            checked += 1
    return checked


def counting_threshold(c):
    """First k with C(ck+c-1, c) < 2^k - 1; checked to stay failing up to COUNT_MAX_K."""
    first = None
    for k in range(1, COUNT_MAX_K + 1):
        fails = math.comb(c * k + c - 1, c) < 2 ** k - 1
        if fails and first is None:
            first = k
        if first is not None:
            require(fails, f"counting failure not monotone at c={c} k={k}")
    require(first is not None, f"no counting failure for c={c}")
    return first


def check_counting():
    table = {c: counting_threshold(c) for c in range(2, COUNT_MAX_C + 1)}
    require(table[3] == 14, "c=3 threshold must agree with PR4232")
    require(math.comb(87, 4) == 2225895 and math.comb(91, 4) == 2672670, "c=4 binomials")
    return table


def check_controls(cert, walks):
    """Mutations that must be rejected."""
    rejected = 0
    path9, readouts9 = walks[9]
    word = build_word(path9, readouts9)
    for mutate in (
        lambda w: w[:-1] if w[-1][0] == "A" else w[1:],
        lambda w: [c for c in w if c != ("A", 511)] + [("A", 511)] * 4,
        lambda w: [("B", 1) if c == ("B", 0) else c for c in w],
    ):
        try:
            check_word(mutate(word), 9, 4)
        except CheckError:
            rejected += 1
    try:  # The same word read in characteristic eight leaves connector dirt.
        check_word(word, 9, 8)
    except CheckError:
        rejected += 1
    run = sorted(path9)  # Run walk: masks of weight above four are missed.
    if len(first_readouts(run, 9, 4)) < 2 ** 9 - 1:
        rejected += 1
    try:  # More blocks than readouts: k = 2c + 1 needs c + 1 blocks.
        block_readouts(3, 7)
    except CheckError:
        rejected += 1
    require(rejected == 6, f"only {rejected} of 6 controls rejected")
    return rejected


def receipt():
    h = hashlib.sha256()
    for name in PACKAGE_FILES:
        data = (HERE / name).read_bytes()
        h.update(name.encode() + b"\0" + hashlib.sha256(data).hexdigest().encode() + b"\n")
    return h.hexdigest()


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    cases = check_blocks()
    depth = check_depth_lemma()
    walks = check_walks(cert)
    deletions = check_deletion(walks, 4)
    table = check_counting()
    controls = check_controls(cert, walks)
    top = max(walks)
    print(f"block_cases={cases} depth_one_three_source_walks="
          + ",".join(f"c{c}:{n}" for c, n in depth.items()))
    print("c4_floor_calls", " ".join(f"k{k}={floor_calls(4, k)}" for k in walks))
    print(f"deletion_checks={deletions} controls={controls}")
    print("counting_first_failure", " ".join(f"c{c}:k{k}" for c, k in table.items()))
    print("receipt_sha256", receipt())
    print(f"PASS_CONNECTOR_DEPTH_BLOCKS blocks_k<=2c c4_attained_k<={top} "
          f"c4_counting_excludes_k>={table[4]}")


if __name__ == "__main__":
    try:
        main()
    except CheckError as exc:
        print("FAIL", exc)
        sys.exit(1)
