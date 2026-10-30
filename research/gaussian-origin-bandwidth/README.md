# The normalized separator corners stay positive at half-bandwidth 3

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, delete the interior
`{3,4,5,6}` and divide each Schur row on `0,1,2,7,8,9` by its diagonal.
The normalized corner from vertex 1 to vertex 8 lies strictly between
`1/10^50` and `1/10^49`. The normalized corner from vertex 8 to vertex 1
lies strictly between `1/10^221` and `1/10^220`. In survivor order those
corners have distance 3, and every other survivor pair at distance
greater than 2 is exactly zero. The survivor-order half-bandwidth is 3.

No new kappa is claimed. The selected record is unchanged. This is one
normalized Schur section, not an all-size bandwidth theorem.

## The corners and the zeros

`INVERSE-CONDITIONING.md` uses a bandwidth `b` for which `E[i,j]=0`
whenever `|i-j|>b`. On this section the survivor order is
`0,1,2,7,8,9`. The six diagonals are positive, so dividing by them does
not fill a zero. The pairs at survivor distance greater than 2 are
`(0,7)`, `(0,8)`, `(0,9)`, `(1,8)`, `(1,9)`, and `(2,9)`. Apart from
`(1,8)`, each of those entries and its transpose is an exact zero of the
Schur matrix, hence of the normalized matrix. The two normalized corners
stay inside the same positive windows as the unnormalized corners. The
same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-bandwidth/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-bandwidth
```

The verifier authenticates the pinned notes, encloses the two normalized
corners, and checks the exact zeros beyond survivor distance 2.

## Open next questions

The narrow Neumann lemma can now take `b=3` and a row gap of `1/5776`
on this section. Nothing here substitutes those values into the inverse
norm bounds.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
principal restrictions are the preceding audit. These corners are this
audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
