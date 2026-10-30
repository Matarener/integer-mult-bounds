# Sharp query count when cubic repair includes an original-b cube

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas's PR6200 supplies the fixed cubic-reader interface; apoursh's
PR6212 supplies the dyadic two-query obstruction and earlier constructions.
The new result is the exact boundary for repairs containing a pure-b query,
including arbitrary nonmonic forms, and the integer construction across it.

## Fixed contract and theorem

Use exact arithmetic with dyadic coefficients R=Z[1/2]. The distinct streams
y,a,b start arbitrary. Retain every one of r original children, each in order

```
y += a^3
a += b
```

The eager comparator restores `a -= b` after each child, ending at
`(y+r*a^3,a,b)` in entry coordinates. The deferred program retains all original
children, then repairs the output and both sources. Source changes are in
GL_2(R); query updates add signed R-weighted cubes of source linear forms.
Coefficients do not depend on input values. There is no output feedback,
intermediate observation, child fusion, nonlinear source map or output recoding.
Source transformations, their inverses and coefficient work are paid separately.

Here **pure-b means a nonzero cube of a nonzero scalar multiple of the
original entry b**, not simply a read from whichever register is currently
named b. General frames may temporarily mix both sources. The theorem counts
appended nonzero cube queries and requires at least one pure-b query. Zero
queries cannot be inserted to meet this requirement.

**Theorem.** For every integer r>=3, the exact minimum in this restricted
family is

```
3, if r mod 9 belongs to {0,1,2,5,8};
4, if r mod 9 belongs to {3,4,6,7}.
```

Every upper bound uses integer source transformations and integer query
weights. The lower bound allows arbitrary nonmonic dyadic forms and arbitrary
GL_2(R) source changes. In particular, widening from source shears to general
dyadic frames cannot remove the four-query floor while retaining a pure-b read.

This is not an unrestricted four-query lower bound. For example r=3 admits
three dyadic queries when all three forms involve entry a. The separate r=2
unrestricted two-query result belongs to PR6212 and is outside this theorem's
domain. No runtime or multiplication-bound improvement is asserted.

## Chronological defect and elementary lower bound

Let A,B denote entry a,b. The retained deferred program ends at

```
(y + sum_{i=0}^{r-1}(A+i*B)^3, A+r*B, B).
```

Its excess output over the eager comparator is, as in PR6200,

```
f_r(A,B) = 3S1*A^2*B + 3S2*A*B^2 + S1^2*B^3,
S1=r(r-1)/2,  S2=r(r-1)(2r-1)/6.
```

Every appended source is an R-linear form in A,B: multiply the source-frame
matrices in chronological order. Thus any repair gives a signed weighted-cube
decomposition of -f_r. Negating weights gives one for f_r, without changing
the number of queries or the pure-B property.

At most two cubes including a pure-B term are impossible. There is then at
most one term involving A. Its A^3 coefficient must vanish, forcing that
term's weight or A coefficient to be zero and therefore also its A^2*B
coefficient to be zero. But 3S1 is nonzero. This proves a three-query lower
bound for the entire restricted family, without invoking the predecessor's
stronger unrestricted dyadic lower bound.

## A modulo-nine obstruction for two remaining forms

Reduction R -> Z/9Z is well defined because 2 is invertible modulo 9.
Ignore the B^3 coefficient and project a physical weighted cube to

```
gamma*(alpha*A+beta*B)^3
    -> (gamma*alpha^3, 3*gamma*alpha^2*beta, 3*gamma*alpha*beta^2) mod 9.
```

If alpha is divisible by 3, this triple is zero. Otherwise alpha is a unit
modulo 9 and the triple is `(lambda,3*lambda*t,3*lambda*t^2)`, where
lambda=gamma*alpha^3 and t=beta/alpha in Z/9Z. A zero triple can be represented
by lambda=0. These reductions do not assume a dyadic normalized slope over Q.

Suppose two projected cubes sum to a vector with its first two coordinates
zero. The first coordinate gives lambda_2=-lambda_1. The second gives
`3*lambda_1*(t_1-t_2)=0`. Consequently the third is

```
3*lambda_1*(t_1^2-t_2^2)
 = [3*lambda_1*(t_1-t_2)]*(t_1+t_2) = 0 mod 9.
```

This identity holds in Z/9Z despite its zero divisors. We never divide by
lambda or by a slope difference. It covers zero weights, nonprimitive forms
and arbitrary nonmonic forms, which only strengthens the obstruction.

For r congruent to 3,4 modulo 9, the target projection of f_r is `(0,0,6)`;
for r congruent to 6,7 it is `(0,0,3)`. Indeed 3S1=3r(r-1)/2 and
3S2=r(r-1)(2r-1)/2 modulo 9 depend only on r modulo 9. A pure-B term projects
to zero. Any three-query repair containing it has at most two remaining
projected cubes, so the preceding identity rules it out in all four classes.

The independent finite certificate enumerates all 9^3=729 triples
(gamma,alpha,beta) modulo 9, obtaining 33 full weighted-cube tensors and 21
distinct projections. Their 441 ordered pair sums have 57 distinct values.
Neither forbidden target is present. This exhaustive finite calculation
corroborates the universal reduction argument; no unbounded search is inferred.

## Integer attainment when r=2 mod 3

This is the construction from PR6212. Put

```
t=(r+1)/3, s=(r-2)/3,
mu=S1*(r-2)*(r+1)/6=2*binom(r+1,4).
```

For r>=3 in this class, r>=5 and t,s,mu are positive integers. Expansion gives

