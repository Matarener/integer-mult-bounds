# Scalar-cone terminal restrictions at fixed native interfaces

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.

## Scope and changed contract

The source is both PR3945 provider words at immutable head
`91f81d131252db704f945891da1ea54e29d46b8b`. The previous PR3988
obstruction fixes all interior frames. Here interior **scalar** frames in A, B and restore may
shrink, together with one protected terminal. Precondition, compensation and
cut operations stay fixed. The literal graph, coefficients,
entrance frames, target and centre checks, native entry/exit frames, removed
registers and 91 protected dirty-buffer identities remain fixed.

The finite domain chooses every codimension-one subspace of each protected
terminal and propagates its restriction backward through scalar dependencies.
Each scalar frame is constrained to be a subspace of its original frame.
Only the greatest frames forced by this propagation are priced; other optional
shrinks, rotations outside the incumbent frames, simultaneous terminal changes,
changed graph/native/check boundaries and global scalar optimization are outside
this result. No κ improvement is claimed.

This is one changed-boundary experiment, followed by its permitted mechanism
pivot. The smallest one-gate test already yielded only five exact ties. Allowing
the entire forced scalar dependency cone did not add a feasible candidate.

## Exact finite domain

Represent a binary subspace of F2^9 by its 512-bit point-set mask. Intersection
is bitwise AND; containment is exact. For a d-dimensional terminal with ordered
basis b_0,...,b_(d-1), every nonzero linear functional has one kernel hyperplane.
Over F2 there is no nontrivial scalar equivalence, so the 2^d−1 nonzero functionals
enumerate every hyperplane once. For a functional with pivot p, its kernel basis
consists of b_j + ell_j b_p for j≠p. The checker verifies cardinality, uniqueness,
containment and dimension for every generated subspace.

The chronological trace represents scalar ADD by one common frame variable
shared by its two registers and SCALE by one variable. Native maps introduce
fixed exit anchors. Entrance anchors are fixed. Required target/centre/native
entry checks force the immediately preceding scalar frame to retain its original
value: that value already equals the check boundary in the source. The trace is
adapted from the retained retiming implementation, and its source histogram is
compared with the retained frame auditor; this is **not** claimed as an independent
implementation of those predecessors.

For a chosen terminal hyperplane T, restrict its last scalar frame U to U∩T.
If a scalar predecessor P is not contained in a restricted successor C, restrict
P to P∩C and revisit its own predecessors. Reaching an immutable anchor outside
C rejects the candidate. Restricting a frame required by a fixed check rejects
it. Otherwise the process terminates: every strict restriction lowers a finite
frame dimension, and all constraints are intersections.

The result is the greatest feasible assignment below the original frame caps.
Every feasible assignment lies below each intermediate cap by induction, so
rejection at a fixed anchor or check is conclusive for this domain. Success
satisfies every incoming containment constraint; unchanged downstream frames
still contain the restricted predecessors. This establishes feasibility, not
moment optimality among additional optional interior restrictions.

## Exact census on both providers

Each provider has 13,285 terminal hyperplanes, partitioned as follows:

| Outcome | Count |
| --- | ---: |
| Terminal would not contain its fixed entrance | 2,688 |
| Forced cone reaches incompatible fixed entrance/native exit | 10,023 |
| Forced cone would alter a scalar frame fixed by a check | 552 |
| Already fits final scalar frame: credited PR3988 direct refund | 17 |
| Feasible changed scalar cone | 5 |

The five survivors are identical for the two providers:

| Helper | B-section index (zero based) | Interior operation |
| --- | ---: | --- |
| 282 | 535 | SCALE −1 |
| 293 | 554 | SCALE −1 |
| 298 | 559 | SCALE −1 |
| 309 | 580 | SCALE −1 |
| 373 | 682 | SCALE −1 |

Each cone changes exactly this scalar frame and its matching terminal. The exact
new bases and guarded old frames appear in RESULT.json. Each deletes one paid
H1, changes one width5 helper to width4, and preserves all other paid ranks.
The source profile is {1:2482,2:712,3:218,4:109,5:20,8:8}; the new profile lowers
only the first multiplicity to2481. The width inventory changes from
{5:28,6:18,7:53,8:96,9:213} to {4:1,5:27,6:18,7:53,8:96,9:213}.

## Complete optimistic owner budget

Use the exact PR3945 endpoint k=1730663236534549309146/10^24 and h(r)=r^(1−k).
Its source convention r(73/r)^k has the same positive common factor73^k.
The credited PR3815/3862/3890 packing dual, rechecked at this endpoint in PR3988,
has q=(h(48)−h(3)−5h(5))/20, pi_w=−h(5)−(w−5)q for5≤w≤9,
and pi_4=1−h(5). Bin prices are mu8=−pi8, mu16=−2pi8,
mu32=−4pi8 and mu48=h48.

For every capacity8,16,32,48 and every width4..9 packing pattern with idle t,
the checker proves h(t)−mu_cap−sum n_w*pi_w≥0. All2,551 patterns are covered:
12 symbolic equalities and2,539 strict rational interval inequalities. The
interval implementation is adapted from PR3988 and uses exact rational bounds
for logarithms/exponentials; it is not a new independent numerical audit.

The frozen actual incumbent pattern counts attain this dual. The checker checks
all aggregate capacities, bin totals and demands against the current408-role
inventory across3,240 calls. Literal owner chronology and source authenticity of
that aggregate are inherited from PR3969/3988; they are not replayed here.

Replacing width5 by width4 changes the dual lower bound on owner idle cost by
pi4−pi5=1=h(1), exactly. Therefore even **arbitrary fractional repacking** must
pay at least the H1 saved inside each surviving module:

    local delta −H1 + owner lower-bound debit +H1 = 0.

This is a lower bound on after-minus-before cost, so nonnegative means no gain.
The bound is optimistic: actual chronological owner restrictions can only add
cost. No new owner realization, supplier root or κ is asserted, and no owner
search is needed after the complete optimistic bill fails. At3,240 uses the
local reduction is3,240 H1 and the owner debit is at least3,240 H1.

## Dirty semantics and limits

For all ten literal provider/candidate words, apply only the declared frame
edits, regenerate cleanup, and run the retained exact forward and dual
arbitrary-dirty checks plus cleanup-boundary check. Cleanup bytes remain exactly
unchanged; all91 protected buffer identities remain present. Native matrices,
frames and phases are not modified. Replaying the predecessor checker is
explicitly credited and does not imply a fresh independent audit of it.

The positive control verifies a literal witness; rejection controls exercise an
invalid scalar frame, a sign mutation breaking arbitrary-dirty semantics,
an omitted owner debit, and changed pinned source bytes. Optimized execution
must reject too. Unknown physical conversion, native compilation, precision,
stock/tape, uniformity, outer, analytic and BIT obligations are not priced as
zero. The construction stopped at the failed optimistic allowance.

A useful next contract changes a pinned native/check boundary or the literal
graph, or supplies a distinct interior-saving mechanism whose complete allowance
is favorable before search. This result does not close those tasks or PR3945's
joint native/scalar refits.
