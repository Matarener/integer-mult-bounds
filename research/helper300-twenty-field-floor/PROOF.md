# Exact 38-H1 floor for the twenty-field backward boundary

## Result and scope

For the selected backward provider's event interval **[9044,9137)**, let the
field set be the dependency closure of roles {19,300,301}. Every exact
replacement in the following model has the source's original per-field
strict frame chains, hence exactly **38 rank-one paid climbs**. The original
block attains the bound. In particular, its paid moment cannot be reduced
for any exponent 0 < t < 1.

The model permits any finite rational ADD/nonzero-SCALE factorization,
arbitrary coefficients, arbitrary chronology, and temporary changes of
basis. It fixes the twenty fields, their capacities, their arbitrary
entering values, and their individual entry and exit frames. ADD operands
must occupy the same actual frame. Paid operations are strict nested frame
ascents of rank dim(new)-dim(old). All intermediate binary subspaces are
allowed; the search is not restricted to the source frame catalogue.

The model excludes auxiliary fields, access to fields outside this closed
block, new warps, descents, chart-changing exchanges, cross-column
conversions, approximate encoding, and changed input/output contracts.
The result is a local finite-frame theorem conditional on the inherited
native chart interpretation. It is not a new kappa, a whole-provider
impossibility theorem, or an unconditional multiplication theorem.

## Source binding and independent exact extraction

Canonical checkpoint: `32890bc5de034ab8fc93ac88ead7279a6a416d04`.

The actual backward tape is:

`research/coupled-helper-neutral-completion/capsule/workspace/swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/WORD.json.gz`

