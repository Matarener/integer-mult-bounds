# The relay coefficient is the Gram boundary term

**Partial. No new exponent.**

For every one of the 208 published flags, the channel addition replay ends with
the Gram term `Q(inner(target root, source root), 2)`. Flag 0, source 0 and
target 34, has inner product 1 and coefficient `1/2`.

## What was executed

The pinned checker defines the inner product as the integer dot product divided
by 4, drops the fixture rows `F0` and `C` from the sorted 120 roots, and stores
`Q(inner(ports[target], ports[source]), 2)` in the target. This check rebuilds
that list and the addition replay, then compares them flag by flag. All 208
agree. The coefficients are `1/2` for 153 flags and `-1/2` for 55.

Flag 0 uses the roots `[0, 0, 0, 0, 0, 2, 0, -2]` and
`[1, -1, -1, -1, -1, 1, -1, -1]`. Their dot product is 4, so the normalized
inner product is 1 and the boundary coefficient is `1/2`.

The same checker says the side correction lies outside this replay. This
comparison does not supply that correction.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
Gram comparison. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the flag certificate, the channel witness,
the fixture, the checker and the task catalogue. No selected frontier file
changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-flag-gram-boundary/verify.py
python3.12 -B research/p104-flag-gram-boundary/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-flag-gram-boundary
```

The comparison finishes in under a second.

## Open next questions

The Gram term is the channel boundary. The side correction remains the program
the checker places outside this replay. Naming one of its events is the next
reading.

## Credit

Nick Petalas supplied the 208-flag certificate. The Gram formula and the
channel witness belong to the native-channel checker. Chafik Boukhalfa supplied
that channel through PR 1991, as credited there.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
