# Exact rational cube-query repair

This scoped proof is produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Work over Q. The distinct streams y,a,b have arbitrary incoming values. For an
integer r>=2 retain exactly r original children, each performing

```
y += a^3
a += b
```

The eager program follows every child by `a -= b`. Its endpoint is
`(y+r*a^3,a,b)`, in entry coordinates. The deferred program retains all the
children and appends a repair. It must have the same endpoint for every input.
There is no intermediate observation and no feedback from y into a or b.

A repair may apply invertible rational linear changes to the source pair and
add signed, rationally weighted cubes of source linear forms to y. Each such
cube accumulation is one query, including its coefficient. Source changes and
coefficient preparation are additional work. The attaining programs use only
`a += c*b`, preserve b throughout, and explicitly restore a. The lower bound
allows the larger class of all rational source linear forms, so it applies to
these programs too. Extra nonlinear operations, access to original child
interiors, output recoding and output-dependent source changes are excluded.

**Theorem.** The exact minimum number of appended cube queries is

```
2, if q_r = (2r^2-2r-1)/12 is a rational square;
3, otherwise.
```

Over R the minimum is always two. In particular r=3 needs three rational
queries, while r=14 needs two. This is a query lower bound and an attaining
restoring program in a declared alphabet, not an arithmetic-circuit lower
bound or a complete supplier cost.

## Derive the chronological defect

Child i, indexed from zero, observes `a+i*b` in entry coordinates. Thus the
unrepaired deferred output differs from the eager output by

```
f(a,b) = 3S1*a^2*b + 3S2*a*b^2 + S3*b^3,
S1 = r(r-1)/2,
S2 = r(r-1)(2r-1)/6,
S3 = S1^2.
```

These expressions follow by expanding each of the r cubes and summing i,
i^2 and i^3 for 0<=i<r. The final drifting source is `a+r*b`. S1>0.

Every appended source transformation is independent of y and linear in entry
a,b. Consequently any q-query repair represents -f as a sum of q signed
weighted cubes of rational linear forms. Multiple queries in the same
direction can be combined for a lower-bound argument. Any additional linear
output terms cannot change these homogeneous cubic coefficients.

## Necessity of the rational-square criterion

One cube cannot represent f. Its zero a^3 coefficient would force its a
coefficient to vanish, contradicting the nonzero a^2*b coefficient.

Suppose two cubes represent f. Neither linear form can have zero a
coefficient, since the remaining cube would then have a nonzero a^3
coefficient. Normalize both a coefficients to one, absorbing their cubes
into their rational weights. Cancellation of a^3 makes the weights opposite.
The two directions must be distinct. We therefore have

```
f = lambda*((a+t*b)^3 - (a+s*b)^3),   t != s.
```

Coefficient comparison gives

```
lambda*(t-s) = S1,
t+s = S2/S1,
t^2+t*s+s^2 = S3/S1.
```

Put `u=(t+s)/2` and `h=(t-s)/2`. The equations become

```
u = S2/(2S1),
h^2 = S3/S1 - 3u^2 = (2r^2-2r-1)/12 = q_r.
```

If t,s are rational, h is rational. Conversely, if q_r is a rational square,
take its positive rational square root h, set t=u+h, s=u-h, and
`lambda=S1/(2h)`. These choices satisfy all four cubic coefficients. Since
q_r>0 for r>=2, h is nonzero. This proves both directions and the two-query
minimum whenever the square criterion holds. Over R, the positive root always
exists, proving the real statement too.

## An explicit three-query repair and source restoration

For any nonzero rational h, direct expansion gives

```
f = S1/(2h)*((a+(u+h)*b)^3 - (a+(u-h)*b)^3)
    + (S3-3S1*u^2-S1*h^2)*b^3.
```

If the square criterion fails, choose h=1. The last coefficient is nonzero,
since otherwise q_r=1 would be a square. This gives exactly three queries.
Starting from the actual drifting source `a+r*b`, append

```
a += (u+h-r)*b
y -= S1/(2h)*a^3
a -= 2h*b
y += S1/(2h)*a^3
a -= (u-h)*b
y -= (S3-3S1*u^2-S1*h^2)*b^3
```

Omit the final cube only when its coefficient is zero, and omit exactly zero
shifts. The first two cube inputs are the required entry-coordinate forms.
The fifth event returns a to its entry value; b never changes. Subtracting f
gives the eager y endpoint for arbitrary incoming y,a,b. Every event is
invertible because its target is absent from its source expression. Reversing
event order and negating coefficients is a literal inverse. No clean state,
copy, hidden source snapshot or discarded dirty value is used.

For r=3, u=5/6 and q_r=11/12. The six repair events have shift coefficients
`-7/6,-2,1/6` and cube coefficients `-3/2,3/2,1/4`, the last reading b.
For r=14, u=9/2 and h=11/2. The five repair events are

```
a -= 4*b
y -= (91/11)*a^3
a -= 11*b
y += (91/11)*a^3
a += b
```

Both examples restore the actual source, rather than assuming an entry copy.

## An integer decision criterion

The square condition is equivalently the existence of an integer k with

```
(2r-1)^2 - 6k^2 = 3.
```

Indeed `q_r=((2r-1)^2-3)/24`. If its reduced rational square root is A/B,
then B^2 divides 24, so B divides 2. Hence k=2A/B is an integer. The converse
uses the root k/2. This is a decision criterion, not a classification of all
solutions of the Pell-type equation. The bounded checker enumerates arities;
the all-r result is the coefficient proof above.

## Complete logical event bill and boundaries

Let `Q_c(N)` price a complete `y += c*a^3` child on N coordinates, including
its coefficient, source access, private restoration and return. Let `L_c(N)`
price a complete `a += c*b`. A b-cube uses the corresponding complete query
price with b as source. Set the prices of omitted zero operations to zero.
Then the eager program costs exactly

```
r*Q_1(N) + r*L_1(N) + r*L_-1(N).
```

The deferred program costs exactly `r*Q_1(N)+r*L_1(N)` plus every displayed
repair event at its own price. In particular r=14 adds `Q_-91/11 + Q_91/11`
and `L_-4 + L_-11 + L_1`. Its original fourteen cube children all remain.
It saves eleven source-shift events and adds two cube-query events, with
nonunit rational coefficients. Query counts alone do not establish a saving.
Coefficient generation, routing, precision, storage and controller preparation
are additional obligations. No numerical backend price is substituted here.

The fixed original calls are essential. If they can be opened, the target
`y += r*a^3` can be computed directly and no deferral comparison is needed.
The all-r statement is exact rational arithmetic. Approximate queries, finite
fields, nonlinear source maps and intermediate observations are outside it.
No selected assumption, physical supplier or multiplication theorem is proved.

## Credit

Sricharan Vagvala / theon199's [PR #1532](https://github.com/CrocSwap/integer-mult-bounds/pull/1532)
provides the quadratic fixed-reader/paid-repair interface and its sharp
square-query floor. Adam Gall / PR1205 and Hanson Sun / PR1246 retain the
underlying linear deferral and paid repair lineage. Their computations are
cited, not replayed as a deliverable here.

Binary-form power decomposition is classical. Carlini, Catalisano and Geramita's
[monomial Waring-rank paper](https://arxiv.org/abs/1110.0745) is relevant
background; this proof does not claim a new general Waring-rank theorem.
The contribution is the exact arithmetic-sensitive cubic-reader criterion,
its rational restoring schedules and the stated interface cost consequence.
