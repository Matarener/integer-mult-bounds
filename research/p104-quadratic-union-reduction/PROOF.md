# A sharp two-plane union theorem for the E8 quadratic shell

This scoped proof and its reduction were produced by Nick Petalas. Apache-2.0.
Quadratic Gauss sums and finite quadratic-space theory are classical.

Let V be an eight-dimensional vector space over F2. Let Q be a nondegenerate
quadratic form of plus type, with polar form B. Thus

    sum_(u in V) (-1)^Q(u) = 16.

Write S = {u : Q(u)=1}; it has 120 elements. For a two-dimensional subspace
A of V and a linear functional b on A, define the live set

    L(A,b) = {u in S : B(u,a)=b(a) for every a in A}.

The constraint plane is A; it need not be isotropic. Two constraint systems
are consistent together exactly when their functionals agree on A intersect A'.
Nondegeneracy of B makes every consistent combined system soluble in V.

## Theorem

For any two live sets, their union has at most **68** points. Equality holds
exactly in the following configuration, up to exchanging the sets:

- A is a nondegenerate plane, and Q restricted to A plus b is anisotropic;
  consequently |L(A,b)|=36.
- A' is an isotropic plane, and Q restricted to A' plus b' is a nonzero
  linear functional; consequently |L(A',b')|=32.
- A intersect A' is a line, and b,b' disagree on its nonzero vector.

The two live sets are then disjoint. Every other union has at most **66**
points. In particular, the maximum union of two 36-point sets is exactly 66.
Here anisotropic means that all three nonzero plane vectors have value one.

## 1. Fourier count

For a subspace D of dimension r and a linear functional h on D, put

    G(D,h) = sum_(a in D) (-1)^(Q(a)+h(a)).

Quadratic completion gives

    sum_(u in V) (-1)^(Q(u)+B(u,a)) = 16 (-1)^Q(a).

Expand the indicator of the r affine linear equations using characters.
The indicator of Q(u)=1 is (1-(-1)^Q(u))/2. Character orthogonality gives

    N(D,h) = 2^(7-r) - 2^(3-r) G(D,h).                 (1)

For a plane, G is 4 or 0 if its polar form is zero: the restricted quadratic
refinement is linear. For a nondegenerate plane it is 2 or -2. Hence every
live-set cardinality lies in {24,28,32,36}; 36 occurs precisely for the
anisotropic plane refinement.

We also use the elementary Gauss-sum rule in dimensions at most four.
Let R be the radical of the polar form on D. If Q+h is nonzero on R,
translation by a radical vector of value one cancels the sum, so G=0.
Otherwise it descends to the nondegenerate quotient D/R; G is |R| times
that quotient's Gauss sum. A nondegenerate quadratic space of dimension
2s has Gauss sum plus or minus 2^s. Sum in a symplectic basis: each binary
pair contributes 2 or -2. No pair census is used in this argument.

## 2. Two 36-point sets have union at most 66

Both constraint-plane refinements are anisotropic. On each nonzero vector
of either plane, its functional is Q(a)+1. Thus the functionals agree on
the intersection. Put D=A+A', r=dim D, and let h be their common extension.
The intersection of the live sets is counted by (1).

If r=2, the planes and functionals coincide; the union has size 36.
Otherwise r is 3 or 4, and the polar form of D has rank at least two because
it contains the nondegenerate plane A.

If the polar rank is two, either Q+h is nonzero on its radical, giving
G=0, or it vanishes there. In the latter case projection identifies A with
the two-dimensional nondegenerate quotient. The induced refinement is
anisotropic, so the quotient Gauss sum is -2 and G is negative. Formula (1)
gives an intersection of size at least 2^(7-r), which is at least eight.

The remaining possibility is r=4 and polar rank four. Here G is 4 or -4,
so (1) gives an intersection of size 6 or 10. In all cases it has at least
six points. The union is at most 36+36-6=66.

## 3. The 68-point equality case is the only larger union

If at most one live set has size 36, the other has size at most 32. Thus
the union is at most 68. Equality requires sizes 36 and 32 and an empty
intersection. Their constraint planes must respectively be nondegenerate
and isotropic, by Section 1. They cannot be the same plane.

