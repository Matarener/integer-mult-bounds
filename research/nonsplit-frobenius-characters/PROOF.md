# Determinant characters for nonsplit Frobenius-truncated products

This note extends the supplied-model character interface to local factors with
nontrivial finite residue fields. It does not recover an algebra, its factors,
or three factor maps from an arbitrary tensor. All vector spaces, determinants,
algebra automorphisms and tensor actions are over one fixed base field K.
The result is an algebraic interface theorem, not a native implementation or
an improvement to the selected multiplication bound.

## 1. Models, coordinates and the theorem

Let K=F_q have characteristic p. For each residue degree d occurring in the
input, fix an explicit field L_d/K of degree d with an ordered K-basis. Use the
same presentation and basis for every component of that degree. Consider a
nonempty finite product

$$
A=\prod_{j=1}^r B_j,\qquad
B_j=L_{d_j}[x_{j1},\ldots,x_{js_j}]/
       (x_{ji}^{p^{h_{ji}}}:1\leq i\leq s_j),\qquad h_{ji}\geq1.
$$

The empty height list is allowed and means B_j=L_{d_j}. Put

$$
M_j=\dim_{L_{d_j}}B_j=p^{\sum_i h_{ji}},\qquad
D_j=\dim_K B_j=d_jM_j,\qquad n=\sum_jD_j,
$$

and define the integer

$$
E_{ji}=M_j(p^{h_{ji}}-1)/2.
$$

If p is odd, the second factor is even; if p=2 and a variable is present,
M_j is even. There is no E exponent for an empty height list. In particular,
**E uses the dimension M_j over the residue field, not the dimension D_j over K.**

A component's type is (d_j, its sorted height list). Within a component, order
the monomials lexicographically in their exponent tuples, and within each
monomial use the fixed ordered K-basis of L_{d_j}. A supplied product may list
its components in any order. The canonical product model orders their types
lexicographically. Heights are sorted before defining the local model; supplied
matrices must refer to that fixed local monomial order.

Let m=q-1. Include a sign exponent T=m/2 precisely when q is odd and at least
one of these conditions holds:

1. Some residue degree d_j is even.
2. Some type with odd residue degree occurs at least twice.

Define

$$
g=\gcd(m,\{E_{ji}\}_{j,i},\ T\text{ if included}),\qquad
H_g=\{c^g:c\in K^\times\}.
$$

The gcd of the singleton list (m) is m. When q=2, m=g=1 and H_g={1}.

**Theorem.** For the K-algebra A above,

$$
\det_K\operatorname{Aut}_K(A)=H_g.
$$

For its multiplication tensor, with the covariant action on
A* tensor A* tensor A, the full stabilizer determinant image is

$$
\Delta(\mu_A)=
 \{(u,v,w)\in(K^\times)^3:uvw\in H_g\}
 =\{(u,v,w):(uvw)^{m/g}=1\}.
$$

Every allowed triple is attained. This image has m^3/g elements, and the GL
orbit of the multiplication tensor splits into exactly g orbits under
SL_n(K) x SL_n(K) x SL_n(K). Section 8 gives a complete label for tensors
with verified maps from the supplied product model, including component-order
normalization. These statements hold over every finite K; finite executable
fixtures are corroboration, not the all-dimension proof.

## 2. The coefficient field is intrinsic

Work first with one factor
$B=L[x_1,\ldots,x_s]/(x_i^{p^{h_i}})$, where L=F_{q^d}.
Its radical J=(x_1,...,x_s) is nilpotent. An element with nonzero constant term
is a unit by a finite geometric series; an element in J is nilpotent. Thus B
is local and B/J=L. Its only idempotents are zero and one: one of e and 1-e is
a unit, and e(1-e)=0 then determines e.

Set Q=q^d. Inside B, the embedded coefficient field is exactly

$$
L=\{a\in B:a^Q=a\}.
$$

