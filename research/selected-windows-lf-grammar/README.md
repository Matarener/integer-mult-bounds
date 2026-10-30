# LF/CRLF-only outer grammar for the PR2477 composed caller

This successor repairs the concrete unresolved [PR2477 review counterexample](https://github.com/CrocSwap/integer-mult-bounds/pull/2477#issuecomment-6205219558).
The exact predecessor at `0760e745c5d3b6e66dbfab1799be75abf01576ed`
accepts a first-LF-to-vertical-tab mutation because its inherited outer validator
uses Python `str.splitlines()`. The new caller rejects all eight additional
separator characters before invoking that unchanged validator. LF, CRLF and
mixed LF/CRLF boundaries remain accepted.

## Change and evidence

`CALLER-DELTA.patch` shows the complete changes to PR2477's two caller files.
`test_controls.py`, its six-positive/203-negative receipt, all eleven vendored
files and `PREDECESSORS.json` are byte-identical to that pinned predecessor.
These executable dependencies are retained because the new caller exercises
the same complete comparator and fresh successor, including their attribution.
`SOURCES.json` pins the original caller/proof and all43 live scientific inputs.
The publication history retains the exact pending PR2477 commit as a history
parent, so a full clone can resolve its source pins. The contribution tree is
current main plus this scoped package; no upstream PR is merged or closed.

`COUNTEREXAMPLE.json` records the actual unmodified-caller reproduction on the
authenticated archived1094 fixture. `GRAMMAR-CONTROLS.json` adds an independent
scan of every Unicode codepoint to discover Python's separator alphabet, eight
unchanged-parser counterexamples,104 guard rejections at all13 boundaries,
24 full-comparison rejections (reference/candidate/both), malformed UTF-8,
and a positive using different mixed line endings on both sides. The guard is
an explicit check and remains active under `-O`.

The registered replay passed on native Windows11 / CPython3.12.11: normal-mode
archived grammar controls, then a fresh optimized-parent execution with the
assertion-enabled scientific child. All105 outputs,30 raw links per side,
6 inherited positives/203 negatives and1 new positive/129 grammar negatives
passed. `VALIDATION.json` records the environment and exact control receipts.
The first attempt encountered an unwritable sandbox TEMP directory; writable
workspace TEMP/TMP resolved that environment failure without changing inputs.

## Acceptance boundary

The six input roles and all30 same-side raw references are authenticated before
log processing. Inner-log canonicalization remains exactly PR2477's CRLF-to-LF
conversion plus bare-CR rejection. Only the outer log gains the eight-character
rejection, after strict UTF-8 decoding. No foreign separator is normalized or
discarded. The complete inherited13-line validator still checks every stage
time and both final result lines; the105-output comparator remains unchanged.
See `PROOF.md` for the implication and its limits.

## Reproduce

From repository root, with standard-library Python3.12 and writable TEMP/TMP:

```sh
python3.12 scripts/research_package.py --package research/selected-windows-lf-grammar --check-only
python3.12 scripts/research_package.py --package research/selected-windows-lf-grammar
```

The registered commands run archived grammar controls without optimization,
then a fresh optimized-parent replay with the scientific child at `optimize=0`
and both control suites. The full replay has a600-second bound. A direct run
can preserve its output using a fresh `--work DIRECTORY --report FILE`.
`--grammar-only` means archived-fixture controls only; `--skip-controls` remains
diagnostic and is not registered acceptance.

## Limits

This is a repair of a historical1094 comparison boundary, selected by a live
review handoff. Current main selects #6030; this package does not execute that
supplier or revise its selected record. Fresh final-stage execution still uses
authenticated archived ancestor inputs, so it is not cold ancestry. Finite
controls are not a formal implementation proof. The inherited Decimal timing
token policy remains numeric, including its accepted spelling variations.
UNC/device roots, new schemas, other log formats, complete multiplication
theorems, hosted CI and independent human review are outside the claim.

## Open next questions

Should timing tokens have an explicit lexical grammar in addition to numeric
equality? This is separate from the newline defect. First compare archived and
native spellings and specify the intended contract; the blocker is the absence
of that separate contract and review. Structured details are in `TASK.json`.

## Credit

Counterexample and repair request: Mister-Meeseeks. Original authenticated-log
composition, serialization, replay and203 controls: ywz65 with OpenAI Codex.
Retained lineage: Dennis / antunishdPursuit (PR2336), AAAmirinu (PR2344), Adam
Gall (PR2101/2059), commdata2338 (PR2040), josecarlosgonzalezroque-design (PR2316),
Josie Elliston (PR1824), Maxime Fleury, Antoine Olivier, Rohan Arun, Jeremy Kothe,
Douglas Colkitt and the retained supplier authors. Their vendor notices and
bytes are unchanged. New grammar guard, controls and write-up: AAAmirinu with
substantial OpenAI Codex assistance, including separate AI source review.
Apache-2.0; AI review is not independent human review or maintainer acceptance.
