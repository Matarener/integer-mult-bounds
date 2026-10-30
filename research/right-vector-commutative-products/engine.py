#!/usr/bin/env python3
"""Exact independent paid-factor BFS on GL_2(F_2)^3.

Credit: Nick Petalas, PRs #4276/#4265/#4243; Wentao Li, PR #4099's
right-vector alphabet/column bound; the retained PR #2513 lineage.  This
implementation was prepared by ToikY with substantial OpenAI Codex assistance.
It imports no predecessor verifier and uses no projective pivot criterion.

Only the invertible target domain is searched.  Each component of a word is
a product of square matrices over F_2.  Invertibility of the final component
forces every component factor to be invertible, so filtering singular paid
factors cannot remove a word attaining a target in this domain.  Free matrices
are constant triples from GL_2(F_2).  BFS starts at all six free endpoints;
the certificate checks every paid edge and every zero-cost free edge as well
as every attaining word.  Thus the distance certificate also directly covers
free maps anywhere in a word.

The two original target roles are arbitrary inputs, not borrowed helpers.
No scratch/helper is allocated.  All six output bits are checked against the
specified target map; no role is silently treated as disposable or restored.
"""

from collections import Counter, deque
import hashlib
import json
import sys


IDENTITY = 9
CANONICAL = (9, 14, 7)  # I, [[0,1],[1,1]], [[1,1],[1,0]].


def require(condition, message):
    if not condition:
        raise ValueError(message)


def entries(code):
    """Row-major entries, with entry i represented by bit i."""
    return tuple((code >> index) & 1 for index in range(4))


def pack(values):
    return sum((value & 1) << index for index, value in enumerate(values))


def multiply_component(left, right):
    a = entries(left)
    b = entries(right)
    return pack(
        sum(a[2 * row + mid] * b[2 * mid + col] for mid in range(2)) % 2
        for row in range(2)
        for col in range(2)
    )


def invertible(code):
    a, b, c, d = entries(code)
    return (a * d) ^ (b * c) == 1


def literal_factor(descriptor):
    """Descriptor is [u0,u1,y0,y1], u entries are three-bit ring values."""
    u0, u1, y0, y1 = descriptor
    require(0 <= u0 < 8 and 0 <= u1 < 8, "ring coefficient outside F2^3")
    require(y0 in (0, 1) and y1 in (0, 1), "right vector outside F2^2")
    return tuple(
        pack((1 ^ (((u0 >> j) & 1) * y0),
              ((u0 >> j) & 1) * y1,
              ((u1 >> j) & 1) * y0,
              1 ^ (((u1 >> j) & 1) * y1)))
        for j in range(3)
    )


def factor_catalogue():
    representatives = {}
    admitted_descriptors = 0
    for u0 in range(8):
        for u1 in range(8):
            for y0 in range(2):
                for y1 in range(2):
                    descriptor = (u0, u1, y0, y1)
                    state = literal_factor(descriptor)
                    if all(invertible(component) for component in state):
                        admitted_descriptors += 1
                        representatives.setdefault(state, descriptor)
    return representatives, admitted_descriptors


def apply_free(free_code, roles):
    """Direct input interpreter, independent of the matrix product table."""
    a, b, c, d = entries(free_code)
    first, second = roles
    return ((first if a else 0) ^ (second if b else 0),
            (first if c else 0) ^ (second if d else 0))


def apply_paid(descriptor, roles):
    u0, u1, y0, y1 = descriptor
    first, second = roles
    readout = (first if y0 else 0) ^ (second if y1 else 0)
    return first ^ (u0 & readout), second ^ (u1 & readout)


def apply_target(state, roles):
    first, second = roles
    out_first = out_second = 0
    for j, code in enumerate(state):
        a, b, c, d = entries(code)
        x, y = (first >> j) & 1, (second >> j) & 1
        out_first |= ((a * x) ^ (b * y)) << j
        out_second |= ((c * x) ^ (d * y)) << j
    return out_first, out_second


def evaluate_word(free_code, descriptors, roles):
    result = apply_free(free_code, roles)
    for descriptor in descriptors:
        result = apply_paid(descriptor, result)
    return result


