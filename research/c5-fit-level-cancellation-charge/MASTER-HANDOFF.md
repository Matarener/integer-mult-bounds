# Handoff: named-class C5 cancellation charge beats termwise `180/7`

## Result

Among named term classes `{diagonal, J, off-diagonal, pairwise Gram}`, after
identical-support opposite-sign netting, an explicit charging certificate with
weights summing to `9/4` dominates every 1- and 2-plane support rectangle and
credits each remaining net full-support term by `159/16`. Fit-level floors:

- **45** when `σ_J = 0` (J-free),
- **561/16** when `σ_J = 1`,

both strictly above the classical termwise ceiling `180/7`. Dual scanners agree
on the `2,547,216`-rectangle census. Diagonal tariff 224 and J-extension tariff
16097 meet the respective floors. Selected κ unchanged at
`0.001672660197076918`.

Pinned CrocSwap main tip (branch base): `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Scientific geometry base (SOURCES): `463113d675af7410ac91d53a4fed51ec6494eb9a`.
Branch: `cursor/c5-fit-level-cancellation-charge-ee22`.
Scientific package tip: `5586f4aa59090c96d8752a335e6e88d4f8d829b4` (Wentao-only; no `Co-authored-by: Victor Li`).
Branch tip: this commit on `cursor/c5-fit-level-cancellation-charge-ee22` (`git rev-parse HEAD`).
Package: `research/c5-fit-level-cancellation-charge/`.

## Switch

Took #3639's open cancellation-identity OQ (preferred next48). Did not reprint
residual/local-opt `460 > 224` as a charge, nor the termwise `180/7` bill.
Avoided: P104 side-correction leave-alones; stock-leaf class-only `S_leaf=1`
DEFERs; centre soft-overlap with open `#3120`/`#3548`/`#3147`; thin rescaled
residual corollary `460 <= (115/56)*224`.

## Exact commands (expected PASS)

```sh
python3.12 -I -W error -B research/c5-fit-level-cancellation-charge/verify.py
# PASS_C5_FIT_LEVEL_CANCELLATION_CHARGE cycles=23 weight_sum=9/4 J_free_floor=45 one_J_floor=561/16 termwise_ceiling=180/7 beats=true

python3.12 -I -O -W error -B research/c5-fit-level-cancellation-charge/verify.py
# same marker

python3.12 -I -W error -B research/c5-fit-level-cancellation-charge/independent.py
# PASS_C5_FIT_LEVEL_CANCELLATION_CHARGE_INDEPENDENT cycles=23 weight_sum=9/4 J_free_floor=45 one_J_floor=561/16 termwise_ceiling=180/7 beats=true

python3.12 -I -O -W error -B research/c5-fit-level-cancellation-charge/test_verify.py
# 9 tests OK

python3.12 -W error -B scripts/research_package.py --package research/c5-fit-level-cancellation-charge
# PASS_REGISTERED_RESEARCH_PACKAGE research/c5-fit-level-cancellation-charge outcome=completed
```

## Closest priors

- `research/c5-fit-level-residual-charge` / #3639 — residual/local-opt fails on
  diagonal; leaves this cancellation-identity OQ (leave-alone).
- `research/c5-global-charging-obstruction` / `c5-global-charging-ceiling` —
  termwise ceiling `180/7` (leave-alone; cited, not reprinted).
- `research/c5-four-residual-floors` — granted local floors.

## Soft-overlap risks

- Do not read this as reprinting the termwise `180/7` derivation or the
  residual/local-opt `460 > 224` falsification.
- Floors 45 / `561/16` are proof-method bounds inside named classes with the
  stated cancellation identity; not a new unconditional decoder floor.
- Uncredited termwise on these weights still fails on full support (`ρ > 9`);
  the improvement is the J credit after netting.
- Leave #3639 and C5 termwise priors alone.

## What remains open

Does a cost-preserving reduction eliminate net full-support terms from every
named-class exact fit, so the J-free floor 45 applies universally in this class?

## Credit

Nick Petalas (termwise charging obstruction/ceiling), Krzysztof Wójt
(four-residual floors), #3639 residual/local-opt audit, Tekalign/PR2782,
Cinna Davis/PR1825, Adam Gall/PR1889, thakrarsagar/PR3256, retained matching
lineage.

Prepared by Wentao Li `<wentaol4@illinois.edu>` with substantial AI assistance.
No CrocSwap PR opened (donor instruction).
