# Sharp two-frame repair obstruction

Fix the 112 literal nine-bit labels in the selected DATA-PHASES payload, with
binary pairing `b(q,r) = popcount(q & r) mod 2`. Fix PR3356's thirteen disjoint
eight-port Gram-I8 frames and its eight remaining ports. A retained frame must
remain an entire group. All other ports may be repartitioned freely.

**Theorem.** Among partitions into nonempty even binary orthonormal groups that
retain at least eleven of those thirteen particular frames, the minimum group
count is exactly sixteen. Consequently, the recipe that assigns two scalar
supports to each group needs at least thirty-two supports in this class. A
fifteen-group construction must disturb at least three original frames.

This is a group-partition theorem. It is not a lower bound for arbitrary fitting
matrices, arbitrary scalar factorizations, a different predecessor packing or
native multiplication algorithms. Unrestricted fifteen-group attainment remains
open. PR3373's global fourteen-frame exclusion is motivation, not a dependency
of this proof.

## Reduction to 78 complete finite domains

An orthonormal group is linearly independent in F2^9: pairing any linear relation
with its jth member recovers the jth coefficient. Its cardinality is at most
nine, and an even group therefore has at most eight members.

Suppose a partition into at most fifteen groups retains eleven original frames.
Select eleven retained frames, even if it actually retains twelve or thirteen.
The unselected pair of original frames and all eight original tail ports form a
24-port set. At most four groups remain to cover it. There are exactly
`choose(13,2) = 78` possible choices. Conversely, a cover of any one of those
24-port sets by at most four even orthonormal groups, together with the eleven
untouched frames, would give a partition into at most fifteen groups.

For each case, the primary checker enumerates every even orthonormal subset G
of sizes 2,4,6,8 of its 24 labels. Increasing-index extension maintains a set of
common orthogonal neighbours. Every orthonormal subset has exactly one increasing
ordering, so none is omitted or duplicated. Diagonal unit norms are checked
against the literal selected labels.

Let U consist of the empty mask, every group mask in G, and the union of every
disjoint pair of masks in G. U is exactly the sets coverable by at most two
nonempty groups. A cover of the complete domain F by at most four groups exists
if and only if some `u in U` also has `F \ u in U`. One direction splits any
four-group cover into two collections of at most two groups. In the other
direction, complementarity makes the two collections disjoint and complete.
Empty collections handle covers using fewer than four groups.

The exact computation finds no complementary pair in every one of the 78
cases. RESULT.json records the complete case list, each even-group histogram
and its number of distinct two-group union masks. The maximum case has 1,511
groups and 222,765 such union masks; the sum of the per-case union counts is
9,761,617. These are exact finite counts, not runtime measurements or solver
UNSAT reports.

Thus at least sixteen groups are necessary. The unchanged PR3370 certificate
has sixteen groups, of sizes eight eleven times, six twice and four three
times. The checker validates its full port partition and every Gram entry and
checks that exactly eleven groups are original full frames. This supplies the
matching upper bound. The sharp witness and its discovery remain Tekalign's
contribution; the new result is the independently checked local lower bound.

## Separate checker and controls

`independent.py` converts each selected q to nine explicit binary coordinates.
It builds orthonormal subsets by increasing tuple layers, independently of the
primary bitset extension. It then searches covers by choosing an uncovered port
with the fewest compatible groups and exhausting every possible group containing
it. Remaining cardinality bounds prune impossible branches. It uses neither the
primary union algorithm nor its group list. All 78 cases agree, with 9,653 unique
search states in total and at most 985 in a case.

Every search limit fails with an error and no exclusion. The independent search
allows 500,000 iterations per case. The primary union set is capped at one
million entries, with a check after each row of at most 4,096 additions. These
limits exceed the checked source instances and are not used as proof cutoffs.

Controls compare both clique enumerators against complete powerset enumeration
and both cover decisions against a minimum-cover dynamic program on 36 small
source subsets. Both feasible and infeasible outcomes occur. A four-group
positive fixture and its missing-group negative fixture check complementarity.
Malformed partitions, false Gram entries, source corruption, input capacities
and an exhausted independent-search budget must be rejected. Optimized Python
runs retain every mathematical check because checks use explicit exceptions.

## What was attempted but not proved

The predecessor PR3370 reports all 78 four-group SAT repair cases as UNSAT,
without proof checking. This package supplies independent exact exhaustion and
the sharp retained-frame theorem. It does not claim first discovery of those
negative solver reports.

A larger set-cover pilot was stopped without a witness. A compact unrestricted
fifteen-colour CP-SAT run returned UNKNOWN at its 240-second limit. A bounded
size-preserving swap search also found no witness. A separate three-original-frame
repair pilot ran 225 of 286 cases with a per-case conflict budget: 92 returned
UNSAT without independently checked proofs and 133 returned unknown. None is
used for an exclusion. These attempts did not produce a fifteen-group partition
and do not rule one out, even in the three-frame domain.

## Boundary and cost ledger

The exact selected labels, predecessor frames, sixteen-group upper witness and
78 local exclusions are checked here. The thirty-two-support consequence is
only for the two-support-per-group recipe with the stated retained frames.
PR3370's reported complete-plane one-total charge is still 224; no cheaper
physical program is constructed here. Arbitrary changed fits, overcomplete
query spaces, source access, frame transport, dirty restoration, storage/hosting,
precision/tape, all-size compiler admission, both suppliers and outer transfer
are outside this proof. Unknown costs are not assigned zero. This is one bounded
interface result, and it does not authorize another supplier expansion or change
the selected frontier.

Credit Nick Petalas/PR3356 and PR3373, Tekalign/PR3370, Matarener/Mark/PR3335,
ctoth, ywz65, Sagar Thakrar, Cinna Davis, Adam Gall, Jeremy Diviney,
Philippe Van Velzen and the retained E8/P112 and selected-supplier lineage.
Apache-2.0. Independent mathematical and proof-assistant review remain open.
