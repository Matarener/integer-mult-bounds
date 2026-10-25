# Coupling a singleton encoder to an actual reader basis

All vector spaces in this file use ordinary transpose, not conjugate transpose.
Delete terms with a zero scalar factor before taking any **actual** factor
space, rank or term count below. Thus all listed factors are scalar-active.
This is essential: a zero encoder could otherwise inflate a reader rank at
zero cost. Raw ambient-inclusion statements allow this initial deletion.
Let E be the 120 E8 root lines, with norm-two rational representatives r_x.
Use the fixed nine-bit dense-COPY labels u_x and nondegenerate dot pairing β.
Define

```
E(h)_x = r_x·h,      C=E(K^8),      N0[x,y]=(r_x·r_y)/2,
U(q)=span_F2{u_x:q(x)≠0},           w(q)=dim U(q),
D_A=span_K{δ_a:a∈A},
H_v={x:β(u_v,u_x)=0},              O_z={x:β(z,u_x)=1}.
```

The binary tariff is fixed before scalar reduction:
B[x,y]=(1+integerGram[x,y]) mod 2. Thus β(u_x,u_y)=1 precisely for
x=y or scalar-orthogonal distinct roots. COPY is the sum of binary ranks
ρ(p,q)=rank B[supp p,supp q] over all scalar-active terms.

## 1. Theorems and inherited inputs

The COPY consumers below are conditional on the retained written premises
from pending same-author PR3755, identified in this section. Pinning its
sources and checking its finite rank certificate do not independently
validate the singleton, low-rank and coordinate-pair proofs.

**Theorem C (all full coordinate extensions).** In characteristic zero,
if scalar-active PQ^t=N0, col(P)⊂C+Kδ_v, and the actual col(Q)=C+D_A for any A⊂E,
then COPY≥72, provided each of the two exceptional P rays below occurs
at most once. Pairwise nonproportional P columns suffice. Q columns may repeat.

**Theorem P (raw coordinate pair).** Over every field of characteristic
other than two, the same floor holds for raw factors satisfying
col(P)⊂C+Kδ_v and col(Q)⊂C+span(δ_a,δ_b), for any two distinct a,b.
No normalization hypothesis is needed in this statement.

The target has image C and rank eight. The retained pending PR3755 source
at 9ab51a1a supplies the singleton classification: every nonzero C word
has full binary span; the only deficient rays in C+Kδ_v are

```
e=δ_v,          J=δ_v−E(r_v)/2,
U(e)=F2 u_v,    U(J)=u_v^⊥,       β(u_v,u_v)=1.
```

These inputs hold in every odd characteristic, by its unit-minor/root-label
certificate and written field argument. Their exact proof/code bytes are
retained under vendor/pr3755 and authenticated by REFERENCES.json. Replaying
that certificate is not a new independent proof of its whole written theorem.

In characteristic zero the following inputs are used. FINITE.md explains
the root-system and quadratic arguments; verify.py recomputes their finite
inventories. The root rank capacities are (0,1,3,6,12,20,36,63,120), so
a nonzero codeword has support at least 57. A nonroot scalar normal has
at most 42 zero root lines. The nonzero binary cuts O_z have sizes 56,64,120.
Consequently deleting at most 13 coordinates cannot make a nonroot evaluation
deficient. The 56 nonself nonorthogonal roots at any a span u_a^⊥ and
have minimum nonzero character support 24. These are the global root-only
and remainder inputs of PR3166/PR968/PR1071, not new geometry here.

For the full-coordinate theorem, sections 3–5 establish every actual
bill-72 basis's cut structure for |A|≤8. Section 7 uses a strict basis floor
for every larger A. EXTENSIONS.md gives the new partial-quotient consumers.

## 2. A reusable abstract coupling lemma

Let a finite coordinate set I carry distinct nonzero labels in an
h-dimensional nondegenerate binary space `(Λ,β)`. Define U, w, and COPY
using these labels. Let `C⊂K^I` have dimension d and let `e=δ_v` lie outside
C. Write `u=u_v`, assume `β(u,u)=1`, and suppose there is a vector
`J∈C+Ke` with quotient coefficient one, `U(J)=u^⊥`, such that the only
projective nonzero vectors in `C+Ke` whose support span is not Λ are e and
J. Put `H={x:β(u,u_x)=0}`.

