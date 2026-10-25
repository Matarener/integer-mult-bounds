"""Certify finite consequences of the shifted Gaussian conditioning theorem.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. The universal argument is in PROOF.md.
"""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("shifted_intervals", HERE / "intervals.py")
arithmetic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arithmetic)
I, D, DOWN, UP, need = (getattr(arithmetic, name) for name in ("I", "D", "DOWN", "UP", "need"))
WIDTH, BITS = 64, 192


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sign(u):
    return 1 if u % 2 == 0 else -1


def check_source(raw, row):
    need(sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + row["path"])


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    for row in rows:
        raw = (ROOT / row["path"]).read_bytes()
        check_source(raw, row)
        rejected(lambda: check_source(raw + b"\x00", row), "changed source rejects its pin")
    return [{"path": row["path"], "sha256": row["sha256"]} for row in rows]


def validate(gamma, shift):
    need(type(gamma) is Q and type(shift) is Q, "rational parameters")
    need(gamma > 0 and abs(shift) < Q(1, 2), "strict shifted Gaussian domain")


def coefficient(gamma, shift, u):
    return I(gamma * (-u * u + 2 * shift * u)).exp()


def tails(gamma, shift, width):
    need(width >= 0 and abs(shift) < Q(1, 2), "Gaussian tail domain")
    return sum((coefficient(gamma, sign * shift, width + 1) /
                (1 - I(-gamma * (2 * width + 3 - 2 * sign * shift)).exp())
                for sign in (-1, 1)), I(0))


