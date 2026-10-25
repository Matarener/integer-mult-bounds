# Line ports cap the replica at one unpaid coordinate per family

**Partial. No new exponent.**

The selected replica has 896 live families, from 2 sides, 4 pairs and 112
ports, across nine calls. A paying call clears one label column. An offset
call swaps two rows and swaps them back, so the label rank stays put and the
dirty bit stays in place.

Eight paying calls clear eight label columns. The dirty bit is still 1.
Nine columns with the same eight calls leave rank 1. Across 112 ports, one
offset direction gives the cap

```text
112 * (9 - 1) = 896.
```

That equals the family count, so the replica is already at one unpaid
coordinate per family. Two unpaid coordinates per family would be 1792,
which is past the cap.

## What was executed

The checker row-reduces the label matrices and reads the replica sentence
in the packing-ceiling note. It does not rerun the ceiling search.

## Scope and evidence

Original card: `coverage-law-change`, priority revision 6, refined to this
cap. [TASK.json](TASK.json) records the scope change. [RESULT.json](RESULT.json)
is the executed receipt and is not rewritten. [SOURCES.json](SOURCES.json)
pins the ceiling note. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:44 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3553 note at 2026-10-18
05:36 UTC, was released work. Draw seed `5e38c5ec06ca1eac9824f64ec93e18b9`,
track `recursive-interfaces`, third card `coverage-law-change`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/line-port-unpaid-cap/verify.py
python3.12 -B research/line-port-unpaid-cap/test_verify.py
python3.12 -B scripts/research_package.py --package research/line-port-unpaid-cap
```

The check finishes in under a second.

## Open next questions

The line-port cap on this replica is one unpaid coordinate per family.
A second coordinate exceeds it.

## Credit

The replica count is in Douglas Colkitt's packing-ceiling note, with Claude
(Anthropic). The one-offset rank cap is the line-port obligation checked here.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
