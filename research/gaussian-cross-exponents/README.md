# The smaller halo exponents survive across a cell

**Claim type:** conditional transfer from one cell to the banded reference.
**No new κ.** The ideal gaps and the within-cell factor stay hypotheses.
The selected record remains `23/10000`.

## Question

#4439 put the exponents 12, 26, 28, 28 and 6 on the rounded block inside one
cell. The global reference also has across-cell entries. Those entries are
the downward Gaussian entries, which are not the ratio
`ahat_j Ghat_(j-k)/ahat_k`. Do the same exponents apply to that reference?

## Lemma

Let `p ≥ 2` be an integer and let `W` be an integer at most `p-1`. Let `N`
be the exact Gaussian matrix, with entries

```text
n_i,h = exp(-a[(ρ h + β_i)^2 - β_(i+h)^2]).
```

Assume each ideal row off-sum and each ideal column off-sum is at most
`1 - 1/(8p^2)`. Assume that inside a cell every off-diagonal entry of `H`
is at most the matching entry of `N` divided by `1-ε`, with
`ε ≤ 1/(16p^2)`. Assume that across a cell

```text
0 ≤ H_i,i+h ≤ n_i,h
```

for every retained distance, and that every entry outside that band is 0.
The diagonal is 1.

Then both off-sums of `H` are at most `(16p^2-2)/(16p^2-1)`, so both gaps
are at least `1/(16p^2-1)`. Hence `||H||_2 < 2` and

```text
||H^{-1}||_2 ≤ 16 p^2 - 1.
```

The polynomial

```text
P = p^{-12} sum_{j < p^{26}} Q^j H^*,    Q = I - p^{-12} H^* H,
```

satisfies `||P - H^{-1}||_2 < p^6 exp(-p^2)`. Its bandwidth is at most
`(2 p^{26} - 1) W < p^{28}`, and the looser count `(2 p^{26} + 1) W` has the
same ceiling. Dividing by `p^6` puts the inverse ceiling strictly below one.

So 12, 26, 28, 28 and 6 all apply to this banded `H`. They remain the
smallest uniform integers with that property. At `p = 2` the inverse ceiling
is 63, and `63^2 = 3969` sits in `(2^{11}, 2^{12}]`. The value 63 is below
`2^6` and above `2^5`. Exponent 27 fails for `p ≥ 3` at `W = p-1`.

## Proof

Write `S = 16 p^2`, and write an off-sum of `N` as `T ≤ (S-2)/S`. Split `T`
into the within-cell part `U` and the across-cell part `T-U`, with
`0 ≤ U ≤ T`. The two rounding hypotheses give

```text
off(H) ≤ U / (1 - 1/S) + (T - U).
```

Clear the positive denominator `S-1`. The resulting polynomial identity, in
the indeterminates `S`, `T` and `U`, is

```text
S U + (T-U)(S-1) - T S = U - T.
```

The right side is at most 0 precisely when `U ≤ T`. Therefore

```text
off(H) ≤ T / (1 - 1/S) ≤ (S-2)/(S-1) = (16p^2-2)/(16p^2-1).
```

The complementary gap is `1/(16p^2-1)`. The row sum is at most
`(32p^2-3)/(16p^2-1)`, and `2(16p^2-1) - (32p^2-3) = 1`, so every absolute
row sum and every absolute column sum is strictly below 2. The 2-norm
comparison `||·||_2 ≤ sqrt(||·||_1 ||·||_∞)` then gives `||H||_2 < 2` and
`||H^{-1}||_2 ≤ 16 p^2 - 1`.

The same ceiling arithmetic as #4439 applies to this global pair of bounds.
`16p^2 - 1 < p^6` because `p^4 - 16 = (p-2)(p+2)(p^2+4)` and the remaining
room is 1 at `p = 2`. The forward square is below 4, so `p^{12}` remains a
legal upper bound on the eigenvalues of `H^* H`. The lower bound `p^{-12}`
is legal because `(16p^2-1)^2 ≤ p^{12}`, and `p^{-11}` is not, since
`3969 > 2048` at `p = 2`. For every integer `p ≥ 3`, even `(16 p^2)^2` is
below `p^{12}`, because `p^8 ≥ 3^8 > 256`. Thus `Q` has spectrum in
`[0, 1 - p^{-24}]`. The scalar step is strict because `1/2! < 1`, and
`p^{26} p^{-24} = p^2`. The shorter length `p^{25}` fails at `p = 2`.

