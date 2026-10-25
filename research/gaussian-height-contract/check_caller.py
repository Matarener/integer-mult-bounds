"""Exact rounded-state audit of the retained tensor compiler.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. The original compiler and generic rounding lemmas retain their
authors' credit. This is an arithmetic/interface model, not a tape execution.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import authenticate, canonical, digest, need, reject, add, scale, times, c_pair

COMPILER = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_tensor_compiler.py"
ZERO, ONE, I = (Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))


def norm(z):
    """Exact complex l1 norm, which dominates complex modulus."""
    return abs(z[0]) + abs(z[1])


def ceiling_log2(q):
    q = Q(q)
    need(q > 0, "positive logarithm argument")
    exponent = q.numerator.bit_length() - q.denominator.bit_length()
    power = Q(1 << exponent) if exponent >= 0 else Q(1, 1 << -exponent)
    return exponent if q <= power else exponent + 1


def rounded(z, fractional):
    unit = 1 << fractional
    return tuple(Q(int(v * unit), unit) for v in z)


def grid(z, fractional):
    return all((v * (1 << fractional)).denominator == 1 for v in z)


def fraction_bits(z):
    degrees = []
    for value in z:
        denominator = value.denominator
        need(denominator & (denominator - 1) == 0, "dyadic arithmetic value")
        degrees.append(denominator.bit_length() - 1)
    return max(degrees)


def exact_product(values):
    value = ONE
    for item in values:
        value = times(value, item)
    return value


def digits(index, n, g):
    result = []
    for _ in range(g):
        index, digit = divmod(index, n)
        result.append(digit)
    return result


def cached_diagonal(tables, fractional, b, omit_carry=False):
    """Axis 0 fastest; fresh stage/coarse-label cache, rounded suffix recurrence."""
    g, n = len(tables), len(tables[0])
    need(g >= 1 and n >= 2 and all(len(row) == n for row in tables), "uniform table shape")
    values = [[rounded(z, fractional) for z in row] for row in tables]
    suffix = [ONE] * (g + 1)
    address = [0] * g
    updates = 0
    max_temporary_bits = 0
    u = Q(2, 1 << fractional)

    def multiply(a, z):
        nonlocal max_temporary_bits
        product = times(a, z)
        max_temporary_bits = max(max_temporary_bits, fraction_bits(product))
        need(grid(product, 2 * fractional), "double-width coefficient product")
        return rounded(product, fractional)

    for j in range(g - 1, 0, -1):
        suffix[j] = multiply(values[j][0], suffix[j + 1])
        updates += 1
    output, reference = [], []
    for index in range(n ** g):
        need(address == digits(index, n, g), "axis-zero-fastest chronology")
        value = multiply(values[0][address[0]], suffix[1])
        exact = exact_product([tables[j][address[j]] for j in range(g)])
        # Independent fresh nested evaluation; never use the cache as its oracle.
        nested = ONE
        for j in range(g - 1, -1, -1):
            nested = rounded(times(values[j][address[j]], nested), fractional)
        need(value == nested, "cache freshness")
        need(norm(add(value, scale(exact, -1))) <= 2 * g * u * b ** (g - 1),
             "coefficient approximation bound")
        need(norm(value) <= 2 * b ** g, "cached coefficient magnitude")
        output.append(value)
        reference.append(exact)
        if index + 1 == n ** g:
            continue
        k = 0
        while address[k] + 1 == n:
            address[k] = 0
            k += 1
        address[k] += 1
        if not omit_carry:
            for j in range(k, 0, -1):
                suffix[j] = multiply(values[j][address[j]], suffix[j + 1])
                updates += 1
    # Includes g-1 initialization, carry recomputation and one output per record.
    need(updates + n ** g <= 4 * n ** g, "complete amortized multiplication count")
    return output, reference, updates + n ** g, max_temporary_bits


def raw_h(values, bit_positions):
    result = list(values)
    for position in bit_positions:
        jump = 1 << position
        for i in range(len(result)):
            if not i & jump:
                j = i | jump
                a, b = result[i], result[j]
                result[i], result[j] = add(a, b), add(a, scale(b, -1))
    return result


def supplier_model(values, positions, restore=True):
    """Exact D/C/D/H0 interface model; no mixed-provider recursion is executed."""
    result = list(values)
    phases = [exact_product([I for p in positions if i & (1 << p)])
              for i in range(len(result))]
    result = [times(z, phase) for z, phase in zip(result, phases)]
    for p in positions:
        jump = 1 << p
        for i in range(len(result)):
            if not i & jump:
                j = i | jump
                (result[i], result[j]), _ = c_pair(result[i], result[j])
    factor = exact_product([(Q(1, 2), Q(-1, 2))] * len(positions))
    result = [times(times(z, phase), factor) for z, phase in zip(result, phases)]
    return [scale(z, 1 << len(positions)) for z in result] if restore else result


def shape(programs):
    signature = []
    length = len(programs[0][0])
    g = len(programs[0])
    for block in programs:
        need(len(block) == g and all(len(axis) == length for axis in block),
             "common stage count across coarse labels")
        local = []
        for step in range(length):
            kinds = [axis[step][0] for axis in block]
            need(len(set(kinds)) == 1, "simultaneous stage kind")
            local.append((kinds[0], tuple(axis[step][1] for axis in block)
                          if kinds[0] == "H" else None))
        if signature:
            need(local == signature, "global H signature across coarse labels")
        signature = local
    return signature


def compile_cases(source):
    namespace = {"__file__": COMPILER, "__name__": "retained_tensor_compiler"}
    exec(compile(source, COMPILER, "exec", optimize=0), namespace)
    s = namespace["s"]
    # Keep two coarse labels with the same H shape and different matchings/tables.
    descriptions = [
        [([(0, 3), (2, 1)], [("upper", (Q(2, 7), Q(0))), ("swap", None)]),
         ([(3, 1), (0, 2)], [("fft", I), ("lower", (Q(-3, 5), Q(0)))])],
        [([(1, 3), (2, 0)], [("upper", ZERO), ("diag", (ONE, ONE))]),
         ([(0, 1), (3, 2)], [("fft", (Q(3, 5), Q(4, 5))),
                             ("lower", (Q(2, 9), Q(0)))])],
    ]

    def sym(z):
        return s.Rational(z[0].numerator, z[0].denominator) + s.I * s.Rational(
            z[1].numerator, z[1].denominator)

    def rational(z):
        real, imag = s.expand(z).as_real_imag()
        need(real.is_Rational and imag.is_Rational, "exact rational-complex compiler table")
        return Q(int(real.p), int(real.q)), Q(int(imag.p), int(imag.q))

    blocks = []
    for description in descriptions:
        axes = []
        for pairs, gates in description:
            words = []
            for kind, value in gates:
                argument = tuple(map(sym, value)) if kind == "diag" else (
                    None if value is None else sym(value))
                if kind in ("upper", "lower"):
                    need(norm(value) <= 10, "source gateword B hypothesis")
                words.append(namespace["gateword"](kind, argument, B=10))
            stages = namespace["local_layer"](4, pairs, words)
            axes.append([(kind, [rational(z) for z in value] if kind == "D" else value)
                         for kind, value in stages])
        blocks.append(axes)
    return blocks, descriptions


def gate_matrix(kind, value):
    if kind == "upper":
        return ((ONE, value), (ZERO, ONE))
    if kind == "lower":
        return ((ONE, ZERO), (value, ONE))
    if kind == "swap":
        return ((ZERO, ONE), (ONE, ZERO))
    if kind == "diag":
        return ((value[0], ZERO), (ZERO, value[1]))
    need(kind == "fft", "known independent gate")
    return ((ONE, value), (ONE, scale(value, -1)))


def independent_endpoint(values, description):
    result = list(values)
    for axis, (pairs, gates) in enumerate(description):
        stride = 4 ** axis
        for (left, right), (kind, value) in zip(pairs, gates):
            matrix = gate_matrix(kind, value)
            for i in range(len(result)):
                if i // stride % 4 == left:
                    j = i + (right - left) * stride
                    a, b = result[i], result[j]
                    result[i] = add(times(matrix[0][0], a), times(matrix[0][1], b))
                    result[j] = add(times(matrix[1][0], a), times(matrix[1][1], b))
    return result


def audit(source):
    blocks, descriptions = compile_cases(source)
    signature = shape(blocks)
    g, n, stages = 2, 4, len(signature)
    bound = max(Q(1), *(norm(z) for block in blocks for axis in block
                       for kind, row in axis if kind == "D" for z in row))
    # A rational upper bound suffices; use its integer ceiling for the bit invoice.
    B = -(-bound.numerator // bound.denominator)
    b, M0, target = B + 1, 2, 24
    R = 4 * b ** g
    K = ceiling_log2(R)
    height = ceiling_log2(M0) + stages * K
    fractional = target + 1 + ceiling_log2(stages * (2 * g + 1)) + height
    u = Q(2, 1 << fractional)
    final_bound = stages * (2 * g + 1) * u * M0 * R ** stages
    need(final_bound <= Q(1, 1 << target), "explicit output precision")
    need(fractional >= height, "nonnegative supplier base precision")
    inputs = [[ONE if i == j else ZERO for i in range(n ** g)] for j in range(n ** g)]
    inputs.append([(Q((i % 5) - 2, 8), Q((i % 3) - 1, 8)) for i in range(n ** g)])
    hashes, max_height, max_fractional, coefficient_products = [], 0, 0, 0
    max_entrance_height = 0
    errors = []
    for block, description in zip(blocks, descriptions):
        diagonal = {}
        for step, (kind, _) in enumerate(signature):
            if kind == "D":
                rounded_values, exact_values, count, temporary = cached_diagonal(
                    [axis[step][1] for axis in block], fractional, b)
                diagonal[step] = rounded_values, exact_values
                coefficient_products += count
                max_fractional = max(max_fractional, temporary)
        for initial in inputs:
            computed, exact = list(initial), list(initial)
            for step, (kind, _) in enumerate(signature):
                if kind == "D":
                    approx, true = diagonal[step]
                    exact = [times(z, d) for z, d in zip(exact, true)]
                    products = [times(z, d) for z, d in zip(computed, approx)]
                    max_fractional = max(max_fractional, *(fraction_bits(z) for z in products))
                    need(all(grid(z, 2 * fractional) for z in products), "double-width data product")
                    need(all(norm(z) <= M0 * R ** (step + 1) for z in products),
                         "unrounded data-product headroom")
                    computed = [rounded(z, fractional) for z in products]
                else:
                    positions = [2 * a + block[a][step][1] for a in range(g)]
                    exact = raw_h(exact, positions)
                    need(all(grid(z, fractional) for z in computed), "actual raw-H input grid")
                    entrance = max(norm(z) for z in computed)
                    max_entrance_height = max(max_entrance_height,
                                             0 if entrance == 0 else ceiling_log2(entrance))
                    computed = supplier_model(computed, positions)
                need(all(grid(z, fractional) for z in computed), "completed stage base grid")
                current = max(norm(z) for z in computed)
                max_height = max(max_height, 0 if current == 0 else ceiling_log2(current))
                need(current <= M0 * R ** (step + 1), "rounded trajectory bound")
            need(exact == independent_endpoint(initial, description), "independent original-gate endpoint")
            error = max(norm(add(a, scale(b0, -1))) for a, b0 in zip(computed, exact))
            need(error <= final_bound, "complete rounded caller error")
            errors.append(error)
            hashes.append(digest(canonical([[str(a), str(b0)] for a, b0 in computed])))
    need(max(errors) > 0, "nonzero rounding error witness")
    need(max_entrance_height > 0, "nonzero actual incoming height")
    need(fractional < max_fractional <= 2 * fractional, "nontrivial transient denominator")
    # Fresh cache controls include zero factors and deeper carries.
    cache_cases = 0
    for radix, axes in ((2, 1), (2, 4), (3, 3), (4, 2)):
        tables = [[(Q((j + 2 * a) % 5 - 2, 3), Q((j + a) % 3 - 1, 5))
                   for j in range(radix)] for a in range(axes)]
        cached_diagonal(tables, 11, 3)
        cache_cases += 1
    changed = [[list(axis) for axis in block] for block in blocks]
    at = next(i for i, stage in enumerate(changed[1][0]) if stage[0] == "H")
    changed[1][0][at] = ("H", 1 - changed[1][0][at][1])
    reject(lambda: shape(changed), "coarse-label H mismatch")
    tables = [[(Q(1, 3), Q(0)), ONE], [ZERO, (Q(2, 3), Q(0))]]
    reject(lambda: cached_diagonal(tables, 11, 3, omit_carry=True), "stale cache after zero")
    probe = [ONE] + [ZERO] * 15
    need(supplier_model(probe, [0, 2], restore=False) != raw_h(probe, [0, 2]),
         "omitted H0 restoration control")
    # A scalar product of F-grid values need not itself belong to that grid.
    q = rounded((Q(1, 3), Q(0)), fractional)
    need(not grid(times(q, q), fractional), "omitted product rounding control")
    return {
        "status": "PASS_ROUNDED_GAUSSIAN_CALLER",
        "coarse_labels": len(blocks), "axes": g, "side": n, "coordinates_per_label": n ** g,
        "stages": stages, "raw_H_calls": sum(kind == "H" for kind, _ in signature),
        "diagonal_stages": sum(kind == "D" for kind, _ in signature),
        "trajectories": len(blocks) * len(inputs), "coefficient_l1_bound": B,
        "R": R, "K": K, "M0": M0, "output_target_bits": target,
        "fractional_bits": fractional, "incoming_height_reserve": height,
        "supplier_base_precision": fractional - height,
        "observed_height": max_height, "maximum_product_fractional_bits": max_fractional,
        "observed_raw_H_entrance_height": max_entrance_height,
        "coefficient_products_for_both_labels": coefficient_products,
        "fresh_cache_controls": cache_cases, "maximum_error": str(max(errors)),
        "proved_error_bound": str(final_bound), "output_sha256": hashes,
        "controls": ["coarse-label H mismatch", "stale cache after zero",
                     "omitted H0 restoration", "omitted product rounding"],
        "scope": "Exact rational replay of actual emitted compiler tables with rounded caches/data and a C/H0 interface model; no physical mixed-provider or full Gaussian execution.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    result = audit(authenticate()[COMPILER])
    if args.emit:
        with args.emit.open("x") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        need(json.loads((HERE / "CALLER-RESULT.json").read_text()) == result,
             "complete caller receipt")
    print(json.dumps({"status": result["status"], "trajectories": result["trajectories"],
                      "fractional_bits": result["fractional_bits"],
                      "receipt_sha256": digest(canonical(result)),
                      "scope": result["scope"]}, sort_keys=True))


if __name__ == "__main__":
    main()
