# Research: Callback.abort bound to parked-numerical-child interrupt (no new kappa)

Independent audit binding Jose Manuel / jmbarrancoml’s PR2753/PR2809
`Callback.abort` stack/residue rollback to the NumericLease parked-child
interrupt invoice. Open [#3999](https://github.com/CrocSwap/integer-mult-bounds/pull/3999)
audits NumericLease / SharedFrame interrupt alone and leaves Callback.abort as
OQ1; this package answers that OQ with one composed fixture that fails inside a
Callback while a lease is already parked in child phase.

At the pinned bytes: `Callback.abort` rolls residue/index to entry protected
sets, rewinds program/fields tapes, and clears both faces of the `pending` and
`values` Stacks (four Stack-role borrows); `Callback.close` rejects nonempty
stacks; after abort, `lease.close(strict=False)` restores the parked parent.
Three omission mutants show stack clear, residue rollback, and abort-not-close
are load-bearing.

Complements open [#3999](https://github.com/CrocSwap/integer-mult-bounds/pull/3999)
(NumericLease/SharedFrame) and [#3993](https://github.com/CrocSwap/integer-mult-bounds/pull/3993)
(ScratchPool lease-end / CALL-empty on the successful path). Primary module is
`controller.py` Callback, not `numerical_frame.py` or ScratchPool. Does not
price park/restore machine steps and does not close a universal enclosing
ownership argument.

**No new kappa.** Selected κ stays `0.001672660197076918`.

## Reproduce

```sh
python3.12 -I -B research/selected-bit-callback-abort/verify.py
python3.12 -I -O -Werror -B research/selected-bit-callback-abort/verify.py
python3.12 -I -B research/selected-bit-callback-abort/independent.py
python3.12 -I -B research/selected-bit-callback-abort/test_package.py
python3.12 -B scripts/research_package.py --package research/selected-bit-callback-abort
```

Expected:

```text
PASS_SELECTED_BIT_CALLBACK_ABORT parked_child_callback_abort stack_residue_rollback lease_nonstrict_restore three_mutants no_new_kappa
PASS_SELECTED_BIT_CALLBACK_ABORT_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-bit-callback-abort outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Corrupted temporary certificates and duplicate JSON keys are rejected.

## Open next questions

1. Compose Callback.abort with ScratchPool lease-end / CALL-empty and residual/CALL
   into one enclosing ownership argument.
2. Supply a complete machine-step charge for park/restore on the interrupt path
   that includes Callback stack faces.
3. Does any selected GL64 coefficient path require Callback.abort under a parked
   numerical child with a nonzero continuation depth?

## Credit

Credit Jose Manuel / jmbarrancoml / PR2809 for NumericLease child-phase
nonstrict close and the physical Callback lowering of David Arias’s PR2753
caller; PR2899 / the physical-contract map for naming the interrupted-macro
gap; open [#3999](https://github.com/CrocSwap/integer-mult-bounds/pull/3999) for
the NumericLease interrupt invoice and OQ1 answered here; [#3993](https://github.com/CrocSwap/integer-mult-bounds/pull/3993)
for the complementary successful-path scratch cut. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
