#!/usr/bin/env python3
"""Follow source values through the channel's published addition rule.

An add updates the destination by the coefficient times the source register.
A copy replaces the destination. This replay does not import the channel checker.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = (
    "PASS_P104_FLAG_RELAY flags=208 arrivals_after_source=208 "
    "flag0=1/2 at=2815 no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_P104_FLAG_RELAY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-joint-unit-flags/CERTIFICATE.json",
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-native-channel/check_native.py",
        "research/p104-endpoint-geometric-budget/geometry.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def replay(program, names):
    state = {name: {name: Fraction(1)} for name in names}
    first_touch = {}
    arrived = {}

    def touch(register, index):
        first_touch.setdefault(register, index)

    for index, event in enumerate(program):
        op = event[0]
        if op == "transport":
            touch(event[1], index)
        elif op == "zero":
            state[event[1]] = {}
            touch(event[1], index)
        elif op == "erase":
            state.pop(event[1], None)
        elif op == "copy":
            _op, reg, src, _frame = event
            state[reg] = dict(state[src])
            touch(reg, index)
            for origin, value in state[reg].items():
                if value and reg.startswith("Y"):
                    arrived.setdefault((origin, reg), index)
        elif op == "add":
            _op, reg, src, coeff, _frame = event
            coeff = Fraction(str(coeff))
            state.setdefault(reg, {})
            had = set(state[reg])
            for origin, value in list(state.get(src, {}).items()):
                updated = state[reg].get(origin, Fraction(0)) + coeff * value
                if updated:
                    state[reg][origin] = updated
                else:
                    state[reg].pop(origin, None)
            touch(reg, index)
            if reg.startswith("Y"):
                for origin in state[reg]:
                    if origin not in had:
                        arrived.setdefault((origin, reg), index)
        else:
            fail("unknown event " + op)
    return state, first_touch, arrived


def flag_path(program):
    """First register that carries X0 into each later register, walked back from Y34."""
    state = {"X0": {"X0": Fraction(1)}}
    born = {"X0": None}
    for index, event in enumerate(program):
        op = event[0]
        if op == "copy":
            _op, reg, src, _frame = event
            state[reg] = dict(state.get(src, {}))
            if state[reg].get("X0") and reg not in born:
                born[reg] = (index, src)
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
            if state[reg].get("X0") and reg not in born:
                born[reg] = (index, src)
        elif op == "zero":
            state[event[1]] = {}
        elif op == "erase":
            state.pop(event[1], None)
    steps = []
    node = "Y34"
    while born[node] is not None:
        index, src = born[node]
        event = program[index]
        steps.append({
            "event": index,
            "op": event[0],
            "register": node,
            "from": src,
            "add_coefficient": None if event[0] != "add" else str(Fraction(str(event[3]))),
        })
        node = src
    steps.reverse()
    return steps


def evaluate():
    authenticate()
    checker = (ROOT / "research/p104-native-channel/check_native.py").read_text(encoding="utf-8")
    geometry = (ROOT / "research/p104-endpoint-geometric-budget/geometry.py").read_text(encoding="utf-8")
    require("z=state[reg].get(name,Q(0))+Q(a)*v" in checker, "the addition rule changed")
    require("state[reg]=dict(state[src])" in checker, "the copy rule changed")
    require("sources = [paths[f'X{s}'] for s in range(104)]" in geometry, "source naming changed")
    require("targets = [paths[f'Y{t}'] for t in range(104)]" in geometry, "target naming changed")
    certificate = json.loads((ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json").read_text(encoding="utf-8"))
    witness = json.loads((ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json").read_text(encoding="utf-8"))
    helpers = certificate["helpers"]
    program = witness["program"]
    require(len(helpers) == 208 and len(program) == 4058, "the published sizes changed")
    require(helpers[0]["source"] == 0 and helpers[0]["target"] == 34, "flag 0 changed")
    state, first_touch, arrived = replay(program, list(witness["initial_frames"]))
    counts = {}
    late = 0
    for row in helpers:
        source, target = f"X{row['source']}", f"Y{row['target']}"
        value = state[target].get(source)
        require(value, "a matched source is absent from its target")
        counts[str(value)] = counts.get(str(value), 0) + 1
        if arrived[(source, target)] >= first_touch[source]:
            late += 1
    require(state["Y34"]["X0"] == Fraction(1, 2), "Y34's coefficient of X0 changed")
    require(arrived[("X0", "Y34")] == 2815 and first_touch["X0"] == 591, "flag 0 timing changed")
    return {
        "flags": 208,
        "final_coefficients": counts,
        "arrivals_after_source_first_touch": late,
        "flag0": {
            "source_first_event": 591,
            "arrival_event": 2815,
            "final_coefficient": "1/2",
            "path": flag_path(program),
        },
        "gram_identity_resolved": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
