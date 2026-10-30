# Validation, coverage and limits

## What was run

`verify.py` performs, on every invocation:

1. The exact admissible region of `90` endpoint shapes with `t <= 12`: for
   each shape the region is recomputed with and without the block rank floor
   `n_g >= t_g`, the region minimum is compared with the published
   parity-rounded `11t/5` value, and the floor is required never to weaken
   the region and never to beat that value.
2. The floor's effect at the ten-call boundary of every open `t = 4` shape,
   with the removed splits enumerated: `(0,10)` and `(2,8)` for `(4,0)`,
   `(1,9)` for `(3,1)`, and none for `(2,2)`.
3. A finite lattice check of the boundary equality statement. In each
   equality case the admissible rank data `a, b >= r` is enumerated
   completely and equality `a + b = n_g + t_g` must occur only at
   `a = b = r`, with `r` inside the allowed rank range.
4. An explicit `F2` rank fixture for the `(2,8)` ten-call balanced profile,
   recomputed with a pivot-based rank routine: `rank X_i = rank Y_i =
   rank X_i Y_i = 2` and the same for the `j` block.

`test_package.py` adds behavioural controls: a region without the rank floor,
a region without the parity classes, a constant-zero rank routine, a fixture
with a dropped minority column, an out-of-range F2 row, an invalid endpoint
shape and an empty shape are all rejected; the unmodified receipt is accepted
and survives a JSON round trip, and the pinned counts (`90` shapes, `10`
strict shapes, `8` boundary cases) are asserted.

Typical wall time is about `0.1 s` single-threaded on CPython 3.12,
macOS/arm64.

## What this does and does not cover

Covered exactly:

- The admissible label splits of the inherited necessary conditions plus the
  block rank floor, for every shape with `t <= 12`, through the region cap
  `n <= 64`.
- The ten-call split lists of the open `t = 4` shapes `(2,2)`, `(3,1)` and
  `(4,0)`, with the splits the floor removes.
- The boundary equality rank statement, checked completely over the
  admissible rank lattice of every equality case in this package's range.
- A rank-level realization of the `(2,8)` profile.

**Not** covered, and not claimed:

- No word is constructed and no word length is excluded at any role count.
  The `{10,12}` minima of PR3570, PR3578 and PR3589 stay open.
- The fixture is rank data, not an executable word: it satisfies the block
  rank identities `rank(X_g Y_g) = t_g` and no endpoint equation.
- The three-target value nine is quoted from PR3536 and its retained PR3471
  exclusion. It is not re-derived, and no new census was run here.
- Shapes with `t > 12` and sizes above the cap are outside the computed
  region.
- No physical cost is computed. No scalar, routing, restoration, hosting,
  precision, recursive or supplier-admission cost appears, no kappa is
  improved and the selected frontier is unchanged.

## Provenance of the inherited conditions

The two count inequalities and the trace parities are PR3589's; the four
boundary ranks and the rank-nullity step are from the same package's
proof; the cubic machinery behind them is PR3570/PR3578; the three-target
minimum quoted in the README and in `RESULT.json` is PR3536's corollary on
the retained PR3471 exclusion. The status correction for
`research/q8-min-length-census` refers to that quoted value. No predecessor
file is used as a hidden premise: every step used here is restated in
[PROOF.md](PROOF.md).
