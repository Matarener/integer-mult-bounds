#!/usr/bin/env python3
"""Independent lease-end algebra and CALL-cut mutants.

Does not import verify.py. Admission uses need() so gates survive -O.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_BIT_LEASE_END_CALL "
    "stale_clear_preserves_borrower "
    "call_requires_empty_pool "
    "three_mutants "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
INPUTS = (
    "research/selected-bit-physical-caller/scratch_pool.py",
    "research/selected-bit-physical-caller/macro_machine.py",
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


class MiniTape:
    """Minimal physical scratch role: symbols after a LEFT origin."""

    def __init__(self):
        self.cells = [0]  # LEFT sentinel as 0; payload bits are 0/1

    def append(self, symbol):
        self.cells.append(int(symbol) & 1)

    def clear(self):
        self.cells = [0]

    def read_payload(self):
        return tuple(self.cells[1:])


class Lease:
    def __init__(self, pool, slot, physical):
        self.pool = pool
        self.slot = slot
        self.physical = physical
        self.active = True

    def read_payload(self):
        need(self.active and self.pool.live.get(self.slot) is self,
             "live scratch lease")
        return self.physical.read_payload()

    def append(self, symbol):
        need(self.active and self.pool.live.get(self.slot) is self,
             "live scratch lease")
        self.physical.append(symbol)

    def clear(self):
        # Source annotation: ended lease close is a no-op.
        if not self.active:
            return
        self.physical.clear()
        self.active = False
        del self.pool.live[self.slot]


class ScratchPool:
    def __init__(self, capacity):
        need(type(capacity) is int and capacity > 0, "fixed scratch capacity")
        self.tapes = tuple(MiniTape() for _ in range(capacity))
        self.live = {}

    def acquire(self):
        for slot, tape in enumerate(self.tapes):
            if slot not in self.live:
                need(tape.read_payload() == (), "empty scratch role before reuse")
                lease = Lease(self, slot, tape)
                self.live[slot] = lease
                return lease
        raise ValueError("fixed scratch role inventory exhausted")

    def empty(self):
        need(not self.live, "completed macro closes all scratch leases")
        for tape in self.tapes:
            need(tape.read_payload() == (), "completed macro leaves scratch bodies empty")


class MutantClearNoActiveGuard(Lease):
    """Semantic mutant: stale clear still erases the physical role."""

    def clear(self):
        self.physical.clear()
        self.active = False
        if self.slot in self.pool.live and self.pool.live[self.slot] is self:
            del self.pool.live[self.slot]
        elif self.slot in self.pool.live:
            # Erase whatever currently owns the slot — the forbidden behaviour.
            del self.pool.live[self.slot]


class MutantPoolSkipEmpty(ScratchPool):
    """Semantic mutant: CALL cut that forgets to require an empty pool."""

    def empty(self):
        return  # acceptance gap: live leases silently cross the cut


def correct_borrower_preservation():
    pool = ScratchPool(2)
    first = pool.acquire()
    first.append(0)
    first.clear()
    second = pool.acquire()
    second.append(1)
    need(first.slot == second.slot, "reuse physical scratch role")
    first.clear()  # stale
    need(second.read_payload() == (1,), "stale cleanup preserves borrower")
    try:
        first.read_payload()
    except ValueError as exc:
        need(str(exc) == "live scratch lease", "stale read message")
    else:
        need(False, "stale read accepted")
    second.clear()
    pool.empty()
    return True


def mutant_stale_clear_erases_borrower():
    """Counterexample: omitting the active guard lets a stale clear wipe the new owner."""
    pool = ScratchPool(1)
    first = pool.acquire()
    # Replace with mutant lease object after first end, simulating a bad clear impl
    # by installing a mutant class method on a fresh pool.
    pool = ScratchPool(1)
    # Build mutant lease manually
    slot = 0
    tape = pool.tapes[slot]
    first = MutantClearNoActiveGuard(pool, slot, tape)
    pool.live[slot] = first
    first.append(0)
    first.clear()
    need(not first.active and slot not in pool.live, "mutant first end")
    second = Lease(pool, slot, tape)
    pool.live[slot] = second
    second.active = True
    second.append(1)
    need(second.read_payload() == (1,), "borrower wrote")
    first.clear()  # stale mutant clear: wipes physical role and drops live map
    need(tape.read_payload() == (), "mutant erased borrower payload")
    need(slot not in pool.live, "mutant dropped current owner from live")
    return True


def call_cut_requires_empty():
    pool = ScratchPool(1)
    lease = pool.acquire()
    lease.append(1)
    try:
        pool.empty()
    except ValueError as exc:
        need(str(exc) == "completed macro closes all scratch leases",
             "live lease blocks CALL cut")
    else:
        need(False, "CALL cut accepted live lease")
    lease.clear()
    pool.empty()
    return True


def mutant_call_skip_empty_crosses():
    pool = MutantPoolSkipEmpty(1)
    lease = pool.acquire()
    lease.append(1)
    pool.empty()  # mutant: no-op
    need(bool(pool.live), "mutant allows live lease across CALL cut")
    need(lease.active and lease.read_payload() == (1,),
         "parent dirt survives skipped empty")
    return True


def authenticate_sources(texts):
    scratch = texts["research/selected-bit-physical-caller/scratch_pool.py"]
    machine = texts["research/selected-bit-physical-caller/macro_machine.py"]
    proof = texts["research/selected-bit-physical-caller/PROOF.md"]
    contract = texts["docs/research/selected-bit-physical-contract-map.md"]

    need("No lease crosses CALL" in scratch, "cite: pool docstring CALL")
    need("stale close does nothing, while a stale read rejects" in proof,
         "cite: PROOF lease-end")
    need("it cannot erase a newer borrower of the role" in proof,
         "cite: PROOF borrower protection")
    need("none crosses CALL" in proof, "cite: PROOF no lease across CALL")
    need("lease-end annotations and CALL invariants" in contract,
         "cite: contract-map open audit")

    # Structural source correspondence for clear() active guard.
    need("if not self.active:" in scratch and "return" in scratch, "source clear active guard")
    need("del self.pool.live[self.slot]" in scratch, "source ends live map")
    need('raise ValueError("live scratch lease")' in scratch, "source stale reject")

    # CALL cut: call() begins with pool.empty() before parking.
    need("def call(self, grants):" in machine, "source call method")
    call_idx = machine.index("def call(self, grants):")
    call_body = machine[call_idx:call_idx + 800]
    lines = [ln.strip() for ln in call_body.splitlines()[:10]]
    need(lines[0] == "def call(self, grants):", "call def line")
    need(lines[1] == "self.pool.empty()", "pool.empty is first statement in call()")
    need("self.streams.park()" in call_body, "park follows empty")
    need(call_body.index("self.pool.empty()") < call_body.index("self.streams.park()"),
         "empty before park")
    need('need(not self.live, "completed macro closes all scratch leases")' in scratch,
         "empty rejects live leases")
    need("lease-end annotations" in contract, "contract names lease-end audit")
    return {
        "scratch_call_docstring": True,
        "proof_borrower_protection": True,
        "call_opens_with_empty": True,
        "contract_names_lease_end_audit": True,
    }


def evaluate():
    texts = pin_sources()
    source_report = authenticate_sources(texts)
    need(correct_borrower_preservation(), "correct algebra")
    need(mutant_stale_clear_erases_borrower(), "mutant stale clear")
    need(call_cut_requires_empty(), "call cut gate")
    need(mutant_call_skip_empty_crosses(), "mutant skip empty")
    # Third mutant: clear that forgets to remove from live blocks reuse.
    pool = ScratchPool(1)

    class StickyLive(Lease):
        def clear(self):
            if not self.active:
                return
            self.physical.clear()
            self.active = False
            # forgot: del self.pool.live[self.slot]

    first = StickyLive(pool, 0, pool.tapes[0])
    pool.live[0] = first
    first.append(1)
    first.clear()
    need(not first.active and 0 in pool.live, "sticky live remains")
    try:
        pool.acquire()
    except ValueError as exc:
        need(str(exc) == "fixed scratch role inventory exhausted",
             "sticky live blocks reuse")
    else:
        need(False, "sticky live allowed reacquire")

    report = {
        "schema_version": 1,
        "status": "PASS_SELECTED_BIT_LEASE_END_CALL",
        "marker": MARKER,
        "kappa_decimal": KAPPA_DECIMAL,
        "no_new_kappa": True,
        "stale_clear_preserves_borrower": True,
        "stale_read_rejects": True,
        "call_requires_empty_pool": True,
        "mutants": {
            "stale_clear_erases_borrower": True,
            "call_skip_empty_crosses_lease": True,
            "clear_without_del_live_blocks_reuse": True,
        },
        "source_correspondence": source_report,
        "scope": (
            "PR2809 ScratchPool lease-end annotations and Machine.call "
            "empty-pool cut; independent algebra and three semantic mutants; "
            "not GL64 execution, H2, stock-envelope, or route-cube"
        ),
    }
    return report


def main():
    report = evaluate()
    print(report["marker"])


if __name__ == "__main__":
    main()
