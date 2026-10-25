"""Independent exact finite-word and scalar-prefix audit for the C01 rewrite.

Only the authenticated historical transport/emitter are run as producers.
Acceptance below uses this separate integer-dyadic row interpreter. Native
Clifford phases, physical CLEAR implementations and recursive rounding are
outside the checked model. Prepared with substantial OpenAI Codex assistance.
"""

from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile


HEAD = "3efbb5de06a49ffeea6684482f2d3fe48cdca3fb"
SOURCE_HASHES = {
    "base": "735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653",
    "extra": "886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f",
}
PRODUCER_HASHES = {
    "transport": "9818e08b819310b40f1441b89be8c4369584a5b3fa5dfe9b86b1df9a7f5d6a76",
    "emitter": "99b59a6fa3feda86785e4225157dcb1a6169d256cec4f5e0acc9cea7a701df76",
}
HISTORICAL_PANEL_HASH = "e7bdb1e299a43a8fcbdad4c598b7161e504a94691df3940a9a4eaf638f5013f0"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def file_record(path):
    raw = path.read_bytes()
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "decoded_sha256": hashlib.sha256(
            gzip.decompress(raw) if path.suffix == ".gz" else raw
        ).hexdigest(),
    }


def dyadic(numerator, denominator=1):
    require(type(numerator) is int and type(denominator) is int,
            "a coefficient must have integer numerator and denominator")
    q = Fraction(numerator, denominator)
    require(q.denominator & (q.denominator - 1) == 0, "non-dyadic coefficient")
    return q.numerator, q.denominator.bit_length() - 1


def normalize(terms, exponent):
    terms = {column: value for column, value in terms.items() if value}
    if not terms:
        return {}, 0
    reduction = min(exponent, min(
        (abs(value) & -abs(value)).bit_length() - 1 for value in terms.values()))
    if reduction:
        terms = {column: value >> reduction for column, value in terms.items()}
        exponent -= reduction
    return terms, exponent


def row_scale(row, numerator, exponent):
    terms, old_exponent = row
    return normalize({column: numerator * value for column, value in terms.items()},
                     old_exponent + exponent)


def row_add(left, right, numerator=1, exponent=0):
    left_terms, left_exponent = left
    right_terms, right_exponent = right
    final_exponent = max(left_exponent, right_exponent + exponent)
    terms = {column: value << (final_exponent - left_exponent)
             for column, value in left_terms.items()}
    shift = final_exponent - right_exponent - exponent
    for column, value in right_terms.items():
        terms[column] = terms.get(column, 0) + numerator * (value << shift)
    return normalize(terms, final_exponent)


def number(numerator, exponent=0):
    require(numerator >= 0, "negative positive-envelope number")
    if not numerator:
        return 0, 0
    reduction = min(exponent, (numerator & -numerator).bit_length() - 1)
    return numerator >> reduction, exponent - reduction


def number_add(left, right):
    exponent = max(left[1], right[1])
    return number((left[0] << (exponent - left[1]))
                  + (right[0] << (exponent - right[1])), exponent)


def number_scale(value, numerator, exponent=0):
    return number(value[0] * abs(numerator), value[1] + exponent)


def greater(left, right):
    return (left[0] << right[1]) > (right[0] << left[1])


def number_json(value):
    numerator, exponent = value
    return {
        "numerator": numerator,
        "denominator_exponent": exponent,
        "value": str(Fraction(numerator, 1 << exponent)),
        "strict_power_of_two_bits": numerator.bit_length() - exponent if numerator else 0,
    }


def key_json(key):
    if isinstance(key, tuple):
        return [key_json(item) for item in key]
    return key


def row_json(row):
    return {"denominator_exponent": row[1],
            "terms": [[key_json(key), value] for key, value in sorted(row[0].items())]}


def state_digest(state):
    return digest([[key_json(key), row_json(row)] for key, row in sorted(state.items())])


