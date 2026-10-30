#!/usr/bin/env python3
"""Exhaust signed-ternary three-channel gauges of the rank-34 P112 fit."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import tarfile
from collections import Counter
import argparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
CERTIFICATE = "research/paired-plane-rank34-copy-audit/PR3335-CERTIFICATE.json"
PORTS, PLANES, CHANNELS = 112, 56, 34
ALPHABET = (-1, 0, 1)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def check_sources() -> dict[str, str]:
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "pinned canonical-main base")
    result = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        need(digest(data) == row["sha256"], "source SHA256: " + row["path"])
        need(git_blob(data) == row["git_blob"], "source Git blob: " + row["path"])
        result[row["path"]] = row["sha256"]
    need(ARCHIVE in result and CERTIFICATE in result, "archive and certificate are live pins")
    return result


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def rank_f2(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def pairing_rank(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return rank_f2([
        sum(dot(a, b) << j for j, b in enumerate(right))
        for a in left
    ])


def load_inputs() -> tuple[list[int], list[tuple[int, int]], list[list[int]]]:
    archive_path = ROOT / ARCHIVE
    with tarfile.open(archive_path, "r:gz") as archive:
        entries = [m for m in archive.getmembers() if m.name == ARCHIVE_MEMBER]
        need(len(entries) == 1 and entries[0].isfile(), "unique regular selected label member")
        stream = archive.extractfile(entries[0])
        need(stream is not None, "selected label member can be read")
        records = json.loads(stream.read())["recipes"]
    records.sort(key=lambda row: row["port"])
    need(len(records) == PORTS and [r["port"] for r in records] == list(range(PORTS)),
         "all selected ports exactly once")
    labels = [r["q"] for r in records]
    need(len(set(labels)) == PORTS and all(type(q) is int and 0 < q < 512 for q in labels),
         "112 distinct nine-bit labels")
    certificate = json.loads((ROOT / CERTIFICATE).read_text(encoding="utf-8"))
    pairs = [tuple(pair) for pair in certificate["pairs"]]
    supports = [list(support) for support in certificate["supports"]]
    need(len(pairs) == PLANES and all(len(p) == 2 for p in pairs), "56 paired planes")
    need(sorted(port for pair in pairs for port in pair) == list(range(PORTS)), "plane partition")
    need(len(supports) == CHANNELS and sorted(p for s in supports for p in s) == list(range(PORTS)),
         "34 published scalar supports partition the ports")
    need(all(dot(labels[a], labels[a]) == dot(labels[b], labels[b]) == 1
             and dot(labels[a], labels[b]) == 0 for a, b in pairs), "every pair spans Gram I2")
    return labels, pairs, supports


def determinant(a: tuple[int, ...]) -> int:
    x = [a[3 * r:3 * r + 3] for r in range(3)]
    return (x[0][0] * (x[1][1] * x[2][2] - x[1][2] * x[2][1])
            - x[0][1] * (x[1][0] * x[2][2] - x[1][2] * x[2][0])
            + x[0][2] * (x[1][0] * x[2][1] - x[1][1] * x[2][0]))


def cofactor(a: tuple[int, ...], row: int, col: int) -> int:
    x = [a[3 * r:3 * r + 3] for r in range(3)]
    rs = [r for r in range(3) if r != row]
    cs = [c for c in range(3) if c != col]
    return (-1 if (row + col) & 1 else 1) * (
        x[rs[0]][cs[0]] * x[rs[1]][cs[1]] - x[rs[0]][cs[1]] * x[rs[1]][cs[0]])


def support_map(a: tuple[int, ...]) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    # Source columns are columns of S. Reader rows are rows of adj(S)/det(S).
    columns = tuple(sum(1 << r for r in range(3) if a[3 * r + c]) for c in range(3))
    inverse_rows = tuple(sum(1 << c for c in range(3) if cofactor(a, c, r))
                         for r in range(3))
    return columns, inverse_rows


def enumerate_gauge_maps() -> tuple[list[dict], int]:
    maps: dict[tuple[tuple[int, ...], tuple[int, ...]], dict] = {}
    invertible = 0
    for matrix in itertools.product(ALPHABET, repeat=9):
        det = determinant(matrix)
        if not det:
            continue
        invertible += 1
        columns, inverse_rows = support_map(matrix)
        key = columns, inverse_rows
        if key not in maps:
            maps[key] = {"source_column_masks": list(columns),
                         "reader_inverse_row_masks": list(inverse_rows),
                         "witness_matrix": list(matrix), "determinant": det}
    return [maps[k] for k in sorted(maps)], invertible


def plane_invoice(labels: list[int], pairs: list[tuple[int, int]],
                  supports: list[list[int]], gauge_maps: list[dict]) -> dict:
    owner = {port: plane for plane, pair in enumerate(pairs) for port in pair}
    plane_vectors = [(labels[a], labels[b]) for a, b in pairs]
    channel_planes = [tuple(sorted({owner[port] for port in support})) for support in supports]

    def vectors(plane_ids: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(q for p in plane_ids for q in plane_vectors[p])

    base_cost = [pairing_rank(vectors(planes), vectors(planes)) for planes in channel_planes]
    need(Counter(base_cost) == Counter({4: 8, 6: 8, 8: 18}) and sum(base_cost) == 224,
         "predecessor full-plane invoice is 224")
    delta_hist: Counter[int] = Counter()
    total_cases = 0
    for triple in itertools.combinations(range(CHANNELS), 3):
        old_cost = sum(base_cost[i] for i in triple)
        subsets = {
            mask: tuple(sorted({p for local, channel in enumerate(triple) if mask >> local & 1
                                for p in channel_planes[channel]}))
            for mask in range(1, 8)
        }
        ranks = {(left, right): pairing_rank(vectors(subsets[left]), vectors(subsets[right]))
                 for left in range(1, 8) for right in range(1, 8)}
        for gauge in gauge_maps:
            delta = sum(ranks[gauge["source_column_masks"][new_channel],
                               gauge["reader_inverse_row_masks"][new_channel]]
                        for new_channel in range(3)) - old_cost
            delta_hist[delta] += 1
            total_cases += 1
    need(total_cases == 5984 * len(gauge_maps), "every triple/support-map case counted once")
    need(min(delta_hist) == 0, "no strict local invoice reduction")
    need(all(delta >= 0 for delta in delta_hist), "all screened transformations are non-improving")
    return {
        "baseline_channel_ranks": base_cost,
        "baseline_histogram": {str(k): v for k, v in sorted(Counter(base_cost).items())},
        "baseline_invoice": sum(base_cost),
        "channel_triples": 5984,
        "distinct_support_maps_per_triple": len(gauge_maps),
        "triple_support_map_cases": total_cases,
        "local_delta_histogram": {str(k): v for k, v in sorted(delta_hist.items())},
        "minimum_invoice": 224 + min(delta_hist),
        "strict_improvement_cases": sum(v for d, v in delta_hist.items() if d < 0),
        "baseline_invoice_cases": delta_hist[0],
        "minimum_delta": min(delta_hist),
        "maximum_delta": max(delta_hist),
    }


def verify_gauge_identity(labels: list[int], pairs: list[tuple[int, int]],
                          supports: list[list[int]]) -> dict:
    """Check one dense, rational, nontrivial instance and a wrong-inverse control."""
    from fractions import Fraction
    matrix = (1, 1, 0, 0, 1, 1, 1, 0, 1)  # determinant 2, so S^{-1} has halves.
    det = determinant(matrix)
    need(det == 2, "fixture determinant two")
    inv = [[Fraction(cofactor(matrix, c, r), det) for c in range(3)] for r in range(3)]
    s = [[Fraction(matrix[3 * r + c]) for c in range(3)] for r in range(3)]
    need([[sum(s[i][k] * inv[k][j] for k in range(3)) for j in range(3)]
          for i in range(3)] == [[Fraction(i == j) for j in range(3)] for i in range(3)],
         "S times exact rational inverse equals identity")
    # Select three channels whose supports make this a genuine cross-group mix.
    triple = (0, 1, 2)
    need(all(supports[i] for i in triple), "three nonempty source supports")
    before = [[Fraction(sum(int(i in support and j in support) for support in supports))
               for j in range(PORTS)] for i in range(PORTS)]
    transformed = []
    for ch in range(3):
        src = [sum(Fraction(matrix[3 * old + ch]) * int(port in supports[triple[old]])
                   for old in range(3)) for port in range(PORTS)]
        dst = [sum(inv[ch][old] * int(port in supports[triple[old]])
                   for old in range(3)) for port in range(PORTS)]
        transformed.append((src, dst))
    after = [[sum(transformed[ch][0][i] * transformed[ch][1][j]
                  for ch in range(3))
               + sum(Fraction(int(i in support and j in support))
                     for k, support in enumerate(supports) if k not in triple)
               for j in range(PORTS)] for i in range(PORTS)]
    need(after == before, "dense rational 112x112 scalar matrix is preserved")
    wrong = []
    for ch in range(3):
        src = [sum(s[old][ch] * int(port in supports[triple[old]]) for old in range(3))
               for port in range(PORTS)]
        dst = [sum(s[ch][old] * int(port in supports[triple[old]]) for old in range(3))
               for port in range(PORTS)]
        wrong.append((src, dst))
    wrong_after = [[sum(wrong[ch][0][i] * wrong[ch][1][j] for ch in range(3))
                    + sum(int(i in support and j in support)
                          for k, support in enumerate(supports) if k not in triple)
                    for j in range(PORTS)] for i in range(PORTS)]
    need(wrong_after != before, "using S instead of its inverse is rejected")
    return {"fixture_matrix": list(matrix), "determinant": det,
            "dense_entries_checked": PORTS * PORTS,
            "wrong_inverse_rejected": True}


def build_certificate(source_hashes: dict, gauge_maps: list[dict], invertible: int,
                      invoice: dict, identity: dict) -> dict:
    return {
        "schema_version": 1,
        "base_commit": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "selected_archive_sha256": source_hashes[ARCHIVE],
        "rank34_certificate_sha256": source_hashes[CERTIFICATE],
        "object": "full-plane one-total invoice under a 3-channel signed-ternary rational gauge",
        "gauge_domain": {
            "coefficient_alphabet": list(ALPHABET),
            "matrices_considered": 3 ** 9,
            "invertible_over_Q": invertible,
            "distinct_source_inverse_support_maps": len(gauge_maps),
            "triples_of_channels": 5984,
            "support_map_cases": invoice["triple_support_map_cases"],
            "gauge_action": "A' = A S; B' = S^{-1} A^T; K'=A'B'=AA^T",
            "scope": "one selected triple; identity on the other31 channels",
        },
        "baseline_copy_invoice": invoice["baseline_invoice"],
        "minimum_invoice_in_domain": invoice["minimum_invoice"],
        "strict_improvements": invoice["strict_improvement_cases"],
        "invoice_search": invoice,
        "support_map_witnesses": gauge_maps,
        "exact_matrix_identity_control": identity,
        "scope_limit": "does not cover larger or overlapping gauge blocks, arbitrary rational coefficient matrices, a physical native implementation, or supplier admission",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-artifacts", action="store_true",
                        help="write exact CERTIFICATE.json and RESULT.json")
    args = parser.parse_args()
    source_hashes = check_sources()
    labels, pairs, supports = load_inputs()
    gauge_maps, invertible = enumerate_gauge_maps()
    need(invertible == 11808 and len(gauge_maps) == 396, "complete signed-ternary 3x3 classification")
    identity = verify_gauge_identity(labels, pairs, supports)
    invoice = plane_invoice(labels, pairs, supports, gauge_maps)
    certificate = build_certificate(source_hashes, gauge_maps, invertible, invoice, identity)
    result = {
        "schema_version": 1,
        "status": "completed scoped negative screen; no kappa change",
        "task_id": "coverage-law-change",
        "priority_revision": 6,
        "base_commit": certificate["base_commit"],
        "baseline_copy_invoice": 224,
        "minimum_after_one_three_channel_gauge": 224,
        "improving_gauges": 0,
        "covered_gauge_maps": 396,
        "covered_channel_triples": 5984,
        "priced_cases": 2369664,
        "delta_histogram": invoice["local_delta_histogram"],
        "result": "no single signed-ternary rational change of basis on any three of the34 scalar channels lowers the complete-plane copy invoice",
        "limitations": [
            "This is a local gauge obstruction for the exact PR3335 factorization, not a lower bound for all scalar factorizations.",
            "Arbitrary rational coefficient matrices and simultaneous changes involving four or more channels remain open.",
            "The pairing tariff is an inherited conditional proxy; no complete physical word, dirty-helper restoration, supplier, or new kappa is established.",
        ],
    }
    cert_path, result_path = HERE / "CERTIFICATE.json", HERE / "RESULT.json"
    if args.write_artifacts:
        cert_path.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
        result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        need(certificate == json.loads(cert_path.read_text(encoding="utf-8")),
             "certificate differs from exact reconstruction")
        need(result == json.loads(result_path.read_text(encoding="utf-8")), "RESULT.json mismatch")
    print("PASS_PAIRED_PLANE_RANK34_TRIPLE_GAUGE matrices=11808 maps=396 triples=5984 "
          "cases=2369664 baseline=224 minimum=224 improvements=0")


if __name__ == "__main__":
    main()
