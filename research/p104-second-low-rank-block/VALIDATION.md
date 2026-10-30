# Validation record

The author regenerated WORD.json.gz, WITNESS.json and RESULT.json with Python
3.12 and the standard library on macOS. The complete direct replay passed,
including all failure controls. It reported:

```text
PASS_P104_SECOND_RANK4_BLOCK_KAPPA_00311325989
```

Both registered modes passed through `scripts/research_package.py` on
2026-10-26. The ordinary mode used `-I -B`; the optimized mode used `-I -O -B`.
The runner reported `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome completed.
The committed-byte check and sealed source export are recorded in the public
PR handoff after execution. No hosted CI, independent
human review, Lean proof or materialized rounded multiplier is claimed here.
