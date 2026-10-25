# Printed rank-7 pattern cover

## Question

The rank-7 note prints a ten-pattern basis and the width inventory `{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}`. Do those patterns cover the inventory, and does the printed face swap preserve the widths?

## Result

Each width total equals nine times the inventory count:

| width | pattern total | nine copies |
| --- | --- | --- |
| 4 | 234 | 234 |
| 5 | 18 | 18 |
| 6 | 144 | 144 |
| 7 | 468 | 468 |
| 8 | 891 | 891 |
| 9 | 1917 | 1917 |

The six widths cover 3,672 slots. The ten multiplicities sum to 2,016. The printed swap `[7,8,8,9]` with `[7,9]` against `[8,8]` with `[7,7,9,9]` has width multiset `{7,7,8,8,9,9}` on both sides. The selected κ is unchanged.

## Boundary

This adds the printed patterns. It does not rerun the packing solver, certify the cap, or decide whether 1,063 swaps meet the stated Hall deficit. The stop rule is to record this cover.

## Reproduce

```bash
python3.12 -B research/rank7-basis-cover/verify.py
python3.12 -B research/rank7-basis-cover/test_verify.py
```

## Open next questions

None. The printed patterns and the inventory are finite. Rerunning the solver would leave this package.

## Credit

Marius-Paul Dumitrean (mdumitrean) printed the basis and the swap in PR #2979. The checker adds the pattern widths. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
