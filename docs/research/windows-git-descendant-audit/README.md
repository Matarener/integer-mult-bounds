# Native Windows Git blob descendant-pipe audit

**Result: a confirmed source-reader lifetime gap, not a production repair.**
On native Windows the shared `git_blobs` reader can remain blocked after its
response watchdog fires when the direct Git process has exited and an ordinary
descendant retains a pipe. It can also return a valid result or a protocol error
while that descendant remains alive. This completes the executable-observation
part of the [open Windows handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19152845).
The [canonical claim and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19170434)
tracks this audit. No new kappa or selected-frontier change is claimed.

## Evidence and exact scope

The unchanged reader is compiled directly from source bytes, with bytecode
caches bypassed. The fixture replaces only its Git subprocess with a controlled
Python leader, observes the existing stop callback, and reduces the response
timeout from 90 seconds to **0.4 seconds**. Its parser, fallback gate, generator
finalizer and Windows stop operation are executed as written.

The observer retains Windows handles to the live leader and descendant **before**
releasing the leader. The descendant verifies that its inherited stdin and stdout
are native pipes (`GetFileType == FILE_TYPE_PIPE`). Process termination is
observed using the retained handles, rather than a later PID lookup. Readiness
and result files are published atomically. The worker runs in a separate process
with bounded observation and cleanup, so a stuck source read cannot hang the
audit indefinitely under the tested conditions.

Both normal and optimized CPython 3.12.0 runs on Windows 11 build 26300 confirm
all **14 cases**:

| Cases | Observation before fixture cleanup |
| --- | --- |
| Header, partial payload, missing terminator, blocked large request; descendant holds pipes (4) | Leader exits with status 0. The real watchdog callback runs. Reader remains blocked and descendant remains alive for a further 0.6 seconds. Only then does the observer terminate the descendant; the reader releases and raises `TimeoutExpired`. |
| Same four boundaries; descendant closes both inherited pipes but stays alive (4) | Reader rejects with `ValueError` before the watchdog fires. A living child alone is insufficient to reproduce the stuck read. |
| Valid binary response, malformed response, early close, suspended consumer, legacy fallback (5) | Expected exact reply or rejection returns, but the descendant is still alive. The consumer is paused for 0.8 seconds, longer than the 0.4-second response deadline, without a false timeout. Fallback uses two batch launches and retains the exact bytes. |
| Live direct leader with no descendant (1) | The watchdog stops the direct leader and the reader raises `TimeoutExpired` without observer intervention. |

The explicit descendant termination in the first row is a **causal intervention
after recording the failed deadline**, not reader cleanup. In every case, fixture
teardown subsequently terminates and waits for the exact retained process objects
and closes their handles. A cleanup error prevents a successful audit receipt.
The fixture processes also have finite backup lifetimes. This is not an
abrupt-observer-crash or hostile-process containment guarantee.

[Normal receipt](RESULT-normal.json) and [optimized receipt](RESULT-optimized.json)
record every case, actual reader/probe hashes, elapsed times, exception class,
native pipe types, descendant state and successful fixture cleanup. Times are
observations on this host, not performance bounds. The emitted status is
`CONFIRMED_WINDOWS_GIT_DESCENDANT_GAP`; it does not report a repaired reader.

Three disposable source mutations are rejected in both Python modes:

1. Removing watchdog startup fails the watchdog-observation bound.
2. Changing the deferred timeout to `ValueError` fails exception preservation
   after the deliberate pipe-release intervention.
3. Appending a byte to the yielded payload fails the exact binary-response check.

See [normal controls](CONTROLS-normal.json) and
[optimized controls](CONTROLS-optimized.json). The controls change only temporary
source copies. They demonstrate that an absent deadline, a different error and
corrupted bytes cannot be counted as the recorded outcome.

An intermediate optimized run aborted before the synthetic fallback leader was
ready. Its option-rejection stub could consume the short response budget during
interpreter startup. The final fixture waits for that stub's exit 129 before
returning it to the reader, and observes early worker errors explicitly. That
aborted run is not counted as evidence; the receipts below use the final probe.

## Reproduction

Standard-library CPython on native Windows is required. The scripts fail
explicitly on other platforms; a passing skip is not used as Windows evidence.
Run from the repository root, writing fresh output files outside the audit:

```powershell
python -I -W error -B docs/research/windows-git-descendant-audit/probe.py --output normal.json
python -I -O -W error -B docs/research/windows-git-descendant-audit/probe.py --output optimized.json
python -I -W error -B docs/research/windows-git-descendant-audit/controls.py --output controls-normal.json
python -I -O -W error -B docs/research/windows-git-descendant-audit/controls.py --output controls-optimized.json
```

Each probe normally takes tens of seconds; the no-watchdog mutation deliberately
uses its 10-second guard. Existing receipts are not evidence that a later failed
run succeeded: check exit status and compare the reported source/probe hashes.
The probe intentionally expects the current gap. A future repair should change
these expected lifetime observations, rather than preserve the failure to make
this diagnostic pass.

A fresh three-source snapshot with no `.git` directory and an empty `PATH` also
completed all 14 cases under optimized Python; its source bytes were unchanged
before and after execution. [The snapshot receipt](EXPORT-optimized.json) binds
the same reader and probe hashes. This is a standalone tooling snapshot, not a
registered scientific package export.

This is an opt-in native diagnostic in `docs/research`, not a registered generic
research replay or a hosted Windows CI claim. It adds no shared-runner change.
Both scripts accept `--reader PATH` for a separately retained exact reader file;
the probe needs neither a Git checkout nor installed Git. For historical replay
after the reader changes, extract its bytes using `subprocess.check_output`
and `Path.write_bytes`, not a shell text conversion:

