"""Explicit rounded block-boundary audit; Apache-2.0.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
The retained exact Strassen/block program keeps its original attribution.
This is a numerical/interface model, not a fixed-tape execution.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUBJECT = "research/capped-phase-fusion/evidence/radical_reduction_ultra/check_constructions.py"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def matrix_digest(matrix):
    return sha(encoded([[str(x) for x in row] for row in matrix]))


def authenticate(override=None):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for row in pins["files"]:
        if row["usage"] == "input":
            name = row["path"]
            data = override[name] if override and name in override else (ROOT / name).read_bytes()
            need(sha(data) == row["sha256"], "source bytes: " + name)
            result[name] = data
    return result


def maximum(matrix):
    return max((abs(x) for row in matrix for x in row), default=Q(0))


def norm(matrix):
    return max((sum(abs(x) for x in row) for row in matrix), default=Q(0))


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def subtract(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def solve(a, rhs):
    """Independent exact reference; ordinary elimination on the augmented matrix."""
    n = len(a)
    augmented = [list(a[i]) + list(rhs[i]) for i in range(n)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if augmented[i][k]), None)
        need(pivot is not None, "invertible reference")
        augmented[k], augmented[pivot] = augmented[pivot], augmented[k]
        divisor = augmented[k][k]
        augmented[k] = [x / divisor for x in augmented[k]]
        for i in range(n):
            if i != k:
                factor = augmented[i][k]
                augmented[i] = [x - factor * y for x, y in zip(augmented[i], augmented[k])]
    return [row[n:] for row in augmented]


def lu(a):
    n = len(a)
    lower, upper = identity(n), [[Q(0)] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            upper[i][j] = a[i][j] - sum(lower[i][k] * upper[k][j] for k in range(i))
        need(upper[i][i] != 0, "no-pivot LU")
        for j in range(i + 1, n):
            lower[j][i] = (a[j][i] - sum(lower[j][k] * upper[k][i] for k in range(i))) / upper[i][i]
    need(multiply(lower, upper) == a, "exact factor identity")
    return lower, upper


def reverse_both(a):
    return [list(reversed(row)) for row in reversed(a)]


def rounded(a, bits):
    unit = 1 << bits
    return [[Q(int(x * unit), unit) for x in row] for row in a]


def on_grid(a, bits):
    unit = 1 << bits
    return all((x * unit).denominator == 1 for row in a for x in row)


def reject(call, label):
    try:
        call()
    except (ValueError, AssertionError):
        return
    raise ValueError("accepted control: " + label)


class RoundedSubject:
    """Keep the source block order; intercept only pages and declared rounding sites."""

    def __init__(self, source, bits, width, y_bound, inverse_bound, sub_bound, fault=None):
        need(fault in (None, "drop_previous", "skip_solved_round"), "known controlled fault")
        self.fault = fault
        self.bits, self.width = bits, width
        self.eta = Q(2, 1 << bits)
        self.y_bound, self.inverse_bound, self.sub_bound = y_bound, inverse_bound, sub_bound
        self.temporary_bound = 128 * width ** 4 * inverse_bound ** 2 * (sub_bound + 1) * y_bound
        self.depth = self.products = self.updates = self.inverse_pages = 0
        self.max_value, self.max_fractional = Q(0), 0
        self.inverse_ids, self.lower_pages = set(), {}
        self.ns = {"__file__": SUBJECT, "__name__": "retained_boundary_subject"}
        exec(compile(source, SUBJECT, "exec", optimize=0), self.ns)
        self.exact_mul, self.exact_add, self.exact_inverse = (
            self.ns["mul"], self.ns["add"], self.ns["inverse"])
        self.ns.update(mul=self.mul, add=self.add, inverse=self.inverse)

    def observe(self, a):
        self.max_value = max(self.max_value, maximum(a))
        need(self.max_value <= self.temporary_bound, "exact Strassen temporary magnitude")
        for row in a:
            for x in row:
                d = x.denominator
                need(d & (d - 1) == 0, "dyadic live arithmetic")
                self.max_fractional = max(self.max_fractional, d.bit_length() - 1)
        need(self.max_fractional <= 2 * self.bits, "double-fraction temporary width")

    def inverse(self, a):
        reference = self.exact_inverse(a)
        need(norm(reference) <= self.inverse_bound, "consecutive inverse-block bound")
        page = rounded(reference, self.bits)
        need(norm(subtract(page, reference)) <= self.width * self.eta, "inverse-page error")
        self.inverse_pages += 1
        self.inverse_ids.add(id(page))
        self.observe(page)
        return page

    def add(self, a, b, sign=1):
        result = self.exact_add(a, b, sign)
        self.observe(result)
        if self.depth == 0:
            need(sign == -1, "declared completed RHS update")
            self.updates += 1
            result = rounded(result, self.bits)
        return result

    def mul(self, a, b):
        root = self.depth == 0
        inverse_product = root and id(a) in self.inverse_ids
        if root:
            self.products += 1
            need(on_grid(b, self.bits), "completed block input grid")
            if not inverse_product:
                key = tuple(map(tuple, a))
                if key not in self.lower_pages:
                    page = rounded(a, self.bits)
                    need(norm(subtract(page, a)) <= self.width * self.eta, "subdiagonal-page error")
                    self.lower_pages[key] = page
                a = self.lower_pages[key]
                if self.fault == "drop_previous":
                    b = [[Q(0) for _ in row] for row in b]
            need(on_grid(a, self.bits), "factor-page grid")
        self.observe(a)
        self.observe(b)
        self.depth += 1
        try:
            result = self.exact_mul(a, b)
        finally:
            self.depth -= 1
        self.observe(result)
        if inverse_product and self.fault != "skip_solved_round":
            result = rounded(result, self.bits)
        return result

    def run(self, a, rhs):
        n, columns = len(a), len(rhs[0])
        w = self.width
        need(w > 0 and w & (w - 1) == 0, "dyadic block width")
        need(all(len(row) == n for row in a) and all(len(row) == columns for row in rhs),
             "matrix and RHS shapes")
        need(all(not a[i][j] for i in range(n) for j in range(n)
                 if j > i or i - j > w), "natural lower band")
        need(on_grid(rhs, self.bits), "RHS input grid")
        need(maximum(rhs) <= self.y_bound and self.y_bound >= 1, "RHS magnitude")
        before = matrix_digest(a), matrix_digest(rhs)
        result = self.ns["block_solve"](a, rhs, w)
        need(before == (matrix_digest(a), matrix_digest(rhs)), "borrowed source preservation")
        need(on_grid(result, self.bits), "completed solved blocks")
        blocks, batches = (n + w - 1) // w, (columns + w - 1) // w
        need(self.products == (2 * blocks - 1) * batches, "complete two-product schedule")
        need(self.updates == (blocks - 1) * batches, "complete RHS rounding schedule")
        need(self.inverse_pages == blocks, "one reference inverse page per block")
        need(self.ns["OPS"] == self.products * 7 ** (w.bit_length() - 1),
             "actual seven-product multiplication count")
        return result


def pass_constants(a, sub, q, width):
    return a * width + 2 * a + 1, width * (a * (sub + 1) + 1), q


def check_pass(source, matrix, rhs, p, bits, width, upper=False, fault=None):
    a, sub, q = (Q(2), Q(2), Q(1040 * p ** 5)) if upper else (
        Q(65 * p ** 3), Q(65 * p ** 3), Q(32 * p ** 2))
    eta, y = Q(2, 1 << bits), max(Q(1), maximum(rhs))
    c0, c1, _ = pass_constants(a, sub, q, width)
    need(width * eta <= 1 and eta * c0 <= 1 and q * eta * c1 <= Q(1, 2),
         "residual absorption")
    need(norm(matrix) <= max(a, sub), "triangular norm contract")
    need(norm(solve(matrix, identity(len(matrix)))) <= q, "whole triangular inverse bound")
    worker = RoundedSubject(source, bits, width, y, q, sub, fault=fault)
    answer = worker.run(matrix, rhs)
    residual = maximum(subtract(multiply(matrix, answer), rhs))
    magnitude = maximum(answer)
    residual_bound = eta * (c0 * y + c1 * magnitude)
    need(residual <= residual_bound, "actual complete residual")
    need(magnitude <= 4 * q * y, "absorbed output magnitude")
    error = maximum(subtract(answer, solve(matrix, rhs)))
    error_bound = q * eta * (c0 + 4 * q * c1) * y
    need(error <= error_bound, "triangular solution error")
    return answer, {
        "residual": str(residual), "residual_bound": str(residual_bound),
        "error": str(error), "error_bound": str(error_bound),
        "maximum": str(magnitude), "temporary_maximum": str(worker.max_value),
        "temporary_bound": str(worker.temporary_bound),
        "temporary_fractional_bits": worker.max_fractional,
        "root_products": worker.products, "scalar_products": worker.ns["OPS"],
        "rhs_roundings": worker.updates, "inverse_pages": worker.inverse_pages,
        "batches": (len(rhs[0]) + width - 1) // width,
    }


def ceil_log2(q):
    q = Q(q)
    need(q > 0, "positive logarithm")
    e = q.numerator.bit_length() - q.denominator.bit_length()
    power = Q(1 << e) if e >= 0 else Q(1, 1 << -e)
    return e if q <= power else e + 1


def schur(a, eliminated):
    kept = [i for i in range(len(a)) if i not in eliminated]
    aa = [[a[i][j] for j in eliminated] for i in eliminated]
    bb = [[a[i][j] for j in kept] for i in eliminated]
    cc = [[a[i][j] for j in eliminated] for i in kept]
    dd = [[a[i][j] for j in kept] for i in kept]
    return subtract(dd, multiply(cc, solve(aa, bb)))


def cases():
    for p in (1, 2, 4):
        rho = 1 - Q(1, 16 * p * p)
        for n, band, width, columns in ((3, 1, 1, 3), (5, 1, 2, 3),
                                         (9, 2, 4, 5), (12, 3, 4, 7)):
            if band > 2 * p:
                continue
            a = identity(n)
            for i in range(n):
                neighbors = [j for j in range(n) if i != j and abs(i - j) <= band]
                for j in neighbors:
                    a[i][j] = rho * (-1 if (i + 2 * j) % 3 else 1) / len(neighbors)
            yield f"band-p{p}-n{n}-w{width}-r{columns}", p, width, columns, a
        # A pair reaches the inverse gap bound and needs non-dyadic inverse pages.
        yield f"near-gap-p{p}", p, 2, 3, [[Q(1), -rho], [-rho, Q(1)]]
    a = identity(12)
    for i in range(12):
        for j in range(12):
            if 0 < abs(i - j) <= 2:
                a[i][j] = Q(-1, 8)
    yield "finite-section-schur", 2, 4, 5, schur(a, [3, 4, 8, 9])


def audit(source):
    result = {}
    for name, p, width, columns, a in cases():
        n = len(a)
        delta = Q(1, 16 * p * p)
        gap = min(abs(a[i][i]) - sum(abs(a[i][j]) for j in range(n) if j != i)
                  for i in range(n))
        band = max((abs(i - j) for i in range(n) for j in range(n) if a[i][j]), default=0)
        need(norm(a) <= 2 and gap >= delta and band <= 2 * p,
             "fine-prime narrow boundary contract")
        need(band <= width <= 4 * p, "consecutive blocks cover scalar bandwidth")
        lower, upper = lu(a)
        real = [[Q(((i + 2 * j) % 7) - 3, 8) for j in range(columns)] for i in range(n)]
        imag = [[Q(((3 * i + j) % 5) - 2, 8) for j in range(columns)] for i in range(n)]
        if name == "near-gap-p4":
            real = [[17 * x for x in row] for row in real]
        y0 = max(Q(1), max(abs(x) + abs(y) for ar, ai in zip(real, imag) for x, y in zip(ar, ai)))
        bits = 8 + 41 + 16 * ceil_log2(p) + ceil_log2(y0)
        eta = Q(2, 1 << bits)
        need(eta <= Q(1, (1 << 21) * p ** 9), "caller absorption guard")
        parts, records = [], []
        for rhs in (real, imag):
            forward, first = check_pass(source, lower, rhs, p, bits, width)
            backward, second = check_pass(source, reverse_both(upper), list(reversed(forward)),
                                          p, bits, width, upper=True)
            answer = list(reversed(backward))
            parts.append(answer)
            records.append({"lower": first, "upper": second})
        reference = [solve(a, real), solve(a, imag)]
        error = max(abs(parts[0][i][j] - reference[0][i][j])
                    + abs(parts[1][i][j] - reference[1][i][j])
                    for i in range(n) for j in range(columns))
        # Each real pass uses eta/2 or less; the shared complex-l1 allowance
        # above already bounds the joint rounding by eta.
        bound = (1 << 40) * p ** 16 * eta * y0
        need(error <= bound <= Q(1, 256), "two-pass complex solution error")
        magnitude = max(abs(parts[0][i][j]) + abs(parts[1][i][j])
                        for i in range(n) for j in range(columns))
        need(magnitude <= (1 << 20) * p ** 7 * y0, "two-pass magnitude")
        need(all(Q(r[side]["temporary_maximum"]) <= (1 << 46) * p ** 16 * y0
                 for r in records for side in ("lower", "upper")), "two-pass temporary bound")
        result[name] = {
            "p": p, "rows": n, "columns": columns, "width": width, "bits": bits,
            "gap": str(gap), "band": band, "Y0": str(y0), "error": str(error),
            "error_bound": str(bound), "magnitude": str(magnitude),
            "production_batch_domain": columns >= width,
            "passes": records, "answer_sha256": [matrix_digest(x) for x in parts],
        }
    need(any(Q(case["error"]) > 0 for case in result.values()), "nonzero rounded solve error")
    # Inverting an already rounded block violates the page's required error.
    raw = [[Q(1, 3)]]
    correct = solve(raw, identity(1))
    wrong = rounded(solve(rounded(raw, 4), identity(1)), 4)
    need(norm(subtract(wrong, correct)) > Q(2, 16), "rounded-input inverse-page control")
    # A nonconsecutive triangular inverse is not the corresponding full block.
    tri = [[Q(1), Q(0), Q(0)], [Q(1, 2), Q(1), Q(0)], [Q(0), Q(1, 2), Q(1)]]
    full = solve(tri, identity(3))
    need(full[2][0] == Q(1, 4) and solve([[tri[i][j] for j in (0, 2)] for i in (0, 2)],
                                      identity(2))[1][0] == 0, "consecutive-block control")
    reject(lambda: check_pass(source, identity(2), [[Q(1)], [Q(1)]], 1, 1, 1),
           "insufficient absorption precision")
    reject(lambda: check_pass(source, [[Q(1), Q(0)], [Q(-1, 2), Q(1)]],
                              [[Q(1)], [Q(0)]], 1, 49, 1, fault="drop_previous"),
           "omitted previous block")
    reject(lambda: check_pass(source, [[Q(3)]], [[Q(1, 8)]], 1, 49, 1,
                              fault="skip_solved_round"), "omitted solved-block rounding")
    bad = [[Q(1), Q(1, 4)], [Q(0), Q(1)]]
    reject(lambda: RoundedSubject(source, 64, 1, Q(1), Q(32), Q(65)).run(bad, [[Q(1)], [Q(1)]]),
           "unreversed upper direction")
    # A cyclic corner is outside the admitted ordinary lower band.
    corner = identity(4)
    corner[3][0] = Q(1, 4)
    reject(lambda: RoundedSubject(source, 64, 1, Q(1), Q(32), Q(65)).run(
        corner, [[Q(1)]] * 4), "unhandled corner")
    return {
        "status": "PASS_ROUNDED_BOUNDARY_BLOCKS", "cases": result,
        "case_count": len(result), "real_triangular_passes": 4 * len(result),
        "controls": ["rounded-input inverse page", "nonconsecutive inverse block",
                     "insufficient absorption precision", "unreversed upper direction",
                     "unhandled cyclic corner", "omitted previous block",
                     "omitted solved-block rounding"],
        "scope": "Source-bound rounded two-product solves and explicit residual/headroom proof for the finite-section narrow boundary; no physical tape execution, broad inverse or full multiplication theorem.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    sources = authenticate()
    reject(lambda: authenticate({SUBJECT: sources[SUBJECT] + b"\n"}), "source corruption")
    result = audit(sources[SUBJECT])
    if args.emit:
        with args.emit.open("x") as handle:
            json.dump(result, handle, sort_keys=True, indent=2)
            handle.write("\n")
    else:
        need(encoded(result) == encoded(json.loads((HERE / "RESULT.json").read_text())),
             "complete typed retained receipt")
    print(json.dumps({"status": result["status"], "cases": result["case_count"],
                      "receipt_sha256": sha(encoded(result)), "scope": result["scope"]}, sort_keys=True))


if __name__ == "__main__":
    main()