def word_agrees(state, free_code, descriptors):
    return all(
        evaluate_word(free_code, descriptors, (first, second))
        == apply_target(state, (first, second))
        for first in range(8)
        for second in range(8)
    )


def delta_by_columns(state, free_codes):
    """Rank of the literal six-by-two binary matrix (M T-I)|K^2."""
    ranks = []
    for free in free_codes:
        t00, t01, t10, t11 = entries(free)
        columns = [0, 0]
        for component, code in enumerate(state):
            a, b, c, d = entries(code)
            # Deliberately do not call multiply_component or use its table.
            m00 = (a * t00) ^ (b * t10) ^ 1
            m01 = (a * t01) ^ (b * t11)
            m10 = (c * t00) ^ (d * t10)
            m11 = (c * t01) ^ (d * t11) ^ 1
            columns[0] |= (m00 << (2 * component)) | (m10 << (2 * component + 1))
            columns[1] |= (m01 << (2 * component)) | (m11 << (2 * component + 1))
        if columns == [0, 0]:
            rank = 0
        elif 0 in columns or columns[0] == columns[1]:
            rank = 1
        else:
            rank = 2
        ranks.append(rank)
    return min(ranks), ranks


def recover_word(state, predecessors, catalogue):
    backwards = []
    while predecessors[state] is not None:
        previous, factor = predecessors[state]
        backwards.append(catalogue[factor])
        state = previous
    return state[0], tuple(reversed(backwards))


def negative_controls(state, free_code, word, free_codes):
    require(word_agrees(state, free_code, word), "positive word rejected")
    dropped = []
    for omitted in range(len(word)):
        damaged = word[:omitted] + word[omitted + 1:]
        require(not word_agrees(state, free_code, damaged), "dropped factor undetected")
        dropped.append({"omitted_step": omitted, "rejected": True})

    wrong_component = None
    for step, descriptor in enumerate(word):
        for first, second in ((0, 1), (0, 2), (1, 2)):
            changed = list(descriptor)
            for coordinate in (0, 1):
                value = changed[coordinate]
                if ((value >> first) ^ (value >> second)) & 1:
                    changed[coordinate] ^= (1 << first) | (1 << second)
            if tuple(changed) == descriptor:
                continue
            candidate = word[:step] + (tuple(changed),) + word[step + 1:]
            require(all(invertible(c) for c in literal_factor(changed)),
                    "component permutation damaged factor admissibility")
            if not word_agrees(state, free_code, candidate):
                wrong_component = {"step": step, "swapped_components": [first, second],
                                   "replacement_descriptor": changed, "rejected": True}
                break
        if wrong_component is not None:
            break
    require(wrong_component is not None, "no discriminating component mutant")

    altered_free = next(code for code in free_codes if code != free_code)
    require(not word_agrees(state, altered_free, word), "wrong free chart undetected")
    return {"positive_word_accepted": True, "dropped_factors": dropped,
            "wrong_component": wrong_component,
            "wrong_free_chart": {"replacement_free_code": altered_free, "rejected": True}}


