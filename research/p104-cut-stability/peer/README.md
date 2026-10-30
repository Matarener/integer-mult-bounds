# Independent all-cut logical scalar norm audit

The exact finite-word claim passes an independent implementation using Python Fraction arithmetic. The checker does not import or copy the parent's dyadic arithmetic, interpreter, norm helpers, compiler, or pricing engine. It reads the published word and compares its independently generated mathematical witnesses with the retained claim. This is a separate AI worker in the same research team, not independent human review.

| Quantity | Independently verified maximum | Maximizing cut |
|---|---:|---:|
| Prefix logical matrix infinity norm | 131072 | 24096 |
| Suffix logical matrix infinity norm | 135415/4 | 24297 |
| Prefix entry dyadic denominator exponent | 4 | 21436 |
| Suffix entry dyadic denominator exponent | 17 | 24214 |

Cut k means the state after the first k of the 25,310 events, with cut zero the entry. Both directions cover all 25,311 cuts. The prefix maximizer is role 93 with row {86: -65536, 93: -65536}. The suffix maximizer is public output 205 with 111 nonzero current-role coefficients; its complete exact row is in RESULT.json. The maximum-value witnesses, denominator maxima, and their witnesses agree exactly with the retained claim.

The forward calculation stores Fraction sparse rows over all 735 arbitrary public originals; the original eight owned roles start at exact zero and are initialized and cleared according to the word. MOVE is identity in the word's logical coordinate representation. A scalar event changes one row, so inspecting that row and retaining the previous maximum covers every current row at every cut. The checker verifies all 743 final rows, including the eight cleared owned roles.

The reverse calculation stores Fraction sparse columns of the response to all 743 possible current-role perturbations, measured in the 735 public endpoints. It maintains each endpoint's absolute row sum exactly when a column changes. Therefore the reported suffix quantity is a matrix infinity norm, not a maximum column norm. All 743 entry columns are checked against the complete prescribed endpoint map.

COPY is implemented as ADD into a newly initialized owned zero on the ideal trace. Its derivative retains an arbitrary perturbation already in the target. Reverse COPY therefore adds the target response into the source response without resetting the target column. RESULT.json retains the entire nonzero public response of every one of the eight owned residual controls, with supports 55, 55, 54, 54, 57, 57, 57, and 57. Replacing COPY with assignment would suppress those target-residual columns and would describe a different error interface. INIT and CLEAR reset owned roles only.

The direct run completed in 2.364618 CPU seconds under an explicit 60 CPU second cap. If that cap is reached, the checker raises an incomplete-audit error instead of writing a partial success. Normal and optimized runs passed and compare against the frozen mathematical receipt:

```sh
python3.12 verify.py
python3.12 -O verify.py
```

Runtime is closed within this folder and uses only the Python standard library. It performs no network or Git access and imports no parent implementation. `--write` explicitly authors receipts; neither verification command writes them. ENVIRONMENT.json contains development timing only and is excluded from mathematical comparisons. FILES.sha256 fixes the complete payload inventory.

The result specializes logical scalar stability to this finite published word. It does not verify the separate chart-diagram norm proof, internal recursive-child implementation, fixed-point rounding allocation, movement or tape bounds, complete caller precision admission, or any new kappa. It does not establish scientific adoption or selected promotion.