class Metrics:
    def __init__(self):
        self.maximum_denominator_exponent = 0
        self.maximum_numerator_bits = 1
        self.maximum_exact_row_sum = (1, 0)
        self.maximum_positive_envelope = (1, 0)
        self.grid_witness = None
        self.row_sum_witness = None
        self.envelope_witness = None

    def observe(self, row, envelope, index, reference):
        terms, exponent = row
        if exponent > self.maximum_denominator_exponent:
            odd = next(key for key, value in sorted(terms.items()) if value % 2)
            self.maximum_denominator_exponent = exponent
            self.grid_witness = {
                "instruction": index, "reference": key_json(reference),
                "input_column": key_json(odd), "numerator": terms[odd],
                "denominator_exponent": exponent,
            }
        if terms:
            self.maximum_numerator_bits = max(
                self.maximum_numerator_bits,
                max(abs(value).bit_length() for value in terms.values()))
        row_sum = number(sum(abs(value) for value in terms.values()), exponent)
        if greater(row_sum, self.maximum_exact_row_sum):
            self.maximum_exact_row_sum = row_sum
            self.row_sum_witness = {
                "instruction": index, "reference": key_json(reference),
                "row": row_json(row), "row_sha256": digest(row_json(row))}
        if greater(envelope, self.maximum_positive_envelope):
            self.maximum_positive_envelope = envelope
            self.envelope_witness = {
                "instruction": index, "reference": key_json(reference)}

    def result(self):
        return {
            "maximum_denominator_exponent": self.maximum_denominator_exponent,
            "maximum_numerator_bits": self.maximum_numerator_bits,
            "maximum_exact_row_sum": number_json(self.maximum_exact_row_sum),
            "maximum_positive_envelope": number_json(self.maximum_positive_envelope),
            "grid_witness": self.grid_witness,
            "exact_row_sum_witness": self.row_sum_witness,
            "positive_envelope_witness": self.envelope_witness,
        }


def inverse_gate(gate):
    tag = gate[0]
    if tag == "add":
        return [tag, gate[1], gate[2], -gate[3], gate[4]]
    if tag == "scale":
        return [tag, gate[1], gate[3], gate[2]]
    require(tag == "warp", "unknown inverse gate")
    return [tag, gate[1], -gate[2]]


def dual_gate(gate):
    tag = gate[0]
    if tag == "add":
        return [tag, gate[2], gate[1], -gate[3], gate[4]]
    if tag == "scale":
        return [tag, gate[1], gate[3], gate[2]]
    require(tag == "warp", "unknown dual gate")
    # Here the generator means the conjugate monomial K-bar, as in the
    # inherited inverse-transpose alphabet. It is an independent free letter.
    return gate[:]


def orientations(program, dual=False, inverse=False):
    result = [dual_gate(gate) if dual else gate[:] for gate in program]
    return [inverse_gate(gate) for gate in reversed(result)] if inverse else result


def bare_gate(gate):
    tag = gate[0]
    require(tag in ("add", "scale", "warp"), "unknown raw-word gate")
    length = {"add": 5, "scale": 4, "warp": 3}[tag]
    return gate[:length]


def raw_prefix(word):
    gates = []
    for correction in word["initial_corrections"]:
        q = Fraction(correction["coefficient"])
        source = correction["source"]
        letters = correction["operator_word"]
        gates += [["warp", source, op] for op in reversed(letters)]
        gates += [["add", correction["target"], source, q.numerator, q.denominator]]
        gates += [["warp", source, -op] for op in letters]
    for section in ("precondition", "compensation"):
        gates += [bare_gate(gate) for gate in word[section]]
    return gates


def raw_program(word):
    gates = raw_prefix(word)
    for section in ("A", "cut"):
        gates += [bare_gate(gate) for gate in word[section]]
    at = {}
    for operator, warp in enumerate(word["warps"], 1):
        at.setdefault(warp[0], []).append(["warp", warp[1], operator])
    for index in range(len(word["B"]) + 1):
        gates += at.get(index, [])
        if index < len(word["B"]):
            gates.append(bare_gate(word["B"][index]))
    for section in ("restore", "cleanup"):
        gates += [bare_gate(gate) for gate in word[section]]
    return gates


