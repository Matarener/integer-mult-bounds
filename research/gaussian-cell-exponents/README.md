# The smaller halo exponents hold inside one cell

**Claim type:** conditional exponent arithmetic for one within-cell block.
**No new κ.** The global rounded matrix, whose across-cell entries are not
this gauge ratio, is outside the claim.

## Question

#4406 showed that HALO's exponents can fall to 12, 26, 28, 28 and 7 when both
2-norms are at most `16 p^2`. #4438 gave a within-cell column budget
`ε ≤ 1/(16p^2)`. Do those five exponents apply to the rounded block

```text
A = diag(ahat) Ghat diag(ahat)^{-1}
```

once that budget holds?

## Lemma

Let `p ≥ 2` be an integer and let `W` be an integer at most `p-1`. Assume the
ideal row and column off-sums are at most `1 - 1/(8p^2)`, the conclusions
GAUSSIAN and #4402 state eventually, and assume the within-cell rounding of
#4438: `Ghat_0 = 1`, `0 ≤ Ghat ≤ exp(-a ρ h^2)`, and
`(1-ε) a ≤ ahat ≤ a` with `ε ≤ 1/(16p^2)`.

Then both rounded off-sums are at most `(16p^2-2)/(16p^2-1)`, so both gaps
are at least `1/(16p^2-1)`. The Neumann series gives

```text
||A^{-1}||_∞ ≤ 16 p^2 - 1,    ||A^{-1}||_1 ≤ 16 p^2 - 1,
```

and therefore `||A^{-1}||_2 ≤ 16 p^2 - 1`. Each absolute row and column sum is
strictly less than 2, so `||A||_2 < 2`.

For this block the polynomial

```text
P = p^{-12} sum_{j < p^{26}} Q^j A^*,    Q = I - p^{-12} A^* A,
```

satisfies `||P - A^{-1}||_2 < p^6 exp(-p^2)`. Its bandwidth is at most
`(2 p^{26} - 1) W < p^{28}`, and the looser count `(2 p^{26} + 1) W` has the
same ceiling. A row at distance `p^{28}` from a section edge of this block
agrees with the block row. Dividing by `p^6` puts the inverse ceiling strictly
below one.

So 12, 26, 28, 28 and 7 all apply. The first four remain the smallest uniform
integers with that property. The normalizer 7 is not smallest: the ceiling
`16 p^2 - 1` is already strictly below `p^6`, while it is above `p^5` at
`p = 2`. The smallest normalizer is 6.

## Proof

The gauge ratio multiplies every off-diagonal entry by at most `1/(1-ε)`, on
a row and on a column. With `ε = 1/(16p^2)` and an ideal off-sum at most
`1 - 1/(8p^2)`,

```text
off ≤ (1 - 1/(8p^2)) / (1 - 1/(16p^2)) = (16p^2 - 2)/(16p^2 - 1).
```

The complementary gap is `1/(16p^2-1)`. Adding the diagonal produces the row
sum `(32p^2-3)/(16p^2-1)`, and `2(16p^2-1) - (32p^2-3) = 1`, so the sum is
strictly below 2. The same bound is the column sum. The 2-norm comparison
`||·||_2 ≤ sqrt(||·||_1 ||·||_∞)` is the one already used for these matrices.
It gives `||A||_2 < 2` and `||A^{-1}||_2 ≤ 16 p^2 - 1`.

The inverse ceiling is 63 at `p = 2`. Then `63^2 = 3969 ≤ 4096 = 2^{12}` and
`3969 > 2048 = 2^{11}`. The forward 2-norm is below 2, so the upper end
`p^{12}` is loose, but `p^{-12}` is still a legal lower bound on the
eigenvalues of `A^* A` and `p^{-11}` is not. Thus `Q` has spectrum in
`[0, 1-p^{-24}]`. The scalar step in the exponential series is strict because
`1/2! < 1`, and `p^{26} p^{-24} = p^2`. The shorter length `p^{25}` leaves a
factor `p^{11}` against `(16p^2-1)^2`, and `2048 < 3969` at `p = 2`.

The error is therefore strictly less than `(16p^2-1) exp(-p^2)`. Since
`p^4 - 16 = (p-2)(p+2)(p^2+4)`, one has `16p^2 - 1 < p^6`, with room 1 at
`p = 2`. The multiplier `p^5` fails because `63 > 32`.

The bandwidth identity is unchanged:

```text
p^{28} - (2 p^{26} - 1)(p-1) = p^{26} ((p-1)^2 + 1) + p - 1 > 0.
```

At `p = 2` the loose radius `(2J+1)W` equals `p^{27}+1`. For every integer
`p ≥ 3` the sharp radius at `W = p-1` exceeds `p^{27}`. Exponent 27 is not a
uniform ceiling. Exponent 28 is.

Dividing by `p^6` is strict, as above. Dividing by `p^7` remains strict and
is the value #4406 recorded for the closed ceiling `16 p^2`.

## Not covered

- Across-cell entries. They are the downward original entries, not
  `ahat_j Ghat_(j-k)/ahat_k`, so this does not move HALO's exponents for the
  global reference.
- A proof that the ideal gaps exceed `1/(8p^2)` for every prime. That remains
  the eventual statement in GAUSSIAN and #4402.
- The core exponent 400. It still dominates a halo of 28, and it is not retuned.
- Any new κ. The selected record remains `23/10000`. The #4100 notes keep
  20, 42, 45, 48 and 100.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-cell-exponents --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-cell-exponents
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-21 did not find a within-cell assignment of these
exponents. #4406 is the conditional arithmetic for a closed ceiling `16 p^2`.
#4438 is the relative-error budget. A search miss is not a novelty certificate.

## Open next questions

1. **Do 12, 26, 28, 28 and 6 survive across a cell?**
   The within-cell block now meets the ceiling those exponents use, and the
   normalizer may be 6 rather than 7. The global reference is still blocked:
   its across-cell entries are the downward approximation of the original
   entry, and no column bound for that rule is written. The first step is a
   column off-sum for those entries under the same `ε`.

## Credit

- HALO's locality witness and its written exponents are #4100's.
- The sharp radius `(2J-1)W` is Nick Petalas's halo audit, PR #4217.
- The in-cell ideal column gap is Ryanson Jonathan's #4402.
- The relative-error budget is #4438.
- The closed-ceiling arithmetic is #4406.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
