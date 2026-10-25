# Authenticate reused native evidence and actual fresh compiler sources

**Prepare full-release dependencies before expensive gates.** The inherited
outer evidence replay explicitly requires SymPy 1.14.0. The workspace initially
lacked SymPy and MPMath, so an otherwise successful discovery run later stopped
at this import requirement. The parent release runner now checks dependencies
before starting reconstruction or bulk admission. `requirements-full.txt`
records NumPy 2.3.5, SymPy 1.14.0 and MPMath 1.3.0; NumPy 2.3.5 is the version
observed in the workspace, while the original native `RESULT.json` records
Python but does not record NumPy.

The two original pure-Python SymPy and MPMath wheels are included intact in
`wheels/`. `WHEELS.json` records their exact hashes, package metadata, intact
license files, and the actual public-index pip download command. Pip reused
cached wheel bytes and did not print per-file download URLs; the provenance
record does not invent such URLs. `requirements-outer-hashed.txt` supports an
offline hash-checked installation of these two packages. NumPy is a separate
prerequisite and is not bundled. The complete release runner installs the
bundled outer dependencies into its fresh `work/python-deps` directory and
performs a strict preflight before expensive checks.

An optional explicit installation into a separate workspace directory is:

```sh
python3 -m pip install --no-index --no-deps --require-hashes \
  --find-links research/kappa-adaptive-continuation/replay-support/wheels \
  --target /absolute/path/to/new-python-deps \
  -r research/kappa-adaptive-continuation/replay-support/requirements-outer-hashed.txt
```

That directory must be placed on `PYTHONPATH` when using it manually. The full
release runner performs this setup itself. Exact dependency availability is
an execution prerequisite; it does not change the conditional theorem or its
scientific input files.

`native_auth.py` makes the release's optional native reuse boundary explicit.
It accepts a reused run only when every file matches the delivered completed
run byte for byte. For a newly executed native run, it independently hashes
the actual compiler source files and compares them with the original PR3734
source pins; the declarations inside `RESULT.json` must agree with those
actual bytes.

This support code is separate from the frozen native construction and runtime
adapter. It neither changes a native instruction nor substitutes a receipt for
the native semantic checks. The default release path still runs the complete
native engines. The reuse path authenticates previously completed evidence.

## Exact pin closure

`NATIVE-PINS.json` is authenticated by a fixed SHA-256 embedded in the checker:

```text
244f97a4590856fe19db10dfdcff80a35e07595235a1863d7abc767a1f4c7568
```

Each of the two provider directories contains 39 pinned files:

| Group | Files per provider | Meaning |
| --- | ---: | --- |
| `native/` | 12 | Complete emitted word, programs, scalar/frame and independent replay receipts, wrappers, phase/warp recipes, and five-stage record |
| `source/` | 18 | Actual executed scientific compiler/interpreter source snapshots and their notices |
| Run root | 9 | `RESULT.json`, exact `INPUT.json.gz`, commands and six execution logs |

The source hashes were checked against both retained original PR3734 native
receipts under `sources/PR3815/research/staged544-producer-return/evidence/`.
Those original receipts and their hashes are identified in the pin file. Both
providers use the same 18 source files, while their complete word and receipt
bindings remain separate. Extra, missing, changed or symlinked files within a
reused native run are rejected. A byte-preserving copy of either complete run
retains the original timing/log provenance; a fresh run need not reproduce
those incidental bytes.

## Python interface for the release runner

Import this module from `replay-support` and use:

```python
authenticate_reused(native_root)
authenticate_fresh_native(native_run, tag)  # tag is "base" or "extra"
authenticate_admission_inputs(work)
```

The first function checks both `native-base` and `native-extra` below
`native_root`. It checks all 78 files against the fixed pins, then verifies the
actual source declarations, target input and five-stage coverage.

The second function checks a completed fresh run. It requires the complete
18-file source tree to match the PR3734 pins, compares `RESULT.json` source
declarations with those actual bytes, binds the exact receiver-sharing input,
checks all five successful stages in order, and requires the complete 12-file
output inventory. It permits freshly generated output bytes and timing values
to differ from the retained run. This source/provenance function does not
independently repeat the native computations whose successful execution the
release runner has just observed.

The third function reads an already prepared admission workspace. It compares
both new-provider cache entries with the pinned completed native outputs,
checks their `CACHE.json` and top-level native receipt declarations, and hashes
the 18 scientific source files in the prepared compiler vendor tree. The
surrounding source manifest covers the larger vendor inventory. Existing
ancestor caches are outside this narrow check and remain covered by the
ordinary admission machinery.

All validation uses explicit failure checks that remain active under Python
optimization. The native engines and ordinary release still require assertions
enabled as documented in their own replay contracts.

## Commands and completed evidence

Authenticate the shipped runs, or an exact copy at `--reuse-root PATH`:

```sh
python3 -B research/kappa-adaptive-continuation/replay-support/native_auth.py \
  --out research/kappa-adaptive-continuation/replay-support/REUSED-NATIVE.json
```

Expected status: `PASS_EXACT_SHIPPED_NATIVE_REUSE`.

Check the actual source bytes of a completed fresh run:

```sh
python3 -B research/kappa-adaptive-continuation/replay-support/native_auth.py \
  --fresh-run PATH/native-base --provider base
```

Expected status: `PASS_ACTUAL_FRESH_NATIVE_SOURCES`.

The earlier low-memory attempt's prepared caches and source bytes were checked
read only with:

```sh
python3 -B research/kappa-adaptive-continuation/replay-support/native_auth.py \
  --admission-work /workspace/scratch/1a12211da438/adaptive-receiver-full-release-low-memory \
  --out research/kappa-adaptive-continuation/replay-support/CURRENT-ADMISSION.json
```

Expected and obtained status: `PASS_PREPARED_ADMISSION_CURRENT_NATIVE_INPUTS`.
This receipt binds source manifest
`18acd9411cbca007d37c5058ecb12b45cc3b82c15ddd0833444fede8fc14473e`
and native receipt
`c7e9538c9c857afa600557cd4817c353b299efe0c8b3c8121fd67c9e0c052146`.
It does not claim that complete admission finished; that attempt later stopped
at the missing outer dependency. `REVIEW-INVOICE.json` independently repeats
both the shipped-run authentication and the prepared-cache/source check in the
new `adaptive-receiver-complete-release` workspace. It finds the same exact
source manifest, native receipt and native output trees. The new release's
completion remains a separate parent-owned gate.

Run the bounded corruption checks:

```sh
python3 -B research/kappa-adaptive-continuation/replay-support/fixtures.py
```

`FIXTURES.json` records `PASS_NATIVE_AUTH_CORRUPTION_CONTROLS`: an exact copy
passes, and nine corruptions fail. They cover changed native output bytes,
changed actual compiler source in both reuse and fresh modes, a dishonest
source-hash declaration, an extra run file, an extra compiler source, a changed
input, a failed stage, and a missing native output. The shipped runs are checked
again after the fixture, and every mutation occurs only in a temporary copy.

## Open next questions and attribution

The parent release can now call these bounded checks before copying reused
evidence or accepting a newly completed native run. Equal decoded words should
be reconstructed before adopting an authenticated shipped gzip container; that
separate release-driver change avoids making gzip encoder metadata part of the
mathematical reconstruction test.

This support code was written with substantial OpenAI assistance. The native
word and the complete interpreter/phase proof retain dataisfire's PR3734,
Tekalign's native driver, and the complete predecessor notices inside the
authenticated source files. The work uses the repository's Apache-2.0 license.
