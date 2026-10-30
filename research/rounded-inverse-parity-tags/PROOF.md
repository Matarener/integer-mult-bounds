# Five coordinate parities are necessary and sufficient

This is a scoped proof using an exhaustive finite certificate for its final
coordinate-covering step. It concerns one fixed rounded map and one restricted
side-information interface. It is not a complete multiplication theorem.

## Map and credited premises

Use zxv's PR5444 matrix M, with 112 rows and eight columns, as copied without
change into MATRIX.json. The Gram identity M^T M = 56 I and the rounded native
inverse interface are predecessor premises, not new results here. PR5444
builds on Ali Romman's PR5323 recovery theorem, JoyboyBrian's PR5035 finite
kernel, and Dillon Amburgey's PR4933 and David Ganz's PR4929 native geometry.
Their source notices and claims remain unchanged.

For x in Z^112 define

    q(x) = R(16 M^T x / 52),
    F(x) = 16 x - M q(x),

where R rounds each coordinate to the nearest integer, with half ties away
from zero. A tag is the tuple of x_i modulo two for a fixed known set S of
owner indices. The set is independent of x and the output. No additional
input read or observation is available to the decoder.

**Theorem.** The smallest cardinality of S making

    x -> (F(x), (x_i mod 2) for i in S)

injective on all of Z^112 is five. One attaining zero-based set is

    S = {0, 9, 27, 76, 79}.

The lower bound is certified by all 6,210,820 four-element subsets of the
112 indices. Each misses at least four of the 128 distinct collision-parity
signatures defined below. These signatures are not preimages of a single
output; they collect all possible collision differences over all outputs.

## Reduction to a fixed finite domain

Choose an integer 112-by-eight matrix B satisfying M^T B = 2 I. The verifier
finds each column B_j as a signed sum of two coordinate unit vectors and
checks all eight identities. This also gives the decoder's quotient
congruences. The source row-lattice description in PR5444 already implies
the existence of such witnesses.

Suppose F(x) = F(x') = y. Write q = q(x), q' = q(x'), and s = M^T y. Then

    16 (x' - x) = M (q' - q),
    M^T (16 x) = s + 56 q.

The rounding equation for a single quotient coordinate is

    R((s_j + 56 q_j) / 52) = q_j.

It implies -26 <= s_j + 4 q_j <= 26. The admissible integers are consecutive
after possibly deleting the boundary endpoints. There can be fourteen
integers in the closed interval only if both endpoints occur. At residual
-26 the lower quotient would need q_j >= 1 for half-away rounding. At
residual +26 the upper quotient would need q_j <= -1. Both conditions cannot
hold because the lower quotient is smaller. Thus at most thirteen
consecutive integers survive, and |q'_j - q_j| <= 12. This scalar interval
argument is also present in PR5444; it is recalled to delimit the new finite
reduction rather than claimed as a new precision frontier.

Multiplying the first equation by B^T gives

    16 B^T (x' - x) = 2 (q' - q).

Consequently q' - q = 8 v for v in {-1,0,1}^8. For a nontrivial collision
v is nonzero, and

    x' - x = M v / 2 in Z^112.

Define

    V = {v in {-1,0,1}^8 \ {0} : M v is even in every coordinate}.

Every nontrivial collision therefore has a difference Mv/2 with v in V.
The full domain is only 3^8 = 6,561 vectors before filtering. No cutoff on
the magnitude of x is used in this implication.

## Every retained direction is an actual collision

The finite reduction above is exact, rather than just a necessary condition.
For any v in V, set

    x = -7 B v,
    x' = x + M v / 2.

These are integer vectors. The predecessor Gram identity gives

    M^T x = -14 v,
    M^T x' = 14 v.

Since R(56/13) = 4, their quotients are -4v and 4v. Hence

    F(x)  = 16 x + 4 M v,
    F(x') = 16 x + 8 M v - 4 M v = F(x).

They are distinct because M has full column rank and v is nonzero. The
literal verifier also checks both endpoints of every one of these new
collision witnesses using a separate Fraction-based implementation of F.

For v in V, define the 112-bit signature

    sigma(v)_i = (M v / 2)_i mod 2.

It follows that a fixed coordinate set S suffices exactly when every
signature is nonzero on S. If a signature vanishes on S, the explicit pair
above defeats those tags. If none vanishes, the necessary collision
reduction proves injectivity for every integer input.

## Finite certificate and exact minimum

The verifier enumerates all of V directly from the literal matrix. It
obtains 480 signed directions and 128 distinct signatures, with no zero
signature. For each owner index i it constructs a bitset recording the
signatures nonzero at i.

The union of the five bitsets for {0,9,27,76,79} contains all 128 signatures.
For the lower bound, the verifier visits every a < b < c < d in {0,...,111}.
It computes the uncovered-signature bitset and rejects if that bitset is
empty. The number of visited sets must equal binomial(112,4) = 6,210,820.
Its smallest uncovered count is four. The complete histogram is generated
in the stdout receipt, together with package-file hashes and five literal
collisions obtained by omitting one member of the attaining set.

This is the finite computational step of the proof. The all-input
conclusion follows from the preceding exact reduction. A set of fewer than
four coordinates extends to a four-element set and therefore also fails.
The five-element witness supplies the matching upper bound.

## Constructive decoding

Given y and the five tags, enumerate possible quotients as follows. For
each sparse B_j, the equality y + Mq = 16x implies

    B_j^T y + 2 q_j = 0 mod 16.

Thus B_j^T y must be even, and q_j is fixed modulo eight. Intersect this
residue class with the closed interval

    ceil((-26-s_j)/4) <= q_j <= floor((26-s_j)/4).

There are at most two choices per coordinate, hence at most 256 quotient
tuples. For each tuple, require y + Mq to be divisible by sixteen, form x,
check the five parities, and check the defining map F(x) = y. Valid encoded
input has one matching candidate. The injectivity theorem rules out a
second. Checking the defining map handles the half-tie endpoint rules
without granting them incorrectly.

The supplied Python codec limits input integers to 4,096 magnitude bits.
Its output parser allows twelve additional bits. That covers the forward
map, whose row supports have size four and column supports have size 56:
|F(x)_i| <= (16 + 896/13) ||x||_infinity + 2.
The mathematical theorem is unrestricted in integer magnitude. The code
rejects excessive requests rather than claiming an all-size machine bill.

## Scope and remaining obligations

PR5444 already supplies a maximum fiber of sixteen and an optimal general
four-bit tag at this precision. Five is the new optimum only for fixed
individual-coordinate parity tags. It does not improve that unrestricted
information optimum. The gap is one bit, and it avoids requiring the tag to
be an arbitrary function of all inputs. No claim about the physical price
of acquiring those parities or computing either decoder follows.

Reversible tag acquisition and cleanup, numerical access, rounding-error
propagation, scratch, fixed-tape travel, native hosting, the complete caller,
recursive pricing and the outer theorem remain unproved here. No selected
frontier change or new kappa is claimed. Independent human and formal
proof-kernel review are unclaimed.
