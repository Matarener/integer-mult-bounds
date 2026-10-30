"""Exact finite obstruction for a single triple in ten source steps."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import factorial
from pathlib import Path
import json

from oracle import canonical_census, difference_bits


def require(condition, message):
    if not condition:
        raise ValueError(message)


def next_word(word):
    """Advance a nine-entry multiset permutation in lexicographic order."""
    pivot = -1
    for index in range(7, -1, -1):
        if word[index] < word[index + 1]:
            pivot = index
            break
    if pivot == -1:
        return False
    for other in range(8, pivot, -1):
        if word[other] > word[pivot]:
            word[pivot], word[other] = word[other], word[pivot]
            word[pivot + 1:] = reversed(word[pivot + 1:])
            return True
    raise ValueError("lexicographic successor is missing")


def prefixes(word):
    values = [0]
    for step in word:
        values.append(values[-1] ^ step)
    return values


def difference_set(word):
    values = prefixes(word)[:-1]
    return {left ^ right for left in values for right in values}


def validate(word):
    require(len(word) == 10, "ten source steps required")
    require(all(type(step) is int and 0 < step < 32 for step in word),
            "nonzero five-bit steps required")
    require(sum(step.bit_count() == 3 for step in word) == 1,
            "exactly one triple required")
    require(all(step.bit_count() in (1, 3) for step in word),
            "remaining steps must be singletons")
    counts = [sum((step >> axis) & 1 for step in word) for axis in range(5)]
    require(sorted(counts) == [2, 2, 2, 2, 4], "incidence profile required")
    require(prefixes(word)[-1] == 0, "restored connector required")


def census(triple):
    counts = tuple((4 if axis == 0 else 2) - ((triple >> axis) & 1)
                   for axis in range(5))
    word = [1 << axis for axis, count in enumerate(counts) for _ in range(count)]
    expected = factorial(9)
    for count in counts:
        expected //= factorial(count)
    histogram = Counter()
    best = None
    # There are at most 9! multiset permutations. Exhaustion is checked below.
    for _ in range(factorial(9)):
        full = tuple(word) + (triple,)
        validate(full)
        size = len(difference_set(full))
        histogram[size] += 1
        if best is None or size > best[0]:
            best = (size, full)
        if not next_word(word):
            break
    require(sum(histogram.values()) == expected, "permutation census incomplete")
    require(best is not None, "empty census")
    return histogram, best


def rejected(word):
    try:
        validate(word)
    except ValueError:
        return True
    return False


def controls(best):
    word = best[1]
    require(not rejected(word), "attaining word rejected")
    mutations = (word[:-1], (0,) + word[1:], (True,) + word[1:],
                 (32,) + word[1:], word[:-1] + (3,),
                 word[:-1] + (11,), (7,) + word[1:])
    require(all(rejected(w) for w in mutations), "invalid word accepted")
    masks = difference_set(word)
    require(len(masks) == 30 and len(set(range(32)) - masks) == 2,
            "sharp witness does not miss exactly two masks")
    # Cyclic rotation changes prefixes by translation, preserving differences.
    for cut in range(10):
        rotated = word[cut:] + word[:cut]
        validate(rotated)
        require(difference_set(rotated) == masks, "rotation reduction failed")
    # A planted full cover exercises the accepting branch, outside this alphabet.
    gray = tuple(index ^ (index >> 1) for index in range(32)) + (0,)
    gray_word = tuple(gray[i] ^ gray[i + 1] for i in range(32))
    require(difference_set(gray_word) == set(range(32)), "full cover rejected")
    require(difference_bits(gray_word) == (1 << 32) - 1, "oracle full cover failed")
    require(difference_set((1, 1, 1, 1)) == {0, 1}, "repeated-prefix test failed")
    require(difference_bits((1, 1, 1, 1)) == 3, "oracle repeated-prefix test failed")
    return len(mutations)


def source_hashes():
    package = Path(__file__).resolve().parent
    paths = sorted(package.iterdir())
    require(len(paths) <= 16, "unexpected package contents")
    return {path.name: sha256(path.read_bytes()).hexdigest()
            for path in paths if path.is_file()}


def main():
    histograms = {}
    best = None
    for axes in combinations(range(5), 3):
        triple = sum(1 << axis for axis in axes)
        histogram, attaining = census(triple)
        key = "contains_repeated" if triple & 1 else "avoids_repeated"
        if key in histograms:
            require(histograms[key] == histogram, "coordinate-symmetry mismatch")
        histograms[key] = histogram
        if best is None or attaining[0] > best[0]:
            best = attaining
    require(sum(histograms["contains_repeated"].values()) == 15120,
            "wrong first domain size")
    require(sum(histograms["avoids_repeated"].values()) == 7560,
            "wrong second domain size")
    require(histograms["contains_repeated"] == canonical_census(7),
            "independent containing-triple census disagrees")
    require(histograms["avoids_repeated"] == canonical_census(14),
            "independent avoiding-triple census disagrees")
    require(max(histograms["contains_repeated"]) == 30, "wrong sharp maximum")
    require(max(histograms["avoids_repeated"]) == 26, "wrong second maximum")
    require(best is not None, "no attaining word")
    rejected_count = controls(best)
    # Positive even incidences summing to 12 have one four and four twos.
    prices = (1, 4, 10, 16, 28)
    base_bill = 2 * sum(prices)
    require(base_bill + 2 * min(prices) == 120, "old incidence tariff changed")
    require(base_bill + 4 * min(prices) == 122, "new incidence floor changed")
    receipt = {"status": "PASS_ONE_TRIPLE_TEN_STEP_OBSTRUCTION",
               "primary_words": 6 * 15120 + 4 * 7560,
               "independent_words": 15120 + 7560,
               "covering_words": 0, "sharp_maximum_masks": best[0],
               "attaining_word": best[1],
               "attaining_prefixes": prefixes(best[1]),
               "missing_masks": sorted(set(range(32)) - difference_set(best[1])),
               "canonical_histograms": histograms,
               "rejected_word_controls": rejected_count,
               "package_sha256": source_hashes()}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
