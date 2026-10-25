#!/usr/bin/env python3
"""Exact request-window price and dirty-state witnesses. Apache-2.0.

Yuzhou Wang, with substantial OpenAI Codex assistance. Standard library only.
Normal replay is read-only; --write-receipt exclusively creates RESULT.json.
"""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    count = 0
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                "source SHA256 mismatch: " + row["path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git blob mismatch: " + row["path"])
        count += 1
    return count


def validate(windows, prices, readers):
    require(len(prices) >= 1, "at least one source-call slot is required")
    require(len(windows) == len(readers), "reader/window count mismatch")
    require(all(type(x) in (int, Fraction) and x > 0
                for x in (*prices, *readers)), "positive exact prices required")
    for lo, hi in windows:
        require(type(lo) is int and type(hi) is int and
                0 <= lo <= hi < len(prices), "invalid window")


def optimize(windows, prices, readers):
    """Scan slots; state is (last selected slot, source-call parity).

    Two B calls at one slot can deliver an output and restore the connector.
    Paths are retained for reproducible ties, not for an optimal space bound.
    """
    validate(windows, prices, readers)
    due = [-1] * len(prices)
    for lo, hi in windows:
        due[hi] = max(due[hi], lo)
    states = {(-1, 0): (Fraction(0), ())}
    for slot, price in enumerate(prices):
        nxt = {}
        for (last, parity), (cost, counts) in states.items():
            for number in (0, 1, 2):
                new_last = slot if number else last
                if new_last < due[slot]:
                    continue
                key = (new_last, parity ^ (number & 1))
                candidate = (cost + number * price, counts + (number,))
                if key not in nxt or candidate < nxt[key]:
                    nxt[key] = candidate
        states = nxt
    cost, counts = min(value for (_, parity), value in states.items() if parity == 0)
    return cost + 2 * sum(readers), counts


def brute_price(windows, prices, readers):
    """Direct finite multiset oracle, independent of the scan recurrence."""
    candidates = []
    for counts in itertools.product(range(3), repeat=len(prices)):
        if sum(counts) % 2 or any(not any(counts[lo:hi+1]) for lo, hi in windows):
            continue
        candidates.append((sum(n*b for n, b in zip(counts, prices)), counts))
    cost, counts = min(candidates)
    return cost + 2 * sum(readers), counts


def hitting_number(windows):
    """Standard earliest-right-endpoint interval stabbing; not a new algorithm."""
    last, number = -1, 0
    for lo, hi in sorted(windows, key=lambda w: (w[1], w[0])):
        if last < lo:
            last = hi
            number += 1
    return number


def emit(windows, counts):
    assigned = [[] for _ in counts]
    for i, (lo, hi) in enumerate(windows):
        slot = next(t for t in range(lo, hi + 1) if counts[t])
        assigned[slot].append(i)
    events = []
    for t, n in enumerate(counts):
        if n:
            events += [(t, "A", i) for i in assigned[t]]
            events.append((t, "B", -1))
            events += [(t, "A", i) for i in assigned[t]]
            events += [(t, "B", -1)] * (n - 1)
    return events


def check_abstract(windows, prices, readers, events):
    """Formal x/z0 coefficients, with every deadline and write window checked."""
    validate(windows, prices, readers)
    by_slot = [[] for _ in prices]
    previous = -1
    cost = Fraction(0)
    for t, kind, i in events:
        require(type(t) is int and 0 <= t and previous <= t < len(prices), "event time/order")
        require(kind in ("A", "B"), "invalid event")
        by_slot[t].append((kind, i))
        previous = t
    z, y = 2, [0] * len(windows)  # bits: x, z0; output dirt implicit
    for t, block in enumerate(by_slot):
        for kind, i in block:
            if kind == "B":
                require(i == -1, "B index")
                z ^= 1
                cost += prices[t]
            else:
                require(type(i) is int and 0 <= i < len(windows), "A index")
                require(windows[i][0] <= t <= windows[i][1], "write outside window")
                y[i] ^= z
                cost += readers[i]
        for i, (_, hi) in enumerate(windows):
            if hi == t:
                require(y[i] == 1, "wrong delivered output")
    require(z == 2, "unrestored connector")
    return cost


