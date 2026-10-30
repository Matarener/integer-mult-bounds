# Fallback and completed-leaf algebra over odd prime powers

Independent audit, 2026-10-19. This closes algebraic identities, not the
complete machine refinement or multiplication theorem. Source conventions:
`selected-bit-recursive-closure/vendor/fallback_program.py`, `descriptor.py`,
and `selected-bit-recursive-closure/leaf.py`.

## Unnormalized elimination and the current row permutation

Let R=Z/q^w for an odd prime q, and let N(P) be the partial interchange from
NORMAL-FORM.md. In an image/kernel basis, it swaps r head/tail pairs
and fixes the others. Hence it is invertible and det N(P)=(-1)^r.
Every invertible matrix over R admits the retained unnormalized elimination:
after the first k pivots, the remaining diagonal block is invertible; its
first column has a unit entry, since its reduction modulo q has a nonzero
entry. Pick the first such row, swap it into place and clear the column in
all other rows. Never normalize a row by multiplying it by a pivot inverse.

The pivot itinerary depends only on the reduction modulo q. In particular it
is constant throughout a complete high-header packet. Retain all zero shear
slots so the schedule is independent of full-ring coefficients. At the end
the matrix is diagonal D with unit entries d_i. Row additions have determinant
one and row swaps determinant -1, so product d_i is either 1 or -1.

For an arbitrary diagonal unit B0=diag(b_i), let pi_t(i) name the original
row at current position i and set B_t=diag(b_(pi_t(i))). If M_t is the
unweighted elimination state, the weighted state is exactly

    M_t^w = B_t M_t B0^-1.

A row swap stays an ordinary unit swap, because it also changes pi_t. A
shear i<-i+c k becomes i<-i+c b_(pi_t(i))/b_(pi_t(k)) k. These assertions
follow by multiplication of the elementary matrices; all divisions are by
units. The final weighted diagonal is

    t_i = d_i b_(pi_final(i))/b_i,
    product_i t_i = product_i d_i in {1,-1}.

To reconstruct the weighted residual, first implement this diagonal and
then undo elimination in reverse chronological order. Each inverse shear
must use its OWN pi_t. Replacing it by pi_final is generally wrong. The
source's `annotated_reductions` records pi before each operation, and
`compile_program` reverses these annotated reductions; `coefficient` uses
that snapshot. This agrees exactly with the covariance identity above.

## Diagonal pairs and the fallback child count

Write J_ij for an ordinary swap and J_ij(t) for the weighted swap
(x_i,x_j)->(t x_j,t^-1 x_i). Executing J_ij followed by J_ij(t) gives
diag(t,t^-1) on these two positions. For i=0,...,2m-2, apply that pair with
j=2m-1 and t=t_i. The first 2m-1 diagonal entries are correct; multiplying
the last coordinate by product d_i, a fixed sign, supplies t_(2m-1).
This is precisely the source's initial diagonal-pair word.

An upper shear is J_ij, one later-target shear, J_ij. There are at most
2m-1 elimination swaps, 2(2m-1) diagonal-pair swaps and twice m(2m-1)
swaps surrounding upper shears. With m=64 this is

    127 + 254 + 2*8128 = 16637 swaps.

Each physical swap of two f-atom fields uses one reversed f-child. If the
fields have the same orientation, reverse the later field before and after.
Each reversal uses one unit reversed child on its two floor(f/2)-atom
halves, leaving the central atom untouched when f is odd. For f=1 these
two half children are omitted. Thus there are at most 3*16637=49911
children, each of width at most f; the retained allowance 32*64^2 is larger.

For a weighted diagonal pair in the tail bank, the physical first-field
index j means logical index f-1-j; the source's `FallbackPair.reverse` and
`physical_atom`/`logical_column` conventions perform exactly this reversal.
Opposite-bank fields already have opposite physical orientations. A same-
orientation swap becomes coordinatewise after the two later-field reversals.
Every half reversal retains the gap and odd middle as complete spectators.
These identities work for all f, not just even f or complete coarse powers.

## A completed weighted leaf without a weighted-child oracle

For a single ordered pair (x,y) and a unit a, the retained eight-step word is

    J; L_a; J; L_(-a^-1); J; L_a; J; sign_on_second,

where L_c sends (x,y) to (x,y+c x). Its successive pair states are

    (y,x), (y,x+a y), (x+a y,y), (x+a y,-a^-1 x),
    (-a^-1 x,x+a y), (-a^-1 x,a y), (a y,-a^-1 x),
    (a y,a^-1 x).

The final identity is exact in R. For n<64 execute it on the disjoint
reversed pairs. Coefficients may depend arbitrarily on frozen ancestor
fields but not on the active pair, so each L_c is an ordered controlled
translation on a complete target fiber. An ordinary interchange supplied
by a PRECEDING completed stage implements J. Four such calls per pair and
three translations plus a linear sign give the stated leaf toll. The
stage-a0 leaf uses elementary q-digit interchanges, so no recursive or
weighted-swap assumption is hidden in its base case.

All these are address identities. The corresponding complete-stream
payload permutations follow by pullback, preserving every spectator and
arbitrary correlations. Physical movement, preparation, parking, and
uniform source compilation remain obligations of the caller audit.
