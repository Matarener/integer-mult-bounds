# A uniform one-coset deficiency budget on full E8

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
This is a written proof with explicit finite integer certificates; its E8
instantiation is not claimed to be a formally verified theorem.

## 1. Statements and exact model

Let K be any field of characteristic different from two. Let L be the 120
root lines of E8, choose standard norm-two representatives r_v over Z[1/2],
and evaluate them in K. Define G and N₀ over K, and define B_d from the
integer root products before scalar reduction:

```text
G_Z[v,w] = the integer product of the standard rational roots,
G = G_Z evaluated in K,            N₀ = G/2,
B_d[v,w] = (1 + G_Z[v,w]) mod 2.
```

Thus B_d[v,w] is one exactly when v=w or v is orthogonal to w. The matrix
B_d is the dense binary COPY table. Orientations of representatives do not
change B_d. Let C ⊆ K^L be the eight-dimensional scalar root-evaluation code:
the vectors (r_v·h)_{v∈L}, for h∈K^8. This scalar code is distinct from the
binary label space Λ defined below.

For X⊆L, write U_X for its binary label span and w(X)=dim_F₂ U_X. For p∈K^L,
write w(p)=w(supp p) and δ(p)=9−w(p). A term p qᵀ costs

```text
ρ(supp p,supp q) = rank_F₂ B_d[supp p,supp q].
```

**Uniform deficiency theorem.** If λ∉C and (p_i) is any finite family of
pairwise nonproportional nonzero vectors in C+Kλ, then

```text
Σ_i δ(p_i) ≤ 9.                                             (1)
```

Every nonzero vector in C has deficiency zero.

**Exact-decoder consequence.** If P,Q∈K^{L×m}, m finite, satisfy

```text
PQᵀ = N₀,             rank_K P ≤ 9,       rank_K Q ≤ 9,       (2)
```

then COPY(P,Q)≥72. This floor is sharp in this class. Transposes are ordinary
transposes, including over the complex numbers. The hypotheses concern the actual factor
ranks, rather than the number of terms or a choice of presentation.
The alternative convention PQᵀ=2G=4N₀ has exactly the same result: multiplying
one factor by four changes neither supports, factor ranks nor COPY.

We prove both statements directly. No catalogue, retraction, or pending
general masked-realization theorem is a premise.

Sections 2–7 first give the proof in characteristic zero, using a rational
A8 model. Section 8 transports the finite facts to every characteristic
different from two and replaces that scalar model by standard K^8. In
particular the A8 divisions by three are not performed in characteristic three.

## 2. A rational A8 realization and its canonical identification

Until section 8 assume that K has characteristic zero.
Write ω=(1,…,1)∈K^9 and V={x:Σ_j x_j=0}. Its dot product is nondegenerate:
V⊥=Kω and ω·ω=9≠0. Use these oriented root representatives:

```text
r_ij = e_i−e_j                 (0≤i<j≤8),
r_S  = 1_S−ω/3                (S⊆{0,…,8}, |S|=3).
```

There are 36+84=120 lines. All have squared norm two. Their integer rows
R_v=3r_v have respectively entries (3,−3,0,…,0) and entries 2 on S, −1 off S.
Pair roots already span V. Below R also denotes the 120×9 matrix of these
integer rows. Its image is C: scaling evaluations by three does not change
the code, and evaluation restricts to an injective map from V.

Here is an explicit rational isometry to the standard E8 model. In Q^8 take
the 56 lines e_a±e_b and the 64 half-root lines (±1,…,±1)/2 with an even
number of minus signs. Choose the eight star roots

```text
s_j=e_0+e_j   (1≤j≤7),        s_8=(1,…,1)/2.
```

Their Gram matrix is I₈+J₈, of determinant nine. The eight vectors
a_j=e_{j−1}−e_8 in V have the same Gram matrix. Therefore the unique rational
linear map T with T(s_j)=a_j is an isometry. Explicitly, for a standard root x,
put d_j=x·s_j and D=Σ_{j=1}^8 d_j. Then

```text
T(x) = (d_1−D/9,…,d_8−D/9,−D/9),
3T(x) = (3d_1−D/3,…,3d_8−D/3,−D/3).                       (3)
```

