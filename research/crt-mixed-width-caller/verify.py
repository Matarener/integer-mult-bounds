"""Explicit-width synchronized CRT caller; source-bound finite corroboration.

Logical address-permutation model only: no tape/E tariff is inferred. Source
Beneš/CRT arithmetic is authenticated and reused; global row decoding is new.
"""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import types


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def schedule(height):
    need(type(height) is int and height >= 1, "positive network height")
    return tuple(range(height)) + tuple(reversed(range(height - 1)))


def local_row(width, ell, global_row):
    """None is a literal idle, with no target address bit or table query."""
    need(type(ell) is int and ell >= 2, "ell at least two")
    need(type(width) is int and width in (ell - 1, ell), "declared width ell-1 or ell")
    need(type(global_row) is int and 0 <= global_row < 2 * ell - 1, "global row range")
    if width == ell:
        return global_row
    if global_row in (ell - 1, ell):
        return None
    return global_row if global_row < ell - 1 else global_row - 2


class Caller:
    def __init__(self, moduli, widths, ell, source):
        self.moduli, self.widths = tuple(moduli), tuple(widths)
        self.ell, self.source = ell, source
        self.d = len(self.moduli)
        need(self.d >= 1 and self.d & (self.d - 1) == 0, "power-of-two axis count")
        need(len(self.widths) == self.d, "one declared width per axis")
        need(type(ell) is int and ell >= 2, "ell at least two")
        for modulus, width in zip(self.moduli, self.widths):
            need(type(width) is int and width in (ell - 1, ell), "declared width family")
            need(type(modulus) is int and 2 <= modulus < (1 << width), "strict dyadic padding")
        need(all(math.gcd(a, b) == 1 for i, a in enumerate(self.moduli) for b in self.moduli[i + 1:]),
             "pairwise coprime moduli")
        self.levels = self.d.bit_length() - 1
        self.shifts = tuple(sum(self.widths[:i]) for i in range(self.d))
        self.length = sum(self.widths)
        self._networks = {}  # Finite host-model cache; no machine-cost claim.

    def state(self, values):
        state = tuple(values)
        need(len(state) == self.d and all(type(v) is int and 0 <= v < (1 << h)
                                        for v, h in zip(state, self.widths)),
             "complete declared padded state")
        return state

    def valid(self, state):
        return all(v < m for v, m in zip(state, self.moduli))

    def pack(self, state):
        return sum(value << shift for value, shift in zip(state, self.shifts))

    def network(self, axis, offset):
        key = axis, offset
        if key not in self._networks:
            height = self.widths[axis]
            net = self.source.benes(self.source.rotation(1 << height, self.moduli[axis], offset))
            need(tuple(bit for bit, table in net) == schedule(height), "retained network schedule")
            need(all(len(table) == 1 << height for bit, table in net), "declared width never shrunk")
            self._networks[key] = net
        return self._networks[key]

    def offsets(self, state, level):
        """Only original left-child coordinates decide validity and offsets."""
        need(1 <= level <= self.levels, "balanced level range")
        size = 1 << level
        result = {}
        for start in range(0, self.d, size):
            middle = start + size // 2
            left = state[start:middle]
            moduli = self.moduli[start:middle]
            lower = self.source.decode_group(left, moduli) if all(v < m for v, m in zip(left, moduli)) else 0
            prefix = math.prod(moduli)
            for axis in range(middle, start + size):
                result[axis] = lower * pow(prefix, -1, self.moduli[axis]) % self.moduli[axis]
                prefix *= self.moduli[axis]
        return result

    def row(self, state, level, global_row, offsets=None, gate_invalid_target=False):
        offsets = self.offsets(state, level) if offsets is None else offsets
        result = []
        for axis, offset in offsets.items():
            row = local_row(self.widths[axis], self.ell, global_row)
            if row is None:
                result.append((axis, None, None, 0))
                continue
            bit, table = self.network(axis, offset)[row]
            need(0 <= bit < self.widths[axis], "no phantom address bit")
            need(bit == schedule(self.ell)[global_row], "canonical active global bit alignment")
            control = table[state[axis]]
            if gate_invalid_target and state[axis] >= self.moduli[axis]:
                control = 0  # Deliberately wrong: intermediate target validity is not invariant.
            result.append((axis, row, bit, control))
        return tuple(result)

    @staticmethod
    def apply(state, specifications):
        result = list(state)
        for axis, row, bit, control in specifications:
            if row is None:
                need(bit is None and control == 0, "idle has no target")
            else:
                result[axis] ^= control << bit
        return tuple(result)

    def run(self, values, reverse=False, inspect=None, gate_invalid_target=False):
        state = self.state(values)
        levels = range(self.levels, 0, -1) if reverse else range(1, self.levels + 1)
        for level in levels:
            offsets = self.offsets(state, level)
            level_input = state
            rows = reversed(range(2 * self.ell - 1)) if reverse else range(2 * self.ell - 1)
            for global_row in rows:
                specs = self.row(state, level, global_row, offsets, gate_invalid_target)
                if inspect is not None:
                    inspect(state, level, global_row, specs)
                state = self.apply(state, specs)
            need(self.valid(state) == self.valid(level_input), "valid set preserved at whole-level endpoint")
        return state


