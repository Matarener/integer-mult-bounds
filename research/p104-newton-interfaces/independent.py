"""Separate full-prefix witness and scalar-port checks for the P104 interface.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
This implementation imports neither the producer/consumer checker nor the
PR3382 lattice model. Its scalar port conclusion is conditional on the separate
phase-sensitive frame-path certificate. The numerical witness is one point,
not a universal full-prefix or full-word theorem.
"""

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


WORD_SHA = "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50"
NATIVE_SHA = "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d"
N = 512
ZERO = (0, 0)


class IndependentError(ValueError):
    """A source or exact arithmetic obligation failed."""


def check(condition, message):
    if not condition:
        raise IndependentError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def pinned(path, expected):
    path = Path(path)
    check(path.is_file() and not path.is_symlink(), "regular source required")
    data = path.read_bytes()
    check(digest(data) == expected, "independent source hash mismatch")
    return data


def rotate(z, exponent):
    a, b = z
    for _ in range(exponent % 4):
        a, b = -b, a
    return a, b


def wrapper(values, recipe):
    rows = recipe["matrix_rows"]
    linear = recipe["linear_Z4"]
    quadratic = recipe["quadratic_rows"]
    check(len(rows) == len(linear) == len(quadratic) == 9, "wrapper dimensions")
    out = [None] * N
    for x, value in enumerate(values):
        address = recipe["offset"]
        phase = recipe["phase"]
        for bit in range(9):
            address ^= ((rows[bit] & x).bit_count() % 2) << bit
            if x >> bit & 1:
                upper = quadratic[bit] & x & ~((1 << (bit + 1)) - 1)
                phase += linear[bit] + 2 * upper.bit_count()
        check(0 <= address < N and out[address] is None, "wrapper bijection")
        out[address] = rotate(value, phase)
    return out


