# The smallest integer coefficient on the Neumann ceiling is 9

**Claim type:** one integer coefficient for the within-cell ceiling.
**No new κ.** The ideal-gap reading stays a hypothesis. The selected record
remains `23/10000`.

## Question

#4492 shows `U < 10 p^2` and leaves the smallest integer open. For

```text
U = 8 p^2 (D - 4) / (D - 32 p^2),    D = 2^{32760 p},
```

what is the smallest integer `c` such that `U < c p^2` for every integer
`p ≥ 2`?

## Lemma

For every integer `p ≥ 2`, `D > 32 p^2` and

```text
8 p^2 < U < 9 p^2.
```

The smallest such integer is therefore `9`. The same `9 p^2` is strictly
sharper than both upper bounds recorded with this formula: `9 p^2 < 16 p^2 - 1`
and `9 p^2 < p^6`. This comparison is a property of the formula. It becomes
an inverse bound only when the #4452 gauge holds, in which case the Neumann
1-norm and ∞-norm are already strictly below `U`, hence strictly below
`9 p^2`.

## Proof

The denominator `D - 32 p^2` is positive once `D > 32 p^2`, which follows
from the stronger estimate below. Cross-multiplying by that positive
denominator, `U < 9 p^2` is equivalent to

```text
8(D - 4) < 9(D - 32 p^2).
```

The difference is

```text
9(D - 32 p^2) - 8(D - 4) = D - 288 p^2 + 32.
```

It is enough to show `D > 288 p^2 - 32`. Since `288 < 512 = 2^9` and
`32 < 288`, the same estimate also gives `D > 32 p^2`.

For every integer `p ≥ 2`, `2^{2p} ≥ p^2 + 1`, so `p^2 < 2^{2p}`. The base
is `2^4 = 16 ≥ 4 + 1`. If the inequality holds at `p`, then

```text
2^{2p+2} = 4 · 2^{2p} ≥ 4(p^2 + 1),
```

and `4(p^2 + 1) - ((p + 1)^2 + 1) = 3p^2 - 2p + 2`. At `p = 2` this surplus
is 10, and the step to the next integer is `6p + 1 > 0`. Thus
`288 p^2 < 2^9 p^2 < 2^{2p+9}`.

The remaining exponent gap is `32760 p - (2p + 9) = 32758 p - 9`. At
`p = 2` it equals 65507, and it increases by 32758 when `p` increases by 1.
Therefore `2^{2p+9} < 2^{32760 p} = D`, and `D > 288 p^2 > 288 p^2 - 32`.

At `p = 2` the same polynomial is `288 · 4 - 32 = 1120 < 2^{13}`, while
`32760 · 2 > 13`. The coefficient 8 reverses the target inequality, because
`U > 8 p^2` exactly when `32 p^2 > 4`. No integer lies strictly between 8
and 9, and every integer `c ≤ 8` fails because `U > 8 p^2 ≥ c p^2`.

The two older ceilings lose to 9 by the same integer comparisons. From
`7 p^2 > 1` one has `9 p^2 < 16 p^2 - 1`. From `p^4 ≥ 16 > 9` one has
`9 p^2 < p^6`.

## Not covered

- A proof of the ideal gaps that make `U` an inverse bound.
- Replacing `10` by `9` in the tensor absorption or the Schur margin.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-neumann-nine --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-neumann-nine
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T01:42:53Z and was
still that commit.

Overlap snapshot: open PRs fetched 2026-10-22T01:43:37Z (346 records) and
discussions fetched 2026-10-22T01:44:21Z (3370 records). A search for `U < 9`,
`9 p^2`, `288 p^2`, `smallest integer c` and `D - 288` returned this draft,
#4492, and its handoff, which leave the coefficient open, plus an unrelated
cyclic-Fourier log ceiling. A search miss is not a novelty certificate.
#4452 is the definition of `U`. HALO is the written error.

## Open next questions

1. **Does the #4484 gate absorb `g (9 p^2)^g exp(K p - p^2)`?** That gate
   spends four bits because `10 < 16`. The first step is to put `9` in place
   of `10` in the exponent `L + 4 g + 2 g L + 2 K p - p^2` and test whether
   three bits fail because `9 > 8`.

## Credit

- The ceiling `U` and the bounds `8 p^2 < U < p^6` and `U < 16 p^2 - 1` are #4452's.
- The coefficient 10, and this question, are #4492's.
- The tensor use of `10 p^2` is #4484. The Schur margin `1/(10 p^2)` is #4481.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
