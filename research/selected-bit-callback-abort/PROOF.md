# Callback.abort bound to the parked-numerical-child interrupt invoice

## Claim

Pin Jose Manuel / jmbarrancoml's PR2809 physical caller on this repository at
base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, specifically the PR2753
export `inputs/pr2753/predecessor/vendor/controller.py` (`Callback.abort` /
`Callback.close`), together with `numerical_frame.py` (NumericLease child-phase
`close(strict=False)`), the written four-Stack-role note in `PROOF.md`, and the
interrupt gap named in
`docs/research/selected-bit-physical-contract-map.md`.

Under those source contracts:

1. **Callback.abort invoice.** On failure, `Callback.abort` rolls residue and
   index arenas back to the entry `protected_residues` /
   `protected_indices`, rewinds `program.tape` and `fields.tape`, and clears
   both faces of the `pending` and `values` Stacks (four Stack-role borrows).
2. **Close is not abort.** `Callback.close` requires both stacks empty. A dirty
   failure path cannot use `close`; it must use `abort`.
3. **Parked-child composition.** When a Callback fails while a NumericLease is
   already in child phase after a completed park, the interrupt invoice is
   `Callback.abort` followed by `lease.close(strict=False)`. The abort restores
   the Callback entry protected sets; the nonstrict lease close frees lease
   grants, clears remaining bank dirt, and restores the parked parent — the
   same child-interrupt invoice audited for NumericLease / SharedFrame alone.

These are source-bound finite obligations. They do not establish ScratchPool
lease-end / CALL-empty cuts, a priced park/restore machine-step charge, full
GL64 refinement, H2 primitives, stock-envelope constants, or supplier
admission. Selected decimal kappa remains `0.001672660197076918`.

## Independent algebra

Model residue/index arenas as finite live-slot sets and each Stack as a pair of
clearable faces. A NumericLease advances `preparing → parking → child`. A
Callback records protected entry sets, may push continuation dirt on both
Stacks and allocate beyond the protected sets, then either `close` (empty
stacks) or `abort` (rollback + four-face clear).

Correct composed fixture: after park and child grants, construct a Callback,
push continuation dirt, fail, `abort`, then `lease.close(strict=False)`. Stacks
are empty, banks are empty, and the codec is unparked.

## Semantic counterexamples (acceptance gaps for omitted branches)

1. **Abort without stack clear.** Residue/index rollback without clearing
   Stack faces leaves continuation dirt. The source clears `stack.tape` and
   `stack.reverse` for both Stacks.
2. **Abort without residue rollback.** Clearing stacks without
   `residue.rollback(protected_residues)` leaves orphan slots beyond the entry
   set.
3. **Close instead of abort on dirty failure.** `close` raises
   `closed continuation interface` when stacks are nonempty; the failure path
   requires `abort` before the enclosing lease interrupt.

## Source correspondence

Authenticated against the pinned bytes:

- `controller.py` defines `protected_residues` / `protected_indices` at
  construction, `abort` with dual rollback, program/fields rewind, and
  `stack.tape.clear()` / `stack.reverse.clear()`, and `close` demanding empty
  stacks.
- `PROOF.md` states that `Callback.close/abort` end all four Stack-role
  borrows.
- `numerical_frame.py` implements child-phase `close(strict=False)`.
- The physical-contract map records that PR2899 covers successful admitted
  execution, not interrupted-macro recovery.

## What this does not claim

- It does not re-audit NumericLease preparing/parking phases already covered by
  `research/selected-bit-abort-recovery`.
- It does not audit ScratchPool lease-end annotations or CALL empty-pool cuts.
- It does not supply a complete machine-step charge for park/restore.
- It does not execute selected GL64 payloads or change kappa.
