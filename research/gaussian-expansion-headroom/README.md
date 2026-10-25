# Certified Gaussian expansion headroom for the physical chirp caller

PR3851 leaves the source-normalized Gaussian expansion and its 0.6-norm
join to PR3763 unfinished. This package supplies one reusable numerical
component: for every positive integer source/target length and Gaussian
width squared u ≥ 1, it constructs downward dyadic expansion coefficients
and inward-rounded complex p-grid outputs whose sup norm is at most
**21/38 < 0.6** on every unit-disk input. The remaining norm margin is
exactly **9/190**. It also supplies a computable approximation-error bound.

[PROOF.md](PROOF.md) proves this for every input and every tensor dimension,
including arbitrary complex signs, periodic windings, nonsquare √u and
unequal axis lengths. The actual bound is
`b(u) = 1/2 + 1/(20^u−1)` per axis and the product of these bounds over
the resampled axes. Earlier errors are discounted by later contractions.
Coefficient precision q must be at least 8; output precision p may be any
positive integer. The chirp caller must additionally meet its own
`p−A ≥ 13` and physical encoding/scheduling requirements.

The contribution combines Gaussian Fourier duality, Poisson periodization,
theta-series majorization, positive operator domination, directed dyadic
rounding, tensor telescoping, coordinate packing and finite-window frames.
[LIBRARY-BRIDGES.md](LIBRARY-BRIDGES.md) maps these to inspected sources in
the shared Lean tree/DAG and states where a new argument is needed.
The classical mathematics and existing inward-rounding method are credited;
no claim of their invention or exhaustive first use in the project is made.

## Evidence and use

The standard-library reference checks 34 prepared rows, 340 complex line
values and 80 complete tensor output coordinates. A separate residue-first
oracle and a direct dense Kronecker evaluation check the finite outputs.
They share Mason Hale's credited interval backend. Seven semantic test
groups cover invalid domains, coefficient/center/error tampering, missing
periodic windings, coarse nearest-grid rounding, dirty exterior ownership,
source-hash corruption, and exported CLI/receipt corruption. The registered
replay includes these controls with Python assertions disabled.

From the repository root with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-expansion-headroom
```

For an extracted standalone package:

```sh
python3.12 -B research/gaussian-expansion-headroom/verify.py
python3.12 -B research/gaussian-expansion-headroom/test_expansion.py
```

The first command ends with
`PASS_GAUSSIAN_EXPANSION_HEADROOM rows=34 line_values=340 tensor_coordinates=80 RECEIPT_MATCH`.
`expansion.prepare(s,t,u,q)` constructs reusable rows;
`expansion.line(values,rows,p)` consumes integer real/imaginary numerators
on the 2^(−p) grid. `tensor` applies all declared axes and returns the
shape, sufficient error bound and hard norm bound. `window` reads named
borrowed source positions and changes only disjoint named output positions.
Inputs outside the unit disk fail rather than silently being rescaled.

This is an exact host reference and an informal universal sufficient proof.
The physical expansion, encoded handoff and complete caller remain open.
No new κ or selected-frontier change is claimed. There is no new Lean
formalization, independent human review or fresh kernel/axiom certification.

## Source and overlap scope

Base: canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. The `uniform-transfer-audit` card was selected and its positive
control returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; the selected cold
replay is unrelated to this additive package and was not rerun.

The round scanned 578 open PR bodies, updated recent all-state records
through PR3875, the visible HTML of Discussions 1163, 1166 and 3664, and
actual related proof sources. Discussion HTML is partial coverage. Shared
library retrieval used bounded lexical/source queries and historical DAG
lookups, not exhaustive semantic retrieval. The relevant DAG hits for
Poisson/theta/Gaussian Fourier facts are source-catalog entries with no
typed proof node in the returned packet. This does not imply fresh kernel
verification or absence of other applications.

Mason Hale's existing certified Gaussian recovery already implements
inward rounding and a dense finite complete integer caller. The RaD
reports already prove expansion norm below 3/4 and tensor error transport.
PR3851 and PR3763 provide the immediate physical producer/consumer contracts.
The added result is the explicit all-parameter 0.6 handoff bound together
with downward coefficient preparation, hard disk preservation, propagated
error, layout and dirty-exterior host interfaces. The existing dense
integer caller is not repackaged as a new multiplication algorithm.

## Open next questions

1. Can one physical expansion block implement these downward coefficients
   and inward grid rounding at the existing paid cost? First freeze its
   encoded source/output/page fields and compare the full output with this
   reference. The missing pieces are the transition schedule, coefficient
   producer and full tape invoice.
2. Can the expansion output be handed to PR3763 under one complete tensor
   schedule? First check the actual p−A guard, target order, source/halo
   ownership and D = d−1 axis count. Protected child returns and restoration
   must be joined before claiming a complete physical caller.
3. How much of the 9/190 norm margin is consumed by the eventual page and
   conversion interface? First bound every added approximation in modulus
   and keep the two final S factors and γ normalization explicit. CRT
   entrance/return and integer recovery are still separate obligations.

## Credit

Prepared by Dugongue with substantial OpenAI Codex assistance in source
retrieval, mathematics, implementation, verification and prose.
Jose Manuel (`jmbarrancoml`) supplies PR3851 and PR3763 and the PR2298
handoff lineage. Mason Hale supplies the unmodified interval backend and
prior certified numerical caller. David Harvey and Joris van der Hoeven,
the retained OpenAI manuscript, Douglas Colkitt, RaD/hipotures, Chafik
Boukhalfa's PR481/486/489, the PR3709/3787 word lineage, PR479 and PR948,
and the linked library authors retain their credit. [NOTICE.md](NOTICE.md)
and the preserved upstream notices give the exact scope and attribution.
