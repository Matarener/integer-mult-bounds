#!/usr/bin/env python3
"""Derive and audit the complete length-22 parity-split domain at n=7.

Independent standard-library implementation of the PR943 singleton
prefix-walk model.  It recomputes the published length-18 and length-20
split lists and budget tables from scratch, reconstructs the `01021323`
calibration, and then applies the same necessary conditions at length 22,
which is the first half of the open question recorded in
research/f7-weight-parity-census-correction (PR #2973).

No census engine, no predecessor package and no external artefact is
imported.  Nothing here enumerates seven-label words: the length-22 result
is arithmetic over the derived necessary conditions, so it is a scoped
reduction, not a census and not an exclusion of any word.

Apache-2.0.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
import sys

MAX_N = 12
MAX_L = 24
MARKER = "PASS_F7_L22_SPLIT_DOMAIN"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def popcount(value: int) -> int:
    return bin(value).count("1")


def half(n: int) -> int:
    """Q = 2^(n-1): the number of masks of each Hamming-weight parity."""
    return 1 << (n - 1)


def prefix_states(word, n: int):
    """q_0 = 0, q_i = q_(i-1) XOR (1 << w_i); the model of PR #943."""
    state = 0
    out = [0]
    for label in word:
        state ^= 1 << label
        out.append(state)
    return out


def parity_classes(states, n: int):
    """Distinct even-weight and odd-weight prefix states, as (E, O)."""
    even, odd = set(), set()
    for state in states:
        (even if popcount(state) % 2 == 0 else odd).add(state)
    return even, odd


def covers(even: set, odd: set, n: int) -> bool:
    """Universality: P + P = F2^n, equivalently every mask is a pair sum."""
    universe = set(range(1 << n))
    if not even or not odd:
        return False
    pool = sorted(even) + sorted(odd)
    return {a ^ b for a in pool for b in pool} == universe


def check_oracle_non_vacuity(n: int, seed_points) -> dict:
    """The universality oracle must reject as well as accept.

    Without this, an always-true `covers` would silently pass every domain and
    every small-domain count. The calibration fixture is not minimal -- four
    of its points can be dropped and the rest still covers -- so a
    single-point-removal control would be wrong. Instead this enumerates all
    2^8 subsets of the fixture's prefix set, compares `covers` against an
    independently written per-mask existence loop, and requires the exact count
    of accepting subsets.
    """
    reference = set(seed_points)
    require(covers(*parity_classes(reference, n), n),
            "the full control set must be accepted")
    require(not covers(*parity_classes(set(), n), n),
            "the empty set must be rejected")
    require(not covers(set(), {1}, n) and not covers({1}, set(), n),
            "a single class alone must be rejected")

    accepted = 0
    for mask in range(1 << len(reference)):
        subset = {point for bit, point in enumerate(sorted(reference))
                  if mask >> bit & 1}
        by_sums = covers(*parity_classes(subset, n), n)
        by_mask = all(any(a ^ b == target for a in subset for b in subset)
                      for target in range(1 << n))
        require(by_sums == by_mask,
                "coverage oracle disagrees with the per-mask reference at "
                + repr(sorted(subset)))
        accepted += by_sums
    require(accepted == 7,
            "exactly 7 subsets of the control set may cover, got " + str(accepted))
    return {"subsets_tested": 1 << len(reference), "subsets_accepted": accepted,
            "independent_reference_agrees": True}


def within_pairs(items):
    """Distinct-sum support of the unordered distinct-element pairs of a class."""
    support = set()
    for i, a in enumerate(sorted(items)):
        for b in sorted(items)[i + 1:]:
            support.add(a ^ b)
    return support


def collision_excess(classes):
    """Sum over classes of C(|class|,2) - |distinct pair sums|, per class."""
    total = 0
    for items in classes:
        total += len(items) * (len(items) - 1) // 2 - len(within_pairs(items))
    return total


