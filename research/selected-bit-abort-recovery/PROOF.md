# NumericLease / SharedFrame interrupt-abort recovery (PR2809)

## Claim

Pin Jose Manuel / jmbarrancoml's PR2809 archive on this repository at base
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, specifically
`research/selected-bit-physical-caller/numerical_frame.py`, together with the
written interruption limit in that package's `PROOF.md`, the named PR2899
boundary in `docs/research/selected-bit-physical-contract-map.md`, and the
ordinary backend's interface disclaimer in
`research/physical-ordinary-interchange/ordinary.py`.

Under the source's own NumericLease / SharedFrame contract:

1. **Preparing-phase abort.** If construction fails while `phase == "preparing"`
   (before a completed park), both banks roll back to the exact entry live sets
   recorded at lease entry, and the phase closes. Parent slots present at entry
   are restored; grants allocated during the failed preparing attempt are not
   left live.
2. **Child-phase interrupt.** If failure occurs after park has completed
   (`phase == "child"`), including SharedFrame construction failure after the
   lease is installed, cleanup uses `close(strict=False)`. Non-strict close does
   not require the successful-return numerical inventory; it frees known grants,
   rolls back remaining child dirt, and restores the parked parent.
3. **Return versus interrupt.** `Callee.run_generator` sets `callee_returned`
   only after the node body completes. `SharedFrame.close` then calls
   `lease.close(strict=self.callee_returned)`. A completed return demands the
   exact inventory; an interrupted exit that reaches close without return does
   not.
4. **Parking mid-command out of contract.** If failure occurs while
   `phase == "parking"` (incomplete codec park), neither the preparing rollback
   nor the child nonstrict close runs. The source comment and PR2809 proof state
   that transactional recovery halfway through a parking-table command is not
   required. PR2899's ordinary interface likewise disclaims interrupted-macro
   recovery.

These are source-bound finite obligations. They do not establish the full
all-size physical refinement, selected GL64 execution, H2 primitives,
stock-envelope constants, lease-end/CALL-empty scratch cuts, or supplier
admission. Selected decimal kappa remains `0.001672660197076918`.

## Independent algebra

Model each numerical bank as a finite live-slot set. A lease records entry live
sets, then advances through phases `preparing → parking → child → closed`.
Acquire allocates slots; park marks the parent checkpoint; close optionally
checks a fixed successful inventory, frees known grants, rolls remaining live
slots to empty, and restores the parent.

Correct preparing abort: allocate during preparing, then fail before park;
rollback restores the entry sets. Correct child interrupt: after park, allocate
extra dirt and fail; nonstrict close clears both banks and restores. Correct
return gate: with exact inventory and `callee_returned=True`, strict close
succeeds; with leftover dirt and `callee_returned=False`, nonstrict close
succeeds. Parking failure leaves preparing grants live and does not restore a
completed park, matching the out-of-contract boundary.

## Semantic counterexamples (acceptance gaps for omitted branches)

The following mutants are **not** defects of the pinned source. They show that
each named branch is load-bearing.

1. **Preparing abort without rollback.** Closing the phase without restoring
   entry live sets leaves orphan residue and index slots beyond the parent
   entry. The source's preparing rollback blocks this.
2. **Child interrupt with strict close.** Requiring the successful-return
   inventory on a dirty interrupt raises
   `callee closes its numerical locals before Frame return`. The source's
   `close(strict=False)` on child-phase and SharedFrame construction failure
   avoids treating interrupt as a completed return.
3. **Always-strict SharedFrame.close.** Ignoring `callee_returned` and always
   passing `strict=True` rejects an interrupted exit that still holds leftover
   child locals. The source's `strict=self.callee_returned` gate is required for
   that distinction.

## Source correspondence

Authenticated against the pinned bytes:

- `numerical_frame.py` implements preparing rollback to `entry_residues` /
  `entry_indices`, child-phase `close(strict=False)`, SharedFrame construction
  interrupt with `lease.close(strict=False)`,
  `lease.close(strict=self.callee_returned)`, the Callee docstring distinguishing
  return from interrupted exit, and the comment that incomplete codec operations
  are outside the retained interruption contract.
- `PROOF.md` records that the claim does not require transactional recovery from
  interruption halfway through a parking-table command.
- The physical-contract map records that PR2899 covers successful admitted
  execution, not interrupted-macro recovery.
- `ordinary.py` states that no interrupted-macro recovery guarantee is part of
  the ordinary mathematical interface.

## What this does not claim

- It does not re-run PR2809's GL2 fixtures or claim formal refinement of the
  whole caller.
- It does not audit ScratchPool lease-end annotations or the CALL empty-pool cut
  (separate successful-path obligation).
- It does not audit residual block implications already treated by
  `research/residual-call-refinement`, nor the compiler/Driver admission gap in
  `research/physical-compiler-correspondence`.
- It does not supply a Callback.abort invoice or a priced park/restore interrupt
  bill.
- It does not touch stock-envelope A/B/rho, route-cube fibre/key meters,
  gate-operand retargets, or rate-substitution reprints.
- No new kappa.
