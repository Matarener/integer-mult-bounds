# Fit-level residual C5 charging fails on the diagonal identity

The natural coefficient-sensitive completed-fit inequality

```
sum_C Cost_opt(K|_C) <= Cost_opt(K)
```

does **not** hold for `K = I_112`. Granting every physical C5 local floor 20
gives left-hand side at least 460, while the explicit diagonal decomposition
`I = sum_i e_i e_i^T` has complete-plane tariff exactly 224. Dual scanners
agree. This answers the residual/local-opt reading of the global-charging
handoff after the termwise ceiling `180/7`.

No new decoder floor, caller exclusion, supplier or kappa is claimed.

[PROOF.md](PROOF.md) states the candidate, the diagonal counterexample, and
why the expensive J-bearing identity extensions do not discriminate.
[RESULT.json](RESULT.json) records the twenty-three cycles, the diagonal
tariff and the exact obstruction arithmetic.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/c5-fit-level-residual-charge
```

Direct Git-free commands:

```sh
python3 -I -W error -B research/c5-fit-level-residual-charge/verify.py
python3 -I -W error -B research/c5-fit-level-residual-charge/independent.py
python3 -I -O -W error -B research/c5-fit-level-residual-charge/test_verify.py
```

Expected primary line:

```text
PASS_C5_FIT_LEVEL_RESIDUAL_CHARGE cycles=23 local_floor_sum=460 diagonal_cost=224 inequality_holds=false
```

Default replay is read-only. Set `TMPDIR` to a private writable directory for
the corruption controls on a read-only export. Optional
`verify.py --emit --output PATH` writes a receipt only outside the package.

## Sources and limits

Scientific geometry pins match the C5 charging lineage at base
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6. Selected
kappa `0.001672660197076918` is unchanged. Live inputs are the authenticated
PR2782/PR1825 matching and label tables under
`research/c5-dyadic-decoder-gate/inputs/`.

Predecessor leave-alones cited, not reprinted as bills:
`research/c5-four-residual-floors` (local floors and the global-charging OQ),
`research/c5-global-charging-obstruction` and
`research/c5-global-charging-ceiling` (termwise `180/7` ceiling). Soft-overlap
with open centre-path PRs `#3120`/`#3548`/`#3147`, mixed566 cut packages, and
P104 side-correction leave-alones is not claimed; this package does not touch
those surfaces.

## Open next questions

Does an explicit cancellation identity, beyond residual local-opt costs, give
a valid fit-level charge that beats the termwise `180/7` ceiling? Start by
writing one inequality that uses coefficient cancellation among named term
classes and test it on the diagonal fit and both J-bearing extensions. No
further construction round is reserved here.

## Credit

Prepared by **Wentao Li** `<wentaol4@illinois.edu>`
([VictorLiwentao](https://github.com/VictorLiwentao),
[Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
No independent human or proof-kernel review is claimed. New work is Apache-2.0.

Credit **Nick Petalas** / `c5-global-charging-obstruction` and
`c5-global-charging-ceiling` for the termwise ceiling and J-extension tests;
**Krzysztof Wójt** / `c5-four-residual-floors` for the residual handoff OQ;
**Tekalign** / PR2782, **Cinna Davis** / PR1825, **Adam Gall** / PR1889,
**thakrarsagar** / PR3256, **Nick Petalas** / PR3279, and the retained
E8/P112 matching lineage. No predecessor artifact is modified.