Let S contain the actual reader columns, and let L be an integer. Assume:

* Every basis B of S has `Σ_{b∈B}w(b)≥L`.
* For every actual basis B of S attaining L and every b∈B,
  `u∈U(b)` implies that its coordinate functional λ_b vanishes on
  `S∩K^H`.

Then any exact factorization

```
P Q^t=M,       col(M)=C,       col(P)⊂C+Ke,       col(Q)=S,
```

with finitely many nonzero scalar-active columns and at most one P column
on each exceptional ray e,J has `COPY≥L`. Pairwise nonproportionality of
P is sufficient but is not required for its other columns. There is no
nonproportionality assumption on Q. No transpose-image or entrywise formula
for M is needed.

The equality cut hypothesis is automatic if `S∩K^H` is spanned by those
actual basis members that are themselves supported on H. Indeed such a
member has U contained in `u^⊥`, which cannot contain u because
`β(u,u)=1`. This is a statement about every actual equality basis, not the
existence of one adapted basis.

### Proof

For every reader q, the three kinds of encoder columns have exact costs

```
U(p)=Λ:           ρ(p,q)=w(q),
p=e:              ρ(e,q)=θ(q):=[supp(q) is not contained in H],
p=J:              ρ(J,q)=w(q)−ε(q),   ε(q):=[u∈U(q)].     (3)
```

The second formula is the rank of a one-row pairing. For the third, the
kernel of `U(q)→(u^⊥)*` is `U(q)∩F2u`, whose dimension is ε(q).
These identities include zero binary cost and do not delete scalar-active
terms. Column rescaling, with the inverse rescaling on its reader,
preserves supports, ranks, actual spans, exactness and costs. Normalize a
present exceptional encoder to exactly e or J.

Let `χ:C+Ke→K` annihilate C and have χ(e)=1. Then χ(J)=1 and exactness gives

```
Σ_i χ(p_i)q_i=0.                                        (4)
```

Write r=dim S. If e is absent, there is at most one unit discount from
`Σw(q_i)`. If every P column belongs to C, there is no exceptional column
and a basis subset of Q proves the bound. Otherwise exactness gives
`C⊂col(P)` and hence `rank P=d+1`. Sylvester's inequality gives `m≥r+1`:
`d=rank M≥rank P+rank Q−m=d+1+r−m`. A basis subset of Q costs at least L,
and each additional nonzero reader has weight at least one. Thus
`Σw(q_i)≥L+1`, which pays the possible J discount.

Now let e occur with reader q_0. Equation (4) shows that every reader except
q_0 still spans the actual S. Their total weight is at least
`L+(m−1−r)`. Equation (3) gives

```
COPY = Σ_{i≠0}w(q_i) − ε(q_J) + θ(q_0),                 (5)
```

where ε(q_J)=0 when J does not occur. A bill below L can therefore occur
only if all the following hold simultaneously:

```
m−1=r;
B=(q_i)_{i≠0} is the actual basis and has weight sum L;
J occurs, u∈U(q_J), and q_0∈S∩K^H.                       (6)
```

The q_J coordinate of (4) is `λ_J(q_0)=−1`, whereas the equality cut
hypothesis makes that coordinate zero. This contradiction proves the
lemma. The quotient relation alone suffices; no dual-root normalization or
row-v equation is used in this abstract argument.

### Strict-floor corollary

If every basis of the actual S has weight sum at least `L+1`, the same
conclusion `COPY≥L` holds with no equality cut hypothesis. In the e-present
case, the other readers span S and cost at least `L+1`; the possible J
discount is only one. In the e-absent case the same sum bound suffices.
In particular any verified strict one-sided floor 73, for an arbitrary
actual right space S containing C, immediately gives this coupled floor
72. This statement is broader than full coordinate extensions.

For E8 take h=9,d=8,L=72,e=δ_v,J=δ_v−E(r_v)/2 and M=N0. If the stronger
scalar identity is useful for an independent check, the critical actual
basis also satisfies

```
λ_J(E(h))=−r_v·h.                                       (7)
```

Indeed write `p_i=E(h_i)+c_iδ_v`; the C component of the exact identity is
`Σ_i E(h_i)q_i^t=N0`. With h_0=0, injectivity and transposition give
`E(h)=2Σ_{i≠0}(h_i·h)q_i`. Since the normalized J column has
`h_J=−r_v/2`, its coordinate is exactly (7). This checks both the minus
sign and factor two; neither is an extra hypothesis of the lemma.

