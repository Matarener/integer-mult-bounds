#!/usr/bin/env python3
"""Source-bound certificate for the all-depth P104 Newton product entrance.

Nick Petalas. Apache-2.0. No predecessor executable is imported.
The written proof quantifies over depth; the literal tensor fixture has depth two.
"""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/p104-rounded-collector/inputs/WORD.json"
NATIVE = "research/p104-rounded-collector/inputs/NATIVE.json.gz"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def load():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(path.is_file() and not path.is_symlink(), "missing regular input " + row["path"])
            need(path.stat().st_size <= 4_000_000, "source byte bound")
            raw = path.read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256 " + row["path"])
    word = json.loads((ROOT / WORD).read_bytes())
    native = json.loads(gzip.decompress((ROOT / NATIVE).read_bytes()))
    need(len(word["program"]) == 5398 and len(word["initial_frames"]) == 358, "word dimensions")
    need(len(native["transports"]) == 1245, "native class count")
    return word, native


def add_row(target, source, coefficient):
    for name, value in source.items():
        total = target.get(name, Fraction(0)) + coefficient * value
        if total:
            target[name] = total
        else:
            target.pop(name, None)


def exponent(value):
    """Negative pi valuation, clipped to zero, for a nonzero dyadic rational."""
    need(value != 0, "nonzero valuation argument")
    denominator = value.denominator
    need(denominator & (denominator - 1) == 0, "dyadic scalar coefficient")
    return 2 * (denominator.bit_length() - 1)


def reverse_coefficient(program, event_index, target, source):
    row = {target: Fraction(1)}
    for event in reversed(program[:event_index + 1]):
        kind, role = event[:2]
        if kind == "add" and role in row:
            add_row(row, {event[2]: row[role]}, Fraction(str(event[3])))
        elif kind == "sign" and role in row:
            row[role] = -row[role]
        elif kind == "zero":
            row.pop(role, None)
        elif kind == "erase":
            need(role not in row, "reverse private lifetime")
    return row.get(source, Fraction(0))


def scalar_certificate(word):
    names = sorted(word["initial_frames"])
    rows = {name: {name: Fraction(1)} for name in names}
    bounds, witnesses, erasures = dict.fromkeys(names, 0), {}, []
    for index, event in enumerate(word["program"]):
        kind, role = event[:2]
        if kind == "zero":
            need(role not in rows, "private allocation")
            rows[role] = {}
        elif kind == "erase":
            need(rows[role] == {}, "literal symbolic private zero")
            del rows[role]
            erasures.append(index)
        elif kind == "add":
            need(role != event[2], "distinct ADD roles")
            add_row(rows[role], rows[event[2]], Fraction(str(event[3])))
        elif kind == "sign":
            need(Fraction(str(event[2])) == -1, "source sign coefficient")
            rows[role] = {name: -value for name, value in rows[role].items()}
        else:
            need(kind == "transport", "event alphabet")
        for source, value in rows.get(role, {}).items():
            power = exponent(value)
            if power > bounds[source]:
                bounds[source] = power
                witnesses[source] = {"event": index, "target": role, "coefficient": str(value)}
    need(set(rows) == set(names) and len(erasures) == 8, "final lifetime inventory")
    for name in names:
        expected = 4 if name.startswith("Y") else 2 if name.startswith("N") else 0
        need(bounds[name] == expected, "sharp source exponent " + name)
        if not name.startswith("X"):
            need(rows[name] == {name: Fraction(1)}, "non-X dirty restoration " + name)
        else:
            need(rows[name].get(name) == 1, "X identity component")
            need(all(s == name or s.startswith("Y") for s in rows[name]), "X shear source")
    for source, witness in witnesses.items():
        actual = reverse_coefficient(word["program"], witness["event"], witness["target"], source)
        need(actual == Fraction(witness["coefficient"]), "independent reverse witness " + source)
    serialized = {name: {s: str(q) for s, q in sorted(row.items())} for name, row in sorted(rows.items())}
    return {"source_exponents": bounds, "attaining_witnesses": witnesses,
            "exponent_histogram": dict(Counter(map(str, bounds.values()))),
            "erasure_events": erasures, "final_scalar_rows_sha256": digest(serialized)}


