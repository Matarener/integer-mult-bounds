# Executed validation

Environment: CPython 3.12.14, Linux, standard library only. Base:
`13be6ac685845c1ff671f5d26e7166165abd998e`. All commands below concern this
coverage package unless expressly described as orientation.

- `python3 -B scripts/research_selected_baseline.py`: passed all selected source
  bindings and exact metadata consistency. No selected scientific cold replay.
- `python3 -B scripts/research_package.py --package research/h8-census-coverage --check-only`:
  passed package metadata and source pins.
- `python3.12 -B scripts/research_package.py --package research/h8-census-coverage`:
  passed normal and optimized complete-receipt checks and all 16 tests (15
  rejecting controls). Marker: `PASS_H8_CENSUS_COVERAGE represented=43122
  unrepresented=343976352 full_joint_coverage=false no_new_kappa`.
- All 23 files in the frozen `research/bit-h8-receiver-census/` package were
  compared byte-for-byte with the base and are unchanged.

The complete 48,620-subset domain reconstruction and every A/B/C/tuning input key
are checked. The predecessor's production/price replay is not run. No native,
compiler, outer, Lean, hosted-CI or full multiplication proof is claimed.

- `python3.12 -B scripts/check_research_commit.py --package research/h8-census-coverage --check-source-history`:
  passed all 25 package/input files and the canonical source-history pin.
- `python3.12 -B scripts/export_research_package.py export --package research/h8-census-coverage --ref HEAD --output /tmp/h8-coverage.tar`
  and its `check` subcommand passed the closed 25-file export inventory.
- A relocated Git-free export passed both verifier modes and all 16 tests from
  an unrelated working directory with an empty PATH. Measured commands took
  0.610 s, 0.660 s and 5.477 s. All 26 exported files, including the export
  manifest, had identical SHA256 inventories before and after execution.
  Files/directories had read-only modes. A privilege-drop attempt failed before
  Python execution, so this run used uid 0: it establishes unchanged bytes, not
  a kernel-enforced read-only sandbox. Rejection controls write only disposable
  copies, made explicitly writable so ordinary users can run them too.
- `git diff --check` passed; the contribution changes only this package and one
  short qualification in `docs/research/research-family-status.md`.

No hosted CI was triggered. Exact remote commit/tree verification belongs to the
publication handoff; it is not a mathematical acceptance claim. The package
remains subject to independent review.
