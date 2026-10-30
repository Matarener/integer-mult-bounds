# A sharp copy tariff for the fixed group-fit row space

The following is a scoped algebraic theorem, over every coefficient field.
Its cost is the declared full-plane one-total tariff. It is not a lower bound
for arbitrary fitting matrices, arbitrary decoders or integer multiplication.

## Objects and tariff

Let the 112 selected binary labels be `l_p` in `F2^9`, with pairing
`<x,y> = sum x_i y_i` in `F2`. Partition the ports into nonempty even groups
`G_1,...,G_t`, each with Gram matrix `I_|G_g|`. Pair consecutive ports within
each group. These are the complete two-port planes used by the contract.

For each group, let `S_(g,0)` and `S_(g,1)` contain its even-position and
odd-position ports. Write `v_(g,s)` for their indicator vectors, regarded over
an arbitrary coefficient field `F`, and define the literal fitting matrix

    K = sum_(g,s) v_(g,s) v_(g,s)^T.

The supports are disjoint and nonempty. Their indicators are independent over
every field. Thus the row space `R` of K has dimension `2t` and basis
`v_(g,s)^T`. The same statement holds in characteristic two, even if K squared
vanishes on some blocks. No invertibility of the support cardinalities is used.

A scalar query `q` has full-plane closure `P(q)`: every port in every plane
containing a nonzero source coefficient of q. Its declared tariff is

    tau(q) = rank_F2 [<l_p,l_r>]_(p,r in P(q)),

with `tau(0)=0`. The rank is binary even when query coefficients lie in another
field. This is the full-plane one-total boundary inherited from the plane-port
work and used in PR3345 and PR3370. Coefficient implementation, source access,
frames, restoration, hosting, precision and the consumer require additional
analysis. The tariff alone does not supply a native algorithm or admission.

## Weighted spanning lemma

Let `v_1,...,v_m` be a basis of a vector space over any field, and attach
nonnegative weights `w_1,...,w_m`. Suppose a nonnegative query cost obeys

    cost(sum_j c_j v_j) >= w_j whenever c_j != 0.

Then every finite spanning query list within this vector space has total cost
at least `sum_j w_j`.

Proof. Select m independent queries from the list. Their m by m coefficient
matrix C in the named basis is nonsingular. The determinant expansion has a
nonzero term, so there is a permutation pi with `C_(i,pi(i)) != 0` for every i.
The selected queries therefore have total cost at least
`sum_i w_pi(i) = sum_j w_j`. Unselected queries have nonnegative costs. This
proves the assertion over finite and infinite fields in every characteristic.

## Application and sharpness

Give both basis vectors of group g weight `|G_g|`. A query in R has a unique
expression in the disjoint-support basis. If its coefficient of `v_(g,s)` is
nonzero, it is nonzero at every port of `S_(g,s)`; other basis vectors cannot
cancel any of these entries. This support meets every plane of group g.
Consequently its full-plane closure contains G_g. The corresponding principal
binary Gram submatrix is `I_|G_g|`, proving `tau(q) >= |G_g|`.

The weighted spanning lemma now gives

    sum_i tau(q_i) >= sum_(g,s) |G_g| = 2 * 112 = 224

for every finite spanning query list in R. The literal indicator basis attains
equality: the closure of each indicator is precisely its group, with tariff
`|G_g|`. Hence the exact minimum is **224**.

This conclusion holds for every even orthonormal partition of these 112 ports,
regardless of its number of groups. It is a conditional statement about each
such partition; no new partition is constructed or ruled out here.

In particular, suppose `K = U Q` is an exact scalar factorization with exactly
`rank(K)=2t` queries, meaning Q has `2t` rows. Then
`rowspace(K) subset rowspace(Q)` and both spaces have dimension `2t`, so they
are equal. Every rank-minimal factorization of this SAME K therefore costs at
least 224 under the tariff. Arbitrary dense changes of basis cannot improve it.
The result also covers redundant queries constrained to R.

## Source-bound instance and checks

PR3370's retained partition has eleven groups of size eight, two of size six
and three of size four. Its literal K has rank 32, and the attaining invoice is

    22 * 8 + 4 * 6 + 6 * 4 = 224.

The primary replay authenticates the selected labels and the retained certificate,
checks every group identity and all 11,392 forced scalar-mask entries, and
enumerates all `2^16-1 = 65,535` nonempty group closures. This covers every
possible closure of a nonzero query in R, over any field. Every closure contains
an identity of the required weight. The binary rank histogram is in RESULT.json.

To compute a closure rank, the primary checker replaces its labels by an
independent binary basis B. If L is the matrix of original labels, write
`L = A B`, where A has full column rank. Then
`rank(L L^T) = rank(A B B^T A^T) = rank(B B^T)`: multiplication by A is injective
and multiplication by A transposed is surjective. This justifies the small
Gram calculation without assuming that the restricted form is nondegenerate.

The dense recoding `C=I+J_32` has inverse `I-J_32/33` whenever 33 is invertible.
Replays over F2, F5 and F1000003 check all 37,632 factorization entries in total.
All 32 queries then touch all groups and cost nine each, for total 288. The
same factorization and cost hold over Q. The unrecoded basis costs 224. Adding
one all-support query to that basis costs 233. These are exact controls, not
performance measurements or a sampled substitute for the spanning proof.

The separate checker uses explicit nine-coordinate vectors and dense Gaussian
elimination, with no import from the primary checker. It verifies 137 geometric
sets and all 264,864 two-query invertible recodings: 496 support pairs times
`|GL2(F2)|+|GL2(F3)|+|GL2(F5)| = 6+48+480`. None costs less than 224. This finite
census checks the claimed tariff calculation and recoding behavior; the proof
above supplies the all-field and arbitrary-recoding conclusion.

## Limits and next boundary

A different fitting matrix for the same matching can have a different row space.
An overcomplete query list spanning a larger space can contain queries outside R.
Neither case is covered. Nonlinear production, a changed reader contract, shared
native operations and a completed consumer are also outside this additive tariff.
No minimum across arbitrary P112 matching decoders or improved kappa follows.

The useful restriction on the next attempt is precise: to beat 224 under this
tariff, change the fitting row space or use queries outside it, or change the
charged boundary. Merely recoding the fixed literal rank 32 matrix cannot do it.
