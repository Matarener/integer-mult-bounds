#!/usr/bin/env python3
"""Exact, bounded C02 geometry and isolated-contact replay.

Reconstructs the fixed historical order-three witness and source-batch DP.
Substantial OpenAI Codex assistance. No whole-caller admission is asserted.
"""
import argparse
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

N = 9
SIZE = 1 << N
C = SIZE - 1
O_COLUMNS = (451, 454, 453, 31, 55, 47, 248, 440, 376)
PORTS_SHA = "addf598581d2a20e13d0c18110607515ad90b06125616a2349e53a47bb5b6c80"
COMPILER_SHA = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"
ZERO = bytes(SIZE)
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def need(ok, message, enabled=True):
    if enabled and not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def captured(path, expected):
    raw = Path(path).read_bytes()
    need(digest(raw) == expected, "input SHA256")
    return raw


def compiler_from_bytes(raw):
    # Execute the already authenticated bytes, never reopen an import path.
    module = types.ModuleType("c02_authenticated_compiler")
    sys.modules[module.__name__] = module
    exec(compile(raw, "<authenticated-clifford-exact>", "exec",
                 dont_inherit=True, optimize=0), module.__dict__)
    return module


def dot(a, b):
    return (a & b).bit_count() & 1


def apply(columns, x):
    result = 0
    for i, v in enumerate(columns):
        if x >> i & 1:
            result ^= v
    return result


def span(values):
    result = {0}
    for x in values:
        result |= {v ^ x for v in result}
    return result


def basis(values):
    pivots = {}
    for x in values:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def orthonormal(values, prefix=()):
    """The original deterministic basis rule, including its alternating guard."""
    space = span(values)
    out = list(prefix)
    need(all(x in space for x in out), "prefix in subspace")
    need(all(dot(x, y) == int(i == j) for i, x in enumerate(out)
             for j, y in enumerate(out)), "orthonormal prefix")
    dimension = len(basis(values))
    while len(out) < dimension:
        for x in sorted(space):
            if not dot(x, x) or any(dot(x, y) for y in out):
                continue
            rest = [v for v in space if not dot(v, x)
                    and all(not dot(v, y) for y in out)]
            if len(out) + 1 < dimension and not any(dot(v, v) for v in rest):
                continue
            out.append(x)
            break
        else:
            raise ValueError("nonalternating orthonormal completion")
    need(span(out) == space, "orthonormal completion coverage")
    return tuple(out)


def accept_orthogonal(columns, enabled=True):
    need(all(dot(x, y) == int(i == j) for i, x in enumerate(columns)
             for j, y in enumerate(columns)), "O orthogonal", enabled)


def accept_partner(p, q, enabled=True):
    need(dot(p, p) == dot(q, q) == 1 and dot(p, q) == 0,
         "paired norm-one perpendicular ports", enabled)


def accept_frame(p, q, pt, qt, frame, omit_nondegenerate=False):
    space = span(frame)
    need(p in space and qt in space, "required contact span")
    need(all(not dot(x, q) and not dot(x, pt) for x in frame),
         "source and target caps")
    need(all(dot(x, y) == int(i == j) for i, x in enumerate(frame)
             for j, y in enumerate(frame)), "orthonormal contact frame",
         not omit_nondegenerate)


@lru_cache(None)
def frame_phase(frame):
    """All 512 exact eigenvalues i^phi; constant term zero fixes global phase."""
    # For an ON basis, wt(sum u(u.x)) = sum wt(u)(u.x) mod 4.
    phase = bytes(sum(u.bit_count() * dot(u, x) for u in frame) % 4
                  for x in range(SIZE))
    for x in range(SIZE):
        projection = 0
        for u in frame:
            if dot(u, x):
                projection ^= u
        need(phase[x] == projection.bit_count() % 4,
             "signed C word equals projector-weight phase")
    return phase


@lru_cache(None)
def phase_product(a, b):
    return bytes((x + y) % 4 for x, y in zip(a, b))


@lru_cache(None)
def phase_inverse(a):
    return bytes((-x) % 4 for x in a)


def transition(a, b):
    return phase_product(b, phase_inverse(a))


def polar(phase):
    alpha = [phase[1 << i] for i in range(N)]
    rows = [0] * N
    for i in range(N):
        rows[i] |= (alpha[i] & 1) << i
        for j in range(i + 1, N):
            difference = (phase[(1 << i) | (1 << j)] - alpha[i] - alpha[j]) % 4
            need(difference % 2 == 0, "quadratic phase polar parity")
            bit = difference // 2
            rows[i] |= bit << j
            rows[j] |= bit << i
    return tuple(rows), tuple(alpha)


