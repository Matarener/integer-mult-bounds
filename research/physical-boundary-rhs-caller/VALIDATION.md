# Validation and limits

Author execution: macOS arm64, CPython3.12.2 (Clang15.0.0), base
32890bc5de034ab8fc93ac88ead7279a6a416d04. No new dependencies.

The initial P8 fixture allowed the rounded consumer to equal its RHS. Before
publication it was strengthened to P16/w32, and a bypass-consumer control now
requires a real change. The full three-case source-bound replay passed in
5.41seconds before the final head/lease controls; that observation is not a
physical tape speed or a portable runtime guarantee. The final receipt includes
all final controls. A module-name collision with the inherited `layout` was
resolved by the specific `rhs_layout` name. A checker initially compared entire
retained output capacity with logical input length; it now compares logical
bodies and independently requires all retained work backing to be erased.

Executed:

- `python3.12 -I -B research/physical-boundary-rhs-caller/verify.py --write`
- `python3.12 -B scripts/research_package.py --package research/physical-boundary-rhs-caller --check-only`

- `python3.12 -B scripts/research_package.py --package research/physical-boundary-rhs-caller` passed the unchanged normal and optimized scientific commands.
- `python3.12 -I -O -B research/physical-boundary-rhs-caller/test_integrity.py` passed four actual CLI controls in10.59seconds: changed source, missing source, Boolean-valued width in the typed receipt, and missing receipt. Both receipt failures execute the real optimized program first.
- `python3.12 -B scripts/check_research_commit.py --package research/physical-boundary-rhs-caller --check-source-history` passed at2544813dbb32bea44d2df8eff8b18340bd3d209e.
- The official committed exporter and offline integrity checker passed with explicit `--input-ref 32890bc5de034ab8fc93ac88ead7279a6a416d04`; the first archive had30files and was about52MiB. All declared runtime source files come from that base.
- Actual Git-free extraction of that archive passed `python3.12 -I -O -B .../verify.py` in5.21seconds. No `.git`, network or installed third-party packages were available to its source loaders.

The second commit adds the CLI controls and registers that same tested command;
the scientific implementation, proof, receipt and reviewed source hashes are
unchanged from the first commit. Final publication-head export/preflight are
read-only checks recorded with the handoff, not reasons to alter frozen receipts.

A separate Codex agent reviewed the actual source/caller, proof, cost/backing,
reference and cleanup boundaries, and independently ran the optimized5-row
R2B2 case with all9layout controls. It reported no blocking findings after
canonical-head validation and partial-acquisition cleanup were fixed. This is
AI peer review, not independent human acceptance. Proof SHA256:
`d8a1bac7b6180110396b9c9257f4ea2e75df86d2c4563a70c3fef9d7880f548f`.

All three actual calls and final source/control checks passed. No hosted CI, production Gaussian preparation, full
Core second-pass integration, selected-frontier replay or formal proof kernel
has run. No inherited numerical theorem is independently accepted by this note.