def bind_emitted_prefix(word, canonical_word, events, dual):
    kept = sorted(set(range(704)) - set(word["removed"]))
    new_id = {register: index for index, register in enumerate(kept)}
    expected_compensation = [
        ["add", new_id[gate[1]], new_id[gate[2]], gate[3], gate[4], 0]
        for gate in word["compensation"]]
    require(canonical_word["compensation"] == expected_compensation,
            "raw-to-canonical compensation mismatch")
    expected = [["phase", "zero_frame_precondition"]]
    for gate in orientations(raw_prefix(word), dual):
        if gate[0] == "warp":
            expected.append(["warp", ["L", new_id[gate[1]]], gate[2], 0, 0])
        elif gate[0] == "scale":
            expected.append(["scalar", ["scale", ["L", new_id[gate[1]]],
                                         gate[2], gate[3]], 0])
        else:
            expected.append(["scalar", ["add", ["L", new_id[gate[1]]],
                                         ["L", new_id[gate[2]]], gate[3], gate[4]], 0])
    end = events.index(["phase", "entry_adapters"])
    require(events[:end] == expected, "literal emitted zero-frame prefix mismatch")
    return {"events": end, "sha256": digest(expected)}


def free_replay(program, live, zero_buffers=()):
    state = {r: ({(r, ()): 1}, 0) for r in live}
    envelope = {r: (1, 0) for r in live}
    for r in zero_buffers:
        require(r not in state, "zero buffer aliases arbitrary input")
        state[r] = ({}, 0)
        envelope[r] = (0, 0)
    metrics = Metrics()
    for index, gate in enumerate(program):
        tag, target = gate[:2]
        require(target in state, "undeclared destination")
        if tag == "warp":
            operator = gate[2]
            require(type(operator) is int and operator != 0, "invalid warp")
            terms, exponent = state[target]
            changed = {}
            for (column, letters), value in terms.items():
                word = letters[1:] if letters and letters[0] == -operator else (operator,) + letters
                key = column, word
                require(key not in changed, "left free-word action must be injective")
                changed[key] = value
            state[target] = changed, exponent
        elif tag == "scale":
            numerator, exponent = dyadic(gate[2], gate[3])
            require(numerator != 0, "singular scale")
            state[target] = row_scale(state[target], numerator, exponent)
            envelope[target] = number_scale(envelope[target], numerator, exponent)
        else:
            require(tag == "add", "unknown operation")
            source = gate[2]
            require(source in state and source != target, "undeclared or aliasing source")
            numerator, exponent = dyadic(gate[3], gate[4])
            require(numerator != 0, "zero addition")
            state[target] = row_add(state[target], state[source], numerator, exponent)
            envelope[target] = number_add(
                envelope[target], number_scale(envelope[source], numerator, exponent))
        metrics.observe(state[target], envelope[target], index, target)
    return state, metrics.result()


def difference(actual, expected):
    for reference in sorted(set(actual) | set(expected)):
        if actual.get(reference) != expected.get(reference):
            return {"reference": key_json(reference),
                    "actual": row_json(actual.get(reference, ({}, 0))),
                    "expected": row_json(expected.get(reference, ({}, 0)))}
    return None


def full_expected(live, zero_buffers, dual, inverse):
    state = {r: ({(r, ()): 1}, 0) for r in live}
    for r in zero_buffers:
        state[r] = ({}, 0)
    for port in range(112):
        target, source = (port, 112 + port) if dual else (112 + port, port)
        sign = (-1 if dual else 1) * (-1 if inverse else 1)
        state[target][0][source, ()] = sign
    return state


def audit_whole_word(word):
    live = sorted(set(range(704)) - set(word["removed"]))
    zero_buffers = sorted(704 + int(r) for r in word["helper_final"])
    require(len(live) == 632 and len(zero_buffers) == 91, "changed input domain")
    program = raw_program(word)
    result = {}
    for dual in (False, True):
        for inverse in (False, True):
            label = ("dual" if dual else "forward") + ("-inverse" if inverse else "")
            oriented = orientations(program, dual, inverse)
            actual, metrics = free_replay(oriented, live, zero_buffers)
            witness = difference(actual, full_expected(live, zero_buffers, dual, inverse))
            require(witness is None, f"whole-word endpoint {label}: {witness}")
            result[label] = {
                "all_arbitrary_input_columns": len(live),
                "zero_buffer_columns_required_zero": len(zero_buffers),
                "literal_gate_count": len(oriented),
                "gate_counts": dict(sorted(Counter(gate[0] for gate in oriented).items())),
                "endpoint_sha256": state_digest(actual),
                "exact_endpoint": True, "all_zero_buffers_returned_exactly": True,
                "metrics": metrics,
            }
    return result


