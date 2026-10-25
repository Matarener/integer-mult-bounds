"""Verify the characteristic-four floor bounds for the unsigned connector.

Stdlib only. Checks raise explicit exceptions so they stay active under -O.
"""
import hashlib
import itertools
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py")
COUNT_MAX_C = 12
COUNT_MAX_K = 200
DIGIT = 3  # bits per Z/4 coordinate in the packed encoding


class CheckError(Exception):
    pass


def require(cond, message):
    if not cond:
        raise CheckError(message)


def packed_masks(k):
    """LOW keeps each coordinate mod 4; HIGH selects each coordinate's 2-bit."""
    low = sum(3 << (DIGIT * j) for j in range(k))
    high = sum(2 << (DIGIT * j) for j in range(k))
    return low, high


def packed_prefixes(path, k):
    """Prefix count vectors mod 4, one packed integer per walk boundary."""
    q = [0] * k
    out = [0]
    for j in path:
        q[j] = (q[j] + 1) % 4
        out.append(sum(v << (DIGIT * i) for i, v in enumerate(q)))
    return out


def pair_sums(prefixes, low):
    vals = sorted(set(prefixes))
    return {(a + b) & low for i, a in enumerate(vals) for b in vals[i:]}


def binary_mask(m, k):
    return sum(((m >> j) & 1) << (DIGIT * j) for j in range(k))


