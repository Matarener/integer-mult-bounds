# Frobenius products over arbitrary finite residue fields

Fix an explicit finite field K=F_q of characteristic p. For each j, let
L_j=F_(q^d_j) be a finite extension of K and let h_ji be positive integers.
Define

    B_j=L_j[x_ji]/(x_ji^(p^h_ji)), N_j=p^(sum_i h_ji), A=product_j B_j.

Empty height lists are allowed and give field factors. The dimension over K
is n=sum_j d_j N_j. All tensor factor maps and determinants below are over K.

**Recognition theorem.** From an arbitrary square K-tensor, the algorithm
decides whether it is isotopic to multiplication in such an A. It returns
the residue degrees, height lists, explicit coefficient-field tables, and
three invertible factor maps U,V,W with t(Ua,Vb)=W ab. It uses deterministic
polynomial time in n for fixed K. Neither a decomposition nor a field section
is supplied. In particular, the algorithm does not enumerate q^d_j elements.

This extends the recognition part of PR5661 beyond split residue fields.
Nick Petalas's PR5252 supplies the finite-etale nucleus and spectral-projector
precedent. PR5637 and PR5502 supply the local semilinear height argument.
The new result recovers nonsplit coefficient fields and composes the complete
recognition test and factor maps. No physical supplier or new kappa is claimed.

During the submission refresh, apoursh's concurrent claim on supplied-field
characters was found in Discussion5655, comment 19187845. That claim explicitly
excludes arbitrary tensor recognition and coefficient-field discovery. This
package is narrowed to those complementary outputs. The character formula,
labels and transporter work remain with that claim and are not outputs here.

## 1. Recover the nucleus and primitive factors

Use the nucleus equations and acceptance gates of PR5661:

    B={(X,Y):t(Xu,v)=Yt(u,v)}, dim_K B=n,

with both projections injective, commutative image, and zero right kernel of t.
The nucleus is a unital commutative matrix algebra. Recover its multiplication
table and unit from a faithful projection.

The least q-power Q>=n has ker(b -> b^Q)=J, the nilradical. The proof of J^n=0
and the construction of primitive idempotents through ker(Frob_q-I) in PR5661
do not require split residues. On each local factor the q-fixed algebra is
exactly K; its basis separates the factors by spectral projectors. Retain that
construction but remove the split-residue test dim(B/J)=number of factors.

For each primitive e_j, calculate

    B_j=e_jB, J_j=e_jJ, d_j=dim_K B_j-dim_K J_j.

The residue is the field F_(q^d_j). All these quantities use K-linear algebra.
This primitive decomposition is an exact algebra decomposition, with no
recognition assumption about the final truncated-polynomial class.

## 2. Recover regular modules over nonsplit residues

For either nucleus module M, require

    dim_K(e_jM / J e_jM)=d_j

for every component. Choose any vector m_j outside J e_jM. The quotient is
one-dimensional over the residue field, so this vector generates it as a
B_j-module. The usual nilpotence argument is elementary here: if C=B_jm_j,
then N=e_jM/C satisfies N=JN, whence N=J^nN=0. The sum m=sum_jm_j is cyclic.
Since dim B=dim M=n, b -> bm is an isomorphism. Both matrices are checked.

Necessity holds for a regular module. This changes the split test from a
one-dimensional K-top to a d_j-dimensional K-top; rejecting all larger tops
would incorrectly reject every nonsplit residue field.

As in PR5661, choose generators u0,w0 for the two actions, put
alpha(b)=X_bu0, gamma(b)=Y_bw0, and Phi(v)=t(u0,v). Cyclicity and the zero right
kernel make Phi invertible. With beta=Phi^-1 gamma,

    t(alpha(a),beta(b))=gamma(ab).

This gives factor maps from the recovered algebra before any local class test.

## 3. Recover the unique coefficient field by a power kernel

Let B be one local component, J its radical, d its residue degree, e its unit,
and D=q^d. The set

    L={b in B : b^D=b}

