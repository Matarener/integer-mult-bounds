# A sharp COPY floor for two singleton outside directions

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
This is a written corollary of the uniform theorem; full proof-assistant
verification is not claimed.

## 1. Statement and inputs

Let K be any field of characteristic different from two. Let L be the 120
standard E8 root lines with oriented norm-two representatives r_x over
Z[1/2], and retain their fixed binary labels u_x in Lambda=F2^9. Their
nondegenerate binary pairing beta gives the dense table B_d. Put

```text
E(h)=(r_x dot h)_{x in L},       C=E(K^8),
G[x,y]=r_x dot r_y,             N0=G/2,
U(p)=span_F2{u_x:p(x)!=0},      Z(p)=U(p)^perp,
w(p)=dim U(p),                 delta(p)=9-w(p).
```

For distinct lines a,b let delta_a,delta_b be the coordinate unit vectors,
and set S=C+span_K(delta_a,delta_b).

**Theorem.** For any finite m, if P,Q in K^{L x m} satisfy

```text
P Q^t=N0,       col(P) subset S,       col(Q) subset C,
```

then COPY(P,Q)>=72, where each term costs the binary pairing rank
rho(supp p_i,supp q_i)=rank_F2 B_d[supp p_i,supp q_i]. The floor is sharp,
including an actual rank-(10,8), ten-term factorization. The transposed
statement holds as well. Transposes are ordinary transposes over every K.

The inputs are the uniform deficiency theorem and annihilator argument in
[PROOF.md](PROOF.md)
section 5, extended to these fields in section 8. Every nonzero codeword
has weight nine. For any lambda outside C, a finite nonproportional family
in C+K lambda has total deficiency at most nine. Moreover, for distinct
normalized outside vectors p=lambda+E(h), p'=lambda+E(h'), their
annihilators have trivial intersection and are beta-orthogonal: every
nonzero cross-pair is compatible, so finite fact 2 applies. The root-hole
support calculation below also occurs in PROOF.md section 7.1.

## 2. Independence and the singleton classification

The evaluation map E is injective: standard roots include the orthogonal
frame e_0+e_1,e_0-e_1,...,e_6+e_7,e_6-e_7 of determinant plus or minus 16.
Distinct standard root lines remain nonproportional over K. Pair roots
have support two and half-roots have support eight. Within either type,
comparison at a nonzero coordinate forces proportionality scalar +1 or
-1; odd characteristic preserves all distinct sign patterns. Thus
E(r_a),E(r_b) are independent. This avoids a Gram-determinant argument,
which would fail for nonorthogonal roots in characteristic three.

Write u=u_a, v=u_b. Distinct root lines have distinct nonzero binary labels,
so u!=v and they are independent over F2. Put D=span_K(delta_a,delta_b).
A nonzero vector in D
has binary weight one or two, so D intersect C=0 and dim S=10.

Because E(r_a)_a=r_a dot r_a=2, define the singleton hole

```text
A=delta_a-E(r_a)/2,        B=delta_b-E(r_b)/2.
```

The support of A is exactly the nonorthogonal-to-r_a roots with line a
omitted. Its labels lie in u^perp. Adding u restores the support of the
nonzero codeword E(r_a), whose label span is Lambda. Hence U(A)=u^perp,
w(A)=8 and Z(A)=F2 u. This calculation survives every characteristic
different from two: at line a the product r_a dot r_a is 2 and is exactly
cancelled; at every other nonorthogonal line the product is +1 or -1 and
remains nonzero. Similarly
w(B)=8 and Z(B)=F2 v.

The vectors delta_a and A are nonproportional and have deficiencies eight
and one. They saturate the uniform budget in C+K delta_a. Therefore they
are the only positive-deficiency projective rays in that extension.
Likewise delta_b and B are the only such rays in C+K delta_b.

## 3. Classification in a mixed singleton direction

Fix s,t in K nonzero and lambda=s delta_a+t delta_b. Since D intersect C=0,
lambda is outside C. Its support has label span W=span_F2(u,v), so

```text
delta(lambda)=7,       Z(lambda)=W^perp.
```

Consider any other positive-deficiency ray in C+K lambda. It has a unique
representative p=lambda+E(h), different from lambda; codewords themselves
have deficiency zero. The annihilator properties in section 1 imply

```text
Z(p) subset Z(lambda)^perp=W,       Z(p) intersect W^perp=0. (1)
```

First suppose the scalar root lines a,b are nonorthogonal. Then
beta(u,v)=0, while beta(u,u)=beta(v,v)=1. Put

