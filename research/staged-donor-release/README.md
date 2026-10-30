# Delayed staged donor releases

**Complete conditional finite release; LOCAL-ONLY, independent AI review approved.**
Two literal donor releases move to the pivots’ first producer frames. Their
arbitrary-dirty operators are unchanged while each donor pays H3 in place of
H1+H2. The unchanged T360 allocation then supports

`κ = 0.001730418899766071163804 − 10^-46 − 10^-70`.

Final refresh found concurrent [PR3642](https://github.com/CrocSwap/integer-mult-bounds/pull/3642) and [PR3653](https://github.com/CrocSwap/integer-mult-bounds/pull/3653). This package matches PR3653’s reported endpoint with smaller T360 stock; it claims no priority or further frontier increase. See [CONCURRENT-WORK.md](CONCURRENT-WORK.md).

This remains a strict conditional gain over the pinned PR3638/PR3633 predecessor of
`0.000000322536237447629574` on their common release grid. The local profile is
`{1:2437,2:724,3:226,4:102,5:20,8:8}`. Widths, 408 helpers, 91 private buffers,
1,321,920 literal roles and 323,069 physical families stay fixed. The complete
profile is in LEAD1-PRICE.json. [PROOF.md](PROOF.md) gives the exact operator,
invoice, source, scope and obligation ledger. The selected record is unchanged.

## Reproduce

Standard-library bounded replay:

```
python3.12 -B scripts/research_package.py --package research/staged-donor-release
```

This reconstructs the words and exact prices, replays the independent structural
check and actual endpoint mutants, and authenticates both the original and
later default-wrapper execution evidence, including four controls that reject
inconsistent wrapper receipts. It is not a fresh full native/global/outer replay.

The self-contained source archive authenticates 734 files, reconstructs both
source manifests, and includes the actual words, engines, T360 fill/order and
explicit retained parent/native evidence. The complete CLI defaults to fresh
changed-provider native chains followed by the complete original admission:

```
python3.12 -B research/staged-donor-release/full_replay.py --work /tmp/fresh-staged-release
```

Runtime: Python3.12.8, numpy1.26.4, scipy1.15.3, sympy1.14.0, mpmath1.3.0;
assertions enabled and one heavy replay at a time.

The default full CLI has now passed end to end: both fresh changed-provider
native chains and all seven admission stages, with fresh preparation and the
complete original release. See [the full-wrapper receipts](evidence/full-wrapper/README.md).
Unchanged retained native/parent ancestry remains explicitly authenticated reuse;
a no-reuse retained-parent cold run remains unexecuted. The earlier run and its
declared-stage repair/preparation reuse are preserved separately under
`evidence/complete`. No Lean or Docker was run.

## Open next questions

Compensated later releases and changed joint consumers remain outside these
two commuting shifts. A new candidate needs an exact dirty-state identity and
complete invoice before synthesis or allocation. Uniform/all-size compiler,
source/hosting, bootstrap, recursive precision/tape/recovery, analytic and BIT
hypotheses remain inherited. This is not an unconditional multiplication theorem,
formal-kernel proof or universal packing/architecture optimum.

## Credit

Retained source bytes/notices preserve Ross Richardson/PR3605, dcharb78/PR3133,
Marius-Paul Dumitrean/PR2979, Jeremy Kothe, PR3638’s T360 and PR3633’s exact
packing lineage, and the credited native/owner/block-norm/outer authors. New
work has substantial OpenAI Codex assistance, with separate fresh Astra AI
review. No independent human or proof-kernel verification is claimed. Apache-2.0.