```
f_r = S1*((A+t*B)^3-(A+s*B)^3) + mu*B^3.
```

Starting at the actual source `(A+r*B,B)`, append

```
a += (t-r)*b
y -= S1*a^3
a -= b
y += S1*a^3
a -= s*b
y -= mu*b^3
```

There are three nonzero queries, including the original-B cube, and three
source shears. The final source is exactly `(A,B)`, and the output subtracts f_r.

## New integer attainment when r=0 or 1 mod 9

Now S1 is divisible by 9. Let N=S1/9 and mu=S1*(3S1-1)/9, both positive
integers. Direct expansion gives

```
f_r = N*((3A+r*B)^3-(3A+(r-1)*B)^3) + mu*B^3.
```

One of r,r-1 is divisible by 3. Its form factors as three times a monic
integer form, moving a factor 27 into its weight. The other form has primitive
integer coefficients and can be a row of an invertible integer source frame.
The following explicit program realizes both cases and charges the frame.

Set epsilon=-1 and q=r/3 for r=0 mod 9; set epsilon=1 and q=(r-1)/3 for
r=1 mod 9. Define simultaneous source transformations

```
M_epsilon(a,b) = (3a+epsilon*b, a),
M_epsilon^-1(a,b) = (b, epsilon*a-3*epsilon*b).
```

Their matrices have integer entries and determinant -epsilon, a unit. From
the actual deferred endpoint append, in this order,

```
a += (q-r)*b
y += epsilon*3*S1*a^3
(a,b) = M_epsilon(a,b)
y -= epsilon*N*a^3
(a,b) = M_epsilon^-1(a,b)
a -= q*b
y -= mu*b^3
```

The first query reads A+qB. The second reads 3A+(3q+epsilon)B. In the
r=0 case their contributions are `-3S1*(A+qB)^3+N*(3A+(r-1)B)^3`;
in the r=1 case they are `+3S1*(A+qB)^3-N*(3A+rB)^3`. Together with the
last query, these are -f_r in both cases. The inverse frame returns both
sources before the last shear restores A. The last query therefore reads
the actual original B. All three coefficients are nonzero.

For r=10, S1=45, N=5, q=3 and mu=670. The decomposition is

```
f_10 = 5*(3A+10B)^3 - 135*(A+3B)^3 + 670*B^3.
```

The repair applies shear -7, query +135, M_1, query -5, M_1^-1,
shear -3, and original-B query -670. B changes temporarily under the frame;
an implementation that silently treats it as immutable would be wrong.

## Four-query attainment and the scope control

For all r>=3, PR6212's integer construction uses

```
p=binom(r+1,3), m=binom(r,3), d=S1^2-S1,
f_r=p*(A+B)^3+m*(A-B)^3-S2*A^3+d*B^3.
```

From `(A+rB,B)` apply shear 1-r, query -p on a, shear -2, query -m on a,
shear +1, query +S2 on a, and query -d on b. All four queries are nonzero;
the source is restored and the last query is pure-B. This attains the
four-query lower bound in residues 3,4,6,7. The other five residues have
three-query attainment and the elementary lower bound, proving the theorem.

For comparison,

```
f_3=(A+B)^3+(A+2B)^3-2*A^3.
```

This gives three unrestricted queries, all with nonzero entry-A coefficient:
from A+3B visit slopes 2,1,0 with three -1 shears and weights -1,-1,+2.
It restores every source and output but has no pure-B query. Thus the new
four-query floor at r=3 cannot be relabeled an unrestricted floor.

## Complete logical tariffs and remaining obligations

Let Q_c^a,Q_c^b price complete weighted cube queries on the current named
source, including source access, coefficient use, private restoration and
return. Let L_c price `a += c*b`; let F_M price the complete simultaneous
source-frame operation M. These are distinct paid operations. The eager bill is

```
r*Q_1^a + r*L_1 + r*L_-1.
```

The deferred bill retains r*Q_1^a+r*L_1. In the new r=0,1 mod 9 construction,
its additional bill is exactly

```
L_(q-r) + Q_(epsilon*3S1)^a + F_Mepsilon + Q_(-epsilon*N)^a
 + F_(Mepsilon^-1) + L_-q + Q_-mu^b.
```

The older three- and four-query programs likewise charge every displayed
shear and query. No frame or its inverse is free, and two source frames
cannot be compared numerically with two shears without an actual tariff.
Coefficient generation, routing, precision, storage and dispatch remain
additional caller obligations. The simultaneous matrix description certifies
an algebraic source map, not an uncharged in-place or scratch-free backend.
Every map is invertible, so reverse order and literal event inverses restore
the arbitrary incoming state. The primary checker executes the reversed repair
and full programs on symbolic inputs; the independent checker separately
checks the forward restoring schedules, including their inverse-frame events.

The result excludes approximate queries, finite-field substitution as the
execution model and altered child interiors. Modulo nine is used only as a
necessary image of exact dyadic arithmetic. No native implementation, complete
favorable physical bill, supplier admission, selected assumption discharge,
independent human/formal-kernel acceptance or new kappa follows.

## Attribution

PR6212 retains credit for the earlier dyadic results, three/four-query formulas
and this open question. Nick Petalas retains PR6200's chronological defect,
rational two-query theorem and source-restoring interface. Sricharan Vagvala /
theon199 retains PR1532's quadratic fixed-reader/paid-repair interface, with
Adam Gall / PR1205 and Hanson Sun / PR1246 retaining the linear lineage.
Elementary modular reduction and binary-form decomposition are classical;
no historical-priority claim is made.
