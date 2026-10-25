#!/usr/bin/env python3
"""Phase-sharp pre-wrapper uniqueness for hyperplane-ended helpers.

Labels.lean proves factor_iff_pre only for lambda = 1. This verifier states the
scalar extension and checks it two ways:

  * equational replay over Q(i): (N) plus invertibility of C gives
    L^{-1} T_U T_E^{-1} R'^{-1} = lambda (C tensor id)
    if and only if R' = lambda^{-1} R, including a singular-C counterexample;
  * exact Z[i] circuits for the three certified pairs in Exact.lean, with the
    pre-wrapper monomial varied and the post wrapper held fixed.

usage: python3 -B research/hpe-pre-wrapper-phase/verify.py [--self-test]
Python 3.10+, standard library only. Apache-2.0.
"""
import ast
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXACT = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"
LABELS = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Labels.lean"
N = 512

BRACKETS = {0x27E8: "[", 0x27E9: "]", 0x2329: "[", 0x232A: "]", 0x00AB: "[",
            0x00BB: "]", 0x2039: "[", 0x203A: "]", 0xFF08: "(", 0xFF09: ")"}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def translated(text):
    return "".join(BRACKETS.get(ord(ch), ch) for ch in text)


def bracket_block(text, start):
    i = text.index("[", start)
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "[":
            depth += 1
        elif text[j] == "]":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    raise ValueError("unterminated bracket block")


def parse_gate_block(block):
    gates = []
    for match in re.finditer(r"\.(dg|pm|cg|xg|ph)\b", block):
        kind = match.group(1)
        pos = match.end()
        if kind in ("dg", "pm"):
            args = []
            for _ in range(2):
                start = block.index("[", pos)
                arg = bracket_block(block, pos)
                args.append(ast.literal_eval(arg))
                pos = start + len(arg)
        elif kind == "cg":
            found = re.match(r"\s*(\d+)\s+(true|false)", block[pos:])
            need(found is not None, "bad cg gate")
            args = [int(found.group(1)), found.group(2) == "true"]
        else:
            found = re.match(r"\s*(\d+)", block[pos:])
            need(found is not None, "bad " + kind + " gate")
            args = [int(found.group(1))]
        gates.append(tuple([kind] + args))
    return gates


def parse_defs(text):
    text = translated(text)
    out = {}
    names = ("fE1", "fU1", "fE2", "fU2", "fE3", "fU3",
             "wL1", "wR1", "wL2", "wR2", "wL3", "wR3",
             "lhsLit1", "rhsLit1", "lhsLit2", "rhsLit2", "lhsLit3", "rhsLit3")
    for name in names:
        match = re.search(r"def " + name + r" : List Gate :=", text)
        need(match is not None, "missing literal " + name)
        out[name] = parse_gate_block(bracket_block(text, match.end()))
    for index in (1, 2, 3):
        match = re.search(r"def pair" + str(index) + r" : Pair :=", text)
        need(match is not None, "missing literal pair%d" % index)
        data = ast.literal_eval(bracket_block(text, match.end()))
        need(len(data) == 4, "pair%d shape" % index)
        out["pair%d" % index] = data
    return out


def mv(rows, value):
    image = 0
    for bit, row in enumerate(rows):
        if bin(row & value).count("1") & 1:
            image |= 1 << bit
    return image


def qv(q_rows, alpha, value):
    total = 0
    for index in range(len(q_rows)):
        if (value >> index) & 1:
            high = (q_rows[index] >> (index + 1)) & (value >> (index + 1))
            total += alpha[index] + 2 * (bin(high).count("1") & 1)
    return total % 4


