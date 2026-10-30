# Validation record

Author-side validation on 2026-10-26, Python 3.12.14, macOS 26.5.1 arm64,
standard library only. Separate Codex agents reviewed the literal compatibility,
complete accounting and publication claims; this is not independent human or
formal-kernel acceptance.

## Source and construction

Base `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
PR5802 is pinned to `9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62`; PR5795
is pinned to `206cb717c0c07737d61637b93f7502ca48850348`. The 33 vendored files
retain exact source Git blobs and SHA256 hashes, including the transitive
source archives and notices. All new adaptations are enumerated in the three
EDITS manifests. The final word's canonical SHA256 is
`a06445539ad73fe16deae66fef8c52ffc39f5f14c765eab3dc3d98e0e2d8074c`.

The final-word replay passes the complete forward and reverse checks on 799
coordinates and 638,401 endpoint coefficients, all 23 COPY payloads, 31 owned
lifetimes and peak 13 live owned fields. It checks 2,919 distinct native maps
with absolute phase, 1,124 helper normalizers, 208 main adapters and the complete
physical caller. Both rational moment implementations, the compiler calculation,
54 strict outer inequalities and four functional conditions pass. Thirty
construction/caller/invoice corruptions and the native-phase corruption reject.

The separately implemented `check_total_gain.py` authenticates the inputs,
recounts the actual word and complete invoice, proves the combined gain positive
throughout `0.9966 <= t < 1` with exact rational logarithm bounds, and rejects
four corrupt receipts. `integrity_check.py` rejects eleven source/inventory/path
corruptions. Both lightweight checks pass with isolated imports, assertions
disabled and warnings treated as errors. The complete receipts are retained.

## Registered replay

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p104-accumulated-block-composition --check-only
python3.12 -W error -B scripts/research_package.py \
  --package research/p104-accumulated-block-composition
```

Metadata and exact repository source pins pass. The final registered replay passed all four commands in 251.79 seconds, ending
with `PASS_REGISTERED_RESEARCH_PACKAGE` (outcome completed).
The manifest runs the entire scientific verifier normally and under `-I -O`,
then both lightweight controls under `-I -O`; all four commands use `-W error -B`.
Only this package was selected. The inherited selected-baseline metadata check
also passed; it does not substitute for the new-word replay.

## Committed export

The committed-byte and executable-mode preflight passes for all 57 package
files at scientific payload commit `f40ad6936e208a3b2430f9a246077f5d8b34ee31`.
The official exporter and its inventory/mode/hash/declared-input checker pass.
Export archive SHA256:
`bc900fa1d6d1818297b8298e8eb914c0969dd5f1e6ecbbe59657ee8883acf277`.

```sh
python3.12 -B scripts/check_research_commit.py \
  --package research/p104-accumulated-block-composition --check-modes
python3.12 -B scripts/export_research_package.py export \
  --package research/p104-accumulated-block-composition \
  --ref f40ad6936e208a3b2430f9a246077f5d8b34ee31 --output publication.tar
python3.12 -B scripts/export_research_package.py check publication.tar --check-inputs
```

The export was extracted outside Git, all files set to 0444 and directories to
0555, and PATH set to the empty string. Using an absolute Python executable,
`-I -O -W error -B verify.py` passed in 75.52 seconds; `integrity_check.py`
and `check_total_gain.py` passed in 0.17 and 0.25 seconds. All 58 files including
the export receipt, and all directory/file modes, were unchanged afterward.
The final documentation commit changes only this validation record; its complete
scientific payload is byte-identical to the tested export.

An earlier sealed run passed the scientific replay but exposed a corruption-test
fixture copying read-only modes into its temporary sandbox. The fix changes only
those private copied fixtures to writable modes. Both normal and optimized
source-corruption checks passed after the fix, followed by the complete fresh
sealed replay above. No scientific source, word, invoice, root or claim changed.

## Scope and current overlap

At the 2026-10-26 22:40 UTC overlap check, concurrent PR5806 by Dugongue
(`20e7289b63d240715aa96006571ae38a46291d97`) described the same baseline join
with conditional kappa at least 0.0031234, without materializing it. That shared
composition is credited; the fourth role92 realization, changed native frames
and complete final price are the additional work here. Ali Romman's released
role92 idea retains its authorship. PR5809's audit covers the three source
accumulations, not this fourth update. This was a bounded check of current PRs
and canonical discussions, not an exhaustive novelty guarantee.

All five framework assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, `analytic_recovery`. The large uniform word and
rounded multiplier are not materialized. The selected frontier remains
unchanged. No independent human review, formal-kernel acceptance or hosted CI
success is inferred from local checks. The optional full-history source-ancestry
preflight was not run: all standard repository pins now resolve to the base or retained source
ancestor `b83ff89de649be3bd2dc2d885da254bae00c8836`. Original pending-head
records remain unchanged under `vendored`, with an exact unique mapping to
the retained blobs. No pending-PR fetch is required. The available checkout
is shallow, so the stricter full-history check is reported separately.
Unrelated repository suites and historical artifacts were not rerun.
