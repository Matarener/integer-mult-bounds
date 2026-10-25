# Independent review of #4411's logarithmic majorant

**Claim type:** a written proof check, certified exact arithmetic and an independent flow
simulation. **No new κ.** It reviews zxv's
[#4411](https://github.com/CrocSwap/integer-mult-bounds/pull/4411) at head `ec2c9505`, with README
SHA256 prefix `3b74b9b2`, as that PR's open question asks. #4411 replaces #4359's power majorant
with

    L(n) = P_n/B_n ≤ F(n) = n^t (1 + log₂ n)^{1/q},

and specifies ranks `2^465000` (complex) and `2^7100` (BIT) at κ = 0.0023. Those supersede my
own #4413 ranks, `2^268300549` and `2^14664`. #4411 and #4413 were posted in parallel.

## Proof check

The induction is checked line by line, and it holds.

- **Base, `n < m`.** For `2 ≤ n < m`, `n^{q(1−t)} < m^{q(1−t)} < 2 ≤ 1 + log₂ n`, using (4).
- **Exit contraction (6).** Since `θ < θ̄` and `n ≥ m`, `log₂ E ≤ log₂ r_max + θ̄(log₂ n − log₂ m)`.
  Then `1 + log₂ E ≤ θ̄(1 + log₂ n)` is equivalent to `2^{1−θ̄} r_max ≤ m^{θ̄}`, which is (2). So
  `C(e) ≤ θ̄^{1/q}C(n)`, and (1) gives `Σ x_e F(e) ≤ θ̄^{1/q}C(n)Σ w_s s^t`.
- **Complements (7).** `C` is increasing, so `F(n−s) ≤ (n−s)^t C(n)`, with `F(0) = 0`. With
  `1 − (1−y)^t ≥ η y^t` on `(1/m, 1]`, this gives `F(n) − Σ w_s F(n−s) ≥ η C(n) Σ w_s s^t`.
- **Induction.** Condition (3), `θ̄ < η^q`, makes (6) smaller than (7). Strong induction then
  gives `L(n) ≤ F(n)` for all `n ≥ 1`, with constant 1.
- **Final rank test.** `L(N) < N^z` holds iff `1 + H < 2^{q(z−t)H}`.

## Certified arithmetic

| | complex | BIT |
| --- | --- | --- |
| `θ < θ̄` | `5^10 < 6^9` | `7^16 < 8^15` |
| (2) `2^{b−a} r_max^b ≤ m^a` | holds | holds |
| (3) `η^q − θ̄` | 0.000646856868 (matches #4411) | 0.009533387925 (matches) |
| (4) `m^{q(1−t)} < 2` | holds | holds |
| stated / **least** `H`, original savings | 2,352,000 / **2,351,697** | 529,000 / **528,066** |
| stated / **least** `H`, κ-preserving savings | 465,000 / **464,850** | 7,100 / **7,091** |

Every stated `H` is certified. #4411's values are rounded up from the least `H` that passes the
same sufficient test; that least value is computed here by bisection with certified logarithms.

## Flow simulation

The separate aggregated lockstep-flow simulator from my #4404 computes exact rational `L(N)` for
every `N ≤ 6000` in both families. At every rank it checks the source range, the exit bound and
the exact rank-one potential identity, and that `L(N) ≤ F(N)`. The largest ratio `L(N)/F(N)` is
0.927 (complex) and 0.843 (BIT), so the majorant holds with room on all simulated ranks.

## Not covered

- #4411's retuned consumer point (`b = 0.0023004`, `a = 0.0023003`) and its 63 + 22 predicates.
- Native closure, the delayed cover and outer transfer.
- Ranks above 6000 in the simulation. The proof, not the simulation, covers all `n`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4411-majorant-review --check-only
python3.12 -B scripts/research_package.py --package research/pr4411-majorant-review
```

The verifier prints `PASS_PR4411_MAJORANT_REVIEW` in about 30 seconds, using only the standard
library.

## Open next questions

1. **Can the `(1 + log₂ n)^{1/q}` factor be replaced by a smaller slowly varying factor?**
   - *Why it matters:* the simulated ratio `L/F` is well below 1.
   - *First step:* fit the simulated `L(N)/N^t` against `log N`.

## Credit

The majorant, ranks and consumer retuning are zxv's (#4411). The compiler is #4359's, and the
lockstep flow is Jacob Alan Sussman's Theorem 1G (#4268).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
