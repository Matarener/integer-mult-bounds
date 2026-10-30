# Raw pencil special-linear recognition and transport

This closes the raw-input boundary for finite-field two-slice tensors.
Given any two m-by-n coefficient matrices over one common finite field,
with m,n>0, it returns a complete SL_m x SL_n x SL_2 orbit label, a fixed
representative and a literal determinant-one map to it. Two equivalent raw
inputs receive an explicit transporter. No supplied block model or invertible
rational slice is required. The complete kappa calculation is unchanged.

The [proof](PROOF.md) gives the complete-orbit argument and positive costs.
[sl.py](sl.py) contains the implementation. [RESULT.json](RESULT.json) and
[EVIDENCE.md](EVIDENCE.md) state the exact checks and limits.
[SOURCES.json](SOURCES.json) pins all eleven retained source files.

The deterministic decision enumerates SL2 slice actions, extracts the raw
strict model, and keeps its actual row/column determinants modulo the complete
fixed-slice character subgroup. Exact general-degree norm witnesses remove
the degree-three limit of the supplied-model executable. Map construction
has expected polynomial cost for fixed field under uniform sampling; this
is not a deterministic worst-case runtime guarantee.

The implementation accepts all finite dimensions, minimal indices, primary
degrees, lengths and multiplicities. This includes zero pencils, zero-index
singular blocks, infinity, nonsplit factors and no-invertible-slice pencils.
The common field encoding is part of the interface. Field isomorphisms and
tensors with more than two slices are outside the claim.

## Reproduce

Use Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/raw-pencil-sl-transport
```

The five phases report `PASS_RAW_PENCIL_SL_SMALL`,
`PASS_RAW_PENCIL_SL_EXTENSION`, `PASS_RAW_PENCIL_SL_FIXTURES`,
`PASS_RAW_PENCIL_SL_NORMS`, and `PASS_RAW_PENCIL_SL_CHARACTERS`.
The runner then reports `PASS_REGISTERED_RESEARCH_PACKAGE`.
The declared caps sum to 1,200 seconds. The two exhaustive phases use at
most four process workers and write no package data. VERIFY.json also gives
the exact commands for a Git-free export.

`analyze` gives the deterministic label and representative. `canonicalize`
also gives the three determinant-one maps. `transporter` gives maps from the
first input to the second, or None for different orbits. The action convention
and all input domains are stated in PROOF.md.

## Credit and scope

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0. No subagents.
The consumed packages use the same assistant family; this is not independent
human review. The new finite-orbit oracle does not use their classification
or character formulas.

[PR #5692](https://github.com/CrocSwap/integer-mult-bounds/pull/5692), head
e34ae992744db135b9d4e378bfe26fd31fb82ad7, supplies raw strict extraction.
[PR #5689](https://github.com/CrocSwap/integer-mult-bounds/pull/5689), head
29172b129a7bb4dbbb3b42ac128fa32ffec1f93b, supplies complete fixed-slice
characters and the norm construction argument. The latter's bounded code
is a separate comparison oracle. All sources and notices remain byte-exact.

Credit also Nick Petalas's
[PR #5250](https://github.com/CrocSwap/integer-mult-bounds/pull/5250),
apoursh's [PR #5672](https://github.com/CrocSwap/integer-mult-bounds/pull/5672),
Ali Romman's [PR #5683](https://github.com/CrocSwap/integer-mult-bounds/pull/5683),
David Ganz's tensor atlas and the classical Kronecker/module/centralizer/norm
lineage retained in those sources. Global literature priority is unclaimed.

## Open next questions

- Name a concrete native producer and consumer that uses this admissibility
  tool, then price all physical preparation, routes, dirty restoration,
  storage, precision and recursive work. Those costs are unknown here.
- Give a deterministic general-degree residue norm solver with its actual
  cost. The present exact witness has expected polynomial runtime.
