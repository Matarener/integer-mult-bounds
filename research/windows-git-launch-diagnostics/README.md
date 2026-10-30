# Preserve launch diagnostics in the opt-in Windows Git stream owner

**Author-checked tooling result; no new kappa.** PR5463's owned Python gate
turns a failure to create the requested executable into gate exit 1. With the
actual blob reader's suppressed stderr, a missing executable, invalid image
or directory used as an executable becomes `ValueError: missing or non-blob
Git source`. The direct reader reports the original native `OSError` instead.

[spawn_checked.py](spawn_checked.py) supplies an **opt-in successor wrapper**
around the unchanged PR5463 owner. It reports successful process creation or
the original `OSError` through a separate temporary JSON file before exposing
the stream. This resolves the launch-diagnostic portion of the
[PR5463 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19170662).
The production runner and all frozen predecessor bytes remain unchanged.

## Exact scope and sources

Canonical base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.
The selected record is PR5413, conditional kappa `0.003027288235`; this work
does not alter that result or its five assumptions.

- [PR5463](https://github.com/CrocSwap/integer-mult-bounds/pull/5463), head
  `991da9010925914ec64a5293286edb10a7910218`, supplies the frozen owned process
  implementation. Its full 25-scenario suite is **not** rerun here.
- The actual `scripts/research_package.py` reader at the canonical base is
  copied byte for byte into `vendor/`, including its gate and retry rules.
- [PR5461](https://github.com/CrocSwap/integer-mult-bounds/pull/5461), head
  `dd30c37b09bc090afa94944cb055b677de2db696`, and the
  [7a9a2b67 native probe](https://github.com/mihir-s-05/integer-mult-bounds/tree/7a9a2b67e1967ba31b7330031daae186d6b87a86/docs/research/windows-git-pipe-audit)
  retain baseline diagnosis and observation-method credit. Their full suites
  are not copied or represented as replayed by this package.

[SOURCES.json](SOURCES.json) pins canonical-main Git provenance.
[VENDOR.json](VENDOR.json) records every standalone copy's original repository,
commit, path, Git blob ID and SHA256. The verifier checks both byte hashes before
importing either implementation. PR5463 is a pending fork dependency: its
commit is not an ancestor of this main-based contribution, so it is deliberately
**not** a Git-resolved SOURCES pin. The original fork bytes were fetched and
compared locally; offline replay authenticates the included snapshot, not its
publication ancestry. This explicit external-source boundary lets an ordinary
fresh checkout and a Git-free export replay without fetching another PR.
Package-local files need no external `VERIFY.json` inputs: the package is
self-contained and its local changes already select its replay.

The handoff-first assignment changes the `portable-replay` card from generic
payload comparisons to its explicit Windows launch-interface request. The
[task card](TASK.json) records the scope, stop rule and next questions.
[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19174004).

## Behavior and boundary

The trusted owner creates a Job Object, starts an isolated `-I -S` Python
gate, assigns the gate to the job, then releases its event. That protocol is
reused, not a newly claimed ownership mechanism. The successor gate calls
`Popen` on the requested argv and atomically publishes either `started` or
the native error fields. The parent then yields the same binary handles or
raises the reconstructed error. No status byte goes through the data stream.

The report wait is bounded at ten seconds **after the owned gate has been
created and released**. Missing, oversized, malformed and unknown reports
fail closed. A transient `PermissionError` opening the report is retried
within that same bound; a persistent denial times out. Reconstructing the
requested executable's `PermissionError` occurs outside this I/O handler,
so an actual denied executable is not retried or converted to a timeout.
The owner stops the job on every setup exception, including
when a requested child started but its success report never arrived. The
existing response watchdog remains separate and still excludes consumer time.
Native creation of the outer gate and filesystem operations are not covered
by this polling timeout. This is not a total wall-clock bound.

The compared diagnostic fingerprint is exception class, `errno`, `winerror`,
`strerror`, `filename` and `filename2`. Traceback identity is not claimed.
The construction uses the documented Windows
[`OSError` native-code mapping](https://docs.python.org/3.12/library/exceptions.html#OSError)
and preserves the distinction between launch exceptions and returned process
statuses described in the
[`subprocess` contract](https://docs.python.org/3.12/library/subprocess.html#exceptions).

| Native fixture | Direct `Popen` on this host | Frozen adapter | Successor |
|---|---|---|---|
| Missing executable | `FileNotFoundError`, WinError 2 | gate exit 1, empty stdout | exact error fingerprint |
| Invalid executable image | `OSError`, WinError 216 | gate exit 1, empty stdout | exact error fingerprint |
| Directory as executable | `PermissionError`, WinError 5 | gate exit 1, empty stdout | exact error fingerprint |
| Missing cwd | `NotADirectoryError`, WinError 267 | original outer-gate error | exact error fingerprint |

These are observed host codes, not hardcoded portability assumptions: the
check compares to direct `Popen` on the executing machine. The three inner
launch failures also run through the actual reader and make one attempt each.
They cannot accidentally trigger its exit-129 compatibility retry.

## Verification

The retained native receipts contain **25 named case groups** in each Python
mode. The complete case arrays agree between normal and optimized execution.

- Four direct/old/new launch comparisons and three actual-reader comparisons.
- Successful launches returning 0, 1, 7 or 129; only the launched 129 performs
  the legacy fallback. The fallback returns two exact 80,000-byte binary blobs.
- Real Git duplicate reads with a consumer pause longer than the response
  deadline; Unicode argv, environment and cwd with uncontaminated stdout.
- Missing report after gate exit 129, missing-report timeout, malformed and
  oversized reports, and native job-assignment denial before command launch.
- Transient report-read denial succeeds on the third attempt; persistent denial
  fails within the startup bound. Real executable permission errors retain
  their original fingerprint instead of entering this channel-I/O retry.
- Retained native process handles establish descendant termination before
  fixture teardown after success, response timeout and early generator close,
  plus a child that started before the missing-success-report timeout.
- Seven portable malformed-report controls and one accepted report.
- Three deliberate regressions are detected: omitted handshake, a banner
  on stdout, and corrupted frozen source bytes.

Source/protocol checks are implementation evidence, not a theorem replay.
The fixtures use controlled Python producers and real Git for valid blobs;
they do not claim a naturally occurring installed-Git hang.

```sh
# Full native coverage; rejects on any other platform.
python -I -W error -B research/windows-git-launch-diagnostics/verify.py --require-windows
python -I -W error -O -B research/windows-git-launch-diagnostics/verify.py --require-windows

# Registered metadata plus bounded normal/optimized replays.
python -B scripts/research_package.py --package research/windows-git-launch-diagnostics
```

Native CPython 3.12.0 on Windows 11 build 26300 passes the full checks;
the direct pair takes about twenty seconds on the observed host.
[Normal receipt](evidence/windows-normal.json) and
[optimized receipt](evidence/windows-optimized.json) retain implementation
hashes, source pins, error fingerprints and every case's outcome.
Non-Windows runs perform source/report controls only and print
`PASS_PORTABLE_CONTROLS_WINDOWS_NOT_RUN`. A hosted Linux pass must not be
reported as a native ownership pass. Publication verification and export
results are recorded in [VALIDATION.md](VALIDATION.md).

## Limitations

This is the reader's nonempty string-argv, binary-stream, context-managed
subset. General `Popen` options, shell/executable overrides, arbitrary Python
argument errors, extreme command-line lengths and every Windows error code
are not certified. The temporary status path adds command-line length and
filesystem I/O. It is a control channel between trusted local components,
not an authentication boundary against a hostile command or same-user process.

Production integration, the full shared consumer/test-seam suite, other
Windows/Python versions, restrictive enclosing jobs, hard owner death during
setup and abrupt parent termination remain separate work. The unchanged
owner's cleanup bounds and error behavior are inherited. Only this author's
checks are claimed; no independent human or separate-agent review, formal
verification or selected mathematical cold replay was performed.

## Open next questions

1. **Production adoption:** combine the reviewed owner and launch wrapper at
   one shared process factory, preserving existing closed-stdin/mock fixture
   seams. Run the current Git-source consumer suites on Windows and POSIX.
   This is needed to fix the shared runner; it requires a separate integration
   patch and full adapter review, not another launch-status experiment.
2. **Host-policy coverage:** execute the same `--require-windows` command on
   a second Windows host and under a restrictive enclosing job, retaining
   native errors and process handles. Such access is the current blocker.

## Attribution and overlap

Credit ywz65 for the gate/Job Object and native observer design; Brian /
JoyboyBrian for deadlines and POSIX lifetime controls; Nick Petalas for the
blob and compatibility reader; Douglas Colkitt for the package runner;
Mihir Srivastava for PR5463/PR5461 and the earlier native probes. Arham Tahir,
Woklerx, yssite, Paul Romeo, Tekalign and the retained source/fixture lineage
remain credited. [NOTICE](NOTICE) and [vendor/NOTICE](vendor/NOTICE) preserve
the source attribution. New wrapper and bounded regression work prepared for
Mihir Srivastava with substantial OpenAI Codex assistance, one agent;
Apache-2.0, with [LICENSE](LICENSE) included.

Initial helper coverage: 375 open PRs and 4,783 Discussion records, both with
complete reported pagination. Sparse local coverage omitted 7,401 of 7,402
tracked in-scope notes. Relevant runner documentation, the central ledger,
the exact predecessor files and the live canonical thread were inspected;
the missing note corpus is an explicit limitation, not a novelty guarantee.
The next integration task stays open; this package does not reserve it.
