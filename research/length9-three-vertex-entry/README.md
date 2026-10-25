# The entry 17/8 zeros both directions of one far pair

On the length-9 width-2 arc `{0,1,2}`, the pivot entry from 0 to 1 has one
positive value that zeros both Schur directions of the far pair `(4,8)`.
That value is `17/8`. The other far pairs stay nonzero, so the bandwidth
remains 4. The row gap rises to `5/2`, outside the Neumann hypothesis.

No new kappa is claimed. Boundary order is not decided here.

## The cofactors

The diagonal is 1 and every positive circular distance up to 2 carries
`-1/8`. Vertices 4 and 8 meet opposite ends of the arc and have no direct
entry. With the pivot entry from 0 to 1 equal to `x`, the two relevant
cofactor sums are equal:

```
a(2 + a - x),    a = 1/8.
```

Both far numerators are therefore

```
(x - 17/8) / 512.
```

The determinant is `(495 + 72x) / 512`. At `x = 17/8` it equals `81/64`,
so both Schur entries are genuinely zero rather than a singular pivot.

## The other far pairs

At that same value the six far entries are

```
(4,8) = 0,       (8,4) = 0,
(3,7) = -1/288,  (7,3) = 1/36,
(3,8) = -1/72,   (8,3) = 1/72.
```

Pairs `(3,7)` and `(3,8)` are still at distance 4, so the bandwidth stays
4. Row 0 sums to `17/8 + 3/8 = 5/2` in absolute value. The complement
remains the complementary block of the inverse. Its 1-norm is `12680/6931`
and its infinity norm is `6178688/3375397`.

The other three directed path edges, each set to `17/8`, likewise zero both
directions of one far pair and leave the bandwidth at 4. Neither corner
entry has a positive common root, and neither does any diagonal.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length9-three-vertex-entry/verify.py
python3 -B scripts/research_package.py --package research/length9-three-vertex-entry
```

The verifier authenticates the pinned note, checks the cofactor identity,
and checks every entry of the pivot.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

The common root `17/8` lies outside `rho < 1`. A longer arc is the
remaining place a positive common root might keep the row gap below 1.

## Credit

Cinna Davis wrote the narrow Neumann bounds in the PR4100 conditioning
note. The two-vertex interior parameter is the preceding audit. The
three-vertex root is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
