"""Independent two-phase connector census. Nick Petalas. Apache-2.0."""

from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import factorial


def require(ok, message):
    if not ok:
        raise ValueError(message)


def matchings(n):
    """Iterative perfect matchings, labelled by least unmatched position."""
    require(type(n) is int and 1 <= n <= 5, "matching domain is 1..5")
    layer = [(-1,) * (2 * n)]
    for label in range(n):
        following = []
        for word in layer:
            first = word.index(-1)
            for second in range(first + 1, 2 * n):
                if word[second] == -1:
                    updated = list(word)
                    updated[first] = updated[second] = label
                    following.append(tuple(updated))
        require(len(following) <= 945, "matching capacity exceeded")
        layer = following
    require(len(layer) == factorial(2 * n) // (2**n * factorial(n)), "pairings")
    return layer


def source_words(n, triple):
    if not triple:
        return matchings(n)
    require(2 <= n <= 5, "triple domain is 2..5")
    words = []
    for places in combinations(range(2 * n + 1), 3):
        for ordinary in matchings(n - 1):
            rest = iter(ordinary)
            words.append(
                tuple(0 if i in places else next(rest) + 1 for i in range(2 * n + 1))
            )
    require(len(words) <= 17325, "source-word capacity exceeded")
    return words


def restoring_ports(word, cut, n, triple):
    """Port-one bitsets from the two-phase restoration equations."""
    positions = [
        tuple(i for i, j in enumerate(word) if j == label) for label in range(n)
    ]
    free = [at for at in positions[int(triple) :] if (at[0] < cut) == (at[1] < cut)]
    seeds = [0]
    if triple:
        at = positions[0]
        seeds = []
        for single in range(3):
            other = [at[i] for i in range(3) if i != single]
            if (other[0] < cut) != (other[1] < cut):
                seeds.append((1 << other[0]) | (1 << other[1]))
    result = []
    for seed in seeds:
        for choice in range(1 << len(free)):
            ports = seed
            for i, at in enumerate(free):
                if choice & (1 << i):
                    ports |= (1 << at[0]) | (1 << at[1])
            result.append(ports)
    require(len(result) <= 48, "port-assignment capacity exceeded")
    return result


def queries(word, cut, ports, n):
    """Literal F2 rows, grouped by their two incoming-dirt coefficients."""
    dirt = (1 << n, 2 << n)
    roots = [dirt[0] ^ dirt[1], dirt[1]]
    groups = [0, 1, 1, 1]
    mask = (1 << n) - 1
    for i in range(len(word) + 1):
        if i == cut:
            roots[0] ^= roots[1]
            for value in roots:
                groups[value >> n] |= 1 << (value & mask)
        if i < len(word):
            roots[(ports >> i) & 1] ^= 1 << word[i]
            for value in roots:
                groups[value >> n] |= 1 << (value & mask)
    require(tuple(roots) == dirt, "literal dirty restoration failed")
    return tuple(groups)


def values(bits):
    return tuple(i for i in range(32) if bits & (1 << i))


def paired_masks(groups):
    covered = 1
    for bits in groups[1:]:
        points = values(bits)
        for i, a in enumerate(points):
            for b in points[i + 1 :]:
                covered |= 1 << (a ^ b)
    return covered


def three_read(groups, target):
    """Three nonzero binary dirt rows sum to zero iff all three differ."""
    return any(
        groups[3] & (1 << (target ^ a ^ b))
        for a in values(groups[1])
        for b in values(groups[2])
    )


def census(n, triple):
    require(type(n) is int and 2 <= n <= 5, "census domain is 2..5")
    words = source_words(n, triple)
    histogram = Counter()
    universal = 0
    repaired = 0
    first = None
    digest = sha256()
    full = (1 << (1 << n)) - 1
    for word in words:
        for cut in range(len(word) + 1):
            for ports in restoring_ports(word, cut, n, triple):
                groups = queries(word, cut, ports, n)
                covered = paired_masks(groups)
                count = covered.bit_count()
                histogram[count] += 1
                universal += int(covered == full)
                success = False
                if not triple and count == (1 << n) - 1:
                    missing = (full ^ covered).bit_length() - 1
                    success = three_read(groups, missing)
                    repaired += int(success)
                if first is None and (success or covered == full):
                    first = {
                        "word": list(word),
                        "cut": cut,
                        "ports": ports,
                        "groups": list(groups),
                        "three_read_repair": success,
                    }
                digest.update(
                    bytes(word)
                    + bytes((cut,))
                    + ports.to_bytes(2, "little")
                    + covered.to_bytes(4, "little")
                    + bytes((success,))
                )
    return {
        "sources": n,
        "triple_source": triple,
        "source_words": len(words),
        "phase_cuts": len(words) * (2 * n + 1 + int(triple)),
        "restoring_assignments": sum(histogram.values()),
        "paired_coverage_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "universal_paired": universal,
        "three_read_repairs": repaired,
        "ordered_sha256": digest.hexdigest(),
        "first_positive": first,
    }
