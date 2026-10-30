# SPDX-License-Identifier: Apache-2.0
"""No-import inverse-depth/slab reconstruction of the complete integer census."""

import json
from bisect import bisect_right
from hashlib import sha256
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def slab(e, q, m, r, factor, compatibility, numerator, denominator):
    width = 1
    for candidate in range(1, e + 1):
        if candidate**denominator >= e**numerator:
            width = candidate
            break
    thresholds = [m]
    for _ in range(e):
        if thresholds[-1] > e:
            break
        thresholds.append(m * ((thresholds[-1] + r - 1) // r))
    need(thresholds[-1] > e or e < m, "complete inverse-depth thresholds")
    order = 1
    for position in range(m):
        order *= q**m - q**position
    level = factor * order * q ** (m * m * (width - 1))
    upper = min((e - 1) // 2, e - m * width)
    candidates = []
    for d in range(1, len(thresholds)):
        stock = compatibility * level**d
        power, threshold = 1, 0
        for _ in range(stock.bit_length() + 1):
            if power >= stock:
                break
            power *= q
            threshold += 1
        lower = max(0, e - width * thresholds[d] + 1, threshold)
        high = min(upper, e - width * thresholds[d - 1])
        if lower <= high:
            candidates.append((lower, d, stock))
    if not candidates:
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
    k, d, stock = min(candidates)
    body, remainder = divmod(e - k, width)
    need(bisect_right(thresholds, body) == d, "inverse slab depth")
    return dict(
        width=width,
        depth=d,
        borrowed=k,
        body=body,
        remainder=remainder,
        stock=stock,
        rows=q**k,
        fits=True,
    )


def main():
    result = json.loads((Path(__file__).parent / "RESULT.json").read_text())
    digest, total, fitted, slack = sha256(), 0, 0, 0
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
                    values = (e, q, m, r, factor, compatibility, numerator, denominator)
                    answer = slab(*values)
                    total += 1
                    fitted += answer["fits"]
                    slack += answer["fits"] and answer["rows"] > answer["stock"]
                    digest.update(json.dumps([values, answer], sort_keys=True).encode())
    actual = dict(
        cases=total, fitted=fitted, strict_radix_slack=slack, sha256=digest.hexdigest()
    )
    need(
        json.dumps(actual, sort_keys=True)
        == json.dumps(result["census"], sort_keys=True),
        "separate inverse-slab census agrees",
    )
    count = 0
    for cap in range(1, 33):
        for left in range(1, 65):
            for right in range(1, 65):
                need(
                    min(cap, min(cap, left) * min(cap, right))
                    == min(cap, left * right),
                    "positive saturation multiplication identity",
                )
                count += 1
    print("PASS_INDEPENDENT_SATURATED_SLABS", total, count, digest.hexdigest())


if __name__ == "__main__":
    main()
