# `log2(n+2)^2` is at most `24n`

**Partial. No new exponent.**

The series for `exp(1/2)`, cut after 40 terms with a geometric tail, is
strictly below 2. Therefore `ln 2 > 1/2`, and `log2(y) <= 2 ln(y)`. The
exponential series also gives `exp(u) >= u^2/2` for `u >= 0`, so
`ln(y)^2 <= 2y`. Combining these estimates yields

```text
log2(y)^2 <= 8y.
```

For every integer `n >= 1`, the width `n+2` is at most `3n`. Substituting
`y = n+2` produces

```text
log2(n+2)^2 <= 24n.
```

The integer form is stronger: if `m = ceil(log2(n+2))`, then `m^2 <= 24n`.
This holds for every `n` from 1 through `2^24 = 16,777,216`.

For a real exponent `delta` in `(0, 1]`, the same three factors contribute
an extra `delta^{-2}` and replace `n` by `n^delta`. The power order
`n^c <= (n+2)^c` keeps `(1+2/n)^delta <= 1+2/n <= 3`, so the stated bound is

```text
log2(n+2)^2 <= 24 delta^{-2} n^delta.
```

The constant is exactly `4 * 2 * 3 = 24`. The selected kappa is unchanged.

## What was executed

The checker sums the exponential series and compares the integer ceiling
with `24n` at every width in the range. It also checks the power order for
bases through 1024 and exponents through 16. It does not run the word
multiplier.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the Gaussian-allowance paragraph
of PR 3787, head `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
bound. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/log-absorption-bound/verify.py
python3.12 -B research/log-absorption-bound/test_verify.py
python3.12 -B scripts/research_package.py --package research/log-absorption-bound
```

## Open next questions

The delta-one bound is checked for every n through 2^24, and the constant
24 is the exact product of the three factors. A word-multiplier replay would
leave this package.

## Credit

Jose Manuel (jmbarrancoml) stated this absorption in PR 3787. This package
checks the integer form and the constant `24`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
