# A middle interval raises Schur bandwidth to at most 2b-1

A prefix pivot keeps bandwidth at most `b`. An interval with survivors on
both sides does not. Its complement has bandwidth at most `2b-1`, and the
bandwidth-2 witness meets that cap.

No new kappa is claimed. Boundary order and the Gaussian tail are not
decided here.

## The two-sided count

Let `H` vanish for `|i-j|>b`, and let the pivot be the contiguous interval
`{L,...,R}`, with an invertible block and at least one survivor. Survivors
to the left of `L` and to the right of `R` stay in that order, with the
gap closed.

The pivot block's inverse may be dense, so the update can fill every pair
of survivors that each meet the interval. A survivor meets the interval
only from the rim `[L-b, L)` or `(R, R+b]`.

Two survivors on the same side of the interval both lie in a rim of length
`b`, so they are at most `b-1` apart. The gap is not between them, and
their new distance is unchanged. A copied entry of `H` is already at
distance at most `b`.

A left survivor `u` and a right survivor `v` in those rims satisfy
`v-u <= R-L+2b`. Closing a gap of `R-L+1` indices leaves new distance
`v-u-(R-L+1) <= 2b-1`. If one side of the interval is empty, there is no
cross term and the bandwidth is at most `b`, which is the prefix case.

## The witness

On the 7 by 7 matrix with `b=2` and `||E||_infinity=1/2`, every proper
interval has Schur bandwidth at most 3, and every one-sided interval stays
within 2. The same cap holds for a generic in-band matrix with distinct
reciprocal entries. Every symmetric complement's inverse equals the
complementary block of `H^{-1}`.

Eliminating `{2,3,4}` leaves survivors `{0,1,5,6}` and bandwidth 3, which
is `2b-1`. The entry between 0 and 6 is `-1/432`. Row scaling leaves the
off-diagonal infinity norm at `37/208`, still below `1/2`, with bandwidth
3. The inverse has both induced norms equal to `488/389`, inside the
original Neumann bounds `2` and `10`.

The bound is sharp on this matrix: the same cap is attained, so a later
step cannot replace `2b-1` by `b` for every middle interval.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/schur-interval-bandwidth/verify.py
python3 -B scripts/research_package.py --package research/schur-interval-bandwidth
```

The verifier authenticates the pinned note, checks every proper interval
of both hosts, and checks the `{2,3,4}` complement against the block
identity and the original bounds.

## Open next questions

The Gaussian caller claims bandwidth `O(W)` after the survivors are placed
in boundary order. These intervals stay in the original order.

A circular band has no prefix. The rim count above uses a linear interval
with two ends.

## Credit

Cinna Davis wrote the Schur paragraph in the PR4100 narrow Neumann note.
The prefix bound is the preceding two-index audit. The two-sided cap and
the interval `{2,3,4}` are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
