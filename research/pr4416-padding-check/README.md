# Independent check of #4416's paid-completion tensor bound

**Claim type:** a written proof check plus certified exact arithmetic. **No new κ.** #4416 is not
accepted, and the native p7 audit and the outer premises are not re-checked. The object is
1337isnot1337's [#4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416) at head
`e9058860`, with `TENSOR.md` SHA256 prefix `b2eba86c` and `ENDPOINT.md` prefix `e7056020`. It
proposes conditional κ = 0.00268647 from zxv's p7 controller. The p7 controller is tensored
`v = 6240` times, small targets are completed to `11^v`, and paid jobs are split at `10^v`.

## Proof check (`TENSOR.md` §1–3, §5)

- **Product moments multiply.**
  - Copy `j` of `U` runs at column `h_j`.
  - Each paid position `l` of `U` makes one call to `V` at column `r_l`, whose role `j` delivers
    rank `r_l h_j`.
  - So the targets are `k_i h_j`, the paid ranks are `r_l s_a`, `T_τ(UV) = T_τ(U)T_τ(V)` and
    `P_τ(UV) = P_τ(U)P_τ(V)`.
- **Completion.** Completing to rank `L` on disjoint axes is the canonical rank-`L` endpoint.
  By concavity it loses moment, since `L^τ − K^τ < D^τ`. What it buys is the separation
  `paid ≤ 10^v < 11^v ≤ target`. The bound conservatively keeps `T_τ^v` as the target moment.
- **Split tails.** `qJ^τ + r^τ ≤ RJ^{−C} + J^τ ≤ 2RJ^{−C}` holds for `R > J`. For completions,
  `charge(D) ≤ (D + J)J^{−C} < 2L/J^C`. Together these give `α^v + 2γ^v + 2δ^v`.
- **Rank formula.**
  - `r_max m^h < 2^{(111/26)v}` follows from `10 < 2⁴` and `121 < 2⁷`.
  - `−log₂η < 1 + 7v(1−z0)` follows from `z0 > 1/2`.
  - `θ < 25/26` follows from `10^26 < 11^25`.
  - `H0 ≥ 7v` covers the base range `n < 121^v`.

I found no gap in these steps.

## Certified arithmetic

| Quantity | This check | #4416 |
| --- | --- | --- |
| fields, paid calls, rank-one masses | 7,688; 55,998; 131,723 / 131,115 | same |
| `α = P_τ/T_τ` at `C = 0.00268648` | `< 0.999999984404` | `< 1 − 10⁻⁸` |
| `γ = P₁/(10^C T_τ)` | `< 0.99819171` | `< 4991/5000 = 0.9982` |
| `δ = 7688·11/(10^C T_τ)` | `< 0.64382471` | `< 2/3` |
| p7 mixed root | `(0.0026864890486, 0.0026864890492)` | above 0.00268648 |
| `α^v + 2γ^v + 2δ^v < 1` at `v = 6240` | holds (Bernoulli and direct) | holds |
| least `v` (direct certified route, `b = 11`, `c = 10`) | **5,745** | 6,240 used |
| `H0`, `H1` | 4,307,773,805,920 and 16,201,843,136,005,340,321 | same |

The tight margin is `γ`: its bound sits only `8·10⁻⁶` below 4991/5000. The tested saving
0.00268648 is `9·10⁻⁹` below the p7 root.

**A tighter rank from the same induction.** Using certified `−log₂η` and the exact
`log₂(r_max m^h)`, together with the best `θ̄ = 145/151` (from `10^151 < 11^145`, so
`h = 6/151`), gives `H1 = 15,370,312,178,898,752,926`. That is 5.4% below #4416's value. It is a
minor gain: the binding factor is `δ_gap = 1/1,400,000,000`, which is set by the choice of κ.

## Not covered

- The native p7 audit: contacts, phases, helpers and the all-column contract.
- The analytic, precision, tape and outer premises.
- The 209-profile screen in `FOLLOWUP.md`.
- Optimality of `(v, b, c)`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4416-padding-check --check-only
python3.12 -B scripts/research_package.py --package research/pr4416-padding-check
```

The verifier prints `PASS_PR4416_PADDING_ARITHMETIC` in about 10 seconds, using only the
standard library.

## Open next questions

1. **Which `(b, c)` minimizes `v`?**
   - *Why it matters:* the least `v` with `(11, 10)` is 5,745.
   - *First step:* scan `c < b < 121` with the direct certified route.

## Credit

- The construction and invoice are 1337isnot1337's (#4416, #4414, #4412).
- The native controller is zxv's (#4359).
- Theorem 1G is Jacob Alan Sussman's (#4268).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
