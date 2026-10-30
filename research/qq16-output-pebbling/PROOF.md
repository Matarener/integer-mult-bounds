# Output-bank pebbling for complete QQ16 recovery

## Statement and boundary

At the first post-B1 recovery boundary, PR3985's literal decoder reads all
224 current X/Y arrays as borrowed inputs and produces all 224 original x/y
arrays in the owned Z/W output banks, in F17. This package keeps that contract
and the 224 H1, 448 wrapper and 352 cover-map invoice. It eliminates all 112
additional full-cover D arrays by scheduling their lifetimes inside eventual
Z output slots. Peak private scratch remains 16.

The resulting word has 424 CLEARs instead of 536, saving 224 scalar primitive
allowance: 27,184 becomes **26,960**. No source/input is discarded. The 224
owned output arrays may enter with arbitrary dirt; all are explicitly
initialized before their logical values are read. All 224 borrowed current
arrays retain their exact values and frames. This is a constructive local
bank allocation, not a minimum-space or global supplier theorem.

The exact source is PR3985 head
`400df7fca8f60c19bf163c77564fe3fbe9154b04`. Only its WORD data is retained.
The checker regenerates that full word from the canonical PR2707 decoder,
then replays the changed whole word against its independent routed inverse
formula and on independent original inputs propagated through F0/B1.
Canonical algebra and native contracts are reused with full transitive byte
and Git-blob authentication before execution.

## The dependency graph that permits deferral

Write A and T for the two eight-port selected sets, and U for the 96 ordinary
ports. The prefix originally defines every Z_p by `Z_p = X_p`. At A and T
ports it also adds the normalized initial W_p. Before the future logger:

- Only the eight Z_T values are ever read. They contribute to the current
  inverse-query correction of W_T and must remain live.
- Each Z_U is only its initial X_U copy and has no reader yet.
- Each Z_A is X_A plus initial W_A and has no reader yet. W_A is unchanged
  through the preceding current-query block and until the future logger's
  final response additions. The intermediate stage-1 maps on W_A cancel;
  the complete routed and phase replay checks their return.

Therefore all 104 Z_(U+A) definitions can be deferred. This is dependency
rescheduling, not destruction of live outputs. The eight Z_T definitions,
map operations and uses remain at their original positions.

The verifier derives the exact pre-logger Z read set from the retained word,
checks every removed definition against its complete expected instruction
sequence, and checks the full W_A write sequence. No generic allocator or
unverified claim that all Z banks are dead supplies this fact.

## A concrete allocation with zero external banks

The source future logger reads 104 query copies D_(U+T), then writes eight
response copies D_A. Let z(p) biject the ordered query ports U+T with the
ordered free output slots U+A. Host each D_p in Z_z(p). Reserve the first
eight slots in U as the eventual response locations; the explicit mappings
are recorded in RESULT.json.

The schedule is:

1. Keep the source prefix except the deferred Z_(U+A) definitions.
2. In each query's assigned output slot, perform the original clear/copy,
   stage-2 affine map and inverse C_q. The 104 query values now have frame
   F16, on coordinates 9 through 24. All original W sources remain F17.
3. Within each owner-private sweep, form **all eight** private F queries
   from all 104 query copies. Only after the last query read, clear the eight
   designated response slots in F16 and write their quarter-query response
   combinations. These eight slots formerly held query copies, whose final
   use at this owner has passed. Clear the eight private F fields in identity
   frame before moving to another owner.
4. All Z_A slots were query-only. After the complete sweep, initialize their
   deferred values X_A + W_A, in F17, while W_A is still unchanged.
5. Apply each original positive C_q and inverse affine map to its response
   slot, returning that correction to F17, and add it into W_A.
6. After every response has been consumed, initialize all deferred Z_U with
   X_U in F17. Resume the untouched inverse-B1 checkpoint and F0 suffix.

This is a local last-use reuse inside the owner body: a query value is
captured in F before the same physical slot is overwritten by a response.
All native/map events remain outside the private body. Across owner moves,
only explicit full-cover output banks persist; private F state is returned
zero/identity. There is no attempt to retain owner-private values through a
native operation or move.

The response locations are chosen from Z_U, not Z_A. Otherwise recreating
Z_A before modifying W_A could overwrite a still-live response. The choice
also means every response has been consumed before its output definition.
The full replay checks these causal boundaries, values and all 73 linear
and quadratic modulo-four phase coordinates.

