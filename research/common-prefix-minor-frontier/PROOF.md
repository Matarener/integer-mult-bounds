# Sharp adaptive choice among higher-rank tests with shared columns

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let F be any finite field of order q. Fix integers 1 <= k < m and let
t=m-k+1 >= 2. Let G be uniform in GL_m(F), and let U be its first k rows.
Write U=[C B], where C consists of the first k-1 columns and B has t columns.
For each nonzero v in F^t define the rank-k determinant test

    d_v(U) = det [C, Bv].

Multiplying v by a nonzero scalar does not change its zero set. A nonempty
family contains at most M projectively distinct vectors, fixed before inspecting
G. A selector may inspect the entire G and choose any member of that family.
It fails precisely when its chosen determinant vanishes. These are actual
k-column tests after a fixed invertible input chart for each v. Each v extends
the first k-1 coordinate vectors to an independent k-tuple. They need not all
be coordinate minors in one common chart.

Put

    D = product_{j=0}^{k-1} (q^m-q^j),
    R = product_{j=0}^{k-2} (q^k-q^j),
    A = R q^(kt-2) (q-1) / D.

An empty product equals one. For every integer M>=1, the maximum failure
probability over such families and selectors is exactly

    P*(q,m,k,M) = 1 - A max(q+1-M, 0).                 (1)

In particular q+1 candidates suffice for failure on every matrix. This is
a sharp result for this shared-column family. It is not a bound for arbitrary
rank-k minors, arbitrary matrix distributions or current-dependent families.

## 1. The top frame is uniform

There are D full-row-rank k-by-m matrices. Choose the rows in order. After
j independent rows, q^j vectors are forbidden for the next row. Every such
matrix U has exactly

    product_{j=k}^{m-1} (q^m-q^j)

invertible completions to G, independent of U. Thus U is uniform on those D
matrices. Giving the selector access to the remaining rows changes neither
the set on which some candidate fails nor its probability. A selector that
chooses the first failing candidate whenever one exists attains that union.

## 2. Separate the common failure from the quotient test

If rank C < k-1, every d_v vanishes. If rank C=k-1, the quotient F^k/im C
is one-dimensional. Choose an arbitrary isomorphism of that quotient with F.
The quotient of B is a row z in F^t, and

    d_v(U)=0  if and only if  z dot v=0.

Full row rank of U forces z nonzero. For each fixed full-rank C, every
nonzero z has exactly q^((k-1)t) lifts B. This number does not depend on z,
so z is uniform on F^t minus zero conditional on C. Choosing a different
quotient coordinate scales z and leaves all its zero tests unchanged.

There are R possible full-rank C. Therefore the probability gamma of an
independent shared prefix is

    gamma = R q^((k-1)t) (q^t-1) / D.                (2)

The common-prefix deficiency contributes 1-gamma before any adaptive
choice. No independence between the candidate failure events is assumed.

## 3. The remaining union is sharp

This is the one-linear-minor geometry cited from ywz65's #2601. The short
argument is included to make the new reduction self-contained. A nonzero v
defines a hyperplane in F^t. For s distinct such hyperplanes, the first has
q^(t-1) points and each further one adds at most q^(t-1)-q^(t-2), because
its intersection with the first already has q^(t-2) points. Consequently,
for 1<=s<=q+1, their union on nonzero z has fraction at most

    b_s = [q^(t-2)(1+s(q-1))-1] / (q^t-1).        (3)

Equality holds for any s members of the pencil with normals

    (1,a,0,...,0) for a in F, and (0,1,0,...,0).

Their pairwise intersections are all the same codimension-two subspace,
and their parts outside that subspace are disjoint. All q+1 members cover
F^t. Extra budget cannot improve on probability one.

Every candidate family has unconditional failure at most

    (1-gamma) + gamma b_M

until saturation, with the same pencil attaining the bound simultaneously
for every full-rank C. Substituting (2) and (3) and cancelling q^t-1 gives
(1), since

    1-b_M = q^(t-2)(q-1)(q+1-M)/(q^t-1).

This proves the theorem for every finite field, including extension fields.
The finite verifier corroborates small cases; it does not supply these
unbounded quantifiers.

## 4. A concrete higher-rank boundary

At q=2, m=3, k=2 there are 42 full-row-rank top frames. Six have a zero
shared column. Formula (1) gives failure probabilities 3/7, 5/7 and 1 for
budgets one, two and three. In particular two candidates give 5/7, whereas
twice the single-test rate is 6/7 and the conditional linear-only rate is
2/3. The common failure event must be counted once, and cannot be omitted.
Every frame has four GL_3(F_2) completions, so the corresponding literal
invertible-matrix counts are 72, 120 and 168 out of 168.

At q=3, m=3, k=2 the rates are 4/13, 7/13, 10/13 and 1. These are examples
of the theorem's new shared-column contract, not measurements of the
selected stopped producer.

## Scope and credit

The original step is the higher-rank shared-prefix reduction, its exact
common-deficiency term, and the resulting sharp formula (1). ywz65's
PR #2601 supplies the bounded-choice interface, projective-pencil formula
and higher-rank-intersection question. Adam Gall's PR #2097 supplies the
fresh-row versus current-dependent-selection boundary, with its retained
three-stage-cover, eumemic source527, Rohan Arun, Jeremy Kothe and PR589
lineage. Matrix completion counts and projective pencils are classical.
No general literature-priority claim is made for these counting methods.

No actual selected candidate family, eligible-prime proof, current-field
transcript, physical selector, routing, dirty restoration, complete paid
invoice or all-size supplier is supplied. The selected five framework
assumptions remain. This is a scoped written proof with finite exact
corroboration, with no new kappa or complete multiplication theorem.
Independent human and formal proof-kernel review are unclaimed.
