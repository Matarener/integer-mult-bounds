# Preserve the complete admission checks within the available memory

This runtime adapter addresses a confirmed out-of-memory failure in the retained
whole-owner admission auditor. It changes data lifetime and mutation isolation;
the mathematical predicates, source bindings, mutation bodies, and scientific
report/export construction remain those of the pinned auditor.

The new receiver-sharing local word is frozen in `../native-alternatives`.
This directory does not change that word, its native receipts, the owner fill,
the complete tariff, or any inherited theorem assumption. The runtime repair is
needed to finish its separate bulk admission gate.

## Failure and exact source boundary

`ENVIRONMENT.json` records an 8 GiB cgroup limit, a measured peak of
8,594,599,936 bytes, and one OOM kill. The earlier clock replay's auditor exited
with signal 9 and no diagnostic output. An overlapping receiver audit was then
stopped by the parent agent, preserving its generated inputs for a fresh run.

The replacement `audit_fast.py` is self-contained, because the retained release
builder copies this wrapper as one file. It authenticates the exact scientific
source before compiling it in memory.

| Source | SHA-256 | Treatment |
| --- | --- | --- |
| `audit_allcold.py` | `fa3488b62efdf8a0c37de0ca0caba587b4b036c5f068e002eb04c71c12b9e9b4` | Seven narrowly anchored runtime substitutions |
| `emit_allcold.py` | `549603ca6d28b163a43b2dfaaaa788161c73d7952ab9190289407caca5418c71` | Original source executed unchanged with the inherited pickle-copy wrapper |

All `audit_fast.py` call sites in the inspected complete receiver release use
these two scripts. An unknown or changed auditor/emitter fails its source pin.
The original source files and their compressed input artifact hashes are never
rewritten. The wrapper's own hash and the transformed source hash are recorded
separately in `RUNTIME-ADAPTER.json`.

## Why the transformations preserve the audit

The ancestral template's helper-owner tails are released immediately after
loading that template. Within the complete pinned source, ancestral calls are
used for the stage/replica order, metadata comparisons that exclude `owners`,
and `old['owners'][:2*V]`. The same source asserts `V == 112`. Therefore deleting
only each ancestral `owners[224:]` preserves every read. The actual hosted
template keeps every owner and every pooled slot; the audit still checks all
1,321,920 actual helper roles over 3,240 complete invocations.

The `touches` accumulator was allocated and appended to once per actual helper
role but never read, returned, or exported. Removing its allocation and append
releases no information consumed by a condition. All live `used`, `roles`,
`sigmas`, chronology, frame, and pooled-slot structures remain intact.

The hosted template's digest is computed by streaming all decoded gzip bytes
through SHA-256. The original code retained a second 258 MB decoded byte buffer
after its sole use in that digest check. Streaming has the same byte sequence
and retains the identical comparison with `summary['template_sha256']`.
Compressed source-artifact SHA checks are unchanged.

The default POSIX control isolation forks after the successful positive audit.
Each child receives the same complete template state, executes one original
mutator, runs the original `audit(q)`, and exits before report/export code. The
parent waits for that child before starting the next control. This replaces the
old complete-template pickle round trip with process copy-on-write isolation.
The actual template was parsed independently of the ancestral template and the
provider registry. The pinned `audit(t)` has no reference to global `ct`, and it
does not modify the input template or write files. Its only direct file read is
the immutable data-phase digest. Provider/witness initialization, including the
existing discovery record append, occurs before the positive audit and is not
repeated by children.

Only `AssertionError`, `KeyError`, `IndexError`, `ValueError`, or `TypeError`
raised **by the audit** count as a rejected mutant, exactly as in the source.
The mutator runs outside that exception handler. Accepted mutants, mutator
errors, unexpected audit exceptions, missing rejection messages, signals, and
nonzero process exits all fail the parent. In particular, an OOM-killed child
cannot become a passing negative control. Every original mutator call site and
its body is preserved, and successful control names are appended in the same
order. The scientific report and idle-frame export source suffix is unchanged.

The adapter also checks its own transformation using Python's AST: 76 unchanged
scientific assertions, one equivalent streamed digest assertion, and all 27
original mutation call sites. Runtime branching can execute a different number
of controls from the number of source call sites; the actual report lists every
executed control.

`AUDIT_RUNTIME_CONTROLS=pickle` retains the original complete-template copy
mechanism with the dead-data and digest changes. This is also the fallback when
POSIX fork is unavailable. The memory reduction established for the POSIX run
does not imply the same peak on that fallback. The old shard-count environment
variable does not parallelize the new fork controls; serial execution is
intentional. Progress and resource data are written separately from scientific
outputs. The `max_rss_kib` label describes Linux `ru_maxrss`; another operating
system may use different units for that diagnostic field.

