"""Constructive logical invoice for the explicit 52-bank admission codec.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
Counts price the stated arithmetic schedule, not a physical or recursive tariff.
The arbitrary six dirty D/Q banks already satisfy their separate B9 contract.
"""

from collections import Counter


def permutation_cycles(plan):
    permutation = [target for target, _ in plan]
    if sorted(permutation) != list(range(len(plan))):
        raise ValueError("wrapper permutation must be bijective")
    seen, count = set(), 0
    for start in range(len(plan)):
        if start in seen:
            continue
        count += 1
        at = start
        while at not in seen:
            seen.add(at)
            at = permutation[at]
    return count


def path_inventory(structure, plans):
    events, wrappers, extras = [], [], []
    for gap in structure["gaps"]:
        if gap["kind"] == "terminal":
            continue
        for event in gap["path_to_read"]:
            events.append(event)
            wrappers.extend((plans[event]["left"], plans[event]["right"]))
        if gap["kind"] == "rank_one":
            extra = gap["transport_event"]
            extras.append(extra)
            wrappers.append(plans[extra]["right"])
    phases = Counter((-phase) % 4 for plan in wrappers for _, phase in plan)
    cycles = [permutation_cycles(plan) for plan in wrappers]
    return {
        "native_event_occurrences": events, "native_occurrence_count": len(events),
        "native_rank_mass": sum(plans[e]["rank"] for e in events),
        "extra_right_wrapper_events": extras, "wrapper_count": len(wrappers),
        "wrapper_cycles": cycles, "wrapper_cycle_sum": sum(cycles),
        "gaussian_payload_swaps": sum(len(plan) - count for plan, count in zip(wrappers, cycles)),
        "inverse_wrapper_phase_histogram": {str(k): phases[k] for k in range(4)},
        "wrapper_phase_positions": sum(len(plan) for plan in wrappers),
        "swap_contract": "Direct Gaussian payload SWAP gates on owned words, n-cycles per permutation; different from the n+cycles clean-scratch implementation.",
    }


def invoice(structure, plans, classifier):
    inventory = path_inventory(structure, plans)
    profiles = [classifier.profile(gap["kind"]) for gap in structure["gaps"]]
    adds = sum(p["encode_schedule"]["gaussian_additions"] for p in profiles)
    pi_steps = sum(p["encode_schedule"]["gaussian_pi_multiplications"] for p in profiles)
    doublings = sum(p["encode_schedule"]["gaussian_doublings"] for p in profiles)
    differences = (52 - 5) * 512
    native_pairs = inventory["native_rank_mass"] * 256
    forward_adds = 2 * (adds + pi_steps + doublings + differences) + 8 * native_pairs
    reverse_adds = forward_adds - 2 * doublings
    native_halves = 4 * native_pairs
    phases = inventory["inverse_wrapper_phase_histogram"]
    phase_turns = phases["1"] + phases["3"]
    negations = phase_turns + 2 * phases["2"] + native_pairs
    swap_adds = 6 * inventory["gaussian_payload_swaps"] + 3 * (phase_turns + native_pairs)
    return {
        "kind": "constructive_logical_upper_bound_not_physical_supplier_invoice",
        "owned_coefficient_banks": 52, "gaussian_payload_words": 52 * 512,
        "separate_already_admitted_dirty_banks": 6, "newton_additions": adds,
        "gaussian_pi_steps": pi_steps, "terminal_gaussian_doublings": doublings,
        "group_field_differences": 47, "gaussian_differences": differences,
        "native_pairs_per_direction": native_pairs, "native_quarter_turns": native_pairs,
        "path_inventory": inventory,
        "forward": {"real_add_subtracts_before_swap_phase_lowering": forward_adds,
                    "real_floor_halves": native_halves,
                    "real_add_subtracts_with_swaps_and_negations": forward_adds + swap_adds + negations},
        "reverse": {"real_add_subtracts_before_swap_phase_lowering": reverse_adds,
                    "real_halves": native_halves + 2 * pi_steps + 2 * doublings,
                    "real_add_subtracts_with_swaps_and_negations": reverse_adds + swap_adds + negations},
        "optional_lowering": {"gaussian_swap_real_adds": 6, "real_component_swap_adds": 3,
                              "unary_negations_as_zero_minus_value": negations,
                              "extra_real_adds_for_swaps": swap_adds,
                              "real_swap_schedule": ["x <- x+y", "y <- x-y", "x <- x-y"],
                              "scope": "Exact unbounded component arithmetic permits source-minus-target overwrite and unary zero-minus-value. This is not automatically the repository strict target-ADD tariff. Fixed-width overflow and physical bit costs remain obligations."},
        "width_bounds": {"coefficient_component_limit": "H",
                         "nonterminal_profile_component_gain": 3828,
                         "unitary_path_component_gain": 122496,
                         "terminal_component_gain": 13452,
                         "prepared_source_component_gain": 244992,
                         "encoder_work_component_gain": 612480,
                         "decoder_input_component_limit": "J",
                         "decoder_work_component_gain": 98304},
        "borrowed_source_copy_option": {"owned_zero_banks": 52, "copy_field_adds": 52,
                                        "cleanup_field_subtracts": 52,
                                        "precondition": "Prepared banks are returned unchanged in their entrance frame before inversion and cleanup; this cone theorem does not prove that return."},
        "unpriced": ["An actual caller and its changed logical input/output interpretation",
                     "Physical word ownership, control, layout and routing",
                     "Bit complexity and fixed-width gate implementation",
                     "Omitted prefix branches and compatible complete external consumer",
                     "Recursive child/coverage costs and all-size transfer"],
        "inherited_unchanged_profile_stop": "599/584 > 1; no changed supplier profile is proposed",
    }
