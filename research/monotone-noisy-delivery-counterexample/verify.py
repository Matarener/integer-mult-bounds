"""Finite certificate in the retained immutable-channel scalar quotient.

This contribution was produced by Nick Petalas. Apache-2.0.
The word, quotient and seven clean directions retain their cited credit.
"""

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import platform
import tarfile


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = ROOT / "research/filtered-native-kappa004/inputs/original-packet.tar.gz"
ARCHIVE_HASH = "595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7"
WORD_HASH = "934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775"
PREFIX = "filtered_native_implementation/"
WORD_MEMBER = PREFIX + "research/retained_state_next/F9-SOURCE-DAG-ALL8-WORD.json.gz"
MODE_MEMBER = PREFIX + "upstream/research/involutory-producer-raw-dual/inputs/R/R.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source():
    raw = ARCHIVE.read_bytes()
    require(sha256(raw).hexdigest() == ARCHIVE_HASH, "archive hash")
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        word_file = archive.extractfile(WORD_MEMBER)
        mode_file = archive.extractfile(MODE_MEMBER)
        require(word_file is not None and mode_file is not None, "archive members")
        word_raw = word_file.read()
        modes = json.loads(mode_file.read())
    require(sha256(word_raw).hexdigest() == WORD_HASH, "word hash")
    word = json.loads(gzip.decompress(word_raw))
    modes = [[F(x) for x in row] for row in modes]
    require(len(modes) == 8 and all(len(row) == 112 for row in modes), "mode shape")
    require(len(word["programs"]["backward"]) == 22585, "event count")
    require(len(word["canonical"]["start"]) == 632, "original fields")
    require(word["owned_extra_slots_by_direction"]["backward"] == 8, "owned fields")
    for i, row in enumerate(modes):
        for j, other in enumerate(modes):
            require(sum(x * y for x, y in zip(row, other)) == 56 * (i == j), "RRt")
    return word, modes


def field(ref):
    require(isinstance(ref, list) and len(ref) == 2, "field reference")
    kind, number = ref
    require(type(number) is int, "field number")
    require(kind in {"L", "C"}, "field kind")
    require(0 <= number < (632 if kind == "L" else 9), "field range")
    return number + (632 if kind == "C" else 0)


def add(destination, source, coefficient):
    for key, value in source.items():
        updated = destination.get(key, F(0)) + coefficient * value
        if updated:
            destination[key] = updated
        else:
            destination.pop(key, None)


def schedule(word, witness):
    channels = witness["channels"]
    require(len(channels) == 22, "channel count")
    require(witness["schema"] == "immutable-channel-counterexample/v1", "schema")
    require(witness["source_word_sha256"] == WORD_HASH, "witness source")
    contacts = defaultdict(list)
    for channel_id, channel in enumerate(channels):
        frame = channel["frame"]
        require(type(frame) is int and 0 <= frame < len(word["canonical"]["frames"]), "frame")
        require(channel["grade"] == len(word["canonical"]["frames"][frame]), "grade")
        require(len(channel["payload"]) == 8, "payload dimension")
        require(1 <= len(channel["contacts"]) <= 69, "contacts per channel")
        for cut, owner, coefficient in channel["contacts"]:
            require(type(cut) is int and 0 <= cut <= 22585, "contact cut")
            require(type(owner) is int and 0 <= owner < 632, "contact owner")
            amount = F(coefficient)
            require(amount != 0, "zero contact")
            contacts[cut].append((channel_id, owner, amount, frame))
    require(sum(map(len, contacts.values())) == 69, "contact count")
    return contacts


def scalar_step(event, rows, frames):
    operation = event[1]
    kind, destination = operation[0], field(operation[1])
    if kind == "clear":
        rows[destination] = {}
        frames[destination] = event[2]
    elif kind == "add":
        source = field(operation[2])
        require(destination != source, "distinct ADD fields")
        require(frames[destination] == frames[source] == event[2], "coframed ADD")
        add(rows[destination], rows[source], F(operation[3], operation[4]))
    elif kind == "scale":
        coefficient = F(operation[2], operation[3])
        require(coefficient != 0 and frames[destination] == event[2], "scale")
        rows[destination] = {i: coefficient * x for i, x in rows[destination].items()}
    else:
        raise ValueError("unsupported scalar event: " + kind)


def event_step(event, rows, frames):
    kind = event[0]
    if kind == "scalar":
        scalar_step(event, rows, frames)
    elif kind in {"climb", "warp"}:
        owner = event[2] if kind == "climb" else field(event[1])
        require(frames[owner] == event[3], "native entry frame")
        frames[owner] = event[4]
    elif kind == "physical_add":
        destination, source = field(event[1]), field(event[2])
        require(not rows[source], "centre tail has zero impulse input")
        add(rows[destination], rows[source], F(event[3], event[4]))
    else:
        require(kind in {"adapter", "phase"}, "known quotient event")
        # The cited common-fixed-vector quotient erases these two event types.


