"""Separate interval oracle for the source dense guard, before primary read.

Complete numeric U|T|Y address order; host arithmetic is semantic only.
The fixtures are source-predicate projections, not three-reservoir callers.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
import types


SOURCE_SHA256 = "681e2e3d71fa74c8b9b326f3860104fd9d89590a222e26ae6ee718d1fd40ff2e"


@dataclass(frozen=True)
class Shape:
    name: str
    G: int
    K: int
    H: int
    Y: int
    positions: tuple[int, ...]

    @property
    def L(self):
        return 2 * self.H + self.Y


SHAPES = (Shape("two_active_digits", 1, 5, 2, 10, (0, 5)),
          Shape("single_with_dirty_spectators", 2, 7, 3, 9, (1,)))


def split(address, shape):
    controls, y = divmod(address, 2 ** shape.Y)
    u, t = divmod(controls, 2 ** shape.H)
    return u, t, y


def pack(u, t, y, shape):
    return (u * (2 ** shape.H) + t) * (2 ** shape.Y) + y


def interval_good(u, t, y, shape, *, lower_strict=False, upper_inclusive=False,
                  mix_target_parity=False, ignore_upper_active=False):
    base = 2 ** shape.G
    count = len(shape.positions)
    active_digits = range(1 if ignore_upper_active else count)
    for i in active_digits:
        if (u // (base ** i)) % base == base - 1:
            return False
        if (t // (base ** i)) % base == base - 1:
            return False
    lower = 2 * base
    upper = 2 ** (shape.K - 1) - lower
    for position in shape.positions:
        value = (y // (2 ** (position + 1))) % (2 ** (shape.K - 1))
        if mix_target_parity:
            value += (y // (2 ** position)) % 2
        if not (value > lower if lower_strict else value >= lower):
            return False
        if not (value <= upper if upper_inclusive else value < upper):
            return False
    return True


def load_source(path):
    path = Path(path)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError("retained guard source changed")
    module = types.ModuleType("_guard_retained_source")
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def good_mask(shape, source=None):
    accepted = bytearray()
    for address in range(1 << shape.L):
        u, t, y = split(address, shape)
        expected = interval_good(u, t, y, shape)
        if source is not None:
            actual = source.good(u, t, y, bits=shape.G, positions=shape.positions, guard=shape.K)
            linear = source.linear_guard(u, t, y, bits=shape.G, positions=shape.positions,
                                         guard=shape.K, control_bits=shape.H, ybits=shape.Y)
            if actual != expected or linear != expected:
                raise ValueError("source predicate or source bit scan differs from interval oracle")
        accepted.append(int(expected))
    return bytes(accepted)


def boundary_checks(shape):
    base = 2 ** shape.G
    low = 2 * base
    high = 2 ** (shape.K - 1) - low
    initial_y = sum(low * (2 ** (p + 1)) for p in shape.positions)
    checks = []
    for position in shape.positions:
        for value, expected in ((low - 1, False), (low, True),
                                (high - 1, True), (high, False)):
            y = initial_y + (value - low) * (2 ** (position + 1))
            if interval_good(0, 0, y, shape) != expected:
                raise ValueError("interval boundary error")
            checks.append({"position": position, "guard_value": value, "good": expected})
    return checks


def inspect(shape, source):
    mask = good_mask(shape, source)
    ignored = [("target_parity", p) for p in shape.positions]
    for bit in range(len(shape.positions) * shape.G, shape.H):
        ignored.append(("inactive_u", shape.Y + shape.H + bit))
        ignored.append(("inactive_t", shape.Y + bit))
    occupied = {q for p in shape.positions for q in range(p, p + shape.K)}
    ignored.extend(("Y_spectator", q) for q in range(shape.Y) if q not in occupied)
    toggles = 0
    for address, accepted in enumerate(mask):
        for _, bit in ignored:
            if mask[address ^ (1 << bit)] != accepted:
                raise ValueError("dirty spectator or target parity affected guard")
            toggles += 1
    ascii_good = bytes(48 + bit for bit in mask)
    ascii_bad = bytes(49 - bit for bit in mask)
    return {"name": shape.name, "G": shape.G, "K": shape.K, "H": shape.H,
            "Y": shape.Y, "positions": list(shape.positions), "L": shape.L,
            "addresses": len(mask), "good": sum(mask), "bad": len(mask) - sum(mask),
            "good_mask_binary_sha256": hashlib.sha256(mask).hexdigest(),
            "good_mask_ascii_sha256": hashlib.sha256(ascii_good).hexdigest(),
            "bad_mask_ascii_sha256": hashlib.sha256(ascii_bad).hexdigest(),
            "ignored_bit_invariance_toggles": toggles,
            "ignored_bits": [{"role": role, "numeric_address_bit": bit} for role, bit in ignored],
            "boundaries": boundary_checks(shape),
            "domain": "complete U|T|Y source predicate projection; no back reservoir/payload permutation"}


def mutations():
    shape = SHAPES[0]
    witnesses = {}
    for label, options in (("strict_lower", {"lower_strict": True}),
                           ("inclusive_upper", {"upper_inclusive": True}),
                           ("target_parity_in_guard", {"mix_target_parity": True}),
                           ("ignore_upper_active_digit", {"ignore_upper_active": True})):
        for address in range(1 << shape.L):
            u, t, y = split(address, shape)
            expected = interval_good(u, t, y, shape)
            wrong = interval_good(u, t, y, shape, **options)
            if expected != wrong:
                witnesses[label] = {"address": address, "u": u, "t": t, "y": y,
                                    "expected_good": expected, "wrong_good": wrong}
                break
        else:
            raise ValueError("semantic mutation did not fail: " + label)
    dirty = SHAPES[1]
    y = 2 * (2 ** dirty.G) * (2 ** (dirty.positions[0] + 1))
    if not interval_good(4, 0, y, dirty) or interval_good(3, 0, y, dirty):
        raise ValueError("inactive/active upper-control distinction failed")
    witnesses["dirty_inactive_upper_control"] = {"u": 4, "t": 0, "y": y,
                                                  "expected_good": True,
                                                  "zero_initialization_assumption_wrong": False}
    return witnesses


def main():
    source = load_source(sys.argv[1])
    rows = [inspect(shape, source) for shape in SHAPES]
    if [row["good"] for row in rows] != [256, 13824]:
        raise ValueError("independently counted accepted cardinality mismatch")
    print(json.dumps({"status": "PASS_PREIMPLEMENTATION_DENSE_GUARD_ORACLE",
                      "source_sha256": SOURCE_SHA256, "fixtures": rows,
                      "negative_controls": mutations(),
                      "scope": "complete Boolean masks and boundary/dirty-coordinate controls; no sequential/tape tariff"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