Its compressed SHA256 is
`7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc`;
its decompressed SHA256 is
`05490717144b3e6c69c0cc9e5c5df5c69d841ca13bf29aabd1b0db180628f038`.
Its source-payload link binds
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, whose compressed
and decompressed hashes are respectively
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05` and
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.

Indices are zero-based and the interval is half-open. Its exact field closure
is `[18,19,39,40,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303]`.
The 85 relevant source events are 38 H1 climbs, 43 ADDs and four SCALEs.
Every interval event touching this set touches only this set. There is no
warp, cache copy, clear or zero retag inside it. Intervening instructions on
other fields commute with a replacement of the isolated block.

The matrix is computed over Q by starting with twenty independent unit rows
and applying every relevant scalar event. Its rank is twenty. The prefix
through event 9043 has only invertible persistent ADD/SCALE, warp and climb
operations, invertible chart adapters and phase annotations. The native
interpretation of those frame changes is inherited. Within that model it
imposes no relation on the twenty values; no zero-input specialization is
used.

| Role | Entry frame | Exit frame | Retained strict chain |
|---|---:|---:|---|
|18|20|437|20,425,437|
|19|21|436|21,423,436|
|39|41|436|41,426,436|
|40|42|422|42,422|
|288|103|432|103,422,432|
|289|103|434|103,423,434|
|290|56|432|56,425,432|
|291|56|433|56,426,433|
|292|104|434|104,427,434|
|293|104|431|104,428,431|
|294|57|433|57,429,433|
|295|57|431|57,430,431|
|296|20|435|20,427,435|
|297|20|420|20,420|
|298|42|435|42,429,435|
|299|42|419|42,419|
|300|0|437|0,21,430,437|
|301|0|419|0,21,419|
|302|0|428|0,41,428|
|303|0|420|0,41,420|

Here zero, line, plane and cube mean dimensions 0,1,2,3 in F_2^9. The
boundary has thirteen line-to-cube fields, three line-to-plane fields,
one zero-to-cube field and three zero-to-plane fields. Its invariant total
paid rank mass is 13*2+3+3+3*2 = 38. The optimistic direct-endpoint profile
would be {H1:3,H2:16,H3:1}, but it is not realizable under this contract.

This enlarged boundary differs from the previous eight-field
one. It has four zero-start fields, and several old plane exits have become
cubes. In particular the old two-input/one-carrier lemma cannot simply be
transferred. The proof below uses the freshly extracted twenty-field matrix
and complete new frame intervals.

## Why rational row equality is the right local condition

Under the inherited native chart contract, a climb preserves its formal
row while changing the invertible chart map; a coframed ADD/SCALE applies its
rational elementary matrix to the formal rows. Therefore a legal warp-free
window with transfer matrix T has physical map

    G_exit (T tensor I) G_entry^{-1}.

With fixed boundary charts, equality of T is necessary and sufficient for
exact local equality at every positive width in that native model. Exterior
scalar coefficients are not raised to the width. This assertion does not
admit new unproved physical primitives or replace absolute-phase validation
where it is required. It states the source semantics used for this local
obstruction. A modified window containing warps would need labelled
operator rows or additional protected boundaries.

Restoring all twenty rows and charts at event 9137 preserves the unchanged
continuation by composition. The first cached-centre copy is later, at
11207; all eight cached copies and all eight zero retags lie after this
boundary. No fresh full caller or physical phase replay is claimed here.

## Frame-path coverage

A field's strict frame path is the chain remaining after suppressing time
spent doing scalar operations at one frame. Every possible path lies in the
finite subspace interval [entry,exit]. The complete path counts are:

- line to plane: one;
- line to cube: four, consisting of a direct jump or one of the three
  intermediate planes containing the entry line;
- zero to plane: four, a direct jump or one of the three lines;
- zero to cube: 36, consisting of one direct jump, seven line-only paths,
  seven plane-only paths and 21 complete flags.

Consequently the full domain has

    4^13 * 36 * 4^3 = 154,618,822,656

path assignments. This is a finite coverage count, not a claim that that
many programs were executed. Scalar programs are not enumerated: the
necessary conditions below apply to every factorization on a given path
assignment.

## Soundness of the optimistic station model

Make a vertex for each actual binary subspace visited by a path. For each
field ascent E -> F, add one directed edge E -> F of unit field capacity.
Parallel edges from different fields retain their multiplicity. All vertices
with the same subspace are merged. Grant unrestricted linear mixing and
storage at each resulting vertex, ignoring chronological overlap and
invertibility constraints.

This graph is an optimistic relaxation. A legal ADD/SCALE can only change
coefficients among values at the same vertex; every change of frame occurs
along an actual field edge. Merging visits that do not occur simultaneously
can add possible communication but cannot remove one. Each strictly ascending
edge is traversed once by its field and carries one whole-field value. No
field returns to that earlier frame. Repeated reads, in-place updates and
fanout at a station do not transmit a second independent value through an
edge already traversed.

Two necessary conditions follow.

**Reachability.** If T[o,i] is nonzero, there must be a directed path from
input i's entry station to output o's exit station. A linear coefficient
cannot appear at a station unreachable from its source.

**Cut rank.** Choose input columns I and output rows O. If deleting a set
of ascent edges disconnects every selected input station from every selected
output station, then

    rank_Q T[O,I] <= sum of the deleted edge capacities.

To see this, set all other entering values to zero. The chosen outputs can
depend on the selected inputs only through the values on the removed edges.
Their joint information dimension is at most one field capacity per edge.
Equivalently in formal rows their span has dimension at most the number of
edges, with multiplicity. The graph is acyclic because every edge strictly
increases dimension. Arbitrary mixing, feedback within a station, temporary
bases and repeated reads cannot increase that cut dimension. At physical
field capacity N the two sides simply acquire a common factor N.

These conditions are only necessary. A path assignment that passes them is
not automatically implementable. The final survivor below is known to be
implementable because it is the original checked scalar word.

## Domain pruning and the remaining exact certificates

Initially give each field every strict path in its complete interval. To
test one candidate path p for one field, fix that field to p and take the
union of the edges from every currently allowed path for each other field.
This union can contain mutually incompatible choices, and is therefore an
even more permissive reachability relaxation. If a required nonzero matrix
entry has no path in this union, p occurs in no feasible completion.

Deleting such a path is sound. Inductively, earlier deletions have already
preserved every feasible complete assignment. A later union of the surviving
domains still contains every actual field edge of every remaining feasible
assignment. Thus domain pruning does not assume a fixed scalar circuit or
discard a solution because of an unfavorable choice of other paths.

There are 68 certified deletions. They leave only four non-singleton domains:
roles 293 and 295 have four paths each, role 300 has seven, and role 302 has
four. The exact remaining Cartesian product has 4*4*7*4 = **448** members.

All 448 members are then handled separately:

- 315 have a required nonzero entry with no directed path even for that
  assignment's optimistic merged stations;
- 132 have an explicit cut whose capacity is below the exact rational rank
  of the required matrix minor;
- one survives, with exactly the retained frame chain on every field.

The independent audit does not trust a max-flow solver to establish the
cut claims. It recomputes every minor rank, verifies every listed cut edge
and its complete parallel-edge capacity, deletes those edges, and checks
disconnection between every selected source and sink. It also checks that
the 447 rejected assignments are distinct, belong to the reconstructed
remaining Cartesian product, and leave exactly the original assignment.

The source assignment uses 38 H1 climbs. Thus every exact factorization in
the stated model must use those same strict per-field frame chains and has
the same paid profile. The floor is attained, and the normalized moment is
38 for every 0 < t < 1. This conclusion concerns arbitrary legal scalar
factorizations, not merely the scalar programs attempted during discovery.

## Reproduction and independent evidence

The primary verifier emits the source-bound certificate `RESULT.json`.
The independently authored `check_certificate.py` validates this sibling
certificate by default, with the repository root resolved from the package
location. Optional `--repo` and `--certificate` flags support separate
read-only audit locations.

`check_certificate.py` imports no search code. It
independently extracts the source matrix, frames and invoice; enumerates
subspaces by spans of every subset of each terminal space; and validates
all coverage and rejection certificates directly. Its observed normal run
took less than one second under CPython 3.13. Three semantic controls run the
actual checker on altered certificates: deleting a rejection exposes a
coverage gap, changing a cut capacity fails the source edge count, and
changing a target rank fails exact minor reconstruction. Normal output is a
concise PASS receipt; `--json` provides the source hashes and detailed
checks. The result is
`PASS_INDEPENDENT_TWENTY_FIELD_PATH_CERTIFICATE`. No whole-provider, selected
cold, compiler, outer, Lean or Docker replay was run for this audit.

This is an exact finite certificate combined with the written station/cut
lemmas. It is not a proof-assistant certificate or independent human review.

## What a further change would have to alter

Reassociation, changes of basis, different intermediate binary subspaces,
and different scalar chronology within this boundary cannot improve the
paid profile. Another attempt must change at least one actual hypothesis:
for example an entry/exit chart or target interface, a transport or warp,
or the field/capacity contract with a fully paid producer and consumer.
Adding one H1 to save one H1+H1 -> H2 merge is already unprofitable, since
the saving 2-2^t is less than one for 0<t<1. Such a change needs an additional
compensating saving. A larger boundary remains untested and is not silently
authorized by this negative result.

Credit the native source and retained compiler lineage, Cao Yifan's word,
Dillon's coupled provider, Ali Romman's cached-centre relations,
Clear1nsight's selected completion and source validation, and GamingPuzzled's
PR5465 bottleneck analysis. PR5471 supplies the smaller-boundary predecessor;
its proof is not a premise of this enlarged-boundary result. Prepared by
apoursh with substantial OpenAI Codex assistance from separate discovery and
audit workers. Apache-2.0. No priority claim is made for elementary rank-cut
arguments.