def replay(word, witness):
    contacts = schedule(word, witness)
    rows = [{} for _ in range(641)]
    frames = word["canonical"]["start"][:] + [None] * 9
    events = word["programs"]["backward"]
    for cut in range(len(events) + 1):
        for channel_id, owner, amount, frame in contacts.get(cut, ()):
            require(frames[owner] == frame, "contact frame")
            rows[owner][channel_id] = rows[owner].get(channel_id, F(0)) + amount
        if cut < len(events):
            event_step(events[cut], rows, frames)
    require(all(not row for row in rows[632:]), "owned impulse return")
    return rows


def evaluate(word, modes, witness):
    rows = replay(word, witness)
    channels = witness["channels"]
    payloads = [[F(x) for x in channel["payload"]] for channel in channels]
    joint = [i for i, channel in enumerate(channels) if channel["kind"] == "joint"]
    require(len(joint) == 15, "joint channels")
    target_mode = [F(x) for x in witness["joint_mode"]]
    require(target_mode == [F(0)] * 4 + [F(1)] * 4, "joint mode")
    retained = [i for i in range(632) if i < 224 or word["canonical"]["start"][i] != 0]
    for owner in retained:
        actual_joint = sum(rows[owner].get(i, F(0)) for i in joint)
        expected_joint = sum(modes[j][owner] * target_mode[j] for j in range(8)) if owner < 112 else 0
        require(actual_joint == expected_joint, "joint clean response")
        for j in range(8):
            actual = sum(amount * payloads[i][j] for i, amount in rows[owner].items())
            expected = modes[j][owner] if owner < 112 else 0
            require(actual == expected, "complete eight-mode response")
    return invoice(word, witness, rows, retained)


def invoice(word, witness, rows, retained):
    profile = Counter(channel["grade"] for channel in witness["channels"])
    require(profile == {0: 1, 7: 14, 8: 7}, "complete delivery profile")
    tariff = [F(witness["tariff"][str(i)]) for i in range(10)]
    require(tariff[0] == 0 and all(x > 0 for x in tariff[1:]), "positive tariff")
    require(all(x <= y for x, y in zip(tariff, tariff[1:])), "monotone tariff")
    charge = sum(tariff[grade] * count for grade, count in profile.items())
    baseline = 8 * tariff[8]
    require(charge < baseline, "strict delivery saving")
    ignored = [i for i in range(224, 632) if word["canonical"]["start"][i] == 0]
    payloads = [[F(x) for x in channel["payload"]] for channel in witness["channels"]]
    residuals = sum(any(sum(amount * payloads[c][j] for c, amount in rows[i].items())
                        for j in range(8)) for i in ignored)
    return {"events": 22585, "channels": 22, "contacts": 69,
            "profile": {str(i): profile[i] for i in sorted(profile)},
            "retained_fields": len(retained), "retained_mode_equalities": 8 * len(retained),
            "owned_fields_zero": 8, "c_slots_zero": 9, "exempt_ground_helpers": len(ignored),
            "exempt_helpers_with_channel_response": sum(bool(rows[i]) for i in ignored),
            "exempt_helpers_with_payload_residual": residuals,
            "charge": str(charge), "baseline": str(baseline), "gain": str(baseline - charge)}


def controls(word, modes, witness):
    mutants = []
    bad = deepcopy(witness)
    bad["channels"][0]["contacts"][0][2] = "5"
    mutants.append(bad)
    bad = deepcopy(witness)
    bad["channels"][0]["contacts"][0][0] = 0
    mutants.append(bad)
    bad = deepcopy(witness)
    bad["channels"][1]["frame"] = 0
    mutants.append(bad)
    bad = deepcopy(witness)
    bad["channels"][1]["grade"] = 6
    mutants.append(bad)
    bad = deepcopy(witness)
    bad["channels"][-1]["payload"][4] = "1"
    mutants.append(bad)
    bad = deepcopy(witness)
    bad["channels"] = bad["channels"][1:]
    mutants.append(bad)
    bad = deepcopy(witness)
    bad["tariff"]["8"] = "14"
    mutants.append(bad)
    bad = deepcopy(witness)
    bad["tariff"]["6"] = "2"
    mutants.append(bad)
    for bad in mutants:
        try:
            evaluate(word, modes, bad)
        except ValueError:
            continue
        raise ValueError("mutation accepted")
    return len(mutants)


def evidence():
    word, modes = load_source()
    witness = json.loads((PACKAGE / "WITNESS.json").read_bytes())
    result = evaluate(word, modes, witness)
    result["rejection_controls"] = controls(word, modes, witness)
    sources = {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
               for name in ("verify.py", "WITNESS.json")}
    sources["source_archive"] = ARCHIVE_HASH
    return {"schema": "immutable-channel-evidence/v1", "hashes": sources, "result": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    report = evidence()
    if args.write_receipt:
        report["environment"] = {"python": platform.python_version(), "platform": platform.platform()}
        with args.write_receipt.open("x") as output:
            output.write(json.dumps(report, indent=2) + "\n")
    else:
        saved = json.loads((PACKAGE / "RESULT.json").read_bytes())
        require(all(saved[key] == value for key, value in report.items()), "complete receipt")
    print("PASS_MONOTONE_NOISY_DELIVERY " + json.dumps(report["result"], sort_keys=True))


if __name__ == "__main__":
    main()