def xor_all(values):
    result = 0
    for value in values:
        result ^= value
    return result


def matrix_product(a, b):
    return tuple(xor_all(b[j] for j in range(len(b)) if row >> j & 1) for row in a)


def scalar_gates(events, b, aa):
    d = len(b)
    gates = []
    for t, kind, i in events:
        matrix = b if kind == "B" else aa[i]
        source = 0 if kind == "B" else d
        target = d if kind == "B" else (2 + i) * d
        for row, mask in enumerate(matrix):
            for col in range(d):
                if mask >> col & 1:
                    gates.append((t, source + col, target + row))
    return gates


def check_scalar(windows, b, aa, events):
    """Exact linear map on every dirty column at every output deadline."""
    d = len(b)
    size = (2 + len(windows)) * d
    rows = [1 << i for i in range(size)]
    expected = rows[:]
    for i, a in enumerate(aa):
        for r, mask in enumerate(matrix_product(a, b)):
            expected[(2+i)*d+r] ^= mask
    gates = scalar_gates(events, b, aa)
    m = max(hi for _, hi in windows) + 1
    for slot in range(m):
        for t, s, dest in gates:
            if t == slot:
                require(s != dest, "aliased scalar gate")
                rows[dest] ^= rows[s]
        for i, (_, hi) in enumerate(windows):
            if hi == slot:
                sl = slice((2+i)*d, (3+i)*d)
                require(rows[sl] == expected[sl], "literal delivery failure")
    require(rows == expected, "literal dirty-state endpoint failure")
    return {"data_bits": size, "xor_writes": len(gates), "reads": 2*len(gates),
            "head_steps": sum(2*max(s,t) for _, s, t in gates),
            "read_latch_resets": len(gates)+1,
            "fixed_width_program_bits": 13*len(gates) if size == 24 else None,
            "program_records": len(gates),
            "map_sha256": digest(rows), "events_sha256": digest(events)}


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def cases():
    for m in range(1, 5):
        intervals = [(lo, hi) for hi in range(m) for lo in range(hi + 1)]
        for k in range(4):
            for windows in itertools.combinations_with_replacement(intervals, k):
                for prices in itertools.product((1, 3), repeat=m):
                    yield windows, prices, tuple(1 + i % 2 for i in range(k))


def reject(operation):
    try:
        operation()
    except (ValueError, StopIteration):
        return
    raise ValueError("negative control accepted")


