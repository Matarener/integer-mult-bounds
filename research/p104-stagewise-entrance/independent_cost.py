#!/usr/bin/env python3
"""Independent source-only inventory; imports no package or predecessor code.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from math import comb
from pathlib import Path


WORD_SHA = "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50"
NATIVE_SHA = "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d"


def require(test, label):
    if not test:
        raise ValueError(label)


def cycle_count(wrapper):
    rows, offset = wrapper["matrix_rows"], wrapper["offset"]
    require(len(rows) == 9 and type(offset) is int and 0 <= offset < 512,
            "invalid affine dimensions")
    require(all(type(r) is int and 0 <= r < 512 for r in rows), "invalid row")
    permutation = [offset ^ sum(((row & x).bit_count() % 2) << j
                              for j, row in enumerate(rows)) for x in range(512)]
    require(len(set(permutation)) == 512, "nonbijective wrapper")
    marked = set()
    sizes = []
    for x in range(512):
        if x in marked:
            continue
        y, size = x, 0
        while y not in marked:
            marked.add(y)
            size += 1
            y = permutation[y]
        require(y == x, "permutation orbit did not close")
        sizes.append(size)
    require(sum(sizes) == 512, "orbit partition")
    return len(sizes), Counter(sizes)


def inverse_phase_counts(wrapper):
    require(type(wrapper["phase"]) is int, "phase type")
    require(len(wrapper["linear_Z4"]) == len(wrapper["quadratic_rows"]) == 9,
            "phase dimensions")
    counts = Counter()
    for address in range(512):
        phase = wrapper["phase"]
        for bit in range(9):
            if address & (1 << bit):
                phase += wrapper["linear_Z4"][bit]
                upper = wrapper["quadratic_rows"][bit] & ~((1 << (bit + 1)) - 1)
                phase += 2 * (upper & address).bit_count()
        # The inverse phase at the permuted address is the negative original
        # phase. Bijectivity preserves its histogram over all 512 inputs.
        counts[-phase % 4] += 1
    return {str(k): counts[k] for k in range(4)}


def audit(root):
    inputs = Path(root) / "research/p104-rounded-collector/inputs"
    wb, nb = (inputs / "WORD.json").read_bytes(), (inputs / "NATIVE.json.gz").read_bytes()
    require(hashlib.sha256(wb).hexdigest() == WORD_SHA, "WORD source hash")
    require(hashlib.sha256(nb).hexdigest() == NATIVE_SHA, "NATIVE source hash")
    word = json.loads(wb)
    program = word["program"]
    archive = json.loads(gzip.decompress(nb))["transports"]
    by_event = {}
    for index, record in enumerate(archive):
        for event in record["events"]:
            require(event not in by_event, "duplicate native occurrence")
            by_event[event] = (index, record)
    cut = next(i for i, event in enumerate(program)
               if event[0] == "zero" and event[1] == "C")
    require(cut == 2025, "first collector cut")
    donors = [event[2] for event in program[cut + 1:cut + 6]]
    require(donors == ["D31", "D30", "D29", "D28", "D27"], "collector donor order")
    occurrences, wrappers, gaps, groups = [], [], [], []

    def add_wrapper(event, side, purpose, group, position):
        index, record = by_event[event]
        count, sizes = cycle_count(record["recipe"][side])
        wrappers.append({"event": event, "record": index, "side": side,
                         "purpose": purpose, "group": group, "position": position,
                         "cycles": count, "swaps": 512 - count,
                         "inverse_phase_counts": inverse_phase_counts(record["recipe"][side]),
                         "cycle_lengths": {str(k): sizes[k] for k in sorted(sizes)}})

    for donor in donors:
        require(word["initial_frames"][donor] == [], "donor not initially empty frame")
        reads = [(i, event) for i, event in enumerate(program[:cut])
                 if event[0] == "add" and event[1] == donor]
        require(all(event[2].startswith("Y") and event[3] == "1/4"
                    for _, event in reads), "unexpected donor write")
        require(len({event[2] for _, event in reads}) == len(reads), "reused group source")
        groups.append({"donor": donor, "source_reads": [[i, e[2]] for i, e in reads]})
        for position, (read_event, read) in enumerate(reads[:-1]):
            next_event = reads[position + 1][0]
            history = [i for i, e in enumerate(program[:read_event])
                       if e[0] == "transport" and e[1] == donor]
            interval = [i for i in range(read_event + 1, next_event)
                        if program[i][0] == "transport" and program[i][1] == donor]
            require(len(interval) <= 1, "unclassified multi-transport interval")
            frame = []
            for i in history:
                event = program[i]
                require(event[2] == frame, "broken donor frame path")
                _, record = by_event[i]
                require(record["old"] == event[2] and record["new"] == event[3]
                        and record["recipe"]["rank"] == event[4], "native binding")
                frame = event[3]
            require(frame == read[4], "path does not end at quarter frame")
            rank = 0
            if interval:
                i = interval[0]
                event = program[i]
                _, record = by_event[i]
                require(event[2] == frame and event[3] == reads[position + 1][1][4],
                        "rank-one interval endpoints")
                require(record["old"] == event[2] and record["new"] == event[3]
                        and record["recipe"]["rank"] == event[4] == 1,
                        "rank-one interval native binding")
                rank = 1
                add_wrapper(i, "right", "inverse extra right wrapper", donor, position)
            else:
                require(frame == reads[position + 1][1][4], "zero interval endpoints")
            gaps.append({"donor": donor, "position": position, "read_event": read_event,
                         "next_event": next_event, "gap_rank": rank,
                         "donor_path": history, "gap_transport": interval})
            for i in reversed(history):
                event = program[i]
                occurrences.append({"event": i, "rank": event[4],
                                    "group": donor, "position": position})
                # Inverse of left*C*right executes left^-1, reversed C^-1, right^-1.
                add_wrapper(i, "left", "inverse donor path", donor, position)
                add_wrapper(i, "right", "inverse donor path", donor, position)

    profile_hist = Counter()
    gap_hist = Counter(g["gap_rank"] for g in gaps)
    for mask in range(512):
        profile_hist[max(4 - mask.bit_count(), 0)] += gap_hist[0]
        profile_hist[max(4 - (mask & ~1).bit_count(), 0)] += gap_hist[1]
        profile_hist[4] += len(groups)
    exponent = sum(k * count for k, count in profile_hist.items())
    rank_mass = sum(e["rank"] for e in occurrences)
    pairs = rank_mass * 256
    newton_pairs = 52 * 9 * 256
    diagonal_pi_steps = exponent - len(groups) * 512 * 4
    gaussian_terminal_doublings = len(groups) * 512 * 2
    add_real = 8 * pairs + 4 * newton_pairs + 2 * diagonal_pi_steps + 2 * 47 * 512
    phases = {str(k): sum(w["inverse_phase_counts"][str(k)] for w in wrappers) for k in range(4)}
    total_swaps = sum(w["swaps"] for w in wrappers)
    quarter_rotations = phases["1"] + phases["3"] + pairs
    pi_l1 = lambda exponent: 1 << ((exponent + 1) // 2)
    gains = {"zero": sum(comb(9, d) * pi_l1(max(4, d)) for d in range(10)),
             "rank_one": sum(comb(8, d) * (pi_l1(max(4, d))
                          + pi_l1(max(4, d) + 1)) for d in range(9)),
             "terminal": 4 * sum(comb(9, d) * pi_l1(d) for d in range(10))}
    result = {
        "status": "PASS", "method": "Independent direct JSON/gzip source scan; no package imports",
        "source_hashes": {"WORD.json": WORD_SHA, "NATIVE.json.gz": NATIVE_SHA},
        "cut": cut, "groups": groups, "gaps": gaps,
        "gap_counts": {str(k): gap_hist[k] for k in sorted(gap_hist)},
        "inverse_donor_native_occurrences": len(occurrences), "rank_mass": rank_mass,
        "inverse_donor_occurrence_rows": occurrences, "pair_applications": pairs,
        "wrapper_occurrences": len(wrappers), "wrapper_cycles": sum(w["cycles"] for w in wrappers),
        "wrapper_swaps": sum(w["swaps"] for w in wrappers),
        "wrapper_groups": {kind: {"occurrences": sum(w["purpose"] == kind for w in wrappers),
                         "cycles": sum(w["cycles"] for w in wrappers if w["purpose"] == kind),
                         "swaps": sum(w["swaps"] for w in wrappers if w["purpose"] == kind)}
                           for kind in ("inverse donor path", "inverse extra right wrapper")},
        "wrapper_rows": wrappers, "wrapper_phase_applications": 512 * len(wrappers),
        "encoder_inverse_wrapper_phase_histogram": phases,
        "decoder_forward_wrapper_phase_histogram": {str(k): phases[str(-k % 4)] for k in range(4)},
        "quotient_exponent_histogram": {str(k): profile_hist[k] for k in sorted(profile_hist)},
        "index_log2": exponent, "ideal_index_log2": 5 * 512 * 4,
        "strong_4B52_index_log2": 52 * 512 * 4,
        "encode": {"newton_tensor_pairs": newton_pairs,
                   "extra_diagonal_pi_multiplications": diagonal_pi_steps,
                   "terminal_gaussian_doublings": gaussian_terminal_doublings,
                   "bank_differences": 47,
                   "real_add_sub_excluding_doublings": add_real,
                   "real_doublings": 2 * gaussian_terminal_doublings,
                   "real_add_sub_if_doubling_is_add": add_real + 2 * gaussian_terminal_doublings,
                   "native_real_floor_halvings": 4 * pairs},
        "optional_fully_lowered_real_arithmetic": {
            "gaussian_swap_real_adds": 6 * total_swaps,
            "phase_and_native_quarter_turn_component_swaps": quarter_rotations,
            "component_swap_real_adds": 3 * quarter_rotations,
            "explicit_real_negations": 2 * phases["2"] + quarter_rotations,
            "encode_real_add_sub_excluding_doublings": add_real + 6 * total_swaps + 3 * quarter_rotations,
            "encode_real_add_sub_including_doublings": add_real + 6 * total_swaps + 3 * quarter_rotations
                                                         + 2 * gaussian_terminal_doublings,
            "model": "Gaussian payload SWAP=6 real add/sub; real-component SWAP=3 add/sub; each +/-i has one negation, each -1 two; no extra clean swap ancilla; source-minus-target overwrite is permitted, so this is not the strict target-ADD tariff."},
        "decode": {"real_add_sub": add_real,
                   "native_real_floor_halvings": 4 * pairs,
                   "codec_exact_real_halvings": 2 * (newton_pairs + diagonal_pi_steps)
                                                + 2 * gaussian_terminal_doublings,
                   "bank_sums": 47},
        "height": {"coefficient_to_local_value_row_gains": gains,
                   "inverse_path_payload_factor": 32 * max(gains["zero"], gains["rank_one"]),
                   "bank_difference_factor": 64 * max(gains["zero"], gains["rank_one"]),
                   "terminal_difference_factor": gains["terminal"]
                                                   + 32 * max(gains["zero"], gains["rank_one"]),
                   "pair_work_factor": 160 * max(gains["zero"], gains["rank_one"])},
        "limits": ["Mutable in-place coefficient banks; functional Python allocation is not priced.",
                   "Swaps and Gaussian phase applications remain separately listed primitives.",
                   "Counts do not price an arbitrary caller, borrowed copies, all physical routing/control or recursive bill.",
                   "A codec inverse is proved only on its image; this does not admit an intervening consumer.",
                   "Preparation arithmetic does not prove all omitted original-prefix events exact."]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in
                     ("status", "index_log2", "rank_mass", "wrapper_swaps", "encode", "decode")},
                     sort_keys=True))


if __name__ == "__main__":
    main()
