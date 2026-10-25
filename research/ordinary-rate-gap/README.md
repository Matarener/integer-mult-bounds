# The line-156 bounds give 8,033,584, not 4,283,584

**Partial. No new exponent.**

With `c = 1/577` the ordinary-rate exponent is `a = c(1-c) = 576/332929`.
The linear piece is `801 = 2 * 2 * 200 + 1`. Composing it with the factor
`17/16` gives

`801 + 4000000 * 17/16 + 32780 + 3 = 4283584`.

The bounds written beside line 156, `n <= e^(1-c)` and `w <= 2 e^c`, replace
that factor by 2 and give `8033584`. Their product exceeds the stated line-158
bound by exactly `2^(1-c)`, and `2^(511/512) > 17/16`.

The selector witness `e = 2^20`, `w = 2`, `n = 1023683` also exceeds the
stated bound by more than `17/16`. The comparison is an integer inequality.
The inequality `n <= e/w` restores the factor `2^c` and the constant
`4283584`.

## What was executed

The checker evaluates the two coefficients and the witness powers. It does
not rerun the moment certificates.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the exposition gap in PR 3724,
head `946d03dd6b9cc794190876fe3f0f89b0ebc01c59`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
gap. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/ordinary-rate-gap/verify.py
python3.12 -B research/ordinary-rate-gap/test_verify.py
python3.12 -B scripts/research_package.py --package research/ordinary-rate-gap
```

## Open next questions

This coefficient pair is the exposition gap. A moment enclosure would leave it.

## Credit

Jose Manuel stated the ordinary-rate bound. thakrarsagar separated the
line-156 gap from the constant 4283584.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
