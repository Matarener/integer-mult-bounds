#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent source/count and rational cost audit; no predecessor imports.

Clear1nsight, with substantial OpenAI assistance.
This script proves no physical running-time or recursive supplier theorem.
With --source-root it authenticates the three exact immutable inputs, derives
the producer dependency cone and the 63-state open program, then counts one
specified direct in-place schedule.  Without it, only the rational arithmetic
and per-bank codec reference counts are evaluated.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path


MAIN = "6f100d4bb5083f8c35d96fd95a539811c62f245c"
SOURCE_PINS = {
    "research/p104-rounded-collector/inputs/WORD.json":
        "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    "research/p104-rounded-collector/inputs/NATIVE.json.gz":
        "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
    "research/p104-consumer-budget-audit/README.md":
        "13694215d0c1a245b392f7155e8395b9c4bad9c5db3558833c784d9449616417",
}
N = 512


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def counted(values):
    return dict(sorted(Counter(str(x) for x in values).items()))


def fixed_consumer():
    """PR2744's unmodified, fixed-profile relaxation; exact rational work only."""
    profiles = {
        "F2458": [1216, 74, 86, 104, 48, 42, 68, 8],
        "D2712": [1498, 60, 74, 92, 58, 56, 92, 8],
        "D2725": [1502, 58, 74, 93, 57, 56, 91, 9],
    }
    masses = {key: sum((r + 1) * n for r, n in enumerate(profile))
              for key, profile in profiles.items()}
    need(masses == {"F2458": 3070, "D2712": 3542, "D2725": 3542},
         "pinned profile mass")
    width, families, forward, dual = 73, 832, 5, 4
    progress = 104 * 8 + 104 * 8 + 150 * 9
    remaining = (width - 1) * families - (forward + dual) * progress
    capacity = width * families
    totals = {key: forward * masses["F2458"] + dual * masses[key] + remaining
              for key in ("D2712", "D2725")}
    need(progress == 3014 and remaining == 32778 and capacity == 60736,
         "coverage arithmetic")
    need(set(totals.values()) == {62296}, "unmodified consumer total")
    gap = totals["D2712"] - capacity
    need(gap == 1560 and Fraction(62296, capacity) == Fraction(599, 584),
         "inherited rational stop")
    bank_samples = {}
    for banks in (0, 1, 22, 63, 83, 832, 10**6):
        lower = Fraction(62296 + width * banks, width * (families + banks))
        need(lower == 1 + Fraction(gap, width * (families + banks)) and lower > 1,
             "fully paid bank identity")
        bank_samples[str(banks)] = str(lower)
    # A meaningful failure control: adding families only to the denominator
    # produces a false favourable screen already at B=22.
    denominator_only = Fraction(62296, width * (families + 22))
    paid = Fraction(62296 + 22 * width, width * (families + 22))
    need(denominator_only < 1 < paid, "unpaid-bank false-positive control")
    return {
        "credit": "Jose Manuel, Discussion2619 comment18955566; Vasek/flyingviper PR2744",
        "predecessor_head": "0166260409f55a56e7fefa48d859f7dd5b42b300",
        "profiles": profiles, "rank_masses": masses,
        "width": width, "original_families": families,
        "forward_calls": forward, "dual_calls": dual,
        "progress_per_call": progress, "remaining_coverage_mass": remaining,
        "capacity": capacity, "unmodified_total": 62296, "excess_mass": gap,
        "no_bank_lower_bound": "599/584",
        "all_finite_fully_paid_banks_formula": "1 + 1560/(73*(832+B))",
        "saving_domain": "0 <= a < 1",
        "proof_step": "For 0 < r <= 73, (r/73)^(1-a) >= r/73.",
        "bank_examples_not_the_universal_proof": bank_samples,
        "negative_control": {
            "unauthorised_denominator_only_B22": str(denominator_only),
            "correct_fully_paid_B22": str(paid),
            "reason_rejected": "Every added bank owes 73 paid coverage units.",
        },
        "scope": "Fixed profiles and coverage only; no universal P104 obstruction.",
        "all_additional_physical_costs": "unresolved nonnegative charges, not zero",
    }


def codec_reference():
    pairs = 9 * N // 2
    return {
        "one_bank_encode": {"pairs": pairs, "real_add_subtracts": 4 * pairs,
                            "component_reads": 4 * pairs, "component_writes": 2 * pairs},
        "one_bank_decode": {"pairs": pairs, "real_add_subtracts": 4 * pairs,
                            "exact_real_halves": 2 * pairs,
                            "component_reads": 4 * pairs, "component_writes": 2 * pairs},
        "hypothetical_63_mutable_bank_roundtrip": {
            "encodes": 63, "decodes": 63,
            "real_add_subtracts": 63 * 8 * pairs,
            "exact_real_halves": 63 * 2 * pairs,
            "component_reads": 63 * 8 * pairs, "component_writes": 63 * 4 * pairs,
        },
        "limitations": [
            "These count separately specified in-place coordinate conversions.",
            "A 63-bank roundtrip is not a complete adapter for the 83 external port targets.",
            "52 Y banks still require 4B admission; encoding ordinary coefficients into B is insufficient.",
            "Original A and E^-1 A E are distinct external numerical contracts.",
            "Borrowed-input copying, setup, routing, widths and physical storage are not included.",
        ],
    }


