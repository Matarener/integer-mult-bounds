"""Independent position-placement census and bitset difference test."""
from collections import Counter
from itertools import combinations


def position_words(counts):
    """Place four labels in disjoint subsets; the fifth fills the remainder."""
    positions = tuple(range(9))
    for a in combinations(positions, counts[0]):
        left_a = tuple(p for p in positions if p not in a)
        for b in combinations(left_a, counts[1]):
            left_b = tuple(p for p in left_a if p not in b)
            for c in combinations(left_b, counts[2]):
                left_c = tuple(p for p in left_b if p not in c)
                for d in combinations(left_c, counts[3]):
                    word = [16] * 9
                    for label, slots in enumerate((a, b, c, d)):
                        for slot in slots:
                            word[slot] = 1 << label
                    yield tuple(word)


def difference_bits(word):
    """For each difference, intersect the prefix set with its XOR translate."""
    prefix_set = 1
    parity = [0] * 5
    for step in word[:-1]:
        for axis in range(5):
            parity[axis] ^= (step >> axis) & 1
        prefix_set |= 1 << sum(bit << axis for axis, bit in enumerate(parity))
    result = 0
    for difference in range(32):
        translated = prefix_set
        for axis in range(5):
            if (difference >> axis) & 1:
                width = 1 << axis
                low = sum(((1 << width) - 1) << start
                          for start in range(0, 32, 2 * width))
                translated = ((translated & low) << width) | (
                    (translated & (low << width)) >> width)
        if translated & prefix_set:
            result |= 1 << difference
    return result


def canonical_census(triple):
    counts = tuple((4 if axis == 0 else 2) - ((triple >> axis) & 1)
                   for axis in range(5))
    histogram = Counter()
    for singles in position_words(counts):
        histogram[difference_bits(singles + (triple,)).bit_count()] += 1
    return histogram