def panel_sections(panel):
    def kind(gate):
        require(gate[0] == "add" and gate[-1] == [], "panel must be zero-frame additions")
        target, source = gate[1:3]
        if 112 <= target < 224 and 112 <= source < 224:
            return "target"
        if target >= 224 and source >= 224:
            return "helper"
        require(112 <= target < 224 and source >= 224, "incorrect panel bank")
        return "residual"
    runs = []
    for gate in panel:
        label = kind(gate)
        if not runs or runs[-1][0] != label:
            runs.append((label, []))
        runs[-1][1].append(gate)
    require([label for label, _ in runs] ==
            ["target", "helper", "residual", "helper", "target"],
            "expected restored two-sided factorization")
    return [gates for _, gates in runs]


def primitive_price(gate):
    require(gate[0] == "add", "panel price only supports ADD")
    numerator, exponent = dyadic(gate[3], gate[4])
    require(numerator != 0, "zero coefficient")
    digits = []
    n = abs(numerator)
    while n:
        digits.append(n % 2)
        n //= 2
    return 3 + len(digits) - 1 + sum(digits) + exponent


def panel_audit(source, candidate):
    live = sorted(set(range(704)) - set(source["removed"]))
    old = [bare_gate(gate) for gate in source["compensation"]]
    new = [bare_gate(gate) for gate in candidate["compensation"]]
    target_prepare, helper_prepare, residual, helper_restore, target_restore = panel_sections(
        candidate["compensation"])
    require([bare_gate(gate) for gate in helper_restore] ==
            [inverse_gate(bare_gate(gate)) for gate in reversed(helper_prepare)],
            "literal helper restoration mismatch")
    require([bare_gate(gate) for gate in target_restore] ==
            [inverse_gate(bare_gate(gate)) for gate in reversed(target_prepare)],
            "literal target restoration mismatch")
    helpers = sorted({r for gate in candidate["compensation"] for r in gate[1:3] if r >= 224})
    require(all(r in live and str(r) not in source["start_extra"]
                and str(r) not in source["helper_final"] for r in helpers),
            "helper not available unwrapped at the compensation cut")
    target_pre = [bare_gate(gate) for gate in target_prepare]
    helper_pre = [bare_gate(gate) for gate in helper_prepare]
    correction = [bare_gate(gate) for gate in residual]
    helper_post = [bare_gate(gate) for gate in helper_restore]
    target_post = [bare_gate(gate) for gate in target_restore]
    checks = {}
    for dual in (False, True):
        for inverse in (False, True):
            label = ("dual" if dual else "forward") + ("-inverse" if inverse else "")
            old_state, old_metrics = free_replay(orientations(old, dual, inverse), live)
            new_state, new_metrics = free_replay(orientations(new, dual, inverse), live)
            require(difference(new_state, old_state) is None, "panel mismatch: " + label)
            checks[label] = {"all_arbitrary_input_columns": len(live),
                             "endpoint_sha256": state_digest(new_state),
                             "old_prefix": old_metrics, "new_prefix": new_metrics}
    sign = copy.deepcopy(new)
    sign[-1][3] *= -1
    controls = {
        "omit_target_prepare": helper_pre + correction + helper_post + target_post,
        "omit_helper_prepare": target_pre + correction + helper_post + target_post,
        "omit_helper_restore": target_pre + helper_pre + correction + target_post,
        "omit_target_restore": target_pre + helper_pre + correction + helper_post,
        "stale_original_pullback": target_pre + helper_pre + old + helper_post + target_post,
        "literal_final_sign": sign,
        "wrong_target_restore_order": target_pre + helper_pre + correction + helper_post
                                      + list(reversed(target_post)),
    }
    rejected = []
    for dual in (False, True):
        expected, _ = free_replay(orientations(old, dual), live)
        for label, program in controls.items():
            state, _ = free_replay(orientations(program, dual), live)
            witness = difference(state, expected)
            require(witness is not None, "insensitive panel control: " + label)
            rejected.append({"control": label, "orientation": "dual" if dual else "forward",
                             "witness": witness})
    # Deliberately omit the reversal required by a literal inverse.
    expected, _ = free_replay(orientations(old, inverse=True), live)
    state, _ = free_replay([inverse_gate(gate) for gate in new], live)
    witness = difference(state, expected)
    require(witness is not None, "insensitive inverse-order control")
    rejected.append({"control": "invert_each_gate_without_reversal", "witness": witness})
    # Deliberately retain the forward sign on exactly one dual ADD.
    bad_dual = orientations(new, dual=True)
    bad_dual[0][3] *= -1
    state, _ = free_replay(bad_dual, live)
    expected, _ = free_replay(orientations(old, dual=True), live)
    witness = difference(state, expected)
    require(witness is not None, "insensitive dual-sign control")
    rejected.append({"control": "wrong_dual_sign", "witness": witness})
    names = ["target_prepare", "helper_prepare", "residual", "helper_restore", "target_restore"]
    groups = [target_prepare, helper_prepare, residual, helper_restore, target_restore]
    bill = {name: {"additions": len(gates),
                   "price_per_real_component": sum(map(primitive_price, gates))}
            for name, gates in zip(names, groups)}
    bill["source"] = {"additions": len(old),
                      "price_per_real_component": sum(map(primitive_price, source["compensation"]))}
    bill["candidate"] = {"additions": len(new),
                         "price_per_real_component": sum(map(primitive_price, candidate["compensation"]))}
    return {"input_columns": len(live), "helper_coordinates": helpers,
            "all_helpers_enter_zero_frame_and_exit_full": True,
            "restored_factorization": True, "checks": checks,
            "bill": bill, "controls": rejected}


