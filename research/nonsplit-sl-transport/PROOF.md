# Field-presentation bridges and nonsplit special-linear transport

This package connects Ali Romman's arbitrary-tensor recognition in PR5664 to
the supplied-model determinant theorem in apoursh's PR5663. The reference
residue fields are explicit inputs. They are not discovered canonical
presentations of abstract finite fields. All maps in this note are linear
over the same explicitly represented base field; semilinear base-field
automorphisms are outside the contract.

The new field-table bridge, its extension to local products, and the exact
determinant correction are proved below. The recognition theorem and the
automorphism character theorem are retained predecessor results, not new
claims of this package. No native supplier, physical cost improvement or new
kappa follows from these algebraic interfaces.

## 1. Common reference model and predecessor contracts

Fix $K=\mathbf F_q$ of characteristic $p$. For every residue degree used by
the requested reference model, fix an explicit extension $L_d/K$ and an
ordered $K$-basis starting with one. Set

$$
A=\prod_j L_{d_j}[x_{j1},\ldots,x_{js_j}]/
       (x_{ji}^{p^{h_{ji}}}:1\leq i\leq s_j),\qquad h_{ji}\geq1.
$$

Empty height lists are allowed. Order types $(d_j,(h_{ji})_i)$
lexicographically, with each height list sorted. Within each component, order
variable monomials lexicographically, then coefficient basis vectors. Every
component of the same residue degree uses the same reference field
presentation. Write $n=\dim_K A$ and $\mu_A$ for its multiplication table.

PR5664 recognizes an arbitrary square tensor $t:K^n\times K^n\to K^n$ in
the declared Frobenius-product class. An accepted certificate supplies a
product $B$ whose coefficient fields are multiplication tables in discovered
bases, together with invertible matrices $U_B,V_B,W_B$ satisfying

$$
t(U_Ba,V_Bb)=W_B\mu_B(a,b).
$$

Its coefficient tables have first basis vector one; the local basis is
monomial first, then coefficient basis. Its certificate checker verifies
field tables and every basis-product identity. The adapter first checks this
contract, including canonical base-field coordinates and matrix shapes.

Let $m=q-1$, $N_j=p^{\sum_i h_{ji}}$, and
$E_{ji}=N_j(p^{h_{ji}}-1)/2$. PR5663 proves

$$
\det_K\operatorname{Aut}_K(A)=H=(K^\times)^g,
$$

where $g$ is the gcd of $m$ and all $E_{ji}$, also including $m/2$ exactly
when $q$ is odd and either some $d_j$ is even or an identical full type with
odd residue degree repeats. It also constructs every multiplication
autotopism determinant triple $(a,b,c)$ for which $ab/c\in H$.
The integer $N_j$ is the dimension over the residue field, not over $K$.
The gcd of the list containing only $m$ is $m$; for $q=2$, $m=g=1$.

## 2. A field isomorphism from a tensor-product factor

Let $C,D$ be two degree-$d$ finite field extensions of $K$, supplied as
checked multiplication tables in bases beginning with one. We construct a
$K$-algebra isomorphism $Q:C\to D$ without listing the $q^d$ elements of
either field.

Form $E=C\otimes_K D$ in its tensor-product basis. Its dimension is $d^2$,
its unit is the first basis vector, and its structure constants are

$$
(c_i\otimes d_j)(c_k\otimes d_\ell)
 =\sum_{r,s} C_{ik}^{r}D_{j\ell}^{s}(c_r\otimes d_s).
$$

**Lemma 1.** The algebra $E$ is a product of $d$ copies of a degree-$d$
field over $K$.

**Proof.** Finite extensions of finite fields are simple and separable.
Write $C=K[z]/(f)$, where $f$ is irreducible of degree $d$. Every root of
$f$ lies in a field of cardinality $q^d$; hence $f$ splits in $D$ into $d$
distinct linear factors. Thus $C\otimes_KD=D[z]/(f)\cong D^d$ by the
Chinese remainder theorem. This argument proves the structure; the algorithm
does not first find $z$, $f$, or any roots. These finite-field facts are
classical; see Milne's [Fields and Galois Theory](https://www.jmilne.org/math/Books/FT0.pdf),
the section on finite fields and the discussion of etale algebras. $\square$

The $q$-power map is $K$-linear. Its fixed algebra

$$
F=\ker(\operatorname{Frob}_q-I:E\to E)
$$

is consequently found by base-field linear algebra. By Lemma 1 it is
isomorphic to $K^d$ and has dimension $d$. Use the retained primitive-factor
procedure on a basis of $F$: for $c\in F$ and $a\in K$, the element

$$
s_{c,a}=1-(c-a1)^{q-1}
$$

is the indicator of the coordinates of $K^d$ where $c$ equals $a$. Starting
with the idempotent one, refine each current nonzero idempotent $e$ into the
nonzero products $es_{c,a}$ for all $a\in K$.

