# MASTER-HANDOFF — odd-kernel-coeff-bit-tariff

## Claim (one sentence)

Under the named ADDRESS affine coefficient-bit tariff, every certified odd
kernel `q∈{3,5,7,9,15}` strictly exceeds the dyadic fused and baseline bills
on `j=0..32`, so larger-`q` coefficient tables never pay for themselves
despite identical typed child/XOR counts (answers #2687 OQ2).

## Closest prior

- #2687 / `research/odd-kernel-query-pair` — exclusion pattern; OQ2 left open
- PR840 / `research/dyadic-query-pair` — dyadic fusion and ADDRESS shape
- triadic-query-pair — kernel-3 specialization feeding #2687

## New checkable fact

Named tariff `T_word` / `T_fused` / `T_baseline`; closed form; prior
`address_word` cross-check; `165+165` strict odd-over-dyadic exceedances;
non-monotonicity of `T_word` (`32<38<45` at `|k|=4,2,1`).

## Evidence commands

```sh
python3.12 -I -B research/odd-kernel-coeff-bit-tariff/verify.py
python3.12 -I -O -Werror -B research/odd-kernel-coeff-bit-tariff/verify.py
python3.12 -I -B research/odd-kernel-coeff-bit-tariff/independent.py
python3.12 -I -B research/odd-kernel-coeff-bit-tariff/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-coeff-bit-tariff
```

## Soft-overlap vs leave-alones

Clear of flag-0 tail / stock envelope / gate-operand / C5 / side-correction /
present-head / groups B–D native clusters. Touches only the #840 / #2687
odd-kernel cascade at the unanswered coefficient-bit OQ. Soft-overlap with
#2687 is intentional predecessor pin of `program.py`, not a typed-invoice
reprint.

## Attribution

Author Wentao Li `<wentaol4@illinois.edu>`. Neutral AI assistance disclosure.
No `Co-authored-by: Victor Li`. No CrocSwap PR from this worker (master publishes).

## Disposition

Ready for master independent review / publish decision. Kappa unchanged
(`0.001672660197076918`).
