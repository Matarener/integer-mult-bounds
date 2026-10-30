# The sharp boundary loss of the prefix encoder

This scoped proof was produced by Nick Petalas. Apache-2.0.

Let G be any finite group, with identity e and order q. The physical column
alphabet and virtual state space are both G. All vector spaces in this proof
are complex Hilbert spaces with their coordinate inner products. Define

    T[y,x]_(a,b) = 1 if y = a x and b = y, and 0 otherwise,
    F = e_e*,       B = sum_(b in G) e_b.

For every positive width f the physical endpoint is

    E_f[Y,X] = F T[y_1,x_1] ... T[y_f,x_f] B.

This uses the fixed physical-table convention of zxv's [PR5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441).
For G=C2 it is the standard prefix-XOR encoder in that package. We use the
table definition, not any claimed physical implementation or paid cost.

## Claim and certificate being optimized

The endpoint E_f is a permutation matrix, so ||E_f||_op=1 at every positive f.
For the following specific sufficient certificate, however, the least uniform
squared bound is exactly q. This remains true after grouping any fixed positive
number k of columns and after any fixed invertible change of virtual basis.

The certificate is Ali Romman's [PR5451](https://github.com/CrocSwap/integer-mult-bounds/pull/5451)
metric criterion. Write L_k for the full local operator whose block from physical
input X to output Y is T[y_1,x_1] ... T[y_k,x_k]. It asks for a positive definite
Hermitian P and nonnegative scalars A,H,c, with c<=1, satisfying

    F*F <= A P,     B* P B <= H,
    L_k* (P tensor I_(q^k)) L_k <= c (P tensor I_(q^k)).

The tensor factors here are ordered virtual then physical. Permuting both
sides gives exactly the source's physical-then-virtual block convention.
The resulting bound at f=k m is A H c^m. Its uniform positive-m bound is
A H c. The theorem below optimizes precisely these inequalities. It neither
asserts that all uniform bounds have this form nor alleges an error in the
source's sufficient theorem.

## 1. The endpoint and local operator are unitary

For an initial state a and input X=(x_1,...,x_k), the only surviving path is

    y_j = a x_1 ... x_j,      b = y_k.

With a=e and the final state summed by B, E_f is the prefix-product map.
Its inverse is x_1=y_1 and x_j=y_(j-1)^(-1) y_j for j>=2. Thus it is a
permutation on G^f, including for noncommutative G.

The direction of the virtual indices matters. As an operator L_k, the input
virtual state is the terminal b, and the output virtual state is a.
For each input (b,X), set a=b (x_1 ... x_k)^(-1), then form the unique Y above.
This defines one output (a,Y). Conversely, (a,Y) determines X by successive
group differences and determines b=y_k. Therefore L_k is itself a permutation
matrix on q^(k+1) coordinates. In particular it is unitary.

## 2. A contractive positive metric is scalar

Put W=P tensor I_(q^k). Its trace is positive. Since L_k is unitary,

    Tr(L_k* W L_k) = Tr(W).

The contraction inequality and c<=1 imply Tr(W)<=c Tr(W), hence c=1.
The positive semidefinite difference W-L_k* W L_k has trace zero, so it is zero.
Equivalently, L_k preserves the full metric W exactly.

Consider two input coordinates (b,X) and (b',X) with the same physical X
and distinct b,b'. Their output physical words Y,Y' are distinct because their
last letters are b,b'. Consequently

    (L_k* W L_k)_((b,X),(b',X)) = 0,
    W_((b,X),(b',X)) = P_(b,b').

Metric invariance forces every off-diagonal entry of P to vanish, including
its imaginary part. On a diagonal coordinate (b,X), invariance then says

    P_(b,b) = P_(a,a),    a=b (x_1 ... x_k)^(-1).

At every k>=1 the product x_1 ... x_k ranges over all G. Thus all diagonal
entries agree. Positive definiteness gives P=t I_q with t>0. Conversely every
such metric is preserved by the permutation L_k. This characterizes all
feasible positive metrics, rather than searching a finite subset of them.

## 3. The exact optimum is q

For P=t I_q, the left inequality forces A>=1/t by evaluating it on e_e.
The right inequality forces H>=q t because B has q unit entries. Thus

    A H c >= (1/t) (q t) = q.

Equality is attained at P=t I_q, A=1/t, H=q t, c=1. Hence the least certified
squared bound is q, although the actual squared operator norm is one.
The multiplicative loss in operator norm is exactly sqrt(q). It persists at
every fixed blocking length. For a residual epsilon E_f with epsilon nonzero,
the same argument gives the least squared bound q |epsilon|^2.

## 4. A virtual basis change cannot remove the loss

Let S be any invertible complex q-by-q matrix, and set

    T'[y,x]=S^(-1) T[y,x] S,    F'=F S,    B'=S^(-1) B.

Products telescope at every block length. A certificate for the primed table
with metric P' is exactly a certificate for the original table with
P=S^(-*) P' S^(-1), with the same A,H,c. Congruence by an invertible matrix
preserves positive definiteness and semidefinite order in both directions.
All feasible primed metrics are therefore P'=t S* S, and the optimum is q.
This permits arbitrary conditioning of S. It is an algebraic statement, not
a claim that a basis change has zero physical or precision cost.

## Consequence and scope

For a desired norm tolerance tau, an error epsilon E_f can satisfy the actual
bound |epsilon|<=tau while this certificate demands sqrt(q)|epsilon|<=tau.
Searching more positive metrics, or blocking more columns within this same
representation and criterion, cannot close that gap. A useful next method
must retain boundary correlation, use a different representation, or change
the certificate. Those possibilities are not excluded by this proof.

The example is a complete algebraic physical endpoint, not a materialized
native/tape implementation. It supplies no paid supplier, dirty-workspace
program, compiler closure, recovery budget, new kappa or multiplication
theorem. No claim is made about arbitrary transfer tables, augmented virtual
spaces, width-dependent metrics, or position-dependent metric sequences.

The trace and congruence arguments and weighted operator norms are classical.
The additional result is this exact optimum, its positive-metric rigidity,
and its permanence under blocking and virtual gauges for the named encoder.
Finite checks in verify.py corroborate the proof and do not replace its
universal quantifiers or constitute formal proof-kernel acceptance.
