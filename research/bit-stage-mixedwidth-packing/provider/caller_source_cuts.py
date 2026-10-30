#!/usr/bin/env python3
"""Independent integer source-history audit of the emitted PR4183 word.

Reads native.py's authenticated serialized output; imports neither producer.
The source50 input is temporarily mutated. Only the actual helper413 read cuts
are proved to hold its original independent integer input, in the right frame.
Python 3.12 standard library. Output is deterministic under normal and -O runs.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parent
PINS = {
    "LOCAL-PROGRAMS.json":
        "c2c35a98c7674c8b16b6c014e2dafd9912ae8ae93cf0ccd2cb1dc654ca2bc6bf",
    "249-states.json":
        "103de24baca3bb119fafee6778d5596bce00f8731cf05d107ea7bad300786f08",
    "frames.json":
        "76a3c2af379ab20bb179baf40eadb5051eadd12cd2442c8eb323404b8ae9b5cd",
}
CUTS = {
    "forward": ((23829, 1, 509), (31990, -1, 1)),
    "reverse": ((6877, 1, 1), (15038, -1, 509)),
}
WRITES = {
    "forward": (24473, 24474, 24475, 24841, 25846, 26229, 26230, 26231),
    "reverse": (12636, 12637, 12638, 13021, 14026, 14392, 14393, 14394),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sparse(row):
    return [[column, row[column]] for column in sorted(row)]


def add(target, source, coefficient):
    for column, value in source.items():
        total = target.get(column, 0) + coefficient * value
        if total:
            target[column] = total
        else:
            target.pop(column, None)


def load_artifacts(path):
    expected = json.loads((ROOT / "NATIVE.json").read_bytes())
    provider = json.loads((path / "NATIVE-PROVIDER.json").read_bytes())
    need(canonical(provider) == canonical(expected), "complete native provider receipt")
    loaded = {}
    for name, pin in PINS.items():
        data = (path / "candidate" / name).read_bytes()
        need(sha256(data).hexdigest() == pin, "source-cut serialized pin " + name)
        need(provider["words"]["candidate"]["emitted_file_sha256"][name] == pin,
             "source-cut provider file binding")
        loaded[name] = json.loads(data)
    return loaded, expected


def frame_table(state, orientation):
    name = "final" if orientation == "reverse" else "initial"
    need(set(state[name]) == {str(i) for i in range(660)}, "complete ordinary frame registry")
    return [state[name][str(i)] for i in range(660)] + [-1]


def replay(events, state, framebank, orientation):
    """Propagate all independent columns; no sampled scalar input is used."""
    reverse = int(orientation == "reverse")
    frames = frame_table(state, orientation)
    rows = [{i: 1} for i in range(660)] + [{}]
    opened = None
    cuts, writes = [], []
    copies = erases = 0
    for position, event in enumerate(events):
        need(all(type(value) is int for value in event), "literal integer record fields")
        op, role = event[:2]
        need(0 <= role < 660, "ordinary source-history role")
        need(event[-1] == reverse, "source-history orientation flag")
        if op == 0:
            _, _, before, after, rank, _ = event
            need(opened is None and frames[role] == before, "MOVE frame and closed COPY")
            need(abs(framebank[str(after)]["dim"] - framebank[str(before)]["dim"]) == rank,
                 "MOVE declared rank")
            frames[role] = after
        elif op == 1:
            _, _, source, coefficient, frame, _ = event
            need(0 <= source <= 660 and source != role and coefficient in (-1, 1),
                 "signed source-history ADD")
            need(frames[role] == frames[source] == frame, "actual source-cut ADD frames")
            need(source != 660 or opened is not None, "private read has a live COPY")
            need(opened is None or role != opened[0], "copied source remains immutable")
            if role == 413 and source == 50:
                need(rows[50] == {50: 1}, "current source50 differs from its original input")
                need(opened is None, "source50 read cut has an open COPY")
                cuts.append({
                    "position": position, "record": event,
                    "source_frame": frames[50], "destination_frame": frames[413],
                    "current_source_integer_row": sparse(rows[50]),
                    "destination_integer_row_before": sparse(rows[413]),
                    "private_closed": True,
                })
            add(rows[role], rows[source], coefficient)
            if role == 50:
                writes.append({"position": position, "record": event,
                               "current_integer_row": sparse(rows[50])})
        elif op == 2:
            _, _, temporary, before, after, rank, _ = event
            need(temporary == 660 and opened is None and not rows[660]
                 and frames[660] == -1, "fresh clean private work")
            need(frames[role] == before and after == 0
                 and framebank[str(before)]["dim"] == rank == 7,
                 "actual transported COPY frames")
            rows[660] = rows[role].copy()
            frames[660] = after
            opened = (role, before, after)
            copies += 1
        else:
            need(op == 3 and opened is not None, "matching integer ERASE")
            _, _, temporary, before, after, rank, _ = event
            need(temporary == 660 and opened == (role, before, after)
                 and frames[role] == before and frames[660] == after
                 and rank == (7 if reverse else 0), "exact ERASE frame guard")
            need(rows[660] == rows[role], "exact integer transported ERASE equality")
            rows[660] = {}
            frames[660] = -1
            opened = None
            erases += 1
    expected_frames = frame_table(state, "forward" if reverse else "reverse")
    need(frames == expected_frames and opened is None and not rows[660],
         "closed ordinary frame and private endpoint")
    need(rows[50] == {50: 1}, "final source50 restoration")
    observed = tuple((cut["position"], cut["record"][3], cut["source_frame"]) for cut in cuts)
    need(observed == CUTS[orientation], "complete source50 read cuts")
    need(tuple(row["position"] for row in writes) == WRITES[orientation],
         "complete source50 mutation history")
    need(len(writes) == 8 and all(row["current_integer_row"] != [[50, 1]]
                                 for row in writes[:-1])
         and writes[-1]["current_integer_row"] == [[50, 1]],
         "nontrivial source50 mutation and exact restoration")
    need(copies == erases == 9, "all literal private lifetimes")
    return {"events": len(events), "independent_integer_columns": 660,
            "cuts": cuts, "source50_write_history": writes,
            "final_source50": [[50, 1]], "source50_globally_immutable": False,
            "integer_COPY_ERASE_equalities": erases, "private_final_zero": True,
            "event_sha256": sha256(canonical(events)).hexdigest()}


def controls(programs, state, framebank):
    cases = []
    forward = programs["forward"]
    changed = deepcopy(forward)
    changed.insert(23829, [1, 50, 413, 1, 509, 0])
    cases.append(("earlier current-source mutation", "forward", changed,
                  "current source50 differs"))
    changed = deepcopy(forward)
    del changed[26231]
    cases.append(("omitted final source restoration", "forward", changed,
                  "current source50 differs"))
    changed = deepcopy(forward)
    changed[23829][4] = 1
    cases.append(("wrong frame at inserted read", "forward", changed,
                  "actual source-cut ADD frames"))
    changed = deepcopy(forward)
    changed.insert(23829, [2, 476, 660, 515, 0, 7, 0])
    cases.append(("open valid COPY at inserted read", "forward", changed,
                  "source50 read cut has an open COPY"))
    changed = deepcopy(programs["reverse"])
    del changed[14394]
    cases.append(("omitted inverse source restoration", "reverse", changed,
                  "current source50 differs"))
    rejected = []
    for label, orientation, events, marker in cases:
        try:
            replay(events, state, framebank, orientation)
        except ValueError as error:
            need(marker in str(error), "unrelated source-cut control failure: " + label)
            rejected.append({"mutation": label, "rejected_by": str(error)})
        else:
            raise ValueError("source-cut control survived: " + label)
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True,
                        help="native.py --output directory, read only")
    args = parser.parse_args()
    files, provider = load_artifacts(args.artifacts)
    programs = files["LOCAL-PROGRAMS.json"]
    state = files["249-states.json"]
    frames = files["frames.json"]["frames"]
    need((state["n"], state["v"], state["R"], state["h"]) == (660, 111, 438, 8),
         "source-cut source dimensions")
    need(set(programs) == {"forward", "reverse"} and len(frames) == 636,
         "source-cut complete orientation/frame inventory")
    result = {
        "status": "PASS_EXACT_CURRENT_SOURCE50_CUTS",
        "scope": ("Independent finite integer column/source-history proof for all actual "
                  "helper413 source50 read cuts; no caller import, GL64 enumeration, "
                  "rounded cleanup or physical tape claim."),
        "serialized_input_sha256": PINS,
        "candidate_word_sha256": provider["words"]["candidate"]["literal_word_sha256"],
        "candidate_native_raw6_sha256": provider["words"]["candidate"]["native_raw6_sha256"],
        "orientations": {},
        "no_new_kappa": True,
    }
    for orientation in ("forward", "reverse"):
        checked = replay(programs[orientation], state, frames, orientation)
        need(checked["event_sha256"] ==
             provider["words"]["candidate"]["local_checks"][orientation]["events_sha256"],
             "source-cut actual event order binding")
        result["orientations"][orientation] = checked
    result["negative_controls"] = controls(programs, state, frames)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
