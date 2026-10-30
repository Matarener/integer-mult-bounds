# Native Windows receipt and measurement evidence

Environment: Windows11 build10.0.26300, CPython3.12.11 AMD64,28 logical CPUs,
2026-10-30. Files are in a OneDrive-backed Windows workspace. Background desktop
load and synchronization activity were not controlled. The missing load-average
API is recorded as `load:null,load_status:unavailable,load_reason:api_absent`;
it is not recorded as zero load.

Canonical main was refreshed before this round:
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision8, selected #6030.
Selected source-binding orientation passed. PR6204 was OPEN at
`9889f94b6ed045c1069b2e6f7e4471d0322f2f16`, with no review comments at the
exact-head check. A local ancestry-only merge retains its source objects while
the tree stays main plus this package; no upstream merge or closure occurred.

## Frozen protocol and actual result

The canonical Discussion claim fixed one official primary workload, nine
alternating pairs of batches and five fresh complete processes per side before
timing. The archive was generated once from the pinned base with the official
exporter. Its529 files,13,701,120 bytes and SHA256
`97d88fe02c1538ecd3570ff028bf1cfea268ced91d9ae811c738701c41e25767` match the
original primary archive exactly. Both measured exporter hashes match the
original PR6204 receipt before timing:

- Baseline: `7126afaebff2328b8d64ba1ce992c497103820284f52d4590a558f97f13965fe`.
- Candidate: `68d1a58056c8ab83690b11833d7e362d5e3b2b2632274415b240c676293547e4`.

The wrapper ran exactly one real90-command experiment. All commands completed
declaration checking, emitted byte-identical output within the experiment and
had empty stderr. The archive hash stayed unchanged. No sample was dropped,
no extra warmup was added and no timing-based repeat occurred. The new wrapper's
authentication is before the frozen benchmark; timed boundaries are unchanged.
All45 observations per side remain in BENCHMARK-WINDOWS.json.

| Observation | Baseline | Candidate |
| --- | ---: | ---: |
| Overall median |158.617000 ms|150.552200 ms|
| Minimum |154.541200 ms|146.974500 ms|
| Maximum |163.255000 ms|153.886900 ms|
| Paired batch median wins |0|9|

The observed median reduction is5.084448703480715%. The raw ranges do not
overlap in this experiment. This is a host/workload observation, not a universal
percentage, statistical acceptance threshold or scientific speed claim. The
original macOS7.46% observation remains its author's separate result.

## Reporting controls and corrections

Ten unit control groups cover absent/available/unsupported/unexpected telemetry,
the frozen late failure after a simulated completed90-command result, preservation
of all fields by the wrapper, both output guards and the exact alternating order.
Ten synthetic receipt-corruption controls reject missing/nonpositive samples,
wrong medians/reduction/source/archive/output, fabricated zero load, failed
commands and a foreign terminal separator. They run no timing subprocesses.

The initial unit attempt encountered sandbox TEMP permission errors before its
checks. Local controls and registered runs use process TEMP/TMP pointed at the
writable workspace parent; neither source nor benchmark conditions were changed.
The single real comparison used that same process environment for both arms.

The first validation of the successful native receipt found a cross-platform
comparison defect in the new verifier: original macOS stdout ends in LF, while
native Windows stdout ends in CRLF. The original benchmark's strict within-run
byte equality already passed. The corrected cross-host validator accepts exactly
the pinned one-line LF output or the same bytes with terminal CRLF, with an
explicit CRLF positive and vertical-tab rejection. It uses no broad whitespace
normalization. All90 native samples and the original captured stdout are
unchanged; the benchmark was not rerun. Only the JSON container's physical
line endings were normalized to LF for Git, preserving every parsed value.

Root reviewed the wrapper, exact sources and verifier. Frozen measurement
functions and all candidate/baseline source bytes are unchanged. Registered
warning-strict normal and optimized checks both passed, validating the same
retained native observation without rerunning timings. Metadata/pins and the
14-file committed-byte/source-history preflight passed. The final diff adds only
this package. No positive timing threshold is enforced by the verifier.

No secondary workload, Linux host, historical mathematical verifier, selected
native supplier or multiplication theorem was executed. Hosted CI and human or
formal proof-kernel acceptance are separate and unclaimed. Source integrity
does not transfer the predecessor's scientific acceptance.

The final overlap attempt encountered a transient GitHub HTTP2 Discussion-read
failure and reported its stale fallback explicitly. A read-only retry succeeded:
358 open PRs at04:17 UTC,5978 Discussion records at04:22 UTC and the complete
8625-note HEAD inventory. Its matches were the predecessor/handoff, an unrelated
older helper and this investigation. No competing receipt repair was identified;
this is bounded coverage, not a novelty guarantee.
