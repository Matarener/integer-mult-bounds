# Six compatible cycles improve the latest T16 packing

Conditional finite-composition **κ = 0.001673626873024029**, an exact gain of
`3143302327/500000000000000000` (about `6.286604654e-9`) over
[PR3354](https://github.com/CrocSwap/integer-mult-bounds/pull/3354).
The complex side still binds. This is a packing improvement, not an optimality
claim or a complete multiplication theorem.

PR3354 appeared during our search and superseded our independently found
three-helper witness. We retain its exact map and combine six other compatible
cycles from that search. Its original cycle is untouched. All six additional
cycles use disjoint occupied bins, so their improvements add without sharing
capacity. Eighteen helpers relocate; forty-four rows change including compacted
offsets. The selected word, helper widths, call order and suppliers stay fixed.

| New cycle (row indices in the complete map) |
| --- |
| 1813 → 2979 → 650 → 1813 |
| 1814 → 2981 → 861 → 1814 |
| 1815 → 2986 → 869 → 1815 |
| 1859 → 2993 → 1009 → 1859 |
| 1861 → 2995 → 231 → 1861 |
| 1862 → 3002 → 260 → 1862 |

Each cycle replaces idle ranks `(2,1,z)` by `(3,0,z)`. The complete paid
profile changes by `-6 H1 -6 H2 +6 H3` relative to PR3354, becoming
`{1:349712,2:60192,3:62326,4:20448,5:11808,7:2,8:1152,16:2,48:4880}`.
Rank mass remains 1,041,408 and deficit 5,120. See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/t16-composed-cycles
python3.12 -Werror -B research/t16-composed-cycles/verify.py --work /absolute/new/output
```

The verifier reconstructs PR3354 from canonical PR2169 data and an authenticated
176-row delta, applies the six explicit cycles, independently audits the full
69,120-role owner map, prices both suppliers and runs unchanged eleven-stage
strict physical admission. It checks the complete typed selected invoice,
including all finite charges, with only the three newly bound source identifiers
allowed to differ. It reconstructs both seven-step bootstraps and all 47 strict
outer inequalities on each tariff path. Private discovery tools are not needed.

The exact predecessor is PR3354 head
`2007d0d1efe82b341e51a32d8b68ebaf8218b394`. Its original construction,
predecessor delta, source export, proof, README and result are preserved under
`predecessor/`. The unchanged admission wrapper is retained as `replay.py`.
All 43 canonical runtime inputs are pinned in `SOURCES.json`; their bytes match
canonical base `6f100d4bb5083f8c35d96fd95a539811c62f245c`.

## Scope and credit

This retains the selected conditional finite-composition scope, including the
all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, exact recovery, analytic and bit H1–H5 premises. Native local
ancestry is source-bound reuse. Full cold native rebuilding, formal-kernel
verification and independent human review are not claimed. The selected
frontier is unchanged.

Credit Nick Petalas for PR3354's three-helper cycle, PR3338's two-role map and
source-closed admission; Gonzalo Mier for PR3308; Philippe Van Velzen for PR2169;
George Lydakis, Rohan Arun and Jeremy Kothe for the vacancy-chain and packing
lineage; Josie Elliston for the independent owner auditor; Hao Yan for the T16
controller; and the retained compiler/native/bit/moment authors. New work by
Pierre (hexapode) with substantial OpenAI Codex assistance from four concurrent
agents. Apache-2.0; predecessor notices are retained.

## Open next questions

Can a neutral rearrangement unlock another legal exchange on this exact map?
Start with one explicit cycle and recompute its complete invoice. The six
composed cycles exhaust neither global packing nor all interacting exchanges.
Preserve and combine candidates when a newer contribution supersedes one.