**Lemma 2.** After processing a basis of $F$, the surviving elements are
exactly the $d$ primitive idempotents of $E$.

**Proof.** The indicator formula follows from $b^{q-1}=1$ for nonzero
$b\in K$ and $0^{q-1}=0$. Therefore each refinement partitions the support
of a current indicator, preserving disjointness and total sum one. Any two
distinct coordinates of $K^d$ differ on some basis element: otherwise their
evaluation functionals would agree on every vector of $K^d$. Thus all
remaining supports are singletons. Stopping early when their number reaches
$d$ is also valid, because a partition of $d$ coordinates into $d$ nonempty
supports consists of singletons. $\square$

Choose any resulting primitive idempotent $e$. Define maps into $eE$ by

$$
J_C(c)=e(c\otimes1),\qquad J_D(d')=e(1\otimes d').
$$

**Lemma 3.** Both maps are $K$-algebra isomorphisms onto $eE$, with units
sent to $e$. Therefore the matrix equation $J_DQ=J_C$ has a unique solution,
and this solution is a $K$-algebra isomorphism $Q:C\to D$.

**Proof.** The maps are unital homomorphisms into the algebra with unit $e$.
For a nonzero element of either field, multiplication by its inverse proves
that its image is invertible in $eE$. Thus each map is injective. Lemma 1
gives $\dim_K eE=d$, so each is surjective. Solving the displayed equation
in the ambient $d^2$ coordinates gives $Q=J_D^{-1}J_C$. $\square$

The returned matrix is checked independently of the choice of idempotent:
it must be invertible, send one to one, and satisfy

$$
\mu_D(Qc_i,Qc_j)=Q\mu_C(c_i,c_j)
$$

for every basis pair. Bilinearity then proves the identity for all elements.
For $d=1$, both unit-first field tables are the table of $K$, the only
primitive idempotent is one, and the map is the identity. Unequal degrees
cannot admit such an isomorphism and are rejected before construction.

The bridge uses arithmetic on a $d^2$-dimensional algebra, kernels, matrix
solves, and enumeration of the $q$ base-field scalars. All dimensions and
loop counts are polynomial in $d$ for fixed $K$. Exponentiation uses repeated
squaring. It does not enumerate the $q^d$ residue elements. No complexity
claim polynomial in $\log q$ is made; explicit dense tables and enumeration
of base-field scalars are part of the interface.

## 3. Extend the field maps and match complete component types

The predecessor classification makes the multiset of full types
$(d,(h_i)_i)$ intrinsic. Degree alone, total $K$-dimension alone, or the sum
of heights is insufficient to match local factors. When comparing two
tensors, reject unequal full type multisets. For each accepted type multiset,
the supplied reference residue fields determine its common reference model.

For every matched pair of components, use Section 2 to identify its reference
coefficient field with its discovered coefficient field. Extend this map
coefficientwise, fixing the ordered variable monomials. A field isomorphism
preserves multiplication of coefficients, and fixing variable exponents
preserves precisely the monomials killed by the truncation ideals. Hence the
extension is an algebra isomorphism of local factors.

Assemble these local maps and the actual component placement into a single
matrix $S:A\to B$. Every model coordinate, including coefficient coordinates,
is placed in its matched component's position. The resulting map obeys

$$
\mu_B(Sa,Sb)=S\mu_A(a,b).
$$

The normalized certificate checks in Section 4 also certify this assembled
identity: the original certificate has already been verified, and its factor
maps are invertible. If component matching permutes blocks, its determinant is part of
$\det S$; there is no implicit assumption that this reordering is even.
Swapping equal types is allowed, whereas swapping unequal types is not a
substitute for a checked algebra isomorphism.

## 4. Normalize maps and retain the bridge determinant

Given the verified discovered-model certificate, put

$$
U=U_BS,\qquad V=V_BS,\qquad W=W_BS.
$$

Then

$$
t(Ua,Vb)=t(U_BSa,V_BSb)
 =W_B\mu_B(Sa,Sb)=W_BS\mu_A(a,b)=W\mu_A(a,b).
$$

Thus $(U,V,W)$ is a checked certificate from the common reference model.
Define

$$
\delta(t;U,V,W)=\frac{\det W}{\det U\det V},\qquad
\lambda_A(t)=\delta(t;U,V,W)^{m/g}.
$$

Normalization changes the discovered-model determinant ratio by

$$
\delta(t;U_BS,V_BS,W_BS)
 =\frac{\delta(t;U_B,V_B,W_B)}{\det S}.
$$

Ignoring this denominator can give a false orbit label. For example, a
single degree-three field over $\mathbf F_3$ has $H=\{1\}$ and $g=2$.
Changing its coefficient basis by $\operatorname{diag}(1,2,1)$ changes the
uncorrected ratio by $-1$. The explicit bridge restores the common-reference
label. The example tests a proper subgroup; a quadratic field over
$\mathbf F_3$ has the whole group as determinant image and would not detect
this error.

