# PR3335 rank-34 fit: exact rational four-cycle gauge census

**Scoped exact negative; no new supplier or kappa.** A useful escape from the pair and triple screens would have to exploit interactions across four latent channels. This package tests a deliberately structured noncommuting move: four reversible shears arranged around a directed channel cycle.

For each of the 24 ordered cycles on a chosen four channels, the gauge word is

`G = E_ab(x0) E_bc(x1) E_cd(x2) E_da(x3)`, where `E_ij(x) = I + x e_ij` and each `x` is rational, including zero. It acts by replacing the selected source columns `A` with `A G` and the matching reader rows with `G^-1 A^T`, preserving the exact scalar fitting matrix.

## Why the coefficient search is complete for this move family

Expand each entry as a polynomial in the four shear weights. Along a directed simple four-cycle, every off-diagonal source or inverse entry is either zero or one path monomial. The only two-term entry is the source diagonal `1 + x0*x1*x2*x3`; the verifier reconstructs these polynomials exactly for all 24 cycle orders. Therefore:

- If at least one weight is zero, the cycle breaks and the support pair depends only on the zero-edge mask.
- If all four weights are nonzero, the support pair depends only on whether their product equals `-1`, the sole cancellation of `1 + product`.

Sixteen zero masks, plus one extra nonzero representative with product `-1`, give 408 exact rational-cell representatives across the 24 orders. They collapse to **193** distinct source/inverse support pairs. Each representative and its inverse is checked exactly; non-unit rational samples exercise every zero mask and both full-cycle product cells. This is an algebraic classification of this cycle-word family, not a classification of all `GL4(Q)` matrices.

## Result

The exact full-plane tariff was priced for all **46,376** four-channel subsets and all **193** rational support pairs: **8,950,568** map/subset cases. No subset has a strict improvement; the minimum full invoice remains **224**. A dense control checks all **12,544** scalar fitting-matrix entries for every representative and rejects a deliberately wrong inverse.

The fully active cycle stratum is stricter: all four weights nonzero give 48 support pairs and **2,226,048** pricing cases. Every four-channel subset pays at least one extra unit under this cycle closure; the best resulting invoice is **225**. Allowing zero weights restores neutral lower-block or broken-cycle moves, but still yields no strict improvement anywhere.

This is a scoped negative result for cycle-ordered four-shear words on the published PR3335 basis. It leaves open other four-channel word orders, arbitrary rational `GL4(Q)` gauges, longer sequences, other factorizations and physical suppliers. The selected kappa remains unchanged.

## Scope and overlap

The scope is one cycle-ordered four-shear word on a fixed four-channel subset of the PR3335 basis. PR3335 supplies the exact rank-34 factorization; [PR4020](https://github.com/CrocSwap/integer-mult-bounds/pull/4020) and [PR4022](https://github.com/CrocSwap/integer-mult-bounds/pull/4022) are the exact rational pair and triple screens that motivate crossing into four channels.

A refreshed text scan at 2026-10-19 09:52 UTC covered 727 open PRs and 2,593 Discussion records with complete pagination. The literal `four-cycle` hits included [discussion #2488](https://github.com/CrocSwap/integer-mult-bounds/discussions/2488), about paired output cycles and payload permutations, and [discussion #1332](https://github.com/CrocSwap/integer-mult-bounds/discussions/1332), about selected T16 helper relocation; both study different objects. The scan found no remote hit for `cycle-ordered` or `four-channel holonomy`. This search does not inspect every code diff, closed PR body or unpublished work, and is not a novelty certificate.

## Reproduction

With Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/paired-plane-rank34-cycle-holonomy/verify.py
python3 -O -B research/paired-plane-rank34-cycle-holonomy/verify.py
```

The verifier authenticates the selected-label archive and PR3335 certificate, reconstructs the rational support cells and complete-plane ranks, and compares the exact result and receipt hashes with `CERTIFICATE.json` and `RESULT.json`.

## Open next questions

Can a four-channel word that is not cycle-ordered, such as a path with a chord, exploit a cancellation invisible to pair and triple gauges? Derive its rational support cells symbolically before pricing all channel quadruples. A strict tariff below 160 would still be only an optimistic copy-screen milestone; dirty-state realization and supplier admission would remain open.

## Credit

Matarener/Mark and Claude via Claude Code supplied PR3335's rematching and rank-34 factorization. Arham Tahir's paired-plane audit and credited predecessors supply the complete-plane tariff and 224 base invoice. The exact rational pair and triple screens are retained in [PR4020](https://github.com/CrocSwap/integer-mult-bounds/pull/4020) and [PR4022](https://github.com/CrocSwap/integer-mult-bounds/pull/4022). This cycle-word classification, verifier and tariff census were prepared by OpenAI Codex with substantial AI assistance. No independent human review or formal proof assistant is claimed. Apache-2.0.