def wrapper_plan(record):
    need(set(record) == {"matrix_rows", "linear_Z4", "quadratic_rows", "offset", "phase"},
         "wrapper schema")
    rows, linear, quadratic = (record[k] for k in ("matrix_rows", "linear_Z4", "quadratic_rows"))
    need(len(rows) == len(linear) == len(quadratic) == 9, "wrapper dimension")
    need(all(type(v) is int and 0 <= v < 512 for v in rows + quadratic), "binary row range")
    need(all(type(v) is int and 0 <= v < 4 for v in linear), "linear phase range")
    need(type(record["offset"]) is int and 0 <= record["offset"] < 512, "offset range")
    need(type(record["phase"]) is int and 0 <= record["phase"] < 4, "constant phase range")
    plan = []
    for x in range(512):
        image = record["offset"] ^ sum(((x & row).bit_count() % 2) << j
                                       for j, row in enumerate(rows))
        phase = record["phase"]
        for j in range(9):
            if x & (1 << j):
                phase += linear[j] + 2 * ((x & quadratic[j] & ~((1 << (j + 1)) - 1)).bit_count())
        plan.append((image, phase % 4))
    need(len({image for image, _ in plan}) == 512, "wrapper address bijection")
    return tuple(plan)


def bind(word, native):
    frames = {name: tuple(frame) for name, frame in word["initial_frames"].items()}
    occurrences, plans, wrapper_hashes = {}, {}, []
    for record in native["transports"]:
        recipe = record["recipe"]
        need(type(recipe["rank"]) is int and 1 <= recipe["rank"] <= 9, "native rank bound")
        right, left = wrapper_plan(recipe["right"]), wrapper_plan(recipe["left"])
        wrapper_hashes.extend((digest(right), digest(left)))
        for index in record["events"]:
            need(type(index) is int and 0 <= index < 5398 and index not in occurrences,
                 "unique bounded native event")
            occurrences[index] = record
            plans[index] = (right, recipe["rank"], left)
    for index, event in enumerate(word["program"]):
        kind, role = event[:2]
        if kind == "zero":
            need(role not in frames, "frame allocation")
            frames[role] = tuple(event[2])
        elif kind == "erase":
            need(frames.pop(role) == tuple(event[2]), "erase frame")
        elif kind == "add":
            need(frames[role] == frames[event[2]] == tuple(event[4]), "ADD common frame")
        elif kind == "transport":
            need(frames[role] == tuple(event[2]), "chronological old frame")
            record = occurrences[index]
            need((record["old"], record["new"], record["recipe"]["rank"]) ==
                 (event[2], event[3], event[4]), "native occurrence binding")
            frames[role] = tuple(event[3])
        else:
            need(kind == "sign" and Fraction(str(event[2])) == -1
                 and frames[role] == tuple(event[3]), "sign frame")
    need(frames == {n: tuple(f) for n, f in word["final_frames"].items()}, "final frame map")
    need(len(occurrences) == 2070, "complete native occurrence inventory")
    return plans, {"classes": len(native["transports"]), "occurrences": len(occurrences),
                   "wrappers": len(wrapper_hashes), "wrapper_plans_sha256": digest(wrapper_hashes)}


def rotate(a, b, phase):
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def floor_pair(a, b):
    """Credited signed-floor convention; no pre-rounding or nearest-even step."""
    dr, di = a[0] - b[0], a[1] - b[1]
    sr, si = b[0] + dr // 2, b[1] + di // 2
    out_b = sr - (-di) // 2, si - dr // 2
    return (out_b[0] - di, out_b[1] + dr), out_b


