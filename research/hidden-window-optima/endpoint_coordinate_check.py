#!/usr/bin/env python3
"""Independent adversarial review, stdlib only; reads reviewed author code.

Apache-2.0. Substantial OpenAI Codex assistance from separate AI review.
Independent exact enumeration in endpoint/Mobius coordinates. No imports of
author predicates, certificate verifier, or existing verification suite.
All checks are explicit and remain enabled under python -O.
The optimizer is compiled from the exact source bytes recorded in the receipt;
no Python bytecode cache is loaded.
"""

import argparse
import hashlib
import json
import platform
from pathlib import Path


CAP = 512


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def candidates(cap):
    """All strict interior-root residuals via positive roots on y>0.

    x=(1+2y)/(1+y), and (1+y)^2 R(x)=ell*y^2-v*y+k.
    Its two roots are distinct and positive iff k,ell,v>0 and v^2>4*k*ell.
    D=9*k+6*v+4*ell. No a,z vertex or endpoint predicate is imported.
    """
    trials = 0
    buckets = [[] for _ in range(cap + 1)]
    for k in range(1, cap // 9 + 1):
        for ell in range(1, (cap - 9 * k) // 4 + 1):
            for v in range(1, (cap - 9 * k - 4 * ell) // 6 + 1):
                trials += 1
                delta = v * v - 4 * k * ell
                if delta <= 0:
                    continue
                a = k + v + ell
                z = 4 * k + 3 * v + 2 * ell
                c = 4 * k + 2 * v + ell
                D = 9 * k + 6 * v + 4 * ell
                check(a + z + c == D, "budget identity")
                check(z * z - 4 * a * c == delta, "discriminant identity")
                check((a - z + c, -4 * a + 3 * z - 2 * c,
                       4 * a - 2 * z + c) == (k, v, ell), "inverse map")
                buckets[D].append((delta, z * z, [a, z, c], [k, v, ell]))
    return trials, buckets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author-package", type=Path, default=Path(__file__).resolve().parent,
                        help="directory containing the reviewed optimum.py; defaults to this directory")
    author = parser.parse_args().author_package
    captured = {name: (author / name).read_bytes() for name in
                ("PROOF.md", "optimum.py", "verify.py", "README.md", "SOURCES.json")}
    namespace = {"__name__": "reviewed_optimum", "__file__": str(author / "optimum.py")}
    exec(compile(captured["optimum.py"], str(author / "optimum.py"), "exec",
                 dont_inherit=True), namespace)
    solve_normalized = namespace["solve_normalized"]
    trials, buckets = candidates(CAP)
    num = den = None
    winners = []
    eligible = 0
    budgets_with_ties = 0
    selected = {}
    for L, rows in enumerate(buckets):
        eligible += len(rows)
        for d, zz, row, coordinates in rows:
            if num is None or d * den < num * zz:
                num, den, winners = d, zz, [row]
            elif d * den == num * zz:
                winners.append(row)
        result = solve_normalized(L)
        if not winners:
            check(result["status"] == "infeasible" and result["residuals"] == [],
                  "feasibility mismatch at L=" + str(L))
        else:
            score = result["score"]
            check(result["status"] == "optimal", "status mismatch at L=" + str(L))
            check(score[0] * den == num * score[1], "score mismatch at L=" + str(L))
            check(result["residuals"] == sorted(winners), "complete winners mismatch at L=" + str(L))
            budgets_with_ties += len(winners) > 1
        if L in (30, 31, 34, 35, 39, 40, 62, 63, 98, 99, 142, 143, 144, 333, 512):
            selected[L] = result
    small = [row for rows in buckets[:35] for _, _, row, _ in rows]
    check(small == [[5, 15, 11]], "small-budget exception mismatch")
    # Deliberately excluded endpoints and coincident roots, expressed without
    # using the author's a,z predicates. Each vanishing condition removes a
    # required positive finite y root or makes the two roots coincide.
    excluded = {"x=1": [0, 3, 1], "x=2": [1, 3, 0],
                "repeated root": [1, 2, 1], "negative y roots": [1, -3, 1]}
    for label, (k, v, ell) in excluded.items():
        check(not (k > 0 and ell > 0 and v > 0 and v * v > 4 * k * ell), label)
    report = {
        "marker": "PASS_ENDPOINT_COORDINATE_ATTACK",
        "python": platform.python_version(), "max_L": CAP,
        "budgets_compared": CAP + 1, "positive_coordinate_triples": trials,
        "eligible_residuals": eligible, "budgets_with_multiple_optima": budgets_with_ties,
        "small_budget_residuals": small, "excluded_boundary_controls": excluded,
        "selected_budget_results": selected,
        "counterexamples": [],
        "scope": "Bounded exact corroboration with alternate coordinates; not formal proof verification.",
        "input_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in captured.items()},
        "source_loading": "compile captured optimum.py bytes with dont_inherit=True; no bytecode cache",
        "review_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
