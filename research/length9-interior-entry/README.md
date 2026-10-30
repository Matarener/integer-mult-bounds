# No positive entry inside this arc zeros both far directions

On the length-9 width-2 cycle, every positive entry inside the arc `{0,1}`
leaves at least one direction of every far touching pair nonzero. The only
positive value that zeros even one direction is the off-diagonal entry `1`,
and there the row gap is `11/8`, outside the Neumann hypothesis. The
bandwidth stays 4.

No new kappa is claimed. Boundary order is not decided here.

## The arc

The diagonal is 1 and every positive circular distance up to 2 carries
`-1/8`. The survivors that meet `{0,1}` are `2, 3, 7, 8`. Three of those
pairs sit at circular distance 4, with no direct entry: `(2,7)`, `(3,7)`,
and `(3,8)`.

Replace the pivot entry from 0 to 1 by a parameter `x`, and leave the
opposite entry at `-1/8`. The pivot determinant is `1 + x/8`. The adjugate's
first column is `(1, 1/8)`, which does not contain `x`. Each far pair has
one direction whose numerator is therefore constant:

```
(2,7): -9/512
(3,7): -1/512
(3,8): -9/512
```

None of these is zero. The opposite directions are `(x-1)/64`, `x/64`, and
`(x-1)/64`. They vanish at `x=1` or `x=0`, never at the same time as the
constant direction. The opposite pivot entry swaps which direction carries
the factor of `x`.

## The positive root

At `x=1` the determinant is `9/8`. The six far entries are

```
(2,7) = -1/64,   (7,2) = 0,
(3,7) = -1/576,  (7,3) = 1/72,
(3,8) = -1/64,   (8,3) = 0.
```

The bandwidth remains 4. Row 0 now sums to `1 + 3/8 = 11/8` in absolute
value, so `rho < 1` fails. The complement is still the complementary block
of the inverse, and both of its induced norms equal `54382596/28735435`.

Either diagonal parameter leaves both directions of `(2,7)` or of `(3,8)`
at the constant numerator `-9/512` or `-1/512`. The one pair that does
depend on the diagonal vanishes only at `-1/8`. That common root is
negative, and the pivot determinant there is `-9/64`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length9-interior-entry/verify.py
python3 -B scripts/research_package.py --package research/length9-interior-entry
```

The verifier authenticates the pinned note, checks the adjugate numerators,
and checks the host with the positive root.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

A three-vertex pivot can put one entry into both adjugate corners. That is
the remaining place one positive value might zero both far directions.

## Credit

Cinna Davis wrote the narrow Neumann bounds in the PR4100 conditioning
note. The width-2 one-vertex split is the preceding audit. The two-vertex
interior parameter is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