def identity_need(s: int, t: int, n: int) -> int:
    """ceil((s*t - Q) / 2): the pair-identity lower bound on sum(A_x*B_x)."""
    excess = s * t - half(n)
    return -((-excess) // 2) if excess > 0 else 0


def even_budget(s: int, t: int, n: int) -> int:
    """B0 = C(s,2) + C(t,2) - (Q-1): the even-mask collision excess budget."""
    return s * (s - 1) // 2 + t * (t - 1) // 2 - (half(n) - 1)


def split_row(s: int, t: int, n: int, length: int) -> dict:
    """Evaluate every derived necessary condition at the split (s, t).

    The identity's upper bound `B0 + a*b` is attained at `a = b = B0/2`, and is
    taken to be `B0` itself when `B0 <= 0`, where no feasible `a, b` pair
    exists. That makes the identity imply the even budget: `need >= 0`, so
    `B0 <= 0` never passes. `check_condition_independence` verifies this over
    the full enumeration range instead of assuming it.
    """
    q = half(n)
    budget = even_budget(s, t, n)
    need = identity_need(s, t, n)
    best = budget + budget * budget // 4 if budget > 0 else budget
    return {
        "split": [s, t],
        "points": s + t,
        "revisits_forced": length - (s + t),
        "even_budget": budget,
        "identity_need": need,
        "identity_max_upper": best,
        "odd_pairs": s * t,
        "odd_masks_needed": q,
        "passes_time_bound": s <= length // 2 and t <= length // 2,
        "passes_odd_budget": s * t >= q,
        "passes_even_budget": budget >= 0,
        "passes_identity": best >= need,
        "self_avoiding_forced": s + t == length,
    }


def admissible_splits(n: int, length: int):
    """All splits with s >= t >= 1 that no derived condition excludes.

    The enumeration range is deliberately wider than `L/2` so that the time
    bound is exercised as a condition rather than hidden in the loop bounds.
    """
    rows = []
    for t in range(1, length):
        for s in range(t, length):
            row = split_row(s, t, n, length)
            keep = (row["passes_time_bound"] and row["passes_odd_budget"]
                    and row["passes_even_budget"] and row["passes_identity"])
            if keep:
                rows.append(row)
    rows.sort(key=lambda r: (-r["points"], -r["split"][0]))
    return rows


def check_condition_independence(n: int, lengths) -> dict:
    """Which derived conditions are load-bearing, measured not assumed.

    Each condition is removed in turn and the resulting domain is compared with
    the full one, over the whole enumeration range. A condition that changes
    nothing here is reported as redundant rather than presented as a filter.
    """
    names = ("passes_time_bound", "passes_odd_budget",
             "passes_even_budget", "passes_identity")
    report = {}
    for length in lengths:
        rows = [split_row(s, t, n, length)
                for t in range(1, length) for s in range(t, length)]
        full = [row["split"] for row in rows if all(row[name] for name in names)]
        redundant = []
        for drop in names:
            kept = [row["split"] for row in rows
                    if all(row[name] for name in names if name != drop)]
            if len(kept) == len(full):
                redundant.append(drop)
        report[str(length)] = {
            "domain_size": len(full),
            "load_bearing": sorted(set(names) - set(redundant)),
            "redundant": sorted(redundant)}
    return report


def check_identity_need_formula() -> dict:
    """The ceiling in `need = ceil((s*t - Q)/2)` must be the real ceiling.

    No length-22 split is decided by rounding, so a floor-for-ceiling mutant
    survives the domain comparison. This checks the arithmetic directly,
    including the odd remainders that make floor and ceiling differ.
    """
    cases = [(7, 11, 7), (7, 9, 9), (7, 10, 8), (7, 11, 11), (7, 10, 7),
             (3, 1, 5), (4, 3, 3), (5, 4, 4)]
    odd = []
    for n, s, t in cases:
        excess = s * t - half(n)
        expected = -((-excess) // 2) if excess > 0 else 0
        require(identity_need(s, t, n) == expected,
                "identity_need wrong at n=%d s=%d t=%d" % (n, s, t))
        require(identity_need(s, t, n) >= excess / 2,
                "identity_need must be at least the real value")
        if excess > 0 and excess % 2:
            odd.append([n, s, t, excess, excess // 2, identity_need(s, t, n)])
            require(identity_need(s, t, n) == excess // 2 + 1,
                    "odd remainder must round up at %d/%d" % (s, t))
    require(odd, "no odd remainder case exercised the ceiling")
    return {"cases": len(cases), "odd_remainder_cases": odd}


def check_identity_tightness(n: int, lengths) -> dict:
    """Measure how hard each admitted split is, and what the a*b term buys.

    Reported rather than assumed: the minimal slack `B0 + a*b - need` over the
    admitted splits bounds how far `need` or the ceiling could be perturbed
    before the domain changes, and the `ab_decides` list records the splits
    where the `a*b` refinement rather than `B0` alone decides the verdict.
    """
    report = {}
    for length in lengths:
        rows = [split_row(s, t, n, length)
                for t in range(1, length) for s in range(t, length)]
        eligible = [r for r in rows if r["passes_time_bound"]
                    and r["passes_odd_budget"] and r["passes_even_budget"]]
        admitted = [r for r in eligible if r["passes_identity"]]
        decisive = [r["split"] for r in eligible
                    if (r["even_budget"] >= r["identity_need"])
                    != (r["identity_max_upper"] >= r["identity_need"])]
        report[str(length)] = {
            "admitted": len(admitted),
            "excluded_by_identity": [r["split"] for r in eligible
                                     if not r["passes_identity"]],
            "min_identity_slack": min(r["identity_max_upper"] - r["identity_need"]
                                      for r in admitted),
            "min_even_budget_slack": min(r["even_budget"] for r in admitted),
            "ab_term_decides_at": decisive}
    return report


def even_count_vectors(labels: int, length: int):
    """Positive even multiplicities summing to `length`."""
    if length < 2 * labels or length % 2:
        return
    extra = length // 2 - labels
    for cuts in product(range(extra + 1), repeat=labels - 1):
        point = extra - sum(cuts)
        if point < 0:
            continue
        yield [2 * (1 + c) for c in cuts] + [2 * (1 + point)]


def arrangements(counts, labels: int, length: int):
    """Every word with the given multiplicity vector, in first-occurrence order."""
    if length == 0:
        yield ()
        return
    for label in range(labels):
        if counts[label]:
            counts[label] -= 1
            for rest in arrangements(counts, labels, length - 1):
                yield (label,) + rest
            counts[label] += 1


def is_canonical(word) -> bool:
    """Restricted growth form: each new label is the next unused one."""
    seen = 0
    for label in word:
        if label > seen:
            return False
        seen = max(seen, label + 1)
    return word[0] == 0


def check_calibration_counterexample(n: int, word) -> dict:
    """Independent reconstruction of the PR #2973 `01021323` fixture."""
    states = prefix_states(word, n)
    distinct = set(states)
    even, odd = parity_classes(distinct, n)
    size = len(distinct)
    weight_split = [len(even), len(odd)]
    bit0_even = {s for s in distinct if s & 1 == 0}
    bit0_odd = {s for s in distinct if s & 1 == 1}
    balanced_budget = even_budget(max(weight_split), min(weight_split), n)
    bit0_budget = even_budget(len(bit0_even), len(bit0_odd), n)
    excess = collision_excess([bit0_even, bit0_odd])
    require(size == 8 and weight_split == [4, 4], "fixture split changed")
    require(sorted(distinct) == [0, 1, 2, 3, 4, 6, 8, 12], "prefix set")
    require(covers(even, odd, n), "fixture is not universal")
    require(excess == 8, "bit-0 collision excess must be 8, got " + str(excess))
    require(balanced_budget == 5 and excess > balanced_budget,
            "the substituted balanced budget must reject the fixture")
    require(bit0_budget == 9 and excess <= bit0_budget,
            "the actual-size bit-0 budget must admit the fixture")
    require(len(bit0_even) == 6 and len(bit0_odd) == 2, "bit-0 split (6,2)")
    return {
        "word": "".join(str(x) for x in word),
        "prefix_states": sorted(set(states)),
        "weight_split": weight_split,
        "bit0_split": [len(bit0_even), len(bit0_odd)],
        "within_even_excess": excess,
        "substituted_balanced_budget": balanced_budget,
        "actual_bit0_budget": bit0_budget,
        "old_prune_rejects": True,
        "actual_bit0_budget_admits": True,
    }


def check_conditions_are_not_vacuous(n: int, length: int) -> dict:
    """The conditions must also reject, not only admit.

    The necessity audit inside `enumerate_restored` is one-sided: on correct
    code it can never fire, so deleting it changes nothing and it is not a
    discriminating check on its own. This is the converse. It enumerates the
    non-universal restored words and requires that the four conditions reject a
    substantial share of them, so an always-true condition set fails.
    """
    names = ("passes_time_bound", "passes_odd_budget",
             "passes_even_budget", "passes_identity")
    non_universal = rejected = 0
    for counts in even_count_vectors(n, length):
        for word in arrangements(list(counts), n, length):
            even, odd = parity_classes(set(prefix_states(word, n)), n)
            if covers(even, odd, n):
                continue
            non_universal += 1
            row = split_row(max(len(even), len(odd)),
                            min(len(even), len(odd)), n, length)
            rejected += not all(row[name] for name in names)
    require(non_universal > 0, "no non-universal words to test against")
    require(rejected >= non_universal // 4,
            "the conditions reject too few non-universal words: %d of %d"
            % (rejected, non_universal))
    return {"n": n, "length": length, "non_universal_words": non_universal,
            "rejected_by_conditions": rejected}


def check_input_rejection() -> dict:
    """The boundary guards must actually reject, not merely be present."""
    for args, label in (((3, 7), "odd length"), ((MAX_N + 1, 8), "n over bound"),
                        ((3, MAX_L + 2), "length over bound")):
        try:
            enumerate_restored(*args)
        except SystemExit:
            continue
        raise SystemExit("FAIL: guard did not reject " + label)
    return {"odd_length_rejected": True, "dimension_bounds_rejected": True}


def enumerate_restored(n: int, length: int) -> dict:
    """Every restored word over n labels, with a universality audit."""
    require(n <= MAX_N and length <= MAX_L, "enumeration domain too large")
    require(length % 2 == 0, "a restored word has even length")
    restored = universal = canonical = 0
    observed_points, observed_splits = set(), set()
    histogram = {}
    for counts in even_count_vectors(n, length):
        for word in arrangements(list(counts), n, length):
            restored += 1
            states = prefix_states(word, n)
            distinct = set(states)
            even, odd = parity_classes(distinct, n)
            require(len(even) <= length // 2 and len(odd) <= length // 2,
                    "time-parity bound violated at " + str(word))
            require(len(distinct) <= length, "|P| exceeds L at " + str(word))
            if not covers(even, odd, n):
                continue
            universal += 1
            s, t = len(even), len(odd)
            row = split_row(max(s, t), min(s, t), n, length)
            for key in ("passes_time_bound", "passes_odd_budget",
                        "passes_even_budget", "passes_identity"):
                require(row[key], "necessary condition rejected a real cover: "
                        + key + " at " + str(word))
            observed_points.add(len(distinct))
            observed_splits.add((max(s, t), min(s, t)))
            key = "%d,%d" % (s, t)
            histogram[key] = histogram.get(key, 0) + 1
            if is_canonical(word):
                canonical += 1
    return {
        "n": n, "length": length, "restored_words": restored,
        "universal_words": universal, "canonical_universal_words": canonical,
        "distinct_prefix_sizes": sorted(observed_points),
        "universal_splits": sorted(observed_splits, reverse=True),
        "split_histogram": dict(sorted(histogram.items())),
    }


def check_padding_lemma(n: int, length: int, steps: int) -> dict:
    """Appending (j,j) pairs preserves restoration and prefix coverage."""
    checked = 0
    for counts in even_count_vectors(n, length):
        for word in arrangements(list(counts), n, length):
            states = prefix_states(word, n)
            even, odd = parity_classes(set(states), n)
            if not covers(even, odd, n):
                continue
            padded, position = list(word), 0
            for _ in range(steps):
                padded += [position % n, position % n]
                position += 1
            new_states = set(prefix_states(padded, n))
            even, odd = parity_classes(new_states, n)
            require(new_states >= set(states), "padding must keep the prefix set")
            require(covers(even, odd, n), "padding must preserve coverage")
            require(prefix_states(padded, n)[-1] == 0, "padding must restore")
            checked += 1
    return {"n": n, "length": length, "pad_steps": steps,
            "universal_words_checked": checked}


def check_published_small_domains(census) -> None:
    """Counts and split histograms as independently recorded by
    research/f7-weight-parity-census-correction/math/check_math.py."""
    published = {
        (3, 6): (90, 60, 10,
                 {"2,3": 18, "3,2": 18, "3,3": 24}),
        (3, 8): (1260, 1092, 182,
                 {"2,3": 252, "2,4": 12, "3,2": 252, "3,3": 408,
                  "3,4": 72, "4,2": 12, "4,3": 72, "4,4": 12}),
        (4, 8): (2520, 624, 26,
                 {"3,4": 48, "4,3": 48, "4,4": 528}),
    }
    for row in census:
        key = (row["n"], row["length"])
        if key not in published:
            continue
        observed = (row["restored_words"], row["universal_words"],
                    row["canonical_universal_words"], row["split_histogram"])
        require(observed == published[key],
                "small-domain mismatch at " + str(key) + ": " + repr(observed))


def check_published_split_domains(splits) -> None:
    """The length-18 and length-20 domains and budgets, recomputed."""
    require([[r["split"] for r in splits[18]]] == [[[9, 9]]],
            "length-18 domain must be the single split (9,9)")
    require([[r["split"] for r in splits[20]]]
            == [[[10, 10], [10, 9], [10, 8], [9, 9], [10, 7]]],
            "length-20 domain must reproduce the five published representatives")
    published_budgets = {"(10,10)": [27, 36], "(10,9)": [18, 26],
                         "(10,8)": [10, 16], "(9,9)": [9, 17],
                         "(10,7)": [3, 6]}
    for row in splits[20]:
        key = "(%d,%d)" % tuple(row["split"])
        require(key in published_budgets, "unpublished length-20 split " + key)
        require([row["even_budget"], row["odd_pairs"] - half(7)]
                == published_budgets[key],
                "length-20 budget mismatch at " + key)
    # The identity is what excludes (9,8): admitted without it, excluded with.
    weak = [r["split"] for r in
            [split_row(s, t, 7, 20) for t in range(1, 20) for s in range(t, 20)]
            if r["passes_time_bound"] and r["passes_odd_budget"]
            and r["passes_even_budget"]]
    require([9, 8] in weak and [9, 8] not in [r["split"] for r in splits[20]],
            "the identity must be the condition excluding (9,8) at length 20")


def check_cardinality_floor() -> dict:
    """The counting conditions set a covering-cardinality floor of 17 at n=7.

    The identity then narrows the 17-point survivors to exactly the two splits
    that PR #2773 and PR #2870 exclude set-level.
    """
    for size in range(1, 24):
        survivors = [tuple(row["split"]) for row in
                     [split_row(s, size - s, 7, 22)
                      for s in range((size + 1) // 2, size)]
                     if row["passes_odd_budget"] and row["passes_even_budget"]
                     and row["passes_identity"]]
        if survivors:
            require(size == 17, "the covering-cardinality floor must be 17")
            require(sorted(survivors) == [(10, 7), (11, 6)],
                    "17-point survivors must be exactly (10,7) and (11,6)")
            return {"floor": size, "splits": [list(x) for x in survivors]}
    raise SystemExit("FAIL: no covering cardinality found below 23")


def build_receipt(fixture, oracle, guards, not_vacuous, census, padding,
                  splits, domain, reporting):
    """The reconstructed receipt, as printed by --emit."""
    receipt = {
        "marker": MARKER,
        "model": "PR943 singleton prefix-walk, first-occurrence labels",
        "calibration_fixture": fixture,
        "oracle_non_vacuity": oracle,
        "input_guards": guards,
        "conditions_not_vacuous": not_vacuous,
        "small_domain_census": census,
        "padding_lemma": padding,
        "split_domains": {
            str(length): [{"split": r["split"], "points": r["points"],
                           "revisits_forced": r["revisits_forced"],
                           "even_budget": r["even_budget"],
                           "identity_need": r["identity_need"],
                           "identity_max_upper": r["identity_max_upper"],
                           "odd_pairs": r["odd_pairs"]}
                          for r in rows]
            for length, rows in splits.items()},
        "length_20_published_budgets": {
            "(10,10)": [27, 36], "(10,9)": [18, 26], "(10,8)": [10, 16],
            "(9,9)": [9, 17], "(10,7)": [3, 6]},
        "length_22_self_contained": domain["self_contained"],
        "length_22_after_imported_17_point_exclusion": domain["after_import"],
        "length_22_revisits_forced": {str(tuple(r["split"])):
                                     r["revisits_forced"] for r in splits[22]},
        "covering_cardinality_floor_n7": domain["cardinality"]["floor"],
        "covering_cardinality_floor_splits": domain["cardinality"]["splits"],
        "length_22_simple_cycle_admissible": domain["simple_only"],
        "condition_independence_n7": reporting["independence"],
        "identity_tightness_n7": reporting["tightness"],
        "identity_need_formula": reporting["need_formula"],
        "excluded_at_length_22": {
            "time_bound_s_t_le_11": [[13, 5], [12, 6]],
            "pair_identity": [[9, 8]],
            "imported_17_point_set_level": [[11, 6], [10, 7]]},
        "claims": {
            "length_22_no_exclusion": "no length-22 split is excluded by the "
                "derived conditions; this is not a census and not f(7)",
            "imported": "the 17-point set-level exclusion is a standing claim "
                "of PR #2773 and PR #2870 and is not re-proved here"},
    }
    return receipt


def check_length_22_domain(splits) -> dict:
    """The length-22 domain, its named exclusions and its imported reduction."""
    self_contained = [r["split"] for r in splits[22]]
    seventeen = {(11, 6), (10, 7)}
    after_import = [r["split"] for r in splits[22]
                    if tuple(r["split"]) not in seventeen]
    require(len(self_contained) == 11 and len(after_import) == 9,
            "length-22 domain size changed")
    require([13, 5] not in self_contained and [12, 6] not in self_contained,
            "the time bound must remove (13,5) and (12,6)")
    cardinality = check_cardinality_floor()
    # Self-avoidance is valid only where the split forces |P| = L.
    simple_only = [r["split"] for r in splits[22] if r["self_avoiding_forced"]]
    require(simple_only == [[11, 11]],
            "only (11,11) may use a simple-cycle restriction at length 22")
    return {"self_contained": self_contained, "after_import": after_import,
            "cardinality": cardinality, "simple_only": simple_only}


def check_identity_reporting() -> dict:
    """Condition independence, the ceiling formula, and measured tightness."""
    independence = check_condition_independence(7, (18, 20, 22))
    require(independence["22"]["redundant"] == ["passes_even_budget"],
            "at length 22 only the even budget may be redundant")
    for name in ("passes_identity", "passes_time_bound", "passes_odd_budget"):
        require(name in independence["22"]["load_bearing"],
                name + " must be load-bearing at length 22")
    need_formula = check_identity_need_formula()
    tightness = check_identity_tightness(7, (18, 20, 22, 24))
    for length in ("18", "20", "22", "24"):
        require(tightness[length]["excluded_by_identity"] == [[9, 8]],
                "the identity must exclude exactly (9,8) at length " + length)
        require(tightness[length]["ab_term_decides_at"] == [],
                "the a*b term must not decide any eligible split at " + length)
    require(tightness["22"]["min_identity_slack"] == 2,
            "the tightest admitted length-22 split must have slack 2")
    return {"independence": independence, "need_formula": need_formula,
            "tightness": tightness}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true",
                        help="print the reconstructed receipt as JSON")
    args = parser.parse_args()

    fixture = check_calibration_counterexample(4, (0, 1, 0, 2, 1, 3, 2, 3))
    oracle = check_oracle_non_vacuity(4, fixture["prefix_states"])
    guards = check_input_rejection()
    not_vacuous = check_conditions_are_not_vacuous(3, 8)

    domains = [(3, 4), (3, 6), (3, 8), (4, 6), (4, 8), (4, 10),
               (5, 10), (5, 12)]
    census = [enumerate_restored(n, length) for n, length in domains]

    check_published_small_domains(census)

    padding = [check_padding_lemma(3, 6, 2), check_padding_lemma(4, 8, 1)]

    splits = {length: admissible_splits(7, length)
              for length in (18, 20, 22)}
    check_published_split_domains(splits)

    domain = check_length_22_domain(splits)
    reporting = check_identity_reporting()

    receipt = build_receipt(
        fixture, oracle, guards, not_vacuous, census, padding, splits,
        domain, reporting)

    if args.emit:
        print(json.dumps(receipt, indent=1, sort_keys=True))
    print("%s length22_self_contained=%d after_17pt_import=%d "
          "f7_untouched" % (MARKER, len(domain["self_contained"]),
                             len(domain["after_import"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())