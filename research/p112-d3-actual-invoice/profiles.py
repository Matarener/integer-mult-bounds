"""Exact profile/arithmetic verifier by conorholds.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
This standalone checker uses only Python's standard library and integers.
It checks finite weight-profile exhaustion and invoice arithmetic. It does
not formalize the E8 geometry, actual correction-group proofs, or the full
written d3 theorem. Its intrinsic geometric boundary is a declared INPUT,
kept separate from the newly enumerated arithmetic. No source is executed.
"""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations_with_replacement
import json


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def profile(text):
    return tuple(int(character) for character in text)


def text(weights):
    return "".join(str(weight) for weight in weights)


def profiles(length, weight_limit, total_limit):
    for ascending in combinations_with_replacement(range(1, weight_limit + 1), length):
        if sum(ascending) <= total_limit:
            yield tuple(reversed(ascending))


# RETAINED INTRINSIC INPUTS, not results established by this program.
# PR3689 head3193d1ea9a4fc5d178570a61e6019454b53c1db9:
# p112-six-seven-supplement/{D2,RAW-SHAPE,RIGIDITY,D2-PROFILE}.md.
# The four/five-piece lists are NECESSARY boundaries, not existence claims.
INTRINSIC = {
    "four_piece_d2_cost_at_most23": {"7771", "7772"},
    "five_piece_d2_cost_at_most24": {"77711", "77721", "77541", "77631"},
    "five_piece_d3_all_weights_at_most6_impossible": True,
    "six_piece_d3_cost_at_most31_all_weights_at_most6_impossible": True,
    "rank1_or_rank2_piece_uncorrected": True,
    "support_capacities_at_ranks1_through7": (1, 2, 4, 8, 12, 20, 36),
}
MINIMUM_BOUNDARY = {
    2: {29: {"77771"}, 30: {"77772"}},
    3: {30: {"777711"}, 31: {"777541", "777631", "777721"}},
}
# Keys are (quotient dimension t, descending minimum T profile, eta).
EXPECTED_ACTUAL = {
    (2, "77771", 2): {"8771"},
    (2, "77771", 3): {"9771", "8871"},
    (2, "77772", 2): {"8772"},
    (3, "777711", 2): {"87711", "77721"},
    (3, "777711", 3): {"97711", "88711", "87721", "77722"},
    (3, "777541", 2): {"87541", "77641", "77551"},
    (3, "777631", 2): {"87631", "77731", "77641"},
    (3, "777721", 2): {"87721", "77731", "77722"},
}
EXPECTED_C9 = {
    key: ((0, 1) if key in {(2, "77771", 2), (3, "777711", 2)} else (0,))
    for key in EXPECTED_ACTUAL
}
CAPACITIES = dict(enumerate(INTRINSIC["support_capacities_at_ranks1_through7"], 1))


def derive_minimum_boundary():
    result = {}
    examined = 0
    for t, by_cost in MINIMUM_BOUNDARY.items():
        result[t] = {}
        length = t + 3
        retained = INTRINSIC[
            "four_piece_d2_cost_at_most23" if t == 2
            else "five_piece_d2_cost_at_most24"
        ]
        for cost, expected in by_cost.items():
            survivors = set()
            for candidate in profiles(length, 7, cost):
                if sum(candidate) != cost:
                    continue
                examined += 1
                # Excluding no-seven candidates uses the declared intrinsic input.
                if candidate[0] != 7:
                    continue
                remainder = list(candidate)
                remainder.remove(7)
                if text(remainder) in retained:
                    survivors.add(text(candidate))
            require(survivors == expected,
                    f"minimum profile mismatch t{t} cost{cost}: {sorted(survivors)}")
            result[t][cost] = sorted(survivors)
    return {"examined_exact_cost_profiles": examined, "derived": result}


def cases():
    result = []
    for t, by_cost in MINIMUM_BOUNDARY.items():
        for cost, minima in by_cost.items():
            for minimum in sorted(minima):
                # r=1 and the inherited eta=r exclusion give eta>=2.
                # The raw ledger cost(T)+40+eta+c9<=70+t and c9>=0
                # supplies the upper endpoint; it is not an assumed eta list.
                eta_max = 70 + t - 40 - cost
                for eta in range(2, eta_max + 1):
                    # r=1; six outside members, each at least weight eight.
                    inside_sum = cost - 8 + eta
                    if inside_sum + 48 <= 70 + t:
                        result.append((t, minimum, eta))
    return tuple(result)


