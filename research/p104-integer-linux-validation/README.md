# Linux validation of the complete PR #5831 precision replay

This focused audit independently reproduces Ali Romman's [PR #5831](https://github.com/CrocSwap/integer-mult-bounds/pull/5831) exact-integer precision replay on Linux, retaining the complete original package and nested source archive unchanged. It supplies a source/coverage review, bounded wall/CPU/memory measurements, corruption controls and portable full qualification. It adds no backend optimization or new kappa.

The predeclared success and stop criteria require exact complete results and witness coverage, all original controls, normal/optimized and sealed read-only Git-free qualification, and at least 15% lower median wall **and CPU** time for a useful Linux speed claim. A failing source, receipt, control, stderr or resource condition stops without retry. The 180-second source command limit is preserved, with an additional 900-second cumulative local scientific budget, 1 GiB sampled process-group RSS and bounded output. All full runs are serialized.

## Linux measurements

One unreserved Ubuntu 24.04.5 LTS / Linux x86_64 host, CPython 3.12.3, Intel Core i7-4790. Six serial fresh processes in the original B,C,C,B,B,C order; all samples retained:

| Complete original precision replay | Wall median | CPU median | Wall range |
| --- | ---: | ---: | ---: |
| Fraction reference | 28.363 s | 28.300 s | 28.217–28.716 s |
| Exact integer candidate | 6.440 s | 6.430 s | 6.386–6.488 s |
| Reduction | **77.30%** | **77.28%** | **4.40x wall speedup** |

Kernel peak RSS maxima are 99.38 MiB for the reference and 98.73 MiB for the candidate; sampled process-group peaks are recorded separately. Each fast replay executes every original event/coordinate, complete expected result and all six original controls. Full reference/witness/finite qualification is a separate cost: the first Linux normal run takes **60.47 seconds**, about 101.14 MiB kernel peak RSS. Its extra cost is not folded into the 4.40x production-replay claim. The author's 5.60x macOS observation and this 4.40x Linux observation are distinct; no universal factor follows.

## Coverage before measurement

The original qualification passes first: all 25,984 events / 799 coordinates, complete original/candidate result, actual signed witness dictionaries, ideal metadata and local weights, final signed coefficient and score checks, guards, literal attaining fixtures, six original controls, 120 extra dyadic programs / 4,240 events and three integer rejection controls. It reports scale exponent 55 and the unchanged sufficient guards 26/23/22 (prefix/public/owned). Four additional custody controls reject whole-export, nested-archive, contract and declared-seam corruption before scientific imports, normally and under optimization.

[PROOF-REVIEW.md](PROOF-REVIEW.md) maps the exact arithmetic and every retained check. [COVERAGE.json](COVERAGE.json) records the source-bound scope. Measurement and qualification receipts are reported separately in BENCHMARK.json, VALIDATION.json and evidence/; a fast candidate replay is not mislabeled as full reference qualification.

## Reproduce a fresh complete qualification

Python 3.12, standard library:

```sh
python3 -B scripts/research_package.py --package research/p104-integer-linux-validation
```

This runs source-custody controls and then the **unchanged full `--qualify` scientific computation**, including the Fraction reference and all extra witness/finite checks. It is not a recorded-evidence-only check. Expect `PASS_PRECISION_LINUX_SOURCE_CONTROLS` and `PASS_P104_INTEGER_ERROR_REPLAY` with the complete qualification receipt. The original 180-second timeout is retained. Original normal Linux qualification took about one minute here; timings depend on host/load.

The official complete 13-file export of PR #5831 at `7c5eb98e7439d778141d63e801e53d4cd7e1d587` is retained as `inputs/PR5831.tar`, SHA256 `6ad8d8e0463e8e6ea8d503610c3f9ec38108f16092bc479bc1cb6f48683f6ab6`. Its nested PR #5826 source `58f93cf41751920f3d6766a39caccc2974ce18b0` remains unchanged. No network, Git, third-party dependency, unmerged provenance-object cache or edited frozen input is required at runtime. All outer export bytes/modes are checked after success. The original verifier's nested temporary scratch retains its original writable behavior; this audit does not claim otherwise.

To repeat the complete six-process comparison on Linux with `/usr/bin/python3.12`, GNU `/usr/bin/time` and `/proc`, first pass full qualification at the same source, then choose a fresh work directory:

