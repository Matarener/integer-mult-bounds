# Current R437 whole-word audit and inherited conditional simulation

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.

## Predecessor and added coverage

Nick Petalas's PR2989, head `133cd8a7c5ce16a3d66e3372c5fdd9e88067d75b`,
already proves the conditional whole-word ordering lemma, supplies exact
abstract-packet differential checks, and exhibits the omitted owner/self-bridge
admission guards. Its canonical package is `research/physical-compiler-correspondence`.
The lemma and owner-guard discussion below are an explicit current-source
restatement/adaptation, **not a new theorem or discovery of the guard gap**.
The added executable coverage is the complete current R437/OQ4 source event
skeleton (903456 residual sites, 288 calls and 29 global checkpoints at one formal
low), complete local/family XOR trace, disposal checks, and the unchanged
Machine.run continuation loop. The predecessor checked eight smaller GL2(F3)
abstract words, 67024 instructions and 8064 residual boundaries. These are
complementary domains; neither check admits physical primitive contracts.

## Result and exact boundary

Fix the compiler `macro_code.compile_node`, dispatcher `Machine.dispatch` and
loop `Machine.run` at canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Let `Driver` denote the retained
PR2753 logical driver in that tree. The theorem below proves the concrete
whole-word translation clauses. It does **not** assume that compilation itself
preserves the source; that is the implication established here. It assumes
specified lower-level packet/residual and recursive-cut contracts, rather than
claiming their uniform physical proof.

**Theorem (successful-run functional refinement).** For a finite admitted source
topology and finite low-class enumeration, suppose conditions A–F below hold.
The code emitted by `compile_node`, executed by `Machine.run`, has the same
ordered complete-packet transformations, final family contents, row/prefix
ordinals and private-COPY lifetime as `Driver.global_word`. The result holds for
arbitrary initial Boolean functions on all family packets, including arbitrary
correlations and dirt; there is no zero-dirt or named-dirt restriction. Source
input preservation and scratch restoration hold to the extent required by B–F.
There is no claim of transactional recovery from malformed or interrupted runs.

A. **Admitted source.** The topology has the declared finite schedule, calls,
owner lists and request identifiers. `LocalState.accept/finish` succeeds on each
literal word. Bridge endpoints are distinct and the source frame requirements
hold. Each local call's pairs `(owner.family, native_low)` are distinct. The
source's low enumerator is complete and in its declared order; it is replayable
at each loop site. The request compiler is deterministic at a fixed
`(identifier, common, low, mode)`.

B. **Packet primitives.** Gather returns the complete selected packet and leaves
the family unchanged. Route implements its declared row/address permutation and
preserves its input. Scatter replaces the specified low packet in the *current*
family, leaves its other packets unchanged, and returns an owned family.
XOR returns the complete pointwise XOR, retaining both inputs. Copy retains its
source, transfer consumes its source into its destination, and clear erases its
owned complete packet. Equal encoded prefix values retain distinct physical
ordinals. These statements concern full packets, including all high lifts,
spectators, rows, prefix occurrences and input dirt.

C. **Residual block composition.** For each binding, the ordered `Cursor` blocks
(or the stated axis specialization) implement precisely the logical
`consumer.apply` residual on its complete packet. Its declared source label,
weight program, low/high fields and common/native header are those at that call
site. It preserves the required borrowed inputs and restores its scratch.
This premise includes the good and fallback algebra, coefficients and leaf
primitives; the test's opaque residual symbol is not evidence for C.

D. **Recursive cut.** A nonterminal block supplies the complete legal child
capsule; CALL saves the successor instruction, restores the exact parent state
on return, and substitutes only the completed child result into `current`.
The child satisfies this theorem at strictly smaller width. Original-width
stock, legal history, numerical capacity and source identity are hypotheses of
this cut, not consequences of the dispatcher theorem.

E. **Node/return.** NODE validates and peels the root input and splits its complete
fresh-row packet into the family representation used by `Driver`. MERGE_RETURN
implements the inverse representation boundary and the declared complete
endpoint, preserving borrowed input ports. No unproved node/merge step is hidden
inside the symbolic comparison.

F. **Physical ownership.** Canonical roles, scratch roles, handoff ports, protected
output and numerical words obey their stated separation and parking contracts.
No live role is aliased to an overwritten scratch or input destination. Required
resource bounds permit successful execution. F is a semantic ownership premise;
it is not a zero-cost abstraction.

## The relation at boundaries