def greedy_threshold_admissible(minimum, actual):
    """Independent actual members cannot outnumber any threshold span."""
    by_threshold = all(
        sum(weight <= level for weight in actual)
        <= sum(weight <= level for weight in minimum)
        for level in range(1, 10)
    )
    by_sorted_weights = all(
        weight >= lower for weight, lower in zip(sorted(actual), sorted(minimum))
    )
    require(by_threshold == by_sorted_weights, "threshold/domination disagreement")
    return by_threshold


def exact_small_threshold_admissible(minimum, actual, allow_plane_weight3=False):
    """Elementary support consequences beyond mere threshold dimensions."""
    small = {weight for weight in actual if weight < 7}
    if minimum == "77771":
        return small <= {1}  # The threshold through six is a unit line.
    if minimum == "77772":
        return small <= {2}  # A rank-two line retains weight two under scaling.
    if minimum == "777711":
        # The two-unit plane is supported at exactly two sites.
        return small <= ({1, 2, 3} if allow_plane_weight3 else {1, 2})
    if minimum == "777541":
        return not (small & {2, 3})  # Threshold through three is the unit line.
    if minimum == "777631":
        return 2 not in small  # Threshold through two is the unit line.
    if minimum == "777721":
        # The unit plus rank-two generator use at most three sites in total.
        return small <= {1, 2, 3}
    raise VerificationError(f"unhandled minimum threshold {minimum}")


def check_actual_profiles(claimed, allow_plane_weight3=False):
    discovered = cases()
    require(set(discovered) == set(claimed), "actual profile case inventory mismatch")
    computed = {}
    for key in discovered:
        t, minimum_text, eta = key
        minimum = profile(minimum_text)
        target = sum(minimum) - 8 + eta
        actuals = {
            text(actual) for actual in profiles(t + 2, 9, 22 + t)
            if sum(actual) == target
            and greedy_threshold_admissible(minimum, actual)
            and exact_small_threshold_admissible(
                minimum_text, actual, allow_plane_weight3=allow_plane_weight3
            )
        }
        require(actuals == claimed[key],
                f"actual profile mismatch {key}: "
                f"unlisted={sorted(actuals - claimed[key])}, "
                f"unsupported={sorted(claimed[key] - actuals)}")
        computed[key] = actuals
    return computed


def check_ledgers(actuals, claimed_allowances):
    require(set(actuals) == set(claimed_allowances), "c9 case inventory mismatch")
    rows = []
    for key, candidates in actuals.items():
        t, minimum_text, eta = key
        minimum_cost = sum(profile(minimum_text))
        inside_sum = minimum_cost - 8 + eta
        allowed = tuple(c9 for c9 in range(7) if inside_sum + 48 + c9 <= 70 + t)
        require(allowed == claimed_allowances[key],
                f"c9 allowance mismatch {key}: derived={allowed}, "
                f"claimed={claimed_allowances[key]}")
        for candidate_text in sorted(candidates):
            candidate = profile(candidate_text)
            eligible_inside = sum(weight >= 3 for weight in candidate)
            for c9 in allowed:
                raw_from_actual = sum(candidate) + 8 * (6 - c9) + 9 * c9
                raw_from_ledger = minimum_cost + 40 + eta + c9
                require(raw_from_actual == raw_from_ledger, "raw ledger disagreement")
                required = raw_from_actual - 64
                require(required >= 0, "negative correction requirement")
                # This is a NECESSARY count, not geometric realizability.
                minimum_outside = max(0, required - eligible_inside)
                require(minimum_outside <= 6, "correction count exceeds outside count")
                require(raw_from_actual <= 70 + t, "raw budget exceeded")
                rows.append({
                    "t": t, "minimum_T": minimum_text, "eta": eta,
                    "actual_inside": candidate_text, "inside_sum": inside_sum,
                    "outside_c9": c9, "raw_sum": raw_from_actual,
                    "corrections_needed_for_I_at_most64": required,
                    "maximum_eligible_inside": eligible_inside,
                    "minimum_corrected_outside": minimum_outside,
                    "maximum_active_D_axes": 8 - minimum_outside,
                })
    return rows


def check_tail_capacities(capacities=CAPACITIES):
    rows = []
    for length, budget, expected in ((4, 24, 40), (5, 25, 41)):
        largest = -1
        witnesses = []
        examined = 0
        for candidate in profiles(length, 9, budget):
            examined += 1
            tail = candidate[2:]
            require(all(weight in capacities for weight in tail),
                    "tail contains an unbounded rank")
            capacity = sum(capacities[weight] for weight in tail)
            if capacity > largest:
                largest, witnesses = capacity, [text(candidate)]
            elif capacity == largest:
                witnesses.append(text(candidate))
        require(largest == expected,
                f"tail capacity mismatch length{length}: {largest} != {expected}")
        require(largest < 53, "tail reaches code distance")
        rows.append({"inside_count": length, "sum_at_most": budget,
                     "examined_profiles": examined, "maximum_tail_capacity": largest,
                     "maximizers": sorted(witnesses)})
    return rows


