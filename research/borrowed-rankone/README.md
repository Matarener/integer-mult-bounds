# Borrowed rank-one adapters: 666 allowance, no extra fields

This package improves the same four native cleanup blocks as [#4494](https://github.com/CrocSwap/integer-mult-bounds/pull/4494) and [#4499](https://github.com/CrocSwap/integer-mult-bounds/pull/4499). The total scalar allowance per orientation is **666 with zero additional owned fields**, versus 686 for #4499's zero-scratch option or 674 for its one-field hybrid. Both actual source orientations are checked. This is a local exact-arithmetic improvement, **not a new κ**.

| Forward persistent scalar ordinals in full_frame_cleanup | Original | #4499, zero fields | #4499, one field | This package, zero fields |
|---|---:|---:|---:|---:|
| 4727–4764 | 418 | 358 | 358 | 358 |
| 1615–1620 | 52 | 52 | 46 | 42 |
| 2900–2905 | 52 | 52 | 46 | 42 |
| 4251–4276 | 244 | 224 | 224 | 224 |
| Total per orientation | 766 | 686 | 674 | 666 |

The new construction temporarily adds one input into another, reads the resulting shared sum into all destinations, then reverses the input addition. It preserves every input and every arbitrary dirty exterior field, uses no CLEAR and requires no clean entry. The inverse-transpose orientation uses the corresponding dirty-target conjugation, with explicit subtraction before the update and restoration afterward. The two affected blocks each save 4 over the owned-field predecessor and 10 over their direct source bill. The other two windows retain #4499's gauges.

The general compiler enumerates every source and target rank-one pivot whose coefficient ratios are dyadic. It selects the cheapest such adapter or the inherited zero-scratch gauge program. This gives a sufficient universal construction and a finite pivot comparison; it does not solve unrestricted circuit minimization. PROOF.md includes exact cost formulas and a sufficient condition under which borrowing beats the owned sum. The programs and native-price receipts are in RESULT.json.

```sh
python3 -I -O -B research/borrowed-rankone/verify.py
python3 scripts/research_package.py --package research/borrowed-rankone
```

The package is standalone against its pinned main inputs, using standard-library Python. It includes the inherited gauge code and proof rather than requiring either pending PR to be merged. No Lean formalization or Linux execution is claimed.

## Open next questions

1. Integrate only these exact source-window replacements into the full native rebuild and replay stock, coefficient/norm and multiplication-bound invariants. This is required before any global bound claim; this local package adds no recursive jobs or productive-temporary credit.
2. Look for a larger source-bound rank-one block whose admissible pivot satisfies the strict cost inequality in PROOF.md. First compare the complete preparation, application and uncomputation bill. A rank-one label or lower gate count alone is insufficient.

Scope and overlap limitations are recorded in TASK.json and ATTRIBUTION.md. The selected frontier and authoritative MathProof DAG are unchanged.