Indeed write a=c+j with c in L and j in J. Characteristic-power Frobenius
gives a^Q=c+j^Q. If a^Q=a then j^Q=j. Iterating this identity eventually kills
j by nilpotence, so j=0. Conversely every c in L satisfies c^Q=c.
This also proves uniqueness of a coefficient-field section of B/J: each
residue has just one lift satisfying that equation.

Every K-algebra automorphism preserves this intrinsic field and restricts to a
power of the q-Frobenius $\varphi:c\mapsto c^q$ of L/K. Extend varphi to B
by applying it to coefficients and fixing each variable. It is a K-algebra
automorphism of order d. Composing any automorphism with the inverse of its
coefficient Frobenius leaves an L-algebra automorphism. Therefore

$$
\operatorname{Aut}_K(B)
 =\operatorname{Aut}_L(B)\rtimes\operatorname{Gal}(L/K).
$$

There are no additional automorphisms obtained by moving the coefficient field
through nilpotent directions. The relevant field automorphism is q-Frobenius;
when K is nonprime, p-Frobenius need not be K-linear.

## 3. Local L-linear characters and restriction of scalars

We give the local filtration argument of Ali Romman's PR5459 over L, then take
its determinant over K. Let M=dim_L B and write

$$
V_e=(\ker(a\mapsto a^{p^e})+J^2)/J^2.
$$

These are L-subspaces, even though the power maps are semilinear. They are
intrinsic: K-algebra isomorphisms preserve the power equations and J^2, while
their restriction to L may be semilinear. The monomial basis shows

$$
V_e=\operatorname{span}_L\{x_i+J^2:h_i\leq e\}.
$$

To see the reverse inclusion, a nonzero linear term in a variable of height
greater than e contributes a surviving degree-p^e monomial to the p^e power.
Other linear terms contribute different monomials, and higher-degree terms
cannot cancel this monomial. Thus the increments of dim_L V_e recover the
height multiset. The residue degree and height multiset consequently classify
the displayed local factors up to K-algebra isomorphism. Equal K-dimension
alone does not classify them.

An L-algebra automorphism has an invertible tangent map on J/J^2 preserving
this height flag. Conversely every invertible flag-preserving linear
substitution defines an algebra automorphism: the image of a height-h variable
uses only variables of height at most h, so its p^h power is zero. Its inverse
preserves the same flag and defines the inverse substitution.

A general automorphism and its linear substitution induce the same map on the
associated graded algebra for J^k. Ordering a monomial basis by total degree
therefore gives them the same L-determinant. The flag-preserving linear group
is generated by diagonal scalings and permitted elementary substitutions.
An elementary substitution x_i -> x_i+c x_k is triangular on monomials ordered
by the x_i exponent and has determinant one. Scaling x_i -> c x_i has
L-determinant

$$
c^{E_i},\qquad
E_i=\sum_{0\leq a_\ell<p^{h_\ell}}a_i
   =M(p^{h_i}-1)/2.
$$

For any L-linear map S on an M-dimensional L-space,

$$
\det_K S=\operatorname{Norm}_{L/K}(\det_L S).
$$

For completeness, Gaussian elimination factors an invertible L-matrix into
elementary matrices, diagonal entries and coordinate swaps. The identity holds
on an elementary matrix since its K-matrix is block triangular with identity
diagonal. A diagonal scalar c contributes its norm by the definition of the
field norm as a multiplication determinant. An L-coordinate swap exchanges
two K-blocks of size d and has determinant (-1)^d, equal to the norm of -1.
Multiplicativity proves the formula.

Consequently the K-determinants of the variable scalings are

$$
\operatorname{Norm}_{L/K}(c)^{E_i}.
$$

The finite-field norm is onto K*: the cyclic group L* has order q^d-1, and
the power $(q^d-1)/(q-1)$ has image of order q-1, contained in K*.
Thus the K-determinant image of Aut_L(B) is generated exactly by
$\{a^{E_i}:a\in K^\times\}$. The extension degree d introduces a norm,
not an extra factor d in E_i.

## 4. Coefficient Frobenius and component permutations

