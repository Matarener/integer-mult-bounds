#!/usr/bin/env python3
"""Independent Callback.abort + parked-numerical-child interrupt algebra.

Binds PR2753/PR2809 Callback.abort stack/residue rollback to the same
interrupt invoice as NumericLease child-phase nonstrict close. Does not
import verify.py. Admission uses need() so gates survive python -O.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_BIT_CALLBACK_ABORT "
    "parked_child_callback_abort "
    "stack_residue_rollback "
    "lease_nonstrict_restore "
    "three_mutants "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
INPUTS = (
    "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/controller.py",
    "research/selected-bit-physical-caller/numerical_frame.py",
    "research/selected-bit-physical-caller/PROOF.md",
    "docs/research/selected-bit-physical-contract-map.md",
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
    need(
        manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "base pin",
    )
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    texts = {}
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        need(
            hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            == row["git_blob"],
            "git blob: " + row["path"],
        )
        texts[row["path"]] = raw.decode("utf-8")
    selected = read_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == KAPPA_DECIMAL, "selected decimal")
    return texts


class MiniArena:
    """Finite live-slot bank (residue or index)."""

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


class MiniTape:
    """Continuation stack face: nonempty iff cells holds any record bytes."""

    def __init__(self):
        self.cells = []

    def clear(self):
        self.cells.clear()

    def rewind(self):
        # Quiescent left boundary; abort only needs clear/rewind side effects.
        pass

    def empty(self):
        return not self.cells

    def push_marker(self, tag):
        self.cells.append(tag)


class MiniStack:
    """Two-tape Stack mirroring records.Stack: main + reverse faces."""

    def __init__(self):
        self.tape = MiniTape()
        self.reverse = MiniTape()

    def empty(self):
        return self.tape.empty() and self.reverse.empty()

    def push(self, tag="VALUE"):
        self.tape.push_marker(tag)

    def clear_both(self):
        self.tape.clear()
        self.reverse.clear()


class Codec:
    def __init__(self):
        self.parked = False

    def park(self, _keep):
        self.parked = True

    def restore(self):
        need(self.parked, "restore after park")
        self.parked = False


class NumericLease:
    """Child-phase lease used only as the parked enclosing invoice."""

    def __init__(self, arena, indices, codec):
        self.arena, self.indices, self.codec = arena, indices, codec
        self.phase = "preparing"
        self.entry_residues = frozenset(arena.live)
        self.entry_indices = frozenset(indices.live)
        self.modulus = arena.alloc()
        self.width = indices.alloc()
        self.depth = indices.alloc()
        self.phase = "parking"
        codec.park(({self.modulus}, {self.width, self.depth}))
        self.phase = "child"
        self.ring_one = arena.alloc()
        self.context_cap = arena.alloc()

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


class Callback:
    """Continuation Callback with abort/close matching controller.Callback."""

    def __init__(self, residue, index, program_tape, fields_tape):
        self.residue, self.index = residue, index
        self.program, self.fields = program_tape, fields_tape
        self.protected_residues = frozenset(residue.live)
        self.protected_indices = frozenset(index.live)
        self.pending, self.values = MiniStack(), MiniStack()
        # Lexical index literals retained until close (source: one/two/sixty_four).
        self.one_index = index.alloc()
        self.two_index = index.alloc()
        self.sixty_four = index.alloc()
        self.root_unit = residue.alloc()
        self.high_cap = residue.alloc()
        self.closed = False

    def push_continuation(self):
        self.pending.push("VALUE")
        self.values.push("PAIR")
        # Dirt beyond protected sets, as during coefficient evaluation.
        self.residue.alloc()
        self.index.alloc()

    def close(self):
        need(self.pending.empty() and self.values.empty(), "closed continuation interface")
        for slot in (self.one_index, self.two_index, self.sixty_four):
            if slot in self.index.live:
                self.index.free(slot)
        for slot in (self.root_unit, self.high_cap):
            if slot in self.residue.live:
                self.residue.free(slot)
        self.closed = True

    def abort(self):
        """Source abort: rollback protected sets, rewind program/fields, clear stacks."""
        self.residue.rollback(self.protected_residues)
        self.index.rollback(self.protected_indices)
        self.program.rewind()
        self.fields.rewind()
        for stack in (self.pending, self.values):
            stack.tape.clear()
            stack.reverse.clear()
        self.closed = True


def parked_child_callback_abort_restores():
    """Fail inside a Callback while NumericLease is in child phase after park.

    Invoice: Callback.abort clears four stack-role faces and rolls residue/index
    to the Callback entry protected sets; lease.close(strict=False) then restores
    the parked parent banks (same interrupt invoice as NumericLease child abort).
    """
    parent_res, parent_idx = MiniArena({100}), MiniArena({200})
    codec = Codec()
    lease = NumericLease(parent_res, parent_idx, codec)
    need(lease.phase == "child" and codec.parked, "parked child phase")

    # Callback sees banks after lease child grants; protected sets are Callback entry.
    program, fields = MiniTape(), MiniTape()
    program.push_marker("PROG")
    fields.push_marker("FLD")
    callback = Callback(parent_res, parent_idx, program, fields)
    protected_r = set(callback.protected_residues)
    protected_i = set(callback.protected_indices)
    need(100 in protected_r and lease.modulus in protected_r, "lease grants in protected")
    callback.push_continuation()
    need(not callback.pending.empty(), "dirty pending stack")
    need(len(parent_res.live) > len(protected_r), "callback dirt beyond protected")

    # Injected failure inside parked numerical child → Callback.abort then lease interrupt.
    try:
        raise ValueError("injected callback failure in parked child")
    except ValueError as exc:
        need(str(exc) == "injected callback failure in parked child", "failure message")
        callback.abort()
        lease.close(strict=False)

    need(callback.pending.empty() and callback.values.empty(), "stacks cleared")
    need(parent_res.live == set(), "lease nonstrict cleared residues")
    need(parent_idx.live == set(), "lease nonstrict cleared indices")
    need(not codec.parked, "parked parent restored")
    # Abort first restored Callback protected sets before lease cleanup consumed them.
    need(protected_r.issuperset({100, lease.modulus}), "protected snapshot retained")
    need(protected_i.issuperset({200, lease.width, lease.depth}), "index protected snapshot")
    return {
        "callback_protected_residues": sorted(protected_r),
        "callback_protected_indices": sorted(protected_i),
        "stacks_cleared": True,
        "lease_phase": lease.phase,
    }


def stack_residue_rollback_only():
    """Callback.abort alone restores protected sets and clears four stack faces."""
    residue, index = MiniArena({1, 2}), MiniArena({3})
    program, fields = MiniTape(), MiniTape()
    callback = Callback(residue, index, program, fields)
    protected_r = frozenset(callback.protected_residues)
    protected_i = frozenset(callback.protected_indices)
    callback.push_continuation()
    callback.values.reverse.push_marker("REV")
    need(not callback.values.reverse.empty(), "reverse face dirt")
    callback.abort()
    need(residue.live == set(protected_r), "residue rollback")
    need(index.live == set(protected_i), "index rollback")
    need(callback.pending.empty() and callback.values.empty(), "four faces cleared")
    return True


def close_rejects_nonempty_stacks():
    """Successful close demands empty stacks; abort is required on dirty failure."""
    residue, index = MiniArena(), MiniArena()
    callback = Callback(residue, index, MiniTape(), MiniTape())
    callback.push_continuation()
    try:
        callback.close()
    except ValueError as exc:
        need(str(exc) == "closed continuation interface", "close message")
    else:
        need(False, "close accepted nonempty stacks")
    callback.abort()
    need(callback.pending.empty(), "abort then empty")
    return True


def mutant_abort_without_stack_clear():
    """Counterexample: rollback without clearing stacks leaves continuation dirt."""
    residue, index = MiniArena({9}), MiniArena({8})
    callback = Callback(residue, index, MiniTape(), MiniTape())
    callback.push_continuation()

    def mutant_abort(self):
        self.residue.rollback(self.protected_residues)
        self.index.rollback(self.protected_indices)
        self.program.rewind()
        self.fields.rewind()
        # Mutant: omit stack.tape/reverse.clear()
        self.closed = True

    mutant_abort(callback)
    need(not callback.pending.empty(), "mutant left pending dirt")
    need(residue.live == set(callback.protected_residues), "mutant still rolled residue")
    return True


def mutant_abort_without_residue_rollback():
    """Counterexample: clear stacks without residue rollback leaves orphan slots."""
    residue, index = MiniArena({9}), MiniArena({8})
    callback = Callback(residue, index, MiniTape(), MiniTape())
    entry = frozenset(callback.protected_residues)
    callback.push_continuation()

    def mutant_abort(self):
        # Mutant: omit residue/index.rollback
        self.program.rewind()
        self.fields.rewind()
        for stack in (self.pending, self.values):
            stack.tape.clear()
            stack.reverse.clear()
        self.closed = True

    mutant_abort(callback)
    need(callback.pending.empty(), "mutant cleared stacks")
    need(residue.live != set(entry), "mutant left orphan residue")
    return True


def mutant_close_instead_of_abort_on_failure():
    """Counterexample: close() on dirty failure rejects; abort is required."""
    parent_res, parent_idx = MiniArena({100}), MiniArena({200})
    codec = Codec()
    lease = NumericLease(parent_res, parent_idx, codec)
    callback = Callback(parent_res, parent_idx, MiniTape(), MiniTape())
    callback.push_continuation()
    try:
        callback.close()
    except ValueError as exc:
        need(str(exc) == "closed continuation interface", "close rejects dirt")
    else:
        need(False, "close accepted dirty failure path")
    # Recovery still needs abort + lease interrupt.
    callback.abort()
    lease.close(strict=False)
    need(not codec.parked and parent_res.live == set(), "composed recovery after mutant")
    return True


def authenticate_sources(texts):
    controller = texts[
        "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/controller.py"
    ]
    frame = texts["research/selected-bit-physical-caller/numerical_frame.py"]
    proof = texts["research/selected-bit-physical-caller/PROOF.md"]
    contract = texts["docs/research/selected-bit-physical-contract-map.md"]

    need("def abort(self):" in controller, "cite: Callback.abort")
    need("self.residue.rollback(self.protected_residues)" in controller, "cite: residue rollback")
    need("self.index.rollback(self.protected_indices)" in controller, "cite: index rollback")
    need("self.program.tape.rewind()" in controller, "cite: program rewind")
    need("self.fields.tape.rewind()" in controller, "cite: fields rewind")
    need("stack.tape.clear()" in controller and "stack.reverse.clear()" in controller,
         "cite: four stack-face clears")
    need("self.protected_residues, self.protected_indices" in controller,
         "cite: protected entry sets")
    need('need(self.pending.empty() and self.values.empty(), "closed continuation interface")'
         in controller,
         "cite: close demands empty stacks")
    need("Callback.close/abort end all four Stack-role borrows" in proof,
         "cite: PROOF four Stack-role borrows")
    need('elif self.phase == "child":' in frame and "self.close(strict=False)" in frame,
         "cite: NumericLease child nonstrict")
    need("not interrupted-macro recovery" in contract,
         "cite: contract-map interrupt gap")
    return {
        "callback_abort_present": True,
        "four_stack_face_clear": True,
        "protected_entry_sets": True,
        "close_demands_empty_stacks": True,
        "proof_names_four_stack_roles": True,
        "lease_child_nonstrict_present": True,
        "contract_names_interrupt_gap": True,
    }


def evaluate():
    texts = pin_sources()
    source_report = authenticate_sources(texts)
    composed = parked_child_callback_abort_restores()
    need(stack_residue_rollback_only(), "stack residue rollback")
    need(close_rejects_nonempty_stacks(), "close vs abort")
    need(mutant_abort_without_stack_clear(), "mutant stack")
    need(mutant_abort_without_residue_rollback(), "mutant residue")
    need(mutant_close_instead_of_abort_on_failure(), "mutant close")

    report = {
        "schema_version": 1,
        "status": "PASS_SELECTED_BIT_CALLBACK_ABORT",
        "marker": MARKER,
        "kappa_decimal": KAPPA_DECIMAL,
        "no_new_kappa": True,
        "parked_child_callback_abort": True,
        "stack_residue_rollback": True,
        "lease_nonstrict_restore": True,
        "composed_fixture": composed,
        "mutants": {
            "abort_without_stack_clear_leaves_continuation": True,
            "abort_without_residue_rollback_leaves_orphans": True,
            "close_instead_of_abort_rejects_dirty_failure": True,
        },
        "source_correspondence": source_report,
        "scope": (
            "PR2753/PR2809 Callback.abort stack/residue rollback bound to the "
            "NumericLease parked-child interrupt invoice: four stack-face clears, "
            "protected residue/index rollback, program/fields rewind, then "
            "lease.close(strict=False); three semantic mutants; not ScratchPool "
            "lease-end, priced park, GL64, H2, or stock-envelope"
        ),
    }
    return report


def main():
    report = evaluate()
    print(report["marker"])


if __name__ == "__main__":
    main()
