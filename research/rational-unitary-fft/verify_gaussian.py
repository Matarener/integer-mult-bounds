"""Check the retained normalized Gaussian coefficient-to-circuit boundary.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from exact import (C, Mat, Vec, apply, ceil_log2, component_l1, eye, multiply,
                   need, norm2, upper, vector_hash)
from full import admission
from gaussian import EVALUATOR, Gaussian, GaussianMatrix
from verify import authenticate, canonical, mv, operator, plan_hash, rejected
from verify_triangle import eliminate, frobenius_error, structure


def finer_reference(producer):
    """Dense scalar reference; shares the declared interval backend, not Tsec."""
    spec = producer.spec
    precision = producer.error_bits + 16 + ceil_log2(2 * spec.n)
    bits = 2 * precision + 32
    table, errors = {}, []
    for u in range(1 - spec.n, spec.n):
        factor = spec.c * ((Q(u) - spec.shift) ** 2 - spec.shift ** 2)
        box = producer.exponential(factor, bits)
        value = Q(box.lo, box.scale)
        table[u] = value
        errors.append(Q(box.hi - box.lo, box.scale))
    epsilon = sum(errors, Q(0))
    need(epsilon * producer.qbar <= Q(1, 2), "fine reference inverse admission")
    matrix = Mat([[table[j - i] for j in range(spec.n)] for i in range(spec.n)])
    return matrix, epsilon, bits


def one_case(label, raw, n, c, shift, target=20, incoming=3, window=None):
    vectors = [Vec(C(Q((3 * i + 1) % 7 - 3, 8), Q((5 * i + 2) % 9 - 4, 8))
                   for i in range(n)),
               Vec(C((-1) ** i * 32, i % 2) for i in range(n))]
    if incoming > 3:
        vectors.append(Vec([C(Q(1, 1 << incoming))] + [C()] * (n - 1)))
    radius = max(Q(1), *(component_l1(v) for v in vectors))
    producer = Gaussian(raw, n, c, shift, radius, target, incoming, window)
    plan = producer.compile()
    inverse = producer.builder.inverse(plan)
    bound = producer.builder.bound
    lam, q, leading = admission(producer.root)
    need(lam <= n and q <= 2 * producer.qbar, "separate exact leading-section admission")
    need(all(producer.root[i][i] == 1 for i in range(n)), "exact normalized diagonal")
    fine, fine_error, fine_bits = finer_reference(producer)
    fine_inverse = eliminate(fine)
    actual, actual_inverse = operator(plan, n), operator(inverse, n)
    rational_inverse = eliminate(producer.root)
    need(multiply(actual, actual_inverse) == eye(n), "Gaussian stored inverse identity")
    forward = frobenius_error(actual, producer.root)
    backward = frobenius_error(actual_inverse, rational_inverse)
    need(max(forward, backward) <= n * bound["coefficient_error"] ** 2,
         "Gaussian full circuit rational reference endpoints")
    height = max(structure(plan, bound), structure(inverse, bound))
    states = []
    for direction, program, stored, root, reference, allowance, reference_error in (
            ("forward", plan, actual, producer.root, fine, producer.forward_error, fine_error),
            ("inverse", inverse, actual_inverse, rational_inverse, fine_inverse,
             producer.inverse_error, 2 * producer.qbar ** 2 * fine_error)):
        for vector in vectors:
            need(norm2(vector) <= radius ** 2, "Gaussian input radius")
            need(all((part * (1 << incoming)).denominator == 1
                     for z in vector for part in (z.re, z.im)), "declared Gaussian incoming grid")
            output, stats = apply(program, vector, bound["data_bits"])
            root_error = norm2(output - mv(root, vector))
            rounding_error = norm2(output - mv(stored, vector))
            need(root_error <= bound["total_error"] ** 2
                 and rounding_error <= bound["rounding_error"] ** 2, "Gaussian rational circuit errors")
            # The component-l1 distance bounds the vector 2-norm.
            ideal_error = component_l1(output - mv(reference, vector)) + reference_error * radius
            need(ideal_error <= allowance and allowance < Q(1, 1 << target),
                 "complete rounded error against ideal Gaussian kernel")
            need(stats["max_observed_height"] <= bound["temporary_bits"]
                 and stats["max_grid_numerator_bits"] + 1 <= bound["data_bits"] + bound["integer_bits"]
                 and stats["max_reduced_fractional_bits"] <= bound["data_bits"],
                 "Gaussian online width and temporary allowances")
            states.append(dict(direction=direction, input_sha256=vector_hash(vector),
                               output_sha256=vector_hash(output), statistics=stats,
                               root_error_squared_upper=str(upper(root_error)),
                               rounding_error_squared_upper=str(upper(rounding_error)),
                               ideal_error_upper=str(upper(ideal_error))))
    record = producer.record()
    record.update(label=label, layers=len(plan), gates=sum(map(len, plan)),
                  plan_sha256=plan_hash(plan), inverse_sha256=plan_hash(inverse),
                  full_source_ast_sha256=producer.builder.source_ast,
                  exact_leading_bounds=[dict(n=b, bound=str(value)) for b, value in leading],
                  fine_reference_bits=fine_bits, fine_reference_error=str(fine_error),
                  fine_reference_sha256=vector_hash([z for row in fine for z in row]),
                  budget={key: str(value) if isinstance(value, Q) else value
                          for key, value in bound.items()},
                  coefficient_height=height, states=states)
    return record


def controls(raw):
    results = []
    for label, kwargs in (
            ("floating-gaussian-scale", dict(c=0.5)),
            ("nonpositive-gaussian-scale", dict(c=0)),
            ("outside-closed-half-shift", dict(shift=Q(5001, 10000))),
            ("nondyadic-gaussian-size", dict(n=3)),
            ("unpaid-truncation", dict(window=0)),
            ("fractional-target-bits", dict(target=Q(3, 2))),
            ("negative-incoming-grid", dict(incoming=-1))):
        values = dict(n=2, c=Q(1, 2), shift=Q(1, 3), radius=1, target=16, incoming=0)
        values.update(kwargs)
        results.append(rejected(lambda: Gaussian(raw, **values), label))
    for label, before, after in (
            ("reversed-gaussian-offset", b"np.arange(n)[None,:]-np.arange(n)[:,None]",
             b"np.arange(n)[:,None]-np.arange(n)[None,:]"),
            ("omitted-normalization", b"-g*(u-s)**2+g*s*s", b"-g*(u-s)**2")):
        changed = dict(raw)
        need(raw[EVALUATOR].count(before) == 1, "unique Gaussian source mutation")
        changed[EVALUATOR] = raw[EVALUATOR].replace(before, after)
        results.append(rejected(lambda: Gaussian(changed, 2, 1, Q(1, 3), 1, 16).compile(), label))
    producer = Gaussian(raw, 2, 1, Q(1, 3), 1, 16)
    original = producer.namespace["Tsec"]
    def changed_root(*args):
        matrix = original(*args)
        matrix[0][0] = C(2)
        return matrix
    producer.namespace["Tsec"] = changed_root
    results.append(rejected(producer.compile, "altered-root-with-old-coefficient-certificate"))
    producer = Gaussian(raw, 2, 1, Q(1, 3), 1, 16)
    producer.namespace["g"] = Q(1)
    results.append(rejected(producer.compile, "omitted-symbolic-pi"))
    producer = Gaussian(raw, 2, 1, Q(1, 3), 1, 16)
    producer.coefficient_bits = 1
    results.append(rejected(producer.compile, "underfunded-coefficient-grid"))
    producer = Gaussian(raw, 1, 1, 0, 1, 16)
    plan = producer.compile()
    results.append(rejected(producer.compile, "reused-stateful-caller"))
    results.append(rejected(lambda: apply(plan, Vec([Q(1, 1 << 512)]), 20),
                            "discarded-gaussian-incoming-grid"))
    results.append(rejected(lambda: GaussianMatrix([[1]]).astype(float), "floating-cast-tag"))
    need(canonical({"window": 1}) != canonical({"window": True}), "typed Gaussian receipt")
    return results + ["typed-gaussian-receipt"]


def run():
    raw, sources = authenticate(include_generator=True, include_full=True, include_gaussian=True)
    fixtures = [
        ("normalized-scalar", 1, Q(1, 3), Q(1, 2), 20, 3, None),
        ("broad-half-shift", 2, Q(1, 8), Q(1, 2), 20, 3, None),
        ("positive-half-shift", 4, Q(1, 2), Q(1, 2), 20, 3, None),
        ("negative-half-shift", 4, Q(1, 2), Q(-1, 2), 20, 3, None),
        ("fine-incoming", 4, Q(2), Q(-3, 8), 20, 512, None),
        ("truncated-narrow", 8, Q(2), Q(1, 3), 20, 3, None),
        ("near-half-shift", 8, Q(1, 2), Q(499, 1000), 20, 3, None),
        ("low-requested-precision", 2, Q(1), Q(1, 3), 8, 3, 1),
        ("high-requested-precision", 2, Q(1), Q(1, 3), 36, 3, 1),
    ]
    records = []
    for label, *args in fixtures:
        records.append(one_case(label, raw, *args))
        print("CHECK_GAUSSIAN_CASE", label, flush=True)
    need(any(row["window"] < row["n"] - 1 and Q(row["tail_bound"]) > 0 for row in records),
         "nonzero paid truncation witness")
    need(any(Q(row["kernel_error"]) > 0 for row in records), "nonzero coefficient approximation")
    need(records[-1]["coefficient_bits"] > records[-2]["coefficient_bits"],
         "requested precision changes preparation")
    probe = Gaussian(raw, 1, 1, 0, 1, 16)
    enclosures = []
    for bits in (16, 38, 70):
        for factor in (Q(0), Q(1, 10 ** 8), Q(1, 4), Q(3), Q(10 ** 6)):
            box = probe.exponential(factor, bits)
            need(0 <= box.lo <= box.hi <= box.scale, "exponential range")
            if factor == 0:
                need(box.lo == box.hi == box.scale, "exact-one exponential")
            enclosures.append(dict(bits=bits, factor=str(factor), lo=box.lo, hi=box.hi))
    return dict(schema_version=1, scope="retained normalized Gaussian coefficients and full logical circuit",
                sources=sources, cases=records, enclosures=enclosures, controls=controls(raw),
                normalized_gaussian_gate_execution=True, complete_gaussian_execution=False,
                raw_gauges=False, physical_tape_execution=False, universal_proof_kernel=False,
                independent_transcendental_backend=False)


def verify_result(write=False):
    result = run()
    path = HERE / "GAUSSIAN-RESULT.json"
    if write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed Gaussian receipt")
    print(json.dumps(dict(status="PASS_NORMALIZED_GAUSSIAN_CIRCUIT", cases=len(result["cases"]),
                          gates=sum(row["gates"] for row in result["cases"]),
                          rounded_states=sum(len(row["states"]) for row in result["cases"]),
                          controls=len(result["controls"]),
                          result_sha256=sha256(canonical(result)).hexdigest()), sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    verify_result(parser.parse_args().write_result)


if __name__ == "__main__":
    main()