The normal basis theorem gives a K-basis
$\theta,\varphi\theta,\ldots,\varphi^{d-1}\theta$ of L. In that basis
varphi is a d-cycle, so

$$
\det_K\varphi=(-1)^{d-1}.
$$

The coefficient action on B is the direct sum of M such actions, one for each
monomial. Therefore its determinant is

$$
(-1)^{M(d-1)}.
$$

This argument remains valid when the characteristic divides d; a permutation
matrix still has the stated determinant. The finite-field norm, cyclicity and
normal basis theorem are classical premises; see J. S. Milne,
[Fields and Galois Theory](https://www.jmilne.org/math/Books/FT0.pdf), the
sections on finite fields, normal bases, and norms. The normal basis is used
to prove the sign, not required as the supplied coordinate basis.

The nonzero primitive idempotents of A are exactly its component identities.
An algebra automorphism permutes these idempotents and restricts to an
isomorphism of their local factors. Section 3 shows that only equal types
(d, sorted heights) can be permuted. Conversely all local automorphisms and
all permutations among copies of an equal type extend to automorphisms of A;
these generate its automorphism group.

Swapping two equal factors of K-dimension D=dM exchanges D pairs of matching
basis vectors, so its determinant is (-1)^D. This is also true for separated
blocks, by conjugating the swap by a fixed coordinate reordering.

If q is odd then p and M are odd. Coefficient Frobenius contributes -1 exactly
when d is even, and a factor transposition contributes -1 exactly when d is
odd. If q is even all signs equal one. Hence the two sign conditions in
Section 1 are exact. They concern residue Frobenius and permutations of
isomorphic whole factors, respectively; they must not be conflated.

The determinant generators established so far are the E_ji power images and,
when present, -1. Writing a generator of K* as zeta, these correspond to
the integer exponents E_ji and m/2 modulo m. They generate exactly
$\langle\zeta^g\rangle=H_g$, proving the first assertion of the theorem.

## 5. Unit determinants remain surjective

For a unit a_j in B_j, write its constant term as c_j in L_{d_j}*, so
a_j=c_j+z_j with z_j in the radical. Multiplication by z_j raises total degree.
On the monomial filtration, multiplication by a_j has M_j diagonal K-blocks,
each equal to multiplication by c_j on L_{d_j}. Thus

$$
\det_K L_a=\prod_j\operatorname{Norm}_{L_{d_j}/K}(c_j)^{M_j}.
$$

This map from $A^\times$ to $K^\times$ is onto. Choose a single component j, use norm
surjectivity there, and use gcd(M_j,q-1)=1 to invert the M_j power map on K*;
put one in every other component. No coprimality involving the total dimension
n or D_j=d_jM_j is needed. When q=2 the unit one already realizes the only
possible determinant.

## 6. Normalize autotopisms and obtain the full image

Let invertible K-linear maps F,G,H on A satisfy

$$
F(x)G(y)=H(xy).
$$

Put a=F(1), b=G(1). Evaluation at the unit gives
$H=L_bF=L_aG$, so L_a and L_b are invertible and a,b are units. Set
$\sigma=L_{ab}^{-1}H$. Then sigma is invertible, sigma(1)=1, and substitution
in the displayed identity gives sigma(x)sigma(y)=sigma(xy). Hence

$$
F=L_a\sigma,\qquad G=L_b\sigma,\qquad H=L_{ab}\sigma,
\quad \sigma\in\operatorname{Aut}_K(A).
$$

Conversely these formulas define an autotopism for any two units and any
algebra automorphism. This is the unital commutative normalization retained
in PR5252 and the split product package.

In the covariant tensor convention, the stabilizer element is
$(F^{-T},G^{-T},H)$, not (F,G,H). Write
$x=\det_K L_a$, $y=\det_K L_b$, and $z=\det_K\sigma$. Its determinant
triple is

$$
(u,v,w)=(x^{-1}z^{-1},\ y^{-1}z^{-1},\ xyz),\qquad uvw=z^{-1}\in H_g.
$$

Conversely, given uvw in H_g, set

$$
z=(uvw)^{-1},\qquad x=vw,\qquad y=uw.
$$

Sections 4 and 5 provide an automorphism with determinant z and two units
with multiplication determinants x and y. They realize the requested triple.
There are m^2 choices for u,v and m/g choices for their allowed product with w,
giving |Delta|=m^3/g.

The same normalization, with multiplication on the two sides taken in two
possibly different unital commutative algebras, shows that an invertible
three-factor isotopy between them induces a K-algebra isomorphism. Therefore
different type multisets do not become GL-equivalent merely by allowing
independent input and output bases.

## 7. Attainment is constructive, without a fast-search claim

For z=zeta^k in H_g, choose Bezout coefficients

$$
g=b_0m+\sum_{j,i}b_{ji}E_{ji}+b_T(m/2),
$$

omitting the last term when the sign generator is absent. For each variable,
choose c_ji in L_{d_j}* with
$\operatorname{Norm}(c_{ji})=\zeta^{b_{ji}k/g}$, and scale that variable by
c_ji. If necessary, compose with a fixed negative-determinant coefficient
Frobenius or an allowed component transposition, to the power b_T k/g.
Determinants multiply to z. Negative integer exponents are allowed because
these maps are invertible. If H_g={1}, the identity suffices.

For a requested unit determinant x, choose a component j and an integer r
with r M_j=1 modulo m, then choose c_j with norm x^r. The componentwise unit
with that constant and ones elsewhere has determinant x. Treat m=1 separately
by returning the identity. Section 6 then gives every allowed triple.

Explicit finite-field presentations allow finite searches for primitive
elements, discrete logarithms and norm preimages, followed by exact checks.
No polynomial bit-complexity assertion in log q or compressed heights follows
from that observation. This proof does not require a field-isomorphism discovery
algorithm, a normal-basis construction, or arbitrary tensor recognition.

## 8. Supplied maps, canonical model order and SL labels

Let t:K^n x K^n -> K^n be supplied with a product model and invertible matrices
U,V,W in the convention

$$
t(Ua,Vb)=W\mu_A(a,b).
$$

Checking this equation on all n^2 model basis pairs verifies it for all inputs.
It is a certificate check, not a method of discovering the model or the maps.
Matrices act on columns, and all determinants in this section lie in K*.

The executable requires the component types to be in canonical order already
and uses the supplied residue polynomial's power basis. Thus its accepted
models have R=I in the normalization below. The general reordering argument is
a theorem about supplied models, not an assertion that the executable accepts
unsorted components or discovers missing coordinate maps.

Let R be the basis map from the canonical component order to the supplied
order, matching complete types and each residue-basis/monomial coordinate.
Because the residue presentations agree degree by degree, R is a permutation
matrix and an algebra isomorphism between those two ordered models. Normalize
the supplied maps to

$$
U_c=UR,\qquad V_c=VR,\qquad W_c=WR.
$$

The determinant product of the resulting covariant transporter
$(U_c^{-T},V_c^{-T},W_c)$ is

$$
d(t)=\frac{\det W_c}{\det U_c\det V_c}
    =\frac{\det W}{\det U\det V}\frac1{\det R}.
$$

The canonical special-linear label is

$$
\ell(t)=d(t)^{m/g}.
$$

Moving adjacent blocks of K-dimensions D_i,D_j contributes
$(-1)^{D_iD_j}$ to det R. This permutation sign must be included even when
the two types differ: R changes the ordered reference model and need not be
an automorphism of one fixed ordered model. Merely sorting type metadata and
leaving the maps unchanged can give the wrong label. Different matchings of
equal copies change R by an algebra automorphism and leave the label invariant.

To prove completeness, let G=GL_n(K)^3 and S=SL_n(K)^3. The determinant map
G -> (K*)^3 is onto with kernel S. The S-orbits inside G/Stab(mu_A) are therefore
classified by (K*)^3/Delta(mu_A). Section 6 identifies this quotient with
K*/H_g by taking the product of the three determinants. The power
d -> d^(m/g) has kernel H_g and image of size g. Thus the label is independent
of the valid supplied certificate, and two certified tensors of the same
canonical type multiset are SL-equivalent if and only if their labels agree.
This proves the orbit count as well. It does not assert that the executable
constructs an SL transporter.

If different explicit presentations of a residue field of the same degree
are supplied, equality of their degree metadata is not a coordinate map.
First supply and verify a K-field isomorphism and extend it coefficientwise
to each monomial. Include that full K-linear model identification in R and
include its determinant in the normalization above. Abstract existence follows
from uniqueness of finite fields of a given order, but this interface does not
discover such isomorphisms. Automorphisms of the base field K are never among
the allowed K-linear factor maps.

## 9. A nonprime-base discriminant for the missing norm

Take

$$
K=\mathbb F_3[t]/(t^2+1),\qquad \beta=1+t.
$$

The polynomial has no root in F3. In K, beta^2=2t and beta^4=-1, so beta has
order eight and is a nonsquare. Thus
$L=K[u]/(u^2-\beta)$ is a quadratic field extension and
$\operatorname{Norm}_{L/K}(u)=-\beta=\beta^5$.

For B=L[x]/(x^3), M=3, D=6 and E=3. The automorphism x -> u x has
L-determinant u^(0+1+2)=u^3 and K-determinant

$$
\operatorname{Norm}(u)^3=\beta^{15}=\beta^7.
$$

This element has order eight, so Aut_K(B) has the full K* determinant image.
The theorem gives gcd(8,3,4)=1. Erroneously replacing M by D makes E=6 and
predicts gcd(8,6,4)=2, missing every nonsquare determinant. The coefficient
Frobenius sign cannot repair that error because -1=beta^4 is already a square.
This fixture distinguishes the nonsplit nilpotent calculation from either
the split local formula alone or the finite-etale sign formula alone.

It also distinguishes q-Frobenius from p-Frobenius: here q=9 and p=3.
The map c -> c^3 sends t to -t and does not fix K pointwise, whereas the
coefficient map c -> c^9 is the K-linear generator of Gal(L/K).

## 10. Provenance, limits and open questions

The retained inputs and their exact heads are:

- Ali Romman's [PR5459](https://github.com/CrocSwap/integer-mult-bounds/pull/5459),
  `bef3575ddb19c44434a7e2460a353eac7c4d9387`,
  `research/frobenius-tensor-characters/README.md`: the local height flag,
  triangular determinant argument and local exponents over the coefficient field.
- apoursh's [PR5656](https://github.com/CrocSwap/integer-mult-bounds/pull/5656),
  `b5e6e7c45f606d639d102570f9fab257e1d0d393`,
  `research/frobenius-product-characters/PROOF.md`: the split product interface,
  type matching, component-order normalization and supplied-certificate labels.
- Nick Petalas's [PR5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252),
  `07e6f55d18d2d3fd6dcea19bd642d71657c5fe14`,
  `research/etale-tensor-determinant-image/README.md`: finite-etale residue signs,
  norm surjectivity and autotopism normalization.

Ali Romman's PR5637 at `86389e525d3efafe236e929f6ae401c68be1d115` also retains
credit for field and linear-algebra helpers reused by the executable. David
Ganz and the retained atlas lineage retain credit for the character/orbit
framework. Norms, restriction of scalars, normal bases and local filtrations
are classical algebra; no general literature-priority claim is made.

This contribution combines nontrivial residue fields and nilpotent truncations
in the supplied product interface. It does not perform the separately claimed
arbitrary-tensor/product-recognition task, recover field presentations, or
import a pending recognition executable as a mathematical premise.

Open next questions are to recover nonsplit factors and compatible residue-field
maps from an arbitrary tensor, and to give efficient witness construction with
explicit complexity guarantees in variable field size. A physical application
would additionally require coefficient preparation, native representation,
movement, precision, restoration and the complete supplier/caller invoice.
None of those conclusions follows from the character theorem alone.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
The written proof and finite checks are not independent human review or a
formal proof-kernel verification.
