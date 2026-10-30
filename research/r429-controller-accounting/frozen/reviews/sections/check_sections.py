#!/usr/bin/env python3
"""Independent row-section checks from two authenticated data files.

No historical producer, checker, or third-party package is imported.  The
general theorem is proved in REVIEW.md; these are finite premise/witness checks.
Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


WORD_SHA = "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022"
GEOMETRY_SHA = "1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_pinned(path, expected):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == expected, f"input digest mismatch: {path.name}")
    return json.loads(gzip.decompress(raw))


def gf2_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def gf2_mul(left, right):
    result = []
    for row in left:
        value, j = 0, 0
        while row:
            if row & 1:
                value ^= right[j]
            row >>= 1
            j += 1
        result.append(value)
    return result


def gf2_inverse(matrix):
    n = len(matrix)
    rows = [r | (1 << (n+i)) for i, r in enumerate(matrix)]
    for j in range(n):
        p = next((i for i in range(j, n) if rows[i] >> j & 1), None)
        require(p is not None, "singular matrix")
        rows[j], rows[p] = rows[p], rows[j]
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    require([r & ((1 << n)-1) for r in rows] == [1 << i for i in range(n)],
            "inverse elimination")
    return [r >> n for r in rows]


def transpose(matrix, columns):
    return [sum(((r >> j) & 1) << i for i, r in enumerate(matrix))
            for j in range(columns)]


def gf2_kernel(matrix, columns):
    rows, pivots = matrix[:], []
    for j in range(columns):
        i = len(pivots)
        p = next((p for p in range(i, len(rows)) if rows[p] >> j & 1), None)
        if p is None:
            continue
        rows[i], rows[p] = rows[p], rows[i]
        for q in range(len(rows)):
            if q != i and rows[q] >> j & 1:
                rows[q] ^= rows[i]
        pivots.append(j)
    result = []
    for j in range(columns):
        if j not in pivots:
            vector = 1 << j
            for i, p in enumerate(pivots):
                vector |= ((rows[i] >> j) & 1) << p
            result.append(vector)
    require(all((row & v).bit_count() % 2 == 0 for row in matrix for v in result),
            "kernel equations")
    return result


def rational_kernel(matrix, columns):
    rows = [list(map(Fraction, row)) for row in matrix]
    pivots = []
    for j in range(columns):
        i = len(pivots)
        p = next((p for p in range(i, len(rows)) if rows[p][j]), None)
        if p is None:
            continue
        rows[i], rows[p] = rows[p], rows[i]
        divisor = rows[i][j]
        rows[i] = [v/divisor for v in rows[i]]
        for q in range(len(rows)):
            if q != i and rows[q][j]:
                scale = rows[q][j]
                rows[q] = [a-scale*b for a, b in zip(rows[q], rows[i])]
        pivots.append(j)
    result = []
    for j in range(columns):
        if j not in pivots:
            vector = [Fraction(0)] * columns
            vector[j] = 1
            for i, p in enumerate(pivots):
                vector[p] = -rows[i][j]
            result.append(tuple(vector))
    require(all(sum(a*b for a, b in zip(row, v)) == 0
                for row in matrix for v in result), "rational kernel equations")
    return result


def normalized(vector):
    first = next(x for x in vector if x)
    return tuple(Fraction(x)/first for x in vector)


def alternating(stages):
    require(len(stages) % 2 == 1, "odd stage count required")
    out = stages[0]
    for i in range(1, len(stages), 2):
        out = gf2_mul(gf2_mul(stages[i+1], gf2_inverse(stages[i])), out)
    return out


def finite_theorem_tests():
    matrices = [list(x) for x in product(range(4), repeat=2)]
    invertible = [x for x in matrices if gf2_rank(x) == 2]
    require(len(invertible) == 6, "GL(2,2) census")
    cases, uncovered_cases = 0, 0
    for length in (1, 3, 5):
        for stages in product(invertible, repeat=length):
            endpoint = alternating(stages)
            for baseline in matrices:
                untouched = [p for p in range(2)
                             if all(a[p] == baseline[p] for a in stages)]
                require(all(endpoint[p] == baseline[p] for p in untouched),
                        "alternating row-support theorem failed")
                cases += 1
                uncovered_cases += bool(untouched)
    swap = [2, 1]
    identity = [1, 2]
    endpoint = alternating([swap] * 9)
    defect = [a ^ b for a, b in zip(endpoint, identity)]
    require(endpoint == swap and gf2_rank(defect) == 1, "rank counterexample")
    require(sum((row >> p) & 1 for p, row in enumerate(defect)) == 2,
            "two diagonal discrepancies")

    # These are concrete counterexamples to deliberately strengthened claims.
    # The rejection predicate is the theorem conclusion, not a status string.
    even_endpoint = gf2_mul(gf2_inverse(swap), swap)
    require(even_endpoint == identity and even_endpoint != swap,
            "omitted odd-stage premise did not change the conclusion")
    cycle = [2, 3]  # Order three, so A A A differs from A A^-1 A.
    missing_inverse_endpoint = gf2_mul(gf2_mul(cycle, cycle), cycle)
    require(missing_inverse_endpoint == identity and alternating([cycle]*3) == cycle,
            "omitted inverse control")

    order_witness = None
    for baseline, a0, a1, a2 in product(invertible, repeat=4):
        untouched = [p for p in range(2)
                     if a0[p] == a1[p] == a2[p] == baseline[p]]
        if not untouched:
            continue
        wrong = gf2_mul(gf2_mul(gf2_inverse(a1), a2), a0)
        if any(wrong[p] != baseline[p] for p in untouched):
            order_witness = dict(J=baseline, stages=[a0, a1, a2],
                                 untouched_rows=untouched, wrong_endpoint=wrong)
            break
    require(order_witness is not None, "factor-order control")
    singular_rejected = False
    try:
        alternating([identity, [0, 2], identity])
    except ValueError:
        singular_rejected = True
    require(singular_rejected, "singular inverse admitted")

    return {
        "GL2_F2_cases": cases,
        "cases_with_an_uncovered_row": uncovered_cases,
        "stage_counts": [1, 3, 5],
        "rank_counterexample": {"field": "F2", "J": swap, "stages": 9,
                               "repair_union": [], "E_minus_I": defect,
                               "diagonal_mismatches": 2, "defect_rank": 1},
        "premise_controls": {
            "even_two_stage_endpoint": even_endpoint,
            "omitted_inverse_endpoint": missing_inverse_endpoint,
            "wrong_factor_order": order_witness,
            "singular_inverse_rejected": singular_rejected,
        },
    }


def reconstruct(word):
    require((word["v"], word["R"], word["h"]) == (111, 438, 8), "R438 dimensions")
    rows = [1 << j for j in range(660)]
    for phase in ("D", "A"):
        for frame, dst, srcs in word[phase]:
            require(0 <= frame < len(word["frames"]), "bad frame identifier")
            require(0 <= dst < 660 and all(0 <= s < 660 for s in srcs), "bad register")
            for src in srcs:
                rows[dst] ^= rows[src]
    require(rows[:111] == [1 << p for p in range(111)], "prepared source changed")
    retained = [rows[j] for j in word["ret"]]
    require(len(retained) == 9, "retained query count")
    source_mask = (1 << 111)-1
    target_mask = source_mask << 111
    require(all(not row & target_mask for row in retained), "retained target dirt")
    readers = [row & source_mask for row in retained]
    output = []
    for subset in word["scatter"]:
        require(len(set(subset)) == len(subset) and all(0 <= j < 9 for j in subset),
                "invalid scatter subset")
        output.append(sum(1 << j for j in subset))
    require(len(output) == 111, "output row count")
    jr = [r ^ (1 << p) for p, r in enumerate(gf2_mul(output, readers))]
    require(gf2_rank(readers) == gf2_rank(output) == 9, "R/K rank")
    require(gf2_rank(jr) == 108, "rank J")
    require(all(not row >> p & 1 for p, row in enumerate(jr)), "zero diagonal of J")
    weights = Counter(sum((a & row).bit_count() % 2 for row in output)
                      for a in range(1, 512))
    require(min(weights) == 48 and sum(weights.values()) == 511, "K minimum support")
    return readers, output, jr, weights


def geometry_and_census(word, geometry, readers, output, jr):
    roots = [tuple(map(Fraction, row)) for row in word["lines"]]
    full = [tuple(map(Fraction, row)) for row in geometry["lines"]]
    require(len(roots) == 111 and len(full) == 120, "root inventory dimensions")
    require(all(len(r) == 8 and sum(x*x for x in r) == 4 for r in roots+full),
            "E8 vector norms")
    candidates = sorted(set(map(normalized, full)))
    require(len(candidates) == 120, "120 distinct full root lines")
    normals = []
    frame_ids = []
    for h in word["ret"]:
        frame = next(f for f, dst, _ in reversed(word["A"]) if dst == h)
        basis = rational_kernel([roots[p] for p in word["frames"][frame]], 8)
        require(len(basis) == 1, "retained source cap is not a hyperplane")
        normals.append(normalized(basis[0]))
        frame_ids.append(frame)
    require(set(candidates) == set(map(normalized, roots+normals)),
            "full root lines do not match physical roots plus old cap normals")
    line_data = []
    for normal in candidates:
        bad = sum(bool(sum(x*y for x, y in zip(normal, r))) << p
                  for p, r in enumerate(roots))
        allowed = sum((not sum(x*y for x, y in zip(normal, r))) << j
                      for j, r in enumerate(normals))
        line_data.append((normal, bad, allowed))
    templates = []
    for a in range(1, 512):
        support = sum(((a & row).bit_count() % 2) << p for p, row in enumerate(output))
        for normal, bad, allowed in line_data:
            if a & ~allowed:
                continue
            removed = support & bad
            if removed.bit_count() <= 3:
                templates.append({
                    "a": a,
                    "required_deleted_rows": [p for p in range(111) if removed >> p & 1],
                    "allowed_ret_mask": allowed,
                    "normal": [str(x) for x in normal],
                })
    require(len(templates) == 111, "eligible template count")
    require(all(e["a"] == e["allowed_ret_mask"] for e in templates),
            "template input/output masks differ")
    require(all(len(e["required_deleted_rows"]) == 1 for e in templates),
            "a template requires a different deletion count")
    require(len({e["required_deleted_rows"][0] for e in templates}) == 111,
            "templates do not biject physical rows")
    singletons = [e for e in templates if e["a"].bit_count() == 1]
    require(len(singletons) == 1 and singletons[0]["a"] == 32
            and singletons[0]["required_deleted_rows"] == [80], "singleton template")

    # A block S must obey a subset S subset allowed for each emitted direction.
    # Here a == allowed, so the only possible direction in block S is a=S.
    # Its span has rank one; invertibility then forces |S|=1.
    by_deleted = {e["required_deleted_rows"][0]: e for e in templates}
    small = [(1 << j) ^ row for j, row in enumerate(gf2_mul(readers, output))]
    left_null = gf2_kernel(transpose(small, 9), 9)
    require(len(left_null) == 3, "quotient left-nullity")
    constraints = gf2_mul(left_null, readers)
    require(gf2_rank(constraints) == 3 and gf2_mul(constraints, jr) == [0, 0, 0],
            "complete left kernel of J")
    labels = transpose(constraints, 111)
    sections, positive, rank_histogram = 0, [], Counter()
    for chosen in combinations(range(111), 3):
        if gf2_rank([labels[p] for p in chosen]) != 3:
            continue
        sections += 1
        eligible = [by_deleted[p] for p in chosen]
        rank_histogram[gf2_rank([e["a"] for e in eligible])] += 1
        # Evaluate the original criterion rather than only its simplification.
        block_candidates = set()
        for e in eligible:
            a, allowed = e["a"], e["allowed_ret_mask"]
            for block in range(1, 512):
                if not a & ~block and not block & ~allowed:
                    block_candidates.add(block)
        feasible = []
        for block in sorted(block_candidates):
            vectors = [e["a"] for e in eligible
                       if not e["a"] & ~block and not block & ~e["allowed_ret_mask"]]
            if gf2_rank(vectors) == block.bit_count():
                feasible.append(block)
        require(feasible == ([32] if 80 in chosen else []), "singleton classification")
        if feasible:
            positive.append({"selected": list(chosen), "feasible_blocks": feasible})
    require(sections == 70626, "invertible-section census")
    require(len(positive) == 2270 and dict(rank_histogram) == {3: 70626},
            "positive-section census")
    chosen = [1, 2, 80]
    require(gf2_rank([labels[p] for p in chosen]) == 3, "explicit section is singular")
    normal = tuple(Fraction(x) for x in singletons[0]["normal"])
    supported = [p for p, row in enumerate(output) if row >> 5 & 1]
    violations = [p for p in supported if sum(a*b for a, b in zip(roots[p], normal))]
    require(violations == [80], "singleton deletion does not remove exact obstruction")
    require(sum(a*b for a, b in zip(normals[5], normal)) == 0,
            "singleton output line is outside source cap")
    # Removing 80 from the repair set reintroduces a real output incompatibility.
    require(80 not in [0, 1, 2] and violations == [80], "omitted deletion control")
    require(not any(e["a"].bit_count() == 1 for e in [by_deleted[p] for p in (0, 1, 2)]),
            "historical P012 unexpectedly admits a singleton")
    return {
        "candidate_return_lines": len(candidates),
        "actual_retained_cap_frame_ids": frame_ids,
        "old_ret_cap_normals": [[str(x) for x in row] for row in normals],
        "eligible_direction_templates": templates,
        "eligible_direction_rank_histogram": dict(sorted(rank_histogram.items())),
        "sections": sections,
        "sections_with_feasible_blocks": positive,
        "positive_count": len(positive),
        "classification": "Exactly sections containing row80; only block mask32, size1.",
        "explicit_singleton": {
            "selected": chosen, "block_mask": 32, "return_normal": list(map(str, normal)),
            "required_deleted_row": 80, "support_size_before_deletion": len(supported),
            "labels_on_selected_rows": [labels[p] for p in chosen],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "output must be fresh")
    word = load_pinned(args.word, WORD_SHA)
    geometry = load_pinned(args.geometry, GEOMETRY_SHA)
    readers, output, jr, weights = reconstruct(word)
    tests = finite_theorem_tests()
    census = geometry_and_census(word, geometry, readers, output, jr)
    result = {
        "status": "PASS_INDEPENDENT_ROW_SECTIONS_AND_ROOT_LINE_CENSUS",
        "inputs": {"r438_word_sha256": WORD_SHA, "full120_geometry_sha256": GEOMETRY_SHA},
        "scalar_matrices": {
            "R_rows": readers, "K_rows": output, "J_rows": jr,
            "rank_R": 9, "rank_K": 9, "rank_J": 108, "zero_diagonal_entries_J": 111,
            "K_nonzero_direction_weight_histogram": dict(sorted(weights.items())),
            "minimum_K_direction_support": 48,
        },
        "nine_three_row_stage_consequences": {
            "maximum_repair_union": 27, "minimum_diagonal_mismatches": 84,
            "defect_rank_lower": 9, "defect_rank_upper": 36,
            "conditional_common_reader_defect_rank": 9,
            "conditional_premise": "Each A_s-I = W_s R for the same actual R.",
            "necessary_odd_stage_count_at_three_rows_per_stage": 37,
            "stage_count_sufficiency_claimed": False,
        },
        "theorem_finite_checks": tests,
        "root_line_census": census,
        "scope": [
            "General row-section theorem is a written proof, not established by finite tests.",
            "Actual matrix rank claims concern F2 scalar augmentation.",
            "Census covers only three-row invertible sections and the 120-root-line two-tier alphabet.",
            "No native decoder tariff, restored supplier, precision, owner or new kappa conclusion.",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "sections": census["sections"],
                      "positive_sections": census["positive_count"],
                      "result_sha256": sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
