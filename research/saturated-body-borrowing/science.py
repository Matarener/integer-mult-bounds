# SPDX-License-Identifier: Apache-2.0
"""Independent bounded host-integer specifications; no selector imports."""

import json
from hashlib import sha256


def depth(n, m, r):
    result = 0
    for _ in range(n + 1):
        if n < m:
            return result
        n = r * (n // m)
        result += 1
    raise ValueError("noncontracting oracle profile")


def oracle(e, q, m, r, factor, compatibility, numerator, denominator):
    width = next(w for w in range(1, e + 1) if w**denominator >= e**numerator)
    order = 1
    for i in range(m):
        order *= q**m - q**i
    level = factor * order * q ** (m * m * (width - 1))
    initial_depth = depth(e // width, m, r)
    initial_stock = compatibility * level**initial_depth if initial_depth else 1
    upper = min((e - 1) // 2, e - m * width)
    for k in range(max(0, upper + 1)):
        body, remainder = divmod(e - k, width)
        d = depth(body, m, r)
        stock = compatibility * level**d if d else 1
        rows = q**k
        if rows >= stock:
            if rows >= q * initial_stock:
                raise ValueError("least-plan final-size bound")
            return dict(
                width=width,
                depth=d,
                borrowed=k,
                body=body,
                remainder=remainder,
                stock=stock,
                rows=rows,
                fits=True,
            )
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


def cases():
    profiles = (
        (2, 1, 1, 0, 1),
        (3, 1, 1, 0, 1),
        (2, 1, 2, 1, 4),
        (2, 1, 1, 1, 1),
        (3, 2, 1, 0, 1),
    )
    for m, r, factor, numerator, denominator in profiles:
        for q in (2, 3):
            for compatibility in (1, 2, 5):
                for e in range(1, 65):
                    yield e, q, m, r, factor, compatibility, numerator, denominator


def census():
    digest = sha256()
    total, fitted, slack = 0, 0, 0
    for values in cases():
        answer = oracle(*values)
        total += 1
        fitted += answer["fits"]
        slack += answer["fits"] and answer["rows"] > answer["stock"]
        digest.update(json.dumps([values, answer], sort_keys=True).encode())
    return dict(
        cases=total, fitted=fitted, strict_radix_slack=slack, sha256=digest.hexdigest()
    )
