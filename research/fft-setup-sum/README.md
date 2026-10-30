# The three FFT setup terms add to at most `1017/7` of `n beta^2`

**Partial. No new exponent.**

For width `n >= 3`, write `beta = ceil(log2 n)`, `q = ceil(n/beta)`,
`ell = ceil(log2(2q))`, `r = 2^ell` and `p0 = 2 beta + ell`. The three
setup terms are

```text
r(ell+1)p0^2,   r p0^3,   p0^3.
```

Their sum `S` satisfies

```text
7 S <= 1017 n beta^2
```

for every width from 3 through `2^22`. Width 7 meets the bound with
equality. There `beta = 3`, `r = 8` and `p0 = 9`, so

```text
S = 8*4*81 + 8*729 + 729 = 9153,
n beta^2 = 63,
9153 / 63 = 1017 / 7.
```

The separate caps `256 + 512 + 64 = 832` are larger than `1017/7`. The
selected kappa is unchanged.

## What was executed

The checker adds the three terms and compares the sum with `1017 n beta^2 / 7`.
It does not run the word multiplier.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the time paragraph of PR 3787,
head `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
sum. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/fft-setup-sum/verify.py
python3.12 -B research/fft-setup-sum/test_verify.py
python3.12 -B scripts/research_package.py --package research/fft-setup-sum
```

## Open next questions

The sum is checked for every width through 2^22, and equality holds at
width 7. A word-multiplier replay would leave this package.

## Credit

Jose Manuel (jmbarrancoml) stated the three setup terms in PR 3787. This
package adds them and records the ratio `1017/7`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
