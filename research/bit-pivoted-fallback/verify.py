"""Exact bounded corroboration of the new pivoted construction. Apache-2.0."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from math import gcd
from pathlib import Path
from random import Random

from model import compile_plan, execute, eye, inverse, mul, require


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def rank_mod(p, q):
    rows, rank = [list(row) for row in p], 0
    for j in range(len(p)):
        pivots = [i for i in range(rank, len(p)) if rows[i][j] % q]
        if not pivots:
            continue
        i = pivots[0]
        rows[rank], rows[i] = rows[i], rows[rank]
        inv = pow(rows[rank][j], -1, q)
        rows[rank] = [x * inv % q for x in rows[rank]]
        for i in range(rank + 1, len(p)):
            c = rows[i][j]
            rows[i] = [(x - c * y) % q for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def oracle(p, data, f, weights, modulus):
    """Direct B N(P) B^-1, independently of elimination or adapters."""
    m = len(p)
    head = [[data[i * f + j] * pow(weights[i * f + j], -1, modulus)
             % modulus for j in range(f)] for i in range(m)]
    tail = [[data[(2 * m - 1 - i) * f + f - 1 - j] for j in range(f)]
            for i in range(m)]
    out = list(data)
    for i in range(m):
        for j in range(f):
            difference = sum(p[i][k] * (tail[k][j] - head[k][j]) for k in range(m))
            out[i * f + j] = weights[i * f + j] * (head[i][j] + difference) % modulus
            out[(2 * m - 1 - i) * f + f - 1 - j] = (tail[i][j] - difference) % modulus
    return out


def check_case(p, rank, modulus, f, rng, counts, controls):
    plan = compile_plan(p, rank, modulus)
    units = [x for x in range(1, modulus) if gcd(x, modulus) == 1]
    weights = [rng.choice(units) for _ in range(plan.m * f)]
    size = 2 * plan.m * f
    inputs = [[int(i == j) for i in range(size)] for j in range(size)]
    inputs.extend([[rng.randrange(modulus) for _ in range(size)] for _ in range(2)])
    for data in inputs:
        expected = oracle(p, data, f, weights, modulus)
        actual, trace = execute(plan, data, f, weights)
        require(actual == expected, "compiled partial-interchange endpoint")
        returned, _ = execute(plan, actual, f, weights)
        require(returned == data, "arbitrary dirty-state involution")
        multiplier = 1 if f == 1 else 3
        require(len(trace) == 2 * multiplier * plan.pivot_swaps, "exact child tariff")
        counts["basis_and_dirty_vectors"] += 1
        counts["roundtrips"] += 1
    data = inputs[-1]
    controls["omitted_pivot_swaps"] |= execute(plan, data, f, weights, omit_swaps=True)[0] != oracle(p, data, f, weights, modulus)
    controls["omitted_return_adapter"] |= execute(plan, data, f, weights, omit_return=True)[0] != oracle(p, data, f, weights, modulus)
    controls["discarded_ancestor_weights"] |= execute(plan, data, f, [1] * (plan.m * f))[0] != oracle(p, data, f, weights, modulus)
    counts["plans"] += 1
    counts["plans_needing_pivot_swaps"] += plan.pivot_swaps > 0
    counts["small_case_max_pivot_swaps"] = max(counts["small_case_max_pivot_swaps"], plan.pivot_swaps)
    return plan


def exhaustive(rng, counts, controls):
    domains = ((2, 3, 1), (2, 5, 1), (2, 3, 2), (2, 5, 2), (3, 3, 1))
    rows = []
    for m, q, w in domains:
        modulus, found = q ** w, 0
        for flat in product(range(modulus), repeat=m * m):
            p = [list(flat[i * m:(i + 1) * m]) for i in range(m)]
            counts["matrix_candidates"] += 1
            if mul(p, p, modulus) != p:
                continue
            rank = rank_mod(p, q)
            if not 0 < rank < m:
                continue
            check_case(p, rank, modulus, 1, rng, counts, controls)
            found += 1
        rows.append({"m": m, "q": q, "w": w, "projectors": found})
    return rows


def sampled(rng, counts, controls):
    rows = []
    for m, q, w in ((3, 3, 2), (4, 5, 2), (5, 3, 3), (8, 3, 2)):
        modulus, seen = q ** w, 0
        for rank in range(1, m):
            for repetition in range(8):
                g = eye(m)
                for _ in range(3 * m):
                    i, k = rng.sample(range(m), 2)
                    c = rng.randrange(modulus)
                    g[i] = [(x + c * y) % modulus for x, y in zip(g[i], g[k])]
                gi = inverse(g, modulus)
                p = mul([row[:rank] for row in g], gi[:rank], modulus)
                f = 1 + repetition % 5
                plan = check_case(p, rank, modulus, f, rng, counts, controls)
                low = compile_plan([[x % q for x in row] for row in p], rank, q)
                itinerary = [(o.kind, o.target, o.source) for o in plan.adapter]
                low_itinerary = [(o.kind, o.target, o.source) for o in low.adapter]
                require(itinerary == low_itinerary, "high lifts preserve complete itinerary")
                counts["low_high_itinerary_comparisons"] += 1
                seen += 1
        rows.append({"m": m, "q": q, "w": w, "charts": seen, "f": [1, 2, 3, 4, 5]})
    return rows


def boundary_controls(rng, counts, controls):
    p = [[1, 1], [0, 0]]
    for bad_p, rank, modulus in (([[1, 1], [1, 0]], 1, 9),
                                 (p, 2, 9), (p, 1, 8)):
        try:
            compile_plan(bad_p, rank, modulus)
        except ValueError:
            counts["rejected_invalid_inputs"] += 1
        else:
            raise ValueError("invalid projector/rank/ring was accepted")
    try:
        execute(compile_plan(p, 1, 9), [1] * 4, 1, [3, 1])
    except ValueError:
        counts["rejected_invalid_inputs"] += 1
    else:
        raise ValueError("nonunit ancestor weight was accepted")
    # A residue-zero but nonzero full-ring entry must survive coefficient generation.
    p = [[1, 3], [0, 0]]
    plan = check_case(p, 1, 9, 3, rng, counts, controls)
    low = compile_plan([[x % 3 for x in row] for row in p], 1, 9)
    data = [rng.randrange(9) for _ in range(12)]
    controls["low_only_coefficients"] = execute(plan, data, 3, [1] * 6)[0] != execute(low, data, 3, [1] * 6)[0]
    # Literal 64-coordinate fixtures cover all retained paid ranks.
    for rank in (1, 2, 3, 4, 5, 6, 7, 42):
        p = [[int(i == j and i >= 64 - rank) for j in range(64)] for i in range(64)]
        plan = compile_plan(p, rank, 9)
        require(plan.pivot_swaps == 2 * rank, "diagonal fixture attains pivot-swap bound")
        for f in (1, 3):
            data = [rng.randrange(9) for _ in range(128 * f)]
            actual, trace = execute(plan, data, f, [2] * (64 * f))
            require(actual == oracle(p, data, f, [2] * (64 * f), 9), "64-coordinate endpoint")
            require(len(trace) == (4 if f == 1 else 12) * rank, "attained child tariff")
            counts["literal_64_coordinate_fixtures"] += 1
            counts["literal_64_pivot_children"] += len(trace)
    require(all(controls.values()), "every semantic mutation must be detected")


def source_hashes():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    out = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            digest = sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "live source hash: " + row["path"])
            out[row["path"]] = digest
    for path in sorted(PACKAGE.iterdir()):
        if path.is_file():
            out[path.relative_to(ROOT).as_posix()] = sha256(path.read_bytes()).hexdigest()
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    hashes = source_hashes()
    rng, counts = Random(104729), Counter()
    controls = dict.fromkeys(("omitted_pivot_swaps", "omitted_return_adapter",
                              "discarded_ancestor_weights", "low_only_coefficients"), False)
    rows = exhaustive(rng, counts, controls)
    charts = sampled(rng, counts, controls)
    boundary_controls(rng, counts, controls)
    report = {"status": "PASS_BIT_PIVOTED_FALLBACK", "counts": dict(counts),
              "exhaustive_domains": rows, "sampled_charts": charts,
              "controls": controls, "sha256": hashes}
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(ROOT), "receipt must be outside checkout")
        with args.receipt.open("x") as handle:
            handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
