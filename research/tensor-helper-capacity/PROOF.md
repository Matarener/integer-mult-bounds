# Sharp tensor composition of dyadic helper capacity

Let D = Z[1/2]. For a finite m-by-n matrix K over D, define

    c(K) = max {s : there exist X,Y over D with X K Y = I_s}.

The empty identity is allowed, so c(K) can be zero. Write r(K) for
rational rank, and rho_p(K) for rank after reduction modulo an odd prime p.
The reduction is defined because every denominator is a power of two.

Ali Romman's [#5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
establishes the single-cut criterion

    c(K) = min_{p odd prime} rho_p(K).

Its Smith-form argument constructs a unit block of that size. This result
is a cited premise. The present contribution concerns how these capacities
compose and how much information individual capacities discard.

## The tensor composition theorem

For any finite nonempty list K_1,...,K_t of dyadic matrices,

    c(K_1 tensor ... tensor K_t) = min_{p odd prime} product_i rho_p(K_i).  (1)

Put c_i = c(K_i) and r_i = r(K_i). Then

    product_i c_i <= c(tensor_i K_i)
                 <= min_i (c_i product_{j != i} r_j).                    (2)

Both bounds are sharp for every prescribed positive integer rank tuple
r_i and capacity tuple 1 <= c_i <= r_i. Rectangular zero padding preserves
the constructions. If some c_i is zero, the tensor capacity is zero.

When every c_i is positive, equality at the lower bound holds exactly when
there is one odd prime p such that rho_p(K_i) = c_i for every i.
In particular c(K tensor ... tensor K) = c(K)^t for repeated equal factors.

### Proof

Over a field, row and column changes put each K_i into a rectangular
identity block with zeros elsewhere. Tensoring the changes shows that
the rank of the tensor is the product of the ranks. Apply this fact
modulo each odd prime, then apply the cited single-cut criterion to the
tensor matrix. This proves (1).

Every rho_p(K_i) is at least c_i, which proves the lower bound in (2).
For a fixed i, choose an odd prime attaining c_i. Such a prime exists:
the ranks are integers in the finite set {0,...,r_i}, so the minimum in
the cited criterion is attained. At that prime all other ranks are at
most their rational ranks. Taking the minimum over i proves the upper
bound. If c_i = 0, that prime forces tensor rank zero.

For positive capacities, equality of a product of integers rho_p(K_i)
with product_i c_i requires equality in every positive factor. The
minimum in (1) is attained for the same finite-integer reason. This
proves both directions of the common-prime equality criterion. Applying
(1) to equal factors gives the repeated-factor identity, including zero.

To attain the lower bound for prescribed r_i,c_i, fix one odd prime p
and take

    K_i = diag(I_{c_i}, p I_{r_i-c_i}).

Its rational rank is r_i, its rank modulo p is c_i and its rank at every
other odd prime is r_i. Formula (1) gives product_i c_i.

To attain the upper bound, choose distinct odd primes p_i and take

    K_i = diag(I_{c_i}, p_i I_{r_i-c_i}).

At prime p_i the tensor rank is c_i product_{j != i} r_j. Outside this
finite set it is product_i r_i. The latter is no smaller than any of
the displayed exceptional values. Formula (1) therefore gives the
upper bound exactly. Smith reduction of the resulting diagonal matrix
constructs X,Y attaining its unit block; existence is not inferred
from a favorable rational rank alone. This completes the proof.

## Explicit smallest strict composition

Take A = diag(1,3) and B = diag(1,5). Each has capacity one. In the
usual tensor order K = A tensor B = diag(1,5,3,15). The matrices

    X = [[1, 0, 0, 0],     Y = [[1, 0],
         [0,-1, 2, 0]]         [0, 1],
                               [0, 1],
                               [0, 0]]

satisfy X K Y = I_2 by -5 + 2*3 = 1. Modulo either 3 or 5 the tensor
has rank two, so a third unit channel is impossible. Thus c(A tensor B)
= 2 > c(A)c(B) = 1. This is a new composition example, distinct from
#5615's direct-sum example diag(3,5).

For every n >= 2 and t >= 2, take t distinct primes and K_i =
diag(1,p_i,...,p_i) of size n. Each individual capacity is one; the
tensor capacity is exactly n^(t-1), the largest possible value with
these rational ranks and individual capacities. This is an arbitrarily
large failure of the product of individual capacities as an upper bound.
The primes are fixed coefficients, not unpaid prime-provider operations.

## Constructive finite corroboration

The verifier uses two independent calculations on new matrices. Exact
determinantal ideals compute capacity: the gcd of numerators of all
k-by-k minors is a power of two exactly when that ideal is the unit
ideal over D. Field elimination computes the prime profiles. For the
two complete 2-by-2 entry alphabets {0,1,3} and {0,1,5}, the only possible
odd divisors of a nonzero maximal minor are 3 and 5. Rational rank
represents every other odd prime. No untested bad prime is omitted.

For the diagonal extremizers, only 3,5,7 can be exceptional; rank modulo
11 is the generic rank. A separate two-pivot Euclidean procedure returns
literal X,Y and checks every entry of X K Y = I_c. If a,b are two
diagonal entries and sa+tb=g=gcd(a,b), its integral transformations are

    U = [[s,t],[-b/g,a/g]],
    V = [[1,-tb/g],[1,sa/g]],
    U diag(a,b) V = diag(g,ab/g),  det U = det V = 1.

The zero-zero case is skipped. Both side transformations are retained,
so the returned unit block is an executable witness. This elementary
Smith operation is classical. It is used here to corroborate the new
composition extremizers, without executing the predecessor's checker.

## Scope and physical boundary

This is a scoped algebraic proof for dyadic pairing matrices. It does not
show that independently supplied physical cuts have a tensor-product
eligible module, simultaneous timing, a common chart or the carriers
required by that product. It does not bound scalar coefficient growth,
basis-operation tariffs, native maps, dirty restoration, storage or
compiler/outer costs. Those quantities are unknown here, not zero.
No extra productive targets or new kappa follow from this theorem alone.

Credit Ali Romman #5615 for the exact single-cut capacity theorem,
#5602/#5609/#5611 for the causal pairing and completion interfaces, and
the retained #5599 helper/controller/native lineage. Classical Smith
normal form, Bezout identities and field rank retain their classical
status. The sharp tensor envelope, equality criterion and composition
examples in this application were produced by Nick Petalas.
