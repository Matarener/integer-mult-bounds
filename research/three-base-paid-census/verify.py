#!/usr/bin/env python3
"""Independent finite accounting audit of the THREE-base native certificate.

No predecessor code is imported. The native event tariff and frame convention
are inherited; operator identities, phases and physical admission are not proved.
Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/kappa-rebuild/complex/full-identity-certificates/"
CANONICAL = PREFIX + "THREE-base-FULL-IDENTITY-CANONICAL.json.gz"
NATIVE = PREFIX + "THREE-base-FULL-IDENTITY-NATIVE.json.gz"
RECEIPT = "research/pr4416-invoice-rebuild/vendor/SUPPLIER-RESULT.json"
PHASES = ["zero_frame_precondition", "entry_adapters", "A", "centers", "B",
          "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done"]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(vectors):
    """Gaussian elimination over F_2, independent of the source's span census."""
    pivots = {}
    for value in vectors:
        while value:
            leading = value.bit_length() - 1
            if leading not in pivots:
                pivots[leading] = value
                break
            value ^= pivots[leading]
    return len(pivots)


def contained(small, large):
    return rank([*large, *small]) == rank(large)


def histogram(counter):
    return {str(k): v for k, v in sorted(counter.items()) if v}


def mass(counter):
    return sum(int(k) * v for k, v in counter.items())


def authenticate(data, expected, label):
    need(hashlib.sha256(data).hexdigest() == expected, "source hash: " + label)


