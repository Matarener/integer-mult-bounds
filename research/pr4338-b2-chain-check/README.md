# Independent check of #4338's ordinary B2 bootstrap arithmetic

**Claim type: an independent exact check of a written arithmetic chain,
including a certified moment enclosure. No new κ.** This does not accept
#4338, and it checks none of its source-relative physical contracts.

## Object

[PR #4338](https://github.com/CrocSwap/integer-mult-bounds/pull/4338) (Ross
Richardson, head `0ac8192b…`) splits the optional ordinary B2 stage out of
#4270. With BIT coupling `c = 1/577`, it claims:

- the ordinary saving `a2 = 57697923247/33292900000000 ≈ 0.00173304`;
- the bound `T_B2 ≤ 4283584·A·V·e^(1−a2)`;
- that `a2` exceeds the pooled complex endpoint `C`.

Its own checker runs a frozen interval engine and an integer-power bisection.
No outside check existed.

## Results

Every link of PROOF.md §1, §3 and §4 holds, recomputed with exact rationals.
The inputs are read from main: `H` is the selected BIT supplier's
`nine.profile`, `a1` is PR2899's `ordinary_saving`, and `C` is
`staged-fourth-mixture-ceiling`'s root.

| Link | Result |
| --- | --- |
| `a2 = c(1−c) + c·a1` | exactly the stated rational; `a2 − C` is exactly the stated `2.06·10⁻⁶` |
| §1: bootstrap at the complex rate | `a_next` and the outer-loss value match to 28 digits. The shortfall below `0.001727989140903569` is `5.84263·10⁻⁸` |
| `F = 32·64²·ΣH` | `118606528512` |
| `μ_1` | exactly `2874298095721977/2890625000000000 < 199/200` |
| `μ_(576/577)` | enclosure width `< 10⁻³³`, inside the stated `10⁻³⁰` interval. `1 − μ = 1.0614·10⁻⁶`, so the `10⁶` coefficient holds, and the old `9999/10000` cap is false |
| Fit comparisons | `17^128 > 32·16^128`; `32780·(17/16)·20 = 696575 < 2^20`; `2^(20/577) < 17/16` |
| Exponent algebra | `(1−c) + c(c−a1) = 1 − a2`; `2^(c−a1) < 17/16`; `a2 < c`; `1 − a2 − c > 1/2` |
| Coefficient | `801 + 4000000·17/16 + 32780 + 3 = 4283584` |
| Gap table | all four exact. `1 − a2 − c(1−a1) = (1−c)²`, and the minimum gap is `c − a2 = 6.24·10⁻⁸` |

**Control.** Dropping the fallback weight `εF` moves `μ_(576/577)` below the
stated interval. The interval does include the fallback, as #4338 says.

**Two tight spots.**

- `1 − μ_(576/577)` exceeds the `10⁻⁶` that the `10⁶` coefficient needs by
  only 6%.
- The minimum gap `c − a2` is `6.2·10⁻⁸`.

**Orientation.** `a2` lies below the selected BIT saving
`0.0017334270…` by `3.9·10⁻⁷`. That is expected, since `a2 < c = 1/577` and the
BIT constructor needs `c` below its moment root. #4338 does not compare them.

## Not covered

- The source-relative contracts:
  - the B1/C1/B2 factory composition and restoration;
  - the 1,123-chart registry;
  - the retained stock-depth bound (coupling-independent; see below);
  - the fit predicates beyond the stated comparisons.
- The production B2 factory and any complex caller.
- The legacy target `0.001727989140903569`. It is quoted from #4338; its
  source is not on main.

## Reproduce

```sh
python3.12 -B research/pr4338-b2-chain-check/verify.py
```

It prints `PASS_PR4338_B2_CHAIN_CHECK` in under a second, using only the
standard library. `vendor/B2-PROOF.md` is #4338's PROOF.md, byte-identical and
SHA256-checked, with 28 phrase checks.

## Open next questions

None from this check. The stock bound `k ≤ 16390 e^c log2 e` does not depend
on the coupling: `retuned-ordinary-coupling` derives it from `D(e) ≤ 2 log2 e`,
`|GL64(F_q)| < q^4096` and `w ≤ 2e^c`, all of which hold at `c = 1/577`. The
remaining obligations are #4338's own physical premises.

## Credit

The B2 construction and its arithmetic are #4338's (Ross Richardson with
OpenAI Codex assistance), composing Jose Manuel's ordinary and fast-primitive
sources, Rohan Arun's PR185/387 argument and the PR589 BIT profile. Prepared
by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
