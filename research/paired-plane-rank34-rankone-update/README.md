# PR3335 rank-34 fit: exact rational rank-one gauge census

**Scoped exact negative; no new supplier or kappa.** The rank-34 P112 factorization has 34 latent channels and complete-plane invoice 224. This package tests every rational rank-one basis update whose left and right support together touch exactly four channels:

`G = I + u v^T`, with `supp(u) union supp(v)` equal to the four-channel block.

The Sherman–Morrison inverse is exact whenever `1 + v^T u != 0`. A diagonal similarity normalizes `u_i=1` on `S=supp(u)` and `v_j=1` on `T=supp(v)` outside their overlap. Only products `x_i=u_i v_i` on `S intersect T` remain free. The source diagonal vanishes at `x_i=-1`; the inverse diagonal vanishes at `1 + sum_{j != i} x_j=0`. Off-diagonal supports are fixed by the rectangle `S x T`.

## Exact rational support classification

There are 79 nonempty support-membership patterns `(S,T)` with `S union T` equal to the four-channel block. The verifier enumerates all **1,294** overlap/diagonal-zero parameter cells. It solves their rational affine equalities and either exhibits a rational point avoiding every forbidden hyperplane or gives an exact inconsistency/forced-hyperplane obstruction. The largest root bound is 52, so the constructive witness search tests at most 53 integer parameter values. The 921 infeasible cells are rejected by 612 forced-hyperplane and 309 inconsistent-equation certificates. The 373 feasible cells collapse to **365** distinct matrix/inverse support pairs, each with an exact rational witness and inverse.

## Result

Pricing all 365 support pairs on all **46,376** channel quadruples checks **16,927,240** exact tariff cases. No quadruple has a strict improvement; the minimum invoice remains **224**. A dense control checks all **12,544** scalar fitting-matrix entries for every representative and rejects a deliberately wrong inverse.

The full-support subfamily is less favorable: its 87 support pairs have minimum invoice **228**, at least four above the baseline. The sparse asymmetric patterns recover neutral cells but no descent. This is a scoped negative for rank-one updates supported on exactly four channels; it does not classify general `GL4(Q)`, rank-two updates, sequences, other factorizations or physical suppliers. The selected kappa is unchanged.

## Scope and overlap

PR3335 supplies the exact rank-34 factorization. The rational pair, triple and cycle-word screens are in [PR4020](https://github.com/CrocSwap/integer-mult-bounds/pull/4020), [PR4022](https://github.com/CrocSwap/integer-mult-bounds/pull/4022) and [PR4026](https://github.com/CrocSwap/integer-mult-bounds/pull/4026).

The refreshed overlap scan at 2026-10-19 10:10 UTC covered 729 open PRs and 2,595 Discussion records with complete pagination. Merged [PR1923](https://github.com/CrocSwap/integer-mult-bounds/pull/1923) exhausts 29,524 ternary Householder reflections on one symmetric ten-term P112 witness; this package instead classifies all rational rank-one support cells on the 34-channel PR3335 factorization and its full-plane tariff. [Discussion #2072](https://github.com/CrocSwap/integer-mult-bounds/discussions/2072) studies rank-one transvections between calls, not latent basis gauges. Open [PR1950](https://github.com/CrocSwap/integer-mult-bounds/pull/1950) mentions an involutive rank-one update in a Lean recovery contract, a different object. These are related mechanisms, not the same object. The scan searches open PR text and discussions, not every code diff or unpublished work; closed work is checked only through local notes and the cited Householder PR.

## Reproduction

With Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/paired-plane-rank34-rankone-update/verify.py
python3 -O -B research/paired-plane-rank34-rankone-update/verify.py
```

The verifier authenticates both pinned inputs, reconstructs all parameter cells and exact witnesses, prices every support pair/quadruple, and checks the dense scalar identity controls.

## Open next questions

Can a rank-two Woodbury update `G=I+U V^T` on four channels lower the invoice where rank-one cells cannot? Derive its rational matrix/inverse support cells before running the tariff census. Any lower tariff would still need to pass the optimistic 160 copy screen and then satisfy physical realization, restoration and supplier admission.

## Credit

Matarener/Mark and Claude via Claude Code supplied PR3335's rematching and rank-34 factorization. Arham Tahir's paired-plane audit and credited predecessors supply the full-plane tariff and 224 base invoice. Hanson Sun's PR1923 is credited for the related Householder support-cost census; its distinct ten-term witness remains intact. This package's general rank-one support classification, verifier and tariff census were prepared by OpenAI Codex with substantial AI assistance. No independent human review or formal proof assistant is claimed. Apache-2.0.
