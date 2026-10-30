# Prime denominators in cubic-reader repair

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
This extends Nick Petalas's PR6200, pinned in SOURCE-PINS.json. Its rational
two-cube criterion is restated and credited below. The new step is the exact
coefficient-ring obstruction, including nonmonic forms, and integer repairs.

## Contract and claims

Let P be any set of primes and R=Z[P^-1], a subring of Q. All coefficients
of appended source transformations and weighted cube queries must lie in R.
Source transformations belong to GL_2(R), so their inverses also lie in R.
The original streams y,a,b are arbitrary and distinct. For an integer r>=2,
retain exactly r original children, in the order

```
y += a^3
a += b
```

The eager comparator restores `a -= b` after each child, ending at
`(y+r*a^3,a,b)` in entry coordinates. A deferred program keeps every child
and then repairs both source and output. There is no intermediate observation,
output feedback into sources, nonlinear source change, output recoding or
access to child interiors. Coefficients are fixed independently of input data.
One signed weighted cube accumulation is one query. Reading b directly is
allowed and separately priced, as in PR6200; source changes and coefficient
preparation are additional work. All claims concern exact arithmetic, not
rounded execution, finite fields or a native implementation.

**Theorem.** Two appended cube queries suffice over R if and only if there
exists a positive integer k such that

```
(2r-1)^2 - 6k^2 = 3
```

and every prime divisor of k belongs to P. One query is always impossible.
This lower bound allows arbitrary nonmonic source forms and all GL_2(R)
source changes. The attaining program uses only integer source shears.

**Dyadic consequences.** For R=Z[1/2], the minimum is two exactly at r=2.
It is exactly three for r>=5 with r=2 mod 3. For every remaining r>=3,
the minimum lies between three and four; no exact three-versus-four claim
is made here. In fact the upper constructions below use integer coefficients.

## The forced two-query parameters

Write entry sources as a,b. The unchanged deferred children add
sum_{i=0}^{r-1}(a+i*b)^3 and leave the actual source a+r*b. Their output
excess over the eager comparator is

```
f = 3S1*a^2*b + 3S2*a*b^2 + S1^2*b^3,
S1 = r(r-1)/2,   S2 = r(r-1)(2r-1)/6.
```

This follows by the sums of first, second and third powers. Each source form
seen by an appended query has coefficients in R in entry coordinates, since
it is a row of a product of matrices over R. Thus q queries give a sum of q
R-weighted cubes representing -f. Changing all signs represents f instead.

The following coefficient comparison is PR6200's rational argument. A single
cube cannot have zero a^3 coefficient and nonzero a^2*b coefficient. In any
two-cube representation, both weights and both a coefficients must be
nonzero, since otherwise the same contradiction holds. Normalize the a
coefficients over Q. Cancellation of a^3 gives opposite normalized weights:

```
f = lambda*((a+t*b)^3 - (a+s*b)^3),
lambda*(t-s)=S1,   t+s=S2/S1,   t^2+t*s+s^2=S1.
```

The directions are distinct. With n=2r-1, u=(t+s)/2 and h=(t-s)/2,

```
u=n/6,   h^2=(2r^2-2r-1)/12,   lambda=S1/(2h).
```

Ordering the directions gives h>0. Set k=2h. Then n^2-6k^2=3. If
k=A/B is reduced with B>0, integrality of 6A^2/B^2 implies B^2 divides 6,
so B=1. Conversely an integer k satisfying this equation yields the above
rational representation. No classification of all Pell solutions is needed.
The nonzero defect also excludes a zero-query repair.

## Exact localization obstruction

The Pell equation implies 3 divides n. Reducing modulo 4, since n is odd,
gives k odd. Hence n/3 and k are odd integers and the forced slopes are

```
t=(n/3+k)/2,   s=(n/3-k)/2,
```

both integers. Moreover

```
4S1 = 3k^2+1,
```

so gcd(S1,k)=1. The reduced denominator of lambda=S1/k is therefore exactly
k. This is the prime-denominator obstruction missing from the rational test.

It cannot be hidden by scaling a query. For any admissible term
gamma*(alpha*a+beta*b)^3 with nonzero alpha, its normalized weight is
gamma*alpha^3, which lies in R because gamma and alpha do. The ratio
beta/alpha need not lie in R and we do not assume it does. Nevertheless the
rational comparison forces the two normalized weights to be +lambda and
-lambda and their slopes to be the integers above. Necessarily lambda lies
in R. A reduced rational S1/k lies in Z[P^-1] exactly when every prime of k
is inverted. This proves necessity even for nonmonic forms and a larger
class of forms than actual source frames may realize.

For sufficiency, from the actual final source a+r*b append

```
a += (t-r)*b
y -= lambda*a^3
a += (s-t)*b
y += lambda*a^3
a -= s*b
```

