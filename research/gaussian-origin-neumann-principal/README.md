# Principal restrictions inherit the displayed-gap Neumann ceilings

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, every principal
restriction of the normalized Schur section on `0,1,2,7,8,9` obeys the
same Neumann ceilings as the full section: infinity norm at most `27`,
1-norm at most `3938`, and 2-norm strictly below `321`.

No new kappa is claimed. The selected record is unchanged. This applies
the pinned lemma to one section and its principal restrictions. It does
not prove the Neumann series.

## The 64 sections

`INVERSE-CONDITIONING.md` says that order compression can only reduce
distances, so every principal section obeys the same bounds. Let `L` be
the rational lower bound for `exp(-9 pi/722)+5 exp(-18 pi)`. The full
normalized rows have off-diagonal absolute sums strictly below `L`, and
`L<1-1/5776`.

There are six rows and five other survivor columns, hence 192 deletions.
Each deletion sums a subset of the nonnegative per-entry majorants, so it
is at most the full-row sum and strictly below `L`. There are 64 survivor
subsets. In each subset the compressed distance between two vertices is at
most their distance in the full survivor order, and every full-order pair
at distance greater than 3 is an exact zero. Every restriction therefore
satisfies the lemma at `b=3` and `rho=L`. The right-hand sides remain in
`(26, 27]`, `(3937, 3938]`, and `(320, 321)`. The same Machin comparison
gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-neumann-principal/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-neumann-principal
```

The verifier authenticates the pinned notes, checks the 192 deletions and
64 compressed orders, and reuses the displayed-gap ceilings.

## Open next questions

Direct elimination of this normalized six-by-six section would enclose its
actual inverse infinity norm. Nothing here inverts that matrix.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
displayed-gap bounds are the preceding audit. These principal restrictions
are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
