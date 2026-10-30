# Validation and reproducibility

## Current evidence index

The current hashes, exact commands, stdout/stderr and results are in [followup-validation.json](logs/followup-validation.json). This follow-up to `9946b1c42466ada889c10cd0cea7522d6360a63b` corrects one explanatory Stone paragraph, adds a semantic mutation for the original #4436 comparison, and updates its verification description. The numerical certificate, source checker, enclosure oracle, RESULT.json and SOURCES.json are unchanged. The theorem and its argument are unchanged.

| Evidence | Receipt | Scope |
| --- | --- | --- |
| Registered replay and metadata | [current run record](logs/followup-validation.json) | All four registered commands, with the new #4436 control; source hashes identify the executed bytes. |
| Optimized mutation controls and deleted-comparison attack | [current run record](logs/followup-validation.json) | A one-count returned-histogram mutation must reach the original-Flow comparison. Removing that comparison makes the control fail; normal and optimized modes are distinguished in the record. |
| Independent rational enclosures | [normal receipt](logs/claude-enclosures-normal.json), [optimized receipt](logs/claude-enclosures-optimized.json) | Unchanged verifier/oracle bytes; 16 log and 127 exp arguments. The current registered run also repeats the normal oracle check. |
| Committed export and Git-free changed-control replay | [current run record](logs/followup-validation.json) | The changed mutation suite is replayed from an exported tree without Git. Earlier full export replays remain evidence for unchanged direct entry points. |
| Written theorem and review | [PROOF.md](PROOF.md), [review findings](REVIEW.md) | Scoped analytic argument with Stone's theorem as an external input; corrected prose makes no quantitative-rate claim. |

The registered replay passed in 75.175 s and metadata in 0.300 s. The isolated mutation suite passed in normal/optimized modes in 31.698/31.589 s; deleting only the original-Flow comparison caused the intended control failure in 1.439/1.541 s. Both positive independent-source baselines passed. All five unchanged numerical/source files were compared byte-for-byte with `6310550e`; the proof differs in exactly one explanatory paragraph. Internal review found no unresolved blocker. At scientific follow-up commit `309eff43c247b711026eda5e5629409a89ff6242`, committed-byte/source-history and official export/check commands passed for 47 package/input files. The changed mutation suite then passed in isolated optimized mode without Git in 33.424 s; all 48 exported files, including the export manifest, remained byte-identical. The subsequent evidence commit adds only this record and the consolidated log, without changing scientific files.

`followup-validation.json` is the current response record. The `claude-` receipts below identify the first response at `553198839618962e07519b51cb3bbe808ca6f1dc`; they do not exercise the new #4436 mutation. Unprefixed receipts identify the initial `ff365dba` evidence. Earlier numerical receipts still apply where their scientific hashes match unchanged files; historical proof/control hashes must not be mistaken for current hashes. No original receipt was replaced.

Base and last upstream refresh: `721c03822c421b7f7fcbb2598993b947c4d88419`, 2026-10-28. Priority revision 8. The branch adds only `research/direct-flow-leaf-saturation/`; frozen predecessors and the selected record are unchanged.

## Reproduction and evidence reuse

