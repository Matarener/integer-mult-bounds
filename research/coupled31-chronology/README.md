# Chronology excludes the 31-leaf five-connector target

**No new kappa.** The requested 31-leaf caller with five rank-two connectors
cannot have the full endpoint under the paired-star contract. Its thin rank
must be at least 28, rather than ten. The new proof also excludes the earlier
127-leaf, ten-rank-one target, whose thin rank must be at least 88.
Even arbitrarily fine nonzero stage splits at d=4 need thin rank at least 20.

The main result is a linear information bound for every finite dimension and
every characteristic-two field. If b is the extra row dimension in the thin
connectors, the paired-stage contract requires `g<=3b+2`. The same bound holds
for extra image dimension. A prefix determinant argument forces a dimension
drop after at most three full calls; restriction to untouched leaves repeats
that drop. [PROOF.md](PROOF.md) gives the complete induction and the extension
to arbitrary full-stage splits with a specified minimum query rank.

This goes beyond the static cut in [PR5673](https://github.com/CrocSwap/integer-mult-bounds/pull/5673)
and its sharp witnesses in [PR5681](https://github.com/CrocSwap/integer-mult-bounds/pull/5681).
Those static witnesses remain valid. Chronology prevents their completion.

[COST.md](COST.md) charges the entire pinned P104 recursive profile. An exact
concave tangent proves that every paired-star caller with one or two coupled
ports loses at saving **.00256**, for every integer leaf count g>=3. This is
a uniform ceiling below selected .00310045, not a bounded parameter search.
The g=1 and g=2 profiles already lose every concave moment.
The invoice marks all unconstructed physical obligations as unknown.

A larger coupling is still possible under this test. At 31 leaves, five
rank-q connectors require q>=20. The q=26 profile fits the 104-port population
and has a positive optimistic .0035 price. It has no supplied operator.
[COMMUTING.md](COMMUTING.md) supplies a second restriction: commuting full
projectors require at least `ceil(g/2)` thin maps, regardless of port count
or thin rank. Thus the five-map large-coupling targets need noncommuting full
projectors or another contract.

[WORD31.json](WORD31.json) supplies a complete 31-leaf binary word at that
map-count bound: 62 full calls and 16 thin maps of rank eight on each pair
of ports. Its exact Laurent endpoint passes; its complete recursive bill
loses every concave moment. It is a control, not a native supplier.

## Reproduce

Python 3.12 and the standard library suffice. A cold registered metadata
check also needs the two open provenance commits:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git c10f75f09e41803ae8efe478331a7509b7379b2f
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 67f07448eec5ad8d84bdf96b46981ac0b893592f
python3.12 -B scripts/research_package.py --package research/coupled31-chronology
python3.12 -I -O -B research/coupled31-chronology/verify.py
```

Expected: `PASS_CHRONOLOGICAL_CONNECTOR_RANK_BOUND` and the registered package
pass. The checker imports no solver or discovery script. It checks formal
polynomial determinants, local dimension-drop systems, the static source
fixture, the full long endpoint, a separate F4 interpolation endpoint proof,
and exact integer-power price bounds. Damaged sources, endpoints and receipts
are rejected. [RESULT.json](RESULT.json) records the exact evidence.

Finite checks support the written universal proofs. They are not independent
human or proof-assistant acceptance. The binary word does not supply a native
lift, legal physical reads, restoration, adapters, tapes, compiler or outer
transfer. The selected frontier is unchanged.

## Open next questions

- Audit the restriction and dimension-drop steps in PROOF.md. Check that the
  signature dimension is the column span of matrix differences, and that
  removed stages do not enter the retained mixed blocks.
- Construct a genuinely noncommuting coupled word. The q=26, g=31, five-map
  profile and the q=8, g=13, five-map profile pass the new rank bound and an
  optimistic price. Both remain unconstructed. First test every independent
  stage coefficient, then provide the native lift and complete physical bill.
- Resolve the saved small coupled seed searches. Two fixed static connector
  choices with all call orders free timed out. They remain unknown. Do not
  infer impossibility or a large-word extension from those runs.

Structured questions and the changed card scope are in TASK.json. Discovery
commands and failed or incomplete routes are in DISCOVERY.md. The canonical
investigation is [Discussion5593](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593).
Work starts from canonical main `df0137efd35e11b4445734bf612bdd4c7ebc330c`,
priority seven. Initial remote overlap covered 401 open PRs and 5060 Discussion
records; sparse local coverage was incomplete.

Credit Cinna Davis's controller/simplex work, PR5617/5631/5649/5673/5681,
the separate PR5701 lift qualification, and the complete retained P104/helper/
native/compiler lineage. Ali Romman with substantial OpenAI Codex assistance;
no subagents. Apache-2.0.

The pinned P104 tariff retains Pierre-Loic Doulcet / hexapode, Joel Pulikkan /
GamingPuzzled, DreamingOfClouds, thu-nmrc, Gareth Davidson / bitplane, David
Arias, Jacob Alan Sussman, zxv and Cao Yifan, with the earlier geometry, BIT
and analytic authors in its source notices. Chris R / Clear1nsight supplies
the separate PR5701 characteristic-zero qualification.