@lru_cache(None)
def native_rank(phase):
    rows, _ = polar(phase)
    return len(basis(rows))


def phase_record(phase):
    rows, alpha = polar(phase)
    return {"sha256": digest(phase), "quadratic_rows": rows,
            "linear_Z4": alpha, "constant_Z4": phase[0],
            "native_rank": native_rank(phase)}


def intern_phase(inventory, values, phase, key=None):
    key = digest(phase) if key is None else key
    if key in values:
        need(values[key] == phase, "phase digest collision")
    else:
        values[key] = phase
        inventory[key] = phase_record(phase)
    return key


def add_row(target, source, coefficient):
    result = dict(target)
    for key, value in source.items():
        result[key] = result.get(key, 0) + coefficient * value
        if result[key] == 0:
            del result[key]
    return result


def move_row(row, operator):
    result = {}
    for (field, phase), value in row.items():
        key = (field, phase_product(operator, phase))
        result[key] = result.get(key, 0) + value
        if result[key] == 0:
            del result[key]
    return result


def expected_rows(source, target, cross, coefficient):
    return [{(0, source): 1},
            {(0, cross): coefficient, (1, target): 1},
            {(2, ZERO): 1}]


def contact_word(phases, coefficient, rank, mutation=None):
    p, qt, common, source_cap, target_cap = phases
    rows = [{(i, ZERO): 1} for i in range(3)]
    operations = []
    ranks = []

    def move(field, before, after, label):
        op = transition(before, after)
        rows[field] = move_row(rows[field], op)
        r = native_rank(op)
        if r:
            ranks.append(r)
        operations.append({"native": label, "field": field, "rank": r,
                           "phase_sha256": digest(op)})

    def add(target, source, sign):
        rows[target] = add_row(rows[target], rows[source], sign)
        operations.append({"add": [target, source, sign]})

    if rank == 1:
        add(1, 0, coefficient)
        move(0, p, source_cap, "source_exit")
        move(1, qt, target_cap, "target_exit")
    else:
        if mutation != "omit_precompensation":
            add(1, 2, -coefficient)
        move(0, p, common, "source_prepare")
        move(1, qt, common, "target_prepare")
        move(2, qt, common, "helper_prepare")
        add(2, 0, 1)
        add(1, 2, -coefficient if mutation == "wrong_delivery_sign" else coefficient)
        add(2, 0, -1)
        if mutation != "omit_helper_return":
            move(2, common, qt, "helper_return")
        move(0, common, source_cap, "source_exit")
        move(1, common, target_cap, "target_exit")
    if mutation == "global_phase":
        rows[1] = move_row(rows[1], bytes([1] * SIZE))
    if mutation == "extra_canceling_adds":
        add(1, 0, 1)
        add(1, 0, -1)
    return rows, operations, ranks


def actual_difference(actual, expected):
    """Return an actual Walsh-character input exposing unequal physical maps."""
    for field in range(3):
        for x in range(SIZE):
            real = imag = 0
            for row, sign in ((actual, 1), (expected, -1)):
                for (source, phase), coefficient in row.items():
                    if source == field:
                        a, b = UNITS[phase[x]]
                        real += sign * coefficient * a
                        imag += sign * coefficient * b
            if real or imag:
                return {"input_field": field, "character": x,
                        "difference_Gaussian": [real, imag]}
    return None


def accept_boundary(rows, expected, omit=None):
    for field in range(3):
        if rows[field] == expected[field]:
            continue
        witness = actual_difference(rows[field], expected[field])
        need(witness is None, f"physical boundary field {field}", omit != field)


def accept_invoice(operations, ranks, rank, enabled=True):
    expected = {7: 2} if rank == 1 else {rank - 1: 4, 8 - rank: 2}
    adds = sum("add" in item for item in operations)
    need(dict(Counter(ranks)) == expected and adds == (1 if rank == 1 else 4),
         "complete native and scalar invoice", enabled)


def accept_schedule(matrix, witness, omit_order=False):
    need(len(set(witness)) == len(witness), "distinct schedule vertices")
    need(all(not matrix[a][b] for i, a in enumerate(witness)
             for b in witness[i + 1:]), "triangular source-batch order",
         not omit_order)


