#!/usr/bin/env python3
"""Compare the channel addition replay with the Gram boundary term.

The term is Q(inner(target root, source root), 2), with inner the integer
dot product divided by 4. The roots and the removed ports come from the
pinned checker. This does not import that checker.
"""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_P104_FLAG_GRAM_BOUNDARY flags=208 gram_matches=208 flag0=1/2 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_FLAG_GRAM_BOUNDARY " + message)


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
            vector[i], vector[j] = 2, 2 * sign
            lines.add(tuple(vector))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            lines.add((1, *signs))
    return sorted(lines)


def inner(left, right):
    return sum(x * y for x, y in zip(left, right)) // 4


def ports_of(fixture):
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    found = [row for row in roots() if row not in removed]
    require(len(roots()) == 120 and len(found) == 104, "the port list changed size")
    return found


def replay(program, names):
    state = {name: {name: Fraction(1)} for name in names}
    for event in program:
        op = event[0]
        if op == "transport":
            continue
        if op == "zero":
            state[event[1]] = {}
        elif op == "erase":
            state.pop(event[1], None)
        elif op == "copy":
            _op, reg, src, _frame = event
            state[reg] = dict(state[src])
        elif op == "add":
            _op, reg, src, coeff, _frame = event
            coeff = Fraction(str(coeff))
            state.setdefault(reg, {})
            for origin, value in list(state.get(src, {}).items()):
                updated = state[reg].get(origin, Fraction(0)) + coeff * value
                if updated:
                    state[reg][origin] = updated
                else:
                    state[reg].pop(origin, None)
        else:
            fail("unknown event " + op)
    return state


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-joint-unit-flags/CERTIFICATE.json",
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-native-channel/inputs/P104-FIXTURE.json",
        "research/p104-native-channel/check_native.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    checker = (ROOT / "research/p104-native-channel/check_native.py").read_text(encoding="utf-8")
    require("inner=lambda a,b:sum(x*y for x,y in zip(a,b))//4" in checker, "the inner product changed")
    require("ports=[r for r in rr if r not in removed]" in checker, "the port rule changed")
    require("Q(inner(ports[t],a),2)" in checker, "the boundary coefficient changed")
    require("The side correction is outside it." in checker, "the correction boundary changed")
    certificate = json.loads((ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json").read_text(encoding="utf-8"))
    witness = json.loads((ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json").read_text(encoding="utf-8"))
    fixture = json.loads((ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json").read_text(encoding="utf-8"))
    section = fixture["section4_explicit_P104"]
    chosen = ports_of(section)
    state = replay(witness["program"], list(witness["initial_frames"]))
    helpers = certificate["helpers"]
    require(len(helpers) == 208, "the flag count changed")
    counts = {}
    for row in helpers:
        source, target = row["source"], row["target"]
        gram = Fraction(inner(chosen[target], chosen[source]), 2)
        got = state[f"Y{target}"].get(f"X{source}")
        require(got == gram and gram != 0, "a replay coefficient left its Gram term")
        counts[str(gram)] = counts.get(str(gram), 0) + 1
    flag = helpers[0]
    require(flag["source"] == 0 and flag["target"] == 34, "flag 0 changed")
    dot = inner(chosen[34], chosen[0])
    return {
        "flags": 208,
        "gram_matches_replay": 208,
        "coefficients": counts,
        "flag0": {
            "source": 0,
            "target": 34,
            "source_root": list(chosen[0]),
            "target_root": list(chosen[34]),
            "inner": dot,
            "coefficient": str(Fraction(dot, 2)),
        },
        "side_correction_included": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
