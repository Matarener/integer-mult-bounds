# Complete sharp-price region in the frozen ideal

All statements here use the fixed exponent
`a = 1730578437266246818741/10^24` and `h(l)=l^(1-a)`, with `h(0)=0`.
This is the upper endpoint used by Erwan Secousses in PR3815 and Sagar Thakrar
in PR3862. It is not a new root enclosure or a new kappa.

## Model and exact dual face

Per owner replica, demands for widths `(4,5,6,7,8,9)` are
`(234,18,162,477,864,1917)` and bin counts for capacities `(8,16,32,48)` are
`(672,448,448,448)`. Each helper fits wholly in one bin; the remainder is
paid as one child. Counts may be fractional. No clock, per-call collision,
restoration or physical staging condition is imposed in this relaxation.

The objective is the sum of `h(remainder)` over all bins. The local paid
profile and live normalizer stay outside this objective and must be added
when pricing any real change. The model is retained from PR3815, following
dataisfire's PR3734 and zxv's PR3682.

The ten columns of `MODEL.json` form an invertible matrix A: six helper
count rows followed by four bin count rows. The basis dual is the unique
solution `A^T lambda = h(remainders)`. Its closed form is independently
reconstructed in `independent.py`. Equivalently, with helper prices pi:

```
pi9 = (h(3)-h(48))/5
pi8 = (3*pi9-h(5))/4
pi7 = 2*pi8-pi9; pi6 = 3*pi8-2*pi9
pi5 = -h(5); pi4 = 1-h(5)
mu8 = -pi8; mu16 = -2*pi8; mu32 = -4*pi8; mu48 = h(48)
```

For every feasible pattern p in a bin c its reduced cost is
`h(c-w.p)-pi.p-mu_c`. Both checkers enumerate all 2,551 integer count
patterns of widths 4..9 in these bins. Exactly twelve have identically zero
symbolic reduced cost: the ten basis columns plus `[8,8]@16` and
`[8,8,8,8]@32`. Every other pattern has a strictly positive outward rational
lower bound at this fixed exponent (minimum exceeds 0.0040545). This proves
both dual feasibility and completeness of this tight face. The check uses
symbolic identities for the zero cases, never a floating tolerance.

PR3815/3862 solve a dual for outward rational lower approximations to h.
Here the symbolic dual uses the exact function h and interval arithmetic
certifies its inequalities. Its prices are consistent with their enclosures;
we do not claim bit-identical rational proxy prices or re-certify their root.

The primary checker uses rational matrix elimination, Cartesian count-vector
enumeration and alternating negative-exponential bounds. The second uses
closed-form dual coordinates, ascending multisets and positive exponential
series followed by reciprocals. Neither imports or executes predecessor
code or the other checker. Logarithms use reduced atanh series with explicit
geometric tails; all rounding is outward. No numerical optimizer is needed.

By weak duality, the common dual gives a lower bound for every packing of
any changed inventory with these bins. Equality occurs exactly when all
positive-count patterns belong to these twelve. Therefore feasibility on this
face is necessary and sufficient for the common price to be attained.

## Eliminate the two extra columns

For a changed demand vector d, let `y=A^-1(d,B)`. The extra `[8,8]@16`
column has basis coordinates `(0,1,0,0,0,1,0,-1,0,0)` and the extra
`[8,8,8,8]@32` column has coordinates `(0,0,0,0,0,2,0,-1,0,0)`.
If their counts are z1,z2, the basic counts are `y-D1*z1-D2*z2`.
All y coordinates except indices 1,5,7 must be nonnegative. The remaining
conditions are

```
z1,z2 >= 0; z1 <= y1; z1+2*z2 <= y5; y7+z1+z2 >= 0.
```

They are feasible exactly when
`y1>=0`, `y5>=0`, `y7+y5>=0`, `2*y7+y1+y5>=0`.
For sufficiency put `L=max(0,-y7)`, `z1=min(L,y1)`, `z2=L-z1`.
The last two inequalities respectively give `L<=y5` and `2L<=y1+y5`,
which imply `z1+2*z2<=y5`. This supplies an explicit rational packing.
Necessity follows by adding the displayed inequalities. The independent
checker eliminates the same face in a different set of direct count variables.

