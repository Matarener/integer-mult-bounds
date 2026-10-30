# Odd cyclotomic response gate

This scoped proof was produced by Nick Petalas. It extends Ross Richardson's
whole-bank cubic trace gate in [PR4081](https://github.com/CrocSwap/integer-mult-bounds/pull/4081).
The cyclotomic extension and the degree-four sharpness example are the new steps.
The predecessor's Pauli character argument is credited below. No historical
priority is claimed for the classical field-degree or Clifford facts.

## Statement

Let n>1 be odd. Let U be a unitary Clifford on M qubits, with every matrix
entry in Q(i), and suppose the **actual whole-bank matrix** satisfies

    Phi_n(U)=0.

Here Phi_n is the nth cyclotomic polynomial. Write S_U for the induced
symplectic matrix on the 2M binary Pauli coordinates. Then:

1. phi(n)=2^a for some integer 1<=a<=M. Equivalently, n is a squarefree
   product of distinct Fermat primes.
2. The characteristic polynomial is Phi_n(X)^(2^(M-a)), and
   Tr(U)=mu(n) 2^(M-a).
3. rank_F2(S_U-I)=2a, exactly. In particular, the native off-diagonal
   B-block rank is at most min(M,2a).

The condition on n is necessary. This proof does not assert Clifford
existence for every such n. A Fermat prime means a prime of the form
2^(2^j)+1, including any not presently known. The statement does not assume
that the currently known Fermat primes are the only ones.

At n=5, the bound B-rank<=4 is attained on four qubits, as constructed below.
Thus the degree-four cap cannot be reduced for all ambient widths.

## Cyclotomic degree and trace

For odd n, adjoining i and a primitive nth root gives Q(zeta_(4n)). Indeed,
the orders 4 and n are coprime, so the product of primitive roots of those
orders has order 4n, and its powers recover both factors. Classical
cyclotomic irreducibility therefore gives

    [Q(i,zeta_n):Q(i)] = phi(4n)/2 = phi(n).

For a proof of the classical irreducibility theorem, see Romyar Sharifi's
[Abstract Algebra, Theorem 6.6.11](https://math.ucla.edu/~sharifi/notes/algebra-ch06.html).
Consequently Phi_n remains irreducible over Q(i). Its roots are distinct.
Since Phi_n(U)=0, the Q(i)[X]-module defined by U is a direct sum of copies
of Q(i)[X]/(Phi_n). Equivalently, its characteristic polynomial is Phi_n^t
for a positive integer t, and

    2^M = t phi(n).

Thus phi(n) is a power of two, say 2^a, with a<=M. If
n=product_p p^e_p, then phi(n)=product_p p^(e_p-1)(p-1). Every p is odd.
No e_p can exceed one, and every p-1 must be a power of two. If p=1+2^b
is prime, b is itself a power of two: an odd divisor c>1 of b would factor
(2^(b/c))^c+1. Conversely, a squarefree product of Fermat primes has
power-of-two totient. This proves the stated equivalence.

Each primitive nth root occurs t times. The sum of the primitive nth roots
is mu(n). One elementary derivation partitions all nth roots by their
exact orders and applies Mobius inversion to their sum. Hence

    Tr(U)=t mu(n)=mu(n) 2^(M-a).

Squarefreeness makes mu(n) equal to plus or minus one. In particular the
trace is nonzero, and its squared absolute value is 2^(2M-2a).

## Pauli adjoint trace

This is the Pauli-character step used in the predecessor's cubic proof.
For completeness, let P_v be Hermitian Pauli representatives, indexed by
v in F2^(2M). Clifford conjugation sends P_v to epsilon(v) P_(S_U v),
where epsilon(v) is plus or minus one. On K=ker(S_U-I), comparing the
conjugation of P_v P_w with the product of the conjugations cancels the
same Pauli multiplication phase. It gives

    epsilon(v+w)=epsilon(v)epsilon(w),  v,w in K.

Thus epsilon restricted to K is a character. Its sum over K is zero if
the character is nontrivial, and 2^dim(K) otherwise. This sum is the trace
of conjugation by U in the Pauli basis. The same linear map on matrices
has trace Tr(U) conjugate(Tr(U)), by its tensor representation U tensor
conjugate(U). The trace computed above is nonzero. Therefore

    2^dim(K) = 2^(2M-2a),
    rank(S_U-I) = 2M-dim(K) = 2a.

In the physical X/Z coordinates, the off-diagonal B block of S_U is also
a submatrix of S_U-I. Its rank is at most 2a, and its size is M by M.
This proves the native-rank cap without any tensor or support restriction.

## A sharp degree-four example

Define H_g=(1+i)[[1,1],[1,-1]]/2, S=diag(1,i), and let C be CNOT with
the first qubit controlling the second. The Gaussian-dyadic Clifford

    U5 = - C (S tensor I) (H_g tensor H_g)

has matrix

    1/2 * [ -i  -i  -i  -i ]
          [ -i   i  -i   i ]
          [  1  -1  -1   1 ]
          [  1   1  -1  -1 ].

Direct matrix multiplication gives U5^5=I and
I+U5+U5^2+U5^3+U5^4=0. Its trace is -1, and its symplectic defect has
rank four. These are complete 4-by-4 identities, checked with integer
Gaussian numerators in verify.py.

Add two identity spectators. On the four qubits numbered 0,1,2,3, let V
be Bell preparation on pairs (0,2) and (1,3). Apply H_g on 0 and 1, then
CNOT 0->2 and 1->3. Set

    W = V^-1 (U5 tensor I_4) V.

Conjugation preserves Phi5(W)=0. Its B block is nonsingular. To see this
without relying on a computed rank, write A for the four-dimensional
symplectic coordinate space of the first two qubits, and E for that of
the spectators. Bell preparation sends the standard Z Lagrangian L to
a graph L' of a symplectic isomorphism A->E. In characteristic two this
graph is Lagrangian, has dimension four, and intersects A trivially.
The active symplectic map T of U5 has T-I invertible. For l in L',

    ((T direct_sum I)-I)l = ((T-I) projection_A(l), 0).

If (T direct_sum I)l also lies in L', the displayed difference lies in
A intersect L', hence is zero. Invertibility of T-I and of
projection_A restricted to L' forces l=0. Thus L' and its image are
transverse. Pulling back by V, L and S_W L are transverse. The map from
input Z coordinates to output X coordinates is therefore invertible,
which is exactly B-rank four. The standalone verifier also checks this
complete 16-by-16 matrix, all eight Pauli generators and every fixed
Pauli sign.

## Meaning for a proposed response interface

The n=3 case is Richardson's result. New examples of the necessary bound
are n=5 with defect four, n=15 with defect six, and n=17 with defect eight.
Orders 7,9,25 and 27 cannot satisfy their primitive cyclotomic relation
on any Gaussian-rational qubit bank, even before Cliffordness is imposed.
Those are exclusions of the primitive relation, not exclusions of those
finite orders among Clifford operators.

For fixed odd n, no family with unbounded native B rank can retain
Phi_n(U)=0 on the whole bank. In terms of a rank r, any such primitive
response needs phi(n)>=2^(r/2). This is an obstruction to a fixed-degree
primitive response identity, not a complete query-price
or caller impossibility theorem.

Order alone is insufficient: U5 tensor U5 still has order five but
does not satisfy Phi5=0, and its symplectic defect rank is eight.
Arbitrary global phases also do not preserve the premise. Non-Gaussian
coefficient fields, non-Clifford operators, restricted-input quotients,
responses with several cyclotomic factors, and complete changed callers
are outside this theorem. No physical implementation invoice, dirty
restoration, supplier admission, new kappa or complete multiplication
theorem follows. The universal proof is written mathematics, not a
finite extrapolation or a formal-kernel result.
