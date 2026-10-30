# A complete restricted recovered-algebra isomorphism test

Produced by Nick Petalas. Apache-2.0.

## 1. Contract and multiplication form

Let K be a finite field of odd order q. Let A be a finite-dimensional,
commutative, associative, unital local K-algebra, with radical J, residue
A/J=K, nonzero one-dimensional J^2 and J^3=0. Require its socle
Ann_A(J) to equal J^2. Put r=dim_K J/J^2. Necessarily r>=1.

Choose a nonzero s in J^2 and a K-linear complement V of J^2 in J.
Then A=K*1 direct-sum V direct-sum K*s. Since J^3=0, there is a symmetric
bilinear form B on V such that

```text
uv = B(u,v)s,   us = s^2 = 0,  for u,v in V.
```

The form is nondegenerate. A vector in its radical annihilates J, so would
belong to the socle J^2 while lying in its chosen complement. Conversely,
every nondegenerate symmetric r-dimensional B defines such an algebra A_B.
Associativity follows because every product of three elements of J is zero.
The socle contains no element with nonzero constant coefficient, and its
intersection with V is zero by nondegeneracy. Thus it is exactly K*s.

Adding multiples of s to the chosen lifts does not change B. A change of
basis in V replaces B by a congruent form; rescaling s multiplies B by a
nonzero scalar. These choices are the only ambiguity relevant below.

## 2. Isomorphism is similarity of forms

A unital K-algebra isomorphism preserves J and J^2. Between A_B and A_D
it therefore has the shape

```text
1 -> 1,    u -> P u + ell(u)s,    s -> c s,
P invertible, c nonzero.
```

Multiplication preservation is equivalent to

```text
P^T D P = c B.                                      (1)
```

Every such P,c and every linear ell give an isomorphism. In particular,
set ell=0 to construct a transporter. Thus the complete invariant is the
similarity class of the nondegenerate symmetric form, not its congruence
class with a fixed socle generator.

## 3. Elementary classification and constructive reduction

We include the classical form argument to specify the maps exactly.
Every nondegenerate symmetric form over odd K has an orthogonal basis.
If every diagonal entry in a nonzero residual block is zero, a nonzero
off-diagonal entry yields a vector e_i+e_j of norm 2B_ij != 0.
Split off that vector and continue on its nondegenerate orthogonal
complement. This terminates after r steps.

For any nonzero a,b in K, the sets

```text
{a*u^2 : u in K},  {1-b*v^2 : v in K}
```

both have size (q+1)/2, so intersect. Choose u,v with au^2+bv^2=1.
In diag(a,b), the vectors (u,v) and (-bv,au) have respective norms
1 and ab and are orthogonal. Their basis determinant is one. Apply this
two-coordinate reduction successively to obtain diag(1,...,1,d).
The square class of d equals that of the original determinant, since
congruence changes the determinant by a square. Scale the last vector
to make d either 1 or one fixed nonsquare nu. This proves both existence
and necessity of the two congruence classes, including r=1.

Scaling the entire form by c changes its determinant square class by c^r.
For even r it changes nothing. Therefore precisely two similarity classes
remain, represented by diag(1,...,1) and diag(1,...,1,nu).

For odd r, multiplying a nonsquare-determinant form by nu makes the
determinant square; a square-determinant form needs no scaling. Apply
the congruence reduction to get the identity. Hence all forms of that odd
dimension are similar. The exact number of algebra isomorphism classes is

```text
1 if r is odd;
2 if r is even, distinguished by the square class of det(B).
```

The distinction cannot be removed by changing lifts or the generator of
J^2 when r is even, by equation (1). For odd r, retaining the determinant
square class would falsely reject isomorphic algebras.

The implementation returns Q and h with Q^T B Q=hD, where D is the
canonical representative. The map from the canonical algebra to A_B sends
its V basis to the columns of Q and its socle generator to h*s. The
displayed equation verifies every product. Composing the two canonical
charts gives a map between the original tables; every basis product is an
independent checkable certificate. A negative answer uses the invariant,
without a search over candidate maps.

## 4. Recover the form from an arbitrary supplied table

Validate the algebra laws and recover the unique unit by linear equations.
For a finite-dimensional commutative local algebra, J is nilpotent and
J^n=0 for n=dim A. One way to see the exponent bound is that the radical
power chain strictly decreases until zero; equality persists and contradicts
nilpotence. These are classical finite-dimensional local-algebra facts.

