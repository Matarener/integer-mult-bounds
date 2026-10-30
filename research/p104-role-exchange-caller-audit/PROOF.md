# Fixed-location return and a bounded inverse-shear caller

## 1. The retained caller and the physical limit of this study

The concrete predecessor is the **two-stage complex bank-exchange caller** in
`notes/copied-centers-complex.tex`, section "Two-stage phase endpoint and its
paid correction". Its first forward shear and inverse second shear have the
scalar composition `(x,y) -> (-y,x+y)`. Its subsequent correction reads the
first output, applies `T^-1` to a paid copy, adds that copy to the second output,
and disposes of the copy. None of those later operations is donated here.
`scripts/copied_centers_network.py` records the separate paid endpoint child.

That is an actual retained caller, but its documented two-factor geometry is
not a supplied P104 global owner embedding. We bind the caller's **inverse
shear equation** and give an explicit conservative realization at the P104
post-channel cut. We do not substitute 104 for the caller's published triple
count, identify its two tensor axes for free, or claim that our local readout
is its complete second-stage physical implementation. This distinction is
essential to the stopping decision.

At this cut, let `R(u,w)=(u-w,w)`, with all 72 dirty helpers unchanged. A legal
common-chart realization lifts each required `Y_i` from `H_i` to FULL, performs
`X_i -= Y_i` while both are FULL, and returns `Y_i` to `H_i`. This realization
costs 104 unit Gaussian additions and 208 rank-one conversions. It preserves
all returned `w` values. This is an explicit local implementation of the
retained equation, not a free source read or an outer recursive admission.

For the source-preserving correction `S(x,y)=(x,x+y)`, the composed endpoint is
`R S(x,y)=(-y,x+y)`. Its return equations are `y=-X_out` and
`x=Y_out+X_out`; every arbitrary helper returns in its stated final chart.

## 2. PR3882's boundary and why relabelling fails

All algebra is over `D=Z[i,1/2]`, acting coordinatewise on arbitrary finite
arrays. Write `A=R_root^t R_root/8` in the pinned doubled-root port order.
For `J=[0,1,3,6,22,31,93,103]`, with complement N of size 96, the retained
geometry gives

```
A = [[I, B], [B^t, B^t B]],    nnz(B)=384,
```

where every nonzero B coefficient is a signed half. PR3882 returns

```
X_J=q=x_J+B x_N,       Y_J=w_J,
X_N=w_N,              Y_N=v_N=y_N+B^t q.
```

`X_J,Y_N` are FULL; `X_N,Y_J` have their port hyperplanes. The 72 inherited
dirty helpers remain FULL and logically restored. This is a changed location
and data contract. Even allowing a free logical gather into residual order
`r=(q,v_N)`, the naive inverse shear returns `(r-w,w)`, whose error from the
required `(-y,w)` is `r-x`. It is generally nonzero. The verifier includes
the explicit nonpivot one-source, zero-y witness; zero dirty values are valid
for this separating witness, while the positive endpoint replay includes all
280 independent input columns.

The residual-as-source error has rational rank exactly 104: its J rows are
`B x_N`, and `B B^t=12 I_8` proves their rank eight. Its N rows additionally
contain the 96 independent `y_N` coordinates with identity coefficient.
Thus the N rows are independent modulo the J rows. This is a logical
incompatibility statement, not a transport or recursive-cost lower bound.

PR3882's inverse equations already recover x from `(w,q,v_N)`; those equations
and its sharp eight-replacement theorem are credited predecessor results.
The new result below is a literal return schedule and its sharp **fixed
physical-location** frame tariff. It is not a new residual-minimality theorem.

## 3. A sharp 192-rank fixed-location restoration adapter

Demand the same physical source and target locations as PR3894: X contains x
in FULL, Y contains w in `H_i`, and all helpers retain their values and frames.
Lift each `X_N` to FULL. In chronological order perform

```
Y_N -= X_N                       # v_N-w_N
Y_N -= B^t X_J                   # -x_N
X_J += B Y_N                     # x_J
for each i in N:
    X_i -= Y_i                   # w_i+x_i
    Y_i += X_i                   # w_i
    X_i -= Y_i                   # x_i
```

Then descend `Y_N` to its target hyperplanes. The other eight sums `Y_J` and
the dirty helpers are untouched. Every scalar source and target is FULL.
No payload swap, sign operation, clean bank or private erasure is hidden in
the three displayed unit additions. The explicit schedule uses 1,152 unit
Gaussian ADD/SUBs, 104 halves and 104 restoring doubles, 96 lifts and 96
descents. It contains 1,552 formal events.

For each fixed physical register, the sum of absolute frame-dimension changes
is at least the absolute difference of its final and initial dimensions.
Here 96 X registers must go from dimension eight to nine, and 96 Y registers
must go from nine to eight. Thus **192 added rank units are necessary** under
the inherited nested dimension-gap tariff. The construction attains 192.
This bound permits arbitrary scalar resynthesis; it does not permit free
physical role renaming, changing the required return locations, or replacing
the caller's frame contract. It is not a scalar-operation or universal decoder
lower bound. Additional temporary banks cannot remove the fixed registers'
required endpoint dimension changes without changing this model.

Consequently the literal PR3882 tail followed by this fixed-location adapter
has 400 added H1 conversions above the original channel, versus PR3894's 208.
The inherited channel mass is 2,368, so the respective totals are 2,768 and
2,576 before the next reader. Appending the separate inverse reader gives
2,976 and 2,784. These are constructive local invoices and a scoped adapter
minimum, not optimum complete caller costs.

