#!/usr/bin/env python3
"""Direct one-target geometry oracle, independent of the encoded producer.

Only the predecessor's published source predicate/consumer alphabet was read.
This module imports no primary implementation and has no runtime source loader.
"""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path


SKIP = ("S", False, False, "0", "0")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def admit_geometry(g, h, k, y, j, b):
    need(all(type(v) is int for v in (g, h, k, y, j, b)), "exact integer geometry")
    need(g >= 1 and h >= g and k >= g + 4 and j >= 0 and b >= 0
         and y >= j + k, "one-target source geometry")
    return 2 * h + y + b


def expected_stencil(g, h, k, y, j, b):
    """Direct MSB-position specification; numeric offsets are oracle-only."""
    length = admit_geometry(g, h, k, y, j, b)
    intervals = ((h - g, h, "D"), (2 * h - g, 2 * h, "D"),
                 (2 * h + y - j - k, 2 * h + y - j - 1, "G"))
    low, high = 1 << (g + 1), (1 << (k - 1)) - (1 << (g + 1))
    result = []
    for position in range(length):
        atom = SKIP
        for start, stop, kind in intervals:
            if start <= position < stop:
                need(atom == SKIP, "oracle interval overlap")
                shift = stop - 1 - position
                atom = (kind, position == start, position == stop - 1,
                        str((low >> shift) & 1) if kind == "G" else "0",
                        str((high >> shift) & 1) if kind == "G" else "0")
        result.append(atom)
    return result


def source_good(address, g, h, k, y, j, b):
    """Direct predecessor formula with MSB-ordered u/t/y/back fields."""
    length = admit_geometry(g, h, k, y, j, b)
    need(type(address) is int and 0 <= address < (1 << length), "fixed-width address")
    y_word = (address >> b) % (1 << y)
    t_word = (address >> (b + y)) % (1 << h)
    u_word = address >> (b + y + h)
    radix = 1 << g
    higher_guard = (y_word >> (j + 1)) % (1 << (k - 1))
    return (u_word % radix != radix - 1 and t_word % radix != radix - 1
            and 2 * radix <= higher_guard < (1 << (k - 1)) - 2 * radix)


def stencil_good(address, cells):
    """Independent interval-integer semantics, not the consumer flag machine."""
    word, low, high, kind = 0, 0, 0, None
    for index, atom in enumerate(cells):
        tag, begin, end, lo, hi = atom
        if tag == "S":
            need(kind is None and atom == SKIP, "skip while active")
            continue
        if begin:
            need(kind is None, "nested interval")
            word, low, high, kind = 0, 0, 0, tag
        need(kind == tag, "interval kind mismatch")
        bit = (address >> (len(cells) - 1 - index)) & 1
        word = 2 * word + bit
        low = 2 * low + int(lo)
        high = 2 * high + int(hi)
        if end:
            if tag == "D":
                # All accumulated bits are one iff word+1 is a power of two.
                # Track interval width by its begin position, independently of G.
                start = index
                while not cells[start][1]:
                    start -= 1
                if word == (1 << (index - start + 1)) - 1:
                    return False
            elif tag == "G":
                if not low <= word < high:
                    return False
            else:
                raise ValueError("unexpected active alphabet")
            kind = None
    need(kind is None, "unterminated interval")
    return True


def expected_boundary_controls():
    count = 0
    examples = []
    for g in (1, 2, 3, 8, 31):
        for j in (0, 1, 3):
            h, k, y, b = g + 2, g + 4, j + g + 6, 2
            lower, upper = 1 << (g + 1), (1 << (k - 1)) - (1 << (g + 1))
            cells = expected_stencil(g, h, k, y, j, b)
            for guard in (lower - 1, lower, lower + 1, upper - 1, upper, upper + 1):
                expected = lower <= guard < upper
                for parity, spectators in product((0, 1), repeat=2):
                    # Both H fields have nonzero inactive prefixes in one case;
                    # active G-bit digits are zero. Every unspecified bit toggles.
                    u = t = (((1 << (h - g)) - 1) << g) if spectators else 0
                    ignored_high = ((1 << (y - j - k)) - 1) << (j + k) if spectators else 0
                    ignored_low = (1 << j) - 1 if spectators else 0
                    y_word = ignored_high | (guard << (j + 1)) | (parity << j) | ignored_low
                    back = (1 << b) - 1 if spectators else 0
                    address = (((u << h) | t) << (y + b)) | (y_word << b) | back
                    need(source_good(address, g, h, k, y, j, b) == expected,
                         "source boundary/parity/spectator discrepancy")
                    need(stencil_good(address, cells) == expected,
                         "stencil boundary/parity/spectator discrepancy")
                    count += 1
            examples.append({"G": g, "J": j, "lower_inclusive": lower,
                             "upper_exclusive": upper, "length": len(cells)})
    return {"checked_addresses": count, "geometries": examples,
            "spectators": ["inactive H prefixes", "Y bits above guard", "Y bits below parity", "B bits"],
            "parity_excluded": True}


