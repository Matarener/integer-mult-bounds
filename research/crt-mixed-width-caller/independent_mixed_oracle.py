"""Independent mixed-height caller oracle, written before primary inspection.

Uses the earlier separate FIFO network compiler and brute-force CRT decoding.
Host arrays/caches are semantic tools, not a fixed-tape time claim.
"""
from functools import lru_cache
import hashlib
from itertools import product
import json
from math import prod
from pathlib import Path
import types


COMPILER_SHA256 = "7a58689072b730201a6b4007f7b2524db2abff460a3116cfa42821fb2e1b63a5"


def load_compiler():
    path = Path(__file__).with_name("independent_benes_oracle.py")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != COMPILER_SHA256:
        raise ValueError("earlier separate FIFO compiler bytes changed")
    module = types.ModuleType("_earlier_fifo_network_oracle")
    module.__file__ = str(path)
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


COMPILER = load_compiler()


def global_rows(height, ell):
    if not 1 <= height <= ell or height not in (ell - 1, ell):
        raise ValueError("mixed adjacent heights required")
    if height == ell:
        return tuple(range(2 * height - 1))
    return tuple(r if r <= ell - 2 else r + 2 for r in range(2 * height - 1))


@lru_cache(None)
def decode_by_search(values, moduli):
    if any(x >= modulus for x, modulus in zip(values, moduli)):
        return None
    prefixes = []
    prefix = 1
    for modulus in moduli:
        prefixes.append(prefix)
        prefix *= modulus
    candidates = [integer for integer in range(prefix)
                  if all((integer * pow(prefix_i, -1, modulus)) % modulus == value
                         for prefix_i, modulus, value in zip(prefixes, moduli, values))]
    if len(candidates) != 1:
        raise ValueError("scaled CRT residues do not select one integer")
    return candidates[0]


def offsets(state, moduli, level):
    group_size = 1 << level
    shifts = {}
    for start in range(0, len(state), group_size):
        middle = start + group_size // 2
        lower = decode_by_search(tuple(state[start:middle]), tuple(moduli[start:middle]))
        factor = prod(moduli[start:middle])
        for axis in range(middle, start + group_size):
            shifts[axis] = (0 if lower is None else lower * pow(factor, -1, moduli[axis]) % moduli[axis])
            factor *= moduli[axis]
    return shifts


@lru_cache(None)
def network(height, modulus, shift):
    size = 1 << height
    permutation = tuple((x + shift) % modulus if x < modulus else x for x in range(size))
    return COMPILER.compile_levelwise(permutation)


def atomic_endpoint(values, moduli, reverse=False):
    state = list(values)
    levels = range(1, len(state).bit_length())
    for level in reversed(tuple(levels)) if reverse else levels:
        shifts = offsets(state, moduli, level)
        for axis, shift in shifts.items():
            if state[axis] < moduli[axis]:
                state[axis] = (state[axis] + (-shift if reverse else shift)) % moduli[axis]
    return tuple(state)


def microscopic_endpoint(values, moduli, widths, reverse=False):
    state = tuple(values)
    ell = max(widths)
    maps = [{g: r for r, g in enumerate(global_rows(height, ell))} for height in widths]
    levels = tuple(range(1, len(state).bit_length()))
    rows = tuple(range(2 * ell - 1))
    row_checks = omission_checks = 0
    for level in reversed(levels) if reverse else levels:
        frozen = offsets(state, moduli, level)
        for g in reversed(rows) if reverse else rows:
            controls = {}
            for axis, shift in frozen.items():
                r = maps[axis].get(g)
                if r is not None:
                    target, table = network(widths[axis], moduli[axis], shift)[r]
                    if target != (g if g < ell else 2 * ell - 2 - g):
                        raise ValueError("local/global active target-bit mismatch")
                    controls[axis] = (target, table[state[axis]])
            snapshot = state
            target_state = list(snapshot)
            for axis, (target, flip) in controls.items():
                target_state[axis] ^= flip << target
                for other, (other_target, _) in controls.items():
                    changed = list(snapshot)
                    changed[other] ^= 1 << other_target
                    changed_offsets = offsets(changed, moduli, level)
                    r = maps[axis][g]
                    changed_flip = network(widths[axis], moduli[axis], changed_offsets[axis])[r][1][changed[axis]]
                    if changed_flip != flip:
                        raise ValueError("control reads an active target")
                    omission_checks += 1
            # Independently recompute controls after each reverse-ordered write.
            sequential = list(snapshot)
            for axis in reversed(tuple(controls)):
                shift = offsets(sequential, moduli, level)[axis]
                target, table = network(widths[axis], moduli[axis], shift)[maps[axis][g]]
                sequential[axis] ^= table[sequential[axis]] << target
            if sequential != target_state or offsets(target_state, moduli, level) != frozen:
                raise ValueError("row commutation or frozen left-child controls failed")
            state = tuple(target_state)
            row_checks += 1
    return state, row_checks, omission_checks