def detected_control(name, check, expected_message):
    """Feed a real mutation through the same production validator."""
    try:
        check()
    except VerificationError as error:
        require(expected_message in str(error), f"control failed for wrong reason: {error}")
        return {"mutation": name, "detected": True, "reason": str(error)}
    raise VerificationError(f"negative control was NOT detected: {name}")


def negative_controls(actuals):
    missing = deepcopy(EXPECTED_ACTUAL)
    missing[(3, "777711", 3)].remove("88711")
    wrong_c9 = deepcopy(EXPECTED_C9)
    wrong_c9[(3, "777711", 3)] = (0, 1)
    wrong_capacity = dict(CAPACITIES)
    wrong_capacity[7] += 1
    return [
        detected_control("omit actual88711", lambda: check_actual_profiles(missing),
                         "actual profile mismatch"),
        detected_control("allow weight3 in two-unit plane",
                         lambda: check_actual_profiles(EXPECTED_ACTUAL, True),
                         "actual profile mismatch"),
        detected_control("allow c9=1 at inside sum25",
                         lambda: check_ledgers(actuals, wrong_c9), "c9 allowance mismatch"),
        detected_control("raise rank7 capacity by one",
                         lambda: check_tail_capacities(wrong_capacity),
                         "tail capacity mismatch"),
        detected_control("omit adapted t3 actual888711",
                         lambda: adapted_t3_report(EXPECTED_ADAPTED_T3_HIGH - {"888711"}),
                         "adapted t3 actual high profile inventory mismatch"),
    ]


def adapted_t2_report():
    """Exact arithmetic of the adapted-t2 proof.

    The intrinsic four-piece dominance boundary is a written RAW-SHAPE
    input. This function does not prove the new geometric case exclusions.
    """
    lower_four = tuple(map(profile, ("7666", "7765", "7771")))
    minimums = {
        text(candidate) for candidate in profiles(5, 7, 32)
        if sum(candidate) >= 29 and any(
            all(actual >= lower for actual, lower in zip(candidate[1:], boundary))
            for boundary in lower_four)
    }
    expected = {
        "77771": {"77771", "87771", "97771", "88771", "98771", "88871"},
        "77772": {"77772", "87772", "97772", "88772"},
        "77773": {"77773", "87773"},
        "77774": {"77774"}, "77765": {"77765"}, "77666": {"77666"},
    }
    require(minimums == set(expected), "adapted minimum-profile boundary mismatch")
    rows = []
    all_actuals = set()
    for minimum_text in sorted(minimums):
        minimum = profile(minimum_text)
        actuals = set()
        for actual in profiles(5, 9, 32):
            if not greedy_threshold_admissible(minimum, actual):
                continue
            if minimum_text.startswith("7777"):
                # The threshold below seven is one line; scalar multiples
                # retain the rank of its generator, which cannot be omitted.
                if {weight for weight in actual if weight < 7} != {minimum[-1]}:
                    continue
            actuals.add(text(actual))
        require(actuals == expected[minimum_text],
                "adapted actual threshold mismatch: " + minimum_text)
        all_actuals.update(actuals)
        for actual_text in sorted(actuals):
            sigma = sum(profile(actual_text))
            allowed_c9 = list(range(min(5, 32 - sigma) + 1))
            rows.append({"minimum_T": minimum_text, "actual_inside": actual_text,
                         "inside_sum": sigma, "outside_c9_allowed": allowed_c9,
                         "corrections_needed": [sigma - 24 + c9 for c9 in allowed_c9]})
    high = sorted(value for value in all_actuals if max(profile(value)) >= 8)
    low = sorted(all_actuals - set(high))
    require(len(all_actuals) == len(rows) == 15 and len(high) == 9 and len(low) == 6,
            "adapted-t2 profile coverage count changed")
    return {"scope": "adapted t2 integer profiles only; geometry is written in ADAPTED-T2.md",
            "intrinsic_four_piece_dominance_input": ["7666", "7765", "7771"],
            "minimum_T_profiles": sorted(minimums), "actual_profile_count": 15,
            "high_containing_profiles": high, "all_low_profiles": low,
            "ledger_rows": rows}


ADAPTED_T3_INTRINSIC_FIVE = {
    "77711", "77721", "77541", "77631", "77731", "77722",
    "77551", "77542", "77641", "77632",
}
EXPECTED_ADAPTED_T3_HIGH = {
    "877711", "977711", "887711", "987711", "877721", "977721",
    "877541", "977541", "877631", "977631", "877722", "887721",
    "888711", "887541", "887631", "877551", "877641", "877731",
    "877542", "877632",
}


