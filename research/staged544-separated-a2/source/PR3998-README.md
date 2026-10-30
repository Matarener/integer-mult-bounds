# A literal A2 graph contraction and its exact staged544 frame budget

The A2 root-system identity yields a concrete simplification on both frozen
PR3734 staged544 providers: replace the three ADDs at A1858 by two ADDs,
removing **one forward and one inverse-cleanup ADD**. The full chronological
recursive profile is unchanged. Every dirty-input and caller boundary is
preserved. The same literal contraction is independently checked on both
current PR3945 terminal-gap-filled words at 91f81d13, with their own complete
profiles and full dirty-word replay. This supplies a reproducible scalar
simplification, **no new κ**.

The same package completes the complementary consecutive two-to-three A2
rewrite search. Each provider has 168 directed two-ADD motifs. All three central
commutator positions and every compatible binary-frame flag are included.
All 460 legal flags have non-improving recursive moments for every `0<a<1`:
396 exact ties and 64 strictly worse flags. The five signed profile types have
an elementary exact subadditivity proof. An initial dimension-only relaxation
has 2714 candidate triples, including 1014 uncertified potentially favorable
cells; exact subspace incidence rejects all apparently favorable candidates.
This is a concrete demonstration that rank-dimension optimization alone can
misprice a changed dependency graph.

The primary field is framed rational circuit optimization. The contrasting
specialization is algebraic groups: the A2/Steinberg transvection relation
changes the literal scalar event graph while an exact rational matrix check
preserves arbitrary dirty state. This differs from the fixed-graph retiming
and stationary-frame domains of PR3886/3941/3942/3957/3964/3970.

## Literal construction

At zero-based A index 1858, all frames are span(82,42):

```
Before                         After
457 <- 457 - 475               456 <- 456 + 457
456 <- 456 + 457               457 <- 457 - 475
456 <- 456 + 475
```

Both sides map `(x456,x457,x475)` to `(x456+x457,x457-x475,x475)` for arbitrary
inputs. The unique legal contracted frame assignment has the complete profile
`{1:2440,2:725,3:224,4:102,5:20,8:8}`: 3519 recursive children, rank mass 5134.
These are the older PR3734 counts; PR3945 applicability retains its separately
recorded source profile. There are 408 helper roles and 91 dirty buffers. A has 4078 events after the rewrite
and cleanup has 5223. No further consecutive inverse A2 motif remains in the
contracted word. This is one bounded fixed-point check, not an arbitrary graph
normal-form theorem.

`RESULT-base.json` and `RESULT-extra.json` retain the exact source bindings,
replacement gates, full invoices, canonical contracted-word/cleanup digests,
all expansion records, complete frame intervals and full-word replay receipts.
`PROOF.md` gives the exact scope and composition argument. `LEDGER.json` states
proved, finite bounded and unknown costs; unknown costs are not zero.

## Reproduce

Python 3.12 or later, standard library only. Commands are read-only by default.

```
python3 -B research/staged544-a2-graph-rewrite/verify.py --provider base
python3 -B research/staged544-a2-graph-rewrite/verify.py --provider extra
python3 -O -B research/staged544-a2-graph-rewrite/check_controls.py
python3 scripts/research_package.py --package research/staged544-a2-graph-rewrite
```

Each complete provider replay takes about four minutes on the author's host;
see `VALIDATION.json` for exact measured runs and failures. A replay may export
the literal contracted word only to an explicit path outside this package:

```
python3 -B research/staged544-a2-graph-rewrite/verify.py --provider base --emit-contracted-word /tmp/staged544-a2-base.json
```

The files under `inputs/` and `vendor/` are immutable predecessor snapshots.
The verifier authenticates byte counts, SHA256 and Git blob IDs before loading
source. These public source heads are attribution pins, not an assertion that
they are ancestors of the package's base. Standalone replay is Git-free; the
repository hook additionally checks pinned catalogue provenance in Git history.

## Coverage and limits

Only consecutive scalar motifs in A after `prelude_events`, B between fixed
native warp cuts, and restore are included. Prelude events, crossed native
maps, separated motifs, changed boundaries and additional registers are outside
the certificate. Exact dirty block and complete frame/cleanup invoice checks
cover every legal flag. All four PR3734/PR3945 baselines and **every contracted word** receive
full 723-input ordinary, dual, reverse and cleanup-boundary replay. Expanded
whole-word interpreter checks are six deterministic samples per provider;
universal expansion coverage uses exact local matrix composition and projected
inverse cleanup. No fresh Clifford-phase, physical owner-schedule, uniform
precision/stock/tape, all-size supplier or multiplication theorem is claimed.

## Open next questions

- Can a nonconsecutive A2 relation or a coordinated graph cycle pay its complete
  frame and restoration invoice? First exhibit one exact block and a favorable
  full optimistic bill before enlarging the search. Intervening frames and the
  physical scalar schedule remain obligations.
- Can one specific rejected dimension-only candidate become useful under a
  changed, fully paid entrance/exit or native consumer? Name that consumer and
  its dirty restoration and phase costs first. Free boundary relaxation does
  not supply an implementation.

## Credit and status

Dataisfire supplies PR3734's frozen literal providers. PR3886 supplies the
retained trace and binary-subspace representation. The retained scalar auditor
credits Sagar Thakrar, roger-sato and Arham Tahir; its original notices are kept.
Jeremy Kothe's rank-profile rewrites and the subsequent fixed-graph obstruction
stream motivate this changed-graph question. Dugongue's PR3945 supplies the changed terminal-gap-filled applicability
words, frozen separately; its native lineage notice is retained. Dugongue's
PR3863 supplies the
`2+2 -> 1+3` implementation target and paid-overhead discipline; the present
scalar contraction does not realize that rank exchange. See `SOURCES.json` and
`vendor/SOURCE-CREDITS.md` for exact pins and full lineage.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
Author-checked finite construction/certificate; no independent human review,
formal-kernel proof, supplier admission or selected-frontier change claimed.
