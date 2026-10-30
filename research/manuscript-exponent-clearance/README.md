# The manuscript exponent clears both parking nodes

**Partial. No new exponent.**

The parking identity on an all-width-one node is `Psi(tau) = (1 - eta) m^(1 - tau)`.
With `m = 10^6` and `tau = 1 - 2^{-50}`, an upper bound on `ln m` below 20 and
a rank deficit above `20 * 2^{-50}` put `Psi` strictly below 1.

The bit deficit is `339/22587335000000`. Its integer gap is
`2659138713000000`. The complex deficit is `73/19906842167500`. Its integer
gap is `6871402692000000`. Both gaps make the role count an integer multiple
of the modulus, and both make `Psi` strictly below 1. The complex node has
the smaller threshold margin, above 298 manuscript steps.

## What was executed

The checker reads the three manuscript files and bounds `ln(10^6)` by a
finite atanh series with an explicit tail. It does not retune the parking
schedule.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the exponent comparison in PR
3727, head `73113d754b6abaafafe07b3140a3fb0dddbb756c`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
exponent. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the three
manuscript files. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/manuscript-exponent-clearance/verify.py
python3.12 -B research/manuscript-exponent-clearance/test_verify.py
python3.12 -B scripts/research_package.py --package research/manuscript-exponent-clearance
```

## Open next questions

The exponent clears both nodes. A tighter series would leave that comparison.

## Credit

The displayed deficits are in `upstream/build/sections/03-motifs.tex`. petalas
compared them with `1 - 2^{-50}`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
