# Local-first two-ADD retiming obstruction

## Statement and fixed contract

Fix either literal PR3734 provider retained in `inputs/`. A first existing ADD
may change its common binary frame in place, or move across exactly one adjacent
ADD or nonzero SCALE and change that frame. A second existing ADD may then move
any distance inside its allowed scalar corridor and choose any common binary
frame. Both the intermediate and final words must satisfy the fixed boundaries.
Every other gate, gate frame, entrance, target/centre cut, native warp, and exit
is unchanged. Each move stays within A after its prelude, B between native warp
cuts, or restore. ADD crossings use the sufficient condition
`destination(g) != source(h)` and `destination(h) != source(g)`; SCALE crossings
use exact conjugation. These are the PR3886 move rules, not every possible
semantics-preserving rewrite. The same ADD may be chosen twice.

**Theorem.** Every word in this class has new-minus-old raw rank moment at least
zero for every real `0 < a < 1`. The raw moment is `sum n_r r^(1-a)`. This is a
finite source-bound theorem conditional on the explicitly stated word/frame
contract, supported by the exact census below. It is not a universal two-gate
barrier or supplier admission.

The first move need not be neutral. The census also includes every locally
losing first move in this radius-one class. The second move has no radius bound.
A simultaneous edit which needs an illegal intermediate, a longer first move,
a moved SCALE, extra/deleted gates, warp/phase crossings, or another changed
boundary is outside the statement.

## 1. Reused scalar and single-move facts

The elementary matrix `I+cE_ds` commutes with `I+bE_uv` under the displayed
sufficient condition. Moving it right across a scale q at d multiplies c by q;
a scale at s divides c by q. Moving left reverses these factors. The source
scales are nonzero powers of two, so coefficients remain dyadic. These are
identities on arbitrary inputs, including dirty helpers. Cleanup is defined as
the literal inverse of the edited forward programme, with the inherited buffer
substitution; it does not require zero dirty state.

The PR3886 trace, move applier, complete single-move census, and sign criterion
are reused verbatim. The primary replay regenerates all 1,776,295 single-move
cut/dimension cases separately for each provider and compares the entire frozen
receipt, rather than trusting its old PASS flag. That census proves every
single-move delta is nonnegative for all real `0<a<1` in its fixed-check
relaxation. This package adds the following reductions and the actual paired
census; it does not claim the scalar identity or sign theorem as new work.

## 2. Reduction for an arbitrary changed first frame

If the second move selects the first moved ADD again, all other instructions
are still in original order with original frames. Removing that ADD from either
word leaves exactly the same sequence. Legal crossings compose, scale factors
telescope, and the final word is an original single-ADD candidate.

If the second ADD has no register in common with the first moved ADD, their
frame changes affect disjoint registers. The first ADD cannot be a scalar
barrier for the second. Removing it preserves the order and frames of every
instruction relevant to the second's price and crossing restrictions. Its
second-move delta is therefore an original single-move delta. The final delta
is the sum of two original nonnegative deltas. This argument remains valid if
their temporal intervals overlap or the moves are in different phases.

It suffices to enumerate second ADDs sharing at least one register with the
first, in all three phases, excluding the first ADD itself. The programme does
this without a distance cutoff. For the changed first frame it enumerates
actual subspaces, not just dimensions: those subspaces can change the next
move's geometry. The full census also compares every such intermediate invoice
with the separately retained frame auditor.

## 3. A fixed-frame adjacent swap creates just one new gap

Suppose the first move swaps adjacent gates g,h without changing either frame.
If they share a register, the two frames on that register are equal. Indeed,
nesting in the original and swapped orders gives both inclusions. If they are
disjoint, their frame actions affect different registers. Consequently the
complete frame state before both and after both is unchanged. The same is true
after removing any third ADD q: deleting q can change the preceding frame but
does not change either fixed gate frame.

