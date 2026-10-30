# The R480 leaver keeps the selected mass and a lower ceiling

**Partial. No new exponent.**

The gauge44-leaver8 witness pays, per call,

```text
{1:2412, 2:418, 3:418, 4:170, 5:68, 8:8}
```

against the selected word `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`.
The difference is fourteen rank-3 children and fourteen rank-5 children
replaced by twenty-eight rank-4 children. Both sides weigh 112, so the local
mass stays 5,586.

The helper inventory is `{4:56, 5:32, 7:30, 8:122, 9:240}`, summing to 480.
Seventy-two calls of the paid profile plus the idle remainder
`{1:1099, 2:9, 3:179, 7:54, 16:23, 48:2419}` reproduce the global profile.
Its rank mass is 520,704. The live count is `72 * 896 / 9 = 7168`.

The pinned endpoint is `835693632195073/500000000000000000`, below the
selected kappa `836330098538459/500000000000000000`. The packing ceiling of
the paid profile is `1689769943/1000000000000`, below the selected word's
ceiling `169005411/100000000000`. The ratio stays under 5%.

The heterogeneous-owner note records this inventory, with the R489 interface,
as a cost vector outside the pinned catalogue whose reduced cost is negative.
That dual sign and this packing ceiling are separate screens. This profile's
ceiling is the lower one.

## What was executed

The checker reads the leaver spec, rebuilds the global bill, and calls
`ceiling.ceiling` on the paid profile and the selected word. It does not
replay the leaver construction or the catalogue dual.

The ceiling package verifier reads the frontier assembly. This checkout has
no `research/community-frontier1094-audit/ASSEMBLY.json`, so that orientation
command was not run.

## Scope and evidence

Original card: `complex-new-helper-inventory`, priority revision 6, refined
to this inventory. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the spec, the catalogue control, the
ceiling and the selected record. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 06:15 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3564 note at 2026-10-18
06:15 UTC, was released work. Draw seed
`b35d4e81a6bbaab3024f2cde36708828`, track `complex-mechanisms`, second card
`complex-new-helper-inventory`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/r480-leaver-rank-bill/verify.py
python3.12 -B research/r480-leaver-rank-bill/test_verify.py
python3.12 -B scripts/research_package.py --package research/r480-leaver-rank-bill
```

The ceiling screens finish in about a second.

## Open next questions

This inventory's rank bill, endpoint and ceiling screen are the instance.

## Credit

The gauge44-leaver8 witness builds on icekylinx's #645. The heterogeneous
catalogue bound was prepared for Ali Romman. The packing ceiling is Douglas
Colkitt's, with Claude (Anthropic). The selected kappa is the #1094 record.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
