# A two-call centre share stays above a tenth after one restoration

**Partial. No new exponent.**

The selected local word pays eight rank-8 children and a centre charge of 64
on every call. The published planning lever shares that path across two calls
by cutting both numbers in half. Its ceiling ratio rounds to 1.90, so the
route is not stopped for a gain under a tenth.

This screen charges the share. Each pair of calls keeps the eight rank-8
copies once and adds one rank-8 restoration, so a call carries 9/2 rank-8
children and centre charge 36. The idle mass stays 1,646. Hosting adds no
child: the bit geometry note says one private centre slot is used at a time,
and the family count stays 896. Precision adds no child: the largest charged
rank stays 8, and the halving guard stays 51. Those two zero charges are
hypotheses taken from those statements. They are not a hosting or precision
proof for the selected complex template.

`ceiling.ceiling` gives these grid ceilings, on the same 10⁻¹² grid as
`levers.py`:

| Profile | Centre | Ceiling |
|---|---:|---|
| Selected word | 64 | 169005411/100000000000 |
| Ideal two-call share | 32 | 1606486447/500000000000 |
| Share plus one restoration per pair | 36 | 1511255751/500000000000 |

The charged ceiling divided by the selected ceiling is still greater than
11/10. This is a relaxation inside the published coverage law. It is not a
shared-path construction and it does not change the selected kappa.

## What was executed

The checker calls `ceiling.ceiling` on the three profiles above. It does not
replay `research/complex-local-word-ceiling/verify.py`, because that replay
reads the frontier certificate. The planning numbers come from `levers.py`.

## Scope and evidence

Original card: `centre-path-sharing`, priority revision 6, refined to this
two-call profile. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the ceiling, the lever table, the bit
geometry note and the selected record. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:26 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3542 note at 2026-10-18
05:14 UTC, was released work. Draw seed `5b21e54f2184a7574e607206a582d4dd`,
track `recursive-interfaces`, first card `centre-path-sharing`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/shared-centre-k2/verify.py
python3.12 -B research/shared-centre-k2/test_verify.py
python3.12 -B scripts/research_package.py --package research/shared-centre-k2
```

The ceiling screen takes a few seconds.

## Open next questions

The two-call relaxation stays above a tenth after the restoration charge.
Building that shared path is a later construction round, and this screen
does not open one.

## Credit

The packing ceiling and the lever table are Douglas Colkitt's, with Claude
(Anthropic). The private-slot sentence is in the split-centres geometry note
for Dylan Crow's PR #370 word. The selected record is the fixture.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
