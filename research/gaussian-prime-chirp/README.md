# A centred prime-scale chirp keeps both corners positive, with a row sum above 1

At `p=19`, `beta0=-1/2`, and the centred coordinates `t_i=i-9/2`, the
bandwidth-2 chirped section keeps both Schur directions between vertices
1 and 8 positive. The forward entry lies strictly between `1/10^50` and
`1/10^49`. The reverse entry lies strictly between `1/10^222` and
`1/10^221`. The half-bandwidth in increasing survivor order is 3.

The same section has no positive infinity-norm row gap. The centred
entry from vertex 0 to vertex 1 equals `exp(63 pi/1444)`, which is
strictly greater than 1. At these parameters the displayed expression
`exp(-2 a theta)+5 exp(-2 a)` is strictly less than 1.

No new kappa is claimed. The selected record is unchanged. This is one
prime, one shift endpoint, one centred 10-vertex chirp, and width 2.

## The centred chirp

`vendor/GAUGEFREE-INTERIORS.md` writes
`log N_ij = -a rho h^2 - 2 a beta0 h + a theta (t_i^2 - t_j^2)` and
describes the gauge as centred. On vertices `0` through `9` the centre
is `9/2`, so `t_i=i-9/2`. Then `t_1^2=t_8^2=49/4`. The kernel is the
endpoint kernel of the preceding audit: `s=722/1445` and `beta0=-1/2`.
The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

Vertex 1 meets the interior only at vertex 3, and vertex 8 meets it
only at vertex 6. The chirped Schur complement puts the forward corner
strictly between `1/10^50` and `1/10^49`, and the reverse corner
strictly between `1/10^222` and `1/10^221`. Vertices 0 and 9 do not
meet the interior, so their Schur rows stay the original rows. The
half-bandwidth is 3.

## The row sum

The distance-1 exponent from vertex 0 to vertex 1 is `8 a theta` from
the squares minus `a theta` from the endpoint kernel, hence
`7 a theta=63 pi/1444`. Its exponential is strictly greater than 1.
The distance-2 entry in that row is positive, and vertex 0 has no Schur
fill, so the off-diagonal row sum is strictly greater than 1. Every
wider bandwidth keeps this same positive entry, so those row sums stay
above 1 as well.

`GAUSSIAN.md` displays `exp(-2 a theta)+5 exp(-2 a)`. At `p=19` and
`theta=1/1444` that expression is strictly less than 1. This section
therefore sits outside the hypothesis `||E||_infinity<1` of the narrow
Neumann bound.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-prime-chirp/verify.py
python3 -B scripts/research_package.py --package research/gaussian-prime-chirp
```

The verifier authenticates the three pinned notes and encloses the
corners and the row entry by rational interval arithmetic.

## Open next questions

Moving the origin to `t_i=i` changes the square differences. Nothing
here encloses those row sums.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note and the
centred chirp in its gauge-free note. The endpoint Toeplitz corners are
the preceding audit. This centred section is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
