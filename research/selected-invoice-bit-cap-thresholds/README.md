# Local thresholds for the selected complex invoice to reach the BIT saving

**Finite exact certificate on an accounting relaxation. No new κ.** This
result is produced by Nick Petalas. The selected frontier is unchanged.

The selected #5599 complex supplier binds at `U = 0.0031004563072…`. The
admitted BIT saving is `17/5000`. This package fixes, exactly, how much the
local word of the selected P104 invoice must change before the complex bill
passes at `C = 17/5000`. Every other paid job and target stays fixed. It also
bounds what free local helper splitting can do.

## Result

The invoice is the authenticated output of `scripts/export_selected_invoice.py`
at base `19fdb086e`. The packaged `INVOICE.json` is its stdout byte for byte,
and its SHA-256 is the exporter's own `invoice_sha256`. The verifier checks
that every local paid job and local helper target appears exactly 18 times,
once per FULL. Paid work is `18·local + 1560 query + idle`, and targets are
`18·helpers + main`.

The bill passes at `C` when `Σ T_r r^(1-C) > Σ P_r r^(1-C)`. At `C = 17/5000`
the selected invoice fails by **72.892623830207**, which is
**4.049590212789 per FULL**.

| Local change per FULL, all else fixed | Passes at 17/5000? |
|---|---|
| delete one paid job of rank 1, 2, 3 or 4 | no; rank 4 gives 3.98 < 4.05 |
| delete one paid job of rank 5, 6 or 7 | yes |
| fewest deletions using only rank ≤ 1 / ≤ 2 / ≤ 3 / ≤ 4 | 5 / 3 / 2 / 2 |
| free full refinement of rank-9 helper targets into rank-1 targets | needs 61 of the 412 |
| free balanced split of rank-9 helpers into 4+5 | needs 194 of the 412 |
| refine every local helper target into rank-1 targets | passes; first crossing in [0.0094772838495, 0.0094772838496] |
| the same, at `C = 1/100` | **fails** |

For a helper target of rank `r`, every partition into positive ranks has
`Σ p^(1-C) ≤ r` when `0 ≤ C < 1`, with equality for `r` parts of rank one.
So full refinement maximizes the target moment at every `C`. Since that
maximum fails at `C = 1/100`, **no split of local helper targets alone, with
paid work fixed, lets the selected invoice pass at 1/100.** The split counts
are minimal for the same reason. A rank-9 helper gives the largest gain, and
the greedy count is optimal.

For comparison, #5599 refines thirteen helpers. theon199's #5702 shows that
fifteen fully refined H9 sources fund one added H1 per FULL. Reaching the BIT
saving needs about four times that, which is 61.

## Claim scope

This is an optimistic accounting relaxation of the complete signed moment
used by the selected invoice. A deletion or split here is free: no restoration,
native alignment, precision, compiler, stock or outer cost is charged, and no
physical word is supplied. A passing row keeps a route open. It does not make
a supplier. Once complex passes at `17/5000`, the admitted BIT saving binds;
this package does not prove the outer κ. Only the sign at each stated `C` and
the stated root bracket are certified. Uniqueness of the refined crossing is
not claimed beyond the separate failure at `1/100`.

Every `r^(1-C)` uses Python's correctly rounded decimal `ln` and `exp` at 80
digits. The total rounding error is far below `1e-50`, and every reported sign
clears `1e-30`. A float evaluation corroborates the deficit. The boundary rows,
including rank 4 versus 5, 4 versus 5 rank-one deletions, 60 versus 61 and
193 versus 194 H9 splits, and the `1/100` failure, are rerun on the actual
changed invoice rather than inferred from the table.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
python3.12 -I -B -W error research/selected-invoice-bit-cap-thresholds/verify.py
python3.12 -I -O -B -W error research/selected-invoice-bit-cap-thresholds/verify.py
python3.12 -B scripts/research_package.py --package research/selected-invoice-bit-cap-thresholds
python3.12 -B scripts/export_selected_invoice.py | shasum -a 256
```

Each verifier run takes about 0.2 s and prints
`PASS_SELECTED_INVOICE_BIT_CAP_THRESHOLDS`. The last command reproduces the
invoice hash in `INPUT.json` from a full checkout.

## Open next questions

1. Which physical window of the selected local word can delete one paid job of
   rank 5, 6 or 7, or two of rank 3 or 4, while keeping every target and
   restoration? Under this accounting, any one of them lets complex pass at the
   admitted BIT saving. The first step is to list the 200 local paid jobs of
   rank at least five and their producers and consumers. Closed rewrites of
   older words do not transfer automatically.
2. Splitting helper targets alone stops below `1/100`. Which changes to the
   paid side or to the main targets, priced with this same moment, would let
   the complex side pass at `1/100`? Any target above `.0034` also needs a BIT
   improvement.

## Credit and sources

The selected P104 word is by Pierre-Loic Doulcet (hexapode), with Ali Romman's
complete caller and helper accounting, Cinna Davis's controller, Jacob Alan
Sussman's productive recursion and zxv's invoice interface. The invoice exporter
is Ali Romman's. theon199's `helper-refinement-budget-s29` (#5702) and
Clear1nsight's #5614 price related helper refinements, and the merged
`productive-lever-reprice` package priced a similar BIT-level gap on the older
#4470 invoice. They are cited, not re-checked. Pins are in
[SOURCES.json](SOURCES.json). Apache-2.0.