def run():
    free_codes = tuple(code for code in range(16) if invertible(code))
    require(len(free_codes) == 6, "GL2(F2) cardinality")
    component_table = tuple(tuple(multiply_component(a, b) for b in range(16))
                            for a in range(16))

    def multiply(left, right):
        return tuple(component_table[a][b] for a, b in zip(left, right))

    catalogue, admitted_descriptors = factor_catalogue()
    factors = tuple(sorted(catalogue))
    free_states = tuple((code,) * 3 for code in free_codes)
    states = tuple((a, b, c) for a in free_codes for b in free_codes for c in free_codes)
    state_set = set(states)
    require(len(states) == 216, "invertible target domain cardinality")

    distances = {state: 0 for state in free_states}
    predecessors = {state: None for state in free_states}
    pending = deque(free_states)
    while pending:
        previous = pending.popleft()
        for factor in factors:
            state = multiply(factor, previous)
            require(state in state_set, "invertible paid transition left target domain")
            if state not in distances:
                distances[state] = distances[previous] + 1
                predecessors[state] = (previous, factor)
                pending.append(state)
    require(set(distances) == state_set, "BFS did not cover the entire invertible domain")

    paid_edges = free_edges = conjugations = 0
    for state in states:
        require((distances[state] == 0) == (state in free_states), "wrong zero-cost set")
        for factor in factors:
            require(distances[multiply(factor, state)] <= distances[state] + 1,
                    "paid-edge distance certificate failed")
            paid_edges += 1
        for free in free_states:
            require(distances[multiply(free, state)] == distances[state],
                    "zero-cost free-edge distance certificate failed")
            free_edges += 1
    for free in free_states:
        inverse = next(other for other in free_states
                       if multiply(free, other) == (IDENTITY,) * 3)
        for factor in factors:
            require(multiply(multiply(free, factor), inverse) in catalogue,
                    "paid alphabet not closed under free conjugation")
            conjugations += 1

    records = []
    for state in states:
        free_code, word = recover_word(state, predecessors, catalogue)
        require(len(word) == distances[state], "predecessor word length mismatch")
        matrix_replay = (free_code,) * 3
        for descriptor in word:
            matrix_replay = multiply(literal_factor(descriptor), matrix_replay)
        require(matrix_replay == state, "predecessor matrix replay failed")
        require(word_agrees(state, free_code, word), "arbitrary-input word replay failed")
        delta, ranks = delta_by_columns(state, free_codes)
        require(delta <= distances[state], "delta lower bound violated")
        records.append({"state": list(state), "components": [list(entries(code)) for code in state],
                        "cost": distances[state], "delta": delta,
                        "delta_ranks_in_free_order": ranks, "free_code": free_code,
                        "word_in_execution_order": [list(d) for d in word]})

    canonical_record = next(record for record in records if tuple(record["state"]) == CANONICAL)
    require(canonical_record["cost"] == 3 and canonical_record["delta"] == 2,
            "canonical target is not cost3/delta2")
    canonical_word = tuple(tuple(d) for d in canonical_record["word_in_execution_order"])
    controls = negative_controls(CANONICAL, canonical_record["free_code"],
                                 canonical_word, free_codes)
    canonical_bytes = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("ascii")
    joint_histogram = Counter((row["cost"], row["delta"]) for row in records)
    return {
        "schema_version": 1,
        "claim_type": "complete_finite_invertible_target_metric",
        "field": "F2", "ring": "F2^3", "roles": 2,
        "scratch_roles": 0, "borrowed_helper_roles": 0,
        "component_encoding": "row-major bit i is matrix entry i; triple order is ring component order",
        "factor_encoding": "[u0,u1,y0,y1]; u0/u1 are three-bit ring values; y0/y1 are F2",
        "word_convention": "apply free_code first, then left-apply listed factors in execution order",
        "free_codes": list(free_codes),
        "paid_descriptor_domain": 256,
        "invertible_paid_descriptors": admitted_descriptors,
        "distinct_invertible_paid_factors": len(factors),
        "paid_factors": [{"state": list(f), "descriptor": list(catalogue[f])} for f in factors],
        "target_count": len(states),
        "cost_delta_histogram": [{"cost": cost, "delta": delta, "count": count}
                                 for (cost, delta), count in sorted(joint_histogram.items())],
        "records": records,
        "records_sha256": hashlib.sha256(canonical_bytes).hexdigest(),
        "canonical_target": canonical_record,
        "checks": {"all_paid_edges": paid_edges, "all_free_edges": free_edges,
                   "free_conjugations": conjugations, "attaining_matrix_words": len(records),
                   "attaining_word_arbitrary_inputs": 64 * len(records),
                   "canonical_arbitrary_inputs": 64, "delta_endpoints_per_target": len(free_codes)},
        "controls": controls,
        "scope": "Formal paid-factor alphabet only; no physical caller, supplier, precision, stock, or kappa claim.",
    }


if __name__ == "__main__":
    require(len(sys.argv) == 1, "engine CLI takes no arguments")
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
