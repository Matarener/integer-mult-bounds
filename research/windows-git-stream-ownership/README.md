# Opt-in Windows ownership for streaming Git source reads

This package supplies a **tested streaming Job Object adapter**, integrated
with the exact Git blob reader from canonical main
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. It fixes the observed lifetime
failures **in this opt-in composition**. It does not install a change in the
shared runner, repin an earlier package, or change the selected frontier.

Both normal and optimized native registered runs pass all 25 process scenarios,
the assignment-denial control, and real-Git exact binary/duplicate reads with
and without the adapter. The registered launcher supplies an enclosing Job
Object, so these runs also exercise nested ownership. See the
[normal](evidence/windows-normal.json), [optimized](evidence/windows-optimized.json)
and [portable Linux](evidence/linux-portable.json) receipts. These are
author-checked tooling results, not independent human review or mathematical
acceptance.

## Concrete delta

The frozen reader has a direct-child Windows `kill()`. Once that child exits,
a live descendant can retain its stdin/stdout handles. Killing the exited leader
does not release the pipe, so the response watchdog fires while the reader stays
blocked. Normal completion, malformed replies, early close and the legacy
fallback can also leave descendants running.

`owned_pipe.OwnedPopen` exposes the subset of Popen used by that reader:

1. Create a private kill-on-close job and a closed event gate.
2. Launch the existing isolated `-I -S` gate, passing stdin/stdout handles
   directly to the requested command.
3. Assign the gate to the job before releasing it to spawn the command.
4. Make `kill()` terminate the job and wait for zero active processes. A lock
   makes this stop idempotent when used by the watchdog and cleanup.
5. On context exit, stop the job, reap the gate, and close pipe/event/job handles.
   Assignment failure never releases the gate.

The native structures, startup isolation, Unicode JSON argv handling and
pre-spawn gate come from ywz65's existing `run_windows_command`, with retained
successors. The new part is its stream lifetime interface and its composition
with the unchanged reader. There is no Python-level pipe relay or blob buffering
added by the adapter; the original one-blob streaming, validation and fallback
code executes from the authenticated frozen bytes.

Microsoft documents default CreateProcess descendant membership and
kill-on-last-handle-close in its
[Job Objects contract](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects);
[TerminateJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject)
terminates current members and nested jobs. These OS contracts motivate the
implementation. The finite tests validate the recorded native environment,
not every Windows host policy or process-creation mechanism.

## Source boundary and reproduction

Python 3.12 and Git; standard library only. From the repository root:

```text
python -I -W error -B research/windows-git-stream-ownership/verify.py --require-windows
python -I -W error -B -O research/windows-git-stream-ownership/verify.py --require-windows
python -B scripts/research_package.py --package research/windows-git-stream-ownership
python -B scripts/check_research_commit.py --package research/windows-git-stream-ownership
```

A Windows run prints `PASS_WINDOWS_GIT_STREAM_OWNERSHIP`. On another OS the
default command runs six portable protocol/deadline controls plus real Git,
and prints **`PASS_PORTABLE_CONTROLS_WINDOWS_NOT_RUN`** with
`windows_observations_executed: false`. Passing Linux CI does not run or
certify the Windows adapter. `--require-windows` rejects that reduced coverage.
The registered commands run both normal and optimized Python; optimization
propagates to the fixture workers, and checks use explicit exceptions.

The direct verifier also runs in a Git-free copy of this package. It needs an
installed Git executable only for fresh temporary object repositories.
`baseline/research_package.py` is a byte-identical behavioral control, not a
modified predecessor. Its SHA256 is
`84a45190a6a96c20993a0d4a1045fbf24de660d2e6fef8f8a447bb3d1aa78db6`,
bound to Git blob `48fe9feb4699c09e95505d95c327ea998ac8b3a7` in
`SOURCES.json`. The verifier compiles the authenticated bytes directly rather
than loading a preexisting bytecode cache. The copied reader is needed to keep
the before/after experiment reproducible after a future production repair.

All source rows are historical provenance. The package executes its local
frozen reader and adapter, so there are no live external inputs to repin when
main advances. The repository metadata checker additionally authenticates those
provenance rows. Receipt hashes bind the two new implementation files.

## Evidence and distinguishing controls

The fixture substitutes a controlled Python producer for the Git process at
the Popen boundary. Its protocol and OS pipes are real; it does not claim that
an installed Git executable spontaneously produces the stall.

Before releasing the producer, the observer waits for readiness and retains
native handles to the actual producer, its child, and the adapter's gate where
present. Later PID reuse cannot count as termination. These handles are observed
before any fixture cleanup. Only fixture processes are stopped in teardown.

