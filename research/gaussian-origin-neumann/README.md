# The narrow Neumann bounds at bandwidth 3 and gap 1/5776

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the normalized Schur
section on `0,1,2,7,8,9` meets the hypotheses of the pinned narrow
Neumann lemma with bandwidth `b=3` and `delta=1/5776`. The lemma's three
right-hand sides are `5776`, `200144176`, and `5776*sqrt(34651)`.

No new kappa is claimed. The selected record is unchanged. This applies
the pinned lemma to one section. It does not prove the Neumann series.

## The three bounds

`INVERSE-CONDITIONING.md` takes `E[i,j]=0` whenever `|i-j|>b` and
`max_i sum_j |E[i,j]| <= rho < 1`, with `delta=1-rho` and `H=I-E`. It
concludes

```text
||H^-1||_infinity <= 1/delta,
||H^-1||_1 <= 1/delta + 2 b rho/delta^2,
||H^-1||_2 <= sqrt((1/delta)(1/delta + 2 b rho/delta^2)).
```

On this section the normalized matrix is `H`. In survivor order every
entry at distance greater than 3 is zero, so `b=3` is allowed. Every
off-diagonal absolute row sum is at most `rho=5775/5776`. Therefore
`1/delta=5776` and

```text
1/delta + 6 rho/delta^2 = 200144176 = 5776*34651.
```

The squared 2-norm bound is `5776^2*34651`. Trial division shows that
`34651` is prime, so the 2-norm bound is `5776*sqrt(34651)`. No factor
in these bounds depends on the six-by-six size. The same Machin
comparison gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-neumann/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-neumann
```

The verifier authenticates the pinned notes, checks the bandwidth and
row-sum hypotheses, and evaluates the three right-hand sides.

## Open next questions

The six off-sums also lie below the displayed expression, whose gap is
larger than `1/5776`. Nothing here recomputes the bounds at that gap.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
normalized corners are the preceding audit. These bounds are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
