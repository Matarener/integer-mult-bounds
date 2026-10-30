"""Independent complete matched two-frame-plane G4 check.

Research by conorholds with OpenAI Codex assistance. Apache-2.0.
E8/P112 geometry lineage remains credited in PR3689's SOURCES.json.
Exact reproduction and its limits are recorded in VERIFY.md.

Domain: 28 unordered frame pairs x 3 complete characteristic-zero support
strata x 2 matched axes x 255 hyperplanes containing the matched frame label.
For every residual support, exact binary rank is eight and no single-site
deletion lowers it. Fundamental binary dependencies certify the latter for
the full domain. Optional direct deletion uses a distinct low-pivot rank
implementation on all distinct minimum-cardinality residuals, or all residuals.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from types import ModuleType


_geometry_path = Path(__file__).resolve().with_name("frame_pair_geometry.py")
_geometry = ModuleType("d3_matched_plane_independent_geometry")
_geometry.__file__ = str(_geometry_path)
exec(compile(_geometry_path.read_bytes(), str(_geometry_path), "exec"), _geometry.__dict__)
model = _geometry.model
require = _geometry.require


def relation_union(vectors):
    """Return rank and the coordinates occurring in fundamental dependencies.

    Store each pivot vector together with its expression in the ORIGINAL
    input coordinates. Reducing a dependent input to zero therefore gives
    a genuine relation, including its own input coordinate. These relations
    form a basis of the relation space: each has its own nonbasis coordinate.
    An input is a coloop precisely when its coordinate is zero in every
    relation. The union of the fundamental relation supports consequently
    covers all inputs exactly when there are no coloops.
    """
    pivots = {}
    covered = 0
    for i, original in enumerate(vectors):
        value = original
        expression = 1 << i
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (value, expression)
                break
            old_value, old_expression = pivots[pivot]
            value ^= old_value
            expression ^= old_expression
        else:
            covered |= expression
    return len(pivots), covered


def rank_by_low_pivot(vectors):
    """Separate rank implementation for direct deletion, using low pivots."""
    pivots = {}
    for original in vectors:
        value = original
        while value:
            pivot = value & -value
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def mask_indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def failure(context, sites, labels, rank, covered):
    absent = [j for j in range(len(sites)) if not (covered >> j) & 1]
    result = {"status": "failure", "counterexample": dict(context),
              "residual_root_indices": sites,
              "residual_labels": [labels[i] for i in sites],
              "binary_rank": rank, "uncovered_relation_coordinates": absent}
    if rank == 8 and absent:
        deleted = absent[0]
        direct = rank_by_low_pivot(labels[root] for j, root in enumerate(sites) if j != deleted)
        require(direct < 8, "fundamental-dependency coloop disagrees with direct deletion")
        result["counterexample"]["unit_root_index"] = sites[deleted]
        result["rank_after_unit_deletion"] = direct
    return result


def checks(source_geometry, direct_deletions="none", direct_limit=4096, mutation=None):
    roots, frame, frame_ids, live_ids, labels, pairings = model(source_geometry)
    if mutation == "omit-live-root":
        # Removing this point really changes the declared two-axis support:
        # the initial pair/stratum has a nonzero pairing there.
        removed = next(i for i in live_ids
                       if pairings[frame_ids[0]][i] + pairings[frame_ids[1]][i])
        live_ids = tuple(i for i in live_ids if i != removed)
    require(len(live_ids) == 112, "incomplete P112 live-root input")
    require(direct_limit >= 0, "negative direct-deletion budget")
    records = 0
    groups = 0
    support_strata = 0
    cardinalities = Counter()
    digest = sha256()
    minimum_size = None
    direct_cases = {}
    for a, b in combinations(range(8), 2):
        for coefficient in (1, -1, 2):
            support = tuple(i for i in live_ids if pairings[frame_ids[a]][i]
                            + coefficient * pairings[frame_ids[b]][i])
            require(len(support) == (76 if coefficient in (-1, 1) else 88),
                    "two-frame characteristic-zero support stratum changed")
            support_strata += 1
            for matched in (a, b):
                matched_label = labels[frame_ids[matched]]
                if (mutation == "matched-live-label" and (a, b, coefficient, matched) == (0, 1, 1, 0)):
                    # A live neighbor lies in W_matched. Thus W_matched becomes
                    # permitted, and its residual is the opposite 32-site
                    # completion of rank seven. This is a genuine G4 failure,
                    # not an assumption that exchanging two frame labels fails.
                    point = next(i for i in live_ids if pairings[frame_ids[matched]][i])
                    matched_label = labels[point]
                hyperplanes = [normal for normal in range(1, 512)
                               if (normal & matched_label).bit_count() % 2 == 0]
                require(len(hyperplanes) == 255, "matched hyperplane domain")
                groups += 1
                for normal in hyperplanes:
                    sites = [i for i in support if (normal & labels[i]).bit_count() % 2]
                    values = [labels[i] for i in sites]
                    rank, covered = relation_union(values)
                    context = {"frame_pair": [a, b], "coefficient": coefficient,
                               "matched_axis": matched, "matched_label": matched_label,
                               "hyperplane_normal": normal}
                    if rank != 8 or covered != (1 << len(sites)) - 1:
                        return failure(context, sites, labels, rank, covered)
                    records += 1
                    cardinalities[len(sites)] += 1
                    digest.update(json.dumps([a, b, coefficient, matched, normal,
                                              len(sites), rank, covered],
                                             separators=(",", ":")).encode())
                    digest.update(b"\n")
                    mask = sum(1 << i for i in sites)
                    if minimum_size is None or len(sites) < minimum_size:
                        minimum_size = len(sites)
                        if direct_deletions == "boundary":
                            direct_cases.clear()
                    if direct_deletions == "all" or (
                            direct_deletions == "boundary" and len(sites) == minimum_size):
                        direct_cases.setdefault(mask, context)
    require(support_strata == 84 and groups == 168 and records == 42840,
            "incomplete matched two-frame-plane domain")
    result = {"status": "pass", "scope": "complete characteristic-zero two-frame G4 geometry",
              "source_geometry_sha256": sha256(source_geometry.read_bytes()).hexdigest(),
              "unordered_frame_pairs": 28, "support_strata": support_strata,
              "matched_axis_groups": groups, "matched_hyperplanes_per_group": 255,
              "residual_checks": records, "rank_eight_checks": records,
              "complete_no_coloop_checks": records,
              "residual_cardinality_histogram": {str(k): v for k, v in sorted(cardinalities.items())},
              "minimum_residual_cardinality": minimum_size,
              "records_sha256": digest.hexdigest(),
              "direct_deletions": {"mode": direct_deletions, "status": "not-requested"}}
    if direct_deletions != "none":
        if len(direct_cases) > direct_limit:
            result["status"] = "verification-gap"
            result["direct_deletions"] = {"mode": direct_deletions, "status": "budget-exhausted",
                                          "distinct_residuals": len(direct_cases),
                                          "limit": direct_limit}
            return result
        deletion_count = 0
        direct_digest = sha256()
        for mask, context in sorted(direct_cases.items()):
            sites = list(mask_indices(mask))
            require(rank_by_low_pivot(labels[i] for i in sites) == 8,
                    "direct residual rank differs from relation-union rank")
            for deleted in sites:
                rank = rank_by_low_pivot(labels[i] for i in sites if i != deleted)
                if rank != 8:
                    return {"status": "failure", "counterexample": context,
                            "residual_root_indices": sites,
                            "unit_root_index": deleted, "rank_after_unit_deletion": rank,
                            "method": "direct low-pivot deletion"}
                deletion_count += 1
                direct_digest.update(f"{mask},{deleted},{rank};".encode())
        result["direct_deletions"] = {"mode": direct_deletions, "status": "pass",
                                      "distinct_residuals": len(direct_cases),
                                      "individual_deletions": deletion_count,
                                      "records_sha256": direct_digest.hexdigest()}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-geometry", type=Path, required=True)
    parser.add_argument("--direct-deletions", choices=("none", "boundary", "all"), default="none")
    parser.add_argument("--direct-limit", type=int, default=4096)
    parser.add_argument("--mutation", choices=("matched-live-label", "omit-live-root"))
    args = parser.parse_args()
    result = checks(args.source_geometry, args.direct_deletions, args.direct_limit, args.mutation)
    print(json.dumps(result, sort_keys=True, indent=2))
    if result["status"] != "pass":
        raise SystemExit(2 if result["status"] == "verification-gap" else 1)


if __name__ == "__main__":
    main()
