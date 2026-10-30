# Idle rank of a nine-stage pair

## Question

A pair starts at level −1 and finishes at level 8. Each level costs 8 unless an owned shear covers it, and a ridden stage pays that 8. What is the total, and what is the opening idle before the first stage?

## Result

For every assignment of the nine stages to absent, ridden or owned, the idle sum is `8 * (9 - owned shears)`. There are 19,683 assignments. The opening idle before a first stage `s` is `8s`. Before stages 2, 4 and 6 that opening is 16, 32 and 48. The selected κ is unchanged.

## Boundary

This adds the idle segments of one pair. It does not census bridge schedules, place a bridge, or price an alphabet. The stop rule is to record this sum.

## Reproduce

```bash
python3.12 -B research/idle-rank-sum/verify.py
python3.12 -B research/idle-rank-sum/test_verify.py
```

## Open next questions

None. The stage assignments are finite. A schedule census would leave this package.

## Credit

Matarener recorded the level accounting in PR #3836. The checker adds every assignment. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