def wrapper_summary(record):
    need(set(record) == {"matrix_rows", "offset", "linear_Z4", "quadratic_rows", "phase"},
         "wrapper schema")
    rows, linear, quadratic = (record[key] for key in
                               ("matrix_rows", "linear_Z4", "quadratic_rows"))
    need(len(rows) == len(linear) == len(quadratic) == 9, "wrapper dimension")
    need(all(type(v) is int and 0 <= v < N for v in rows + quadratic), "binary rows")
    need(all(type(v) is int and 0 <= v < 4 for v in linear), "linear phase")
    need(type(record["offset"]) is int and 0 <= record["offset"] < N, "offset")
    need(type(record["phase"]) is int and 0 <= record["phase"] < 4, "global phase")
    permutation, phases = [], []
    for address in range(N):
        target = record["offset"]
        for bit, row in enumerate(rows):
            target ^= ((address & row).bit_count() & 1) << bit
        phase = record["phase"]
        for j in range(9):
            if address & (1 << j):
                phase += linear[j]
                phase += 2 * (address & quadratic[j] & ~((1 << (j + 1)) - 1)).bit_count()
        permutation.append(target)
        phases.append(phase % 4)
    need(sorted(permutation) == list(range(N)), "wrapper is a permutation")
    seen, cycles = set(), 0
    for first in range(N):
        if first in seen:
            continue
        cycles += 1
        at = first
        while at not in seen:
            seen.add(at)
            at = permutation[at]
        need(at == first, "closed wrapper cycle")
    return {"cycles": cycles, "phase_histogram": Counter(phases),
            "plan_sha256": canonical_sha(list(zip(permutation, phases)))}


