# Complete single-pass precision qualification

This opt-in verification package builds on Ali Romman's [PR #5831](https://github.com/CrocSwap/integer-mult-bounds/pull/5831) and its [Linux validation in PR #5839](https://github.com/CrocSwap/integer-mult-bounds/pull/5839). Both complete arithmetic implementations still execute. It retains the actual ideal metadata, local weights, complete error traces and every signed witness from those executions, instead of recomputing the same values solely to compare them. All literal and transpose oracles, actual source controls and original finite differential remain.

See [COVERAGE.md](COVERAGE.md) for the obligation-by-obligation preservation argument and observation lifetime. This changes verification cost only; it does not change the precision theorem, physical construction, five framework assumptions, kappa or selected result. Frozen archives and expected results are unchanged.

## Reproduce

Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/p104-single-pass-qualification
```

The registered command performs the four inherited pre-import source-custody controls, 27 new finite observation controls, and **fresh full qualification**. It authenticates the complete official source export, runs both complete Fraction and exact-integer contracts on all 25,984 events/799 coordinates, compares all observed actual ideal/weight/trace/witness values and executes the original 120-program/4,240-event finite differential and three integer rejections. Both full contracts still run the six original semantic rejections, signed final transpose and literal attaining fixtures. The source's 180-second timeout is unchanged. Expected time on this Linux host is about 40 seconds, subject to host load.

For deliberate optimized validation use the same source-isolated registered runner or the README export procedure. All new guards raise explicit exceptions; they remain effective under `-O`.

## Bounded performance comparison

Run only with separately available local budget in a fresh complete checkout/export. `runs/` must not already contain these labels; an existing or failed measurement is never overwritten or retried automatically.

```sh
python3 -B research/p104-single-pass-qualification/benchmark.py pair
python3 -B research/p104-single-pass-qualification/benchmark.py remaining
```

The first command measures one fresh complete frozen qualification and one fresh candidate, including its 27 new finite controls. It requires **at least 15% less wall AND CPU time** before the second command can run. The second retains the original serial B,C,C,B,B,C order and applies the same threshold to all six medians. Every run has the original 180-second limit, 1 GiB sampled process-group RSS, bounded output, complete scientific-receipt equality, clean private bytecode prefix and before/after source-byte/mode inventory. The cumulative 1,500-second cap includes the fixed prior profiling/finite development cost declared in `guard.py`. OS caches are not flushed. The host is unreserved. Three observations per arm establish a local measurement, not universal or statistical performance.

The inherited four custody controls are a separate small prequalification stage in `verify.py`; their cost is included in registered normal/optimized/export validation, while the B/C comparison concerns the complete scientific qualification. The profile is excluded from benchmark statistics. Full finite actual-corpus comparisons are never replaced with a stored receipt.

## Profiling and feasibility before construction

The unchanged nominated shared-helper group passes all ten tests after exact historical fixture closure. Its 0.287-second fixture setup is only 0.56% of the 51.317-second group bill. Eliminating it could not meet the requested threshold, so shared scripts/tests/fixtures/waits/skips are unchanged. Most cost is required actual historical/negative CLI execution.

Full precision qualification profiles at 61.609 seconds. Extra same-input ideal/error calls account for over 23 seconds in the Fraction reference alone. Before constructing the full candidate, a five-event valid COPY/SCALE/CLEAR fixture passes with both real frozen backends, full fresh output comparisons and 27 input/lifetime/exception/alias controls, normally and under `-O`. A small hardening preserves the original set argument type; both earlier and final finite receipts are retained. These are finite feasibility checks, followed by complete actual qualification.

## Source and independence boundaries

`inputs/PR5831.tar` is the complete official 13-file export at `7c5eb98e7439d778141d63e801e53d4cd7e1d587`, SHA256 `6ad8d8e0463e8e6ea8d503610c3f9ec38108f16092bc479bc1cb6f48683f6ab6`, retained at this branch's own ancestor. It contains the unchanged PR #5826 source at `58f93cf41751920f3d6766a39caccc2974ce18b0`. Original notices and source licenses remain inside the archives. No pending contributor Git objects are runtime dependencies.

No persisted cache, source-result substitution, cross-backend weight reuse, changed arithmetic or sampled witness is introduced. Each observation context is scoped to one successful complete contract, holds full deep copies, binds all exact inputs and is consumed once. The independent Fraction module still loads afresh; only its factory return is observationally wrapped and the factory is restored on success or failure. The original private nested scratch remains writable; the outer authenticated export is read-only and checked. The coverage statement concerns this deterministic frozen source, not fault-injection independence from repeating an identical call.

## Credit

Ali Romman supplied the integer backend, exact dyadic scale proof, explicit contract seam, original qualification and macOS measurements. Retain PR #5826, [PR #5819](https://github.com/CrocSwap/integer-mult-bounds/pull/5819), Adam Gall, ywz65, [PR #2878](https://github.com/CrocSwap/integer-mult-bounds/pull/2878), Mason Hale/[PR #5811](https://github.com/CrocSwap/integer-mult-bounds/pull/5811) and every retained native/compiler/precision notice. The test-only [PR #5761](https://github.com/CrocSwap/integer-mult-bounds/pull/5761) dependency retains Ali Romman's authorship and exact cherry-pick credit. roger-sato/Arham Tahir supplied the historical-source-role test lineage. Guard/custody mechanics follow [PR #5816](https://github.com/CrocSwap/integer-mult-bounds/pull/5816), [PR #5818](https://github.com/CrocSwap/integer-mult-bounds/pull/5818), [PR #5832](https://github.com/CrocSwap/integer-mult-bounds/pull/5832) and PR #5839. New profiling, one-use observation, controls and Linux measurements: Chris R / Clear1nsight, with substantial OpenAI Codex assistance; no subagents or independent human/kernel acceptance. Apache-2.0.

## Open next questions

1. Does another Linux host reproduce the complete-qualification saving? Authenticate the same export and repeat the bounded six-process comparison; retain every observation.
2. Should the source qualifier expose explicit first-pass outputs? A source-owned return interface could simplify the scoped module-factory wrapper. Review the coverage and lifetime rules before any source change, and coordinate with the source author.
3. Can the optimization transfer to a changed word/backend? Only after new source binding, input/operation/ownership mapping and finite feasibility. This package gives no automatic transfer.

Kappa research, Work 1/2, feeds, workers and automations remain paused. The bounded engineering scope ends after this submission/handoff and starts no successor experiment.