def batched_maximum(ports, partners):
    matrix = [[dot(p, q) for q in partners] for p in ports]
    count = len(ports)
    zeros = [sum(1 << j for j in range(count) if i != j and not matrix[i][j])
             for i in range(count)]
    compat = [sum(1 << j for j in range(count)
                  if i != j and not (matrix[i][j] and matrix[j][i]))
              for i in range(count)]

    @lru_cache(None)
    def upper(mask):
        colors = 0
        while mask:
            colors += 1
            available = mask
            while available:
                bit = available & -available
                v = bit.bit_length() - 1
                mask ^= bit
                available ^= bit
                available &= ~compat[v]
        return colors

    @lru_cache(None)
    def solve(mask):
        if not mask:
            return ()
        choices = []
        left = mask
        while left:
            bit = left & -left
            left ^= bit
            v = bit.bit_length() - 1
            sub = mask & zeros[v]
            choices.append((upper(sub), sub.bit_count(), v, sub))
        choices.sort(reverse=True)
        best = ()
        for bound, _, v, sub in choices:
            if bound + 1 <= len(best):
                continue
            candidate = (v,) + solve(sub)
            if len(candidate) > len(best):
                best = candidate
        return best

    witness = solve((1 << count) - 1)
    accept_schedule(matrix, witness)
    need(len(witness) == 8, "fixed-O batched maximum eight")
    return matrix, {"maximum": len(witness), "witness": witness,
                    "states": solve.cache_info().misses,
                    "matrix": matrix, "matrix_sha256": digest(canonical(matrix))}


def rejection(name, rejected, deleted, message, details=None):
    try:
        rejected()
    except ValueError as exc:
        need(str(exc) == message, "unexpected mutation rejection")
    else:
        raise ValueError("mutation survived: " + name)
    deleted()
    return {"name": name, "rejected_by": message,
            "same_gate_deletion": "ACCEPTED", "witness": details}