def inv_rows(rows, width):
    aug = [[rows[i] if i < len(rows) else 0, 1 << i] for i in range(width)]
    for col in range(width):
        pivot = next((i for i in range(col, width) if (aug[i][0] >> col) & 1), None)
        need(pivot is not None, "singular matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        for row in range(width):
            if row != col and (aug[row][0] >> col) & 1:
                aug[row][0] ^= aug[col][0]
                aug[row][1] ^= aug[col][1]
    return [aug[i][1] for i in range(width)]


def mono_gates(mono):
    q_rows, alpha, linear, offset, phase = mono
    return [("dg", q_rows, alpha), ("pm", linear, inv_rows(linear, 9)),
            ("xg", offset), ("ph", phase)]


def adj(gate):
    kind = gate[0]
    if kind == "pm":
        return ("pm", gate[2], gate[1])
    if kind == "dg":
        return ("dg", gate[1], [(4 - a % 4) % 4 for a in gate[2]])
    if kind == "cg":
        return ("cg", gate[1], not gate[2])
    if kind == "xg":
        return gate
    return ("ph", (4 - gate[1] % 4) % 4)


def adj_c(circ):
    return [adj(gate) for gate in reversed(circ)]


def fourier_c(width):
    return [("cg", 1 << i, True) for i in range(width)]


def ipow(power, real, imag):
    power %= 4
    if power == 0:
        return real, imag
    if power == 1:
        return -imag, real
    if power == 2:
        return -real, -imag
    return imag, -real


def apply_circuit(circ, real, imag):
    for gate in circ:
        kind = gate[0]
        if kind == "pm":
            nxt_r, nxt_i = [0] * N, [0] * N
            for state in range(N):
                source = mv(gate[2], state)
                nxt_r[state], nxt_i[state] = real[source], imag[source]
            real, imag = nxt_r, nxt_i
        elif kind == "dg":
            for state in range(N):
                real[state], imag[state] = ipow(qv(gate[1], gate[2], state), real[state], imag[state])
        elif kind == "cg":
            qubit, sign = gate[1], gate[2]
            nxt_r, nxt_i = [0] * N, [0] * N
            for state in range(N):
                left_r, left_i = real[state], imag[state]
                right_r, right_i = real[state ^ qubit], imag[state ^ qubit]
                if sign:
                    nxt_r[state] = (left_r - left_i) + (right_r + right_i)
                    nxt_i[state] = (left_r + left_i) + (-right_r + right_i)
                else:
                    nxt_r[state] = (left_r + left_i) + (right_r - right_i)
                    nxt_i[state] = (-left_r + left_i) + (right_r + right_i)
            real, imag = nxt_r, nxt_i
        elif kind == "xg":
            bit = gate[1]
            nxt_r, nxt_i = [0] * N, [0] * N
            for state in range(N):
                nxt_r[state], nxt_i[state] = real[state ^ bit], imag[state ^ bit]
            real, imag = nxt_r, nxt_i
        else:
            for state in range(N):
                real[state], imag[state] = ipow(gate[1], real[state], imag[state])
    return real, imag


def packed(circ, base):
    real = [0] * N
    imag = [0] * N
    power = 1
    for state in range(N):
        real[state] = power
        power *= base
    return apply_circuit(circ, real, imag)


def ncg(circ):
    return sum(gate[0] == "cg" for gate in circ)


def signed_digits(value, base, count):
    digits = []
    for _ in range(count):
        digit = value % base
        if digit > base // 2:
            digit -= base
        digits.append(digit)
        value = (value - digit) // base
    need(value == 0, "packed value exceeds digit budget")
    return digits


def map_equal(left, right):
    count_l, count_r = ncg(left), ncg(right)
    scale_l, scale_r = 1 << count_l, 1 << count_r
    expo = max(count_r + 2 * count_l, count_l + 2 * count_r)
    base = 1 << (expo + 3)
    real_l, imag_l = packed(left, base)
    real_r, imag_r = packed(right, base)
    for state in range(N):
        if real_l[state] * scale_r != real_r[state] * scale_l or imag_l[state] * scale_r != imag_r[state] * scale_l:
            digits = [signed_digits(real_l[state] * scale_r, base, N),
                      signed_digits(imag_l[state] * scale_r, base, N),
                      signed_digits(real_r[state] * scale_l, base, N),
                      signed_digits(imag_r[state] * scale_l, base, N)]
            for column in range(N):
                if (digits[0][column], digits[1][column]) != (digits[2][column], digits[3][column]):
                    return (state, column, [digits[0][column], digits[1][column]],
                            [digits[2][column], digits[3][column]])
            need(False, "row differs but no column witness decodes")
    return None


def pre_circuit(pre_mono, post_mono, entrance, terminal):
    """L^{-1} T_U T_E^{-1} R'^{-1}, with R' applied first."""
    return (adj_c(mono_gates(pre_mono)) + adj_c(entrance) + terminal
            + adj_c(mono_gates(post_mono)))


def phase_target(power):
    return fourier_c(7) + [("ph", power % 4)]


# ---- exact equational model over Q(i) ----

class G:
    __slots__ = ("re", "im")

    def __init__(self, real, imag=0):
        self.re = Fraction(real)
        self.im = Fraction(imag)

    def __add__(self, other):
        return G(self.re + other.re, self.im + other.im)

    def __sub__(self, other):
        return G(self.re - other.re, self.im - other.im)

    def __mul__(self, other):
        return G(self.re * other.re - self.im * other.im,
                 self.re * other.im + self.im * other.re)

    def __eq__(self, other):
        return self.re == other.re and self.im == other.im

    def inv(self):
        norm = self.re * self.re + self.im * self.im
        need(norm != 0, "zero is not invertible in Q(i)")
        return G(self.re / norm, -self.im / norm)


def mat_mul(left, right):
    width = len(left)
    return [[sum((left[i][k] * right[k][j] for k in range(width)), G(0))
             for j in range(width)] for i in range(width)]


def mat_inv(matrix):
    width = len(matrix)
    aug = [row[:] + [G(int(i == j)) for j in range(width)] for i, row in enumerate(matrix)]
    for col in range(width):
        pivot = next((row for row in range(col, width)
                      if aug[row][col].re != 0 or aug[row][col].im != 0), None)
        need(pivot is not None, "singular matrix in the equational model")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col].inv()
        aug[col] = [scale * entry for entry in aug[col]]
        for row in range(width):
            if row != col and (aug[row][col].re != 0 or aug[row][col].im != 0):
                factor = aug[row][col]
                aug[row] = [aug[row][j] - factor * aug[col][j] for j in range(2 * width)]
    return [row[width:] for row in aug]