For standard doubled roots A=2x and doubled stars S_j=2s_j,
d_j=(A·S_j)/4. Enumerate e_a±e_b and the half-roots with first sign positive,
apply (3), and choose the sign with first nonzero entry positive. The resulting
120 integer rows are exactly the canonical signs of the rows R above. This
finite equality is checked explicitly, together with the star Gram identity.
Thus row permutations and individual row signs transport scalar evaluations,
supports, and exact Gram factorizations between the two models.

The label model is especially simple in A8 coordinates. Set Λ=F₂^9 with
β(z,z′)=Σ_j z_j z′_j and assign

```text
u_ij = ω+e_i+e_j,              u_S = 1_S.                    (4)
```

All 120 labels are nonzero. They span Λ: differences of triples sharing two
coordinates generate every e_i+e_j, hence the eight-dimensional even-weight
space, and a triple adds an odd vector. Direct multiplication gives

```text
β(u_v,u_w) = (1+r_v·r_w) mod 2 = B_d[v,w].                  (5)
```

For pair/pair and pair/triple, the parity of the scalar product is the parity
of the intersection of the indicated index sets; the extra ω contributes
one. For triple/triple, r_S·r_T=|S∩T|−1, giving (5) as well. This includes
the diagonal. Isometry (3) transfers the identity to canonical E8 roots.
Because the labels span Λ and β is nondegenerate, B_d has rank nine.
Thus (4) realizes the full canonical dense table, including all COPY ranks;
it is not merely a label convention for a different incidence table.

## 3. The three finite facts and complete profile coverage

For nonzero z∈Λ define

```text
O_z = {v∈L : β(z,u_v)=1}.
```

Call distinct nonzero z,z′ **compatible** when the scalar roots indexed by
O_z∩O_z′ have rank at most seven. For an even-weight vector set
q(z)=wt(z)/2 mod 2. The required finite facts are:

1. The roots indexed by O_z span V for every nonzero z.
2. Compatible z,z′ satisfy β(z,z′)=0.
3. If compatible z,z′ both have even weight, then q(z)≠q(z′).

Fact 1, including its validity in every characteristic different from two,
was already certified by CubeJerry / PR3095 with power-of-two integer minors.
The present certificate independently reconstructs that premise together with
the forbidden-pair witnesses needed for facts 2 and 3.

Only full-rank witnesses are needed to prove these statements. The attached
[CERTIFICATE.json](CERTIFICATE.json) gives nine single-character witnesses and
100 forbidden-pair witnesses, each an explicit nonzero integer 8×8 minor
in standard doubled-root coordinates, with row IDs in the A8 label order.
Here is the entire reduction from these witnesses to all characters and pairs.

Permutations of nine coordinates act on V, its root lines, and the labels
(4). A pair root can change orientation; this multiplies a scalar row by −1
and does not change its binary label. A coordinate permutation σ maps O_z
to O_{σz} and preserves scalar ranks, β, and q. Nonzero single characters have exactly nine orbits,
specified by their weight k=1,…,9. The representative z_k has its first k
bits equal to one, that is integer bitmask 2^k−1 with bit zero first.

For ordered pairs (z,z′), simultaneous coordinate permutation is classified
completely by the four counts n_ab of coordinates with (z_j,z′_j)=(a,b).
Two pairs with the same counts are related by a permutation, obtained by
matching each of the four coordinate classes. There are

```text
#{(n_00,n_01,n_10,n_11)≥0 : Σ n_ab=9} = binom(12,3)=220.
```

Delete the profiles with z=0, z′=0, or z=z′. Each condition gives ten
profiles. Every intersection of two or three conditions is the single
all-zero pair profile, so their union has 30−3+1=28 profiles. Exactly
220−28=192 valid ordered profiles remain. For each one use contiguous
coordinate blocks 00,01,10,11 of their stated lengths to define a,b.

The forbidden predicate on these representatives is precisely

```text
n_11 odd
or [wt(a),wt(b) both even and wt(a)/2 ≡ wt(b)/2 (mod 2)].      (6)
```

Exactly 100 of the 192 profiles satisfy (6). The certificate contains exactly
this inventory, without omissions or duplicates, and binds each a,b to its
four counts. For each listed pair it selects eight standard doubled-root
rows lying in O_a∩O_b with the stated nonzero determinant.
Thus every forbidden profile has scalar rank eight. Its contrapositive proves
facts 2 and 3 for all pairs; no assertion that the remaining profiles are
compatible is required.

