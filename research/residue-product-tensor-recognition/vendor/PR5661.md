# Recover split products from arbitrary tensors

Let K=F_q be an explicitly represented finite field of characteristic p.
For a nonempty list of sorted height lists H=(h_1,...,h_s), put

    A_H = product_j K[x_ji] / (x_ji^(p^h_ji)).

An empty height list is a field factor K. Sort the component height lists
lexicographically. Each local model uses the monomial order of the retained
PR5637 implementation. This fixes one reference tensor for each type multiset.

**Result.** For any square tensor t:K^n x K^n -> K^n, the algorithm decides
whether t is isotopic to some A_H. On acceptance it returns H and invertible
U,V,W such that t(Ua,Vb)=W ab. It also returns a complete special-linear orbit
label and constructs determinant-one factor maps between equal-label tensors.
No algebra promise, component list, common input basis or invertible slice is
supplied. The algorithm is deterministic and polynomial in n for fixed K.

The new result removes the supplied-decomposition premise of PR5656. It uses
the nucleus and local recognition results of PR5252, PR5540 and PR5637, the
height criterion of PR5502, and the product character theorem of PR5656.
These sources retain their credit. This is an algebraic interface result.
It supplies no physical supplier, paid implementation or complete kappa gain.

## 1. Recover the algebra

Solve the linear equations

    B = {(X,Y): t(Xu,v)=Y t(u,v) for every u,v}.

Require dim B=n, injective projections to X and Y, commutativity of the Y
projection, and zero right kernel of t. B is a unital algebra under componentwise
composition. The injective Y projection identifies it with a commutative matrix
algebra and gives a multiplication table and unit by linear coordinates.

For multiplication in any commutative unital algebra A, setting u=1 shows
Y(v)=X(1)v, and setting v=1 shows X=Y. Thus B is exactly the regular copy of
A. Isotopy transports both representations. All four tests are necessary.
They are not sufficient alone: both nucleus modules must also be regular.

## 2. Find the radical and every primitive idempotent

This extends Nick Petalas's fixed-algebra spectral projectors in PR5252 from
the reduced case to algebras with a nilradical. The projector formula itself
is retained mathematical precedent.

Write J for the nilradical of B. A finite-dimensional commutative algebra has
a decomposition into local Artinian factors. Here is the needed nilpotence
bound. Its radical is nilpotent: choose a finite basis of nilpotent generators;
every sufficiently long monomial contains a generator to a zero power. If two
successive nonzero powers J^k and J^(k+1) were equal, iteration would contradict
nilpotence. Their dimensions strictly decrease until zero. Therefore J^n=0.

Let Q be the least q-power at least n. The map b -> b^Q is K-linear. Its kernel
is J: it kills J by the bound above, and any element it kills is nilpotent.
This calculates J with exact linear algebra.

The reduced quotient B/J is a product of finite residue fields. Primitive
idempotents lift uniquely through J. For existence, lift an idempotent to b;
then (b^2-b)^Q=0 gives an idempotent b^Q with the same residue. For uniqueness,
if idempotents e,f differ by an element of J, their commuting products e(1-f)
and f(1-e) are nilpotent idempotents, hence zero. Thus e=f.

Let C=ker(b -> b^q-b). On each local factor the only fixed elements are the
scalars in K times that factor's unit. Indeed, its residue must lie in F_q.
After subtracting that scalar, a fixed nilpotent z satisfies z=z^(q^a)=0 for
large a. Hence C is K^s, where s is the number of local factors. The dimensions
give the exact split-residue test

    dim(B/J) = dim C.

Each residue-field degree is positive. Equality holds precisely when every
degree is one. A nonsplit residue field is rejected, even when its q-power
map is invertible.

Choose any K-basis c_1,...,c_s of C. Start with the part 1. For each c_i and
each lambda in K, refine every current part e by

    e * (1 - (c_i-lambda*1)^(q-1)),

and discard zero results. In C=K^s this is the characteristic function of the
coordinates where c_i=lambda. The full basis separates every pair of distinct
coordinates. The resulting nonzero parts are exactly the s primitive
idempotents. Stop once s parts are present. This works when s>q; it does not
assume that one element separates all components. It also works with nonzero
nilpotent directions because every c_i belongs to the fixed subalgebra.

## 3. Recover regular-module generators without enumeration

For either nucleus module M, let M_j=e_j M. Compute JM_j from the literal
matrix actions. Require dim(M_j/JM_j)=1 for every j. Choose a basis vector of
M_j outside JM_j and call it m_j. Set m=sum_j m_j.

In a regular module these dimensions are one because the residue fields are
K. Conversely, the cyclic submodule Bm maps onto each component's top. The
quotient N=M/Bm satisfies N=JN. Iteration and J^n=0 give N=0. Thus m is cyclic.
Since dim B=dim M=n, b -> bm is an isomorphism. This proves sufficiency and
gives a deterministic generator selection, without enumerating q^n vectors.

