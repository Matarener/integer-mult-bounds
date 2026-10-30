# Pairing rank of the E8 label alphabet is at most 9

This note bounds one support alphabet. It does not construct a decoder, price a
frame or a restoration, or change κ. The selected exponent stays
`0.001672660197076918`.

## Alphabet

Use the 240 doubled E8 roots and their 120 lines, with the integer inner
product normalized by 4. Off the diagonal those products lie in `{-1, 0, 1}`,
and each line has norm 2. The PR717 label pairing is the `120 × 120` matrix
over `F_2`

```text
B_ij = (<r_i, r_j> + 1) mod 2.
```

`verify.py` rebuilds this matrix from the roots. It does not import the
frame-pair decoder checker.

## Rank cap

Gaussian elimination produces nine independent rows. Every one of the 120 rows
reduces to zero against that basis, so the row space has dimension 9 and
`rank(B) = 9`.

Any term support is a row set `X` and a column set `Y`. The corresponding
block is a column restriction of a set of vectors in a 9-dimensional space, so

```text
rank B[X, Y] <= 9.
```

The same nine basis rows, kept against all 120 columns, have rank 9. The cap
is attained by those supports. A synthetic extra column of rank 10 is rejected
by the rank routine and is not a row of `B`.

If a child in this alphabet is priced by this pairing rank, no such child has
rank 10 or more. Copies, frame conversions and restoration that are not
themselves pairing-rank terms of `B` are outside the alphabet.

## Favorable screen on the selected template

The pinned ceiling record fixes the selected template: width 73, `2 · 4 · 112`
families, nine stages, centre charge 64, local mass 5586 and idle mass 1646.
The outer halving guard leaves idle rank 51. The published local profile is
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`.

For `a > 0`, the per-unit child cost `r^{-a} m^{a-1}` is strictly decreasing
in the child rank `r`. The checker compares the pinned enclosures at
`a = 1/99` for every rank `1..8` against rank 9. Among local histograms of
mass 5586 whose ranks are at most 9, the fractional histogram

```text
{9: 5586/9}
```

is therefore strictly cheapest at that saving. It keeps the same idle mass
1646, packed at rank 51. Its relaxation moment is strictly above 1. The
integer histogram `{9:620, 6:1}` has the same mass and is also strictly above
1. The certified ceiling bracket of the fractional histogram, on the pinned
`1e-15` grid, lies strictly below `1/99`.

The same screen accepts the fractional rank-44 histogram at `a = 1/99`. The
rank-9 failure is not a comparator that rejects every profile.

Extra local children of rank at most 9, including unpaid frame or restoration
children inside this alphabet, add a nonnegative moment and cannot bring the
relaxation back through 1. A child whose rank is not a pairing rank of `B` is
a different alphabet.

## What this does not say

The cap is not a bound on multiplication width, on idle children, or on a
block climb whose rank is a tensor or frame dimension. It does not say that an
exact eight-term decoder uses a rank-9 term. It does not meet the card's
five-percent construction gate. No new κ is claimed.