def mat_scale(scalar, matrix):
    return [[scalar * entry for entry in row] for row in matrix]


def mat_eq(left, right):
    return all(a == b for row_l, row_r in zip(left, right) for a, b in zip(row_l, row_r))


def eye(width):
    return [[G(int(i == j)) for j in range(width)] for i in range(width)]


def replay_equation(size, ell, arr, cee, lam):
    """Replay (N) => the phase-sharp pre-wrapper equivalence at this size."""
    block = mat_mul(ell, mat_mul(cee, arr))
    predicted = mat_scale(lam.inv(), arr)
    left = mat_mul(mat_inv(ell), mat_mul(block, mat_inv(predicted)))
    need(mat_eq(left, mat_scale(lam, cee)), "forward direction failed")
    # Converse, read off the cancelled equation: C (R R'^{-1}) = lambda C.
    recovered = mat_mul(mat_inv(cee), left)
    need(mat_eq(recovered, mat_scale(lam, eye(size))), "cancelled residual is not lambda I")
    solved = mat_mul(arr, mat_inv(recovered))
    need(mat_eq(solved, predicted), "solved pre-wrapper is not lambda^{-1} R")


def algebraic_model():
    units = [G(1), G(0, 1), G(-1), G(0, -1), G(2, 1)]
    sizes = {
        2: ( [[G(1), G(1)], [G(0), G(1)]],
              [[G(1), G(0, 1)], [G(0), G(1)]],
              [[G(1), G(0)], [G(1), G(2)]] ),
        3: ( [[G(1), G(0), G(0)], [G(1), G(1), G(0)], [G(0), G(1), G(1)]],
              [[G(0, 1), G(1), G(0)], [G(0), G(1), G(0)], [G(0), G(0), G(1)]],
              [[G(1), G(1), G(0)], [G(0), G(1), G(0)], [G(0), G(1), G(1)]] ),
    }
    checked = 0
    for size, (ell, arr, cee) in sizes.items():
        for lam in units:
            replay_equation(size, ell, arr, cee, lam)
            checked += 1
            bad = [row[:] for row in mat_scale(lam.inv(), arr)]
            bad[0][-1] = bad[0][-1] + G(1)
            block = mat_mul(ell, mat_mul(cee, arr))
            left = mat_mul(mat_inv(ell), mat_mul(block, mat_inv(bad)))
            need(not mat_eq(left, mat_scale(lam, cee)), "a shifted pre-wrapper was accepted")
    # Singular residual: equality can hold while R' is not lambda^{-1} R.
    lam = G(0, 1)
    cee = [[G(1), G(0)], [G(0), G(0)]]
    arr = eye(2)
    ell = [[G(1), G(3)], [G(0), G(1)]]
    pre_inv = [[lam, G(0)], [G(5), G(1)]]
    pre = mat_inv(pre_inv)
    block = mat_mul(ell, mat_mul(cee, arr))
    left = mat_mul(mat_inv(ell), mat_mul(block, pre_inv))
    need(mat_eq(left, mat_scale(lam, cee)), "singular control did not satisfy the scaled equation")
    need(not mat_eq(pre, mat_scale(lam.inv(), arr)), "singular control accidentally used the unique pre-wrapper")
    return checked


