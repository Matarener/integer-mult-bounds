# The ordinary rate clears its width threshold

**Partial. No new exponent.**

At `c = 1/576` the ordinary saving is

```text
c(1 - c) = 575/576^2 = 575/331776.
```

That rational is larger than the selected kappa. It is not adopted. The stock
coefficient is `lcm(28416, 28425) = 269241600`. The rate sits strictly between
`17/10000` and `1/512`.

The inherited width estimate doubles `8195` to `16390` and again to `32780`.
At exponent 20,

```text
32780 · (17/16) · 20 = 696575 < 2^20,
```

and `2^(20/576) < 17/16`, because `2^20 · 16^576 < 17^576`. Those two
comparisons are what the threshold argument uses to get `2k < e` at
`e = 2^20`.

## What was executed

The checker compares these integers. It does not enclose the moment and it
does not reconstruct the paid requests.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the ordinary coupling in PR 3690,
head `03c141ef1fd372cf42951488767537e55675c072`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
rate. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/ordinary-rate-threshold/verify.py
python3.12 -B research/ordinary-rate-threshold/test_verify.py
python3.12 -B scripts/research_package.py --package research/ordinary-rate-threshold
```

## Open next questions

This rate is the comparison. Enclosing the moment would leave it.

## Credit

zxv published the ordinary rate `575/331776` and the width threshold.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
