# SPDX-License-Identifier: Apache-2.0
"""Direct exhaustive integer specification; never imported by the selector."""

import json
from hashlib import sha256


def depth(n, m, r):
    for result in range(n + 1):
        if n < m:
            return result
        n = r * (n // m)
    raise ValueError("noncontracting oracle profile")


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
                for e in range(1, 97):
                    yield e, q, m, r, factor, compatibility, numerator, denominator


def oracle(e, q, m, r, factor, compatibility, numerator, denominator, covering=False):
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
        accepted = rows >= stock if covering else 2 * rows > stock
        if accepted:
            if not covering and 2 * rows > q * initial_stock:
                raise ValueError("final strict-power bound")
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


def census():
    digest = sha256()
    total = fitted = gains = new_fits = 0
    examples = {}
    for values in cases():
        answer = oracle(*values)
        old = oracle(*values, covering=True)
        fitted += answer["fits"]
        gain = answer["fits"] and old["fits"] and answer["borrowed"] < old["borrowed"]
        new_fit = answer["fits"] and not old["fits"]
        gains += gain
        new_fits += new_fit
        if gain and "saved_digit" not in examples:
            examples["saved_digit"] = dict(inputs=values, strict=answer, covering=old)
        if new_fit and "new_fit" not in examples:
            examples["new_fit"] = dict(inputs=values, strict=answer, covering=old)
        if old["fits"] and (
            not answer["fits"] or not 0 <= old["borrowed"] - answer["borrowed"] <= 1
        ):
            raise ValueError("one-digit comparison theorem")
        digest.update(json.dumps([values, answer], sort_keys=True).encode())
        total += 1
    return dict(
        cases=total,
        fitted=fitted,
        saved_digit=gains,
        newly_fitted=new_fits,
        sha256=digest.hexdigest(),
        examples=examples,
    )
