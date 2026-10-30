# Stage-2 break-even offset

## Question

The rank-7 note prints five stage-2 extraction prices and their margins against break-even. Do the margins share one exact offset?

## Result

Each printed margin equals the negation of its price minus 2,091,300. The two prices are −2,101,683 and −2,106,679, and the two margins are 10,383 and 15,379. Both gaps are 4,996. The five prices sum to −10,523,403. The selected κ is unchanged.

## Boundary

This checks the printed rows. It does not rerun the extraction search or rebuild the words. The stop rule is to record this offset.

## Reproduce

```bash
python3.12 -B research/stage2-breakeven/verify.py
python3.12 -B research/stage2-breakeven/test_verify.py
```

## Open next questions

None. The five printed rows are finite. Rerunning the extraction search would leave this package.

## Credit

Marius-Paul Dumitrean (mdumitrean) printed the stage-2 prices in PR #2979. The checker compares each margin with the common offset. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
