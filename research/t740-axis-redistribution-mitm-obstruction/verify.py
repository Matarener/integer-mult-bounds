#!/usr/bin/env python3
"""Exact MITM screen for per-axis T740 residual-support redistributions."""

from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import json
import math
from math import comb
from pathlib import Path
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREDECESSOR = ROOT / "research/idle-star-paired-axis-census/verify.py"
N = 8
ZERO = (0, 0)
ONE = (1, 0)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_predecessor():
    spec = importlib.util.spec_from_file_location("t740_paired_axis_census", PREDECESSOR)
    require(spec is not None and spec.loader is not None, "cannot load pinned predecessor verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def gadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def is_zero(a):
    return a == ZERO


def identity():
    return tuple(tuple(ONE if i == j else ZERO for j in range(N)) for i in range(N))


def matmul(left, right):
    out = [[ZERO for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for k in range(N):
            a = left[i][k]
            if is_zero(a):
                continue
            for j in range(N):
                b = right[k][j]
                if not is_zero(b):
                    out[i][j] = gadd(out[i][j], gmul(a, b))
    return tuple(tuple(row) for row in out)


def matvec(matrix, vector):
    result = []
    for row in matrix:
        total = ZERO
        for a, b in zip(row, vector, strict=True):
            if not is_zero(a) and not is_zero(b):
                total = gadd(total, gmul(a, b))
        result.append(total)
    return tuple(result)


def matvecs(matrix, vectors):
    return tuple(matvec(matrix, vector) for vector in vectors)


def scale_vectors(vectors, stream, value):
    result = []
    for vector in vectors:
        changed = list(vector)
        changed[stream] = gmul(value, changed[stream])
        result.append(tuple(changed))
    return tuple(result)


def phase_matrix(stream, exponent, m):
    out = [list(row) for row in identity()]
    out[stream][stream] = m.rotate(ONE, exponent)
    return tuple(tuple(row) for row in out)


def scale_row(matrix, stream, value):
    out = [list(row) for row in matrix]
    out[stream] = [gmul(value, item) for item in out[stream]]
    return tuple(tuple(row) for row in out)


def scale_column(matrix, stream, value):
    out = [list(row) for row in matrix]
    for i in range(N):
        out[i][stream] = gmul(out[i][stream], value)
    return tuple(tuple(row) for row in out)


def inverse_unimodular(matrix):
    """Exact Gaussian-rational inverse; all schedule factors are unimodular."""
    # Fast floating elimination is only a candidate generator. Accept its
    # rounded result solely after both integer matrix products prove it is an
    # exact two-sided inverse. Ill-conditioned or large cases use the exact
    # Fraction fallback below.
    try:
        work = [[complex(*matrix[i][j]) for j in range(N)] +
                [complex(1 if i == j else 0) for j in range(N)] for i in range(N)]
        for k in range(N):
            pivot_row = max(range(k, N), key=lambda i: abs(work[i][k]))
            if abs(work[pivot_row][k]) == 0:
                raise ArithmeticError("singular floating pivot")
            if pivot_row != k:
                work[k], work[pivot_row] = work[pivot_row], work[k]
            pivot = work[k][k]
            work[k] = [item / pivot for item in work[k]]
            for i in range(N):
                if i == k:
                    continue
                factor = work[i][k]
                if factor:
                    work[i] = [x - factor * y for x, y in zip(work[i], work[k], strict=True)]
        candidate = []
        for row in work:
            values = []
            for value in row[N:]:
                if not (math.isfinite(value.real) and math.isfinite(value.imag)):
                    raise ArithmeticError("non-finite floating inverse")
                real, imag = round(value.real), round(value.imag)
                if abs(value.real - real) > 1e-6 or abs(value.imag - imag) > 1e-6:
                    raise ArithmeticError("floating inverse is not close to Gaussian integers")
                values.append((real, imag))
            candidate.append(tuple(values))
        candidate = tuple(candidate)
        if matmul(matrix, candidate) == identity() and matmul(candidate, matrix) == identity():
            return candidate
    except (ArithmeticError, OverflowError, ValueError, ZeroDivisionError):
        pass

    # Exact Gaussian-rational fallback.
    def cv(z):
        return (Fraction(z[0]), Fraction(z[1]))

    def add(a, b):
        return (a[0] + b[0], a[1] + b[1])

    def neg(a):
        return (-a[0], -a[1])

    def mul(a, b):
        return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])

    def div(a, b):
        denominator = b[0] * b[0] + b[1] * b[1]
        require(denominator != 0, "singular fixed schedule segment")
        return ((a[0] * b[0] + a[1] * b[1]) / denominator,
                (a[1] * b[0] - a[0] * b[1]) / denominator)

    zero, one = (Fraction(0), Fraction(0)), (Fraction(1), Fraction(0))
    work = [[cv(matrix[i][j]) for j in range(N)] +
            [one if i == j else zero for j in range(N)] for i in range(N)]
    for k in range(N):
        pivot_row = next((i for i in range(k, N) if work[i][k] != zero), None)
        require(pivot_row is not None, "singular fixed schedule segment")
        if pivot_row != k:
            work[k], work[pivot_row] = work[pivot_row], work[k]
        pivot = work[k][k]
        work[k] = [div(item, pivot) for item in work[k]]
        for i in range(N):
            if i == k:
                continue
            factor = work[i][k]
            if factor != zero:
                work[i] = [add(x, neg(mul(factor, y)))
                           for x, y in zip(work[i], work[k], strict=True)]
    result = []
    for row in work:
        values = []
        for real, imag in row[N:]:
            require(real.denominator == 1 and imag.denominator == 1,
                    "fixed schedule segment inverse left Gaussian integers")
            values.append((int(real), int(imag)))
        result.append(tuple(values))
    return tuple(result)


def event_matrix(event, context, residual, character, m):
    matrix = [list(row) for row in identity()]
    m.run_data_event(matrix, event, context, residual, character)
    return tuple(tuple(row) for row in matrix)


def raw_operations(context, residual, character, blocks, m):
    operations = []
    for tick, (stage, replica) in enumerate(context["order"]):
        for stream, axes in context["hosts"].get(tick, ()):
            exponent = sum(m.parity(character, axis) for axis in axes)
            operations.append((phase_matrix(stream, exponent, m), None))
        if replica != 0:
            continue
        for event in blocks[stage]:
            if event["kind"] == "idle_cover_sweep":
                for side, child in enumerate(event["child_indices"]):
                    stream = 2 * event["pair"] + side
                    exponent = sum(m.parity(character, axis) for axis in residual[child])
                    exponent += 2 * m.parity(
                        character, context["recipe"]["idle_children"][child]["translation_after"]
                    )
                    operations.append((phase_matrix(stream, exponent, m), (child, stream)))
            else:
                operations.append((event_matrix(event, context, residual, character, m), None))
    return operations


def load_shared(m):
    # Reuse the exact, source-bound operator semantics from the prior census.
    m.authenticate()
    vendor = m.PACKAGE / "vendor"
    base = m.decode(m.read_bytes(vendor / "BASE-FILL.json.gz"))["rows"]
    journal = m.decode(m.read_bytes(vendor / "EXCHANGE.json"))
    rows = m.project_all_ports(base, m.journal_edits(base, journal))
    order_base = m.decode(m.read_bytes(ROOT / "research/rank7-joint-endframes/allocation/ORDER.json"))
    order = [[stage, replica + 74 * copy] for stage, replica in order_base for copy in range(10)]
    dispatch_rows = m.decode(m.read_bytes(ROOT / "research/rank7-joint-endframes/allocation/DISPATCH.json"))
    dispatch = {(stage, replica): tag for stage, replica, tag in dispatch_rows}
    providers = m.decode(m.read_bytes(vendor / "PROVIDERS.json"))
    plan = m.decode(m.read_bytes(ROOT / "research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz"))
    template = m.decode(m.read_bytes(ROOT / "research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz"))
    recipes = m.decode(m.read_bytes(ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"))["recipes"]
    require(len(rows) == len(recipes) == 112, "expected all 112 T740 port recipes")
    return rows, order, dispatch, providers, plan, template, recipes, m.stage_blocks(template)


def build_axis_operations(context, residual, axis, blocks, variables, m):
    raw = raw_operations(context, residual, axis, blocks, m)
    literal = tuple(tuple(row) for row in m.replay(context, residual, axis, blocks))
    product = identity()
    for matrix, _ in raw:
        product = matmul(matrix, product)
    require(product == literal, "raw event sequence differs from the literal exact replay")

    sign_by_child = {child: sign for child, sign in variables}
    operations = []
    for matrix, meta in raw:
        operations.append((matrix, None))
        if meta is not None:
            child, stream = meta
            if child in sign_by_child:
                operations.append((None, (child, sign_by_child[child], stream)))
    variable_ops = [variable for matrix, variable in operations if variable is not None]
    require(len(variable_ops) == len(variables), "toggle variable insertion mismatch")

    segments, current, ordered_variables = [], identity(), []
    for matrix, variable in operations:
        if variable is None:
            current = matmul(matrix, current)
        else:
            segments.append(current)
            current = identity()
            ordered_variables.append(variable)
    segments.append(current)

    # A positive control compares every one of the first four toggle masks
    # against a direct replay, including masks outside the balanced domain.
    return operations, segments, ordered_variables, literal


def verify_small_masks(context, residual, axis, blocks, operations, variables, m):
    selected = variables[:4]
    if len(selected) < 4:
        return 0
    checked = 0
    for mask in range(1 << len(selected)):
        trial = {child: list(axes) for child, axes in residual.items()}
        selected_set = set(selected)
        for child, sign in selected:
            if mask & (1 << selected.index((child, sign))):
                if sign < 0:
                    trial[child].remove(axis)
                else:
                    trial[child].append(axis)
        product = identity()
        toggle_index = 0
        for matrix, variable in operations:
            if variable is None:
                product = matmul(matrix, product)
            else:
                child, sign, stream = variable
                if (child, sign) in selected_set and (mask & (1 << selected.index((child, sign)))):
                    product = matmul(phase_matrix(stream, sign, m), product)
                toggle_index += 1
        direct = tuple(tuple(row) for row in m.replay(context, trial, axis, blocks))
        require(product == direct, "toggle-factor replay disagrees with literal operator")
        checked += 1
    return checked


def search_axis(context, residual, axis, blocks, m, do_positive_control=False):
    variables = []
    for child in sorted(residual):
        if axis in residual[child]:
            variables.append((child, -1))
        elif (len(residual[child]) < 51 and
              m.orthonormal(context["hosted_axes"].get(child, []) + residual[child] + [axis])):
            variables.append((child, +1))

    operations, segments, ordered, literal = build_axis_operations(
        context, residual, axis, blocks, variables, m
    )
    product = identity()
    for segment in segments:
        product = matmul(segment, product)
    require(product == literal, "MITM fixed-segment factorization differs from exact replay")
    if do_positive_control:
        masks_checked = verify_small_masks(context, residual, axis, blocks, operations, variables, m)
    else:
        masks_checked = 0

    n = len(ordered)
    nremove = sum(sign < 0 for _, sign, _ in ordered)
    nadd = n - nremove
    balanced = sum(comb(nremove, t) * comb(nadd, t)
                   for t in range(min(nremove, nadd) + 1))
    if n == 0:
        return {"toggle_variables": 0, "balanced_patterns": 1, "meet_states": 0,
                "matches": 0, "positive_control_masks": masks_checked,
                "column_width": 0, "column_candidates": 0}

    middle = n // 2
    inverse_segments = [inverse_unimodular(segment) for segment in segments]

    # A full-operator equality must preserve every input column. Meet on one
    # column first; widen only if that necessary signature leaves candidates.
    # Every surviving pattern is replayed through the literal full operator.
    width_used = 0
    final_candidates = []
    states_seen = 0
    # Six columns are a cheap, strong necessary signature for these 8-stream
    # operators. Widen to all eight only if the bounded direct-replay set is
    # still too large.
    for width in range(6, N + 1):
        columns = tuple(range(width))
        basis_columns = tuple(tuple(ONE if row == col else ZERO for row in range(N))
                              for col in columns)
        prefixes = [(matvecs(segments[0], basis_columns), 0, 0, 0)]
        for j in range(middle):
            _, sign, stream = ordered[j]
            fixed = segments[j + 1]
            next_prefixes = []
            for prefix, delta, count, mask in prefixes:
                next_prefixes.append((matvecs(fixed, prefix), delta, count, mask))
                changed = matvecs(fixed, scale_vectors(prefix, stream, m.rotate(ONE, sign)))
                next_prefixes.append((changed, delta + sign, count + 1, mask | (1 << j)))
            prefixes = next_prefixes

        baseline_columns = tuple(tuple(literal[row][col] for row in range(N))
                                 for col in columns)
        suffixes = [(baseline_columns, 0, 0, 0)]
        # Apply S^-1 to the selected baseline columns in reverse chronology.
        for j in range(n - 1, middle - 1, -1):
            _, sign, stream = ordered[j]
            fixed_inverse = inverse_segments[j + 1]
            next_suffixes = []
            for suffix, delta, count, mask in suffixes:
                pulled = matvecs(fixed_inverse, suffix)
                next_suffixes.append((pulled, delta, count, mask))
                changed = scale_vectors(pulled, stream, m.rotate(ONE, -sign))
                next_suffixes.append((changed, delta + sign, count + 1, mask | (1 << j)))
            suffixes = next_suffixes

        suffix_index = {}
        for suffix, delta, count, mask in suffixes:
            suffix_index.setdefault((suffix, delta), []).append((count, mask))
        candidates = []
        for prefix, delta, count, mask in prefixes:
            for suffix_count, suffix_mask in suffix_index.get((prefix, -delta), ()):
                if count + suffix_count:
                    candidates.append((mask, suffix_mask))
                    if len(candidates) > 16:
                        break
            if len(candidates) > 16:
                break
        width_used = width
        final_candidates = candidates
        states_seen += len(prefixes) + len(suffixes)
        if len(candidates) <= 16:
            break

    for prefix_mask, suffix_mask in final_candidates:
        trial = {child: list(values) for child, values in residual.items()}
        combined_mask = prefix_mask | suffix_mask
        for j, (child, sign, _) in enumerate(ordered):
            if combined_mask & (1 << j):
                if sign < 0:
                    trial[child].remove(axis)
                else:
                    trial[child].append(axis)
        after = tuple(tuple(row) for row in m.replay(context, trial, axis, blocks))
        if after == literal:
            raise ValueError("exact operator-preserving nonempty per-axis redistribution found: " +
                             json.dumps({"axis": axis, "column_width": width_used}))
        if width_used == N:
            raise ValueError("full-column segment factorization disagrees with literal replay")

    return {"toggle_variables": n, "balanced_patterns": balanced,
            "meet_states": states_seen, "matches": 0,
            "column_width": width_used,
            "column_candidates": len(final_candidates),
            "positive_control_masks": masks_checked}


def check_port(port, shared, m):
    rows, order, dispatch, providers, plan, template, recipes, blocks = shared
    context = m.prepare_port(port, rows[port], order, dispatch, providers, plan, template, recipes)
    residual = context["residual"]
    for child in sorted(residual):
        require(m.orthonormal(context["hosted_axes"].get(child, []) + residual[child]),
                "baseline hosted/residual child frame is not orthonormal")
    axes = sorted(set().union(*(set(values) for values in residual.values())))
    require(len(axes) == 72, "unexpected residual-axis dictionary size")
    for i, axis in enumerate(axes):
        require(m.parity(axis, axis) == 1, "axis self-character does not isolate its own phase")
        for other in axes[i + 1:]:
            require(m.parity(axis, other) == 0,
                    "distinct residual axes are not pairwise orthogonal")

    totals = {"toggle_variables": 0, "balanced_patterns": 0,
              "meet_states": 0, "matches": 0, "positive_control_masks": 0,
              "max_column_width": 0, "column_candidates": 0}
    for index, axis in enumerate(axes):
        result = search_axis(context, residual, axis, blocks, m,
                             do_positive_control=(port == 0 and index == 0))
        for key in totals:
            if key == "max_column_width":
                totals[key] = max(totals[key], result["column_width"])
            elif key in result:
                totals[key] += result[key]
    require(totals["matches"] == 0, "unexpected exact-preserving redistribution")
    return {"port": port, "residual_axes": len(axes), **totals}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ports", required=True, help="half-open port range, e.g. 0:56")
    parser.add_argument("--receipt", required=True, help="expected or newly written JSON receipt")
    parser.add_argument("--write", action="store_true", help="write the deterministic receipt")
    args = parser.parse_args()
    try:
        lo, hi = (int(value) for value in args.ports.split(":"))
    except Exception as exc:
        raise SystemExit("--ports must be a half-open range LO:HI") from exc
    require(0 <= lo < hi <= 112, "port range outside [0,112]")

    started = time.monotonic()
    m = load_predecessor()
    shared = load_shared(m)
    if lo == 0:
        vendor = m.PACKAGE / "vendor"
        base = m.decode(m.read_bytes(vendor / "BASE-FILL.json.gz"))["rows"]
        journal = m.decode(m.read_bytes(vendor / "EXCHANGE.json"))
        require(m.check_mutations(base, journal), "journal preimage mutation control failed")
    ports = []
    for port in range(lo, hi):
        ports.append(check_port(port, shared, m))
        if port % 8 == 0 or port == hi - 1:
            print(f"PROGRESS port={port} elapsed={time.monotonic()-started:.1f}s", flush=True)

    totals = {key: sum(entry[key] for entry in ports) for key in ports[0]
              if key not in {"port", "residual_axes", "max_column_width"}}
    totals["max_column_width"] = max(entry["max_column_width"] for entry in ports)
    totals["residual_axes"] = sum(entry["residual_axes"] for entry in ports)
    receipt = {
        "schema_version": 1,
        "scope": "T740 owner replica zero; fixed residual-axis dictionary; per-axis copy count conserved",
        "port_range": [lo, hi],
        "ports": ports,
        "totals": totals,
        "controls": {
            "source_authentication": "PASS",
            "literal_operator_vs_event_product": "PASS for each axis and port",
            "segment_factorization_vs_literal_operator": "PASS for each axis and port",
            "all_16_direct_toggle_masks": "PASS" if lo == 0 else "not scheduled in this half",
            "journal_mutation_rejected": "PASS" if lo == 0 else "covered by 0:56 half",
        },
        "result": "NO_NONTRIVIAL_EXACT_OPERATOR_PRESERVING_PATTERN",
        "kappa_improved": False,
        "selected_frontier_changed": False,
    }
    destination = PACKAGE / args.receipt
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write:
        destination.write_text(encoded, encoding="utf-8")
    else:
        require(destination.is_file(), "missing expected receipt: " + str(destination))
        require(destination.read_text(encoding="utf-8") == encoded,
                "computed receipt differs from " + str(destination))
    print(json.dumps({"range": [lo, hi], "ports": len(ports), "totals": totals,
                      "result": receipt["result"], "elapsed_seconds": round(time.monotonic()-started, 2)},
                     sort_keys=True))


if __name__ == "__main__":
    main()
