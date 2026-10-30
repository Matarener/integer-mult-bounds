# Relative rounded-trace transfer for streamed QQ16 recovery

This proves a compiler-style relative statement about the complete retained
PR3985 and PR4015 words. It does not infer a numerical decoder certificate from
the producer certificate. Source identities and credit are in PREDECESSORS.json
and SOURCES.json. No predecessor executable is imported or rerun.

## Result and concrete obligation removed

The 3,935-event materialized word and 3,813-event hosted streaming word have
exactly the same 3,392 value-producing event expressions, including occurrence
multiplicity: 2,816 ordered scalar ADDs, 352 cover maps and 224 signed native
calls. All 224 final output expression roots match. The inverse-B1 checkpoint
matches at old event2852 / new event2730. The sequence of native labels, signs
and input expressions also matches in order.

The comparison does not cancel inverses, commute cover maps, reassociate sums,
replace a rounded operation by exact arithmetic, or compare numerical samples.
It interns structural tuples by exact equality; hashes only record evidence.
The complete old-to-new event mapping is in RESULT.json. Thus the streaming
change does not create another set of arithmetic-error or intermediate-value
expressions. Under the contract below, a valid certificate for the materialized
word transfers to the streamed word without a new rescheduling-error term or
an additional range analysis of those same arithmetic expressions.

This removes a *duplicate proof obligation*, not an arithmetic operation or an
already established error reserve. There are zero eliminated ADD/map/native
rounding sites. PR3985 itself explicitly leaves numerical defects open.
A valid finite-format/range/error certificate for that decoder is still needed.

## Explicit finite-storage and primitive contract

Let every logical field be an array on the actual common owner/payload domain;
the argument applies to every positive tensor depth and does not enumerate that
domain. Native and cover tags retain their actual port, stage and sign. Supply:

1. A common finite value representation for all paired roles, including the
   old private F accumulators, the old D copies, the new persistent Q roles and
   reusable D, and the output banks that host them. One concrete permitted
   representation has signed W-bit real/imaginary integers in a common binary
   quantum q. Signed zero, exceptional values and overflow conventions must
   also agree if the chosen format has them.
2. CLEAR writes the same exact zero bit pattern independently of prior dirt.
   Plain loads, stores, copies within an arithmetic primitive, and retention
   across native calls preserve those bits. Moving private F into persistent Q
   must not introduce an extra store-round, narrowing conversion or rescaling.
3. For each scalar coefficient c in {1,-1,1/4,-1/4}, ADD is the *same ordered
   deterministic function* of the prior destination and source in both words.
   For example, it may separately round the product c*s, then add to d and
   round/store the result, with one fixed signed division and overflow policy.
   A fused multiply-add and a separately rounded product/add are different
   contracts. Division by four is not silently made exact.
4. Each tagged cover map and signed native call is the same deterministic
   whole-array function with the same internal arithmetic sequence, precision,
   factor order, coefficients and wrapper recipe in the two executions. This
   includes every native interior, coordinate permutation and signed operation;
   it is not merely equality of the ideal unitary operator.
5. A native call's scratch is disjoint from live query/output banks. Its
   entrance protocol removes dependence on disposable dirt, and its specified
   zero-return state is restored. There is no unmodelled shared accumulator,
   global random stream, sticky-state-dependent rounding, clock/address-dependent
   result, or concurrent external reader of temporary output-bank contents.
   Reordering independent calls/ADDs is allowed only under this isolation.

These premises allow signed-floor, truncation, nearest rounding, deterministic
saturation or modular overflow, provided the paired operations use the same
rules. Bit equality under overflowing arithmetic is not an accuracy theorem.
For a trapping implementation, the matched dataflow expressions have the same
potential traps; the theorem below concerns executions where all required
operations are defined. The first trap in chronological order need not match.

If a real kernel uses variable widths, it is enough to assign equal complete
primitive implementations to each paired event; a common W/q is a simple
sufficient condition. That assignment must also cover persistent stores and
native internal widths. The finite words do not supply it themselves.

## Structural proof and storage safety

Use an arena of terms. Initial borrowed inputs have distinct symbols X_p,Y_p.
An initialized zero field has the single common zero term. An ADD creates
`ADD(format,c,old_destination,source)`; a cover creates
`MAP(format,stage,p,inverse,input)`; a native creates
`LINE(format,p,sign,input)`. No algebraic identities are imposed on these
constructors. Each term denotes its entire array, including every owner and
coordinate. Identical constructor terms denote identical bits by induction
under the deterministic primitive contract, regardless of interleaving with
unrelated terms. The same argument applies to every internal instruction of a
paired native call because its input bits and complete kernel are identical.

The new checker interprets both full words and validates the access discipline:
borrowed X/Y cannot be written or cleared; every arithmetic read has a live
initialized value; only owned fields or the active private scope can be written;
no native/map call occurs inside a private scope; every private scope returns
zero with an identity clear; all materialized D copies return zero/identity.
When a private scope ends its names cease to exist. Missing recycled-D clears,
premature query clears, missing deferred output copies and hidden private
workspace are rejecting controls. Thus matching roots does not assume that
aliased storage starts clean or that dead private fields survive implicitly.

The source trace records numerical arrays, with control frame tags preserved in
the source words. Legal native/chart/frame identities were checked in the
predecessors and remain inherited. This relative audit does not repeat their
73-coordinate phase proof or claim a new physical owner-layout construction.

For the future query, let t_p be the output of the source copy, map and negative
native call for p in the ordered 104-port U+T list. Both words compute, for each
k, the same left-associated chain starting at zero and visiting the same
nonzero coefficients R[k,p] in the same p order. The old outer loop is k; the
new outer loop is p. Different k chains have no dependencies on one another.
The eight response chains similarly retain k order and the same quarter ADDs,
positive native, inverse map and addition to W_A. Reusing D changes its storage
name, not the input or evaluation order of any term.