def historical_panel_audit(source, path):
    require(hashlib.sha256(path.read_bytes()).hexdigest() == HISTORICAL_PANEL_HASH,
            "historical rank-basis panel hash mismatch")
    panel = read(path)
    live = sorted(set(range(704)) - set(source["removed"]))
    old = [bare_gate(gate) for gate in source["compensation"]]
    new = [bare_gate(gate) for gate in panel]
    checks = {}
    for dual in (False, True):
        for inverse in (False, True):
            label = ("dual" if dual else "forward") + ("-inverse" if inverse else "")
            expected, _ = free_replay(orientations(old, dual, inverse), live)
            actual, metrics = free_replay(orientations(new, dual, inverse), live)
            require(difference(actual, expected) is None,
                    "historical panel endpoint mismatch: " + label)
            checks[label] = {"all_arbitrary_input_columns": len(live),
                             "endpoint_sha256": state_digest(actual), "prefix": metrics}
    bill = sum(map(primitive_price, panel))
    require(len(panel) == 3214 and bill == 17334, "historical rank-basis bill changed")
    return {"additions": len(panel), "price_per_real_component": bill,
            "checks": checks, "scope": "Fresh boundary and panel-prefix replay only."}


def lower_scalar(operation):
    """Binary Horner scalar expansion, independently spelled out."""
    tag = operation[0]
    target = tuple(operation[1])
    work = ("W", 0)
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        return [("copy", target, tuple(operation[2]))]
    if tag == "scale":
        numerator, exponent = dyadic(operation[2], operation[3])
        absolute = abs(numerator)
        require(absolute and absolute & (absolute - 1) == 0, "non-binary scale")
        shift = absolute.bit_length() - 1 - exponent
        result = [("double" if shift >= 0 else "halve", target)] * abs(shift)
        if numerator < 0:
            result.append(("negate", target))
        return result
    require(tag == "add", "unknown scalar macro")
    source = tuple(operation[2])
    require(target != source and work not in (target, source), "aliased scalar ADD")
    numerator, exponent = dyadic(operation[3], operation[4])
    require(numerator != 0, "zero scalar ADD")
    bits = []
    absolute = abs(numerator)
    while absolute:
        bits.append(absolute % 2)
        absolute //= 2
    result = [("clear", work)]
    for index, bit in enumerate(reversed(bits)):
        if index:
            result.append(("double", work))
        if bit:
            result.append(("add", work, source, 1))
    result += [("halve", work)] * exponent
    result += [("add", target, work, 1 if numerator > 0 else -1), ("clear", work)]
    return result


