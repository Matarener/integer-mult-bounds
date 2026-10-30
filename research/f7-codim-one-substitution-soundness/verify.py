#!/usr/bin/env python3
"""Codimension-one soundness of the fixed L/2 substitution on double transversals.

The walk is the PR943 singleton prefix model: q_0 = 0 and
q_{i+1} = q_i XOR (1 << w_i). A word is restored when every label occurs a
positive even number of times, simple when q_0, ..., q_{L-1} are distinct, and
universal when the sumset of those states is F_2^n.

False pruning means the substituted budget base(n, L) rejects a universal word
that the actual class sizes still admit. This verifier checks the written
argument in PROOF.md. It does not import a predecessor enumerator.

Apache-2.0.
"""

import json
from itertools import combinations


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binom2(k):
    return k * (k - 1) // 2


def parity(value):
    return bin(value).count("1") & 1


def base_budget(n, length):
    require(length % 2 == 0 and length > 0, "even positive length")
    half = length // 2
    return 2 * binom2(half) - ((1 << (n - 1)) - 1)


def kernel_count(length, stays):
    """Number of prefix states q_0, ..., q_{L-1} in the kernel of f.

    `stays` are the step indices that preserve f. Every other step flips f,
    and f(q_0) = 0.
    """
    stay = set(stays)
    require(len(stay) == len(stays), "duplicate stay")
    bit = 0
    zeros = 0
    for index in range(length):
        if bit == 0:
            zeros += 1
        if index not in stay:
            bit ^= 1
    return zeros


def two_stay_lemma(lengths=(6, 8, 10, 12, 14)):
    """Exactly two preserving steps change the zero count by at most one."""
    checked = 0
    for length in lengths:
        require(length % 2 == 0, "even length")
        balanced = length // 2
        for i, j in combinations(range(length), 2):
            zeros = kernel_count(length, (i, j))
            require(abs(zeros - balanced) <= 1, f"two-stay imbalance {length} {i} {j}")
            # The patterns differ from k |-> k mod 2 exactly on (i, j].
            interval = range(i + 1, j + 1)
            evens = sum(1 for k in interval if k % 2 == 0)
            odds = sum(1 for k in interval if k % 2 == 1)
            require(zeros - balanced == odds - evens, "interval delta")
            checked += 1
    four_stay = kernel_count(8, (1, 2, 3, 4))
    require(abs(four_stay - 4) == 2, "four stays can leave the two-stay bound")
    return checked


def three_point_sums(dimension=4):
    """Any three distinct vectors have three distinct pairwise sums."""
    space = range(1 << dimension)
    checked = 0
    for triple in combinations(space, 3):
        sums = {triple[0] ^ triple[1], triple[0] ^ triple[2], triple[1] ^ triple[2]}
        require(len(sums) == 3 and 0 not in sums, "three-point sums")
        checked += 1
    return checked


def five_point_cover():
    """Every 5-subset of F_2^3 meets every nonzero direction."""
    space = range(8)
    checked = 0
    for subset in combinations(space, 5):
        sums = {left ^ right for left, right in combinations(subset, 2)}
        require(sums == set(range(1, 8)), "five-point cover")
        checked += 1
    # Sharpness: some 4-subset misses a direction.
    missed = {left ^ right for left, right in combinations((0, 1, 2, 3), 2)}
    require(missed != set(range(1, 8)), "four-point cover is not forced")
    return checked


def prefix_states(word):
    state = 0
    states = [0]
    for label in word:
        state ^= 1 << label
        states.append(state)
    return states


def restored(word, n):
    counts = [0] * n
    for label in word:
        counts[label] += 1
    return all(count > 0 and count % 2 == 0 for count in counts)


def universal(states, n):
    occupied = set(states[:-1])
    require(len(occupied) == len(states) - 1, "simple prefix")
    return {left ^ right for left in occupied for right in occupied} == set(range(1 << n))


def class_excess(states, mask):
    occupied = set(states[:-1])
    even = [point for point in occupied if parity(point & mask) == 0]
    odd = [point for point in occupied if parity(point & mask) == 1]
    even_sums = {left ^ right for left, right in combinations(even, 2)}
    odd_sums = {left ^ right for left, right in combinations(odd, 2)}
    excess = binom2(len(even)) + binom2(len(odd)) - len(even_sums) - len(odd_sums)
    return len(even), len(odd), excess


