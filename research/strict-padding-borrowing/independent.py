"""Direct stock/padding enumeration; imports no primary code or receipt."""

import json
from hashlib import sha256


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def height(n, m, rank):
    for d in range(4097):
        if n < m:
            return d
        n = (n // m) * rank
    raise ValueError("independent height capacity")


def brute(q, m, w, b, compatibility, e, cover):
    for k in range((e - 1) // 2 + 1):
        n, ell = divmod(e - k, w)
        if n < m:
            continue
        d = height(n, m, m - 1)
        stock = compatibility * b**d if d else 1
        rows = q**k
        padded = -(-rows // stock) * stock
        if (rows >= stock) if cover else (padded < 2 * rows):
            return k, n, ell, d
    return None


def main():
    digest = sha256()
    cases = admitted = improved = newly = 0
    for q in (2, 3):
        for m in (2, 3):
            for w in (1, 2):
                for b in (1, 6):
                    for compatibility in (1, 2):
                        for e in range(1, 257):
                            new = brute(q, m, w, b, compatibility, e, False)
                            old = brute(q, m, w, b, compatibility, e, True)
                            admitted += int(new is not None)
                            improved += int(
                                new is not None and old is not None and new[0] < old[0]
                            )
                            newly += int(new is not None and old is None)
                            row = [q, m, w, b, compatibility, e, new, old]
                            digest.update(
                                json.dumps(row, separators=(",", ":")).encode() + b"\n"
                            )
                            cases += 1
    ensure(
        (cases, admitted, improved, newly) == (8192, 8030, 3058, 32),
        "independent finite classifications",
    )
    ensure(
        digest.hexdigest()
        == "105ddb1e28467f0c83fddffc7e70cf659fe0a011c43aaefedc369f346a01b984",
        "independent complete case decisions",
    )
    print(
        json.dumps(
            {
                "cases": cases,
                "admitted": admitted,
                "improved": improved,
                "newly_fitted": newly,
                "sha256": digest.hexdigest(),
            },
            sort_keys=True,
        )
    )
    selected()


def selected():
    threshold = 64
    for _ in range(84):
        quotient, remainder = divmod(threshold, 42)
        threshold = 64 * (quotient + int(remainder != 0))
    q = 2**127 - 1
    coefficient = 9475 * pow(28416, 85)
    ensure(
        height(threshold, 64, 42) == 85 and height(threshold - 1, 64, 42) == 84,
        "independent forward threshold endpoints",
    )
    ensure(coefficient * (q - 86) > q**10 * (q - 1), "covering digit fails")
    ensure(coefficient < 2 * q**10, "strict digit succeeds")
    ensure(coefficient * (q - 86) > 2 * q**9 * (q - 1), "previous strict digit fails")
    k = 4096 * 2 * 85 + 10
    e = 2 * threshold + k
    ensure((e - k) // 2 == (e - k + 1) // 2 == threshold, "two prior bodies")
    ensure((e - k - 1) // 2 == threshold - 1, "covering successor body")
    ensure(e**17 <= 2**10000 and 2 * k < e, "existing width and strict fit")
    print(
        json.dumps(
            {"e": e, "threshold": threshold, "strict_k": k, "covering_k": k + 1},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