```python
from pathlib import Path
import subprocess
Path('reader.py').write_bytes(subprocess.check_output([
    'git', 'show',
    '32890bc5de034ab8fc93ac88ead7279a6a416d04:scripts/research_package.py']))
```

Then pass `--reader reader.py` and check the SHA256 below. The recorded source
commit must be fetched if absent from a shallow checkout. No external history
is silently assumed by the probe.

## Sources, coordination and attribution

Started from canonical main **32890bc5de034ab8fc93ac88ead7279a6a416d04**,
priority revision **7**, selected result #5413. The `portable-replay` card was
retrieved after reading handoffs; scope is **changed** from canonical-payload
comparison to the explicit Windows source-reader lifetime obligation. A stuck
source read prevents verification from completing, without changing the
mathematical content or granting permission to weaken source pins.

| Source at that main commit | Git blob | SHA256 |
| --- | --- | --- |
| `scripts/research_package.py` | `48fe9feb4699c09e95505d95c327ea998ac8b3a7` | `84a45190a6a96c20993a0d4a1045fbf24de660d2e6fef8f8a447bb3d1aa78db6` |
| `tests/test_research_git_descendants.py` | `599bbd707dfda57cea562a002195ea658e2f03bc` | `ce212173528b31e961f82295c6795e6674b9062d215c30d3d0e148bb4c41f874` |
| `tests/test_research_windows_job.py` | `ddd4c5ab0061a2069aae436590d6b5f1d5ceb461` | `63577aea850d79fb9af2b87f5dce225eeaa34736f2115a6f4061db75f57e7877` |

Only the first source is executed. The latter two supply credited fixture and
native-observation patterns; they are not silently represented as rerun tests.
The initial overlap scan covered 331 open PRs and 4,726 Discussion records with
complete pagination, supplemented by a live all-state Windows/descendant PR
search and the canonical thread. The submission refresh retained the same main
commit and found 331 open PRs (22:34 UTC), 4,729 Discussion records (22:37 UTC),
and all 7,402 tracked in-scope local notes, with reported complete coverage.
Arbitrary diffs, nested vendor
notes, unpublished work and later updates remain outside that overlap claim.

That refresh exposed a [concurrent audit claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19170424)
posted just after the initial snapshot. Its [published ten-case artifact](https://github.com/mihir-s-05/integer-mult-bounds/tree/7a9a2b67e1967ba31b7330031daae186d6b87a86/docs/research/windows-git-pipe-audit)
is separate OpenAI Codex-assisted work under the same account. The four stalled
boundaries here are **independent corroboration**, not a novelty claim or
independent human review. This implementation additionally observes malformed
return, early generator close, consumer suspension and fallback; closes already
inherited child pipes as a control; and deliberately terminates the descendant
after the failed deadline to observe the released read's exception. It uses
retained-handle fixture cleanup rather than the other audit's outer Job Object.
The peer artifact is linked and credited, not imported or silently claimed as
locally replayed. The [separate active streaming-adapter claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19170460)
owns the implementation follow-up; this audit does not duplicate that adapter.

Predecessors retain their attribution: Douglas Colkitt's shared runner;
Nick Petalas's source transport/fallback; Mihir Srivastava's #4686 pipe-error and
#5358 installed-Git checks; Brian / JoyboyBrian's #4738 response deadline and
#5185 POSIX descendant fixture/ownership; ywz65's retained-handle Windows
replay-lifetime work; Arham Tahir, Woklerx and the source-authentication
contributors. The existing [POSIX ownership note](../git-blob-descendant-ownership.md)
and [Windows command Job Object note](../windows-replay-lifetime.md) explicitly
separate these boundaries. This contribution supplies native Windows observations
and a reusable audit; it does not claim discovery of the general OS behavior.

The OS interpretation follows Microsoft's documentation on
[pipe handle inheritance](https://learn.microsoft.com/en-us/windows/win32/ipc/pipe-handle-inheritance),
[file types](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfiletype),
[process termination](https://learn.microsoft.com/en-us/windows/win32/procthread/terminating-a-process)
and [retained-handle waits](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject).
Prepared for Mihir Srivastava with substantial OpenAI Codex assistance, one agent.
Apache-2.0; author-checked evidence, not independent human or mathematical review.

## Limitations and open next questions

This is a controlled process-boundary witness. It does not show that any
installed Git version or promisor helper spontaneously creates these conditions.
The synthetic OID is a protocol fixture, not an independently hashed Git object.
The 0.4-second timeout tests the mechanism, not the elapsed 90-second default.
Separate `git()` calls, legacy `git_source_rows`, other Python/Windows versions,
escaped processes, restrictive external jobs and scientific cold replay are
outside this audit. The registered-command Job Object can bound a containing
verification command; it does not make an individual blob response finish at
its own deadline while that command remains running.

1. **Follow the active adapter's Windows ownership work.**
   This would make a response deadline meaningful even after leader exit. Start
   by adapting the existing gated Job Object mechanism to streamed stdin/stdout,
   retaining the no-start-before-assignment rule and failure propagation. The
   command helper currently returns an exit code, so this is not a drop-in call.
   The native pipe protocol, nested-job policies and bounded teardown must be
   validated before claiming a production repair.
2. **Turn the observations into acceptance tests for that repair.** Require all
   four held-pipe stalls to finish without observer intervention and require
   successful/error/early-close returns to leave no owned descendant alive.
   Keep exact bytes, first-request/no-response/129 fallback, and consumer
   suspension controls. Review shared-control invalidation and historical
   source-pin impacts separately; do not repin old evidence to hide failures.
3. **Test one actual Git/helper producer if a concrete report identifies it.**
   First capture its exact executable versions, helper invocation and pipe
   inheritance. No installed-Git incidence claim is justified by this fixture.
