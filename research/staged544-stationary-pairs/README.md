# Stationary simultaneous two-ADD frames have a legal intermediate on staged544

On both pinned PR3734 providers, every legal simultaneous replacement of the
common frames at two stationary ADD addresses admits at least one legal direct
single-edit intermediate. This closes the **stationary** part of the
illegal-intermediate gap left open by PR3942. It does not close simultaneous gate
reorderings or changed native/caller boundaries. No new κ or supplier is claimed.

This is the new compatibility result. The prior legal-sequential price
obstruction is credited to PR3942; the independent price rows here corroborate
it and explicitly include all stationary ADDs, including 48 prelude ADDs that
are outside the predecessor's movable scalar corridors.

Per provider, 5,549 addresses define 15,392,926 unordered distinct pairs.
8,923 pairs interact through consecutive events on a register; the remaining
15,384,003 factor into individually checked single edits. All 10,591 exact
coupled subspace assignments (9,883 dimension cells) admit a legal intermediate.
All 19 single and 42 joint signed-profile types are non-improving for every
`0<a<1`. These counts are compatibility assignments, not new physical circuits.
The two providers are checked separately; their equal counts do not merge their
source identities.

A naive dimension relaxation admits 100 impossible cells per provider. The
actual B362/B366 proposal with dimensions 4,4 needs a successor of dimension at
least five. Independent subset-XOR enumeration checks all 1,345 distinct frame
intervals. A crossed-line synthetic control has a legal simultaneous final pair
and **neither** legal intermediate, proving that the detector does not assume a
general sequentialization theorem. See [PROOF.md](PROOF.md).

## Reproduce

Standard-library Python 3.12, read-only:

```
python3 -B scripts/research_package.py --package research/staged544-stationary-pairs
python3 -B scripts/check_research_commit.py --package research/staged544-stationary-pairs --check-source-history
```

Direct Git-free scientific checks are `python3 -B verify.py` and
`python3 -O -B test_controls.py` from this directory. Ordinary verification
compares the complete frozen receipts and writes no package files. The generic
runner provides a fresh private bytecode-cache namespace; a direct call should
also use a clean export or a fresh `-X pycache_prefix` directory.

RESULT-base/extra.json contain complete sign rows, frame intervals, coverage,
assignment-stream hashes and whole-word selections. CHECKS-base/extra.json contain
full exact semantics receipts and the cost ledger. VALIDATION.json records the
actual commands and execution status. SOURCES.json authenticates exact immutable
bytes before retained executables run; external PR snapshots are authenticated
by SHA256 and Git-blob hashes, not asserted to be Git ancestors. The canonical
catalogue is separately pinned to main 20ecf289.

The universal arbitrary-dirty identity follows because all semantic operators,
coefficients, order and cleanup remain literally identical. Exact frame and
invoice checks cover every assignment. The attributed full interpreter checks
both baselines and four edited whole words per provider: 632 live inputs plus 91
arbitrary dirty buffers, forward/dual orientations and reverse cleanup. These
are additional whole-word controls, not an exhaustive interpreter replay.

The complete local bill retains 3,519 baseline children, rank mass 5,134,
408 helper roles,91 dirty buffers and all native/scalar primitive inventories.
Every changed local profile is recorded by its signed delta. No new gates,
helpers or buffers are introduced. Fresh native phase, physical owner/hosting,
uniform precision/stock/tape, all-size compiler, supplier/outer, analytic and BIT
obligations remain inherited or unknown. They are never priced as zero.

## Task and expansion decision

This was an explicitly assigned multi-agent continuation under scalar-to-moment,
canonical main 20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority 6.
The family decision is **narrow and stop**: the exact stationary compatibility
check removes the proposed illegal-intermediate escape in this contract; it
does not justify another larger stationary census. Entry overlap covered 662
open PR bodies plus partial visible Discussion handoffs. See TASK.json for scope,
claim, pins, current checkpoint, stop test and next questions. No exhaustive
novelty claim or selected-frontier change is made.

## Open next questions

- Moving ADDs changes the event graph. Find one exact scalar identity whose final
  frame pair is legal but neither direct intermediate is legal; price all changed
  edges and cleanup before extending a search. Exact scalar realization and its
  complete local/physical invoice are the current blockers.
- PR3929 supplies compatible changed native entrances/exits. Its published
  example loses. A useful successor needs a favorable full entrance/scalar/
  terminal/caller invoice, exact phases and physical hosting. PR3945's changed
  terminal proposal is separately active and must be checked before overlap.

## Credit and scope

Chris R / Clear1nsight prepared the new compatibility reduction, finite checker,
controls and packaging with substantial OpenAI Codex assistance. No independent
human review or formal-kernel verification is claimed. Apache-2.0.

The unchanged trace/sign code is from PR3886 (scientific 359fe0fe), and
PR3942 (1416f8cd) supplies the legal-sequential predecessor and this open question.
PR3941 (001ebcdb) and PR3957 (c8285dba) are parallel retiming-domain results.
The pinned providers and retained semantic tools come from dataisfire/PR3734
(fa041037). Credit Sagar Thakrar's auditor, roger-sato's adapter and Arham Tahir's
frame-contract reading; these are reused tools, not new independent interpreters.
Retain Jeremy Kothe's PR2957/2979 word/frame lineage and the full source notices
in vendor/SOURCE-CREDITS.md. Dugongue's PR3863 (635fe845) motivates the paid
`2+2→1+3` exchange; its ranked-pair/MathProof predecessor credit remains there.
Dugongue's PR3929 (0c0e31cf) informs the distinct changed-native follow-up; no
native implementation from it is imported or newly replayed here.
