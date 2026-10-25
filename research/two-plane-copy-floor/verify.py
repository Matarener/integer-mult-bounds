#!/usr/bin/env python3
"""Exact finite premises for PROOF.md; no predecessor implementation imports.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
The all-field, unbounded-term conclusion is a written proof, not a finite test.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import io
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MATCHING = "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
ARCHIVE_HASH = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MATCHING_HASH = "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1"
MEMBER_HASH = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"


class Rejected(ValueError):
    """An explicit mathematical or source obligation failed."""


def require(ok, message):
    if not ok:
        raise Rejected(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rank2(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def dot(a, b):
    return (a & b).bit_count() % 2


def validate_matching(labels, planes):
    require(len(labels) == 112 and len(set(labels)) == 112, "112 distinct labels")
    require(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    require(len(planes) == 56 and all(len(e) == 2 for e in planes), "56 two-port planes")
    require(sorted(i for e in planes for i in e) == list(range(112)), "matching partition")
    for u, v in planes:
        require((dot(labels[u], labels[u]), dot(labels[v], labels[v]),
                 dot(labels[u], labels[v])) == (1, 1, 0), "plane Gram I2")


def inputs():
    archive = (ROOT / ARCHIVE).read_bytes()
    require(sha(archive) == ARCHIVE_HASH, "selected archive hash")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tf:
        member = tf.extractfile(MEMBER)
        require(member is not None, "selected member present")
        payload = member.read()
    require(sha(payload) == MEMBER_HASH, "selected member hash")
    raw = (ROOT / MATCHING).read_bytes()
    require(sha(raw) == MATCHING_HASH, "matching hash")
    cert = json.loads(raw)
    require(cert["selected_archive_sha256"] == ARCHIVE_HASH, "matching archive binding")
    require(cert["selected_payload_sha256"] == MEMBER_HASH, "matching payload binding")
    data = json.loads(payload)
    recipes = sorted(data["recipes"], key=lambda r: r["port"])
    require(data["ports"] == 112 and [r["port"] for r in recipes] == list(range(112)),
            "selected recipe order")
    labels = [r["q"] for r in recipes]
    planes = cert["matching"]
    validate_matching(labels, planes)
    return labels, planes


def costs_for_pair(labels, planes, pair):
    first, second = (planes[i] for i in pair)
    groups = {1: first, 2: second, 3: first + second}
    costs = {}
    for s, t in itertools.product((1, 2, 3), repeat=2):
        rows = [sum(dot(labels[a], labels[b]) << j for j, b in enumerate(groups[t]))
                for a in groups[s]]
        costs[s, t] = rank2(rows)
    return costs


def certify_tariff(costs, p=2, q=2):
    """Check the nine atom inequalities for the rank-subadditivity dual."""
    c = costs[1, 2]
    require(costs[2, 1] == c and 0 <= c <= min(p, q), "cross-rank domain")
    require(costs[1, 1] == p and costs[2, 2] == q, "nondegenerate blocks")
    require(costs[3, 3] + c >= p + q, "Schur rank inequality")
    weights = (p - c, q - c, c)
    slacks = []
    for s, t in itertools.product((1, 2, 3), repeat=2):
        # Rank of an atom's diagonal block is one iff both factors touch it.
        lower = weights[0]*bool(s & t & 1) + weights[1]*bool(s & t & 2) + weights[2]
        require(costs[s, t] >= lower, f"atom dual ({s},{t})")
        slacks.append(costs[s, t] - lower)
    require(weights[0]*p + weights[1]*q + weights[2]*(p+q) == p*p + q*q,
            "identity dual objective")
    return list(weights), slacks


def general_block_checks():
    """Finite corroboration only: every binary B for 1 <= p,q <= 3."""
    cases = 0
    for p, q in itertools.product(range(1, 4), repeat=2):
        for code in range(1 << (p*q)):
            cross = [(code >> (i*q)) & ((1 << q)-1) for i in range(p)]
            columns = [sum(((cross[i] >> j) & 1) << i for i in range(p))
                       for j in range(q)]
            block = [(1 << i) | (cross[i] << p) for i in range(p)]
            block += [columns[j] | (1 << (p+j)) for j in range(q)]
            c, r = rank2(cross), rank2(block)
            table = {(1, 1): p, (2, 2): q, (1, 2): c, (2, 1): c,
                     (1, 3): p, (3, 1): p, (2, 3): q, (3, 2): q, (3, 3): r}
            certify_tariff(table, p, q)
            cases += 1
    return cases


# Small exact Q(i) arithmetic: ordinary transpose, no floating point.
def scalar(x):
    return (Fraction(x), Fraction(0)) if not isinstance(x, tuple) else tuple(map(Fraction, x))


def add(x, y):
    return (x[0]+y[0], x[1]+y[1])


def mul(x, y):
    return (x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0])


def closure(nonzero):
    return (1 if any(nonzero[:2]) else 0) | (2 if any(nonzero[2:]) else 0)


def endpoint(terms, hermitian=False):
    result = [[scalar(0) for _ in range(4)] for _ in range(4)]
    for left, right in terms:
        for i, j in itertools.product(range(4), repeat=2):
            a, b = scalar(left[i]), scalar(right[j])
            if hermitian:
                b = (b[0], -b[1])
            result[i][j] = add(result[i][j], mul(a, b))
    return result


def identity_check(terms, hermitian=False):
    expected = [[scalar(i == j) for j in range(4)] for i in range(4)]
    require(endpoint(terms, hermitian) == expected, "arbitrary-input identity endpoint")


def term_costs(terms, costs):
    out = []
    for left, right in terms:
        s = closure([scalar(x) != scalar(0) for x in left])
        t = closure([scalar(x) != scalar(0) for x in right])
        require(s != 0 and t != 0, "nonzero rank-one term")
        out.append(costs[s, t])
    return out


def fixtures():
    e = [[int(i == j) for i in range(4)] for j in range(4)]
    direct = [(x, x) for x in e]
    # Inverse entry (0,2) vanishes by cancellation 2*3 - 6 = 0.
    matrix = [[1, 2, 6, 0], [0, 1, 3, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    inverse = [[1, -2, 0, 0], [0, 1, -3, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    cancellation = [(list(column), row) for column, row in zip(zip(*matrix), inverse)]
    mixed = [([1, 0, 1, 0], [1, 0, 1, 0]), ([0, 1, 0, 1], [0, 1, 0, 1])]
    overcomplete = mixed + [([-x for x in e[i]], e[j]) for i, j in ((0, 2), (2, 0), (1, 3), (3, 1))]
    gaussian = [(list(x), list(y)) for x, y in direct]
    gaussian[0] = ([(0, 1), 0, 0, 0], [(0, -1), 0, 0, 0])
    return {"identity": direct, "rational_cofactor_cancellation": cancellation,
            "six_term_overcomplete": overcomplete, "ordinary_complex_transpose": gaussian}


def negative_controls(labels, planes, example_costs, examples):
    controls = []

    def rejects(name, f):
        try:
            f()
        except Rejected:
            controls.append(name)
        else:
            raise Rejected("control accepted: " + name)

    duplicate = [list(e) for e in planes]
    duplicate[0] = [0, 0]
    rejects("duplicate_matching_port", lambda: validate_matching(labels, duplicate))
    altered = list(labels)
    altered[0] = 0
    rejects("invalid_selected_label", lambda: validate_matching(altered, planes))
    underpriced = dict(example_costs["1,3"])
    underpriced[3, 3] = 2
    rejects("underpriced_joint_copy", lambda: certify_tariff(underpriced))
    # Keep the actual cross rank in the dual and falsify one cross tariff.
    cross = dict(example_costs["1,4"])
    cross[2, 1] = 0
    rejects("cross_term_cannot_be_free", lambda: certify_tariff(cross))
    terms = fixtures()["six_term_overcomplete"]
    rejects("omitted_off_diagonal_compensation", lambda: identity_check(terms[:-1]))
    rejects("broadcast_is_not_identity", lambda: identity_check(terms[:2]))
    rejects("Hermitian_is_not_ordinary_transpose",
            lambda: identity_check(fixtures()["ordinary_complex_transpose"], True))
    require(examples["0,4"]["six_term_overcomplete"] == [4, 4, 0, 0, 0, 0],
            "equal-mass power-cost boundary control")
    return controls


def compute():
    labels, planes = inputs()
    pair_list = list(itertools.combinations(range(56), 2))
    histogram, representatives, example_costs = Counter(), {}, {}
    tariff_digest = hashlib.sha256()
    slacks_histogram = Counter()
    for pair in pair_list:
        costs = costs_for_pair(labels, planes, pair)
        _, slacks = certify_tariff(costs)
        kind = f"{costs[1, 2]},{costs[3, 3]}"
        histogram[kind] += 1
        representatives.setdefault(kind, list(pair))
        example_costs.setdefault(kind, costs)
        slacks_histogram.update(slacks)
        tariff_digest.update(bytes(costs[s, t] for s, t in itertools.product((1, 2, 3), repeat=2)))
        require(2*costs[1, 1] + 2*costs[2, 2] == 8, "attaining separate basis")
    examples = {}
    for kind, costs in sorted(example_costs.items()):
        examples[kind] = {}
        for name, terms in fixtures().items():
            identity_check(terms)
            values = term_costs(terms, costs)
            require(sum(values) >= 8, "fixture lower bound")
            examples[kind][name] = values
    controls = negative_controls(labels, planes, example_costs, examples)
    power_profile = examples["0,4"]["six_term_overcomplete"]
    baseline_profile = examples["0,4"]["identity"]
    power_squares = []
    for profile in (power_profile, baseline_profile):
        positive = [r for r in profile if r]
        require(len(set(positive)) == 1, "uniform positive ranks in power fixture")
        power_squares.append(len(positive)**2 * positive[0])
    require(power_squares[0] < power_squares[1], "strict power improvement control")
    seed_pair = pair_list[27]
    seed_costs = costs_for_pair(labels, planes, seed_pair)
    width, live, calls, copy = 73, 896, 9, 224
    mass, capacity = (width-2)*live + copy*calls, width*live
    require(Fraction(mass, capacity) == Fraction(293, 292) > 1, "coverage rejection")
    return {
        "schema": "two-plane-copy-floor-v1", "assignment_seed": 27,
        "source_archive_sha256": ARCHIVE_HASH, "source_member_sha256": MEMBER_HASH,
        "matching_sha256": MATCHING_HASH,
        "selected_planes": 56, "selected_pairs": len(pair_list),
        "cross_rank_joint_rank_histogram": dict(sorted(histogram.items())),
        "class_representatives": representatives,
        "tariff_table_sha256": tariff_digest.hexdigest(),
        "atom_inequalities": 9*len(pair_list),
        "atom_slack_histogram": {str(k): v for k, v in sorted(slacks_histogram.items())},
        "general_binary_block_cases_p_q_1_to_3": general_block_checks(),
        "seed_pair": {"indices": list(seed_pair), "ports": [planes[i] for i in seed_pair],
                      "dual_weights": certify_tariff(seed_costs)[0],
                      "cross_rank": seed_costs[1, 2], "joint_rank": seed_costs[3, 3]},
        "exact_minimum_copy_mass_per_pair": 8,
        "all_field_theorem": "PROOF.md, not inferred from the finite replay",
        "fixture_tariffs_by_geometry": examples,
        "rejected_controls": controls,
        "power_boundary": {"profile": {str(r): n for r, n in Counter(power_profile).items()},
                           "mass": sum(power_profile), "squared_bill_at_half": power_squares[0],
                           "squared_baseline_bill_at_half": power_squares[1]},
        "pair_local_partition_budget": {"plane_pairs": 28, "minimum_copy_mass": copy,
              "width": width, "live": live, "calls": calls, "paid_mass_lower": mass,
              "capacity": capacity, "mass_ratio": str(Fraction(mass, capacity)),
              "extra_charges_optimistically": 0, "positive_saving_possible_in_this_model": False},
        "selected_kappa_changed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new receipt; refuse overwrite")
    parser.add_argument("--certificate", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    result = compute()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as out:
            out.write(encoded)
    else:
        require(args.certificate.read_text(encoding="utf-8") == encoded, "receipt differs from exact replay")
    print("PASS_TWO_PLANE_COPY_FLOOR pairs=1540 atom_inequalities=13860 "
          "copy_min=8 pair_local_mass=224 coverage_ratio=293/292 "
          f"controls={len(result['rejected_controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