The nine deferred Z_U definitions are independent initial CLEAR/X-copy pairs.
The streamed word first uses their storage for Q0..Q7,D, then performs the
same nine paid definitions at events2600..2617 before any preserved Z update
(first at2618). The full trace checks this by reads and output dependencies;
no equality is obtained by erasing an observable output value. The 120 removed
CLEARs and one removed begin/end pair have no value-producing counterpart to
match. Their effects are initialization/retirement of dead roles, not new
rounding events or a claim of physically free cleanup.

Inductively evaluate the shared term arena. Every paired arithmetic expression
has equal arguments and equal output bits. The complete occurrence multiset
check supplies an event bijection even when two equal terms were recomputed.
All final output roots and the intermediate checkpoint agree. Initial borrowed
states are untouched. This proves the relative bit-equivalence theorem and
transfers every bound on matched intermediate arithmetic values or decoder
output error, once its actual finite-primitive premises are supplied.

This is a dependency-trace equivalence, not equality of the global chronological
trace, wall-clock behavior, tape-head movements, simultaneous storage peaks,
physical addresses, or observable intermediate output-bank contents.

## Discriminating finite-format controls

The actual first two nonzero future F0-query contributions are

```
old2140: F0 += D2        new1716: Z1 += Z10
old2141: F0 += D9        new1764: Z1 += Z10
```

At this *query boundary*, choose the two aligned source components as3 and1,
with a four-bit old private accumulator and a three-bit new owned accumulator.
The first addition gives3 in both. The second gives4 in the old accumulator;
the new one traps, wraps to-4, or saturates to3 according to its policy. This is
an actual source-site format counterexample, not an asserted reachable full
producer trajectory or a failure of PR4015 under its missing format premise.

At old2563 and its mapped new event, the literal instruction is the response
coefficient-1/4 applied to F0/Q0. With query component1 and initial response0,
signed floor gives-1 whereas truncation toward zero gives0. A common signed
floor policy agrees in both schedules; a storage-dependent change does not.
The test compares negative-quarter decisions and overflow handling against an
independent exact-rational/two's-complement oracle. Reordering the source loop
also fails the symbolic DAG check, even when exact commutative arithmetic
would permit that reordering.

A second countermodel isolates hidden state: the second native call, port1
with positive sign, occurs at old9/new7 after respectively4 and3 scalar ADDs.
A kernel adding the parity of that hidden global count returns different bits
on equal declared inputs. This is not an observed actual-kernel defect; it
demonstrates why even matching the native call sequence is insufficient
without declared-input determinism.

Native scratch isolation is separately indispensable: a kernel that reads a
live query bank through shared scratch is not a function of its declared input.
The new schedule keeps owned queries alive across112 future native calls;
the old query-private scope begins after104 source natives. Hence old private
scratch permission cannot be reused for those new owned query slots. The
checker rejects a private scope spanning a native call, while the physical
non-alias proof is an actual caller obligation.

## Binding the available precision results

The authenticated canonical PR3303 proof, independently checked by ToikY's
retained PR3652 proof, gives for the *literal producer F0 then B1*:

```
q = h*2^(-71-19*(lambda-1))
W = P+215+38*(lambda-1).
```

Its domain is all704 persistent entry fields in h Z with component magnitudes
strictly below2^P h; eight private fields begin zero. It bounds53,118 producer
events and native/product interiors. Every required division is exactly
divisible, so no rounding or overflow occurs for that producer reference.
It explicitly excludes F17 consumption. Neither its grid exponent nor its
width statement is a decoder-interior bound. The first absent format fact for
this transfer is the paired decoder primitive/retention assignment, especially
old private F_k versus persistent hosted Q_k. Even adopting its global q/W
would require proving the decoder intermediates fit and its divisions obey the
chosen finite lowering; the producer's completed output is only the input.

PR3932's first F0-child audit shows why an unchanged coarse grid is unsafe and
why the finer PR3303 format conditionally repairs that *first producer child*.
It does not supply the new decoder format. The canonical concrete native-rounding
package likewise exhibits genuine producer rounding under its different
binary64 contract; that observation is adjacent, not rerun or transferred here.

The authenticated PR2965 README states the completed-output implication
`49 epsF + 1923 epsB + epsD`. Its epsD must bound the implemented decoder against
the ideal inverse. Its use of the older PR2736 state-relative theorem concerns
the fixed PR2707 decoder, not an automatic certificate for PR3985's changed
rectangular word. The present result shows that once epsD is valid for a paired
finite implementation of PR3985, the same epsD is valid for PR4015. It does not
establish epsD, regenerate the old constants, or admit a supplied entry lattice.

## Decision and remaining obligations

Close the rescheduling-specific arithmetic-equivalence question under the
explicit contract. Do not optimize an isolated guard or claim a new kappa.
Next pin one actual paired finite decoder implementation: scalar product/add
rounding, native interior recipes/widths, persistent query-store representation
and scratch disjointness. Prove its range/error certificate once on the shared
DAG and transfer it. Caller entry format, owned output banks, physical movement,
helper return, recursion and productive-family coverage remain additional
obligations. Unknown costs are not zero. No physical tariff is altered here.

Credit Chris R / Clear1nsight PR3985/4015; ywz65 PR2707; Arham Tahir PR2681;
Ali Romman and the retained QQ16/native/geometry lineage; Nick Petalas PR3303,
PR2965 and numerical predecessors; ToikY PR3652. Substantial OpenAI Codex
assistance, no independent human or formal-kernel review. Apache-2.0.
