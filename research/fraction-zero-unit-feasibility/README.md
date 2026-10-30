# Scoped negative Fraction zero/unit feasibility

**Decision: stop before complete candidate construction. No speedup or kappa claim.** The full current [PR #5848](https://github.com/CrocSwap/integer-mult-bounds/pull/5848) qualifier profiles at 38.314 seconds. Its Fraction error propagation takes 20.053 seconds. A source-bound zero/unit shortcut routine passes correctness, but one fresh full-word comparison measures **20.180 seconds original versus 19.943 seconds derived**: only 0.237 seconds difference. That is about 0.62% of the profiled whole qualifier, far below the roughly 5.75 seconds needed for a 15% complete-stage saving. This is an insufficient-headroom decision, not a universal performance obstruction or verified kernel speedup.

No complete optimized qualifier, first complete B/C pair, six-process benchmark or performance PR was built. The numerical/physical construction, source archives, precision guards, original independent integer backend and selected result remain unchanged. Kappa research, Work 1/2, feeds, agents and automations stay paused.

## Sources and scope

The input is the complete official 97-file PR #5848 export at `66fb6c6b8683b37967e9d7f313b3df99a49d2406`, containing unchanged PR #5831 and nested PR #5826 sources and notices. The exact original Fraction module SHA256 is `a4c743e79c55e9c2ac26deb6d87cb948b1b0fbe942e4f7912ccbfba55db4b32a`; its `error_trace` source SHA256 is `379c0e7c1c5ab7433ab5ad2669c1bda1234dbf0530fc61b21bfbe83528f37f53`.

The prototype reuses immutable Fraction constants and applies exact identities for coefficients ±1 and magnitude changes 0/±1. It preserves generic Fraction arithmetic for every other case. Exact full-module/function hashes, unique replacement sites, ordinary function shape and recursive executable-code binding are required before deriving a function. The frozen files are never edited. The scoped installer restores the original callable on success and exception. `PROOF.md` explains the value/type invariants.

The finite gate precedes the actual audit and any complete candidate. All **241 programs / 10,164 events**, complete traces, signed witnesses, numeric types and unmodified inputs agree. **16 controls** cover returned-output mutation, source/module/type/live/nested-code drift, wrong signs, missing witnesses/rounding/zero-delta arithmetic, original malformed-input exceptions, installation/restoration and a fresh derivation. Normal and optimized gates pass.

The full actual audit compares all **25,984 events / 799 coordinates**, every trace/witness value and type, with unchanged inputs. The complete output digest is `954c7448ff74d78753828e9623ad44c46da9e5ce459420b6e50a5d47294250b9`, weights digest `cf98bf5da5df28ec1ca3ca7e8723d740b98e142f31e94ff7ec36815cc387c373`.

## Reproduce

Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/fraction-zero-unit-feasibility
```

This runs a **fresh finite differential and all 16 controls**, about one second locally. It does not replay the full actual trace, substitute for PR #5848 qualification, establish performance or admit a mathematical theorem. The manifest states this limited coverage explicitly.

The separately opt-in full actual audit is:

```sh
python3 -B research/fraction-zero-unit-feasibility/actual_audit.py
```

It took 42.807 seconds locally and should run only under a fresh serial budget with the original 180-second cap, 1 GiB sampled group RSS and no automatic retries. Do not rerun it merely to validate these recorded results. Its within-process old/derived timers are not fresh-process wall/CPU qualification benchmarks. Ordering, retained output, unflushed caches and unreserved host load limit the timing inference.

## Failures preserved

Two attempts stopped before arithmetic comparison. The first wrapper retained an obsolete 14-member uniqueness count while checking the 98-member PR #5848 export. The official complete export check had already passed. The labelled correction requires both exact counts to be 98 and retains all 97 file/hash/mode bindings.

The second code-binding check compared nested code objects with source-location metadata, rejecting a recompiled comprehension. The labelled correction compares executable structure recursively, including nested bytecode/constants, names, argument layout, flags, free/cell variables, stack/local counts and exception table, while excluding location metadata. Exact source hashes remain mandatory; a new nested-code corruption control verifies rejection.

Original failed receipts, original hashes, reconstructed rejected sources and diagnoses are retained in `evidence/`. Public stderr replaces only the workspace prefix; its public hash and original stderr hash are both retained. Neither correction changes source arithmetic or expected scientific outputs. Every attempt is charged to the common cap. No failed arithmetic differential was repaired.

## Open next questions

The most useful next nomination would require a separately authorized primitive-level Fraction profile and an explicit bound on complete-stage headroom. The current data do not establish which branch, allocation or arithmetic primitive dominates the remaining cost. Repeating zero/unit tweaks or removing independent oracles is not justified by this result. A broader algorithm needs new source/coverage/purity review and finite feasibility before construction.

## Credit

Ali Romman supplied the original precision/error arithmetic and exact integer backend. Retain [PR #5831](https://github.com/CrocSwap/integer-mult-bounds/pull/5831), [PR #5826](https://github.com/CrocSwap/integer-mult-bounds/pull/5826), [PR #5819](https://github.com/CrocSwap/integer-mult-bounds/pull/5819), Adam Gall, ywz65, [PR #2878](https://github.com/CrocSwap/integer-mult-bounds/pull/2878), Mason Hale/[PR #5811](https://github.com/CrocSwap/integer-mult-bounds/pull/5811) and all retained P104/native/compiler/precision notices. PR #5848 and [PR #5839](https://github.com/CrocSwap/integer-mult-bounds/pull/5839) supply the qualifier and Linux baseline. Guard and custody lineage follows [PR #5816](https://github.com/CrocSwap/integer-mult-bounds/pull/5816), [PR #5818](https://github.com/CrocSwap/integer-mult-bounds/pull/5818), [PR #5832](https://github.com/CrocSwap/integer-mult-bounds/pull/5832) and the exact test-only [PR #5761](https://github.com/CrocSwap/integer-mult-bounds/pull/5761) dependency with original authorship/cherry-pick credit. New feasibility work by Chris R / Clear1nsight with substantial OpenAI Codex assistance; no subagents or independent human/kernel acceptance. Apache-2.0.
