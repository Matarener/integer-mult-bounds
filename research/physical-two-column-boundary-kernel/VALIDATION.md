# Validation and limits

Python 3.12, standard library, macOS; base
`32890bc5de034ab8fc93ac88ead7279a6a416d04`.

- `python3.12 -I -B research/physical-two-column-boundary-kernel/verify.py --write`:
  PASS, 16.176 seconds, all four cases and six physical controls. The explicit
  generation run executes the same scientific checks as normal receipt replay;
  it writes RESULT.json rather than comparing the existing JSON.
- `python3.12 -B scripts/research_package.py --package research/physical-two-column-boundary-kernel --check-only`:
  PASS metadata and source pins. The registered runner's combined scientific
  commands were not rerun; this avoids duplicating the unchanged normal suite.
- `python3.12 -I -O -B research/physical-two-column-boundary-kernel/test_integrity.py`:
  PASS four actual optimized Git-free CLI source-binding rejections: changed
  and missing main predecessor, changed retained layout helper, changed adapted
  fixture. Every rejection happens before scientific execution.
- Independent peer review ran optimized `verify.py --quick`: PASS B4 full
  output, cost/backing and all six controls. The final committed export is
  intended for one optimized full receipt replay using the command below;
  its external handoff records the exact publication hash and outcome.

```
python3.12 -B scripts/check_research_commit.py --package research/physical-two-column-boundary-kernel --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/physical-two-column-boundary-kernel --ref HEAD --input-ref 32890bc5de034ab8fc93ac88ead7279a6a416d04 --output /tmp/physical-two-column.tar
python3.12 -B scripts/export_research_package.py check /tmp/physical-two-column.tar
# Extract the checked archive into a new Git-free directory, then:
python3.12 -I -O -B research/physical-two-column-boundary-kernel/verify.py
```

The B4 one-block receipt pays 7,017,713→4,200,707 complete consumer tape
operations, 9,953→9,731 retained owner cells, and 128→64 scalar products.
The two-block receipt pays 21,413,925→12,862,809 operations,
13,697→13,511 cells, and 384→192 products. All padded words agree exactly,
and positive same-owner reuse repeats the exact measured bill and backing.
B2 pays 1,307,609→1,307,953 operations and 4,827→4,861 cells; B1 pays
1,225,648→1,227,592 operations and 3,803→3,854 cells. Those fallback sizes
retain the original product algorithm, with a small encoded dispatch overhead.

All measured tapes, including borrowed banks and cleanup, are charged. The
receipt reports read/write/unit-move counts, not Python instruction counts;
PROOF supplies the separate encoded-control bound. Historical high-water
backing for arbitrary previous invocations is not reduced by this claim.

The two-cell source fixture extends the supplied-factor calibration from
PR5483 and exercises actual Core gathering and cell execution. It does not
prove the all-size Gaussian coefficient producer or LU growth bounds. The
reference is exact supplied LU(round_P(S)), not the original unrounded matrix
or the old BandedSolve rounding algorithm. Complete second-cell and normalized
Core integration, general many-field suppliers, recursive tariffs and a new
κ remain unrun/unproved here. No Lean, Docker, selected-frontier suite or
historical full suite was run. No upstream source or frozen archive changed.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