def exact_pair(a, b):
    ar, ai = a
    br, bi = b
    numerators = (ar + br - ai + bi, ai + bi + ar - br,
                  ar + br + ai - bi, ai + bi - ar + br)
    need(all(n % 2 == 0 for n in numerators), "nonintegral ideal butterfly")
    return ((numerators[0] // 2, numerators[1] // 2),
            (numerators[2] // 2, numerators[3] // 2))


def tensor_wrapper(values, plan, depth):
    need(type(depth) is int and 1 <= depth <= 2, "finite diagnostic depth bound")
    need(len(values) == 1 << (9 * depth) and len(plan) == 512, "tensor wrapper width")
    out = [(0, 0)] * len(values)
    for x, value in enumerate(values):
        target, phase = 0, 0
        for block in range(depth):
            image, power = plan[(x >> (9 * block)) & 511]
            target |= image << (9 * block)
            phase += power
        out[target] = rotate(*value, phase)
    return out


def tensor_native(values, plan, depth, reverse_blocks=False):
    right, rank, left = plan
    values = tensor_wrapper(values, right, depth)
    blocks = list(range(depth))
    if reverse_blocks:
        blocks.reverse()
    pairs = 0
    for block in blocks:
        for coordinate in range(rank):
            step = 1 << (9 * block + coordinate)
            for base in range(0, len(values), 2 * step):
                for offset in range(step):
                    low, high = base + offset, base + offset + step
                    a, b = values[low], values[high]
                    literal, ideal = floor_pair(a, b), exact_pair(a, b)
                    need(literal == ideal, "signed-floor versus exact tensor pair")
                    values[low], values[high] = literal
                    pairs += 1
    return tensor_wrapper(values, left, depth), pairs


def tensor_fixture(plans):
    """One full nonseparable B18 array, both actual rank-seven recipes."""
    size = 1 << 18
    initial = [(1, 2 if (x & 1 and x & 512) else 0) for x in range(size)]
    a, b, c, d = (initial[x] for x in (0, 1, 512, 513))
    determinant = (a[0] * d[0] - a[1] * d[1] - b[0] * c[0] + b[1] * c[1],
                   a[0] * d[1] + a[1] * d[0] - b[0] * c[1] - b[1] * c[0])
    need(determinant == (0, 2), "actual nonseparable two-block minor")
    forward, first = tensor_native(initial, plans[2031], 2)
    returned, second = tensor_native(forward, plans[2033], 2)
    need(returned == initial, "literal tensor-two actual return")
    other_order, third = tensor_native(initial, plans[2031], 2, reverse_blocks=True)
    need(other_order == forward and third == first, "disjoint-block stage commutation")
    # This input is 1 + pi^2*x_0*x_9, not a simple tensor across the blocks.
    return {"depth": 2, "address_bits": 18, "gaussian_coordinates": size,
            "input_polynomial": "1 + pi^2*x_0*x_9", "block_matrix_determinant": "2i",
            "native_events": [2031, 2033], "rank_per_transport": 14,
            "exact_pair_comparisons": first + second + third,
            "forward_sha256": digest(forward), "return_sha256": digest(returned),
            "reverse_block_order_sha256": digest(other_order)}


def algebra_controls():
    count, integral, rejected = 0, 0, 0
    for ar in range(-3, 4):
        for ai in range(-3, 4):
            for br in range(-3, 4):
                for bi in range(-3, 4):
                    count += 1
                    if (ar - br + ai - bi) % 2 == 0:
                        need(floor_pair((ar, ai), (br, bi)) == exact_pair((ar, ai), (br, bi)),
                             "Gaussian parity signed pair")
                        integral += 1
                    else:
                        try:
                            exact_pair((ar, ai), (br, bi))
                        except ValueError:
                            rejected += 1
    need(count == 2401 and integral + rejected == count, "complete small pair domain")
    # A payload lift retains q; tensoring the register map would replace q by q^2.
    need(exponent(Fraction(1, 4)) == 4 and exponent(Fraction(1, 4) ** 2) == 8,
         "payload/register tensor distinction")
    # pi*x_0*x_1 has every one-bit slice in B1, but is outside B2.
    slices = [(0, 0), (0, 0), (0, 0), (1, 1)]
    for low, high in ((0, 1), (2, 3), (0, 2), (1, 3)):
        difference = tuple(a - b for a, b in zip(slices[low], slices[high], strict=True))
        need(sum(difference) % 2 == 0, "slice Newton parity")
    first = list(slices)
    first[0], first[1] = exact_pair(slices[0], slices[1])
    first[2], first[3] = exact_pair(slices[2], slices[3])
    try:
        exact_pair(first[0], first[2])
    except ValueError:
        slice_counterexample = True
    else:
        slice_counterexample = False
    need(slice_counterexample, "separate slice domains incorrectly admitted")
    return {"small_pairs": count, "integral": integral, "nonintegral_rejected": rejected,
            "quarter_payload_exponent": 4, "incorrect_squared_quarter_exponent": 8,
            "separate_slice_domains_fail_composition": slice_counterexample,
            "slice_counterexample": "pi*x_0*x_1"}


def result():
    word, native = load()
    scalar = scalar_certificate(word)
    plans, binding = bind(word, native)
    return {"schema_version": 1, "claim": "sharp independent product entrance for every positive payload depth",
            "proof_scope": "written universal lifting; finite source certificate and one literal depth-two fixture",
            "scalar": scalar, "binding": binding, "algebra_controls": algebra_controls(),
            "tensor_fixture": tensor_fixture(plans)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    actual = result()
    if args.write_receipt:
        with args.write_receipt.open("x") as stream:
            stream.write(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "RECEIPT.json").read_text())
        need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), "complete receipt equality")
    print("PASS_P104_TENSOR_NEWTON all_positive_depths source_exponents=104x4,78x2,176x0 "
          "literal_depth=2 nonseparable_coordinates=262144 no_new_kappa")


if __name__ == "__main__":
    main()
