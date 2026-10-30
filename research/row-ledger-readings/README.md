# The two row readings carry the same constant degrees

**Partial. No new exponent.**

The gauge note gives family pairs `(367, 27)`, `(9, 28)` and `(200, 28)`.
Their products are 9909, 252 and 5600, and the printed sum is 15761. The
frozen assembler uses only the first two, together with a prefix term
`2 * 512 = 1024`:

`physical_row_coefficient = 2 * stock.bit_length() + 9909 + 252 + 1024`.

The retained cap is 20161. The orthogonal order in the layer proof is
`2^1296 * product_{i=1}^{36} (2^{2i}-1)`. It lies strictly between `2^2627`
and `2^2628`. With the live width 14336, the ceiling of its base-2 logarithm
is 2642. The constant degrees therefore total

`11185 = 9909 + 252 + 1024`,

and the two published readings are

`16469 = 2 * 2642 + 11185`,

`15555 = ceil(43 * 2642 / 26) + 11185`.

Their difference is 914. Dropping 9909 and 252 leaves the lean row
`2 * 2642 + 1024 = 6308`, which is still below 16469 and below the cap. The
selected kappa is unchanged.

## What was executed

The checker parses these formulas and evaluates the order. It does not
recompute the fourteen stage headrooms.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the row-ledger arithmetic in
PR 3667, head `ad7c0e10e5476136498b377a3a28b80640e55c08`.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to
these two readings. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the gauge note, the layer proof, the
envelope note and the frozen assembler. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/row-ledger-readings/verify.py
python3.12 -B research/row-ledger-readings/test_verify.py
python3.12 -B scripts/research_package.py --package research/row-ledger-readings
```

## Open next questions

These two readings are the comparison. A stage-headroom replay would leave it.

## Credit

Mainzu traced these row readings.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
