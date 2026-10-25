# Arbitrary dual bridges in the nine-stage clock model

This is a scoped finite obstruction, with two written reductions. It changes
neither selected result nor supplier admission. The source word, entrance
and exit law, and the monotone one-flag architecture remain fixed.

## Model and exact boundary

There are four physical data pairs. Each pair has a top and a bottom scalar
register and one common clock. Clocks start at -1 and end at 8. Stage `s`
contains exactly one rank-one cross shear on a pair at clock `s-1`; that call
advances the pair to clock `s`. A forward call adds top to bottom and a reverse
call subtracts bottom from top.

At a common clock, any number of **dual bridges** is allowed, with no bound
on integer coefficients or word length. Their joint matrix is
`diag(A,A^(-transpose))`. This includes every bridge in the published B4
controllers. A nonzero idle advance changes one physical pair's clock. The
goal before the final signed exchange is a block antidiagonal scalar matrix.

The dimension of one clock step is 7 on the current BIT supplier and 8 on the
legitimate complex supplier. This follows from their existing entrance/exit
law: respectively `m=1+7*9=64` and `m=1+8*9=73`. The present analysis does not
change those projectors or reinterpret stored endpoints.

Independent primal and dual bridge matrices `diag(A,B)` are **outside the
completed orbit search**. They need not preserve the pairing used below.
The span lemma in the next section does cover such matrices. Controllers
with a different permutation, several pair-calls per stage, a different
clock law, cross-stage helper splitting, or changed local words are outside
the final economic ceiling unless separately reduced to this model.

## A dormant interval spans at most six of nine calls

First put the abstract controller in clock order. Every free bridge has the
common level of the pair it touches. Along a physical register the level is
monotone. Out-of-order operations at different levels therefore have disjoint
register support and can be interchanged. This puts all level-`j` free maps
between stages `j` and `j+1`, without changing the scalar product. An idle
jump of `Delta` levels then contains `Delta` cross-shear stages during which
that pair is untouched. This is an abstract necessary-condition reduction;
no claim is made that a native hosted program can be rescheduled for free.

Suppose a pair is untouched during at least seven of the nine calls. The
middle matrix fixes that physical pair and acts on its complement. In top /
bottom block notation its diagonal blocks `A,D` have positive rank, while
its off-diagonal blocks `B,C` have rank at most three. Arbitrary block
diagonal maps at its two ends preserve those four rank properties. At most
two cross shears remain outside the middle interval.

If there is one shear on each side, equal orientations leave one of `B,C`
rank deficient. Opposite orientations leave one of `A,D` unchanged: a lower
shear before and an upper shear after leave `D` unchanged; the other order
leaves `A` unchanged. Neither product can be block antidiagonal.

If both shears are after the interval, equal orientations again leave an
off-diagonal block rank deficient. For lower then upper, the lower shear
would have to make `D+SB=0` while `B` is rank deficient. This contradicts the
column rank four of the invertible matrix's last block column `(B,D)`.
For upper then lower, use the first block column `(A,C)`. Two shears before
the interval are excluded by inversion. Zero or one outside shear is a
special case of the same argument (insert an identity shear).

Thus every idle jump has `Delta<=6`. This argument uses invertibility and
block diagonality, not symplectic duality, coefficient bounds, or F2.

## Quotienting arbitrary equal-clock dual bridges

Reduce the integral scalar controller modulo two. Every integral elementary
dual bridge remains invertible; allowing the entire finite group
`GL(k,F2)` inside an equal-clock group is a relaxation. Failure in this
relaxation excludes every such integral controller.

A clock group of `k` physical pairs has a `k`-dimensional top row space `P`
and bottom row space `Q`. Their symplectic pairing is perfect. A dual bridge
changes a basis of `P` and applies its inverse transpose to the basis of `Q`.
Consequently the ordered spaces `(P,Q)` determine the complete orbit. The
search chooses the unique RREF basis of `P` and the unique dual basis in `Q`
as its canonical representative.

To split off one physical pair, choose nonzero `x in P` and `y in Q` with
pairing one. The remaining spaces are uniquely

`P' = P intersect y^perp`, `Q' = Q intersect x^perp`.

There are `(2^k-1)*2^(k-1)` such choices. This is an exhaustive replacement
for arbitrary-length bridge words, not a bounded list of bridges. An idle
transition moves the selected pair to any higher currently occupied clock
and merges its spaces into that group. A local transition changes `y` to
`y+x` or `x` to `x+y` and advances its clock by one.

Moving to an unoccupied intermediate level cannot help the scalar product:
there is no pair there with which to mix. Such moves can be combined with
the next move of the same pair. If a local needs a level, that level is
already occupied by the preceding stage's pair. These observations justify
using only currently occupied destinations in the idle closure.

## Rank pruning and exhaustive finite result

Let `Phi=rank(A)+rank(D)` be the sum of diagonal block ranks. It starts at
eight and ends at zero. A dual bridge preserves it, and one cross shear
changes only one diagonal block by a rank-one update, so it lowers `Phi` by
at most one. The first shear leaves both diagonal blocks equal to identity.
Thus each of the remaining eight calls must lower `Phi` by exactly one.
This is the published 2K+1 count floor, credited to Johnny Franks / the
archived report M and the recipe-floor formulation.