## Replay and evidence

Run the bounded failure-mode fixtures against the exact emitted source:

```sh
python3 -B research/kappa-adaptive-continuation/runtime-repair/fixtures.py \
  --audit-script /workspace/scratch/1a12211da438/adaptive-receiver-full-release/admission/layout/packing74/code/audit_allcold.py
```

Expected status: `PASS_RUNTIME_ADAPTER_FAILURE_MODES`, with 19 checks in
`FIXTURES.json`. These cover all five expected exception classes, a successful
mutant, every expected-class mutator error, an unexpected exception, signals,
nonzero exits, missing receipts, parent aliasing and independent globals, and
streamed hash equality across a chunk boundary. The fixture also checks that
the original scientific report/export suffix is exactly unchanged.

Replay the already emitted receiver audit into a fresh directory:

```sh
python3 -B research/kappa-adaptive-continuation/runtime-repair/replay_audit.py \
  --admission /workspace/scratch/1a12211da438/adaptive-receiver-full-release/admission \
  --out /workspace/scratch/1a12211da438/adaptive-runtime-receiver-audit
```

The output directory must not already exist. The driver copies the three hosted
input files so even the original auditor's idle-frame export stays in fresh
work. It records exact input hashes and the discovery environment, uses the
retained `run_portable.py`, and writes a separate witness discovery record.
The scientific reports are `audit/ASYNC-AUDIT.json`,
`audit/OWNERS-AND-PROFILE.json`, and `audit/IDLE-REMAINDER-FRAMES.json`, alongside
`hosted/IDLE-REMAINDER-FRAMES.json.gz`. Progress and memory measurements go to
`audit/RUNTIME-PROGRESS.jsonl`; `RESULT.json` binds the complete replay outcome.

The complete receiver replay finished with `PASS_FULL_RUNTIME_AUDIT_REPLAY` in
286.12 seconds, exit code 0. It checked all 1,321,920 helper roles and 3,240
complete invocations, and rejected all 25 controls selected by the original
two-provider branch. The parent process peak was 3,802,896 KiB; the largest
control child's peak was 3,804,856 KiB. These are individual Linux RSS peaks;
shared fork pages overlap, so their sum is not a measurement of total memory.
The complete run succeeded under the same 8 GiB cgroup limit.

The retained runtime receipts are copied to `evidence/`, including the exact
input bindings, three scientific JSON reports, the progress trace, the wrapper
transformation receipt, and the full replay result. The generated idle-frame
gzip is bound by the full result and its decoded-payload receipt; it is not
duplicated in this runtime scope. The scientific output hashes are:

| Output | SHA-256 |
| --- | --- |
| `ASYNC-AUDIT.json` | `066d599d294ad01dc08375323c8157a124fb3f865fdbffe218205c4b7e46038e` |
| `OWNERS-AND-PROFILE.json` | `cd3128cf8ca547070f5205f75b3a81c77c70d7e397b418f4ca9956a4839bd9a7` |
| `IDLE-REMAINDER-FRAMES.json` | `eaa9344621f102133fa7f4c01c56c6ed084c092c91066bbd20b9f7e19d86163e` |

`REVIEW-SYMMETRIC.json` and `REVIEW-INVOICE.json` independently bind the frozen
adapter and review the source equivalence and failure handling. The invoice
lane's review can be replayed with:

```sh
python3 -B research/kappa-adaptive-continuation/global-budget/review_runtime.py
```

Successful completion of this isolated owner audit is a finite admission gate.
The parent release still runs the full ordinary/outer admission chain separately.

## Open next questions

The next step is to integrate this reviewed wrapper into a fresh complete
release, retaining the original scientific source and every downstream gate.
Further memory changes should be motivated only by a
measured remaining failure. Portable copy-mode peak memory remains unmeasured;
the safe first check on a non-POSIX platform is the bounded fixture, followed by
a serial full run with sufficient memory.

## Attribution and scope

The original auditor credits OpenAI Codex's independent asynchronous
controller/spectator audit and its two-provider width-seven extension, retaining
the inherited controller checks. The original acceleration wrapper and
`run_portable.py` are inherited unchanged in scientific purpose. This runtime
repair, source analysis, failure-mode fixtures, and replay driver were produced
with substantial OpenAI assistance, with independent reviews by the invoice and
symmetric-transition agents. Repository predecessor credit remains in the
frozen release and native construction. New code is under Apache-2.0.
