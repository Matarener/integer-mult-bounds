"""Decide a complete native endpoint at one width or at all positive widths.

Reuse the pinned parser, exact native paths and dirty-role expansion.
The new decision uses projective phase buckets and the pointwise theorem.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
import compact
import certify as exact
from bounds import decision_widths, pointwise_bound


def projective_buckets(coefficients, paths, inner, width):
    representatives, grouped = [], []
    for j, coefficient in enumerate(coefficients):
        match = next((i for i, k in enumerate(representatives)
                      if exact.norm2(inner[k][j]) == 1), None)
        if match is None:
            representatives.append(j)
            grouped.append(coefficient)
        else:
            phase = inner[representatives[match]][j]
            exact.require(exact.power(phase, 4) == 1, "Dyadic Clifford scalar phase")
            grouped[match] += coefficient*exact.power(phase, width)
    keep = [i for i, value in enumerate(grouped) if value]
    indices = [representatives[i] for i in keep]
    return ([grouped[i] for i in keep], [paths[j] for j in indices],
            [[inner[i][j] for j in indices] for i in indices])


def decide(problem, width=None, *, witness=False):
    n = problem.get("axes")
    exact.require(type(n) is int and n >= 0, "Nonnegative axis count")
    widths = decision_widths(n) if width is None else [width]
    for f in widths:
        exact.require(type(f) is int and f >= (4*n+4 if n else 1),
                      "Width is below the proved pointwise threshold")
    entries = compact.residuals(problem)
    decisions = []
    for f in widths:
        lower = pointwise_bound(n, f, clifford=True)
        exact.require(lower > 0, "Positive theorem bound")
        failures = []
        for output_role, input_role, coefficients, paths, inner in entries:
            coefficients, paths, inner = projective_buckets(coefficients, paths, inner, f)
            if not coefficients:
                continue
            mass = sum(exact.norm2(value) for value in coefficients)
            energy = exact.energy(coefficients, inner, f)
            exact.require(lower*mass <= energy <= (2-lower)*mass, "Pointwise Gram estimate")
            failure = {"output_role": output_role, "input_role": input_role,
                       "projective_terms": len(paths), "coefficient_mass": str(mass),
                       "normalized_squared_norm": str(energy)}
            if witness:
                failure["witness"] = compact.entry_witness(coefficients, paths, inner, f)
            failures.append(failure)
        decisions.append({"width": f, "phase_residue": f % 4,
                          "gram_lower_bound": str(lower), "equal": not failures,
                          "failures": failures})
    digest = hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"schema": "clifford-pointwise/v1", "problem_sha256": digest,
            "axes": n, "scope": "all-positive-widths" if width is None else "specified-width",
            "equal": all(row["equal"] for row in decisions), "decisions": decisions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--witness", action="store_true")
    args = parser.parse_args()
    print(json.dumps(decide(json.loads(args.problem.read_text()), args.width,
                            witness=args.witness), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
