#!/usr/bin/env python3
"""Read one appended tail coefficient for the channel's flag-0 pair.

The tail word keeps the 4,058-event channel and later adds Y34 += -1/2 * X0.
This checker rebuilds the two port roots and compares that coefficient with
the channel prefix. It does not import either package's verifier.
"""

import gzip
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
TAIL = ROOT / "research/p104-tail-side-correction-seed749717"
CHANNEL = ROOT / "research/p104-native-channel"
MARKER = "PASS_P104_TAIL_FLAG0_COEFFICIENT event=5759 coefficient=-1/2 sum=0 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_TAIL_FLAG0_COEFFICIENT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def roots():
    lines = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            vector = [0] * 8
            vector[i] = 2
            vector[j] = 2 * sign
            lines.add(tuple(vector))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            lines.add((1, *signs))
    require(len(lines) == 120, "the root list changed")
    return sorted(lines)


def ports(fixture):
    removed = {tuple(root) for root in fixture["F0"] + fixture["C"]}
    kept = [root for root in roots() if root not in removed]
    require(len(kept) == 104, "the port count changed")
    return kept


def inner(left, right):
    return sum(x * y for x, y in zip(left, right)) // 4


def correction(target, source, gram):
    delta = 1 if target == source else 0
    return Fraction(delta) - Fraction(gram, 2)


def channel_coefficient(program, names):
    state = {name: {name: Fraction(1)} for name in names}
    for event in program:
        op = event[0]
        if op == "transport":
            continue
        if op == "zero":
            state[event[1]] = {}
            continue
        if op == "erase":
            state.pop(event[1], None)
            continue
        if op == "copy":
            _op, reg, src, _frame = event
            state[reg] = dict(state[src])
            continue
        if op != "add":
            fail("unknown channel event " + op)
        _op, reg, src, coeff, _frame = event
        coeff = Fraction(str(coeff))
        state.setdefault(reg, {})
        for origin, value in list(state.get(src, {}).items()):
            updated = state[reg].get(origin, Fraction(0)) + coeff * value
            if updated:
                state[reg][origin] = updated
            else:
                state[reg].pop(origin, None)
    return state.get("Y34", {}).get("X0", Fraction(0))


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-native-channel/inputs/P104-FIXTURE.json",
        "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
        "research/p104-tail-side-correction-seed749717/CORRECTION-ROWS.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    fixture = json.loads((CHANNEL / "inputs/P104-FIXTURE.json").read_text(encoding="utf-8"))
    section = fixture["section4_explicit_P104"]
    kept = ports(section)
    source_root = tuple(kept[0])
    target_root = tuple(kept[34])
    gram = inner(target_root, source_root)
    formula = correction(34, 0, gram)
    rows = json.loads((TAIL / "CORRECTION-ROWS.json").read_text(encoding="utf-8"))
    require(rows["formula"] == "coefficient[t,s] = delta[t,s] - G[t,s]/2", "the published formula changed")
    row = rows["rows"][34]
    require(row["target"] == 34 and tuple(row["target_root"]) == target_root, "target 34 left its port")
    matches = [entry for entry in row["nonzero"] if entry["source"] == 0]
    require(len(matches) == 1, "source 0 is not a single tail entry")
    entry = matches[0]
    require(tuple(entry["source_root"]) == source_root, "source 0 left its port")
    require(entry["gram"] == gram == 1, "the Gram term left 1")
    require(Fraction(entry["coefficient"]) == formula == Fraction(-1, 2), "the row left the formula")
    channel = json.loads((CHANNEL / "inputs/LOWRANK-WITNESS.json").read_text(encoding="utf-8"))
    tail = json.loads(gzip.decompress((TAIL / "AUGMENTED-WITNESS.json.gz").read_bytes()))
    require(tail["program"][:4058] == channel["program"], "the tail prefix left the channel word")
    hits = [
        (index, event)
        for index, event in enumerate(tail["program"])
        if event[0] == "add" and event[1] == "Y34" and event[2] == "X0"
    ]
    require(len(hits) == 1 and hits[0][0] == 5759, "the flag-0 add moved")
    event = hits[0][1]
    require(Fraction(str(event[3])) == formula, "the event left the row")
    prefix = channel_coefficient(channel["program"], list(channel["initial_frames"]))
    require(prefix == Fraction(1, 2), "the channel prefix left 1/2")
    first = tail["program"][4059]
    require(first[:4] == ["add", "Y0", "X2", "-1/2"], "the first tail add moved")
    return {
        "prefix_events": 4058,
        "prefix_matches_channel": True,
        "first_tail_add": {"event": 4059, "target": "Y0", "source": "X2", "coefficient": "-1/2"},
        "flag0": {
            "event": 5759,
            "target": "Y34",
            "source": "X0",
            "source_root": list(source_root),
            "target_root": list(target_root),
            "gram": gram,
            "coefficient": "-1/2",
            "channel_coefficient": "1/2",
            "sum_with_channel": "0",
        },
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
