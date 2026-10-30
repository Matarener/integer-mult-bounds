"""One frozen finite pilot. No warmups, searches, automatic retries or science imports."""
from __future__ import annotations
import time
_COLD_WALL_START = time.perf_counter()
import resource

def process_and_child_cpu():
    own = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime

_COLD_CPU_START = process_and_child_cpu()
import argparse
from array import array
from collections import deque
import hashlib
import json
from pathlib import Path
import struct
import sys
import traceback
from load_pilot import ROOT, compile_and_load, verify_sources

EVENTS = 32768
LOOKUPS_PER_EVENT = 80
KEYS_PER_EVENT = 10
REPETITIONS = 8
CALLS = EVENTS * LOOKUPS_PER_EVENT
CAPACITY = 16384
ACTUAL_CALLS = 2579750
ORDER = (("B1", 0), ("C1", 1), ("C2", 1), ("B2", 0))
BASELINE = {"wall": 34.66178539200337, "cpu": 34.47}
INTEGER_GROSS = {"wall": 4.684712576272432, "cpu": 4.683428714999984}
RESERVE = {"wall": 0.5, "cpu": 0.5}


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def literal_oracle(rows, capacity):
    """Independent ordinary dict + deque, no C/custom hash or shared lookup code."""
    cache = {}
    fifo = deque()
    ids = []
    flags = bytearray()
    prefixes = []
    hits = misses = evictions = 0
    for i, key in enumerate(rows, 1):
        value = cache.get(key)
        flag = 0
        if value is not None:
            hits += 1
        else:
            misses += 1
            value = misses
            flag = 1
            if len(fifo) == capacity:
                del cache[fifo.popleft()]
                evictions += 1
                flag |= 2
            cache[key] = value
            fifo.append(key)
        ids.append(value)
        flags.append(flag)
        if i % LOOKUPS_PER_EVENT == 0 or i == len(rows):
            prefixes.append((i, hits, misses, evictions, len(cache)))
    stats = dict(calls=len(rows), hits=hits, misses=misses, evictions=evictions,
                 resident=len(cache), capacity=capacity)
    return tuple(ids), bytes(flags), tuple(prefixes), stats


def assert_equal(actual, expected, mode):
    if type(actual) is not tuple or len(actual) != 4:
        raise AssertionError("malformed output packet")
    # Full sequence comparisons; hashes never substitute for equality.
    for index, name in ((0, "ordered IDs"), (1, "ordered hit/miss/eviction flags"),
                        (2, "all 80-operation prefixes")):
        if actual[index] != expected[index]:
            raise AssertionError(f"mismatched {name}")
    actual_stats = dict(actual[3])
    rehashes = actual_stats.pop("rehashes", None)
    if type(rehashes) is not int or rehashes < 0 or actual_stats != expected[3]:
        raise AssertionError("mismatched counters or rehash metadata")
    if mode == 0 and rehashes != 0:
        raise AssertionError("baseline must report zero custom rehashes")


def retain_full(destination, name, result):
    ids = array("Q", result[0])
    if ids.itemsize != 8:
        raise RuntimeError("Q output format is not 64 bits on this interpreter")
    id_path = destination / (name + "-ids.u64")
    with id_path.open("wb") as stream:
        ids.tofile(stream)
    flag_path = destination / (name + "-flags.u8")
    flag_path.write_bytes(result[1])
    prefix_path = destination / (name + "-prefixes.json")
    write_json(prefix_path, result[2])
    return {"ids": id_path.name, "flags": flag_path.name,
            "prefixes": prefix_path.name, "id_byteorder": sys.byteorder,
            "id_itemsize": ids.itemsize, "calls": len(result[0]),
            "stats": result[3],
            "ids_sha256": hashlib.sha256(ids.tobytes()).hexdigest(),
            "flags_sha256": hashlib.sha256(result[1]).hexdigest()}


def clone_key(key):
    # int(existing_int) may preserve object identity; decimal construction avoids
    # that for non-interned values. Small immortal/cached ints may still be shared.
    return tuple(int(str(field)) for field in key)


def finite_key(i):
    return (i * 2 + 10001, 2, -3, 4, -i * 2 - 10001, 8, i % 3587)


