# Sharp rank cost of noncentral cyclic reversal

This contribution is produced by Nick Petalas. Apache-2.0.

## Contract and statement

Let K be any field, p >= 2, q >= 1 and w >= 0. Let C_p be the permutation
matrix sending e_i to e_(i+1 mod p). On K^(pq+w), put

    U = C_p direct-sum ... direct-sum C_p direct-sum I_w,
                q copies
    g = gcd(p,2),    D = q(p-g),    N = D/2.

The w workspace coordinates have arbitrary initial values. A boundary map
J is any invertible K-linear map on this complete space. It may couple
different cycles and workspace coordinates. Its rank charge is rank(J-I).
Define the complete reversal defect by

    E(U,J) = J^-1 U J - U^-1.

All ranks include workspace rows and columns. Exact reversal means E=0,
so the complete conjugated program acts as the inverse on every cycle and
as the identity on every workspace coordinate, with no input promise.

**Theorem.** For every integer r >= 0,

    min { rank E(U,J) : J invertible, rank(J-I) <= r }
        = max(0, D-2r).                                      (1)

In particular, the exact minimum boundary rank for reversal is N,
independently of w. One attaining boundary is the permutation reflection
i -> -i modulo p on each cycle, extended by identity on workspace.
The theorem includes characteristic two and characteristics dividing p.

The defect rank is an exact algebraic error measure. It is not an
entrywise error, a norm error or a recursive power tariff.

## Lower bound, including arbitrary workspace mixing

The kernel of C_p-C_p^-1 is the kernel of C_p^2-I, after multiplication
by an invertible matrix. The latter consists of vectors constant on each
orbit of adding two modulo p. There are g such orbits. This argument uses
only equality of coordinates, so it works in every characteristic.
Consequently rank(U-U^-1)=D, including the identity workspace block.

Set A=J-I. Multiplication by invertible J preserves rank, and

    J E(U,J) = UJ-JU^-1
             = (U-U^-1) + UA-AU^-1.

Rank subadditivity and the reverse triangle inequality give

    rank E(U,J) >= D-rank(UA-AU^-1)
                >= D-2 rank A >= D-2r.

Nonnegativity supplies the other lower bound. No block structure, field
extension, diagonalization or restriction on J was used. In particular,
an arbitrarily large finite identity-stage workspace cannot lower it.

## Attainment by partial reflections

First take q=1 and w=0. Put n=(p-g)/2. For 0 <= s <= n, let J_s be the
product of the disjoint transpositions

    (1,p-1), (2,p-2), ..., (s,p-s).

Thus J_s is involutory and rank(J_s-I)=s over every field. Each swapped
pair contributes a nonzero rank-one block, even in characteristic two.

The permutation J_s C_p consists of the s transpositions

    (0,p-1), (1,p-2), ..., (s-1,p-s)

and one cycle on s,s+1,...,p-s-1, of length L=p-2s. A cycle of length one
is allowed. Squaring fixes every transposition coordinate, and its action
on the remaining cycle has gcd(L,2)=g cycles. Therefore

    rank((J_s C_p)^2-I) = L-g = p-g-2s.

The identity

    C_p J_s-J_s C_p^-1
        = J_s ((J_s C_p)^2-I) C_p^-1

shows that this is exactly the reversal defect rank. This proves (1)
for one cycle up to budget n; the full reflection gives zero for larger
budgets.

For q cycles, set r'=min(r,qn) and choose integers s_i in [0,n] summing
to r'. Fill one cycle up to n, then the next, until r' is exhausted.
Take the direct sum of their J_(s_i), together with I_w. Its boundary rank
is r' and its defect rank is

    sum_i (p-g-2s_i) = D-2r' = max(0,D-2r).

This proves attainment for every parameter and completes the theorem.

## A two-sided boundary consequence

Even if the input and output boundaries are different, any invertible
L,R with L U R=U^-1 must satisfy

    rank(L-I)+rank(R-I) >= D.                                (2)

Indeed U^-1-U=(L-I)UR+U(R-I), and both U and R are invertible.
The two full reflections attain equality in (2). This is the total
ordinary boundary-rank allowance, which is positive for p>2. It does not
determine a concave price, physical realization or complete cost.

## Relevance and limits

Ali Romman's [PR6168](https://github.com/CrocSwap/integer-mult-bounds/pull/6168)
leaves noncommuting native address maps outside its forward cyclic tariff.
The new result quantifies one such changed boundary, on the regular cyclic
coordinate representation, including arbitrary finite dirty workspace.
It neither invokes nor replays the predecessor tariff. Its rank inequality
and elementary permutation facts are standard; the scoped sharp tradeoff
and its application are the contribution here. No literature-priority
claim is made.

Adam Gall / [PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941)
already gives concrete cyclic-reflection permutations and swap counts for
even cycles. This result adds optimality over all invertible boundaries,
the residual-rank tradeoff and arbitrary-field workspace stability.


For example p=7,q=1 has exact reversal boundary rank 3. Budgets 0,1,2,3
leave minimum defect ranks 6,4,2,0. All are attained by the displayed
partial reflections. The checker computes these cases directly.

A regular permutation representation is essential to the stated formula.
An action whose order merely divides p can have a smaller rank difference.
The result does not identify this matrix rank with a Clifford symplectic
rank, a Gaussian/BIT child rank or an ordinary execution cost. A native
realization, phases, productive credits, caller, precision, movement and
compiler bill remain separate obligations. There is no supplier admission,
new kappa or change to the selected frontier or its five assumptions.

The universal statement follows from the written proof. Finite checking
corroborates it and checks the implementation. Independent human and
formal proof-kernel review are unclaimed.
