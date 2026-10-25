# MASTER-HANDOFF — gate-operand-export-parity

## Claim (one sentence)

At the selected PR589 checker/exporter boundary, destination-free gate source
lists always make accumulate-XOR and sequential ADD agree, while
destination-in-sources lists can diverge; the checker rejects them and the
exporter does not.

## Closest prior

- #2977 scatter multiplicity counterexample
- #3004 scatter odd-multiplicity agreement; OQ2 left gate operands open
- #2992 / #3273 / #3346 scatter successor schemas (scatter-only)

## New checkable fact

Exact Sym/Exp lemma with exhaustive 4686 dest-free agreements, named
`self_even` / `dest_with_src` witnesses, selected-word 5472 distinct gates,
four checker rejects, exporter +1 record on `self_even`.

## Evidence commands

```sh
python3.12 -I -B research/gate-operand-export-parity/verify.py
python3.12 -I -O -Werror -B research/gate-operand-export-parity/verify.py
python3.12 -I -B research/gate-operand-export-parity/independent.py
python3.12 -I -B research/gate-operand-export-parity/test_package.py
python3.12 -B scripts/research_package.py --package research/gate-operand-export-parity
```

## Soft-overlap vs leave-alones

Clear of stock-leaf / router / flag-0 / C5 / side-correction / present-head /
groups B–D native clusters. Touches only the #2977 supplier-boundary cascade
at the unanswered #3004 gate-operand OQ.

## Attribution

Author Wentao Li `<wentaol4@illinois.edu>`. Neutral AI assistance disclosure.
No `Co-authored-by: Victor Li`. No CrocSwap PR from this worker (master publishes).

## Disposition

Ready for master independent review / publish decision. Kappa unchanged.