**Lemma 4.** The label $\lambda_A(t)$ is independent of all checked
field-bridge choices, equal-type matching choices, and recognition
certificates, for the fixed reference model $A$.

**Proof.** If $S,S':A\to B$ are two checked bridges, then
$S'=S\sigma$ for $\sigma\in\operatorname{Aut}_K(A)$. Thus their
normalized determinant ratios differ by $(\det\sigma)^{-1}\in H$.
More generally, any two certificates from $A$ to the same tensor differ
by a multiplication autotopism of $A$. PR5663's normalization theorem says
its determinant ratio lies in $H$. The homomorphism
$x\mapsto x^{m/g}$ on the cyclic group $K^\times$ has kernel exactly
$H=(K^\times)^g$, so all these differences disappear in the label.
$\square$

This is a label relative to the chosen ordered reference presentations.
Changing that reference may relabel all orbits by a fixed common factor.
Comparisons must use the same reference model; no abstract, presentation-free
choice of a preferred finite-field isomorphism is asserted.

## 5. Determinant-one transporters

Let accepted tensors $t_1,t_2$ have checked normalized certificates
$(U_i,V_i,W_i)$ from the same reference $A$. Write
$u_i=\det U_i$, $v_i=\det V_i$, $w_i=\det W_i$, and
$\delta_i=w_i/(u_iv_i)$.

If their labels agree, then $\delta_2/\delta_1\in H$. The predecessor
constructor therefore provides a multiplication autotopism $(F,G,J)$ with

$$
\mu_A(Fa,Gb)=J\mu_A(a,b),\qquad
\det F=u_1/u_2,\quad \det G=v_1/v_2,\quad \det J=w_1/w_2.
$$

Its required determinant condition holds because

$$
\frac{\det F\det G}{\det J}=\frac{\delta_2}{\delta_1}\in H.
$$

Set

$$
P=U_2FU_1^{-1},\qquad
Q=V_2GV_1^{-1},\qquad
R=W_2JW_1^{-1}.
$$

These matrices have determinant one and satisfy

$$
t_2(Px,Qy)=R\,t_1(x,y).
$$

Indeed substitute $x=U_1a,y=V_1b$ and use both certificates and the
autotopism identity. Invertibility extends the result to every pair of
inputs. The executable checks all basis pairs and all three determinants.

Conversely, such a determinant-one isotopy, composed with the two model
certificates, gives an autotopism whose determinant condition forces
$\delta_2/\delta_1\in H$. Therefore the labels agree if and only if a
determinant-one isotopy exists. Different full type multisets cannot be
isotopic: the unital commutative isotopy normalization in the predecessors
would produce an algebra isomorphism, contradicting their intrinsic local
types. The character theorem supplies exactly $g$ labels in each GL orbit.

For the tensor in $(K^n)^*\otimes(K^n)^*\otimes K^n$, the corresponding
covariant action is

$$
t_2=(P^{-T}\otimes Q^{-T}\otimes R)t_1.
$$

The inverse transposes on the two input factors are required. The bilinear
identity and this tensor-coordinate identity are separate useful checks;
the literal triple $(P,Q,R)$ is generally not the covariant transporter.

## 6. Scope and verification boundary

This connects arbitrary-tensor recognition to a fixed-reference complete
orbit test and an explicit transporter. It does not accept unchecked
field tables, unchecked maps, or equality of dimensions as certificates.
It does not identify different presentations of the base field, permit
semilinear base automorphisms, or infer missing reference residue fields.

Only the field-table bridge is claimed polynomial in residue degree for
fixed $K$. The retained explicit-extension implementation constructs
residue arithmetic tables and searches finite sets for norm preimages and
determinant witnesses. The full implementation therefore inherits those
enumerative costs; no polynomial-in-dimension or polynomial-in-$\log q$
bound for the complete transporter pipeline is claimed.

Finite tests support the implementation and detect convention, basis and
certificate failures. They do not replace the all-dimension arguments above,
validate the entire multiplication theorem, or provide independent human or
proof-kernel acceptance. Physical preparation, native realization, storage,
ownership, cleanup, precision and the complete paid caller remain unpriced.

Credit Ali Romman for PR5664 recognition, PR5661 product recovery and the
retained PR5637 finite-field helpers; apoursh for PR5663 characters, PR5656
split-product characters and PR5502 height recognition; Nick Petalas for
PR5252's etale and determinant interface; David Ganz and the retained atlas
lineage. Tensor products, finite-field structure and spectral idempotents are
classical. The new contribution is the checked bridge and its composition
with these particular recognition and character interfaces. Prepared by
apoursh with substantial OpenAI Codex assistance. Apache-2.0.
