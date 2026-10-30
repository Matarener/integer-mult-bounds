# Exact joint transition cost

This proof was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Take any finite number h of independent complex helpers. Write helper j as
two real coordinates and prescribe multiplication by

`g_j = 2^(a_j) (1 + epsilon_j i)^(b_j)`,

where a_j is any integer, b_j belongs to {0,1}, and epsilon_j belongs to
{-1,1}. The complete required real map is block diagonal, with blocks

`T_j = 2^a [[1, -epsilon*b], [epsilon*b, 1]]`.

Any finite number of extra real registers may contain arbitrary independent
dirty inputs. They must return exactly unchanged, without leaking into or
receiving data from the helpers at exit. Thus the complete endpoint is
`T = diag(T_1,...,T_h,I_dirty)` on every real input.

The charged elementary operations are signed unit ADDs `x_r += +/- x_s`
with r != s, and individual doublings or halvings. Each costs one. Coordinate
permutations and negations are granted free. Every operation may connect any
two registers, including workspace. No other scalar coefficients, constants,
COPY, clear, nonlinear operation, or larger native map is free.

Every implementing word needs at least

`S = sum_j |2a_j+b_j|` doublings/halvings, and
`A = 2 sum_j b_j` signed ADDs.

One explicit word attains both bounds simultaneously. Consequently its exact
minimum total charge is `S+A`, even with arbitrary cross-helper mixing and
any finite restored dirty workspace. The inverse endpoint has exactly the
same two minima.

This answers the pure joint-transition question of Sagar Thakrar's PR1566.
It does not price a transition fused with a different surrounding operation.

## A lattice-index distance counts scales

For two full rational lattices L,M in Q^n, define

`d(L,M) = log_2([L:L intersect M] [M:L intersect M])`.

All these indices are finite. Applying the same invertible rational map to
both lattices preserves them. Also d satisfies the triangle inequality.
Indeed, for a third lattice N,

`[L:L intersect N] <= [L:L intersect M] [M:M intersect N]`.

To see this, insert the smaller subgroup L intersect M intersect N, split
its index at L intersect M, and inject the latter quotient into
M/(M intersect N). Apply the same inequality with L and N exchanged and
multiply the two bounds. Taking logarithms proves the triangle inequality.
This is a standard lattice-index argument, not a claimed new metric.

Let Z denote Z^n and let P be the current rational matrix. A next gate G
satisfies

`d(GPZ,Z) <= d(GPZ,GZ) + d(GZ,Z) = d(PZ,Z) + d(GZ,Z)`.

A signed ADD, permutation or negation maps Z onto itself and has last term
zero. A single doubling or halving has last term one. Starting from P=I
therefore gives

`number of scales >= d(TZ,Z)`.

This uses a distance between lattices, rather than the absolute valuation of
the determinant. Opposite expansions and contractions cannot cancel it.

For b=0, the two-coordinate block lattice is 2^a Z^2. Its distance from
Z^2 is 2|a|. For b=1 put

`B_epsilon = [[1,-epsilon],[epsilon,1]]`,
`B_epsilon^-1 = (1/2) [[1,epsilon],[-epsilon,1]]`.

If a >= 0, `2^a B_epsilon Z^2` lies inside Z^2 with index
`2^(2a+1)`. If a <= -1, its inverse matrix is integral, so the block lattice
contains Z^2, with index in the opposite direction `2^(-2a-1)`.
In either case the distance is |2a+1|. Intersections of direct-product
lattices are direct products and their indices multiply. Restored dirty
registers contribute zero. Hence `d(TZ,Z)=S` as asserted.

## Row support counts ADDs

Call a row mixed when it has at least two nonzero entries. The initial
identity has no mixed rows. A doubling, halving, negation or coordinate
permutation preserves the number of mixed rows. A signed ADD changes only
one row and can increase that number by at most one. At the required
endpoint exactly the two rows of each b=1 block are mixed; the other helper
and dirty rows each have support one. Thus every word needs at least A ADDs.

This argument remains valid when temporary rows have large support, when
mixing is undone, and when arbitrary dirty registers are used. The scale
and ADD arguments apply to disjoint charged gate types, so their bounds add.

## Simultaneous attainment

For b=0, scale both coordinates by 2^a, using 2|a| individual scales.
For b=1 and a >= 0, the three operations

```text
x -= epsilon*y
y *= 2
y += epsilon*x
```

produce `(x-epsilon*y, epsilon*x+y)`. Scale both outputs by 2^a.
There are two ADDs and 2a+1 scales.

For b=1 and a <= -1, instead use

```text
x -= epsilon*y
x /= 2
y += epsilon*x
```

This produces half of that same block. Scale both outputs by 2^(a+1).
There are two ADDs and -2a-1 scales. Execute these words independently on
all helpers and leave all workspace unchanged. They attain S and A.

The inverse of a b=0 block replaces a by -a. The inverse of a b=1 block
replaces `(a,epsilon)` by `(-a-1,-epsilon)`. This stays in the stated
family and preserves |2a+b| and b, proving the inverse claim.

## The requested reciprocal boundary

For `(g_1,g_2) = (1+i, (1+i)^-1)`, the parameters are
`(a,b,epsilon)=(0,1,1),(-1,1,-1)`. Thus S=2, A=4 and the exact cost is
six. The determinant of the combined four-coordinate map is one, so its
determinant valuation alone gives zero. The lattice distance is two.
Arbitrary dirty workspace cannot lower six; a separately required return
costs six more. This is a boundary cost, not a lower bound on a fused round
trip whose only required endpoint is the identity.

## Scope of the conclusion

The quantified result is this written proof; finite software checks are
corroboration. General unit phases beyond the stated conjugate family,
nonunit odd coefficients, singular clean workspace, COPY/clear, alternative
native primitives and endpoints fused with an original SCALE or ADD require
separate analysis. Physical routing, precision, coefficient production,
compiler admission, productive targets and recursive costs are not supplied.
No new kappa or complete multiplication theorem is claimed.
