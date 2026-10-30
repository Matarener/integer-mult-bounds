# Complete supplied finite-field pencil characters

The determinant-character interface now covers every supplied Kronecker block model over a finite field. This includes regular pencils with no invertible rational slice, nonsplit primaries, arbitrary Jordan lengths and multiplicities, infinity, and all right/left singular mixtures. **No new kappa is claimed.** The model and its coordinate maps must be supplied; arbitrary-tensor extraction remains open.

For each GL2 slice action R, normalize each regular primary block in its own affine chart. Its cyclic vector gives a literal companion-basis map. Retain R exactly when the transformed block multiset matches. Let `(p_R,q_R,z_R)` be the actual lift determinants, including permutation signs. Let F be the complete fixed-slice determinant subgroup from the singular vectors `(e,-e-1)`, `(-e-1,e)` and the regular length vectors `(ell,-ell)`. Then

`Delta = union_R {(p_R*x,q_R*y,z_R) : (x,y) in F}`.

The [proof](PROOF.md) includes all regular/singular Hom spaces, full determinant completeness, a constructive converse, finite SL labels and correction of supplied maps. It preserves the exact slice cosets instead of assuming that all actions of the same determinant have the same lift class. For fixed q, image extraction from the supplied model is deterministic polynomial time in dimension. General norm witnesses have an exact expected-polynomial randomized construction; the bounded executable uses finite enumeration instead.

A closed family shows the new scope. Put a length-ell Jordan primary, with common multiplicity r, at every point of P1(F_q). Every rational slice is singular. The exact image is

`Delta = {(x,y,z): x in (F_q*)^ell and x*y*z^(r*ell)=1}`.

There are `(q-1)*gcd(q-1,ell)` SL orbits. The binary diag(s,t,s+t) example is included. F5 at length two has eight orbits, and F4 at length three has nine. The determinant polynomial alone misses the extra length restriction.

## Evidence and replay

```sh
python3.12 -B scripts/research_package.py --package research/finite-field-pencil-characters
python3.12 -I -O -W error -B research/finite-field-pencil-characters/verify.py
```

Expected: `PASS_COMPLETE_SUPPLIED_FINITE_FIELD_PENCIL_CHARACTERS`. Python 3.12 and the standard library suffice. Four source files are authenticated before any retained code is imported. Direct replay compares [RESULT.json](RESULT.json) and does not modify publication files.

The exact finite evidence contains:

- 320 coefficient-equation Hom cases over F2/F3/F4/F5, including zero indices and finite/infinity regular blocks.
- Sixteen literal stabilizer domains: all GL2 actions in fourteen, and explicit action subsets in two larger cases. All 52,807 linear solutions and 13,042 invertible stabilizers are enumerated across 429 selected slice actions. The oracle imports no lift or character formula.
- Twenty-seven supplied models, with all 4,032 GL2 actions screened and 2,194 literal admitted lifts. All fixed determinant cosets give 7,450 prescribed-action witnesses.
- All 567 determinant triples in those models: 239 witnesses and determinant-one corrections, plus 328 exclusions. Exact image closure and quotient cardinalities pass.
- Nine mathematical controls and nine malformed-model rejections. The controls include the source Jordan sign example, missing global invertible slices, coloured support, nonsplit norms, mixed gcd restrictions and damaged literal maps.

The executable bounds are indices 0..5, residue degrees and lengths 1..3, multiplicities 1..3, and total dimensions at most sixteen. The declared models are a subset of that domain. The all-dimension finite-field result is the written theorem, not an exhaustive finite census. The bounded residue search is not a general fast norm solver. Polynomial complexity in log(q), arbitrary decomposition discovery and proof-kernel acceptance are not claimed.

## Use and limits

This closes the supplied matrix-pencil part of the determinant-image handoff from Nick Petalas PR5250, apoursh PR5672 and Ali Romman PR5683. It provides exact tensor-atlas admissibility and literal SL corrections. A multiplication use still needs a native producer and consumer, paid maps, ownership, movement, restoration, storage, precision and the complete recursive invoice. Those obligations remain unknown.

Canonical base is `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority7. Selected .00310045 is unchanged. Normal/optimized replays, committed-byte checks and export checks are separate from hosted CI, independent human review and a complete multiplication theorem. Full-history ancestry preflight is unavailable in this shallow checkout.

Credit Nick Petalas and the retained centralizer/canonical-form lineage; apoursh for the singular symmetric-power implementation; Ali Romman PR5683 for singular mixing and the coefficient-equation oracle; David Ganz A030/A026/A029; and classical Kronecker and finite-field theory. The four frozen files and notices remain unchanged. New construction, proof and checks: Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0. Global literature priority is unclaimed.

## Open next questions

- Recover a complete Kronecker model and literal factor maps from an arbitrary rectangular tensor. Include zero indices and infinity; do not assume an invertible rational slice.
- Use one classified pencil in a concrete native multiplication interface and price the complete caller. An algebraic stabilizer does not make the correction maps free.
