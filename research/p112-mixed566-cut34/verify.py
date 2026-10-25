"""Exact new inequalities for the conditional mixed566 common-cut34 theorem."""

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "6f100d4bb5083f8c35d96fd95a539811c62f245c"
INPUTS = {
    "research/d6-axis-concentration14/PROOF.md":
        "ccff2c13d4ac590646002f198a4d729a6b5f9b48fba17493a63c8fa461f7ba55",
    "research/p112-mixed566-cut32/PROOF.md":
        "fd34597aa7e0e358cf2cb20ac71d597f24dbf7a1b90570f025f8b79950dcd43d",
    "research/p112-mixed566-cut33/PROOF.md":
        "09050050da60676b68454047f13813ea3294a759626ce60bfeed8c24d76e455a",
    "research/p112-root-simplex-exclusion/geometry.py":
        "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021",
}
PLANE_COUNTS = {82: 448, 84: 2688, 85: 448, 86: 168, 88: 28}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_bytes(path):
    require(path.is_file() and not path.is_symlink(), "regular JSON input required")
    require(path.stat().st_size <= 200_000, "JSON input capacity")
    return json.loads(path.read_text(encoding="utf-8"))


def authenticate(root=ROOT, package=HERE):
    manifest = json_bytes(package / "SOURCES.json")
    require(manifest["base_commit"] == BASE, "scientific baseline")
    rows = manifest["files"]
    require(len(rows) == 6, "complete source inventory")
    require(len({row["path"] for row in rows}) == 6, "unique source paths")
    live = {row["path"]: row["sha256"] for row in rows if row["usage"] == "input"}
    require(live == INPUTS, "exact proof and executable input pins")
    data = {}
    for path, digest in INPUTS.items():
        source = root / path
        require(source.is_file() and not source.is_symlink(), "regular source input")
        require(source.stat().st_size <= 200_000, "source input capacity")
        payload = source.read_bytes()
        require(hashlib.sha256(payload).hexdigest() == digest, "source SHA256: " + path)
        data[path] = payload
    return data


def load_geometry(data):
    path = "research/p112-root-simplex-exclusion/geometry.py"
    module = ModuleType("authenticated_geometry")
    # Execute only the authenticated canonical source, without a bytecode import.
    exec(compile(data[path], path, "exec"), module.__dict__)
    return module


def axis_upper(assignment, capacities, live_axis_size):
    require(len(assignment) == len(capacities) == 3, "three-piece axis assignment")
    require(set(assignment) <= {0, 1}, "two axes")
    total = 0
    for axis in range(2):
        group = tuple(i for i in range(3) if assignment[i] == axis)
        upper = min(live_axis_size, sum(capacities[i] for i in group))
        if len(group) == 2 and 0 in group:
            upper = min(upper, 28)  # PR3325 full-axis rank5 + rank6 union bound.
        total += upper
    return total


def d6_case(union, cut):
    require(type(union) is int and union in (82, 84, 85, 86), "permitted D6 union")
    require(type(cut) is int and 0 <= cut <= 35, "bounded common cut")
    retained = union - cut
    singleton = tuple(c - (52 - retained) for c in (12, 20, 20))
    if union == 82:
        require(singleton[1] >= 14 and singleton[2] >= 14, "rank6 concentration")
        capacities = (12, 18, 18)  # Four orthogonal frame punctures per large axis.
        require(retained >= sum(capacities), "equality step needs at least48 sites")
        if retained > sum(capacities):
            return {"required": retained, "preliminary_upper": 48, "contradiction": True}
        # Equality in N <= union of supports <= sum M_i <= 48 forces disjoint
        # supports, all in R, of sizes12/18/18. Thus all12 rank5 sites are singleton.
        require(retained == 48, "capacity equality")
        singleton = capacities
        axis_size = 29
    else:
        capacities, axis_size = (12, 20, 20), 33
    require(singleton[0] > 8 and min(singleton[1:]) > 12, "no small singleton fiber")
    require(singleton[0] >= 10 and min(singleton[1:]) >= 14, "all-piece concentration")
    bounds = tuple(axis_upper(a, capacities, axis_size) for a in product((0, 1), repeat=3))
    require(max(bounds) < retained, "two-axis contradiction")
    return {"required": retained, "preliminary_upper": sum(capacities),
            "singleton_lower_after_refinement": list(singleton),
            "eight_axis_assignment_bounds": list(bounds), "coverage_upper": max(bounds),
            "contradiction": True}


def arithmetic(cut):
    require(type(cut) is int and 0 <= cut <= 35, "bounded common cut")
    e6_lower = 2 * (78 - cut)
    require(e6_lower > 86, "strict E6 incidence gap")
    return {"cut": cut, "E6": {"required_twice": e6_lower, "incidence_upper": 86},
            "D6": {str(u): d6_case(u, cut) for u in (82, 84, 85, 86)}}


def geometry_receipt(g):
    roots, points, _, coordinates = g.root_data()
    gram = tuple(tuple(g.dot(a, b) for b in roots) for a in roots)
    point_ids = tuple(i for i, r in enumerate(roots) if r in points)
    frame_ids = tuple(i for i in range(120) if i not in point_ids)
    counts = {}
    for i, j in combinations(range(120), 2):
        if gram[i][j]:
            continue
        size = sum(bool(gram[i][k] or gram[j][k]) for k in point_ids)
        counts[size] = counts.get(size, 0) + 1
        if size == 82:
            for a, b in ((i, j), (j, i)):
                axis = tuple(k for k in range(120) if gram[a][k] and not gram[b][k])
                punctures = tuple(k for k in axis if k in frame_ids)
                require(len(axis) == 33 and len(punctures) == 4, "four-puncture axis")
                require(all(gram[x][y] == 0 for x, y in combinations(punctures, 2)),
                        "orthogonal frame punctures")
    require(counts == PLANE_COUNTS, "all D6 unions, including the new86 case")
    five = tuple(sum(all(c[i] == 0 for i in omitted) for c in coordinates)
                 for omitted in combinations(range(8), 3))
    six = tuple(sum(all(c[i] == 0 for i in omitted) for c in coordinates)
                for omitted in combinations(range(8), 2))
    require(max(five) == 20, "rank-at-most-five parabolic capacity")
    require({n for n in six if n >= 26} == {30, 36}, "normalization at26 zeros")
    require(max(n for n in six if n < 26) == 21, "other rank-six parabolics")
    roots_digest = hashlib.sha256(json.dumps(roots).encode()).hexdigest()
    return {"full_roots_sha256": roots_digest, "plane_union_counts": counts,
            "minimum_zeros": 26, "rank5_parabolic_max": max(five),
            "large_rank6_parabolics": [30, 36], "other_rank6_max": 21,
            "union82_ordered_axes_checked": 896}


def same_receipt(actual, expected):
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "exact result receipt including JSON types")


def compute():
    data = authenticate()
    return {"status": "PASS_CONDITIONAL_MIXED566_CUT34", "arithmetic": arithmetic(34),
            "geometry": geometry_receipt(load_geometry(data)),
            "inherited_proof_inputs": {p: h for p, h in INPUTS.items() if p.endswith('.md')},
            "scope": "Conditional commoncut34, not sharpness, a caller, a supplier or kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.output is None:
        same_receipt(result, json_bytes(HERE / "RESULT.json"))
    else:
        require(not args.output.resolve().is_relative_to(ROOT), "external output only")
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
