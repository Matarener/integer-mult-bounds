# Schur complements keep a row margin of 1/(10 p^2)

**Claim type:** one elimination lemma, plus the exponent arithmetic it feeds.
**No new κ.** The ideal gaps stay hypotheses. The selected record remains
`23/10000`.

## Question

#4462 transferred the exponents 11, 24, 26, 26 and 6 to the whole banded
reference, with inverse bound `10 p^2` in its robust reading. Its open
question asks whether those exponents survive the Schur complement. The
first step named there is to restate the interior-elimination row gap with
`10 p^2` in place of `16 p^2 - 1`.

## Lemma

Let `p ≥ 2` be an integer and let `δ = 1/(10 p^2)`. Suppose `H` has diagonal
entries equal to 1, and every row and every column has absolute off-sum at
most `1 - δ`. Let `S` be the Schur complement of any principal set whose
pivots stay nonzero.

Then every row and every column of `S` has margin at least `δ`, and absolute
sum at most `2 - δ`. In particular

```text
||S^{-1}||_1 ≤ 10 p^2,    ||S^{-1}||_∞ ≤ 10 p^2,    ||S||_2 < 2,
```

and the same holds for `||S^{-1}||_2`. The polynomial used in #4452, with
spectral endpoint 11, therefore satisfies
`||P - S^{-1}||_2 < p^6 exp(-p^2)` on this complement. Its bandwidth is at
most `(2 p^{24} - 1) W < p^{26}` for every integer `W ≤ p - 1`, and a row at
distance `p^{26}` from a section edge agrees with the block row.

So 11, 24, 26, 26 and 6 apply to every such Schur complement. Replacing
`10 p^2` by `16 p^2 - 1` does not: at `p = 2` that ceiling squares to
`3969 > 2048 = 2^{11}`.

## Proof

Write `δ` for the margin. The hypothesis gives, on the original matrix,
margin `1 - off-sum ≥ δ` and absolute row sum `1 + off-sum ≤ 2 - δ`. The
same holds for columns. Proceed by eliminating one index at a time. The
active diagonal `d` and off-sum `o` of a remaining row satisfy `d - o ≥ δ`,
and the active absolute row sum `d + o` is at most `2 - δ`. The pivot
diagonal `a` satisfies `a ≥ δ`, so it is not zero. A coupling entry has
absolute value `c`, and the pivot row has off-sum `o1 ≤ a - δ`.

The new row is the old row minus `c/a` times the pivot row. The triangle
inequality produces a lower bound `L` for the new margin and an upper bound
`U` for the new absolute row sum:

```text
a L = a d - a (o - c) - c o1 = a (d - o) + c (a - o1),
a U = a (d + o) + c (o1 - a).
```

The first right-hand side is at least `a δ`, so `L ≥ δ`. The second says
`U = (d + o) - c (a - o1) / a ≤ d + o`. Thus the new margin is at least `δ`
and the new absolute row sum is at most the old one, hence at most `2 - δ`.
Columns are the rows of the transpose, so the same two identities apply to
them. After the whole set has been eliminated, the active matrix is the
block Schur complement `D - C A^{-1} B`.

The bound `||S^{-1}||_∞ ≤ 1/δ` is the one-row estimate: if `S y = x` and
`|y_k|` is maximal, the margin at `k` multiplies `|y_k|` by at most `||x||_∞`.
The same estimate on `S^*` bounds the 1-norm. Therefore both inverse norms
are at most `10 p^2`, and the 2-norm is at most `10 p^2`. Absolute row and
column sums at most `2 - δ` give `||S||_2 < 2`.

The eigenvalues of `S^* S` are then strictly larger than `p^{-11}` and
strictly smaller than 4. Indeed `(10 p^2)^2 = 100 p^4`, and `100 < p^7` for
every integer `p ≥ 2` because the minimum is `128` at `p = 2`. Also
`4 < p^{11}`. The matrix `Q = I - p^{-11} S^* S` has spectrum in
`[0, 1 - p^{-22})`. The length `p^{24}` contributes `p^2`. The length
`p^{23}` contributes only `p`. The scalar step is strict because `1/2! < 1`.
The normalizer 6 is legal because `10 p^2 < p^6`, while `10 p^2 > p^5` at
`p = 2`, so 5 fails. The bandwidth identity is the same one used for the
within-cell block:

```text
p^{26} - (2 p^{24} - 1)(p - 1) = p^{24} ((p - 1)^2 + 1) + p - 1 > 0.
```

At `p = 2` the loose radius equals `p^{25} + 1`. For every integer `p ≥ 3`
the sharp radius at `W = p - 1` exceeds `p^{25}`.

#4462's robust margin `(4p - 1)/(32 p^3)` is at least `7/(64 p^2)`, and
`7/64 > 1/10`, so that margin is at least `δ`. Those matrices meet the
hypothesis of this lemma. This package does not reprove the robust margin.

| Role | With margin `1/(16 p^2 - 1)` | With margin `1/(10 p^2)` |
| --- | --- | --- |
| Inverse ceiling | `16 p^2 - 1` | `10 p^2` |
| Spectral endpoint on the Schur complement | 12, because `63^2 > 2^{11}` | 11 |
| Series, bandwidth, agreement, normalizer | 26, 28, 28, 6 | 24, 26, 26, 6 |

## Not covered

- A proof that the ideal gaps exceed `1/(8 p^2)` for every prime.
- The core side `L = 2^{ceil(400 log2 p)}`. Agreement distance 26 does not
  by itself replace that choice.
- The broad matrix. HALO still applies `S` and does not invert it.
- Any new κ. The #4100 notes keep their written gap, `p^{10}`, and `A = p^{48}`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-schur-gap --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-schur-gap
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-22, from the snapshot fetched at 00:40 UTC, matched this
draft, PR #4462, and the unrelated width-2 note
`research/gaussian-origin-displayed`. #4462 asks for this elimination step
and does not take it. No other open pull request assigns the margin
`1/(10 p^2)` to a Schur complement. A search miss is not a novelty
certificate. #4452 is the within-cell δ ceiling.

## Open next questions

1. **Can the core side exponent 400 fall?** Every Schur complement now has
   the same inverse ceiling `10 p^2`, and the agreement distance on the
   halo polynomial is `p^{26}`. HALO still chooses `L ≥ p^{400}` against
   `A = p^{48}`. The first step is to substitute `A = p^{26}` into the two
   sparse powers and name the smallest uniform integer that keeps both
   negative whenever the group exponents are strictly less than 1.

## Credit

- The elimination sentence and the written core side are #4100's.
- The inverse-ceiling `10 p^2`, and this question, are Ryanson Jonathan's #4462.
- The exponent route is #4452. The across-cell contract it used is Mihir S's #4449.
- The sharp bandwidth radius is Nick Petalas's halo audit, PR #4217.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
