#!/usr/bin/env python3
"""Price one PR #3929 transported frame: entrance, terminal, and caller.

The frame bill is the vendored PR #3929 module. The compiler below is the
published compile_frames algorithm, transcribed so this file does not import
research/transported-warp-frames/frames.py. No new kappa is claimed.
"""
import copy
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE / "vendor"))
import audit_core as audit  # noqa: E402

BASE_SHA256 = "5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699"
RECIPE_SHA256 = "465166937e5c92e6eec1b4b481fc54b689e13e958ad75d0628756c4ea171bc9f"
BILL_SHA256 = "888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951"
ENTRANCE = [258, 130, 82, 42, 7]
OLD_ENTRANCE = [261, 133, 85, 45]
EXIT = [320, 192, 42, 25, 7]
OLD_EXIT = [320, 192, 45, 30]
CALLER_FIELDS = (
    "ports", "start_extra", "helper_final", "target_levels", "cut",
    "precondition", "compensation", "centers", "center_frames",
    "initial_corrections", "A", "restore", "removed", "prelude_events",
)
OLD_PROFILE = {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}
NEW_PROFILE = {1: 2468, 2: 709, 3: 220, 4: 106, 5: 20, 8: 8}
INVENTORY = {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}
END_CLIMBS = {1: 289, 2: 77, 3: 54}


def need(ok, why):
    if not ok:
        raise SystemExit("FAIL: " + why)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load():
    base_path = PACKAGE / "inputs" / "BASE-WORD.json.gz"
    recipe_path = PACKAGE / "inputs" / "RECIPE.json"
    bill_path = PACKAGE / "vendor" / "audit_core.py"
    need(sha256(base_path) == BASE_SHA256, "base word bytes")
    need(sha256(recipe_path) == RECIPE_SHA256, "recipe bytes")
    need(sha256(bill_path) == BILL_SHA256, "frame-bill bytes")
    with gzip.open(base_path, "rt", encoding="utf-8") as handle:
        word = json.load(handle)
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    return word, recipe


def compile_frames(source, recipe):
    """PR #3929 compile_frames, including the paid entrance scale."""
    word = copy.deepcopy(source)
    seen = set()
    for edit in recipe["scalar_edits"]:
        section, index = edit["section"], edit["index"]
        need(section in ("A", "B", "restore"), "invalid scalar section")
        need((section, index) not in seen, "duplicate scalar edit")
        seen.add((section, index))
        gate = word[section][index]
        need(gate[0] != "warp" and gate[-1] == edit["old"], "scalar source guard")
        gate[-1] = list(edit["new"])
    warp_edits = {}
    for edit in recipe["warp_edits"]:
        index = edit["index"]
        need(index not in warp_edits, "duplicate warp edit")
        need(source["warps"][index][3:] == edit["old"], "warp source guard")
        warp_edits[index] = edit["new"]
    current = {register: audit.span((point,)) for register, point in enumerate(word["ports"])}
    current.update({register: audit.ZERO for register in range(audit.V, audit.N)})
    for register, frame in word["start_extra"].items():
        current[int(register)] = audit.span(frame)
    for gate in word["A"]:
        if gate[0] == "warp":
            current[gate[1]] = audit.span(gate[4])
        else:
            for register in audit.touched(gate):
                current[register] = audit.span(gate[-1])
    levels = {audit.V + int(target): audit.span(frame) for target, frame in word["target_levels"].items()}
    for register in word["centers"]:
        served = {levels.get(gate[1], audit.ZERO) for gate in word["cut"] if gate[2] == register}
        for frame in sorted(served, key=lambda mask: -audit.dim(mask)):
            current[register] = frame
    at = {}
    for index, record in enumerate(source["warps"]):
        at.setdefault(record[0], []).append(index)
    out = []
    for index in range(len(word["B"]) + 1):
        for warp_index in at.get(index, ()):
            old = source["warps"][warp_index]
            entrance, exit_frame = warp_edits.get(warp_index, old[3:])
            entrance_mask, exit_mask = audit.span(entrance), audit.span(exit_frame)
            images = audit.warp_images(old[2])
            need(audit.image_mask(images, entrance_mask) == exit_mask, "incompatible transported frame")
            need(current[old[1]] & ~entrance_mask == 0, "warp entrance would shrink")
            if current[old[1]] != entrance_mask:
                out.append(["scale", old[1], 1, 1, list(entrance)])
            word["warps"][warp_index] = [len(out), old[1], copy.deepcopy(old[2]), list(entrance), list(exit_frame)]
            current[old[1]] = exit_mask
        if index < len(word["B"]):
            gate = word["B"][index]
            out.append(gate)
            for register in audit.touched(gate):
                current[register] = audit.span(gate[-1])
    word["B"] = out
    word["cleanup"] = audit.derive_cleanup(word)
    audit.hygiene(word)
    profile, inventory, chain, _, _ = audit.frame_bill(word, lagrangian=True)
    word["report"]["local_profile"] = {str(rank): count for rank, count in profile.items()}
    word["report"]["width_inventory"] = {str(width): count for width, count in inventory.items()}
    return word, profile, inventory, chain


def positive_climbs(chain):
    located = defaultdict(list)
    for events in chain.values():
        for event in events:
            if len(event) == 3 and isinstance(event[0], tuple) and event[1]:
                located[event[0]].append(event[1])
    return located


def end_climb_counts(chain):
    counts = Counter()
    for ranks in positive_climbs(chain).items():
        where, values = ranks
        if where == ("end",):
            counts.update(values)
    return dict(counts)


def b_climb_rows(chain):
    rows = defaultdict(list)
    for events in chain.values():
        for event in events:
            if len(event) == 3 and isinstance(event[0], tuple) and event[0][0] == "B":
                rows[event[0][1]].append(event[1])
    return rows


