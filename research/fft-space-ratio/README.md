# The FFT record uses at most `88/7` cells per input bit

**Partial. No new exponent.**

For width `n >= 3`, write `beta = ceil(log2 n)`, `q = ceil(n/beta)`,
`ell = ceil(log2(2q))`, `r = 2^ell` and `p0 = 2 beta + ell`. The packed
record has length `r(p0 + 2)`.

The digit comparisons `r beta < 8n` and `p0 <= 4 beta` give the coarse
estimate

```text
r(p0 + 2) < 32n + 16n/beta <= 40n
```

for `beta >= 2`. The sharp ratio on the checked range is smaller. Every
width from 3 through `2^22` satisfies

```text
7 r(p0 + 2) <= 88 n,
```

and width 7 meets the bound with equality: the record has 88 cells. The
selected kappa is unchanged.

## What was executed

The checker builds the digit geometry and compares the record length with
`88n/7`. It does not run the word multiplier.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the space paragraph of PR 3787,
head `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
ratio. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/fft-space-ratio/verify.py
python3.12 -B research/fft-space-ratio/test_verify.py
python3.12 -B scripts/research_package.py --package research/fft-space-ratio
```

## Open next questions

The ratio is checked for every width through 2^22, and equality holds at
width 7. A word-multiplier replay would leave this package.

## Credit

Jose Manuel (jmbarrancoml) stated that the packed record is linear in the
width in PR 3787. This package supplies the ratio `88/7`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