def covered(target, s2, low):
    """True when some boundary 4-multiset sums to target mod 4.

    Adding 4 to every digit before subtracting keeps digits borrow-free.
    """
    shifted = target + ((low // 3) << 2)
    return any(((shifted - s) & low) in s2 for s in s2)


def check_walk(cert):
    """The nine-source walk of PR4248 reaches all 511 masks."""
    path = cert["walk9"]
    require(sorted(path) == sorted(list(range(9)) * 4), "walk9 must use each source four times")
    low, _ = packed_masks(9)
    s2 = pair_sums(packed_prefixes(path, 9), low)
    for m in range(1, 2 ** 9):
        require(covered(binary_mask(m, 9), s2, low), f"walk9 misses mask {m}")
    return path


def check_insertions(path):
    """Every four-event insertion of a tenth source misses some mask.

    Returns (insertions checked, distinct witness masks used).
    """
    k = 10
    low, _ = packed_masks(k)
    length = len(path) + 4
    order = [binary_mask(m, k) for m in range(1, 2 ** k)]
    witnesses = set()
    checked = 0
    for pos in itertools.combinations(range(length), 4):
        rest = iter(path)
        chosen = set(pos)
        walk = [9 if i in chosen else next(rest) for i in range(length)]
        s2 = pair_sums(packed_prefixes(walk, k), low)
        for idx, target in enumerate(order):
            if not covered(target, s2, low):
                witnesses.add(target)
                if idx:  # move the witness to the front for the next insertion
                    order.insert(0, order.pop(idx))
                break
        else:
            raise CheckError(f"insertion {pos} reaches every mask")
        checked += 1
    require(checked == math.comb(40, 4), "insertion count must be C(40,4)")
    return checked, len(witnesses)


def multiset_count(c, k):
    """PR4248 bound: c-multisets of the ck boundary values."""
    return math.comb(c * k + c - 1, c)


def parity_count(c, k):
    """Distinct parity sums of c boundaries, after the adjacency collapse."""
    n = c * k - 1
    spread = sum(math.comb(n - i + 1, i) for i in range(1, c + 1))
    adjacent = k * sum(math.comb(n, i) for i in range(c - 1))
    return spread + adjacent


def first_failure(count, c):
    first = None
    for k in range(1, COUNT_MAX_K + 1):
        fails = count(c, k) < 2 ** k - 1
        if fails and first is None:
            first = k
        if first is not None:
            require(fails, f"counting failure not monotone at c={c} k={k}")
    require(first is not None, f"no counting failure for c={c}")
    return first


def check_counting():
    old = {c: first_failure(multiset_count, c) for c in range(2, COUNT_MAX_C + 1)}
    new = {c: first_failure(parity_count, c) for c in range(2, COUNT_MAX_C + 1, 2)}
    require(old[4] == 22 and new[4] == 21, "c=4 thresholds must be 22 and 21")
    require(parity_count(4, 21) == 1743531 < 2 ** 21 - 1, "c=4 k=21 parity count")
    require(parity_count(4, 20) >= 2 ** 20 - 1, "c=4 k=20 is not excluded")
    require(new[2] == 6, "c=2 bound must stay above the known N(2)=4")
    for c, k in new.items():
        require(k <= old[c], f"parity bound weaker than multiset bound at c={c}")
    return old, new


def parity_vector(path, t, k):
    v = 0
    for j in path[:t]:
        v ^= 1 << j
    return v


def check_parity_lemma(path):
    """On walk9, every parity sum of at most four inner boundaries lies in the
    two families counted by parity_count: a spread subset, or e_j plus at most
    two boundaries. Also checks each 4-multiset reduces to such a subset."""
    k = 9
    n = 4 * k - 1
    u = [parity_vector(path, t, k) for t in range(4 * k + 1)]
    require(u[0] == 0 and u[4 * k] == 0, "end parities must vanish")
    spread = set()
    small = {0}
    for size in (1, 2):
        for r in itertools.combinations(range(1, n + 1), size):
            acc = 0
            for t in r:
                acc ^= u[t]
            small.add(acc)
    adjacent = {(1 << j) ^ s for j in range(k) for s in small}
    total = 0
    for size in range(1, 5):
        for r in itertools.combinations(range(1, n + 1), size):
            acc = 0
            for t in r:
                acc ^= u[t]
            if all(b - a > 1 for a, b in zip(r, r[1:])):
                spread.add(acc)
            else:
                require(acc in adjacent, f"adjacent subset {r} escapes the bound")
            total += 1
    require(len(spread | adjacent) <= parity_count(4, k), "walk9 parity count")
    reached = set()
    for ts in itertools.combinations_with_replacement(range(4 * k + 1), 4):
        acc = 0
        for t in ts:
            acc ^= u[t]
        reached.add(acc)
    require(reached <= spread | adjacent | {0}, "a 4-multiset parity escapes")
    require(len(reached) == 2 ** k, "walk9 parities must reach every mask and zero")
    return total


def check_controls(path):
    """Mutations that must be rejected."""
    rejected = 0
    low, _ = packed_masks(9)
    swapped = path[:]
    swapped[0], swapped[1] = swapped[1], swapped[0]  # breaks one readout
    s2 = pair_sums(packed_prefixes(swapped, 9), low)
    if not all(covered(binary_mask(m, 9), s2, low) for m in range(1, 2 ** 9)):
        rejected += 1
    s2 = pair_sums(packed_prefixes(sorted(path), 9), low)  # run walk
    if not all(covered(binary_mask(m, 9), s2, low) for m in range(1, 2 ** 9)):
        rejected += 1
    if parity_count(4, 22) < multiset_count(4, 22):  # refinement must be tighter
        rejected += 1
    require(rejected == 3, f"only {rejected} of 3 controls rejected")
    return rejected


def receipt():
    h = hashlib.sha256()
    for name in PACKAGE_FILES:
        data = (HERE / name).read_bytes()
        h.update(name.encode() + b"\0" + hashlib.sha256(data).hexdigest().encode() + b"\n")
    return h.hexdigest()


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    path = check_walk(cert)
    subsets = check_parity_lemma(path)
    old, new = check_counting()
    controls = check_controls(path)
    print(f"walk9_masks=511 parity_lemma_subsets={subsets} controls={controls}")
    print("multiset_first_failure", " ".join(f"c{c}:k{k}" for c, k in old.items()))
    print("parity_first_failure", " ".join(f"c{c}:k{k}" for c, k in new.items()))
    if "--skip-insertions" not in sys.argv:
        checked, witnesses = check_insertions(path)
        print(f"walk9_insertions_checked={checked} witness_masks={witnesses}")
    print("receipt_sha256", receipt())
    print(f"PASS_CONNECTOR_CHAR4_FLOOR_BOUNDS c4_excludes_k>={new[4]}"
          + ("" if "--skip-insertions" in sys.argv else " walk9_has_no_ten_source_extension"))


if __name__ == "__main__":
    try:
        main()
    except CheckError as exc:
        print("FAIL", exc)
        sys.exit(1)