def audit_scalar_projection(events, canonical_word, orientation):
    n = 2 * canonical_word["v"] + canonical_word["R"]
    require(n == 632, "unexpected compact logical dimension")
    centers = len(canonical_word["centers"])
    zeroes = canonical_word["zero_buffers"]
    sizes = {"L": set(range(n)), "C": set(range(centers)), "Z": set(zeroes), "W": {0}}
    state = {("L", i): ({i: 1}, 0) for i in range(n)}
    envelope = {("L", i): (1, 0) for i in range(n)}
    for kind in ("C", "Z", "W"):
        for i in sizes[kind]:
            state[kind, i] = ({}, 0)
            envelope[kind, i] = (0, 0)
    metrics = Metrics()
    counts = Counter()
    by_phase = {}
    phase = None
    nonzero_clears = Counter()
    active_zeroes = set()
    primitive_index = 0
    macro_count = 0
    primitive_hash = hashlib.sha256()
    for event_index, event in enumerate(events):
        tag = event[0]
        if tag == "phase":
            phase = event[1]
            continue
        if tag == "zero_buffer":
            z = event[2]
            require(z in sizes["Z"], "undeclared zero buffer")
            require(not state["Z", z][0], "nonzero private buffer at allocation/free")
            if event[1] == "alloc":
                require(z not in active_zeroes, "double zero-buffer allocation")
                active_zeroes.add(z)
            else:
                require(event[1] == "free" and z in active_zeroes, "invalid zero-buffer free")
                active_zeroes.remove(z)
            continue
        if tag != "scalar":
            require(tag in ("adapter", "residual_adapter", "warp", "climb", "center"),
                    "unknown nonscalar event")
            continue
        macro_count += 1
        primitives = lower_scalar(event[1])
        for operation in primitives:
            op, target = operation[:2]
            require(target[0] in sizes and target[1] in sizes[target[0]], "invalid scalar destination")
            if target[0] == "Z":
                require(target[1] in active_zeroes, "unallocated private destination")
            primitive_hash.update(canonical(operation) + b"\n")
            counts[op] += 1
            by_phase.setdefault(phase, Counter())[op] += 1
            if op == "clear":
                if state[target][0]:
                    nonzero_clears[target[0]] += 1
                state[target] = ({}, 0)
                envelope[target] = (0, 0)
            elif op == "copy":
                source = operation[2]
                require(source in state, "invalid scalar COPY source")
                state[target] = state[source]
                envelope[target] = envelope[source]
            elif op == "add":
                source, sign = operation[2:4]
                require(source in state and source != target and sign in (-1, 1),
                        "invalid scalar ADD")
                if source[0] == "Z":
                    require(source[1] in active_zeroes, "unallocated private source")
                state[target] = row_add(state[target], state[source], sign)
                envelope[target] = number_add(envelope[target], envelope[source])
            elif op == "double":
                state[target] = row_scale(state[target], 2, 0)
                envelope[target] = number_scale(envelope[target], 2, 0)
            elif op == "halve":
                state[target] = row_scale(state[target], 1, 1)
                envelope[target] = number_scale(envelope[target], 1, 1)
            else:
                require(op == "negate", "unknown scalar primitive")
                state[target] = row_scale(state[target], -1, 0)
            metrics.observe(state[target], envelope[target], primitive_index, target)
            primitive_index += 1
    require(not active_zeroes, "live private buffers at scalar endpoint")
    expected = {("L", i): ({i: 1}, 0) for i in range(n)}
    for i in range(112):
        target, source, sign = ((112 + i, i, 1) if orientation == "forward"
                                else (i, 112 + i, -1))
        expected["L", target][0][source] = sign
    for kind in ("C", "Z", "W"):
        for index in sizes[kind]:
            expected[kind, index] = ({}, 0)
    witness = difference(state, expected)
    require(witness is None, f"scalar endpoint {orientation}: {witness}")
    return {
        "arbitrary_logical_inputs": n,
        "initial_zero_registers": {"C": centers, "Z": len(zeroes), "W": 1},
        "scalar_macro_count": macro_count,
        "primitive_count_per_real_component": primitive_index,
        "primitive_counts_per_real_component": dict(sorted(counts.items())),
        "two_real_component_count": 2 * primitive_index,
        "primitive_stream_sha256": primitive_hash.hexdigest(),
        "primitive_counts_by_phase": {key: dict(sorted(value.items()))
                                      for key, value in sorted(by_phase.items())},
        "nonzero_clear_assignments": dict(sorted(nonzero_clears.items())),
        "endpoint_sha256": state_digest(state),
        "exact_scalar_endpoint": True,
        "metrics": metrics.result(),
        "scope": "Scalar projection: nonscalar events act as identity; CLEAR is an assignment. "
                 "This is not a physical implementation or a reversible-erasure proof.",
    }