```sh
python3 -B research/p104-integer-linux-validation/benchmark.py pair --workdir /tmp/precision-linux-fresh
python3 -B research/p104-integer-linux-validation/benchmark.py remaining --workdir /tmp/precision-linux-fresh
```

The first pair must preserve the complete scientific receipt and save at least 15% wall and CPU before the remaining four original-order runs are allowed. Existing run directories are never overwritten; every sample is kept. These commands measure complete baseline/candidate production replays, with identical outer authentication/extraction charged to both arms. They do not time the extra full-reference qualification as the fast path. The Linux development round's qualification and all six samples share the same cumulative guard; reproduction's standalone qualification and new benchmark directory have separately stated costs.

## Mode and export qualification

Full normal, optimized and read-only Git-free isolated optimized qualification pass in **60.47 / 63.86 / 60.26 seconds**. The scientific receipts agree exactly; raw output retains its varying runtime field. The sealed implementation `48479b602545f27e9a35742938be2d5f2bd8459e` runs with `-I -O -B`, empty PATH and an explicit authenticated import root; all **53 exported files** stay unchanged.

One relative-path launcher invocation failed before target entry. Its zero-output exit-2 receipt and exact diagnosis are retained. The absolute-path correction is separately labelled, manually justified and uses unchanged source/expected records/limits; it is not an automatic retry, scientific repair or discarded timing sample. Nine full scientific commands pass; the additional pre-target launch failure is charged. All ten local attempts total **289.30 seconds**, below 900 seconds cumulative. Qualification and export costs are outside the fast-path speed claim.

Public receipts remove only local absolute script paths; the one failed stderr replaces the local workspace prefix, retaining original receipt/stderr hashes and public redaction details. Scientific stdout is unfiltered. Final committed bytes/modes, immediate input ancestry, official export/input integrity and hosted CI are reported separately; later additions change evidence/reporting only.

## Source and overlap scope

Canonical main is `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. The donor assigned Linux validation directly; the task card is refined accordingly. [The source claim](https://github.com/CrocSwap/integer-mult-bounds/pull/5831#issuecomment-6433618407) precedes execution. Targeted PR/body and source-comment checks found no competing Linux follow-up. The author's [released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19209571) explicitly requests Linux reproduction; the neighbouring rounded-gauge transport claim is a different word and scope. Coverage is bounded and does not establish exhaustive novelty or unpublished-work availability.

The initial shallow checkout lacked several declared provenance objects; exact commits/blobs were fetched and all seven declared source hashes and unchanged original metadata checks passed before execution. No frozen manifest was weakened. Full-history preflight remains unavailable; final committed bytes/modes, own-input immediate ancestry and official export/input integrity are checked separately.

The branch retains the same exact [PR #5761](https://github.com/CrocSwap/integer-mult-bounds/pull/5761) test-only dependency used by the source, preserving Ali Romman's authorship and cherry-pick reference. It changes no scientific artifact. This package does not transfer the integer backend to a new word or silently broaden the source operation/scale contract.

## Open next questions

- Does the complete-check gain hold on another Linux host? Authenticate the same source and repeat full qualification plus all six bounded samples. Three samples per arm on an unreserved host are not a universal factor.
- Does a changed word satisfy the dyadic representation contract? Prove its complete source-specific scale and operations before finite feasibility or any full implementation. This validation does not admit successors.
- Does the physical caller meet the retained gauge/reset/owned-return allowances? That is separate research, outside this verification-only task. No kappa work, peer thread, feed, worker or automation is resumed here.

## Credit and limits

Ali Romman supplied the integer backend, exact-scale proof, original adaptation, qualification and macOS measurements. Preserve [PR #5826](https://github.com/CrocSwap/integer-mult-bounds/pull/5826), [PR #5819](https://github.com/CrocSwap/integer-mult-bounds/pull/5819), Adam Gall, ywz65, [PR #2878](https://github.com/CrocSwap/integer-mult-bounds/pull/2878), Mason Hale/[PR #5811](https://github.com/CrocSwap/integer-mult-bounds/pull/5811) and all native/compiler/precision notices in the unchanged archive and NOTICE. New Linux validation for Chris R / Clear1nsight with substantial OpenAI Codex assistance; no subagents. Guard/custody mechanics follow PR5816/5818/5832. Apache-2.0. Same-agent assisted review and hosted CI are not independent human/kernel acceptance. Five framework assumptions, physical reset/owned-return and selected status remain unchanged; kappa research stays paused.
