# Validation record

Scientific base: `721c03822c421b7f7fcbb2598993b947c4d88419`. Runtime: CPython 3.12.14 on Linux; standard library only. No dependency installation was needed. Repository activation and inherited authentication/remotes were preserved.

## Scientific checks actually run

```sh
python -B scripts/research_package.py --package research/p104-6030-deferred-layer
```

Result: `PASS_REGISTERED_RESEARCH_PACKAGE`, outcome completed. This executes primary and independent checkers with `-I -B`, then `-I -O -B`, each with its own 120-second timeout. The combined local run completed in under one second. The actual output is retained in [evidence/registered.txt](evidence/registered.txt).

- Primary: 11 source inputs, seven selected-source bindings, exact moment/margin/atom arithmetic, 48 symbolic-threshold fixtures, 528 whole-row padding fixtures, 12 rejected controls.
- Independent: 4,152 exact stopped-recursion models, 255 deferred schedules, three rejected parameter mutations, and an eager-reservation failure family. Normal and optimized outputs agree.
- `git diff --check` passed before packaging. Lightweight startup `make selected-record-check` and selected baseline binding checks passed; these are source/metadata checks, not scientific replays.

An initial metadata invocation rejected the nonstandard outcome string; it was changed to the allowed `completed` value before the successful run. No scientific evidence depended on that metadata error.

## Publication checks

At scientific commit `d5893178e0eda61b111fdd48f8807e075c0420f1`, these commands passed:

```sh
python -B scripts/check_research_commit.py --package research/p104-6030-deferred-layer --check-source-history
python -B scripts/export_research_package.py export --package research/p104-6030-deferred-layer --ref d5893178e0eda61b111fdd48f8807e075c0420f1 --output /tmp/reviewed-package.tar
python -B scripts/export_research_package.py check /tmp/reviewed-package.tar
```

The output archive location is incidental; a fresh path is required. Actual receipts: [committed-bytes.txt](evidence/committed-bytes.txt) and [export.txt](evidence/export.txt). The byte preflight checks 22 package/input files and ancestry of the exact scientific base. The export/integrity checks pass the same 22 files.

The checked archive was extracted into a fresh directory. Every file was set read-only, directories nonwritable, PATH was empty, and the working directory was unrelated to the export. Both direct verifiers ran with absolute paths, `-I -B`, normally and with `-O`; all four passed on CPython 3.12.14. SHA256 of every exported file, including the export receipt, was unchanged afterward. See [portable.json](evidence/portable.json) and [actual outputs](evidence/portable.txt).

These receipts are added in a following evidence-only commit. Final committed-byte/source-history and fresh export/direct replay checks are repeated at the publication head and recorded in the PR; the scientific proof and both checkers are unchanged. Export is a transport/dependency check, not mathematical certification.

## Checks deliberately not run

No `make verify`, selected `make frontier6030-verify`, all-historical suite, Lean, Docker, native/physical replay or external Claude review. The package changes no selected construction or shared verifier. Its inherited compiler, physical, precision and analytic contracts are explicit; rerunning unrelated historical suites would not prove those missing universal implications. Hosted CI is reported separately from local evidence.
