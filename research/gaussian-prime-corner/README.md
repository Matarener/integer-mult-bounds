# A prime-scale truncated Gaussian keeps its separator corner positive

At `p=19`, `theta=1/1444`, `rho=1445/1444`, and `alpha=3`, the centered
bandwidth-2 truncation of `k(h)=exp(-gamma h^2)` uses
`gamma=9 pi 1445/1444`. Deleting the interior `{3,4,5,6}` leaves a
positive Schur entry between vertices 1 and 8. That entry lies strictly
between `1/10^136` and `1/10^135`. The half-bandwidth in increasing
survivor order is 3.

No new kappa is claimed. The selected record is unchanged. This is one
prime and one truncation width, not the all-size bandwidth claim.

## The prime parameters

`GAUSSIAN.md` takes `theta=t/s-1` in `[1/(4p^2),1/p^2]`, `rho=1+theta`,
`alpha=ceil(sqrt((4/pi)log(16p)))`, and `a=pi alpha^2`. This section
uses the prime `p=19` and the lower endpoint `theta=1/1444`. Machin's
formula and the series for `log(304)` prove `pi < log(304) < 9 pi/4`,
so `alpha=3`, and they prove `4 log(304) <= 9 pi <= 5 log(304)`. Thus
`gamma=a rho=9 pi 1445/1444`. The shift is zero, which
`|beta0/rho|<1/2` allows.

`vendor/GAUGEFREE-INTERIORS.md` normalizes the same kernel by
`gamma=a rho` and `G'_s(0)=1`. The section keeps distances 1 and 2
only. The note's physical bandwidth is `O(sqrt(p) polylog p)`; width 2
is the truncation under test.

## The corner

The path has length 10 and diagonal 1. `vendor/FINE-PRIME.md` says an
eliminated interior joins only its two neighboring separators. The
survivors stay in increasing index: `0,1,2,7,8,9`. Vertices 0 and 9 do
not meet the interior, so their Schur rows stay the original rows. The
only survivor pair at distance 3 that can be nonzero is `(1,8)`. Vertex
1 meets the interior only at vertex 3, and vertex 8 meets it only at
vertex 6, both at weight `exp(-4 gamma)`.

Seven Neumann terms on that `4x4` interior, with the tail bounded by
the off-diagonal infinity norm, put the corner strictly between
`1/10^136` and `1/10^135`. Both directions agree because the kernel is
even. The half-bandwidth is 3. The original-index span of the corner
is 7.

Every off-diagonal row sum of this truncation is below `1/10^11`. That
is a fact about the truncated section. It is not a check of the note's
tail bound `exp(-2 a theta)+5 exp(-2a)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-prime-corner/verify.py
python3 -B scripts/research_package.py --package research/gaussian-prime-corner
```

The verifier authenticates the three pinned notes and encloses the
corner by rational interval arithmetic.

## Open next questions

The note's kernel also carries a shift `s=-beta0/rho`. Nothing here
takes a nonzero `beta0`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note and the
normalized shift in its gauge-free note. The shifted `gamma=1` corner is
the preceding audit. This prime-scale centered corner is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
