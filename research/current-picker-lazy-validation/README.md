# Defer unused task-picker validation

This contribution was produced by Nick Petalas.

The current task picker loads the frozen legacy picker in the parent process
before launching that same picker in a child. Move the parent load into the
historical-route branch. Cards already carrying current commands need only the
child execution. The legacy subprocess, its catalogue checks and output, and
historical route validation retain their code.

This is an empirical tooling improvement with a scoped equivalence argument
and finite regression evidence. It supplies no new mathematical bound, supplier
admission or kappa. [BENCHMARK.json](BENCHMARK.json) records the complete-command
measurements, source hashes, Python and host, raw timings and error count.
The recorded median falls from 104.461 ms to 99.598 ms, 4.66% less wall time.
Every one of the nine paired batches improves. Batch-average ranges are
103.434–110.213 ms before and 93.962–105.575 ms after; the paired decreases
range from 3.769 to 9.565 ms. All 180 timed commands succeed with identical
output, and the direct-CLI control agrees. The raw ranges overlap, so the
paired observations and host-specific scope matter. The profile attributes
about 4 ms of the original complete command to the removed parent load;
child startup and catalogue validation remain the main cost.

## Why the checks survive

Before the moved statement, the resolver identifies the exact historical
commands. If none occurs, it returns without using the legacy namespace. If a
historical command occurs, it loads the same exact source and obtains the same
validation function before validating or changing any card. Loading is not
cached between resolver calls. Subsequent calls therefore still read current
source. The CLI always runs its unchanged legacy subprocess before resolving
successful JSON output, and passes through its help and errors as before.

This argument assumes the retained legacy module's top-level definitions and
imports. It is not an equivalence claim for arbitrary side-effectful replacements
of that module, imports by external code of the removed incidental module global,
or concurrent changes to the source tree. No public helper API is documented for
that global. Historical mapped routes may pay the same load on every resolver
call; no performance gain is claimed there.

[verify.py](verify.py) reconstructs the exact pre-change source and checks its
pinned SHA256, authenticates the unchanged legacy source, checks loading at the
actual resolver boundary, compares all 22 live first-step cards and both frozen
route shapes, and exercises seven source/route rejection controls. Explicit
exceptions keep checks active under optimized Python. The existing routing suite
also covers CLI help/errors, exact matching, atomic failure, sparse references,
staged replacements and historical output preservation.

## Reproduction

Use CPython 3.12 and its standard library from the repository root. The local
interpreter was `/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12`.

```sh
python3.12 -I -W error -B research/current-picker-lazy-validation/verify.py
python3.12 -I -O -W error -B research/current-picker-lazy-validation/verify.py
python3.12 -B scripts/research_package.py --package research/current-picker-lazy-validation
python3.12 -B scripts/check_research_commit.py --package research/current-picker-lazy-validation --check-source-history --check-modes
python3.12 -W error -B -m unittest discover -s tests -p test_research_current_assignment.py -v
```

Expected marker: `PASS_CURRENT_PICKER_LAZY_VALIDATION`. Registered checks are
bounded correctness checks; they do not assert a host-independent timing ratio.
To repeat the timing experiment, choose a scratch directory and a new receipt
path. The writer refuses an existing receipt.

```sh
python3.12 -W error -B research/current-picker-lazy-validation/benchmark.py --pairs 9 --repetitions 10 --scratch /tmp --write /tmp/new-picker-timings.json
```

Both sides execute the entire CLI in fresh interpreters, using the real script
filename and root with different authenticated source bytes. The identical
launcher reads and compiles one temporary source file per command. It retains
the legacy child, all its checks and Git queries. Timings include output capture,
JSON decoding and equality checks. Every complete `(status, stdout, stderr)`
triple must agree, and a separate direct CLI invocation must match the candidate.
The script does not write or replace checkout source files. Nine alternating
batches contain ten complete commands per side, 180 timed commands in total.
The measurement is of this source-executed CLI, not a subtraction of isolated
import times. Concurrent host load and the launcher's common overhead limit
transfer of the measured ratio to other environments.

## Scope and next questions

The original `replay-runtime` card is changed from scientific replay to research
onboarding startup. This small improvement helps repeated coordination commands;
it does not accelerate the selected scientific replay. The first improving
implementation is frozen. Canonical base is
`3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority revision 8.
[The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19267797)
records the scope before implementation.

The existing historical picker, catalogue, selected frontier and predecessor
packages are unchanged. No historical scientific suite, native replay, Lean,
Docker, formal proof kernel or independent human review is claimed.

## Open next questions

Does startup loading still matter for the historical mapped routes, where the
resolver genuinely needs validation? Profile those complete commands separately
before changing their execution boundary. Preserving child failure propagation,
source freshness and sparse-reference rejection is the blocker to a broader
startup change. This package supplies no such change.

## Code constraints

The implementation moves one load and adds no cache, recursive call or loop.
The package's bounded verifier handles at most 1,000 cards, four route references,
two route shapes and three source mutants. Benchmark options cap work at 31 pairs
and 100 commands per batch, with a 20-second timeout on each child. Functions are
below 60 physical lines.

Power of Ten deviations apply to the package's Python-managed allocation and
explicit trusted-source execution. Live memory is bounded by the pinned scripts,
the checked catalogue limit and one captured command output at a time. The
trusted picker emits a finite catalogue report; the benchmark rejects output
above 1 MiB after capture. It does not claim a hard capture-memory limit for
an arbitrarily changed child. Temporary fixtures have four files and are
removed by their context manager on both success and failure. Dynamic
execution is needed to compare actual source versions with the same filename;
both versions are authenticated before execution. No arbitrary submitted program
is accepted. The benchmark additionally uses the fixed standard-library module
loader for the local verifier. Replacing these mechanisms would require a new
benchmark contract; no shared runtime or build configuration is relaxed.

## Credit

Ali Romman / PR5378 supplied the current-command wrapper. Mihir Srivastava /
PR4906 and PR5520 supplied startup guidance and historical-ceiling routing.
Douglas Colkitt and the retained sparse-reference contributors supplied the
frozen picker and its reference checks. Deferred initialization is standard
programming practice. This contribution is its measured application at this
specific CLI boundary, with exact-source conformance and reproduction. Existing
source credit lines retain their bytes. New work is Apache-2.0.