## 3. All corrected vectors of weight at most eight for |A|≤8

Set `a=|A|≤8` and `S=C+D_A`. Since every nonzero codeword has binary weight
nine while a vector in D_A has binary weight at most a, `C∩D_A=0` and
`dim S=8+a`. Each q has a unique decomposition `q=E(h)+d`, d∈D_A.

Suppose h is nonzero and w(q)≤8. Restricting outside A shows that deleting
at most eight coordinates from E(h) reduces its label span to at most
eight. The global root-only input makes h proportional to a root, say
`h=c r_t`, c≠0. The 56 nonself nonorthogonal coordinates, after deletion
of at most eight members, still span `u_t^⊥` by the 24-character-support
bound. Thus

```
U(q)=u_t^⊥,               w(q)=8.                        (8)
```

Its own label u_t is outside this hyperplane. Its entry must cancel:
`0=q(t)=2c+d(t)`. Consequently t∈A and d(t)=−2c. Every other coordinate
x orthogonal to r_t also has u_x outside this hyperplane, and E(h)(x)=0,
so d(x)=0. Conversely, corrections at nonorthogonal lines have labels in
`u_t^⊥`, and at most eight deletions cannot destroy its span. Therefore the
complete, coefficient-sensitive classification is

```
q=c(E(r_t)−2δ_t)+d',
t∈A, c≠0,   d'∈span{δ_x:x∈A∩H_t}.                      (9)
```

Here t itself is not in H_t because β(u_t,u_t)=1. Every displayed vector
has weight exactly eight. In particular every vector of weight at most
seven is in D_A, and the normal directions of weight-eight nonpure vectors
are precisely roots indexed by A. This is a classification of all actual
vectors; no minimizing-basis choice has been made.

## 4. Basis lower bound and complete equality structure

Let `s=rank_K{r_t:t∈A}`. By (9), the span of all weight≤7 vectors is D_A,
of dimension a. The span of all weight≤8 vectors is

```
F8=D_A+E(span{r_t:t∈A}),        dim F8=a+s.               (10)
```

The equality follows because all δ_t have weight one and all
`E(r_t)−2δ_t` have weight eight. Every actual basis of S therefore has
weight sum at least

```
a·1+s·8+(8−s)·9 =72+a−s.                               (11)
```

For a direct counting proof, at most a independent basis members can have
weight≤7, and at most a+s can have weight≤8. If n7 and n8 denote these
counts, a basis of dimension 8+a has sum weight at least
`n7+8(n8−n7)+9(8+a−n8)=72+9a−7n7−n8`, which is minimized at
`n7=a,n8=a+s`, giving (11). Replacing an intermediate member by a heavier
member cannot lower this bound.

If s<a, (11) is at least 73, so the abstract coupling lemma applies
without inspecting equality bases. If s=a, the bound is 72. Any actual
basis attaining 72 must have exactly

```
a members of weight 1,
a members of weight 8,
8−a members of weight 9.                                (12)
```

Weight-one vectors are nonzero scalar coordinate units because the labels
are distinct nonzero vectors. The first group is therefore
`{α_tδ_t:t∈A}`, α_t≠0, and spans D_A. Every weight-eight member is nonpure,
as it is independent of that first group. Its scalar normal is a root
from A by (9). The a such normals must be independent and, since all roots
of A are independent, there is exactly one such member `b_t` for each
t∈A. Write it as

```
b_t=c_t(E(r_t)−2δ_t)+d_t',    c_t≠0,
d_t'∈span{δ_x:x∈A∩H_t},     U(b_t)=u_t^⊥.               (13)
```

The eight normal directions of the weight-eight and weight-nine members
form a basis of K^8, by quotienting S by D_A. This is the full equality
structure of every actual basis, including arbitrary allowed correction
coefficients in (13) and arbitrary weight-nine members. It is stronger
than exhibiting one basis with the desired weights.

## 5. The actual equality basis satisfies the cut condition

Assume a=s≤8 and let B be any actual equality basis described above.
The cut subspace has the following exact description:

```
S∩K^{H_v} = D_{A∩H_v}                              if v∉A;
S∩K^{H_v} = D_{A∩H_v}+K b_v                      if v∈A. (14)
```