def produced_programs(word_path, transport, emitter, directory):
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for label, source, arguments in (
        ("transport", transport, [str(word_path), str(directory)]),
        ("emitter", emitter, [str(directory)]),
    ):
        source_bytes = source.read_bytes()
        require(hashlib.sha256(source_bytes).hexdigest() == PRODUCER_HASHES[label],
                "producer execution buffer hash mismatch: " + label)
        bootstrap = (
            "import sys\n"
            "source = sys.stdin.buffer.read()\n"
            "sys.argv = sys.argv[1:]\n"
            "namespace = {'__name__': '__main__', '__file__': sys.argv[0]}\n"
            "exec(compile(source, sys.argv[0], 'exec', dont_inherit=True, optimize=0), namespace)\n"
        )
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", bootstrap, str(source), *arguments],
            input=source_bytes, capture_output=True, env=env, timeout=120)
        require(completed.returncode == 0,
                label + " failed: " + completed.stderr.decode(errors="replace"))
    canonical_word = read(directory / "CANONICAL-WORD.json.gz")
    programs = read(directory / "LOCAL-PROGRAMS.json.gz")
    producer_checks = read(directory / "LOCAL-CHECKS.json")
    require(set(programs) == {"forward", "backward"}, "incomplete emitted orientations")
    for orientation, events in programs.items():
        require(digest(events) == producer_checks[orientation]["sha256"],
                "emitted producer hash mismatch")
    return canonical_word, programs, producer_checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-base", "source-extra", "candidate-base", "candidate-extra",
                 "historical-panel-base", "historical-panel-extra",
                 "transport-source", "emitter-source", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    paths = {name: value.resolve() for name, value in vars(args).items()}
    require(len(set(paths.values())) == len(paths), "input/output path alias")
    output = paths.pop("output")
    for label in ("transport", "emitter"):
        actual = hashlib.sha256(paths[label + "_source"].read_bytes()).hexdigest()
        require(actual == PRODUCER_HASHES[label], "producer source hash mismatch: " + label)
    result = {
        "status": "PASS_EXACT_FINITE_WORD_AND_SCALAR_PREFIX",
        "head": HEAD, "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "inputs": {name: file_record(path) for name, path in sorted(paths.items())},
        "providers": {},
        "scope": {
            "free_operator_model": "All632 arbitrary logical inputs over dyadic free warp algebra; "
                                   "91 private buffers initially and finally zero. Four orientations.",
            "scalar_model": "Both emitted orientations lowered to charged binary-Horner scalar primitives; "
                            "nonscalar events are identity and CLEAR is assignment.",
            "not_established": ["physical Clifford phase correctness",
                                "physical reversible CLEAR implementation",
                                "native-child internal precision", "recursive rounding",
                                "all-size compiler or tape cost", "new kappa"],
        },
    }
    with tempfile.TemporaryDirectory(prefix="c01-wholeword-") as temporary:
        scratch = Path(temporary)
        for provider in ("base", "extra"):
            source_path = paths["source_" + provider]
            candidate_path = paths["candidate_" + provider]
            require(hashlib.sha256(source_path.read_bytes()).hexdigest() == SOURCE_HASHES[provider],
                    "historical word hash mismatch: " + provider)
            source, candidate = read(source_path), read(candidate_path)
            require(set(source) == set(candidate), "changed full-word key set")
            require(all(source[key] == candidate[key] for key in source if key != "compensation"),
                    "candidate changed a field outside compensation")
            panel = panel_audit(source, candidate)
            historical = historical_panel_audit(source, paths["historical_panel_" + provider])
            full = {}
            generated = {}
            for name, word, word_path in (("source", source, source_path),
                                          ("candidate", candidate, candidate_path)):
                full[name] = audit_whole_word(word)
                canonical_word, programs, producer_checks = produced_programs(
                    word_path, paths["transport_source"], paths["emitter_source"],
                    scratch / (provider + "-" + name))
                generated[name] = {
                    "canonical_sha256": digest(canonical_word),
                    "program_sha256": digest(programs),
                    "producer_checks": producer_checks,
                    "canonical_word": canonical_word,
                    "programs": programs,
                }
            old_canonical, new_canonical = (generated[name]["canonical_word"]
                                            for name in ("source", "candidate"))
            require(all(old_canonical[key] == new_canonical[key]
                        for key in old_canonical if key != "compensation"),
                    "canonical transport changed outside compensation")
            scalar = {}
            preserved = {}
            for orientation in ("forward", "backward"):
                old_events = generated["source"]["programs"][orientation]
                new_events = generated["candidate"]["programs"][orientation]
                old_nonscalar = [event for event in old_events if event[0] != "scalar"]
                new_nonscalar = [event for event in new_events if event[0] != "scalar"]
                require(old_nonscalar == new_nonscalar, "changed nonscalar event stream")
                old_boundary = old_events.index(["phase", "entry_adapters"])
                new_boundary = new_events.index(["phase", "entry_adapters"])
                require(old_events[old_boundary:] == new_events[new_boundary:],
                        "changed post-compensation native stream")
                preserved[orientation] = {
                    "nonscalar_events": len(old_nonscalar),
                    "nonscalar_sha256": digest(old_nonscalar),
                    "unchanged_suffix_events": len(old_events) - old_boundary,
                    "suffix_sha256": digest(old_events[old_boundary:]),
                }
                preserved[orientation]["literal_prefix_binding"] = {
                    name: bind_emitted_prefix(
                        word, generated[name]["canonical_word"],
                        generated[name]["programs"][orientation],
                        orientation == "backward")
                    for name, word in (("source", source), ("candidate", candidate))}
                scalar[orientation] = {
                    name: audit_scalar_projection(generated[name]["programs"][orientation],
                                                  generated[name]["canonical_word"], orientation)
                    for name in ("source", "candidate")}
                for name in ("source", "candidate"):
                    ours = scalar[orientation][name]
                    theirs = generated[name]["producer_checks"][orientation]
                    require(ours["two_real_component_count"] ==
                            theirs["real_component_primitive_bound"],
                            "independent literal primitive invoice mismatch")
                    require(ours["scalar_macro_count"] == theirs["scalar_macros"],
                            "independent macro coverage mismatch")
                actual_saving = (
                    scalar[orientation]["source"]["primitive_count_per_real_component"]
                    - scalar[orientation]["candidate"]["primitive_count_per_real_component"])
                predicted_saving = (
                    panel["bill"]["source"]["price_per_real_component"]
                    - panel["bill"]["candidate"]["price_per_real_component"])
                require(actual_saving == predicted_saving, "whole primitive bill delta mismatch")
            result["providers"][provider] = {
                "panel": panel, "whole_word": full, "scalar_projection": scalar,
                "historical_rank_basis_panel": historical,
                "native_nonscalar_stream_preservation": preserved,
                "generated": {name: {key: value for key, value in row.items()
                                      if key not in ("canonical_word", "programs")}
                              for name, row in generated.items()},
            }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(json.dumps(result, indent=2, sort_keys=True).encode() + b"\n")
    print("PASS_EXACT_FINITE_WORD_AND_SCALAR_PREFIX", output)


if __name__ == "__main__":
    main()
