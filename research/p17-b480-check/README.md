# Independent arithmetic check of the p17 chain: #4440, #4441, #4446, #4447, #4453

**Claim type:** an independent certified arithmetic check. **No new κ, and neither PR is
accepted.** The native contact replay is not re-run. Two PRs report the same patch, made at phase B
scalar contact 480 on #4441's p17 invoice:

- 1337isnot1337's [#4447](https://github.com/CrocSwap/integer-mult-bounds/pull/4447), at κ = 0.00300123
  (head `322e0ec7`);
- zxv's [#4453](https://github.com/CrocSwap/integer-mult-bounds/pull/4453), at κ = 0.00300120
  (head `de6869e2`).

The patch replaces frame 732 by a three-dimensional span, which changes the four incident paid ranks
from `[2,2,1,3]` to `[1,1,2,4]`. Since `(1,4)` majorizes `(2,3)` and `x^τ` is strictly concave,
`1 + 4^τ < 2^τ + 3^τ` holds for every `0 < τ < 1`, by Karamata.

## Results

**The invoice.** The shared p17 invoice equals #4441's invoice plus exactly 19 per-call swaps:
paid ranks 1 and 4 rise by 19 each, ranks 2 and 3 fall by 19 each, and the targets are unchanged.
That gives 11,560 productive fields, 69,273 paid calls and rank surplus `260,798 − 259,998 = 800`.

**The raw root.** It lies in `(0.0030012390168, 0.0030012390174)`, certified.

**Strictification.** Each PR uses main's higher-moment theorem: `α = P_t/T_t`,
`γ_u = P_{t+u}/(c^u T_t)`, `δ = B·b/(c^C T_t)`, and the bound `α^v + 2γ_u^v + 2δ^v`. The split
bound `2RJ^{−C} ≤ 2R^{t+u}J^{−u}` for `R > J` was checked by hand: it needs `u ≥ C`.

| | #4447 | #4453 |
| --- | --- | --- |
| `(C, v, c, b, u)` | (0.003001235, 1024, 20, 21, 1/5) | (0.00300122, 675, 18, 22, 3/25) |
| `α` upper (stated limit) | 0.999999995876755 (`1 − 10⁻⁹`) | 0.999999980480395 (`0.999999981`) |
| `γ_u` upper (stated limit) | 0.969136675521 (`97/100`) | 0.981971727000 (`491/500`) |
| `δ` upper (stated limit) | 0.932537504514 (`19/20`) | 0.977253011856 (`391/400`) |
| tensor bound | 0.9999989760 | 0.9999970702 |
| compiler `θ̄`, power `p` | 63/64, 1000 | 15/16, 160 |
| stated `H` / **least certified `H`** | 64,215,200,000,000 / **64,215,171,181,937** | 2,299,850,000,000 / **2,299,613,602,047** |

All three ratios agree with the PRs' printed intervals to every printed digit.

**The compiler conditions.** These hold at ambient `153^v`, with `r_max = c^v` and `k_min = b^v`:

- `c^b < b^a` gives `θ < θ̄ = a/b`;
- `2^{b−a}r_max^b ≤ m^a`;
- `θ̄^p < η = t·m^{t−1}`, which is tight for #4453: `(15/16)^160 ≈ 3.27·10⁻⁵` against `η ≈ 3.74·10⁻⁵`;
- `m^{1−t} < 2^p`;
- `z − t = d = (C − κ)/7`.

## Predecessors #4441 and #4440

The same engine also checks the predecessors.

**#4441** (κ = 0.00300105) uses its own invoice and the same tail parameters as #4447. Its ratios
match its printed intervals: `α < 0.999999997758999`, `γ_u < 0.969126930834` and
`δ < 0.932537400875`. Its stated `H` = 165,315,500,000,000 is certified, and the least passing value
is 165,312,667,114,238.

**#4440** (κ = 0.00296) consists of two query-thinned units, both at `v = 1024` and `u = 1/5`. Only
their strictification ratios and its power-majorant compiler are checked here.

| Unit | `α` upper | `γ_u` upper | `δ` upper | tensor bound |
| --- | --- | --- | --- | --- |
| complex (`c = 20`, `b = 21`) | 0.999999952117241 | 0.967466409565 | 0.941649713485 | `< 0.99995098` |
| BIT (`c = 17`, `b = 18`) | 0.999995735238060 | 0.957429821066 | 0.949707924145 | `< 0.99565187` |

