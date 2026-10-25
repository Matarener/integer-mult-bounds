# A reusable full-root union bound for two seven-flats

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.

This is a written binary-quadratic lemma. The quadratic model and
ambient positive Gauss sign are those of the retained
`p112-six-seven-supplement/PROOF.md`, Sections 1--2. The exact finite corroboration is recorded separately in RESULT.json.

## Statement

In the eight-dimensional plus-type quadratic space (V,q) over F2, call the
120 points q(x)=1 full roots. An affine six-flat contains 24, 28, 32, or 36
full roots. Any two affine six-flats contain at most 68 full roots in their
union. If both contain 36 roots and are distinct, their common full-root
count belongs to {6,10,12,20}; in particular their union has at most 66.

Consequently the 68 union bound holds for any two binary support-label spaces
of rank at most 7 in F2 direct-sum V, with root labels (1,x). If their union
contains s distinct excluded frame labels, their LIVE union has at most 68-s
sites. Two arbitrary seven-flats and at most 7 extra sites cannot cover a
genuine two-axis frame normal, whose retained live support minimum is 76.

## 1. Character sums and six-flat cardinalities

Let B be the nondegenerate polar form of q, and retain

    sum_(x in V) (-1)^q(x)=16.

Translation gives the ambient Walsh identity

    sum_(x in V) (-1)^(q(x)+B(v,x))=16*(-1)^q(v).        (1)

Let W be an m-dimensional linear space of normal vectors and lambda a
linear functional on W. Nondegeneracy of B makes the affine system

    A(W,lambda)={x : B(w,x)=lambda(w), every w in W}

consistent, of dimension 8-m. Character orthogonality and (1) give

    S(A):=sum_(x in A) (-1)^q(x)
      =2^(-m) sum_(w in W) (-1)^lambda(w)
                     sum_(x in V) (-1)^(q(x)+B(w,x))
      =2^(4-m) G(W,Q),                                (2)

where Q=q+lambda on W and G(W,Q)=sum_W(-1)^Q. The root count in A is
(2^(8-m)-S(A))/2.

For an affine six-flat, m=2 and W=E is a two-plane. If E has zero polar
form, Q is linear; its Gauss sum is 0 or 4. Equation (2) gives S=0 or 16,
so the root counts are 32 or 24. If E is nondegenerate, a binary quadratic
form on E has Gauss sum +2 or -2; the root counts are 28 or 36.

The 36 case occurs exactly when Q takes value 1 on all three nonzero
vectors of E. Thus its affine six-flat is uniquely characterized by

    B(v,x)=q(v)+1 for every nonzero v in E.             (3)

These three prescribed values define one linear functional precisely
because E is nondegenerate: if its independent vectors are a,b, then
q(a+b)+1=q(a)+q(b) when B(a,b)=1. No coset enumeration or Arf invariant
is needed for this uniqueness statement.

## 2. Two maximal sections: explicit radical bound

Let A,A' be 36-root sections, with their nondegenerate normal planes E,E'.
If E=E', uniqueness in (3) makes A=A'. Otherwise, their normal equations
agree on E intersect E' by (3). They therefore define a linear lambda on
W=E+E', and A intersect A'=A(W,lambda) is nonempty. Put m=dim W, equal
to 3 or 4, and Q=q+lambda on W. Both restrictions Q|E and Q|E' take
value 1 on all three nonzero vectors.

Here is the exact quadratic Gauss bound, including its radical dependence.
For R=rad(B|W) of dimension t, changing variables y=x+r gives

    G(W,Q)^2
      =sum_(x,r in W) (-1)^(Q(x)+Q(x+r))
      =sum_(r in W) (-1)^Q(r) sum_(x in W) (-1)^B(x,r)
      =2^m sum_(r in R) (-1)^Q(r).                     (4)