Suppose their combined affine equations are consistent. Their span D has
dimension three or four and polar rank at least two. For r=3, the radical
rule gives |G| at most four, so (1) gives at least twelve intersection
points. For r=4, polar rank is two or four, giving |G| at most eight and
at least four intersection points. Consistency therefore precludes equality.

The equations must instead be inconsistent. Two distinct planes can have
inconsistent functionals only when their intersection is a line. Conversely,
inconsistency on that line makes the live sets disjoint and attains 68.
On its nonzero vector v, the anisotropic refinement has value one;
inconsistency is equivalently (Q+b')(v)=0, the kernel of the nonzero linear
refinement on A'. This proves the stated equality classification.

Finally every union has even size. For inconsistent equations this follows
from the individual cardinalities. For consistent equations r is at most
four. Formula (1) is even for r at most three. For r=4 the polar rank is
even and at most four, so G is divisible by four by the radical rule;
N=8-G/2 is even. A union below 68 is therefore at most 66.

## 4. Attainment

Use a hyperbolic basis e1,f1,...,e4,f4, so Q(u)=sum x_i y_i and
B(u,e_i)=y_i, B(u,f_i)=x_i.

For 68, the first live set imposes x1=y1=1. It has 36 points, since the
remaining six-dimensional plus form must be zero. The second imposes
y1=0,y2=1. It has 32 points: x2 is determined by the other five free bits.
They are disjoint. Their planes are span(e1,f1) and span(e1,e2), and their
affine values disagree on e1, exactly as in Section 3.

The plus sign matters. For the minus-type form Q'(u)=Q(u)+x1+y1,
the plane systems y3=y4=0 and y3=1,y4=0 give disjoint live sets of
sizes 40 and 32, hence union 72. The checker evaluates this counterdomain
directly. It is outside the theorem's hypotheses.

For the sharp two-36 bound, impose x1=y1=1 for one set and x2=y2=1 for the
other. Each has 36 points. In their intersection, the last two hyperbolic
pairs have Q=1, which has six solutions. The union has 66 points.

## 5. Exact reduction of the outstanding P104 counting step

Matarener's [PR6218](https://github.com/CrocSwap/integer-mult-bounds/pull/6218),
head 159352d273bd7b9f92c55cee3a9ac9b955de9b86, Section 4 uses a finite
P104 union bound of 66 in a proposed hand-proof route to compatible-plane
disjointness. Its counting result is cited; neither that pair census nor
its compatibility result is replayed here.

In that source's E8/2E8 model, V is the even-weight subspace of F2^9,
Q(u)=wt(u)/2 modulo two, and a root label is q=u+1. For a label constraint
z, write epsilon=wt(z) modulo two and a=z+epsilon*1 in V. Then

    q dot z = B(u,a)+epsilon.

A label plane containing 1 has empty live set. Every other label plane
projects injectively to a plane A in V and gives exactly the affine system
above. The 104 ports are S minus sixteen specified root lines T.

The theorem shows that proving the P104 union bound 66 requires checking
only the exceptional 68-point configuration: it is equivalent to

    |(L(A,b) union L(A',b')) intersect T| >= 2

for every configuration in the theorem's equality class. All other pairs
already have full-E8 union at most 66, before puncturing. This is a precise
reduction, not a proof of the displayed puncture inequality. The latter
depends on the two removed frames. The unrelated hyperplane and at-most-four
pairwise non-orthogonal exception conditions in compatibility also remain.
The 68-point fixture proves that the full-E8 relaxation alone cannot yield
the required 66 bound. No compatible-plane or decoder-floor theorem is
claimed as a new consequence here.

## Finite corroboration domain

The written proof is universal. Its finite checker separately enumerates all
alternating polar matrices and all quadratic refinements on spaces D of
dimension 2..4, with all unordered spanning pairs of planes. For consistent
affine equations a common offset is absorbed into the quadratic refinement.
For inconsistent equations the quadratic diagonal is absorbed into the two
separate offsets; all sixteen pairs of linear offsets are tested. Thus the
normalization removes no relative configuration. These small representative
cases are not a count of literal pairs of planes in the eight-space.
The second check directly evaluates every affine plane system in the full
eight-space, without the Fourier formula, and compares its cardinality.
