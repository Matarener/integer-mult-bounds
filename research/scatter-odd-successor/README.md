# An odd-multiplicity successor cancels the even duplicate

**Partial. No new exponent.**

The published scatter replay XORs a retained total once per occurrence. The
frozen exporter emits one ADD when the index is present. On the selected tuned
word those actions agree. Appending `[0, 0]` to the first row makes the replay
coefficient `0` and the frozen export coefficient `1`.

The successor exporter emits one ADD when the occurrence count is odd. On that
even duplicate its coefficient is `0`, matching the replay. Appending
`[0, 0, 0]` leaves both coefficients at `1`. On the selected word the successor
matches both the replay and the frozen export, because every selected row is
unique. The frozen exporter is unchanged, and the repair is not adopted
upstream.

## What was executed

The pinned membership loop and the pinned per-occurrence replay are run on the
selected word, the even duplicate, and the odd triple. The successor record
loop is separate: one phase-3 ADD for each odd count. No frozen source is
edited.

## Scope and evidence

Original card: `supplier-boundary-audit`, priority revision 6, refined to this
odd-multiplicity successor. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the exporter, the symbolic checker, the tuned
word, and the earlier duplicate receipt. No selected frontier file changes.

Upstream checkpoint: `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6, checked 2026-10-18 04:29 UTC. Canonical main and the fork main
were at that commit. The task draw was `supplier-boundary-audit`, seed
`1cd876d46fd0914d48e990ae5ea76c29`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/scatter-odd-successor/verify.py
python3.12 -B research/scatter-odd-successor/test_verify.py
python3.12 -B scripts/research_package.py --package research/scatter-odd-successor
```

The replay finishes in about a second.

## Open next questions

The odd-multiplicity successor matches the per-occurrence replay on the
selected word, the even duplicate, and the odd triple. Putting that rule into
the frozen exporter is a separate adoption.

## Credit

eumemic supplied the per-occurrence replay. Dylan Crow supplied the membership
exporter. Nick Petalas's #2977 named the duplicate and left the guard opt-in.
The earlier duplicate receipt records the selected word and the two appendages.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
