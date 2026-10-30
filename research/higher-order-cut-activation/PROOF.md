# Arbitrarily high activation arity at a parallel helper cut

Produced by Nick Petalas. Apache-2.0.

## Contract and credited premise

Let D = Z[1/2]. For a reversible scalar prefix A and suffix B = A^-1,
fix the coordinate support G of helper inputs/outputs and eligible cut
support F. The eligible rows are all v supported in F with vA supported
in G. The eligible columns are all u supported in F with Bu supported
in G. Choose full D-module bases L0 and R0 and write K = L0 R0.

A t-channel normalized algebraic interface is X K Y = I_t over D.
Ali Romman's PR5615 proves that its maximum t is

    c(K) = min over odd primes p of rank over F_p of (K mod p).

We cite that single-cut theorem, including its requirement for full module
bases. It is not a result reverified by this contribution. Smith normal
form and Bezout identities are classical. The new claims below concern
activation arity under parallel composition and a causal scalar realization.
No native frame, Gaussian response, independent productive target or free
basis conversion is part of this scalar contract.

## Theorem 1: activation arity is unbounded

For every integer q >= 2, there are q independent reversible scalar banks
such that every proper nonempty subpool has capacity zero and their full
parallel pool has capacity exactly one. All inputs, including excluded
coordinates, are arbitrary, and the complete scalar word restores them.
For q = 2 the algebraic phenomenon is already illustrated by PR5615's
diag(3,5) example. The arbitrary q statement and scalar banks are the
present contribution.

Choose distinct odd primes p_1,...,p_q. Put P = product_i p_i and

    d_i = P/p_i,       K = diag(d_1,...,d_q).

If J is a proper nonempty index subset, choose j outside J. Every d_i for
i in J is divisible by p_j. Reducing K_J modulo p_j gives the zero matrix,
so c(K_J) = 0. This obstruction applies to arbitrary dyadic row/column
combinations within that subpool, not just to its individual entries.

For the full pool, gcd(d_1,...,d_q) = 1: every prime divisor of P is absent
from one of the d_i, and there are no other prime divisors. Bezout therefore
provides integers b_i with sum_i b_i d_i = 1. Taking X = (b_1,...,b_q) and
Y = (1,...,1)^T gives X K Y = 1. Hence c(K) >= 1.

For any j, the reduction of the full K modulo p_j has exactly one nonzero
diagonal entry, d_j. Its rank is one, so c(K) <= 1. This proves the exact
capacity and every proper-subpool exclusion. Section 3 realizes each d_i
as the full pairing of an actual reversible scalar bank, completing the
causal assertion.

Consequently, for every fixed h >= 1, testing only subpools with at most h
banks cannot justify excluding all joint channels: choose q = h+1. This
is a statement about the declared algebraic parallel-cut model. It does
not invalidate a census with a stronger source-specific theorem limiting
which banks can share a physical chart or time.

## 3. Reversible scalar bank with full pairing [d]

For any positive integer d, take three arbitrary scalar coordinates
(x_0,x_1,z). The prefix consists of ordinary unit-coefficient ADDs:

    x_0 += z
    x_1 += z
    z   += x_0
    repeat d-1 times: z += x_1

It has d+2 ADDs and column-convention matrix

    A_d = [[1, 0, 1],
           [0, 1, 1],
           [1, d-1, d+1]].

The suffix reverses the prefix order and negates each ADD, so it has the
same cost and restores all three arbitrary input values. In particular,

    B_d = A_d^-1 = [[2, d-1, -1],
                    [1, d,   -1],
                    [-1, 1-d, 1]].

At the cut and boundary take F = G = span_D(e_0,e_1), excluding z.
A row (a,b,0) is eligible exactly when its excluded prefix coordinate
vanishes, a+b=0. Thus its full module basis is l = (1,-1,0).
A column (a,b,0)^T is eligible exactly when -a+(1-d)b=0. Its full module
basis is r = (d-1,-1,0)^T. These descriptions parameterize every solution
over D directly; there is no independently rescaled rational nullspace.
The pairing l r equals d. Both generators are primitive. In fact lA_d=l
and B_d r=r, so the displayed boundary supports hold exactly.

Parallel banks are disjoint coordinate blocks. Their eligibility equations
separate by block, even when candidate vectors use arbitrary combinations
across banks. The full eligible modules are therefore the direct sums of
the displayed modules, and their pairing is exactly diag(d_i). Every bank
prefix precedes one common scalar cut and every inverse suffix follows it.
The total scalar ADD cost is 2 sum_i(d_i+2), on 3q arbitrary coordinates.

This is a complete ordinary scalar invoice for the calibration word. It
is not the native or recursive invoice of a productive helper supplier.
The word itself is identity and earns no productive credit by that fact.

## 4. Concrete three-bank certificate

Take (d_1,d_2,d_3) = (15,21,35). Their pairwise gcds are 3,5,7 respectively,
so all three pairs have capacity zero; each singleton also has capacity
zero. The full pool has the unit certificate

    (1,1,-1) diag(15,21,35) (1,1,1)^T = 1.

Modulo 3,5 or 7 its rank is one, proving optimality. Its integer Smith
factors are 1,105,105: the gcd of entries is 1, the gcd of nonzero 2-minors
is 105 and the determinant is 11025.

The nine-coordinate causal realization costs

    2((15+2)+(21+2)+(35+2)) = 154 signed ADDs.

The pooled eligible row is (l,l,-l) and column is (r_15,r_21,r_35)^T.
Their pairing is one. The suffix restores all nine arbitrary coordinates;
no zero-initialized workspace, source consumption, erasure or discarded
history is used. Preparing a physical common helper frame and executing
these cross-bank combinations still requires its own charged construction.

## Verification boundary

The dimension-uniform assertions are the written proof above. The finite
checker corroborates 57 prime families from subsets of {3,5,7,11,13,17},
all 602 proper nonempty subpools, 57 Bezout witnesses, 25 literal scalar
banks at odd d between 1 and 49, and the complete nine-coordinate word.
It computes determinantal divisors without the predecessor Smith program,
checks exact prefix/inverse matrices, full dirty basis columns, support
identities, primitive generators and explicit invalid controls. It imports
no predecessor executable and performs no predecessor scientific replay.
