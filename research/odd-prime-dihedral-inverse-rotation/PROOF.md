# Proof sketch: odd-prime inverse-rotation four-call floor

## Object

For an odd prime `p`, let `D_{2p}=⟨s,t|s²=t²=e,(st)^p=e⟩`. In `F₂[D_{2p}]`,
paid factors are `I+([g]+[e])N` with `g∈{s,t}` and `N` any of the 28 rank-one
idempotents of `M₃(F₂)`. The target is `diag([st],[ts],[e])` on three dirty
registers.

## Upper bound

The word `D_{E₀₀}(s) D_{E₀₀}(t) D_{E₁₁}(t) D_{E₁₁}(s)` multiplies to the target
on every certified `p`. Each factor is an admitted paid call, so the
paid-call count is four.

## Lower bound on the certified range

Every ordered word over `{s,t}` of length `k≤3`, with every choice of the 28
projectors at each position, is evaluated in the full formal group algebra.
There are `Σ_{k=0}^{3} 2^k · 28^k = 178809` candidates per prime. For each
`p∈{5,7,11,13,17,19,23,29,31}` the number of exact endpoint hits is zero.
Therefore no word of length at most three realizes the target, and four is
minimal on this domain.

The primary engine uses the encoding `r^k s^ε ↦ 2k+ε` and packs each
coefficient matrix as a nine-bit integer. An independent engine builds
`D_{2p}` from permutations of the `p`-gon and stores coefficient matrices as
three row masks; it does not import the primary multiplication routines. Both
engines agree on zero hits and on the direct four-call endpoint.

## Cross-check at `p=5`

The same encoding and search at `p=5` reproduce the primary state digests of
the pinned D10 certificate (`research/d10-reflection-sharing-seeda3def8`), so
the multi-prime package does not silently change the already-certified D10
case.

## Limits

This is a finite certified-range theorem, not a proof for every odd prime and
not a physical supplier invoice. Even rotation orders and reflection-target
tariffs are outside the claim.
