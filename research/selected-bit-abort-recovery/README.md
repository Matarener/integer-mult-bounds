# PR2809 NumericLease / SharedFrame interrupt-abort recovery

**Scoped independent audit with semantic counterexamples; no new kappa.**
Jose Manuel / jmbarrancoml's PR2809 physical caller distinguishes preparing-phase
bank rollback, child-phase nonstrict close, and a return-versus-interrupt
strictness gate on `SharedFrame.close`. The physical-contract map records that
PR2899's ordinary backend covers successful admitted execution, not
interrupted-macro recovery; PR2809's own proof excludes transactional recovery
halfway through a parking-table command. This package pins those sources at base
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, checks structural correspondence, and
supplies an independent live-slot / phase algebra with three mutants that show
each load-bearing branch.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.

## Results

1. Preparing-phase abort: on failure before park, rollback restores the exact
   entry live sets on both numerical banks.
2. Child-phase interrupt: after park, `close(strict=False)` clears child dirt and
   restores the parent without the successful-return inventory gate.
3. Return versus interrupt: `callee_returned` gates `strict` on
   `SharedFrame.close`; only a completed callee body demands the exact inventory.
4. Parking mid-command: incomplete codec park is explicitly outside the retained
   interruption contract; neither preparing nor child recovery runs on that path.

Three semantic counterexamples (not source defects): omit preparing rollback and
orphan slots remain; force strict close on a dirty interrupt and the inventory
gate rejects; ignore `callee_returned` and always-strict frame close rejects an
interrupted exit with leftover locals.

Selected decimal stays `0.001672660197076918`. This is not the #3993 lease-end /
CALL-empty slice, GL64 execution, H2 pricing, stock-envelope work, route-cube
metering, or a rate substitution.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -I -B research/selected-bit-abort-recovery/verify.py
python3.12 -I -O -B research/selected-bit-abort-recovery/verify.py
python3.12 -I -B research/selected-bit-abort-recovery/independent.py
python3.12 -I -B research/selected-bit-abort-recovery/test_package.py
python3.12 -B scripts/research_package.py --package research/selected-bit-abort-recovery
```

Expected markers include
`PASS_SELECTED_BIT_ABORT_RECOVERY preparing_rollback child_interrupt_nonstrict return_vs_interrupt parking_out_of_contract three_mutants no_new_kappa`
and `PASS_SELECTED_BIT_ABORT_RECOVERY_TESTS groups=6`.
Default `verify.py` is read-only; admission uses `need()` under `-O`.

## Open next questions

1. Bind Callback.abort stack/residue rollback to the same interrupt invoice as
   NumericLease, with one fixture that fails inside a parked numerical child.
2. Compose this interrupt discipline with the lease-end / CALL-empty cut and
   residual/CALL refinement into one enclosing ownership argument that states
   which paths remain successful-only.
3. Supply a complete machine-step charge for park/restore on the interrupt path,
   separating returned output disposal from failed construction cleanup.

## Credit

Closest priors: Jose Manuel / jmbarrancoml PR2809
(`selected-bit-physical-caller`) for NumericLease/SharedFrame abort paths;
PR2899 `physical-ordinary-interchange` for the successful-path ordinary interface
that disclaims interrupted-macro recovery; Nick Petalas
`physical-compiler-correspondence` and `residual-call-refinement` for adjacent
independent audits that leave interruption open; the physical-contract map for
naming the interrupt gap. David Arias PR2753 supplies the logical caller
retained by PR2809. The just-published lease-end / CALL-empty audit is a
complementary successful-path scratch obligation, not repeated here.
