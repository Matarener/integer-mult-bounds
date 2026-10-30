# Executed evidence and limits

Scientific base: `12fa8c5c844be21bfefb38a19503fbd867a11244`.
Task: `supplier-boundary-audit`, priority revision 7, refined to the exact
PR4088/PR4165 four-provider admission handoff. The assignment and experiments
are deterministic; there was no randomized task lottery.

## Baseline and bounded evidence

The inexpensive `python3 -B scripts/research_baseline.py` passed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. This checks source bindings, not
mathematical acceptance.

The retained PR4085 source preflight was executed freshly, redirecting only its
output location into a private external work directory. Its three independent
terminal, staged-entry and receiver reviews passed. It reconstructed exactly
676 source files, manifest SHA256
`4116ef61479e509811b60b5fd4e84db8811dae079092f2f83bdcc2c80052c0da`,
and admission engine SHA256
`e69184d235d8790a3c520977dd44dcfb73a99d56989825485f922ff61059c8b1`.
All 95 non-source archive inputs matched their retained inventory.

An unmodified inherited owner reconstruction on the real PR4085 THREE control
reproduced its old invoice, including idle
`{3:22842,5:1890,48:138438}`. The independent mixed scan and the new binding
then reproduced the distinct PR4088 invoice in the README. PR4165's existing
five rejection controls also passed; its idle finding is predecessor credit.

The separate THREE baseline copied `PREFLIGHT/inputs/source` to
`BASELINE_CONTROL`, installed the unchanged retained
`PREFLIGHT/inputs/helpers/reconstruct_replica.py` as `reconstruct.py`, and
placed PR4076's `owner/FILL.json.gz` and `owner/inputs/{ORDER,DISPATCH}.json`
in `new/borrow-fill/`. Its executed command was:

```sh
python3 -B BASELINE_CONTROL/reconstruct.py --out BASELINE_OWNERS
```

Those aliases denote fresh external directories. The source package is
`research/staged544-triple-entry-fill` at the scientific base. Its baseline
input hashes are `a8de70d8cc5e15914881dd4849e51014af261bdd215ced7222ceb111cc5baab9`
(fill), `743e74b538432e2b2045e754b0de9c18f36fc5039fdb8eb542177a898ec78e44`
(order), and `5d6fa711d704a1b498e5fe066ea821c4fa0217463702e82a7ce5be9da4023e8a`
(dispatch). The unchanged helper hash is
`5472811c24aef3852dc7e189dff5060076a6c0b25bfde928da50dcfe9b5bdc15`.
This initial experiment used the full canonical checkout; the isolated export
contains the 192 inputs consumed by the successor's documented replay commands.

Both FOUR native sources were freshly executed through all five stages:
`native`, `ledgers`, `local-replay`, `wrappers`, `phases`. Initial executions
took 63.145 and 68.423 seconds. These are observed wall times, not a speedup
claim. Unchanged THREE and parent-admission evidence is explicitly authenticated
reuse, not a fresh cold replay of the entire historical ancestry.

Executed bounded commands:

```sh
python3 -B scripts/research_package.py --package research/mixed-provider-admission
python3 -O -B research/mixed-provider-admission/independent_ledger.py --controls
python3 -B research/mixed-provider-admission/challenge.py --work REPLAY_WORK --preflight PREFLIGHT
python3 -O -B research/mixed-provider-admission/challenge.py --work REPLAY_WORK --preflight PREFLIGHT
```

`REPLAY_WORK` and `PREFLIGHT` above denote the actual external output directories,
not repository dependencies. The registered command passed the 192 live pins,
14 semantic test methods, all 1,321,920 real rows, the optimized unit controls
and the independent event/span checker. The independent checker also passed
separately under `-O`, with an identical result object.

The public actual-output challenges passed 18 cases in normal and optimized
Python. They include all four providers, changed phase with coherently rebound
references, skipped native stage, equivalent serialization/timing positives,
and a changed predecessor engine with its completion receipt rebound.

`python3 -O -B research/mixed-provider-admission/replay.py --work NEW_DIRECTORY`
was rejected before creating the directory, with
`inherited admission requires assertions`. An optimized full release is not
reported as passing.

## Development failures and corrections

The first mixed wrapper attempt reached the new rebind gate and failed because
the inherited reconstructor serializes dispatch rows chronologically, while the
literal input table has a different row order. The correction compares the
table as a sorted relation while separately requiring a bijection and checking
every chronological call, program, orientation and width. A permutation
positive control and changed-selector negative controls cover this distinction.
No owner or accounting predicate was removed.

