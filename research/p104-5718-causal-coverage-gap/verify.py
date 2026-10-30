#!/usr/bin/env python3
"""Show that the fixed #5719 causal certificate does not cover merged #5718.

The published checker is executed only as a custody control. The census below
is a separate reading of the two authenticated words. No new kappa is claimed.
"""

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD_WORD = ROOT / "research/p104-temporal-fixed-independent-audit/inputs/WORD.json.gz"
OLD_CHECKER = ROOT / "research/p104-temporal-fixed-independent-audit/verify.py"
NEW_WORD = ROOT / "research/p104-two-boundary-helper-split/WORD.json.gz"
OWNED_WORD = ROOT / "research/p104-caller-owned-interface/source/WORD.json.gz"
OWNED_BINDING = ROOT / "research/p104-caller-owned-interface/source/BINDING.json"

PINS = {
    OLD_WORD: "d6db1d0d97b13ea483a462c65437664d15d34dec56c3682cf6e1de31266ec6c2",
    OLD_CHECKER: "bce6cdf82cb1492d209c241670df894548a485b89622a39851f26352f61e999b",
    NEW_WORD: "cff7196f8b168c4ebf8227185eed98387b66ec5db0179108adfea4045775cc31",
    OWNED_WORD: "9fd67dd89ed24a644257cd9aef06934ed4c6fbe0441804684a968868f2ef66a8",
    OWNED_BINDING: "aff998b6d3069cea1a0a10b2a2fcd3b8100d3c84e521ef54b679a5c996839a99",
}

# Index literals of the #5719 subject. These are the certificate's coordinates,
# not a claim that the same numbers name the same events on a later word.
INTERVAL = (823, 14983)
PROVENANCE = (11202, 14983)
STABILITY = (14654, 14983)
ANCHORS = {
    823: ["ADD", 207, 720, "-2", 3],
    11202: ["ADD", 340, 337, "1", 396],
    13572: ["ADD", 712, 747, "1", 598],
    13577: ["MOVE", 715, 3, 598, False],
    13578: ["ADD", 715, 747, "1", 598],
    13737: ["ADD", 525, 712, "-4", 598],
    14654: ["ADD", 525, 340, "1", 396],
    14982: ["MOVE", 715, 598, 396, False],
    14983: ["ADD", 340, 715, "-4", 396],
}
ABSENT_ON_SUCCESSOR = (13572, 13577, 13578, 14982)
SCALAR = {"ADD", "COPY", "SCALE", "INIT", "CLEAR"}


