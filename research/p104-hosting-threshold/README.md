# Rank-1 hosting of 1127 meets the selected saving

**Partial. No new exponent.**

The native channel histogram is

```text
1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 8 H7 + 8 H8
```

with rank mass 2,368. The minimizing side correction is 208 unit-step
helpers, nine rank-one steps each, adding 1,872. The local mass is 4,240.
On the template `W=832/9`, centre 56 and total mass 6,712, the idle mass is
2,472, which is `824/17` ideal rank-51 children.

At the selected saving the moment of that bill is `0.9988962438816702`,
below one. The same bill still beats the selected saving after 1,126 extra
rank-1 hosting units. At 1,127 units the moment goes above one. Both counts
fit inside the idle room.

The geometric budget leaves native ADDs, owners, routing, precision and tape
unpriced. This cut is the rank-1 hosting threshold for that omission.

## What was executed

The checker rebuilds the histogram and calls `ceiling.relax` at the selected
saving. It does not rerun the 208-flag matching or the two-type optimizer.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the channel histogram and the
geometric-budget sentences.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
hosting cut. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the two notes, the ceiling function and
the selected record. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 06:15 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3564 note at 2026-10-18
06:15 UTC, was released work. Draw seed
`b35d4e81a6bbaab3024f2cde36708828`, track `complex-mechanisms`, third card
`p104-side-correction`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-hosting-threshold/verify.py
python3.12 -B research/p104-hosting-threshold/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-hosting-threshold
```

The moment checks finish in about a second.

## Open next questions

The 1,126/1,127 rank-1 cut is this template's hosting decision.

## Credit

The channel histogram is Rohan Arun's PR1972, with the native recipes
prepared for Chafik Boukhalfa. The two-history budget and the 208-unit
minimum are Nick Petalas's. The interval engine is Douglas Colkitt's packing
ceiling, with Claude (Anthropic). The selected kappa is the #1094 record.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