All six ratios match #4440's printed interval endpoints to within `10⁻²⁸`.

**#4440's compiler** is defined in its PROOF.md §3 with `h = 1/64`, `v = 1024` and `z0 = (t+z)/2`. It
reproduces exactly:

| Unit | `H0` | `H1` | uniform saving |
| --- | --- | --- | --- |
| complex | 75,415,467,350 | 10,418,370,291,022,217 | `κ + 6d = 103609/35000000`, with `κ = 0.00296` |
| BIT | 3,755,884,544 | 25,986,965,159,937 | 0.003459 |

The Bernoulli surpluses also match exactly, and so do `c^64 < b^63` and the decay blocks
`(31/32)^128, (19/20)^128 < 1/16`.

## Outer ledgers of all five κ PRs

For #4440, #4441, #4446, #4447 and #4453, all nine outer rows reproduce **exactly** from each PR's printed
parameters. The FINE-PRIME row formulas are used:

| Row | Formula |
| --- | --- |
| main transform | `εq` |
| global router | `a` |
| fused Gaussian | `1−ε+qβ` |
| group bit router | `1−ε+aβ` |
| group scans | `1−ε+β` |
| polynomial products | `ε` |
| sparse union movement | `ξ+1/2−ε` |
| micro-box faces | `79−ε−β` |
| boundary algebraic matrix | `3/32+ξ−ε` |

In every case the binding row is the main transform. Its margin above κ is:

| PR | Margin above κ |
| --- | --- |
| #4440 | `1.3·10⁻⁷` |
| #4441 | `8.6·10⁻¹⁰` |
| #4446 | `4.3·10⁻¹⁰` |
| #4447 | `2.1·10⁻⁹` |
| #4453 | `8.6·10⁻⁹` |

## #4446

**#4446** (κ = 0.003001053) uses #4441's invoice with the rank-one tail of #4416, where
`γ = P₁/(c^C T_t)`. Its parameters are `v = 17160`, cutoff `18^v`, target floor `19^v` and ambient
`281^v`. Its ratios match the 36-digit printed intervals to `10⁻³⁰`:

- `α < 0.999999999811973`;
- `γ < 0.999071242992`, against the limit 9991/10000;
- `δ < 0.843991137666`, against the limit 6/7.

The tensor bound is 0.99999876. Its compiler is #4405's refined power majorant. Each conservative
constant it uses dominates the true quantity:

- the exit constant 88,608 exceeds the actual `log₂(r_max·m^h) = 74,093.9`;
- the bound `−log₂η ≤ 464.483` exceeds the actual value, 418.912;
- `18^55 < 19^54` gives `θ < 54/55`.

The stated `H0` = 357,651,736,794,440 and `H1` = 15,026,650,096,742,881,962,201 reproduce exactly.


**#4446's separate p6 BIT supplier**, which supplies the ordinary BIT premise, is also checked:

- the rank masses are 102,419 (paid) and 102,932 (target), with surplus 513;
- the raw root lies in `(0.00314, 0.00315)`, above the admitted 0.00312;
- `α < 99999/100000` at the tested saving `157/50000` (computed upper bound 0.9999882);
- the rank-one tail `γ = P_1/(7^C T_t) < 999/1000` (upper bound 0.998596);
- the finite paid moment `1/(1 + 6000/100000) + 2·2^{−6} = 1653/1696`;
- the separation `7^{16} < 8^{15}`;
- the compiler, `H0 = 850,090,000` and `H1 = 1,066,862,950,001`;
- the delayed-cover gap `1/200000`.

## Not covered

- The native replay of the new contact, its transports and phases.
- #4441's predecessor native work, which mihir-s-05's #4448 audits separately.
- The outer ledgers.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/p17-b480-check --check-only
python3.12 -B scripts/research_package.py --package research/p17-b480-check
```

The verifier prints `PASS_PR4447_PR4453_ARITHMETIC` in about 3 seconds, using only the standard
library.

## Open next questions

1. **Does a second missing span exist at another contact?**
   - *Why it matters:* the same concavity gain would apply.
   - *First step:* rerun #4453's line/hyperplane min-cut discovery with the B/480 contact fixed.

## Credit

- The patch and constructions are 1337isnot1337's (#4447, #4440, #4441) and zxv's (#4453, #4359).
- The higher-moment theorem and the polylog majorant are on main (`higher-moment-strictification`).
- Theorem 1G is Jacob Alan Sussman's.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
