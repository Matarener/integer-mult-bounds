# Eleven length-22 splits survive

**Partial. No new exponent.**

At seven labels there are `2^6 = 64` masks of each Hamming-weight parity. For
a split `(s, t)` the even budget is

```text
B0 = C(s, 2) + C(t, 2) - 63
```

and the pair identity needs `ceil((s t - 64) / 2)`. The time bound requires
both sides to be at most 11. The odd budget requires `s t >= 64`. A positive
even budget also supplies the upper estimate `B0 + floor(B0^2 / 4)`.

Exactly eleven splits with `s >= t` pass all four tests. Their budgets match
the published table, from `(11, 11)` with `B0 = 47` and need 29, down to
`(10, 7)` with `B0 = 3` and need 3. Only `(11, 11)` has `|P| = 22`, so only
that split is self-avoiding. The other ten force 1 to 5 revisits.

`(13, 5)` and `(12, 6)` meet the counting tests and fail the time bound.
`(9, 8)` has `B0 = 1` and need 4, so the pair identity removes it. No split
with a nonpositive even budget passes the identity. The smallest point count
that passes the counting tests is 17, and its only survivors are `(10, 7)`
and `(11, 6)`. Importing that standing exclusion leaves 9 splits.

## What was executed

The checker evaluates the budgets. It does not census words and it does not
claim `f(7)`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the split domain in PR 3708, head
`44334c60341e4354378666838c7921e6cabd6c03`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
domain. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/l22-split-domain/verify.py
python3.12 -B research/l22-split-domain/test_verify.py
python3.12 -B scripts/research_package.py --package research/l22-split-domain
```

## Open next questions

This domain is the count. A word census would leave it.

## Credit

petalas published the length-22 split domain.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
