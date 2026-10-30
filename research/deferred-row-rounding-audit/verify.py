#!/usr/bin/env python3
"""Exact projected-defect audit. No repository mathematics engine imported.

CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import json

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
SUPPORT = ("research/kappa-observation-integration/release-work/current/package/"
           "vendor/pr1673/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md")
CLOSURE = "research/kappa-rebuild/transfer-audit/FINITE-TEMPLATE-CLOSURE.md"
OUTER = "research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_check(root=ROOT):
    pins = read_json(PKG / "SOURCES.json")
    hashes = {}
    for item in pins["files"]:
        if item["usage"] == "input":
            data = (root / item["path"]).read_bytes()
            hashes[item["path"]] = sha256(data).hexdigest()
            need(hashes[item["path"]] == item["sha256"], "source bytes: " + item["path"])
    selected = read_json(root / "certificates/selected-result.json")
    inventory = read_json(root / selected["source_manifest"])["files"]
    for path in (SUPPORT, CLOSURE, OUTER):
        need(hashes[path] == inventory[path], "selected source closure: " + path)
    need(hashes[selected["certificate"]] == selected["certificate_sha256"], "selected claim")
    support = (root / SUPPORT).read_text(encoding="utf-8")
    for fragment in ("Each padded zero row is therefore zero at completion and can be deleted",
                     "H0=(1/2)[[1,1],[1,-1]]", "by the scalar 2^g"):
        need(fragment in support, "source statement: " + fragment)
    closure = (root / CLOSURE).read_text(encoding="utf-8")
    need("A child is never rounded," in closure, "actual fixed-grid boundary")
    return selected["kappa"]


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    need(len(a[0]) == len(b), "matrix dimensions")
    out = [[F(0) for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                for j, right in enumerate(b[k]):
                    if right:
                        out[i][j] += value * right
    return out


def apply(a, x):
    return [sum((v*x[j] for j, v in enumerate(row) if v), F(0)) for row in a]


def norm(a):
    return max(sum(abs(v) for v in row) for row in a)


def hadamard(n, bit):
    step = 1 << bit
    a = [[F(0) for _ in range(n)] for _ in range(n)]
    for start in range(0, n, 2*step):
        for offset in range(step):
            i, j = start+offset, start+offset+step
            a[i][i] = a[i][j] = a[j][i] = F(1, 2)
            a[j][j] = F(-1, 2)
    return a


def program(m=F(1, 2), a=F(4)):
    # Expose original bit 1 as the active low bit; bit 2 remains the row label.
    q = [[F(0) for _ in range(8)] for _ in range(8)]
    for old in range(8):
        new = (old & 4) | ((old & 1) << 1) | ((old & 2) >> 1)
        q[new][old] = F(1)
    embed = [[F(i == j) for j in range(8)] for i in range(12)]
    project_rows = [[F(i == j) for j in range(12)] for i in range(8)]
    lower, upper = identity(12), identity(12)
    lower_inverse, upper_inverse = identity(12), identity(12)
    for i in range(4):
        lower[i+8][i] = m
        upper[i][i+8] = a
        lower_inverse[i+8][i] = -m
        upper_inverse[i][i+8] = -a
    return [("expose", q, False), ("pad", embed, False),
            ("lower", lower, True), ("upper", upper, True),
            ("upper_inverse", upper_inverse, True),
            ("lower_inverse", lower_inverse, True),
            ("active_H0", hadamard(12, 0), True),
            ("unpad", project_rows, False), ("restore", q, False),
            ("tail_H0", hadamard(8, 2), True)]


def endpoint(ops):
    result = identity(8)
    for _, matrix, _ in ops:
        result = multiply(matrix, result)
    return result


def padded_phase_endpoint(ops):
    result, active = identity(12), False
    for name, matrix, _ in ops:
        if name == "pad":
            active = True
            continue
        if name == "unpad":
            break
        if active:
            result = multiply(matrix, result)
    return result


def walsh_endpoint():
    mask = 6  # original selected bits 1 and 2; bit 0 is a spectator
    return [[F(0) if (i ^ j) & ~mask else F((-1)**((i & j & mask).bit_count()), 4)
             for j in range(8)] for i in range(8)]


def closed_phase_endpoint():
    # Direct coefficient formula, independent of the gate-matrix constructor.
    return [[F((-1)**((i & 1)*(j & 1)), 2) if i//2 == j//2 else F(0)
             for j in range(12)] for i in range(12)]


def suffixes(ops):
    after = identity(8)
    result = {}
    for name, matrix, noisy in reversed(ops):
        if noisy:
            result[name] = after
        after = multiply(after, matrix)
    return result


def defect_bound(suffix, unit):
    rows = [sum(unit * sum(abs(v) for v in matrix[i]) for matrix in suffix.values())
            for i in range(8)]
    best = max(range(8), key=rows.__getitem__)
    return rows[best], best


def forward(ops, x, defects=None, rounding=False):
    values = list(map(F, x))
    for name, matrix, noisy in ops:
        values = apply(matrix, values)
        if noisy and rounding:
            values = [F(round(v*4), 4) for v in values]
        if defects and name in defects:
            values = [x+y for x, y in zip(values, defects[name])]
    return values


def sharpness(ops, suffix, unit):
    bound, row = defect_bound(suffix, unit)
    defects = {name: [unit * ((v > 0) - (v < 0)) for v in matrix[row]]
               for name, matrix in suffix.items()}
    output = forward(ops, [0]*8, defects)
    need(output[row] == bound and max(map(abs, output)) == bound, "attaining defects")
    raw_error = 4 * max(map(abs, output))
    need(raw_error == 4*bound and raw_error > bound, "raw recovery needs factor four")
    return bound


def discard_boundary_checks(ops, suffix):
    late = [F(0)]*8 + [F(66)]*4
    output = forward(ops, [0]*8, {"active_H0": late})
    need(output == [0]*8, "completed padded residual projects away")
    need(all(not v for row in suffix["active_H0"] for v in row[8:]),
         "terminal padded columns vanish")
    early = [F(0)]*8 + [F(1, 8)]*4
    output = forward(ops, [0]*8, {"upper": early})
    need(any(output), "internal padded defects reach retained output")
    missing_cleanup = [(name, identity(12) if name == "lower_inverse" else matrix, noisy)
                       for name, matrix, noisy in ops]
    need(endpoint(missing_cleanup) == walsh_endpoint(), "retained correctness can hide missing cleanup")
    need(padded_phase_endpoint(missing_cleanup) != closed_phase_endpoint(),
         "missing cleanup violates full phase contract")
    return {"terminal_padded_columns": 4,
            "discarded_terminal_residual_size": "66",
            "early_padded_defect_output_error": str(max(map(abs, output))),
            "missing_cleanup_retained_endpoint_correct": True,
            "missing_cleanup_full_phase_correct": False}


def round_half_even(n):
    """Nearest integer to n/2, ties to even; independent integer implementation."""
    q, r = divmod(n, 2)
    return q + (q % 2 if r else 0)


def literal_quantized(units):
    # Input/output units are 1/4. This engine uses no dense matrix routines.
    v = [units[(i & 4) | ((i & 1) << 1) | ((i & 2) >> 1)] for i in range(8)] + [0]*4
    for i in range(4):
        v[i+8] = round_half_even(2*v[i+8] + v[i])
    for i in range(4):
        v[i] += 4*v[i+8]
    for i in range(4):
        v[i] -= 4*v[i+8]
    for i in range(4):
        v[i+8] = round_half_even(2*v[i+8] - v[i])
    for i in range(0, 12, 2):
        x, y = v[i], v[i+1]
        v[i], v[i+1] = round_half_even(x+y), round_half_even(x-y)
    v = v[:8]
    v = [v[(i & 4) | ((i & 1) << 1) | ((i & 2) >> 1)] for i in range(8)]
    for i in range(4):
        x, y = v[i], v[i+4]
        v[i], v[i+4] = round_half_even(x+y), round_half_even(x-y)
    return v


def exhaustive_quantizer(ops, bound):
    maximum, count, dense_checks = F(0), 0, 0
    target = walsh_endpoint()
    for count, units in enumerate(product((-1, 0, 1), repeat=8), start=1):
        computed_units = literal_quantized(units)
        exact = apply(target, [F(x, 4) for x in units])
        error = max(abs(F(x, 4)-y) for x, y in zip(computed_units, exact))
        maximum = max(maximum, error)
        need(error <= bound, "quantizer defect bound")
        # Seed 66 selects one of 81 disjoint, evenly spaced cross-check slices.
        if (count-1) % 81 == 66:
            dense = forward(ops, [F(x, 4) for x in units], rounding=True)
            need(dense == [F(x, 4) for x in computed_units], "independent nonlinear execution")
            dense_checks += 1
    return {"inputs": count, "dense_cross_checks": dense_checks,
            "maximum_observed_normalized_error": str(maximum),
            "maximum_observed_raw_error": str(4*maximum)}


def echo(x, z, m, a, epsilon=F(0)):
    z += m*x
    x += a*z
    z += epsilon
    x -= a*z
    z -= m*x
    return x, z


def echo_checks():
    cases = 0
    for k in range(13):
        m = F(2**k)
        for a in (F(1, 2), F(1), F(4), F(66)):
            for x, z in product((F(-2), F(-1, 2), F(0), F(1, 2), F(2)), repeat=2):
                need(echo(x, z, m, a) == (x, z), "arbitrary-input exact echo")
                epsilon = F(1, 8)
                need(echo(x, z, m, a, epsilon) == (x-a*epsilon, z+(1+m*a)*epsilon),
                     "sharp retained/padded channel")
                cases += 1
    m, a, x, z = F(1, 2), F(4), F(1), F(0)
    before_round = z + m*x
    epsilon = F(round(before_round)) - before_round
    observed = echo(x, z, m, a, epsilon)
    need(observed == (F(3), F(-3, 2)), "literal rounding counterexample")
    need(abs(observed[0]-x) == 4*abs(epsilon), "endpoint-only bound falsified")
    return {"exact_channel_fixtures": cases, "literal_rounding_error": str(epsilon),
            "literal_retained_error": str(observed[0]-x),
            "discarded_to_retained_ratio_at_M4096_a1": 4097}


def main():
    selected = source_check()
    ops = program()
    need(padded_phase_endpoint(ops) == closed_phase_endpoint(), "full padded phase endpoint")
    need(endpoint(ops) == walsh_endpoint(), "full deferred endpoint")
    need(norm(walsh_endpoint()) == 1, "normalized endpoint is contractive")
    suffix = suffixes(ops)
    bound = sharpness(ops, suffix, F(1, 8))
    summary = {
        "selected_kappa_unchanged": selected,
        "retained_matrix_coefficients": 64,
        "full_phase_matrix_coefficients": 144,
        "noise_sites": len(suffix),
        "sharp_defect_box_bound_normalized": str(bound),
        "sharp_defect_box_bound_raw": str(4*bound),
        "discard_boundary": discard_boundary_checks(ops, suffix),
        "quantized_inputs": exhaustive_quantizer(ops, bound),
        "echo": echo_checks(),
        "scope": "Conditional numerical interface audit; exact selected fixed-grid algorithm unchanged; no new kappa.",
    }
    expected = PKG / "EXPECTED.json"
    need(summary == read_json(expected), "expected certificate")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("PASS_DEFERRED_ROW_ROUNDING_AUDIT")


if __name__ == "__main__":
    main()
