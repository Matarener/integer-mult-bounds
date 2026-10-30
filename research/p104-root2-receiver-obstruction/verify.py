"""Exact cut obstruction for one proposed P104 descent edit. Apache-2.0.

Produced by Nick Petalas. Predecessor word: DreamingOfClouds, PR6144;
Ali Romman and the retained P104 lineage. See README.md and PROOF.md.
"""

import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEGIN, END = 12935, 15647
WITNESS = {32: Fraction(1), 5: Fraction(-1)}
ANCHORS = {
    12888: ["MOVE", 497, 3, 519, False],
    12918: ["ADD", 451, 228, "1", 737],
    12932: ["ADD", 497, 48, "1", 519],
    12933: ["MOVE", 497, 519, 520, False],
    12934: ["ADD", 497, 228, "1", 520],
    13484: ["MOVE", 772, 529, 520, True],
    13485: ["ADD", 497, 772, "-4", 520],
    13486: ["MOVE", 772, 520, 737, True],
    13487: ["ADD", 451, 772, "-4", 737],
    15459: ["MOVE", 497, 520, 914, False],
    END: ["ADD", 145, 161, "-1/2", 914],
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source():
    pin = json.loads((HERE / "UPSTREAM.json").read_bytes())
    raw = (HERE / "inputs/pr6144-WORD.json.gz").read_bytes()
    need(len(raw) == pin["size"], "Source size")
    need(sha256(raw).hexdigest() == pin["sha256"], "Source SHA256")
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    need(blob == pin["git_blob"], "Source Git blob")
    word = json.loads(gzip.decompress(raw))
    need((word["public"], word["owned_fields"]) == (770, 29), "Role bound")
    need(len(word["program"]) == 22818, "Frozen event bound")
    need(len(word["frames"]) == 1093, "Frozen frame bound")
    return word, pin


def proposed(word):
    """Return an explicit attempted edit and its base-indexed cut locations."""
    for index, event in ANCHORS.items():
        need(word["program"][index] == event, "Source anchor " + str(index))
    removed = {12888, 12932, 12933, 12934, 13484, 13485, 13486}
    events, cuts = [], {}
    for index, event in enumerate(word["program"]):
        cuts[index] = len(events)
        if index in removed:
            continue
        if index == 12918:
            events.extend([["MOVE", 497, 3, 737, False],
                           ["ADD", 497, 228, "1", 737]])
        if index == 13487:
            events.extend([["MOVE", 772, 529, 737, True],
                           ["ADD", 497, 772, "-4", 737]])
        replacement = ["MOVE", 497, 737, 914, False]
        events.append(replacement if index == 15459 else list(event))
    changed = deepcopy(word)
    changed["program"] = events
    need(all(e[2] != 161 for e in events[cuts[BEGIN]:cuts[END]]
             if e[0] in ("ADD", "COPY")), "No receiver feedback in window")
    return changed, cuts[BEGIN], cuts[END]


def span(basis):
    values = {0}
    need(len(basis) <= 9, "Frame dimension bound")
    for vector in basis:
        need(type(vector) is int and 0 < vector < 512, "Binary frame vector")
        need(vector not in values, "Independent frame basis")
        values |= {x ^ vector for x in tuple(values)}
    return values


def witness_trace(word, begin, end, witness):
    """Scan every cut, including cuts having no existing receiver ADD."""
    frames = [span(basis) for basis in word["frames"]]
    current = list(word["initial"]) + [None] * 29
    values = [witness.get(r, Fraction(0)) for r in range(799)]
    observed = comparisons = 0
    for index, event in enumerate(word["program"][:end + 1]):
        if begin <= index:
            need(values[161] == 0, "Receiver starts and stays zero")
            for role in range(799):
                if role != 161 and current[role] == current[161]:
                    need(values[role] == 0, "Every available source vanishes")
                    comparisons += 1
            observed += 1
        if index == end:
            break
        op, role = event[:2]
        if op == "MOVE":
            _, role, old, new, private = event
            need(current[role] == old, "Move source frame")
            need(frames[new] < frames[old] if private else
                 frames[old] < frames[new], "Nested move")
            current[role] = new
        elif op in ("INIT", "CLEAR"):
            values[role] = Fraction(0)
            current[role] = event[2] if op == "INIT" else None
        else:
            coefficient, frame = Fraction(event[-2]), event[-1]
            need(current[role] == frame, "Scalar destination frame")
            if op == "SCALE":
                values[role] *= coefficient
            else:
                donor = event[2]
                need(current[donor] == frame, "Scalar source frame")
                need(op in ("ADD", "COPY"), "Scalar opcode")
                value = coefficient * values[donor]
                values[role] = value if op == "COPY" else values[role] + value
    return {"cuts": observed, "coframed_source_checks": comparisons,
            "receiver_value": str(values[161])}


def add_row(destination, row, coefficient):
    for symbol, value in row.items():
        updated = destination.get(symbol, 0) + coefficient * value
        if updated:
            destination[symbol] = updated
        else:
            destination.pop(symbol, None)


def symbolic_prefix(word, end):
    """Independent full symbolic rows, without the witness observer."""
    rows = [{r: Fraction(1)} for r in range(799)]
    for event in word["program"][:end]:
        op, role = event[:2]
        if op == "MOVE":
            continue
        if op in ("INIT", "CLEAR"):
            rows[role] = {}
        elif op == "SCALE":
            rows[role] = {s: Fraction(event[-2]) * value
                          for s, value in rows[role].items()}
        elif op == "COPY":
            rows[role] = {s: Fraction(event[-2]) * value
                          for s, value in rows[event[2]].items()}
        else:
            need(op == "ADD", "Symbolic opcode")
            need(role != event[2], "Distinct ADD roles")
            add_row(rows[role], rows[event[2]], Fraction(event[-2]))
    return rows


def rejected(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("False-claim control was accepted")


def establish(word):
    changed, begin, end = proposed(word)
    observed = witness_trace(changed, begin, end, WITNESS)
    original = symbolic_prefix(word, END)
    edited = symbolic_prefix(changed, end)
    missing = {r: Fraction(1) for r in (32, 48, 85, 98)}
    need(symbolic_prefix(word, 12932)[48] == missing, "Old register-48 read")
    differences = {}
    for role in range(799):
        difference = dict(edited[role])
        add_row(difference, original[role], Fraction(-1))
        if difference:
            differences[role] = difference
    need(differences == {497: {r: -v for r, v in missing.items()},
                         161: {r: v / 2 for r, v in missing.items()}},
         "Exact full-input effect of this edit at the consumer cut")
    target = sum(value * WITNESS.get(r, 0)
                 for r, value in original[161].items())
    need(target == Fraction(-1, 2), "Nonzero required consumer input")
    need(sum(value * WITNESS.get(r, 0)
             for r, value in edited[161].items()) == 0, "Symbolic witness")
    return changed, begin, end, observed, target, missing


def controls(word, changed, begin, end):
    bad = deepcopy(word)
    bad["program"][12932][-2] = "2"
    rejected(lambda: proposed(bad))
    wrong = {32: Fraction(1), 5: Fraction(1)}
    rejected(lambda: witness_trace(changed, begin, end, wrong))
    bad = deepcopy(changed)
    bad["program"][begin:begin] = [["ADD", 161, 48, "1", 3]]
    rejected(lambda: witness_trace(bad, begin, end + 1, WITNESS))
    bad = deepcopy(changed)
    bad["program"][begin:begin] = [["ADD", 161, 497, "1", 3]]
    rejected(lambda: witness_trace(bad, begin, end + 1, WITNESS))
    bad = deepcopy(changed)
    site = bad["program"].index(["ADD", 497, 772, "-4", 737])
    bad["program"][site][-2] = "-3"
    rejected(lambda: need(symbolic_prefix(bad, end)[497] ==
                          symbolic_prefix(changed, end)[497], "Root coefficient"))
    return ["changed_source_anchor", "wrong_witness_sign",
            "unavailable_48_read", "unavailable_497_read", "wrong_root_read"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    word, pin = source()
    changed, begin, end, observed, target, missing = establish(word)
    result = {"status": "PASS_ROOT2_RECEIVER_OBSTRUCTION", "claim_type":
              "Scoped linear obstruction with an exact finite certificate",
              "source_sha256": pin["sha256"], "source_head": pin["head"],
              "base_window": [BEGIN, END], "edited_window": [begin, end],
              "edited_events": len(changed["program"]),
              "witness": {str(k): str(v) for k, v in WITNESS.items()},
              "missing_form": {str(k): str(v) for k, v in missing.items()},
              "required_receiver_value": str(target), "observation": observed,
              "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "controls": controls(word, changed, begin, end)}
    rendered = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    if args.output:
        need(args.output.write_bytes(rendered) == len(rendered), "Receipt write")
    else:
        need(rendered == (HERE / "RESULT.json").read_bytes(),
             "Exact generated receipt")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
