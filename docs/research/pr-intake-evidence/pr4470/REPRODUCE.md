# Reproduce the scoped review

Use committed base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc` and the
repository's `scripts/export_research_package.py export` command to export:

- `research/joint-helper-lattice`
- `research/pr4470-frame-audit`
- `research/pr4470-arithmetic-check`
- `research/stage-zero-commutation-audit`
- `research/stage-zero-forced-translation`

Run the export utility's `check` command on each archive. Extract to a disposable
directory using a data-only tar filter, retaining each export receipt separately.
Overlapping input files must be byte-identical; do not overwrite differing
inputs. PR4466's manifest omits two provenance files that its verifier reads:
also export `certificates/selected-result.json` and
`docs/research/agent-task-catalog.json` from that same base and check their hashes
against its `SOURCES.json`. `REVIEWED-SOURCES.json` binds all 110 source files.
None requires Git or network access during mathematical replay.

Copy this directory's `run_bounded.py` into the export root. Copy
`all_final_transports.py` into its `review-evidence/` directory. The runner uses
its own parent as the working root and saves logs under `review-evidence/`.
Set `TMPDIR` to an existing **resolved absolute directory**, avoiding macOS's
`/var` and `/tmp` aliases; this works around PR4504's source path guard without
modifying the pinned audit.

Run these commands serially from that export:

```sh
python3 -B run_bounded.py dependencies 300 research/joint-helper-lattice/verify.py --part dependencies
python3 -B run_bounded.py native 600 research/joint-helper-lattice/verify.py --part native
python3 -B run_bounded.py arithmetic 300 research/joint-helper-lattice/verify.py --part arithmetic
python3 -B run_bounded.py all-final-transports 300 review-evidence/all_final_transports.py
python3 -B run_bounded.py independent-frame 120 research/pr4470-frame-audit/verify.py
python3 -B run_bounded.py independent-arithmetic 300 research/pr4470-arithmetic-check/verify.py
python3 -B run_bounded.py stage-zero 120 research/stage-zero-commutation-audit/verify.py
python3 -B run_bounded.py forced-translation 120 research/stage-zero-forced-translation/verify.py
```

The retained runner samples descendant RSS and stops above 1 GiB or the given
timeout. It uses POSIX process groups and `ps`; this is a maintainer replay
harness, not a new portable project test runner. Python 3.14 on macOS was used
here; the source manifests advertise standard-library Python 3.12.

This reproduces the **changed construction review**, with source-identical
PR4359/PR4416 evidence reused as described in `SOURCE-REUSE.json` and the proof
review. It is not a replacement for the selected cold replay, a replay of all
historical sources, or a proof of the inherited all-size/tape/analytic premises.
No Lean, Docker, optimization search or `--write` authoring mode is needed.
