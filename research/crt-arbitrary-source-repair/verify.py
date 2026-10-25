"""Caller-specific compact address audit; no machine-cost or theorem checker.

Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance.
Apache-2.0. See README/PROOF for predecessor attribution and the universal proof.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREDECESSOR = ROOT / "research/unconditional-batched-crt"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    count = 0
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "source SHA256 mismatch: " + row["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git blob mismatch: " + row["path"])
        count += 1
    return count


def source_module(name, filename):
    """Execute authenticated source bytes, without a predecessor .pyc lookup."""
    module = types.ModuleType(name)
    path = PREDECESSOR / filename
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


@dataclass(frozen=True)
class Word:
    digit_bits: int
    control_bits: int
    y_bits: int
    targets: tuple[int, ...]
    guard: int

    def __post_init__(self):
        require(self.digit_bits >= 1, "positive compact radix width")
        require(self.control_bits >= len(self.targets) * self.digit_bits, "control capacity")
        require(self.guard >= self.digit_bits + 4, "nonempty guard margin")
        require(len(self.targets) > 0, "at least one target")
        last = -self.guard
        for target in self.targets:
            require(target >= last + self.guard, "disjoint ordered guards")
            require(target + self.guard <= self.y_bits, "complete guard")
            last = target

    @property
    def size(self):
        return 1 << (2 * self.control_bits + self.y_bits)

    @property
    def address_bits(self):
        return 2 * self.control_bits + self.y_bits

    def unpack(self, address):
        mask = (1 << self.control_bits) - 1
        return (address >> (self.control_bits + self.y_bits),
                (address >> self.y_bits) & mask,
                address & ((1 << self.y_bits) - 1))

    def pack(self, state):
        u, t, y = state
        return (u << (self.control_bits + self.y_bits)) | (t << self.y_bits) | y

    def good(self, state):
        u, t, y = state
        radix = 1 << self.digit_bits
        for i, target in enumerate(self.targets):
            shift = self.digit_bits * i
            if (u >> shift) % radix == radix - 1 or (t >> shift) % radix == radix - 1:
                return False
            higher = (y >> (target + 1)) % (1 << (self.guard - 1))
            if not 2 * radix <= higher < (1 << (self.guard - 1)) - 2 * radix:
                return False
        return True

    def run(self, state, source, inverse=False, freeze_source=False):
        """Ten literal modular shears; inversion reverses and negates each.

        Source is called at CURRENT y for both load operations. No inverse
        table, good-set simplification, source primitive or guard is used here.
        freeze_source is an intentionally incorrect negative control.
        """
        state = list(state)
        masks = ((1 << self.control_bits) - 1,) * 2 + ((1 << self.y_bits) - 1,)
        radix_mask = (1 << self.digit_bits) - 1
        frozen = source(state[2]) if freeze_source else None
        for step in reversed(range(10)) if inverse else range(10):
            u, t, y = state
            if step in (4, 9):
                bits = frozen if freeze_source else source(y)
                field = 0
                offset = sum(bit << (i * self.digit_bits) for i, bit in enumerate(bits))
                if step == 9:
                    offset = -offset
            else:
                shear = step if step < 4 else step - 5
                field = 2 if shear in (0, 2) else 1
                offset = 0
                for i, target in enumerate(self.targets):
                    z = (u >> (i * self.digit_bits)) & 1
                    digit = (t >> (i * self.digit_bits)) & radix_mask
                    bit = (y >> target) & 1
                    if shear == 0:
                        offset += (2 * z * digit) << target
                    elif shear == 1:
                        offset += bit << (i * self.digit_bits)
                    elif shear == 2:
                        offset += (z * (1 - 2 * digit)) << target
                    else:
                        offset -= (bit ^ z) << (i * self.digit_bits)
            state[field] = (state[field] + (-offset if inverse else offset)) & masks[field]
        return tuple(state)

    def ideal(self, state, source):
        u, t, y = state
        delta = sum(bit << target for bit, target in zip(source(y), self.targets))
        return u, t, y ^ delta

    def check_source(self, source):
        for y in range(1 << self.y_bits):
            bits = source(y)
            require(len(bits) == len(self.targets) and all(bit in (0, 1) for bit in bits),
                    "Boolean source dimension")
            for target in self.targets:
                require(bits == source(y ^ (1 << target)), "all-target source independence")


def radix_pairs(pairs, bits):
    for bit in range(bits):
        low, high = [], []
        for pair in pairs:
            (high if (pair[0] >> bit) & 1 else low).append(pair)
        pairs = low + high
    return pairs


def repair(word, source, values):
    """Extract actual holes, compute inverse at each hole, sort and reinsert."""
    raw = [None] * word.size
    for address, payload in enumerate(values):
        destination = word.pack(word.run(word.unpack(address), source))
        require(raw[destination] is None, "raw permutation injectivity")
        raw[destination] = payload
    holes = [not word.good(word.unpack(q)) for q in range(word.size)]
    pairs = []
    for q, is_hole in enumerate(holes):
        if is_hole:
            origin = word.run(word.unpack(q), source, inverse=True)
            key = word.pack(word.ideal(origin, source))
            pairs.append((key, raw[q]))
    pairs = radix_pairs(pairs, word.address_bits)
    cursor = 0
    for q, is_hole in enumerate(holes):
        if is_hole:
            key, payload = pairs[cursor]
            require(key == q, "sorted key must equal current marked hole")
            raw[q] = payload
            cursor += 1
    require(cursor == len(pairs), "exception stream exhaustion")
    for address, payload in enumerate(values):
        destination = word.pack(word.ideal(word.unpack(address), source))
        require(raw[destination] == payload, "ideal payload correspondence")
    return raw, len(pairs)


def digest(values):
    data = b"".join(value.to_bytes(4, "little") for value in values)
    return hashlib.sha256(data).hexdigest()


def compare_source(word, source, state, original):
    kwargs = dict(bits=word.digit_bits, positions=word.targets,
                  ybits=word.y_bits, control_bits=word.control_bits)
    require(word.run(state, source) == original.compact(*state, source, **kwargs),
            "independent shears disagree with pinned compact")
    require(word.good(state) == original.good(*state, bits=word.digit_bits,
            positions=word.targets, guard=word.guard), "independent good predicate")


def complete_domain(name, word, source, original):
    word.check_source(source)
    good_count = 0
    upper_digit_changes = 0
    for address in range(word.size):
        state = word.unpack(address)
        out = word.run(state, source)
        require(word.run(out, source, inverse=True) == state, "explicit inverse after forward")
        before = word.run(state, source, inverse=True)
        require(word.run(before, source) == state, "forward after explicit inverse")
        compare_source(word, source, state, original)
        wanted = word.ideal(state, source)
        is_good = word.good(state)
        require(word.good(out) == is_good and word.good(wanted) == is_good,
                "good and bad sets invariant")
        if is_good:
            require(out == wanted, "arbitrary-source endpoint on good set")
            good_count += 1
        used = len(word.targets) * word.digit_bits
        upper_digit_changes += any((state[i] >> used) != (out[i] >> used) for i in (0, 1))
    final, bad = repair(word, source, list(range(word.size)))
    return dict(name=name, parameters=word.__dict__, addresses=word.size,
                good_addresses=good_count, repaired_bad_addresses=bad,
                inactive_control_change_cases=upper_digit_changes,
                repaired_payload_sha256=digest(final))


def sampled_domains(original):
    rng = random.Random(4100763)
    parameters = [
        Word(2, 5, 13, (1, 7), 6),
        Word(3, 10, 23, (0, 8, 16), 7),
        Word(4, 14, 29, (2, 11, 20), 8),
        Word(1, 6, 21, (1, 6, 11, 16), 5),
    ]
    count = good_count = 0
    for word in parameters:
        selected = sum(1 << j for j in word.targets)
        def source(y):
            other = y & ~selected
            return tuple(((other >> (i + 1)).bit_count() ^ (other >> (i + 3))) & 1
                         for i in range(len(word.targets)))
        for _ in range(256):
            state = (rng.randrange(1 << word.control_bits),
                     rng.randrange(1 << word.control_bits), rng.randrange(1 << word.y_bits))
            out = word.run(state, source)
            require(word.run(out, source, inverse=True) == state, "sample inverse")
            before = word.run(state, source, inverse=True)
            require(word.run(before, source) == state, "sample other inverse direction")
            compare_source(word, source, state, original)
            wanted = word.ideal(state, source)
            require(word.good(state) == word.good(out) == word.good(wanted), "sample invariance")
            if word.good(state):
                require(out == wanted, "sample good endpoint")
                good_count += 1
            count += 1
    require(good_count > 0, "samples include good states")
    return dict(seed=4100763, states=count, good_states=good_count,
                parameters=[word.__dict__ for word in parameters])


def actual_caller(original, caller):
    """Same source network/packing as the frozen caller; new inverse/repair."""
    values = list(range(4096))
    table_values = values[:]
    networks = [original.benes(original.rotation(8, 5, (2 * a) % 5 if a < 3 else 0))
                for a in range(4)]
    schedule = []
    for layer in range(5):
        target = networks[0][layer][0]
        require(all(net[layer][0] == target for net in networks), "common Benes schedule")
        word = Word(2, 2, 8, (target,), 6)
        def source(y, layer=layer):
            return (networks[(y >> 3) & 3][layer][1][y & 7],)
        word.check_source(source)
        schedule.append((word, source))
    repairs = 0
    forward_hash = None
    for index, (word, source) in enumerate(schedule + list(reversed(schedule))):
        values, count = repair(word, source, values)
        table_values, table_count = caller.layer(table_values, word.targets[0], source)
        require(values == table_values and count == table_count, "actual caller comparison")
        repairs += count
        if index == 4:
            oracle = [None] * 4096
            for address in range(4096):
                u, t, y = word.unpack(address)
                a, b = (y >> 3) & 3, y & 7
                new_b = (b + 2 * a) % 5 if a < 3 and b < 5 else b
                oracle[word.pack((u, t, (y & ~7) | new_b))] = address
            require(values == oracle, "direct padded CRT rotation with dirty spectators")
            forward_hash = digest(values)
    require(values == list(range(4096)), "all ten layers restore every payload")
    return dict(addresses=4096, repaired_layers=10, exceptional_pair_visits=repairs,
                forward_payload_sha256=forward_hash, inverse_payload_sha256=digest(values),
                original_caller_agrees=True)


def negative_controls():
    controls = []
    word = Word(2, 4, 12, (0, 6), 6)
    own_only = lambda y: ((y >> 6) & 1, 0)
    state = (4, 0, 1040)
    require(word.good(state), "own-target mutant starts inside good set")
    require(word.run(state, own_only) == (5, 0, 1041), "literal own-target witness")
    require(word.ideal(state, own_only) == (4, 0, 1040), "ideal own-target witness")
    require(all(own_only(y)[i] == own_only(y ^ (1 << target))[i]
                for y in range(4096) for i, target in enumerate(word.targets)),
            "mutant really omits each component's own target")
    controls.append(dict(name="own_target_only_is_insufficient", state=state,
                         actual=word.run(state, own_only), ideal=word.ideal(state, own_only)))
    word = Word(2, 3, 6, (0,), 6)
    source = lambda y: (((y >> 1).bit_count() & 1),)
    holes = [q for q in range(word.size) if not word.good(word.unpack(q))]
    witnesses = {}
    wrong_keys = []
    for q in holes:
        state = word.unpack(q)
        origin = word.run(state, source, inverse=True)
        right = word.pack(word.ideal(origin, source))
        wrong = word.pack(word.ideal(state, source))
        wrong_keys.append(wrong)
        if right != wrong:
            witnesses.setdefault("ideal_of_current_address", dict(address=q, right_key=right, wrong_key=wrong))
        frozen = word.run(state, source, inverse=True, freeze_source=True)
        if frozen != origin:
            witnesses.setdefault("inverse_reuses_stale_source", dict(address=q, right_origin=origin, wrong_origin=frozen))
        simplified = word.ideal(state, source)
        if simplified != origin:
            witnesses.setdefault("guarded_identity_used_as_bad_inverse",
                                 dict(address=q, right_origin=origin, wrong_origin=simplified))
    require(sorted(wrong_keys) == holes, "wrong T(q) keys still fill all holes")
    for name in ("ideal_of_current_address", "inverse_reuses_stale_source",
                 "guarded_identity_used_as_bad_inverse"):
        require(name in witnesses, "discriminating control: " + name)
        controls.append(dict(name=name, **witnesses[name]))
    keys = [word.pack(word.ideal(word.run(word.unpack(q), source, inverse=True), source)) for q in holes]
    truncated = [key & ((1 << (word.address_bits - 1)) - 1) for key in keys]
    require(len(set(truncated)) < len(truncated), "truncated full key creates collisions")
    controls.append(dict(name="truncated_high_control_key", holes=len(holes),
                         distinct_truncated_keys=len(set(truncated))))
    return controls


def run():
    source_count = authenticate()
    original = source_module("_audited_batched_crt", "check_batched_crt.py")
    saved = sys.modules.get("check_batched_crt")
    try:
        sys.modules["check_batched_crt"] = original
        caller = source_module("_audited_compact_crt", "check_compact_crt.py")
    finally:
        if saved is None:
            sys.modules.pop("check_batched_crt", None)
        else:
            sys.modules["check_batched_crt"] = saved
    one = Word(2, 3, 6, (0,), 6)
    two = Word(1, 3, 10, (0, 5), 5)
    cases = [
        ("constant_one", one, lambda y: (1,)),
        ("guard_parity", one, lambda y: ((y >> 1).bit_count() & 1,)),
        ("nonlinear_guard", one, lambda y: (((y >> 1) & (y >> 4)) & 1,)),
        ("two_targets_cross_guard", two,
         lambda y: (((y >> 3) ^ (y >> 7)) & 1,
                    ((y & ~33).bit_count() ^ ((y >> 2) & (y >> 8))) & 1)),
    ]
    domains = [complete_domain(name, word, source, original) for name, word, source in cases]
    require(any(row["inactive_control_change_cases"] for row in domains),
            "complete domains exercise inactive high control changes")
    return dict(status="PASS_CRT_ARBITRARY_SOURCE_REPAIR", source_inputs=source_count,
                exhaustive_domains=domains, sampled_domains=sampled_domains(original),
                actual_caller=actual_caller(original, caller), negative_controls=negative_controls(),
                universal_argument="PROOF.md; written proof, not inferred from finite checks",
                machine_cost_verified=False, new_kappa_claimed=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="explicitly write the regenerated receipt")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(text)
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(json.loads(text) == expected, "committed result differs")
    print(text, end="")


if __name__ == "__main__":
    main()