Let `F[f]` be the logical driver's current family packet and `M[family,f]` the
compiled role's packet. At a global checkpoint relate states by exact packet
content and physical ordinal equality for every family. In a local call extend
the relation with `buffers[i] = M[stage,i]`, with `private = len(owners)`.
A residual subrun relates its logical input to `M[current]`; its caller role is
retained until the completed result is transferred back. The retained source
role in a COPY interval is outside this mutable residual role. Inactive local
roles hold empty bodies.

This is a separation relation on named owned packets. It is also an algebraic
simulation: gather, route, scatter, residual and XOR can first be treated as
uninterpreted total operators satisfying their ownership interfaces. Substituting
actual Boolean packet operators into equal expressions preserves equality. The
argument therefore does not require independence of packet contents, linearity
of residuals, clean helper inputs or a distribution on dirt. Boolean linearity
is only needed to identify the final algebraic supplier endpoint, a separate
source theorem.

## Concrete emission and dispatch cases

**Initialization.** The first emitted instruction is NODE. By E it establishes
the family relation. The compiler's `staged_roles` is the maximum owner count
plus one private role, so all emitted stage labels exist. For current R437 this
number is 660, with ordinary roles 0–658 and private 659.

**Gather and route.** For each owner, the compiler calls the same
`compile_owner(topology.matrix(owner.chart), low, catalogue.codes)` as the
logical driver. It emits `gather_route(stage_i, family, native, forward)` and
retains `(family,native,backward)` for scatter. The dispatcher gathers from the
family, routes the complete selected packet and commits the owned result to
`stage_i`. The logical driver executes these same operators before entering the
literal word. A makes these independently owned packet selections admissible;
B and F preserve the family relation and establish every buffer relation.

**MOVE (opcode 0).** Both paths accept the literal event with the same
`LocalState`, then apply the same identified common-header residual to that
role. Compiler RESIDUAL_BEGIN copies the role to `current`; its blocks establish
C, using D for a nonterminal child; RESIDUAL_END transfers the completed result
back and clears directory/prefix work. The original role is overwritten only
by its completed result. This agrees with `changed = residual(buffers[role])`,
then clearing the old buffer and installing `changed`.

**XOR (opcode 1).** Both paths use the literal event's source `item[2]` and its
accepted destination. The dispatcher calls `xor_packet(source,target,...)` and
commits to the destination. The logical driver does the same. No complete-stream
term is dropped. The LocalState guard forbids changing the copied source while
its private interval is open. XOR sign ±1 has the same Boolean operation; source
admission still checks the signed literal field.

**COPY (opcode 2).** The compiler emits copy of the accepted source into
`copy_source`, residual on `copy_source`, then transfer into `stage_private`.
The dispatcher copy uses `commit(source,destination)`, retaining its source.
`residual_end` puts the completed result back into `copy_source`; move consumes
that result into the private role. This equals the logical clone followed by
residual into `buffers[private]` and final erasure of the clone. The original
source remains present throughout, with all arbitrary dirt. No equality between
the input and transformed copy is required. Readers consume exactly the complete
private result and do not rerun the child.

**ERASE (opcode 3).** Both paths first accept the same guarded source/private
versions and frames. The compiler clears private; the driver pops and clears its
private buffer. Thus erasure happens after the same final consumer and is part
of the completed invocation. It cannot be omitted merely because private is not
returned to a family.

**Scatter and final role cleanup.** After the same `state.finish`, both paths
visit roles in increasing order and route back with the retained backward map.
Crucially, each scatter reads the *latest* family state. This preserves changes
from earlier role scatters to other low packets of that family. The compiler's
clear of every ordinary and private stage role realizes the driver's `finally`
cleanup. A's packet distinctness ensures all intended returns coexist.

**IDLE.** The loop order is replica, source idle identifier, low. Both paths
perform gather, identified native-header residual, scatter into the latest
family, then clear the temporary. IDLE27776's rank26 and IDLE27777's rank42 are
current source labels. Their internal algebra remains C; it cannot be replaced
by the obsolete rank34 implementation because the surrounding word simulates.

**Bridge and exchange.** Both paths loop replica, port, then the two explicitly
ordered `(target,source,side)` pairs. Each complete family XOR sees the current
family. Exchange uses a single empty swap role: first→swap, second→first,
swap→second. B/F make this the same permutation as the driver's reference swap.
All relevant source checks, including distinct bridge endpoints, are in A.

Each case establishes the relation at its successor boundary, so induction on
local position, low ordinal, replica and schedule position proves every global
checkpoint and final family relation. This is a finite nested-loop induction;
no materialization of all GL64 lows is needed for the mathematical statement.
It does not establish that the supplied low enumeration or chart maps satisfy A.

