# The chirp residue step preserves the quadratic state

**Partial. No new exponent.**

The residue producer stores, for each axis,

```text
c = -s (r / t) mod 2r,
v = c j^2 mod 2r,
Delta = c (2j + 1) mod 2r.
```

The ordinary step adds `Delta` to the running total and to `v`, adds `2c` to
`Delta`, and increments `j`. The two integer identities

```text
(j + 1)^2 - j^2 = 2j + 1,
2(j + 1) + 1 = (2j + 1) + 2
```

show that the updated state is the same formula at `j + 1`. On a wrap the
producer subtracts `v` from the total and restores `j = 0`, `v = 0`,
`Delta = c`. A full pass therefore returns the total to 0.

Every odd slope on both flag lengths `r/2` and `r` was rolled out for every
`ell` from 2 through 12: 6,141 rollouts and 13,981,010 steps. Every pair of
odd slopes on a two-axis cube was checked for `ell` from 2 through 4: 21,840
states. Each state matched the closed form, and every rollover returned to 0.

The same producer visits `sum_i T / product(t_j : j > i)` axis records. When
every axis length is at least 2, each tail product is at least the
corresponding power of 2, so the visit count is strictly less than `2T`.
All 3,905 tuples with one to five axes and lengths in `{2, 4, 8, 16, 32}`
satisfy that bound. The selected kappa is unchanged.

## What was executed

The checker proves the square identities, runs the published transitions, and
compares every visited state with the closed form. It does not run the
middle-map consumer.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the residue section of PR 3763,
head `6bb7dfdae182a69f7c8836a9ec1be0b2b747e124`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
residue step. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/chirp-residue-step/verify.py
python3.12 -B research/chirp-residue-step/test_verify.py
python3.12 -B scripts/research_package.py --package research/chirp-residue-step
```

## Open next questions

The ordinary step and the wrap are integer identities, and every admitted
one-axis rollout through ell 12 returns to zero. A middle-map replay would
leave this package.

## Credit

Jose Manuel (jmbarrancoml) stated this residue producer in PR 3763. The
residue schedule is Chafik Boukhalfa's, and the square-step checks follow
Ross Richardson's symbolic checks of that schedule.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
