# Extension-field tensor recognition and special-linear orbit labels

This package recognizes, from an arbitrary square tensor over an explicit
finite field K=F_q of characteristic p, the multiplication tensors of

    K[x_1,...,x_s]/(x_i^(p^h_i)),  h_i >= 1.

It returns the heights and three invertible maps U,V,W with
`t(Ua,Vb)=W mu(a,b)`. The empty height list gives K. The test is necessary
and sufficient. It uses deterministic polynomial time in the tensor dimension
for each fixed field. No algebra-class or common-basis promise is required.

The result also removes the recognition promise from the determinant-character
formula of PR #5459. For each accepted tensor it returns the exact number of
special-linear orbits in its general-linear orbit and a complete orbit label.
Two accepted tensors over the same explicit field are equivalent under the
product of three special linear groups if and only if their height lists and
labels agree. This supplies an executable input test for that atlas interface.
It also constructs determinant-one factor maps between equivalent accepted
tensors. It supplies no physical tensor implementation, paid supplier or kappa increase.

## Sources and scope

Main is `6cf7a683f447b9f1e2333791907fd92be5009a63`, priority revision 7.
The [released handoff and claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19186074)
identify the extension-field gap. A complete cached open-PR and Discussion
search and a search of every tracked main research README/TASK file found no
active claim on this scope. These searches do not prove global novelty.

The three proof inputs are pinned in `SOURCES.json`, authenticated on replay,
and preserved without changes. No predecessor executable is imported.