For completeness the certificate's nine single-character determinants are

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| det | −512 | −256 | 512 | −256 | −1024 | −256 | −512 | −256 | 256 |

Rows are indexed from zero: first pair roots in lexicographic order of (i,j),
then triple roots in lexicographic order of S. Every witness index must be
distinct, in 0,…,119, and satisfy its stated character conditions. The verifier
uses (3) to bind each indexed A8 line to its standard eight-dimensional
doubled-root row. Nonzero determinants give fact 1 and all forbidden
rank-eight assertions. Every absolute determinant is a power of two,
belonging to {256,512,1024,2048}; this permits the extension in section 8.

The displayed formulas reconstruct every finite input: enumerate the roots,
labels, nine singles and 220 four-count tuples; select the 100 tuples by (6);
check witness membership and recompute every determinant. [verify.py](verify.py)
enforces these complete inventories. [independent.py](independent.py) separately
reconstructs the standard D8-plus-half-root model and exhausts all nonzero
characters and unordered distinct pairs in intrinsic dense-table coordinates.

Every doubled-root entry and every witness determinant is an integer. A nonzero
integer remains nonzero in every characteristic-zero field. Consequently
these facts hold for scalar rank over any such K, including fields not
embedded in R or C. No reduction-mod-prime assumption is used for this
transfer; modular rank can select a witness, but the exact determinant
certifies it.

## 4. Every compatibility clique is linearly independent

Credit mightyOil / PR1248's compatible-edge independence argument as the
method ancestor. Here it is applied to arbitrary compatible cliques, then
grouped across all support annihilators in section 5.

Let E be a set of distinct pairwise compatible nonzero binary vectors.
Fact 2 says that its off-diagonal β pairings vanish. For an odd-weight member
z, β(z,z)=1. Pairing a linear relation among E with z therefore makes its
coefficient zero. All odd-weight members disappear from any relation.

The remaining members have even weight. By fact 3, any two have opposite
q values. There are only two values, so there are at most two such members
in E. A single nonzero vector is independent, and two distinct nonzero
vectors over F₂ are independent. The remaining relation is therefore zero.
This proves independence of E, and in particular |E|≤9.

## 5. Annihilator packing proves the uniform theorem

For any scalar vector p define its binary support annihilator

```text
Z(p) = {z∈Λ : β(z,u_v)=0 for every v∈supp p}.
```

Nondegeneracy gives dim Z(p)=9−w(p)=δ(p). Equivalently, z∈Z(p) means p
vanishes on O_z. If 0≠p∈C and 0≠z∈Z(p), the evaluation defining p
vanishes on roots spanning V by fact 1, forcing p=0. Thus Z(p)=0 for
every nonzero p∈C.

It remains to consider the members outside C. Each has a unique expression
p_i=a_i λ+R h_i with a_i≠0 and h_i∈V. Divide by a_i, which preserves support
and annihilator, and rename h_i to obtain

```text
p_i = λ+R h_i.
```

Here Rω=0 because every A8 root row has coordinate sum zero. Together with
the direct sum K^9=V⊕Kω in characteristic zero and injectivity on V, this
justifies taking each evaluation representative uniquely in V.

These normalized vectors are distinct: equality would make the original
members proportional. Thus h_i−h_j≠0 for i≠j. Write Z_i=Z(p_i).

First, Z_i∩Z_j=0. Indeed a common nonzero z would make both vectors vanish
on O_z. Their difference R(h_i−h_j) would vanish there as well, contradicting
fact 1 and injectivity of evaluation on V.

Second, every nonzero z∈Z_i and z′∈Z_j with i≠j form a compatible pair.
They are distinct by the preceding paragraph. Both p_i and p_j vanish on
O_z∩O_z′. The nonzero linear functional defined by h_i−h_j therefore
vanishes on every scalar root there. Its kernel in V is a hyperplane, so
that root set has rank at most seven. This is compatibility by definition.

