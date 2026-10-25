# Independent arithmetic check of the #4412 and #4414 tensor endpoints

**Claim type:** certified exact arithmetic plus a written check of the split bound. **No new κ.**
Neither PR is accepted, and their native audits are not re-checked. The objects are
1337isnot1337's
[#4412](https://github.com/CrocSwap/integer-mult-bounds/pull/4412) (κ = 0.00247755, head
`9f0df9bf`, with `TENSOR.md`/`ENDPOINT.md` SHA256 prefixes `d65a3997`/`2b0d1524`) and
[#4414](https://github.com/CrocSwap/integer-mult-bounds/pull/4414) (κ = 0.00267987, head
`90da4b0a`, prefixes `96e4593f`/`3d17949e`).

Both PRs tensor a native mixed unit `v` times and split each paid job at a cutoff `J` below the
smallest target rank:

- #4412 tensors the all-fresh p3 unit with `J = 4^v`;
- #4414 tensors the p6 unit with `J = ⌊(19/4)^v⌋`.

My [#4428](https://github.com/CrocSwap/integer-mult-bounds/pull/4428) checked their successor,
#4416.

## Split bound

For a paid rank `R > J`, the split satisfies `qJ^τ + r^τ ≤ 2RJ^{−C}`. That gives a normalized
paid moment below `α^v + 2γ^v`, where `α = P_τ/T_τ` and `γ = P₁/(c^C T_τ)`. For #4414,
`J ≥ (19/4)^v/2` doubles the tail, giving `α^v + 4γ^v`. The other requirements also hold:

- **Exit exponents.** `4^8 < 5^7` gives `θ < 7/8` for #4412, and `19^32 < 4^32·5^31` gives
  `θ < 31/32` for #4414.
- **Exit constants.** These are `B = (2 + 6h)v` for #4412 and `B = (79/32)v` for #4414, the latter
  from `19^4 < 2^17`. Both hold.
- **Base range.** `H0 ≥ log₂m·v` covers it.

## Results

| | #4412 | #4414 |
| --- | --- | --- |
| tested saving | 0.00247756 | 0.00267988 |
| `α` upper (stated) | 0.999999996840 (`≤ 1 − 10⁻⁹`) | 0.999999982435 (`< 1 − 10⁻⁸`) |
| `γ` upper (stated) | 0.99896534 (`< 999/1000`) | 0.99986298 (`< 9999/10000`) |
| raw mixed root | (0.0024775616403, 0.0024775616409) | (0.0026798899695, 0.0026798899701) |
| tested saving below root by | `1.6·10⁻⁹` | `1.0·10⁻⁸` |
| tensor power used / **least** under the same certified bound | 15,000 / **10,714** | 150,000 / **60,701** |
| `H0`, `H1` reproduced | 2,508,580,090,000; 8,701,218,254,312,470,001 | 126,106,333,450,000; 473,129,651,134,046,950,001 |

The `γ` margins are tight but certified: `3.5·10⁻⁵` and `3.7·10⁻⁵` under the stated bounds. The
least tensor powers are well below the ones used, at 0.71× and 0.40×. Smaller `v` shrinks every
tensor constant, though not the compiler rank, which is set by the slack gap `1/(1.4·10⁹)`.

## Not covered

- The native p3-fresh and p6 audits.
- The chronological tensor construction's native realization.
- The outer premises.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4412-pr4414-tensor-check --check-only
python3.12 -B scripts/research_package.py --package research/pr4412-pr4414-tensor-check
```

The verifier prints `PASS_PR4412_PR4414_TENSOR_ARITHMETIC` in about 15 seconds, using only the
standard library.

## Open next questions

1. **Does a rational cutoff closer to the minimum target rank reduce `v` further?**
   - *Example:* `(24/5)^v` for #4414's p6 unit.
   - *First step:* scan rational `c` below 5 with the same certified `γ` and the floor factor.

## Credit

- The constructions and invoices are 1337isnot1337's (#4412, #4414).
- The native controllers are zxv's (#4359).
- Theorem 1G is Jacob Alan Sussman's (#4268).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
