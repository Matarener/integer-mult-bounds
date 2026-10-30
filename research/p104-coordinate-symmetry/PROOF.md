# Exact coordinate symmetry and its frame quotient

This is a source-specific finite group certificate followed by a scoped
counting proof. All vector spaces in this note are over F2. No physical
supplier theorem follows from these statements.

## The coordinate group

Let P be the set of 104 nine-bit integers in the pinned `ports.json`.
A coordinate permutation sends bit i to bit pi(i), with zero-based indices.
Let G consist of the permutations pi in S9 for which pi(P)=P.

**Finite certificate.** G has exactly two elements. Its nonidentity element is

    sigma = (0 3)(2 8)(4 7)(5 6),

and coordinate 1 is fixed. In image-list notation this is
`[3,1,8,0,7,6,5,4,2]`.

Here is the complete finite reduction used by the checker. Every member of P
has weight three or seven. Among all weight-three masks the missing masks are

    7,25,42,52,67,76,82,97,104,137,162,266,289,448.

Among all weight-seven masks the missing masks are `127,491`. A coordinate
permutation preserves weight. It preserves P if and only if it preserves both
of these missing sets. The checker visits every one of the 9! permutations.
Exactly 960 preserve the weight-seven missing set, and exactly identity and
sigma also preserve the weight-three missing set. For each survivor it also
checks the image of every original port. This is an exhaustive certificate,
not a computer-free proof of the two-survivor step.

The 960 count also has a direct check. The complements of the two missing
weight-seven masks have supports `{7,8}` and `{2,4}`. Their setwise stabilizer
has size `2! * 2! * 2! * 5! = 960`. The first two factors exchange the ends of
the two pairs, the third exchanges the pairs, and the last permutes the other
five coordinates.

The induced port action has eight fixed ports

    11,98,146,251,262,367,415,502,

and 48 two-element orbits. Hence the exact port quotient has 56 elements.
These are binary coordinate symmetries of this literal label set. They are
not the full root-system symmetry group or the full binary linear stabilizer.

## Invariant frames of an involution

The following elementary counting argument is included to state exactly what
the finite computation implies for every frame dimension. Gaussian binomial
coefficients and the orbit-counting lemma are classical; the contribution is
the exact application to this pinned P104 coordinate action.

Let V have dimension n, let N:V->V satisfy N^2=0, and put
`a=rank N`, `h=n-a`. Write `[b choose c]_2` for the number of c-dimensional
subspaces of F2^b, and zero when c is outside `0..b`. The number of
k-dimensional subspaces U with N(U) contained in U is

    f(n,a,k) = sum_r [a choose r]_2 [h-r choose k-2r]_2
                     * 2^(r*(h-k+r)),                         (1)

where the sum includes just `0<=r<=min(a,floor(k/2))` and `k-r<=h`.

To prove (1), set `R=N(U)` and `S=U intersect ker N`, so `dim R=r` and
`dim S=k-r`. Invariance is exactly the additional inclusion R contained in S.
First choose R inside im N, in `[a choose r]_2` ways. Since im N is contained
in ker N, choose S containing R inside the h-dimensional ker N, in
`[h-r choose k-2r]_2` ways.

For a fixed R,S, the map from `N^-1(R)/S` to R induced by N is onto, with
kernel `ker N/S` of dimension `h-k+r`. Each admissible U/S is the image of a
linear section of this map, and every section gives an admissible U. A fixed
section identifies the remaining sections with
`Hom(R,ker N/S)`, which has `2^(r*(h-k+r))` elements. A section is uniquely
determined by its image because N restricts to its inverse there. This also
proves there is no overcount. Multiplying and summing proves (1).

For sigma above, put N=sigma+I. Each of the four exchanged coordinate pairs
contributes one rank to N, and the fixed coordinate contributes zero. Thus
N^2=0, a=4 and h=5. A frame is sigma-invariant exactly when it is N-invariant.
Formula (1) gives the fixed-frame profile, in dimensions zero through nine,

    1,31,395,1955,4371,4371,1955,395,31,1.                       (2)

Every frame that is not fixed has a two-element orbit. Consequently the exact
number of coordinate-symmetry orbits on k-frames is

    ([9 choose k]_2 + f(9,4,k)) / 2.                           (3)

The checker independently enumerates every reduced binary basis in every
one of these ten Grassmannians, tests sigma-invariance directly and compares
the resulting counts to (1). The proof of (1) does not depend on this census.

For planes, `[9 choose 2]_2=43435` and `f(9,4,2)=395`, so (3) is **21915**.
The 395 fixed planes split as 155 planes contained in ker N and 240 planes
with rank-one N restriction. This split also follows immediately from (1).

## What the result excludes, and what it permits

Any quotient based only on coordinate permutations preserving all literal
ports has equivalence classes of size at most two. A more constrained caller
or frozen word may have fewer symmetries. For the pure plane search, the
exact reduction is 43435 candidates to 21915 representatives. This is a count
of equivalence classes, not a wall-time guarantee or a proof that a particular
caller permits the nonidentity relabeling.

Global invariance does allow proper frames. For example, the line generated
by port 11 is fixed, and the plane spanned by masks 1 and 8 is fixed while
neither generating line is fixed. The symmetry hypothesis alone therefore
cannot force a shared frame to have dimension nine. Equation (2) gives its
precise finite admissible-space counts. It does not decide productive target
capacity, chronology, physical delivery or restoration on any of those spaces.

Larger binary linear maps, signed root maps in another coordinate system,
multiple frames permuted by a group, changed port sets and nonsymmetric words
are outside the coordinate-permutation contract. The result is not an
obstruction to those routes or a universal bound on P104 helper constructions.
