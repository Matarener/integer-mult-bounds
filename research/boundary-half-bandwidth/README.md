# Half-bandwidth after removing cell interiors

## Question

After a linear window drops the interior of every piece longer than `4w`, how far apart can two coupled boundary rows be in the remaining order?

## Result

A piece of length at most `4w` stays entirely boundary. A longer piece keeps its first `w` rows and its last `w` rows, and those two interior-edge buffers are disjoint. In the remaining order the two groups occupy `2w` consecutive places, so the Schur fill between them has rank separation `2w-1`. An original pair at distance at most `w` has rank separation at most that distance.

All 196,605 compositions with width 1, 2, or 3 and length at most 16 obey the separation bound, and each of those widths attains `2w-1`. A single piece of length `4w+1` attains the same separation for every width from 1 through 40. The published allowance is `2w`, which covers `2w-1`. The selected κ is unchanged.

## Boundary

This checks these compositions and witnesses. It does not run the Gaussian core. The stop rule is to record this bandwidth.

## Reproduce

```bash
python3.12 -B research/boundary-half-bandwidth/verify.py
python3.12 -B research/boundary-half-bandwidth/test_verify.py
```

## Open next questions

None. The rank separation is settled on these compositions. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the boundary half-bandwidth in PR #3851. The checker measures rank separation after interior removal. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