def source_gap(labels):
    need("theorem factor_iff_pre" in labels, "factor_iff_pre moved")
    need("↔ R' = R" in labels or "<-> R' = R" in translated(labels),
         "factor_iff_pre no longer concludes R' = R")
    need("factor_iff_post" not in labels, "Labels.lean already contains factor_iff_post")
    need("lambda" not in labels and "λ" not in labels,
         "Labels.lean already quantifies a wrapper scalar")


def run(defs):
    checked = algebraic_model()
    witnesses = []
    for index in (1, 2, 3):
        pair = defs["pair%d" % index]
        entrance, terminal = defs["fE%d" % index], defs["fU%d" % index]
        post, pre = pair[2], pair[3]
        need(adj_c(entrance) + terminal == defs["lhsLit%d" % index],
             "pair%d adj port" % index)
        need(defs["wR%d" % index] + fourier_c(7) + defs["wL%d" % index] == defs["rhsLit%d" % index],
             "pair%d composition port" % index)
        need(mono_gates(post) == defs["wL%d" % index], "pair%d post monomial port" % index)
        need(mono_gates(pre) == defs["wR%d" % index], "pair%d pre monomial port" % index)
        q_rows, alpha, linear, offset, phase = pre
        mutants = [
            ("shipped", pre, "phase", 0),
            ("phase+1", [q_rows, alpha, linear, offset, phase + 1], "phase", 3),
            ("phase-1", [q_rows, alpha, linear, offset, phase - 1], "phase", 1),
            ("phase+2", [q_rows, alpha, linear, offset, phase + 2], "phase", 2),
            ("offset-xor-1", [q_rows, alpha, linear, offset ^ 1, phase], "reject", None),
            ("linear-Z4-flip", [q_rows, [alpha[0] ^ 1] + list(alpha[1:]), linear, offset, phase], "reject", None),
            ("quadratic-live-bit", [[q_rows[0] ^ 2] + q_rows[1:], alpha, linear, offset, phase], "reject", None),
            ("swapped-L-R", post, "reject", None),
            ("quadratic-dead-bit", [[q_rows[0] ^ 1] + q_rows[1:], alpha, linear, offset, phase], "phase", 0),
        ]
        for name, mono, kind, expected in mutants:
            hits = []
            witness = None
            for power in range(4):
                found = map_equal(pre_circuit(mono, post, entrance, terminal), phase_target(power))
                if found is None:
                    hits.append(power)
                elif witness is None:
                    witness = found
            if kind == "phase":
                need(hits == [expected],
                     "pair%d %s holds at %s, expected only %s" % (index, name, hits, expected))
            else:
                need(hits == [], "pair%d %s held at %s" % (index, name, hits))
                need(witness is not None, "pair%d %s has no witness" % (index, name))
            witnesses.append({"pair": index, "mutant": name, "holds_at": hits,
                              "witness": None if witness is None else [witness[0], witness[1]]})
        plain = pre_circuit(pre, post, entrance, terminal)
        need(map_equal(plain, fourier_c(8)) is not None, "pair%d accepts residual width 8" % index)
    return checked, witnesses


def main():
    labels = LABELS.read_text(encoding="utf-8")
    source_gap(labels)
    defs = parse_defs(EXACT.read_text(encoding="utf-8"))
    if "--self-test" in sys.argv:
        defs["pair1"][3][4] = (defs["pair1"][3][4] + 1) % 4
        defs["wR1"] = mono_gates(defs["pair1"][3])
        defs["rhsLit1"] = defs["wR1"] + fourier_c(7) + defs["wL1"]
        try:
            run(defs)
        except ValueError as exc:
            print("PASS_SELF_TEST corrupted pre-wrapper rejected: " + str(exc))
            return
        need(False, "self-test accepted a phase-shifted shipped pre-wrapper as lambda 1")
    checked, witnesses = run(defs)
    phase_rows = sum(1 for row in witnesses if row["mutant"].startswith("phase") or row["mutant"] == "shipped")
    reject_rows = sum(1 for row in witnesses if row["holds_at"] == [] )
    print("PASS_HPE_PRE_WRAPPER_PHASE pairs=3 algebraic=%d phase_rows=%d reject_rows=%d no_new_kappa"
          % (checked, phase_rows, reject_rows))


if __name__ == "__main__":
    main()
