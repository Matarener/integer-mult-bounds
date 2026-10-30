#!/usr/bin/env python3
"""Replay the typed actual-width physical H against the frozen PR #3623 tensor."""

from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

import physical_h

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "frozen" / "pr3623-check_join.py"
FROZEN_SHA256 = "33f91624d60be8c7124ecc24be073f8a5a3759b671979b6a17a6e26538f4355e"
FROZEN_BLOB = "421ae05f081ec37e4c5fa0b1b7e200a1578ab16d"
RECEIPT_PATH = HERE / "RECEIPT.json"

CASES = (
    (2, (False,), 1),
    (2, (True,), 1),
    (3, (False, False), 1),
    (3, (True, False), 1),
    (3, (True, True), 1),
    (3, (False, False, False), 1),
    (3, (True, False, True), 1),
    (3, (False, False, False, False), 2),
    (3, (True, False, False, False), 2),
    (4, (True, False), 2),
)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def rejected(call, reason):
    try:
        call()
    except ValueError as error:
        need(str(error) == reason, "unexpected rejection: " + str(error))
        return reason
    raise ValueError("missing rejection: " + reason)


def load_frozen():
    data = FROZEN.read_bytes()
    digest = sha256(data).hexdigest()
    blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    need(digest == FROZEN_SHA256, "frozen sha256")
    need(blob == FROZEN_BLOB, "frozen git blob")
    spec = importlib.util.spec_from_file_location("pr3623_check_join", FROZEN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cube_for(ell, original):
    records = 1 << len(original)
    coeffs = 1 << ell
    return [[((17 * x + 5 * j + 3) % 7 - 3, (11 * x + 7 * j + 2) % 7 - 3)
             for j in range(coeffs)] for x in range(records)]


def run_cases(frozen):
    rows = []
    totals = {"read": 0, "write": 0, "move": 0, "gate": 0}
    widths = set()
    for ell, flags, k in CASES:
        original, physical = physical_h.slots_for(ell, flags, k)
        need((original, physical) == frozen.slots_for(ell, flags, k), "layout pin")
        cube = cube_for(ell, original)
        for order in ("physical", "original"):
            source = cube if order == "original" else frozen.reorder(cube, original, physical)
            for h in physical_h.levels_for(ell, flags):
                machine = physical_h.TypedActualWidthH(ell, flags, k, 4)
                decoded, ledger, info = machine.run(source, h, source_order=order)
                bits = info["selected_bits"]
                need(bits == machine.matched_bits(h), "descriptor")
                physical_cube = source if order == "physical" else frozen.reorder(
                    source, original, physical)
                raw, _den = frozen.h_direct(physical_cube, bits)
                need(decoded == frozen.truncate(raw, _den), "tensor return")
                closed = physical_h.closed_read_write_gate(
                    info["records"], info["coefficients"], len(bits), 4)
                need({key: ledger[key] for key in closed} == closed, "read write gate bill")
                slots = machine.original if order == "original" else machine.physical
                origin = physical_h.origin_of_target(slots, machine.physical)
                moves = physical_h.itinerary_moves(
                    info["records"], info["coefficients"], len(bits), 4, origin, bits)
                need(ledger["move"] == moves, "head itinerary")
                need(rejected(lambda: machine.run(source, h, source_order=order),
                              "one-shot physical H") == "one-shot physical H", "one-shot")
                for key in totals:
                    totals[key] += ledger[key]
                widths.add(len(bits))
                rows.append({
                    "ell": ell,
                    "flags": list(flags),
                    "K": k,
                    "h": h,
                    "order": order,
                    "bits": list(bits),
                    "records": info["records"],
                    "ledger": ledger,
                })
    return rows, totals, sorted(widths)


def negative_and_rejections():
    machine = physical_h.TypedActualWidthH(2, (False,), 1, 4)
    h = machine.levels[0]
    need(machine.matched_bits(h) == (0,), "single selected bit")
    coeffs = 1 << 2
    cube = [[(0, 0) for _ in range(coeffs)] for _ in range(2)]
    cube[1][0] = (1, 0)
    decoded, ledger, _info = machine.run(cube, h, source_order="physical")
    need(decoded[0][0] == (0, 0) and decoded[1][0] == (0, 0), "toward-zero witness")
    need(physical_h.arithmetic_shift(-1, 1) == -1, "arithmetic shift stays negative")
    need(physical_h.trunc_pow2(-1, 1) == 0, "toward zero clears the odd numerator")
    signed = physical_h.bits_from_int(1, 6)
    lsb, msb = list(reversed(signed)), list(signed)
    need(physical_h.int_from_bits(msb) == 1, "msb consumer word")
    need(physical_h.int_from_bits(lsb) != 1, "skipping the bridge changes the integer")
    need(physical_h.int_from_bits(list(reversed(lsb))) == 1, "bridge restores the integer")
    old = physical_h.TypedActualWidthH(3, (False, False, False), 1, 4)
    descriptor = rejected(lambda: old.require_bits(1, (0, 1, 2)), "selected-bit descriptor")
    disk_machine = physical_h.TypedActualWidthH(2, (False,), 1, 4)
    bad = [[(0, 0) for _ in range(4)] for _ in range(2)]
    bad[0][0] = (17, 0)
    disk = rejected(lambda: disk_machine.run(bad, disk_machine.levels[0]), "unit disk")
    need(physical_h._level_moves(2, 1, 0) == 4, "hand-checked adjacent pair")
    need(physical_h._linear_level_moves(2, 1) == 14, "hand-checked linear level")
    failures = 0
    for g in range(0, 7):
        work = 4 + g + 2
        width = 6
        for value in range(-(1 << (4 + g)), (1 << (4 + g)) + 1):
            gates = [0]
            out = physical_h._q_component(physical_h.bits_from_int(value, work), g, width, gates)
            if physical_h.int_from_bits(out) != physical_h.trunc_pow2(value, g):
                failures += 1
    need(failures == 0, "Q_p range")
    return {
        "negative_output": [list(decoded[0][0]), list(decoded[1][0])],
        "negative_ledger": ledger,
        "arithmetic_shift_of_minus_one": -1,
        "old_descriptor": descriptor,
        "disk": disk,
        "adjacent_pair_moves": 4,
        "linear_level_moves_m2_rw1": 14,
        "q_range_failures": failures,
    }


def digest(rows):
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return sha256(payload).hexdigest()


def main():
    frozen = load_frozen()
    rows, totals, widths = run_cases(frozen)
    controls = negative_and_rejections()
    receipt = {
        "pass_token": "PASS_TYPED_ACTUAL_WIDTH_PHYSICAL_H",
        "calls": len(rows),
        "selected_bit_widths": widths,
        "totals": totals,
        "digest_sha256": digest(rows),
        "controls": controls,
    }
    expected = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    need(receipt == expected, "receipt mismatch")
    print("PASS_TYPED_ACTUAL_WIDTH_PHYSICAL_H")


if __name__ == "__main__":
    main()