Indeed any vector supported on H_v has weight at most eight. If it is
nonpure, (8) implies that its support span is `u_t^⊥` for some t∈A.
Containment in `u_v^⊥` forces equality of those two hyperplanes. The
nondegenerate binary form gives `F2u_t=F2u_v`, hence t=v. Formula (9)
then gives (14), using (13) to replace the canonical root-hole by the
actual b_v. Conversely every generator on the right is supported in H_v.

Every generator on the right of (14) is a scalar multiple of an actual
member of B supported on H_v. Such a member has binary support span
contained in `u_v^⊥`, so its span cannot contain u_v. Therefore, for every
b∈B with `u_v∈U(b)`, its coordinate functional vanishes on all of (14).
This verifies the strong equality cut condition in the abstract lemma,
without even using (7).

For a scalar-constant cross-check, suppose b is non-coordinate and obeys
(7). If v∈A, (13) gives `E(r_v)=c_v^{-1}b_v+d`, d∈D_A, while
`λ_b(E(r_v))=−r_v·r_v=−2≠0`. As λ_b vanishes on D_A, this forces b=b_v;
but then `U(b)=u_v^⊥` does not contain u_v. If v∉A, the cut is pure D_A and
λ_b already vanishes on it. For coordinate b, u_v∈U(b) forces b to be the
coordinate unit at v, and all cut generators are other basis members.
This independent cross-check yields the same conclusion.

Combining (11), (14), and the abstract coupling lemma proves

```
PQ^t=G/2, col(P)⊂C+Kδ_v, col(Q)=C+D_A, |A|≤8
                         ⇒ COPY(P,Q)≥72                 (16)
```

for every finite m and every active projectively nonproportional P family.
No assumption that the actual Q columns are initially nonproportional is
needed. If a purported counterexample reaches the critical case, exactness
itself makes all readers except q_0 an actual basis.

## 6. The all-odd coordinate-pair case

### 6.1 Two coordinate lines in every odd characteristic

Let `A={a,b}` be a two-element coordinate set with arbitrary distinct root
lines a and b. This case extends the coupled result to every field of
characteristic other than two using only source3755 SPARSE-PAIR, without
the characteristic-zero deletion census.

That source proves `C∩D_A=0`, scalar independence of r_a,r_b, the basis
floor 72, and filtered spans of dimensions two and four. Its complete
singleton/mixed-direction classification says every positive-deficiency
nonpure vector in `C+D_A` has weight eight and binary support span either
`u_a^⊥` or `u_b^⊥`, with scalar normal proportional to the corresponding
root. Consequently every actual equality basis has units at a,b and two
weight-eight nonpure members b_a,b_b, one of each root normal, followed by
six weight-nine members. This follows from actual basis independence,
not a choice of the explicit equality fixture in that source.

Normalize a nonpure member with normal c r_t, t=a or b. Its support in
`u_t^⊥` forces self cancellation `d(t)=−2c` and permits correction at the
other coordinate only when that label is in `u_t^⊥`. Thus (13) is valid
for each actual b_t in every odd characteristic. The proof of (14) now
applies verbatim using this complete pair classification. Every equality
cut is spanned by permitted actual singleton columns and, if v is one of
a,b, its matching actual b_v. The generic lemma therefore gives

```
PQ^t=G/2, col(P)⊂C+Kδ_v, col(Q)=C+span(δ_a,δ_b)
                         ⇒ COPY(P,Q)≥72
```

for every finite m and every char K≠2 under the unique-exceptional-ray
condition. No dot-product Gram determinant is used to establish root
independence: that determinant can vanish at characteristic three for a
nonorthogonal pair. Source3755 proves independence directly from the
standard root representatives, which is the required field-safe input.

The actual-space condition matters. If only `col(Q)⊂C+D_A` is given,
exactness still gives C⊂col(Q). At rank eight, Q lies in C; at rank nine
the existing rank-at-most-nine theorem applies to P,Q; and at rank ten
the actual span is C+D_A. Thus these exits can separately extend this
specific pair result to inclusion without claiming that arbitrary
normalization preserves a prescribed actual full coordinate span.


## 7. Complete all-A assembly

For a=|A| between 9 and 15, distance 57 gives C∩D_A=0. Any mixed word
E(h)+d retains at least 57−a≥42 support sites outside A. Binary weight
at most seven can support at most 36 root labels, so every mixed word has
weight at least eight. The minimum basis bill therefore satisfies

