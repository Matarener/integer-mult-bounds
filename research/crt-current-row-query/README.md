# Actual CRT offsets to a physical current-row query

The sequential numerical result of Ali Romman's PR5353 now feeds the
unchanged PR5092 encoded Beneš ROM producer. The join reads the produced
ROM on its original backing, selects the current padded coordinate with
an encoded countdown, and returns the actual micro-row coordinate stream.
It pays for serialization, queries, rewinds and disposal of both the
selected ROM and the unused complete-layer output.

[PROOF.md](PROOF.md) gives the source-relative quantified interface theorem,
admission W=P, current-coordinate convention, complete local time bound
and retained-backing bound. [RESULT.json](RESULT.json) records the small
actual producer/query cases and four falsifying controls. The h=2 checks
exercise the complete encoded producer, not a verifier-supplied row table.

```sh
python3.12 -B scripts/research_package.py --package research/crt-current-row-query
```

The registered normal and optimized runs authenticate every source input
and compare typed deterministic receipts. The separate, expensive h=4
four-axis test is explicitly opt-in:

```sh
python3.12 -B research/crt-current-row-query/verify.py --four-axis
```

This optional whole-ROM test is distinct from the small executed h=2 ABI
checks. The author attempt exceeded180seconds without completion; no
ACTUAL4 receipt exists and no h=4 joined result is claimed. See
[ATTEMPT.json](ATTEMPT.json) for exact attempted bytes and the subsequent
all-size repairs. A future completed optional run checks the caller and
invoices even without a frozen receipt; `--write-result` records one.

The small mixed-width case reaches padded coordinate3 before its last
query. Suppressing that query gives the wrong endpoint. Mutating the
offset, selected row or unused-layer disposal also fails. All source and
protected words are restored; all63 numerical ports and every joined
owned backing are retired. Separate row invocations use test-harness
input serialization; no uninterrupted physical level execution is claimed.

## Open next questions

- Physically update the canonical axis input with the returned row stream,
  so successive rows need no host serialization.
- Compose the current query into the complete three-epoch exceptional key,
  paying for all original/current coordinate conversions and restorations.
- Resolve cross-session bank ownership and a complete binary numerical
  lowering before claiming a global machine or outer multiplication bound.

No new kappa, selected frontier, human acceptance or formal-kernel proof is
claimed. Source models and initial blank owned backing remain explicit
premises. This is one actual caller boundary, not full total repair.

## Provenance and credit

Base32890bc5de034ab8fc93ac88ead7279a6a416d04, priority7. The scope takes
PR5353's explicit physical-query handoff, Discussion4709 comment19152738;
the new claim is comment19173182. Fresh overlap covered352 open PRs and
4747 fully paginated Discussion records through2026-10-25T04:14:44Z,
plus exact local source packages. Unpublished work was not searched.
[SOURCES.json](SOURCES.json) freezes the complete input closure.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Retain Ali Romman's actual RowEntry, Hiroki KUMAZAKI's mixed-width caller,
JoyboyBrian's numerical entry and ROM producer, Cinna Davis's CRT/Beneš
construction, ToikY's arena/DFS proof and all predecessor notices and
credits listed in PROOF.md. No predecessor file is modified.
