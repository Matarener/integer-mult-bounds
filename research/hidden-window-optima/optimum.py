#!/usr/bin/env python3
"""Exact hidden-window optimum under the hypotheses in PROOF.md.

Private draft, substantial OpenAI Codex assistance, Apache-2.0.
No external imports, network, subprocesses, or file writes.
The uniform theorem has no size cap; this reference API deliberately does.
"""

import argparse
import json
from math import isqrt

MAX_L = 100_000
MAX_H = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_int(value, low, high, name):
    require(type(value) is int, name + " must be an integer, not bool")
    require(low <= value <= high, name + " outside reference implementation range")
    return value


def residuals_from_squares(L, z):
    """All discriminant-one residuals at fixed odd trace, via k=R(1)."""
    found = []
    for k in range(1, L - 2 * z + 1):
        U = 2 * z * k + k * k + 1
        u = isqrt(U)
        if u * u != U or (z + k - u) % 2:
            continue
        a = (z + k - u) // 2
        c = (z + k + u) // 2
        if a > 0 and c > 0 and 2 * a < z - 1 and z + 1 < 4 * a:
            found.append([a, z, c])
    return sorted(found)


def solve_normalized(L):
    """Return all optimum residuals and a replayable search certificate."""
    checked_int(L, 0, MAX_L, "L")
    common = {"schema": 1, "normalized_budget": L}
    if L < 31:
        return dict(common, status="infeasible", residuals=[])
    if L < 35:
        return dict(common, status="optimal", discriminant=5, z_star=15,
                    residuals=[[5, 15, 11]], score=[1, 45],
                    seed_trace=None, excluded_odd_traces=[])
    n = isqrt((L + 1) // 4)
    z0 = 2 * n * n - 1
    Z = (L - 1) // 2
    top = Z if Z % 2 else Z - 1
    excluded = []
    for z in range(top, z0 - 1, -2):
        found = residuals_from_squares(L, z)
        if found:
            return dict(common, status="optimal", discriminant=1, z_star=z,
                        residuals=found, score=[1, z * z], seed_trace=z0,
                        excluded_odd_traces=excluded)
        excluded.append(z)
    raise ArithmeticError("proved seed was not found")


def solve_budget(h, N):
    checked_int(h, 1, MAX_H, "h")
    S = 6 ** h // 2
    checked_int(N, 1, S * (MAX_L + 1) - 1, "N")
    cert = solve_normalized(N // S)
    return {"h": h, "per_profile_budget": N, "normalization": S,
            "normalized_certificate": cert,
            "residual_counts": [S * sum(row) for row in cert["residuals"]]}


def divisor_residuals(L, z):
    """Separate certificate check using divisors of t(t+1), not square tests."""
    t = (z - 1) // 2
    product = t * (t + 1)
    found = []
    for a in range((t + 1) // 2 + 1, t):
        c, rem = divmod(product, a)
        if rem == 0 and a + z + c <= L:
            found.append([a, z, c])
    return found


def verify_certificate(cert):
    """Recompute all exclusions and all winners with the divisor oracle.

    This verifies the finite certificate given the uniform proof in PROOF.md.
    It is not a proof-kernel implementation of that proof.
    """
    require(type(cert) is dict, "certificate must be a dictionary")
    require(type(cert.get("schema")) is int and cert["schema"] == 1, "schema")
    L = checked_int(cert.get("normalized_budget"), 0, MAX_L, "L")
    if L < 31:
        expected = {"schema": 1, "normalized_budget": L,
                    "status": "infeasible", "residuals": []}
    elif L < 35:
        expected = {"schema": 1, "normalized_budget": L, "status": "optimal",
                    "discriminant": 5, "z_star": 15, "residuals": [[5, 15, 11]],
                    "score": [1, 45], "seed_trace": None, "excluded_odd_traces": []}
    else:
        z = checked_int(cert.get("z_star"), 1, (L - 1) // 2, "z_star")
        require(z % 2 == 1, "trace must be odd")
        n = isqrt((L + 1) // 4)
        z0 = 2 * n * n - 1
        require(z >= z0, "trace worse than available seed")
        excluded = list(range(((L - 1) // 2 - 1) // 2 * 2 + 1, z, -2))
        for higher in excluded:
            require(not divisor_residuals(L, higher), "a better residual exists")
        winners = divisor_residuals(L, z)
        require(bool(winners), "claimed trace has no eligible residual")
        expected = {"schema": 1, "normalized_budget": L, "status": "optimal",
                    "discriminant": 1, "z_star": z, "residuals": winners,
                    "score": [1, z * z], "seed_trace": z0,
                    "excluded_odd_traces": excluded}
    # Canonical JSON comparison also distinguishes bool from integers.
    require(json.dumps(cert, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "certificate fields or complete residual list disagree")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--normalized-budget", type=int)
    group.add_argument("--budget", type=int, help="per-profile budget N")
    parser.add_argument("--h", type=int, default=1)
    args = parser.parse_args()
    if args.normalized_budget is not None:
        result = solve_normalized(args.normalized_budget)
        verify_certificate(result)
    else:
        result = solve_budget(args.h, args.budget)
        verify_certificate(result["normalized_certificate"])
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