def tracked_objects(rows):
    unique = {id(rows): rows}
    for row in rows:
        unique[id(row)] = row
        for field in row:
            # Small cached integers can acquire legitimate references from the
            # retained counter/ID receipts, so they cannot diagnose key leaks.
            if not -5 <= field <= 256:
                unique[id(field)] = field
    return list(unique.values())


def refs(objects):
    return tuple(sys.getrefcount(obj) for obj in objects)


def finite_controls(module):
    receipts = []
    p = sys.hash_info.modulus
    collision_keys = tuple((p*i, -p*i, p*(i+1), 1, 0, 1, p*(i+2)) for i in range(1, 21))
    if len({hash(key) for key in collision_keys}) != 1:
        raise AssertionError("declared exact-PyLong and tuple hash collision construction failed")
    a = finite_key(1)
    a_equal = clone_key(a)
    if a_equal != a or a_equal[0] is a[0]:
        raise AssertionError("distinct numerically equal key control failed")
    big = (1 << 8191) + 73
    broad = ((0, 0, 0, 0, 0, 0, 0),
             (-1, 1, -2, 2, -3, 3, -4),
             (big, -big, big-1, 1, -big+1, 2, 3586))
    cases = [
        ("empty", (), 1),
        ("numeric-equality-and-no-FIFO-refresh", (a, finite_key(2), a_equal,
             finite_key(3), a_equal, finite_key(2)), 2),
        ("signed-zero-8192-bit", broad + tuple(clone_key(k) for k in broad), 3),
        ("full-hash-and-table-collisions", collision_keys + collision_keys[5:]
             + tuple(clone_key(k) for k in collision_keys), 16),
        ("capacity-one", tuple(finite_key(i) for i in range(40)), 1),
        ("tombstone-rehash-turnover", tuple(finite_key(i) for i in range(512))
             + tuple(finite_key(i) for i in range(480, 512)), 16),
        ("full-capacity-turnover", tuple(finite_key(i) for i in range(16416))
             + tuple(finite_key(i) for i in range(16390, 16416)), 16384),
    ]
    natural_rehashes = 0
    for name, rows, cap in cases:
        expected = literal_oracle(rows, cap)
        tracked = tracked_objects(rows)
        before = refs(tracked)
        for mode in (0, 1):
            actual = module.run(mode, rows, cap)
            assert_equal(actual, expected, mode)
            if mode == 1:
                natural_rehashes += actual[3]["rehashes"]
            receipts.append({"control": name, "mode": mode, "stats": actual[3],
                             "ordered_ids": actual[0], "ordered_flags": list(actual[1]),
                             "prefixes": actual[2], "full_equality": True})
            del actual
            if refs(tracked) != before:
                raise AssertionError(f"reference leak on success: {name}/{mode}")
    if natural_rehashes < 1:
        raise AssertionError("finite controls never exercised natural rehash")

    class IntSubclass(int):
        def __hash__(self):
            raise AssertionError("subclass hash must never run")
        def __eq__(self, other):
            raise AssertionError("subclass comparison must never run")
    class TupleSubclass(tuple):
        pass
    bad_calls = [
        (False, (a,), 2), (2, (a,), 2), (0, (a,), True),
        (0, (a,), IntSubclass(2)), (0, (a,), 0), (0, (a,), -1),
        (0, (a,), 16385), (0, (a,), 1 << 100),
        (0, [a], 2), (0, TupleSubclass((a,)), 2),
        (0, (a[:-1],), 2), (0, (a + (1,),), 2),
        (0, (list(a),), 2), (0, (TupleSubclass(a),), 2),
        (0, ((True,) + a[1:],), 2),
        (0, ((IntSubclass(a[0]),) + a[1:],), 2),
        (0, ((object(),) + a[1:],), 2), (0, ((1.5,) + a[1:],), 2),
        (0, (("1",) + a[1:],), 2), (0, ((None,) + a[1:],), 2),
        (0, (a,), 2, True, 1), (0, (a,), 2, 0, True),
        (0, (a,), 2, -2, 1), (0, (a,), 2, 0, 7),
        (0, (a,), 2, -1, 1), (0, (a,), 2, 0, 0),
        (0, (a,), 2, 1, 1), (0, (a,), 2, 0, 6),
    ]
    for index, args in enumerate(bad_calls):
        # Type/capacity/row rejection is shared prevalidation, but check both arms
        # whenever the explicit test does not itself target the mode selector.
        modes = (None,) if index < 2 else (0, 1)
        for mode in modes:
            packet = args if mode is None else (mode,) + args[1:]
            if index == len(bad_calls)-1 and mode == 1:
                continue  # phase 6 is a supported custom-only cleanup hook.
            try:
                module.run(*packet)
            except (TypeError, ValueError, OverflowError):
                receipts.append({"rejection": index, "mode": mode, "rejected": True})
            else:
                raise AssertionError(f"malformed packet accepted: {index}/{mode}")
    fault_rows = tuple(finite_key(i) for i in range(8))
    tracked = tracked_objects(fault_rows)
    before = refs(tracked)
    for mode in (0, 1):
        for phase in range(1, 7 if mode else 6):
            try:
                module.run(mode, fault_rows, 2, 4, phase)
            except MemoryError:
                pass
            else:
                raise AssertionError(f"declared fault did not fire: {mode}/{phase}")
            if refs(tracked) != before:
                raise AssertionError(f"reference leak after failure: {mode}/{phase}")
            receipts.append({"cleanup_fault_mode": mode, "phase": phase,
                             "raised_MemoryError": True, "reference_counts_equal": True})
    hit_rows = (a, a_equal, a, a_equal)
    tracked = tracked_objects(hit_rows)
    before = refs(tracked)
    for mode in (0, 1):
        for phase in (1, 5):
            try:
                module.run(mode, hit_rows, 2, 2, phase)
            except MemoryError:
                pass
            else:
                raise AssertionError(f"declared hit fault did not fire: {mode}/{phase}")
            if refs(tracked) != before:
                raise AssertionError(f"reference leak after hit failure: {mode}/{phase}")
            receipts.append({"cleanup_hit_fault_mode": mode, "phase": phase,
                             "raised_MemoryError": True, "reference_counts_equal": True})
    return {"status": "PASS_FINITE_KEY_ONLY", "receipts": receipts,
            "natural_rehashes": natural_rehashes,
            "allocator_failures_exhaustive": False}


