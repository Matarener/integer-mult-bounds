#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fit-level residual local-opt C5 charging fails on the diagonal identity."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/c5-dyadic-decoder-gate/inputs/"
USAGES = {
    "certificates/selected-result.json": "provenance",
    "docs/research/agent-task-catalog.json": "provenance",
    PREFIX + "DATA-PHASES.json.gz": "input",
    PREFIX + "MATCHING.json": "input",
}
PASS_LINE = (
    "PASS_C5_FIT_LEVEL_RESIDUAL_CHARGE "
    "cycles=23 local_floor_sum=460 diagonal_cost=224 inequality_holds=false"
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sources(root: Path = ROOT, inventory: Path | None = None) -> dict[str, bytes]:
    path = HERE / "SOURCES.json" if inventory is None else inventory
    need(path.stat().st_size <= 32_000, "bounded manifest")
    doc = json.loads(path.read_bytes())
    need(set(doc) == {"schema_version", "base_commit", "files"}, "manifest schema")
    need(doc["schema_version"] == 1, "manifest version")
    need(doc["base_commit"] == "463113d675af7410ac91d53a4fed51ec6494eb9a", "base")
    rows = doc["files"]
    need(isinstance(rows, list) and len(rows) == 4, "four source rows")
    need(
        all(
            isinstance(r, dict) and set(r) == {"path", "usage", "git_blob", "sha256"}
            for r in rows
        ),
        "source row schema",
    )
    need(len({r["path"] for r in rows}) == 4, "unique source paths")
    need({r["path"]: r["usage"] for r in rows} == USAGES, "fixed paths/usages")
    payloads: dict[str, bytes] = {}
    for row in rows:
        if row["usage"] == "provenance":
            continue
        src = root / row["path"]
        need(src.is_file() and not src.is_symlink(), "regular source")
        need(src.resolve().is_relative_to(root.resolve()), "source inside root")
        need(src.stat().st_size <= 2_000_000, "bounded input")
        raw = src.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        need(blob == row["git_blob"], "source Git blob")
        payloads[src.name] = raw
    return payloads


def geometry(root: Path = ROOT, inventory: Path | None = None):
    raw = sources(root, inventory)
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        data = stream.read(2_000_001)
    need(len(data) <= 2_000_000, "bounded decompression")
    rows = json.loads(data)["recipes"]
    need(isinstance(rows, list) and len(rows) == 112, "112 scalar labels")
    need(
        all(
            isinstance(r, dict)
            and type(r.get("port")) is int
            and type(r.get("q")) is int
            for r in rows
        ),
        "label row schema",
    )
    labels = {r["port"]: r["q"] for r in rows}
    need(sorted(labels) == list(range(112)), "unique ports")
    need(
        len(set(labels.values())) == 112 and all(0 < q < 512 for q in labels.values()),
        "distinct nine-bit labels",
    )
    matching = json.loads(raw["MATCHING.json"])["matching"]
    need(isinstance(matching, list) and len(matching) == 56, "56 planes")
    need(
        all(
            isinstance(pair, list)
            and len(pair) == 2
            and all(type(p) is int for p in pair)
            for pair in matching
        ),
        "pair schema",
    )
    need(
        sorted(p for pair in matching for p in pair) == list(range(112)), "partition"
    )
    planes = tuple(tuple(labels[p] for p in pair) for pair in matching)
    need(
        all([[dot(x, y) for y in e] for x in e] == [[1, 0], [0, 1]] for e in planes),
        "nondegenerate complete planes",
    )
    return planes, matching


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() % 2


def pairing_rank(left, right) -> int:
    need(len(left) <= 112 and len(right) <= 112, "rank dimensions")
    pivots = [0] * len(right)
    for label in left:
        row = sum(dot(label, other) << j for j, other in enumerate(right))
        for j in range(len(right) - 1, -1, -1):
            if row >> j & 1:
                if pivots[j]:
                    row ^= pivots[j]
                else:
                    pivots[j] = row
                    break
    rank = sum(bool(p) for p in pivots)
    need(rank <= 9, "ambient rank bound")
    return rank


def cycles(planes):
    adj = [
        {j for j in range(56) if i != j and pairing_rank(planes[i], planes[j]) == 0}
        for i in range(56)
    ]
    found = set()
    for a in range(56):
        for b in adj[a]:
            for c in adj[b] - adj[a] - {a}:
                for d in adj[c] - adj[a] - adj[b] - {a, b}:
                    for e in (adj[d] & adj[a]) - adj[b] - adj[c] - {b, c}:
                        if a == min(a, b, c, d, e) and b < e:
                            found.add((a, b, c, d, e))
    need(len(found) == 23, "23 induced physical C5s")
    return tuple(sorted(found))


def diagonal_fit_cost(planes, matching) -> dict:
    """I = sum_i e_i e_i^T; each term touches one complete plane twice."""
    need(len(matching) == 56 and len(planes) == 56, "plane inventory")
    port_to_plane = {}
    for plane_index, pair in enumerate(matching):
        for port in pair:
            port_to_plane[port] = plane_index
    need(sorted(port_to_plane) == list(range(112)), "every port mapped")
    term_costs = []
    matrix = [[0] * 112 for _ in range(112)]
    for port in range(112):
        plane = planes[port_to_plane[port]]
        cost = pairing_rank(plane, plane)
        need(cost == 2, "single-plane self-pairing is I2")
        term_costs.append(cost)
        matrix[port][port] += 1
    need(
        all(matrix[i][j] == int(i == j) for i in range(112) for j in range(112)),
        "diagonal terms sum to identity",
    )
    total = sum(term_costs)
    need(total == 224 and len(term_costs) == 112, "exact diagonal tariff")
    return {
        "terms": 112,
        "per_term_tariff": 2,
        "total_cost": total,
        "formula": "I = sum_i e_i e_i^T",
    }


def identity_extension_term_count(n: int = 112) -> int:
    """I = J - sum_{i != j} e_i e_j^T retains J; used only as a non-discriminating test."""
    need(type(n) is int and 2 <= n <= 112, "bounded extension dimension")
    matrix = [[1] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] -= 1
    need(
        all(matrix[i][j] == int(i == j) for i in range(n) for j in range(n)),
        "complete strict identity extension",
    )
    return 1 + n * (n - 1)


def signed_gram_extension_term_count(n: int = 112) -> int:
    """I = J - sum_{i<j}(e_i+e_j)(e_i+e_j)^T + (n-1) sum_i e_i e_i^T."""
    need(type(n) is int and 2 <= n <= 112, "bounded extension dimension")
    matrix = [[0] * n for _ in range(n)]
    # +J
    for i in range(n):
        for j in range(n):
            matrix[i][j] += 1
    # - sum_{i<j} (e_i+e_j)(e_i+e_j)^T
    for i in range(n):
        for j in range(i + 1, n):
            for a in (i, j):
                for b in (i, j):
                    matrix[a][b] -= 1
    # + (n-1) sum_i e_i e_i^T
    for i in range(n):
        matrix[i][i] += n - 1
    need(
        all(matrix[i][j] == int(i == j) for i in range(n) for j in range(n)),
        "signed Gram identity extension",
    )
    return 1 + (n * (n - 1)) // 2 + n


def build() -> dict:
    planes, matching = geometry()
    cycle_rows = []
    for cycle in cycles(planes):
        local = tuple(q for i in cycle for q in planes[i])
        cycle_rows.append(
            {"cycle": list(cycle), "full_support_rank": pairing_rank(local, local)}
        )
    ranks = [row["full_support_rank"] for row in cycle_rows]
    global_rank = pairing_rank(
        tuple(q for plane in planes for q in plane),
        tuple(q for plane in planes for q in plane),
    )
    need(global_rank == 9 and Counter(ranks) == {7: 4, 8: 6, 9: 13}, "rank receipt")

    granted_floor = 20
    cycle_count = 23
    local_floor_sum = granted_floor * cycle_count
    diagonal = diagonal_fit_cost(planes, matching)
    upper = diagonal["total_cost"]
    inequality_holds = local_floor_sum <= upper
    need(local_floor_sum == 460 and upper == 224, "exact obstruction arithmetic")
    need(not inequality_holds, "uniform residual-local-opt inequality must fail")

    # Necessary weight-sum ceiling for the candidate on K=I under the diagonal upper bound.
    max_weight_sum = Fraction(upper, granted_floor)
    need(max_weight_sum == Fraction(56, 5), "224/20 = 56/5")

    j_terms = identity_extension_term_count()
    gram_terms = signed_gram_extension_term_count()
    # Expensive J-bearing extensions do not discriminate: 460 <= huge decomposition cost.
    need(j_terms == 12433 and gram_terms == 6329, "predecessor extension counts")
    need(local_floor_sum <= j_terms and local_floor_sum <= gram_terms, "non-discriminating")

    return {
        "schema_version": 1,
        "claim": "fit_level_residual_local_opt_C5_charge_fails_on_diagonal_identity",
        "scalar_ports": 112,
        "complete_planes": 56,
        "cycles": cycle_rows,
        "cycle_count": cycle_count,
        "rank_histogram": {str(k): v for k, v in sorted(Counter(ranks).items())},
        "global_full_support_rank": global_rank,
        "granted_local_floor": granted_floor,
        "uniform_local_floor_sum": local_floor_sum,
        "diagonal_fit": diagonal,
        "candidate_inequality": "sum_C Cost_opt(K|_C) <= Cost_opt(K)",
        "candidate_evaluated_on": "K = I_112",
        "inequality_holds": False,
        "max_nonnegative_weight_sum_on_I_via_diagonal_upper_bound": str(max_weight_sum),
        "j_identity_extension_terms": j_terms,
        "signed_gram_extension_terms": gram_terms,
        "j_extensions_discriminate_candidate": False,
        "no_new_kappa": True,
        "selected_kappa": "0.001672660197076918",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = build()
    if args.emit:
        text = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output is not None:
            out = args.output.resolve()
            need(not out.exists(), "refuse overwrite")
            need(out.parent.is_dir(), "output parent")
            out.write_text(text)
        else:
            print(text, end="")
        return
    committed = json.loads((HERE / "RESULT.json").read_bytes())
    need(result == committed, "exact receipt")
    print(PASS_LINE)


if __name__ == "__main__":
    main()
