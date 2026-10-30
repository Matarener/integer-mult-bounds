"""Explicit unsigned connector walks from binary covering walks.

The interface, prefix criterion, block composition and depth-one pair are
Nick Petalas's PR4248/6035, following Ross Richardson's connector lineage.
The upward/downward Gray-walk construction is new in this package.
Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter


def require(condition, message):
    if not condition:
        raise ValueError(message)


def covering_block(k, c, states):
    """Return a source word and explicit two-prefix witnesses for every mask.

    ``states`` is a zero-start covering walk in the k-dimensional binary
    cube. Each step flips one bit; repeats are allowed. The characteristic
    must be at least the largest total flip count of a coordinate.
    Readout keys include zero, whose witness is the empty tuple.
    """
    require(type(k) is int and k >= 1, "positive integer source count required")
    require(type(c) is int and c >= 2, "characteristic must be an integer >= 2")
    states = iter(states)
    old = next(states, None)
    require(type(old) is int and old == 0, "covering walk must start at zero")
    up, down = [], []
    first = {0: (0, 0)}
    for new in states:
        require(type(new) is int and 0 <= new < 1 << k, "mask outside cube")
        difference = old ^ new
        require(difference != 0 and difference & (difference - 1) == 0,
                "each covering-walk step must flip exactly one bit")
        bit = difference.bit_length() - 1
        (up if new & difference else down).append(bit)
        first.setdefault(new, (len(up), len(down)))
        old = new
    require(len(first) == 1 << k, "covering walk does not visit every mask")
    flips = Counter(up + down)
    require(all(flips[j] <= c for j in range(k)),
            "characteristic smaller than a coordinate's flip count")
    middle = [j for j in range(k) for _ in range(c - flips[j])]
    word = up + middle + down[::-1]
    # The reversed downward suffix has exactly d original downward events
    # still to run at boundary kc-d. Its count vector is c*1-D(t).
    readouts = {mask: (u, k * c - d) for mask, (u, d) in first.items()}
    readouts[0] = ()
    return word, readouts


def gray_block(k, c):
    """A depth-at-most-two block for c >= 2**(k-1), c >= 2.

    Reflected Gray transition i flips bit v_2(i), so bit j changes exactly
    2**(k-1-j) times. The returned witnesses are chronological boundaries.
    """
    require(type(k) is int and k >= 1, "positive integer source count required")
    require(type(c) is int and c >= max(2, 1 << (k - 1)),
            "Gray block requires c >= max(2, 2**(k-1))")
    return covering_block(k, c, (i ^ (i >> 1) for i in range(1 << k)))


def pair_block(c):
    """PR4248's two-source depth-one word and prefix witnesses."""
    require(type(c) is int and c >= 2, "characteristic must be an integer >= 2")
    return [0, 1] + [0] * (c - 1) + [1] * (c - 1), {
        0: (), 1: (1,), 2: (c + 1,), 3: (2,)}


def compose_blocks(c, blocks):
    """Concatenate certified disjoint blocks and pad every output to c reads.

    Each block is ``(width, word, readouts)`` with local labels 0..width-1,
    all mask keys including zero, and boundary tuples. The caller must check
    each block's prefix identity; this routine validates shape, counts and
    the sufficient sum-of-depths budget. Its output has nonzero mask keys.
    """
    require(type(c) is int and c >= 2, "characteristic must be an integer >= 2")
    blocks = list(blocks)
    require(bool(blocks), "at least one block required")
    word, shifted, width, depth = [], [], 0, 0
    for k, path, hits in blocks:
        require(type(k) is int and k >= 1, "positive block width required")
        require(all(type(j) is int and 0 <= j < k for j in path),
                "source label outside block")
        require(Counter(path) == {j: c for j in range(k)},
                "each block source must occur exactly c times")
        require(set(hits) == set(range(1 << k)), "block mask coverage is incomplete")
        require(hits[0] == (), "zero block mask must use no readouts")
        for times in hits.values():
            require(all(type(t) is int and 0 <= t <= len(path) for t in times),
                    "readout boundary outside source word")
            require(tuple(sorted(times)) == tuple(times), "readouts must be chronological")
        depth += max(map(len, hits.values()))
        shifted.append((k, width, len(word), hits))
        word.extend(width + j for j in path)
        width += k
    require(depth <= c, "sum of block depths exceeds the c-readout budget")
    readouts = {}
    for mask in range(1, 1 << width):
        times = []
        for k, shift, offset, hits in shifted:
            local_mask = (mask >> shift) & ((1 << k) - 1)
            times.extend(offset + t for t in hits[local_mask])
        times.extend([0] * (c - len(times)))
        readouts[mask] = tuple(sorted(times))
    return word, readouts


def literal_calls(word, readouts):
    """Yield ('B', source) and ('A', mask) calls in chronological order."""
    at = {}
    for mask, times in readouts.items():
        for time in times:
            require(type(time) is int and 0 <= time <= len(word),
                    "readout boundary outside source word")
            at.setdefault(time, []).append(mask)
    for time in range(len(word) + 1):
        for mask in sorted(at.get(time, [])):
            yield "A", mask
        if time < len(word):
            yield "B", word[time]


def source_bound(c):
    """The theorem's attainable global source count, without building its word."""
    require(type(c) is int and c >= 2, "characteristic must be an integer >= 2")
    return c.bit_length() * (c // 2) + 2 * (c % 2)
