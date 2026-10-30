# Validation record

Environment: CPython 3.12.0, Windows 11 (10.0.26300), standard library only.
Canonical main: `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7.
Source PR4470: `b9a13c1673e0e9697de410de16e8bbf3207a7363`.
PR4478 overlap: `4e5072ad3bbdf76f2935f9488207db3969b38c90`.
Both heads and canonical main were unchanged at the pre-submission refresh.

The authoring run completed with `PASS_PR4470_CHRONOLOGICAL_FRAME_AUDIT` and
generated RESULT.json. It checked both orientations of the predecessor and
changed word, plus all eleven semantic failure controls.

The following checks completed on 2026-10-22 UTC:

```text
python -B scripts/research_package.py --package research/pr4470-frame-audit
  PASS_REGISTERED_RESEARCH_PACKAGE research/pr4470-frame-audit outcome=completed

python -I -O -B research/pr4470-frame-audit/verify.py
  PASS_PR4470_CHRONOLOGICAL_FRAME_AUDIT

python -B scripts/check_research_commit.py --package research/pr4470-frame-audit
  PASS_RESEARCH_COMMIT_BYTES (20 package/input files)

python -B scripts/export_research_package.py export \
  --package research/pr4470-frame-audit --output <temporary-archive.tar.gz>
python -B scripts/export_research_package.py check <temporary-archive.tar.gz>
  PASS_RESEARCH_EXPORT (20 files)
```

The committed export was extracted outside any Git worktree. Its standalone
verifier passed under `python -I -O -B` in 9.5 seconds. Appending one space to
the **exported copy** of the pinned PR4470 PATCH.json caused the same command
to fail with `source SHA256 mismatch`, before calling the source constructor.
The retained snapshots were not modified. The exporter and its checker
authenticate the package inventory; the standalone command performs the actual
frame/billing audit. All non-source verification code and source snapshots were
unchanged between that replay and publication; only this record and task
freshness metadata were subsequently completed.

The first byte preflight caught CRLF in this package's newly authored
UPSTREAM.json versus Git's LF content. Normalizing that manifest's working
newlines fixed the preflight. All nine frozen source snapshots remained
byte-exact; no mathematical assertion or source pin was weakened.

Overlap refresh: all 354 open PR records and 3,381 Discussion records were
paginated, at 02:32:04Z and 02:33:19Z respectively. All 5,731 base HEAD
top-level README/TASK/ledger paths were present in the local note inventory.
This does not cover every diff, nested note or closed PR body. Exact source
heads were separately rechecked. The introductory historical baseline command
was not used as evidence: its selected-certificate inputs were initially
omitted by the sparse checkout; the selected record and review were read
directly, and this package has its own self-contained replay.

Linux execution, hosted CI, the optional full-history preflight, physical
Clifford lowering, full column identity replay, the p16 controller, Lean and
full supplier admission were not run. A selected-frontier change is outside
the scope.
