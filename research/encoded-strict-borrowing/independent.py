# SPDX-License-Identifier: Apache-2.0
"""Independent inverse-depth/slab oracle, with no imports of runtime or selector."""

import json
from hashlib import sha256
from pathlib import Path


def slab(values):
    e, q, m, r, factor, compatibility, numerator, denominator = values
    width = 1
    for candidate in range(1, e + 1):
        if candidate**denominator >= e**numerator:
            width = candidate
            break
    # Independent-column GL order, enumerated by remaining codimension.
    gl = 1
    for codimension in range(1, m + 1):
        gl *= q ** (m - codimension) * (q**codimension - 1)
    level = factor * gl * q ** (m * m * (width - 1))
    upper = min((e - 1) // 2, e - m * width)
    boundaries = [0, m]
    for _ in range(e + 1):
        if boundaries[-1] > e // width:
            break
        boundaries.append(m * ((boundaries[-1] + r - 1) // r))
    else:
        raise ValueError("inverse-depth bound")
    winners = []
    for d in range(len(boundaries) - 1):
        stock = compatibility * level**d if d else 1
        threshold, power = 0, 1
        for _ in range(stock.bit_length() + 1):
            if 2 * power > stock:
                break
            threshold += 1
            power *= q
        else:
            raise ValueError("strict-power threshold bound")
        lower = max(0, e - width * boundaries[d + 1] + 1, threshold)
        high = min(upper, e - width * boundaries[d])
        if lower <= high:
            body, remainder = divmod(e - lower, width)
            winners.append(
                dict(
                    width=width,
                    depth=d,
                    borrowed=lower,
                    body=body,
                    remainder=remainder,
                    stock=stock,
                    rows=q**lower,
                    fits=True,
                )
            )
    if winners:
        return min(winners, key=lambda row: row["borrowed"])
    return dict(
        width=width,
        depth=0,
        borrowed=0,
        body=0,
        remainder=0,
        stock=1,
        rows=1,
        fits=False,
    )


def census():
    digest, total, fitted = sha256(), 0, 0
    for m, r, factor, numerator, denominator in (
        (2, 1, 1, 0, 1),
        (3, 1, 1, 0, 1),
        (2, 1, 2, 1, 4),
        (2, 1, 1, 1, 1),
        (3, 2, 1, 0, 1),
    ):
        for q in (2, 3):
            for compatibility in (1, 2, 5):
                for e in range(1, 97):
                    values = (e, q, m, r, factor, compatibility, numerator, denominator)
                    answer = slab(values)
                    digest.update(json.dumps([values, answer], sort_keys=True).encode())
                    total += 1
                    fitted += answer["fits"]
    return dict(cases=total, fitted=fitted, sha256=digest.hexdigest())


if __name__ == "__main__":
    actual = census()
    expected = json.loads((Path(__file__).parent / "RESULT.json").read_text())[
        "integer"
    ]
    if any(actual[key] != expected[key] for key in actual):
        raise ValueError("independent slab receipt mismatch")
    print(
        json.dumps(
            dict(status="PASS_INDEPENDENT_STRICT_SLABS", **actual), sort_keys=True
        )
    )
