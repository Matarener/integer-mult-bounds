# The rotating-normal correction spends the deficit

**Partial. No new exponent.**

The standard complex structure on eight coordinates sends each of the 120
canonical E8 lines to another line, squares to minus the identity, and fixes
none of them projectively. The 120 lines form 60 pairs. Each image hyperplane
contains 63 roots and has rational rank 7.

Six nested steps then move the inactive address axis along

`0 -> 1 -> 8 -> 15 -> 22 -> 29 -> 36`.

The chart dimension is 43. The rank histogram is `{1: 6, 6: 6, 7: 6}`, so the
uncorrected mass is `6 * (1 + 6 + 7) = 84`. The two endpoint address masks
differ by the input axis and axis 36. XORing that rank-two mask closes the
second bank. The paid mass is `84 + 2 = 86 = 43 * 2`, so the zero-saving bill
is exactly 1.

At saving `1/499`, the same pinned outward rounding puts the corrected bill's
lower endpoint above 1. One extra rank-one child, without that address
correction, still has its upper endpoint below 1. The selected kappa is
unchanged.

## What was executed

The checker rebuilds the roots, walks the six steps, and prices both
histograms. It does not rerun the 111 port boundary charts.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the rotating-normal closure in
PR 3772, head `5b1d4c2ade90dfa0d8b837148cc5b9cc4be1cdab`.

## Scope and evidence

Original card: `bit-helper-contract`, priority revision 6, refined to this
closure. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the lever rounding and
the root geometry. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/rotating-normal-closure/verify.py
python3.12 -B research/rotating-normal-closure/test_verify.py
python3.12 -B scripts/research_package.py --package research/rotating-normal-closure
```

## Open next questions

This correction spends the deficit. A fused endpoint would leave it.

## Credit

Gonzalo Mier recorded this six-step closure. That account credits the
Gaussian line construction to Joel Pulikkan / GamingPuzzled.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
