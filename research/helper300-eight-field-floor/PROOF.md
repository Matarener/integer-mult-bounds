# Exact ten-H1 floor for one eight-field backward block

This is a local mathematical obstruction, not an improved kappa or a
complete multiplication theorem. It concerns arbitrary ADD/SCALE
refactorizations in the fixed eight-field, monotone-frame, no-warp model
specified below. It is stronger than an adjacent-swap failure, but is not a
barrier to a larger native redesign.

## Sources and exact interval

Canonical repository checkpoint: `32890bc5de034ab8fc93ac88ead7279a6a416d04`.

Actual backward provider:

`research/coupled-helper-neutral-completion/capsule/workspace/swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/WORD.json.gz`

- Container SHA256: `7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc`.
- Decompressed payload SHA256: `05490717144b3e6c69c0cc9e5c5df5c69d841ca13bf29aabd1b0db180628f038`.
- Its source payload pin is `cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.

That source payload is the decompressed
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, also copied as
`.../repository/research/native-center-free-code/SOURCE-WORD.json.gz` in
the selected capsule. Both compressed copies have SHA256
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`.

The interval is **[9044, 9116)**, with zero-based native event indices.
Starting from roles {19,300,301}, its exact closure under every scalar
contact inside this interval is

`[19,40,288,289,295,299,300,301]`.

It contains no warp, cache COPY, owned CLEAR, or zero retag on these roles.
Every instruction inside the interval that touches a role in this set touches
only roles in this set. Thus the intervening other-role instructions commute
with an isolated replacement of the block. The emitted `RESULT.json`
contains every retained event and the exact rational matrix.

The fixed boundary charts are:

| Role | Entry frame | Exit frame |
|---|---:|---:|
|19|21|423|
|40|42|422|
|288|103|422|
|289|103|423|
|295|57|430|
|299|42|419|
|300|0|430|
|301|0|419|

Frame 0 is the zero subspace. Frames 21,42,57,103 are lines. The four exit
frames 419,422,423,430 are pairwise distinct planes in F_2^9.
In particular 419=span(273,51), 423=span(273,102), and
430=span(273,85). All fixed entry frames lie in their respective exit planes.

The source block uses exactly ten rank-one climbs, so has paid cost 10 in
the normalized moment sum. This statement is about this isolated block,
not the complete local provider invoice.

## Replacement model

A replacement uses exactly these eight whole fields, with independent
arbitrary entering values, and the same field capacities and boundary charts.
It may use any finite number of rational scalar ADD and nonzero SCALE gates,
any coefficients, any order, and any temporary basis changes. ADD operands
must occupy the identical actual frame. It may choose any intermediate
binary subspaces, not merely frames appearing in the source catalogue.
Every field's frame moves by strict nested ascent from its entry to its fixed
exit. A paid climb from E to F has positive integer rank dim(F)-dim(E).

No auxiliary field, new warp, descent, chart-changing exchange, cross-column conversion, new input
relation, or changed boundary is permitted. No approximation or packing of
multiple arbitrary fields into a field of smaller capacity is permitted.
These are explicit restrictions of this small optimization instance.

Since each final frame is a plane, an intermediate frame for that field is
a subspace of that plane. A field at one exit plane cannot later contact a
field whose exit plane is different: equal frames at such a contact would
force the different plane to contain the first plane, impossible in dimension
two. This fact is independent of the ordering or scalar coefficients.

## Exact local identity criterion

Use the repository's native chart semantics: a climb changes a field's chart
and preserves its formal row; a coframed ADD/SCALE acts on those rows by its
ordinary rational elementary matrix. This is the convention explicitly used
by `research/kappa-rebuild/complex/native_extensions.py:84-142`.

In a warp-free window, let G_E and G_F be the block diagonal invertible chart
maps at entry and exit. A legal scalar factorization with rational transfer
matrix T induces the physical map

    G_F (T tensor I) G_E^{-1}.

Consequently, with the same boundary charts, equality of rational transfer
matrices is necessary and sufficient for exact local physical equality at
every positive width under the inherited native chart contract. Scalar
coefficients remain exterior coefficients; they are not raised to the width.
This conclusion does not excuse checking frame legality or admitting a new
physical primitive. It also does not apply to an unmodelled warp: such a
window would require its operator labels and phases, or segmentation at the
warp boundaries, instead of an unlabelled rational matrix.

There is no hidden zero-input assumption. The actual native prefix through
event 9043 consists only of invertible persistent ADD/SCALE, warp and climb
operations, plus annotations. The source audit checks that there is no
destructive scalar operation in this prefix. Under the inherited native
contract, each of its warps and climbs is invertible. Thus all 632 persistent
values at this cut can vary arbitrarily; in particular these eight values are
independent. The provider's exterior input basis and monomial/scalar wrappers
are themselves invertible and do not impose an input relation.

## A two-input, one-carrier lemma

