# Arbitrary-plane temporal rails on the PR1094 word

## Claim and boundary

This is a scoped proof and an exhaustive finite obstruction. Fix the historical
PR1094 gauge44 word, with compressed member SHA256
`49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289`.
Use exactly the temporal-rail contract posed by Cinna Davis in PR1996:

- Preserve the scalar word, initial frames, helper inventory and scalar maps.
- At one existing A/B helper-helper addition, enlarge its common frame by a
  subspace P of the binary address space F2^9.
- Thereafter use the least common-frame closure. At each event, the new common
  frame is the join of its original frame and the incoming participant frames.
- Preserve every A/B target-level and centre-frame boundary exactly, together
  with every final live, target and dirty-helper endpoint.
- Charge every induced frame climb at its actual rank. The eight fixed rank-8
  centre descents are unchanged.

The theorem below answers the arbitrary **two-dimensional** P question left
open in PR1996. It does not constrain the current selected P104 word, changed
scalar programs, changed boundaries, multiple injections, or nonminimal closure.
The scalar endpoint identity is inherited from the pinned word. No new native
operator replay or supplier admission is claimed.

## Backward safety lemma

The following statement holds in every finite-dimensional vector space over
any field, for a finite common-frame schedule with monotone original frames.
A fixed event must retain its original common frame; other common frames may
enlarge. The original schedule satisfies every fixed event.

For each register immediately after the last event, start with the whole
ambient space as its safe space. Process events backward. For an event i with
participant set R_i and original common frame F_i, put

    C_i = intersection of the current safe spaces of registers in R_i.
    If event i is fixed, replace C_i by C_i intersect F_i.
    Replace each participant's safe space by C_i.

Other registers keep their safe spaces. For a nonfixed seed s, introduce P into
all its participants immediately after the seed common frame. Its least
forward closure respects every later fixed event **if and only if P <= C_s**.

Proof by backward induction: a participant output must satisfy its own future
safe space. Since the event makes one common frame, that common frame must lie
in the intersection of all participant safe spaces. At a fixed event it must
also lie in F_i. The original F_i already lies in that intersection, because the
unmodified schedule is valid. Thus joining incoming excess X to F_i is safe
exactly when X lies in C_i. This condition applies independently to each
participant's incoming excess, so assigning C_i to every participant is both
necessary and sufficient. Nonparticipants are unaffected. The base case has
no future constraints. Applying the induction after the seed gives the stated
criterion. This argument also covers an excess that later becomes contained in
an original frame: every later use of that frame already preserves it.

This proves more than a heuristic pruning rule. It identifies the complete
admissible injection subspace at each seed. It uses no symmetry assumption and
no coordinate-plane restriction.

## Complete finite enumeration

`model.py` reconstructs 6,237 frame events on 704 registers from the authenticated
word. There are 2,525 eligible A/B helper-helper seeds. It inserts the exact
internal barriers and terminal frames from the source contract. Subtracting its
original climb histogram from the reported complete profile leaves precisely
eight rank-8 centre descents.

The binary two-spaces are in bijection with triples {a,b,a XOR b} of nonzero
vectors. The iterator emits the unique ordering a < b < a XOR b. In a cap with
q points there are (q-1)(q-2)/6 such triples, checked against the emitted total
at every seed. The whole ambient space therefore has 43,435 planes, including
36 coordinate planes. The full domain has 109,673,375 plane/seed pairs.

The backward cap dimensions and number of seeds are:

| Dimension | Seeds |
|---|---:|
| 0 | 1014 |
| 1 | 49 |
| 2 | 223 |
| 3 | 78 |
| 4 | 376 |
| 5 | 168 |
| 6 | 408 |
| 7 | 202 |
| 8 | 7 |

Enumerating the planes inside each cap gives 919,876 legal pairs. Of these,
718,317 have P <= F_s and change nothing. The remaining 201,559 pairs are
propagated and priced explicitly. The complement has 108,753,499 illegal pairs,
by the necessary and sufficient backward criterion. This complement count is
not a classification of distinct failure causes.

For a plane P and an original binary frame F, the number of nonzero points in
P intersect F is 0, 1 or 3. Consequently

    dim(F + P) = dim(F) + 2 - dim(F intersect P).

The implementation obtains the intersection dimension from that point count.
It propagates a perturbation only along affected register events, and stops
propagating on a register once P is absorbed in its original frame. All affected
incoming and outgoing climb ranks are accounted for. The total rank mass must
remain unchanged: along each register's monotone chain, the sum of climb ranks
is its fixed final dimension minus its fixed initial dimension.

The changed legal pairs produce exactly 45 distinct complete paid profiles.
Their multiplicities and one attaining plane/seed per profile are generated in
`RESULT.json`. This is the new domain extension. The predecessor coordinate
census and its native auditor are not run or used as result oracles.

## Exact cost comparison

Use only the historical word's fixed-template ceiling model from
`complex-local-word-ceiling/ceiling.py`: m=73, 896 families, 9 stages, centre
charge 64, idle rank 51, and one unpaid coordinate per family. It is an
optimistic accounting model, not a current supplier or outer theorem.

The baseline profile is

    {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}.

The verifier encloses its root between
1690054109/10^12 and 169005411/10^11, using the pinned rational interval engine.
For each of the 44 different profiles, the lower bound for its complete
normalized moment at the **lower** baseline endpoint is strictly greater than
one. This includes the idle mass at rank 51. Hence every such profile's root
is below the baseline's lower endpoint. Monotonicity follows because all
normalized ranks are strictly between zero and one and the charges are
nonnegative.

Exactly one distinct profile equals the baseline. It occurs at 28,224 changed
legal pairs, in addition to the 718,317 no-op pairs. Thus allowing every binary
plane yields no ceiling improvement at all, even before charging any additional
physical implementation fees. The finite result is stronger than failure to
reach the predecessor's 5% screen.

## Verification limits

The registered replay authenticates both live inputs, rebuilds caps, enumerates
every admissible plane, recomputes every changed legal profile and checks all
44 strict interval comparisons. A full-frame forward implementation checks
one witness for each of the 45 profiles. It joins actual incoming frames rather
than using sparse active-plane propagation. There are also 28,672 exhaustive
small schedule/plane checks of the safety criterion and profile propagation,
plus rejecting controls for forbidden injections and a corrupted paid profile.
The normal and optimized interpreters exercise the same explicit checks.

These finite checks corroborate the written reduction. Independent human,
formal proof-kernel and full native operator review are unclaimed. No selected
replay, Lean, Docker, physical movement, rounding, stock or all-size theorem
obligation is discharged. The contribution is produced by Nick Petalas.
