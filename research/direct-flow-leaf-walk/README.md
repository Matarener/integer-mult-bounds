# The leaf-exit walk of #4436's direct flow: a √G regime now, saturation later

**Claim type:** exact finite computation of the leaf log-depth up to lockstep depth 60, plus a standard
large-deviation heuristic for its limit. **No new κ.** It explains the growth of the log-gap `g` in my
[#4465](https://github.com/CrocSwap/integer-mult-bounds/pull/4465). That growth comes from the leaf exits
alone, and `g` sets the refined-induction ceiling `s*·g/(g + 1 + ln m)` on zxv's #4436 direct flow.

## The walk

A leaf exit at rank `N` is `rρ`, where `ρ` is a product of `G = ⌊log₅(N/m)⌋` letters of `P`, under
`mρr ≤ N` at each step. Its `t*`-potential weight is `cnt(ρ)·P_r·(rρ)^{t*}`. Each step `ln r` is
nonnegative, so only the final constraint binds: `S_G = ln ρ ≤ B = ln(N/m)`. The leaf log-depth
therefore splits as

    D(G) = E[ln(N/(rρ))] = (ln m − E ln r) + E[B − S_G | S_G ≤ B].

At level starts `B = G ln 5`. The `t*`-tilted step law has mean `μ = 1.62592`, which is above
`ln 5 = 1.60944` by `ε = 0.01648`, and standard deviation `σ = 1.48391`.

## The √G regime (exact data)

`D(G)` is computed exactly from `F[G]`, which lives on {2,3,5}-smooth states, at `N = 121·5^G`. The
verifier covers `G ≤ 40` in about 12 seconds. `evidence/leafwalk.py` extends this to `G = 60`, with
output in `evidence/LEAF-DEPTH-G60.txt`.

| G | 2 | 5 | 10 | 20 | 30 | 40 | 60 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D(G) | 5.005 | 5.683 | 6.777 | 8.297 | 9.447 | 10.354 | 11.940 |

Fits over `7 ≤ G ≤ 40`:

| law | max residual |
| --- | --- |
| `a + b√G` | **0.054**, with `a = 3.26`, `b = 1.125` |
| linear | 0.38 |
| logarithmic | 0.32 |

The intercept matches `ln m − μ = 3.17`. The slope is close to the CLT value `σ√(2/π) = 1.18`.
That is the law of `E[B − S | S ≤ B]` while `B` sits inside the CLT window (`εG ≪ σ√G`).

## Saturation (heuristic)

Once `G ≫ G× = σ²/ε² ≈ 8,100`, the barrier lies far below the mean. By the exponential change of
measure with Esscher parameter `λ* = 0.0075`, which tilts the step mean to `ln 5`, the overshoot
`B − S_G` given survival tends to `Exp(λ*)`. Hence

    D(G) → ln m − μ + 1/λ* ≈ 136.5.

So `g` stays bounded and the refined-induction cap stays strictly below `s*`.

- **Estimate with stable shares.** Keeping the measured shares (leaf about 0.914) and depths (boundary
  about 1.84, sources about 2.45) gives `g∞ ≈ 122` and a cap near `0.955·s* ≈ 0.00256`.
- **Lower estimate.** My #4459 bound `β ≤ 0.321` gives a leaf share of at least 0.68, which yields
  `g∞ ≳ 88` and a cap of at least about 0.00252.

Either way, saving 0.0023 is reached at `g ≈ 34.5`. That happens inside the √G regime, near
`G ≈ 1,340`, or `N ≈ 10^{940}`. `diagnostics/SATURATION.md` refines the earlier `10^{700}` and observes the
saturation directly by importance sampling up to `G = 10⁶`: the overshoot reaches 131.7, against `1/λ* = 133.3`.

## Reading

- **#4436's direct flow certifies at most roughly 0.0025–0.0026 under #4405's single-step test.** This
  heuristic asymptotic ceiling sits strictly below the root `s* = 0.0026865`, because the tilted
  P-step mean exceeds `ln k_min`.
- **The only practical gap is the rank.** The selected 0.0023 is certifiable only at astronomically
  large rank.
- **What the shortfall comes from.** It is caused by the leaf exits sitting `Θ(1/λ*)` nats below `N`,
  not by the boundary exits.

## Not covered

- A proof of the saturation, including the lattice and non-Gaussian corrections, and the stability
  of the shares at large `G`.
- Any multi-step test.
- Native premises.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-leaf-walk --check-only
python3.12 -B scripts/research_package.py --package research/direct-flow-leaf-walk
python3.12 -B research/direct-flow-leaf-walk/evidence/leafwalk.py 60    # ~3 min, the G = 60 table
```

The verifier prints `PASS_DIRECT_FLOW_LEAF_WALK`, using only the standard library.

## Open next questions

1. **Can the leaf walk be steered to `μ ≤ ln k_min`?**
   - *Why it matters:* with zero or negative relative drift, the overshoot would grow without bound,
     and the direct cap would tend to `s*`.
   - *First step:* check whether a different job order or leaf depth (for example `G + 1` levels)
     changes the effective barrier slope.
2. **A rigorous Bahadur–Rao bound for `E[B − S_G | S_G ≤ B]` with explicit constants.**
   - *First step:* the three-dimensional {2,3,5} lattice local CLT.

## Credit

- The direct flow and the gate are zxv's (#4436).
- The refined induction is 1337isnot1337's (#4405).
- The lockstep construction is Jacob Alan Sussman's Theorem 1G.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
