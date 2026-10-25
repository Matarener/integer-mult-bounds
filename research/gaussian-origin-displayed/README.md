# Every translated width-2 row sum lies below the displayed Gaussian bound

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, every off-diagonal
row sum on the 10-vertex path is strictly below the expression
`exp(-2 a theta)+5 exp(-2 a)` displayed in `GAUSSIAN.md`. At these
parameters that expression is `exp(-9 pi/722)+5 exp(-18 pi)`.

No new kappa is claimed. The selected record is unchanged. This is one
prime, one shift endpoint, one translated origin, and width 2.

## The comparison

The forward step from vertex 0 has coefficient `9/722` and equals the
first term of the displayed expression. Every other in-band entry has
coefficient at least `6462/361`. The gap from that coefficient down to
`18` is `36/361`, and `exp(36 pi/361)` is strictly below `5/3`. Three
copies of the largest other entry are therefore strictly smaller than
the second term `5 exp(-18 pi)`.

A row has at most one forward step and at most three other in-band
entries. The resulting majorant lies strictly below a lower bound for
the displayed expression, on all ten rows. The same Machin comparison
gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-displayed/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-displayed
```

The verifier authenticates the pinned notes, checks every in-band
exponent, and compares the row majorants with the displayed expression.

## Open next questions

Deleting `{3,4,5,6}` replaces six rows by their Schur complement.
Nothing here encloses those survivor row sums.

## Credit

Cinna Davis wrote the narrow kernel and the displayed row estimate in
the PR4100 Gaussian note. The translated separator corners are the
preceding audit. This comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
