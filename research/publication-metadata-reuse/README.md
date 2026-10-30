# Reuse authenticated publication metadata

The complete publication byte/history check can avoid two duplicate Git
processes. `check()` already reads the committed `SOURCES.json` blob and compares
it with the working file. It now retains those immutable bytes for the subsequent
source-history validation. The standalone `source_history()` interface and every
source-commit resolution and ancestry query remain.

This is a measured verifier improvement with a scoped equivalence argument and
finite executable controls. It supplies no mathematical construction, supplier
admission, complete multiplication theorem or new kappa. No predecessor
mathematical verifier is run by this package.

## Evidence

On CPython 3.12.15, macOS arm64, nine alternating baseline/candidate complete
checks per package gave:

| Unchanged package | Baseline median, range | Candidate median, range | Reduction |
| --- | --- | --- | --- |
| `stage-zero-forced-translation` | 121.65 ms, 117.86–132.99 | 99.36 ms, 97.92–102.72 | 18.33% |
| `p104-helper470-twin-rung-removal` | 120.33 ms, 118.24–126.17 | 101.49 ms, 98.93–103.96 | 15.66% |

All 36 timed checks returned identical complete receipts within their package;
no timed call failed. Each call checks the full package/input inventory, exact
working/committed bytes, committed source metadata, shallow-history guard and
all declared source-commit ancestry. These are complete `check()` function times
in a warm Python process. Imports, baseline extraction and CLI startup are outside
the timed region. Mathematical replay is outside the measured workload.

A separate profile attributed 109 of 130 ms to synchronous Git subprocess
calls, including 21 ms in the duplicate metadata reader. For these one-pin
packages, history-specific Git calls fall from five to three and total Git
processes from nine to seven. The host had 18 logical CPUs and load averages
5.76, 3.64 and 2.80 at orientation; other work was active. Alternating samples
have separated ranges. There is no cross-host speed claim.

[PROOF.md](PROOF.md) gives the acceptance argument, bounded retention, failure
ordering, controls and implementation limits. The registered verifier runs the
new tests plus retained history, byte, executable-mode and replacement controls.
Its generated stdout receipt binds all executed test files and their shared
scripts by SHA256, including the exporter and scaffold imported by replacement
controls. [TASK.json](TASK.json) records the scope and next question.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/publication-metadata-reuse/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/publication-metadata-reuse/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/publication-metadata-reuse
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/publication-metadata-reuse --check-source-history
```

Elsewhere substitute CPython 3.12. Git and full source history are required.
Tests create and remove only synthetic temporary repositories. They do not
change project refs or execute predecessor mathematical packages.

For optional timing, first materialize both benchmark packages and their
`VERIFY.json` inputs. Use an existing directory outside the checkout:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/publication-metadata-reuse/benchmark.py --scratch /absolute/external/scratch --repeats 9
```

The benchmark obtains the baseline from immutable Git objects at
`721c03822c421b7f7fcbb2598993b947c4d88419`, compares complete receipts, records
every sample and source hash, and removes its temporary baseline module.
Timing is optional and has no CI speed threshold.

## Open next questions

Does the same saving remain measurable on a second operating system and Git
implementation? Run the same complete-check benchmark on unchanged fixtures,
with imports outside both arms. A second host and materialized inputs are
required. Joint ancestry batching is separate open work.

## Credit

This contribution was produced by Nick Petalas. Credit ywz65 for the publication
byte preflight, Nick Petalas for its original source-history check, roger-sato
for immutable Git source isolation, Douglas Colkitt for the package runner and
the retained source-reader contributors. Reusing immutable bytes is an ordinary
technique; the contribution is its bounded integration, failure controls and
measured complete-check improvement. Apache-2.0. Existing notices are unchanged.
