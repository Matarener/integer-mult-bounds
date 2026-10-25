#!/usr/bin/env python3
"""Exact fixed-D4 carrier words on 28 arbitrary Gaussian field inputs.

Standard-library only. Apache-2.0. Substantial OpenAI Codex assistance.
This finite operator check has no rounding, physical-tape, or kappa conclusion.
"""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import sys
import types

GEOMETRY_SHA = "93716ba2a0297c4b468ca7344a9b744fcdaee4013f490443a58ddc7a6610eedd"
COMPILER_SHA = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"
SCIENTIFIC_PIN = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
N, FIELDS = 7, 28


class CheckFailure(ValueError):
    """A named acceptance-gate failure, not an arbitrary implementation error."""

    def __init__(self, code, detail=None):
        self.code, self.detail = code, detail
        super().__init__(code)


def need(condition, code, detail=None):
    if not condition:
        raise CheckFailure(code, detail)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), "output_already_exists")
    geometry_bytes, compiler_bytes = args.geometry.read_bytes(), args.compiler.read_bytes()
    need(hashlib.sha256(geometry_bytes).hexdigest() == GEOMETRY_SHA, "geometry_pin")
    need(hashlib.sha256(compiler_bytes).hexdigest() == COMPILER_SHA, "compiler_pin")
    geometry = json.loads(geometry_bytes)
    # Execute the authenticated buffer, not a second read by a path-based loader.
    ce = types.ModuleType("carrier_authenticated_clifford")
    ce.__file__ = "authenticated:clifford_exact.py"
    sys.modules[ce.__name__] = ce
    exec(compile(compiler_bytes, ce.__file__, "exec", dont_inherit=True, optimize=0), ce.__dict__)
    G = geometry["groups7"]
    need(G == [[7, 2, 50, 55], [13, 61, 8, 56], [117, 64, 69, 112]], "fixed_geometry")
    core = [group[0] for group in G]
    chart = ce.perm(N, ce.inv(ce.transpose(core + [5, 53, 30, 96], N), N))
    D = chart.then(ce.hadamard(N, [3, 4])).then(chart.adjoint())
    D = D.then(ce.Op(N, ce.identity(N), [("phase", 3)]))
    E = [D.then(ce.cgate(N, p)) for p in core]
    V = [E[1].then(ce.cgate(N, core[2])),
         E[0].then(ce.cgate(N, core[2])),
         E[0].then(ce.cgate(N, core[1]))]
    F = ce.fourier(N).then(ce.xgate(N, 33))
    invariant = ce.ident(N)
    for p in core:
        invariant = invariant.then(ce.cgate(N, p))
    for p, q in [(5, 30), (53, 96)]:
        invariant = invariant.then(ce.cgate(N, p)).then(ce.cgate(N, q))
        invariant = invariant.then(ce.cgate(N, p ^ q).adjoint())

    def same(a, b):
        return a.tab == b.tab and a.zero_state() == b.zero_state()

    need(same(invariant, F), "full_phase_invariant_frame")
    ops, fingerprints, lower_cache, composition_cache, conjugate_cache = {}, {}, {}, {}, {}

    def intern(op):
        payload = {"tableau": op.tab, "zero_column": op.zero_state()}
        key = digest(payload)
        if key not in ops:
            ops[key], fingerprints[key] = op, payload
        else:
            need(fingerprints[key] == payload, "operator_digest_collision")
        return key

    identity = intern(ce.ident(N))

    def compose(a, b):
        """The key of b*a."""
        pair = (a, b)
        if pair not in composition_cache:
            composition_cache[pair] = intern(ops[a].then(ops[b]))
        return composition_cache[pair]

    def conjugate(op):
        key = intern(op)
        if key in conjugate_cache:
            return ops[conjugate_cache[key]]
        out = ce.ident(N)
        for event in op.circuit:
            kind = event[0]
            if kind == "P":
                gate = ce.perm(N, event[1])
            elif kind == "X":
                gate = ce.xgate(N, event[1])
            elif kind == "C":
                gate = ce.cgate(N, event[1], -event[2])
            elif kind == "D":
                gate = ce.diag(N, event[1], tuple((-x) % 4 for x in event[2]))
            elif kind == "phase":
                gate = ce.Op(N, ce.identity(N), [("phase", (-event[1]) % 4)])
            else:
                raise CheckFailure("unknown_conjugation_primitive", event)
            out = out.then(gate)
        # This compares actual Gaussian amplitudes, not just symplectic data.
        vec, den = op.zero_state()
        need(out.zero_state() == ([(a, -b) for a, b in vec], den), "literal_conjugation")
        conjugate_cache[key] = intern(out)
        return out

    def transpose(op):
        return conjugate(op).adjoint()

    def lower(key):
        if key not in lower_cache:
            record, literal = ce.lower_child(ops[key])
            need(same(ops[key], literal), "native_lowering_phase")
            lower_cache[key] = record
        return lower_cache[key]

    def native_rank(op):
        return lower(intern(op))["rank"]

    source_in = [ce.cgate(N, p) for group in G for p in group]
    target_in = [ce.cgate(N, G[(g + 1) % 3][j]) for g in range(3) for j in range(4)]
    source_out = [ce.cgate(N, G[(g + 1) % 3][j]).adjoint().then(F)
                  for g in range(3) for j in range(4)]
    target_out = [ce.cgate(N, p).adjoint().then(F) for group in G for p in group]

    def build(kind):
        frames = source_in[:] + target_in[:] + ([E[0]] * 4 if kind == "bus" else [ce.ident(N)] * 4)
        initial_frames = frames[:]
        events, swaps, native_products = [], [], [identity] * FIELDS

        def add(dst, src, coefficient=1, purpose="delivery"):
            if purpose == "delivery":
                need(same(frames[dst], frames[src]), "common_delivery_frame")
            events.append({"gate": "ADD", "dst": dst, "src": src,
                           "coefficient": coefficient, "purpose": purpose})

        def move(reg, frame, purpose):
            query = intern(frames[reg].adjoint().then(frame))
            events.append({"gate": "NATIVE", "register": reg, "operator": query, "purpose": purpose})
            native_products[reg] = compose(native_products[reg], query)
            frames[reg] = frame

        def swap(a, b, raw=False):
            if not raw:
                need(same(frames[a], frames[b]), "common_swap_frame")
            start = len(events)
            purpose = "raw_id_swap" if raw else "contact_swap"
            add(a, b, 1, purpose)
            add(b, a, -1, purpose)
            add(a, b, 1, purpose)
            events.append({"gate": "NEG", "register": b, "purpose": purpose})
            frames[a], frames[b] = frames[b], frames[a]
            swaps.append({"registers": [a, b], "raw": raw, "start": start, "length": 4})

        for g in range(3):
            for j in range(4):
                move(4 * g + j, E[g], "source_prepare")
                move(12 + 4 * g + j, E[(g + 1) % 3], "target_prepare")
        for j in range(4):
            a, b, c, h = j, 4 + j, 8 + j, 24 + j
            ta, tb, tc = 12 + j, 16 + j, 20 + j
            if kind in ("open", "bus"):
                carrier = h if kind == "bus" else a
                if kind == "bus":
                    swap(h, a)
                    move(a, source_out[a], "source_return")
                move(carrier, E[1], "carrier_to_B")
                add(ta, carrier)
                swap(carrier, b)
                move(b, source_out[b], "source_return")
                move(carrier, E[2], "carrier_to_C")
                add(tb, carrier)
                swap(carrier, c)
                move(c, source_out[c], "source_return")
                move(carrier, V[1], "carrier_open_pivot")
                move(carrier, V[2], "carrier_open_endpoint")
                move(tc, V[2], "target_C_contact")
                add(tc, carrier)
                for t in (ta, tb, tc):
                    move(t, target_out[t - 12], "target_return")
            else:
                move(a, V[0], "reverse_first_contact")
                move(c, V[0], "reverse_C_contact")
                move(ta, V[0], "reverse_target_A_contact")
                add(ta, a)
                swap(a, c)
                move(c, source_out[c], "source_return")
                move(a, V[2], "reverse_second_contact")
                move(b, V[2], "reverse_B_contact")
                move(tc, V[2], "reverse_target_C_contact")
                add(tc, a)
                swap(a, b)
                move(b, source_out[b], "source_return")
                move(a, V[1], "reverse_third_contact")
                move(tb, V[1], "reverse_target_B_contact")
                add(tb, a)
                move(a, source_out[a], "source_return")
                for t in (ta, tb, tc):
                    move(t, target_out[t - 12], "target_return")
        frames_before_cleanup = frames[:]
        for j in range(4):
            if kind == "bus":
                for g in (2, 1, 0):
                    swap(24 + j, 4 * g + j, raw=True)
            elif kind == "open":
                swap(j, 8 + j, raw=True)
                swap(j, 4 + j, raw=True)
            else:
                swap(j, 4 + j, raw=True)
                swap(j, 8 + j, raw=True)
        need(all(same(initial_frames[r].adjoint().then(frames_before_cleanup[r]),
                      ops[native_products[r]]) for r in range(FIELDS)), "fixed_id_query_products")
        return events, swaps, native_products

    def expected(kind, orientation):
        result = [{} for _ in range(FIELDS)]

        def put(row, column, op, coefficient=1):
            result[row][(column, intern(op))] = coefficient

        for g in range(3):
            for j, p in enumerate(G[g]):
                i = 4 * g + j
                q, r = G[(g + 1) % 3][j], G[(g + 2) % 3][j]
                cp, cq, cr = ce.cgate(N, p), ce.cgate(N, q), ce.cgate(N, r)
                S = cp.adjoint().then(cr.adjoint()).then(F) if g < 2 else cp.adjoint().then(V[2])
                J = ce.xgate(N, p).then(F)
                T = cq.adjoint().then(cp.adjoint()).then(F)
                if kind == "reverse":
                    S = J
                if orientation == "forward":
                    put(i, i, S); put(12 + i, i, J); put(12 + i, 12 + i, T)
                elif orientation == "inverse":
                    put(i, i, S.adjoint()); put(12 + i, 12 + i, T.adjoint())
                    put(12 + i, i, S.adjoint().then(J).then(T.adjoint()), -1)
                elif orientation == "dual":
                    put(i, i, conjugate(S)); put(12 + i, 12 + i, conjugate(T))
                    put(i, 12 + i, conjugate(T).then(transpose(J)).then(conjugate(S)), -1)
                elif orientation == "dual_inverse":
                    put(i, i, transpose(S)); put(12 + i, 12 + i, transpose(T))
                    put(i, 12 + i, transpose(J))
                else:
                    raise CheckFailure("unknown_orientation")
        for j in range(4):
            H = E[0].adjoint().then(source_out[j]) if kind == "bus" else ce.ident(N)
            if orientation == "inverse":
                H = H.adjoint()
            elif orientation == "dual":
                H = conjugate(H)
            elif orientation == "dual_inverse":
                H = transpose(H)
            put(24 + j, 24 + j, H)
        return result

    def inverse_word(events):
        out = []
        for event in reversed(events):
            new = dict(event)
            if event["gate"] == "NATIVE":
                new["operator"] = intern(ops[event["operator"]].adjoint())
            elif event["gate"] == "ADD":
                new["coefficient"] *= -1
            out.append(new)
        return out

    def dual_word(events):
        out = []
        for event in events:
            new = dict(event)
            if event["gate"] == "NATIVE":
                new["operator"] = intern(conjugate(ops[event["operator"]]))
            elif event["gate"] == "ADD":
                new["dst"], new["src"] = event["src"], event["dst"]
                new["coefficient"] *= -1
            out.append(new)
        return out

    def canonical_key(key, phase_sensitive):
        return key if phase_sensitive else digest(ops[key].tab)

    def combine(row, key, coefficient):
        value = row.get(key, 0) + coefficient
        if value:
            row[key] = value
        elif key in row:
            del row[key]

    def replay(events):
        rows = [{(i, identity): 1} for i in range(FIELDS)]
        for event in events:
            gate = event["gate"]
            if gate == "NATIVE":
                reg, query = event["register"], event["operator"]
                replacement = {}
                for (column, key), coefficient in rows[reg].items():
                    combine(replacement, (column, compose(key, query)), coefficient)
                rows[reg] = replacement
            elif gate == "ADD":
                dst, src = event["dst"], event["src"]
                need(dst != src and event["coefficient"] in (-1, 1), "literal_add_grammar")
                for key, coefficient in rows[src].items():
                    combine(rows[dst], key, event["coefficient"] * coefficient)
            elif gate == "NEG":
                reg = event["register"]
                rows[reg] = {key: -coefficient for key, coefficient in rows[reg].items()}
            else:
                raise CheckFailure("literal_gate_grammar", gate)
        return rows

    def collapse(rows, phase_sensitive=True):
        result = []
        for row in rows:
            collapsed = {}
            for (column, key), coefficient in row.items():
                combine(collapsed, (column, canonical_key(key, phase_sensitive)), coefficient)
            result.append(collapsed)
        return result

    def basis_sum(row, column, address):
        terms = [(coefficient, ops[key].zero_state(address))
                 for (col, key), coefficient in row.items() if col == column]
        denominator = max((state[1] for _, state in terms), default=0)
        vector = [[0, 0] for _ in range(1 << N)]
        for coefficient, (state, den) in terms:
            for index, (a, b) in enumerate(state):
                scale = coefficient * (1 << (denominator - den))
                vector[index][0] += scale * a
                vector[index][1] += scale * b
        while denominator and all(a % 2 == b % 2 == 0 for a, b in vector):
            vector = [[a // 2, b // 2] for a, b in vector]
            denominator -= 1
        return vector, denominator

    def discrepancy(actual, wanted):
        # Different operator keys alone do not prove unequal linear combinations.
        # Search the complete 128-address basis for a physical Gaussian witness.
        for row in range(FIELDS):
            if actual[row] == wanted[row]:
                continue
            for column in sorted({col for col, _ in actual[row]} | {col for col, _ in wanted[row]}):
                for address in range(1 << N):
                    a, ad = basis_sum(actual[row], column, address)
                    b, bd = basis_sum(wanted[row], column, address)
                    den = max(ad, bd)
                    for target_address, (av, bv) in enumerate(zip(a, b)):
                        av = [x << (den - ad) for x in av]
                        bv = [x << (den - bd) for x in bv]
                        if av != bv:
                            return {"input_field": column, "input_address": address,
                                    "output_field": row, "output_address": target_address,
                                    "actual_gaussian_numerator": av,
                                    "expected_gaussian_numerator": bv,
                                    "common_denominator_exponent": den}
        raise CheckFailure("operator_key_mismatch_without_physical_witness")

    def accept(events, wanted, phase_sensitive=True):
        rows = replay(events)
        if collapse(rows, phase_sensitive) != collapse(wanted, phase_sensitive):
            raise CheckFailure("all_column_endpoint", discrepancy(rows, wanted))
        return rows

    def encode_rows(rows):
        return [[{"input_field": col, "operator": key, "integer_coefficient": coefficient}
                 for (col, key), coefficient in sorted(row.items())] for row in rows]

    def bill(events):
        histogram, signed_adds, negations, legs, nonidentity_legs = Counter(), 0, 0, 0, 0
        for event in events:
            if event["gate"] == "ADD":
                signed_adds += 1
            elif event["gate"] == "NEG":
                negations += 1
            else:
                record = lower(event["operator"])
                histogram[record["rank"]] += 1
                for side in ("right", "left"):
                    rec = record[side]
                    if rec is None:
                        continue
                    legs += 1
                    is_identity = (list(rec["matrix_rows"]) == [1 << i for i in range(N)]
                                   and rec["offset"] == rec["phase"] == 0
                                   and not any(rec["quadratic_rows"]) and not any(rec["linear_Z4"]))
                    nonidentity_legs += not is_identity
        return {"native_histogram": dict(sorted(histogram.items())),
                "native_calls": sum(histogram.values()),
                "native_rank_mass": sum(rank * count for rank, count in histogram.items()),
                "signed_complex_ADD": signed_adds, "complex_NEG": negations,
                "lowering_monomial_legs": legs,
                "nonidentity_lowering_monomial_legs": nonidentity_legs,
                "paid_whole_field_monomial_scan_upper_bound": legs,
                "literal_D_P_X_phase_pass_upper_bound": 4 * legs}

    receipts, programs = {}, {}
    histograms = {"open": {1: 8, 2: 40, 3: 16}, "reverse": {1: 20, 2: 56, 3: 4},
                  "bus": {1: 8, 2: 40, 3: 20}}

    def accept_bill(kind, costs):
        need(costs["native_histogram"] == histograms[kind], "complete_native_histogram")
        need(costs["signed_complex_ADD"] == (84 if kind == "bus" else 60), "complete_add_bill")
        need(costs["complex_NEG"] == (24 if kind == "bus" else 16), "complete_negation_bill")

    for kind in ("open", "reverse", "bus"):
        events, swaps, query_products = build(kind)
        variants = {"forward": events, "inverse": inverse_word(events), "dual": dual_word(events)}
        variants["dual_inverse"] = inverse_word(variants["dual"])
        orientations = {}
        for orientation, word in variants.items():
            wanted = expected(kind, orientation)
            actual = accept(word, wanted)
            costs = bill(word)
            accept_bill(kind, costs)
            orientations[orientation] = {"bill": costs, "events": word,
                                         "operator_endpoint": encode_rows(actual),
                                         "all_28_field_columns": True,
                                         "all_3584_address_basis_columns_by_exact_operator_identity": True}
        wanted = expected(kind, "forward")
        fixed_ranks = [lower(key)["rank"] for key in query_products]
        moved_ranks = [lower(next(iter(wanted[i]))[1])["rank"] for i in range(12)]
        helper_ranks = [lower(next(iter(wanted[24 + j]))[1])["rank"] for j in range(4)]
        need(moved_ranks == ([7] * 12 if kind == "reverse" else [5] * 12), "moved_source_widths")
        need(helper_ranks == ([3] * 4 if kind == "bus" else [0] * 4), "moved_helper_widths")
        if kind == "bus":
            need(fixed_ranks[24:] == [1] * 4, "fixed_id_helper_query_width_one")
        receipts[kind] = {"ordinary_helpers": 4 if kind == "bus" else 0,
                          "untouched_audit_spectators": 0 if kind == "bus" else 4,
                          "swap_expansions": swaps,
                          "whole_field_swap_count": len(swaps),
                          "raw_id_swap_count": sum(s["raw"] for s in swaps),
                          "fixed_physical_id_native_query_product_ranks": fixed_ranks,
                          "moved_source_diagonal_ranks": moved_ranks,
                          "moved_helper_diagonal_ranks": helper_ranks,
                          "orientations": orientations}
        programs[kind] = (events, swaps, wanted)

    # A blockwise exact identity, including all dirty-helper-to-public zeros.
    open_rows, bus_rows = expected("open", "forward"), expected("bus", "forward")
    need(open_rows[:24] == bus_rows[:24], "public_direct_sum_factor")
    need(all(all(col >= 24 for col, _ in row) for row in bus_rows[24:]), "helper_direct_sum_factor")
    need(all(all(col < 24 for col, _ in row) for row in bus_rows[:24]), "dirty_public_isolation")
    need(Counter(histograms["bus"]) - Counter(histograms["open"]) == Counter({3: 4}),
         "rank_three_marginal_histogram")
    # Restoring the helper's ID does not make its nonidentity channel free.
    # Supply and charge the literal optional tail when physical helper values
    # must return unchanged. This tail is outside the mass-148 boundary.
    restored_bus_word = [dict(event) for event in programs["bus"][0]]
    for j in range(4):
        H = E[0].adjoint().then(source_out[j])
        restored_bus_word.append({"gate": "NATIVE", "register": 24 + j,
                                 "operator": intern(H.adjoint()),
                                 "purpose": "paid_optional_helper_value_restore"})
    restored_variants = {"forward": restored_bus_word,
                         "inverse": inverse_word(restored_bus_word),
                         "dual": dual_word(restored_bus_word)}
    restored_variants["dual_inverse"] = inverse_word(restored_variants["dual"])
    restored_orientations = {}
    for orientation, word in restored_variants.items():
        rows = accept(word, expected("open", orientation))
        costs = bill(word)
        need(costs["native_histogram"] == {1: 8, 2: 40, 3: 24},
             "optional_helper_restore_histogram")
        need(costs["signed_complex_ADD"] == 84 and costs["complex_NEG"] == 24,
             "optional_helper_restore_scalar_bill")
        restored_orientations[orientation] = {
            "events": word, "operator_endpoint": encode_rows(rows), "bill": costs,
            "all_28_field_columns": True,
            "all_3584_address_basis_columns_by_exact_operator_identity": True}
    programs["bus_restored"] = (restored_bus_word, [], open_rows)

    controls = []

    def expect_rejection(name, kind, word, phase_sensitive=True):
        wanted = programs[kind][2]
        try:
            accept(word, wanted, phase_sensitive)
        except CheckFailure as error:
            need(error.code == "all_column_endpoint", "unexpected_control_failure", error.code)
            controls.append({"name": name, "kind": kind, "expected_failure": error.code,
                             "actual_physical_basis_witness": error.detail})
            return
        # Deliberately outside the catch: acceptance is a failed negative control.
        raise CheckFailure("expected_rejection_missing", name)

    for kind in ("open", "reverse", "bus"):
        events, swaps, _ = programs[kind]
        raw = next(s for s in swaps if s["raw"])
        bad = events[:raw["start"]] + events[raw["start"] + raw["length"]:]
        expect_rejection("omit_actual_raw_cleanup_swap", kind, bad)
        contact = next(s for s in swaps if not s["raw"])
        bad = [dict(e) for e in events]
        bad[contact["start"] + 1]["coefficient"] *= -1
        expect_rejection("actual_contact_swap_wrong_subtraction_sign", kind, bad)
        delivery = next(i for i, e in enumerate(events) if e["gate"] == "ADD" and e["purpose"] == "delivery")
        expect_rejection("omit_actual_delivery_ADD", kind, events[:delivery] + events[delivery + 1:])
        return_index = next(i for i, e in enumerate(events) if e["gate"] == "NATIVE" and e["purpose"] == "target_return")
        bad = [dict(e) for e in events]
        old = ops[bad[return_index]["operator"]]
        altered = old.then(ce.Op(N, ce.identity(N), [("phase", 1)]))
        need(old.tab == altered.tab and old.zero_state() != altered.zero_state(), "genuine_global_phase_control")
        bad[return_index]["operator"] = intern(altered)
        expect_rejection("actual_return_query_global_i_phase", kind, bad)
        # Reproduce loss of the semantic rejection when the phase-sensitive key
        # check is deleted. This calls the same gate and rejection oracle.
        accept(bad, programs[kind][2], phase_sensitive=False)
        try:
            expect_rejection("phase_check_deleted", kind, bad, phase_sensitive=False)
        except CheckFailure as error:
            need(error.code == "expected_rejection_missing", "phase_deletion_oracle_wrong_failure")
            controls.append({"name": "phase_check_deletion_detected", "kind": kind,
                             "expected_failure": error.code,
                             "phase_blind_acceptance_observed": True})
        else:
            raise CheckFailure("phase_deletion_oracle_not_exercised")
    bus_events = programs["bus"][0]
    contamination = {"gate": "ADD", "dst": 12, "src": 24, "coefficient": 1,
                     "purpose": "executed_bad_dirty_helper_to_public_ADD"}
    expect_rejection("actual_helper_to_public_contamination_ADD", "bus", bus_events + [contamination])
    expect_rejection("omit_actual_final_helper_inverse_query", "bus_restored", restored_bus_word[:-1])
    open_events = programs["open"][0]
    delivery_index = next(i for i, event in enumerate(open_events)
                          if event["gate"] == "ADD" and event["purpose"] == "delivery")
    positive = dict(open_events[delivery_index])
    negative = dict(positive)
    negative["coefficient"] *= -1
    cancelling_pair_word = open_events[:delivery_index] + [positive, negative] + open_events[delivery_index:]
    accept(cancelling_pair_word, programs["open"][2])
    cancelling_pair_bill = bill(cancelling_pair_word)
    try:
        accept_bill("open", cancelling_pair_bill)
    except CheckFailure as error:
        need(error.code == "complete_add_bill", "unexpected_cancelling_pair_invoice_failure")
        controls.append({"name": "actual_cancelling_pair_preserves_endpoint_but_breaks_invoice",
                         "kind": "open", "expected_failure": error.code,
                         "endpoint_acceptance_observed": True,
                         "claimed_signed_complex_ADD": 60, "actual_signed_complex_ADD": 62})
    else:
        raise CheckFailure("expected_cancelling_pair_invoice_rejection_missing")

    # Only catalog operators used in published words/endpoints, plus fixed frame
    # definitions. Intermediate replay-cache operators need not enlarge the receipt.
    catalog_keys = {intern(D), intern(F), *(intern(x) for x in E), *(intern(x) for x in V)}
    for receipt in receipts.values():
        for variant in receipt["orientations"].values():
            catalog_keys.update(e["operator"] for e in variant["events"] if e["gate"] == "NATIVE")
            catalog_keys.update(term["operator"] for row in variant["operator_endpoint"] for term in row)
    for variant in restored_orientations.values():
        catalog_keys.update(e["operator"] for e in variant["events"] if e["gate"] == "NATIVE")
        catalog_keys.update(term["operator"] for row in variant["operator_endpoint"] for term in row)
    catalog = {key: {"literal_circuit": ops[key].circuit, **fingerprints[key], "native_lowering": lower(key)}
               for key in sorted(catalog_keys)}
    result = {
        "schema": "fixed_d4_native_carriers.v1",
        "status": "PASS",
        "scientific_pin": SCIENTIFIC_PIN,
        "dependencies": {"geometry_sha256": GEOMETRY_SHA, "compiler_sha256": COMPILER_SHA},
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fixed_labels": G,
        "address_bits": N,
        "arbitrary_field_inputs": FIELDS,
        "address_basis_columns": FIELDS * (1 << N),
        "field_domain": "arbitrary Gaussian-rational 128-coordinate arrays; exact linear extension over C",
        "phase_gauge": "F = X_33 F_7; D includes phase -i",
        "frame_operator_keys": {"D": intern(D), "F": intern(F),
                                "E": [intern(x) for x in E], "V": [intern(x) for x in V]},
        "operator_catalog": catalog,
        "programs": receipts,
        "direct_sum_identity": "bus = OPEN on public fields direct_sum H_0 direct_sum H_1 direct_sum H_2 direct_sum H_3",
        "helper_channels": "H_j = F C_(G_B[j])^-1 E_A^-1; rank 3; arbitrary dirty helper preserved as an isolated transformed channel",
        "optional_physical_helper_value_restoration": {
            "orientations": restored_orientations,
            "identity": "bus followed by four paid H_j^-1 native queries equals OPEN direct_sum I_4",
            "inside_mass_148_boundary": False},
        "negative_controls": controls,
        "cost_contract": {
            "scalar_ADD": "one signed whole-field complex ADD",
            "scalar_NEG": "one whole-field complex negation",
            "SWAP": "three signed complex ADDs and one complex NEG, all executed",
            "normalizers": "all positive-rank native lowerings include both phase-bearing monomial legs",
            "monomial_scan_bound": "one paid abstract whole-field monomial map per leg; at most four literal D,P,X,phase map applications per leg; these are not physical tape-pass counts",
            "physical_tape_steps": "not claimed",
            "rounded_precision": "not claimed"},
        "limits": [
            "Fixed selected D4 geometry only; no claim covering omitted parent labels or other blocks.",
            "OPEN/reverse have 24 active arbitrary fields and 4 untouched arbitrary audit spectators.",
            "28 operator-valued field columns cover 3584 address-basis columns by exact Clifford operator identities, not 3584 enumerated simulations.",
            "Helper native rank 1 on a fixed physical query path differs from moved-value helper channel rank 3.",
            "Literal inverse and inverse-transpose dual of each declared raw boundary are covered; a separately normalized common-F inverse-B interface is not claimed here.",
            "All raw swaps, scalar operations and monomial scans remain charged.",
            "No physical access schedule, ownership allocation, rounded network, whole supplier, universal sharing obstruction, or kappa claim."
        ],
        "no_new_kappa": True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS: OPEN 136, reverse 144, four-helper bus 148; all 28 field columns; four orientations; executed controls")


if __name__ == "__main__":
    main()