Pairwise trivial intersection alone would not suffice to add dimensions.
Here the stronger cross-pair property supplies the missing step. Suppose
there is a relation Σ_i z_i=0 with z_i∈Z_i. Discard its zero summands. The
remaining z_i are distinct nonzero vectors, one from each participating
space, and every two are compatible. Section 4 makes them independent,
contradicting this nonempty relation. Hence the sum of all Z_i is direct in
the nine-dimensional Λ, and

```text
Σ_i δ(p_i) = Σ_i dim Z_i = dim(⊕_i Z_i) ≤ 9.
```

Members inside C contribute zero, proving (1) for the entire finite family.
The proof imposes no bound on its cardinality and makes no assumption about
the weights or support shapes of the individual vectors.

The budget nine is attained. Set λ=0 on pair roots and λ=−2 on triple roots,
and let p_j=λ+R_column_j for j=0,…,8. The pair roots force λ∉C: a codeword
vanishing on all pair roots is zero. These nine vectors have different
supports, hence are nonproportional. Their nonzero triple entries are exactly
the triples avoiding j; their nonzero pair entries are exactly pairs incident
to j. All corresponding labels lie in e_j⊥. The triples on the other eight
coordinates span that eight-dimensional space by the same even-space plus
odd-vector argument used after (4). Therefore w(p_j)=8 and Σ_j δ(p_j)=9.
This is sharpness of the family budget, not an exact-decoder fixture.

## 6. Normalization of an exact factorization preserves the needed bounds

Start with (2). Drop any term having a zero factor, since its scalar outer
product and its COPY cost are both zero. If p_j=μp_i with μ≠0, replace

```text
p_i q_iᵀ+p_j q_jᵀ  by  p_i(q_i+μq_j)ᵀ.
```

The new column support is contained in supp q_i∪supp q_j. For a fixed row
support, binary pairing rank is monotone under restricting columns and
subadditive under taking their union. Hence the new cost is at most the sum
of the two old costs. The new columns of either factor lie in its old column
span, so neither actual factor rank increases. The symmetric operation merges
proportional q columns. Remove any zero factor created by a merge.

Repeat merges on either side until neither side has a proportional pair.
Each operation decreases the number of terms, so this terminates. Denote the
remaining number by m′. Both final families consist of pairwise
nonproportional nonzero vectors; exactness is preserved and cost has not
increased. Retain every term with two nonzero factors, even if its binary
COPY cost is zero: such an outer product can be nonzero and can be necessary
for exact equality to N₀. There is no deletion of off-mask scalar entries.

The standard root matrix R₀ has full column rank: its rows include the basis
e_0±e_1,…,e_6±e_7. Thus R₀ is injective and R₀ᵀ is surjective. Their product
G=R₀R₀ᵀ has rank eight and image C, without requiring R₀ᵀR₀ to be invertible.
Exactness and its transpose imply

```text
C = col(N₀) ⊆ col(P),              C ⊆ col(Q).
```

For the normalized factors their ranks are consequently 8+s and 8+t with
s,t∈{0,1}. If s=0, all p columns are in C and their total deficiency is zero.
If s=1, their span is C+Kλ_P for some λ_P∉C; apply (1) to the normalized
family. The same argument applies on the q side. In both cases,

```text
Σ_k δ(p_k)≤9s,      Σ_k δ(q_k)≤9t.                         (7)
```

The values s,t here are the final ranks: normalization can lower a rank,
and (7) covers (9,9) and every exit into (8,8), (9,8), or (8,9).

## 7. The COPY floor, sharpness, and the boundary of the result

For binary subspaces U,W⊆Λ, the pairing map U→W* has kernel U∩W⊥. Hence

```text
ρ(U,W)=dim U−dim(U∩W⊥) ≥ dim U+dim W−9.
```

This also applies to cost-zero terms. Summing it and using (7) gives

```text
COPY ≥ Σ_k [w(p_k)+w(q_k)−9]
     = 9m′−Σ_k δ(p_k)−Σ_k δ(q_k)
     ≥ 9(m′−s−t).                                          (8)
```

Sylvester's inequality, applied to the normalized exact product, gives

```text
8=rank(PQᵀ) ≥ rank P+rank Q−m′ = 16+s+t−m′.
```

For clarity this follows by restricting P:K^{m′}→K^L to im(Qᵀ): its kernel
has dimension at most m′−rank P. Thus m′≥8+s+t, and (8) is at least 72.
The original factorization has no smaller cost, proving the consequence.

