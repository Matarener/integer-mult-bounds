# Sharp query dimension for unequal cycle payloads

This is an algebraic result about a precisely specified linear query interface.
It extends the equal-block argument in `paired-plane-block-rank` to arbitrary
payload dimensions and gives a compressed optimal construction. It does not
supply a physical copy tariff, native decoder, changed supplier or new κ.

## Five-cycle theorem

Let F be any field and d_0,...,d_4 be arbitrary nonnegative integers. Write
S=sum_i d_i and alpha=max_i(d_i+d_(i+2)), with indices modulo five. Let M be an
S-by-S matrix, partitioned into row/column blocks of sizes d_i, satisfying

    M_ii = I_(d_i),
    M_ij = 0 whenever i != j and i-j is not ±1 modulo five.

The permitted ordered blocks are arbitrary d_i-by-d_j matrices. Opposite
blocks need not be transposes. No shared eigenbasis, commutativity, coefficient
sign, or characteristic restriction is assumed. A zero-size block is empty.
Then the exact minimum rank is

    R(d) = max(alpha, ceil(S/2)).                         (1)

Equivalently, every linear query factorization M=A B needs at least R(d) field
coordinates of intermediate query capacity; a construction with exactly R(d)
coordinates always exists. This counts total query-vector dimension, not the
number of native calls or the binary geometric rank of a copy operation.

## Lower bound

Factor any admissible M through an r-dimensional space, where r=rank(M).
Let B_i:F^(d_i)->F^r be the i-th source block of B and
A_i:F^r->F^(d_i) its target block. Set U_i=image(B_i). The identity A_i B_i=I
makes B_i injective and A_i injective on U_i, so dim(U_i)=d_i. Both forbidden
blocks give

    U_i intersect (U_(i+2)+U_(i-2)) = {0}.                (2)

Indeed A_i kills that sum but is injective on U_i. In particular two
nonneighboring U's are disjoint, giving r>=d_i+d_(i+2) and hence r>=alpha.

Put t_i=dim(U_i intersect U_(i+1)). The two nonneighbors of i are themselves
adjacent. By (2) and the dimension formula for a sum,

    r >= d_i+d_(i+2)+d_(i-2)-t_(i+2).

Meanwhile the two spaces U_i intersect U_(i-1) and U_i intersect U_(i+1)
lie in U_i and have zero intersection, since U_(i-1) and U_(i+1) are
nonneighbors. Thus t_(i-1)+t_i<=d_i. Sum the latter inequalities to obtain
2 sum_i t_i<=S, and the former to obtain

    5r >= 3S-sum_i t_i >= 5S/2.

Consequently r>=ceil(S/2). These are inequalities of integer dimensions,
not division in F, so the proof includes characteristic two and zero blocks.

## Constant-size attaining recipe

Assign a nonnegative integer x_i to each permitted edge {i,i+1}, and p_i to
a private channel at vertex i. Require

    x_(i-1)+x_i+p_i = d_i.                              (3)

For each of the x_i coordinates, share one query between one unused coordinate
of payload i and one unused coordinate of payload i+1. Each of the p_i remaining
coordinates has its own query. The matrix associated with a shared coordinate
is the all-ones two-by-two block on that pair of coordinates; a private query
is a scalar identity. All other coefficients are zero. This fits the mask and
factors through sum_i(x_i+p_i) coordinates. We now attain (1).

**Dominant-pair case: alpha>=ceil(S/2).** Rotate indices so a maximum pair is
{0,2}. Maximality against {0,3} and {2,4} gives d_3<=d_2 and d_4<=d_0.
Since d_0+d_2>=S/2, the two residual capacities d_0-d_4 and d_2-d_3 sum
to at least d_1. Set

    x_2=d_3, x_4=d_4, x_3=0,
    x_0=min(d_1,d_0-d_4), x_1=d_1-x_0.

The inequalities above make every x_i nonnegative and within both endpoint
capacities. Define p_i by (3). All three vertices outside {0,2} are saturated;
only these two vertices can have private coordinates. Therefore

    sum_i x_i = d_1+d_3+d_4 = S-alpha,
    sum_i(x_i+p_i) = S-sum_i x_i = alpha.

This also covers the all-zero input and equality cases.

