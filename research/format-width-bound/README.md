# The format bounds are 3296H and 6592H

**Partial. No new exponent.**

Each initial component is bounded by `H`. A field with 1,024 such components
has Euclidean norm at most `sqrt(1024) H = 32H`, because `32² = 1024`. The
published trace has maximum row `ℓ1` norm 103, so a complete field is bounded
by

```text
M = 103 · 32H = 3296H
```

The four-term numerator has coefficient norm 2, so the scratch magnitude is
at most `2M = 6592H`.

Both coefficients sit under a power of two: `3296 < 2^12` and `6592 < 2^13`.
With a sign bit and fractional guard 7, the signed widths are `b+20` for
fields and `b+21` for scratch. Guard 6 gives `b+19` and `b+20`.

## What was executed

The checker multiplies these constants. It does not retrace entrance
operation 929.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the format proof in PR 3620,
head `5a4354c669dc05a9368f58321b1951ebac36d80d`.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to these
widths. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/format-width-bound/verify.py
python3.12 -B research/format-width-bound/test_verify.py
python3.12 -B scripts/research_package.py --package research/format-width-bound
```

## Open next questions

These widths are the format bound. Retracing the entrance would leave them.

## Credit

Clear1nsight stated the row norm 103 and the format widths in the
caller-feasibility note.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