Python 3.12, standard library only. From the repository root, run the four checks serially with the registered entry point (observed total about 75 seconds):

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-leaf-saturation
```

The runner enforces Python 3.12; a default `python3` selecting 3.13 fails its version gate. For an exported tree without Git, run these direct commands from the export root:

```sh
python3.12 -B research/direct-flow-leaf-saturation/verify.py --expect research/direct-flow-leaf-saturation/RESULT.json
python3.12 -B research/direct-flow-leaf-saturation/independent_source.py
python3.12 -B research/direct-flow-leaf-saturation/test_controls.py
python3.12 -B research/direct-flow-leaf-saturation/test_enclosures.py
```

The JSON run manifests preserve the additional optimized-mode commands actually executed. Metadata-only validation uses the registered command with `--check-only`; it does not execute the mathematical checks.

Reusing these receipts requires matching the scientific hashes and predecessor pins. Changes to the proof require renewed argument review; changes to code, numerical data or inputs require the affected numerical/source checks and updated receipts. Documentation-only navigation edits require link, claim-consistency and metadata checks plus confirmation that the scientific bytes remain unchanged. Export checks establish availability and integrity; they do not prove the theorem.

## First review response: historical validation

The first response addressed the six findings on `ff365dba6911ce615bec76e8d1f149faf1fe16ca`; [REVIEW.md](REVIEW.md#claude-review-findings) maps scope and evidence. All `RESULT.json.parameters` values compare exactly equal to that snapshot. The receipt's source-check labels changed to report histogram equality and fixture sensitivity accurately. The finite source domains remain G≤3.

The following Python 3.12 runs all exited 0. Commands, environment and final scientific-source hashes are in [logs/claude-validation.json](logs/claude-validation.json):

| Check | Seconds | Output |
| --- | --- | --- |
| metadata | 0.282 | [log](logs/claude-metadata.log) |
| registered | 75.068 | [log](logs/claude-registered.log) |
| optimized | 14.372 | [log](logs/claude-optimized.log) |
| independent-optimized | 0.155 | [log](logs/claude-independent-optimized.log) |
| mutations-optimized | 30.389 | [log](logs/claude-mutations-optimized.log) |

The first response expanded the registered replay to four commands, including the independent rational enclosure test. Normal and optimized oracle checks additionally passed in 28.674 s and 27.920 s with identical receipts; [timings](logs/claude-enclosures-timing.json), [normal receipt](logs/claude-enclosures-normal.json), [optimized receipt](logs/claude-enclosures-optimized.json). They cover 16 integer logarithm arguments and 127 distinct rational exponential arguments, and reject all three reported remainder faults. Their receipts identify the loaded verifier SHA and exact argument-domain digest. This independently certifies finite-domain enclosure containment, not all-input correctness or the asymptotic theorem.

Both standalone source checkers reject altered source bytes. In this first response, re-pinned empty and terminal-truncated #4467 branches were rejected by the #4467 histogram comparisons, in normal and optimized modes; this evidence did not guard the original #4436 comparison. This separates source semantics from checksum failures and from fixture sensitivity. Fixed-root-bracket and corrupted-receipt controls remain separately labelled.

The final internal review found no blocking issue in the updated proof, source binding, mutation tests or oracle mathematics. Primary numerical functions were compared by AST against the reviewed snapshot and are unchanged; only `finite_law` changed in verify.py. The oracle's last change adds the loaded source SHA to its receipt and was separately reviewed. The earlier README's “adds eight”→“checks eight” wording avoids implying eighteen distinct source ranks; this prose-only change affects no evidence.

## First response: committed export and Git-free replay

Scientific follow-up commit: `553198839618962e07519b51cb3bbe808ca6f1dc`. Committed-byte comparison with `--check-source-history` passed for all 41 package/input files, with the original base as the source-history ancestor. The official exporter and archive check both reported `PASS_RESEARCH_EXPORT` for those 41 files:

```sh
python3.12 -B scripts/check_research_commit.py --package research/direct-flow-leaf-saturation --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/direct-flow-leaf-saturation --ref 553198839618962e07519b51cb3bbe808ca6f1dc --output /tmp/leaf-saturation-reviewed.tar
python3.12 -B scripts/export_research_package.py check /tmp/leaf-saturation-reviewed.tar
```

The archive was extracted into a fresh directory, using an absolute Python 3.12 executable with PATH set to an empty directory and no Git available. All four direct commands passed: primary certificate 15.962 s, independent source checker 0.090 s, mutation controls 31.220 s, and independent enclosure checks 28.117 s. [logs/claude-portable-results.json](logs/claude-portable-results.json) records exact commands, exit codes and links to their logs. The scientific bytes are exactly the commit above; the subsequent evidence commit adds only these logs, this validation record and model attribution. Final publication-byte and export checks are repeated after that evidence commit.

Pre-publication refresh at 2026-10-28T12:34:31Z found canonical main unchanged at `721c03822c421b7f7fcbb2598993b947c4d88419` and no guidance/priority change. A bounded live check of the 100 most recently updated PRs (all states) and 100 Discussions reached back to October 28 00:24Z and October 25 03:58Z respectively, overlapping the earlier complete body snapshots. Exact predecessor and saturation-term checks found no new competing saturation result; this is body-level coverage, not a claim to have reviewed every diff or reply. Existing #6118 was confirmed open and draft before the update.

## Historical documentation consolidation checks

The documentation commit `9946b1c42466ada889c10cd0cea7522d6360a63b`, following `6310550e932de70243fc2aaab6f4885688b6fe21`, changed only README.md, REVIEW.md, CLAUDE-RESPONSE.md and this file. A Python 3.12 link/anchor scan passed all 56 relative links in those documents. SHA256 checks matched all eight scientific files to `logs/claude-validation.json` and `553198839618962e07519b51cb3bbe808ca6f1dc`; byte comparisons confirmed all 28 logs unchanged from `6310550e`. Package metadata/source pins and `git diff --check` passed. Independent AI documentation review preserved the original limitations and corrected wording that had overstated the executed drift controls. Positive drift is certified; no nonpositive-drift test is claimed.

No scientific replay was rerun for this documentation-only change; the then-current scientific receipts applied to identical bytes at `9946b1c`. The later Stone/control response is indexed separately above. Committed-byte/source-history and export checks are performed on the documentation commit before publication. Reproduce the metadata and committed-byte checks with:

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-leaf-saturation --check-only
python3.12 -B scripts/check_research_commit.py --package research/direct-flow-leaf-saturation --check-source-history
```

## Hosted CI

