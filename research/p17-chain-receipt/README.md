# Disposition receipt: the p17 κ ≈ 0.003 PR chain

**Claim type:** a source-bound overlap and disposition receipt (the overlap-receipt card). **No new κ.**
It makes no closures, no merge recommendations and no judgement of the κ claims. It covers 10 open PRs
on base `2a13eb18`. `RECEIPT.json` records heads, merge bases and per-path blobs.

## The PRs

| PR | Author | Role | Independent coverage |
| --- | --- | --- | --- |
| #4440 | 1337isnot1337 | κ claim 0.00296 (query-thinned productive controllers) | #4455 (arithmetic), #4457 (controllers) |
| #4441 | 1337isnot1337 | κ claim 0.00300105 (thinning plus helper retiming) | #4448 (invoice), #4455 |
| #4446 | 1337isnot1337 | κ claim 0.003001053 (retimed certificate) | #4455 |
| #4447 | 1337isnot1337 | κ claim 0.00300123 (missing three-dimensional contact span) | #4455, #4457 (native word) |
| #4453 | zxv | κ claim 0.00300120 (smaller uniform-rank exponent) | #4455 |
| #4448 | mihir-s-05 | reconstructs #4441's helper tariffs and invoice | |
| #4455 | pinterbanget | arithmetic of all five κ claims | |
| #4457 | Matarener | #4440's controllers and #4447's native word on lifted operators | |
| #4464 | mihir-s-05 | stage-zero premise `[D0, Q] = 0` (#4457's open question 1) | #4466 |
| #4466 | pinterbanget | check of #4464; the translations are forced | |

## Findings

1. **Retention.** Nothing in the set is retained on main. Every added path is absent at base.
2. **Stacked content, not git ancestry.** No κ PR is a git ancestor of another. The five agree
   blob-for-blob on **44 shared paths**. These include the whole `research/query-thinned-controllers`
   package and the docs edits. #4440's changed paths are a subset of those of #4441, #4446 and #4447.
3. **The only differing shared paths are two `SOURCES.json` files**:
   `research/historical-1042-link/` and `research/test-suite-locale-reads/`. They differ **only in the
   per-PR `pin` commit fields**; `git_blob` and `sha256` agree. This was checked locally by stripping the
   pin fields, and the verifier records the allowance.
4. **A docs conflict with #4436.** All five carry the same edits to `docs/ci-verification.md` and
   `docs/research/current-status.md`. #4436 edits the same two files with different blobs, so whichever
   merges second needs a textual merge.
5. **Unique content.**
   - #4446 adds `research/kappa-hybrid-controller`.
   - #4447 adds `research/missing-join-frame`.
   - #4453 adds `research/native-lattice-retiming`.
   - #4440 and #4441 add nothing beyond the shared stack.

## Not covered

- The κ claims themselves. See the coverage column.
- PRs outside the set.
- Merge order.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/p17-chain-receipt --check-only
python3.12 -B scripts/research_package.py --package research/p17-chain-receipt
```

The verifier prints `PASS_P17_CHAIN_RECEIPT`. To compare recorded blobs, fetch `pull/<n>/head`.

## Open next questions

1. **Which single κ PR should carry the shared stack?**
   - *Why it matters:* merging any one makes the 44 shared paths land and turns the others into
     deltas.
   - *First step:* a maintainer choice, outside this receipt.

## Credit

- The authors listed above.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