A separate adversarial AI context demonstrated two draft reuse gaps: an
unbound cached admission driver and native output phases authenticated only by
successful flags. The fixed engine commitment and fixed scientific output
commitments close those demonstrated gaps. That context's 17 bounded follow-up
cases passed before the public four-provider challenge script was added.
These were defects in this unpublished draft, not new allegations about
predecessor mathematics.

A preliminary metadata-only check rejected the draft outcome string
`in-progress`; it was corrected to the schema's `partial` state. The registered
metadata and pin checks then passed.

## Full release

The development replay completed the inherited engine in 1,780.781 seconds:

* `PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE`;
* all seven outer-driver stages, including discovery and final release;
* all 23 ordinary stages, ending in strict replay and geometry controls;
* actual control counts: 201 assembly, 43 controller, 12 bit,
  8 independent owner and 6 geometry;
* `PASS_RELEASE`, 63 strict outer inequalities, 17 rejecting outer controls,
  independent balance derivation, union schedule and 19 exact evidence replays.

The counts above were inspected in the produced ordinary result, strict
receipts and nested outer ledger, rather than inferred from a PR title.
Source and native-cache inventories remained unchanged after admission.

The implementation commit is
`b1eb3cec856e1f56a4ce70c583bce738223be6b2`. Its 208-file committed export
(16 package files and 192 declared inputs) passed archive integrity and
committed-byte checks. Extracting into a fresh directory without `.git`
passed the direct binding regression and optimized controls. The default full
replay then passed from that export, with fresh source reconstruction and fresh
FOUR native execution. Its seven wrapper stages totalled 2,021.013 seconds,
including 1,829.767 seconds in inherited admission. The fresh FOUR base/extra
native drivers reported 74.377 and 65.274 seconds respectively. These are
single-run wall measurements, not performance comparisons.

The clean replay reproduced all the statuses and control counts above.
[EVIDENCE.json](EVIDENCE.json) records the actual stage results, receipt hashes,
provider provenance, exact invoice and semantic controls.
[REPLAY.log](REPLAY.log) contains actual executed stdout excerpts, with only
work, source and interpreter paths normalized. Raw receipt hashes identify
this execution; they are not cross-environment deterministic hash claims.
All 208 exported files remained unchanged after execution, and all nine tested
Python files remain byte-identical in the final package. Subsequent changes
only finalize documentation, metadata and these execution receipts.
The registered package check was then rerun on the final tree and returned
`PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `completed`.

The executed default command, with its external work path abbreviated, was:

```sh
python3 -B research/mixed-provider-admission/replay.py --work ISOLATED_RELEASE
```

The ordinary release ran its 19 exact outer evidence replays. This does not
mean every historical native/parent receipt was rebuilt cold: unchanged THREE
and retained ancestry evidence use the authenticated reuse described above.

## Review and overlap scope

The 2026-10-20 08:54 UTC refresh still found canonical main at the scientific
base and priority revision 7. The helper covered all 295 open/draft PRs and
2,695 Discussion records with complete pagination and no warnings. The latest
50 updated PRs were also inspected for merged successors.
A final canonical fetch at 09:06 UTC still returned the same base SHA.

PR4170's pooled-ceiling transfer and PR4171's independent moment/paid-power
arithmetic are complementary to this actual caller/ordinary/outer integration.
PR4169 audits a PR4100 CRT repair implication. The new Discussion4173
claim concerns CRT reservoir placement, and PR4172 concerns QQ16 comparison.
No equivalent admission successor or active claim was found in that coverage.
This is an overlap check,
not a proof of novelty. Coordination remained local-only.

## Checks outside this result

No repository-wide historical suite, selected #1094 cold replay, Lean proof,
reference dense native backend, Windows execution, or hosted CI was run.
The selected construction is not changed. No complete all-size theorem,
independent human review or maintainer acceptance is established.

The optional `--check-source-history` publication preflight was not run:
this workspace has shallow history and that check requires a full clone.
All declared source pins resolve at the canonical base, which is the
implementation commit's immediate parent; no unreachable PR-head object is
needed. Metadata, Git-blob pins, committed bytes and the Git-free export are
checked separately. A reviewer with full history can additionally run:

```sh
python3 -B scripts/check_research_commit.py \
  --package research/mixed-provider-admission --check-source-history
```

The numerical environment is CPython 3.12.14 on Linux, NumPy 2.3.5,
SciPy 1.17.0, SymPy 1.14.0 and mpmath 1.3.0, all already installed.
The full driver checks these dependency versions before running.
The registered regression itself uses the Python standard library.

Prepared for yssite with substantial OpenAI Codex assistance. Apache-2.0;
all predecessor credits and source-specific notices remain applicable.
