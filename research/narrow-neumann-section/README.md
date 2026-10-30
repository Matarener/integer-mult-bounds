# Periodic sections of the narrow Neumann bound

PR4100's narrow Gaussian reference quotes a banded Neumann lemma and then
uses it on periodic axes and on finite sections. The written lemma proves
the linear-band case. Its compression sentence does not prove the periodic
case. The arc count below does, and the caller's `p^10` comparison follows
from the stated numerical hypotheses for every integer `p>=2`.

No new kappa is claimed. The Gaussian tail, truncation, rounding, and the
broad shifted inverse are not re-proved here. Those hypotheses stay assumptions
of the plug-in.

## The linear bound

Let `E` be an `N` by `N` matrix with `E[i,j]=0` whenever `|i-j|>b`, and
`||E||_infinity <= rho < 1`. Put `delta=1-rho` and `H=I-E`. Then

```
||H^-1||_infinity <= 1/delta,
||H^-1||_1 <= 1/delta + 2 b rho/delta^2,
||H^-1||_2 <= sqrt((1/delta)(1/delta + 2 b rho/delta^2)).
```

Submultiplicativity gives `||E^k||_infinity <= rho^k`, so every entry of
`E^k` is at most `rho^k`. The product of two banded matrices adds bandwidth,
so `E^k` has bandwidth at most `kb` and each column has at most `2kb+1`
nonzeros. Hence `||E^k||_1 <= (2kb+1) rho^k`. The geometric sums
`sum rho^k = 1/delta` and `sum k rho^k = rho/delta^2` give the first two
bounds. The third is `||M||_2^2 <= ||M||_1 ||M||_infinity`.

The factor `2b` is the support count, not a spare constant. One column with
`2b+1` entries equal to `rho`, and no other entries in those rows, has
infinity norm `rho`, bandwidth `b`, and 1-norm `(2b+1) rho`.

A row gap without a bandwidth cap does not give an `N`-independent 1-norm
bound. The first column `(0, rho, ..., rho)` has infinity norm `rho` and
square zero, and `||(I-E)^-1||_1 = 1+(N-1)rho`. At `N=12` and `rho=1/2`
this is `13/2`, larger than both `1/delta=2` and the `b=1` formula `6`.

## Periodic axes and finite sections

Index a circle of length `N`. Suppose `E[i,j]=0` when the circular distance
exceeds `w`, and `||E||_infinity <= rho < 1`. For an arbitrary index set
`S`, let `F` be the corresponding principal submatrix. Row sums only drop,
so `||F||_infinity <= rho` and every entry of `F^k` is at most `rho^k`.

A nonzero entry of `F^k` is a walk of `k` steps in the induced subgraph.
Each step moves at most `w` places on the circle, so the endpoints lie in
a circular arc of radius `kw`. That arc contains at most `2kw+1` ambient
indices and therefore at most `2kw+1` selected indices. The same column
count as in the linear case follows, and the three norm bounds follow with
`b` replaced by `w`. They hold for every principal section, not only for
contiguous blocks.

The note's compression sentence does not supply this. On a line, passing
to a principal submatrix cannot increase bandwidth. On a circle it can.
For `N=8` and `w=1`, the section on `{0,1,7}` has induced linear bandwidth
`2`, because the circular neighbors `0` and `7` become the two ends. The
norm bound still holds, by the arc count rather than by compression.

A simultaneous permutation of rows and columns preserves the induced 1-norm
and infinity norm, hence the 2-norm bound. The caller's permutation
similarity between the augmented matrix and `H` direct-sum `I` can use that
invariance once `H` itself satisfies the hypotheses.

## The stated `p^10` comparison

Assume the caller's numerical hypotheses and nothing further: the row gap
is at least `1/(16p^2)`, the bandwidth is an integer strictly less than
`p`, and the row norm is strictly less than `2`. For every integer `p>=2`,

```
||H^-1||_2^2 <= (16 p^2 + 512 (p-1) p^4) 16 p^2 < p^20,
||H||_2^2 < 4 (2p-1) <= p^20.
```

The first product is checked directly through `p=400`. For `p>=3` it is
at most `8192 p^7`, and `8192 p < p^14`. Both square roots are therefore
strictly less than `p^10`. This is the comparison the caller calls
"eventually." It does not prove that the narrow reference actually has
this gap or this bandwidth.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/narrow-neumann-section/verify.py
python3 -B scripts/research_package.py --package research/narrow-neumann-section
```

The verifier authenticates the pinned note and caller, checks the geometric
sums, linear support through power 4, one saturated column, the
bandwidth-free column at `N=12`, every principal section of the length-8
width-1 circle and the length-7 width-2 circle, permutation invariance, and
the `p^10` arithmetic.

## Open next questions

The norm bound now covers the periodic sections the caller names. The row
gap `delta>=1/(16p^2)` and the bandwidth after truncation and rounding are
still the Gaussian tail argument, which this package does not audit.

The note also says that iterated Schur complements inherit the inverse
bounds when each intermediate is a Schur complement of one original
principal section. That identity is separate from the bandwidth count. A
later step that reapplies bandwidth `b` to a filled Schur complement is
not justified by either argument.

## Credit

Cinna Davis wrote the narrow Neumann note and the Gaussian caller in PR4100.
The geometric series and the banded support count are classical. The arc
count for circular sections, the compression distinction, and the all-`p>=2`
comparison are the audit recorded here.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
