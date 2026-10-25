# Residual reader floors with crossing closure cells

The [self-contained proof](PROOF.md) removes the cell-locality premise from
PR3560's VVV/MMM residual rank bounds. Three indexed target groups may partition
their complete orthonormal block bases into arbitrary closure cells, including
cells crossing blocks. Block dimensions may be odd and bases may differ between
groups. Each cell has one unit indicator representative.

With n_k the binary dimension present in exactly k groups and original bill
D=n_1+2n_2+3n_3, the fixed four-query VVV family costs at least D+n_2 and MMM
costs at least D+n_1+n_2, over every field of characteristic different from two,
with arbitrary ambient readers. The exact crossing example has D=6, VVV minimum
7 and MMM minimum 9. Crossing cells can force a strictly larger residual bill.
These are scoped obstructions, with no supplier or kappa claim.

[RESULT.json](RESULT.json) contains 6,660 complete assignments in ten fixtures.
Two implementations match every four-charge stream, histogram and minimum.
The separate implementation checks 15,584 exact integer or gauged field entries.
[VALIDATION.md](VALIDATION.md) records verification scope and controls.

From the repository root, with CPython 3.12 and an existing private TMPDIR:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/p112-cell-crossing-residual-floor --check-only
python3.12 -Werror -B scripts/research_package.py --package research/p112-cell-crossing-residual-floor
python3.12 -Werror -B scripts/check_research_commit.py --package research/p112-cell-crossing-residual-floor --check-source-history
```

All three scientific/control commands in [VERIFY.json](VERIFY.json) also run
from a committed Git-free package export, without network or third-party
Python dependencies. The proof and runtime have no external scientific inputs.
The exact PR3560 comparison bytes and origin are in [COMPARISONS](COMPARISONS/origin.json),
separate from canonical provenance pins in [SOURCES.json](SOURCES.json).

## Open next questions

- Remove the full-block-basis premise for a nonreducing pair of spans. First
  derive the actual rectangular rank inequality or give an exact saving;
  neither finite sampling nor the present proof covers that change.
- Characterize when crossing-cell correlations force strict excess. Start with
  one incidence pattern containing unique and common blocks, using the exact
  7-versus-6 example as a control. A full optimum for other partitions is open.

This is a changed-scope local result on the coverage-law card. Arbitrary queries,
characteristic two, physical execution, restoration, complete invoices and
supplier/outer transfer remain open. Independent human and formal proof-kernel
review are unclaimed.

Nick Petalas. Apache-2.0. Credit retains PR3560, PR3549/3538, Philippe Van Velzen,
Arham Tahir, Tekalign/PR3370 and the P112/E8/native/compiler source lineage.
