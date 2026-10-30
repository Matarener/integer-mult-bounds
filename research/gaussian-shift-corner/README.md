# A shifted truncated Gaussian keeps both separator corners positive

On the truncated kernel `exp(-h^2 + h/2)`, deleting the interior
`{3,4,5,6}` leaves both Schur directions between vertices 1 and 8
positive. The forward entry lies strictly between `1/1600` and `1/1500`.
The reverse entry lies strictly between `5/10000000` and `6/10000000`.
The half-bandwidth in increasing survivor order is 3.

No new kappa is claimed. The scale here is `gamma=1` and `s=1/4`, not the
eventual large prime scale.

## The shifted row

`GAUSSIAN.md` writes the narrow kernel
`k(h)=exp(-a rho h^2-2a beta0 h)`. `vendor/GAUGEFREE-INTERIORS.md`
normalizes it by `G'_s(0)=1` and `exp(-gamma u^2 + 2 gamma s u)`. This
section takes `gamma=1` and `s=1/4`, and keeps signed distances 1 and 2
only. The four weights are `exp(-1/2)`, `exp(-3/2)`, `exp(-3)`, and
`exp(-5)`. Forty terms of each alternating series enclose them. Every
off-diagonal absolute row sum is less than `9/10`.

The path has length 10 and diagonal 1. `vendor/FINE-PRIME.md` says an
eliminated interior joins only its two neighboring separators. The
survivors stay in increasing index: `0,1,2,7,8,9`.

## The two corners

The only survivor pairs at distance 3 are the two directions between 1
and 8. From 1 to 8 the enclosure lies strictly between `1/1600` and
`1/1500`. From 8 to 1 it lies strictly between `5/10000000` and
`6/10000000`. The row of vertex 0 equals its original row, so it has no
entry at 7, 8, or 9. The half-bandwidth is 3. The original-index span of
either corner is 7.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-shift-corner/verify.py
python3 -B scripts/research_package.py --package research/gaussian-shift-corner
```

The verifier authenticates the three pinned notes and encloses both
corners by rational interval arithmetic.

## Open next questions

The eventual caller uses `gamma=a rho` with `a=pi alpha^2`, which grows.
Nothing here takes that scale.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note and the
normalized shift in its gauge-free note. The centered corner is the
preceding audit. This shifted pair is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