**Balanced case: alpha<ceil(S/2).** If S is odd, remove one coordinate from any
positive d_i and assign it a private query. Let the resulting dimensions be e_i;
if S is even take e_i=d_i and no private query. Now sum_i e_i=2h is even and
every nonneighbor pair has weight at most h: for odd S, the original integer
alpha was already at most (S-1)/2; reducing a coordinate cannot increase it.
Set

    x_i = h-e_(i+2)-e_(i+4).

These counts are nonnegative, and

    x_(i-1)+x_i = 2h-sum_(j!=i) e_j = e_i.

Thus sum_i x_i=h and adding the optional private coordinate yields ceil(S/2)
queries. This completes the attaining proof over every field.

`cycle.construct` implements exactly these two cases. The output contains five
edge counts, five private counts, the rank and a diagnostic branch name; the
five input dimensions are also recorded. It uses a constant number of exact
integer additions, comparisons and one halving, regardless of dimension.
For maximum bit length b the arithmetic and compressed storage cost O(b).
Expanding a matrix or actually moving payloads has its separate dimension-
dependent cost; the compressed construction is not a fast physical decoder.
No solver, dimension loop or floating-point arithmetic is used to construct it.

## Actual P112 principal-core consequence

PR2484's pinned certificate supplies the permitted-plane five-cycle

    C = [13,23,35,16,34]

and the separated 22-plane set

    Q = [0,4,8,17,18,19,20,21,24,26,28,29,32,36,38,39,41,42,43,45,46,52].

Both ports within a plane have forced off-diagonal zeros. Distinct planes of Q
are pairwise nonorthogonal and nonorthogonal to every plane of C. These are the
predecessor's finite geometry premises; both implementations reconstruct them
from the actual selected labels and matching rather than assume a graph input.

Give each of the 112 ports an arbitrary dimension n_p. For the two ports a_i,b_i
of cycle plane C_i put d_i=n_(a_i)+n_(b_i). Put
W=sum_(q in Q) sum_(p in plane q) n_p. The principal submatrix on these 54 ports
is exactly an identity of size W in direct sum with a five-cycle matrix having
block sizes d_i. Its exact minimum rank is

    W + max(max_i(d_i+d_(i+2)), ceil(sum_i d_i/2)).        (4)

The construction above attains this bound **on that principal mask**. Every
fitting matrix on all 112 ports has at least this rank, because taking a
principal submatrix cannot increase rank. We do not claim that (4) is the exact
minimum for the entire unequal-width 112-port mask: the other 58 ports may
require more query dimension. Native source access, copies, dirty restoration,
frames, hosting, numerical precision and physical realization remain unpriced.

Uniform n_p=d gives d_i=2d and W=44d, recovering the predecessor's 49d lower
bound. The predecessor already owns that value and its full equal-width
attainment. A literal seed-40 nonuniform example gives d_i=(5,8,8,5,4), W=101,
and exact principal rank 116. Its 131-by-131 principal matrix is checked over
three fields. This is an interface result, not a numerical supplier gain.

## Why both terms and the exact interface matter

For (100,1,1,1,1), half the total rounded up is only 52, but the true answer is
101. For five unit payloads the maximum nonneighbor pair is only two, but the
answer is three. For five dimensions equal to two the answer is five, smaller
than two copies of the scalar rank-three optimum. Neither averaging widths,
retaining only pair constraints, nor scaling the scalar optimum is valid.

A nonzero forbidden two-by-two block `[[1,-1],[1,-1]]` has zero trace and kills
the all-ones vector. Those weaker tests cannot replace the full ordered zero
mask. The proof requires the stated two-direction forbidden blocks and identity
normalization; changed masks, side information, nonlinear encoders, and different
source/consumer contracts need a new argument.

The independent finite audit enumerates all 17,859 directed binary completions
in its explicitly listed small dimension patterns, as well as 1,024 complete
integer edge-capacity problems. These are finite corroborations of the written
all-field proof, not a formal proof of all dimensions or the multiplication
theorem. Source archives and the selected frontier are unchanged.

Credit PR2484/thakrarsagar, PR2471/ywz65, the retained paired-plane-block-rank
argument and classical block-fitting/fractional-Haemers framework, Cinna Davis,
Adam Gall, ctoth, Philippe Van Velzen and the selected lineage. Tekalign, with
substantial OpenAI Codex assistance. Apache-2.0.