Choose q^e>=n. The q^e-power map on A is K-linear and has kernel exactly J:
it kills J, while the residue of a unit remains nonzero. Compute this kernel
by linear algebra. Check codim J=1, dim J^2=1 and J*J^2=0. Choose s from
J^2, extend it to a basis of J, and express all lift products in that basis.
Reject if the resulting symmetric B is singular, which by section 1 is
equivalent to the socle being larger than J^2. This recognizes exactly the
declared class and constructs its chart. It does not recognize every local
algebra.

For recognition before locality is known, in any finite-dimensional
commutative unital K-algebra the same power kernel is the nilradical: every
nilpotent is killed by exponent n and no nonnilpotent has a zero power.
Codimension one makes the reduced quotient K, so the algebra is local.
This justifies using that check without a locality promise on the input.

The mathematical algorithm works over any explicit odd finite field.
Searching at most q^2 pairs for each binary reduction and at most q scalars
for a square root gives polynomial arithmetic complexity in n for fixed K.
No complexity polynomial in log q is claimed. The bounded implementation
uses only odd prime fields 3<=p<=31 and table dimensions 3<=n<=10; the
written proof has neither bound. The verifier exercises exact forms and
arbitrary-basis algebra tables within those executable limits.

## 5. Consequence for the recovered multiplication tensor

Ali Romman's PR #5540 reconstructs a general commutative unital algebra and
three explicit factor maps from a qualifying square prime-field tensor.
That theorem and its full source lineage are cited premises here. Applying
section 4 to its recovered table decides whether that table belongs to our
class. Applying sections 2 and 3 to two such tables decides their algebra
isomorphism and constructs the missing map when it exists.

For completeness, independent input/output tensor equivalence introduces
no further classes. Suppose invertible K-linear F,G,H satisfy

```text
F(x)G(y) = H(xy)
```

between two commutative unital algebras. Put a=F(1), b=G(1). Then
F(x)b=H(x) and aG(y)=H(y). Since all maps are bijective, multiplication
by a and by b is surjective, so a,b are units. Also H(1)=ab and
H(x)H(y)=ab H(xy). Consequently phi(x)=(ab)^(-1)H(x) is a unital algebra
isomorphism. Conversely any algebra isomorphism gives a tensor equivalence.
This elementary unital-isotopy argument proves that the signatures above
also classify the multiplication tensors. It does not perform or recheck
the predecessor's nucleus reconstruction.

## 6. Evidence and limits

The proof is the all-dimension claim; finite checks corroborate its
construction and class boundary. `verify.py` enumerates all symmetric forms
for (p,r)=(3,1..4),(5,1..3),(7,1..2). For each nonsingular form it verifies
the exact similarity certificate, with a permutation-sum determinant oracle.
An independent complete orbit generator enumerates GL2 at p=3,5,7 and GL3
at p=3, including every nonzero scalar. It compares the entire resulting
partition with the new signature. New changed-basis algebra tables check
the reconstruction and complete isomorphism maps on every basis product.

Negative controls include even characteristic, composite primes, malformed
coefficients/tables, noncommutativity, nonassociativity, absence of a unit,
wrong residue, zero radical square, nonzero radical cube and excess socle.
Transporter mutations change the image of the recovered unit, so are actual
mathematical corruptions rather than arbitrary changes that might give
another valid isomorphism. All acceptance checks survive optimized Python.

This result supplies an algebraic interface only. It leaves physical
coefficient preparation, native realization, storage, movement, dirty-state
restoration, precision and a complete paid recursive caller unknown. It
does not improve kappa, change the selected frontier or prove the complete
multiplication theorem. Independent human and proof-kernel review are
unclaimed. No historical scientific replay is used as the deliverable.

## Credit

The new specialization and implementation were produced by Nick Petalas.
Credit Ali Romman #5540 for the explicit isomorphism handoff and recovered
table interface, apoursh #5502, Ali Romman #5525, Nick Petalas #5252,
David Ganz and their retained tensor/algebra predecessors. Finite-field
symmetric-form reduction, radical theory and unital isotopy are classical.
No general mathematical or literature priority is asserted.
