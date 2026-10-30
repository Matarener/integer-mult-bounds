"""Independent inverse-depth slab oracle; no primary or receipt imports.

Nick Petalas. Apache-2.0.
"""

import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def thresholds(m, r, maximum):
    result = [0, m]
    for _ in range(2048):
        if result[-1] > maximum:
            return result
        result.append(m * ((result[-1] + r - 1) // r))
    raise ValueError("inverse-depth capacity")


def logarithm(q, value):
    power = 1
    for exponent in range(8193):
        if power >= value:
            return exponent
        power *= q
    raise ValueError("radix-power capacity")


def slab_plan(e, w, m, r, digits):
    boundaries = thresholds(m, r, e // w)
    best = None
    for d in range(1, len(boundaries) - 1):
        candidate = max(digits[d], e - w * boundaries[d + 1] + 1, 0)
        if candidate <= e - w * boundaries[d] and 2 * candidate < e:
            n, remainder = divmod(e - candidate, w)
            plan = [candidate, n, remainder, d, digits[d]]
            if best is None or candidate < best[0]:
                best = plan
    return best


def census():
    profiles = (
        (2, 1, 2, 6, 2),
        (3, 2, 3, 12, 5),
        (4, 3, 2, 1, 1),
        (5, 2, 5, 7, 5),
        (6, 5, 3, 8, 2),
        (7, 3, 5, 11, 1),
        (8, 7, 2, 12, 5),
        (64, 42, 3, 6, 2),
    )
    digest = hashlib.sha256()
    admitted = 0
    for i, (m, r, q, b, compatibility) in enumerate(profiles):
        for e in range(1, 257):
            for w in range(1, 5):
                bounds = thresholds(m, r, e // w)
                digits = [0] + [
                    logarithm(q, compatibility * b**d) for d in range(1, len(bounds) - 1)
                ]
                plan = slab_plan(e, w, m, r, digits)
                admitted += plan is not None
                row = [i, e, w, plan]
                digest.update((json.dumps(row, separators=(",", ":")) + "\n").encode())
    return {"cases": 8192, "admitted": admitted, "sha256": digest.hexdigest()}


def selected(e):
    q, w = 2**127 - 1, 2
    require(1 < e**17 <= 2**10000, "selected ceiling power")
    boundaries = thresholds(64, 42, e // w)
    digits = [0]
    coefficient = 9475
    for d in range(1, len(boundaries) - 1):
        coefficient *= 28416
        h = logarithm(q, coefficient)
        require(
            coefficient * (q - d - 1) > (q - 1) * q ** (h - 1),
            "separate exact group-product enclosure",
        )
        digits.append(8192 * d + h)
    return slab_plan(e, w, 64, 42, digits)


def main():
    result = census()
    require(
        result
        == {
            "cases": 8192,
            "admitted": 7113,
            "sha256": "2e796c10883b9dcc6ba238dc6359f391bae3e3bd1f4e30c7d2c165bfa210d51a",
        },
        "complete independent slab census",
    )
    expected = {
        250000: [122882, 63559, 0, 15, 122882],
        262144: [122882, 69631, 0, 15, 122882],
        524288: [147459, 188414, 1, 18, 147459],
        1048576: [163843, 442366, 1, 20, 163843],
        970370: [159747, 405311, 1, 19, 155651],
    }
    for e, answer in expected.items():
        require(selected(e) == answer, "independent selected slab witness")
    print("PASS_INDEPENDENT_BODY_SLABS " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
