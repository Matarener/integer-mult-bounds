# Direct residual-run emission with unchanged continuation PCs

The actual pinned compiler can skip its inner Cursor enumeration entirely:
it emits one existing BlockRun descriptor per residual while preserving every
factory call, original Residual identity and indexed operation. This closes
PR4791's explicit block-enumeration handoff. Outer LOW and factory enumeration
remain unchanged; no selected GL64 practicality or new κ is claimed.

The [proof](PROOF.md) justifies the exact source-AST substitution under the
predecessor stable immutable-source contract. Each distinct plan is indexed and
snapshotted once during compilation. Compilation calls neither Cursor nor
repeated plan validation. The inherited indexed runtime still performs its
full mutation checks; it is not made faster by this change.

A per-append observer deliberately selects the old enumerating path and gets
every tuple. Source namespace replacement, hostile mutation during compilation,
allocation identity and frame tracing remain outside the declared contract.
No frozen predecessor file is edited or production loader modified.

## Evidence and reproduction

Python3.12 and standard library only:

```sh
python3.12 -I -B research/selected-regional-block-emitter/verify.py
python3.12 -I -O -B research/selected-regional-block-emitter/verify.py
python3.12 -I -B research/selected-regional-block-emitter/verify.py --physical
```

[RESULT.json](RESULT.json) includes independent literal Cursor grammar checks,
six actual GL2 source schedules (both modes,1/2/8 replicas), every indexed tuple
and original-wrapper identity, exact factory transcript, and full append-observer
comparisons. During direct compile, Cursor construction/take and repeated
PlanIndex.validate are replaced by failing sentinels; exactly one PlanIndex
build per distinct plan is counted. This distinguishes skipped work from storage
compression that still enumerates every block.

[PHYSICAL.json](PHYSICAL.json) records the separately budgeted original/direct
actual two-level physical fixture, including nonzero saved/restored PCs,
independent1024-bit payload endpoint, borrowed fields, counters and erasure.
It is not a full selected supplier replay. Source hashes and typed receipts
are checked before and after replay; committed exports need no Git/network.

For fallback-heavy repeated plans, direct sink work becomes O(A+S+P) rather
than retaining an O(B) block loop: A is non-block tuples, S residual segments,
P distinct-plan size and B block count. Outer/factory work is unchanged, and
runtime snapshot scans remain paid. Axis-only mode can gain nothing and incurs
index overhead. No physical tariff, production speed benchmark or stock saving
is inferred from these host-operation counts.

## Open next questions

- Prove an outer regional LOW schedule with source-dependent lengths, exact
  header PCs and callback contract; it must not hide enumeration in indexing.
  This package leaves those loops untouched and supplies only the inner run.
- Admit the direct representation through the selected loader/bindings and
  full resource model. Start with the actual installation policy; reduced
  same-byte fixtures do not provide selected admission.
- Enforce immutable plan ownership cheaply enough to remove runtime snapshots.
  That separate observer/lifetime problem is deliberately not weakened here.

## Coordination and credit

Base32890bc5de034ab8fc93ac88ead7279a6a416d04, priority7; selected conditional
κ=.003027288235 unchanged. [Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19173187)
contains the canonical claim. Fresh overlap covered352openPRs and4747Discussion
records; the released PR4791 finding leaves this exact inner task open. The
parallel outer LOW scheduling task is separate. Closed histories, arbitrary
diffs and unpublished work were not exhaustively searched.

Prepared for **JoyboyBrian**, with substantial **OpenAI Codex assistance**.
Retain Jose Manuel's emitter/Cursor/physical runtime; Kewin Talaga's source
bridge; Nick Petalas's correspondence/continuation audits; David Arias/ywz65
and all original source notices. PR4758 wrapper sharing and PR4791's existing
itinerary index remain predecessor contributions. Apache-2.0; no human or
formal-kernel acceptance, Lean run, selected promotion or invoice change.