The previously opened draft #6118's hosted run at `ff365dba` had a failed planning job and skipped replay. Its [actual job log](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/40681403297/job/122792722146) reports two failures in `test_research_current_status`: the old selected-family CI text and an exact bold-value match. The shared files involved are unchanged from base. This is separate from the passing package replay; no unrelated suite or shared documentation repair was added here. The subsequent run at `6310550e932de70243fc2aaab6f4885688b6fe21` has the same two failing tests and skipped replay, confirmed from its [job log](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/40689120787/job/122819086604): 678 tests, two failures, 23 skips. These are pinned historical statuses; consult #6118 for later heads.

## Historical validation

The remaining records describe the initial `ff365dba6911ce615bec76e8d1f149faf1fe16ca` contribution. Numerical parameter intervals remain unchanged, but these older receipts predate the source-check and remainder-control improvements.

### Initial local evidence actually run

Environment: 3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]; Linux-6.18.55-x86_64-with-glibc2.41. Standard library only. The retained environment was activated in the isolated contribution worktree. No dependencies were installed.

The exact commands, elapsed seconds, return codes, and final scientific-file hashes are in [logs/validation.json](logs/validation.json). All commands below exited 0:

| Check | Exit | Seconds | Output |
| --- | --- | --- | --- |
| metadata | 0 | 0.207 | [log](logs/metadata.log) |
| primary | 0 | 15.394 | [log](logs/primary.log) |
| optimized | 0 | 16.419 | [log](logs/optimized.log) |
| independent | 0 | 0.098 | [log](logs/independent.log) |
| independent-optimized | 0 | 0.169 | [log](logs/independent-optimized.log) |
| mutations | 0 | 30.049 | [log](logs/mutations.log) |
| mutations-optimized | 0 | 30.11 | [log](logs/mutations-optimized.log) |
| registered | 0 | 43.277 | [log](logs/registered.log) |

Primary and optimized outputs match RESULT.json exactly. The two independent source runs cover ten exact fixtures and reject outgoing-rank truncation. Mutation controls reject altered input bytes in normal/optimized modes, a corrupted receipt under optimized Python, and +1 paid/target multiplicity changes. The registered replay runs all three commands serially and passes; metadata validation is separate from the mathematical proof.

The final proof's reference spelling and canonical Discussion link were normalized after these runs; these prose-only edits change no numerical input or mathematical statement. The scientific hash inventory records the final proof bytes and states that adjustment. The full source root monotonicity bound, corrected citation, independent source integration and mutation controls were already present for these runs.

### Freshness and overlap

Canonical upstream was fetched before selection and again before packaging; both fetched SHAs equal the base above, so no rebase or scientific-source migration was needed. Final cached body refresh: open PRs 2026-10-28T11:20:57Z (376 records), Discussions 2026-10-28T11:22:05Z (5,771 records), complete pagination with no warnings. The earlier closed/merged snapshot at 11:11:49Z has 5,222 records. All 8,348 tracked local note paths were searched; the new package adds two notes. No additional saturation proof was found. A separate live read confirmed the user's [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19240402). Searches cover bodies and local top-level notes, not every diff or historical source.

### Verification scope

The finite verifier certifies source bindings, rational numerical hypotheses, and semantic controls. The asymptotic argument is the written PROOF.md using the explicitly stated classical interval local-limit theorem. Internal AI reviewers found no unresolved mathematical blocker; REVIEW.md records corrections, final integration and shared dependencies.

No selected-construction replay, `make verify`, historical heavy suite, Lean, or Docker run is applicable to this isolated package. Explicit finite-depth bounds, stable whole-flow shares, the exact refined-induction ceiling, supplier admission, and all five selected framework assumptions remain unrun/unresolved here. Hosted CI is separate; consult the contribution PR for its actual status.

### Initial committed bytes and portable replay

At scientific commit `9465f263a673d2d86e7262523cbeb0e796f486cf`, the following commands passed on all 26 package/input files:

```sh
python3 -B scripts/check_research_commit.py --package research/direct-flow-leaf-saturation --check-source-history
python3 -B scripts/export_research_package.py export --package research/direct-flow-leaf-saturation --ref 9465f263a673d2d86e7262523cbeb0e796f486cf --output /tmp/leaf-saturation.tar
python3 -B scripts/export_research_package.py check /tmp/leaf-saturation.tar
```

The actual temporary archive path was outside the repository; `/tmp/leaf-saturation.tar` above is the portable equivalent. Both exporter commands reported `PASS_RESEARCH_EXPORT`. Committed-byte comparison reported `PASS_RESEARCH_COMMIT_BYTES`, with source-history commit `721c03822c421b7f7fcbb2598993b947c4d88419`.

After extraction into a fresh directory, with PATH pointing to an empty directory and no Git available, all three direct package commands passed: main verifier 14.383 s, independent source checker 0.094 s, mutation controls 28.189 s. [logs/portable-results.json](logs/portable-results.json) records the actual commands, exits and logs. Their source bytes are exactly the scientific commit above; subsequent packaging adds these logs and this record without changing the proof or checker.

These checks establish committed-source availability, transport integrity and portable replay. They do not prove the analytic theorem. Final publication-byte preflight is repeated after recording this evidence; the PR pins the final contribution SHA.
