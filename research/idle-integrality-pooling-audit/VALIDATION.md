# Validation and limits

Scientific baseline: canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6, selected-record SHA256 `bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`. The entry fetch and three required entry documents were read before task selection. Main inputs and frozen source bytes remain unchanged.

Environment: macOS 26.3.1, arm64; CPython 3.12.14 and 3.14.7; Git 2.53.0. Standard library only. No dependency installation, native build, Docker, Lean or repository-wide suite.

## Executed checks

- `python3 -B scripts/research_baseline.py`: `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. Selected source bindings and diagnostic arithmetic only.
- `python3.12 -I -B research/idle-integrality-pooling-audit/verify.py`: `PASS_IDLE_INTEGRALITY_POOLING_AUDIT`.
- `python3.12 -I -O -B research/idle-integrality-pooling-audit/test_verify.py`: all eight groups passed. This includes 72 square and ten cube calibrations, small exhaustive partitions, histogram domain and normalization controls, five owner-ledger corruptions, and retained/main-source corruption checks.
- `python3.12 -B scripts/research_package.py --package research/idle-integrality-pooling-audit`: `PASS_REGISTERED_RESEARCH_PACKAGE`; both registered commands ran successfully.
- The direct verifier and test suite also passed with CPython 3.14.7.

`RESULT.json` is deterministic mathematical output, not a timing log. All acceptance/rejection decisions use exact integers and fractions. The independent engine confirms the primary PR's two per-call bracket signs, then separates that model from the pooled one. It does not execute the primary DP. The pooled optimizer proof is credited reuse from PR1685; the price implementation and selected capacity recount are newly implemented for this audit.

The selected PR1094 archive's `t16/indep16.py` and `hosting/PROOF.md` were read without execution and compared byte-for-byte to the declared main inputs. SHA256 values matched: `1beb512a1d072f81d3e8e492c8827636029686897093bd433e4d4c92d0c830c7` and `45bb3de8a10298a4cf5a278c3343be22a7d2e735be93a4e9454f24df7275faf0`. Replays use the declared main files, not the archive or a foreign cached Git commit.

## Coordination coverage

Entry `find_overlap.py --refresh` reported 444 open PRs fetched at 2026-10-18 19:16:17 UTC and 2495 Discussion records at 19:17:01 UTC, with complete pagination and no warnings. A targeted cached query inspected PR3729, the adjacent per-call arithmetic PR3737, prior pooled integrality work and relevant board posts. This searches titles/bodies/comments and local notes, not every code diff, and is not proof of novelty. The audit claim was posted as a reply to the existing ceiling finding, rather than opening a duplicate investigation thread.

## Remaining obligations

No actual owner map realizes the pooled histogram here. The literal recount authenticates declared windows but does not derive them from source events or replay native frames, phases, compiler/precision/tape costs or supplier admission. The all-size/analytic interfaces and selected cold replay are unrun. The new domain inference and proof have not received independent human or formal proof-kernel review. A stronger physical bound remains possible, provided its additional source restrictions are proved and stated.

## Publication and source availability

On scientific commit `f044582477d87956c6cb4d17cd8d0fedbdbf4942`, the committed-byte/source-history preflight passed for all 23 package/input files, with only canonical main required in declared source history. The official committed exporter and archive integrity checker passed. Both direct commands passed again on CPython 3.12.14 in a Git-free export under `/tmp`, without network or PR3729's Git objects. This demonstrates declared source availability, not physical or theorem admission.

The pre-submission canonical fetch retained main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`; PR3729 retained its pinned head. Live PR comments exposed a concurrent same-boundary investigation at [Discussion2278](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278#discussioncomment-19022491) and [its preliminary finding](https://github.com/CrocSwap/integer-mult-bounds/pull/3729#issuecomment-6254060645). It independently reported the same counterexample using the retained price engine while this session was implementing binomial pricing. No priority over that finding is claimed. This package adds independent arithmetic implementation, the complete fixed-144 aggregate root bracket, and a literal owner ledger/shared-bin witness. The existing investigation is the canonical scientific thread; the original hub claim is a pointer.

## Final scope after concurrent publication

PR3747 at `98847f9aba65ba835a15725c9f173c04a98788b3` published the same aggregation correction, corrected bracket and its own newly written positive-binomial engine. We retain this independently written replay and literal selected-bin evidence as a public complementary artifact and Discussion finding, rather than opening a duplicate PR. This is separate code with the same mathematical enclosure method, not a different method from PR3747 or independent human review.

The final source census also confirms every literal bin has capacity at most 48. Therefore rank-51 pooled children are not physically realizable within that unchanged bin recipe. The already incorporated `selected-t16-pattern-dual` / PR1129 lineage gives a stronger fixed-inventory screen; this audit cites its scope and does not replay or reopen its completed optimization. The precise objection remains the per-call inference from aggregate integrality in the rank-51 mass relaxation.

The revised registered CPython3.12 replay passed with the capacity inventories and all eight test groups. The added historical-scope README is an authenticated declared input; no predecessor files changed.

Final scientific artifact `d578cb74958c1b22143c647c4fb9790a4d52a4b8`: committed-byte/source-history validation passed for all **24** package/input files. The official final exporter and archive integrity check passed; the verifier and optimized eight-group test suite passed on CPython3.12 in a fresh Git-free export of those exact bytes. No code or scientific receipt changed after that run; later closeout edits concern documentation/coordination only. At the final 2026-10-18 19:33:51 UTC checkpoint, canonical main and the pinned PR3729/PR3747 heads were unchanged.

The planned session cap was 60 minutes, with 15 minutes reserved for final checks. The bounded milestone was reached early and the concurrent PR covered the same correction. We stopped research at that milestone, completed the relevant verification and published the complementary artifact/handoff instead of using the unused budget for a duplicate round.
