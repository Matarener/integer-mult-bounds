# The product exponent is 603/1000

**Partial. No new exponent for the selected frontier.**

With block length `ell = Theta(p^(1-epsilon))`, dividing the product invoice by
the volume leaves the online exponent `8/5 - epsilon`. At
`epsilon = 997/1000`,

```text
8/5 - 997/1000 = 603/1000.
```

The inherited Fourier exponent is `1 - 576/332929 = 332353/332929`. The
product exponent is strictly smaller. At `epsilon = 1/40` the same difference
is `63/40`, which is greater than 1, so that parameter regime is not covered.

The working precision is `Q = 2p + 2m + s` with `m = ell + 1` and
`s = ceil(log2(12m+2)) + 3`. For every `m >= 1`, `12m+2` is divisible by 2
exactly once, so it is not a power of two. Its ceiling therefore supplies a
strict extra bit, and

```text
(12m+2) 2^(-s) < 1/8.
```

For `p >= 2` and `m <= p`, the same ceiling is at most `4p`, so `Q <= 8p`.
The base `p = 2` meets `4p` exactly, and multiplying the exponential side by
16 preserves the inequality.

## What was executed

The checker compares these rationals. It does not run the convolution.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the product exponent in PR 3709,
head `360e2a5a74eae146dfb1535756b0bd06049aa141`.

## Scope and evidence

Original card: `scalar-to-moment`, priority revision 6, refined to this
exponent. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/product-exponent-gap/verify.py
python3.12 -B research/product-exponent-gap/test_verify.py
python3.12 -B scripts/research_package.py --package research/product-exponent-gap
```

## Open next questions

This exponent is the comparison. The convolution replay would leave it.

## Credit

Jose Manuel published the product exponent and the one-eighth recovery bound.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
