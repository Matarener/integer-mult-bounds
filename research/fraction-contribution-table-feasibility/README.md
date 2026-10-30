# Fraction primitive profile and contribution-table feasibility

**Scoped finding: correctness passes; stop before complete qualifier construction. No performance PR or kappa gain.** This follows [PR #5848](https://github.com/CrocSwap/integer-mult-bounds/pull/5848) and the [released zero/unit experiment](https://github.com/CrocSwap/integer-mult-bounds/pull/5848#issuecomment-6435104002).

A complete unchanged qualification passes with cProfile enabled only around its actual Fraction error trace. That trace makes **26,030,845 `_from_coprime_ints` calls, 10,396,952 `_add` calls, 7,892,384 `_mul` calls and 2,579,750 coefficient updates**. The profiled trace costs 65.737 seconds and whole qualification 86.794 seconds; instrumentation inflates these times. They are not benchmark observations and cannot be directly compared to the unprofiled 39.015-second complete median.

## Exact table and feasibility result

The prototype tabulates the pure local result `(new coefficient, weighted increment A, weighted increment C, unweighted increment)` as a function of exact Fraction values `(old coefficient, scalar, source coefficient, weight A, weight C)`. Canonical numerator/denominator pairs form the complete key. Misses use the original Fraction arithmetic. Every score/row update, rounded site, peak/witness, signed hash and original independent integer operation remains active. Each trace creates a fresh bounded FIFO table; it shares no answers across backends or calls. See `PROOF.md`.

All **241 finite programs / 10,164 events** compare complete values, witnesses, types and unchanged inputs at capacities **0,1,2,16384**: 964 complete differential comparisons. All **34** key/hash/capacity/eviction/source/exception/mutation/restoration controls pass normally and under optimization. The previous finite harness recompiled four unchanged functions per program; the final harness derives those same four functions once and explicitly checks fresh table lifetimes across repeated calls. No numerical case is removed.

Two separately labelled full actual audits preserve every trace/witness value/type and input on **25,984 events / 799 coordinates**:

| Table | Original trace | Derived trace | Hits | Misses | Evictions |
|---|---:|---:|---:|---:|---:|
| 2,048 entries, dictionary FIFO | 19.996 s | 16.578 s | 1,934,536 | 645,214 | 643,166 |
| 16,384 entries, OrderedDict FIFO | 20.251 s | 14.600 s | 2,252,966 | 326,784 | 310,400 |

The first result had insufficient whole-stage headroom. The plan was reassessed before any complete construction, allowing one final bounded size/constant-time FIFO test under the unchanged resource cap. Both prototypes and the reassessment remain in evidence. These are single ordered within-process comparisons, not fresh-process wall/CPU benchmarks, medians or a causal separation of capacity and container effects.

## Complete-cost decision

The larger table removes 5.652 seconds in its observed trace comparison. Against PR #5848's complete wall median of 39.015 seconds, that is only **14.49% before new checks**. The new full finite/control stage takes about 1.621 seconds. A simple screen gives:

`39.014916 - 5.651933 + 1.620956 = 34.983939 seconds`, about **10.33% modelled saving**.

The required 15% target is at most 33.162678 seconds, alongside an independently passing complete CPU gate. The screen does not justify a complete candidate. No complete qualifier, complete B/C pair, six-process expansion or performance PR is constructed. This is a scoped engineering decision, not a universal obstruction or measured complete-stage/CPU result.

## Reproduce and coverage boundary

Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/fraction-contribution-table-feasibility
```

This performs a **fresh full finite differential at all four capacities and all 34 controls**, about 1.6 seconds locally. It does not freshly replay the complete actual source, profile it, replace qualification, prove a mathematical theorem or certify performance. The manifest explicitly states finite-only coverage.

`actual_audit.py` is separately opt-in: it repeats the fresh original/16k derived full actual trace comparison, about 38 seconds here. Run only with a separately available serial budget, the original 180-second cap, 1 GiB sampled process-group RSS and no automatic retries. No automatic rerun is justified by this handoff.

The input is the complete official 97-file PR #5848 export at `66fb6c6b8683b37967e9d7f313b3df99a49d2406`, including unchanged PR #5831 and PR #5826 archives/notices. Exact module/function hashes, unique source edits and recursive executable-code binding are mandatory. Frozen files are never edited. The scoped installer restores the source callable on success and failure. `evidence/` retains all raw outputs/resource receipts, both table versions, cProfile statistics/data, runtime hashes and the screen.

## Open next questions

A separately assigned follow-up could examine whether source-bound type invariants allow moving the new table's repeated type validation out of the hot loop while preserving failure behaviour. The table currently checks five operand types per coefficient update, about 12.9 million checks. This overhead is visible in the implementation; its exact cost and any saving from relocation remain unmeasured. Such work needs an explicit well-formed-input contract, a proof of internal type preservation, malformed-input fallback and a new feasibility gate. No successor is dispatched here.

Other table policies or exact arithmetic algorithms require a fresh bounded reuse/primitive census and complete memory/time bill. No further capacity trial is authorized by this completed round. Kappa research, Work 1/2, feeds, agents and automations remain paused.

## Credit

Ali Romman supplied the original Fraction/error arithmetic and integer backend. Preserve [PR #5831](https://github.com/CrocSwap/integer-mult-bounds/pull/5831), [PR #5826](https://github.com/CrocSwap/integer-mult-bounds/pull/5826), [PR #5819](https://github.com/CrocSwap/integer-mult-bounds/pull/5819), Adam Gall, ywz65, [PR #2878](https://github.com/CrocSwap/integer-mult-bounds/pull/2878), Mason Hale/[PR #5811](https://github.com/CrocSwap/integer-mult-bounds/pull/5811) and every retained P104/native/compiler/precision notice. [PR #5839](https://github.com/CrocSwap/integer-mult-bounds/pull/5839) supplies Linux observations; verification lineage includes [PR #5816](https://github.com/CrocSwap/integer-mult-bounds/pull/5816), [PR #5818](https://github.com/CrocSwap/integer-mult-bounds/pull/5818), [PR #5832](https://github.com/CrocSwap/integer-mult-bounds/pull/5832) and exact test-only [PR #5761](https://github.com/CrocSwap/integer-mult-bounds/pull/5761) authorship/cherry-pick credit. The previous negative artifact `71f22c77b393e5cc14925c771894dc1a92c8443c` supplies source-binding and fixture lineage. New profile/table/feasibility work: Chris R / Clear1nsight with substantial OpenAI Codex assistance; no subagents or independent human/kernel acceptance. Memoization is standard. Apache-2.0.
