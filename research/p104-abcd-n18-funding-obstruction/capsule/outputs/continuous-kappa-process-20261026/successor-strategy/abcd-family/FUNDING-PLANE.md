# Joint raw-price and tail-price gate for every signed ABCD profile

Status: **paper dual with pinned input hypotheses; not root-qualified**.
This note keeps the original n=18 caller, cutoff 17, floor 18, offset 1/5
and tail decay .97. It does not change the compiler route. It extends the
full-witness failures in `PROOF-AND-BUDGET.md` to all nonnegative real
profiles reachable in the signed ABCD affine relaxation, including partial
mixtures and reverse exchanges.

At both C=.0033 and C=.0033000005, a rational dual separates the necessary
raw and gamma inequalities, conditional on the pinned current B18 bound
and the very weak source input `gamma(.0030818905)>.965`. The captured
author interval is stronger, but this worker has not independently
validated that source moment interval. Root must qualify the source input
(or directly bound the goal-point headroom) before promoting this result.
No moment engine, numerical optimizer, constructor, native calculation or
contact search was executed here.

## The signed affine closure is exactly a four-dimensional simplex

The four exchange vectors on paid ranks 1 through 6 preserve two quantities:

```
sum(r*p_r, r=1..6) = 5915,
p1+p2+p3+p4+p5+2p6 = 3458.
```

Paid rank seven stays p7=14, and all targets/nonlocal terms stay fixed.
These invariants are sufficient for membership in the real signed affine
closure. Indeed recover the unique signed exchange counts by

```
a = p6-18,
c = p5+p6-182,
d = p4+p5+p6-276,
b = p3+2p4+2p5+2p6-1046.
```

Substitution gives the remaining two coordinates

```
p1 = 1001+p3+2p4+3p5+2p6,
p2 = 2457-2p3-3p4-4p5-4p6.
```

Thus nonnegative profiles are precisely

```
p3,p4,p5,p6 >= 0,
2p3+3p4+4p5+4p6 <= 2457.
```

Here p1 is automatically at least 1001. This explicit inverse proves that
the four exchange vectors span the full invariant affine plane, without
assuming forward realizability of the recovered signed counts.

The five vertices, listing only nonzero ranks 1 through 6, are

| Vertex | Profile |
|---|---|
|V2|{1:1001,2:2457}|
|V3|{1:4459/2,3:2457/2}|
|V4|{1:2639,4:819}|
|V5|{1:11375/4,5:2457/4}|
|V6|{1:4459/2,6:2457/4}|

The raw-optimum vertex is V6. Minimizing the tail moment subject to a raw
constraint is a different linear program; its solution need not be V6.
The dual below covers the entire simplex directly.

## Exact linear feasibility formulation

Put `t=1-C`, `s=t+1/5`, and define the local six-rank moments

```
R(p) = sum(p_r*r^t, r=1..6),
S(p) = sum(p_r*r^s, r=1..6).
```

Let p0 be the current source six-rank profile
`(2211,459,494,94,164,18)`, and write
`G=R(p0)-R(p)` and `DeltaS=S(p)-S(p0)`.
Rank seven and all nonlocal terms cancel in these differences.

The complete raw gap for the changed n18 invoice is `18*(G-B18(C))`.
Even the weaker necessary condition alpha<1 therefore requires
`G>B18(C)`. The actual alpha reserve 10^-10 only strengthens this requirement.

Let T(C) be the complete source target moment at exponent t, and P0s(C)
the complete source paid moment at exponent s. The gamma requirement is

```
DeltaS < W(C)/18,
W(C) = .97*17^(1/5)*T(C) - P0s(C).
```

Both constraints are linear in the candidate paid histogram. A failed
whole witness does not prove infeasibility; the following dual does.

## A rational six-rank Farkas inequality

Set `lambda=799/10`. Define tag_r=1 for r=1,...,5 and tag_6=2.
For each stated C, the arithmetic JSON supplies rational `mu,nu` such that

```
r^s + lambda*r^t >= mu*r + nu*tag_r    for r=1,...,6.
```

The construction uses only elementary rational bounds. For the inherited
logarithm brackets `(l_r,u_r)`, put

```
Elo(r)=1-C*u_r+(C*u_r)^2/2-(C*u_r)^3/6,
Ehi(r)=1-C*l_r+(C*l_r)^2/2.
```

Taylor's theorem gives `Elo<=exp(-C ln r)<=Ehi`; both bounding polynomials
are decreasing on the tiny argument range here. Thus
`r*Elo<=r^t<=r*Ehi`. Rational fifth-root brackets are:

| r | q_lo | q_hi |
|---|---:|---:|
|1|1|1|
|2|1.14869835|1.14869836|
|3|1.24573093|1.24573094|
|4|1.31950791|1.31950792|
|5|1.37972966|1.37972967|
|6|1.43096908|1.43096909|

Every bracket is certified by the exact integer-power inequalities
`q_lo^5<=r<=q_hi^5`; the rational residuals are retained in the JSON.
Consequently `r*q_lo*Elo<=r^s<=r*q_hi*Ehi`.
No negative-C engine evaluation or newly evaluated logarithm is involved.

Let `F2lo` be the lower bound on `2^s+lambda*2^t`. Set

```
mu = F2lo-(1+lambda),
nu = 1+lambda-mu.
```

This makes the rank-one inequality exact and the lower rank-two inequality
exact. The remaining four lower slacks are strictly positive:

| C | rank3 | rank4 | rank5 | rank6 |
|---|---:|---:|---:|---:|
|.0033|>.00213232089437416600|>.01403166894892380295|>.03779312051181381577|>.00068551599794297727|
|.0033000005|>.00213229975531319194|>.01403161293520574584|>.03779301941329319163|>.00068530558308600864|

Multiply these six inequalities by any nonnegative p_r and use the two
invariants:

```
S(p)+lambda*R(p) >= 5915mu+3458nu.
```

Define the source's dual slack
`sigma0=S(p0)+lambda*R(p0)-(5915mu+3458nu)`.
Upper bounds on the six powers give a rational `sigma_upper>=sigma0`.
Rearranging proves for every profile in the real signed closure

```
DeltaS >= lambda*G-sigma_upper.
```

Inserting the existing strict B18 lower bound yields:

| C | sigma_upper | Necessary DeltaS if alpha<1 |
|---|---:|---:|
|.0033|<8.69809130645176079643|>228.36752123200990441786|
|.0033000005|<8.69805524932209460307|>228.36810050287430728456|

This is an all-profile lower bound. It does not assume that the candidate
uses nonnegative exchange counts, has the raw-optimal profile, or lies on
the line between the source and that optimum.

## Bound the available tail headroom without reusing a source-point ratio

The retained source interval is at `C0=.0030818905`, not at the goal.
It reports
`gamma0 > .967392647519607666245315102667` for the original n18 invoice.
For a deliberately weaker sufficient input, require only `gamma0>.965`.

Let `Delta=C-C0>0`, `K=17^(1/5)`, and `L=4.3177>ln72`.
The source's maximum paid rank is 72, so

```
P0s(C) >= (1-Delta*L)*P0s(C0).
```

Its fixed targets have decreasing moments in C, so `T(C)<=T(C0)`.
With `gamma0=P0s(C0)/(K*T(C0))`, these imply

```
W(C) <= K*T(C0)*(.97-(1-Delta*L)*gamma0).
```

Because `K<1.763` (check `1.763^5>17`), `T(C0)<=242010`, and the
displayed upper bracket using gamma0=.965 is positive,

```
W(C)/18 < (1.763*242010/18)*(.97-.965*(1-Delta*4.3177)).
```

This is an explicit analytic transport inequality. It neither identifies
gamma(C) with gamma(C0) nor treats the source's own alpha/delta values as
goal-point values.

| C | Available DeltaS upper, gamma0>.965 | Necessary DeltaS lower | Separation gap |
|---|---:|---:|---:|
|.0033|140.05875521742568639125|228.36752123200990441786|>88.30876601458421802661|
|.0033000005|140.05880459876904242500|228.36810050287430728456|>88.30929590410526485956|

Using the full author lower interval instead gives respective available
upper bounds 83.39796054001357533560 and 83.39801004379439115765.
The deliberately weaker .965 bound already separates the constraints.

Therefore, **if the pinned B18 bounds and the source input gamma0>.965 are
independently qualified**, no nonnegative real signed-ABCD profile satisfies
both raw alpha<1 and gamma<.97 at either stated point with the original
n18 route. All integer profiles and forward-order realizable profiles are
subsets of that real relaxation, so they are also excluded in that scope.

For n17 the fixed target invoice alone gives delta>.975 at both points,
as proved in the companion budget. Hence no ABCD mixture changes that
n17 obstruction. This note does **not** exclude another controller count,
different tail parameters, changed helper targets, a new primitive, a
changed ordinary/compiler route or a different exchange family. A raw
controller optimum does not imply a funding optimum over controller counts.

## The supplied partial probe

The proposed probe `(a,b,c,d)=(268,82,194,152)` is nonnegative and gives

```
P={1:2219,2:253,3:272,4:52,5:90,6:286,7:14}.
```

This is an integer histogram feasibility statement, not a physical edit.
At C=.0033 its raw gain is strictly between 3.39970138840804262682 and
3.40362630348670644059 per FULL, so it clears the raw threshold. Its tail
numerator increase is between 268.13231948867220570575 and
268.13721149867646086287 per FULL, which exceeds even the weak available
headroom bound above. The tested point gives the same conclusion. This
probe is illustrative; it is not used to prove the all-profile exclusion.

## Smallest root qualification needed

Freeze the source inputs and the two existing price-transfer points, then
qualify this finite certificate under root's guarded serial executor:

1. Verify source custody, original n18 P/T invoices, max paid rank 72,
   target rank mass 242010, source C0, cutoff 17 and offset 1/5.
2. Independently establish gamma(C0)>.965 on that source invoice, or
   establish directly that W(C)/18<140.05875522 and <140.05880460 at the
   two goal points. Reading the author interval is not this qualification.
3. Check the affine inverse and both invariants symbolically; check every
   fifth-power bracket, inherited log bound, Taylor-domain condition,
   rational dual slack, source slack upper bound and strict separation.
4. Include controls for wrong sign of lambda, missing tag6=2, a corrupted
   fifth-root bracket, omitted rank-seven/nonlocal cancellation, wrong
   source/goal C, wrong B18 denominator, discarded target/idle, and the
   source gamma silently reused as a goal value. A control increasing
   available headroom above the necessary bound must be classified as
   inconclusive, not a false exclusion.

No executable checker or execution request is supplied by this paper-only
worker. `FUNDING-PLANE-ARITHMETIC.json` contains the exact finite fractions
and provenance needed to prepare that frozen request. Physical G1a remains
prospective and ownership-gated; broad frame or helper-basis searches are
not authorized by this funding calculation.
