# A filled Schur complement keeps the inverse bound and loses bandwidth

The narrow Neumann note says that the inverse bounds pass to a Schur
complement because the complementary block of the inverse is the inverse
of that complement. It does not say that the complement is still a band
of width `b`. One explicit elimination separates those two claims.

No new kappa is claimed. This does not establish the Gaussian tail, the
`p^10` hypotheses, or a block elimination in boundary order.

## Witness

Take the 7 by 7 matrix `H=I-E` with bandwidth `b=2` and
`||E||_infinity=1/2`. Off-diagonal entries at distance 1 or 2 equal `-1/8`.
Eliminate index 3. The complementary Schur matrix `S` is the 6 by 6 update

```
S[i,j] = H[i,j] - H[i,3] H[3,j]
```

on the surviving indices `{0,1,2,4,5,6}`. Original indices 1 and 5 are not
within bandwidth 2, so `H[1,5]=0`. Both meet index 3, and

```
S = -(-1/8)(-1/8) = -1/64
```

at that pair. In the surviving order those rows are three apart, so `S`
has bandwidth 3. The diagonal of `S` is not identically 1: four diagonal
entries equal `63/64`.

Row scaling `R[i,j]=S[i,j]/S[i,i]` restores a unit diagonal. Its
off-diagonal infinity norm is `3/7`, still below `1/2`, and its bandwidth
is still 3. The original width `b=2` is not a hypothesis of `S` or of `R`.

## What still holds

For this scalar pivot, `S^{-1}` equals the complementary principal block
of `H^{-1}`. Both induced norms of that block are `648/389`. The Neumann
bounds at `b=2` and `rho=1/2` are `2` and `10`, and both norms of the
block are at most the corresponding norms of `H^{-1}`. The inverse bound
survives. It survives because of this block identity, not because `S` is
still a band of width 2.

A later step that reapplies the bandwidth-`b` support count to this filled
complement is using a hypothesis this matrix does not satisfy.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/schur-bandwidth-gap/verify.py
python3 -B scripts/research_package.py --package research/schur-bandwidth-gap
```

The verifier authenticates the pinned note, builds this elimination in
exact arithmetic, and checks the bandwidth, the row-scaled norm, the block
identity, and the comparison with the original Neumann bounds.

## Open next questions

The Gaussian caller says that eliminating interiors leaves a Schur matrix
of bandwidth `O(W)` after the survivors are put in boundary order. This
witness uses the original order and one scalar pivot. It does not decide
that boundary-order claim.

A block pivot, rather than this single index, can create a different fill
pattern. The same separation has not been checked for a pivot larger than
one.

## Credit

Cinna Davis wrote the Schur paragraph in the PR4100 narrow Neumann note.
The block identity used here is the standard one-pivot Schur formula. The
witness that separates bandwidth from the inverse bound is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