def load_inputs():
    pins = json.loads((HERE / "SOURCES.json").read_bytes())
    inputs = {row["path"]: row for row in pins["files"] if row["usage"] == "input"}
    need(set(inputs) == {CANONICAL, NATIVE, RECEIPT}, "exact three-input closure")
    decoded, hashes = {}, {}
    for name, pin in inputs.items():
        raw = (ROOT / name).read_bytes()
        authenticate(raw, pin["sha256"], name)
        hashes[name] = pin["sha256"]
        decoded[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return decoded[CANONICAL], decoded[NATIVE], decoded[RECEIPT], hashes


def frame_data(canonical):
    need((canonical["h"], canonical["v"], canonical["R"]) == (9, 112, 408),
         "fixed nine-bit THREE-base domain")
    need(not canonical["zero_buffers"], "no external cleanup bank")
    frames = canonical["frames"]
    dimensions = []
    for vectors in frames:
        need(all(type(x) is int and 0 < x < 512 for x in vectors), "frame vector domain")
        dimension = rank(vectors)
        need(dimension == len(vectors), "dependent frame basis")
        dimensions.append(dimension)
    need(dimensions[0] == 0 and dimensions[1] == 9, "zero/full frame anchors")
    for key in ("start", "final"):
        need(len(canonical[key]) == 632, "632 persistent fields")
        need(all(type(i) is int and 0 <= i < len(frames) for i in canonical[key]),
             "persistent frame index")
    return frames, dimensions


def census(canonical, program):
    frames, dimensions = frame_data(canonical)
    current = {("L", i): f for i, f in enumerate(canonical["start"])}
    current["C", 0] = None
    counts, paid = Counter(), Counter()
    by_phase, by_kind = defaultdict(Counter), defaultdict(Counter)
    phases, phase = [], None
    scalar_operands = 0
    center_cleared = False

    def frame(index):
        need(type(index) is int and 0 <= index < len(frames), "event frame index")
        return index

    def role(value):
        need(isinstance(value, list) and len(value) == 2, "role shape")
        result = tuple(value)
        need(result in current, "unknown or unowned field")
        return result

    def at(field, index):
        need(current[field] == frame(index), "chronological frame mismatch")

    for event in program:
        need(isinstance(event, list) and event, "event shape")
        kind = event[0]
        counts[kind] += 1
        if kind == "phase":
            need(len(event) == 2 and event[1] in PHASES, "phase marker")
            phase = event[1]
            phases.append(phase)
        elif kind in ("climb", "center"):
            if kind == "climb":
                need(len(event) == 6 and event[1] in ("A", "B", "cleanup_tail", "final"), "climb shape")
                _, _, index, old, new, declared = event
                field = role(["L", index])
            else:
                need(len(event) == 5, "center shape")
                _, index, old, new, declared = event
                field = role(["C", index])
            at(field, old)
            frame(new)
            up = dimensions[old] < dimensions[new] and contained(frames[old], frames[new])
            down = dimensions[new] < dimensions[old] and contained(frames[new], frames[old])
            need(up if kind == "climb" else up or down, "non-nested paid edge")
            actual = abs(dimensions[new] - dimensions[old])
            need(type(declared) is int and declared == actual, "declared paid rank")
            paid[actual] += 1
            by_phase[phase][actual] += 1
            by_kind[kind][actual] += 1
            current[field] = new
        elif kind == "warp":
            need(len(event) == 5 and type(event[2]) is int, "warp shape")
            field = role(event[1])
            at(field, event[3])
            current[field] = frame(event[4])
        elif kind == "scalar":
            need(len(event) == 3 and isinstance(event[1], list), "scalar shape")
            op, f = event[1], frame(event[2])
            need(op and op[0] in ("add", "copy", "clear", "scale"), "scalar opcode")
            opcode = op[0]
            need(len(op) == {"add": 5, "copy": 3, "clear": 2, "scale": 4}[opcode],
                 "scalar operand count")
            target = role(op[1])
            if opcode == "clear":
                need(target == ("C", 0), "borrowed field overwritten")
                current[target] = f
                center_cleared = True
                continue
            at(target, f)
            scalar_operands += 1
            if opcode in ("add", "copy"):
                source = role(op[2])
                at(source, f)
                scalar_operands += 1
                need(target != source, "self scalar operation")
                if opcode == "copy":
                    need(target == ("C", 0), "borrowed field overwritten")
                    center_cleared = False
                    continue
                if target == ("C", 0):
                    center_cleared = False
            numerator, denominator = op[-2:]
            need(type(numerator) is int and type(denominator) is int and denominator != 0,
                 "scalar rational encoding")
            value = Fraction(numerator, denominator)
            need(value and value.denominator & (value.denominator - 1) == 0, "dyadic scalar")
            if opcode == "scale":
                need(abs(value.numerator) & (abs(value.numerator) - 1) == 0, "unit dyadic scale")
        elif kind == "adapter":
            need(len(event) == 4 and event[1] in ("old_to_new", "new_to_old"), "adapter marker")
            role(["L", event[2]])
            frame(event[3])
        elif kind == "residual_adapter":
            need(len(event) in (4, 5) and event[1] in ("pre", "post"), "residual adapter marker")
            role(["L", event[2]])
            frame(event[3])
            if len(event) == 5:
                frame(event[4])
        else:
            raise ValueError("unknown native event: " + str(kind))
    need(phases == PHASES, "complete ordered phase sequence")
    need([current["L", i] for i in range(632)] == canonical["final"], "final persistent frames")
    need(center_cleared, "final owned-center clear")
    return {"events": len(program), "event_counts": dict(sorted(counts.items())),
            "paid_profile": histogram(paid), "paid_calls": sum(paid.values()),
            "paid_rank_mass": mass(paid), "paid_by_phase": {k: histogram(v) for k, v in by_phase.items()},
            "paid_by_kind": {k: histogram(v) for k, v in sorted(by_kind.items())},
            "checked_scalar_operands": scalar_operands, "final_frames_match": True}


def coalesce_centers(canonical, program):
    """Cancel the common frame in adjacent U_a^* U_b, U_b^* U_c factors.

    This also applies after complex conjugation. It is an abstract telescoping
    argument under the inherited canonical-frame convention, not a phase replay.
    """
    frames, dimensions = frame_data(canonical)
    output, pairs = [], []
    i = 0
    while i < len(program):
        first = program[i]
        if first[0] != "center":
            output.append(first)
            i += 1
            continue
        need(i + 1 < len(program), "missing second center piece")
        second = program[i + 1]
        need(second[0] == "center" and first[1] == second[1] == 0 and first[3] == second[2],
             "adjacent center chain")
        old, mid, new = first[2], first[3], second[3]
        need([dimensions[old], dimensions[mid], dimensions[new]] in ([8, 3, 0], [0, 3, 8]),
             "center 8/3/0 chain")
        high = old if dimensions[old] == 8 else new
        need(contained(frames[mid], frames[high]), "center intermediate containment")
        pairs.append({"event_indices": [i, i + 1], "frames": [old, mid, new],
                      "piece_ranks": [abs(dimensions[old] - dimensions[mid]),
                                      abs(dimensions[mid] - dimensions[new])], "coalesced_rank": 8})
        output.append(["center", 0, old, new, 8])
        i += 2
    need(len(pairs) == 8, "eight center pairs")
    high_frames = [p["frames"][0] if dimensions[p["frames"][0]] == 8 else p["frames"][2] for p in pairs]
    need(high_frames == canonical["center_frames"], "original ordered center frames")
    return output, pairs


def audit(canonical, words, receipt, hashes):
    provider = receipt["providers"]["THREE-base"]
    for name in (CANONICAL, NATIVE):
        need(provider["artifacts"][Path(name).name] == hashes[name], "receipt artifact binding")
    need(set(words) == {"forward", "backward"}, "both orientations")
    frames, dimensions = frame_data(canonical)
    helpers = Counter()
    for i in range(224, 632):
        a, b = canonical["start"][i], canonical["final"][i]
        need(dimensions[a] < dimensions[b] and contained(frames[a], frames[b]), "nested helper endpoint")
        helpers[dimensions[b] - dimensions[a]] += 1
    boundary = provider["helper_boundary"]
    need(histogram(helpers) == boundary["widths"] and sum(helpers.values()) == boundary["count"]
         and mass(helpers) == boundary["total_width"], "helper inventory")
    directions = {}
    for direction, program in words.items():
        split = census(canonical, program)
        need(split["paid_profile"] == canonical["local_profile"], "canonical split profile")
        unsplit_word, pairs = coalesce_centers(canonical, program)
        unsplit = census(canonical, unsplit_word)
        for result, expected in (
            (split, provider["split_replays"][direction]["independent_native_replay"]),
            (unsplit, provider["unsplit_replays"][direction]),
        ):
            need(result["paid_profile"] == expected["paid_profile"], "receipt paid profile")
            need(result["paid_rank_mass"] == expected["paid_rank_mass"], "receipt rank mass")
            need(result["event_counts"] == expected["event_counts"], "receipt event counts")
        need(split["paid_rank_mass"] == unsplit["paid_rank_mass"], "coalescence rank mass")
        directions[direction] = {"split": split, "unsplit": unsplit, "center_pairs": pairs}
    need(directions["forward"]["unsplit"]["paid_profile"] ==
         directions["backward"]["unsplit"]["paid_profile"], "orientation invoice equality")
    p = directions["forward"]["unsplit"]["paid_profile"]
    return {"frame_count": len(frames), "helper_count": sum(helpers.values()),
            "helper_widths": histogram(helpers), "helper_rank_mass": mass(helpers),
            "orientations": directions,
            "fifteen_call_scaling": {"paid_profile": {k: 15 * n for k, n in p.items()},
                                      "paid_rank_mass": 15 * mass(p),
                                      "helper_widths": {k: 15 * n for k, n in histogram(helpers).items()},
                                      "scope": "Arithmetic scaling by #4416's inherited 15 calls; controller not replayed."}}


def controls(canonical, words, receipt, hashes):
    rejected = {}

    def reject(name, expected_message, change):
        c, w, r = deepcopy(canonical), deepcopy(words), deepcopy(receipt)
        change(c, w, r)
        try:
            audit(c, w, r, hashes)
        except ValueError as exc:
            need(expected_message in str(exc), name + ": failed at an unintended check: " + str(exc))
            rejected[name] = str(exc)
        else:
            raise ValueError("control unexpectedly accepted: " + name)

    word = words["forward"]
    climb = next(i for i, e in enumerate(word) if e[0] == "climb")
    center = next(i for i, e in enumerate(word) if e[0] == "center")
    warp = next(i for i, e in enumerate(word) if e[0] == "warp")
    scalar = next(i for i, e in enumerate(word) if e[0] == "scalar" and e[1][0] == "add")
    reject("wrong_declared_rank", "declared paid rank",
           lambda c, w, r: w["forward"][climb].__setitem__(-1, word[climb][-1] + 1))
    reject("deleted_climb", "chronological frame mismatch", lambda c, w, r: w["forward"].pop(climb))
    reject("stale_warp_entrance", "chronological frame mismatch",
           lambda c, w, r: w["forward"][warp].__setitem__(3, 1 if word[warp][3] != 1 else 0))
    reject("wrong_scalar_frame", "chronological frame mismatch",
           lambda c, w, r: w["forward"][scalar].__setitem__(2, 1 if word[scalar][2] != 1 else 0))
    reject("borrowed_clear", "borrowed field overwritten",
           lambda c, w, r: w["forward"][scalar].__setitem__(1, ["clear", ["L", 0]]))
    reject("missing_center_piece", "chronological frame mismatch", lambda c, w, r: w["forward"].pop(center))
    reject("interrupted_center_pair", "adjacent center chain",
           lambda c, w, r: w["forward"].insert(center + 1,
               ["scalar", ["scale", ["C", 0], 2, 1], word[center][3]]))
    reject("dependent_basis", "dependent frame basis", lambda c, w, r: c["frames"][1].append(256))
    reject("wrong_final_frame", "final persistent frames", lambda c, w, r: c["final"].__setitem__(0, 0))
    reject("unknown_event", "unknown native event", lambda c, w, r: w["forward"].insert(1, ["unpaid_jump"]))
    reject("wrong_artifact", "receipt artifact binding",
           lambda c, w, r: r["providers"]["THREE-base"]["artifacts"].__setitem__(Path(NATIVE).name, "0" * 64))

    def drift(profile):
        profile["1"] += 2
        profile["2"] -= 1  # Equal rank mass is deliberately insufficient.

    reject("mass_preserving_canonical_drift", "canonical split profile", lambda c, w, r: drift(c["local_profile"]))
    reject("mass_preserving_receipt_drift", "receipt paid profile",
           lambda c, w, r: drift(r["providers"]["THREE-base"]["unsplit_replays"]["forward"]["paid_profile"]))

    def helper_drift(c, w, r):
        h = r["providers"]["THREE-base"]["helper_boundary"]["widths"]
        h["5"] += 1
        h["6"] -= 2
        h["7"] += 1  # Preserves both helper count and total rank mass.

    reject("mass_and_count_preserving_helper_drift", "helper inventory", helper_drift)
    frames, dims = frame_data(canonical)
    nonnested = next((i, j) for i, e in enumerate(word) if e[0] == "climb" and dims[e[3]] > 0
                     for j, f in enumerate(frames) if dims[j] == dims[e[4]] and not contained(frames[e[3]], f))
    reject("equal_dimension_nonnested_edge", "non-nested paid edge",
           lambda c, w, r: w["forward"][nonnested[0]].__setitem__(4, nonnested[1]))

    # Independent finite cross-check of the elimination routine, including
    # dependent vectors and zeros: all 512 ordered triples in F_2^3.
    for vectors in product(range(8), repeat=3):
        span = {0}
        for vector in vectors:
            span |= {x ^ vector for x in span}
        need(1 << rank(vectors) == len(span), "small-space rank cross-check")

    raw = (ROOT / NATIVE).read_bytes()
    try:
        authenticate(raw + b"corruption", hashes[NATIVE], NATIVE)
    except ValueError as exc:
        rejected["corrupted_source_bytes"] = str(exc)
    else:
        raise ValueError("source corruption unexpectedly accepted")

    # A scoped census must not be presented as an operator proof. Changing an
    # ADD sign keeps frames and prices; the hash guard catches file changes,
    # but the accounting layer intentionally cannot detect this algebraic error.
    altered = deepcopy(words)
    altered["forward"][scalar][1][3] *= -1
    need(audit(canonical, altered, receipt, hashes) == audit(canonical, words, receipt, hashes),
         "accounting-only scope probe")
    return {"rejected": rejected, "rank_cross_check_ordered_triples": 512,
            "scope_probe": "An in-memory ADD sign flip preserves this census; no operator identity is certified."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the deterministic RESULT.json after all checks")
    args = parser.parse_args()
    canonical, words, receipt, hashes = load_inputs()
    report = {"status": "PASS_THREE_BASE_PAID_CENSUS", "source_sha256": hashes,
              "claim": "Finite native-event accounting and nested helper widths; no new kappa.",
              "result": audit(canonical, words, receipt, hashes),
              "controls": controls(canonical, words, receipt, hashes)}
    target = HERE / "RESULT.json"
    if args.write:
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    else:
        need(json.loads(target.read_bytes()) == report, "committed RESULT.json differs from fresh census")
    print(report["status"], "orientations=2 controls=" + str(len(report["controls"]["rejected"])))


if __name__ == "__main__":
    main()
