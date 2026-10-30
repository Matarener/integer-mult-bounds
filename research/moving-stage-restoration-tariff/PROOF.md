# Exact restoration tariff for positive moving stages

This scoped proof is produced by Nick Petalas. Apache-2.0.

## Contract

Take finitely many coordinate blocks indexed by `0,1,...,m-1`, each of
the same positive width `w`. Block 0 is the anchor. Let `D_j` be the
normalized Gaussian on block j. The `D_j` commute, and `D_j^2` is a
block-local monomial. Let `P_s` exchange blocks 0 and s, with `P_0=I`.
The only charged stages are the positive operators

    E_s = P_s D_0,    s=0,...,m-1.

This is Cinna Davis's #5113 moving-coordinate interface, with the terminal
anchor stage used by Chris R / Clear1nsight's #5133. These premises are
cited, not independently audited here. Their native and coded-owner
semantics remain their premises.

Write an endpoint in the exact normal form

    P_pi product_j D_j^(a_j),    a_j >= 0.

The requested boundary requires `pi=identity`. It requests odd Gaussian
exponent on precisely a set S of nonanchor blocks and anchor parity b
in `{0,1}`. All other blocks must have even exponent. The whole-block
permutation must restore inside the charged word. The even powers are
explicit residual block-local monomials. They are not removed for free.
This is a Gaussian-support quotient with internal block-permutation
restoration, not exact identity restoration of every address and phase.

## Theorem

For `k=|S|`, the least number of positive stages is

    L(S,b) = 2k + ((k+b) mod 2).

It is independent of the number of unrequested spectator blocks.
For all m blocks requested, the value is `2m-2+(m mod 2)`.

## Lower bound

In any prefix normal form, left multiplication by `E_s` adds one to
`a_(pi^-1(0))`, then replaces `pi` by `(0 s) pi`. This follows by moving
`D_0` through `P_pi`. Consequently `sum_j a_j` is exactly the word length.
Its parity at the requested endpoint is `k+b` modulo two.

Every requested nonanchor label j must occur among the stage indices.
If it never occurs, every block permutation fixes j, so `pi^-1(0)`
can never be j. Its Gaussian exponent stays zero, contradicting the
requested odd exponent.

Moreover j cannot occur exactly once when the final permutation is the
identity. Before that occurrence the coordinate initially at j is still
at j. That occurrence moves it to block 0. No later transposition touches
position j, so that coordinate cannot return to j. Thus every member of
S needs at least two nonanchor stages. The length is at least `2k` and
has parity `k+b`. These two conditions give the displayed bound. The
argument allows arbitrarily many additional unrequested blocks and visits.

## Attaining word and its exact residual

For every j in S, use the consecutive pair `E_j E_j`. Since
`D_0 P_j = P_j D_j`, this pair is exactly

    E_j^2 = D_j D_0.

Each pair restores its entire block permutation. Use all k pairs, then
append `delta=((k+b) mod 2)` copies of `E_0`. The exact endpoint is

    D_0^(k+delta) product_(j in S) D_j
      = M_0 D_0^b product_(j in S) D_j,
    M_0 = (D_0^2)^((k+delta-b)/2).

The exponent of `M_0` is a nonnegative integer. Thus the word meets
every requested parity and restores all block permutations, with exactly
`2k+delta` charged stages. All unrequested nonanchor coordinates are
untouched. `M_0` is part of the explicit endpoint, not a waived fee.
This proves equality for every block width w and every finite number of
spectators. For w=8 it applies to #5113's eight-axis Gaussian blocks.

## Consequence for an internally restored three-block word

Request all three blocks, with `k=2,b=1`. The exact minimum is five
stages. The three-stage word `E_0 E_2 E_1` in #5133 obtains the same
Gaussian support after an external block permutation is removed. Its
permutation is `P_2 P_1`, not identity, so it is outside this theorem's
return boundary. This is a changed requirement, not a disagreement with
that source. The five-stage constructor has residual `D_0^2`.

The theorem prices stage occurrences only. It does not establish a
minimal physical tape tariff or compare stages against the price of an
external permutation. It gives no main-owner independence, helper-target
credit, legal consumer, new signed invoice, supplier admission, new kappa
or complete multiplication theorem. Arbitrary nonmonomial free maps,
independently available `D_j`, and a boundary accepting a residual block
permutation change the model.

## Finite corroboration

The verifier implements the constructor and exact nonnegative exponent
normal form. An independent breadth-first search instead stores the
output-frame representation `D_mask P_pi`. It enumerates the full finite
quotient for one through six blocks, permits every stage at every state,
and obtains the distances to every permutation-restored support. It
imports no predecessor implementation.

A separate literal address-array interpreter uses the Gaussian
`[[a,b],[b,a]]` over F_65537 with `a=(1+i)/2`, `b=(1-i)/2`, `i=256`.
Here `i^2=-1`, `D^2=X` and `D^4=I`. It checks every operator column for
all support requests on the declared one-axis and two-axis block fixtures,
including the explicit `M_0`. This is finite-field corroboration; the
all-width theorem is the algebraic argument above.
