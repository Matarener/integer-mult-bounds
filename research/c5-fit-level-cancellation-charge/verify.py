#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Named-class fit-level C5 cancellation charge beats termwise 180/7."""

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
    "PASS_C5_FIT_LEVEL_CANCELLATION_CHARGE "
    "cycles=23 weight_sum=9/4 J_free_floor=45 one_J_floor=561/16 "
    "termwise_ceiling=180/7 beats=true"
)

# Integer weights are 16 * lambda; sum W = 36 <=> sum lambda = 9/4.
WEIGHT16 = (
    0,
    0,
    2,
    0,
    0,
    0,
    8,
    0,
    1,
    0,
    7,
    0,
    2,
    0,
    0,
    0,
    0,
    3,
    0,
    3,
    4,
    6,
    0,
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
    if not left or not right:
        return 0
    pivots = [0] * len(right)
    for label in left:
        row = 0
        for j, other in enumerate(right):
            if dot(label, other):
                row |= 1 << j
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


def named_supports():
    singles = [(i,) for i in range(56)]
    pairs = [(i, j) for i in range(56) for j in range(i + 1, 56)]
    return singles + pairs


def local_rank_tables(planes, cycle_rows):
    tables = []
    for cycle in cycle_rows:
        table = [0] * (32 * 32)
        for mask_l in range(32):
            left = tuple(
                q
                for bit in range(5)
                if mask_l >> bit & 1
                for q in planes[cycle[bit]]
            )
            for mask_r in range(32):
                right = tuple(
                    q
                    for bit in range(5)
                    if mask_r >> bit & 1
                    for q in planes[cycle[bit]]
                )
                table[mask_l + 32 * mask_r] = pairing_rank(left, right)
        tables.append(table)
    return tables


def support_masks(support, cycle_rows):
    present = set(support)
    out = []
    for cycle in cycle_rows:
        mask = 0
        for bit, plane in enumerate(cycle):
            if plane in present:
                mask |= 1 << bit
        out.append(mask)
    return out


def dominate_named_supports(planes, cycle_rows, weight16=WEIGHT16) -> dict:
    need(len(weight16) == 23 and sum(weight16) == 36, "fixed weight sum 9/4")
    need(all(type(w) is int and w >= 0 for w in weight16), "nonnegative int weights")
    tables = local_rank_tables(planes, cycle_rows)
    supports = named_supports()
    need(len(supports) == 56 + 56 * 55 // 2, "all 1- and 2-plane supports")
    masks = [support_masks(s, cycle_rows) for s in supports]
    labels = [tuple(q for i in s for q in planes[i]) for s in supports]
    checked = 0
    min_slack = None
    for i, left in enumerate(labels):
        mi = masks[i]
        for j, right in enumerate(labels):
            mj = masks[j]
            global_rank = pairing_rank(left, right)
            loc16 = 0
            for k, w in enumerate(weight16):
                if w:
                    loc16 += w * tables[k][mi[k] + 32 * mj[k]]
            need(loc16 <= 16 * global_rank, "named-support domination")
            slack = 16 * global_rank - loc16
            if min_slack is None or slack < min_slack:
                min_slack = slack
            checked += 1
            need(checked <= 3_000_000, "bounded named census")
    need(checked == len(supports) ** 2, "complete named census")
    need(min_slack == 0, "certificate is tight on at least one rectangle")
    return {
        "named_supports": len(supports),
        "rectangles_checked": checked,
        "min_slack_x16": min_slack,
        "domination_holds": True,
    }


def full_support_local_ranks(planes, cycle_rows):
    ranks = []
    for cycle in cycle_rows:
        local = tuple(q for i in cycle for q in planes[i])
        ranks.append(pairing_rank(local, local))
    return ranks


def diagonal_fit_cost(planes, matching) -> dict:
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
        "net_full_support_terms": 0,
    }


def j_identity_extension_tariff(planes, matching) -> dict:
    """I = J - sum_{i != j} e_i e_j^T; one net full-support term."""
    port_to_plane = {
        port: plane_index
        for plane_index, pair in enumerate(matching)
        for port in pair
    }
    all_labels = tuple(q for plane in planes for q in plane)
    j_cost = pairing_rank(all_labels, all_labels)
    need(j_cost == 9, "full-support tariff")
    od_total = 0
    od_terms = 0
    matrix = [[1] * 112 for _ in range(112)]
    for i in range(112):
        for j in range(112):
            if i == j:
                continue
            cost = pairing_rank(planes[port_to_plane[i]], planes[port_to_plane[j]])
            od_total += cost
            od_terms += 1
            matrix[i][j] -= 1
    need(
        all(matrix[i][j] == int(i == j) for i in range(112) for j in range(112)),
        "J-identity extension exact",
    )
    need(od_terms == 112 * 111, "off-diagonal term count")
    total = j_cost + od_total
    need(total == 16097, "pinned J-extension tariff")
    return {
        "formula": "I = J - sum_{i != j} e_i e_j^T",
        "full_support_tariff": j_cost,
        "off_diagonal_tariff_sum": od_total,
        "off_diagonal_terms": od_terms,
        "total_cost": total,
        "net_full_support_terms": 1,
    }


def build() -> dict:
    planes, matching = geometry()
    cycle_rows = cycles(planes)
    ranks = full_support_local_ranks(planes, cycle_rows)
    global_rank = pairing_rank(
        tuple(q for plane in planes for q in plane),
        tuple(q for plane in planes for q in plane),
    )
    need(global_rank == 9 and Counter(ranks) == {7: 4, 8: 6, 9: 13}, "rank receipt")

    need(sum(WEIGHT16) == 36, "weight sum")
    weight_sum = Fraction(sum(WEIGHT16), 16)
    need(weight_sum == Fraction(9, 4), "9/4")
    lambda_rows = []
    rho16 = 0
    for index, (cycle, rank, w16) in enumerate(zip(cycle_rows, ranks, WEIGHT16)):
        if w16:
            lambda_rows.append(
                {
                    "cycle_index": index,
                    "cycle": list(cycle),
                    "full_support_rank": rank,
                    "lambda": str(Fraction(w16, 16)),
                    "weight16": w16,
                }
            )
        rho16 += w16 * rank
    rho = Fraction(rho16, 16)
    need(rho == Fraction(303, 16), "exact rho")
    credit = rho - 9
    need(credit == Fraction(159, 16), "exact J credit")

    census = dominate_named_supports(planes, cycle_rows)
    j_free_floor = 20 * weight_sum
    one_j_floor = j_free_floor - credit
    termwise_ceiling = Fraction(180, 7)
    need(j_free_floor == 45, "J-free floor")
    need(one_j_floor == Fraction(561, 16), "one-J floor")
    need(j_free_floor > termwise_ceiling, "beats 180/7 on J-free")
    need(one_j_floor > termwise_ceiling, "beats 180/7 with one net J")

    diagonal = diagonal_fit_cost(planes, matching)
    j_ext = j_identity_extension_tariff(planes, matching)
    # Validity checks of the fit-level corollary on the two named identity fits.
    need(diagonal["net_full_support_terms"] == 0, "diagonal is J-free after netting")
    need(diagonal["total_cost"] >= int(j_free_floor), "diagonal satisfies J-free floor")
    need(j_ext["net_full_support_terms"] == 1, "J-extension has one net J")
    need(j_ext["total_cost"] >= float(one_j_floor), "J-extension satisfies one-J floor")

    # Classical all-rectangle termwise on these weights is blocked by full support:
    # rho = 303/16 > 9, so uncredited domination fails on J.
    need(rho > 9, "full-support obstructs uncredited termwise")

    return {
        "schema_version": 1,
        "claim": (
            "named_class_netting_plus_J_credit_C5_charge_beats_termwise_180_over_7"
        ),
        "scalar_ports": 112,
        "complete_planes": 56,
        "cycle_count": 23,
        "cycles": [{"cycle": list(c), "full_support_rank": r} for c, r in zip(cycle_rows, ranks)],
        "rank_histogram": {str(k): v for k, v in sorted(Counter(ranks).items())},
        "global_full_support_rank": global_rank,
        "named_term_classes": [
            "diagonal_e_i_e_i_T",
            "full_support_J",
            "off_diagonal_e_i_e_j_T",
            "pairwise_gram_e_i_plus_e_j",
        ],
        "cancellation_identity": (
            "identical-support opposite-sign netting, then termwise domination on "
            "every 1- and 2-plane named support, with explicit credit (rho-9) per "
            "remaining net full-support term"
        ),
        "weight_sum": str(weight_sum),
        "weights": lambda_rows,
        "rho": str(rho),
        "j_credit": str(credit),
        "named_support_domination": census,
        "j_free_floor": str(j_free_floor),
        "one_j_floor": str(one_j_floor),
        "termwise_ceiling": str(termwise_ceiling),
        "beats_termwise_ceiling_j_free": True,
        "beats_termwise_ceiling_one_j": True,
        "diagonal_fit": diagonal,
        "j_identity_extension": j_ext,
        "granted_local_floor": 20,
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
