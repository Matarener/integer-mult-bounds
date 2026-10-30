# Validation and review

Prepared for DLamdata with substantial OpenAI Codex assistance. Apache-2.0. This is local verification and internal AI review, not hosted CI success, human mathematical acceptance or proof-kernel verification.

## Scope and environment

The scientific input is canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. The selected source is `09dd0965711ca7eeb169057a420abab1c9052137`. The selected record and baseline binding checks passed. The four traced execution-chain files have identical Git content at the selected head and base. The code and evidence concern one actual MOVE, alongside a complete occurrence inventory and a source-coverage argument. No full selected replay was run.

CPython 3.12.14, Linux x86_64, glibc 2.41; standard library only. The shared environment was activated without changing its dependencies, managed authentication or remotes. No package installation was needed. Direct runs isolate the source imports from existing bytecode caches.

## Commands actually run

From the contribution repository root, with the activated Python 3.12 interpreter:

```sh
python -I -W error -B research/selected-move-phase-coverage/verify.py
python -I -O -W error -B research/selected-move-phase-coverage/verify.py
python -B scripts/research_package.py --package research/selected-move-phase-coverage
```

All passed. Normal and optimized stdout agree byte-for-byte with [RESULT.json](RESULT.json), SHA256 `1f01afc7022e37b5d5fa54679fb89371254a9bf0c2b11c59d08dfb768f844a51`. The [registered log](logs/registered.txt) includes both exact receipts and `PASS_REGISTERED_RESEARCH_PACKAGE research/selected-move-phase-coverage outcome=completed`. The complete registered invocation took approximately 0.82 seconds locally; its individual command limits are 30 seconds.

The evidence is 512 exact positive columns, 512 detected phase-fault columns, 512 detected address-fault columns, an unchanged signed tableau under the phase fault, and rejection specifically by the retained absolute-phase check. The source inventory is 3,447 MOVE occurrences, 2,887 ordered frame pairs and 11 owned occurrences; only one pair is newly replayed.

## Internal review and resolved findings

An independent native agent derived the Pauli-commutant proof before reading the other review. It derived the first MOVE's closed form directly from the canonical basis and diagonal form, then compared every basis column through a separate monomial-record evaluator. The original independent normal/optimized runs passed in 0.181/0.266 seconds. The lead integrated that calculation with source authentication, inventory counts, address-fault controls and portable replay. The verifier agent reviewed those changes and found no blocking issue.

A second native agent traced the actual registered path through `VERIFY.json`, `verify.run`, `local.replay`, `local.native`, `native_verify.equal` and the final saved-word comparison. It then reviewed the completed README, verifier, receipt and manifests, and independently ran the normal isolated warning-strict command. It confirmed the same receipt SHA256 and unchanged reviewed files.

Review findings resolved:

- Separate existing all-occurrence coverage from the single newly executed pair; distinguish occurrence count from distinct pairs.
- Preserve #5837's scalar proposition and valid physical limitation; correct only its description of the existing phase check and resulting next task.
- State the circuit execution order and keep native phases inside tensor powers while external scalar coefficients remain outside.
- Distinguish dynamically synthesized recipes from a literal arbitrary-width tape program.
- Correct a draft's spectator count from seven to six; all 512 tested columns were unchanged.
- Use fresh import-cache namespaces so `-B` cannot consume stale source-module bytecode.
- Add an address fault as a nonphase control; retain explicit runtime checks under optimized Python.
- Describe the future input as a dynamically lowered recipe, rather than implying a retained emitted tape word.

Both final internal reviews found no blocking issue in the narrowed claim. The producer remains shared because it supplies the actual source recipe; the independent equality oracle does not use either state engine, but shares the declared monomial semantics. The audit does not formally prove the complete compiler/checker implementation.

## Overlap and research decision

The initial completed scan at 2026-10-27T11:03:55Z covered all 7,845 local notes, 437 open PRs, 5,350 Discussion records and 4,943 closed/merged PRs, with complete remote pagination and no warnings. The source-impact target is the exact #5837 handoff, not an assertion of literature-wide novelty. Relevant predecessors #5442 and the selected #5599 proof already contain the elementary lifting argument. The selected-monomial and control-reservation packages concern the older #5413 caller and require a source/layout applicability argument before reuse.

Decision: finish the bounded coverage correction and release the physical implementation task. Repeating a full selected census would not resolve that physical premise. No broader search, new supplier, cost change or family expansion was performed.

## Unrun obligations

No `make verify`, `make frontier5599-verify`, all-map native replay, complete body/controller endpoint replay, physical tape executor, rounded multiplier, Lean or Docker run was performed. All five selected framework assumptions remain. Hosted CI, if a PR is opened, is reported separately on that PR and is not inferred from these local passes.

## Committed scientific snapshot and portable replay

Scientific snapshot `c1187a843403000cb6591f1fb4914f509be96d3e` passed the committed-byte, executable-mode and full source-history preflight for 16 package/input files. Its official export passed integrity checking. Commands:

```sh
python -B scripts/check_research_commit.py --package research/selected-move-phase-coverage --check-source-history --check-modes
python -B scripts/export_research_package.py export --package research/selected-move-phase-coverage --ref c1187a843403000cb6591f1fb4914f509be96d3e --output /tmp/selected-move-phase-coverage.tar
python -B scripts/export_research_package.py check /tmp/selected-move-phase-coverage.tar
```

The artifact location is replaceable; the executed archive was in external research scratch. See [byte/history receipt](logs/scientific-commit-check.txt), [export receipt](logs/scientific-export-check.txt) and [portable receipt](logs/portable-check.json).

After extraction, both direct commands were run from an unrelated directory using an absolute Python 3.12 path, empty PATH, and read-only package/input files and directories. Both produced the exact saved scientific receipt, in 0.242/0.265 seconds. All 17 files including the export manifest retained their bytes and modes. A separate writable copy with one newline appended to the compiler source failed before imports with `source SHA256: research/p104-native-channel/vendor/clifford_exact.py`, exit 1 and empty stdout.

The final publication commit adds only these validation records and provenance documentation to that scientific snapshot. The final committed-byte/export checks are repeated before publication and reported with the final head in the PR. No scientific executable or result changed after the checked snapshot.

A second complete open/discussion refresh at 2026-10-27T11:11:29Z retained 437 open PRs and 5,350 Discussion records with no warnings. #5837 remained at its pinned head. The earlier fully paginated closed/merged snapshot remains timestamped 11:03:54Z. Canonical main was fetched again and remained `de5ec2e7a6074068452f45b1a191b5c72832df4a`; relevant guidance and the selected record were unchanged. No competing correction was found within these text/source checks; unpublished work and arbitrary diffs are outside their coverage.