## Joint adjacent inventory flows

Let xj be the nonnegative number of helper-calls moved from width j to j-1,
for j=5,6,7,8,9, per owner replica. These are net inventory flows; if a literal
rewrite can touch each original helper only once it has additional availability
constraints. In particular x5<=18 must then be imposed separately.

The changed demands are

```
(234+x5, 18-x5+x6, 162-x6+x7, 477-x7+x8, 864-x8+x9, 1917-x9).
```

Writing `S=x6+x7+x8+x9`, exact matrix elimination gives

```
y0=672; y1=448; y2=234+x5; y3=162-x6+x7; y4=18-x5+x6
y5=15+(x6-x7-x8+x9)/2; y6=12-S/4
y7=7-S/4+x8; y8=1916/5+S/20; y9=324/5-S/20.
```

Substituting into the previous feasibility conditions gives exactly

```
S <= 48
x5 <= 18+x6
x7+x8 <= 30+x6+x9
3*x7 <= 88+x6+x8+x9.
```

All flows must also be nonnegative. There are no hidden additional inequalities:
the first makes y3>=114, y8>0, y9>=312/5, and
`2*y7+y1+y5=477-x7+x8>=429`. Other nontrivial conditions are exactly the
four displayed ones. The constructive formula above proves sufficiency for
every rational point, not merely the finite comparison grid. The argument
extends to real counts in the same fractional relaxation.

If V0 is the incumbent idle cost and
`q=(h(48)-h(3)-5*h(5))/20`, throughout this region

`V(d)-V0 = x5 + (x6+x7+x8+x9)*q`.

Outside it no packing attains that common-dual value. The value remains a
lower bound; the model itself may also be infeasible for extreme inventories.
This is not a claim that PR3862 asserted simultaneous exactness outside its
ranges. Its single-basis ranges and global lower bound remain valid.

## Sharp axial ranges and integral controls

Setting all other flows to zero gives maximal xj:

| Move | PR3862 sufficient single-basis range | Complete tight-face range |
|---|---:|---:|
| 5 to 4 | 18 | 18 |
| 6 to 5 | 28 | 48 |
| 7 to 6 | 28 | 88/3 |
| 8 to 7 | 30 | 30 |
| 9 to 8 | 28 | 48 |

Each upper endpoint is attained by a nonnegative rational packing in
`RESULT.json`; each is forced by one of the joint inequalities, so it is
sharp for this price. At T360 all five endpoint witnesses have integer
aggregate helper and bin counts. This checks integrality of the clock-free
aggregate only, not a chronological owner assignment or per-call matching.

## An actual coupled counterexample and a strict gap

Take x6=x7=28, all other flows zero. Each change lies within the old individual
range, but S=56 and y6=-2. Since row 6 of A^-1 is nonnegative on every tight
column, this separates the changed demand from the whole twelve-column face.
An explicit feasible packing nevertheless exists: in 28 original
`[6,8,9,9]@32` bins shrink the 6 to 5, and in 28 `[7,9]@16` bins shrink
the 7 to 6. Both new remainders are 1. The resulting rational pattern counts
and all ten conservation equations are checked exactly; T360 clears them.

Let delta be the certified minimum strictly positive reduced cost and M the
maximum negative magnitude of row 6 on any of the 2,551 columns. The row sum
-2 forces at least 2/M units of non-tight patterns. Consequently every feasible
packing has idle cost at least `common_dual + 2*delta/M`, strictly above the
putative linear price. `RESULT.json` supplies exact delta, M and this gap.
Thus the rejection is an objective obstruction, not a failed packing search.

## Limits

Only widths 4..9, fixed bins, fixed exponent and the paid-remainder objective
are certified. No all-concave or all-exponent optimality is asserted. Actual
staging signatures, circuit identities, dirty restoration, stock, source
access, chronology, collision rules, native/recursive invoices and both
supplier caps require their own admission. No full multiplication theorem,
formal proof-kernel check, selected-frontier change or new kappa is claimed.