| Cases | Frozen reader | Adapter composition |
|---|---|---|
| Header, partial payload, absent terminator, blocked write | Producer has exited; child alive; watchdog fired; reader still pending 1.2 seconds later. Terminating that child then releases the pipe and returns TimeoutExpired. | TimeoutExpired returns and all retained process handles stop before teardown. |
| Exact binary success, malformed header, early generator close, first-request exit-129 fallback | Reader returns the expected bytes/error, but child remains alive. | Same bytes/error/fallback count; descendants and gate stop before teardown. |
| Consumer pause of 1.2 seconds between replies | Direct-child positive control passes. | Two exact replies pass despite the pause exceeding the 0.8-second response deadline; no abandoned descendant remains. |
| Assignment denied with native error 5 | Not applicable. | Error retained, unassigned gate reaped, streams closed, requested-command marker absent. |

Six portable cases are no-descendant header/payload/terminator stalls,
binary success, malformed reply and consumer suspension. Eight Windows cases
reproduce the old failure boundaries. Two separate whole-command controls use
the unchanged registered launcher: it stops the stalled experiment at its
15-second outer timeout and cleans descendants after success. Those results
are not credited to the blob reader. Nine Windows cases run the streaming
adapter. The real Git control checks exact NUL/non-UTF-8/CR/LF bytes and duplicate
requests both with the baseline and with the adapter.

The response timer is shortened from 90 seconds to 0.8 seconds only in the
temporary worker. Startup readiness happens before that timer starts. Whole-job
cleanup retains the predecessor's 10-second accounting limit; harness waits are
separate failure bounds. The early-close case retains the frozen reader's
existing five-second leader grace period. This is not a tight latency benchmark.

Native receipts use Windows 11 build 26300 / CPython 3.12.0; the portable receipt
uses Ubuntu/WSL2 / CPython 3.12.3. An initial five-second whole-command control
exited before readiness; the final harness uses explicit absolute script paths
and a 15-second outer budget. The reader's 0.8-second response budget is unchanged.
A disposable baseline-byte mutation rejects before fixture launch, and Linux
`--require-windows` rejects rather than misreporting native coverage.

## Scope, overlap and attribution

The `portable-replay` card is changed from canonical payload comparison to
the explicit Windows source-reader lifetime handoff in
[Discussion #4681](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19152845).
The [canonical scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19170460)
records the correction: the full overlap refresh surfaced two earlier concurrent
audit claims,
[19170424](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19170424)
and [19170434](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19170434).
This work released the duplicate audit scope and supplies a complementary
ownership adapter; its baseline observations are controls, not a novelty claim.

The entry refresh covered 331 open PR bodies, 4,728 Discussion records and all
7,402 tracked in-scope README/TASK/ledger notes, with complete reported
pagination and inventory. It excludes arbitrary historical diffs and unpublished
work. The selected metadata-only baseline passed at priority revision 7,
selected #5413; the complete selected cold replay was not run.

The submission refresh still uses the same canonical main. It covered 332
open PRs at 22:46 UTC, 4,732 Discussion records at 22:48 UTC and all 7,402
tracked notes (plus this package's two untracked notes). The concurrent
return-lifetime audit is now [PR #5461](https://github.com/CrocSwap/integer-mult-bounds/pull/5461);
the other baseline probe is published at
[7a9a2b67e1967ba31b7330031daae186d6b87a86](https://github.com/mihir-s-05/integer-mult-bounds/tree/7a9a2b67e1967ba31b7330031daae186d6b87a86/docs/research/windows-git-pipe-audit).
Their diagnosis is complementary evidence, not an implementation dependency.

Credit **ywz65 / #2469** for the gated Job Object lifecycle and **#2452** for
retained process-handle observation; **Brian / JoyboyBrian / #4738 and #5185**
for the response deadline, POSIX descendant fixture and source-reader lifetime
contract; **Nick Petalas / #2752** for the fallback and source-reader lineage;
**Mihir Srivastava / #4686, #5358 and #5047** for retained Windows pipe,
installed-Git and Unicode argument work; **Douglas Colkitt** for the package
runner; **Paul Romeo, yssite, Arham Tahir, Woklerx and Tekalign** for retained
lifecycle/source/export predecessors. The original source header is unchanged.

Prepared for Mihir Srivastava with substantial OpenAI Codex assistance, one
agent. Apache-2.0; [LICENSE](LICENSE) and [NOTICE](NOTICE) apply. No new kappa, supplier
admission, unconditional theorem or independent human/formal review is claimed.

## Open next questions

1. **Production adoption.** Review whether to factor the shared command launcher
   into a reusable lifetime context and use it in `_git_blob_batch`. Start with
   this Popen-subset contract and the independent concurrent audit fixtures.
   Updating production test seams, source-pin invalidation and all affected
   consumers remains a separate review task. Spawn-error diagnostic equivalence
   is not established: this gate changes the process-launch boundary. This is
   a Popen subset for the frozen reader, not a general subprocess replacement.
2. **Actual deployment.** Bind the adapter to an identified real Git/helper
   invocation under the intended enclosing Job Object policy. Controlled
   producers establish the pipe-boundary failure and repair, not every helper
   chain. Alternate Windows/Python versions, restrictive host policies, owner
   process death during setup, non-CreateProcess descendants and hostile
   breakaway attempts were not tested. Assignment failure is explicitly covered.
