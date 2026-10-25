# One positive entry cancels only one width-2 far direction

On the length-9 width-2 cycle, deleting one vertex leaves a far touching
pair at distance 4. One positive body entry, set equal to the update,
zeros that Schur direction and leaves the other. The bandwidth stays 4.
Both directions have to be set before the bandwidth falls to 3.

No new kappa is claimed. Boundary order is not decided here.

## The one-vertex fill

The diagonal is 1. Every positive circular distance up to 2 carries
`-1/8`, so each off-diagonal row sums to `1/2`. Deleting vertex 0, the
survivors that meet it are `1, 2, 7, 8`. Vertices 2 and 7 are at circular
distance 4, and neither direct entry exists. Each spoke is `-1/8`, so both
Schur directions are

```
-(-1/8)(-1/8) = -1/64.
```

Pairs at distance 3 have the same fill. Pairs already inside the width have
direct entry `-1/8`, so their Schur entries are `-9/64`. The bandwidth is
4, the touching diameter. The complement inverse has both induced norms
`4772/2435`, inside the width-2 bounds `2` and `10`.

## One entry, one direction

The pivot is the single diagonal entry, so a body entry appears in only
one of the two products. Replacing the entry from 2 to 7 by `+1/64` makes
that Schur entry

```
1/64 - 1/64 = 0.
```

The opposite entry is still absent, so its Schur entry stays `-1/64`. The
bandwidth remains 4. Every other ordered pair among the four touching
survivors behaves the same way: `+1/64` zeros the direction it is written
in and leaves the reverse entry at `-1/64` or `-9/64`.

This one-sided host has row gap `33/64` and circular bandwidth 4. The
complement inverse has both norms `371769784/189854515`, inside the bounds
`64/31` and `18880/961`.

## Both directions

Writing `+1/64` from 7 to 2 as well zeros both directions of the distance-4
pair. The distance-3 entries stay `-1/64`, so the bandwidth is 3, below
the touching diameter 4. The complement inverse has both norms `461/236`,
inside the same widened bounds.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length9-width2-entry/verify.py
python3 -B scripts/research_package.py --package research/length9-width2-entry
```

The verifier authenticates the pinned note, checks every one-vertex
touching direction, and checks the two far-pair hosts.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

An entry inside a longer pivot changes both inverse corners at once. That
is the remaining place one positive value might zero both far directions.

## Credit

Cinna Davis wrote the narrow Neumann bounds in the PR4100 conditioning
note. The width-1 one-entry split is the preceding audit. The width-2 far
pair is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
