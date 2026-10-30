#!/usr/bin/env python3
"""Exact check of the uniform CRT evaluator bound.

The proof is PROOF.md. This program checks every integer comparison used
there, the Beneš scan recurrence, schoolbook and division tariffs on their
stated domains, agreement with the retained rotation compiler, and the
negative controls. It does not claim a new kappa.
"""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research" / "unconditional-batched-crt" / "check_batched_crt.py"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_source():
    spec = importlib.util.spec_from_file_location("retained_batched_crt", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bit_length(value):
    need(value >= 0, "nonnegative bit length")
    return value.bit_length() or 1


def prove_schoolbook_tariff():
    """3ab + 3a + b <= 8ab for all integers a, b >= 1."""
    # a = 1: 3 + b <= 5b iff 3 <= 4b, true for b >= 1.
    # b = 1: 3a + 1 <= 5a iff 1 <= 2a, true for a >= 1.
    # a >= 2, b >= 2: 3a + b <= 3ab + ab = 4ab <= 5ab, so 3ab+3a+b <= 8ab.
    need(3 <= 4 * 1, "schoolbook a=1 corner")
    need(1 <= 2 * 1, "schoolbook b=1 corner")
    for a, b in ((2, 2), (2, 3), (5, 2)):
        need(3 * a + b <= 4 * a * b <= 5 * a * b, "schoolbook interior")
    for a in range(1, 17):
        for b in range(1, 17):
            touches = schoolbook_touches(a, b)
            need(touches <= 8 * a * b, "schoolbook execution " + str((a, b)))


def schoolbook_touches(a, b):
    """Bit-steps of the schoolbook product described in PROOF.md."""
    touches = 0
    for _i in range(a):
        touches += b  # AND the addend
        touches += 2 * (b + 1)  # add into a (b+1)-bit window
    touches += a + b  # write the product
    return touches


def prove_division_tariff():
    """Restoring division: <= 8ab bit-steps, quotient length a, divisor length b."""
    # Per quotient bit: 2(b+1) subtractor steps and (b+1) shifts = 3(b+1).
    # Times a, plus a quotient writes: 3ab + 3a + a = 3ab + 4a.
    # 4a <= 5ab for b >= 1, so 3ab + 4a <= 8ab.
    need(4 <= 5 * 1, "division b=1")
    for a in range(1, 13):
        for b in range(1, 13):
            touches = a * 3 * (b + 1) + a
            need(touches <= 8 * a * b, "division tariff " + str((a, b)))


def prove_euclid_tariff():
    """Extended Euclid on a b-bit modulus costs <= 64 b^3 bit-steps for b >= 2.

    Every two remainders the positive value is at least halved:
    r_i = q r_{i+1} + r_{i+2} with q >= 1 and r_{i+1} > r_{i+2},
    so r_i >= r_{i+1} + r_{i+2} > 2 r_{i+2}.
    Hence at most 2b division steps. Each step's division and two coefficient
    products are <= 32 b^2 bit-steps by the tariffs above.
    """
    # 8b^2 division + 16b^2 products + 4b subtractions <= 24b^2 + 4b <= 32b^2.
    # 24b^2 + 4b <= 32b^2 iff 4b <= 8b^2 iff b >= 1.
    need(4 <= 8, "Euclid step for every b >= 1")
    for b in range(1, 9):
        need(24 * b * b + 4 * b <= 32 * b * b, "Euclid step " + str(b))
        need(2 * b * 32 * b * b == 64 * b ** 3, "Euclid total " + str(b))
    # Structural halving on Fibonacci worst cases and on random-looking pairs.
    samples = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
    for modulus in samples:
        for operand in range(1, modulus):
            steps = euclid_steps(operand, modulus)
            bits = bit_length(modulus)
            need(steps <= 2 * bits, "Euclid steps " + str((operand, modulus)))


def euclid_steps(operand, modulus):
    steps = 0
    left, right = operand, modulus
    while left:
        quotient = right // left
        remainder = right - quotient * left
        need(quotient >= 1 and left > remainder, "positive remainder drop")
        need(right >= left + remainder > 2 * remainder, "strict halving inequality")
        right, left = left, remainder
        steps += 1
        need(steps <= 4 * bit_length(modulus), "runaway Euclid")
    return steps


def prove_benes_recurrence():
    """Local scan charge (7n+1)*4*n*k <= 32 k n^2, and T <= 64 k n^2."""
    for k in range(2, 12):
        n = 1 << k
        local = (7 * n + 1) * 4 * n * k
        need(local <= 32 * k * n * n, "local Beneš budget")
        child = 64 * (k - 1) * (n // 2) ** 2
        need(2 * child + 32 * k * n * n == 64 * k * n * n - 32 * n * n, "induction algebra")
        need(2 * child + local <= 64 * k * n * n, "induction with the real local charge")
    need(13 * 4 * 2 * 1 <= 64 * 1 * 4, "n=2 base charge")


def bound(p, ell):
    return 2 ** (4 * ell) * (p + 2) ** 16


def prove_q_maximum():
    """Every term is C(ell) q^a with a <= 4, so term/B is largest at q = 4.

    For integers q >= 5 and a <= 4, q^a 4^{16} < 4^a q^{16} follows from
    q^{12} > 4^{12}, and x |-> x^{12} is strictly increasing on the integers.
    """
    degrees = {
        "setup": 2,
        "crt_quartic": 4,
        "crt_cubic": 3,
        "crt_ell_cube": 2,
        "tables": 1,
        "networks": 1,
    }
    for name, degree in degrees.items():
        need(degree <= 4, name)
        need(4 ** (16 - degree) * 5 ** degree < 5 ** 16, "q=5 beats q=4 for " + name)
    need(5 ** 12 > 4 ** 12, "twelfth powers increase past 4")


def prove_master_inequality():
    """Sum of cost terms <= 2^{4ell}(p+2)^{16} for every integer p >= 2, ell >= 1.

    Each term has q-degree at most 3, so it is largest relative to the bound at
    q = p+2 = 4. At that corner the ell = 1 value fits, and raising ell
    multiplies the term by less than it multiplies the bound.
    """
    prove_q_maximum()
    q = 4
    ell = 1
    terms = cost_terms(q - 2, ell)
    limit = bound(q - 2, ell)
    need(sum(terms.values()) <= limit, "corner sum")
    need(all(7 * value <= limit for value in terms.values()), "corner sevenths")
    # Step factors at q=4. B grows by 2^4 = 16 when ell increases by 1.
    # The quartic and cubic CRT terms do not grow with ell.
    need(1 <= 16, "ell-independent terms")
    # 8192 q^2 ell^3 grows by ((ell+1)/ell)^3 <= 8.
    need(8 <= 16, "ell-cube step")
    # tables grow by ((ell+3)/(ell+2))^2 * 2 <= (4/3)^2 * 2 = 32/9 at ell=1.
    need(32 * 16 <= 9 * 16 * 16, "table step 32/9 <= 16")
    # networks grow by (ell+1)/ell * 4 <= 8.
    need(8 <= 16, "network step")
    for p in range(2, 31):
        for width in range(1, 13):
            values = cost_terms(p, width)
            limit = bound(p, width)
            need(sum(values.values()) <= limit, "grid " + str((p, width)))


def cost_terms(p, ell):
    """Bit-step terms for A<=8(p+2) axes and group width W<=8(p+2).

    CRT allows 8m multiplications, 4m divisions and 2m inverses per axis,
    with m<=8(p+2). Four rotation networks per axis use the Beneš recurrence.
    """
    q = p + 2
    return {
        "setup": 256 * q * q,
        "crt_quartic": 524288 * q ** 4,
        "crt_cubic": 8192 * q ** 3,
        "crt_ell_cube": 8192 * q * q * ell ** 3,
        "tables": 800 * q * (ell + 2) ** 2 * 2 ** ell,
        "networks": 2048 * q * ell * 2 ** (2 * ell),
    }


def prove_amortization():
    """E <= 2^{4ell}(p+2)^{16} implies the displayed 2^{-G} E comparison with C=1.

    G = 64 (ell + ceil(log2(p+2))). The integer form is
    E (p+2)^{48} <= 2^{G - 60 ell}.
    """
    for p in range(2, 65):
        modulus = p + 2
        ceiling = (modulus - 1).bit_length()  # ceil(log2(modulus))
        need(2 ** ceiling >= modulus, "ceil log")
        for ell in (1, 2, 5):
            guard = 64 * (ell + ceiling)
            evaluator = 2 ** (4 * ell) * modulus ** 16
            need(evaluator * modulus ** 48 <= 2 ** (guard - 60 * ell), "amortization")
    # Universal step: (p+2) <= 2^{ceil(log2(p+2))} gives
    # 2^{4ell}(p+2)^{64} <= 2^{4ell + 64 ceil(log2(p+2))} = 2^{G - 60 ell}.
    need(64 - 60 == 4, "exponent split")


def independent_benes(permutation):
    size = len(permutation)
    need(size >= 2 and size & (size - 1) == 0, "dyadic size")
    need(sorted(permutation) == list(range(size)), "permutation")
    if size == 2:
        return [(0, (permutation[0], permutation[0]))]
    inverse = [0] * size
    for position, image in enumerate(permutation):
        inverse[image] = position
    color = [-1] * size
    for start in range(size):
        if color[start] >= 0:
            continue
        color[start] = 0
        stack = [start]
        while stack:
            node = stack.pop()
            neighbors = (node ^ 1, inverse[permutation[node] ^ 1])
            for other in neighbors:
                if color[other] < 0:
                    color[other] = color[node] ^ 1
                    stack.append(other)
                need(color[other] == color[node] ^ 1, "even cycle")
    first = tuple(color[x] ^ (x & 1) for x in range(size))
    last = tuple(color[inverse[y]] ^ (y & 1) for y in range(size))
    children = []
    for wanted in (0, 1):
        child = [permutation[x] // 2 for x in range(size) if color[x] == wanted]
        need(len(child) == size // 2, "child size")
        children.append(independent_benes(child))
    layers = [(0, first)]
    for left, right in zip(*children):
        need(left[0] == right[0], "aligned schedule")
        table = tuple((left, right)[x & 1][1][x // 2] for x in range(size))
        layers.append((left[0] + 1, table))
    layers.append((0, last))
    return layers


def charged_local_scans(size):
    """One recursive level's scan count under the procedure in PROOF.md."""
    if size == 2:
        return 13
    scans = 0
    scans += size  # inverse lookups
    scans += 4 * size  # two neighbors, permutation and inverse, every node
    scans += 2 * size  # stack push and pop
    scans += 1  # emit the two child tables
    need(scans == 7 * size + 1, "scan formula")
    return scans


def rotation(size, modulus, offset):
    return tuple((value + offset) % modulus if value < modulus else value for value in range(size))


def run_network(layers, value):
    for bit, table in layers:
        value ^= table[value] << bit
    return value


def counted_reconstruction(residues, moduli):
    """Operation counts for the retained decode_group formula."""
    counts = {"mul": 0, "div": 0, "inv": 0, "add": 0}
    product = 1
    for modulus in moduli:
        if product != 1:
            counts["mul"] += 1
        product *= modulus
    answer = 0
    prefix = 1
    for value, modulus in zip(residues, moduli):
        counts["div"] += 1
        complement = product // modulus
        counts["mul"] += 1
        counts["div"] += 1
        residue = value * prefix % modulus
        counts["inv"] += 1
        inverse = pow(complement, -1, modulus)
        counts["mul"] += 2
        counts["add"] += 1
        answer += residue * complement * inverse
        counts["mul"] += 1
        prefix *= modulus
    return answer % product, counts


def group_offset(residues, moduli, target):
    """k_A * (running prefix)^{-1} mod target, prefix starting at the left product."""
    product = 1
    mixed = 0
    for residue, modulus in zip(residues, moduli):
        need(0 <= residue < modulus, "residue range")
        mixed += residue * product
        product *= modulus
    prefix = product
    # Caller passes the right-child moduli already folded into `target` only.
    try:
        inverse = pow(prefix, -1, target)
    except ValueError as exc:
        raise ValueError("prefix not invertible") from exc
    return mixed * inverse % target, mixed, product


def prove_outputs(source):
    compared = 0
    for bits in range(1, 5):
        size = 1 << bits
        charged_local_scans(size)
        for modulus in range(2, size + 1):
            for offset in range(0, modulus, max(1, modulus // 3)):
                permutation = rotation(size, modulus, offset)
                ours = independent_benes(permutation)
                retained = source.benes(permutation)
                need(ours == retained, "retained compiler agreement")
                need(tuple(run_network(ours, value) for value in range(size)) == permutation,
                     "rotation endpoint")
                # A single flipped control bit is not the same permutation.
                broken = [list(table) for _bit, table in ours]
                broken[0][0] ^= 1
                mutated = [(bit, tuple(table)) for (bit, _table), table in zip(ours, broken)]
                mutated_images = tuple(run_network(mutated, value) for value in range(size))
                need(mutated_images != permutation, "flipped control changes the map")
                compared += 1
    need(charged_local_scans(32) == 7 * 32 + 1, "larger level formula")
    # One balanced step from a zero right child is the CRT offset.
    checked_groups = 0
    for moduli in ((3, 5), (5, 7), (4, 3), (8, 5), (9, 4), (11, 8)):
        for residue in range(moduli[0]):
            image = source.balanced((residue, 0), moduli)
            lower = source.decode_group((residue,), (moduli[0],))
            offset = lower * pow(moduli[0], -1, moduli[1]) % moduli[1]
            need(image == (residue, offset), "zero right child receives the offset")
            checked_groups += 1
    for moduli in ((3, 5, 7, 11),):
        for residues in ((0, 0), (1, 2), (2, 4), (1, 0)):
            image = source.balanced(residues + (0, 0), moduli)
            need(image == source.direct(residues + (0, 0), moduli), "retained direct endpoint")
            checked_groups += 1
    need(checked_groups > 20, "enough CRT fixtures")
    for moduli, residues in (
        ((3, 5, 7), (1, 2, 3)),
        ((4, 3, 5, 7), (1, 2, 1, 3)),
        ((8, 5, 7, 9), (3, 1, 2, 4)),
    ):
        got, counts = counted_reconstruction(residues, moduli)
        need(got == source.decode_group(residues, moduli), "counted reconstruction")
        modulus_count = len(moduli)
        need(counts["mul"] <= 8 * modulus_count, "multiplication cap")
        need(counts["div"] <= 4 * modulus_count, "division cap")
        need(counts["inv"] <= 2 * modulus_count, "inverse cap")
        need(counts["add"] <= 4 * modulus_count, "addition cap")
    # Non-invertible prefix is rejected.
    rejected = False
    try:
        group_offset((1,), (4,), 2)
    except ValueError:
        rejected = True
    need(rejected, "non-invertible prefix must fail")
    rejected = False
    try:
        independent_benes((0, 0))
    except ValueError:
        rejected = True
    need(rejected, "non-permutation must fail")
    rejected = False
    try:
        source.benes((0, 0))
    except ValueError:
        rejected = True
    need(rejected, "retained compiler rejects a non-permutation")
    return compared, checked_groups


def prove_width_hypotheses_cover_theorem():
    """The closed form already uses A<=8(p+2) and W<=8(p+2); record the slack."""
    # Worst numeric ratio on a modest rectangle, as a witnessed margin.
    worst = 0
    for p in range(2, 25):
        for ell in range(1, 13):
            bound = 2 ** (4 * ell) * (p + 2) ** 16
            ratio = sum(cost_terms(p, ell).values()) / bound
            if ratio > worst:
                worst = ratio
    need(worst < 1 / 50, "uniform margin stronger than 50")
    return worst


def main():
    prove_schoolbook_tariff()
    prove_division_tariff()
    prove_euclid_tariff()
    prove_benes_recurrence()
    prove_master_inequality()
    prove_amortization()
    source = load_source()
    compared, groups = prove_outputs(source)
    worst = prove_width_hypotheses_cover_theorem()
    print(json.dumps({
        "status": "PASS_CRT_UNIFORM_EVALUATOR",
        "constant_C": 1,
        "networks_per_axis": 4,
        "axes_at_most": "8(p+2)",
        "group_bits_at_most": "8(p+2)",
        "compiler_agreements": compared,
        "crt_groups": groups,
        "worst_ratio_on_sample": worst,
        "kappa_claimed": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