is a K-subalgebra: the D-power map is additive and multiplicative in the
commutative algebra, and it fixes every scalar in K. It maps bijectively onto
B/J. For existence, lift a residue c to t and choose a power R=D^a at least
dim_K B. Then (t^D-t)^R=0, so t^R lies in L; its residue remains c. For
uniqueness, the difference of two lifts is a fixed nilpotent z, so
z=z^(D^a)=0 for large a. Thus reduction gives a field isomorphism L -> B/J.
Every K-algebra automorphism preserves this uniquely defined L.

Compute the K-linear kernel of Frob_D-I. Its dimension is d. Put e first in
its basis and extend by independent kernel vectors. Multiplication gives an
explicit d-dimensional field table in that basis. There is no search over the
elements of L. Exponent D has only d*log_2(q)+1 bits, so repeated squaring is
polynomial in d and log q.

The separate certificate check verifies the coefficient table is a field:
check commutativity, associativity, identity, zero nilradical and
dim ker(Frob_q-I)=1. A finite reduced commutative K-algebra is a product of
finite fields, and the last dimension is its number of factors. These tests
therefore prove that the supplied table has one field factor, without an
elementwise inverse search.

## 4. Recover heights over the coefficient field

Use the semilinear p-power kernels K_h=ker(b -> b^(p^h)). The matrices and
their inverse coefficient twists are computed over K as in PR5637. Each K_h
is also an L-subspace: raising an L-scalar to p^h is an automorphism of L.
Likewise J^2 is an L-subspace.

Start with J^2. For h in increasing order, inspect a K-basis of K_h. When a
vector v adds a new tangent direction, add the full L-span Lv by multiplying
v with every coefficient-field basis element. Its K-dimension increment is
exactly d: a nonzero line over L has dimension d over K. Record v as one
generator of height h. This does not record d copies of the same generator.

The result is a list g_i with g_i^(p^h_i)=0 whose classes form an L-basis of
J/J^2. They generate B over L by the radical-power argument of PR5502:
expand each J^k modulo J^(k+1), then iterate to J^n=0. Therefore substitution
gives a surjective L-algebra map

    L[x_i]/(x_i^(p^h_i)) -> B.

Accept precisely when d*p^(sum_i h_i)=dim_K B. The dimensions then agree and
the map is an isomorphism. In the target algebra the p-power tangent flag
recovers exactly its variable heights; no nonlinear term can cancel the
surviving single-variable monomial of a lower-degree linear term. This proves
necessity as well as sufficiency.

The model basis consists of each ordered variable monomial multiplied by every
coefficient-field basis element. These explicit columns are checked for full
rank. Combining the local model maps with alpha,beta,gamma gives U,V,W. The
certificate checker verifies all n^2 transported basis products independently
of the discovery kernels. This proves the recognition theorem.

## 5. Complexity and the kappa boundary

The nucleus elimination costs O(n^7) base-field operations. Radical and fixed
spaces use K-linear systems. Powers q^d require O(d log q) algebra products,
not q^d operations. Tangent tests use coefficient-field basis vectors, not
all coefficient-field elements. The primitive splitting enumerates q scalars
for each fixed-algebra basis vector. A conservative bound for the complete
algorithm and certificate check is O(n^9+q*n^6*log(q*n)) K-operations, after
the explicit base-field table is built. Space is polynomial in n. This is a
fixed-q statement; no polynomial bit bound in log q is claimed.

The package closes recognition and explicit factor-map extraction for the full
declared family of finite residue-field Frobenius products. The tensor atlas
can apply it directly to tensor coefficients. General local algebras with other
relations, efficient canonical field isomorphisms, physical native maps,
coefficient costs, ownership, restoration, precision, storage and a complete
caller remain separate. Unknown physical costs are not zero. The selected
frontier and complete kappa calculation are unchanged.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0. The same
assistant wrote the proof and checks. Independent scientific review remains
open; no proof-kernel acceptance is claimed.
