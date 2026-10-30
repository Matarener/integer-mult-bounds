#!/usr/bin/env python3
"""Independent mask and complete-plane tariff audit of PR3335's fixed fit.

Arham-Tahir64, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported by this checker.
"""
import argparse
import hashlib
import json
import tarfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
MEMBER_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"


class CheckFailure(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise CheckFailure(message)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def blob(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def authenticate(payload, row):
    need(digest(payload) == row["sha256"], "source SHA256: " + row["path"])
    need(blob(payload) == row["git_blob"], "source Git blob: " + row["path"])


def check_sources():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            authenticate((ROOT / row["path"]).read_bytes(), row)
    vendor = json.loads((HERE / "VENDOR.json").read_text())
    for row in vendor["files"]:
        authenticate((HERE / row["local_file"]).read_bytes(), row)


def load_labels():
    with tarfile.open(ROOT / ARCHIVE) as archive:
        entries = [m for m in archive.getmembers() if m.name == MEMBER]
        need(len(entries) == 1 and entries[0].isfile(), "unique regular label member")
        with archive.extractfile(entries[0]) as handle:
            payload = handle.read()
    need(digest(payload) == MEMBER_SHA256, "selected DATA-PHASES payload")
    data = json.loads(payload)
    need(data["m"] == 73 and data["ports"] == 112, "selected dimensions")
    rows = sorted(data["recipes"], key=lambda r: r["port"])
    need([r["port"] for r in rows] == list(range(112)), "all selected port indices")
    labels = [r["q"] for r in rows]
    need(len(set(labels)) == 112 and all(type(q) is int and 0 < q < 512 for q in labels),
         "distinct binary labels in nine dimensions")
    return labels


def dot(a, b):
    return (a & b).bit_count() % 2


def binary_basis(vectors):
    """Return an independent subsequence, eliminating from the lowest bit."""
    pivots, independent = {}, []
    for original in vectors:
        value = original
        while value:
            bit = (value & -value).bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                independent.append(original)
                break
    return independent


def pairing_rank(left, right):
    rows = [sum(dot(a, b) << j for j, b in enumerate(right)) for a in left]
    return len(binary_basis(rows))


def plane_model(labels, pairs):
    n = len(labels)
    need(len(pairs) * 2 == n and all(len(p) == 2 for p in pairs), "pair count")
    need(all(type(i) is int for p in pairs for i in p), "integer port indices")
    need(sorted(i for p in pairs for i in p) == list(range(n)), "perfect matching")
    planes = [[labels[i] for i in p] for p in pairs]
    for q, r in planes:
        need(dot(q, q) == dot(r, r) == 1 and dot(q, r) == 0, "Gram-I2 pair")
    owner = {port: j for j, pair in enumerate(pairs) for port in pair}
    orth = [[all(dot(a, b) == 0 for a in left for b in right)
             for right in planes] for left in planes]
    return planes, owner, orth


def fitting_matrix(supports, n):
    need(supports and all(s for s in supports), "nonempty supports")
    need(all(type(i) is int and 0 <= i < n for s in supports for i in s), "support port range")
    need(sorted(i for s in supports for i in s) == list(range(n)), "disjoint support partition")
    matrix = [[0] * n for _ in range(n)]
    for support in supports:
        for i in support:
            for j in support:
                matrix[i][j] += 1
    return matrix


def check_mask(matrix, owner, orth):
    n = len(owner)
    need(len(matrix) == n and all(len(row) == n for row in matrix), "scalar matrix dimensions")
    forced = 0
    for i in range(n):
        for j in range(n):
            if i == j or not orth[owner[i]][owner[j]]:
                forced += 1
                need(matrix[i][j] == int(i == j), "strict mask entry (%d,%d)" % (i, j))
    return forced


def channel_invoice(labels, pairs, supports):
    planes, owner, orth = plane_model(labels, pairs)
    matrix = fitting_matrix(supports, len(labels))
    check_mask(matrix, owner, orth)
    channels = []
    for number, support in enumerate(supports):
        # A port carries its entire source/reader plane, including its partner.
        full = [v for port in support for v in planes[owner[port]]]
        gram = [[dot(a, b) for b in full] for a in full]
        need(gram == [[int(i == j) for j in range(len(full))] for i in range(len(full))],
             "complete support planes form an orthonormal direct sum")
        rank = pairing_rank(full, full)
        need(rank == len(binary_basis(full)) == 2 * len(support), "full-plane tariff rank")
        singleton = [labels[i] for i in support]
        need(pairing_rank(singleton, singleton) == len(support), "singleton-label control")
        channels.append({"channel": number, "ports": support,
                         "plane_basis": full, "copy_rank": rank,
                         "singleton_label_rank": len(support)})
    return channels


def require_invoice(channels, claimed):
    need(sum(c["copy_rank"] for c in channels) == claimed, "complete-plane copy invoice")


def orthogonal_local_factor_check(labels, pairs, factors):
    """Exact rational fixtures for the orthogonal-local floor in README.md.

    A factor is (weight, target_coefficients, source_coefficients), with sparse
    integer-keyed dictionaries. This does not decide an arbitrary factorization
    problem. The all-field claim follows from the written rank argument.
    """
    planes, owner, orth = plane_model(labels, pairs)
    matrix = [[Fraction(0) for _ in labels] for _ in labels]
    hits = Counter()
    cost = 0
    for weight, target, source in factors:
        weight = Fraction(weight)
        need(weight != 0 and target and source, "nonzero scalar term")
        need(all(type(p) is int and 0 <= p < len(labels) and Fraction(c) != 0
                 for part in (target, source) for p, c in part.items()), "nonzero factor support")
        row_planes = {owner[i] for i in target}
        col_planes = {owner[i] for i in source}
        union = row_planes | col_planes
        need(all(p == q or orth[p][q] for p in union for q in union),
             "term stays within mutually orthogonal distinct planes")
        row_basis = [v for p in sorted(row_planes) for v in planes[p]]
        col_basis = [v for p in sorted(col_planes) for v in planes[p]]
        rank = pairing_rank(row_basis, col_basis)
        need(rank == 2 * len(row_planes & col_planes), "orthogonal-local tariff identity")
        cost += rank
        hits.update(row_planes & col_planes)
        for i, a in target.items():
            for j, b in source.items():
                matrix[i][j] += weight * Fraction(a) * Fraction(b)
    check_mask(matrix, owner, orth)
    need(all(hits[p] >= 2 for p in range(len(pairs))), "I2 needs two scalar totals per plane")
    need(cost == 2 * sum(hits.values()) and cost >= 4 * len(pairs), "orthogonal-local cost floor")
    return cost, matrix


def half_weight_fixture(labels, pairs, supports):
    """Polarize the two independent totals on each published plane group."""
    _, owner, _ = plane_model(labels, pairs)
    groups = {}
    for support in supports:
        groups.setdefault(tuple(sorted(owner[i] for i in support)), []).append(support)
    factors = []
    for group in groups.values():
        need(len(group) == 2, "two disjoint port-position totals per plane group")
        first, second = group
        plus = {i: 1 for i in first + second}
        minus = {i: 1 for i in first} | {i: -1 for i in second}
        factors.extend([(Fraction(1, 2), plus, plus), (Fraction(1, 2), minus, minus)])
    cost, matrix = orthogonal_local_factor_check(labels, pairs, factors)
    need(matrix == fitting_matrix(supports, len(labels)), "half-weight polarization preserves the exact fit")
    return {"plane_groups": len(groups), "terms": len(factors), "copy_rank_mass": cost}


def evaluate(labels, certificate):
    pairs, supports = certificate["pairs"], certificate["supports"]
    _, owner, orth = plane_model(labels, pairs)
    matrix = fitting_matrix(supports, len(labels))
    forced = check_mask(matrix, owner, orth)
    representatives = [s[0] for s in supports]
    need([[matrix[i][j] for j in representatives] for i in representatives]
         == [[int(i == j) for j in range(len(supports))] for i in range(len(supports))],
         "support representative identity minor")
    clique = certificate["clique_planes"]
    need(len(clique) == len(set(clique)) and all(type(i) is int and 0 <= i < len(pairs) for i in clique),
         "clique plane indices")
    ports = [i for p in clique for i in pairs[p]]
    need(all(i == j or not orth[owner[i]][owner[j]] for i in ports for j in ports),
         "forced identity minor in every fit")
    need(len(ports) == len(supports), "matching all-field lower and upper bounds")
    channels = channel_invoice(labels, pairs, supports)
    cost = sum(c["copy_rank"] for c in channels)
    # Necessary rank-mass bound under the retained two-unpaid coverage law.
    W, N, m = 896, 9, 73
    mass = (m - 2) * W + cost * N
    capacity = m * W
    forbidden_parity = [(i, j) for i in range(len(labels)) for j in range(len(labels))
                        if i != j and dot(labels[i], labels[j])]
    need(all(matrix[i][j] == 0 for i, j in forbidden_parity), "new fit avoids parity-forced cross entries")
    i, j = forbidden_parity[0]
    return {
        "status": "PASS_PAIRED_PLANE_RANK34_COPY_AUDIT",
        "ports": len(labels), "planes": len(pairs), "forced_scalar_entries": forced,
        "scalar_fitting_rank_all_fields": len(supports),
        "forced_identity_minor": len(ports),
        "support_sizes": dict(sorted(Counter(map(len, supports)).items())),
        "copy_rank_histogram": dict(sorted(Counter(c["copy_rank"] for c in channels).items())),
        "singleton_label_invoice": sum(c["singleton_label_rank"] for c in channels),
        "complete_plane_copy_invoice": cost,
        "rational_half_weight_control": half_weight_fixture(labels, pairs, supports),
        "rank_mass_model": {"m": m, "W": W, "N": N, "mass": mass,
                            "capacity": capacity, "moment_at_zero_lower_bound": str(Fraction(mass, capacity)),
                            "deficit_per_call": str(Fraction(2 * W, N) - cost)},
        "parity_forced_old_cross_entries": len(forbidden_parity),
        "binary_target_total_mismatches": sum(matrix[i][j] % 2 != dot(labels[i], labels[j])
                                               for i in range(len(labels)) for j in range(len(labels))),
        "parity_target_witness": {"ports": [i, j], "labels": [labels[i], labels[j]],
                                  "old_binary_target": 1, "new_scalar_fit": matrix[i][j]},
        "channels": channels,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new receipt, refusing an existing path")
    args = parser.parse_args()
    check_sources()
    result = evaluate(load_labels(), json.loads((HERE / "PR3335-CERTIFICATE.json").read_text()))
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(payload)
    else:
        need(payload == (HERE / "RESULT.json").read_text(), "exact recomputed receipt")
    print("PASS_PAIRED_PLANE_RANK34_COPY_AUDIT scalar_rank=34 channels=34 copy_rank_mass=224 "
          "zero_moment_lower_bound=293/292 no_new_kappa")


if __name__ == "__main__":
    main()