```
c(C+D_A) ≥ a+8·8 ≥73.
```

Here is the justification that does not replace an arbitrary actual basis.
The a coordinate units form an independent set of minimum nonzero weight
one. Start with a minimum-weight basis and successively insert any missing
unit by basis exchange, removing a vector of weight at least one. This
produces a minimum basis containing all units. Its remaining eight members
are mixed and have weight at least eight. The lower bound is on the
minimum, hence on every actual basis, as required by the coupling lemma.

For a≥16, dim(C+D_A)≥24: if 16≤a≤23, distance 57 gives dimension 8+a;
if a≥24, the coordinate units alone give dimension at least 24. No
trivial-intersection assertion is made for arbitrary large A. FINITE.md's
strict dimension screen says every basis of a space S⊃C of dimension
at least 24 costs at least 73. The strict-floor corollary in section 2
therefore applies. Together with sections 3–5 this proves Theorem C for
every A, including A=∅ and A=E.

The dimension screen is the integer size relaxation of PR2962, used here
with one extra unit of required slack. It does not classify realizable
minimum bases, and its dimension-23 optimum is a relaxation witness only.

## 8. Normalization and the raw pair theorem

Group proportional nonzero P columns. If p_i=α_i p on one ray, replace
those terms by p(Σ_i α_i q_i)^t and delete a zero reader if it results.
Supports of the sum lie inside the union of the old supports. The pairing
rank of that union is at most the sum of the old pairing ranks, so COPY
does not increase. This preserves exactness and both ambient inclusions.
It may shrink the actual Q space, which is why Theorem C explicitly asks
for the actual space after this operation.

For a coordinate pair, the new actual S contains C by exactness and lies
in C+span(δ_a,δ_b), which has dimension ten over every odd field. If dim S≤9,
PR3755's rank-at-most-nine-on-both-sides theorem gives COPY≥72. If dim S=10,
S is the full pair extension and section 6.1 applies. The normalized bill
is at least 72, so the original raw bill is no smaller. This proves
Theorem P. It does not infer full actual right span merely from ambient
inclusion for larger coordinate sets.

## 9. Sharp normalized concave bill

In any covered family, suppose the actual left rank is nine, the actual
right rank n≥10, and the exceptional P rays occur at most once each.
Sylvester gives m≥n+1. Only the two exceptional P rays can have zero
tariff; every other term has tariff w(q)≥1. Hence there are at least nine
positive tariffs in {1,...,9}. COPY≥72 implies for every real 0<q≤1

```
Σ_i ρ_i^q ≥ 1+8^q+7·9^q.
```

To see this, reduce positive integer tariffs until their sum is 72 while
keeping at least nine positive entries. If there are more than nine,
one may remove a smallest entry and redistribute its mass into the others
without exceeding 9; concavity cannot increase the bill when mass is
transferred toward larger entries. Repeating gives nine entries. Among
nine entries of sum 72 in [1,9], the concave minimum occurs by successively
saturating the largest entry or the smallest boundary. The resulting
multiset is (1,8,9,9,9,9,9,9,9). With more than 72 positive entries the
claim is immediate since each costs at least one. At q=1 this is 72;
for q<1 it strictly exceeds 8·9^q by 1+8^q−9^q>0.

The expression and mass-transfer method already occur in adamgall's
PR2062. The new point is the coupled factor-space coverage, not a new
concavity lemma. SHARPNESS.md gives an exact eleven-term, ranks-(9,10)
fixture attaining this profile over Q and every odd characteristic.
No fixed-space sharpness is asserted for larger n. Raw-rank padding can
inflate both ranks with scalar-active zero-tariff cancellation pairs;
the executable countercontrol explains why raw ranks cannot replace
actual ranks after left normalization in this strict concave statement.

## 10. Boundary of the result

Theorem C is an actual-space statement. Arbitrary partial right quotients
of dimensions 10–23 are not automatically covered. EXTENSIONS.md proves
two normalization-stable families of those partial quotients, including
all neighbor supports of size at most 28. General C′, general G1-MFREE,
L120, masked/punctured supports and a multiplication-exponent improvement
remain outside these claims. The E8 instantiation and full assembly are
written proofs, not complete Lean formalizations.
