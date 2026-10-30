# Closing the 24 coordinate-kernel pools at span six

Prepared for Nicholas Stone with substantial OpenAI Codex assistance, 2026-10-25.
New material: Apache-2.0. This is a written reduction using the explicitly cited
predecessor lemma, with finite exact corroboration, not a proof-kernel theorem.

## Statement

In the four-scalar-register formal abelian BIT model, no eight-call word of
rational address span six with noncoordinate projectors in a coordinate
permutation of (0x0003,0x0022,0x0550) can have a diagonal monomial endpoint
with three invertible rational 3-by-3 target addresses. The fourth endpoint
address is arbitrary and all four input registers are arbitrary.

A paid factor is D_N([A])=I+([A]-1)N over F2[G], where G is the additive
group of rational 3-by-3 matrices, rank_Q(A)=1, and N=xy^t is a binary
rank-one idempotent. Coordinate-projector calls may be interleaved arbitrarily.
No arbitrary scalar basis change of a diagonal endpoint is made in this proof.

## Inherited lemma

David Govea's PR720, research/three-register-no-target-flag/README.md sections
1--4, states: for a three-register word with torsion-free abelian exponents,
relation lattice of rank at most two, and diagonal monomial endpoint, the
three endpoint exponents are sums of pairwise disjoint subsets of the paid
exponents. In particular their matrix ranks sum to at most the sum of the
paid matrix ranks. No invertibility or target flag is required for this lemma.
This is the low-corank lemma, not PR720's span-five exhaustive census.
Its source and inherited PR468/PR288/PR203 attribution are recorded in SOURCES.json.
The present package does not independently reprove that predecessor lemma.

## 1. A literal coordinate block

For packed bit 4i+j denoting entry (i,j), the representative is

    X = [[1,1,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]],
    Y = [[0,1,0,0], [0,1,0,0], [0,0,0,0], [0,0,0,0]],
    Z = [[0,0,0,0], [1,0,1,0], [1,0,1,0], [0,0,0,0]].

Each has zero fourth row AND zero fourth column. Every coordinate projector
also preserves the coordinate decomposition F2^4=F2^3 direct-sum F2.
Thus EVERY allowed factor, including every interleaved coordinate factor,
is block diagonal in this decomposition. E_33 acts only on the singleton;
X,Y,Z,E_00,E_11,E_22 act only on the triple. Restricting a triple factor
leaves a nonzero rank-one idempotent. No dirty input is discarded: the
decomposition is an identity of full operators on arbitrary inputs.

The 24 pools are coordinate permutations of this representative (PR5231).
A coordinate permutation preserves diagonality and merely relocates the
singleton. It need not preserve which coordinate is auxiliary, and the
argument below makes no such assumption.

## 2. Relation rank cannot grow on restriction

Let J be the set of triple-block calls and K the singleton calls, with
|J|+|K|=8. The full rational relation space is

    L_Q = {c in Q^8 : sum_j c_j A_j=0},   dim L_Q=8-6=2.

Every relation among (A_j)_{j in J}, extended by zeros on K, lies in L_Q.
This is an injection, so the triple subword's relation rank is at most two.
The generated address group is finitely generated and torsion free, so its
integral relation lattice has this same rank. Relations involving both
blocks do not invalidate this injection. No direct-sum assumption about
their ADDRESS spans is needed.

## 3. Rank budget

The full diagonal endpoint restricts to a diagonal monomial endpoint on
the triple. Apply the inherited disjoint-subset lemma to that subword:

    sum_(i in triple) rank_Q(C_i) <= |J|.

On the singleton each factor is multiplication by its monomial, so

    C_singleton = sum_(j in K) A_j,
    rank_Q(C_singleton) <= |K|.

Adding gives sum_(i=0)^3 rank_Q(C_i) <= 8. Three invertible 3-by-3 targets
already contribute nine, and the remaining rank is nonnegative. Contradiction.
This covers a singleton data register as well as a singleton auxiliary.
It allows arbitrary auxiliary diagonal address and arbitrary call order.

Equivalently, the lemma supplies disjoint frame assignments on the triple;
the singleton uses only the complementary indices K. Hence all four target
addresses admit disjoint-subset assignments in this class at relation rank <=2.
This stronger statement holds for any call count and any rational matrix size,
provided the coordinate 3+1 decomposition and relation-rank condition hold.

## 4. Scope and consequence

This resolves the 24-pool handoff of PR5231 using coordinate isolation, not
the kernel-support-union >=2 obstruction from that PR. The union is indeed
one here; that old argument failing does not make the coordinate block coupled.

Combining this result with the retained PR4119 classification, PR5075 cyclic-line
closure, and PR5231 exclusion of the other 48 pools would exclude the entire
eight-call span-six case for FOUR scalar registers. That combined statement
additionally depends on those predecessor reductions; the new checker does
not independently validate their universal proofs or re-enumerate the full
four-register flag census. The local result proved here is the 24-pool closure.

This does not settle span five or arbitrarily many auxiliary registers, and
does not change a physical supplier or the selected multiplication exponent.
For an upper-bound control, nine coordinate calls can produce three invertible
targets with total address span six. They belong to the allowed alphabet but
do not use all three exceptional projectors; no nine-call attainer with an
exactly prescribed occurring exceptional triple is asserted.

## Verification and credit

verify.py checks all 24 coordinate permutations, the literal 3+1 block and
restricted idempotents, and all positions of the three data targets. A separate
dense-matrix formal Laurent engine checks block factorization for every word
through length four in the seven-letter representative alphabet, and for
nontrivial cancelling words. It checks a nine-call span-six positive control,
rejects the two previously excluded 48-orbit representatives as coordinate-
isolation inputs, and rejects an off-block bridge and a rank-two projector.
These finite checks support the algebraic proof; they do not enumerate all
eight-call rational-address words or replace the inherited lemma.

Credit: woklerx/PR1846 (scalar orbit split), unpaidmoon/PR4119 (span-six
classification), Nick Petalas/PR5231 (48-pool exclusion and the explicit
24-pool question), David Govea/PR720 (arbitrary-target disjoint-subset lemma),
Ali Romman/PR468, eumemic/PR288 and huxint/PR203 (underlying model and methods).
JoyboyBrian/PR5075 supplies the separate cyclic-line closure. Only the
coordinate-isolation application and its checks are new work here.

Open next question: at four scalar registers, can frame span five permit eight
calls? Its relation rank is three, so the lemma used here cannot decide the
general coupled case. Start by retaining exact chronological endpoints while
classifying three-dimensional off-diagonal pattern spaces. No search of that
new problem was performed in this package.