def result():
    pins = authenticate()
    records = []
    for windows, prices, readers in cases():
        price, counts = optimize(windows, prices, readers)
        require((price, counts) == brute_price(windows, prices, readers), "multiset oracle disagreement")
        require(check_abstract(windows, prices, readers, emit(windows, counts)) == price, "invoice")
        tau = hitting_number(windows)
        uniform, _ = optimize(windows, (2,) * len(prices), readers)
        require(uniform == 2*sum(readers) + 4*((tau+1)//2), "uniform corollary")
        records.append([windows, prices, readers, str(price), counts])
    windows = tuple((i, i + 1) for i in range(6))
    b = (3, 6, 7)
    aa = tuple((1, 2, 4) if i % 2 == 0 else (3, 2, 4) for i in range(6))
    readers = tuple(sum(row.bit_count() for row in a) for a in aa)
    price, counts = optimize(windows, (7,)*7, readers)
    events = emit(windows, counts)
    closed = []
    for i, (_, hi) in enumerate(windows):
        closed += [(hi, "A", i), (hi, "B", -1), (hi, "A", i), (hi, "B", -1)]
    pilot = check_scalar(windows, b, aa, events)
    baseline = check_scalar(windows, b, aa, closed)
    disjoint_windows = tuple((hi, hi) for _, hi in windows)
    disjoint_price, disjoint_counts = optimize(disjoint_windows, (7,)*7, readers)
    disjoint_word = emit(disjoint_windows, disjoint_counts)
    disjoint = check_scalar(disjoint_windows, b, aa, disjoint_word)
    require(pilot["xor_writes"] == price == 70, "pilot expected count")
    require(baseline["xor_writes"] == 126, "baseline expected count")
    require(disjoint_price == disjoint["xor_writes"] == 84, "PR1442 comparator")
    require(pilot["map_sha256"] == baseline["map_sha256"], "pilot map mismatch")
    require(pilot["map_sha256"] == disjoint["map_sha256"], "disjoint map mismatch")
    small_windows = ((0, 1), (1, 2), (2, 3))
    _, small_counts = optimize(small_windows, (1,)*4, (1,)*3)
    small_word = emit(small_windows, small_counts)
    matrices = tuple(itertools.product(range(4), repeat=2))
    matrix_checks = 0
    for bm, a0, a1 in itertools.product(matrices, repeat=3):
        check_scalar(small_windows, bm, (a0, a1, (2, 1)), small_word)
        matrix_checks += 1
    wa, bp, ap = ((0, 0), (1, 1)), (1, 1), (1, 1)
    good = emit(wa, (1, 1))
    require(check_abstract(wa, bp, ap, good) == 6, "control fixture")
    controls = [
        lambda: check_abstract(wa, bp, ap, [(0,"A",1),(0,"A",1)] + good),
        lambda: check_abstract(wa, bp, ap, good + [(1,"A",0),(1,"A",0)]),
        lambda: check_abstract(((0,0),), (1,), (1,), [(0,"A",0),(0,"B",-1),(0,"A",0)]),
        lambda: check_abstract(wa, bp, ap, [e for e in good if e != (0,"A",0)]),
        lambda: optimize(((0,2),), (1,1), (1,)),
        lambda: optimize(((0,0),), (0,), (1,)),
        lambda: optimize(((0,0),), (1.0,), (1,)),
    ]
    for control in controls:
        reject(control)
    require(hitting_number(((0,0),)) == 1 and optimize(((0,0),), (5,), (1,))[0] == 12, "parity matters")
    require(optimize(((0,1),(1,2)), (1,9,1), (1,1)) == (6, (1,0,1)), "weighted fixture")
    return {"schema_version": 1, "domain_cases": len(records), "domain_digest": digest(records),
            "cost_digest": digest([row[:-1] for row in records]),
            "source_pins": pins, "literal_matrix_cases": matrix_checks,
            "semantic_rejections": len(controls),
            "odd_transversal_control": {"tau": 1, "source_calls": 2},
            "weighted_fixture": {"windows": [[0,1],[1,2]], "b": [1,9,1],
                                 "a": [1,1], "cost": 6, "counts": [1,0,1]},
            "pilot": {"windows": windows, "counts": counts, "events": events,
                      "B": b, "A": aa, "persistent": pilot, "closed": baseline,
                      "disjoint_persistent": disjoint, "disjoint_events": disjoint_word},
            "claim": "Exact generic complete-query optimum; no physical supplier or kappa"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    receipt = result()
    encoded = json.dumps(receipt, indent=2) + "\n"
    if args.write_receipt:
        with (HERE / "RESULT.json").open("x", encoding="utf-8") as out:
            out.write(encoded)
    else:
        require(json.loads((HERE / "RESULT.json").read_text()) == json.loads(encoded), "RESULT.json mismatch")
    print("PASS_CONNECTOR_OVERLAPPING_WINDOWS cases=%d matrices=%d controls=%d XORs=126/84->70 kappa=unchanged" %
          (receipt["domain_cases"], receipt["literal_matrix_cases"], receipt["semantic_rejections"]))


if __name__ == "__main__":
    main()