All shears have integer coefficients, each has determinant one, and both
query weights are in R. The source returns to entry a, b stays fixed, and
the output subtracts f. Omit exactly zero shifts. This is an admissible
two-query program for arbitrary incoming y,a,b, completing both directions.

For dyadics, k must be a power of two and is odd, hence k=1. The equation
then forces n=3 and r=2. At r=2 the two queries have coefficients -1,+1;
the source shifts are -1,-1. For every r>2, at least three dyadic queries
are required even when two rational queries exist.

## Three integer queries for r=2 mod 3

Set t=(r+1)/3 and s=(r-2)/3, so t-s=1 and both are integers in this class.
Expanding gives

```
f = S1*((a+t*b)^3 - (a+s*b)^3) + mu*b^3,
mu = S1*(r-2)*(r+1)/6 = 2*binom(r+1,4).
```

The last expression proves mu is an integer. It is positive for r>=5
and zero at r=2. Append

```
a += (t-r)*b
y -= S1*a^3
a -= b
y += S1*a^3
a -= s*b
y -= mu*b^3
```

At r=2 omit the zero shift and zero query. At r>=5 this is exactly three
queries and three shears, attaining the dyadic lower bound. For r=14:

```
a -= 9*b
y -= 91*a^3
a -= b
y += 91*a^3
a -= 4*b
y -= 2730*b^3
```

PR6200's optimal rational repair uses two queries with weights +/-91/11.
Here k=11, so a dyadic repair cannot retain that count even with nonmonic
forms. The three-query integer repair is optimal in the dyadic alphabet.

## Four integer queries for every r

Let p=(S1+S2)/2=binom(r+1,3), m=(S2-S1)/2=binom(r,3), and
d=S1^2-S1. All are integers. Coefficient comparison proves

```
f = p*(a+b)^3 + m*(a-b)^3 - S2*a^3 + d*b^3.
```

From the actual drifting source append

```
a += (1-r)*b
y -= p*a^3
a -= 2*b
y -= m*a^3
a += b
y += S2*a^3
y -= d*b^3
```

The source returns to entry a before the last two queries; b is unchanged.
For r>=3 every displayed query coefficient is nonzero. Thus the construction
has four queries and three shears. At r=2 use the sharper program above.
The bracket outside r=2 mod 3 does not mean each such arity is unresolved.
For example, expansion gives the dyadic three-query identities

```
f_3 = (a+b)^3 + (a+2*b)^3 - 2*a^3,
f_4 = (5/2)*(a+2*b)^3 + (1/4)*(a+4*b)^3 - (11/4)*a^3.
```

Visit the displayed nonzero slopes in descending order and finish at slope
zero to restore the actual source. Thus these two arities also attain three.
We do not classify three-query attainability for all remaining arities.
Every event in every program is invertible, since its target is absent from
its source expression; reversal with negated coefficients is a literal inverse.
No entry snapshot, clean scratch, lost dirty value or change to an original
child is used. The identities and chronology prove the result for arbitrary
incoming values, beyond any finite verifier domain.

## Paid boundary and limits

Use PR6200's complete-event prices: Q_c^a(N) or Q_c^b(N) for a weighted cube
on its named source, and L_c(N) for `a += c*b`. A query includes its coefficient,
source access, private restoration and return. Zero events are omitted.
The eager bill is

```
r*Q_1^a + r*L_1 + r*L_-1.
```

The deferred bill retains r*Q_1^a+r*L_1 and adds every displayed repair event
at its own price. In the exact-three class, the increment is

```
L_(t-r) + Q_-S1^a + L_-1 + Q_S1^a + L_-s + Q_-mu^b.
```

The universal four-query increment is

```
L_(1-r) + Q_-p^a + L_-2 + Q_-m^a + L_1 + Q_S2^a + Q_-d^b.
```

At r=14 the integer repair replaces fourteen eager restoring shifts by
three shears and three additional cube queries. It saves eleven shift events;
it does not establish a cheaper execution. The distinct weights, coefficient
generation, routing, precision, storage, dispatch and controller preparation
still need a matched physical bill. If a backend can only cube a fixed
register, routing b into that register and restoring it must also be priced.
No such backend is supplied. Changing the permitted operations or allowing
child fusion is a different problem. No selected-frontier change follows.

## Attribution

Nick Petalas's PR6200 supplies the defect, rational lower bound, Pell criterion,
restoring-schedule pattern and the explicit dyadic open question. Those steps
are reproduced here to make the strengthened theorem self-contained, not
claimed as new. Sricharan Vagvala / theon199's PR1532 retains the quadratic
fixed-reader/paid-repair interface; Adam Gall / PR1205 and Hanson Sun / PR1246
retain the linear deferral and repair lineage. Binary-form power decomposition
and elementary localization arguments are classical. No literature-priority
claim or independent human/formal-kernel acceptance is made.
