# A revisit-1 length-22 word cannot carry both return lengths 4 and 6

**Partial. No new exponent and no `f(7)` claim.**

Open PR #3730 shows that every even length from 4 through 18 occurs as a
prefix return for every positive length-22 split, using separate restored
words. It does not say those lengths can share a word. At split `(11,10)`
they cannot, for the pair 4 and 6.

A restored length-22 word has 23 prefix positions and returns to the origin
at the end. Its revisit count in the length-22 witness notes is
`22 - |distinct prefixes|`. Split `(11,10)` has 21 distinct prefixes, so the
revisit count is 1 and the 23 positions contain exactly two extra visits.

Those two extras, with the ends identified, fall into one of two patterns:

- the origin also occurs at one intermediate step `k`, and every other prefix
  is unique, so the return lengths are `{k, 22-k, 22}`;
- the origin occurs only at the two ends, and exactly one other prefix repeats
  once, so the return lengths are `{d, 22}` for the distance `d` between that
  pair.

There are 231 such position patterns. None of them contains both distances
4 and 6.
Whenever a pattern meets the range 4 through 18 in two distances, those
distances add to 22. A one-bit step flips Hamming-weight parity, so an actual
hypercube return is even; that does not create a pattern containing both 4
and 6.

The two shapes are attained. One restored `(11,10)` word has return lengths
exactly `{2, 20, 22}`. Another has exactly `{4, 18, 22}`.

## Scope

Original card: `census-pruning-audit`, priority revision 6, refined to this
one-word gap after the existence cover. [TASK.json](TASK.json) records the
scope change. [RESULT.json](RESULT.json) is the executed receipt.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

This is not a universal-word census and it does not decide `f(7)`. The
existence cover of the eight even lengths remains the open length note; this
package does not redo it.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/revisit-one-return-gap/verify.py
python3.12 -B scripts/research_package.py --package research/revisit-one-return-gap
```

Expected marker:

```text
PASS_REVISIT_ONE_RETURN_GAP split=11,10 incompatible=4+6 patterns=231 no_new_kappa
```

The replay finishes in well under a second and uses the standard library only.

## Open next questions

Which pairs of even distances in 4 through 18 can share a restored word at
revisit 2? Split `(11,9)` has 20 distinct prefixes, so the same counting
allows one more repeated visit, and the revisit-1 obstruction does not apply.
The first step is to enumerate the three-extra-visit patterns and test the
pair 4 and 6. Nothing structural blocks that enumeration; this package stops
at revisit 1.

## Credit

The positive length-22 splits and the revisit count are the length-22
split-domain note. The length-2 witness with distances 2, 20 and 22, and the
question of lengths 4 through 18, are the later witness notes; the existence
cover is the open even-length note. The one-bit parity fact is the preceding
return note. The prefix-walk model is Ross Richardson's. The corrected parity
census that frames `f(7)` is Nicholas Stone's.

Prepared by unpaidmoon with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
