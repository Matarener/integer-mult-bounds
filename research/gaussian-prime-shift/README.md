# At the prime-scale shift endpoint both separator corners stay positive

At `p=19`, `theta=1/1444`, `alpha=3`, and `gamma=9 pi 1445/1444`, take the
bandwidth-2 truncation at `beta0=-1/2`. Deleting `{3,4,5,6}` leaves both
Schur directions between vertices 1 and 8 positive. The forward entry lies
strictly between `1/10^50` and `1/10^49`. The reverse entry lies strictly
between `1/10^222` and `1/10^221`. The half-bandwidth in increasing survivor
order is 3.

No new kappa is claimed. The selected record is unchanged. This is one
prime, one shift endpoint, and width 2, not the all-size bandwidth claim.

## The endpoint shift

`GAUSSIAN.md` writes `k(h)=exp(-a rho h^2-2a beta0 h)` with
`|beta0/rho|<1/2`. `vendor/GAUGEFREE-INTERIORS.md` sets
`s=-beta0/rho` and allows `|s|<=1/(2 rho)`. Here
`s=722/1445=1/(2 rho)`, so `beta0=-1/2`. That is the closed endpoint of
the gauge-free range, and it still lies inside the strict Gaussian range.
The same Machin and `log(304)` comparison used for the centered section
gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

The four kept weights are `exp(-gamma/1445)`,
`exp(-gamma 2889/1445)`, `exp(-gamma 2892/1445)`, and
`exp(-gamma 8668/1445)`. The forward distance-1 weight is the heavy one:
its exponent is `a theta`. Every off-diagonal row sum of this truncation
is below `99/100`, so the section's own row gap exceeds `1/(16 p^2)`.
That is a fact about the truncated Toeplitz kernel. It is not a check of
the note's bound `||N-I||_infinity<=exp(-2 a theta)+5 exp(-2a)` for the
gauged matrix `N`.

## The two corners

The path has length 10 and diagonal 1. `vendor/FINE-PRIME.md` says an
eliminated interior joins only its two neighboring separators. The
survivors stay in increasing index: `0,1,2,7,8,9`. Vertices 0 and 9 do
not meet the interior, so their Schur rows stay the original rows. The
only survivor pair at distance 3 that can be nonzero is `(1,8)`.

Vertex 1 meets the interior only at vertex 3, and vertex 8 meets it only
at vertex 6. The forward corner is the square of the step `+2` times the
interior inverse entry from local index 3 back to 0. The reverse corner
is the square of the step `-2` times the opposite interior entry. Both
interior entries are negative, and both corners are positive. The
half-bandwidth is 3. The original-index span of either corner is 7.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-prime-shift/verify.py
python3 -B scripts/research_package.py --package research/gaussian-prime-shift
```

The verifier authenticates the three pinned notes and encloses both
corners by rational interval arithmetic.

## Open next questions

The note's matrix `N` multiplies this kernel by the diagonal chirp
`exp(a theta t^2)`. Nothing here includes that gauge.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note and the
normalized shift in its gauge-free note. The centered `p=19` corner is
the preceding audit. This endpoint shift is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
