# The chirp online power sits under the Fourier power

**Partial. No new exponent.**

For every precision `p` from 16 through 128 and every length `ell` from 2
through `p - 1`, the guard `ell.bit_length() + 4` makes the working width
lie between 16 and `2p`, and `4(ell+1)` divided by `2` to that guard is at
most `1/4`. There are 7910 such rows. The final phase split satisfies
`(7/4)^2 > 2` and `7/4 + 1/4 = 2`. The ring margin `32 * 1000^2` is below
`2^26`. The output norm bound is `3/5 + 1/1000 = 601/1000`. The error bill
is `3*4 + 2 + 2*4 = 22`.

The online power is `8/5 - 997/1000 = 603/1000`. The stated Fourier power is

`1 - (997/1000) * (1 - 99827101/100000000) = 99827619697/100000000000`.

Both `603/1000` and the primitive exponent `332353/332929` are strictly
below that Fourier power. The selected kappa is unchanged.

## What was executed

The checker evaluates these rows and fractions. It does not run the
middle-map consumer.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the budget section of PR 3763,
head `6bb7dfdae182a69f7c8836a9ec1be0b2b747e124`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
budget. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/chirp-budget-clearance/verify.py
python3.12 -B research/chirp-budget-clearance/test_verify.py
python3.12 -B scripts/research_package.py --package research/chirp-budget-clearance
```

## Open next questions

This budget is the finite comparison. A middle-map replay would leave it.

## Credit

Jose Manuel (jmbarrancoml) recorded this budget. The Fourier power formula is
the one stated from the corrected predecessor.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