If q is one of g,h, the final order is obtainable by a single original ADD move.
If a crossed gate is a SCALE, it cannot itself be chosen as the second ADD.
If q is a third gate, its old removal cost is unchanged. An insertion outside
the unique interior gap meets the same frame constraints as in the original
word. It also crosses the same relevant gates, either both members of the pair
or neither; their order does not change the sufficient crossing conditions or
commuting scalar scale factors. Thus only the interior gap in h,g order can
have a genuinely new price. Moves in another phase or warp corridor reduce to
the original census as well.

Even at that gap, q must touch both g and h to require a new check. If it touches
only h, the identical price/frame occurs after both in the original g,h order;
if it touches only g, it occurs before both. If it touches neither, either side
works. The additional gate crossed in that comparison is disjoint from q and
cannot be a barrier. Duplicate descriptions of an unchanged placement must be
normalised: insertion immediately after the original q is the same position
as immediately before it once q is removed. The unpruned control implements
this address convention explicitly.

The fast bridge census therefore tests third ADDs touching both members of
each legal fixed-frame adjacent pair, at its one new gap. It computes removal
costs from the original trace and insertion constraints after the literal
swap. A separate direct adjacent-pair enumerator checks the first-pair set.
Controls compare the fast formula against full intermediate traces, include all
four nonzero bridge cases per provider, and test omitted non-bridge cases
without the pruning predicate. These finite controls supplement this reduction;
they do not replace its proof.

## 4. Complete finite frames and prices

For either moved ADD, with preceding frames P1,P2 and next fixed constraints
Q1,Q2 after removal, its possible common frame F satisfies
`L=P1+P2 <= F <= H=Q1 intersect Q2`. If L is not contained in H there is no
candidate. Otherwise every dimension between `dim L` and `dim H` occurs.
On one register, removal contributes

    f(q-p)-f(u-p)-f(q-u),       f(r)=r^(1-a), f(0)=0,

and insertion at dimension d contributes

    f(d-p)+f(q-d)-f(q-p).

The second price depends only on d, so enumerating dimensions covers every
second frame without sampling bases. The first frame is enumerated as a full
subspace because it changes the second interval. One-vector extensions enumerate
all such subspaces inductively. Every actual first interval has quotient rank
at most three; the implementation raises an error, rather than silently
truncating, if its declared resource bound of four is exceeded. An independent
quotient-basis/subset-XOR enumeration checks all 3,118 source intervals across
both providers.

As in PR3886, a fixed check is relaxed to a virtual climb for pricing. This
charge is zero on the original and every genuinely legal candidate. Native-map
entrances are explicit checks, and no move crosses them. Centre descents are
separately billed without overwriting the main forward frame. Intermediate
words are checked against the actual boundaries; second candidates form a
possibly larger relaxation. Non-improvement throughout that relaxation implies
the stated result for legal final words.

## 5. Exact all-exponent conclusion and accounting scope

For each combined new-minus-old histogram d, define
`C_k=sum_r d_r min(r,k)` and `S_j=sum_{k<=j} C_k`. All emitted deltas have zero
rank mass and nonnegative S_j. PR3886's summation-by-parts identity writes their
moment difference as

    sum_j S_j (theta_j-theta_(j+1)),
    theta_k=2f(k)-f(k-1)-f(k+1),

with the final theta set to zero only for this finite identity. The real-power
curvatures are positive and decreasing on `0<a<1`; the triangular integral
proof, including its convergent endpoint at k=1, is retained in the predecessor.
Every coefficient in this sum is nonnegative. Every nonzero delta is strictly
losing; zero is exactly neutral. The 49 combined types are retained with their
multiplicities, caps, and prefixes. No floating-point grid supplies the proof.

An unchanged positive normaliser and common added bill preserve this ordering.
Extra nonnegative charges cannot turn it into a saving. Helper widths, fixed
entrances/exits, and buffer identities are unchanged by the class. This does
not establish uniform coefficient/precision costs, native Clifford identities,
hosting, or outer admission for every edited word. A programme which also
reduces some previously common physical bill would be a different comparison.
There is no new kappa, all-size multiplication theorem, human peer review, or
formal-kernel proof in this package.