def timed_corpus():
    rows = []
    qs = ((-3, 1), (-1, 2), (0, 1), (1, 1), (3, 2), (1, 4), (5, 8))
    for event in range(EVENTS):
        qn, qd = qs[event % len(qs)]
        first = []
        second = []
        for offset in range(KEYS_PER_EVENT):
            serial = event * KEYS_PER_EVENT + offset
            old_num = (serial * 2 + 1) * (-1 if serial % 2 else 1)
            old_den = 1 << (serial % 13)
            v_num = 0 if serial % 19 == 0 else (2*(serial % 511)+1) * (-1 if serial % 3 == 0 else 1)
            v_den = 1 if v_num == 0 else 1 << ((serial // 13) % 9)
            key = (old_num, old_den, qn, qd, v_num, v_den, serial % 3587)
            first.append(key)
            second.append(clone_key(key))
        for repeat in range(REPETITIONS):
            rows.extend(first if repeat % 2 == 0 else second)
    if len(rows) != CALLS:
        raise AssertionError("frozen work-unit count mismatch")
    return tuple(rows)


def optimistic_screen(samples):
    indexed = {sample["name"]: sample for sample in samples}
    result = {"interpretation": "ILLUSTRATIVE_OPTIMISTIC_SCREEN_ONLY",
              "measured_complete_saving": False, "construction_admitted": False,
              "integer_residual_assumed_seconds": 0,
              "new_bill_reserve_measured": False, "actual_calls_for_illustration": ACTUAL_CALLS,
              "real_integer_residual": "UNPRICED_NONZERO",
              "complete_new_validation_build_bill": "UNPRICED_NONZERO",
              "diagnostic_integer_regions_include_clock_overhead": True}
    gates = []
    for metric in ("wall", "cpu"):
        deltas = [indexed["B1"][metric] - indexed["C1"][metric],
                  indexed["B2"][metric] - indexed["C2"][metric]]
        smaller = min(deltas)
        per_call = smaller / CALLS
        illustrative = per_call * ACTUAL_CALLS
        optimistic = INTEGER_GROSS[metric] + illustrative - RESERVE[metric]
        threshold = BASELINE[metric] * 0.15
        gate = optimistic >= threshold
        gates.append(gate)
        result[metric] = {"paired_gross_seconds": deltas,
                          "smaller_paired_gross_seconds": smaller,
                          "synthetic_gross_seconds_per_call": per_call,
                          "illustrative_key_saving_at_actual_calls": illustrative,
                          "diagnostic_integer_gross_region": INTEGER_GROSS[metric],
                          "provisional_new_bill_reserve": RESERVE[metric],
                          "optimistic_budget_seconds": optimistic,
                          "necessary_15pct_threshold_seconds": threshold,
                          "necessary_threshold_met": gate}
    result["status"] = ("HEADROOM_FOR_SOURCE_SPECIFIC_COST_DESIGN_ONLY" if all(gates)
                        else "REJECT_THIS_OPTIMISTIC_NOMINATION")
    return result


def main(destination):
    if destination.exists():
        raise RuntimeError("fresh output directory required; no answer/build reuse")
    destination.mkdir(parents=True)
    report = {"status": "STARTED", "scope": "finite synthetic key-only comparator",
              "source_only_preparation_precedes_parent_run": True,
              "performance_publication": False, "construction_admitted": False,
              "frozen_order": [name for name, _ in ORDER], "calls_per_sample": CALLS,
              "events": EVENTS, "lookups_per_event": LOOKUPS_PER_EVENT,
              "capacity": CAPACITY, "samples": [], "automatic_retries": 0}
    write_json(destination / "RESULT.json", report)
    try:
        report["source_manifest"] = verify_sources()
        module, report["build"] = compile_and_load(destination)
        controls = finite_controls(module)
        write_json(destination / "FINITE-CONTROLS.json", controls)
        report["finite_controls"] = controls["status"]
        rows = timed_corpus()
        corpus_hash = hashlib.sha256()
        for row in rows:
            corpus_hash.update(struct.pack("<7q", *row))
        report["corpus_sha256_little_endian_i64_fields"] = corpus_hash.hexdigest()
        expected = literal_oracle(rows, CAPACITY)
        expected_counts = dict(calls=CALLS, hits=EVENTS*KEYS_PER_EVENT*7,
                               misses=EVENTS*KEYS_PER_EVENT,
                               evictions=EVENTS*KEYS_PER_EVENT-CAPACITY,
                               resident=CAPACITY, capacity=CAPACITY)
        if expected[3] != expected_counts:
            raise AssertionError("synthetic trace does not have its frozen hit/miss/FIFO counts")
        report["oracle_output"] = retain_full(destination, "oracle", expected)
        write_json(destination / "RESULT.json", report)
        for name, mode in ORDER:
            wall_start = time.perf_counter_ns()
            cpu_start = time.process_time_ns()
            actual = module.run(mode, rows, CAPACITY)
            cpu_elapsed = time.process_time_ns() - cpu_start
            wall_elapsed = time.perf_counter_ns() - wall_start
            sample = {"name": name, "mode": mode, "calls": CALLS,
                      "wall": wall_elapsed/1e9, "cpu": cpu_elapsed/1e9}
            report["samples"].append(sample)
            # Retain a failed output as well; no failing sample is discarded.
            sample["output"] = retain_full(destination, name, actual)
            write_json(destination / "RESULT.json", report)
            assert_equal(actual, expected, mode)
            if mode == 1 and actual[3]["rehashes"] < 1:
                raise AssertionError("timed candidate never exercised natural rehash")
            sample["full_output_equality"] = True
            del actual
            write_json(destination / "RESULT.json", report)
        verify_sources()
        report["optimistic_screen"] = optimistic_screen(report["samples"])
        report["status"] = "PASS_FINITE_KEY_COMPARISON_ONLY"
    except BaseException as exc:
        report["status"] = "FAIL_RETAINED_NO_RETRY"
        report["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        (destination / "traceback.txt").write_text(traceback.format_exc())
        raise
    finally:
        # Parent's guard receipt remains authoritative for process startup, exit,
        # this final write, group RSS and whole-command compiler-child CPU.
        report["child_cold_through_final_receipt_boundary"] = {
            "wall": time.perf_counter() - _COLD_WALL_START,
            "cpu_including_compiler_children": process_and_child_cpu() - _COLD_CPU_START,
            "excludes_process_startup_exit_and_this_final_write": True}
        report["parent_outer_guard_receipt_required"] = True
        write_json(destination / "RESULT.json", report)
    print(json.dumps({"status": report["status"], "screen": report["optimistic_screen"]["status"],
                      "result": str(destination / "RESULT.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    main(arguments.output.resolve())
