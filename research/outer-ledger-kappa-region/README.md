# Exact κ region of the selected outer ledger

**Scoped written proof with exact finite corroboration; no new κ.**

The selected #5599 result passes its supplier savings through one outer
ledger: zxv's PR4359 parameter ledger, recomputed by
`research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py` and
called by `research/p104-helper-subspace-splits/pricing.py`. It has 54 strict
checks and 4 functional checks over the free parameters
b, a, q, ε, β, r0, stop and layout.

**Theorem.** For complex uniform saving U and admitted BIT saving B, the
58 checks are jointly satisfiable at κ exactly when

    OLD_BASELINE < κ < min(U, B, 1/32),

where OLD_BASELINE = 0.001730970419199163702738 is the ledger's constant.

Necessity is a chain through nine named checks: κ < εq < q < a < B and
a < b < min(U, 1/32). Sufficiency uses PR4359's own `family` shape with
d = (min(U, B, 1/32) − κ)/7. [PROOF.md](PROOF.md) checks all 58 rows.

## What this tells the next contributor

- The outer rows lose nothing beyond strict slack. Revision 8's "work
  backward from the nine outer rows" step for κ > .01 reduces to U > κ and
  B > κ. These rows impose no other condition.
- κ ≥ 1/32 is excluded for every supplier pair. The cap comes from the
  `complex_below_one_over_32` row.
- At the selected values, U = 21703153/7000000000 binds. The selected
  κ = 62009/20000000 is 3/7000000000 below the ledger supremum U.
- At the selected κ, any admitted BIT saving above κ passes. The admitted
  17/5000 has 5991/20000000 of headroom. The historical .0027 control fails
  only because .0027 < κ.

## Evidence

`verify.py` loads the ledger unchanged and checks:

- inventory: 54 strict plus 3 functional checks in the ledger, and the fourth
  functional check and the ledger call in the selected `pricing.py`;
- the closed form of each of the nine chain checks on 400 random exact inputs;
- the explicit witness at 528 points: a 9×9 grid of (U, B) with three κ per
  admissible pair, including κ = OLD + 10⁻³⁰ and κ = M − 10⁻³⁰, plus random
  pairs;
- 4,000 random perturbations of witnesses. The 58 that satisfy every check
  all lie inside the region. This is corroboration, not the proof;
- controls: κ = B fails `actual_bit_above_effective`; κ = OLD fails only the
  baseline row; b > 1/32 fails `complex_below_one_over_32`; ε > 1 fails
  `epsilon_below_one`;
- the selected corollary from `certificates/frontier5599/CLAIM.json`.

## Reproduce

From the repository root with CPython 3.12 and only the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/outer-ledger-kappa-region
python3.12 -B scripts/check_research_commit.py --package research/outer-ledger-kappa-region --check-source-history
python3.12 -I -W error -B research/outer-ledger-kappa-region/verify.py
python3.12 -I -O -W error -B research/outer-ledger-kappa-region/verify.py
```

Success prints `PASS_OUTER_LEDGER_KAPPA_REGION`. The run takes under a
second and writes no files. Inputs are pinned in [SOURCES.json](SOURCES.json).

## Limitations

This is about the ledger's parameter arithmetic only. It does not prove the
outer theorems the ledger encodes, the five inherited framework assumptions,
native, compiler or stock costs, or any supplier admission. Other outer
assemblies in the repository are not covered. No κ or selected frontier
changes.

## Open next questions

1. **Which proof obligation behind the 1/32 row binds first?** The row
   `complex_below_one_over_32` is the only supplier-independent cap. An older
   assembly audit (`research/format-limits-corrected`) calls its 1/32 domain
   cap conservative. First step: trace the row to its PR4359 source lemma and
   find whether a larger domain is provable. Blocker: the lemma is an
   inherited framework premise, not re-proved here.
2. **Does a joint supplier change cost the ledger anything?** The region
   depends only on min(U, B). A change trading complex for BIT saving gains
   κ only while U < B. First step: state any proposed trade as (ΔU, ΔB) and
   apply the min. Blocker: no such joint supplier exists yet.

## Credit

Produced by Nick Petalas. The ledger and its `family` shape are zxv's PR4359
outer parameters, as retained in `research/pr4359-p7-padding`; the selected
call and fourth functional check are from the #5599 package
`research/p104-helper-subspace-splits` and its contributor lineage. New work
is Apache-2.0.
