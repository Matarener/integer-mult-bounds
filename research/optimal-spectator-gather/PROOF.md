# Optimal overlap-aware spectator gathers

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and result

Partition a finite binary address into N neighborhoods of K coordinates each.
All neighborhoods use the same offset convention. Let A and B be sets of h
neighborhoods, with c=|A intersection B|. Write S and T for their full sets of
hK binary coordinates. The input is the complete binary rectangle, with arbitrary
payloads, preceding fibers and arbitrary correlations between all coordinates.

The completed operator on each active neighborhood is the same operator U.
The assignment of source neighborhoods to target neighborhoods is free, while
all K offsets within each neighborhood must be preserved. This is appropriate
for the common completed kernels in zxv's PR6070 global-H interface. It is a
changed assignment policy, not a new proof of its router or callee.

**Theorem.** There is a gather P sending S to T that moves exactly

    2K(h-c) binary coordinate positions

and is a product of exactly

    h-c whole-neighborhood swaps = K(h-c) binary-coordinate swaps.

Both counts are minimum, simultaneously. The binary-coordinate lower bounds
hold even if a competing coordinate permutation is allowed to split or reorder
neighborhoods, provided it still sends the complete set S onto T.

The theorem is an exact optimum in a coordinate-permutation model. A
coordinate swap is one transposition of two binary address positions. It is
not a claim about a minimum CNOT count, adjacent tape movements, arbitrary
linear charts, native recursive children or a complete physical invoice.

## Construction and lower bound

Put L=A minus B and E=B minus A. They have the same cardinality m=h-c.
Choose any bijection f:L to E. Exchange neighborhood a with neighborhood f(a),
offset by offset, for each a in L. Fix every other coordinate.

These exchanges have disjoint endpoints. They map A onto B, fix A intersection B
pointwise, fix every coordinate outside their symmetric difference and form an
involution. They move 2Km positions and use Km disjoint coordinate transpositions.
The deterministic implementation pairs the two sorted difference lists.

Let sigma be any coordinate permutation with sigma(S)=T. Every coordinate of
S minus T must move: fixing one would leave a coordinate outside T in sigma(S).
Every coordinate of T minus S must also move: if fixed, its unique preimage
would lie outside S. Thus at least |S symmetric-difference T|=2Km positions move.

The support of a word of l coordinate transpositions is contained in their
2l endpoints. Consequently l>=Km. The construction attains both lower bounds.
The same endpoint argument on neighborhood indices proves the m-swap lower
bound when each instruction exchanges two complete neighborhoods. This proof
works for every finite N,K,h and every overlap, including A=B, when no routing
is needed. The executable API requires h>=1; the empty case is trivial.

The use of disjoint transpositions and elementary support counting is standard.
The new contribution is the optimal assignment at this spectator gather
boundary, its executable constructor and its exact before/after application.
The original sparse-extension theorem already allows arbitrary bijections.
Its general extension and support-routing cost are not claimed again here.

## Arbitrary-input operator boundary

For any common linear operator U on one K-bit neighborhood, let U_A be the
product of its copies on A. Disjoint copies commute. Because P preserves every
neighborhood's offsets and sends A bijectively onto B,

    P inverse * U_B * P = U_A.

One can check this on basis tensors and extend linearly. It holds on all
payloads, including correlated dirty spectator data. No separability of the
actual input or zero workspace is assumed. P inverse=P, so the exact same
finite swap word restores the layout.

The hypothesis that the kernels are identical matters. Distinguishable jobs
must follow their own assignment constraints; a shared neighborhood may then
have to move. Offsets matter too: the implementation preserves them even for
an operator that treats different offsets differently. The finite checks use
both exact phase-sensitive Gaussian columns and a nonsymmetric, nonseparable
four-entry neighborhood operator.

## The spectator-row wrapper

Retain PR6070's row, front, active and back field capacities and its complete
nested stock Q. Suppose the source neighborhoods are aligned to the same K-bit
grid as the target active slots. Replace only its ordered exposure permutation
by P above. The active target slots and every field capacity are unchanged.

Every source coordinate maps into T. Therefore every preimage of a physical
position outside T is a genuine source spectator. This includes the complete
row prefix and compact controls, even if they originally intersect S. The
original wrapper's one whole-row padding and its row-independent completed
callee can consequently be used with the same declared contracts.

On a completed exact return, restrict to the original rows, then apply P again.
The result is U_A. For surrounding coarse-dependent diagonals D1,D2, the result
is exactly D2 U_A D1. The second diagonal must still wait for padding removal
and inverse exposure. This proof does not assume that a diagonal commutes with
exposure or with internal row mixing.

This is a local replacement implication under PR6070's stated completed-callee,
paid-router, ownership, precision, padding-disposal and tape hypotheses. It
does not discharge those hypotheses or any selected framework assumption.
No predecessor scientific replay is needed or claimed for this implication.

Under the retained support-router theorem, substitute k=2K(h-c) in its cost

    O(V (k+1)^(1-a_BIT) polylog(p) + poly(p)).

When c=0 this equals the previous 2Kh upper bound. When overlap is present it
can be smaller. The ordered construction can also already be optimal on some
inputs; no strict gain is claimed for every gather. When c=h the exposure is
identity and its routing can be omitted. No asymptotic exponent improvement
or fully priced supplier gain follows from these local counts alone.

## A strict before/after example

In the PR6070 layout take h=3, Q=3, G>=1 and K=128G. The row, front and back
widths are all K. The target block indices are B={2,3,4}; choose A={0,2,3}.
Enough trailing spectator capacity is retained.

The ordered gather maps 0 to 2, 2 to 3, 3 to 4 and closes with 4 to 0. At each
of the K offsets it is a four-cycle. Hence it moves 4K coordinates and its
shortest coordinate-transposition word has length 3K. The usual cycle-count
lower bound follows because a transposition changes the number of cycles by
at most one; each four-cycle can be built with three transpositions.

The new gather simply exchanges blocks 0 and 4. It moves 2K coordinates and
uses K coordinate transpositions, both optimal by the theorem. Blocks 2 and 3
stay fixed. The original row block 0 receives the old block 4, which is a
source spectator. All three original kernel jobs are still delivered.

The verifier constructs and enumerates both actual sparse permutations.
An encoded fixture has log2(p)=32, G=134, K=17152 and enough ambient reservoir
and suffix capacity. Its counts are 68608 to 34304 moved coordinates and
51456 to 17152 coordinate swaps. It is an encoded geometry, not an exported
production caller or execution of its enormous tensor. Small exact complete
row fixtures separately execute padding, dirty internal row cycling, return,
inverse exposure and both surrounding diagonals.

## Verification boundaries

The all-parameter theorem is the written proof above. Exhaustive enumeration
through seven neighborhood positions independently minimizes over every
permutation, including permutations moving unrelated spectators. The exact
operator checks corroborate the new implementation and boundary. They do not
formally prove the universal result or accept the inherited multiplication
framework. Unaligned source neighborhoods, different active operators, physical
router lowering and actual production-call installation remain open.
