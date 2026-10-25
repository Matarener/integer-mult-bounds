# The retimed pair keeps rank mass 5,135

**Partial. No new exponent.**

One direct jump replaces `H1 + H2` by `H3`. The two pairs in an invocation
change the local histogram from

```text
{1:2439, 2:726, 3:224, 4:102, 5:20, 8:8}
```

to

```text
{1:2437, 2:724, 3:226, 4:102, 5:20, 8:8}
```

The rank change is `-2·1 - 2·2 + 2·3 = 0`, so both histograms have rank mass
5,135. The width inventory `{4:26, 5:2, 6:18, 7:52, 8:97, 9:213}` still has
`26 + 2 + 18 + 52 + 97 + 213 = 408` helpers.

For every rational `p` strictly between 0 and 1, write the complementary gap
`g ≥ 1`. Then `3^g > 1` and `3^g > 2^g`, so

```text
(1/3)^p > 1/3  and  (2/3)^p > 2/3
```

Adding these strict inequalities gives `(1/3)^p + (2/3)^p > 1`, and multiplying
by `3^p` gives

```text
3^p < 1 + 2^p
```

Thus the moment contribution of one rank-3 child is strictly smaller than the
contribution of one rank-1 child and one rank-2 child, for every saving
strictly between 0 and 1.

## What was executed

The checker adds the two histograms and checks the integer comparison,
including the induction step through gap 24. It does not replay the 632
columns.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the local exchange in PR 3642,
head `044d24f12e74f228dd462c07ae2d7f3ea35e2be9`.

## Scope and evidence

Original card: `scalar-to-moment`, priority revision 6, refined to this pair.
[TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/retimed-pair-moment/verify.py
python3.12 -B research/retimed-pair-moment/test_verify.py
python3.12 -B scripts/research_package.py --package research/retimed-pair-moment
```

## Open next questions

This pair is the exchange. Replaying the columns would leave it.

## Credit

roger-sato published the commuting release retiming and these two histograms.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
