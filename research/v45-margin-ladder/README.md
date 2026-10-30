# Printed V45 margin ladder

## Question

The rank-7 note prints the V45 margins for one through four helpers as −53,141 / −27,770 / −2,399 / +22,972, and it prints five joint prices. Do the margins share one difference, and do the prices sum to the stated stage-1 total?

## Result

The four margins form an arithmetic progression with difference 25,371. The four-helper value +22,972 is the printed V45 joint margin. The five joint prices −8,388,172, −10,499,041, −10,499,041, −8,382,370 and −8,382,370 sum to −46,150,994. The selected κ is unchanged.

## Boundary

This checks the printed margins and prices. It does not rerun the extraction search or rebuild the words. The stop rule is to record this ladder.

## Reproduce

```bash
python3.12 -B research/v45-margin-ladder/verify.py
python3.12 -B research/v45-margin-ladder/test_verify.py
```

## Open next questions

None. The printed margins and prices are finite. Rerunning the extraction search would leave this package.

## Credit

Marius-Paul Dumitrean (mdumitrean) printed the climb and the joint prices in PR #2979. The checker compares the differences and adds the prices. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
