# Preserve completed Windows export-benchmark receipts

PR6204's benchmark calls `os.getloadavg()` after all measurements and before
writing its receipt. Native Windows CPython has no such attribute, so the
otherwise completed result is lost at this final environment-reporting step.
This package adds a portable entry point around the unchanged measurement
functions. An unavailable load average becomes explicit null/status metadata;
available values are retained and unexpected failures still propagate.

The old and candidate exporter scripts, their import helpers, the benchmark
functions and original primary receipt are byte-identical retained sources.
The candidate is the exact pending PR6204 exporter, not the old main exporter
under a new name. No shared exporter or frozen predecessor file is changed.

## Evidence

[BENCHMARK-WINDOWS.json](BENCHMARK-WINDOWS.json) records one native Windows
comparison using the original fixed protocol: nine alternating pairs of batches,
five fresh complete CLI processes per side per pair, all90 observations retained.
The official529-file,13,701,120-byte export has SHA256
`97d88fe02c1538ecd3570ff028bf1cfea268ced91d9ae811c738701c41e25767`, matching the
original primary workload. There is no timing-based rerun or sample exclusion.
[VALIDATION.md](VALIDATION.md) records the observed result and its host limits.

On this Windows11/CPython3.12.11 host, the complete-command medians were
158.617000 ms before and150.552200 ms after, a5.08445% reduction. All nine
paired batch medians favor the candidate. The45-sample ranges are
154.5412–163.2550 ms and146.9745–153.8869 ms, respectively. These observations
support the predecessor's change on this one host/workload; they do not transfer
its macOS percentage or establish a universal speedup.

The regression controls reproduce the original late failure after a simulated
completed90-command result, then prove the wrapper preserves every measurement
field when load telemetry is absent. They also cover available values, supported
unavailability, unexpected exceptions and output preservation. These simulations
test reporting; they are separate from the90 actual benchmark commands.

Registered normal and optimized checks validate source bindings, reporting
controls and the arithmetic/protocol of the retained native receipt. They do
not rerun timing or impose a performance threshold on CI. Byte authentication
does not constitute a new proof of exporter equivalence or a scientific replay.

## Reproduce

From the repository root, using CPython3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/windows-export-benchmark --check-only
python3.12 -B scripts/research_package.py --package research/windows-export-benchmark
python3 -B scripts/check_research_commit.py --package research/windows-export-benchmark --check-source-history
```

To perform a separate host measurement, choose new external paths:

```sh
python3.12 -B scripts/export_research_package.py export --package research/p104-designer-toolkit-v2 --ref a5bff3bf133e482541c09eba4e773884bdb2b1b7 --output /tmp/toolkit-benchmark.tar
python3.12 -W error -B research/windows-export-benchmark/benchmark.py --archive /tmp/toolkit-benchmark.tar --output /tmp/windows-export-benchmark.json
```

On Windows, replace `/tmp/...` with actual writable external paths. The wrapper
refuses existing outputs and paths inside the actual checkout. The source
benchmark still uses empty PATH, strict stderr/output checks, complete declaration
checking, alternating side order and archive hash preservation. Its measurement
functions are loaded from authenticated source with optimization disabled.

## Scope and provenance

Base main is `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision8,
selected #6030. PR6204's exact head is
`9889f94b6ed045c1069b2e6f7e4471d0322f2f16`. An ancestry-only local merge retains
that pending source for cold-clone provenance; its shared-code tree is not
imported. Only this new package differs from main. No upstream PR is merged or
closed and the selected frontier is unchanged.

The [canonical claim and finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19284816)
records the protocol before measurement and live overlap. The secondary export,
other hosts, historical scientific verifiers, native suppliers and a new kappa
are outside scope. The performance observations apply to this host and workload;
they do not establish a portable percentage or kernel/human acceptance.

## Open next questions

Repeat the pinned original comparison on a separately declared Linux host or
another storage/CPU environment, retaining every sample. This would distinguish
host effects from a broadly reproducible timing difference. A separate native
measurement is required; the Windows and original macOS observations cannot
supply it. [TASK.json](TASK.json) records the same first step and blocker.

## Attribution

Prepared by AAAmirinu with substantial OpenAI Codex assistance, including
parallel wrapper/control work and root review. Apache-2.0. Credit Nick Petalas
for PR6204's measurement design and archive-index reuse; Tekalign/PR3138 for the
exporter; Ali Romman, roger-sato, Mihir Srivastava,
josecarlosgonzalezroque-design, Douglas Colkitt and the retained exporter and
Git-reader authors. Their notices and exact source bytes are preserved.
