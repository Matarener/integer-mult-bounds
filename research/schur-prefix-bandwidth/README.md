# A prefix pivot keeps bandwidth, and an interior pair does not

Eliminating one index of the bandwidth-2 witness can raise the Schur
bandwidth. A two-index pivot does not do so for every choice of indices.
Every invertible prefix does keep bandwidth at most `b`. An adjacent
interior pair, and a split pair, do not.

No new kappa is claimed. Boundary order and the Gaussian tail are not
decided here.

## Prefixes

Let `H` vanish outside bandwidth `b`, and suppose the leading principal
block on `{0,...,r-1}` is invertible. The survivors are the contiguous
suffix `{r,...,n-1}`, so distances among them are unchanged.

A survivor `u >= r+b` has no nonzero entry into the prefix: every prefix
index is at least `b+1` away. The Schur update in that row is zero, and
likewise for a column. An entry with either index outside the window
`[r, r+b)` is therefore copied from `H`, which is already zero past
bandwidth `b`. Both indices inside that window are at most `b-1` apart, so
a filled entry there still lies inside bandwidth `b`. The complement has
bandwidth at most `b`.

On the 7 by 7 witness with `b=2` and `||E||_infinity=1/2`, every prefix
length from 1 through 6 satisfies this. The same holds for a generic
in-band matrix whose nonzero entries are distinct reciprocals. The length-2
prefix is the endpoint pair `{0,1}`: bandwidth stays 2, and row scaling
leaves the off-diagonal infinity norm equal to `1/2`.

## Interior pairs

Eliminating `{2,3}` is not a prefix. The survivors are `{0,1,4,5,6}`.
Original indices 0 and 5 are three apart in that order, and the complement
has entry `-1/504` there, so the bandwidth is 3. Row scaling leaves the
off-diagonal infinity norm at `1/3`.

Eliminating the split pair `{2,4}` leaves survivors `{0,1,3,5,6}` and
bandwidth 4. The entry between original indices 0 and 6 is `-1/504`, at
distance 4.

In all three cases the inverse of the complement equals the complementary
block of `H^{-1}`. Its induced norms are `42152/23729` for the endpoint
pair, `35536/23729` for `{2,3}`, and `585/389` for `{2,4}`. Each is inside
the original Neumann bounds `2` and `10`. The inverse bound does not
require the complement to keep bandwidth `b`. The bandwidth count does.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/schur-prefix-bandwidth/verify.py
python3 -B scripts/research_package.py --package research/schur-prefix-bandwidth
```

The verifier authenticates the pinned note, checks every prefix of both
hosts, and checks the three exact complements against the block identity
and the original bounds.

## Open next questions

The Gaussian caller claims that interior elimination leaves bandwidth
`O(W)` after the survivors are reordered to the boundary. These witnesses
use the original order.

The prefix argument uses a contiguous leading block on a line. A circular
band, or a pivot that is an arbitrary interval in the middle, needs a
separate count.

## Credit

Cinna Davis wrote the Schur paragraph in the PR4100 narrow Neumann note.
The one-pivot separation is the preceding witness. The prefix argument and
the two-index comparisons are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
