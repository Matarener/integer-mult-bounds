# Compare invoices at one exact power

The concave-order screen can be inconclusive when a particular power has a
strict sign. Compare the same declared invoices at `r^t` with:

```sh
python3 -B scripts/evaluate_recursive_power.py OLD.json NEW.json --exponent 0.9969
```

The exponent is the exact decimal or fraction supplied. If the proposed tariff
is `r^(1-C)`, pass `t=1-C`; the tool does not choose or certify κ. Input contracts
must match. Paid jobs and target credits use the existing invoice schema. The
report binds the input bytes by SHA256 and gives rational lower and upper bounds
for `(new paid-new targets)-(old paid-old targets)`.

To choose compatible changes under shared resource limits at this exponent,
use the [exact edit selector](recursive-edit-selection.md).

A negative upper bound proves `new_cost_lower` at this exponent. A positive lower
bound proves `new_cost_higher`. Exact zero gives `equal`. All other intervals give
`unresolved`; this does not mean equality or failure of the candidate. Increase
`--bits` from its default 128 up to 256 if a narrow margin needs more precision.
This is the grid size, not a promise of that many correct output bits.

## Why the bounds hold

Let `F=2^bits`. Represent an interval by integer endpoints `[L,U]/F`. For a
nonnegative value in this interval, its square root is enclosed by
`floor(sqrt(L*F))/F` and `ceil(sqrt(U*F))/F`. Python's integer square root gives
these endpoints without floating-point arithmetic. Products of nonnegative
intervals use the lower product rounded down and the upper product rounded up.

Write `m=floor(F*t)`. Repeated square roots enclose `r^(1/2^j)` for each binary
digit of `m/F`. Multiply the factors selected by those digits. This encloses
`r^(m/F)`. If `F*t` is not an integer, `0<t-m/F<1/F`. Since `r>=1`, the lower
endpoint remains valid. Multiplying the upper endpoint by the last root's upper
bound encloses `r^t`. For an exact binary exponent, that last factor is not needed.

Cancel equal ranks in the signed invoice first. For a positive coefficient,
multiply the lower and upper endpoints in order. For a negative coefficient,
reverse them. Adding the resulting intervals encloses the exact signed cost.
This uses elementary monotonicity and directed rounding; it is not a new
multiplication theorem.

## Checks and limits

Tests compare the returned intervals with independent integer-power inequalities
for 216 rank/exponent cases. Exact square/fourth-root cases, target debits,
large-denominator decimal exponents, unresolved equality and the isolated
optimized CLI are also checked. A high-precision decimal value is a secondary
sanity check only; it is not the interval certificate.

The tool permits 16..256 grid bits and at most 512 nonzero ranks after cancellation.
The existing invoice limits apply. Exponent text is at most 128 characters and
uses fractions or decimals without scientific notation. For example, old paid
jobs `{"2":2}` and new jobs `{"1":1,"4":1}` are inconclusive in concave order,
but this tool proves the new cost is higher at `t=1/2`.

The report does not check circuit legality, invoice extraction, ownership,
precision, supplier admission or compiler endpoints. Keep those proof obligations
with the source construction. Credit the existing signed-invoice comparator,
mightyOil's T16 moment-order audit and their retained predecessors for the invoice
interface and accounting context. Prepared for aliromman with OpenAI Codex
assistance. Apache-2.0.

For arbitrary ranks over a closed exponent range, use the
[interval cover and crossing checker](recursive-interval-comparison.md).
It retains unresolved cells and can certify unique crossings.
