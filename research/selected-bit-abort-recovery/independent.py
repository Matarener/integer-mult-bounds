#!/usr/bin/env python3
"""Independent NumericLease / SharedFrame interrupt-abort algebra.

Does not import verify.py. Admission uses need() so gates survive -O.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_BIT_ABORT_RECOVERY "
    "preparing_rollback "
    "child_interrupt_nonstrict "
    "return_vs_interrupt "
    "parking_out_of_contract "
    "three_mutants "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
INPUTS = (
    "research/selected-bit-physical-caller/numerical_frame.py",
    "research/selected-bit-physical-caller/PROOF.md",
    "docs/research/selected-bit-physical-contract-map.md",
    "research/physical-ordinary-interchange/ordinary.py",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "base pin")
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    texts = {}
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"],
             "source hash: " + row["path"])
        texts[row["path"]] = raw.decode("utf-8")
    return texts


class MiniArena:
    """Finite live-slot bank used by the independent abort algebra."""

    def __init__(self, live=()):
        self.live = set(live)
        self._next = (max(self.live) + 1) if self.live else 0

    def alloc(self):
        slot = self._next
        self._next += 1
        self.live.add(slot)
        return slot

    def free(self, slot):
        need(slot in self.live, "free live slot")
        self.live.remove(slot)

    def rollback(self, protected):
        self.live = set(protected)


class Codec:
    def __init__(self):
        self.parked = False
        self.fail_park = False

    def park(self, _keep):
        if self.fail_park:
            raise ValueError("injected incomplete park")
        self.parked = True

    def restore(self):
        need(self.parked, "restore after park")
        self.parked = False


class NumericLease:
    """Phase machine mirroring PR2809 numerical_frame.NumericLease abort paths."""

    def __init__(self, arena, indices, codec, fail_at=None, extra_child_slots=0):
        self.arena, self.indices, self.codec = arena, indices, codec
        self.modulus = self.width = self.depth = None
        self.ring_one = self.context_cap = None
        self.phase = "preparing"
        self.entry_residues = frozenset(arena.live)
        self.entry_indices = frozenset(indices.live)
        self.extra_child_slots = extra_child_slots
        try:
            self.modulus = arena.alloc()
            self.width = indices.alloc()
            self.depth = indices.alloc()
            if fail_at == "preparing":
                raise ValueError("injected preparing failure")
            self.phase = "parking"
            if fail_at == "parking":
                codec.fail_park = True
            codec.park(({self.modulus}, {self.width, self.depth}))
            self.phase = "child"
            self.ring_one = arena.alloc()
            self.context_cap = arena.alloc()
            for _ in range(extra_child_slots):
                arena.alloc()
            if fail_at == "child":
                raise ValueError("injected child-phase failure")
        except BaseException:
            if self.phase == "preparing":
                self.arena.rollback(self.entry_residues)
                self.indices.rollback(self.entry_indices)
                self.phase = "closed"
            elif self.phase == "child":
                self.close(strict=False)
            # Parking-phase incomplete codec ops are outside the retained contract.
            raise

    def close(self, strict=True):
        need(self.phase == "child", "one completed numerical lease return")
        first_error = None
        if strict:
            residues = {self.modulus, self.ring_one, self.context_cap}
            indices = {self.width, self.depth}
            if self.arena.live != residues or self.indices.live != indices:
                first_error = ValueError(
                    "callee closes its numerical locals before Frame return"
                )
        for slot in (self.modulus, self.ring_one, self.context_cap):
            if slot is not None and slot in self.arena.live:
                self.arena.free(slot)
        for slot in (self.width, self.depth):
            if slot is not None and slot in self.indices.live:
                self.indices.free(slot)
        self.arena.rollback(frozenset())
        self.indices.rollback(frozenset())
        self.codec.restore()
        self.phase = "closed"
        if first_error is not None and strict:
            raise first_error


class SharedFrame:
    """Return-versus-interrupt distinction for SharedFrame.close."""

    def __init__(self, lease, callee_returned=False):
        self.lease = lease
        self.callee_returned = callee_returned
        self.closed = False

    def close(self):
        need(not self.closed, "shared Frame closes once")
        try:
            self.lease.close(strict=self.callee_returned)
        finally:
            self.closed = True


def preparing_rollback_restores_entry():
    arena, indices = MiniArena({10, 11}), MiniArena({20})
    codec = Codec()
    try:
        NumericLease(arena, indices, codec, fail_at="preparing")
    except ValueError as exc:
        need(str(exc) == "injected preparing failure", "preparing message")
    else:
        need(False, "preparing failure swallowed")
    need(arena.live == {10, 11}, "preparing rollback residues")
    need(indices.live == {20}, "preparing rollback indices")
    need(not codec.parked, "preparing never parks")
    return True


def child_interrupt_nonstrict_restores():
    """SharedFrame construction failure after park uses close(strict=False)."""
    arena, indices = MiniArena({10}), MiniArena({20})
    codec = Codec()
    try:
        NumericLease(arena, indices, codec, fail_at="child", extra_child_slots=2)
    except ValueError as exc:
        need(str(exc) == "injected child-phase failure", "child message")
    else:
        need(False, "child failure swallowed")
    need(arena.live == set() and indices.live == set(), "child interrupt clears banks")
    need(not codec.parked, "child interrupt restores parent")
    return True


def return_vs_interrupt_strictness():
    """Successful return uses strict inventory; interrupt uses non-strict."""
    # Successful return: exact inventory, strict close OK.
    arena, indices = MiniArena(), MiniArena()
    codec = Codec()
    lease = NumericLease(arena, indices, codec)
    need(lease.phase == "child", "child after success")
    frame = SharedFrame(lease, callee_returned=True)
    frame.close()
    need(lease.phase == "closed" and not codec.parked, "strict return closes")

    # Interrupt path: leftover child dirt; non-strict close still restores.
    arena, indices = MiniArena({99}), MiniArena({88})
    codec = Codec()
    lease = NumericLease(arena, indices, codec, extra_child_slots=1)
    need(len(arena.live) > 3, "dirty child locals present")
    frame = SharedFrame(lease, callee_returned=False)
    frame.close()
    need(lease.phase == "closed" and not codec.parked, "interrupt nonstrict restores")
    need(arena.live == set() and indices.live == set(), "interrupt clears dirt")
    return True


def parking_out_of_contract_no_recovery():
    """Parking-phase failure neither rolls back nor runs child close."""
    arena, indices = MiniArena({10}), MiniArena({20})
    codec = Codec()
    try:
        NumericLease(arena, indices, codec, fail_at="parking")
    except ValueError as exc:
        need(str(exc) == "injected incomplete park", "parking message")
    else:
        need(False, "parking failure swallowed")
    # Grants allocated during preparing remain; no preparing/child recovery branch ran.
    need(10 in arena.live and len(arena.live) > 1, "parking leaves preparing residue grants")
    need(20 in indices.live and len(indices.live) > 1, "parking leaves preparing index grants")
    need(not codec.parked, "failed park did not complete")
    return True


def mutant_preparing_without_rollback():
    """Counterexample: omit preparing rollback; orphan slots remain."""
    arena, indices = MiniArena({10}), MiniArena({20})
    codec = Codec()

    class MutantLease(NumericLease):
        def __init__(self, *args, **kwargs):
            self.arena, self.indices, self.codec = args[0], args[1], args[2]
            self.modulus = self.width = self.depth = None
            self.ring_one = self.context_cap = None
            self.phase = "preparing"
            self.entry_residues = frozenset(self.arena.live)
            self.entry_indices = frozenset(self.indices.live)
            try:
                self.modulus = self.arena.alloc()
                self.width = self.indices.alloc()
                self.depth = self.indices.alloc()
                raise ValueError("injected preparing failure")
            except BaseException:
                # Mutant: forgot preparing rollback.
                self.phase = "closed"
                raise

    try:
        MutantLease(arena, indices, codec)
    except ValueError:
        pass
    else:
        need(False, "mutant preparing swallowed")
    need(arena.live != {10}, "mutant left orphan residue slots")
    need(indices.live != {20}, "mutant left orphan index slots")
    return True


def mutant_child_interrupt_strict():
    """Counterexample: child interrupt uses strict=True and rejects leftover locals."""
    arena, indices = MiniArena(), MiniArena()
    codec = Codec()
    lease = NumericLease(arena, indices, codec, extra_child_slots=2)
    try:
        lease.close(strict=True)
    except ValueError as exc:
        need(
            str(exc) == "callee closes its numerical locals before Frame return",
            "strict rejects dirty interrupt",
        )
    else:
        need(False, "strict accepted dirty interrupt")
    # After failed strict close the source still restores (strict raises after cleanup),
    # but the mutant acceptance gap is that interrupt *requires* the successful inventory.
    need(lease.phase == "closed" and not codec.parked, "strict still cleans then raises")
    return True


def mutant_always_strict_frame_close():
    """Counterexample: SharedFrame.close ignores callee_returned and always uses strict."""
    arena, indices = MiniArena({50}), MiniArena({60})
    codec = Codec()
    lease = NumericLease(arena, indices, codec, extra_child_slots=1)

    class AlwaysStrict(SharedFrame):
        def close(self):
            need(not self.closed, "shared Frame closes once")
            try:
                self.lease.close(strict=True)  # mutant: ignore callee_returned
            finally:
                self.closed = True

    frame = AlwaysStrict(lease, callee_returned=False)
    try:
        frame.close()
    except ValueError as exc:
        need(
            str(exc) == "callee closes its numerical locals before Frame return",
            "always-strict interrupt rejects",
        )
    else:
        need(False, "always-strict interrupt accepted")
    return True


def authenticate_sources(texts):
    frame = texts["research/selected-bit-physical-caller/numerical_frame.py"]
    proof = texts["research/selected-bit-physical-caller/PROOF.md"]
    contract = texts["docs/research/selected-bit-physical-contract-map.md"]
    ordinary = texts["research/physical-ordinary-interchange/ordinary.py"]

    need("Incomplete codec operations are outside the retained interruption"
         in frame, "cite: codec out of contract")
    need("distinguish return from interrupted exit" in frame,
         "cite: Callee docstring")
    need("self.lease.close(strict=self.callee_returned)" in frame,
         "cite: return-vs-interrupt gate")
    need('if self.phase == "preparing":' in frame
         and "self.arena.rollback(self.entry_residues)" in frame,
         "cite: preparing rollback")
    need('elif self.phase == "child":' in frame
         and "self.close(strict=False)" in frame,
         "cite: child-phase nonstrict")
    need("self.lease.close(strict=False)" in frame,
         "cite: SharedFrame construction interrupt")
    need("does not require transactional\nrecovery from interruption halfway through a parking-table command"
         in proof or "recovery from interruption halfway through a parking-table command"
         in proof, "cite: PROOF parking-table limit")
    need("not interrupted-macro recovery" in contract,
         "cite: contract-map PR2899 boundary")
    need("No interrupted-macro\n    recovery guarantee is part of this mathematical interface"
         in ordinary or "No interrupted-macro recovery guarantee" in ordinary,
         "cite: ordinary B1 interface limit")
    return {
        "preparing_rollback_present": True,
        "child_nonstrict_present": True,
        "return_vs_interrupt_gate": True,
        "codec_parking_out_of_contract": True,
        "contract_names_interrupt_gap": True,
        "ordinary_disclaims_interrupt": True,
    }


def evaluate():
    texts = pin_sources()
    source_report = authenticate_sources(texts)
    need(preparing_rollback_restores_entry(), "preparing rollback")
    need(child_interrupt_nonstrict_restores(), "child interrupt")
    need(return_vs_interrupt_strictness(), "return vs interrupt")
    need(parking_out_of_contract_no_recovery(), "parking out of contract")
    need(mutant_preparing_without_rollback(), "mutant preparing")
    need(mutant_child_interrupt_strict(), "mutant strict interrupt")
    need(mutant_always_strict_frame_close(), "mutant always-strict frame")

    report = {
        "schema_version": 1,
        "status": "PASS_SELECTED_BIT_ABORT_RECOVERY",
        "marker": MARKER,
        "kappa_decimal": KAPPA_DECIMAL,
        "no_new_kappa": True,
        "preparing_rollback": True,
        "child_interrupt_nonstrict": True,
        "return_vs_interrupt": True,
        "parking_out_of_contract": True,
        "mutants": {
            "preparing_without_rollback_leaves_orphans": True,
            "child_interrupt_strict_rejects_dirt": True,
            "always_strict_frame_rejects_interrupt": True,
        },
        "source_correspondence": source_report,
        "scope": (
            "PR2809 NumericLease/SharedFrame interrupt-abort discipline: "
            "preparing rollback, child-phase nonstrict close, return-versus-interrupt "
            "strictness gate, and explicit parking mid-command out-of-contract boundary; "
            "independent algebra and three semantic mutants; not lease-end/CALL empty, "
            "GL64, H2, stock-envelope, or route-cube"
        ),
    }
    return report


def main():
    report = evaluate()
    print(report["marker"])


if __name__ == "__main__":
    main()
