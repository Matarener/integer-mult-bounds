# Optimal dirty-register basis preparation

For every finite binary rank-one idempotent `N=u v^T`, the exact minimum
number of scalar row-XORs that conjugates N to any coordinate projector is

    d = wt(u)+wt(v)-(wt(u&v)+3)/2.

Additional restored dirty roles do not lower this minimum. Each row-XOR
costs one; arbitrary free scalar basis changes are excluded. The
[written proof](PROOF.md) uses a coordinate-color potential and an attaining
three-XOR elimination of each pair of shared coordinates.

This improves Arham Tahir's [PR3137](https://github.com/CrocSwap/integer-mult-bounds/pull/3137)
finite-array Q8 compiler. Its two-star preparation takes `wt(u)+wt(v)-2`
row-XORs. Replacing the preparation and inverse restoration saves exactly
`wt(u&v)-1` whole-array XORs per nonidentity action. The regular Q8 address
action, contiguous eight-block layout and block-swap algorithm are inherited.
No predecessor bytes are changed.

If each block contains B bits, the complete new data invoice is

    C = 2 wt(u)+2 wt(v)-wt(u&v)-3 whole-array XORs,
    8 B C + 3 B S_g bit XORs,

where `S_g=4` for the central label `-1` and `S_g=6` for the other six
nonidentity labels. Identity performs no work. At `u=v=(1,1,1)`, a noncentral
action costs **66B rather than 82B bit XORs**, with all role data dirty and
the full required output preserved. These are exact operation counts, not
runtime measurements. The scalar round trip is at most
`2 floor(3(r-1)/2)` XORs on r roles, and this bound is sharp.

Only the scalar preparation distance is proved optimal. The data invoice
is for this conjugate-once/action/inverse-restore compiler, not for every
possible bit circuit. Physical routing, address arithmetic, descriptor
generation/storage, ownership and an actual recursive caller remain unpriced.
This is a local implementation improvement. It establishes no new formal Q8
paid-word tariff, complete supplier, kappa or selected-frontier change.

## Evidence and replay

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -W error -B research/optimal-dirty-preparation/verify.py
python3.12 -W error -O -B research/optimal-dirty-preparation/test_verify.py
python3.12 -W error -B scripts/research_package.py \
  --package research/optimal-dirty-preparation
```

Normal replay reads [RESULT.json](RESULT.json) and never writes evidence.
`verify.py --emit` prints the recomputed receipt. The proof and checked
sample bills do not depend on timing, probabilistic tests or external libraries.

- Independent multisource BFS checks every one of **43,435 idempotents through
  eight roles**, including every row-XOR and every coordinate endpoint. It
  neither uses the formula nor imports the constructor's pair-update logic.
  Emitted schedules match all distances. Of these cases, 18,831 improve the
  predecessor's preparation. Four additional cases reach the implementation's
  256-role capacity boundary or nearby large odd supports.
- **21,360 Q8 fixtures check 972,864 independent dirty-input columns** and
  inverses. They cover all idempotents through six roles, all eight labels,
  and additional payload widths 2, 3 and 7 with a dirty spectator. The oracle
  uses Hamilton integer-quaternion multiplication; the implementation uses
  affine address arithmetic and literal three-XOR swaps.
- Six behavioral groups include rejected deleted/reordered preparation,
  wrong pivot, omitted restoration, a correct but nonminimal old preparation,
  invalid domain/capacity/aliasing, and actual optimized Git-free CLI runs
  rejecting false bills, Boolean-for-integer receipts, duplicate JSON keys,
  changed sources and missing sources. The old preparation remains a passing
  full-operator control before failing the new minimum-distance check.

The all-role theorem is a written proof. Finite exhaustive checks corroborate
it and the executable implementation, whose resource boundary is r<=256,
B<=7 and bit-packet width<=14,336. The packet bound concerns symbolic evidence
packing; the data algorithm acts independently on ordinary bits.
No Lean, Docker, hosted acceptance, full selected cold replay, independent
human or formal proof-kernel review is claimed. The selected source-binding
baseline passed, with the complex supplier still binding.

[TASK.json](TASK.json) pins priority revision 6 and the changed card scope;
[SOURCES.json](SOURCES.json) binds the canonical base, historical guidance
and exact PR3137 README. [VERIFY.json](VERIFY.json) declares that live input.
The source-bound mathematical dependency is the stated Q8 conjugation and
array contract, not an assumption that a selected supplier can provide it.
Standalone replay works in a Git-free export containing the declared input;
the generic runner additionally checks Git provenance.

## Engineering bounds

Build the Lever led to the rerunnable compiler and independent distance graph.
Prove It Works led to complete dirty-output comparison and real rejecting CLI
controls. Power of Ten led to explicit role/payload/packet capacities, bounded
cycle and BFS loops, enabled runtime contracts under `-O`, and read-only normal
replay. All new scientific functions are kept within one page.

Managed Python allocations are a scoped rule-3 deviation. The BFS preallocates
two arrays of at most 65,536 entries at r=8. Pair enumeration is bounded by
255 squared; a live symbolic fixture has at most 48 cells in the exhaustive
run, or 224 in the extra packet run. The public compiler accepts at most
14,336 cells of at most 14,336 bits, and preparation has at most 382 row-XOR
descriptors. Interpreter/library allocations remain outside direct inspection.
Follow-up for a production backend would replace Python packet evidence with
fixed-capacity bit buffers after binding the actual caller.

The test suite uses scoped mock callbacks and the standard unittest runner.
The JSON parser uses one named duplicate-key callback on bounded receipts.
These are rule-8/9 deviations limited to explicit targets with synchronous
lifetimes. Production arithmetic uses direct calls without recursive traversal.
Tests verify that each modified schedule fails for the intended semantic
reason. Temporary test directories are released on every exit. Shared
historical code and frozen archives remain unchanged.

## Open next questions

Can one actual recursive caller supply this eight-block layout and projector
at a chronological cut where the local saving survives routing, ownership,
restoration and its consumer? First bind one literal caller and compare the
complete old/new invoice. That caller contract is missing. No larger word
census or dependent construction round is justified by this local result.
Structured details are in TASK.json.

## Credit and coordination

Credit Arham Tahir/PR3137 for the dirty Q8 compiler, regular affine encoding,
sparse two-star construction, swaps and original invoice; ywz65 for the
arbitrary-coupling basis-conjugation method; Gareth Davidson/PR1333 for the
separate affine-rank model; Aaron Wang, Cinna Davis and the retained Q8/register
lineage for the formal paid-word context. The elementary potential and graph
argument claim no literature priority. New work is Apache-2.0. Nick Petalas.
Independent human and formal proof-kernel review are unclaimed.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19009906)
joins the existing Q8 thread. Entry overlap covered 368 open PR bodies and
2,294 Discussion records with complete pagination at 02:33-34 UTC on
2026-10-18, without warnings. Local notes and peer reservations were checked;
not every historical diff or unpublished result was covered. Worker 4's
positive-only signed-target tariff is a disjoint formal word question.
The submission checkpoint fetched the same canonical main and found no
guidance or input delta. Complete overlap refresh covered 372 open PR bodies
at 02:39:46 UTC and 2,299 Discussion records at 02:40:18 UTC, without warnings.