def minimum(gamma, shift, coefficients):
    direct = sum((sign(u) * coefficients[u] for u in range(-WIDTH, WIDTH + 1)), I(0))
    direct = direct.widen(tails(gamma, shift, WIDTH))
    # Jacobi's product, with the omitted positive deficits bounded geometrically.
    count = max(4, (40 * gamma.denominator + gamma.numerator - 1) // gamma.numerator)
    step = I(-2 * gamma).exp()
    c, a, b = step, I(-gamma * (1 - 2 * shift)).exp(), I(-gamma * (1 + 2 * shift)).exp()
    product = I(1)
    for _ in range(count):
        product = product * (1 - c) * (1 - a) * (1 - b)
        c, a, b = c * step, a * step, b * step
    deficit = (c + a + b) / (1 - step)
    need(0 <= deficit.lo <= deficit.hi < 1, "positive product tail")
    product = I(DOWN.multiply(product.lo, DOWN.subtract(D(1), deficit.hi)), product.hi)
    result = direct.intersect(product)
    need(result.lo > 0, "positive minimum enclosure")
    return result, {"direct": direct.record(), "product": product.record(),
                    "product_terms": count, "tail": tails(gamma, shift, WIDTH).record()}


def circle_checks(coefficients, minimum_bound, tail):
    points = [(Q(1), Q(0)), (Q(4, 5), Q(3, 5)), (Q(0), Q(1)),
              (Q(-4, 5), Q(3, 5)), (Q(-1), Q(0)), (Q(0), Q(-1))]
    for x, y in points:
        real, imag = I(1), I(0)
        total = coefficients[0]
        for u in range(1, WIDTH + 1):
            real, imag = real * x - imag * y, real * y + imag * x
            total = total + (coefficients[u] + coefficients[-u]) * real
        total = total.widen(tail)
        if x == -1:
            total.intersect(minimum_bound)
        else:
            need(total.lo > minimum_bound.hi, "sampled real part exceeds minimum")
    return len(points)


def rounded_kernel(coefficients, tail):
    rounded, error = {}, tail
    scale = 1 << BITS
    for u, value in coefficients.items():
        lower = Q(value.lo)
        rounded[u] = Q((lower * scale).__floor__(), scale)
        error = error + (value - I(rounded[u]))
    need(error.lo >= 0 and rounded[0] == 1, "rounded normalized coefficients")
    return rounded, error


def ldl(matrix):
    size = len(matrix)
    lower = [[Q(0) for _ in range(size)] for _ in range(size)]
    pivots = []
    for i in range(size):
        pivot = matrix[i][i] - sum((lower[i][k] ** 2 * pivots[k] for k in range(i)), Q(0))
        need(pivot > 0, "strict positive rational LDL pivot")
        pivots.append(pivot)
        lower[i][i] = 1
        for j in range(i + 1, size):
            lower[j][i] = (matrix[j][i] -
                          sum((lower[j][k] * lower[i][k] * pivots[k]
                               for k in range(i)), Q(0))) / pivot
    # Verify the full factorization, rather than treating pivot signs alone as a receipt.
    for i in range(size):
        for j in range(size):
            need(sum((lower[i][k] * pivots[k] * lower[j][k]
                      for k in range(min(i, j) + 1)), Q(0)) == matrix[i][j],
                 "exact rational LDL reconstruction")
    return pivots


def fraction_hash(values):
    digest = sha256()
    for value in values:
        for integer in (value.numerator, value.denominator):
            raw = abs(integer).to_bytes(max(1, (abs(integer).bit_length() + 7) // 8), "big")
            digest.update(bytes([integer < 0]))
            digest.update(len(raw).to_bytes(8, "big"))
            digest.update(raw)
    return digest.hexdigest()


def sections(coefficients, rounded, m, finite_constant):
    result = []
    for size in (1, 2, 4, 8, 16):
        margin = Q(m.lo) / 2
        gram = [[(rounded[j - i] + rounded[i - j]) / 2 -
                 (margin if i == j else 0) for j in range(size)] for i in range(size)]
        pivots = ldl(gram)
        norm_squared = I(0)
        for i in range(size):
            row = sum(((-1) ** j * coefficients[j - i] for j in range(size)), I(0))
            norm_squared = norm_squared + row.square() / size
        need(norm_squared.lo > 0, "positive alternating-vector image")
        inverse_lower = (1 / norm_squared.sqrt()).lo
        inverse_upper = (1 / m).hi
        need(inverse_lower <= inverse_upper, "finite inverse bounds consistent")
        result.append({"size": size, "ldl_pivot_sha256": fraction_hash(pivots),
                       "smallest_pivot": I(min(pivots)).record(),
                       "ideal_inverse_norm_lower": str(inverse_lower),
                       "ideal_uniform_inverse_norm_upper": str(inverse_upper),
                       "ideal_gap_free_inverse_norm_upper": str((size * finite_constant).hi)})
    return result


def size_descriptor(gamma, m):
    # This certifies a lemma's size threshold; no matrix of this size is executed.
    a0, relative = 2 * (1 + gamma) ** 2 / gamma ** 2, Q(1, 8)
    threshold = (a0 / (relative * Q(m.lo))) ** 2
    power = max(0, threshold.numerator.bit_length() - threshold.denominator.bit_length())
    if (1 << power) < threshold:
        power += 1
    need(a0 ** 2 <= relative ** 2 * Q(m.lo) ** 2 * (1 << power),
         "dyadic near-sharp size threshold")
    if power:
        need((1 << (power - 1)) < threshold, "smallest certified dyadic threshold")
    return {"log2_size": power, "relative_error": "1/8",
            "inverse_fraction_of_limit_at_least": "8/9", "executed": False}


def rejected(operation, label):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("control unexpectedly passed: " + label)


def multiply(left, right):
    return [[sum((left[i][k] * right[k][j] for k in range(len(right))), Q(0))
             for j in range(len(right[0]))] for i in range(len(left))]


def finite_shift_validate(shift):
    need(abs(shift) <= Q(1, 2), "closed half-shift domain")


def exact_power(base, exponent):
    exponent = Q(exponent)
    need(exponent.denominator == 1, "integer power in rational Gaussian fixture")
    return base ** exponent.numerator


def finite_cap_certificates():
    records = []
    wrong_shift_rejections = 0
    for root_q in (Q(1, 2), Q(3, 4), Q(15, 16)):
        q = root_q ** 2
        for size in (1, 2, 4, 8):
            product = [Q(1)]
            for j in range(1, size):
                product.append(product[-1] * (1 - q ** (2 * j)))
            choose = [[product[i] / (product[j] * product[i - j]) if j <= i else Q(0)
                       for j in range(size)] for i in range(size)]
            lower = [[q ** ((i - j) ** 2) * choose[i][j] if j <= i else Q(0)
                      for j in range(size)] for i in range(size)]
            lower_inverse = [[(-q) ** (i - j) * choose[i][j] if j <= i else Q(0)
                              for j in range(size)] for i in range(size)]
            identity = [[Q(i == j) for j in range(size)] for i in range(size)]
            centered = [[q ** ((i - j) ** 2) for j in range(size)] for i in range(size)]
            diagonal_times_transpose = [[product[i] * lower[j][i] for j in range(size)]
                                        for i in range(size)]
            need(multiply(lower, diagonal_times_transpose) == centered, "retained q-LDU identity")
            need(multiply(lower_inverse, lower) == identity, "finite q-binomial triangular inverse")
            centered_inverse = [[sum((lower_inverse[k][i] * lower_inverse[k][j] / product[k]
                                      for k in range(max(i, j), size)), Q(0))
                                 for j in range(size)] for i in range(size)]
            # The finite product is larger than P_infinity, so this is a stronger
            # finite-fixture bound than the universal P_infinity expression.
            constant = 1 / product[-1] ** 3
            for shift in (Q(-1, 2), Q(-1, 4), Q(0), Q(1, 4), Q(1, 2)):
                finite_shift_validate(shift)
                matrix = [[exact_power(root_q, 2 * ((j - i) ** 2 - 2 * shift * (j - i)))
                           for j in range(size)] for i in range(size)]
                inverse = [[centered_inverse[i][j] * exact_power(root_q, 4 * shift * (i - j))
                            for j in range(size)] for i in range(size)]
                need(multiply(matrix, inverse) == identity and multiply(inverse, matrix) == identity,
                     "exact shifted Gaussian left and right inverse")
                for i in range(size):
                    for j in range(size):
                        decay = exact_power(root_q, 2 * abs(i - j) + 4 * shift * (i - j))
                        need(abs(inverse[i][j]) <= constant * decay <= constant,
                             "gap-free inverse entry bound")
                row_norm = max(sum(abs(x) for x in row) for row in inverse)
                column_norm = max(sum(abs(inverse[i][j]) for i in range(size)) for j in range(size))
                need(max(row_norm, column_norm) <= size * constant, "finite Euclidean norm majorant")
                if shift and size > 1:
                    wrong = [[centered_inverse[i][j] * exact_power(root_q, -4 * shift * (i - j))
                              for j in range(size)] for i in range(size)]
                    need(multiply(matrix, wrong) != identity, "reversed shift conjugation rejects")
                    wrong_shift_rejections += 1
                records.append({"q": str(q), "shift": str(shift), "size": size,
                                "inverse_sha256": fraction_hash([x for row in inverse for x in row]),
                                "row_norm": I(row_norm).record(), "column_norm": I(column_norm).record(),
                                "finite_product_constant": I(constant).record(),
                                "gap_free_inverse_norm_upper": I(size * constant).record()})
    rejected(lambda: finite_shift_validate(Q(3, 4)), "outside closed half-shift domain")
    return {"cases": records, "reversed_shift_rejections": wrong_shift_rejections,
            "outside_domain_rejected": True}


def controls():
    rejected_cases = [
        rejected(lambda: validate(Q(1), Q(1, 2)), "positive half-shift"),
        rejected(lambda: validate(Q(1), Q(-1, 2)), "negative half-shift"),
        rejected(lambda: validate(Q(0), Q(0)), "zero scale"),
        rejected(lambda: ldl([[Q(1), Q(4)], [Q(4), Q(1)]]), "indefinite off-diagonal"),
    ]
    # Exact cancellation at the endpoint pairs u with 1-u.
    for u in range(-WIDTH, WIDTH + 2):
        v = 1 - u
        need(-u * u + u == -v * v + v and sign(u) == -sign(v),
             "half-shift pair cancellation")
    need((coefficient(Q(8), Q(3, 4), 1) +
          coefficient(Q(8), Q(3, 4), -1)).lo > 2,
         "outside-domain two-by-two Hermitian part is indefinite")
    coeff = {u: coefficient(Q(8), Q(1, 4), u) for u in range(-WIDTH, WIDTH + 1)}
    m, _ = minimum(Q(8), Q(1, 4), coeff)
    raw_diagonal = I(-Q(8) * Q(1, 4) ** 2).exp()
    need(m.lo > raw_diagonal.hi, "missing normalization overstates raw one-by-one margin")
    need((coefficient(Q(1, 16), Q(0), 1) +
          coefficient(Q(1, 16), Q(0), -1)).lo > 1,
         "zero-width truncation cannot meet half-minimum budget")
    need(canonical({"size": 1}) != canonical({"size": True}),
         "receipt comparison preserves scalar types")
    return {"rejected": rejected_cases, "half_shift_pairs": 2 * WIDTH + 2,
            "outside_domain_indefinite": True, "normalization_control": True,
            "unpaid_tail_control": True, "typed_receipt_control": True}


def run():
    sources = authenticate()
    arithmetic_record = arithmetic.arithmetic_controls()
    pi = arithmetic.pi_interval()
    cases = [(g, s) for g in (Q(1, 16), Q(1, 8), Q(1, 2), Q(1), Q(4), Q(8))
             for s in (Q(0), Q(1, 4), Q(-1, 4), Q(1, 2) - Q(1, 2 ** 20))]
    cases.append((Q(1, 16), Q(1, 2) - Q(1, 2 ** 40)))
    records = []
    for gamma, shift in cases:
        validate(gamma, shift)
        coefficients = {u: coefficient(gamma, shift, u) for u in range(-WIDTH, WIDTH + 1)}
        m, methods = minimum(gamma, shift, coefficients)
        delta = 1 - 2 * abs(shift)
        floor = delta * (pi / gamma).sqrt() * (-pi.square() / (4 * gamma)).exp()
        old_floor = (1 - I(-gamma * delta).exp()) * (-pi.square() / (3 * gamma)).exp()
        need(m.lo >= floor.hi, "new lower bound below certified minimum")
        if gamma <= 1:
            need(floor.lo > old_floor.hi, "small-scale improvement")
        lead = (2 * I(gamma * shift ** 2).exp() * (pi / gamma).sqrt() *
                (-pi.square() / (4 * gamma)).exp() * arithmetic.cos_interval(pi * shift))
        qp = (-2 * pi.square() / gamma).exp()
        relative_tail = qp * (3 - qp) / (1 - qp).square()
        need(relative_tail.hi < Q(1, 2), "positive Poisson leading bound for fixture")
        poisson = I((lead * (1 - relative_tail)).lo, (lead * (1 + relative_tail)).hi)
        poisson.intersect(m)
        tail = tails(gamma, shift, WIDTH)
        circle_count = circle_checks(coefficients, m, tail)
        rounded, error = rounded_kernel(coefficients, tail)
        need(error.hi < DOWN.divide(m.lo, D(2)), "complete kernel perturbation budget")
        finite_constant = (pi.square() / (4 * gamma)).exp()
        records.append({"gamma": str(gamma), "shift": str(shift), "gap": str(delta),
                        "minimum": m.record(), "enclosures": methods,
                        "new_floor": floor.record(), "old_floor": old_floor.record(),
                        "poisson_enclosure": poisson.record(),
                        "circle_samples": circle_count, "kernel_error_majorant": error.record(),
                        "rounded_inverse_norm_upper": str((1 / (m - error)).hi),
                        "finite_sections": sections(coefficients, rounded, m, finite_constant),
                        "near_sharp_size_descriptor": size_descriptor(gamma, m)})
    return {"schema_version": 1, "scope": "finite certified evidence; universal proof in PROOF.md",
            "sources": sources, "arithmetic": arithmetic_record, "pi": pi.record(),
            "kernel_half_width": WIDTH, "coefficient_fractional_bits": BITS,
            "cases": records, "finite_cap": finite_cap_certificates(), "controls": controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed receipt")
    print(json.dumps({"status": "PASS_SHIFTED_GAUSSIAN_CONDITIONING",
                      "case_count": len(result["cases"]),
                      "finite_sections": sum(len(row["finite_sections"]) for row in result["cases"]),
                      "circle_samples": sum(row["circle_samples"] for row in result["cases"]),
                      "exact_finite_cap_cases": len(result["finite_cap"]["cases"]),
                      "result_sha256": sha256(canonical(result)).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
