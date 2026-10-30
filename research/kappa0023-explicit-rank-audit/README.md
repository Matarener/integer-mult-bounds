# Independent check of #4359's explicit-rank chain

**Claim type:** an independent exact check of one quantitative chain in zxv's
[#4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359), plus a separate simulation
of its integer flow up to rank 10,000. **No new κ.** #4359's construction is not accepted
here. Native closure, the delayed BIT cover, adapters, precision and the outer bill are
outside this check.

## Object

This package audits #4359 at head `da637c87c89482bc4c86be36bd0071b3d400dbed`. That PR turns
its p3 mixed invoices into fixed uniform suppliers at ranks `2^276540184361` (complex) and
`2^6552928412` (BIT). The step is argued in two notes:

- `FINITE-PRECOMPILATION.md` §3–5 (SHA256 `4cb32f6b…921e8`): the integer lockstep flow, the
  leaf recurrence `L(n) = Σ w_s L(n−s) + Σ x_e L(e)`, and the induction.
- `EXPLICIT-TEMPLATE-BOUNDS.md` (`e54345bf…f8b0`) and its JSON receipt (`3f1abfaf…2c3f`):
  explicit `H0` and `H1`.

#4359's own open question 1 asks for review "beginning with the source/exit recurrence". Those
files are not on main. The verifier therefore embeds the two invoices and the rational
parameters as printed in the receipt, and it imports nothing from #4359.

## Results

**Part A: certified powers.**

- **Superpotential.** `Σ W_k k^t − Σ p_r r^t` at the tested `t` is 0.008726900863 (complex) and
  0.067093183910 (BIT). Both match the receipt's `strict_test_margin`.
- **Root brackets.** The author's mixed-balance root brackets straddle the balance. That covers
  the 10⁻³⁰-wide complex bracket and the 10⁻¹² BIT one.
- **Surpluses and η.** The rank-one surpluses are 224 and 225, and `η = z0·m^(z0−1) > 1/4`
  holds.

**Part B: the exact chain.** All of these hold:

- `θ < θ̄`: `5^10 < 6^9` and `7^16 < 8^15`;
- `m^h < 2` and `2r_max ≤ 16`;
- `H0 = ⌈(3+4δ)/(hδ)⌉ = 60,000,040` and `10,666,731`. Each is the least value giving the
  exit coefficient `(16·n^(−h))^δ ≤ 1/8`;
- `H1 = ⌊H0(1−z0)/(z−z0)⌋ + 1 = 276,540,184,361` and `6,552,928,412`. Each is the least value
  with `A·N^(z0) < N^z`.

**The induction, written out.** Put `S = Σ w_s s^(z0)` and assume `L(k) ≤ A k^(z0)` for
`k < n`, where `n > n0`. Concavity gives `Σ w_s (n−s)^(z0) ≤ n^(z0) − ηS`. The exit bound gives
`Σ x_e e^(z0) ≤ S/8`. Then `L(n) ≤ A(n^(z0) − ηS + S/8) < A n^(z0)`, because `η > 1/4`. For
`n ≤ n0`, use `L(n) ≤ n ≤ A n^(z0)`, which holds because `A = n0^(1−z0)`. The exit bound
itself is `Σ x_e e^(z0) ≤ E^δ Σ x_e e^t ≤ E^δ Σ w_s s^t ≤ (mE/n)^δ S`. Its last step uses
`s > n/m`. I found no gap in this chain.

**Part C: the flow.** The exit-rank bound follows from §3's class structure. Exits occur only
in the deepest classes (`d = G`, `a = 0`), at rank `r_j ρ_s ≤ r_max^(G+1)`. Since
`k_min^G ≤ c(a) ≤ N/m`, this gives `r_max^G ≤ (N/m)^θ`. Sources lie in `(N/m, N]` because
`a + e_k` overflows at size `G + 1`. Every parent paid job is matched, because `r_j < k`.

The verifier simulates the flow independently, grouping classes by dilation. It runs every top
rank from `m` to 10,000: 9,944 complex flows and 9,951 BIT flows. At every rank it checks
exactly:

- all sources lie in `(N/m, N]`;
- all exits are at most `r_max^(G+1) < N`, with `r_max^(Gb) ≤ (N/m)^a` for `θ̄ = a/b`;
- `Σ S_s s − Σ X_e e` equals the surplus times the total unit column mass. This is the
  potential conservation the recurrence relies on;
- the exact rational `L(N)` satisfies `L(N) ≤ N`.

**Observation.** The effective saving `1 − log L(N)/log N` is still small at these ranks:

| `N` | complex | BIT |
| --- | --- | --- |
| 1,500 | 0.001047 | 0.000999 |
| 10,000 | 0.001193 | 0.001155 |

Both are about half of the claimed limits, 0.002304 and 0.002760. This is consistent with the
slow convergence the explicit `H1` implies. It is not evidence against the asymptotic claim.

## Not covered

- Hypotheses 1–4 of `FINITE-PRECOMPILATION.md` §1: the all-column native word, disjoint
  splitting, whole-job adapters and finite-program closure.
- The denominator clearing of §4, beyond the normalized recurrence it produces.
- Scalar and routing passes, which §4 says must enter the asymptotic cost.
- The delayed BIT cover, precision and storage constants, and the nine-row outer bill.
- Whether the p3 invoices match their native words. The invoice is taken as printed.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/kappa0023-explicit-rank-audit --check-only
python3.12 -B scripts/research_package.py --package research/kappa0023-explicit-rank-audit
```

The verifier prints `PASS_KAPPA0023_EXPLICIT_RANK_AUDIT` in about 75 seconds, using only the
standard library.

## Open next questions

1. **Is the scalar and routing work per productive array sublinear in the same sense as
   `L(n)`?**
   - *Why it matters:* §4 requires these passes in the asymptotic cost, but no recurrence for
     them is written.
   - *First step:* add a per-unit scalar count to this flow simulation and fit its growth per
     array.
   - *Blocked by:* nothing at the level of normalized counts.
2. **Can a much smaller explicit rank be certified?**
   - *Why it matters:* the simulated saving at `N = 10⁴` is about half the limit, while `H1` is
     about `2.8·10¹¹` bits.
   - *First step:* replace the uniform `1/8` exit coefficient with the actual exit mass that the
     simulation measures.
   - *Blocked by:* nothing.

## Credit

The construction, invoices and explicit-rank argument are zxv's (#4359). The lockstep flow is
Jacob Alan Sussman's Theorem 1G (#4268). Prepared by Ryanson Jonathan with substantial Claude
Code (Claude Opus 5.5) assistance. Apache-2.0.
