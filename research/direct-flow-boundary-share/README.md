# #4436's boundary exits: a mirror identity, a rigorous share bound, and a correction

**Claim type:** an exact identity and a rigorous uniform bound for #4436's boundary exits, plus a
**correction** to this package's first version and finite measurements of the true exit coefficient.
**No new κ.** It concerns zxv's [#4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436)
open direct-exponent gate.

## Correction to the first version

The first version (head `04da76eb`) claimed that the gate reduces to a uniform boundary-exit share
bound. That claim is **wrong**.

- **The flaw.** Its lemma assumed leaf exits have rank `E(n) = o(n)`, so that their term
  `(mE/n)^δ` vanishes. In #4436's direct flow this is false. Leaf exits `rρ` with `ρ ∈ F[G]` reach
  **0.397·N**, and they carry **85–92 %** of the source `t`-potential at every scanned rank.
- **What stands.** The lemma is still valid as a conditional statement, but its leaf hypothesis
  fails here.
- **What controls the gate.** The total exit coefficient, measured below.

## Mirror identity (exact)

Use #4436's lockstep nodes. A *base* is a pair `(ρ, a)` with `ρ ∈ F[d]`, `|a| = G−d−1` and
`0 ≤ d < G`, of weight `μ = cnt(ρ)·u(a)` and size `z = ρ·c(a)`. Write `I(x) = m z/N ∈ x` for the
window condition. Then:

    boundary exits = Σ_{r>k} P_r W_k · [base (ρ,a) with I(1/r, 1/k]] at rank r k z,
    sources        = Σ_{k>r} P_r W_k · [base (ρ,a) with I(1/k, 1/r]] at rank r k z  +  top layer.

An exit occurs where node `(ρ, a+e_k)` is present but `(ρr, a)` is absent. A source occurs where
`(ρr, a)` is present but `(ρ, a+e_k)` is absent. So exits and inner sources are the same base measure
seen through mirrored windows. `verify.py` checks both equalities exactly, as multisets, at
`N = 1089, 3000, 20000` and `100000`.

## Rigorous uniform bound on the boundary share

Let `M(J) = Σ_{bases in J} μ z^t`. Split the windows into elementary intervals `J` cut at the
points `1/r` and `1/k`. Then exits `= Σ_J E_J M(J)` and inner sources `= Σ_J S_J M(J)`, where
`E_J` and `S_J` sum `P_r W_k (rk)^t` over the exit and source windows covering `J`. Every exit window
lies inside `(1/48, 1/5]`, and each of its pieces is covered by source windows. Hence, for every `N`:

    β(N) ≤ max_J E_J / S_J = 0.3208   (raw p7, t = 1 − 0.0026865).

The measured maximum is 0.1545. Even the crude cover bound, which compares all exits against the
source pairs `r ≤ 5`, `k ≥ 57` only, gives 0.753. So hypothesis (C) of the first version is now a
theorem. It is no longer the bottleneck.

## The exit coefficient, measured

This is the quantity #4405's refined induction actually needs:

    κ(N, z0) = Σ x_e e^{z0} / Σ w_s s^{z0},     with κ ≤ η = z0·m^{z0−1} required.

At `t` the exit and source potentials balance (κ = 1.000000), and κ falls only slowly as `z0` rises.

| saving `1−z0` | η | sup κ, N ≥ 10³ | N ≥ 10⁴ | N ≥ 10⁵ | N ≥ 3·10⁵ |
| --- | --- | --- | --- | --- | --- |
| 0.002 | 0.98847 | 0.99864 | 0.99826 | 0.99807 | 0.99798 |
| 0.001 | 0.99422 | 0.99667 | 0.99573 | 0.99526 | 0.99504 |
| 0.0008 | 0.99537 | 0.99628 | 0.99523 | 0.99470 | **0.99445** |

Through `N ≤ 5·10⁵`, the refined-induction test with the direct flow passes at saving 0.0008 for
`N ≥ 3·10⁵`, and fails at 0.001. That agrees with the effective saving of about 0.0008 that #4456
measured near `N = 3·10⁴`. The slow downward drift of sup κ is finite evidence only.

## Not covered

- Any asymptotic statement about κ(N, z0).
- An explicit-rank endpoint.
- Native premises.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-boundary-share --check-only
python3.12 -B scripts/research_package.py --package research/direct-flow-boundary-share
```

The verifier prints `PASS_DIRECT_FLOW_BOUNDARY_SHARE` in about 35 seconds, using only the standard
library.

## Open next questions

1. **Do the leaf exits admit a mirror-type comparison with the sources?**
   - *Why it matters:* leaf exits are about 90 % of the exit potential, so they decide κ.
   - *First step:* write leaf exits `rρ` (`ρ ∈ F[G]`) and last-layer sources over a common base, as
     above.
2. **Does sup κ(N, z0) converge, and to what?**
   - *Why it matters:* it decides the direct saving.
   - *First step:* a renewal-type analysis of the tilted base measure near `log(N/m)`.

## Credit

- The direct flow and the gate are zxv's (#4436).
- The refined induction is 1337isnot1337's (#4405).
- The lockstep construction is Jacob Alan Sussman's Theorem 1G.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