The one-sided slices are low-dimensional instances of the L120 basis-cost
programme. If S contains C and dim S=8+s with s in {0,1}, any basis of S is
nonproportional. The uniform theorem gives total basis deficiency at most 9s,
so every such basis costs at least 9(8+s)-9s=72. SPARSE-PAIR.md proves the
specified dimension-ten instance. These statements do not prove L120 for
arbitrary S; the genuinely two-sided consumer here is the (s,t)=(1,1) cell.

Sharpness requires only the ordinary rank-(8,8) decoder. In standard root
coordinates use the orthogonal norm-two frame f_k=e_{2a}±e_{2a+1}, a=0,…,3.
Let X[v,k]=r_v·f_k. Since Σ_k f_k f_kᵀ=2I₈, the factors P=Q=X/2 satisfy
PQᵀ=G/2. They have rank eight. Every nonzero column is a scalar codeword,
so its support has label span Λ by section 5. Each of the eight terms
therefore costs nine, for total 72. No rank-(9,9), ten-term equality fixture
is needed for this sharpness claim. There is also the following normalized
two-sided equality construction, retained in [fixtures.py](fixtures.py).

### 7.1. Normalized rank-(9,9), ten-term equality

Write E(h)=(r_x·h)_{x∈L} for scalar evaluation in standard root coordinates.
Choose v=e_0+e_1 and w=e_0+e_2, so v·w=1, and their root lines a,b. The
actual oriented representatives at those lines may be ±v and ±w. Use the
following dual bases; inspection gives h_i·d_j=δ_ij:

```text
(h_1,…,h_8) = (v, e_1, e_0−e_2, e_3,…,e_7),
(d_1,…,d_8) = (w, −e_0+e_1−e_2, −e_2, e_3,…,e_7).
```

Let δ_a,δ_b denote coordinate unit vectors in K^L and define nine terms by

```text
λ=E(v)_a δ_a,      p_0=λ,             p_j=λ−E(h_j)  (1≤j≤8),
q_j=−E(d_j)/2      (1≤j≤8),          q_0=−Σ_{j=1}^8 q_j.
```

Since E(v)_a=±2, λ≠0. It is outside C because its binary support weight is
one, whereas every nonzero scalar codeword has weight nine. Duality gives

```text
Σ_{i=0}^8 p_i q_iᵀ
  = −Σ_{j=1}^8 E(h_j)q_jᵀ
  = (1/2)Σ_{j=1}^8 E(h_j)E(d_j)ᵀ = G/2.                   (9)
```

The p columns span C+Kλ: their differences with p_0 give the basis E(h_j).
They are pairwise nonproportional, since all have the same nonzero quotient
modulo C and the h_j, together with zero, are distinct. The q_1,…,q_8 are
a basis of C; q_0 is their negative sum, hence nonzero and nonproportional
to each of them. This is therefore a normalized rank-(9,8) decoder.

The support of p_1=λ−E(v) is exactly the roots nonorthogonal to v with line
a omitted. Its labels lie in u_a⊥. Adding label u_a gives the support of
E(v), whose label span is Λ, so w(p_1)=8. Thus δ(p_0)=8 and δ(p_1)=1.
The family theorem forces all other p_j to have weight nine. Since each q_i
is a nonzero codeword, these nine terms have costs (1,8,9,9,9,9,9,9,9).

Now put μ=δ_b and c=N₀[:,b], and replace the nine q columns, adding one term:

```text
q_i′ = q_i−q_i(b)μ   (0≤i≤8),       (p_9,q_9′)=(c,μ).
```

Equation (9) implies Σ_i p_i q_i(b)=c, so this changes the product by
−cμᵀ+cμᵀ=0. The p rank is still nine, since c∈C. The new q columns span
C+Kμ: μ is present and each old q_i is q_i′+q_i(b)μ. This has dimension
nine, since the singleton μ is outside C.

All ten terms are normalized. The old p columns are outside C and pairwise
nonproportional, so none is proportional to the new nonzero c∈C. On the
other side, a relation q_i′=αq_j′ would give q_i−αq_j∈C∩Kμ=0, contradicting
the old nonproportionality. No q_i′ is zero or proportional to μ for the same
reason. Thus neither side admits a proportional merge.

