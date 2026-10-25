#!/usr/bin/env python3
"""Price one actual K/adjoint round trip from the frozen native-lift recipes.

The quadratic form and tag formula are the statements in PR #4002's proof.
This file does not import that package. Apache-2.0.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECIPES_SHA256 = "64b85f6aef485026eebaec7acddb41999f57e074b0dfde8077b6543700cd684b"
WITNESS = (1, 2, 8, 32, 44, 128, 59, 66, 489)
WIDTH = 9
STATES = 1 << WIDTH


def fail(message):
    raise SystemExit("FAIL_K_ADJOINT_BOUNDARY_PRICE " + message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate JSON key " + str(key))
        result[key] = value
    return result


def load_recipes():
    raw = (HERE / "RECIPES.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != RECIPES_SHA256:
        fail("RECIPES.json bytes differ from the PR #4002 pin")
    data = json.loads(raw, object_pairs_hook=unique_object)
    items = data["items"]
    if len(items) != 40:
        fail("expected 40 recipe descriptors")
    return items


def invert_columns(columns):
    width = len(columns)
    rows = [sum(((columns[j] >> i) & 1) << j for j in range(width)) | (1 << (width + i))
            for i in range(width)]
    for col in range(width):
        pivot = next((row for row in range(col, width) if (rows[row] >> col) & 1), None)
        if pivot is None:
            fail("singular binary map")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for row in range(width):
            if row != col and (rows[row] >> col) & 1:
                rows[row] ^= rows[col]
    return tuple(sum(((rows[i] >> (width + j)) & 1) << i for i in range(width))
                 for j in range(width))


def apply_columns(columns, state):
    out = 0
    bit = 0
    while state:
        if state & 1:
            out ^= columns[bit]
        state >>= 1
        bit += 1
    return out


def quadratic_rows(columns):
    inverse = invert_columns(columns)
    width = len(columns)
    rows = []
    for i in range(width):
        row = 0
        for j in range(width):
            diagonal = 1 if i == j else 0
            gram = (inverse[i] & inverse[j]).bit_count() & 1
            row |= (diagonal ^ gram) << j
        rows.append(row)
    return tuple(rows)


def quadratic_value(rows, state):
    total = 0
    for i, row in enumerate(rows):
        if (state >> i) & 1:
            higher = row & state & ~((1 << (i + 1)) - 1)
            total += (row >> i) & 1
            total += 2 * higher.bit_count()
    return total % 4


def tag_mask(columns, rows=None):
    rows = quadratic_rows(columns) if rows is None else rows
    mask = 0
    for j, column in enumerate(columns):
        # wt(e_j) = 1, so the input correction in the proof is +1.
        difference = (quadratic_value(rows, column) - (column.bit_count() - 1)) % 4
        if difference not in (0, 2):
            fail("phase-section difference is not an even residue")
        mask |= (difference // 2) << j
    return mask


def canonical_phase(columns, rows, state):
    return quadratic_value(rows, apply_columns(columns, state))


def section_phase(columns, state):
    image = apply_columns(columns, state)
    return (image.bit_count() - state.bit_count()) % 4


def pin_boundary(items):
    warps = [item for item in items if item.get("kind") == "warp"]
    maps = {tuple(item["G_columns"]) for item in warps}
    if len(warps) != 16 or len(maps) != 4 or WITNESS not in maps:
        fail("frozen warp inventory is not the four changed-interface maps")
    witness = [item for item in warps if tuple(item["G_columns"]) == WITNESS]
    if len(witness) != 4:
        fail("witness map does not have four frozen descriptors")
    for item in witness:
        if any(row.get("register") != 333 or row.get("index") != 4 for row in item["coverage"]):
            fail("witness map is not confined to register 333 index 4")
    forward_rows = [item for item in witness
                    if item["sign"] == 1 and item["entrance"] == [266, 138, 74, 30, 1]
                    and item["terminal"] == [426, 96, 24, 6, 1]]
    if len(forward_rows) != 1:
        fail("new-version sign-+1 boundary not unique")
    forward = forward_rows[0]
    backward = None
    for item in warps:
        if (tuple(item["G_columns"]) == WITNESS and item["sign"] == -1
                and item["entrance"] == forward["terminal"]
                and item["terminal"] == forward["entrance"]):
            backward = item
            break
    if backward is None:
        fail("matching adjoint descriptor is absent")
    providers = sorted({(row["provider"], row["version"]) for row in forward["coverage"]})
    if providers != [("base", "new"), ("extra", "new")]:
        fail("new-version owner rows are not the two providers")
    return forward, backward


def round_trip():
    items = load_recipes()
    forward, backward = pin_boundary(items)
    columns = WITNESS
    inverse = invert_columns(columns)
    rows = quadratic_rows(columns)
    inverse_rows = quadratic_rows(inverse)
    tag = tag_mask(columns, rows)
    inverse_tag = tag_mask(inverse, inverse_rows)
    # Masks add by XOR. t_I = 0, so ell(G, G^{-1}) = t_G XOR G^t t_{G^{-1}}.
    pulled = sum(((column & inverse_tag).bit_count() % 2) << j
                 for j, column in enumerate(columns))
    defect = tag ^ pulled
    if (tag, inverse_tag, defect) != (144, 68, 256):
        fail("credited witness tags were not recomputed")
    if defect.bit_count() != 1 or defect != 1 << 8:
        fail("round-trip support is not the single coordinate 8")
    j_wrong = 0
    for state in range(STATES):
        k_phase = (canonical_phase(columns, rows, state)
                   + canonical_phase(inverse, inverse_rows, apply_columns(columns, state))) % 4
        j_phase = (section_phase(columns, state)
                   + section_phase(inverse, apply_columns(columns, state))) % 4
        expected = (2 * ((defect & state).bit_count() % 2)) % 4
        if k_phase != expected or j_phase != 0:
            fail("round-trip phase identity failed at state " + str(state))
        if k_phase != j_phase:
            j_wrong += 1
        image = apply_columns(inverse, apply_columns(columns, state))
        if image != state:
            fail("binary round trip is not the identity")
    if j_wrong != 256:
        fail("J substitution does not miss exactly the odd states of bit 8")
    # The recipe's own Z4 linear field is a different charge from the coboundary.
    linear = forward["recipe"]["left"]["linear_Z4"]
    if linear == [(tag >> j) & 1 for j in range(WIDTH)]:
        fail("linear_Z4 collapsed onto the coboundary; the separation is gone")
    if any(entry not in (0, 1, 2, 3) for entry in linear):
        fail("linear_Z4 left the Z4 alphabet")
    controls(columns, rows)
    return {
        "register": 333,
        "index": 4,
        "version": "new",
        "providers": ["base", "extra"],
        "sign_pair": [1, -1],
        "tag": tag,
        "inverse_tag": inverse_tag,
        "central_child": "Z_256",
        "support_coordinate": 8,
        "support_weight": 1,
        "states": STATES,
        "states_wrong_under_J": j_wrong,
        "binary_round_trip": "identity",
        "recipe_phase": forward["recipe"]["left"]["phase"],
        "recipe_linear_Z4": linear,
        "linear_Z4_equals_coboundary": False,
        "recipe_rank_field": forward["recipe"]["rank"],
        "helper_routing_tape": "unknown",
        "precision_extra_denominator": 0,
        "favorable_complete_bill": False,
        "new_kappa": False,
        "adjoint_descriptor_sign": backward["sign"],
    }


def controls(columns, rows):
    # Dropping the weight-one correction selects a different mask.
    broken = 0
    for j, column in enumerate(columns):
        difference = (quadratic_value(rows, column) - column.bit_count()) % 4
        if difference in (0, 2):
            broken |= (difference // 2) << j
    if broken == 144:
        fail("control did not move the tag")
    # A zero defect is the J product, which is not the K product.
    if any((2 * ((0 & state).bit_count() % 2)) % 4
           == (canonical_phase(columns, rows, state)
               + canonical_phase(invert_columns(columns),
                                 quadratic_rows(invert_columns(columns)),
                                 apply_columns(columns, state))) % 4
           for state in (256,)):
        fail("control accepted a zero central child")


def main():
    invoice = round_trip()
    print("PASS_K_ADJOINT_BOUNDARY_PRICE " + json.dumps(invoice, sort_keys=True))


if __name__ == "__main__":
    main()