Consider two independent entering field values a,b, initially the only fields
at the zero frame. Assume one of them jumps directly from zero to its final
plane P. Call it the direct field, allowing any prior changes of basis between
the two zero-frame fields.

Then the collection of outputs on fields whose final plane differs from P
has dependence of rank at most one on (a,b) in formal scalar-row coordinates.
Equivalently, its physical rank on these two full input fields is at most one
field's capacity.

Proof. Before either zero-frame field leaves zero, only those two fields can
interact with a or b: all other fields start at nonzero frames and cannot
descend. Arbitrary scalar operations at zero may replace a,b by arbitrary
linear combinations. Once one of these two fields departs zero it cannot
return. The direct field never visits an intermediate line; after its jump
to P, it can contact only fields whose final plane is P. Such fields also
cannot carry a subsequent message to another exit plane once they have
reached P. Thus all dependence of the other exit-plane outputs on (a,b)
must pass through the *other* zero-frame field at its single departure from
zero. At that moment it holds one linear combination alpha*a+beta*b.
Subsequent ADD/SCALE operations and legal climbs can distribute or cancel
this value but cannot create a second independent dependence on (a,b).
This reasoning permits feedback, arbitrarily many scalar gates, either
departure order, and arbitrary initial temporary bases. End proof.

The conclusion fails if extra zero-frame fields, descending transport,
new inter-plane warps, or modified final planes are admitted. They are
outside this lemma's use here.

## Applying the lemma to both potential H2 replacements

Let a and b denote the entering values of roles 300 and 301. In the exact
backward transfer matrix, the following coefficients on (a,b) occur:

| Output | Final plane | Coefficient row on (a,b) |
|---|---:|---|
|19|423|(0,1)|
|300|430|(1,0)|
|301|419|(-1,-1)|

Other entering values occur in these outputs but do not affect this rank
calculation. These three rows can be read directly from the exact eight-field
matrix in `RESULT.json`.

If role 300 jumped directly 0 -> 430, outputs 19 and 301 are outside plane
430, and their two coefficient rows have determinant 1. Their dependence on
(a,b) therefore has rank two, contradicting the lemma's rank-one bound.

If role 301 jumped directly 0 -> 419, outputs 19 and 300 are outside plane
419; their two coefficient rows have determinant -1. Again rank two
contradicts the lemma.

Hence neither zero-start role may make a direct rank-two climb in an exact
replacement. Each must visit a line and use two rank-one climbs. Each of the
other six roles starts at a line and ends at a plane, so requires one rank-one
climb. The total cost is therefore at least

    2 + 2 + 6 = 10 H1.

The original block attains this cost. The minimum is exactly ten H1 for
every exponent 0 < t < 1, not merely for a sampled value of t. In fact the
rank-count statement itself is independent of t. There is no positive
recursive moment saving in this fixed-boundary, eight-field model.

## Protected interfaces and limitations

Restoring all eight rows and frames at event 9116 preserves every later
instruction, including the cached-centre copies at source event indices
11207,11222,11237,11252,11267,11282,11297,11322. Their sources and frames are
listed in `RESULT.json`, as are all eight later exact-zero retags. This is
a compositional statement, not a fresh full cached-centre or phase replay.

The illustrative h300 motif in PR5465 is forward-oriented. Its x19-to-plane430
coefficient is not a valid backward witness: the actual backward outputs at
plane430 have no x19 coefficient. The rank-two witnesses above use the actual
selected backward tape and remain valid under arbitrary initial bases.

This does not rule out a rewrite extending past the chosen boundary. The
same seed's closure in [9044,9137) has twenty fields, not eight. Other routes
include auxiliary fields with their complete bill, changed warps or charts,
a larger helper factorization, or a genuinely changed caller interface.
No global optimality, whole-provider lower bound, improved kappa, compiler
funding, or formal-kernel acceptance is claimed.

## Evidence and predecessor credit

`verify.py` and the separately authored `check_window.py` independently read
the frozen inputs and compute the small rational matrix, fixed boundary frames,
source paid histogram, closed role set and source bindings. The primary checker
also records the prefix grammar and later cache checkpoints. Both run read-only
against the repository by default; the primary checker compares its recomputed
certificate with `RESULT.json`.
The executable computation is finite exact evidence. The carrier lemma and
the resulting arbitrary-factorization floor are the written mathematical
argument above, not an exhaustive program enumeration or proof-assistant
result.

Credit Cao Yifan's native word, Dillon's coupled provider, the cached-centre
relations of Ali Romman, the selected completion and source validation of
Clear1nsight, and the native/compiler lineage retained in those sources.
PR5465 (`b123ff44a211b9fc96b9f8fd1538e9965a95b34e`), especially R13 sections
3-4, supplied the h300 bottleneck and motivation to go beyond one-step swaps.
This note is an independent AI-assisted local mathematical audit and does not
claim independent human review or priority for elementary cut-rank arguments.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