def fail(message):
    raise SystemExit("FAIL_P104_5718_CAUSAL_COVERAGE_GAP " + message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(path):
    raw = path.read_bytes()
    digest = sha256(raw)
    if digest != PINS[path]:
        fail(path.name + " sha256 " + digest)
    return raw


def load_word(path):
    word = json.loads(gzip.decompress(pinned(path)))
    if not isinstance(word, dict) or not isinstance(word.get("program"), list):
        fail(path.name + " has no program")
    if not isinstance(word.get("frames"), list) or len(word["frames"]) <= 598:
        fail(path.name + " frame inventory does not contain 598")
    return word


def span_mask(basis):
    values = [0]
    for vector in basis:
        if not isinstance(vector, int) or vector <= 0:
            fail("frame basis vector is not a positive integer")
        # Materialize before extending. A live generator would walk the new items.
        values.extend([item ^ vector for item in values])
    mask = 0
    for item in values:
        mask |= 1 << item
    return mask


def strict_subspace(frames, left, right):
    return (len(frames[left]) < len(frames[right])
            and span_mask(frames[left]) & span_mask(frames[right]) == span_mask(frames[left]))


def locations(program, event):
    return [index for index, item in enumerate(program) if item == event]


def scalar_writes(program, role, lo, hi):
    return [index for index, event in enumerate(program)
            if lo <= index < hi and event[0] in SCALAR and event[1] == role]


def forbidden_715(program, lo, hi):
    """Field-715 touches in [lo, hi) other than MOVE or a destination-only ADD."""
    found = []
    for index, event in enumerate(program):
        if not (lo <= index < hi):
            continue
        op = event[0]
        if op == "MOVE":
            continue
        if op == "ADD" and event[1] == 715 and event[2] != 715:
            continue
        if op in ("ADD", "COPY") and (event[1] == 715 or event[2] == 715):
            found.append((index, event))
        elif op in ("SCALE", "INIT", "CLEAR") and event[1] == 715:
            found.append((index, event))
    return found


def lifetime(program, role):
    return [(event[0], event[2]) for event in program
            if event[0] in ("INIT", "CLEAR") and event[1] == role]


def moves_of(program, role):
    return [(index, event) for index, event in enumerate(program)
            if event[0] == "MOVE" and event[1] == role]


def run_predecessor(word_path):
    completed = subprocess.run(
        [sys.executable, "-B", str(OLD_CHECKER), str(word_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=60, check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        fail("predecessor checker did not return JSON; exit " + str(completed.returncode))
    receipt = payload.get("receipt")
    if not isinstance(receipt, dict):
        fail("predecessor checker returned no receipt")
    return completed.returncode, receipt


def require_old_certificate(old):
    program = old["program"]
    if old["schema"] != "p104-r22-reframe/1" or old["public"] != 743:
        fail("pinned #5684 word lost its schema or public count")
    if [len(old["frames"][frame]) for frame in (3, 598, 396)] != [0, 1, 3]:
        fail("pinned #5684 frame dimensions changed")
    if not (strict_subspace(old["frames"], 3, 598) and strict_subspace(old["frames"], 598, 396)):
        fail("pinned #5684 frame chain is not strict")
    for index, event in ANCHORS.items():
        if locations(program, event) != [index]:
            fail("pinned #5684 anchor " + str(index) + " is not unique at that index")
    if scalar_writes(program, 712, *INTERVAL) != [13572]:
        fail("pinned #5684 field-712 interval census changed")
    if scalar_writes(program, 525, *INTERVAL) != [13737, 14654]:
        fail("pinned #5684 field-525 interval census changed")
    if scalar_writes(program, 340, *PROVENANCE) != [11202]:
        fail("pinned #5684 field-340 provenance census changed")
    if scalar_writes(program, 340, *STABILITY) != []:
        fail("pinned #5684 field-340 stability interval is not empty")
    if forbidden_715(program, *INTERVAL) != []:
        fail("pinned #5684 interval already has a forbidden field-715 touch")
    if moves_of(program, 715) != [
        (13577, ANCHORS[13577]), (14982, ANCHORS[14982]), (14988, ["MOVE", 715, 396, 127, False])
    ]:
        fail("pinned #5684 field-715 moves changed")


def injection_controls(program):
    allowed = [list(event) for event in program]
    allowed[900] = ["ADD", 715, 525, "1/4", 3]
    if forbidden_715(program, *INTERVAL) != [] or forbidden_715(allowed, *INTERVAL) != []:
        fail("destination-only field-715 ADD was treated as an observer")
    observed = [list(event) for event in program]
    observed[900] = ["ADD", 206, 715, "2", 3]
    if forbidden_715(observed, *INTERVAL) != [(900, ["ADD", 206, 715, "2", 3])]:
        fail("injected field-715 source read was not detected")


def require_successor_gap(old, new):
    program = new["program"]
    if new["schema"] != "p104-terminal-main-split-short-cleanup/1" or new["public"] != 744:
        fail("successor schema/public count is not the merged #5718 word")
    if len(new["initial"]) != 744 or len(new["final"]) != 744 or len(program) != 25546:
        fail("successor endpoint or program length changed")
    if [len(new["frames"][frame]) for frame in (3, 598, 396)] != [0, 1, 3]:
        fail("successor lost the 0/1/3 frame dimensions")
    if not (strict_subspace(new["frames"], 3, 598) and strict_subspace(new["frames"], 598, 396)):
        fail("successor lost the strict frame chain; that part of the certificate does transfer")

    displacements = []
    for index in sorted(ANCHORS):
        found = locations(program, ANCHORS[index])
        if index in ABSENT_ON_SUCCESSOR:
            if found:
                fail("anchor " + str(index) + " is present on the successor")
            continue
        if len(found) != 1:
            fail("surviving anchor " + str(index) + " is not unique")
        displacements.append(found[0] - index)
    if displacements != [91, 91, 89, 90, 92]:
        fail("surviving-anchor displacements changed: " + str(displacements))
    if len(set(displacements)) == 1:
        fail("a single index translation would cover the surviving anchors")

    if scalar_writes(program, 712, *INTERVAL) != [13663]:
        fail("successor field-712 interval write is not the shifted role")
    if program[13663] != ["ADD", 712, 748, "1", 598]:
        fail("successor field-712 write is not source 748")
    if scalar_writes(program, 340, *PROVENANCE) != [11260, 11293]:
        fail("successor provenance window is not the two observed writes")
    if program[11260] != ["ADD", 340, 344, "1", 70]:
        fail("extra field-340 write at 11260 changed")
    if program[11293] != ANCHORS[11202]:
        fail("credited field-340 provenance ADD is not at 11293")
    # The numeric stability interval is empty on both words. On the successor
    # its endpoints are different operations, and the old read now sits inside it.
    if scalar_writes(program, 340, *STABILITY) != []:
        fail("numeric stability interval unexpectedly contains a field-340 write")
    if program[14654] == old["program"][14654] or program[14983] == old["program"][14983]:
        fail("numeric stability endpoints still denote the old events")
    if not (STABILITY[0] < 14744 < STABILITY[1]) or not (15075 >= STABILITY[1]):
        fail("the old read/cut no longer witnesses that the numeric interval moved")

    observed = forbidden_715(program, *INTERVAL)
    if observed != [(911, ["ADD", 206, 715, "2", 3])]:
        fail("field-715 observer failure is not the single read at 911")
    successor_moves = moves_of(program, 715)
    if successor_moves != [
        (15072, ["MOVE", 715, 3, 396, False]),
        (15080, ["MOVE", 715, 396, 127, False]),
    ]:
        fail("field-715 chart path is not the direct 3-to-396 move")
    if any(event[2] == 598 for _, event in successor_moves):
        fail("a field-715 move through frame 598 is present")

    if lifetime(program, 743) != []:
        fail("successor role 743 is an owned lifetime")
    for role in range(743, 752):
        if lifetime(old["program"], role) != lifetime(program, role + 1):
            fail("owned frame sequence does not shift by one at role " + str(role))
    if lifetime(old["program"], 747) == lifetime(program, 747):
        fail("role 747 names the same lifetime on both words")
    mutated = [list(event) for event in program]
    for event in mutated:
        if event[0] == "INIT" and event[1] == 748:
            event[2] += 1
            break
    else:
        fail("successor has no role-748 birth to mutate")
    if all(lifetime(old["program"], role) == lifetime(mutated, role + 1)
           for role in range(743, 752)):
        fail("owned-sequence comparison ignores the birth frame")


def require_distinct_owned_candidate():
    binding = json.loads(pinned(OWNED_BINDING))
    if binding.get("word_bytes_sha256") != PINS[OWNED_WORD]:
        fail("published #5717 binding does not name its packaged word")
    if PINS[OWNED_WORD] in (PINS[OLD_WORD], PINS[NEW_WORD]):
        fail("the #5717 candidate word is not a third artifact")


def require_checker_custody(old_receipt, successor_code, successor_receipt):
    if old_receipt.get("status") != "PASS_FIXED_CAUSAL_LEDGER_AND_TYPED_CONTACTS_ONLY":
        fail("predecessor checker did not accept its pinned word")
    if old_receipt.get("new_kappa") is not None:
        fail("predecessor checker reported a new kappa")
    census = old_receipt.get("write_census")
    if census != {"712": [13572], "525": [13737, 14654], "340": [11202]}:
        fail("predecessor write census disagrees with the independent reading")
    if successor_code == 0 or successor_receipt.get("status") == old_receipt["status"]:
        fail("predecessor checker accepted the successor bytes")
    if successor_receipt.get("status") != "BINDING_UNRESOLVED":
        fail("successor refusal was not a binding failure: " + str(successor_receipt.get("status")))
    if successor_receipt.get("scientific_falsifier") is not False:
        fail("binding refusal was labeled as a scientific falsifier")
    if successor_receipt.get("coverage_complete") is not False:
        fail("binding refusal claimed complete coverage")


def main():
    pinned(OLD_CHECKER)
    old = load_word(OLD_WORD)
    new = load_word(NEW_WORD)
    require_old_certificate(old)
    injection_controls(old["program"])
    require_successor_gap(old, new)
    require_distinct_owned_candidate()
    old_code, old_receipt = run_predecessor(OLD_WORD)
    if old_code != 0:
        fail("predecessor checker exit " + str(old_code) + " on its pinned word")
    with tempfile.TemporaryDirectory() as directory:
        successor_copy = Path(directory) / "WORD.json.gz"
        successor_copy.write_bytes(NEW_WORD.read_bytes())
        successor_code, successor_receipt = run_predecessor(successor_copy)
    require_checker_custody(old_receipt, successor_code, successor_receipt)
    print(
        "PASS_P104_5718_CAUSAL_COVERAGE_GAP"
        " absent_anchors=4"
        " displacements=91,91,89,90,92"
        " observer_read=911"
        " owned_shift=1"
        " direct_715_move=15072"
        " checker_binding_refusal=true"
        " no_new_kappa=true"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
