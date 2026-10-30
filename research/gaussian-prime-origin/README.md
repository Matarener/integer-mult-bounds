# Translating the prime-scale origin puts every row sum below 97/100

At `p=19`, `beta0=-1/2`, and bandwidth 2, put the chirp origin on vertex
0 by taking `t_i=i`. Every off-diagonal row sum on the 10-vertex path is
strictly below `97/100`. The last row, whose steps all point backward,
is strictly below `1/1000`.

No new kappa is claimed. The selected record is unchanged. This is one
prime, one shift endpoint, one translated origin, and width 2.

## The translated origin

`vendor/GAUGEFREE-INTERIORS.md` writes
`log N_ij = -a rho h^2 - 2 a beta0 h + a theta (t_i^2 - t_j^2)`. The
preceding audit centred the path at `9/2`, and the entry from vertex 0
to vertex 1 exceeded 1. This section uses the same endpoint kernel,
`s=722/1445` and `beta0=-1/2`, with `t_i=i`. The same Machin comparison
gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

With this origin the forward step from vertex `i` has exponent
`-2 a theta (i+1)`. The largest of those steps is the one leaving
vertex 0, and it equals `exp(-2 a theta)=exp(-9 pi/722)`. Every other
in-band entry is at most the backward step into vertex 9, whose
exponent is `-6462 pi/361`. A row has at most one forward step and at
most three other in-band entries.

The forward step is strictly below `193/200`. Three copies of the
backward majorant are strictly below `1/1000`. Their sum is strictly
below `97/100`, and that majorant covers all ten rows. The infinity-norm
row gap of this section is therefore greater than `3/100`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-prime-origin/verify.py
python3 -B scripts/research_package.py --package research/gaussian-prime-origin
```

The verifier authenticates the three pinned notes, checks the exponent
of every in-band entry, and encloses the two majorants by rational
series.

## Open next questions

The separator corners of this translated kernel are not enclosed here.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note and the
chirp formula in its gauge-free note. The centred row sum above 1 is
the preceding audit. This translated origin is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
