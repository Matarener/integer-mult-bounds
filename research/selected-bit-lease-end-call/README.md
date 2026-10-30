# PR2809 lease-end annotations and the CALL empty-pool cut

**Scoped independent audit with semantic counterexamples; no new kappa.**
Jose Manuel / jmbarrancoml's PR2809 ScratchPool states that clearing ends a
lease, that a stale close cannot erase a later borrower, and that no lease
crosses CALL. The physical-contract map still lists lease-end annotations and
CALL invariants as an open independent-audit handoff after the opcode/source
and residual/CALL packages. This package pins those sources at base
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, checks the structural
correspondence, and supplies an independent lease algebra with three mutants
that demonstrate each annotation is load-bearing.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.

## Results

1. Correct algebra: end lease A, reacquire the same physical role as B, then
   stale-clear A; B's payload survives and stale reads of A reject.
2. CALL cut: `Machine.call` begins with `pool.empty()`, and `empty` rejects a
   nonempty live map, so a live lease cannot cross the recursive cut on the
   source's successful path.
3. Three semantic counterexamples (not source defects): omitting the active
   guard lets a stale clear wipe a later borrower; omitting live-map deletion
   blocks reuse; skipping `empty` at CALL lets parent dirt cross the cut.

Selected decimal stays `0.001672660197076918`. This is not GL64 execution,
H2 pricing, stock-envelope work, route-cube metering, or a rate substitution.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -I -B research/selected-bit-lease-end-call/verify.py
python3.12 -I -O -B research/selected-bit-lease-end-call/verify.py
python3.12 -I -B research/selected-bit-lease-end-call/independent.py
python3.12 -I -B research/selected-bit-lease-end-call/test_package.py
python3.12 -B scripts/research_package.py --package research/selected-bit-lease-end-call
```

Expected markers include
`PASS_SELECTED_BIT_LEASE_END_CALL stale_clear_preserves_borrower call_requires_empty_pool three_mutants no_new_kappa`
and `PASS_SELECTED_BIT_LEASE_END_CALL_TESTS groups=6`.
Default `verify.py` is read-only; admission uses `need()` under `-O`.

## Open next questions

1. Compose this lease-end cut with the residual/CALL refinement and the
   whole-word ordering audit into one enclosing NODE/MERGE ownership argument.
2. Bind fixed scratch-role initialization and marker provisioning to a complete
   machine-step invoice, separating returned output disposal from failed calls.
3. Independently audit interrupted-macro recovery; the present claim is
   successful-path only.

## Credit

Closest priors: Jose Manuel / jmbarrancoml PR2809
(`selected-bit-physical-caller`) for the ScratchPool annotations and CALL cut;
Nick Petalas `physical-compiler-correspondence` for the opcode/source handoff
and supplier-boundary mutant style; Nick Petalas `residual-call-refinement`
for residual/CALL packet preservation; the physical-contract map for naming
lease-end / CALL invariants as the remaining audit. David Arias PR2753 supplies
the logical caller retained by PR2809. Historical owner/scatter boundary cards
remain catalogue provenance only.
