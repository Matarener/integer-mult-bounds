"""Forward-depth census independent of cutoff.py and RESULT.json. Apache-2.0."""

import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def forward(width):
    for d in range(44):
        if width < 64:
            return d
        width = (width // 64) * 42
    raise ValueError("bounded forward contraction")


def exact_digits():
    q = 257501199577916014212415489
    require(pow(7, 213 * 2**79, q) == q - 1, "separate prime order check")
    require(q < (2**80 + 1) ** 2, "separate prime square-root check")
    digits = [[0], [0]]
    coefficient = 9475
    for d in range(1, 23):
        coefficient *= 28416
        for index, factor in enumerate((1, 2)):
            for h in range(1, 16):
                if coefficient <= factor * q**h:
                    break
            else:
                raise ValueError("coefficient digit capacity")
            require(
                coefficient * (q - 1 - d) > factor * q ** (h - 1) * (q - 1),
                "exact lower product bound for this predicate",
            )
            require(coefficient <= factor * q**h, "exact upper product bound")
            digits[index].append(8192 * d + h)
    return digits


def census():
    digits = exact_digits()
    digest = hashlib.sha256()
    fitted = [0, 0]
    last_failure = [0, 0]
    # For 2<=e<2^20 the exact selected atom width is two.
    require(17 * 20 < 10000, "exact common atom ceiling")
    for e in range(1, 2**20):
        w = 1 if e == 1 else 2
        maximum = min((e - 1) // 2, e - 64 * w)
        d = forward((e - maximum) // w) if maximum >= 0 else 0
        decisions = []
        for index in range(2):
            fits = maximum >= 0 and digits[index][d] <= maximum
            if fits:
                fitted[index] += 1
            else:
                last_failure[index] = e
            decisions.append(int(fits))
        digest.update(f"{e},{decisions[0]},{decisions[1]},{d}\n".encode())
    require(last_failure == [245766, 245766], "last failure for each predicate")
    require(fitted == [802809, 802809], "complete fitted counts")
    require(
        digest.hexdigest() == "af7b7197d5977772fdd5a6a8339bf365cf3dbab317d63e8dc75b8791b6cc15f3",
        "complete independent finite decision digest",
    )
    return dict(
        cases=2**20 - 1,
        fitted=fitted,
        last_failure=last_failure,
        predicates=2,
        sha256=digest.hexdigest(),
    )


if __name__ == "__main__":
    print(json.dumps(census(), sort_keys=True))
