# Windows gate lifetime after abrupt owner death

An **unassigned gate that has already opened its event survives abrupt owner
termination until the original 30-second native wait expires**. It does not
start the requested workload. If the owner dies before the gate opens that
event, the subsequent real `OpenEventW` fails and the gate exits. Once native
assignment succeeds, owner termination stops the gate, including a ready
workload and its child after gate release.

This is source-pinned, author-checked native evidence for the specific startup
handoff in [Discussion #1472](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19174060).
It exercises current main's `run_windows_command` and PR5463's opt-in
`OwnedPopen` directly. Their source bytes are unchanged. The isolated-test CLI,
complete Git reader, production adoption and mathematical construction are
outside this replay. There is no new kappa or selected-frontier change.

The final overlap refresh exposed a [concurrent PR5463 setup-death
audit](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19174028).
Its three shared stream-adapter cuts retain that investigation's credit; this
probe's corresponding observations are independent corroboration. This
contribution centers on #4905's **shared-runner** handoff, the separate
**before/after event-open schedules**, and the **kill-on-close-disabled
counterfactual**. The concurrent audit remains separately owned. These are
separate Codex-assisted sessions under the same contributor account.

## Observed boundaries

Both targets have seven cases. Ten boundary/positive cases and four deliberate
mutation cases pass in each complete run on Windows 11 build 26300, CPython
3.12.0 x64. The receipts bind the final probe and both executable source hashes:
[normal](evidence/windows-normal.json) and
[optimized standalone](evidence/windows-optimized-standalone.json).

| Boundary at owner termination | Observed result for both targets |
|---|---|
| Before gate `OpenEventW`, before assignment | Owner's event handle disappears. After the observer releases the gate's **instrumentation** barrier, the real open fails, the gate exits and no workload starts. |
| Gate has opened the event and entered its native wait, before assignment | The retained gate handle is still live after the owner stops. The gate exits with code 1 at approximately 30 seconds from wait entry, with no workload-start marker. The timeout argument remains exactly 30,000 ms. |
| Successful native assignment, before `SetEvent` | The gate stops after owner termination; no workload starts. |
| Released gate with ready workload and child | Owner, gate, workload and child handles all stop before the outer fixture job is closed. |
| Resume the paused owner instead of killing it | Work begins after successful assignment, the workload joins its child and both launchers return zero with all retained handles stopped. |

Two counterfactuals run for **each** target. Replacing the gate's wait condition
with `if False` starts the workload while the owner remains paused before
assignment; the early-work predicate rejects it. Clearing only the
`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` flag before the real native limits call
leaves the ready gate/workload/child alive after owner termination; the owned
lifetime predicate rejects it. The shared and stream implementations execute
their real native APIs in both controls. These are explicit fixture mutations,
not changes to the retained source files or claims about the production settings.

The separate outer containment job remains open during every observation. It
cleans the deliberate survivors **after** their failure is recorded; its cleanup
is not credited to the target. Every recorded fixture process is stopped before
its retained handle is closed. The `resume` case's `observation_boundary` is
`joined_owner_return`; its legacy-shaped `alive_after_owner_death` field records
the state after that normal return, with no forced termination in this case.

## What the probe instruments

The observer executes authenticated source bytes using `compile`, without an
import of a cached source module. In the owner, thin wrappers forward each
native function's ctypes signature and real return value. They pause immediately
before assignment, after successful assignment, or after gate release. The
`Popen` seam substitutes a small tracing launcher for the original `-c` entry;
that launcher executes the **same gate string** with its original arguments.
Its hooks record successful event opening and entry to the real native wait.
The gate retains its event handle; the observer never opens or signals it.
The hooks preserve native thread-local last-error values across marker writes.

This distinction matters: the source files and original gate algorithm are
unchanged, but the execution is instrumented and its timing is controlled.
These are reproducible schedules, not an incidence measurement of naturally
occurring crashes. The pre-open case deliberately pauses just before the real
open so that it can test the other side of the event-handle race.

At each readiness barrier, the observer opens native process handles while
those fixture processes are live. It subsequently uses those same handles for
termination/state/exit-code queries, rather than considering disappearance of
a PID sufficient evidence. Only the known fixture owner is forcibly terminated
for the result. Owner Python `finally` blocks cannot provide its cleanup. An
independent outer Job Object contains every scenario, including the mutants,
and is released only after observation. All cases therefore exercise nested
jobs under this host's policy.

Microsoft's [Job Objects contract](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
describes default child membership and termination when the final kill-on-close
job handle closes. These finite observations cover the recorded native
environment and source schedules; they do not prove every OS policy or launch
mechanism satisfies that contract.

## Reproduce and inspect

Use native Windows and Python 3.12; no Git installation or third-party Python
package is needed to execute the snapshot:

```text
python -I -W error -B docs/research/windows-owner-death-audit/probe.py --output normal.json
python -I -O -W error -B docs/research/windows-owner-death-audit/probe.py --output optimized.json
```

A complete invocation prints 14 case lines, followed by
`CONFIRMED_WINDOWS_OWNER_DEATH_BOUNDARIES cases=14`. Allow about two minutes per
run; two cases intentionally execute the full original 30-second wait. The
checks use explicit exceptions under `-O`, which also propagates to the fixture
interpreters. `-W error` applies to the outer probe. For a single named case,
use, for example, `--target shared --phase before_assign`. A partial run reports
its actual case count and is not equivalent to the complete run. On another
platform the probe rejects with `native Windows required` rather than claiming
Windows coverage.

The optimized receipt comes from a fresh standalone copy with no `.git` and an
empty `PATH`. [The standalone receipt](evidence/standalone-integrity.json)
records its input inventory before/after execution and the additional rejection
of a changed executable source byte. The snapshot only contains this directory;
the interpreter remains the installed, absolute-path CPython executable.
The inventory records the execution-time snapshot; the final notice links,
byte-preservation attributes and validation receipt were added afterward and
do not change its executable inputs.

[SOURCES.json](SOURCES.json) records exact commits, paths, Git blobs and SHA256s.
The two files under `sources/` are byte-identical executable inputs, required
to preserve this experiment if either launcher later changes:

| Input | Exact source |
|---|---|
| Shared job helper and gate | `scripts/research_package.py`, main `32890bc5de034ab8fc93ac88ead7279a6a416d04`, blob `48fe9feb4699c09e95505d95c327ea998ac8b3a7` |
| Opt-in stream owner and outer fixture containment | `research/windows-git-stream-ownership/owned_pipe.py`, PR5463 head `991da9010925914ec64a5293286edb10a7910218`, blob `8150b9a79df8fa59997caffe96f28889a3452c6e` |

This native-only audit is intentionally not registered as a generic Linux
research replay. Its local receipts do not imply hosted native CI execution.

## Task, overlap and attribution

Started from canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority
revision 7. Handoff-first selection took [#4905's explicit pre-assignment
request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134563)
and PR5463's corresponding untested setup-death boundary. The `portable-replay`
card was then retrieved, nonce `be461e0156490165c286b00a0ca6046a`, scope key
`831cc1a3c8f9ff01b197`. **Scope status: changed** from payload/environment repair
to a native lifetime audit: the complete replay needs an accurate cancellation
contract, and the handoff supplies a bounded unresolved question. Success is
the source-bound boundary table and meaningful controls, not a new algorithm.

The initial idea of launch-error preservation was abandoned before implementing
or claiming it, after the refresh found [the concurrent diagnostic
claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19174004).
[The pointer in #4681](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19174075)
keeps these scopes separate. The entry overlap snapshot covered 377 open PR
bodies and 4,786 Discussion records with reported complete pagination. After
sparse materialization, the helper searched all 7,402 tracked in-scope
README/TASK/ledger notes. This excludes arbitrary diffs, nested package sources,
unpublished work and a complete remote closed-PR scan. The final checkpoint is
recorded in [VALIDATION.json](VALIDATION.json).
That checkpoint searched 379 open PR bodies, 4,797 Discussion records and all
7,402 tracked in-scope notes, then read the concurrent claim live. The scope
distinction above was posted to its thread before submission. Canonical main
and the relevant guidance remained unchanged.

The current selected metadata-baseline command was attempted and stopped at
the sparse-omitted `certificates/frontier5413/CLAIM.json`; no selected baseline
pass or mathematical cold replay is claimed. The selected record remains #5413
and its five assumptions. This audit does not edit the selection, catalogue,
shared code, predecessor package or existing test suite.

Credit **ywz65 / #2469** for the gated Job Object protocol and **#2452** for
retained native-handle observations; **Mihir Srivastava / #4683, #4905 and #5463**
for the isolated supervisor, native replay handoff and opt-in streaming owner;
**Nick Petalas / #2906 and #2752**, **Brian / JoyboyBrian / #4738 and #5185**,
**Paul Romeo / #1484**, **Douglas Colkitt**, **Aaron Wang/navinor**, **woklerx**,
**Tekalign**, **Arham Tahir** and the retained lifecycle/reader/source lineage.
The source headers, [LICENSE](LICENSE), [repository NOTICE](NOTICE) and
[stream adapter's original NOTICE](sources/NOTICE-stream) are retained.

Prepared for **Mihir Srivastava with substantial OpenAI Codex assistance, one
agent**; Apache-2.0. This is a newly authored probe from another session under
the same contributor account, not independent human review or a formal proof.

## Open next questions and limits

1. **Is the transient unassigned waiter acceptable?** The measured gap leaves
   no workload running, but immediate cleanup throughout startup is not the
   implemented contract. If that stronger requirement is needed, design
   creation-time ownership or a parent-liveness wait, then use these schedules
   and mutation controls to test it. The design must retain the prohibition on
   workload execution before ownership. This audit supplies no such repair.
2. **Can the stream owner be adopted by its actual consumers?** The diagnostic
   successor and production test seams remain separately coordinated. Start
   from the exact source pins and combine lifetime, launch-error, binary-stream
   and fallback checks in the proposed production composition. This probe
   doesn't rerun the Git blob protocol or the entire isolated-test CLI.

Other Windows/Python versions, restrictive enclosing-job policies, owner death
inside native API calls, external/WMI launch mechanisms, malicious breakaway,
and uninstrumented crash frequencies were not tested. The native five-second
exit observations and original 30-second gate timeout are finite test bounds,
not a universal operating-system scheduling guarantee. No claim about the full
integer multiplication theorem follows from these tooling results.