Q is linear on R. If this linear form is nonzero, G=0. If it vanishes,
|G|=2^((m+t)/2). W contains a nondegenerate two-plane, so t<=m-2.
For m=3, necessarily t=1; for m=4, t is 0 or 2. Equation (2) therefore
gives |S(A intersect A')|<=8 in every case. The root intersection is
at least 12 when m=3 and at least 4 when m=4. This already proves the
conservative 68 union bound used by the invoice arguments.

The perpendicular affine direction W-perp has the SAME radical R:
rad(W-perp)=W-perp intersect W=rad(W). Thus the equivalent direct
affine-character-sum derivation has exactly the same radical dimensions;
there is no omitted nondegeneracy assumption on the common direction.

## 3. Sign refinement: intersections are 6, 10, 12, or 20

If W is nondegenerate, m=4 and G(W,Q)=+4 or-4 by (4). Equation (2)
gives S=+4 or -4, hence 6 or 10 common roots.

Otherwise B|W has rank 2. Split W=E direct-sum R, with E perpendicular
to R. The projection E'->E is an isomorphism: its kernel is E' intersect
R, zero by nondegeneracy of E'. Thus E' is the graph of a linear map
f:E->R. Since W=E+E', the image of f is all of R. For every nonzero
y in E, both Q(y) and Q(y+f(y)) equal 1 by (3), and B(y,f(y))=0.
Consequently Q(f(y))=0. Surjectivity of f proves Q|R=0.

Therefore

    G(W,Q)=|R|*G(E,Q|E)=-2^(t+1).

For m=3,t=1, (2) gives S=2*(-4)=-8, so the common root count is 20.
For m=4,t=2, (2) gives S=-8, so the common root count is 12. This
excludes the apparent 4-root case from the unsigned estimate. The exact
36-root-pair lower bound is 6, and its corresponding union upper bound
is 66. This statement does not assert a 66 bound for mixed 32/36 sections.

## 4. Arbitrary seven-flats and puncturing

For any two affine six-flats, if one has at most 32 roots, their union
has at most 32+36=68. Otherwise both have 36 roots and Section 3 gives
the stronger 66 bound. Thus 68 holds uniformly. Smaller nonempty affine
sections can be enlarged to dimension 6; a rank-seven label space with
no leading-one section contains no root labels. This proves the
rank-at-most-7 version of the statement.

Excluded frame labels are among the FULL roots counted in this union.
Subtracting s distinct excluded labels gives the claimed LIVE bound 68-s,
independently of piece coefficients, overlaps, or cancellation. This
finite binary lemma is uniform in the characteristic-zero coefficient
field used for the actual codeword expansions.

The exact checker `flat_union.py` enumerates the 5,440 maximal sections and
all 14,794,080 unordered distinct pairs. Its pair-union statistic refers
only to 36-root sections; universal 68 coverage additionally uses the full
43,180-section count spectrum. The 255 rank-seven spaces contained in
tau=0 have empty root section and complete the 43,435 nine-bit subspaces.

## 5. The universal 68 bound is sharp

In canonical plus coordinates q(x)=x0*x1+x2*x3+x4*x5+x6*x7, choose
isotropic a=e0,b=e1,c=e2. Then B(a,b)=1 and c is perpendicular to a,b.
The section A={B(a,x)=1,B(b,x)=1} has 36 roots: its normal plane is
hyperbolic and q+lambda is anisotropic. The section
A'={B(a,x)=0,B(c,x)=1} has 32 roots: its normal plane is totally singular
and q+lambda is a nonzero linear form. The opposite B(a,x) equations make
A and A' disjoint. Thus their full-root union attains 68. Both root-label
sets have rank 7, since their sizes exceed the rank 6 capacity 20 and each
lies in a rank 7 label flat.

Equivalently A fixes x0=x1=1, leaving 36 zeros of the plus6 quadratic;
A' fixes x1=0,x3=1 and x2=1+x4*x5+x6*x7, with x0 free, giving 32 roots.
This is full-root sharpness, not invoice sharpness. flat_union.py also
materializes this construction directly in its independently reconstructed
E8 model, retaining normal equations and both 120-bit root masks.

The separate canonical_union.py imports no E8 model. It repeats the complete
section and maximal-pair inventories directly in canonical plus coordinates,
computes the two sharp-fixture binary ranks independently, and rejects a
wrong coset even when both section sizes and ranks stay unchanged. Both
engines' spectra are compared by the registered replay. This computational
cross-check is separate from the written universal character-sum proof.