## Why the final clears disappear

In PR3985, each D is separate from every output and must finish zero/identity.
Here no D allocation exists. Each temporary lifetime ends by the explicit
initialization of its owned output slot, or by the F16 clear that begins its
response lifetime. The 112 original final D CLEARs are thus obsolete; they
would clear actual output storage at the wrong time if retained indiscriminately.

The source's 104 initial query clears and eight initial response clears are
still paid. The latter move to the query last-use cut inside the private
body. Every original Z initialization remains paid, merely deferred. Thus
arbitrary output dirt and all temporary contents are erased by charged
operations, while every borrowed input survives. Zero/I return remains
required for private scratch; final output slots are live outputs in F17,
not promised zero/I temporary outputs.

## Complete local invoice

| Charge | PR3985 | Output-hosted word | Change |
|---|---:|---:|---:|
| H1 children |224|224|0|
| Native wrappers |448|448|0|
| Full-cover maps |352|352|0|
| Unit ADDs |1920|1920|0|
| Quarter ADDs |896|896|0|
| CLEARs |536|424|−112|
| Real scalar primitive allowance |27184|26960|−224|
| Owned output arrays |224|224|0|
| Additional owned full-cover temporaries |112|0|−112|
| Peak owner-private fields |16|16|0|
| Borrowed current X/Y arrays |224|224|0|

Allowance is 8 per unit ADD, 12 per quarter ADD and 2 per CLEAR. The source
F0/B1 producer is unchanged and additional. This contribution deletes local
storage obligations and charged clears; it does not lower the recursive
native count or automatically increase kappa.

## Actual caller and physical limits

The frozen hosted template identifies replica 0's F0 as physical source
 event 0, B1 as event 1, the other pair's idle preparation as event 2 and
ordinary bridge as event 3. This recovery insertion is at the cut after B1
and before the subsequent idle preparation. Current pair-0 X/Y remains
borrowed. This is the full recovery endpoint, not the reduced bridge-only
endpoint examined in PR3977.

The bank reuse is real **within the 224 exclusively owned output banks of
the pinned decoder contract**. It does not identify these output banks with
borrowed current state, uncleared dirty helpers, or free storage in the
original gauge44 controller. The actual placement and access of those 224
owned outputs in a physical caller remain obligations. The local result
removes the need to supply 112 more fields once that output contract is
provided; it does not prove a complete six-tape hosting schedule.

| Obligation | Status |
|---|---|
| Exact first-B1 source cut and source word | Pinned and checked |
| Deferred definitions and last-use allocation | Constructively checked |
| Complete arbitrary-array inverse and output frames | Replayed under authenticated canonical contracts |
| Borrowed preservation, arbitrary owned dirt and private zero return | Checked |
| Signed native recipe coverage and primitive invoice | Checked |
| Physical placement and access of the existing 224 owned outputs | Unknown |
| Movement, control, output consumption and actual family coverage | Unknown |
| Changed rounded errors, dirty magnitudes and all-depth supplier admission | Unknown |

No supplier moment or kappa improvement is claimed from the storage delta.
The bounded next test is physical placement of this existing output bank at
one actual caller, with all movement and coverage costs; a new local storage
search without that contract is not justified by this result alone.

## Attribution and overlap

Credit PR3985 for the rectangular correction and its 224-H1 full word; ywz65
PR2707 for F17 normalization and native checking; Arham Tahir PR2681 for the
ordered inverse; Ali Romman and the retained QQ16/geometry/native lineage.
Discussion2617 and commdata2338's PR2651 supplied prior output-bank lifetime
coalescing for sixteen early records in PR2540. This result concerns the
104 query and eight response lifetimes in the newer zero-retention PR3985
word, not a second claim for those early-record savings. Credit Nick Petalas
PR2722 for explicit storage-layout access accounting and PR3339 for the
separate consumer/coverage boundary. Source notices remain unchanged.

New contribution: the exact deferral, query/response/output allocation,
whole-word verification and 112-bank/224-scalar reduction. Chris R /
Clear1nsight with substantial OpenAI Codex assistance, Apache-2.0. Independent
agent review is recorded separately; no human or formal proof-kernel review
is claimed.