def source_audit(root):
    raw, authenticated = {}, []
    for path, expected in SOURCE_PINS.items():
        data = (root / path).read_bytes()
        need(sha(data) == expected, "source SHA256 mismatch: " + path)
        raw[path] = data
        authenticated.append({"path": path, "sha256": expected, "bytes": len(data),
                              "git_blob": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()})
    word = json.loads(raw["research/p104-rounded-collector/inputs/WORD.json"])
    native = json.loads(gzip.decompress(raw["research/p104-rounded-collector/inputs/NATIVE.json.gz"]))
    program = word["program"]
    need(len(program) == 5398 and len(native["transports"]) == 1245, "source dimensions")
    need(word["chart"] == "Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)", "source chart")
    # Independently re-derive initial dependencies backwards from actual writes.
    roles = {"Q7"} | {"D" + str(i) for i in range(27, 32)}
    cone = []
    for index in range(2024, -1, -1):
        event = program[index]
        if event[0] == "transport" and event[1] in roles:
            cone.append(index)
        elif event[0] == "add" and event[1] in roles:
            cone.append(index)
            roles.add(event[2])
        elif event[0] in ("zero", "erase") and event[1] in roles:
            raise ValueError("unexpected producer lifecycle")
    cone.sort()
    need(len(cone) == 257 and len(roles) == 58, "producer dependency cone")
    producer_roles = sorted(roles)
    need(sum(role.startswith("Y") for role in roles) == 52, "52 strengthened sources")
    roles |= {"G" + str(i) for i in range(27, 32)}
    need(all(word["initial_frames"][role] == [] for role in roles), "initial frames")
    internal, ports = [], []
    for index, event in enumerate(program[:4517]):
        if 2025 <= index <= 2039:
            internal.append(index)
        elif event[0] == "transport" and event[1] in roles:
            internal.append(index)
        elif event[0] == "add" and event[1] in roles:
            need(event[2] in roles, "unadmitted inward dependency")
            internal.append(index)
        elif event[0] == "add" and event[2] in roles:
            ports.append(index)
    need(len(internal) == 576 and len(ports) == 675, "open program source counts")
    need(len(set(internal) | set(ports)) == 1251, "no internal/port double counting")
    frame = {role: word["initial_frames"][role] for role in roles}
    # A positive rational envelope, measured in units of 32H for array l2 norm.
    # Source transports and all their wrapper/C prefixes are unitary on the
    # separately proved admitted domain.  This deliberately ignores cancellation.
    norm_weight = {role: Fraction(1) for role in roles}
    max_internal = {"weight": Fraction(1), "event": None, "field": None}
    max_increment = {"weight": Fraction(0), "event": None, "field": None}
    for index in sorted(internal + ports):
        event = program[index]
        if event[0] == "transport":
            need(frame[event[1]] == event[2], "old source frame at " + str(index))
            frame[event[1]] = event[3]
        elif event[0] == "zero":
            need(event[1] == "C" and event[1] not in frame, "owned C creation")
            frame[event[1]] = event[2]
            norm_weight[event[1]] = Fraction(0)
        elif event[0] == "erase":
            need(event[1] == "C" and frame[event[1]] == event[2], "owned C erase frame")
            del frame[event[1]]
            del norm_weight[event[1]]
        elif event[0] == "add":
            need(frame[event[2]] == event[4], "source read frame at " + str(index))
            increment_weight = abs(Fraction(event[3])) * norm_weight[event[2]]
            if index in internal:
                need(frame[event[1]] == event[4], "internal target frame at " + str(index))
                norm_weight[event[1]] += increment_weight
                if norm_weight[event[1]] > max_internal["weight"]:
                    max_internal = {"weight": norm_weight[event[1]], "event": index,
                                    "field": event[1]}
            elif increment_weight > max_increment["weight"]:
                max_increment = {"weight": increment_weight, "event": index,
                                 "field": event[1]}
    need(len(frame) == 63 and "C" not in frame, "final frame inventory")
    need(max_internal == {"weight": Fraction(49), "event": 4165, "field": "G27"}
         and max_increment == {"weight": Fraction(50), "event": 3250, "field": "X28"},
         "conservative triangle norm envelope")
    norm_bounds = {
        "assumption": "Every initial real component of all63 admitted internal arrays has absolute value <= integer H>=0, in common-grid numerator units.",
        "initial_array_l2_norm": "<=32H since sqrt(2*512)=32",
        "native_prefix_fact": "Every affine/unit-phase wrapper and partial C product is unitary; literal equality is supplied by the admitted-domain proof.",
        "propagation": "w_target <- w_target + abs(coefficient)*w_source; w_initial=1; w_C_zero=0; native w unchanged.",
        "max_internal_l2_weight": int(max_internal["weight"]),
        "first_max_internal_event": max_internal["event"],
        "first_max_internal_field": max_internal["field"],
        "max_port_increment_l2_weight": int(max_increment["weight"]),
        "first_max_port_event": max_increment["event"],
        "first_max_port_target": max_increment["field"],
        "internal_payload_component_bound": "1568H",
        "literal_pair_work_component_bound": "7840H",
        "port_increment_component_bound": "1600H",
        "signed_core_width_sufficient_condition": "2^(h-1)>7840H",
        "port_target_condition": "A current target bound H_target needs capacity for H_target+1600H; H_target and its intervening external history remain caller obligations.",
        "signed_floor_lemma": "For integer |a|,|b|<=B, |d|<=2B, |floor(d/2)|<=B, |middle|<=2B, |second|<=3B, |first|<=5B, componentwise and after quarter rotation.",
        "status": "Conservative constructive bounds, not minimum widths or physical time/space tariffs.",
    }
    by_event = {}
    for transport in native["transports"]:
        for index in transport["events"]:
            need(index not in by_event, "duplicate native event")
            by_event[index] = transport
    cache, native_records, cycles, phases = {}, [], 0, Counter()
    for index in internal:
        event = program[index]
        if event[0] != "transport":
            continue
        transport = by_event[index]
        need(transport["old"] == event[2] and transport["new"] == event[3]
             and transport["recipe"]["rank"] == event[4], "native event/frame/rank binding")
        wrappers = []
        for side in ("right", "left"):
            record = transport["recipe"][side]
            key = canonical_sha(record)
            if key not in cache:
                cache[key] = wrapper_summary(record)
            summary = cache[key]
            cycles += summary["cycles"]
            phases.update(summary["phase_histogram"])
            wrappers.append({"side": side, "cycles": summary["cycles"],
                             "plan_sha256": summary["plan_sha256"]})
        native_records.append({"event": index, "rank": event[4], "wrappers": wrappers})
    rank_histogram = Counter(program[i][4] for i in internal if program[i][0] == "transport")
    rank_mass = sum(rank * count for rank, count in rank_histogram.items())
    need(rank_mass == 581 and len(native_records) == 392, "native totals")
    pairs = N // 2 * rank_mass
    add_indices = [i for i in internal + ports if program[i][0] == "add"]
    fractions = Counter(Fraction(program[i][3]) for i in add_indices)
    need(set(fractions) <= {Fraction(x) for x in ("1", "-1", "1/4", "-1/4", "2", "-2")}, "ADD alphabet")
    quarter_adds = fractions[Fraction(1, 4)] + fractions[Fraction(-1, 4)]
    doubled_adds = fractions[Fraction(2)] + fractions[Fraction(-2)]
    swap_count = 2 * len(native_records) * N + cycles
    port_records = [{"event": i, "target": program[i][1], "source": program[i][2],
                     "coefficient": str(Fraction(program[i][3])), "frame": program[i][4]}
                    for i in ports]
    direct = {
        "native_transports": len(native_records), "native_rank_mass": rank_mass,
        "signed_floor_pairs": pairs, "native_real_add_subtracts": 8 * pairs,
        "native_real_floor_halves": 4 * pairs, "native_gaussian_quarter_turns": pairs,
        "native_pair_component_reads": 4 * pairs, "native_pair_component_writes": 4 * pairs,
        "wrappers": 2 * len(native_records), "wrapper_cycles": cycles,
        "wrapper_gaussian_swaps": swap_count, "wrapper_unit_phase_applications": 2 * len(native_records) * N,
        "wrapper_phase_histogram": dict(sorted(phases.items())),
        "wrapper_swap_component_reads": 4 * swap_count,
        "wrapper_swap_component_writes": 4 * swap_count,
        "field_adds_including_all_ports": len(add_indices),
        "field_add_real_add_subtracts_excluding_doublings": 2 * N * len(add_indices),
        "quarter_field_adds": quarter_adds, "quarter_exact_real_halves": 4 * N * quarter_adds,
        "double_field_adds": doubled_adds, "double_real_doublings": 2 * N * doubled_adds,
        "field_add_component_reads": 4 * N * len(add_indices),
        "field_add_component_writes": 2 * N * len(add_indices),
        "source_component_reads_subtotal_not_additional": 2 * N * len(add_indices),
        "private_C_initialization_components": 2 * N,
        "private_C_zero_inspection_components": 2 * N,
        "total_real_add_subtracts_excluding_doublings": 8 * pairs + 2 * N * len(add_indices),
        "total_if_each_doubling_is_one_real_add": 8 * pairs + 2 * N * (len(add_indices) + doubled_adds),
        "core_persistent_gaussian_state_words": 63 * N,
        "owned_C_gaussian_words": N, "owned_wrapper_zero_scratch_gaussian_words": 1,
        "pair_real_work_words": 4, "distinct_external_target_banks": len({x["target"] for x in port_records}),
        "distinct_wrapper_recipes": len(cache),
        "setup": "Compile one 512-entry wrapper plan at a time: O(784*512*9^2) Boolean/control operations and O(512) temporary plan entries; not free physical setup.",
        "internal_common_grid_numerator_bounds": "Constructively upper-bounded in conservative_norm_bounds; external target widths remain unknown.",
        "physical_tariff_routing_owner_map": "unknown",
        "codecs_or_admission_included": False,
    }
    need(pairs == 148736 and len(add_indices) == 857 and quarter_adds == 675 and doubled_adds == 156,
         "complete direct source bill")
    return {
        "source_main": MAIN, "authenticated_inputs": authenticated, "chart": word["chart"],
        "scope": "63-state open-interface projection through event4516; all675 outgoing reads retained as ports. Omitted external histories are not executed or priced.",
        "producer": {"events": cone, "initial_roles": producer_roles,
                     "opcode_counts": counted(program[i][0] for i in cone),
                     "rank_mass": sum(program[i][4] for i in cone if program[i][0] == "transport")},
        "internal_event_indices": internal, "internal_opcode_counts": counted(program[i][0] for i in internal),
        "initial_roles": sorted(roles), "final_frames": frame,
        "rank_histogram": dict(sorted(rank_histogram.items())),
        "internal_add_coefficients": counted(Fraction(program[i][3]) for i in internal if program[i][0] == "add"),
        "port_add_coefficients": counted(Fraction(program[i][3]) for i in ports),
        "outgoing_ports": port_records, "outgoing_port_sha256": canonical_sha(port_records),
        "transport_wrapper_bindings": native_records,
        "transport_wrapper_bindings_sha256": canonical_sha(native_records),
        "direct_reference_schedule": direct,
        "conservative_norm_bounds": norm_bounds,
        "semantic_restoration_proof": "provided separately; this script checks source closure, frame consistency and the bill only",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {"schema_version": 1, "implementation_sha256": sha(Path(__file__).read_bytes()),
              "fixed_consumer": fixed_consumer(), "codec_reference": codec_reference()}
    if args.source_root is not None:
        result["source_audit"] = source_audit(args.source_root)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(payload)
        print(json.dumps({"status": "PASS", "output": str(args.output), "sha256": sha(payload.encode()),
                          "source_audit_executed": args.source_root is not None}))
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
