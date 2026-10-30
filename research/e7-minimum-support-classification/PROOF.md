# Equality in the E7 support bound

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source geometry and support bound are due to Nick Petalas, PR5238.

## Statement

Use doubled E8 roots, with squared norm eight. Fix
`a=(2,0,0,0,2,0,0,0)`. Let R be the 63 root lines perpendicular to a,
with one root on each line. Let H be the incidence matrix of all 135
orthogonal seven-line frames in R. Let K be any field of characteristic zero.

A nonzero function f:R -> K with Hf=0 has support at least twelve.
If its support has size twelve, there are exactly two possibilities up to
a nonzero scalar and E7 root reflections. Representatives are the
restrictions to a-perp of

```
A(x) = x0^2+x1^2+x2^2+x3^2-x4^2-x5^2-x6^2-x7^2,
B(x) = (x0-x1)(x2-x3).
```

The support orbit of A has 630 members. The support orbit of B has 1008
members. They are disjoint and include all 1638 minimum supports. Each
support admits exactly one scalar family of frame relations. Every such
relation is the evaluation of a trace-zero quadratic. The two quadratic
ranks on a-perp are six and two. Thus the two types cannot be identified
by any orthogonal map and nonzero scalar.

The same statement holds on the perpendicular slice of any E8 root,
by rational orthogonal transport. It also classifies every trace-zero
quadratic that attains support twelve. The zero quadratic is excluded.

## Finite certificate and its completeness

The retained PR5238 code constructs the 63 roots in two ways, constructs all
135 frames by increasing orthogonal cliques, and computes a binary kernel
basis of dimension 27. Its free-coordinate submatrix is the identity.
Each basis vector has zero parity on every frame. These checks prove that
all binary frame relations are in the generated code.

The new checker traverses all 2^27-1 nonzero coefficient vectors in Gray
order. It uses every basis direction at its prescribed toggle. Independence
makes the resulting codewords distinct and nonzero. The minimum weight is
twelve. Exactly 1638 distinct supports have this weight. No saved support
list or numerical rank test supplies this result.

For each root r in R, the map

```
s_r(x) = x - (x dot r) r / 4
```

is an orthogonal reflection because r dot r=8. It fixes a. The checker
constructs its exact permutation of R and checks its action on every frame.
These 63 maps generate the E7 reflection action used here. Breadth-first
closure of the two representative supports gives sets of sizes 630 and
1008. Their union is exactly the exhaustive minimum-support set, and their
intersection is empty. This proves coverage; it does not require an assumed
Weyl-group order or an external group catalogue.

The evaluations of A are six +8 values, six -8 values, and 51 zeros.
The evaluations of B are six +4 values, six -4 values, and 51 zeros.
The checker verifies all 135 frame sums for both vectors. Exact rational
elimination gives rank eleven for H restricted to either representative
support. Therefore each restricted kernel has dimension one. Reflection
transport gives the same rank and a nonzero quadratic lift on every support.
As a separate check, removal of any one coordinate from either support gives
column rank eleven and no nonzero relation.

## From the binary certificate to characteristic zero

First let f be rational and nonzero with Hf=0. Clear denominators and divide
all entries by their greatest common divisor. The result is a primitive
integer relation. Its reduction modulo two is nonzero, lies in the binary
kernel, and has support contained in that of f. Thus f has support at least
twelve. If f has support twelve, its binary reduction must have the same
support, which is in the two checked orbits. This is the PR5238 reduction,
now used with the full equality list.

Now let f have values in any characteristic-zero field K, and let S be its
support. The integer matrix H restricted to S has the same rank over Q and
K: its nonzero rational minors stay nonzero in K. A nonzero K-kernel therefore
implies a nonzero rational kernel. A rational vector in that kernel has
support at most |S|, so the rational lower bound gives |S| >= 12.

If |S|=12, any nonzero rational kernel vector has support exactly S. The
previous paragraph puts S in the two orbits. The checked restricted rank
is eleven over Q and hence over K. The K-kernel is the scalar span of the
transported representative. This proves the stated classification for
arbitrary characteristic zero, without reduction of K itself modulo two.

## Quadratic interpretation

On a-perp, set y=x0=-x4 and use the other coordinates
`x1,x2,x3,x5,x6,x7`. The Euclidean metric in this basis is
`diag(1,1,1,1,1,1,2)`. The trace of a quadratic matrix M in these coordinates
is the sum of its first six diagonal entries plus M_yy/2.
Both representatives have trace zero. Exact polarization gives ranks six
and two. A frame is an orthogonal basis of a-perp of equal squared length,
so every trace-zero quadratic gives a frame relation.

The quadratic evaluation map is injective in characteristic zero. On the
six ordinary coordinates, the roots `2e_i +/- 2e_j` force all mixed
coefficients to zero and every pair of diagonal coefficients to sum to zero.
Three indices force all six diagonal coefficients to zero. The root
`2e0-2e4` then kills the y-square term. Only y times a linear form in the
six coordinates remains. The 32 odd-parity sign rows have Gram matrix
32I, so their evaluations kill all six remaining coefficients. These are
exact identities over Q and remain valid in every characteristic-zero field.
This is the injectivity argument retained from PR5238.

Thus the relation classification gives the quadratic classification as well.
The retained nine ambient generators preserve the E8 roots and move a to
all 120 root lines. They are rational orthogonal maps. This transports the
whole result to every root slice.

## Relevance and limits

This resolves PR5238's equality-classification question. Sparse incidence
failures at the twelve-line threshold have two explicit quadratic types;
a diagonal balanced-pair ansatz alone misses the rank-two type. A future
sharp deletion-boundary proof can now use a complete equality list.

The arbitrary-deletion extension statement in Discussion1502 remains open.
This result does not prove it, the seven-deletion incidence implication,
a decoder cost floor, a physical supplier, or an improvement in complete
kappa. The selected metadata still has conditional kappa 0.00310045, with
the main transform as its limiting outer row. No formal proof kernel or
independent human review is claimed.
