# Lease-end annotations and the CALL empty-pool cut (PR2809)

## Claim

Pin Jose Manuel / jmbarrancoml's PR2809 archive on this repository at base
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, specifically
`research/selected-bit-physical-caller/scratch_pool.py` and
`macro_machine.py`, together with the written annotations in that package's
`PROOF.md` and the named remaining boundary in
`docs/research/selected-bit-physical-contract-map.md`.

Under the source's own ScratchPool contract:

1. **Lease-end.** Clearing an owned scratch value ends that lease: `active`
   becomes false and the slot is removed from `pool.live`. A later stale
   `clear` is a no-op. A stale `read` (or other live operation) rejects. In
   particular, a stale `clear` cannot erase a newer borrower of the same
   physical role.
2. **CALL cut.** `Machine.call` begins with `self.pool.empty()` before
   parking parent streams. `ScratchPool.empty` rejects whenever `pool.live`
   is nonempty. Hence no live lease identity crosses the recursive CALL cut
   on the successful path the source claims.

These are source-bound finite obligations. They do not establish the full
all-size physical refinement, selected GL64 execution, H2 primitives, stock
envelope constants, or supplier admission. Selected decimal kappa remains
`0.001672660197076918`.

## Independent algebra

Model a fixed inventory of physical roles. A lease holds a slot label and an
active bit. Acquire selects an empty role; clear ends the lease only when
active; empty requires no live leases and blank bodies.

Correctness of borrower preservation: end lease A, reacquire the same slot as
lease B, write a payload under B, then call A's `clear`. Because A is inactive,
the call returns immediately, B's payload and live map entry survive, and a
subsequent A read rejects.

CALL cut: with a live lease, `empty()` raises; after that lease ends, `empty()`
succeeds. Thus the first statement of `call` is an acceptance gate for the
cut invariant, not a documentation-only remark.

## Semantic counterexamples (acceptance gaps for omitted annotations)

The following mutants are **not** defects of the pinned source. They show that
each named annotation is load-bearing.

1. **Stale clear without an active guard.** A clear that always erases the
   physical role and drops whatever currently owns the slot lets an ended
   lease wipe a later borrower's payload and live map entry. The source's
   early `if not self.active: return` blocks this.
2. **Clear that forgets `del pool.live[slot]`.** Ending active without
   releasing the live map leaves the slot occupied, so reacquire reports
   inventory exhaustion even though the role is blank. The source's
   `del self.pool.live[self.slot]` is required for reuse.
3. **CALL that skips `pool.empty()`.** A no-op empty lets a live parent lease
   and its dirt remain across the simulated CALL cut. The source's leading
   `self.pool.empty()` in `call`, together with empty's live check, rejects
   that crossing.

## Source correspondence

Authenticated against the pinned bytes:

- `scratch_pool.py` documents "No lease crosses CALL", implements the active
  guard, live-map deletion, stale `ValueError("live scratch lease")`, and
  `need(not self.live, ...)` inside `empty`.
- `macro_machine.py` method `call` has `self.pool.empty()` as its first body
  statement, before `self.streams.park()`.
- `PROOF.md` records stale-close/no-op, stale-read reject, borrower
  protection, and "none crosses CALL".
- The physical-contract map names "lease-end annotations and CALL invariants"
  as the open independent-audit handoff after opcode/source work.

## What this does not claim

- It does not re-run PR2809's GL2 fixtures or claim formal refinement of the
  whole caller.
- It does not audit residual block implications already treated by
  `research/residual-call-refinement`, nor the compiler/Driver admission gap
  in `research/physical-compiler-correspondence`.
- It does not touch stock-envelope A/B/rho, route-cube fibre/key meters,
  gate-operand retargets, or rate-substitution reprints.
- No new kappa.
