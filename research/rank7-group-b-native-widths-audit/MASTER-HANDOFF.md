# Master handoff: rank7-group-b-native-widths-audit

## Result

Group B of #2979: both providers and both orientations emit residual pairs
`0:260` (helper 299, cold, width **7**) and `114:260` (helpers 448/449/484/485,
entrance `[51]`, width **6**) under shared
`W = ⟨256,128,64,34,17,11,4⟩`. Adapter and `LOCAL-CHECKS` hashes match the
retained `FULL-NATIVE-RECEIPT.json`. These widths join all **3330** T74 fill
placements. No new kappa.

**Not headlined (soft-overlap trap):** guide margins `+42541` / single-299
`-58943` — already on deferred tip `f795116d` and in `#2979` `STAGE-PRICES.json`
/ group-A registered margins. Do not open a CrocSwap PR that reprints them.

## Pins

- Base / selected main: `6f100d4bb5083f8c35d96fd95a539811c62f245c`
- Selected κ: `0.001672660197076918`
- Task card: `independent-moment` (priority revision 6)
- Predecessor head #2979: `be191346391661f4d35fc0d1508d0a6029572576`
- Branch: `cursor/group-b-native-widths-60b9`
- Content tip SHA: `5241640244d2521818a6fe3b1f6c34e99d67a4e3`
- Publish tip (package+handoff): branch HEAD of `cursor/group-b-native-widths-60b9` (content package commit `5241640244d2521818a6fe3b1f6c34e99d67a4e3`; docs-only handoff commits may follow)
- Package: `research/rank7-group-b-native-widths-audit/`

## Exact commands

```sh
python3 -I -B research/rank7-group-b-native-widths-audit/verify.py
python3 -I -O -B research/rank7-group-b-native-widths-audit/verify.py
python3 -I -B research/rank7-group-b-native-widths-audit/test_verify.py -v
python3 -I -B scripts/research_package.py --package research/rank7-group-b-native-widths-audit --check-only
python3 -I -B scripts/research_package.py --package research/rank7-group-b-native-widths-audit
```

## Expected PASS lines

```text
PASS_GROUP_B_NATIVE_WIDTHS providers=2 helpers=5 residual_widths=7,6,6,6,6 pairs=299:0:260,448:114:260,449:114:260,484:114:260,485:114:260 placements=3330 adapter_pinned both_orientations no_new_kappa
PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)
PASS_REGISTERED_RESEARCH_PACKAGE research/rank7-group-b-native-widths-audit outcome=partial
```

(`-O` verify must print the same `PASS_GROUP_B_NATIVE_WIDTHS` line; `need`/`require`
admission stays enforced.)

## Closest priors

| Prior | Relation |
|---|---|
| `research/rank7-group-a-entrance-audit/` | Methodology predecessor (native section); different helpers/W |
| `research/rank7-joint-endframes/` (#2979 @ `be191346…`) | Source WORD / FULL-NATIVE / adapters |
| `research/rank7-group-b-single-control-audit/` (`f795116d`) | Deferred soft-overlap margins; this package answers its native OQ |
| #2993 `rank7-joint-frame-audit` | Frame invoices; not imported |

## What is new vs soft-overlap traps

- **New:** phase-exact residual classes `0:260` / `114:260`, entrance `[51]` vs
  cold `[]`, climb/wrapper/scalar clocks in both orientations, adapter pin
  match, native-width → T74 join for helpers `{299,448,449,484,485}`.
- **Do not claim as new:** joint/single guide margins, width inventory
  `7/6/6/6/6` alone without native residual binding, or 3330 placements alone
  (those were the deferred single-control headline).

## Open next questions

1. Complete peer-native / private-cleanup dependency closure for group B.
2. Physical movement, precision/tape, supplier caps and outer release for the
   unchanged #2979 source.

## Leave-alone

Open CrocSwap #3392, #3386, #3374, #3349; deferred V45 `1910fd12`; deferred
group-B single-control `f795116d`; blocked W=532 unpaid F17 terms; merged
tariff series through #2883; do not reprint #3259 / `p104-pooled-cut-independent`.

## Attribution

Wentao Li `<wentaol4@illinois.edu>`. Prepared by Wentao Li with substantial AI
assistance. No `Co-authored-by: Victor Li`. Do **not** open a CrocSwap PR from
this worker (master publishes).
