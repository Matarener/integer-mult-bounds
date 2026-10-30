# Faster exact P104 fold solves

This contribution was produced by Nick Petalas. It replaces the repeated
Gauss-Jordan solves in one actual P104 shadow-relay fold with forward elimination
and back substitution. The complete first fold still rejects its first variant,
accepts its second variant and emits the identical 22821-event word. The measured
complete-command results are in [BENCHMARK.json](BENCHMARK.json).

The claim type is an empirical tooling improvement with a scoped solver
equivalence proof and finite regression evidence. No new kappa is claimed.
The output word and its construction are predecessor work.

## Result and evidence

Five alternating complete-command pairs give median wall time **127.86 seconds
before and 89.58 seconds after, a 29.94% reduction**. Baseline range is
123.44 to 132.11 seconds; candidate range is 86.47 to 91.41 seconds. All ten
commands succeed and emit the same complete word and fold report.

[PROFILE.json](PROFILE.json) records an untimed discovery profile. The
retained solver consumes 75.6 of 83.3 profiled seconds. That profile is the first
relocation variant, which correctly rejects as illegal. It is excluded from
the repeated timings. [PROOF.md](PROOF.md) explains why the replacement returns
the identical canonical basic solution over the source prime field, including
inconsistent systems and free variables.

[benchmark.py](benchmark.py) runs five alternating baseline/candidate pairs of
the complete first fold. Its timed region includes fresh-process startup,
source authentication, census and planning, both attempted variants, all retained
checks and output serialization. Every command must succeed and produce the
same full canonical word and fold status. The generated receipt binds the
implementation hashes, environment, samples and output. It is not a hand-written
receipt. Single-host timings do not predict another machine's speedup.

[verify.py](verify.py) compares 1234 complete small systems with the retained
solver, checks the returned solutions and input preservation, rejects malformed
inputs and a changed source, and runs the complete accepted solver variant in
both modes. The registered checks repeat this with optimization enabled.

## Reproduction

Run from the repository root with CPython 3.12 and NumPy 2.5.4:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-fold-elimination
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-fold-elimination --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-fold-elimination/verify.py
```

To repeat the timings, choose an external scratch directory and extract the
retained closure there. The output directory passed to the benchmark must not
already exist:

```sh
tar -xzf research/p104-fold-elimination/toolkit-closure.tar.gz -C "$fold_source_dir"
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-fold-elimination/benchmark.py "$fold_source_dir" "$fold_timing_dir" --pairs 5
```

For a single accepted solve, use `run.py baseline SOURCE_DIR OUTPUT.json.gz` or
`run.py candidate SOURCE_DIR OUTPUT.json.gz`. Add `--whole-fold` to include the
preceding rejected variant and complete first-step driver. All outputs and
toolkit work files go beside the supplied output path.

## Sources and limitations

The source question is Open next question 2 of DreamingOfClouds' [PR6170](https://github.com/CrocSwap/integer-mult-bounds/pull/6170),
at `445fb9124eb3fcb5d4f342c476b9ae3637f185aa`. The measured bottleneck justified
elimination in place of the question's suggested rule caching. The package
retains a minimal 50-file closure, 491345 uncompressed bytes. Every retained
file has its original Git blob and SHA256 in [RETAINED.json](RETAINED.json).
The archive is authenticated before extraction, and source files are checked
before use. The original README and all retained headers preserve their credit.
The published source head is identified by its Git tree and downloaded blob
hashes; it is not added as a local ref or represented as admitted main-line work.

DreamingOfClouds retains the toolkit, fold rule and PR6030/6143/6144 construction
credit. Ali Romman retains PR6167 and the retained-operand pass. The P104,
native, helper, caller, compiler and BIT predecessors retain their attribution
in the original README. Gaussian elimination is standard background; the new
contribution is the measured integration and its equivalence evidence.

The solver supports dimensions at most 4096. The performance measurement covers
the first H705 fold on the shipped PR6030 word, not all sites, arbitrary words,
or the complete rebuild. The retained projection, legality oracle and prices
keep their existing scope. This is not a supplier audit, native replay, finite
certificate of a multiplication theorem or frontier update. All five selected
framework assumptions remain. Independent human and formal proof-kernel review
are unclaimed.

Warning-strict controls expose retained `tkcommon.py` ResourceWarnings from
`json.load(open(f))` while loading profile files. These are unraisable file-finalizer
warnings in unchanged predecessor code. They are not suppressed, and the checks
are not described as warning-clean. New files use scoped file operations.

## Open next questions

- Does the same substitution help every accepted fold and the complete rebuild?
  First compare each emitted word and acceptance status across that full path.
  A separately budgeted run and larger-system coverage remain necessary.
- Can exact factorization reuse help successive Newton systems? First establish
  an equality or controlled update relation between the two actual matrices.
  No such relation is supplied here.

The structured versions and blockers are in [TASK.json](TASK.json).
