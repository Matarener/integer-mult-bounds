# Recognition and transporters for finite etale multiplication tensors

This proof removes the orbit promise from the finite-etale tensor interface
in Nick Petalas's [PR #5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252).
It recognizes the full nonzero finite-etale multiplication class and constructs
three explicit changes of basis. The complete kappa calculation is unchanged.
This is an algebraic interface result. No physical supplier is supplied.

## Exact criterion

Let K=F_q and let nu:U times V -> W be any bilinear map, with all three spaces
of dimension n>=1. Compute the left nucleus by linear equations:

```text
N_L = {(X,Y): nu(Xu,v)=Y nu(u,v) for every u,v}.
```

Then nu is isotopic to multiplication in a finite etale K-algebra if and only
if all of the following conditions hold:

1. The nucleus has dimension n, and each projection to End(U) and End(W)
   is injective.
2. Its image B in End(W) is commutative.
3. The K-linear Frobenius map b -> b^q on B is injective.
4. The right radical {v: nu(U,v)=0} is zero.

All conditions use linear algebra and matrix products. The test does not
assume an invertible slice, an algebra basis or a list of field factors.
It rejects tensors outside this class. A failed condition is not a statement
about their other algebraic or physical uses.

## Proof and constructive transporter

For canonical multiplication in a commutative unital algebra A, putting v=1
and then u=1 in the nucleus equation shows X=Y=L_a. Independent changes of
basis conjugate its two projections. For finite etale A the resulting
nucleus has dimension n and both projections are faithful; it is commutative,
Frobenius is bijective, and the right radical is zero. This proves necessity.

For sufficiency, the nucleus contains (I,I) and is closed under pairwise
composition. The injective projections identify it with a unital matrix
algebra B and a faithful representation rho on U. Condition 2 makes B
commutative. Condition 3 implies that B has no nonzero nilpotent: an iterated
q-power would kill such an element, contrary to injectivity. A finite reduced
commutative algebra over a finite field is a product of finite fields,
B=product_i K_i. This classical structure fact is a premise, not a new claim.

Both U and W are faithful B-modules of dimension dim_K B=n. In a module for
this product, each field factor K_i occurs with a positive integer multiplicity
m_i when the action is faithful. Since sum_i m_i dim_K K_i=n=sum_i dim_K K_i,
every m_i is one. Thus both modules are regular. This dimension argument is
the required regularity implication. Faithfulness in a larger dimension
would not suffice.

Compute the primitive idempotents e_i by the predecessor's fixed-algebra
procedure. On each e_i U choose a nonzero u_i, and on each e_i W choose a
nonzero w_i. Set u0=sum_i u_i and w0=sum_i w_i. Each component is one-dimensional
over its field K_i, so the maps

```text
alpha:B -> U, a -> rho(a) u0,
gamma:B -> W, a -> a w0
```

are isomorphisms. Define Phi:V -> W by Phi(v)=nu(u0,v). If Phi(v)=0, then
nu(alpha(a),v)=a Phi(v)=0 for every a. Since alpha is onto, condition 4 gives
v=0. Hence Phi is an isomorphism. Put beta=gamma^-1 Phi:V -> B. Then

```text
nu(alpha(a), beta^-1(b)) = gamma(ab) for every a,b in B.
```

These are the requested three invertible maps. Their complete basis-product
identities give a direct certificate. B is recovered with a multiplication
table. A standard irreducible-polynomial presentation of each field is not
needed for this certificate.

The credited idempotent procedure uses C={b in B:b^q=b}, which is K^r.
Start with I, and for each basis c of C replace each nonzero current h
by the nonzero h*(I-(c-lambda I)^(q-1)) for lambda in K. These are orthogonal
indicator idempotents. The final pieces are primitive because a basis of K^r
separates its coordinates. Choose a nonzero matrix column in each piece for
u_i and w_i. The rank of e_i on W is its field degree. This also recovers the
degree multiset needed for the predecessor determinant formula.

The nucleus has 2n squared unknowns and n cubed equations. All subsequent
spaces have dimension at most n squared. There are at most n fixed-basis
vectors, n pieces and q scalars at each refinement. For fixed q, the complete
recognition and transporter algorithm is deterministic polynomial time in n.
For varying q this enumeration gives a polynomial dependence on q, not on
log q. No large-field bit-complexity claim is made.

## Exact evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/etale-tensor-recognition
```

Use Python 3.12 and the standard library. Normal and optimized modes must print
`PASS_ETALE_TENSOR_RECOGNITION` and the launcher must print
`PASS_REGISTERED_RESEARCH_PACKAGE`. The standalone implementation uses exact
prime-field fixtures. The written proof covers all finite base fields.

The checker classifies every binary two-by-two-by-two tensor. Its independent
reference is the union of all GL2-cubed images of split F2-squared and F4
multiplication. The reference does not use the nucleus test. Exactly 120 of
256 tensors are accepted; 54 fail the reducedness test and 82 fail the nucleus
dimension test. Every accepted tensor gets a literal transporter.

The full run checks 326 tensors, 187 accepted presentations, 955 transported
basis products and 21 controls. Sixty changed presentations over F2,F3,F5
include repeated field factors and three independent basis changes through
dimension four. A separate certificate check verifies the algebra's unit,
associativity, commutativity, Frobenius and all transported basis products.
Controls reject nilpotent algebras, noncommutative matrix algebras, twelve
changed transporter entries and invalid inputs. Finite evidence does not
establish proof-kernel acceptance.

## Sources and limits

The [pinned predecessor proof](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/etale-tensor-determinant-image/README.md)
supplies the left-nucleus extraction, fixed-algebra spectral projectors,
determinant formula and explicit recognition question. The new step is the
necessary-and-sufficient criterion and constructive three-map certificate.
It uses classical semisimple module structure. It does not replace the
predecessor's determinant-sign classification.

The live overlap refresh also found apoursh's
[PR #5502](https://github.com/CrocSwap/integer-mult-bounds/pull/5502).
That result recognizes supplied Frobenius-truncated prime-field algebra tables.
The present result recognizes arbitrary-basis finite-etale tensors. Their
classes and input contracts differ. No executable from that work is used.
The overlap search covered all tracked package notes, open PR bodies and
paginated Discussions; unpublished work and arbitrary historical diffs are
outside coverage.

Nilpotent multiplication tensors and arbitrary tensor isomorphism are outside
scope. The code is a bounded exact research implementation. Physical preparation,
movement, precision, supplier admission and complete recursive costs remain
open. No predecessor executable, selected cold replay, Lean or Docker run,
independent human review or formal kernel acceptance is claimed. Frozen
sources are unchanged.

## Open next questions

Extend recognition to one specified nonreduced local algebra class. Start with
a recovered local nucleus and test whether both faithful modules have cyclic
vectors. The dimension argument above fails for nonsemisimple algebras, so a
correct cyclic-vector construction or a counterexample is required before
using the same transporter formula. Coordinate with the separate supplied-table
recognition work before extending its scope.

## Credit

Nick Petalas (@petalas) supplies PR #5252 and its recognition handoff. David
Ganz and the tensor-action atlas retain the attribution in that pinned source.
Finite algebra decomposition and regular-module theory are classical. Proof
and checks by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
No global literature-priority claim is made.