def falsely_pruned(n, length, states, mask):
    even, odd, excess = class_excess(states, mask)
    base = base_budget(n, length)
    slack = ((even - odd) // 2) ** 2
    return base < excess <= base + slack, (even, odd, excess, base, base + slack)


def enumerate_words(n, length):
    seen = {0}
    word = []

    def walk(index, state, max_label):
        if index == length:
            yield tuple(word)
            return
        for label in range(min(max_label + 2, n)):
            nxt = state ^ (1 << label)
            if index == length - 1:
                if nxt == 0:
                    word.append(label)
                    yield from walk(index + 1, 0, max(max_label, label))
                    word.pop()
                continue
            if nxt in seen:
                continue
            seen.add(nxt)
            word.append(label)
            yield from walk(index + 1, nxt, max(max_label, label))
            word.pop()
            seen.discard(nxt)

    yield from walk(0, 0, -1)


def universal_words(n, length):
    words = []
    for word in enumerate_words(n, length):
        if not restored(word, n):
            continue
        states = prefix_states(word)
        if universal(states, n):
            words.append(word)
    return words


def weight_masks(n, weight):
    return [mask for mask in range(1, 1 << n) if bin(mask).count("1") == weight]


def double_transversal_theorem():
    """Weight at least n-1 is sound for every simple universal word of length 2n, n<=4."""
    summary = {}
    for n in (3, 4):
        length = 2 * n
        words = universal_words(n, length)
        base = base_budget(n, length)
        per_weight = {}
        for weight in range(n - 1, n + 1):
            fires = {}
            for mask in weight_masks(n, weight):
                fires[mask] = 0
                for word in words:
                    states = prefix_states(word)
                    hit, detail = falsely_pruned(n, length, states, mask)
                    even, odd, excess, got_base, _correct = detail
                    require(got_base == base, "base")
                    require(not hit, f"codimension-one false prune n={n} mask={mask}")
                    if weight == n:
                        require(even == odd == n, "all-ones classes are time parity")
                        require(excess <= base, "all-ones excess")
                    else:
                        require(abs(even - odd) <= 2, "two-stay size bound")
                        if abs(even - odd) == 2:
                            if n == 4:
                                require(excess == 3, "exact five-plus-three excess")
                            if n == 3:
                                require(excess == base, "tight n=3 excess")
                        fires[mask] += int(hit)
            require(all(count == 0 for count in fires.values()), "no fires")
            per_weight[weight] = len(fires)
        summary[f"{n},{length}"] = {"universal": len(words), "weights": per_weight, "base": base}
    require(summary["4,8"]["universal"] == 22, "published (4,8) universal count")
    require(summary["3,6"]["universal"] == 4, "published (3,6) universal count")
    # Known bit-0 false prune, so the predicate is not vacuously strict.
    witness = (0, 1, 0, 2, 1, 3, 2, 3)
    hit, detail = falsely_pruned(4, 8, prefix_states(witness), 0b0001)
    require(hit and detail == (6, 2, 8, 5, 9), "bit-0 witness still false-prunes")
    return summary


def weight_law_fails_at_four_twelve():
    """Three weight-3 masks fire at (4, 12); omitting only the last label does not."""
    words = universal_words(4, 12)
    counts = {}
    for mask in weight_masks(4, 3):
        counts[mask] = sum(
            falsely_pruned(4, 12, prefix_states(word), mask)[0] for word in words
        )
    require(counts[0b0111] == 0, "last-coordinate omission stays sound")
    require(counts[0b1011] == 4 and counts[0b1101] == 4 and counts[0b1110] == 4,
            "the other three weight-3 masks fire")
    require(len(words) == 314, "published (4,12) universal count")
    return {"universal": len(words), "weight3_fires": counts}


def exception_ledger():
    """Finite soundness of the two published weight-(n-2) exceptions. Not a theorem."""
    rows = []
    for n, length, mask, expected_words, expected_max in (
        (4, 8, 0b1010, 22, 3),
        (5, 12, 0b11010, 828, 14),
    ):
        words = universal_words(n, length)
        require(len(words) == expected_words, "exception domain count")
        base = base_budget(n, length)
        max_excess = 0
        fires = 0
        for word in words:
            hit, detail = falsely_pruned(n, length, prefix_states(word), mask)
            fires += int(hit)
            max_excess = max(max_excess, detail[2])
        require(fires == 0 and max_excess == expected_max and max_excess <= base,
                "exception ledger")
        rows.append({"n": n, "L": length, "mask": mask, "max_excess": max_excess, "base": base})
    return rows


def main():
    receipt = {
        "two_stay_pairs": two_stay_lemma(),
        "three_point_triples": three_point_sums(),
        "five_point_subsets": five_point_cover(),
        "double_transversal": double_transversal_theorem(),
        "four_twelve": weight_law_fails_at_four_twelve(),
        "exceptions": exception_ledger(),
        "new_kappa": False,
    }
    print("PASS_F7_CODIM_ONE_SUBSTITUTION_SOUNDNESS " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