## Residual suspension and the actual dispatch loop

For a good plan the actual Cursor emits `forward, good, backward`. For a fallback
plan it advances one source command at a time, emitting one sweep for ADD/sign,
and the three stages of a pair child in source order. The compiler advances the
cursor before emitting the block. After CALL the suspended caller resumes at
its saved successor instruction, not at the start of the residual. Contract C
identifies the concatenation of these blocks with the source residual; D
identifies each completed child substitution. No proof of the internal algebra
is inferred merely from these itinerary facts.

The actual `Machine.run` loop has three actions. `next` increments PC exactly
once; `jump` leaves the state established by CALL or RETURN; `done` exits. CALL
writes `self.pc + 1` into the parent header before setting child PC=0. Return
restores that stored PC before dispatch reports `jump`. Thus the first resumed
instruction is exactly the successor of the suspended block, with neither
re-execution nor skipping. Induct simultaneously on decreasing child width and
remaining finite instructions. Leaves use C; nonterminal blocks use the
smaller-width hypothesis plus D. The symbolic loop check executes the unchanged
run function with explicit cut-contract actions at depths 0,1,2,17; it tests the
loop composition and deliberately does not substitute for D's physical proof.

## An exact admission gap in the compiler interface

`Driver.local` rejects duplicate `(family,native)` owner pairs with
`disjoint complete owned low packets`. `compile_node` contains no corresponding
check. The verifier supplies a two-owner topology with identical family/chart
keys: the actual logical driver rejects it while the actual compiler emits a
word. Consequently **compiler success alone is not source admission**. This is
an interface precondition, not a counterexample to current R437 on admitted data.
The concurrent transport lane investigates the actual current owner separation
premise using a different chart entry with value ±1 or ±1/2 for each same-family
pair; see the submission's coordination record for its exact artifact/status.
This package remains valid if that separate result is not admitted: A stays an
explicit hypothesis.

## Scope of the executable evidence

The verifier extracts the pinned Driver, LocalState, compiler, Cursor and
Machine.dispatch AST nodes, without importing physical primitives. The compiler
has exactly one transparent test-only transformation: its append-only operation
list becomes an immediate ordered sink; the final tuple is empty because the
sink has already consumed every append. No branch, loop bound, emitted operation
or argument changes. This avoids retaining millions of operations in memory.
The source and compiled paths share their intended source controller and opaque
primitive semantics. They are **differential source-reuse checks**, not an
independent numerical implementation or formal-kernel proof.

The direct source adapter reconstructs the current 28233 request ordinals,
positive idle supports, owner/chart labels, all 288 calls and 29 global events.
For one formal low label it executes every emitted opcode through the actual
dispatcher, with a distinct initial variable for each of 28416 families. SHA256
hashes compact free expression terms. It compares every ordered residual result, every local/family XOR input and
output, and every global family checkpoint, plus each completed disposal and empty final stage/private roles. This checks
expression equality with the usual hash-collision limitation; the written
induction, not a digest collision assumption, supplies the universal theorem.
A tiny two-low case detects stale scatter, moved instead of cloned source,
missing private output, omitted disposal and reversed XOR roles. These address
semantic translation failures. Full GL64 low enumeration, actual high lifts,
physical packet bodies and production residual permutations are not executed.

The abstract chart token records the source chart label, not its evaluated
matrix. Distinct chart tokens are not proof of distinct native packets modulo q.
That is precisely A's separate owner-separation premise. The current source
schema check also does not independently reprove its 903456-request digest or
projector ranks; PR3967 retains that finite catalogue audit.

## Complete cost boundary

This is a functional translation theorem. Let each emitted primitive/residual
and matched call cut carry its actual completed physical cost, including
preparation, packet copies, routes, directory/count scans, parking/restoration,
XOR readers, disposal, leaf work, coefficient delivery and cleanup. Summing these
costs in emitted order is a complete *symbolic invoice*. No term may be erased
because its free-term interpretation is abstract. The theorem gives no numerical
upper bound on any primitive or on gamma/history/visited storage.

In particular a rank26 residual contains its complete recursive child node;
its cost cannot be replaced by the sampled rank7 COPY bill. Conversely, charging
a completed rank26 child and then adding its internal rank7 episode again would
double-count that episode. The stock, source refinement, precision, tape bound,
ordinary/native/router join and recovery obligations retained by PR3950/3967
remain. No selected-frontier update or complete multiplication theorem follows.