```text
p_a=lambda-(s/2)E(r_a)=sA+t delta_b,
p_b=lambda-(t/2)E(r_b)=s delta_a+tB.
```

The first vector vanishes on O_u={x:beta(u,u_x)=1}: its entry at a cancels,
all other roots there are orthogonal to r_a, and b is not there. Thus
u belongs to Z(p_a). Similarly v belongs to Z(p_b). Both deficiencies
are at least one. These vectors and lambda are nonproportional: their
quotient coefficients modulo C are all one, and E(r_a),E(r_b) are
independent. Their deficiencies sum to at least 7+1+1=9. The uniform
theorem forces both new deficiencies to equal one and excludes every
other positive-deficiency ray in C+K lambda.

Now suppose the root lines are orthogonal, so beta(u,v)=1. On W the
pairing matrix is [[1,1],[1,1]], with radical F2(u+v)=W intersect W^perp.
By (1), a nonzero Z(p) must have dimension one and generator u or v.
Suppose it is u; the other case is symmetric. The vector

```text
p'=p-sA=t delta_b+E(h+(s/2)r_a)
```

still vanishes on O_u. It is nonzero and outside C, because t!=0 and
delta_b is outside C. It is therefore a positive-deficiency vector in
C+K delta_b and must be proportional to delta_b or B by section 2.
But delta_b does not vanish on O_u, since beta(u,v)=1; and B has
annihilator F2 v, which does not contain u. This contradiction proves
that lambda itself is the only positive-deficiency ray in this case.

## 4. Filtered spans and the basis bound

Every nonzero p in S is a codeword or lies in one of the quotient
directions just classified. Consequently

```text
{p in S:w(p)<=7} subset D,
{p in S:w(p)<=8} subset H=D+span_K(E(r_a),E(r_b)).
```

The first set spans D, and the second spans H because it contains
delta_a,delta_b,A,B. Thus these filtered spans have dimensions two and
four respectively; dim H=4 follows from D intersect C=0 and the root
independence proved above. The weight-one vectors also span D.

Any ten-vector basis of S therefore contains at most two vectors of
weight at most seven and at most four of weight at most eight. Nonzero
vectors have weight at least one. Its ordered weights are bounded below by

```text
(1,1,8,8,9,9,9,9,9,9),       sum=72.                    (2)
```

## 5. Every finite exact factorization and sharpness

Delete terms with a zero factor. Each remaining q_i is a nonzero codeword,
so U(q_i)=Lambda and its term costs exactly w(p_i). Exactness implies
C=col(N0) subset col(P): the standard root matrix is injective and its
transpose is surjective, so N0 has rank eight and image C.

If the remaining P has rank at most nine, the rank-at-most-nine
floor applies, since Q has rank eight. Otherwise its rank is ten and its
columns span S. Choose a ten-column basis subset. Its weights sum to at
least 72 by (2); all other costs are nonnegative. This proves the theorem,
including rank drops caused by deleting zero-reader columns.

### 5.1 Equality survives proportional normalization

The sheared variant below was suggested and computationally checked in the
local Claude Fable 5.1 AI-assisted audit; this is not human peer review.

Extend h_1=r_a,h_2=r_b to any basis h_1,...,h_8 of K^8, and let d_1,...,d_8
be its dot-product dual. Such an extension exists also in characteristic three:
the two root representatives are independent, as proved in section 2; a
two-root Gram determinant is not needed. Put

```text
A=delta_a-E(h_1)/2,       B=delta_b-E(h_2)/2,
y_3=E(h_3)+delta_a,       y_4=E(h_4)+delta_b,

P=(delta_a,delta_b,A,B,y_3,y_4,E(h_5),...,E(h_8)),
Q=(E(d_1-d_3/2),E(d_2-d_4/2),-E(d_1),-E(d_2),
   E(d_3)/2,E(d_4)/2,E(d_5)/2,...,E(d_8)/2).
```

Every P column lies in S=C+span_K(delta_a,delta_b). The unsheared columns
delta_a,delta_b,A,B,E(h_3),...,E(h_8) form a basis of S: their span contains
delta_a,delta_b and E(h_1),...,E(h_8), while dim S=10. Adding delta_a to
E(h_3), and delta_b to E(h_4), are invertible column operations. Hence the
displayed P has rank ten, all its columns are nonzero, and they are pairwise
nonproportional.

