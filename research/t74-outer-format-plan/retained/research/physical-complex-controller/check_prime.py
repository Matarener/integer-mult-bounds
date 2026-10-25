# SPDX-License-Identifier: Apache-2.0
"""Finite selected rational admissibility for the explicit PR2234 Proth prime.

Jose Manuel/Codex: bounded audit. I retain the PR589 projector/geometry
implementation and the PR2234 prime certificate; I do not run their CLIs.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
from production_native import PRIME


def run():
    q = PRIME
    require = cohort.require
    require(q == 213 * (1 << 80) + 1 and 213 < 1 << 80 and
            pow(7, (q - 1) // 2, q) == q - 1 and gcd(7, q) == 1, "Proth prime certificate")
    inputs = cohort.authenticate()
    path = "research/pr589-five-helper-hosting/verify.py"
    old = types.ModuleType("bounded_selected_prime_source")
    old.__file__ = str(cohort.ROOT / path)
    exec(compile(inputs[path], old.__file__, "exec"), old.__dict__)
    w, t, geometry = (old.read(x) for x in (old.WORD, old.HOST, old.GEO))
    denominators = Counter()

    def scan(matrix):
        for row in matrix:
            for entry in row:
                entry = F(entry)
                require(gcd(entry.denominator, q) == 1, "selected rational denominator unit")
                denominators[entry.denominator] += 1

    def eye(n):
        return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))

    def chosen(matrix):
        rows = [[F(x).numerator * pow(F(x).denominator, -1, q) % q for x in row] for row in matrix]
        rank, columns = 0, []
        for j in range(len(rows[0])):
            pivot = next((i for i in range(rank, len(rows)) if rows[i][j]), None)
            if pivot is None:
                continue
            rows[rank], rows[pivot] = rows[pivot], rows[rank]
            inverse = pow(rows[rank][j], -1, q)
            rows[rank] = [x * inverse % q for x in rows[rank]]
            for i in range(len(rows)):
                if i != rank and rows[i][j]:
                    coefficient = rows[i][j]
                    rows[i] = [(x - coefficient * y) % q for x, y in zip(rows[i], rows[rank])]
            columns.append(j)
            rank += 1
            if rank == len(rows):
                break
        return columns

    projectors, dimensions = [], []
    for frame in w["frames"]:
        projector, rank = old.projection([w["lines"][j] for j in frame])
        scan(projector)
        require(len(chosen(projector)) == rank, "selected frame rank modulo prime")
        projectors.append(projector)
        dimensions.append(rank)
    pairs = set()
    for program in t["local_programs"].values():
        for event in program:
            if event[0] in (0, 2):
                a, b, rank = event[2:5] if event[0] == 0 else event[3:6]
                lo, hi = (a, b) if dimensions[a] <= dimensions[b] else (b, a)
                require(dimensions[hi] - dimensions[lo] == rank, "literal selected residual rank")
                pairs.add((lo, hi, rank))
    rank_histogram, base_keys = Counter(), set()
    for lo, hi, rank in sorted(pairs):
        projector = old.sub(projectors[hi], projectors[lo])
        scan(projector)
        require(old.mul(projector, projector) == projector, "exact selected residual projector")
        complement = old.sub(eye(8), projector)
        image, kernel = chosen(projector), chosen(complement)
        require((len(image), len(kernel)) == (rank, 8 - rank), "complementary modular ranks")
        basis = tuple(tuple(projector[i][j] for j in image) +
                      tuple(complement[i][j] for j in kernel) for i in range(8))
        scan(basis)
        require(len(chosen(basis)) == 8, "complete selected split basis")
        require(old.mul(projector, basis) == tuple(
            tuple(basis[i][j] if j < rank else F(0) for j in range(8)) for i in range(8)),
            "exact rational split identity")
        rank_histogram[rank] += 1
        base_keys.add(projector)
    for entry in geometry["ports"]:
        basis = tuple((F(entry["q"][i], 2),) + tuple(map(F, entry["complement_columns"][i])) for i in range(8))
        rho = tuple(tuple(map(F, row)) for row in entry["rho15"])
        scan(basis)
        scan(rho)
        require(old.mul(basis, old.trans(basis)) == eye(8), "rational port orthogonality")
        require(old.mul(rho, old.trans(rho)) == eye(15) and old.mul(rho, rho) == eye(15),
                "rational involutory routing chart")
        require(len(chosen(basis)) == 8 and len(chosen(rho)) == 15, "modular chart invertibility")
    idles = {event["idx"]: event for event in t["schedule"] if event["kind"] == "idle"}
    pending = {i: old.pending_axes(event) for i, event in idles.items()}
    charts, occupied = set(), defaultdict(set)
    for call in t["calls"]:
        for family, route in call["owners"]:
            if route[0] == "data":
                require(route[1] == call["stage"] and 0 <= route[2] < 111, "selected data chart")
                charts.add(("data", route[2], route[1]))
            else:
                require(route[0] == "hosted", "selected helper chart")
                _, child, offset, width = route
                axes = pending[child][offset:offset + width]
                require(width == 8 and len(set(axes)) == 8 and all(0 <= axis < 64 for axis in axes),
                        "complete hosted chart embedding")
                port = family % 111 if min(axes) < 8 else -1
                charts.add(("host", port, tuple(axes)))
    for child, copy, offset, width, stage, helper in t["hosting"]["slots"]:
        axes = pending[child][offset:offset + width]
        require(len(axes) == width and not occupied[child, copy].intersection(axes), "disjoint hosted slots")
        occupied[child, copy].update(axes)
    idle_positive, idle_bases, idle_histogram = 0, set(), Counter()
    for child, axes in pending.items():
        for copy in range(222):
            remainder = tuple(sorted(set(axes) - occupied[child, copy]))
            require(len(set(remainder)) == len(remainder) and all(0 <= axis < 64 for axis in remainder),
                    "idle coordinate split")
            if remainder:
                require(len(remainder) <= 42, "selected idle rank bound")
                idle_positive += 1
                idle_bases.add(remainder)
                idle_histogram[len(remainder)] += 1
                charts.add(("family", copy % 111))
    canonical_local = sum(sum(event[0] in (0, 2) for event in
        t["local_programs"][t["calls"][32 * stage]["orientation"]]) for stage in range(9))
    require(canonical_local + idle_positive == 28278, "complete selected request inventory")
    result = dict(status="PASS_BOUNDED_SELECTED_PRIME_ADMISSIBILITY", q=q,
                  frame_projectors=len(projectors), local_residual_pairs=len(pairs),
                  distinct_local_bases=len(base_keys), local_rank_histogram=dict(sorted(rank_histogram.items())),
                  split_basis_checks=len(pairs), port_bases=len(geometry["ports"]), rho15=len(geometry["ports"]),
                  chart_labels=len(charts), canonical_local_requests=canonical_local,
                  idle_positive_requests=idle_positive, distinct_idle_bases=len(idle_bases),
                  idle_rank_histogram=dict(sorted(idle_histogram.items())), canonical_requests=canonical_local+idle_positive,
                  denominators=sorted(denominators), denominator_occurrences=sum(denominators.values()),
                  scope="Fixed rational admission; no GL64 program construction, generated-unit replay or production payload.")
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["sha256"] = sha256(canonical).hexdigest()
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