def exact_literal_pair(a, b):
    """Compare direct Gaussian numerators with componentwise signed floors."""
    p, q = a[0] - b[0], a[1] - b[1]
    numerators = (a[0] + b[0] - q, a[1] + b[1] + p,
                  a[0] + b[0] + q, a[1] + b[1] - p)
    check(all(x % 2 == 0 for x in numerators), "nonintegral ideal butterfly")
    ideal = ((numerators[0] // 2, numerators[1] // 2),
             (numerators[2] // 2, numerators[3] // 2))
    middle = (b[0] + p // 2, b[1] + q // 2)
    second = (middle[0] - (-q) // 2, middle[1] - p // 2)
    literal = ((second[0] - q, second[1] + p), second)
    check(literal == ideal, "signed floor differs from ideal")
    return literal


def native_apply(values, recipe):
    out = wrapper(values, recipe["right"])
    for bit in range(recipe["rank"]):
        step = 1 << bit
        for address in range(N):
            if address & step == 0:
                other = address | step
                out[address], out[other] = exact_literal_pair(out[address], out[other])
    return wrapper(out, recipe["left"])


def first_newton_failure(values):
    coefficients = values[:]
    for bit in range(9):
        step = 1 << bit
        for x in range(N):
            if x & step:
                a, b = coefficients[x], coefficients[x ^ step]
                coefficients[x] = a[0] - b[0], a[1] - b[1]
    for mask, coefficient in enumerate(coefficients):
        a, b = coefficient
        for power in range(mask.bit_count()):
            if (a + b) % 2:
                return {"mask": mask, "degree": mask.bit_count(),
                        "coefficient": list(coefficient), "pi_valuation": power}
            a, b = (a + b) // 2, (b - a) // 2
    return None


def bind_native(word, native):
    index = {}
    for row in native["transports"]:
        for event in row["events"]:
            check(event not in index, "duplicate occurrence")
            op = word["program"][event]
            check(op[0] == "transport" and op[2:5] ==
                  [row["old"], row["new"], row["recipe"]["rank"]],
                  "native occurrence binding")
            index[event] = row["recipe"]
    return index


def full_prefix_witness(word, native):
    recipes = bind_native(word, native)
    frames = {name: frame[:] for name, frame in word["initial_frames"].items()}
    state = {name: [ZERO] * N for name in frames}
    state["Y27"][0] = (64, 0)
    check(all(first_newton_failure(v) is None for v in state.values()),
          "all358 initial banks in B9")
    stronger_failure = first_newton_failure([(a // 4, b // 4) for a, b in state["Y27"]])
    check(stronger_failure is not None, "the witness must fail the strengthened Y admission")
    active_native = []
    active_add = []
    failures = []
    pairs = 0
    native_occurrences = 0
    for event, op in enumerate(word["program"][:2025]):
        kind, target = op[:2]
        check(target in state, "initial field lifetime")
        if kind == "transport":
            check(frames[target] == op[2] and event in recipes, "prefix frame and native")
            native_occurrences += 1
            if any(value != ZERO for value in state[target]):
                state[target] = native_apply(state[target], recipes[event])
                active_native.append(event)
                pairs += 256 * recipes[event]["rank"]
            frames[target] = op[3][:]
        elif kind == "add":
            source, coefficient, frame = op[2:]
            check(frames[target] == frames[source] == frame, "prefix ADD frame")
            c = Fraction(str(coefficient))
            p, q = c.numerator, c.denominator
            if any(value != ZERO for value in state[source]):
                scaled = []
                for real, imag in state[source]:
                    check(p * real % q == p * imag % q == 0, "nonintegral quarter source")
                    scaled.append((p * real // q, p * imag // q))
                state[target] = [(a[0] + b[0], a[1] + b[1])
                                 for a, b in zip(state[target], scaled)]
                active_add.append(event)
        elif kind == "sign":
            check(len(op) == 4 and op[2] == "-1" and frames[target] == op[3],
                  "sign grammar and frame")
            state[target] = [(-a, -b) for a, b in state[target]]
        else:
            raise IndependentError("unexpected prefix opcode")
        if any(value != ZERO for value in state[target]):
            failure = first_newton_failure(state[target])
            if failure is not None:
                failures.append({"event": event, "field": target, **failure})
    check(len(active_native) == 20 and len(active_add) == 6, "full witness active events")
    check(first_newton_failure(state["D31"]) is not None, "D31 entrance must fail")
    entrance = {}
    for name in ("D31", "D30", "D29", "D28", "D27", "Q7"):
        entrance[name] = {"sha256": digest(canonical(state[name])),
                          "newton_failure": first_newton_failure(state[name]),
                          "frame": frames[name],
                          "nonzero_complex_entries": sum(z != ZERO for z in state[name])}
    return {"status": "PASS", "scope": "one explicit point, full events0..2024",
            "initial_banks": len(frames), "point": {"Y27[0]": [64, 0], "all_other_components": 0},
            "all_initial_banks_in_B9": True, "initial_Y27_not_in_4B9": stronger_failure,
            "all_actual_quarters_integral": True,
            "all_actual_literal_native_pairs_exact": True,
            "prefix_native_occurrences_bound": native_occurrences,
            "active_native_events": active_native, "active_add_events": active_add,
            "active_pair_comparisons": pairs,
            "first_full_prefix_B9_failure": failures[0], "entrance": entrance}


def scalar_ports(word):
    ys = {"Y" + str(j) for j in list(range(22, 33)) + list(range(63, 104))}
    roles = ys | {"D" + str(j) for j in range(27, 32)}
    roles |= {"G" + str(j) for j in range(27, 32)} | {"Q7"}
    rows = {name: {name: Fraction(1)} for name in roles}
    outputs = defaultdict(dict)
    ports = []
    counts = Counter()
    for event, op in enumerate(word["program"][:4517]):
        kind, target = op[:2]
        if event == 2025:
            check(kind == "zero" and target == "C", "private allocation")
            rows["C"] = {}
        elif event == 2039:
            check(kind == "erase" and target == "C" and not rows["C"], "private erasure")
            del rows["C"]
        elif kind == "add" and op[2] in rows:
            source, coefficient = op[2:4]
            c = Fraction(str(coefficient))
            destination = rows[target] if target in rows else outputs[target]
            for name, value in rows[source].items():
                destination[name] = destination.get(name, Fraction(0)) + c * value
            for name in list(destination):
                if not destination[name]:
                    del destination[name]
            if target not in rows:
                ports.append(event)
                counts[(source[0], target[0])] += 1
        elif target in rows:
            check(kind == "transport", "unmodelled write into closed roles")
    check(all(rows[name] == {name: Fraction(1)} for name in roles), "63 scalar restorations")
    x_rows = {name: row for name, row in outputs.items() if name.startswith("X")}
    check(len(x_rows) == 52, "52 actual X targets")
    signs = {}
    for name, row in x_rows.items():
        check(set(row) == ys and len(set(row.values())) == 1, "rank-one source sum")
        value = next(iter(row.values()))
        check(value in (Fraction(1, 2), Fraction(-1, 2)), "signed half increment")
        signs[name] = int(2 * value)
    check(Counter(signs.values()) == {1: 39, -1: 13}, "actual target signs")
    check(len(ports) == 675, "complete port count")
    return {"status": "PASS", "scope": "scalar rows in separately certified frame gauges",
            "frame_map_certificate_required": True, "restored_initial_rows": 63,
            "private_zero": True, "external_port_count": len(ports),
            "external_port_indices_sha256": digest(canonical(ports)),
            "external_port_counts": {a + "->" + b: v for (a, b), v in sorted(counts.items())},
            "X_target_signs": dict(sorted(signs.items())),
            "X_map": "Sum of outgoing increments pulled back through the certified port-frame gauges is sign_j * sum_{s in Y22..32,Y63..103} y_s / 2; this is not a final external X-array endpoint.",
            "all_initial_D_Q_G_coefficients_cancel_in_X_ports": True,
            "excluded": "External target updates/transports and all other word operations are not a full numerical execution."}


def verify_independent(word_path, native_path):
    word = json.loads(pinned(word_path, WORD_SHA))
    native = json.loads(gzip.decompress(pinned(native_path, NATIVE_SHA)))
    return {"status": "PASS", "source_sha256": {"word": WORD_SHA, "native": NATIVE_SHA},
            "full_prefix_witness": full_prefix_witness(word, native),
            "scalar_ports": scalar_ports(word)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    inputs = args.repo / "research/p104-rounded-collector/inputs"
    result = verify_independent(inputs / "WORD.json", inputs / "NATIVE.json.gz")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