The two modified columns still have weight nine. By section 2, the only
positive-deficiency rays in C+K delta_a are delta_a and A. The normal h_3
is independent of h_1, so y_3 is proportional to neither: comparison modulo
C would force the proportionality coefficient to be one, and then would
force h_3=0 or h_3=-h_1/2, respectively, by injectivity of E. Thus w(y_3)=9.
The same argument with h_4,h_2 gives w(y_4)=9. The full P weight list is
therefore

```text
(1,1,8,8,9,9,9,9,9,9),       sum=72.
```

For the Q columns, use the dual basis as coordinates. Their normal supports
are respectively

```text
{1,3}, {2,4}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}.
```

Every displayed coefficient is nonzero in characteristic different from two.
These supports are nonempty and distinct, so these normals are nonzero and
pairwise nonproportional. Injectivity of E gives the same facts for Q. Its
last eight normals, -d_1,-d_2,d_3/2,...,d_8/2, form a basis, so rank Q=8.
Every reader is a nonzero codeword and has binary support weight nine.
Consequently the actual binary pairing rank of each term equals the weight
of its P column, and COPY=72.

Exactness follows directly by grouping terms:

```text
PQ^t
 = (delta_a-A)E(d_1)^t + (delta_b-B)E(d_2)^t
   + (y_3-delta_a)E(d_3)^t/2
   + (y_4-delta_b)E(d_4)^t/2
   + sum_{j=5}^8 E(h_j)E(d_j)^t/2
 = sum_{j=1}^8 E(h_j)E(d_j)^t/2 = G/2 = N0.
```

Neither zero-term deletion nor proportional-factor merging on either side
can change this factorization: all ten terms are active and both factor
families are pairwise nonproportional. Thus the rank-(10,8) equality example
already survives that normalization. These statements use no characteristic
restrictions beyond 2 being invertible and apply to both orthogonal and
nonorthogonal a,b.

The unsheared fixture retained in `sparse_pair.py` is a useful positive control:
remove the added units from y_3,y_4 and restore the first readers E(d_1),E(d_2).
Its two pairs of proportional readers merge to eight code-code terms of ranks
(8,8), with COPY still 72. The finite verifier retains those six controls
and adds the sheared construction for both pair types over F3, F5, F7. Each
new fixture checks all 14,400 product entries, actual binary term ranks,
scalar factor ranks, active terms, both families' proportionality, and the
result of an independent proportional normalizer. Omitting the compensating
changes to the first two readers is explicitly rejected by the product check:
its product error is

```text
(delta_a E(d_3)^t + delta_b E(d_4)^t)/2 != 0.
```

The two nonzero rows lie at distinct coordinates a,b, so the error cannot
cancel in any permitted characteristic. The finite fixtures do not exhaust
F5 or F7 or all root pairs; the argument above supplies the universal claim.

The theorem concerns the specific space C+span(delta_a,delta_b) and exact
N0 on full E8, with fixed B_d. It makes no assertion for arbitrary two
outside directions, all rank-ten factors, masked identities, punctures,
or a physical multiplication construction.

## 6. Relation to earlier singleton and root-swap work

DreamingOfClouds's [PR2816](https://github.com/CrocSwap/integer-mult-bounds/pull/2816),
`research/one-sided-decoders-all-m/README.md` sections 5.2, 6 and 9, already
analyzes singleton root swaps and `T=span(delta_t,delta_u)` in the P112
characteristic-zero, low-excess correction programme. Those geometric
observations are antecedents, not discoveries claimed here. The floor of 68 in PR2862 is a historical
full-E8 lift baseline, rather than the current status of the one-sided programme. The present statement is full E8, all finite
term counts and every characteristic different from two, in the explicitly
restricted coordinate-pair extension. Its proof uses the uniform theorem
directly, without importing their correction, minimum-basis or survivor-list
hypotheses. These results do not supply a general one-sided rank-ten floor.

The relevant broader programme is **L120**, the basis-cost bound for every
scalar space containing C. PR3074 states its sufficiency for the one-sided
problem, and PR3154 separates that B-prime node from the two-sided C-prime
node. Draft PR3191 claims completion of its one-sided ledger conditional on
an implementation slot that remains unfilled at head `9c9e094`; conorholds'
PR3166 supplies its C7 branch. In characteristic zero a completed L120 proof
would imply the present sparse-pair corollary. Here this dimension-ten case
is proved directly, in every characteristic different from two, without that
conditional chain. The main new theorem of the package is the arbitrary-family
one-coset budget; its genuinely two-sided application is the rank-(9,9) cell.
