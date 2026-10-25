# A centered truncated Gaussian keeps a positive separator corner

On one centered truncated Gaussian path of bandwidth 2, deleting the
interior `{3,4,5,6}` and keeping the survivors in increasing index leaves
a positive Schur entry between the outermost separators. That entry lies
strictly between `1/51000` and `1/50000`, and the half-bandwidth is 3.

No new kappa is claimed. The scale here is `gamma=1`, not the eventual
large prime scale.

## The truncated row

`GAUSSIAN.md` writes the narrow kernel
`k(h)=exp(-a rho h^2-2a beta0 h)`. `vendor/GAUGEFREE-INTERIORS.md`
normalizes the centered shift by `G'_s(0)=1` and
`exp(-gamma u^2 + 2 gamma s u)`. This section takes `s=0` and `gamma=1`,
so the kernel is `exp(-h^2)`, and keeps distances 1 and 2 only.

The path has length 10 and diagonal 1. Distance 1 carries `exp(-1)` and
distance 2 carries `exp(-4)`. Twelve terms of the alternating series
enclose `exp(-1)` in

```
[1468457/3991680, 16019531/43545600],
```

a gap of `1/12!`. The squared enclosure supplies `exp(-4)`. Twice the
upper values is still less than 1, so every row gap is positive.

`vendor/FINE-PRIME.md` says an eliminated interior joins only its two
neighboring separators. The survivors are kept in increasing index:
`0,1,2,7,8,9`.

## The corner

The entry between 1 and 8 is the only survivor pair at distance 3. Its
rational enclosure lies strictly between `1/51000` and `1/50000`. The
opposite direction has the same lower bound. The row of vertex 0 equals
its original row, so it has no entry at 7, 8, or 9. The half-bandwidth
is 3. The original-index span of the corner is 7.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-separator-corner/verify.py
python3 -B scripts/research_package.py --package research/gaussian-separator-corner
```

The verifier authenticates the three pinned notes and encloses the corner
by rational interval arithmetic.

## Open next questions

The same interior with shift `s=1/4` is not measured. The note allows a
nonzero `beta0`, and the kernel then differs in the two directions.

The eventual caller uses `gamma=a rho` with `a=pi alpha^2`, which grows.
Nothing here takes that scale.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note and the
normalized shift in its gauge-free note. The width-3 constant-band
measurement is the preceding audit. This centered corner is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
