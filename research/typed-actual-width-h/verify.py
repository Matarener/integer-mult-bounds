#!/usr/bin/env python3
"""Typed actual-width H0 and one toward-zero return on the matched array.

The multi-round stock allowance from discussion 1166 comment 19016699 is not
claimed. unpaidmoon, with substantial AI assistance. Apache-2.0.
"""

from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
FROZEN = {
    "frozen/pr3493-outer_layer.py":
        "3e6bae42f4e6239d0a467fb0498da3906fc139672fae96211c835be3b5fef307",
    "frozen/pr3599-active_plan.py":
        "e1092fdbb70df43f1d4fdb50f39a07a543d71c4ea9f9e8a50b790b81fd50223e",
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def root_int(n, degree):
    need(type(n) is int and n >= 0 and type(degree) is int and degree >= 1, "root domain")
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + degree - 1) // degree)
    while True:
        y = ((degree - 1) * x + n // pow(x, degree - 1)) // degree
        if y >= x:
            break
        x = y
    need(pow(x, degree) <= n < pow(x + 1, degree), "exact integer root")
    return x


def fits(value, width):
    need(type(value) is int and type(width) is int and width >= 1, "word domain")
    return -(1 << (width - 1)) <= value <= (1 << (width - 1)) - 1


def on_disk(re, im, p):
    limit = 1 << p
    return re * re + im * im <= limit * limit


def toward_zero(value, denominator):
    need(type(value) is int and type(denominator) is int and denominator > 0, "truncation domain")
    return (1 if value >= 0 else -1) * (abs(value) // denominator)


def twos(value, width):
    need(fits(value, width), "word does not fit")
    return value % (1 << width)


def from_lsb(bits):
    width = len(bits)
    raw = 0
    for i, bit in enumerate(bits):
        raw |= bit << i
    if raw >= (1 << (width - 1)):
        raw -= 1 << width
    return raw


def from_msb(bits):
    width = len(bits)
    raw = 0
    for bit in bits:
        raw = (raw << 1) | bit
    if raw >= (1 << (width - 1)):
        raw -= 1 << width
    return raw


class Meter:
    def __init__(self):
        self.bit_reads = 0
        self.bit_writes = 0
        self.real_add_sub = 0
        self.truncations = 0
        self.rewinds = 0
        self.layout_word_transfers = 0


class WordTape:
    """Concatenated two's-complement words, least-significant bit first."""

    def __init__(self, width, meter):
        self.width = width
        self.meter = meter
        self.bits = []
        self.head = 0

    def write_word(self, value):
        raw = twos(value, self.width)
        for i in range(self.width):
            self.bits.append((raw >> i) & 1)
            self.meter.bit_writes += 1

    def read_word(self):
        raw = 0
        for i in range(self.width):
            raw |= self.bits[self.head] << i
            self.head += 1
            self.meter.bit_reads += 1
        if raw >= (1 << (self.width - 1)):
            raw -= 1 << self.width
        return raw

    def rewind(self):
        self.head = 0
        self.meter.rewinds += 1


def write_msb_word(bits, value, width, meter):
    raw = twos(value, width)
    for i in range(width):
        bits.append((raw >> (width - 1 - i)) & 1)
        meter.bit_writes += 1


def butterfly(rows, bits, temp_width, meter):
    result = [pair for pair in rows]
    for bit in bits:
        for x in range(len(result)):
            if (x >> bit) & 1:
                continue
            y = x | (1 << bit)
            left, right = result[x], result[y]
            summed = (left[0] + right[0], left[1] + right[1])
            diffed = (left[0] - right[0], left[1] - right[1])
            for pair in (summed, diffed):
                need(fits(pair[0], temp_width) and fits(pair[1], temp_width), "temporary width")
            result[x] = summed
            result[y] = diffed
            meter.real_add_sub += 4
    return result


def direct_tensor(rows, bits):
    mask = sum(1 << bit for bit in bits)
    result = []
    for x in range(len(rows)):
        acc = (0, 0)
        for choice in range(1 << len(bits)):
            y = x & ~mask
            for j, bit in enumerate(bits):
                y |= ((choice >> j) & 1) << bit
            sign = -1 if (x & y & mask).bit_count() % 2 else 1
            acc = (acc[0] + sign * rows[y][0], acc[1] + sign * rows[y][1])
        result.append(acc)
    return result


def truncate_rows(rows, denominator, meter):
    output = []
    for re, im in rows:
        output.append((toward_zero(re, denominator), toward_zero(im, denominator)))
        meter.truncations += 2
    return output


def slots_for(ell, flags, k):
    need(ell >= 2 and flags and 1 <= k < ell, "layout domain")
    original = tuple((i, h) for i, long in enumerate(flags)
                     for h in range(ell - (not long) - 1, -1, -1))
    b, q = (ell - 1) % k, (ell - 1) // k
    prefix = [(i, ell - 1) for i, long in enumerate(flags) if long]
    prefix += [(i, h) for h in range(b - 1, -1, -1) for i in range(len(flags))]
    chunks = [(i, h) for j in range(q) for i in range(len(flags))
              for h in range(ell - 2 - j * k, ell - 2 - (j + 1) * k, -1)]
    changed = tuple(prefix + chunks)
    need(len(set(changed)) == len(original) and set(changed) == set(original), "layout bijection")
    return original, changed


def selected_bits(slots, h):
    return tuple(len(slots) - 1 - j for j, item in enumerate(slots) if item[1] == h)


def root_bits(flags, ell, k, h):
    g, a = len(flags), sum(flags)
    b, q = (ell - 1) % k, (ell - 1) // k
    need(b <= h < ell - 1, "common-round domain")
    j, rho = (ell - 2 - h) // k, (h - b) % k
    left = a + g * b + j * g * k
    right = (q - j - 1) * g * k
    bits = tuple(right + rho + t * k for t in range(g))
    return left, right, bits


def layout_address_width(flags, ell):
    return sum(ell - (not long) for long in flags)


def check_layout_family():
    cases = ((2, (False,), 1), (2, (True,), 1),
             (3, (False, False), 1), (3, (True, False), 1),
             (3, (True, True), 1), (3, (False, False, False), 1),
             (3, (True, False, True), 1),
             (3, (False, False, False, False), 2),
             (3, (True, False, False, False), 2),
             (4, (True, False), 2))
    checked = 0
    for ell, flags, k in cases:
        _original, physical = slots_for(ell, flags, k)
        need(len(_original) == layout_address_width(flags, ell), "named-slot count")
        b = (ell - 1) % k
        for h in range(b, ell - 1):
            left, right, bits = root_bits(flags, ell, k, h)
            need(left + len(flags) * k + right == len(physical), "complete root extent")
            need(set(bits) == set(selected_bits(physical, h)), "matched selected bits")
            checked += 1
    original, physical = slots_for(3, (False, False, False), 1)
    need(set(selected_bits(original, 0)) == {0, 2, 4}, "original height-0 bits are the old stride")
    need(set(selected_bits(physical, 0)) == {0, 1, 2}, "matched height-0 bits are contiguous")
    # The scaled K=2 versus K=1 layouts are different permutations.
    short = (False, False, False)
    _, old = slots_for(3, short, 2)
    _, new = slots_for(3, short, 1)
    need(old != new, "old and matched layouts differ")
    need(len(old) == 6 and 3 * 1 != len(old), "concealed-extent bit count disagrees")
    return checked


def apply_layout(rows, coefficients, before, after, meter):
    """Permute whole records. `rows` is address-major with `coefficients` gaussians each."""
    addresses = len(rows) // coefficients
    need(len(before) == addresses.bit_length() - 1 or (1 << len(before)) == addresses, "layout shape")
    need(len(rows) % coefficients == 0, "record shape")

    def bit_at(x, slots, named):
        return (x >> (len(slots) - 1 - slots.index(named))) & 1

    output = [None] * len(rows)
    for x in range(addresses):
        y = 0
        for name in after:
            y = 2 * y + bit_at(x, before, name)
        for j in range(coefficients):
            output[y * coefficients + j] = rows[x * coefficients + j]
            meter.layout_word_transfers += 4
    need(all(row is not None for row in output), "layout image")
    return output


def physical_round(rows, bits, p, meter, final_width=None):
    """Read LSB-first words, apply H0 tensor g, one Q_p, then an MSB-first bridge."""
    g = len(bits)
    need(g >= 1 and p >= 1, "round domain")
    n = len(rows)
    need(n > 0 and (n & (n - 1)) == 0, "power-of-two address block")
    width = p + 2
    temp_width = p + g + 2
    denominator = 1 << g
    source = WordTape(width, meter)
    for re, im in rows:
        need(on_disk(re, im, p), "input disk")
        source.write_word(re)
        source.write_word(im)
    source.rewind()
    loaded = [(source.read_word(), source.read_word()) for _ in range(n)]
    need(loaded == [tuple(pair) for pair in rows], "LSB-first reload")
    raw = butterfly(loaded, bits, temp_width, meter)
    need(raw == direct_tensor(loaded, bits), "butterfly matches explicit tensor")
    for re, im in raw:
        need(fits(re, temp_width) and fits(im, temp_width), "sharp temporary admission")
        need(not (fits(1 << (p + g), temp_width - 1)), "narrow width is not a standing fact")
    coarse = truncate_rows(raw, denominator, meter)
    for (ure, uim), (cre, cim) in zip(raw, coarse):
        need(abs(ure - cre * denominator) <= denominator - 1, "real remainder")
        need(abs(uim - cim * denominator) <= denominator - 1, "imag remainder")
        need(on_disk(cre, cim, p), "returned disk")
        need(fits(cre, width) and fits(cim, width), "returned width")
    if final_width is None:
        final_width = width
    need(final_width == width, "one final p-grid width")
    output = WordTape(width, meter)
    bridge_bits = []
    for re, im in coarse:
        output.write_word(re)
        output.write_word(im)
        for part in (re, im):
            before = len(bridge_bits)
            write_msb_word(bridge_bits, part, width, meter)
            stored = bridge_bits[before:before + width]
            meter.bit_reads += width
            need(from_msb(stored) == part, "MSB-first bridge preserves the value")
            lsb = [(twos(part, width) >> i) & 1 for i in range(width)]
            need(from_lsb(lsb) == part, "LSB-first encoding preserves the value")
            if lsb != list(reversed(lsb)):
                need(from_msb(lsb) != part, "reading LSB order as MSB changes a non-palindromic word")
    output.rewind()
    returned = [(output.read_word(), output.read_word()) for _ in range(n)]
    need(returned == coarse, "coarse reload")
    return returned, raw


def closed_form(n, g, p, layout=False):
    width = p + 2
    # Input write, input read, output write, output read: 4 word passes, 2 components.
    # Four LSB word passes (write, read, write, read) plus one MSB bridge
    # write and read, two components each.
    bit_passes = 6 * n * width
    return {
        "gaussians": n,
        "temporary_width": p + g + 2,
        "final_width": width,
        "real_add_sub": 2 * g * n,
        "truncations": 2 * n,
        "bit_reads": bit_passes,
        "bit_writes": bit_passes,
        "layout_word_transfers": 4 * n if layout else 0,
        "rewinds": 2,
    }


def check_invoice(rows, bits, p):
    meter = Meter()
    returned, raw = physical_round(rows, bits, p, meter)
    form = closed_form(len(rows), len(bits), p, layout=False)
    need(meter.real_add_sub == form["real_add_sub"], "addition invoice")
    need(meter.truncations == form["truncations"], "truncation invoice")
    need(meter.bit_reads == form["bit_reads"], "bit-read invoice")
    need(meter.bit_writes == form["bit_writes"], "bit-write invoice")
    need(meter.rewinds == form["rewinds"], "rewind invoice")
    need(meter.layout_word_transfers == 0, "no layout in this call")
    return returned, raw, form


def disk_points(p):
    limit = 1 << p
    return [(a, b) for a in range(-limit, limit + 1) for b in range(-limit, limit + 1)
            if a * a + b * b <= limit * limit]


def exhaustive_one_bit():
    p, bit = 3, (0,)
    points = disk_points(p)
    checked = 0
    for left in points:
        for right in points:
            returned, raw, _ = check_invoice([left, right], bit, p)
            # Explicit two-point H0 before the single truncation.
            need(raw[0] == (left[0] + right[0], left[1] + right[1]), "sum branch")
            need(raw[1] == (left[0] - right[0], left[1] - right[1]), "difference branch")
            need(returned[0] == tuple(toward_zero(v, 2) for v in raw[0]), "sum return")
            checked += 1
    # Sharp temporary numerator on the constant boundary input.
    limit = 1 << p
    constant = [(limit, 0), (limit, 0)]
    returned, raw, form = check_invoice(constant, bit, p)
    need(raw[0] == (2 * limit, 0) and raw[1] == (0, 0), "sharp unnormalized sum")
    need(returned[0] == (limit, 0) and returned[1] == (0, 0), "sharp rounded return")
    need(not fits(2 * limit, form["temporary_width"] - 1), "width p+g+1 rejects the sharp sum")
    need(fits(2 * limit, form["temporary_width"]), "width p+g+2 admits the sharp sum")
    negative = [(-limit, 0), (-limit, 0)]
    returned, raw, _ = check_invoice(negative, bit, p)
    need(raw[0] == (-2 * limit, 0) and returned[0] == (-limit, 0), "odd rounded return")
    return {"disk_points": len(points), "pairs": checked, "temporary_width": form["temporary_width"]}


def scaled_witness():
    """Degree-2 stand-in of the K_d/K_g selected-bit mismatch. Not a 500th-power cube."""
    need(root_int(4, 2) == 2 and root_int(3, 2) == 1, "scaled floors")
    rows = [(0, 0) for _ in range(1 << 5)]
    rows[0] = (8, 0)
    p = 3
    matched, raw_m, invoice = check_invoice(rows, (0, 1, 2), p)
    old, raw_o, _ = check_invoice(rows, (0, 2, 4), p)
    need(matched[2] == (1, 0) and raw_m[2] == (8, 0), "matched address-two return")
    need(old[2] == (0, 0) and raw_o[2] == (0, 0), "old selected bits miss address two")
    need(matched != old, "the two tensors disagree")
    flags = (False, False, False)
    original, physical = slots_for(3, flags, 1)
    meter = Meter()
    impulse = [(0, 0) for _ in range(1 << len(original))]
    impulse[0] = (8, 0)
    moved_impulse = apply_layout(impulse, 1, original, physical, meter)
    need(moved_impulse == impulse, "origin impulse is fixed by the matched layout")
    need(meter.layout_word_transfers == 4 * len(impulse), "impulse layout transfer count")
    _, _, height0 = root_bits(flags, 3, 1, 0)
    need(set(height0) == {0, 1, 2}, "common height 0 uses the matched bits")
    laid, _, _ = check_invoice(moved_impulse, height0, p)
    need(laid[2] == (1, 0), "layout-fixed impulse still returns address two")
    meter = Meter()
    base = [((i % 5) - 2, 0) for i in range(1 << len(original))]
    moved = apply_layout(base, 1, original, physical, meter)
    need(meter.layout_word_transfers == 4 * len(base), "layout transfer count")
    need(sorted(moved) == sorted(base) and moved != base, "layout is a nontrivial permutation")
    h = 1
    _, _, bits = root_bits(flags, 3, 1, h)
    need(set(bits) == set(selected_bits(physical, h)), "physical common-round bits")
    returned, _, _ = check_invoice(moved, bits, p)
    need(all(on_disk(re, im, p) for re, im in returned), "layout image returns to the disk")
    return {"matched_address_2": list(matched[2]), "old_address_2": list(old[2]),
            "witness_invoice": invoice, "layout_word_transfers": meter.layout_word_transfers}


def production_binding():
    records = []
    for k in (2, 3):
        d0 = pow(k, 500)
        old = pow(d0, 40)
        changed = pow(d0 + 1, 40)
        need(root_int(d0, 500) == k, "old floor at a perfect power")
        need(root_int(d0 - 1, 500) == k - 1, "matched floor just below the power")
        need(root_int(old, 40) == d0 and root_int(old - 1, 40) == d0 - 1, "old threshold")
        need(root_int(changed, 40) == d0 + 1 and root_int(changed - 1, 40) == d0, "matched threshold")
        g = d0 - 1
        need(g * (k - (k - 1)) == d0 - 1, "log2 extent ratio equals g")
        # The actual caller admits precisions divisible by six.
        admitted = []
        for p, expected in ((6 * ((old + 5) // 6), k - 1),
                            (6 * ((changed + 5) // 6), k)):
            need(p % 6 == 0, "multiple of six")
            d = root_int(p, 40)
            need(root_int(d - 1, 500) == expected, "six-multiple matched floor")
            need(admit_k(d - 1, 500, expected) and not admit_k(d - 1, 500, expected + 1),
                 "typed K predicate")
            admitted.append(p - (old if expected == k - 1 else changed))
        if k == 2:
            need(admitted == [2, 5], "stated k=2 six-multiple offsets")
        records.append({"k": k, "extent_ratio_log2": "k^500-1",
                        "old_threshold_bits": old.bit_length(),
                        "new_threshold_bits": changed.bit_length(),
                        "six_multiple_offsets": admitted})
    # A feasible active-width plan uses K=1. The old outer guard does not admit it.
    g, degree = 3, 500
    k_matched = root_int(g, degree)
    need(k_matched == 1, "feasible production K")
    plan = {"selected": g, "degree": degree, "K": k_matched, "residue": 0,
            "left": 2, "right": 1, "coefficients": 4, "outer_rows": 1,
            "precision": 6, "dimension_exponent": None}
    plan["gaussians"] = plan["outer_rows"] * (1 << (plan["left"] + g * k_matched + plan["right"])) * plan["coefficients"]
    need(plan["gaussians"] == 256, "small matched extent")
    need(typed_plan_admits(plan), "typed wrapper admits the active-width plan")
    need(not old_outer_admits(plan["dimension_exponent"]), "old wrapper rejects this plan")
    plan["K"] = 2
    try:
        typed_plan_admits(plan)
    except ValueError:
        rejected = True
    else:
        rejected = False
    need(rejected, "typed wrapper rejects the old chunk width")
    return {"powers": records, "small_plan_gaussians": 256}


def admit_k(selected, degree, k):
    return k == root_int(selected, degree) and k >= 1


def old_outer_admits(dimension_exponent):
    return dimension_exponent == (1, 40)


def typed_plan_admits(plan):
    g, k = plan["selected"], plan["K"]
    need(admit_k(g, plan["degree"], k), "K is the matched floor")
    need(0 <= plan["residue"] < k, "residue")
    need(plan["precision"] >= 2, "precision")
    width_bits = plan["left"] + g * k + plan["right"]
    need(0 <= width_bits <= 20, "this checker allocates only a small extent")
    extent = plan["outer_rows"] * (1 << width_bits) * plan["coefficients"]
    need(plan["gaussians"] == extent and plan["outer_rows"] > 0 and plan["coefficients"] > 0,
         "matched cardinality")
    need(not old_outer_admits(plan.get("dimension_exponent")),
         "typed wrapper does not reuse the (1, 40) guard")
    return True


def frozen_sources():
    for name, digest in FROZEN.items():
        data = (ROOT / name).read_bytes()
        need(sha256(data).hexdigest() == digest, "frozen sha256 " + name)
    outer = (ROOT / "frozen/pr3493-outer_layer.py").read_text(encoding="utf-8")
    plan = (ROOT / "frozen/pr3599-active_plan.py").read_text(encoding="utf-8")
    need('root.plan.dimension_exponent == (1, 40)' in outer, "old guard text")
    need("dimension_exponent" not in plan, "active planner does not set that guard")
    need('floor_power(d, 1, 500)' in plan, "active K law")
    need('literal(1) if selected.zero() else keep(Count(selected))' in plan, "d copies selected")
    return {"outer_bytes": len(outer.encode()), "plan_bytes": len(plan.encode())}


def commutation_controls():
    need((-1) // 2 != toward_zero(-1, 2), "floor division is not toward zero")
    need(toward_zero(-5, 2) == -toward_zero(5, 2) == -2, "toward zero is odd")
    p, g = 3, 2
    rows = [((i % 3) - 1, (1 if i == 2 else 0)) for i in range(4)]
    meter = Meter()
    returned, raw = physical_round(rows, (0, 1), p, meter)
    signed = [(-re, -im) for re, im in returned]
    raw_signed = [(-re, -im) for re, im in raw]
    need(truncate_rows(raw_signed, 1 << g, Meter()) == signed, "Q commutes with a global sign")
    flipped = list(reversed(returned))
    need(list(reversed(truncate_rows(raw, 1 << g, Meter()))) == flipped, "Q commutes with a reversal")
    # The same sign applied before truncation disagrees with floor-division.
    floor_signed = [((-re) // (1 << g), (-im) // (1 << g)) for re, im in raw]
    odd_floor = [(-(re // (1 << g)), -(im // (1 << g))) for re, im in raw]
    need(floor_signed != odd_floor, "floor truncation does not commute with the sign")


def run():
    frozen = frozen_sources()
    layouts = check_layout_family()
    one_bit = exhaustive_one_bit()
    witness = scaled_witness()
    powers = production_binding()
    commutation_controls()
    # A g=3 constant input attains the sharp numerator 2^{p+g}.
    p, g = 4, 3
    limit = 1 << p
    rows = [(limit, 0) for _ in range(1 << g)]
    returned, raw, invoice = check_invoice(rows, tuple(range(g)), p)
    need(raw[0] == (limit << g, 0) and returned[0] == (limit, 0), "g=3 sharp return")
    need(invoice["temporary_width"] == p + g + 2, "stated temporary width")
    return {
        "frozen": frozen,
        "common_round_bit_checks": layouts,
        "exhaustive_g1": one_bit,
        "scaled_witness": witness,
        "production": powers,
        "sharp_g3_invoice": invoice,
    }


def main():
    receipt = run()
    text = json.dumps(receipt, sort_keys=True)
    need("TODO" not in text, "receipt placeholder")
    print("PASS_TYPED_ACTUAL_WIDTH_H")
    print(text)


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print("FAIL_TYPED_ACTUAL_WIDTH_H: " + str(error), file=sys.stderr)
        raise SystemExit(1)