- Ali Romman's [PR #5540](https://github.com/CrocSwap/integer-mult-bounds/pull/5540)
  gives the prime-field tensor reconstruction, the regular-module criterion,
  and this extension-field handoff. Its
  [retained proof](https://github.com/CrocSwap/integer-mult-bounds/blob/6cf7a683f447b9f1e2333791907fd92be5009a63/research/nonreduced-tensor-recognition/README.md)
  credits Nick Petalas's [PR #5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252)
  for the nucleus method and Ali Romman's
  [PR #5525](https://github.com/CrocSwap/integer-mult-bounds/pull/5525) for its implementation.
- apoursh's [PR #5502](https://github.com/CrocSwap/integer-mult-bounds/pull/5502)
  gives the prime-field height flag and dimension criterion. Its
  [retained proof](https://github.com/CrocSwap/integer-mult-bounds/blob/6cf7a683f447b9f1e2333791907fd92be5009a63/research/frobenius-algebra-recognition/PROOF.md)
  explicitly leaves extension fields open.
- Ali Romman's [PR #5459](https://github.com/CrocSwap/integer-mult-bounds/pull/5459)
  gives the finite-field stabilizer determinant image under an algebra-class
  promise. Its
  [retained proof](https://github.com/CrocSwap/integer-mult-bounds/blob/6cf7a683f447b9f1e2333791907fd92be5009a63/research/frobenius-tensor-characters/README.md)
  supplies the character theorem used below. David Ganz and the atlas lineage
  retain credit for the orbit and character framework.

The new work supplies the finite-field contract, semilinear kernel correction,
composed recognition and orbit label, proof below, and a separate implementation.
It extends the stated local truncated-polynomial class. It does not extend
PR #5540's general commutative-algebra recovery to all residue fields or products.

## Input and output contract

`Field(p, modulus)` uses a monic polynomial over F_p, with coefficients in
constant-first order. An element is the integer whose base-p digits are its
polynomial coefficients of degrees less than the modulus degree e. All entries
must be canonical integers from 0 through q-1, where q=p^e. The constructor
checks primality by trial division, builds quotient-ring addition and
multiplication tables, and checks that each nonzero element has an inverse.
A finite commutative unital ring with this property is a field. Thus this test
rejects every reducible modulus, including repeated factors.

`recognize(t, field)` uses `t[i][j][k]` for the output coefficient k of basis
inputs i,j. All three dimensions must equal n>0. Invalid shapes or entries
raise `ValueError`. A well-formed tensor outside the class returns
`(None, reason)`. Acceptance returns `(certificate, None)`. The certificate
contains `heights`, `U`, `V`, `W`, `sl_orbit_count` and `sl_orbit_label`.
`sl_transporter(first, second, field)` returns determinant-one matrices F,G,H
with `second(Fu,Gv)=H first(u,v)`, or a rejection reason.
Matrix columns are basis images. The field object must retain its constructed
operation tables. Different presentations of the same field require an
explicit field isomorphism before labels can be compared.

## Reconstruct the local algebra and its factor maps

Solve the linear nucleus equations

    B = {(X,Y): t(Xu,v)=Y t(u,v) for all u,v}.

Require dimension n, injective projections to both matrix algebras,
commutativity, and zero right kernel for t. The nucleus is automatically a
unital algebra under componentwise composition: composing two identities gives
the product identity. The faithful Y projection gives coordinates for its
multiplication table and identity.

Let Q=q^a be the least q-power at least n. The map b -> b^Q is K-linear,
because each coefficient in K is fixed by q-power Frobenius. Its kernel J is
the nilradical. Indeed, in a finite-dimensional commutative unital algebra the
nilradical is nilpotent and J^n=0. A proof uses a finite nilpotent generating
set and the strictly decreasing power chain until zero. Thus this power kills
every nilpotent and kills no other element. Require `dim J=n-1`. Then B is
local with residue field K: every element outside J is a nonzero scalar plus
a nilpotent and has an inverse by the finite geometric series.

For each nucleus module M=U or W, form JM from the columns of the radical
matrices and require `dim(M/JM)=1`. Choose a coordinate vector m outside JM.
It generates the quotient. For C=Bm, the quotient M/C satisfies M/C=J(M/C).
Iteration through J^n=0 gives M=C. Its dimension equals dim B, so b -> bm is
an isomorphism. Obtain cyclic vectors u0,w0 and matrices

    alpha(b)=X_b u0,   gamma(b)=Y_b w0,   Phi(v)=t(u0,v).

If Phi(v)=0, cyclicity of u0 and the nucleus identity give t(U,v)=0. The zero
right kernel makes Phi invertible. Set beta=Phi^-1 gamma. Then

    t(alpha(a),beta(b)) = Y_a gamma(b) = gamma(ab).

This constructs the three factor maps to B without a search over vectors or
invertible slices. Necessity follows from ordinary multiplication: evaluating
the nucleus identity at 1 in each input shows that both X and Y are
multiplication by the same algebra element. Both modules are regular.
The argument is valid over K; it does not require a prime field.

## The semilinear height flag

For h>=0, form C_h by raising each algebra basis element to p^h. With
sigma(c)=c^p on coefficients, the actual map on coordinate vectors is

    F^h(v) = C_h sigma^h(v).

Consequently a basis of its kernel is obtained by applying sigma^(-h) to a
basis of the ordinary K-linear kernel of C_h. The inverse twist on F_q is
`c -> c^(p^((-h) mod e))`. This is a semilinear change of coordinates, so it
preserves independence and spans the full kernel. An ordinary kernel basis
without this twist need not contain nilpotent elements. Likewise, C_1^h is
not the matrix of F^h: composition twists the next matrix's coefficients.
The implementation computes the actual basis powers separately at each h.

Let H be the least integer with p^H>=n. Set K_h=ker F^h and

    V_h=(K_h+J^2)/J^2,   d_h=dim V_h-dim V_(h-1),
    N=p^(sum_h h d_h).

Choose representatives of each newly independent tangent class directly in
K_h, assign them height h, and call them g_i. Accept exactly when N=n.

For necessity, in the target algebra J/J^2 has basis the variables. A nonzero
coefficient of x_i with h_i>h survives F^h as a nonzero coefficient of
x_i^(p^h). No other linear term, or term of degree at least two, can cancel
this monomial. The coefficient twist is a field automorphism and cannot turn
a nonzero coefficient into zero. Thus V_h is exactly the span of variables
with height at most h. The flag recovers all heights and N=n.

For sufficiency, each g_i satisfies its required power relation, and the g_i
span J/J^2. They generate the algebra: expand products in J^k using their
linear parts to obtain `J^k subset C+J^(k+1)`, where C is their unital
subalgebra. Iterate until J^n=0. Substitution therefore gives a surjection
from the proposed truncated-polynomial algebra of dimension N to B. If N=n,
it is an isomorphism. Its matrix C consists of the ordered monomials in g_i.
Compose alpha C, beta C, gamma C to obtain U,V,W. Every basis product of these
maps is checked before acceptance. This proves both directions and supplies
explicit certificates. For n=1, J=0 and the height list is empty.

The q-power computation is used for the radical. The p-power flag is used for
heights. They cannot be interchanged: over F4, K[x]/x^4 has height two even
though fourth powers already kill its entire radical.

## Recover the special-linear orbit label

Let the accepted dimension be n and define

    h=gcd(q-1, n(p^h_1-1)/2, ..., n(p^h_s-1)/2).

Each exponent is an integer. With no variables, use h=q-1. The pinned PR #5459
theorem gives the stabilizer determinant image for the covariant action on
`A* tensor A* tensor A`:

    Delta = {(a,b,c): (abc)^((q-1)/h)=1}.

The empty-height case follows directly: multiplication in K has stabilizer
triples with abc=1. The product of the three determinant-one groups is the
kernel of the determinant map. Hence the number of its orbits in this GL
orbit is h.

Our certificate gives the tensor action `(U^-T,V^-T,W)`. Its determinant
product is `d=det(W)/(det(U)det(V))`. Define the label

    label = d^((q-1)/h) in K*.

Two choices of transporter differ by a stabilizer element, whose determinant
product has this power equal to one. The label is therefore intrinsic. The
map `K* -> K*`, d -> d^((q-1)/h), has kernel the h-th power subgroup, exactly
the possible stabilizer products. Its fibers are exactly the cosets of Delta,
so label equality is necessary and sufficient within the fixed height class.
The height list itself is intrinsic by the flag proof. This proves the stated
classification for all accepted tensors. It does not classify tensors outside
this family or claim a new proof of PR #5459's character formula.

## Construct determinant-one maps

For two equal-label certificates (U1,V1,W1) and (U2,V2,W2), put
`a=det(U1)/det(U2)`, `b=det(V1)/det(V2)`, `c=det(W1)/det(W2)`.
A model autotopism with these three determinants makes the composite maps
from the first tensor to the second have determinant one. Write the model
autotopism as `(L_x sigma,L_y sigma,L_(xy) sigma)`. Its required automorphism
determinant is `z=ab/c`; its unit determinants must be `a/z` and `b/z`.
Equal labels put z in the character subgroup H_h.

Find a generator g of K* by enumeration, and write z=g^k. Bezout coefficients
for `h=gcd(q-1,E_1,...,E_s)`, where `E_i=n(p^h_i-1)/2`, give integers b_i
with `sum b_i E_i = h mod (q-1)`. Scale variable i by `g^(b_i k/h)`.
This defines a diagonal algebra automorphism sigma with determinant z. Since
n is a power of p, n is invertible modulo q-1. Scalar units x,y can therefore
supply the required determinants: raise a/z and b/z to that inverse power.
The resulting three model maps have determinants a,b,c. Compose them between
the second certificate and the inverse first certificate. The implementation
checks all three determinants and every transported basis product. This gives
an explicit special-linear transporter without enumerating algebra bases or
automorphisms. Field generator and discrete-log enumeration are bounded by q;
the stated polynomial guarantee remains for fixed q. The empty-height and
q=2 cases use the same formulas with the trivial multiplicative group.

## Verification and cost

Run:

```sh
python3.12 -B scripts/research_package.py --package research/extension-field-tensor-recognition
```

The standard library suffices. The registered normal and optimized commands
print `PASS_EXTENSION_FIELD_TENSOR_RECOGNITION`. Every check uses explicit
exceptions and remains active under `-O`.

The complete F4 2x2x2 domain contains 65,536 tensors. Exactly 13,500 pass,
with exact agreement with a separate orbit generator that applies elementary
GL2 matrices to the three literal coefficient indices. The complete binary
domain gives 54 accepted tensors out of 256. Every accepted transporter is
checked by all basis products. The orbit generator does not use the nucleus,
radical, regular-module or height tests. These complete finite checks do not
replace the written proof in other dimensions.

Ninety changed-basis presentations cover F2,F3,F4,F8,F9,F16,F25, dimensions
through nine, empty and unequal heights, 2,322 transported products, and 90
comparisons of orbit labels with known factor maps. Ninety additional
determinant-one transporters pass all 2,322 basis products. The 125 controls include
altered transporters, reducible field polynomials, extra algebra relations,
nonregular dual modules, split algebras and invalid tensors. Over F4, write
a^2=a+1 and use basis `(1,a+x)` for K[x]/x^2. The ordinary kernel of the
squaring columns is `(a^2,1)`, which represents `1+x` and squares to 1. The
correct kernel is `(a,1)`, which represents x and squares to zero. A second
control rejects ordinary matrix iteration. The cutoff-four and two-variable
cutoff-two algebras have orbit counts three and one; all three labels of the
first algebra are attained by explicit output scalings.

The nucleus has n^3 equations in 2n^2 unknowns. All subsequent steps use
matrix arithmetic, algebra powers and at most ceil(log_p n) kernel levels.
The model monomials are built only after the dimension test accepts, so there
are exactly n. These are deterministic polynomial operations in n at fixed q.
The constructor builds O(q^2) field tables and uses trial-division primality;
there is no polynomial bit-complexity claim in log q. The proof inputs and
finite field operations are checked, but no prior full executable suite,
proof assistant, selected cold replay or independent human review was run.

## Open next questions

- Extend the certificate to products and larger residue fields. First specify
  component matching and field-isomorphism data; the local residue-K test here
  must not be silently removed.
- Use a recognized tensor in a named native producer/consumer pair. Charge its
  field representation, coefficients, movement, precision and restoration before
  drawing a kappa conclusion. No such physical cost is zero by this result.

New work: Ali Romman (@aliromman), with substantial OpenAI Codex assistance.
Predecessor methods: apoursh (@apoursh), Nick Petalas (@petalas), David Ganz,
and the linked sources. Apache-2.0. No general literature-priority claim.
