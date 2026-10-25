# The R437 histogram has rank mass 1,808,352

**Partial. No new exponent.**

The published profile is

```text
{1:380160, 2:400864, 3:22176, 4:26592, 5:29376, 6:17376, 7:26496, 34:64, 42:352}
```

It has 903,456 children and rank mass 1,808,352. Across 32 replicas the
schedule hosts `32 · 3933 = 125856` helper occurrences, with width
`32 · 888 = 28416` and physical width `28416 + 9 = 28425`. Window 6 uses
209 five-slot families, 2 single-slot families and 11 empty families, so it
has `209 + 2 + 11 = 222` families and `209 · 5 + 2 = 1047` occupied slots.

The BIT coefficient is

```text
868314126713557740143/500000000000000000000000
= 0.001736628253427115480286
```

That value is greater than the selected kappa
`836330098538459/500000000000000000`.

## What was executed

The checker adds the published counts and compares the two rationals. It does
not replay the word.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the profile in PR 3647, head
`36ff441479ff9c7e70d83f0becccd44da50effb8`.

## Scope and evidence

Original card: `bit-helper-contract`, priority revision 6, refined to this
histogram. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/r437-histogram-mass/verify.py
python3.12 -B research/r437-histogram-mass/test_verify.py
python3.12 -B scripts/research_package.py --package research/r437-histogram-mass
```

## Open next questions

This histogram is the invoice. Replaying the word would leave it.

## Credit

ai-nanachi published the R437 composition. Ali Romman published the helper470
deletion it uses.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