def adapted_t3_report(claimed_high=None):
    """Necessary actual profiles; intrinsic E8 exclusions remain written inputs.

    High-containing actual bases force minimum cost <=32. All-low sum33
    is handled by a written correction-pair merge, without a profile list.
    """
    minimums = {
        text(candidate) for candidate in profiles(6, 7, 32)
        if candidate[0] == 7 and text(candidate[1:]) in ADAPTED_T3_INTRINSIC_FIVE
    }
    expected_minimums = {
        "777711", "777721", "777541", "777631", "777731", "777722",
        "777551", "777542", "777641", "777632",
    }
    require(minimums == expected_minimums, "adapted t3 minimum profile inventory mismatch")
    high, low = set(), set()
    threshold_rows = []
    for minimum_text in sorted(minimums):
        minimum = profile(minimum_text)
        candidates = set()
        for actual in profiles(6, 9, 33):
            if not greedy_threshold_admissible(minimum, actual):
                continue
            small = {weight for weight in actual if weight < 7}
            if minimum_text == "777711" and not small <= {1, 2}:
                continue  # Two unit generators: their plane has only two sites.
            if minimum_text == "777721" and not small <= {1, 2, 3}:
                continue  # Unit plus rank-two generator: at most three sites.
            if minimum_text == "777541" and small & {2, 3}:
                continue  # The threshold through three is the unit line.
            if minimum_text == "777631" and 2 in small:
                continue  # The threshold through two is the unit line.
            candidate = text(actual)
            if actual[0] >= 8:
                high.add(candidate)
                candidates.add(candidate)
            elif sum(actual) <= 32:
                low.add(candidate)
        threshold_rows.append({"minimum_T": minimum_text,
                               "high_actual_candidates": sorted(candidates)})
    require(high == (EXPECTED_ADAPTED_T3_HIGH if claimed_high is None else claimed_high),
            "adapted t3 actual high profile inventory mismatch")
    require(low == expected_minimums, "adapted t3 all-low profile inventory mismatch")
    residual = {candidate[1:] for candidate in high}  # Delete a heaviest actual high.
    expected_residual = {
        "77711", "87711", "77721", "77541", "77631", "77722", "87721",
        "88711", "87541", "87631", "77551", "77641", "77731", "77542", "77632",
    }
    require(residual == expected_residual, "adapted t3 residual actual profile mismatch")
    rows = []
    for candidate in sorted(high | low):
        sigma = sum(profile(candidate))
        c9s = list(range(min(5, 33 - sigma) + 1))
        rows.append({"actual_inside": candidate, "inside_sum": sigma,
                     "outside_c9_allowed": c9s,
                     "corrections_needed": [sigma - 24 + c9 for c9 in c9s]})
    require(33 + 40 == 73 and 33 + 40 - 64 == 9,
            "adapted t3 merge boundary arithmetic differs")
    return {"scope": "necessary integer profiles, not E8 invoice proof",
            "intrinsic_five_piece_input": sorted(ADAPTED_T3_INTRINSIC_FIVE),
            "minimum_T_profiles_through_cost32": sorted(minimums),
            "high_actual_candidates": sorted(high), "high_actual_candidate_count": len(high),
            "residual_actual_profiles": sorted(residual),
            "all_low_actual_profiles_through_sum32": sorted(low),
            "threshold_rows": threshold_rows, "ledger_rows": rows,
            "all_low_sum33": {"outside_c9": 0, "corrections_at_least": 9,
                              "written_method": "same-axis correction merge to t2, d2 or d3"}}


def report():
    minimum = derive_minimum_boundary()
    actuals = check_actual_profiles(EXPECTED_ACTUAL)
    ledger = check_ledgers(actuals, EXPECTED_C9)
    tail = check_tail_capacities()
    controls = negative_controls(actuals)
    report = {
        "status": "pass",
        "scope": "integer profile exhaustion and arithmetic only; E8 proof not formalized",
        "retained_intrinsic_inputs": {
            key: sorted(value) if isinstance(value, set) else value
            for key, value in INTRINSIC.items()
        },
        "minimum_T_boundary_arithmetic": minimum,
        "actual_profile_case_count": len(actuals),
        "actual_profile_occurrences": sum(len(value) for value in actuals.values()),
        "invoice_ledger_rows": ledger,
        "generic_dim_at_least3_tail_bounds": tail,
        "failure_controls": controls,
        "adapted_t2_arithmetic": adapted_t2_report(),
        "adapted_t3_arithmetic": adapted_t3_report(),
    }
    return report


def main():
    print(json.dumps(report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
