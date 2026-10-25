# The Neumann bounds at the displayed-expression gap

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, keep survivor
bandwidth `b=3` and replace `delta=1/5776` by one minus the rational
lower bound `L` for `exp(-9 pi/722)+5 exp(-18 pi)`. On the normalized
Schur section the three Neumann right-hand sides then lie in `(26, 27]`,
`(3937, 3938]`, and `(320, 321)`.

No new kappa is claimed. The selected record is unchanged. This applies
the pinned lemma to one section. It does not prove the Neumann series.

## The three tighter bounds

`L` is the same rational lower bound used for the displayed expression:
one over the upper enclosure of `exp(9 pi/722)`, plus five over the upper
enclosure of `exp(18 pi)`. Every normalized off-diagonal absolute row sum
on `0,1,2,7,8,9` is strictly below `L`, and `L` itself is strictly below
`1-1/5776`. The lemma therefore applies with `rho=L` and
`delta=1-L>1/5776`.

Its right-hand sides are `1/delta`, `1/delta + 6 rho/delta^2`, and the
square root of their product. Those values are at most `27`, at most
`3938`, and strictly between `320` and `321`. Against the bounds at
`delta=1/5776`, the infinity bound is smaller by a factor in
`[221, 222)`, the 1-norm bound by a factor in `[50824, 50825)`, and the
squared 2-norm bound by a factor in `[11274122, 11274123)`. The same
Machin comparison gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-neumann-tight/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-neumann-tight
```

The verifier authenticates the pinned notes, checks the row-sum and
bandwidth hypotheses, and encloses the three right-hand sides.

## Open next questions

The lemma also passes these bounds to every principal restriction,
because deleting columns cannot increase a row sum or a bandwidth.
Nothing here forms those restrictions.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
bounds at `delta=1/5776` are the preceding audit. These tighter bounds
are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