Let u0,w0 be the generators for the X and Y actions. Define

    alpha(b)=X_b u0, gamma(b)=Y_b w0, Phi(v)=t(u0,v).

If Phi(v)=0, the nucleus identity and cyclicity give t(u,v)=0 for every u.
The zero right kernel makes Phi invertible. Set beta=Phi^-1 gamma. Then

    t(alpha(a),beta(b)) = Y_a gamma(b) = gamma(ab).

This gives three factor maps from B to the original tensor. The algorithm
checks each primitive component separately and then checks the generator
matrices for invertibility.

## 4. Recognize each local factor and fix its basis

For e_j, obtain a basis for e_j B from the columns of multiplication by e_j.
Restrict the recovered table to that basis. Apply the retained finite-field
recognizer of PR5637. It accepts exactly the split Frobenius-truncated local
algebras. Its semilinear p-power kernels recover the height flag; q-power
Frobenius is used only for the radical. The two operations are not exchanged.

The local routine returns maps U_j,V_j,W_j with

    U_j(a) V_j(b) = W_j(ab).

They need not be the same map. Put c=W_j(1). Setting one argument to 1 shows
that U_j(1) and V_j(1) are units: their multiplication maps are compositions of
invertible factor maps. Their product is c. The normalized map

    sigma_j = L_c^-1 W_j

is a unital algebra isomorphism. Indeed, evaluation at 1 gives
U_j=L_(U_j(1)) sigma_j and V_j=L_(V_j(1)) sigma_j; substitution gives the
multiplication identity for sigma_j. The algorithm applies this normalization.
Treating W_j itself as an algebra isomorphism would be incorrect.

Embed each sigma_j into B, sort the components by their full height lists,
and concatenate the actual basis columns into C. Set

    U=alpha C, V=beta C, W=gamma C.

All n^2 transported basis products are checked. Bilinearity makes this a
certificate for all inputs. Rejected local factors cannot be replaced by
equal-dimensional ones: the height multiset is intrinsic. Necessity follows
from the primitive decomposition of A_H and the local recognition theorem.
Sufficiency follows from the explicit maps. This proves the recognition result.

## 5. Product characters and determinant-one maps

Use the exact theorem of PR5656. For component dimension N_j=p^(sum_i h_ji),
let E_ji=N_j(p^h_ji-1)/2. Let g be the gcd of q-1 and all these integers,
including (q-1)/2 if q is odd and some full component type repeats. If there
are no variables and no such repetition, g=q-1. The automorphism determinant
image is the subgroup of g-th powers in K*. The covariant tensor stabilizer
has determinant products in that same subgroup.

Define

    d=det(W)/(det(U)det(V)), label=d^((q-1)/g).

The full height-type multiset and label decide special-linear equivalence.
The basis concatenation above fixes the component-order determinant sign;
sorting metadata without reordering the matrix columns would lose it.

For two equal-label certificates, set a=det(U1)/det(U2), b=det(V1)/det(V2),
c=det(W1)/det(W2). Construct a model automorphism sigma of determinant z=ab/c.
Bezout coefficients for the character exponents give it as variable scalings
and, when needed, one transposition of identical odd-dimensional components.
The implementation uses the literal block permutation, not a free scalar sign.

The unit-multiplication determinant map is onto K*: choose one component of
dimension N_j, which is coprime to q-1, and vary only its scalar constant.
Choose units x,y with determinants a/z,b/z. Then
(L_x sigma,L_y sigma,L_(xy) sigma) has determinants a,b,c. Compose these maps
between the second certificate and the inverse first certificate. The resulting
F,G,H have determinant one and satisfy t2(Fu,Gv)=H t1(u,v). The checker verifies
all three determinants and every basis product. The total product dimension
need not be coprime to q-1; no inverse of that total dimension is used.

## 6. Cost, use and limits

The nucleus has n^3 equations in 2n^2 unknowns. Dense elimination uses O(n^7)
field operations. The component refinements use at most n^2 q exponentiations
with exponent q-1; dense algebra multiplication costs O(n^3). The local
recognizers cost at most the sum of their dimension-seventh powers, bounded
by n^7. Module, coordinate and product checks are polynomial as well. A
conservative total bound is O(n^8 + q*n^6*log(q*n) + q^2) field operations,
with polynomial space. This is polynomial in n for fixed q. The explicit
field tables and primitive-element/discrete-log enumeration are not polynomial
bit algorithms in log q. No such uniform claim is made.

This closes the decomposition-discovery task for the declared split product
class, including extension fields, repeated factors, nilpotents, and independent
tensor factor bases. It does not recognize arbitrary commutative algebras or
nontrivial residue extensions. The tensor atlas can now check this class from
raw tensors and return exact maps. A physical application must still pay for
coefficient operations, native realization, ownership, restoration, storage,
precision and the whole supplier/caller. These costs are unknown here. The
complete kappa calculation and selected frontier are unchanged.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0. The same
assistant supplied the proof and checks. Independent human and formal review
remain open.
