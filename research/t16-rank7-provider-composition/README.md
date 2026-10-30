# Full-bin patterns improve the rank-seven T16 allocation

This is a focused descendant of [PR3457](https://github.com/CrocSwap/integer-mult-bounds/pull/3457), exact head `e47d1dd9e38241b902545dbc41d1bbe7fa0c4bcd`. It retains that construction's 408-helper rank-seven words, T16 call chronology and complete admission machinery. The new allocation admits two previously omitted full-bin patterns, `[7,7,9,9]` in capacity 32 and `[7,7,7,9,9,9]` in capacity 48, then repairs a bounded set of actual chronological groups. `BOUNDED-DOMAIN.md` records the precise discovery scope and limits; no packing optimum is claimed.

**Complete finite admission passes.** The modern conditional exponent is
`κ = 0.001727254340596650594393 - 10^-46 - 10^-70`, an exact improvement of `0.000000101127658098000618` over PR3457. It remains below the supported T740 construction. This is a scoped T16 improvement; selected records remain unchanged.

The certificate reconstructs 58,752 helper occurrences across all 144 calls from 189 group/pattern allocations and 1,222 nonzero integer flows. Verification has no optimizer dependency. The idle-profile change is `-229 H1 + 110 H2 + H3 - 2 H5 + 2 H8`; the concavity decomposition in the proof makes this a strict paid-profile gain throughout `0<a<1`.

| Quantity | Value |
| --- | --- |
| Idle profile | `4147 H1 + 110 H2 + 1091 H3 + 456 H5 + 2 H8 + 6078 H48` |
| Full paid profile | `{1:354499,2:104366,3:33923,4:14688,5:3336,8:1154,48:6078}` |
| Rank mass / deficit | `1,041,408 / 5,120` |
| Helpers per call / private cleanup families | `408 / 91` |
| Complete physical stock | `14,845` |
| Dispatch | `(0,0): extra`; remaining 143 calls: `gauge44` |

Both exact moment engines certify complex endpoint `0.001727254340596650594393`. It realizes approximately **99.85413418259235506%** of the same current-word packing cap; `CAP-RATIO.json` gives exact rational inputs and bounds, credited to PR3361. The ancestral pricing adapter separately gives `0.001724276077257820`; that diagnostic is not the modern admitted exponent.

Complete admission freshly checks this changed allocation, parent lift, physical/controller invoice, discovery ledger and modern outer release. It authenticates and reuses both native providers from a prior fresh PR3148 replay. No new native-provider rebuild is claimed. The fifteen scientific inputs, canonical-source closure, compressed overlay and native-cache provenance are unchanged from PR3457. `SOURCE-ORIGINS.json` and `PREDECESSOR-3457.json` retain exact source identities. No private solver is required.

## Reproduce

From this directory with Python 3.12, numpy 2.3.5 and sympy 1.14.0 (including its mpmath dependency; tested with mpmath 1.3.0):

```sh
python3 -I -Werror -B reconstruct.py
python3 -I -Werror -B price_profile.py
python3 -I -Werror -B test_reconstruct.py
python3 -I -O -Werror -B test_reconstruct.py
python3 -I -Werror -B test_materialize.py
python3 -I -Werror -B verify.py --work /absolute/new/external/admission
```

The last command runs complete finite admission and writes its receipts outside the checkout. `MATERIALIZE.json` authenticates the canonical source files listed in `VERIFY.json` plus the compressed derived overlay; the registered package exporter includes all required files. Native cache reuse is explicit and does not replace owner/controller/physical/outer execution.

Use `reconstruct.py --output /absolute/new/owned/directory` to save the literal owners, source geometry, modern fill and audit receipts. The output directory must not already exist. No source is rewritten.

Nine test groups exercise valid reconstruction and reject duplicate/missing flow, fractional or Boolean counts, width/bin corruption, unavailable windows, literal role time/width/family faults, source-byte corruption, mismatched native widths and duplicate JSON keys.

`PROOF.md` explains the exact allocation argument. `CREDITS.md` preserves the predecessor algorithms and provider ancestry. PR3390 and the earlier T16 work remain valid historical branch improvements; this descendant preserves PR3457’s composition of the PR3413 chronology and current rank-seven supplier, and claims only its new bounded allocation improvement.

## Open next questions

1. Can a distinct omitted pattern or changed chronology improve the remaining gap with exact source windows and the complete bill? This bounded construction is not a global or chronological packing optimum.
2. Can a changed recursive interface improve the global T740 endpoint? Further fixed-word allocations remain below its attained cap.
3. The inherited all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery and analytic assumptions remain distinct from finite replay.

The retained fill uses 115 capacity-32 bins of the newly admitted `[7,7,9,9]` pattern. The capacity-48 candidate pattern was allowed in discovery but is unused in this certificate; no gain is attributed to it.