def must_reject(arguments):
    try:
        expected_stencil(*arguments)
    except ValueError:
        return True
    raise RuntimeError("invalid geometry was admitted: " + repr(arguments))


def admission_controls():
    invalid = [(0, 1, 5, 5, 0, 0), (2, 1, 6, 6, 0, 0),
               (1, 1, 4, 5, 0, 0), (1, 1, 5, 4, 0, 0),
               (1, 1, 5, 5, -1, 0), (1, 1, 5, 5, 0, -1),
               (True, 1, 5, 5, 0, 0), (1, 1.0, 5, 5, 0, 0),
               (1, 1, 5, 6, 2, 0)]
    return {"rejected_geometry_cases": sum(must_reject(args) for args in invalid),
            "classes": ["zero G", "H<G", "K<G+4", "incomplete Y guard", "negative J",
                        "negative B", "bool parameter", "float parameter", "shifted incomplete guard"]}


def semantic_controls():
    g, h, k, y, j, b = 1, 2, 5, 7, 1, 1
    cells = expected_stencil(g, h, k, y, j, b)
    lower, upper = 4, 12
    evidence = []
    for guard, expected, label in ((lower, True, "strict-lower-mutant"),
                                   (upper, False, "inclusive-upper-mutant"),
                                   (2, False, "unshifted-lower-mutant")):
        address = (guard << (j + 1)) << b
        need(source_good(address, g, h, k, y, j, b) == expected, label)
        evidence.append({"control": label, "guard": guard, "expected_good": expected})
    # A G-bit all-ones digit is invalid even though its complete H-bit field is
    # not all ones. This catches accidentally testing H rather than active G.
    address = ((1 << (y + b + h)) | ((lower << (j + 1)) << b))
    need(not source_good(address, g, h, k, y, j, b), "inactive-H-width control")
    need(not stencil_good(address, cells), "active digit interval control")
    evidence.append({"control": "test-H-instead-of-G-mutant", "expected_good": False})
    # Including parity yields different interpreted words at a guard boundary.
    correct = ((upper - 1) << (j + 1)) << b
    wrong_guard_with_parity = (correct >> (b + j)) % (1 << k)
    need(source_good(correct, g, h, k, y, j, b)
         and not lower <= wrong_guard_with_parity < upper,
         "include-parity counterexample not discriminating")
    evidence.append({"control": "include-parity-mutant", "expected_good": True,
                     "wrong_guard": wrong_guard_with_parity})
    return evidence


def run():
    rows, addresses, total_good = [], 0, 0
    for g, extra_h, extra_k, j, extra_y, b in product((1, 2), (0, 1), (0, 1),
                                                   (0, 1, 2), (0, 1), (0, 1)):
        h, k = g + extra_h, g + 4 + extra_k
        y = j + k + extra_y
        length = 2 * h + y + b
        if length > 14:
            continue
        cells = expected_stencil(g, h, k, y, j, b)
        mask = bytearray()
        good_count = 0
        for address in range(1 << length):
            expected = source_good(address, g, h, k, y, j, b)
            need(stencil_good(address, cells) == expected, "source/stencil finite mismatch")
            mask.append(ord("0") if expected else ord("1"))
            good_count += expected
        addresses += len(mask)
        total_good += good_count
        rows.append({"G": g, "H": h, "K": k, "Y": y, "J": j, "B": b,
                     "L": length, "addresses": len(mask), "good_addresses": good_count,
                     "bad_mask_sha256": hashlib.sha256(mask).hexdigest(),
                     "stencil_json_sha256": hashlib.sha256(json.dumps(cells, separators=(",", ":")).encode()).hexdigest()})
    return {"status": "PASS", "scope": "direct one-target numeric oracle, not a charged producer",
            "finite_cap": {"G": [1, 2], "extra_H": [0, 1], "extra_K": [0, 1],
                           "J": [0, 1, 2], "extra_Y": [0, 1], "B": [0, 1], "max_L": 14},
            "geometry_count": len(rows), "address_count": addresses,
            "good_address_count": total_good, "rows": rows,
            "boundary_controls": expected_boundary_controls(),
            "admission_controls": admission_controls(), "semantic_controls": semantic_controls(),
            "limitations": ["Finite corroboration; arbitrary parameters require the written proof.",
                            "No primary producer imported or inspected before oracle freeze.",
                            "No production multi-target reservoir, payload repair, E evaluator, or outer theorem."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "scope", "geometry_count", "address_count", "good_address_count")}, sort_keys=True))


if __name__ == "__main__":
    main()
