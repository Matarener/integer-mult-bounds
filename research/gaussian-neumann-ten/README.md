# The Neumann ceiling U is below 10 p^2

**Claim type:** one rational comparison for the within-cell ceiling.
**No new κ.** The ideal-gap reading stays a hypothesis. The selected record
remains `23/10000`.

## Question

#4452 defines

```text
U = 8 p^2 (D - 4) / (D - 32 p^2),    D = 2^{32760 p},
```

and proves `8 p^2 < U < p^6` together with `U < 16 p^2 - 1`. The tensor
chain uses the ceiling `10 p^2`. Is `U` at most `10 p^2`?

## Lemma

For every integer `p ≥ 2`, `D > 32 p^2` and

```text
U < 10 p^2.
```

The coefficient 8 does not work: `U > 8 p^2`. This comparison is a property
of the formula. It becomes an inverse bound only when the #4452 gauge holds,
in which case the Neumann 1-norm and ∞-norm are already strictly below `U`,
hence strictly below `10 p^2`.

## Proof

The denominator `D - 32 p^2` is positive once `D > 32 p^2`, which follows
from the stronger estimate below. Cross-multiplying by that positive
denominator, `U < 10 p^2` is equivalent to

```text
8(D - 4) < 10(D - 32 p^2).
```

The difference is

```text
10(D - 32 p^2) - 8(D - 4) = 2D - 320 p^2 + 32 = 2(D - 160 p^2 + 16).
```

It is enough to show `D > 160 p^2 - 16`. Since `160 < 256 = 2^8` and
`32 < 160`, the same estimate also gives `D > 32 p^2`.

For every integer `p ≥ 2`, `2^{2p} ≥ p^2 + 1`, so `p^2 < 2^{2p}`. The base
is `2^4 = 16 ≥ 4 + 1`. If the inequality holds at `p`, then

```text
2^{2p+2} = 4 · 2^{2p} ≥ 4(p^2 + 1),
```

and `4(p^2 + 1) - ((p + 1)^2 + 1) = 3p^2 - 2p + 2`. At `p = 2` this surplus
is 10, and the step to the next integer is `6p + 1 > 0`. Thus
`160 p^2 < 2^8 p^2 < 2^{2p+8}`.

The remaining exponent gap is `32760 p - (2p + 8) = 32758 p - 8`. At
`p = 2` it equals 65508, and it increases with `p`. Therefore
`2^{2p+8} < 2^{32760 p} = D`, and `D > 160 p^2 > 160 p^2 - 16`.

At `p = 2` the same polynomial is `160 · 4 - 16 = 624 < 2^{10}`, while
`32760 · 2 > 10`. Replacing 10 by 8 reverses the target inequality, because
`U > 8 p^2` exactly when `32 p^2 > 4`.

## Not covered

- The smallest integer coefficient `c` with `U < c p^2`.
- A proof of the ideal gaps that make `U` an inverse bound.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-neumann-ten --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-neumann-ten
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap snapshot: open PRs fetched 2026-10-22T01:35:47Z (345 records) and
discussions fetched 2026-10-22T01:36:30Z (3369 records). A narrow search for
`U < 10`, `10 p^2 (D`, `160 p^2` and `D - 32` returned this draft and #4452.
#4452 stops at `U < p^6` and `U < 16 p^2 - 1`. A search miss is not a novelty
certificate. HALO is the written error.

## Open next questions

1. **What is the smallest integer `c` with `U < c p^2` for every integer
   `p ≥ 2`?** The coefficient 8 fails and 10 works. The first step is to
   clear `8(D - 4)` against `9(D - 32 p^2)`.

## Credit

- The ceiling `U` and the bounds `8 p^2 < U < p^6` are #4452's.
- The tensor use of `10 p^2` runs through #4462 and #4481.
- The question is the open step of #4491.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
