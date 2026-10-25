# Neutral fixed-frame displacement-two reduction

The scope is the two immutable PR3734 words, with PR3886's scalar corridor,
sufficient ADD commutation rule, and exact nonzero SCALE conjugation. The first
ADD moves across **exactly two scalar neighbours**, retaining its binary frame;
the intermediate must satisfy all fixed entrance, cut, native-map and exit
checks. The second ADD can be any existing ADD, at any allowed scalar-corridor
cut and any common binary subspace. All other frames and interfaces are fixed.
No statement covers simultaneous rewrites with an illegal intermediate.

## First-word admission and neutrality

Write the affected three-instruction block as `g,h,k -> h,k,g` or its reverse.
For every crossed event sharing a register with g, baseline monotonicity puts
its frame after (or before) g's; reversed order puts it before (or after).
Containment in both directions requires equality of those two frames. Conversely,
these pairwise equalities preserve every register's ordered frame sequence up
to equal consecutive frames, while exclusive-register events only change their
chronological addresses. All source and destination block endpoints are the same.
Thus the equal-frame condition is necessary and sufficient for frame legality;
all first words have exactly the source invoice, including zero-rank omissions.
The exact incremental chronological tracer checks each changed block. An
independent direct event-itinerary oracle enumerates every first admission and
rejection; deterministic phase/direction/operation-pattern controls compare the
entire incremental trace and pricing geometry with fresh full reconstruction. SCALEs have frames and obey the same shared-register condition.

The scalar move is exact because each crossed ADD satisfies the sufficient
commutation rule, and each crossed SCALE adjusts the moved coefficient by the
appropriate rational conjugation. An independent rational matrix on every
register touched by each three-instruction block verifies the actual before/after
blocks, using independent input symbols for arbitrary dirty state. Composition
with identical surrounding operators proves whole-word equality. The inverse
cleanup is rederived when constructing complete-word controls.

## Why exactly two new insertion cuts suffice

Let the block occupy positions `[l,l+3)`. Cover second moves as follows.

1. If the second ADD is one of the ADDs in this block, explicitly enumerate
   **all** its legal corridor cuts and every relaxed legal frame dimension.
   This includes the first-moved ADD and both crossed ADDs, when present.
2. For a second ADD outside the block, explicitly enumerate its insertion at
   the two cuts `l+1` and `l+2`, with every relaxed legal frame dimension.
3. Every other destination has an equal-price counterpart in the pinned
   baseline single-move census.

For (3), the outside ADD's original location and frame are unchanged. Removing
it has the same frame predecessors and successors, modulo events of identical
frame on a shared register inside the permuted block. Destinations at or outside
the block endpoints similarly see the same before/after register frames. The
insertion interval (join of preceding frames through intersection of following
frames) and every dimension price therefore agree. A move reaching across the
entire block encounters the same set of ADD/SCALE instructions, so sufficient
commutation eligibility is unchanged and scalar conjugation factors multiply to
the same rational value. A move that does not enter the block changes nothing
there. Other phases are untouched. Thus baseline non-improvement applies without
iterating a theorem on an altered baseline.

For (2), the outside ADD's reach to the original block edge is unchanged.
The implementation checks the actual permuted instructions between that edge
and each interior cut. It then computes the new register frame neighbours and
insertion dimension prices. These are distinct cuts: checking just a single
middle cut, as for an adjacent pair, would omit a domain.

## Frames, relaxed checks, and exact signs

For a fixed removal/insertion cut, let `(p,q)` be the preceding and following
frames on each ADD register. The allowed common frame interval is their preceding
join through following intersection. Every dimension between its endpoint ranks
has a binary subspace, and its invoice depends only on that dimension. Pricing
all dimensions therefore covers all legal second frames, with no representative
orientation assumption. Fixed check boundaries are relaxed to virtual climbs as
in credited PR3886; every genuinely legal witness has zero such extra charge.

The new-minus-old signed histogram has zero rank mass. For ranks 1 through 9,
let `c_k = sum_r delta_r min(r,k)`. The retained exact criterion checks every
prefix sum of `c_1,...,c_8` is nonnegative and `c_9=0`. Discrete summation by parts
against the positive decreasing curvatures of `r^a`, `0<a<1`, proves the moment
difference nonnegative. The certificate is sufficient, not assumed complete;
unclassified rows cause a failure rather than a claimed improvement or theorem.
The first invoice is exactly zero, so the second difference is also the combined
difference from the source.

## Evidence boundary

The finite census authenticates both inputs separately and regenerates their
PR3886 baseline premise. Universal first dirty-state coverage is local rational
matrix composition, with whole-word free-operator replay on the baseline and
explicit deterministic samples. Sampled whole-word controls are not described as
8,034 independent whole-word interpreter runs. The sources, cost ledger and
validation receipt distinguish these scopes. The result does not admit a native
supplier, physical allocation, uniform precision implementation, all-size compiler,
outer release, or new selected kappa.

## Credit

PR3886 supplies the single-move theorem, tracer, applier and sign criterion.
PR3941 supplies the adjacent middle-cut idea and dirty scalar matrix check;
PR3942 supplies the exact frame-interval pricing implementation and legal
intermediate distinctions; PR3957 identifies the excluded neutral fixed-frame
displacement-two gap and supplies reusable verification/ledger scaffolding.
New work is the three-instruction/two-interior-cut reduction and its finite census,
by Chris R / Clear1nsight with substantial OpenAI Codex assistance. Retain
Jeremy Kothe's PR2957 positive fixture, dataisfire's PR3734 provider, Dugongue's
PR3863 target, Sagar Thakrar's auditor, roger-sato's adapter, and Arham Tahir's
frame-contract attribution. Apache-2.0 and retained source notices apply.
