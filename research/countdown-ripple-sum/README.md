# A countdown ripple sums to `2N - popcount(N)`

**Partial. No new exponent.**

Decrementing `m` rewrites its trailing zeros and the first one-bit. That
prefix has length `1 + v_2(m)`, where `v_2(m)` is the number of trailing
zeros. Across the countdown from `N` down to 1, the lengths therefore sum to

```text
sum_(m=1)^N (1 + v_2(m)).
```

Passing from `m - 1` to `m` changes the popcount by `1 - v_2(m)`, so the
closed forms increase by exactly the new term:

```text
sum_(m=1)^N v_2(m) = N - popcount(N),
sum_(m=1)^N (1 + v_2(m)) = 2N - popcount(N).
```

Both identities hold for every `N` from 1 through `2^24 = 16,777,216`. At
the last point the popcount is 1, and the ripple sum is `33,554,431`. The
selected kappa is unchanged.

## What was executed

The checker walks every integer in that range, checks the popcount step, and
compares both running totals with the closed forms. It does not run the word
multiplier.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the counter paragraph of PR 3787,
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
python3.12 -B research/countdown-ripple-sum/verify.py
python3.12 -B research/countdown-ripple-sum/test_verify.py
python3.12 -B scripts/research_package.py --package research/countdown-ripple-sum
```

## Open next questions

The two sums are proved by the one-step change in popcount, and every N
through 2^24 was checked. A word-multiplier replay would leave this package.

## Credit

Jose Manuel (jmbarrancoml) stated this countdown sum in PR 3787. This package
checks the popcount step that produces it.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