def one_inserted_scale(old, new, opcode):
    if len(new) != len(old) + 1:
        return False
    old_index = new_index = found = 0
    while old_index < len(old) and new_index < len(new):
        if old[old_index] == new[new_index]:
            old_index += 1
            new_index += 1
        elif found == 0 and tuple(new[new_index][:-1]) == opcode:
            found = 1
            new_index += 1
        else:
            return False
    return found == 1 and old_index == len(old) and new_index == len(new)


def histogram_parts(old_rows, new_rows, edit_indices, scale_index):
    entrance = Counter()
    edited = Counter()
    propagated = Counter()
    mapped = set()
    for index, climbs in old_rows.items():
        new_index = index if index < scale_index else index + 1
        mapped.add(new_index)
        before = Counter(rank for rank in climbs if rank)
        after = Counter(rank for rank in new_rows.get(new_index, []) if rank)
        bucket = edited if index in edit_indices else propagated
        for rank in set(before) | set(after):
            change = after[rank] - before[rank]
            if change:
                bucket[rank] += change
    extra = set(new_rows) - mapped
    need(extra == {scale_index}, "unexpected B climb index " + str(sorted(extra)))
    for rank in new_rows[scale_index]:
        if rank:
            entrance[rank] += 1
    return entrance, edited, propagated


def tariff_hypotheses(delta):
    """Integer hypotheses of PROOF.md. The sign argument is that prose."""
    need(delta == {1: 28, 2: -16, 3: -4, 4: 4}, "histogram delta")
    need(28 - 16 - 4 + 4 == 12, "f(0)")
    need(28 - 16 * 2 - 4 * 3 + 4 * 4 == 0, "f(1)")
    need(2 ** 8 > 3 ** 5, "log2(3) < 8/5")
    need(2 ** 3 < 3 ** 2, "log2(3) > 3/2")
    need(8 * 3 < 5 * 5, "L(L-1) < 24/25")
    need(24 < 25 * 2, "24/25 < 2")
    need(4 * 4 - 9 < 16, "h(2) upper bound 7/4 is below 4")


def main():
    word, recipe = load()
    need(word["base"] == "PR2312-width-exchange-plus-coherent-joint616", "base label")
    need(len(recipe["warp_edits"]) == 1, "one warp edit")
    warp = recipe["warp_edits"][0]
    need(warp["index"] == 0, "warp index")
    need(warp["old"] == [OLD_ENTRANCE, OLD_EXIT], "old frames")
    need(warp["new"] == [ENTRANCE, EXIT], "new frames")
    need(len(recipe["scalar_edits"]) == 36, "36 scalar edits")
    need({edit["section"] for edit in recipe["scalar_edits"]} == {"B"}, "B-only scalar edits")
    edit_indices = {edit["index"] for edit in recipe["scalar_edits"]}
    need(len(edit_indices) == 36 and 916 in edit_indices, "edit index set")

    old_profile, old_inventory, old_chain, _, _ = audit.frame_bill(word, lagrangian=True)
    compiled, new_profile, new_inventory, new_chain = compile_frames(word, recipe)
    need(old_profile == OLD_PROFILE and new_profile == NEW_PROFILE, "profiles")
    need(old_inventory == new_inventory == INVENTORY, "width inventory")
    need(sum(rank * count for rank, count in old_profile.items()) == 5134, "old mass")
    need(sum(rank * count for rank, count in new_profile.items()) == 5134, "new mass")

    for field in CALLER_FIELDS:
        need(word[field] == compiled[field], "caller field changed: " + field)
    need(end_climb_counts(old_chain) == end_climb_counts(new_chain) == END_CLIMBS, "terminal end climbs")
    need(compiled["warps"][0][2] == word["warps"][0][2], "native map")
    need(len(word["B"]) == 1869 and len(compiled["B"]) == 1870, "B length")
    need(sum(gate[0] == "scale" for gate in compiled["B"]) == 74, "one new scale")
    need(word["warps"][0][0] == 916 and compiled["warps"][0][0] == 917, "warp position")
    need(compiled["B"][916] == ["scale", 243, 1, 1, ENTRANCE], "entrance scale")
    need(one_inserted_scale(word["cleanup"], compiled["cleanup"], ("scale", 243, 1, 1)), "cleanup inverse")

    entrance, edited, propagated = histogram_parts(
        b_climb_rows(old_chain), b_climb_rows(new_chain), edit_indices, 916)
    need(dict(entrance) == {1: 1}, "entrance climb")
    need(dict(edited) == {1: 11, 3: -4, 4: 4}, "edited-index climbs")
    need(dict(propagated) == {1: 16, 2: -16}, "propagated climbs")
    total = Counter()
    for part in (entrance, edited, propagated):
        for rank, change in part.items():
            total[rank] += change
    need(dict(total) == {1: 28, 2: -16, 3: -4, 4: 4}, "parts sum")
    tariff_hypotheses(dict(total))

    # The published exit is the image of the new entrance. A swapped exit is illegal.
    broken = copy.deepcopy(recipe)
    broken["warp_edits"][0]["new"] = [ENTRANCE, OLD_EXIT]
    try:
        compile_frames(word, broken)
    except SystemExit as exc:
        need("incompatible transported frame" in str(exc), "wrong rejection")
    else:
        need(False, "swapped exit was accepted")

    print(
        "PASS_TRANSPORTED_FRAME_CALLER_PRICE "
        "entrance=+1H1 terminal_end_climbs=0 caller_fields=0 "
        "histogram=+28H1-16H2-4H3+4H4 mass=5134 "
        "power_tariff_strict_for_q_in_[0,1) no_new_kappa"
    )


if __name__ == "__main__":
    main()
