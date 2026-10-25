# The stock receipt leaves the selected coefficient null

**Partial. No new exponent.**

The audit receipt has two branches of seven stages. All fourteen stages store
`actual_stock_coefficient` as null. The source boundary stores the same null
for the stage coefficients and records completed inner-leaf borrowing as 0.
Its status is `NOT_ESTABLISHED`.

The historical candidate is width 120 with coefficient 57,604. The selected
candidate is width 73 and has no coefficient. The receipt marks
`sigma_j = sigma_0 + j*57604` as not established. The audit text says the
factor-16 fit does not measure or derive sigma, and that the actual selected
coefficients remain unknown.

## What was executed

The checker reads those fields. It does not recompute a cutoff margin.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the audit receipt's coefficient
fields.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to
this absence. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the audit note and its receipt. No selected
frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/stock-coefficient-absent/verify.py
python3.12 -B research/stock-coefficient-absent/test_verify.py
python3.12 -B scripts/research_package.py --package research/stock-coefficient-absent
```

## Open next questions

The receipt's null coefficient is this lemma. Another margin row would leave
this absence.

## Credit

Josie Elliston supplied the PR 1965 headrooms that this audit corroborates.
The audit was prepared for ToikY with OpenAI Codex.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
