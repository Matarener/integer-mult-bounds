# Compare arbitrary ranks across an exponent range

The fixed-power checker tests one rational exponent. The polynomial checker
classifies all powers when the changed ranks share one integer base. Use this
bounded interval checker when the ranks do not share a base:

```sh
python3 -B scripts/compare_recursive_intervals.py OLD.json NEW.json \
  --left 0.99 --right 1 --bits 128 --max-boxes 255 --max-depth 24
```

The inputs use the existing signed-invoice schema. The output partitions the
whole closed range. Each cell contains exact rational bounds for the cost
difference and its derivative. `new_cost_lower` and `new_cost_higher` certify
strict order throughout that cell. `equal` certifies an identically zero bound.
`single_crossing` certifies exactly one interior root. `unresolved` makes no
root-count claim. Adjacent closed cells share their endpoint. No cell is dropped
when the depth or work budget is exhausted.

For example, `2^t + 3^t - 4` has incompatible integer bases. Its derivative
is strictly positive and its endpoint signs differ. The tool isolates its
unique crossing. A numerical grid alone would not prove uniqueness or cover
the gaps between samples.

## Why the bounds hold

Write `F(t) = sum d_r r^t`, with paid counts positive and target counts negative.
For `a <= t <= b`, each `r^t` lies between its certified bounds at `a` and `b`.
Reverse bounds when multiplying by a negative count. The same rule applies to
`F'(t) = sum d_r r^t log(r)`, since `log(r) >= 0`.

To bound the logarithm, write `r = 2^k u`, with `1 <= u < 2`. For
`z = (u-1)/(u+1)`, use `log(u) = 2 sum z^(2j+1)/(2j+1)`.
Here `0 <= z < 1/3`; `log(2)` uses `z=1/3`. After N terms, the positive tail
is at most `2 z^(2N+1)/((2N+1)(1-z^2))`. Exact fractions and outward dyadic
rounding preserve the bounds. The existing integer square-root engine bounds
the powers. At exponents zero and one, powers are exact integers.

Integrate the derivative interval from each endpoint and intersect those
enclosures with the direct power sum. Every intersection still contains F on
the full cell. Strict derivative sign proves strict monotonicity. Opposite
strict endpoint signs then give exactly one interior root by continuity.
Subdivision preserves coverage; stopping without a strict certificate retains
an unresolved cell. This is elementary interval arithmetic, not a new theorem.

## Limits and next questions

The limits are 64 nonzero ranks after cancellation, 16..256 dyadic bits,
1..2047 allocated boxes and depth 0..40. The box budget includes internal nodes.
Large cancellations, tangent roots and endpoint roots can remain unresolved.
Use the polynomial tool for a complete common-base decision, including equality.
Increase precision or narrow a range when the interval output identifies a
specific unresolved obligation. A positive comparison concerns declared bills;
source legality, complete charges, native maps and compiler closure remain open.

The inputs are read once and bound by their byte hashes. The tools preserve
zxv's signed-invoice interface, mightyOil's T16 moment-order context and the
retained predecessor credits. The integer-power engine is from PR5732; the
common-base alternative is PR5746. Ali Romman with substantial OpenAI Codex
assistance. Apache-2.0. No selected result is changed.


## Selected-bill example

The test fixture `tests/fixtures/recursive-invoice-selected5599.json` copies the
complete paid and target histograms from the selected source receipt at main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. Its source is
`research/p104-helper-subspace-splits/RESULT.json`, SHA-256
`1d92e587915052110dfb3aca8890df5afdaf496164efa5a4a52e69ceeb3c70f3`.
That hash was checked against the selected record before extraction. The fixture
is a fixed arithmetic example; it does not track later frontier selections.

Comparing a zero invoice with that bill on `99/100 <= t <= 1` at 128 bits,
box budget 511 and depth 30 produces 31 cells. Exactly one cell crosses zero:
`53520636719/53687091200 < t < 107041273439/107374182400`.
All other cells have a strict sign. The width is `1/107374182400`.
This recovers the raw invoice crossing; it is not a new compiler or κ result.
Use the authenticated selected-invoice exporter for a new live comparison.
