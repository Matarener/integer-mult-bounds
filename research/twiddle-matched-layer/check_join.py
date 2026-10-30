"""Exact bounded checks for the changed outer layout; no physical root replay.

New audit by Clear1nsight with substantial OpenAI assistance, Apache-2.0.
The two imported source modules remain byte-identical and separately credited.
"""

from fractions import Fraction
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def rejected(call, reason):
    try:
        call()
    except ValueError as error:
        need(str(error) == reason, "unexpected rejection reason: " + str(error))
        return reason
    raise ValueError("missing rejection: " + reason)


def root_int(n, degree):
    need(type(n) is int and n >= 0 and degree >= 1, "integer root domain")
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


def integer_digest(n):
    return sha256(n.to_bytes((n.bit_length() + 7) // 8 or 1, "big")).hexdigest()


def floors_and_cost():
    records = []
    for k in (2, 3):
        d0 = pow(k, 500)
        old = pow(d0, 40)
        changed = pow(d0 + 1, 40)
        cases = ((old - 1, k - 1, k - 1), (old, k, k - 1),
                 (changed - 1, k, k - 1), (changed, k, k))
        for p, expect_old, expect_new in cases:
            d = root_int(p, 40)
            need(root_int(d, 500) == expect_old, "old exact-K threshold")
            need(root_int(d - 1, 500) == expect_new, "matched exact-K threshold")
        for p, expected in ((6 * ((old + 5) // 6), k - 1),
                            (6 * ((changed + 5) // 6), k)):
            need(p % 6 == 0, "actual precision multiple")
            need(root_int(root_int(p, 40) - 1, 500) == expected,
                 "actual precision floor boundary")
        records.append({"k": k, "old_threshold_bits": old.bit_length(),
                        "new_threshold_bits": changed.bit_length(),
                        "old_threshold_sha256": integer_digest(old),
                        "new_threshold_sha256": integer_digest(changed),
                        "actual_old_offset": (-old) % 6,
                        "actual_new_offset": (-changed) % 6})
    need(2 ** 39 > 12 * 41 ** 2, "record base inequality")
    need(2 ** 39 * 41 ** 80 > 42 ** 80, "record monotonic ratio")
    ell_min = (2 ** 39 + 11) // 12
    need(ell_min == 45812984491 and ell_min > 32, "actual caller versus executable cap")
    tau = Fraction(99830289, 10 ** 8)
    alpha = Fraction(99827101, 10 ** 8)
    old_bottleneck = Fraction(1, 40 * 500) * (1 - tau)
    new_layer_saving = (1 - alpha) / 40
    need(old_bottleneck == Fraction(169711, 2000000000000), "preserved outer ordinary bill")
    need(new_layer_saving == Fraction(172899, 4000000000), "new layer exponent")
    need(new_layer_saving > old_bottleneck, "outer bottleneck remains narrower")
    return {"thresholds": records, "minimum_nontrivial_ell_lower_bound": ell_min,
            "source_band_integer_checks": 2,
            "exact_K_saving": str(old_bottleneck), "new_layer_saving": str(new_layer_saving)}


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


def bit_at(x, slots, named):
    return (x >> (len(slots) - 1 - slots.index(named))) & 1


def selected(slots, h):
    return tuple(len(slots) - 1 - j for j, item in enumerate(slots) if item[1] == h)


def reorder(data, before, after):
    need(set(before) == set(after), "permutation named domain")
    output = [None] * len(data)
    for x, row in enumerate(data):
        y = 0
        for name in after:
            y = 2 * y + bit_at(x, before, name)
        output[y] = list(row)
    need(all(row is not None for row in output), "complete permutation")
    return output


def h_fast(data, bits):
    result = [list(row) for row in data]
    for bit in bits:
        for x in range(len(result)):
            if (x >> bit) & 1:
                continue
            y = x | (1 << bit)
            left, right = result[x], result[y]
            result[x] = [(a[0] + b[0], a[1] + b[1]) for a, b in zip(left, right)]
            result[y] = [(a[0] - b[0], a[1] - b[1]) for a, b in zip(left, right)]
    return result, 1 << len(bits)


def h_direct(data, bits):
    """Independent explicit tensor matrix, before its 2^g denominator."""
    mask = sum(1 << bit for bit in bits)
    result = []
    for x in range(len(data)):
        row = [(0, 0) for _ in data[0]]
        for choice in range(1 << len(bits)):
            y = x & ~mask
            for j, bit in enumerate(bits):
                y |= ((choice >> j) & 1) << bit
            sign = -1 if ((x & y & mask).bit_count() % 2) else 1
            row = [(a[0] + sign * b[0], a[1] + sign * b[1])
                   for a, b in zip(row, data[y])]
        result.append(row)
    return result, 1 << len(bits)


def truncate(data, denominator):
    def part(v):
        return (1 if v >= 0 else -1) * (abs(v) // denominator)
    return [[(part(a), part(b)) for a, b in row] for row in data]


def exponent(x, slots, ell, flags, h, opposite=False):
    value = 0
    for i, long in enumerate(flags):
        if h >= ell - (not long):
            continue
        branch = bit_at(x, slots, (i, h))
        low = sum((1 << v) * bit_at(x, slots, (i, v)) for v in range(h))
        value += branch * low
    return ((1 if opposite else -1) * (1 << (ell - h)) * value) % (2 << ell)


def rotate(row, e):
    r = len(row)
    output = [None] * r
    for j, (a, b) in enumerate(row):
        quotient, destination = divmod(j + e, r)
        sign = -1 if quotient % 2 else 1
        output[destination] = (sign * a, sign * b)
    return output


def diagonal(data, slots, ell, flags, h, opposite=False):
    return [rotate(row, exponent(x, slots, ell, flags, h, opposite))
            for x, row in enumerate(data)]


def reference_round(data, slots, ell, flags, h, opposite=False):
    if opposite:
        data = diagonal(data, slots, ell, flags, h, True)
    raw, denominator = h_direct(data, selected(slots, h))
    if not opposite:
        raw = diagonal(raw, slots, ell, flags, h)
    return truncate(raw, denominator)


def caller_round(data, slots, ell, flags, k, h, opposite=False):
    g, a = len(flags), sum(flags)
    b, q = (ell - 1) % k, (ell - 1) // k
    if b <= h < ell - 1:
        j, rho = (ell - 2 - h) // k, (h - b) % k
        left, right = a + g * b + j * g * k, (q - j - 1) * g * k
        need(left + g * k + right == len(slots), "complete root extent")
        bits = tuple(right + rho + t * k for t in range(g))
        need(set(bits) == set(selected(slots, h)), "literal root selected positions")
    else:
        bits = selected(slots, h)
    if opposite:
        data = diagonal(data, slots, ell, flags, h, True)
    raw, denominator = h_fast(data, bits)
    result = truncate(raw, denominator)
    if not opposite:
        result = diagonal(result, slots, ell, flags, h)
    return result


def cube_checks():
    cases = ((2, (False,), 1), (2, (True,), 1),
             (3, (False, False), 1), (3, (True, False), 1),
             (3, (True, True), 1), (3, (False, False, False), 1),
             (3, (True, False, True), 1),
             (3, (False, False, False, False), 2),
             (3, (True, False, False, False), 2),
             (4, (True, False), 2))
    results = []
    for ell, flags, k in cases:
        original, physical = slots_for(ell, flags, k)
        m, r = 1 << len(original), 1 << ell
        cube = [[((17 * x + 5 * j + 3) % 7 - 3, (11 * x + 7 * j + 2) % 7 - 3)
                 for j in range(r)] for x in range(m)]
        levels = list(range(ell - 2, -1, -1))
        if any(flags):
            levels.insert(0, ell - 1)
        b, q = (ell - 1) % k, (ell - 1) // k
        need(len(levels) == ell - 1 + int(any(flags)), "complete round count")
        need(sum(b <= h < ell - 1 for h in levels) == q * k, "common root invocation count")
        need(sum(len(selected(original, h)) for h in levels if h < b or h == ell - 1)
             == sum(flags) + len(flags) * b, "prefix singleton inventory")
        checked = 0
        for opposite in (False, True):
            reference = cube
            actual = reorder(cube, original, physical)
            for h in reversed(levels) if opposite else levels:
                reference = reference_round(reference, original, ell, flags, h, opposite)
                actual = caller_round(actual, physical, ell, flags, k, h, opposite)
                need(actual == reorder(reference, original, physical), "complete repaired round")
                need(all(a * a + b0 * b0 <= 16 ** 2 for row in actual for a, b0 in row),
                     "complete-round disk return for p=4")
                checked += 1
        results.append({"ell": ell, "long_axes": list(flags), "declared_layout_K": k,
                        "records": m, "coefficients": r, "complete_round_comparisons": checked,
                        "common_calls_each_direction": q * k,
                        "prefix_individual_sweeps_each_direction": sum(flags) + len(flags) * b})
    return results


def controls():
    ell, flags = 3, (False, False, False)
    original, old = slots_for(ell, flags, 2)
    _, new = slots_for(ell, flags, 1)
    a = len(original)
    need(a == 6 and 3 * 1 != a, "old descriptor extent must disagree")
    impulse = [[(int(x == 0 and j == 0), 0) for j in range(1 << ell)]
               for x in range(1 << a)]
    # Scale by eight so the final truncation cannot hide the selected-bit error.
    impulse[0][0] = (8, 0)
    intended, den = h_fast(impulse, (0, 2, 4))
    concealed, bad_den = h_fast(impulse, (0, 1, 2))
    intended, concealed = truncate(intended, den), truncate(concealed, bad_den)
    need(intended[2][0] == (0, 0) and concealed[2][0] == (1, 0), "wrong-root endpoint witness")
    need(reorder(impulse, original, new) == impulse, "impulse origin invariant")
    nonconstant = [[(x + j, 0) for j in range(1 << ell)] for x in range(1 << a)]
    mapped = reorder(nonconstant, original, new)
    need(reorder(mapped, old, original) != nonconstant, "old inverse layout control")
    bad_offset, _ = h_fast(impulse, (1, 2, 3))
    good_offset, _ = h_fast(impulse, (0, 1, 2))
    need(bad_offset != good_offset, "offset control")
    # Inverse order matters even though rounding commutes with the diagonal.
    small_slots, _ = slots_for(2, (True,), 1)
    one = [[(0, 0)] * 4 for _ in range(4)]
    one[3][0] = (4, 0)
    correct = reference_round(one, small_slots, 2, (True,), 1, True)
    raw, d = h_fast(one, selected(small_slots, 1))
    wrong = diagonal(truncate(raw, d), small_slots, 2, (True,), 1, True)
    need(correct != wrong, "inverse round order control")
    need((-1) // 2 != -(1 // 2), "floor rounding is not odd")
    need(truncate([[(-1, 1)]], 2) == [[(0, 0)]], "toward-zero control")
    p = 4
    need(2 ** p > 2 ** ((p + 1) - 1) - 1, "p+1 misses positive disk endpoint")
    need(-(2 ** (p + 1)) < -(2 ** p), "signed minimum outside caller disk")
    return {"old_extent_bits": a, "wrong_active_extent_bits": 3,
            "concealed_extent_witness_address": 2,
            "correct_value": [0, 0], "wrong_value": [1, 0],
            "rejected_failures": ["old chunk extent", "concealed extent wrong tensor",
                                  "old inverse layout", "wrong offset", "inverse round order",
                                  "floor rounding", "short signed format"]}


def load_frozen(name, filename, expected_blob):
    path = HERE / filename
    data = path.read_bytes()
    blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    need(blob == expected_blob, "frozen source bytes: " + filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, {"path": filename, "git_blob": blob, "sha256": sha256(data).hexdigest()}


def actual_packet_boundary():
    producer, pp = load_frozen("audited_pr3593", "pr3593-controller.py", "2e72164d9429baeb1b18621f6f4b9576dbcc60a4")
    consumer, cp = load_frozen("audited_pr3611", "pr3611-consumer.py", "d916056a4ae22d668ad3269ba881e4f518e982ab")
    cap_controls = [rejected(lambda: producer.encode(33, 1, 0, (True,)), "bad ell"),
                    rejected(lambda: consumer.Consumer(33, 6), "allocation ell")]
    ell, flags, k, h, p = 3, (False, False, False), 1, 1, 4
    original, physical = slots_for(ell, flags, k)
    address = (1, 0, 0, 1, 0, 0)
    x = int("".join(map(str, address)), 2)
    r, w = 1 << ell, p + 2
    cube = []
    for index in range(1 << len(original)):
        sign = -1 if bit_at(index, original, (0, h)) else 1
        cube.append([(sign * (j % 3 + 1), sign * (1 - j % 3)) for j in range(r)])
    raw, denominator = h_fast(reorder(cube, original, physical), selected(physical, h))
    complete_h = truncate(raw, denominator)
    packet = complete_h[x]
    need(any(a or b for a, b in packet), "nonzero complete-H packet")
    before_packet = packet
    receipts = []
    for opposite in (False, True):
        descriptor = producer.encode(ell, k, h, flags, opposite)
        ctrl = producer.Controller(descriptor, address)
        ctrl.execute()
        expected_e = exponent(x, physical, ell, flags, h, opposite)
        actual_e = int("".join(map(str, ctrl.data["output"].cells)), 2)
        need(actual_e == expected_e, "actual emitted matched-layout exponent")
        prod_snapshot = ctrl.invoice()
        prod_cost = (sum(sum(v.values()) for v in prod_snapshot["data"].values())
                     + prod_snapshot["control_tape_actions"] + prod_snapshot["descriptor_actions"]
                     + sum(prod_snapshot["gates"].values()))
        producer_bound = 5000 * (len(address) + ell + 1) ** 2 * (ell + k + h + len(flags) + 10)
        need(prod_cost <= producer_bound, "actual producer tariff")
        bits = [int(bit) for pair in packet for value in pair
                for bit in format(value % (1 << w), "0%db" % w)]
        source = consumer.Tape(["^"] + bits + ["$"])
        width = consumer.Tape(["^"] + ["1"] * w + ["$"])
        module = consumer.Consumer(ell, w)
        borrowed = (ctrl.data["output"], ctrl.descriptor, width, source)
        snapshots = [(list(t.cells), t.head) for t in borrowed]
        observed_tapes = tuple(module.tapes.values()) + borrowed
        counts_before = [sum(t.counts.values()) for t in observed_tapes]
        result = module.run(*borrowed)
        need([(list(t.cells), t.head) for t in borrowed] == snapshots, "actual borrow return")
        output_bits = result.cells[1:1 + 2 * r * w]
        values = []
        for j in range(0, len(output_bits), w):
            v = int("".join(map(str, output_bits[j:j + w])), 2)
            values.append(v - (1 << w) if v >> (w - 1) else v)
        packet = list(zip(values[::2], values[1::2]))
        need(packet == rotate(before_packet if not opposite else receipts[-1]["packet"], expected_e),
             "actual packet endpoint")
        need(all(not any(module.tapes[role].cells) and module.tapes[role].head == 0
                 for role in ("prefix", "suffix", "word", "a", "b")), "actual private return")
        consumer_cost = sum(module.invoice.values())
        observed_cost = sum(sum(t.counts.values()) - old for t, old in zip(observed_tapes, counts_before))
        observed_cost += sum(module.gates.values())
        need(consumer_cost == observed_cost, "independent shared-role action reconciliation")
        need(consumer_cost <= 256 * (2 * r * w + ell + w + 1), "actual consumer tariff")
        rearm_control = rejected(lambda: module.run(*borrowed), "one-shot consumer")
        need([(list(t.cells), t.head) for t in borrowed] == snapshots, "one-shot rejection preserves borrows")
        receipts.append({"opposite": opposite, "exponent": actual_e, "producer_tariff": prod_cost,
                         "producer_tariff_bound": producer_bound, "consumer_tariff": consumer_cost,
                         "consumer_actions_independently_reconciled": observed_cost,
                         "used_object_rejection": rearm_control, "packet": packet})
    need(packet == before_packet, "actual opposite packet return")
    wrong = producer.Controller(producer.encode(ell, 2, h, flags), address)
    wrong.execute()
    wrong_e = int("".join(map(str, wrong.data["output"].cells)), 2)
    need(wrong_e != receipts[0]["exponent"], "old-K actual header must differ")
    return {"source_pins": [pp, cp], "arithmetic_H_only": True,
            "whole_physical_root_or_diagonal_pass_executed": False,
            "matched_layout_address": x, "wrong_K_exponent": wrong_e, "source_cap_rejections": cap_controls,
            "actual_single_packet_calls": receipts}


def run():
    return {"scope": "source-relative matched outer layout; bounded arithmetic and two actual single-packet joins",
            "floor_and_cost": floors_and_cost(), "complete_cube_checks": cube_checks(),
            "controls": controls(), "actual_interface": actual_packet_boundary()}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
