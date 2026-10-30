"""Bounded new reversible-interface checks; emit a source-bound receipt."""

import hashlib
import json
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import chart, dimensions, gaussian, overwrite, residue, rotate


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def unpack(value: int, size: int, precision: int) -> tuple[int, ...]:
    return tuple((value >> (u * precision)) & ((1 << precision) - 1)
                 for u in range(size))


def literal_response(bank: tuple[int, ...], n: int, precision: int) -> tuple[int, ...]:
    """An endpoint oracle for the new interface, using only C butterflies."""
    result = [gaussian(value, precision) for value in bank]
    for axis in range(n):
        for low in range(1 << n):
            high = low | (1 << axis)
            if low != high:
                ar, ai = result[low]
                br, bi = result[high]
                result[low] = (br - ai, bi + ar)
                result[high] = (ar - bi, ai + br)
    return tuple(residue(*value, precision) for value in result)


def complete_permutations() -> dict[str, int]:
    cases, states, clean_endpoints = 0, 0, 0
    for n in range(4):
        for precision in range(5):
            size, clean = dimensions(n, precision)
            public_bits = size * precision
            if public_bits + clean > 14:
                continue
            seen = set()
            for state in range(1 << (public_bits + clean)):
                bank = unpack(state, size, precision)
                auxiliary = state >> public_bits
                output, garbage = overwrite(bank, auxiliary, n, precision)
                require(overwrite(output, garbage, n, precision, True) ==
                        (bank, auxiliary), "full-state inverse failed")
                require((output, garbage) not in seen, "permutation collision")
                seen.add((output, garbage))
                if auxiliary == 0:
                    require(output == literal_response(bank, n, precision),
                            "clean overwrite endpoint failed")
                    clean_endpoints += 1
                states += 1
            require(len(seen) == (1 << (public_bits + clean)), "missing state")
            cases += 1
    return {"complete_permutation_cases": cases, "full_states": states,
            "clean_endpoints": clean_endpoints}


def larger_interfaces() -> dict[str, int]:
    cases, endpoints, erasure_collisions = 0, 0, 0
    for n in range(6):
        for precision in range(9):
            size, clean = dimensions(n, precision)
            expected = size * precision - sum(
                comb(n, j) * max(precision - 2 * j, 0) for j in range(n + 1))
            require(clean == expected, "capacity complement failed")
            if precision >= 2 * n:
                require(clean == n * size, "high-precision closed form failed")
            for sample in range(8):
                bank = tuple((sample * 17 + u * u + 3 * u) % (1 << precision)
                             for u in range(size))
                auxiliary = ((1 << clean) - 1) if sample & 1 else 0
                output, garbage = overwrite(bank, auxiliary, n, precision)
                require(overwrite(output, garbage, n, precision, True) ==
                        (bank, auxiliary), "larger inverse failed")
                if auxiliary == 0:
                    require(output == literal_response(bank, n, precision),
                            "larger clean endpoint failed")
                    endpoints += 1
                cases += 1
            zero = (0,) * size
            for bit in range(clean):
                first = overwrite(zero, 0, n, precision, True)
                second = overwrite(zero, 1 << bit, n, precision, True)
                require(first[1] == second[1] == 0, "fiber witness is not clean")
                require(first[0] != second[0], "kernel bit was not independent")
                require(overwrite(second[0], 0, n, precision) == (zero, 1 << bit),
                        "lost-bit witness failed")
                erasure_collisions += 1
    return {"larger_interfaces": cases, "larger_clean_endpoints": endpoints,
            "independent_garbage_bit_witnesses": erasure_collisions}


def dirty_capacity() -> dict[str, int]:
    """Pigeonhole counts include every dirty state, even with changed outputs."""
    cases = 0
    for lost in range(1, 9):
        for dirty in range(6):
            for clean in range(lost):
                inputs = 1 << (lost + dirty)
                outputs = 1 << (clean + dirty)
                require(inputs > outputs, "undercapacity was accepted")
                cases += 1
    return {"dirty_undercapacity_comparisons": cases}


def controls() -> dict[str, int]:
    rejected = 0
    invalid = [((0,), 0, -1, 1), ((0,), 0, 9, 1), ((0,), 0, 0, 17),
               ((0,), 0, True, 1), ((2,), 0, 0, 1), ((0, 0), 0, 0, 1),
               ((0,), -1, 0, 1), ((0,), 1, 0, 1), ((0,), 0, 0, -1)]
    for bank, auxiliary, n, precision in invalid:
        try:
            overwrite(bank, auxiliary, n, precision)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid interface was accepted")
    # Replacing pi^(2|u|) by pi^|u| produces a wrong public endpoint.
    bank = chart((0, 1), 1, 3, "Tinv")
    require(overwrite(bank, 0, 1, 3)[0] != chart((0, 2), 1, 3, "S"),
            "wrong-valuation control did not distinguish")
    # Forgetting one retained bit merges two legal inputs with the same output.
    x0 = overwrite((0, 0), 0, 1, 3, True)[0]
    x1 = overwrite((0, 0), 1, 1, 3, True)[0]
    y0, h0 = overwrite(x0, 0, 1, 3)
    y1, h1 = overwrite(x1, 0, 1, 3)
    require(x0 != x1 and y0 == y1 and (h0 >> 1) == (h1 >> 1),
            "garbage-erasure collision control failed")
    # Uninitialized auxiliary bits can leak into the required output.
    require(overwrite((0, 0), 1, 1, 3)[0] != (0, 0),
            "dirty-in-place-of-clean control did not distinguish")
    require(rotate((0, 7), 0, 3) != ((0, 0), 0),
            "zeroing all discarded data was accepted")
    try:
        overwrite((0,), 0, 0, 1, 1)
    except ValueError:
        rejected += 1
    else:
        raise RuntimeError("non-Boolean inverse flag was accepted")
    return {"invalid_input_controls": rejected, "semantic_controls": 4}


def main() -> None:
    receipt = {"status": "PASS", "claim_type": "scoped proof with finite corroboration"}
    for result in (complete_permutations(), larger_interfaces(), dirty_capacity(), controls()):
        receipt.update(result)
    package = Path(__file__).resolve().parent
    files = ("engine.py", "verify.py", "PROOF.md", "README.md", "TASK.json",
             "SOURCES.json", "VERIFY.json")
    receipt["sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                         for name in files}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
