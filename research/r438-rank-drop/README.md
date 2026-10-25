# The R438 profile drops 132 rank units locally

**Partial. No new exponent.**

The published profile is

```text
{1:1298, 2:1342, 3:79, 4:44, 5:93, 6:11, 7:9}
```

It has 2,876 paid children and rank mass 4,989. The exact change from the
pinned word is `-9 e7 -24 e1 -9 e5`, and

```text
9·7 + 24·1 + 9·5 = 132
5121 - 132 = 4989
```

Those 42 deleted children are `2918 - 42 = 2876`. Nine unread helper families
take the dirty-helper count from 438 to 429. Under width-8 accounting the
same nine families return

```text
9 · 8 = 72
```

rank units per local call, and `72 · 9 = 648` across nine calls. That return
cancels the extra 72-unit pruning reduction, so the local drop of 132 is not
a global saving.

The ADD split is `5758 + 5619 + 1499 + 347 = 13223`, down from 24,248 by
11,025.

## What was executed

The checker adds the published counts. It does not regenerate the ordered
word.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the invoice in PR 3645, head
`99b901c9b5ac70cf441b3d7e585cc7b8744b5359`.

## Scope and evidence

Original card: `bit-helper-contract`, priority revision 6, refined to this
profile. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/r438-rank-drop/verify.py
python3.12 -B research/r438-rank-drop/test_verify.py
python3.12 -B scripts/research_package.py --package research/r438-rank-drop
```

## Open next questions

This profile is the local bill. Regenerating the word would leave it.

## Credit

Ross Richardson published the three-snapshot R438 word and this invoice.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
