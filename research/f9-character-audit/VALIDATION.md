# Validation receipt

Environment: CPython 3.12.14, Linux x86_64, glibc 2.41; standard library only.
Canonical base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
Scientific source: PR5459 `bef3575ddb19c44434a7e2460a353eac7c4d9387`.
This is local independent finite verification, not hosted CI or human review.

Completed:

- `python3 -B scripts/research_package.py --package research/f9-character-audit --check-only`:
  metadata and main-branch provenance pins pass.
- `python3 -B scripts/research_package.py --package research/f9-character-audit`:
  normal and `-O` warning-strict commands pass, each with all 12,315 maps,
  156,978 generator products, 11,280 division-free determinant comparisons,
  163 norm comparisons and nine controls. Every field agrees with RESULT.json.
- The standalone computation takes approximately six seconds locally. This
  is a runtime observation, not a performance comparison or speedup claim.
- Retained PR5459 proof/checker bytes match their GitHub API Git blob IDs
  and recorded SHA256 hashes. Scientific code never imports them.

Additional completed checks:

- `scripts/check_research_commit.py --package research/f9-character-audit
  --check-source-history`: all 11 package files match committed bytes; the
  sole declared history commit is the canonical base and is an ancestor.
  PR5459's pending head is independently identified in REFERENCE.json and its
  exact consumed bytes are shipped, not required as a Git-history object.
- `scripts/export_research_package.py export` and `check`: a committed
  11-file package export passes the integrity inventory. The source copy,
  local reference manifest and frozen result are included.
- A relocated export in a path containing spaces passes `python -I -O -B`
  with empty PATH, no Git checkout and read-only files. All 12 exported files
  (11 package files plus export receipt) retain their SHA256 values afterward.
- Separate disposable copies reject (1) an altered source proof before
  scientific execution and (2) a changed expected map count after replay,
  both under optimized Python. These complement the nine mathematical
  controls; they are not additional theorem cases.
- `git diff --check` passes. Final canonical-main refresh remains the exact
  base above, and PR5459 remains at the pinned head. A renewed all-state
  F9/character PR search found no overlapping audit; this is bounded search
  coverage, not a novelty theorem.

The export and corruption controls do not import predecessor executables.
Only this validation prose was completed after the first committed export;
scientific code, sources and RESULT.json remain byte-identical. The final
handoff records the exact publication commit, patch and export integrity.

The selected cold replay, unrelated historical suites, full-source theorem
proofs and hosted CI are not required or run for this isolated audit. Selected
sources, upstream/ and predecessors stay unchanged. See the separate handoff
for publication status; a successful push or CI job is not mathematical adoption.