def check_decoder():
    cases = idles = 0
    for ell in range(2, 17):
        for width in (ell - 1, ell):
            rows = [local_row(width, ell, g) for g in range(2 * ell - 1)]
            need([r for r in rows if r is not None] == list(range(2 * width - 1)),
                 "every local row appears exactly once and in order")
            for g, row in enumerate(rows):
                if row is None:
                    idles += 1
                    need(width == ell - 1 and g in (ell - 1, ell), "exact two idle locations")
                else:
                    need(schedule(width)[row] == schedule(ell)[g], "active target bit exists and aligns")
            cases += 1
    return {"ell_values": [2, 16], "height_cases": cases, "literal_idles": idles,
            "proof_scope": "all integer ell>=2; finite decoder check is corroboration"}


def fixture(name, moduli, widths, ell, source):
    caller = Caller(moduli, widths, ell, source)
    domain = itertools.product(*(range(1 << h) for h in widths))
    count = valid = row_checks = omission_checks = idle_checks = 0
    endpoint_digest = hashlib.sha256()
    inverse_digest = hashlib.sha256()
    seen = bytearray(1 << caller.length)
    changed_invalid = None
    minimal = all(h == (m - 1).bit_length() for h, m in zip(widths, moduli))
    compiled_checks = 0

    def inspect(state, level, g, specs):
        nonlocal row_checks, omission_checks, idle_checks
        row_checks += 1
        # Recomputed current left-child controls agree with the frozen level controls.
        need(specs == caller.row(state, level, g), "freeze only unchanged left-child controls")
        for axis, row, bit, control in specs:
            if row is None:
                idle_checks += 1
                need(bit is None and control == 0, "literal idle performs no phantom query")
                continue
            toggled = list(state)
            toggled[axis] ^= 1 << bit
            need(caller.row(tuple(toggled), level, g) == specs, "all active targets omitted at actual row")
            omission_checks += 1

    for state in domain:
        count += 1
        forward = caller.run(state, inspect=inspect)
        inverse = caller.run(state, reverse=True)
        need(forward == source.balanced(state, moduli), "whole synchronized tree equals retained arithmetic caller")
        need(inverse == source.balanced(state, moduli, reverse=True), "reverse rows/levels equal inverse CRT endpoint")
        need(caller.run(forward, reverse=True) == state and caller.run(inverse) == state,
             "two-sided all-padded inverse")
        if minimal:
            need(forward == source.balanced(state, moduli, compiled=True), "minimal-width compiled source oracle")
            compiled_checks += 1
        if caller.valid(state):
            valid += 1
            need(forward == source.direct(state, moduli), "direct CRT formula on complete valid subset")
        elif forward != state and changed_invalid is None:
            changed_invalid = {"input": list(state), "output": list(forward)}
        need(caller.valid(state) == caller.valid(forward), "global invalid set preserved, not pointwise fixation")
        destination = caller.pack(forward)
        need(not seen[destination], "all declared dirty tuples permuted bijectively")
        seen[destination] = 1
        endpoint_digest.update(destination.to_bytes((caller.length + 7) // 8, "big"))
        inverse_digest.update(caller.pack(inverse).to_bytes((caller.length + 7) // 8, "big"))
    need(all(seen), "complete padded destination coverage")
    need(count == 1 << caller.length and valid == math.prod(moduli), "complete domain/valid count")
    return {"name": name, "domain": "canonical logical axes; no reservoir placement or physical macro executed",
            "hash_input_order": "lexicographic logical tuples, axis0 outermost; packed axis0 is least significant",
            "hash_destination_encoding": "ceil(L/8) bytes per packed destination, big endian",
            "moduli": list(moduli), "widths": list(widths), "ell": ell,
            "axes": caller.d, "address_bits": caller.length, "tree_levels": caller.levels,
            "global_rows_per_level": 2 * ell - 1, "padded_states": count,
            "valid_states": valid, "invalid_states": count - valid,
            "forward_row_checks": row_checks, "actual_row_omission_toggles": omission_checks,
            "literal_idle_checks": idle_checks, "minimal_width_compiled_source_checks": compiled_checks,
            "changed_invalid_tuple": changed_invalid,
            "forward_permutation_sha256": endpoint_digest.hexdigest(),
            "inverse_permutation_sha256": inverse_digest.hexdigest()}


def rejection(call, label):
    try:
        call()
    except (ValueError, IndexError):
        return label
    raise ValueError("negative control accepted: " + label)


def negatives(source):
    # A genuine CRT caller, not an isolated made-up switch predicate.
    caller = Caller((7, 3), (3, 2), 3, source)
    state = (1, 1)
    trace = []
    right = caller.run(state, inspect=lambda x, level, g, specs:
                       trace.append({"global_row": g, "before": list(x),
                                     "local_row": specs[0][1], "target": specs[0][2]}))
    # Run the mutant manually: its purpose is to violate the endpoint, so do
    # not apply the correct caller's endpoint-validity postcondition to it.
    wrong = state
    offsets = caller.offsets(state, 1)
    for g in range(5):
        wrong = caller.apply(wrong, caller.row(wrong, 1, g, offsets, gate_invalid_target=True))
    need(right == (1, 2) and wrong == (1, 3), "per-micro-layer target-validity mutant detected")
    need(any(row["before"][1] == 3 for row in trace), "dirty target occurs between valid endpoints")
    wider = Caller((5, 3), (3, 3), 3, source)
    need(wider.run((0, 4)) == (0, 4), "declared wider padding endpoint")
    boundary = rejection(lambda: source.balanced((0, 4), (5, 3), compiled=True),
                         "minimal-width finite source helper cannot index declared wider dirty target")
    invalid = (5, 0, 1, 0)
    full = Caller((5, 7, 11, 13), (3, 3, 4, 4), 4, source)
    need(not full.valid(invalid) and full.run(invalid) == (5, 0, 1, 6),
         "globally invalid tuple is not necessarily pointwise fixed")
    return {"target_validity_mutant": {"moduli": [7, 3], "widths": [3, 2], "ell": 3,
                                       "input": list(state), "correct": list(right), "wrong": list(wrong),
                                       "trace_before_rows": trace},
            "source_helper_api_boundary": boundary,
            "invalid_pointwise_fixation_counterexample": {"input": list(invalid), "output": [5, 0, 1, 6]},
            "admission_rejections": [
                rejection(lambda: local_row(2, 4, 0), "width outside ell-1/ell"),
                rejection(lambda: local_row(3, 4, 7), "global row outside schedule"),
                rejection(lambda: Caller((3, 5, 7), (3, 3, 3), 3, source), "non-power-of-two axes"),
                rejection(lambda: Caller((3, 9), (4, 4), 4, source), "noncoprime moduli"),
                rejection(lambda: Caller((3, 8), (3, 3), 3, source), "missing strict dyadic padding"),
            ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    pins = json.loads((PACKAGE / "SOURCE-PINS.json").read_text())
    authenticated = {}
    for row in pins:
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        need(hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == row["git_blob"],
             "source Git blob: " + row["path"])
        authenticated[row["path"]] = data
    path = "research/unconditional-batched-crt/check_batched_crt.py"
    source = types.ModuleType("_mixed_width_authenticated_source")
    source.__file__ = str(ROOT / path)
    sys.modules[source.__name__] = source
    exec(compile(authenticated[path], source.__file__, "exec"), source.__dict__)
    result = {"schema_version": 1, "result": "PASS_EXPLICIT_WIDTH_SYNCHRONIZED_CRT_CALLER",
              "base_commit": "12fa8c5c844be21bfefb38a19503fbd867a11244", "source_inputs_checked": len(authenticated),
              "decoder": check_decoder(), "fixtures": [
                  fixture("mixed_four_axis", (5, 7, 11, 13), (3, 3, 4, 4), 4, source),
                  fixture("declared_wider_padding", (5, 3), (3, 3), 4, source),
                  fixture("microscopic_padding_validity", (7, 3), (3, 2), 3, source),
              ], "negative_controls": negatives(source),
              "limitations": ["Quantified caller/decoder proof is separate from finite corroboration.",
                              "All-target omission is predecessor coverage; this binds literal mixed-width rows.",
                              "Canonical logical-axis host model only; no reservoir or physical compact macro executed.",
                              "No tape/E tariff, full CRT implementation, precision/native/outer theorem or new kappa."]}
    output = PACKAGE / "RESULT.json"
    if args.write_result:
        output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(output.read_text()) == result, "stored receipt differs from replay")
    print(json.dumps({"result": result["result"],
                      "padded_states": sum(r["padded_states"] for r in result["fixtures"]),
                      "row_checks": sum(r["forward_row_checks"] for r in result["fixtures"])}, sort_keys=True))


if __name__ == "__main__":
    main()