def compiler_samples(ce, examples):
    def from_phase(phase):
        # Every sample is supplied with an actual signed-C circuit below.
        return polar(phase)[0]

    def frame_op(frame):
        out = ce.ident(N)
        for u in frame:
            sign = 1 if u.bit_count() % 4 == 1 else -1
            out = out.then(ce.cgate(N, u, sign))
        return out

    records = []
    full_basis = tuple(1 << i for i in range(N))
    for rank, item in sorted(examples.items()):
        p, q, pt, qt, common = item
        source_cap = orthonormal(full_basis, (q,))[1:]
        target_cap = orthonormal(full_basis, (pt,))[1:]
        steps = [((p,), common), ((qt,), common), (common, (qt,)),
                 (common, source_cap), (common, target_cap)]
        if rank == 1:
            steps = [((p,), source_cap), ((qt,), target_cap)]
        for before, after in steps:
            phase = transition(frame_phase(before), frame_phase(after))
            actual = frame_op(before).adjoint().then(frame_op(after))
            rows = tuple(x for x, _, _ in actual.tab[N:])
            need(rows == from_phase(phase), "compiler B-block equals exact phase polar")
            recipe, compiled = ce.lower_child(actual)
            need(recipe["rank"] == native_rank(phase), "compiler actual native rank")
            need(actual.tab == compiled.tab, "compiled signed Pauli images")
            need(actual.zero_state() == compiled.zero_state(), "compiled global phase")
            vec, den = actual.zero_state()
            # Full zero-state convolution column from all character eigenvalues.
            for z in range(SIZE):
                a = b = 0
                for x in range(SIZE):
                    s = -1 if dot(x, z) else 1
                    r, i = UNITS[phase[x]]
                    a += s * r
                    b += s * i
                need((vec[z][0] * SIZE, vec[z][1] * SIZE) ==
                     (a * (1 << den), b * (1 << den)),
                     "compiler complete phase-bearing convolution column")
            records.append({"contact_rank": rank, "before": before, "after": after,
                            "operator": phase_record(phase), "recipe": recipe,
                            "signed_Pauli_images": actual.tab,
                            "zero_state_denominator_exponent": den,
                            "zero_state_sha256": digest(canonical(vec))})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ports", required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    need(not output.exists(), "output must not exist")
    ports_raw = captured(args.ports, PORTS_SHA)
    compiler_raw = captured(args.compiler, COMPILER_SHA)
    ce = compiler_from_bytes(compiler_raw)
    ports = json.loads(gzip.decompress(ports_raw))["ports"]
    need(len(ports) == len(set(ports)) == 112, "all112 distinct ports")
    partners = [apply(O_COLUMNS, p) for p in ports]
    accept_orthogonal(O_COLUMNS)
    need(all(apply(O_COLUMNS, apply(O_COLUMNS, apply(O_COLUMNS, x))) == x
             for x in range(SIZE)), "O order three on all512 vectors")
    need(all(apply(O_COLUMNS, x) ^ apply(O_COLUMNS, apply(O_COLUMNS, x)) ==
             x ^ (C if dot(C, x) else 0) for x in range(SIZE)),
         "O plus transpose identity on all512 vectors")
    for p, q in zip(ports, partners):
        accept_partner(p, q)
    need(all(dot(p, r) == dot(q, s) for p, q in zip(ports, partners)
             for r, s in zip(ports, partners)), "complete112 squared partner Gram")
    full_basis = tuple(1 << i for i in range(N))
    full = frame_phase(full_basis)
    contracts = []
    for p, q in zip(ports, partners):
        residual = orthonormal(full_basis, (p, q))[2:]
        need(phase_product(phase_product(frame_phase((p,)), frame_phase((q,))),
                           frame_phase(residual)) == full,
             "complete paired phase factorization")
        contracts.append({"P": p, "Q": q, "R": residual})
    edges = []
    representatives = {}
    sample_phases = {}
    phase_inventory = {}
    phase_values = {}
    histogram = Counter()
    for source, p in enumerate(ports):
        q = partners[source]
        source_cap = phase_product(full, phase_inverse(frame_phase((q,))))
        for target, pt in enumerate(ports):
            if dot(p, pt):
                continue
            qt = partners[target]
            a, b = dot(p, qt), dot(q, pt)
            need(a ^ b == 1, "opposite cross pairings")
            if p == qt:
                common = (p,)
            elif not a:
                common = (p, qt)
            else:
                radical = p ^ qt
                extension = next(x for x in range(1, SIZE)
                                 if not dot(x, q) and not dot(x, pt)
                                 and dot(x, radical) and dot(x, qt ^ C))
                common = orthonormal((p, qt, extension), (qt,))
            accept_frame(p, q, pt, qt, common)
            rank = len(common)
            minimal = 1 if p == qt else 2 if not dot(p, qt) else 3
            need(rank == minimal, "minimal nondegenerate contact rank")
            phases = (frame_phase((p,)), frame_phase((qt,)), frame_phase(common),
                      source_cap,
                      phase_product(full, phase_inverse(frame_phase((pt,)))))
            expected_operators = (transition(phases[0], phases[3]),
                                  transition(phases[1], phases[4]),
                                  transition(phases[0], phases[4]))
            for coefficient in (-1, 1):
                rows, operations, ranks = contact_word(phases, coefficient, rank)
                expected = expected_rows(*expected_operators, coefficient)
                accept_boundary(rows, expected)
                accept_invoice(operations, ranks, rank)
            phase_ids = []
            for phase in phases + expected_operators:
                phase_ids.append(intern_phase(phase_inventory, phase_values, phase))
            edges.append({"source": source, "target": target,
                          "frame": common, "minimal_rank": rank,
                          "phase_ids": phase_ids,
                          "operations_coefficient_plus_one": operations,
                          "native_histogram": dict(Counter(ranks)),
                          "rank_mass": sum(ranks),
                          "whole_field_signed_adds": sum("add" in x for x in operations),
                          "both_coefficients": [-1, 1],
                          "physical_helper_return": True})
            histogram[rank] += 1
            if rank not in representatives:
                representatives[rank] = (p, q, pt, qt, common)
                sample_phases[rank] = phases
    need(len(edges) == 5824 and dict(histogram) == {1: 104, 2: 2912, 3: 2808},
         "complete edge coverage and rank histogram")
    matrix, scheduling = batched_maximum(ports, partners)
    controls = []
    bad = list(O_COLUMNS)
    bad[0] ^= 1
    controls.append(rejection("perturb_O", lambda: accept_orthogonal(bad),
                              lambda: accept_orthogonal(bad, False), "O orthogonal"))
    controls.append(rejection("self_partner", lambda: accept_partner(ports[0], ports[0]),
                              lambda: accept_partner(ports[0], ports[0], False),
                              "paired norm-one perpendicular ports"))
    p, q, pt, qt, common = representatives[3]
    controls.append(rejection(
        "omit_rank_three_extension", lambda: accept_frame(p, q, pt, qt, (p, qt)),
        lambda: accept_frame(p, q, pt, qt, (p, qt), True),
        "orthonormal contact frame", {"nonzero_radical": p ^ qt}))
    witness = scheduling["witness"]
    bad_schedule = next(tuple(reversed(witness[:i])) + witness[i:]
                        for i in range(2, len(witness) + 1)
                        if any(matrix[a][b] for j, a in enumerate(
                            tuple(reversed(witness[:i])) + witness[i:])
                            for b in (tuple(reversed(witness[:i])) + witness[i:])[j + 1:]))
    controls.append(rejection("reverse_schedule_prefix",
                              lambda: accept_schedule(matrix, bad_schedule),
                              lambda: accept_schedule(matrix, bad_schedule, True),
                              "triangular source-batch order", list(bad_schedule)))
    for rank in (2, 3):
        phases = sample_phases[rank]
        expected = expected_rows(transition(phases[0], phases[3]),
                                 transition(phases[1], phases[4]),
                                 transition(phases[0], phases[4]), 1)
        for mutation, field in (("omit_helper_return", 2), ("omit_precompensation", 1),
                                ("wrong_delivery_sign", 1), ("global_phase", 1)):
            rows, _, _ = contact_word(phases, 1, rank, mutation)
            difference = actual_difference(rows[field], expected[field])
            need(difference is not None, "mutation has actual physical witness")
            controls.append(rejection(
                f"rank{rank}_{mutation}",
                lambda rows=rows, expected=expected: accept_boundary(rows, expected),
                lambda rows=rows, expected=expected, field=field:
                    accept_boundary(rows, expected, field),
                f"physical boundary field {field}", difference))
        rows, operations, ranks = contact_word(phases, 1, rank, "extra_canceling_adds")
        accept_boundary(rows, expected)
        controls.append(rejection(
            f"rank{rank}_omit_scalar_invoice",
            lambda: accept_invoice(operations, ranks, rank),
            lambda: accept_invoice(operations, ranks, rank, False),
            "complete native and scalar invoice"))
    need(len(controls) == 14, "complete control inventory")
    compiler_records = compiler_samples(ce, representatives)
    # A separately declared old screening model, with a changed helper terminal.
    old_helpers = len(edges) - histogram[1]
    old_helper_mass = old_helpers * 7
    old_data_mass = 2 * len(ports) * 7
    old_total_mass = old_helper_mass + old_data_mass
    need(all(not dot(partners[row["source"]], partners[row["target"]])
             for row in edges), "alternative helper entrance inside terminal cap")
    need(9 * old_total_mass > 65 * 896, "alternative terminal zero-rate obstruction")
    receipt = {
        "status": "PASS_FIXED_9D_GEOMETRY_AND_RESTORED_ISOLATED_CONTACTS",
        "inputs": {"ports_sha256": PORTS_SHA, "compiler_sha256": COMPILER_SHA},
        "dimension": N, "O_columns": O_COLUMNS, "O_order": 3,
        "ports": ports, "partners": partners, "contracts": contracts,
        "geometry_contracts_sha256": digest(canonical(contracts)),
        "edge_rank_counts": dict(histogram), "edge_witnesses": edges,
        "phase_operators": phase_inventory, "batched_source_screen": scheduling,
        "compiler_lowering_samples": compiler_records,
        "controls": controls,
        "alternative_terminal_screen": {
            "scope": "Fixed old 65-dimensional, 896/9 productive-call model; one separate helper per nondirect edge",
            "helper_entrance": "Q_t", "helper_terminal": "Q_s perpendicular",
            "literal_helper_return": False, "helper_residual_rank": 7,
            "helpers": old_helpers, "helper_rank_mass": old_helper_mass,
            "data_rank_mass": old_data_mass, "total_rank_mass_lower_bound": old_total_mass,
            "zero_rate_capacity_numerator": 65 * 896, "zero_rate_capacity_denominator": 9,
            "positive_difference_numerator": 9 * old_total_mass - 65 * 896,
            "decision": "FAIL_EVEN_BEFORE_OTHER_PAID_WORK",
            "not_the_restored_contact_contract": True},
        "coverage": {"partners": 112, "partner_Gram_entries": 12544,
                     "ambient_vectors": 512, "edges": 5824,
                     "contact_coefficients": [-1, 1], "fields": 3,
                     "all_phase_character_values": 512,
                     "compiler_lowering_samples": len(compiler_records),
                     "production_rejections": len(controls),
                     "executed_guard_deletions": len(controls)},
        "limits": [
            "All contacts are isolated arbitrary-input words; shared edge interleavings are not certified.",
            "The DP maximum concerns this fixed O and source-batched triangular-zero model only.",
            "No old helper inventory, global supplier, caller recurrence or all-size improvement is admitted.",
            "All-edge exact character replay and rank proof are distinct from representative compiler lowerings.",
            "No formal proof-kernel certificate is claimed."
        ]}
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "edges": len(edges),
                      "maximum": scheduling["maximum"],
                      "controls": len(controls), "output_sha256": digest(output.read_bytes())}))


if __name__ == "__main__":
    main()