Because d_1=w, q_1′ has exactly the nonorthogonal-to-w support with line b
omitted. As above its label span is u_b⊥ of dimension eight. Together with
q_9′=μ of weight one this saturates the q-side deficiency budget nine, so
all other q_i′ have weight nine. Both p_1 and q_1′ consequently have
hyperplane label spans. Since v·w=1, equation (5) gives β(u_a,u_b)=0, and

```text
ρ(p_1,q_1′) = 8−dim_F₂(u_a⊥∩F₂u_b) = 7.
```

The first and last terms pair a singleton with a full label span and cost
one each. The seven remaining terms have both label spans full and cost
nine each. The ten costs are therefore

```text
(1,7,9,9,9,9,9,9,9,1),                total COPY = 72.
```

This is an explicit equality example in the strict normalized (9,9), m=10
class, rather than an enumeration of arbitrary coefficient choices.

### 7.2. Necessary structure of every equality case

Suppose an original factorization in (2) has COPY=72. Any completed
normalization still costs 72: cost cannot rise, and the proved floor applies
to its final ranks. For those ranks 8+s,8+t, the two inequalities in section
7 force

```text
m′=8+s+t,       Σ_i δ(p_i)=9s,       Σ_i δ(q_i)=9t.
```

Indeed m′>8+s+t would force COPY≥81; with equality in the term count, any
unsaturated deficiency budget would make (8) strictly greater than 72.
Every individual pairing inequality is also an equality, since all their
nonnegative gaps sum to zero. In annihilator notation this is equivalent to

```text
Z(q_i) ⊆ U_supp(p_i),   or equivalently β(Z(p_i),Z(q_i))=0.
```

For either factor with excess one, its annihilators form a β-orthogonal
direct-sum decomposition of all Λ. Orthogonality follows from fact 2 and
the cross-compatibility in section 5; their dimensions sum to nine by
budget saturation. Consequently β restricts nondegenerately to each nonzero
annihilator: a vector in its radical would be orthogonal to every summand,
hence all Λ, and would be zero. These are necessary equality conditions;
they do not classify the scalar coefficient families. The exact fixtures
check the dimensions, same-side orthogonality, restricted nondegeneracy,
and matched cross-side orthogonality after every normalization exit.

As a useful unrestricted-rank corollary, every exact ten-term decoder whose
two factors both leave C costs at least 72. Indeed write their ranks as
8+s,8+t with s,t≥1. Sylvester gives s+t≤2, so s=t=1 and the theorem applies.
A cheaper exact decoder with both factors outside C would therefore need at
least eleven terms. A rank-(10,8) ten-term decoder is outside this result.

The theorem is for the full E8 root set and exact N₀, with dense table B_d.
It does not prove the general masked P120 floor, a punctured-root floor,
or an unrestricted floor with a factor of rank ten or more. The separate
[SPARSE-PAIR.md](SPARSE-PAIR.md) derives a restricted rank-(10,8) extension:
one factor lies in C and the other in C plus two root-coordinate unit vectors.
This is a consequence of the one-coset theorem, not a uniform two-direction
family budget. Singleton padding of a
punctured decoder can raise the factor ranks beyond nine. Nor does the
family budget extend to two arbitrary outside directions: over an infinite
field the vectors δ_a+tδ_b for arbitrarily many distinct nonzero t have support size two,
are pairwise nonproportional, and all have deficiency seven. There is no
new κ, physical realization, supplier admission, or multiplication theorem.

## 8. Extension to every scalar field of characteristic different from two

Both the uniform theorem and the exact-decoder COPY floor hold for every
field K with char K≠2, using the standard E8 roots over Z[1/2]. Define C as
their scalar evaluation code over K and retain the fixed integer-incidence
table B_d and the binary labels (4). In particular B_d is defined before
scalar reduction, rather than by taking parity of a field element.

The 109 standard-coordinate determinant witnesses are powers of two, hence
remain nonzero in K. To transport their profiles when char K=3, do not reduce
the rational A8 isometry or its sum-zero scalar space: those were only used
over Q to index the root lines. Instead use the following integral reflection
identities. For each adjacent transposition of the nine A8 coordinates, let
α be the standard doubled E8 root corresponding to that pair root. Its
reflection is H=I−ααᵀ/4. For N=4I−ααᵀ the verifier checks

