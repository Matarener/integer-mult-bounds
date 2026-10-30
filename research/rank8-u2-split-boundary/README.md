# Rank-8/u2 slack versus one moved family

**Negative screen, no new κ.** Selected κ stays `0.001672660197076918`.

## Question

PR #3889's tight integer cell is the nine-call profile with paid mass delivered
at ranks 8 and 2, selected centre 64, and two unpaid coordinates. Its open
question asks whether a physical producer and consumer can fit that cell's
remaining moment slack. The stated stop test is an additive bill of rank-1
children, with no mass credit: 16 still pass `a = 1/98`, and 17 fail, on the
pooled idle histogram.

This note does not build that producer. It asks whether the same 16-child
sentence survives the integer per-call family splits already allowed by the
coverage identity.

## Contract

Width `m = 73`, nine calls, 896 live families, centre 64 on every call, and
two unpaid coordinates. Call mass is `71 * families + 64`. The ideal per-call
paid profile is `{8: 698, 2: 1}`, mass 5586, the same local mass as the
selected word `{1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}`. A call needs
at least 78 families; 77 leaves negative idle. Nine-call totals are paid
50274, idle 13918 and mass 64192.

Idle children have rank at most 51. Each call's idle is packed by the usual
exchange: `floor(idle / 51)` children of rank 51 and at most one remainder.
The pooled alternative packs all 13918 idle units together as
`{51: 272, 46: 1}`.

Additive rank-1 children are extra. They are not paid for by deleting idle
mass. The moment is the sum of pinned `child_cost` enclosures divided by 896.
A high end below 1 is a pass, and a low end above 1 is a fail, at
`a = 1/98`.

## Result

| Hosting | 15 extra rank-1 | 16 extra rank-1 | 17 extra rank-1 |
|---|---|---|---|
| Pooled idle `{51: 272, 46: 1}` | | pass | fail |
| Five calls of 100 families and four of 99 | | pass | fail |
| One family moved between two 100-calls: `101, 100, 100, 100, 99 × 5` | pass | fail | |

The third row is the second row after transferring one family from one
100-call to another. Its separate idle histogram is
`{51: 267, 48: 3, 28: 5, 17: 1}` instead of `{51: 266, 48: 5, 28: 4}`.
That one remainder of rank 17 is enough to spend the last rank-1 child of
slack. The published "16 still pass" sentence is true for the pooled
histogram and for the balanced split, and false for this adjacent split.

## What this does not establish

No rank-8 local word, no consumer, no owner chronology, and no proof that the
selected template uses either split. Unknown restoration and precision costs
are not zero. Passing either split is not a supplier. The catalogue acceptance
gate for a new helper inventory is not met. Selected κ is unchanged.

## Reproduce

```sh
python3.12 -B research/rank8-u2-split-boundary/verify.py
python3.12 -B scripts/research_package.py --package research/rank8-u2-split-boundary
```

Expected marker: `PASS_RANK8_U2_SPLIT_BOUNDARY pooled=LT/GT balanced=LT/GT shifted=LT/GT no_new_kappa`.

## Open next questions

1. Which of the integer splits of 896 into nine calls of at least 78 families
   still pass 16 additive rank-1 children? The examples show the answer is
   not "all" and not "only the pool".
2. Is there a literal local word with paid profile `{8: 698, 2: 1}`, centre
   64 and two unpaid coordinates? Until there is, this boundary does not
   reject a construction.

## Credit

The ceiling engine and the halving cap are Douglas Colkitt's
`research/complex-local-word-ceiling`, with Claude assistance. The 16/17
pooled screen and the rank-8/u2 question are ToikY's PR #3889, following
Nick Petalas's PR #3874. The coverage identity is PR #1012. This note only
recomputes that screen on two family splits.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
