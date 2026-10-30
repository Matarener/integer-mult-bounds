"""Independent dot-product and regular-action census. Imports no primary algebra.

Quaternion basis order is 1,i,j,k,-1,-i,-j,-k. Apache-2.0.
"""

import hashlib
import json

LEFT_I = (1, 4, 3, 6, 5, 0, 7, 2)
LEFT_J = (2, 7, 4, 1, 6, 3, 0, 5)


def mul(a, b):
    n = len(a)
    columns = [sum(((b[r] >> c) & 1) << r for r in range(n)) for c in range(n)]
    return tuple(sum(((row & col).bit_count() % 2) << c
                     for c, col in enumerate(columns)) for row in a)


def dimension(rows):
    span = {0}
    for row in rows:
        span |= {x ^ row for x in span}
    return len(span).bit_length() - 1


def decode(code, n):
    """An integer counter covers the off-diagonal entries in row-major order."""
    a = [0] * n
    for r in range(n - 1, -1, -1):
        word = code & ((1 << (n - 1)) - 1)
        code >>= n - 1
        a[r] = 1 << r
        k = 0
        for c in range(n):
            if c != r:
                a[r] |= ((word >> k) & 1) << c
                k += 1
    return tuple(a)


def projections(a, mask, si, sj):
    n = len(a)
    li = tuple(row & mask for row in a)
    lj = tuple(row & (((1 << n) - 1) ^ mask) for row in a)
    zi, zj = mul(li, a), mul(lj, a)
    if dimension(zi) != si or dimension(zj) != sj:
        return None
    if mul(li, zi) != zi or mul(lj, zj) != zj:
        return None
    if any(mul(li, zj)) or any(mul(lj, zi)):
        return None
    return zi, zj


def action(a, mask):
    n = len(a)
    state = [[(a[r] >> c) & 1 for c in range(n)] for r in range(n)]
    for call in range(n):
        permutation = LEFT_I if mask >> call & 1 else LEFT_J
        delta = [packet ^ sum(((packet >> h) & 1) << permutation[h]
                              for h in range(8)) for packet in state[call]]
        for r in range(n):
            if a[r] >> call & 1:
                state[r] = [x ^ y for x, y in zip(state[r], delta, strict=True)]
    return tuple(tuple(sum(((state[r][c] >> h) & 1) << c for c in range(n))
                       for r in range(n)) for h in range(8))


def wanted(a, zi, zj):
    n = len(a)
    result = [(0,) * n for _ in range(8)]
    result[0] = tuple(a[r] ^ zi[r] ^ zj[r] for r in range(n))
    result[5], result[6] = zi, zj
    return tuple(result)


def census(n):
    if n not in (3, 5):
        raise ValueError("oracle census supports three or five calls")
    shapes = ((3, 0), (2, 1))
    recs = {str(s): {"first_order": 0, "accepted": 0} for s in shapes}
    streams = {s: hashlib.sha256() for s in shapes}
    spectral = 0
    for code in range(1 << (n * (n - 1))):
        a = decode(code, n)
        square = mul(a, a)
        if mul(square, a) != square or dimension(square) != 3:
            continue
        spectral += 1
        for mask in range(1 << n):
            for shape in shapes:
                pair = projections(a, mask, *shape)
                if pair is None:
                    continue
                rec = recs[str(shape)]
                rec["first_order"] += 1
                actual = action(a, mask)
                accepted = actual == wanted(a, *pair)
                rec["accepted"] += int(accepted)
                packet = [list(a), mask, [list(part) for part in actual], accepted]
                streams[shape].update(json.dumps(packet, separators=(",", ":")).encode() + b"\n")
    for shape in shapes:
        recs[str(shape)]["stream_sha256"] = streams[shape].hexdigest()
    return {"calls": n, "diagonal_one_matrices": 1 << (n * (n - 1)),
            "rank_three_spectral_matrices": spectral, "shapes": recs}