At the last local stage exactly one pair reaches clock eight. The other
three pairs each require one final idle advance. Therefore any controller
with at most nine idle segments has at most six before that final cleanup.
The search enumerates the complete idle closure with budget six before
each next rank-decreasing local, retaining the lowest idle count for each
canonical clock state. A higher count at the same state cannot improve any
future minimum. No bound on idle jump size is used in this run.

The completed K4 run has these frontier sizes:

| Stage just executed | Idle closure before stage | States after local |
|---|---:|---:|
| 1 | 58 | 625 |
| 2 | 3,489 | 19,281 |
| 3 | 63,809 | 103,656 |
| 4 | 295,288 | 512,232 |
| 5 | 1,213,716 | 618,744 |
| 6 | 1,038,492 | 531,468 |
| 7 | 698,208 | 71,960 |
| 8 | 84,224 | 12,264 |

Every final state has minimum pre-cleanup count six, hence total count nine.
The unchanged B4 recipe attains nine. K2 and K3 checks give three and six.
This is a finite computer-assisted result, not proof-assistant verification
or an independent second full K4 enumeration.

## BIT economics, allowing all controller partitions

The four pairs collectively advance 36 levels, nine through locals. Thus
the nonzero idle jumps sum to 27. With `Delta<=6`, a rank `7*Delta` slot
holds at most `Delta-1` whole width-eight helpers. There are 222 slot copies
per replica. For `n` idle segments, total capacity is `222*(27-n)`.
The unchanged word needs `9*437=3933` helpers, forcing `n<=9`. Combined with
the finite floor, every fully hosted controller in this class has exactly
nine segments.

There are 88 nondecreasing partitions of 27 into nine integers in 1..6.
`geometry_budget.py` ignores all stage eligibility and all physical-axis
constraints, pools every replica, and gives a rational packing dual for
each partition. At the test value 0.001740157, the least possible normalized
moment is strictly greater than one by more than 2.62e-9, even after dropping
all bad-branch fallback cost. Therefore the unchanged BIT word cannot reach
0.001740157 in this entire controller model, and cannot reach 0.001745.

The most favorable relaxed partition is `(1,1,1,1,1,4,6,6,6)`. Its hypothetical
idle remainder per replica is `{2:653.4,4:222,7:1110,42:12.6}`. The numerical
root near 0.0017401561948 is only an orientation aid; the rounded strict
rejection is the exact certificate. No physical controller with that
partition is asserted.

## Complex economics with its actual width inventory

The legitimate local complex profile has rank mass 5134, helper-width sum
3278, and width counts `{4:26,5:2,6:18,7:53,8:96,9:213}`. Each clock step is
rank eight, and there are 224 slot copies per replica. Thus its complete
local charge is nine copies of that profile, and its idle mass is
`8*27*224 - 9*3278 = 18882`. The productive family count is 896 and `m=73`.

For every rank `8*Delta` slot, enumerate every nonnegative integer helper
multiset of these six widths fitting the slot; the remaining dimension pays
one residual child. There are 3,663 patterns over the six slot capacities.
For each of the 88 partitions, a continuous packing program is only used to
propose six helper prices. Those prices are rounded to rationals; each slot
price is reset to the minimum allowed by **all** its integer patterns using
exact rational lower bounds on `r*(73/r)^a`. This explicitly constructs a
valid dual and does not rely on a numerical solver's optimality assertion.

More than nine segments cannot improve this relaxation. When `n>=10`, the
two smallest positive parts have sum at most six: otherwise the second
smallest is at least four, giving total at least 39. Merge those parts,
combine their packed helper multisets, and pay the sum of the two residual
ranks as one child. Concavity gives `f(r+s)<=f(r)+f(s)`, so the merge cannot
increase cost. Repeat until nine segments remain.

All 88 exact duals reject 0.001745, with minimum normalized excess greater
than 3.72865e-6. `COMPLEX-CLOCK-PACKING.json` retains all prices and margins.
The separate rounded upper test 0.001744 is also rejected by every dual,
with minimum excess greater than 9.13778e-7; its full receipt is
`COMPLEX-CLOCK-CEILING.json`.
The favorable fractional layout is `(1,1,1,2,2,3,5,6,6)`; it is a relaxation,
not a constructed controller. These calculations use the legitimate local
word and width inventory and do not import the disputed operator overlays.

## What this changes and what remains open

The preceding recipe search bounded one bridge per gap and scalar entries
by eight. The new finite floor removes both restrictions for integral dual
bridges. Its proof obligations are the stated orbit reduction and the
transparent exhaustive program, not a search over bounded coefficient lists.

The gap can still be addressed by changing the local word or helper widths,
changing the initial/final flag law, allowing split or interleaved helpers,
using a different pair permutation, or developing independent top and bottom
bridge networks. No impossibility claim is made for those constructions.
The exact width budget shows that six ideal width-seven helpers per BIT
call could suffice under known mixed-width hosting, but no such word is
constructed here.
