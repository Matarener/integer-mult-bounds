# The translated prime-scale kernel keeps both separator corners positive

At `p=19`, `beta0=-1/2`, and `t_i=i`, delete the interior `{3,4,5,6}` from
the bandwidth-2 chirped path. Both Schur directions between vertices 1
and 8 stay positive. The forward entry lies strictly between `1/10^50`
and `1/10^49`. The reverse entry lies strictly between `1/10^221` and
`1/10^220`. The half-bandwidth in increasing survivor order is 3.

No new kappa is claimed. The selected record is unchanged. This is one
prime, one shift endpoint, one translated origin, and width 2.

## The translated section

`vendor/GAUGEFREE-INTERIORS.md` writes
`log N_ij = -a rho h^2 - 2 a beta0 h + a theta (t_i^2 - t_j^2)`. This
section takes the endpoint kernel `s=722/1445`, `beta0=-1/2`, and puts
the origin on vertex 0, so `t_i=i` and `t_8^2-t_1^2=63`. The same Machin
comparison gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`. The
preceding audit showed that every off-diagonal row sum of this section
is below `97/100`.

The path has length 10 and diagonal 1. Survivors stay in increasing
index: `0,1,2,7,8,9`. Vertex 1 meets the interior only at vertex 3, and
vertex 8 meets it only at vertex 6. The forward corner uses the two
steps of `+2`. The reverse corner uses the two steps of `-2`. Both
interior inverse entries are negative, and both corners are positive.
Vertices 0 and 9 do not meet the interior, so their Schur rows stay the
original rows. The half-bandwidth is 3. The original-index span of
either corner is 7.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-corner/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-corner
```

The verifier authenticates the three pinned notes and encloses both
corners by rational interval arithmetic.

## Open next questions

`GAUSSIAN.md` displays `exp(-2 a theta)+5 exp(-2 a)`. Nothing here
compares the ten row sums with that expression.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note and the
chirp formula in its gauge-free note. The translated row sums are the
preceding audit. These separator corners are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