```text
N²=16I,             4u−(u·α)α = ε·4u′    (ε∈{1,−1})
```

for all 120 standard doubled-root rows u, with u′ the A8-permuted line,
and checks that its binary label is the same coordinate permutation of u's
label. These are eight generator checks, 960 signed root-image identities,
and 512 matrix-entry identities. They hold over Z, so H is an invertible
root-line permutation over every K of odd characteristic. The generators
give the full S9 action needed for the nine single and 192 pair profiles.
Thus the same unit witnesses prove all three finite facts over K, defining
compatibility by scalar rank over K itself.

In sections 4–7 replace the scalar A8 space V by standard K^8 and its
evaluation map R₀. Its dot product is nondegenerate, and R₀ has rank eight
because the orthogonal frame basis has determinant ±16. The annihilator,
grouped-relation, merge, binary rank and Sylvester arguments are unchanged.
In particular rank N₀=8 follows from injectivity of R₀ and surjectivity of
R₀ᵀ, even in characteristics three and five where R₀ᵀR₀=30I is singular.
The ordinary rank-(8,8) decoder still attains 72. This extension does not
assert that the nine A8 integer vectors in section 5 retain their stated
supports after reduction at three, and makes no characteristic-two claim.

The sparse-pair consequence in SPARSE-PAIR.md uses this all-odd-field theorem
directly; its singleton-ray classification, binary orthogonality and filtered
basis argument require no further field-transfer premise.

The strict normalized rank-(9,9), ten-term equality construction in section
7.1 also persists over every such field: its integral dual bases remain bases,
its quotient-space nonproportionality arguments remain valid, and the two
distinguished support hyperplanes still saturate the deficiency budgets.
Their nonzero root pairings are ±1 or ±2, so exactly the same single root
line is removed on each side in every characteristic different from two.

## 9. Predecessors and proof dependencies

Credit joaqcoo / PR1224 for the all-m projection equations, one-sided
annihilator constraints and original compatible-pair census; mightyOil /
PR1248 for the fixed-A8-frame deficiency-nine theorem and compatible-edge
independence method; adamgall / PR2062 for the fixed A7+A1 family; CubeJerry /
PR3095 for the single-character rank premise in every odd characteristic;
and bbMisk / PR1633
for the sharp factor excess-rank budget and full two-sided ten-term residual
form. PR717 and PR446 supply the exact-decoder and per-term pairing-rank COPY
model; PR968 and PR1077 supply earlier exact-root decoder floors. The new
assembly proves an arbitrary one-coset family budget and its all-m,
rank-at-most-nine exact-N₀ consumer; the rank and merge arguments are rederived.

The one-sided slices belong to L120, the programme documented in PR3074 and
PR3154's B-prime node. PR3191's draft completion claim still has an unfilled
implementation slot at its pinned head; conorholds / PR3166 supplies C7 in
that programme. None of that conditional chain is a premise here. The
two-sided (1,1) result addresses PR3154's C-prime node and its requested
term-count-independent deficiency budget. philippeVV's restricted clean
lift-family credit-at-most-nine argument in Discussion 1587 is related prior
work; the arbitrary-family theorem here does not assume its lift hypotheses.

The proof uses only the explicitly constructed root/label model, the 109
finite rank witnesses and their orbit coverage, and the linear algebra in
sections 4–7. It imports none of the C1–C5, catalogue, capacity, root-swap,
or retraction assertions in the later master-floor programme. Reproduction
and the distinction between executable checks and formal coverage are recorded
in the package README and verification records. [FORMAL.md](FORMAL.md) describes
the checked Init-only Lean core for odd-coefficient elimination, the Boolean
even-color argument, and absence of nonempty zero relations among compatible
cliques and nonzero grouped choices from trivially intersecting subspaces. It does
not formalize the E8 finite facts, their geometric instantiation, the connection
to Mathlib linear independence or finrank, the dimension budget, or the
exact-factorization COPY consequence. A second Init-only file checks the final
natural-number implication from the two displayed budget inequalities to
COPY≥72, with both inequalities left as explicit premises. The first file also
instantiates the addition and pairing laws on Fin 9→Bool; the E8 geometric
orthogonality and even-color hypotheses remain explicit premises.