The bandwidth identity is unchanged:

```text
p^{28} - (2 p^{26} - 1)(p-1) = p^{26} ((p-1)^2 + 1) + p - 1 > 0.
```

At `p = 2` the loose radius equals `p^{27}+1`. For every integer `p ≥ 3`
the sharp radius at `W = p-1` exceeds `p^{27}`.

## Where the across-cell inequality comes from

LOG-A defines the Gaussian coefficient `n_i,h` by the square-gap formula
above, and it tells the construction to use the retained downward Gaussian
entries across cells. The same paragraph separately names the downward
Toeplitz kernel `Ghat`. Downstream says to use the downward dyadic
approximation of the original entry across cells, and to put every entry
outside the band at zero. The review says the within-cell ratios can sit
slightly above the true entries, and it assigns downward dyadic entries to
the across-cell places. Read together, those sentences are the hypothesis
`0 ≤ H ≤ n` on across-cell pairs. Zeroing a tail only lowers an off-sum.

That formula is not printed as an inequality in those notes. This package
uses it as the reading of “downward” and then proves the off-sum comparison.
FINE-PRIME’s sentence for the same places says “rounded Gaussian entries”.
That file does not contain the words “downward Gaussian entries”, so the
rounded sentence is not this hypothesis.

A downward rounding of the bare kernel `exp(-a ρ h^2)` is a different rule.
At `θ = 1/4`, `β = 1/4`, `h = 1` and a step `g = 2`, the next weight is
`β + θ - 1 = -1/2`. The Gaussian square gap is `2` and the bare kernel uses
`ρ h^2 = 5/4`. In sixteenths those are 32 and 20. The bare value is larger,
so a number that is only downward for the bare kernel can exceed `n`.

The ceiling is tight against that kind of excess. At `p = 2`,
`63/64 > 62/63` because `63 · 63 = 3969 > 3968 = 62 · 64`. An across-cell
overshoot of one part in 64 above the ideal off-sum `(S-2)/S` already
exceeds `(S-2)/(S-1)`. The inverse ceiling 63, and the strict normalizer
`p^6`, use that smaller gap.

## Not covered

- A proof that the rounding procedure returns a value in `[0, n]`. The
  four-ulp repair is written for weights and for truncated Toeplitz
  coefficients.
- A proof that the ideal gaps exceed `1/(8p^2)` for every prime. That
  remains the eventual statement in GAUSSIAN and #4402.
- The Schur complement. LOG-A tracks a coarser row gap through elimination.
- The core exponent 400. It still dominates a halo of 28, and it is not
  retuned.
- Any new κ, and any edit to the #4100 notes. Those notes keep 20, 42, 45,
  48 and 100.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-cross-exponents --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-cross-exponents
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-21 found this question only as the open end of #4438 and
#4439, both of which stop before the across-cell off-sum. A search hit is
not a novelty certificate.

## Open next questions

1. **Does the written rounding procedure put each across-cell entry in
   `[0, n]`?** The transfer above treats `0 ≤ H ≤ n` as the reading of the
   downward sentences. The four-ulp repair is stated for the weights and for
   the truncated Toeplitz coefficients. The first step is to apply that
   repair to the exponent `-a[(ρ h + β_i)^2 - β_(i+h)^2]` and prove the
   stored value is at most the true exponential.

## Credit

- HALO's locality witness and its written exponents are #4100's.
- The sharp radius `(2J-1)W` is Nick Petalas's halo audit, PR #4217.
- The in-cell ideal column gap is Ryanson Jonathan's #4402.
- The relative-error budget is #4438. The within-cell exponents are #4439.
- The closed-ceiling arithmetic is #4406.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
