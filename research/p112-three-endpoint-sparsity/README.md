# A conditional exclusion of the literal P112 `2,5,6^8` caller

Ten independent P112 pieces of binary support ranks at most `2,5,6^8`
cannot span a space whose intersection with the root-evaluation code has
dimension at least six, over any characteristic-zero field. The result
inherits PR3397's exact four-piece theorem/capacities and the standard E8
Weyl-chamber premise. [PROOF.md](PROOF.md) states every dependency and implication.

The new argument handles the actual eight distinct projective endpoints left
open by PR3397. It rechecks PR3253/3322's existing 1,200 root/D7 direction
classification for support at most74.
An incidence bound forces at least nine root triples, so two share an endpoint
pair. Their four endpoints form a forced orthogonal-root configuration.
A complete exact check shows that it has no fifth endpoint.

The primary uses Weyl orbits and exterior-product pencils. A separate explicit
lattice-shell and projected-coordinate reconstruction agrees on all 360
normalized candidates and all 32 first-pencil possibilities. None passes the
second pencil. Complete set digests and finite quantities are in
[RESULT.json](RESULT.json). A separate integer dynamic program corroborates
the incidence allowance 3,772 and resulting quota nine. These are internal
computational checks, not independent human or proof-kernel review.

## Reproduction

Standard library, Python 3.12. Run from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-three-endpoint-sparsity
```

Direct commands work in a Git-free source export containing all declared inputs:

```sh
python3.12 -W error -B research/p112-three-endpoint-sparsity/verify.py
python3.12 -W error -B research/p112-three-endpoint-sparsity/independent.py
python3.12 -O -W error -B research/p112-three-endpoint-sparsity/test_controls.py
```

Set TMPDIR to an external run directory for disposable control fixtures.
Eight behavioral groups include the actual four-endpoint positive fixture,
the 32 failed fifth-endpoint fixtures, exact determinant relations, the
161-incidence losing control, the 37-perpendicular threshold boundary,
non-root normals, duplicate JSON keys and four actual rejecting CLI mutations.

## Limits and source credit

This closes one literal caller under the stated premises. The inherited
PR3397 multi-million-space census and four-piece proof are retained and
hashed, not independently reproved or replayed here. The standard Weyl theorem,
human/proof-kernel review, historical heavy caller suites, selected cold replay,
Lean and Docker remain unrun. There is no full C5, wider unresolved-row count,
C(P112)>=64, native decoder, dirty-restoration/hosting/precision/consumer bill,
supplier, new kappa or selected-frontier change.

[SOURCES.json](SOURCES.json) pins canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6 and the live
root-simplex geometry. [PREDECESSORS.json](PREDECESSORS.json) authenticates
verbatim PR3397 proof and receipt bytes from exact head
`10ac93be8dbf2ba5f85859dbeec90895ebbbabfd`. Fresh CI needs no foreign Git object.
Credit Nick Petalas/PR3397/3295/3289/3322/3253/3161/3162 and root-simplex geometry,
DreamingOfClouds/PR3154, joaqcoo and the retained E8/P112 lineage. Apache-2.0.
Automated assistance was used for research and implementation.

## Open next questions

Independently review the quotient normalization and the fifth-endpoint lemma,
including the characteristic-zero rationality step. Start with PROOF.md and
rerun both finite implementations. This would test the new implication before
using it in any wider TWOSIDE/C5 accounting. Reconcile exact current public
caller contracts separately; this package deliberately makes no global residue
count. No further construction or larger search is assigned here.
