# One stored L359 magnitude meets the F0 tolerance

**Partial. No new exponent.**

The F0 fault checker keeps a state of 712 rationals. It sets register 359
to `2^e` for `e` in `{0, 8, 64, 256}` and records the completed data defect
`4 u 2^e`, with `u = 2^-80`. The final response entries are pairs of a
register index and one rational.

The #2965 transfer states a sufficient F0 tolerance `epsF <= H 2^(-beta-8)`.
At `H = 1` and `beta = 64` that tolerance is `2^-72`. The stored defect
meets it at `e = 0` and misses it at `e = 8`, `e = 64` and `e = 256`.
The transfer also states that its forward bounds are endpoint bounds. This
comparison uses the stored completed defects.

## What was executed

The checker reads the fault source, its receipt and the transfer note. It
recomputes `4 u 2^e` and compares each stored defect with `2^-72`. It does
not replay the 26,099-event word.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to
these four scalars. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the fault checker, its receipt and the
transfer note. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:32 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3547 note at 2026-10-18
05:31 UTC, was released work. Draw seed `5b21e54f2184a7574e607206a582d4dd`,
track `recursive-interfaces`, second card `joint-query-controller`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-l359-scalar/verify.py
python3.12 -B research/qq16-l359-scalar/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-l359-scalar
```

The comparison finishes in under a second.

## Open next questions

The four stored magnitudes are scalars in register 359. One meets the
published F0 tolerance and three miss it. Replaying the word would leave
this comparison.

## Credit

Arham Tahir supplied the F0 scalar fault witness. Nick Petalas supplied the
#2965 completed-output tolerance. The selected record is unchanged.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
