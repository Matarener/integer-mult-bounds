#!/usr/bin/env python3
"""Exact range and atomic additive-defect audit of two pinned BIT words.

Standard library only; no producer code is imported.  This is finite exact
integer computation, not a proof of native-child accuracy or rounded cleanup.
SPDX-License-Identifier: Apache-2.0
Substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


PUBLIC = 651
PORTS = 111
PRIVATE = 651
DIM = PUBLIC + 1
PINS = {
    "parent": {
        "gzip": "1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870",
        "decoded": "ebc33ee086f610c1fd540fa56bb99b2b96a768e4aed4a18defcb0e1f507fca89",
        "format": "coded-r429-pruned-three-source-copy-v1",
    },
    "candidate": {
        "gzip": "e802611104c61fc8477837b4ab41abc4f13cf41fbca6ef3de60d0b5e768fb949",
        "decoded": "127f48ecae91547e90bd2e64769f222cb17601ab36edcfdfdb0fce6f2d1bd9b7",
        "format": "coded-r429-signed-quotient-variant-v1",
    },
    "controller_decoded": "859cdd2a87ea6ce58eb0ccdf2ca675e77c7134d6a7bbc7d450493d1abb108271",
}
OPNAMES = {0: "move", 1: "add", 2: "copy", 3: "clear"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def sparse_items(row):
    return sorted(row.items())


def read_json(path):
    transport = Path(path).read_bytes()
    decoded = gzip.decompress(transport) if transport[:2] == b"\x1f\x8b" else transport
    return json.loads(decoded), {
        "transport_sha256": sha256(transport).hexdigest(),
        "decoded_sha256": sha256(decoded).hexdigest(),
    }


def load_word(path, label):
    obj, hashes = read_json(path)
    require(hashes["transport_sha256"] == PINS[label]["gzip"], label + " gzip pin")
    require(hashes["decoded_sha256"] == PINS[label]["decoded"], label + " decoded pin")
    require(obj["format"] == PINS[label]["format"], label + " format")
    require(obj["public_registers"] == PUBLIC and obj["private_register"] == PRIVATE,
            "651 public coordinates and one private coordinate")
    records = obj["records"]
    require(len(records) == 16102, "complete record count")
    require(Counter(r[0] for r in records) == Counter({0: 2873, 1: 13223, 2: 3, 3: 3}),
            "complete operation coverage")
    for r in records:
        require(len(r) == 6 and all(type(v) is int for v in r), "record schema")
        op, dst, src, coefficient, rank, phase = r
        require(op in OPNAMES and 0 <= dst < PUBLIC, "public destination")
        if op == 1:
            require(0 <= src < DIM and src != dst and coefficient in (-1, 1),
                    "unit signed distinct-coordinate shear")
        elif op == 0:
            require(1 <= rank <= 7, "MOVE paid rank")
        else:
            require(src == PRIVATE, "COPY/ERASE private address")
    return obj, hashes


def events_of(records, reverse=False):
    """Tuples (kind, dst, src, coefficient, rank, original_record)."""
    out = []
    iterator = reversed(list(enumerate(records))) if reverse else enumerate(records)
    for index, (op, dst, src, c, rank, phase) in iterator:
        if op == 1:
            out.append(("add", dst, src, -c if reverse else c, 0, index))
        elif op == 0:
            out.append(("move", dst, -1, 0, rank, index))
        elif op == (3 if reverse else 2):
            # Reverse COPY comes from the forward ERASE record; its paid
            # rank belongs to the paired COPY, which is 1 in these pins.
            out.append(("copy", PRIVATE, dst, 0, 1, index))
        else:
            out.append(("clear", PRIVATE, dst, 0, 0, index))
    return out


def add_sparse(dst, src, coefficient):
    require(dst is not src, "sparse source and destination must differ")
    for key, value in src.items():
        result = dst.get(key, 0) + coefficient * value
        if result:
            dst[key] = result
        else:
            dst.pop(key, None)


def block_l1(row):
    totals = [0, 0, 0]
    for j, value in row.items():
        totals[0 if j < PORTS else 1 if j < 2 * PORTS else 2] += abs(value)
    return tuple(totals)


def forward_values(events, values, stop=None, impulses=None, mutation=None):
    """Independent scalar simulation, with optional errors after each event."""
    values = list(values)
    selected = events if stop is None else events[:stop]
    for i, (op, dst, src, c, rank, original) in enumerate(selected):
        if op == "add":
            if mutation == "transpose_shear":
                values[src] += c * values[dst]
            else:
                values[dst] += c * values[src]
        elif op == "copy":
            if mutation != "ignore_copy":
                values[dst] = values[src]
        elif op == "clear":
            values[dst] = 0
        else:
            require(op == "move", "scalar replay opcode")
        if impulses is not None:
            values[dst] += impulses[i]
    return values


def range_audit(events):
    rows = [{i: 1} for i in range(PUBLIC)] + [{}]
    envelopes = {(1, 0, 0), (0, 1, 0), (0, 0, 1)}
    prefix = 1
    peak = {"after_event": -1, "coordinate": 0, "row": {0: 1}}
    snapshot = None
    copies = 0
    row_trace = sha256()
    for i, (op, dst, src, c, rank, original) in enumerate(events):
        if op == "add":
            require(snapshot is None or dst != snapshot, "immutable snapshot source")
            add_sparse(rows[dst], rows[src], c)
        elif op == "copy":
            require(snapshot is None and not rows[PRIVATE], "private COPY entrance")
            rows[PRIVATE] = dict(rows[src])
            snapshot = src
            copies += 1
        elif op == "clear":
            require(snapshot == src and rows[PRIVATE] == rows[src],
                    "exact ideal ERASE snapshot return")
            rows[PRIVATE] = {}
            snapshot = None
        else:
            require(op == "move", "range opcode")
        weights = block_l1(rows[dst])
        envelopes.add(weights)
        norm = sum(weights)
        if norm > prefix:
            prefix = norm
            peak = {"after_event": i, "coordinate": dst, "row": dict(rows[dst])}
        row_trace.update(canonical([i, dst, sparse_items(rows[dst]), weights]) + b"\n")
    require(snapshot is None and not rows[PRIVATE] and copies == 3, "private ideal endpoint")
    for j in range(2 * PORTS, PUBLIC):
        require(rows[j] == {j: 1}, "all 429 ideal helpers restored")
    for j in range(PORTS):
        require(all(k < PORTS for k in rows[j]), "source endpoint has only source inputs")
        require(rows[PORTS + j].get(PORTS + j) == 1 and
                all(k < PORTS or k == PORTS + j or k >= 2 * PORTS
                    for k in rows[PORTS + j]), "target self block is identity")
    endpoints = {
        "source_source_l1": max(sum(abs(c) for c in row.values()) for row in rows[:PORTS]),
        "target_source_l1": max(block_l1(row)[0] for row in rows[PORTS:2 * PORTS]),
        "target_helper_l1": max(block_l1(row)[2] for row in rows[PORTS:2 * PORTS]),
    }
    signs = [0] * DIM
    for j, coefficient in peak["row"].items():
        signs[j] = 1 if coefficient > 0 else -1
    witness = forward_values(events, signs, peak["after_event"] + 1)
    require(witness[peak["coordinate"]] == prefix, "range peak forward witness")
    return {
        "exact_prefix_l1": prefix,
        "block_prefix_envelope": sorted(envelopes),
        "block_prefix_envelope_sha256": digest(sorted(envelopes)),
        "prefix_changed_row_trace_sha256": row_trace.hexdigest(),
        "endpoint_blocks": endpoints,
        "endpoint_sparse_matrix_sha256": digest([sparse_items(row) for row in rows]),
        "ideal_helper_restoration_count": 429,
        "ideal_private_copies_and_erases": [copies, copies],
        "peak_witness": {
            "after_event": peak["after_event"],
            "original_record": events[peak["after_event"]][-1],
            "coordinate": peak["coordinate"],
            "row_sparse": sparse_items(peak["row"]),
            "input_signs_sparse": [(j, s) for j, s in enumerate(signs) if s],
            "forward_observed_coordinate": witness[peak["coordinate"]],
        },
    }, rows


def source_code_audit(records, legacy_gates, local_rows):
    selected = [(i, r) for i, r in enumerate(records) if r[0] == 1 and 21 <= r[5] <= 24]
    require(len(selected) == 1499, "complete source code extraction")
    require(Counter(r[5] for i, r in selected) == Counter({21: 474, 22: 504, 23: 47, 24: 474}),
            "source code phase coverage")
    for i, r in selected:
        require(r[1] < PORTS and r[2] < PORTS, "source code support")
    output = []
    matrices = []
    for reverse in (False, True):
        rows = [{j: 1} for j in range(PORTS)]
        prefix = 1
        peak = -1
        iterator = reversed(selected) if reverse else selected
        for original, r in iterator:
            _, dst, src, c, rank, phase = r
            add_sparse(rows[dst], rows[src], -c if reverse else c)
            norm = sum(abs(v) for v in rows[dst].values())
            if norm > prefix:
                prefix, peak = norm, original
        require(rows == local_rows[int(reverse)][:PORTS],
                "selected source code equals full local integer source endpoint")
        matrices.append(rows)
        output.append({
            "exact_prefix_l1": prefix,
            "endpoint_l1": max(sum(abs(v) for v in r.values()) for r in rows),
            "peak_original_record": peak,
            "sparse_matrix_sha256": digest([sparse_items(r) for r in rows]),
        })
    # Literal inverse on all 111 integer columns, independently of GF(2).
    restored = [dict(row) for row in matrices[0]]
    for original, r in reversed(selected):
        _, dst, src, c, rank, phase = r
        add_sparse(restored[dst], restored[src], -c)
    require(restored == [{j: 1} for j in range(PORTS)], "source code literal inverse")
    legacy = [1 << j for j in range(PORTS)]
    for gate in legacy_gates:
        require(len(gate) == 2 and all(type(j) is int and 0 <= j < PORTS for j in gate)
                and gate[0] != gate[1], "legacy binary source gate")
        dst, src = gate
        legacy[dst] ^= legacy[src]
    selected_binary = [
        sum(1 << j for j, v in row.items() if v % 2)
        for row in matrices[0]
    ]
    for reverse, local in enumerate(local_rows):
        for j in range(PORTS):
            row = local[PORTS + j]
            binary_source = sum(1 << k for k, v in row.items() if k < PORTS and v % 2)
            require(binary_source == (1 << j if reverse else selected_binary[j]),
                    "actual local binary target fits the selected abstract source code")
            require(all(v % 2 == 0 for k, v in row.items() if k >= 2 * PORTS),
                    "actual local helper leakage vanishes over GF(2)")
    differences = [i for i, (a, b) in enumerate(zip(legacy, selected_binary)) if a != b]
    require(len(legacy_gates) == 6372 and differences,
            "historical controller code is explicitly a different source endpoint")
    return {
        "source_code_adds": len(selected),
        "source_code_record_indices": [i for i, r in selected],
        "source_code_records_sha256": digest([r for i, r in selected]),
        "phase_counts": dict(sorted(Counter(r[5] for i, r in selected).items())),
        "forward": output[0],
        "inverse": output[1],
        "source_integer_inverse_verified": True,
        "actual_local_binary_interfaces_all_columns_verified": True,
        "actual_local_binary_interface":
            "Forward (x,y,h)->(A x,y+A x,h); literal reverse "
            "(x,y,h)->(A^-1 x,y+x,h). The controller uses the reverse "
            "interface with source Y and target X.",
        "legacy_controller_binary_gate_count": len(legacy_gates),
        "legacy_binary_endpoint_sha256": digest(legacy),
        "selected_binary_endpoint_sha256": digest(selected_binary),
        "legacy_binary_endpoint_equals_selected_source_mod2": False,
        "legacy_binary_endpoint_different_rows": differences,
        "first_legacy_binary_mismatch": {
            "row": differences[0], "legacy_row_bits": legacy[differences[0]],
            "selected_row_bits": selected_binary[differences[0]],
        },
        "integer_sweep_binding":
            "Each abstract sweep uses this word's selected phase21..24 signed code "
            "or its literal inverse; the controller's legacy binary gate list is "
            "a different endpoint and is not the implementation being bounded.",
    }


def abstract_schedule_audit(ordered):
    """Exact free noncommuting GF(2)-polynomial evaluation of the 8 bank columns."""
    banks = [{((), j)} for j in range(8)]
    levels = [-1] * 4
    trace = []
    def encoded(row, stages):
        result = row
        for stage in stages:
            result = {((stage,) + word, column) for word, column in result}
        return result
    for index, event in enumerate(ordered):
        op = event.get("op")
        if op == "code sweep":
            pair, side = event["pair"], int(event["side"] == "Y")
            for stage in event["stages"]:
                require((side == 1 and (levels[pair] == -1 or stage > levels[pair]))
                        or (side == 0 and levels[pair] >= stage),
                        "abstract sweep native-level side premise")
            coordinate = 2 * pair + side
            banks[coordinate] = encoded(banks[coordinate], event["stages"])
        elif op == "complete local coded call":
            pair, stage = event["pair"], event["stage"]
            require(levels[pair] == stage - 1, "abstract local incoming native level")
            x, y = banks[2 * pair:2 * pair + 2]
            if event["reverse"]:
                banks[2 * pair:2 * pair + 2] = [x ^ y, encoded(y, [stage])]
            else:
                coded_x = encoded(x, [stage])
                banks[2 * pair:2 * pair + 2] = [coded_x, y ^ coded_x]
            levels[pair] = stage
        elif op == "unchanged idle child":
            pair = event["pair"]
            require(levels[pair] == event["source_level"], "abstract idle incoming chart")
            levels[pair] = event["target_level"]
        elif event.get("kind") == "bridge":
            d, s = event["dst"], event["src"]
            require(levels[d] == levels[s], "abstract bridge common native chart")
            banks[2 * d] ^= banks[2 * s]
            banks[2 * s + 1] ^= banks[2 * d + 1]
        else:
            require(event.get("kind") == "exchange" and levels == [8] * 4,
                    "abstract terminal exchange")
            banks = [banks[j ^ 1] for j in range(8)]
        trace.append([sorted(row) for row in banks])
    endpoint = [{(tuple(range(8, -1, -1)), j)} for j in range(8)]
    require(banks == endpoint, "abstract all-column common-code endpoint")
    return {
        "coefficient_ring": "free noncommuting polynomial algebra over GF(2)",
        "independent_bank_columns": 8,
        "generator_labels": list(range(9)),
        "all_controller_events": len(ordered),
        "all_prefixes_sha256": digest(trace),
        "endpoint": "diag(G8 G7 ... G0, ..., G8 G7 ... G0)",
        "endpoint_verified": True,
        "scope": "Formal binary VALUE model only. Arbitrary substitution of linear "
                 "maps for G_s is allowed by polynomial evaluation. This does not "
                 "identify the integer lifted target with that binary local formula.",
    }


def controller_bound(ordered, local, source):
    bank = [[1, 1] for _ in range(4)]
    maximum = 1
    counts = Counter()
    transcript = []
    local_checkpoints = []
    directions = ["forward", "inverse"]
    seen_stages = []
    for index, event in enumerate(ordered):
        before = [list(pair) for pair in bank]
        op = event.get("op")
        entry = {"controller_event": index, "before": before}
        if op == "code sweep":
            pair = event["pair"]
            require(0 <= pair < 4 and event["side"] in ("X", "Y"), "code bank")
            side = int(event["side"] == "Y")
            factors = []
            for stage in event["stages"]:
                require(type(stage) is int and 0 <= stage <= 8, "code stage")
                direction = directions[stage % 2]
                prefix = source[direction]["exact_prefix_l1"] * bank[pair][side]
                maximum = max(maximum, prefix)
                bank[pair][side] *= source[direction]["endpoint_l1"]
                counts[direction + "_code"] += 1
                factors.append({"stage": stage, "direction": direction,
                                "prefix_upper": prefix, "endpoint_upper": bank[pair][side]})
            entry.update(kind="code sweep", factors=factors)
        elif op == "complete local coded call":
            pair = event["pair"]
            stage = event["stage"]
            reverse = int(event["reverse"])
            require(0 <= pair < 4 and stage % 2 == reverse, "local source orientation")
            source_side = reverse
            target_side = 1 - reverse
            x, y = bank[pair][source_side], bank[pair][target_side]
            h = max(v for pair_values in bank for v in pair_values)
            direction = directions[reverse]
            envelopes = local[direction]["block_prefix_envelope"]
            values = [(a * x + b * y + c * h, (a, b, c)) for a, b, c in envelopes]
            prefix, maximizing_block = max(values)
            maximum = max(maximum, prefix)
            endpoint = local[direction]["endpoint_blocks"]
            bank[pair][source_side] = endpoint["source_source_l1"] * x
            bank[pair][target_side] = (
                y + endpoint["target_source_l1"] * x + endpoint["target_helper_l1"] * h)
            counts["local_" + direction] += 1
            seen_stages.append(stage)
            entry.update(kind="local", stage=stage, direction=direction,
                         source_input=x, target_input=y, hosted_helper_input=h,
                         maximizing_block=maximizing_block, prefix_upper=prefix)
            local_checkpoints.append({"stage": stage, "prefix_upper_bits": maximum.bit_length()})
        elif op == "unchanged idle child":
            require(0 <= event["pair"] < 4 and
                    event["rank"] == 7 * (event["target_level"] - event["source_level"]),
                    "idle chart rank")
            counts["isometric_idle_events"] += 1
            entry.update(kind="assumed isometric idle endpoint", rank=event["rank"])
        elif event.get("kind") == "bridge":
            d, s = event["dst"], event["src"]
            coefficient = event["coefficient"]
            require(0 <= d < 4 and 0 <= s < 4 and d != s and coefficient in (-1, 1),
                    "bridge schema")
            bank[d][0] += abs(coefficient) * bank[s][0]
            bank[s][1] += abs(coefficient) * bank[d][1]
            maximum = max(maximum, *(v for pair in bank for v in pair))
            counts["scalar_bridge_shears"] += 2
            entry.update(kind="two scalar bank shears", coefficient=coefficient)
        elif event.get("kind") == "exchange":
            bank = [[y, x] for x, y in bank]
            counts["exchange"] += 1
            entry.update(kind="exchange")
        else:
            raise ValueError("uncovered controller event: " + repr(event))
        entry.update(after=[list(pair) for pair in bank], running_prefix_upper=maximum)
        transcript.append(entry)
    require(len(ordered) == 56 and seen_stages == list(range(9)), "full ordered controller")
    require(counts == Counter(forward_code=35, inverse_code=28, local_forward=5,
                              local_inverse=4, scalar_bridge_shears=18,
                              isometric_idle_events=10, exchange=1), "all controller counts")
    pf, pr = [source[d]["exact_prefix_l1"] for d in directions]
    lf, lr = [local[d]["exact_prefix_l1"] for d in directions]
    crude = (1 << 18) * lf**5 * lr**4 * pf**35 * pr**28
    require(maximum <= crude, "block-aware bound below full factor product")
    decode_factor = pf**4 * pr**5
    terminal = maximum * decode_factor
    return {
        "counts": dict(counts),
        "controller_event_count": len(ordered),
        "sweep_instantiation": source["integer_sweep_binding"],
        "ordered_scalar_growth_upper": maximum,
        "ordered_scalar_growth_upper_bits": maximum.bit_length(),
        "block64_reserve_bits": 64 * ((maximum.bit_length() + 63) // 64),
        "crude_product_upper": crude,
        "crude_product_upper_bits": crude.bit_length(),
        "terminal_decode_factor_upper": decode_factor,
        "with_per_bank_nine_factor_decode_upper": terminal,
        "with_per_bank_nine_factor_decode_upper_bits": terminal.bit_length(),
        "terminal_block64_reserve_bits": 64 * ((terminal.bit_length() + 63) // 64),
        "local_stage_checkpoints": local_checkpoints,
        "full_ordered_recurrence": transcript,
        "full_ordered_recurrence_sha256": digest(transcript),
    }


def row_adjoint_coefficients(events, output, mutation=None):
    """Scalar dual recurrence; independent of the sparse-column implementation."""
    row = [0] * DIM
    row[output] = 1
    coefficients = [0] * len(events)
    for i in range(len(events) - 1, -1, -1):
        op, dst, src, c, rank, original = events[i]
        coefficients[i] = row[dst]
        if op == "add":
            if mutation == "wrong_adjoint":
                row[dst] += c * row[src]
            else:
                row[src] += c * row[dst]
        elif op == "copy":
            row[src] += row[dst]
            row[dst] = 0
        elif op == "clear":
            row[dst] = 0
    return coefficients


def impulse(events, after_event, coordinate, mutation=None):
    values = [0] * DIM
    values[coordinate] = 1
    suffix = events[after_event + 1:]
    if mutation == "wrong_order":
        suffix = list(reversed(suffix))
    return forward_values(suffix, values, mutation=mutation)


def suffix_row(events, before_event, output):
    """One full row of M_last ... M_before_event, by scalar backward recurrence."""
    row = [0] * DIM
    row[output] = 1
    for op, dst, src, c, rank, original in reversed(events[before_event:]):
        if op == "add":
            row[src] += c * row[dst]
        elif op == "copy":
            row[src] += row[dst]
            row[dst] = 0
        elif op == "clear":
            row[dst] = 0
    return row


def as_sparse(values):
    return [(j, v) for j, v in enumerate(values) if v]


def suffix_audit(events):
    # Column j is S_i e_j, where S_i consists of events strictly after i.
    columns = [{j: 1} for j in range(DIM)]
    row_norms = [1] * DIM
    groups = Counter()
    sums_max = Counter()
    row_sums = {}
    suffix_peak = {"before_event": len(events), "output": 0, "row_l1": 1}
    peak = {"after_event": len(events) - 1, "destination": events[-1][1],
            "influence": 0, "column": {}}
    columns_digest = sha256()
    selected_indices = {0, len(events) // 5, len(events) // 2,
                        4 * len(events) // 5, len(events) - 1}
    selected_indices.update(i for i, event in enumerate(events) if event[0] in ("copy", "clear"))
    selected_columns = {}
    influences = [0] * len(events)
    for i in range(len(events) - 1, -1, -1):
        op, dst, src, c, rank, original = events[i]
        column = columns[dst]
        influence = max((abs(v) for v in column.values()), default=0)
        influences[i] = influence
        categories = [op, "all_events"]
        if op != "clear":
            categories.append("exact_clear")
        if op in ("move", "copy"):
            categories += ["move_and_copy", "paid_rank_" + str(rank)]
        for group in categories:
            groups[group] += 1
            sums_max[group] += influence
            totals = row_sums.setdefault(group, [0] * DIM)
            for row, value in column.items():
                totals[row] += abs(value)
        if influence > peak["influence"]:
            peak = {"after_event": i, "destination": dst,
                    "influence": influence, "column": dict(column)}
        if i in selected_indices:
            selected_columns[i] = dict(column)
        columns_digest.update(canonical([i, sparse_items(column)]) + b"\n")
        # Exact right multiplication S <- S M_i.
        if op in ("add", "copy"):
            multiplier = c if op == "add" else 1
            target = columns[src]
            for row, value in columns[dst].items():
                old = target.get(row, 0)
                new = old + multiplier * value
                row_norms[row] += abs(new) - abs(old)
                if new:
                    target[row] = new
                else:
                    target.pop(row, None)
        if op in ("copy", "clear"):
            for row, value in columns[dst].items():
                row_norms[row] -= abs(value)
            columns[dst] = {}
        candidate = max(row_norms)
        if candidate > suffix_peak["row_l1"]:
            suffix_peak = {"before_event": i, "output": row_norms.index(candidate), "row_l1": candidate}
    independently_summed = [0] * DIM
    for column in columns:
        for row, value in column.items():
            independently_summed[row] += abs(value)
    require(independently_summed == row_norms, "complete final suffix row accounting")
    peak_row = suffix_row(events, suffix_peak["before_event"], suffix_peak["output"])
    require(sum(map(abs, peak_row)) == suffix_peak["row_l1"],
            "independent scalar adjoint confirms maximum suffix row")
    peak_row_signs = [1 if v > 0 else -1 if v < 0 else 0 for v in peak_row]
    suffix_output = forward_values(events[suffix_peak["before_event"]:], peak_row_signs)
    require(suffix_output[suffix_peak["output"]] == suffix_peak["row_l1"],
            "maximum suffix row sign vector forward attainment")
    suffix_peak.update(row_sparse=as_sparse(peak_row),
                       forward_attained_coordinate=suffix_output[suffix_peak["output"]])
    selected_columns[peak["after_event"]] = peak["column"]
    impulses = []
    for i, expected in sorted(selected_columns.items()):
        observed = impulse(events, i, events[i][1])
        require(dict(as_sparse(observed)) == expected, "forward impulse and reverse adjoint")
        impulses.append({"after_event": i, "original_record": events[i][-1],
                         "destination": events[i][1], "influence": influences[i],
                         "output_sparse_sha256": digest(as_sparse(observed)),
                         "nonzero_outputs": len(expected)})
    peak_output = min(j for j, v in peak["column"].items() if abs(v) == peak["influence"])
    witness_coefficients = row_adjoint_coefficients(events, peak_output)
    require(witness_coefficients[peak["after_event"]] == peak["column"][peak_output],
            "peak scalar adjoint agrees")
    wrong_coefficients = row_adjoint_coefficients(events, peak_output, "wrong_adjoint")
    wrong_candidates = [i for i, e in enumerate(events)
                        if wrong_coefficients[i] != witness_coefficients[i]]
    require(wrong_candidates, "wrong-adjoint negative control must fail")
    bad_i = next((i for i in wrong_candidates if witness_coefficients[i]), wrong_candidates[0])
    direct = impulse(events, bad_i, events[bad_i][1])
    require(direct[peak_output] == witness_coefficients[bad_i] != wrong_coefficients[bad_i],
            "source-specific wrong-adjoint control")
    correct_peak = impulse(events, peak["after_event"], peak["destination"])
    wrong_order = impulse(events, peak["after_event"], peak["destination"], "wrong_order")
    require(wrong_order != correct_peak, "source-specific reversed-order control")
    copy_control = None
    for i, event in enumerate(events):
        if event[0] != "copy":
            continue
        source_coordinate = event[2]
        correct = impulse(events, i - 1, source_coordinate)
        ignored = impulse(events, i - 1, source_coordinate, "ignore_copy")
        if correct != ignored:
            output = next(j for j in range(DIM) if correct[j] != ignored[j])
            copy_control = {
                "before_copy_event": i, "injected_coordinate": source_coordinate,
                "output_coordinate": output, "correct": correct[output], "ignored_copy": ignored[output],
            }
            break
    require(copy_control is not None, "source-specific ignored-COPY control")
    aggregates = {}
    for group, sums in sorted(row_sums.items()):
        maximum = max(sums)
        output = sums.index(maximum)
        aggregates[group] = {
            "event_count": groups[group],
            "exact_linf_defect_constant": maximum,
            "maximizing_output": output,
            "row_sums": sums,
            "loose_sum_of_event_linf_influences": sums_max[group],
        }
    aggregate_witnesses = {}
    for group in ("all_events", "exact_clear", "move_and_copy"):
        maximum = aggregates[group]["exact_linf_defect_constant"]
        output = aggregates[group]["maximizing_output"]
        coefficients = row_adjoint_coefficients(events, output)
        admitted = [
            group == "all_events" or group == "exact_clear" and e[0] != "clear"
            or group == "move_and_copy" and e[0] in ("move", "copy")
            for e in events
        ]
        signs = [(1 if a > 0 else -1 if a < 0 else 0) if allowed else 0
                 for a, allowed in zip(coefficients, admitted)]
        require(sum(abs(a) for a, allowed in zip(coefficients, admitted) if allowed) == maximum,
                "dual row reproduces exact aggregate")
        observed = forward_values(events, [0] * DIM, impulses=signs)
        require(observed[output] == maximum and max(map(abs, observed)) == maximum,
                "simultaneous signed errors attain aggregate exactly")
        all_positive = [int(allowed) for allowed in admitted]
        positive_observed = forward_values(events, [0] * DIM, impulses=all_positive)
        signed_sum = sum(a for a, allowed in zip(coefficients, admitted) if allowed)
        require(positive_observed[output] == signed_sum, "all-positive error replay")
        require(abs(signed_sum) < maximum, "error-sign cancellation control is strict")
        aggregate_witnesses[group] = {
            "output_coordinate": output, "attained": maximum,
            "signed_coefficients": coefficients,
            "admitted_event_mask_sha256": digest(admitted),
            "attaining_error_signs": signs,
            "forward_output_sparse": as_sparse(observed),
            "all_positive_errors_at_same_output": signed_sum,
            "strict_sign_cancellation": True,
        }
    peak.pop("column")
    peak.update(original_record=events[peak["after_event"]][-1], output_coordinate=peak_output,
                output_sparse=as_sparse(correct_peak))
    return {
        "events": len(events),
        "normalized_event_sha256": digest(events),
        "per_event_single_destination_influences": influences,
        "per_event_single_destination_influences_sha256": digest(influences),
        "all_destination_columns_reverse_order_sha256": columns_digest.hexdigest(),
        "maximum_suffix_row_l1": suffix_peak["row_l1"],
        "maximum_suffix_row_l1_witness": suffix_peak,
        "maximum_single_destination_influence": peak["influence"],
        "peak_impulse_witness": peak,
        "groups": aggregates,
        "aggregate_attainment_witnesses": aggregate_witnesses,
        "independent_forward_impulse_checks": impulses,
        "negative_controls": {
            "wrong_adjoint": {"after_event": bad_i, "output": peak_output,
                              "correct": witness_coefficients[bad_i],
                              "wrong": wrong_coefficients[bad_i]},
            "wrong_suffix_order": {
                "after_event": peak["after_event"],
                "correct_output_sha256": digest(correct_peak),
                "wrong_order_output_sha256": digest(wrong_order),
                "wrong_order_norm": max(map(abs, wrong_order)),
            },
            "ignored_copy": copy_control,
            "error_signs": "For each aggregate witness, all-positive errors strictly "
                           "underachieve at the maximizing output; the saved signs "
                           "attain the exact absolute-coefficient sum.",
        },
    }


def compare_words(parent, candidate):
    result = {}
    for direction in ("forward", "inverse"):
        a = parent["suffix"][direction]
        b = candidate["suffix"][direction]
        old = a["per_event_single_destination_influences"]
        new = b["per_event_single_destination_influences"]
        increased = [i for i, (x, y) in enumerate(zip(old, new)) if y > x]
        decreased = [i for i, (x, y) in enumerate(zip(old, new)) if y < x]
        equal = [i for i, (x, y) in enumerate(zip(old, new)) if y == x]
        require(len(increased) + len(decreased) + len(equal) == 16102, "all defect comparisons")
        changes = {}
        for group in a["groups"]:
            changes[group] = {
                "parent_exact_aggregate": a["groups"][group]["exact_linf_defect_constant"],
                "candidate_exact_aggregate": b["groups"][group]["exact_linf_defect_constant"],
                "parent_loose_sum": a["groups"][group]["loose_sum_of_event_linf_influences"],
                "candidate_loose_sum": b["groups"][group]["loose_sum_of_event_linf_influences"],
            }
        result[direction] = {
            "increased_event_count": len(increased),
            "decreased_event_count": len(decreased),
            "equal_event_count": len(equal),
            "increased_events_sha256": digest(increased),
            "decreased_events_sha256": digest(decreased),
            "first_increase": None if not increased else {
                "event": increased[0], "parent": old[increased[0]], "candidate": new[increased[0]]},
            "largest_absolute_increase": None if not increased else (
                lambda i: {"event": i, "parent": old[i], "candidate": new[i]})(
                    max(increased, key=lambda j: new[j] - old[j])),
            "group_comparison": changes,
        }
    return result


def run(parent_path, candidate_path, controller_path):
    parent_obj, parent_hashes = load_word(parent_path, "parent")
    candidate_obj, candidate_hashes = load_word(candidate_path, "candidate")
    controller_obj, controller_hashes = read_json(controller_path)
    require(controller_hashes["decoded_sha256"] == PINS["controller_decoded"],
            "controller decoded source pin")
    abstract_schedule = abstract_schedule_audit(controller_obj["ordered_controller"])
    parent_records, candidate_records = parent_obj["records"], candidate_obj["records"]
    changed = []
    for index, (old, new) in enumerate(zip(parent_records, candidate_records)):
        if old == new:
            continue
        require(old[:3] == new[:3] and old[4:] == new[4:] and
                old[0] == 1 and old[5] == 23 and old[3] == 1 and new[3] == -1,
                "only phase23 signs change")
        changed.append(index)
    require(len(changed) == 23, "exactly 23 changed signs")
    outputs = {}
    for label, records, hashes in (
            ("parent", parent_records, parent_hashes),
            ("candidate", candidate_records, candidate_hashes)):
        normalized = {d: events_of(records, d == "inverse") for d in ("forward", "inverse")}
        ranges, rows = {}, []
        suffixes = {}
        for direction in ("forward", "inverse"):
            ranges[direction], endpoint = range_audit(normalized[direction])
            rows.append(endpoint)
            suffixes[direction] = suffix_audit(normalized[direction])
        code = source_code_audit(records, controller_obj["inplace_code_CNOTs"], rows)
        controller = controller_bound(controller_obj["ordered_controller"], ranges, code)
        paid = Counter()
        for op, dst, src, c, rank, phase in records:
            if op == 0:
                paid[rank] += 1
            elif op == 2:
                paid[phase] += 1
        require(sum(rank * count for rank, count in paid.items()) == 4989, "full paid rank mass")
        outputs[label] = {
            "source": hashes, "record_count": len(records), "public_inputs": PUBLIC,
            "helper_inputs": PUBLIC - 2 * PORTS, "private_coordinate": PRIVATE,
            "opcode_counts": dict(Counter(OPNAMES[r[0]] for r in records)),
            "paid_rank_counts": dict(sorted(paid.items())),
            "paid_rank_mass": sum(rank * count for rank, count in paid.items()),
            "range": ranges, "source_code": code, "controller": controller,
            "suffix": suffixes,
        }
    return {
        "status": "PASS_EXACT_RANGE_AND_ATOMIC_DEFECT_CONSTANTS_NO_PRECISION_ADMISSION",
        "schema": "b04-range-and-atomic-defect-review-v1",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "controller_source": controller_hashes,
        "controller_ordered_events_sha256": digest(controller_obj["ordered_controller"]),
        "abstract_binary_schedule": abstract_schedule,
        "changed_phase23_sign_record_indices": changed,
        "parent": outputs["parent"],
        "candidate": outputs["candidate"],
        "comparison": compare_words(outputs["parent"], outputs["candidate"]),
        "scope": {
            "arithmetic": "exact unbounded integers; exact normalized atomic operations",
            "norm": "maximum absolute scalar coordinate, including the private coordinate",
            "defects": "independent scalar additive errors after each admitted event in its "
                       "single destination; MOVE is the identity in this normalized model",
            "copy_extension": "COPY overwrites the private coordinate with its source; "
                              "ERASE assigns private zero. This noninvertible extension "
                              "is conditional and does not justify physical cleanup.",
            "strict_cleanup": "The exact_clear aggregate sets all ERASE defects to zero; "
                              "actual rounded copy/zero-return still requires a separate proof.",
            "controller": "Conditional on source-selected codes at admitted native charts, "
                          "isometric frame/owner/address maps and exact helper restoration.",
            "excluded": ["native-child internal prefixes and defects", "actual rounding/tie rules",
                         "overflow or finite machine exponent admission", "relative error feedback",
                         "tape/storage/work invoice", "general sign optimality",
                         "global integer BIT identity", "new supplier or kappa"],
            "proof_kind": "finite exhaustive integer calculation plus written all-input "
                          "conditional linear-algebra proof; no formal-kernel proof",
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-word", required=True)
    parser.add_argument("--candidate-word", required=True)
    parser.add_argument("--controller", required=True,
                        help="pinned JSON or gzip JSON; decoded bytes are bound")
    parser.add_argument("--output", help="write deterministic JSON or .gz JSON receipt")
    parser.add_argument("--verify", help="require equality with an existing JSON/.gz receipt")
    args = parser.parse_args()
    result = run(args.parent_word, args.candidate_word, args.controller)
    if args.verify:
        old, _ = read_json(args.verify)
        require(canonical(old) == canonical(result), "complete deterministic receipt differs")
    if args.output:
        body = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
        if args.output.endswith(".gz"):
            body = gzip.compress(body, mtime=0)
        Path(args.output).write_bytes(body)
    print(result["status"])
    for label in ("parent", "candidate"):
        r = result[label]
        print(label, "range", [r["range"][d]["exact_prefix_l1"] for d in ("forward", "inverse")],
              "controller bits", r["controller"]["ordered_scalar_growth_upper_bits"],
              "terminal bits", r["controller"]["with_per_bank_nine_factor_decode_upper_bits"])
        for d in ("forward", "inverse"):
            s = r["suffix"][d]
            print(" ", d, "peak impulse", s["maximum_single_destination_influence"],
                  "exact aggregate", s["groups"]["exact_clear"]["exact_linf_defect_constant"],
                  "loose sum", s["groups"]["exact_clear"]["loose_sum_of_event_linf_influences"])
    print("receipt_sha256", digest(result))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError) as error:
        print("FAIL:", error, file=sys.stderr)
        raise SystemExit(1)