def encode(values, widths):
    result = shift = 0
    for value, width in zip(values, widths):
        result |= value << shift
        shift += width
    return result


def check_rectangle(moduli, widths):
    digest = hashlib.sha256()
    images = set()
    columns = valid_columns = rows = omissions = 0
    byte_width = (sum(widths) + 7) // 8
    for original in product(*(range(1 << h) for h in widths)):
        actual, count, checked = microscopic_endpoint(original, moduli, widths)
        expected = atomic_endpoint(original, moduli)
        recovered, inverse_count, inverse_checked = microscopic_endpoint(actual, moduli, widths, reverse=True)
        if actual != expected or recovered != original:
            raise ValueError("all-padded endpoint or literal inverse mismatch")
        valid = all(x < modulus for x, modulus in zip(original, moduli))
        if valid:
            prefix = 1
            integer = 0
            prefixes = []
            for value, modulus in zip(original, moduli):
                prefixes.append(prefix)
                integer += value * prefix
                prefix *= modulus
            direct = tuple(integer * pow(prefix_i, -1, modulus) % modulus
                           for prefix_i, modulus in zip(prefixes, moduli))
            if actual != direct:
                raise ValueError("valid global CRT endpoint mismatch")
            valid_columns += 1
        if valid != all(x < modulus for x, modulus in zip(actual, moduli)):
            raise ValueError("valid rectangle was not preserved")
        images.add(actual)
        digest.update(encode(actual, widths).to_bytes(byte_width, "big"))
        rows += count + inverse_count
        omissions += checked + inverse_checked
        columns += 1
    if len(images) != columns:
        raise ValueError("full padded endpoint is not bijective")
    return {"moduli": list(moduli), "declared_widths": list(widths),
            "dirty_columns": columns, "valid_columns": valid_columns,
            "forward_inverse_global_rows": rows,
            "active_target_omission_checks": omissions,
            "endpoint_sha256": digest.hexdigest()}


def negative_controls():
    layers = network(2, 3, 1)
    state = gated = 1
    trace = [state]
    for target, table in layers:
        state ^= table[state] << target
        if gated < 3:
            gated ^= table[gated] << target
        trace.append(state)
    if state != 2 or gated == state or 3 not in trace:
        raise ValueError("current-target-validity mutant was not detected")
    # Treating the minimal network as low-bit-only in a larger declared field
    # moves an invalid padded value that the declared permutation must fix.
    padded = 5
    low = padded & 3
    for target, table in layers:
        low ^= table[low] << target
    broken = (padded & ~3) | low
    expected = COMPILER.endpoint(network(3, 3, 1), padded)
    if expected != padded or broken == expected:
        raise ValueError("minimal-width substitution mutant was not detected")
    return {"current_target_validity_gate": {"size": 4, "modulus": 3, "offset": 1,
                                              "input": 1, "literal_trace": trace,
                                              "expected": state, "wrong": gated},
            "low_minimal_width_substitution": {"declared_size": 8, "modulus": 3,
                                                "offset": 1, "input": padded,
                                                "expected": expected, "wrong": broken}}


def main():
    for ell in range(2, 65):
        for height in (ell - 1, ell):
            mapping = global_rows(height, ell)
            if len(mapping) != 2 * height - 1 or tuple(sorted(set(mapping))) != mapping:
                raise ValueError("row embedding is not ordered and injective")
            for r, g in enumerate(mapping):
                local_bit = r if r < height else 2 * height - 2 - r
                global_bit = g if g < ell else 2 * ell - 2 - g
                if local_bit != global_bit:
                    raise ValueError("embedding does not preserve the common target bit")
    print(json.dumps({"status": "PASS_PREIMPLEMENTATION_MIXED_CALLER_ORACLE",
                      "rectangles": [check_rectangle((5, 7, 11, 13), (3, 3, 4, 4)),
                                     check_rectangle((5, 3), (3, 3))],
                      "negative_controls": negative_controls(),
                      "compiler_sha256": COMPILER_SHA256,
                      "scope": "independent mixed-row caller and brute scaled-CRT oracle; predecessor omission argument reused; no tape/E theorem"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
