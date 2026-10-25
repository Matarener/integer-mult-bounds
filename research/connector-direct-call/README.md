# One charged direct call meets the one-by-one connector

**Partial. No new exponent.**

The published alphabet allows only `B: z += B x` and `A: y += A z`. It
excludes a direct `A B` call. On one source, one output and one dirty
connector, with both maps equal to the identity, the word

```text
B A B A
```

sends every initial state `(x, y, z)` to `(x, y XOR x, z)`. No word of `A`
and `B` with length at most three does that.

The extra operation `D: y += x` leaves `z` untouched. It meets the same eight
states. Its price is one complete call. The old schedule costs four. The
premise that changes is the ban on a direct product call. The new call is
charged, so it is not a free copy.

## What was executed

The checker evaluates both words on all eight states and enumerates the
fourteen shorter alphabet words. It does not rerun the 945-pairing census.

The card's orientation command is
`research/universal-connector-boundary/verify.py`. This package reads the
alphabet sentence in that note and does not repeat the census.

## Scope and evidence

Original card: `connector-alphabet-change`, priority revision 6, refined to
this one call. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the connector note. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/connector-direct-call/verify.py
python3.12 -B research/connector-direct-call/test_verify.py
python3.12 -B scripts/research_package.py --package research/connector-direct-call
```

## Open next questions

This one-by-one direct call is the extra operation. The five-source census
would leave this instance.

## Credit

The universal connector note states the alphabet and the paired-readout
schedule. This package adds one charged call on the one-by-one instance.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
