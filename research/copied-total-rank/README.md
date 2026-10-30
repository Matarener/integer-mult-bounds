# Eight height-8 copies cost 64

**Partial. No new exponent.**

The bit geometry states that when `U` is contained in `V`,

```text
D_V D_U = D_(V intersect U-perp), with rank dim(V)-dim(U).
```

The same note says this rank is unchanged for copied totals, and it retains
nine copied totals at height 8. The selected complex lever counts eight
rank-8 copies. On coordinate masks, a full 8-dimensional copy has rank 8,
and a copy with dimensions 6 and 3 has rank 3. A mask that leaves `V` does
not match that formula.

Eight such totals therefore cost `8 * 8 = 64` per call. The published
two-call lever sets the centre charge to 32. That charge is below 64.

## What was executed

The checker multiplies the doubled coordinate matrices for those masks and
reads the lever text. It does not rerun the packing ceiling.

## Scope and evidence

Original card: `centre-path-sharing`, priority revision 6, refined to this
rank bound. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the bit geometry note and the lever
script. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:41 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3553 note at 2026-10-18
05:36 UTC, was released work. Draw seed `5e38c5ec06ca1eac9824f64ec93e18b9`,
track `recursive-interfaces`, second card `centre-path-sharing`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/copied-total-rank/verify.py
python3.12 -B research/copied-total-rank/test_verify.py
python3.12 -B scripts/research_package.py --package research/copied-total-rank
```

The check finishes in under a second.

## Open next questions

Eight height-8 totals cost 64. A decoder that emits fewer totals would be
another contract, and this bound does not build one.

## Credit

The rank formula and the copied-total sentence are in the split-centres
geometry note for Dylan Crow's PR #370 word. The two-call lever is Douglas
Colkitt's, with Claude (Anthropic).

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
