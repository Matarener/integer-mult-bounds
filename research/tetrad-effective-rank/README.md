# The tetrad alphabet's exhibited effective rank is 2

**Partial. No new exponent.**

The one-sided tetrad-local alphabet has 28 four-frames. Each frame demands
four terms that meet it on both sides, so the copied rank is at least 112.
Each paid term has rank at most 4. The note's completed identities are the
copy profile `{2: 56}` and the all-pairs profile `{1: 112}`. Their effective
ranks, copied rank divided by the number of paid terms, are 2 and 1.

A paired-frame design realizes the rank-2 count: 14 pairs, four terms on
each pair, every frame met four times. Four terms on each single frame
realize the rank-1 count. Twenty-seven rank-4 terms supply 108, short of
112. Twenty-eight rank-4 terms meet the count. The note does not exhibit
that rank-4 identity.

The selected local word is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`,
mass 5,586. Its ideal ceiling is `169005411/100000000000`. Delivering that
mass as rank-2 children gives `856878183/500000000000`, a ratio under 5%.
Delivering it as rank-4 children gives `2108498843/1000000000000`, a ratio
above 5%. That second screen is the term-cap relaxation. Rank-16 delivery,
the published 2.31 lever, sits outside the cap of 4.

## What was executed

The checker rebuilds the two frame designs and calls `ceiling.ceiling` on
the selected word, the rank-2 shape and the rank-4 shape. It does not run
the tetrad package verifier and it does not search for a rank-4 identity.

The ceiling package verifier reads the frontier assembly. This checkout has
no `research/community-frontier1094-audit/ASSEMBLY.json`, so that orientation
command was not run. The screen uses the published ceiling function on the
three profiles above.

## Scope and evidence

Original card: `complex-rank-shape-decoder`, priority revision 6, refined to
this alphabet. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the tetrad note, the ceiling function and
the ceiling note. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 06:15 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3564 note at 2026-10-18
06:15 UTC, was released work. Draw seed `62d1bb03bd616a4181145882d30534b2`
landed on the closed helper-star and three-register cards. The next seed is
`b35d4e81a6bbaab3024f2cde36708828`, track `complex-mechanisms`, first card
`complex-rank-shape-decoder`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/tetrad-effective-rank/verify.py
python3.12 -B research/tetrad-effective-rank/test_verify.py
python3.12 -B scripts/research_package.py --package research/tetrad-effective-rank
```

The ceiling screens finish in about a second.

## Open next questions

The copy floor, the rank cap and the two ideal screens are this alphabet.

## Credit

The tetrad-local note was prepared for Adam Gall, with DreamingOfClouds /
PR717, Aaron Wang / Navinor / PR1226, and PR1012 named in that note. The
packing ceiling and its levers are Douglas Colkitt's, with Claude
(Anthropic). The selected word is the #1094 local profile.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
