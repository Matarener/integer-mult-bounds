#!/usr/bin/env python3
"""Source-bound P104 open consumer interface, independently reconstructed.

Prepared by Clear1nsight, with substantial OpenAI assistance.
No predecessor executable or primary producer/model module is imported.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path


WORD_SHA256 = "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50"
NATIVE_SHA256 = "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d"
N = 512
BITS = 9
STOP = 4516
FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)
QUERY = (364,)
OLD = (256, 136, 64, 40, 16, 4, 2, 1)
Y_NAMES = tuple(f"Y{i}" for i in (*range(22, 33), *range(63, 104)))
D_NAMES = tuple(f"D{i}" for i in range(27, 32))
G_NAMES = tuple(f"G{i}" for i in range(27, 32))
ROLES = frozenset((*Y_NAMES, *D_NAMES, "Q7", *G_NAMES))
ZERO = (0, 0)
ONE = (1, 0)
PI = (1, 1)


class Rejected(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Rejected(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def mul(z, w):
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def unit(z, power):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def pi_power(exponent):
    out = ONE
    for _ in range(exponent):
        out = mul(out, PI)
    return out


PI_POWERS = tuple(pi_power(k) for k in range(BITS + 1))


def encode(coefficients):
    need(len(coefficients) == N, "encoder dimension")
    out = [mul(z, PI_POWERS[i.bit_count()]) for i, z in enumerate(coefficients)]
    for j in range(BITS):
        bit = 1 << j
        for i in range(N):
            if i & bit:
                a, b = out[i], out[i ^ bit]
                out[i] = a[0] + b[0], a[1] + b[1]
    return out


def decode(values):
    need(len(values) == N, "decoder dimension")
    out = list(values)
    for j in range(BITS):
        bit = 1 << j
        for i in range(N):
            if i & bit:
                a, b = out[i], out[i ^ bit]
                out[i] = a[0] - b[0], a[1] - b[1]
    for i, z in enumerate(out):
        a, b = z
        for _ in range(i.bit_count()):
            need((a + b) % 2 == 0 and (b - a) % 2 == 0, f"Newton divisibility at coefficient {i}")
            a, b = (a + b) // 2, (b - a) // 2
        out[i] = a, b
    return out


def in_scaled_B(values, scalar):
    need(all(a % scalar == 0 and b % scalar == 0 for a, b in values), f"entry divisibility by {scalar}")
    return decode([(a // scalar, b // scalar) for a, b in values])


def invert_rows(rows):
    work = [row | (1 << (BITS + i)) for i, row in enumerate(rows)]
    for j in range(BITS):
        pivots = [i for i in range(j, BITS) if (work[i] >> j) & 1]
        need(bool(pivots), "singular wrapper address matrix")
        i = pivots[0]
        work[i], work[j] = work[j], work[i]
        for i in range(BITS):
            if i != j and ((work[i] >> j) & 1):
                work[i] ^= work[j]
    need([row & (N - 1) for row in work] == [1 << i for i in range(BITS)], "wrapper inverse reduction")
    return [row >> BITS for row in work]


def row_apply(rows, value):
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(rows))


class Wrapper:
    def __init__(self, raw):
        need(set(raw) == {"matrix_rows", "offset", "linear_Z4", "quadratic_rows", "phase"}, "wrapper schema")
        self.raw = raw
        self.rows = raw["matrix_rows"]
        self.linear = raw["linear_Z4"]
        self.quadratic = raw["quadratic_rows"]
        need(len(self.rows) == len(self.linear) == len(self.quadratic) == BITS, "wrapper width")
        need(all(type(a) is int and 0 <= a < N for a in self.rows + self.quadratic), "wrapper binary masks")
        need(all(type(a) is int and 0 <= a < 4 for a in self.linear), "wrapper linear phase")
        need(type(raw["offset"]) is int and 0 <= raw["offset"] < N, "wrapper offset")
        need(type(raw["phase"]) is int and 0 <= raw["phase"] < 4, "wrapper global phase")
        self.inverse = invert_rows(self.rows)
        self.permutation = [row_apply(self.rows, x) ^ raw["offset"] for x in range(N)]
        need(len(set(self.permutation)) == N, "wrapper permutation")
        self.phases = [self.phase(x) for x in range(N)]
        self.pauli_cache = {}

    def phase(self, x):
        phase = self.raw["phase"]
        for j in range(BITS):
            if (x >> j) & 1:
                phase += self.linear[j]
                phase += 2 * (self.quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
        return phase % 4

    def apply(self, values):
        out = [ZERO] * N
        for i, z in enumerate(values):
            out[self.permutation[i]] = unit(z, self.phases[i])
        return out

    def pauli(self, value):
        """W P(u,v,k) W^-1, P|x> = i^k (-1)^(v.x) |x xor u>."""
        if value in self.pauli_cache:
            return self.pauli_cache[value]
        u, v, k = value
        shifted_v = v
        for j in range(BITS):
            if ((u >> j) & 1) and (self.linear[j] & 1):
                shifted_v ^= 1 << j
            neighbors = 0
            for h in range(BITS):
                if h != j and ((self.quadratic[min(j, h)] >> max(j, h)) & 1):
                    neighbors ^= ((u >> h) & 1)
            if neighbors:
                shifted_v ^= 1 << j
        out_v = 0
        for j in range(BITS):
            if (shifted_v >> j) & 1:
                out_v ^= self.inverse[j]
        out_u = row_apply(self.rows, u)
        out_k = (k + self.phase(u) - self.phase(0) + 2 * (out_v & self.raw["offset"]).bit_count()) % 4
        out = out_u, out_v, out_k
        # This independent, finite basis comparison authenticates the formula
        # for each Pauli actually encountered by the path certificate.
        for x in range(N):
            y = self.permutation[x]
            need(self.permutation[x ^ u] == (y ^ out_u), "Pauli wrapper address action")
            left_phase = self.phases[x ^ u] - self.phases[x] + k + 2 * (v & x).bit_count()
            right_phase = out_k + 2 * (out_v & y).bit_count()
            need((left_phase - right_phase) % 4 == 0, "Pauli wrapper phase action")
        self.pauli_cache[value] = out
        return out


def normalize_dyadic(values, denominator_power):
    while denominator_power and all((a & 1) == 0 and (b & 1) == 0 for a, b in values):
        values = [(a // 2, b // 2) for a, b in values]
        denominator_power -= 1
    return values, denominator_power


def c_numerators(a, b):
    ar, ai = a
    br, bi = b
    return ((ar + br - ai + bi, ai + bi + ar - br),
            (ar + br + ai - bi, ai + bi - ar + br))


def floor_pair(a, b):
    dr, di = a[0] - b[0], a[1] - b[1]
    sr, si = b[0] + dr // 2, b[1] + di // 2
    rr, ri = -di, dr
    out_b = sr - rr // 2, si - ri // 2
    return (out_b[0] + rr, out_b[1] + ri), out_b


class Native:
    def __init__(self, raw, wrapper_cache):
        need(set(raw) == {"left", "rank", "right"}, "native recipe schema")
        need(type(raw["rank"]) is int and 0 <= raw["rank"] <= BITS, "native rank")
        self.raw = raw
        self.rank = raw["rank"]
        pair = []
        for side in ("right", "left"):
            key = digest(raw[side])
            if key not in wrapper_cache:
                wrapper_cache[key] = Wrapper(raw[side])
            pair.append(wrapper_cache[key])
        self.right, self.left = pair

    def pauli(self, value):
        u, v, k = self.right.pauli(value)
        mask = (1 << self.rank) - 1
        u ^= v & mask
        k = (k + 3 * (v & mask).bit_count()) % 4
        return self.left.pauli((u, v, k))

    def dyadic(self, values, denominator_power=0):
        out = self.right.apply(values)
        for j in range(self.rank):
            bit = 1 << j
            for i in range(N):
                if not i & bit:
                    out[i], out[i | bit] = c_numerators(out[i], out[i | bit])
            denominator_power += 1
        return normalize_dyadic(self.left.apply(out), denominator_power)

    def integral(self, values, counts, domain_scale=1):
        out = self.right.apply(values)
        in_scaled_B(out, domain_scale)
        counts["complete_wrapper_domain_checks"] += 1
        for j in range(self.rank):
            bit = 1 << j
            for i in range(N):
                if not i & bit:
                    a, b = out[i], out[i | bit]
                    numerator_a, numerator_b = c_numerators(a, b)
                    need(all(x % 2 == 0 for x in (*numerator_a, *numerator_b)), "literal native Gaussian division")
                    exact = tuple((z[0] // 2, z[1] // 2) for z in (numerator_a, numerator_b))
                    need(exact == floor_pair(a, b), "literal signed-floor disagreement")
                    out[i], out[i | bit] = exact
                    counts["native_pair_comparisons"] += 1
            in_scaled_B(out, domain_scale)
            counts["complete_coordinate_domain_checks"] += 1
        out = self.left.apply(out)
        in_scaled_B(out, domain_scale)
        counts["complete_wrapper_domain_checks"] += 1
        return out


def read_inputs(word_path, native_path):
    word_path, native_path = Path(word_path), Path(native_path)
    need(word_path.stat().st_size <= 1_000_000, "WORD byte bound")
    need(native_path.stat().st_size <= 1_000_000, "NATIVE compressed byte bound")
    word_bytes, native_bytes = word_path.read_bytes(), native_path.read_bytes()
    need(hashlib.sha256(word_bytes).hexdigest() == WORD_SHA256, "WORD SHA256")
    need(hashlib.sha256(native_bytes).hexdigest() == NATIVE_SHA256, "NATIVE SHA256")
    with gzip.GzipFile(fileobj=io.BytesIO(native_bytes)) as stream:
        inflated = stream.read(16_000_001)
    need(len(inflated) <= 16_000_000, "NATIVE inflated byte bound")
    word, native = json.loads(word_bytes), json.loads(inflated)
    need(word["chart"] == "Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)", "literal chart")
    need(native["chart"] == word["chart"], "matching native chart")
    need(len(word["program"]) == 5398, "literal word length")
    frames = {key: tuple(value) for key, value in word["initial_frames"].items()}
    for i, event in enumerate(word["program"][:STOP + 1]):
        op, role = event[:2]
        if op == "transport":
            need(frames[role] == tuple(event[2]), f"old frame at event {i}")
            frames[role] = tuple(event[3])
        elif op == "sign":
            need(Fraction(event[2]) == -1 and frames[role] == tuple(event[3]), f"sign frame at event {i}")
        elif op == "add":
            need(frames[role] == frames[event[2]] == tuple(event[4]), f"ADD frame at event {i}")
        elif op == "zero":
            need(role not in frames, f"private freshness at event {i}")
            frames[role] = tuple(event[2])
        elif op == "erase":
            need(frames.pop(role) == tuple(event[2]), f"erase frame at event {i}")
        else:
            raise Rejected(f"unexpected opcode at event {i}")
    need(all(tuple(word["initial_frames"][role]) == () for role in ROLES), "initial interface frames")
    need(all(frames[role] == FULL for role in ROLES), "all63 final physical frames")
    entries = {}
    for record in native["transports"]:
        for i in record["events"]:
            need(i not in entries, "duplicate native occurrence")
            entries[i] = record
    wrapper_cache = {}
    recipe_cache = {}
    bound = {}
    for i, event in enumerate(word["program"][:STOP + 1]):
        if event[0] != "transport" or not (event[1] in ROLES or 2025 <= i <= 2039):
            continue
        need(i in entries, f"missing native occurrence {i}")
        record = entries[i]
        need(record["old"] == event[2] and record["new"] == event[3], f"native frame binding {i}")
        need(record["recipe"]["rank"] == event[4], f"native rank binding {i}")
        key = digest(record["recipe"])
        if key not in recipe_cache:
            recipe_cache[key] = Native(record["recipe"], wrapper_cache)
        bound[i] = recipe_cache[key]
    return word, bound, wrapper_cache


def extract(word):
    program = word["program"]
    for i, event in enumerate(program[:STOP + 1]):
        if event[0] == "add" and ((event[1] == "C" and event[2] in ROLES)
                                  or (event[1] in ROLES and event[2] == "C")):
            need(2025 <= i <= 2039, "all selected/private interactions belong to the retained collector")
    closed = [i for i, event in enumerate(program[:STOP + 1])
              if (event[1] in ROLES and event[0] in ("transport", "sign", "add")) or 2025 <= i <= 2039]
    ports = [i for i, event in enumerate(program[:STOP + 1])
             if event[0] == "add" and event[2] in ROLES and event[1] not in ROLES and event[1] != "C"]
    for i in closed:
        event = program[i]
        if event[0] == "add":
            need(event[2] in ROLES or event[2] == "C", f"unbound incoming source {i}")
        need(event[0] != "sign", "unexpected selected sign")
    need(len(closed) == 576 and len(ports) == 675, "source cone counts")
    need(len(set(closed) & set(ports)) == 0, "closed/port overlap")
    return closed, ports


def same_operator(candidate, reference, context):
    need(candidate["paulis"] == reference["paulis"], f"Pauli path action: {context}")
    need(candidate["anchor"] == reference["anchor"], f"global path phase: {context}")


def certify_paths(word, bound, closed):
    generators = [(1 << j, 0, 0) for j in range(BITS)] + [(0, 1 << j, 0) for j in range(BITS)]
    anchor = [ONE] + [ZERO] * (N - 1)
    potentials = {(): {"paulis": generators, "anchor": (anchor, 0), "path": []}}
    edge_records = []
    redundant = 0
    for i in closed:
        event = word["program"][i]
        if event[0] != "transport":
            continue
        old, new = tuple(event[2]), tuple(event[3])
        need(old in potentials, f"disconnected actual frame path at {i}")
        previous = potentials[old]
        native = bound[i]
        candidate = {
            "paulis": [native.pauli(p) for p in previous["paulis"]],
            "anchor": native.dyadic(*previous["anchor"]),
            "path": previous["path"] + [i],
        }
        if new in potentials:
            same_operator(candidate, potentials[new], f"event {i}")
            redundant += 1
        else:
            potentials[new] = candidate
        edge_records.append({"event": i, "old": list(old), "new": list(new), "recipe_sha256": digest(native.raw)})
    need(FULL in potentials and QUERY in potentials and OLD in potentials, "required frame potentials")
    # A genuine source-shaped global phase corruption must be detected even
    # though it has identical action on all Pauli generators.
    mutated_raw = json.loads(json.dumps(bound[2033].raw))
    mutated_raw["left"]["phase"] = (mutated_raw["left"]["phase"] + 1) % 4
    mutated = Native(mutated_raw, {})
    start = potentials[QUERY]
    candidate = {"paulis": [mutated.pauli(p) for p in start["paulis"]],
                 "anchor": mutated.dyadic(*start["anchor"])}
    need(candidate["paulis"] == potentials[OLD]["paulis"], "phase control calibration")
    try:
        same_operator(candidate, potentials[OLD], "mutated event2033 phase")
    except Rejected as error:
        need(str(error).startswith("global path phase"), "phase control diagnostic")
    else:
        raise Rejected("phase-only path mutation accepted")
    return potentials, {
        "status": "PASS_ALL_ACTUAL_FRAME_PATHS",
        "method": "18 Pauli generator images plus exact nonzero dyadic anchor column",
        "native_occurrences": len(edge_records),
        "distinct_frames": len(potentials),
        "redundant_path_equalities": redundant,
        "native_edge_manifest_sha256": digest(edge_records),
        "frame_potentials_sha256": digest([
            {"frame": list(frame), "paulis": value["paulis"], "anchor": value["anchor"], "path": value["path"]}
            for frame, value in sorted(potentials.items())]),
        "actual_return_global_phase_control": "REJECT_GLOBAL_PATH_PHASE_WITH_IDENTICAL_PAULI_ACTION",
        "query_frame_path": potentials[QUERY]["path"],
        "full_frame_path": potentials[FULL]["path"],
    }


def apply_path(values, path, bound):
    denominator = 0
    out = list(values)
    for i in path:
        out, denominator = bound[i].dyadic(out, denominator)
    return out, denominator


def verify_full_frame_tensor(potentials):
    """Independently bind Delta_F to the tensor product of inverse C gates."""
    generators = [(1 << j, 0, 0) for j in range(BITS)] + [(0, 1 << j, 0) for j in range(BITS)]
    paulis = [(u ^ v, v, (k + v.bit_count()) % 4) for u, v, k in generators]
    values = [ONE] + [ZERO] * (N - 1)
    for j in range(BITS):
        bit = 1 << j
        for i in range(N):
            if not i & bit:
                (ar, ai), (br, bi) = values[i], values[i | bit]
                values[i] = ar + br + ai - bi, ai + bi - ar + br
                values[i | bit] = ar + br - ai + bi, ai + bi + ar - br
    candidate = {"paulis": paulis, "anchor": normalize_dyadic(values, BITS)}
    same_operator(candidate, potentials[FULL], "full-frame tensor C inverse")
    return {
        "physical_operator": "A_F = (C^-1) tensor-power 9 for the authenticated actual full-frame path",
        "coefficient_operator": "E^-1 A_F E = [[1,i],[0,-i]] tensor-power 9",
        "proof_certificate": "equal 18-generator Pauli action and exact nonzero anchor",
    }


def conjugated_matrix(path, bound):
    hasher = hashlib.sha256()
    max_component = 0
    nonzero = 0
    first_column = None
    for s in range(N):
        # This is one complete column of E, derived without calling encode.
        encoded = [PI_POWERS[s.bit_count()] if x & s == s else ZERO for x in range(N)]
        native_values, denominator = apply_path(encoded, path, bound)
        need(denominator == 0, "conjugated map Gaussian integrality")
        column = decode(native_values)
        nonzero += sum(z != ZERO for z in column)
        max_component = max(max_component, max(max(abs(a), abs(b)) for a, b in column))
        hasher.update(json.dumps(column, separators=(",", ":")).encode() + b"\n")
        if s == 0:
            first_column = column
    return {"columns": N, "nonzero_entries": nonzero, "maximum_absolute_component": max_component,
            "column_json_lines_sha256": hasher.hexdigest()}, first_column


def scale_array(values, coefficient):
    coefficient = Fraction(coefficient)
    numerator, denominator = coefficient.numerator, coefficient.denominator
    need(all((a * numerator) % denominator == 0 and (b * numerator) % denominator == 0 for a, b in values),
         "whole-array coefficient Gaussian integrality")
    return [(a * numerator // denominator, b * numerator // denominator) for a, b in values]


def add_arrays(left, right):
    return [(a[0] + b[0], a[1] + b[1]) for a, b in zip(left, right, strict=True)]


def symbolic_rows(program, closed, ports):
    """Integer rows: each Y symbol is its INITIAL value divided by four."""
    names = sorted(ROLES)
    index = {role: i for i, role in enumerate(names)}
    rows = {role: [((4 if role in Y_NAMES else 1) if i == index[role] else 0) for i in range(len(names))]
            for role in names}
    initial = {role: list(row) for role, row in rows.items()}
    port_set = set(ports)
    port_rows = []
    totals = {}
    for i in sorted(closed + ports):
        event = program[i]
        op, role = event[:2]
        if op == "transport":
            # The independent operator path certificate is established first.
            continue
        if op == "zero":
            need(role not in rows, "symbolic private freshness")
            rows[role] = [0] * len(names)
        elif op == "erase":
            need(not any(rows.pop(role)), "symbolic private erase")
        elif op == "add":
            coefficient = Fraction(event[3])
            raw = [coefficient.numerator * v for v in rows[event[2]]]
            need(all(v % coefficient.denominator == 0 for v in raw), "normalized initial-symbol division")
            increment = [v // coefficient.denominator for v in raw]
            if i in port_set:
                port_rows.append({"event": i, "target": role, "source": event[2],
                                  "coefficient": str(coefficient), "frame": event[4],
                                  "initial_symbol_row": {name: v for name, v in zip(names, increment) if v}})
                previous = totals.setdefault(role, [0] * len(names))
                totals[role] = [a + b for a, b in zip(previous, increment, strict=True)]
            else:
                rows[role] = [a + b for a, b in zip(rows[role], increment, strict=True)]
        else:
            raise Rejected(f"unexpected symbolic opcode {op}")
    return names, initial, rows, port_rows, totals


def certify_symbolic_interface(word, closed, ports):
    names, initial, rows, port_rows, totals = symbolic_rows(word["program"], closed, ports)
    need(rows == initial, "63-bank final restoration in authenticated frame gauges")
    x_rows = {role: row for role, row in totals.items() if role.startswith("X")}
    need(len(x_rows) == 52, "external X-port channel width")
    signs = {}
    for role, row in x_rows.items():
        values = {row[j] for j, name in enumerate(names) if name in Y_NAMES}
        need(values in ({2}, {-2}), "external X-port uniform Y channel")
        need(all(v == 0 for name, v in zip(names, row) if name not in Y_NAMES), "external X-port dirty cancellation")
        signs[role] = next(iter(values)) // 2
    changed_program = [list(event) for event in word["program"]]
    need(changed_program[2162] == ["add", "D28", "Y103", "-1/4", list(FULL)], "actual quarter control target")
    changed_program[2162][3] = "1/4"
    _, changed_initial, changed_rows, _, _ = symbolic_rows(changed_program, closed, ports)
    need(changed_rows != changed_initial, "wrong actual quarter sign accepted")
    delta = [a - b for a, b in zip(changed_rows["D28"], changed_initial["D28"], strict=True)]
    need({name: v for name, v in zip(names, delta) if v} == {"Y103": 2}, "wrong quarter sign residual")
    return {
        "status": "PASS_EXACT_OPEN_INTERFACE_ROWS",
        "symbol_convention": "Y symbol = initial Y / 4; other symbol = initial bank, all in B_9",
        "persistent_banks_restored_in_full_frame": sorted(ROLES),
        "external_port_count": len(port_rows),
        "external_port_records": port_rows,
        "external_port_records_sha256": digest(port_rows),
        "external_port_counts_by_source_family": dict(Counter(row["source"][0] for row in port_rows)),
        "external_port_counts_by_target_family": dict(Counter(row["target"][0] for row in port_rows)),
        "external_port_coefficient_counts": dict(Counter(row["coefficient"] for row in port_rows)),
        "gauge_normalized_X_port_operator": {
            "target_signs": dict(sorted(signs.items())),
            "input_sources": list(Y_NAMES),
            "coefficient_on_each_original_Y": "target_sign / 2",
            "scalar_52_by_52_bank_matrix_rank_over_Q_i": 1,
            "expanded_512_entry_array_map_rank_over_Q_i": 512,
            "dirty_D_Q_G_coefficients": "all zero",
            "scope": "sum of frame-normalized outgoing ports; omitted external bank histories and terminal states are not executed",
        },
        "wrong_actual_quarter_sign_control": {
            "event": 2162, "original": "-1/4", "mutation": "1/4",
            "result": "REJECT_D28_RESTORATION",
            "residual_on_initial_Y103": "1/2",
            "lattice_admission_unchanged": True,
        },
    }


def dense_open_replay(word, bound, closed, ports, potentials):
    coefficients = {}
    initial = {}
    for role in sorted(ROLES):
        tag = int.from_bytes(hashlib.sha256(role.encode()).digest()[:4], "big")
        c = [(((17 * j + tag + (j >> 2)) % 7) - 3, ((11 * j + tag + (j >> 3)) % 9) - 4) for j in range(N)]
        coefficients[role] = c
        initial[role] = scale_array(encode(c), 4 if role in Y_NAMES else 1)
        in_scaled_B(initial[role], 4 if role in Y_NAMES else 1)
    states = {role: list(values) for role, values in initial.items()}
    counts = Counter()
    port_set = set(ports)
    port_hash = hashlib.sha256()
    milestone_hashes = {}
    max_state_component = max(max(abs(a), abs(b)) for values in states.values() for a, b in values)
    for i in sorted(closed + ports):
        event = word["program"][i]
        op, role = event[:2]
        if op == "transport":
            states[role] = bound[i].integral(states[role], counts, 4 if role in Y_NAMES else 1)
        elif op == "zero":
            need(role not in states, "dense private freshness")
            states[role] = [ZERO] * N
            counts["private_zero_allocations"] += 1
        elif op == "erase":
            need(states.pop(role) == [ZERO] * N, "dense literal private erase")
            counts["private_literal_zero_erasures"] += 1
        elif op == "add":
            increment = scale_array(states[event[2]], event[3])
            decode(increment)
            if i in port_set:
                counts["computed_external_increment_arrays"] += 1
                port_hash.update(json.dumps([i, increment], separators=(",", ":")).encode() + b"\n")
            else:
                states[role] = add_arrays(states[role], increment)
                in_scaled_B(states[role], 4 if role in Y_NAMES else 1)
                counts["executed_internal_array_adds"] += 1
        else:
            raise Rejected(f"unexpected dense opcode {op}")
        if role in states and i not in port_set:
            max_state_component = max(max_state_component, max(max(abs(a), abs(b)) for a, b in states[role]))
        if i in (2039, 2480, 3056, 4173, 4516):
            milestone_hashes[str(i)] = digest({role: states[role] for role in sorted(ROLES)})
    expected = {}
    for role in sorted(ROLES):
        values, denominator = apply_path(initial[role], potentials[FULL]["path"], bound)
        need(denominator == 0, "dense expected final Gaussian integrality")
        need(states[role] == values, f"dense final transported restoration {role}")
        expected[role] = values
    need(counts["native_pair_comparisons"] == 148736, "dense pair count")
    need(counts["computed_external_increment_arrays"] == 675, "dense external increment count")
    need(counts["executed_internal_array_adds"] == 182, "dense internal ADD count")
    return {
        "status": "PASS_DENSE_CHRONOLOGICAL_OPEN_REPLAY",
        "fixture": "all63 banks nonzero signed deterministic Gaussian Newton coefficients",
        "initial_values_sha256": digest(initial),
        "initial_coefficients_sha256": digest(coefficients),
        "final_values_sha256": digest(states),
        "external_increment_json_lines_sha256": port_hash.hexdigest(),
        "milestone_state_hashes": milestone_hashes,
        "observed_maximum_absolute_internal_component": max_state_component,
        "counts": dict(counts),
        "external_execution_scope": "actual source increments computed and checked; recipient updates and omitted external histories are not simulated",
    }


def verify_consumer(word_path, native_path):
    word, bound, wrappers = read_inputs(word_path, native_path)
    closed, ports = extract(word)
    potentials, path_receipt = certify_paths(word, bound, closed)
    result = {
        "status": "PASS_P104_OPEN_CONSUMER_INTERFACE",
        "inputs": {"WORD.json": WORD_SHA256, "NATIVE.json.gz": NATIVE_SHA256},
        "chart": word["chart"],
        "through_event": STOP,
        "closed_event_indices": closed,
        "external_read_event_indices": ports,
        "closed_opcode_counts": dict(Counter(word["program"][i][0] for i in closed)),
        "closed_native_rank_sum": sum(word["program"][i][4] for i in closed if word["program"][i][0] == "transport"),
        "path_certificate": path_receipt,
        "authenticated_wrapper_count": len(wrappers),
        "full_frame_tensor_identity": verify_full_frame_tensor(potentials),
    }
    query_matrix, query_column = conjugated_matrix(potentials[QUERY]["path"], bound)
    full_matrix, _ = conjugated_matrix(potentials[FULL]["path"], bound)
    native_column, denominator = apply_path([ONE] + [ZERO] * (N - 1), potentials[QUERY]["path"], bound)
    differences = [i for i, z in enumerate(native_column) if z != tuple(v * (1 << denominator) for v in query_column[i])]
    need(bool(differences), "actual query map falsely commutes with E")
    i = differences[0]
    result["coefficient_maps"] = {
        "convention": "E^-1 A E for the actual source-bound frame operator A",
        "query_frame": query_matrix,
        "full_frame": full_matrix,
        "wrong_unconjugated_map_control": {
            "input_coefficient_index": 0,
            "first_difference_index": i,
            "conjugated_integer_output": query_column[i],
            "unconjugated_output_numerator": native_column[i],
            "unconjugated_denominator": 1 << denominator,
            "differing_coordinates": len(differences),
        },
    }
    result["symbolic_open_interface"] = certify_symbolic_interface(word, closed, ports)
    result["dense_open_replay"] = dense_open_replay(word, bound, closed, ports, potentials)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify_consumer(args.repo / "research/p104-rounded-collector/inputs/WORD.json",
                             args.repo / "research/p104-rounded-collector/inputs/NATIVE.json.gz")
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