## 4. Fuse the return instead of paying an intermediate encoded boundary

At the original channel exit X=x, Y=v=y+A x. Lift all 104 Y fields to FULL.
Use the eight original source pivots as temporary accumulators:

```
X_J += B X_N
Y_J -= B X_N
Y_N -= B^t X_J
X_J -= B X_N
Y_N += X_N
```

After the first two operations, `X_J=q` and `Y_J=w_J`. The third gives
`Y_N=v_N-B^t q=y_N`. The fourth restores the original `x_J`; the last gives
`Y_N=w_N`. Every `X_N` source is unchanged. The result is exactly S, including
all source, target and helper rows, so a caller which accepts PR3894's physical
endpoint accepts the same endpoint here **conditional on the same native
chart semantics**. The derivation uses the same source-pivot geometry as
PR3882; source-consuming and in-place pivot ideas are credited, not invented.

There are four B traversals and 96 direct additions: `4*384+96=1632` unit
Gaussian ADD/SUBs. For a literal dyadic lowering, each of the two X_N gather
passes halves and restores each of 96 donors; the scatter halves and restores
eight pivots. Thus there are 200 halves and 200 doubles. The final 104 Y
descents and initial 104 lifts give exactly the same **208 H1** profile as
PR3894. This source-preserving suffix contains 2,240 formal events.

To consume S with the bounded inverse reader, perform all `X_i -= Y_i`
**before** the Y descents. The result is `(-y,w)` with 1,736 unit additions,
200 halves, 200 doubles and 208 conversions: 2,344 suffix events. No X source
is consumed until every corrected Y sum exists. This chronology matters.

For a fair control, retime PR3894's direct correction into the same all-Y-FULL
window. Halve each of the 104 original X sources once, apply its 4,992 signed
unit correction additions, restore every X by doubling, then perform the same
104 inverse-reader additions and descend Y. This uses 5,096 unit additions,
104 halves, 104 doubles and the same 208 conversions: 5,512 suffix events.
The new scalar schedule saves 3,360 unit additions but adds 96 halves and 96
doubles. A separate copy/cleanup operation, less precision, faster runtime or
lower recursive-child profile does not follow from the addition count.

At 512 complex words, multiply a Gaussian array addition/halving/doubling by
1,024 real component operations. The exact real-addition saving is 3,440,640;
each extra halving/doubling category has 98,304 real component operations.

The normalized scalar prefixes have sharp maximum coefficient denominator
four in the pivot schedule and two in the retimed baseline; both have maximum
row one-norm 26 including their channel-exit entrance. The direct bound is
`26H` per computed data component when original normalized x,y components are
bounded by H. Untouched helpers retain their own input bounds. These are
**tail-only common-chart** certificates. The original channel
interior, physical native entrance, literal signed-floor divisibility, native
scratch, accumulated rounding and all-depth numerical formats are not proved.

The all-Y-FULL schedules have 2,520 persistent frame coordinates at peak,
including 72 FULL dirty helpers; PR3894's target-major suffix peaks at 2,417.
The receipt also records after-event frame-coordinate sums with an explicit
convention. These finite occupancy diagnostics omit native internal scratch
and are not a recursive owner/idle tariff.

## 5. Complete-cost decision and precise exclusions

Retiming either baseline or pivot suffix into the reader window leaves the
profile `(1282,58,86,104,48,24,8,8)` and mass 2,576. The unchanged local
width-nine, 280-role bare screen is `2576/2520=46/45>1`. Every positive child
rank is at most nine, so for `0<=a<1`, `(r/9)^(1-a)>=r/9`. Nonnegative omitted
costs cannot rescue this particular unchanged-interface screen. This is not a
universal obstruction to a caller with a different coverage law.

For the retained **source-preserving nine-call paired-chain template**, use
width 73, 832 families, one unpaid coordinate per live family, 2,312 persistent
progress units per local call, and no extra progress from the closed terminal
excursion. The remaining collective correction/helper/residual/idle coverage
is `72*832-9*2312=39096`. The favorable whole rank bill for the unchanged
profile is therefore

```
9*2576 + 39096 = 62280 > 60736 = 73*832,
M(0) >= 7785/7592 > 1.
```

This is the inherited complete-coverage rejection, now applied to an explicit
source-preserving resynthesis of the role-exchange idea. It is not a new
coverage theorem and does not transplant the separate PR3609/3620 dual's
425/426 threshold or six/seven/six format. Fully paid auxiliary banks add 73
to both coverage and capacity, preserving the positive 1,544-rank deficit for
every finite number. The already charged terminal mass is not subtracted from
idle coverage as a free credit.

The complete **physical** price retains native wrappers/arithmetic, inherited
private COPY/disposal, source availability, original and changed bank owners,
all holding/routing/address/control work, actual numerical formats, paid
endpoint copy/correction/cleanup, recursive backend, all-size transfer and
the outer caller's actual coverage law. Those quantities are unknown or
inherited as stated, not zero. The rejection uses a favorable lower bound,
so no additional implementation is needed to reject this unchanged budget.

Decision **NARROW**: retain the exact fixed-location adapter, its sharp tariff,
the all-input caller-cut compositions, the scalar resynthesis and the fair
baseline comparison. No native expansion or supplier claim is justified.
The older 1,352-add chronological snapshot correction and 2,376-add dirty-root
factorization remain credited alternatives; this is not a record for all
source-preserving correction words. All native recipes, global ownership,
physical caller adoption, formal-kernel acceptance and independent human
review remain separate.
