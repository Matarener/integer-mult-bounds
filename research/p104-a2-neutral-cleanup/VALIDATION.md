# Validation of the common cleanup/A2 word

Environment: Python 3.12.8, macOS 26.5.1, arm64; standard library only. Canonical publication base `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority revision 7. The scientific predecessor heads and retained input hashes are in REPLAY-SOURCES.json. Original frozen predecessor files remain unchanged.

## Complete scientific replay

```sh
python3.12 -B research/p104-a2-neutral-cleanup/verify.py --write
python3.12 -B scripts/research_package.py --package research/p104-a2-neutral-cleanup
```

The first command generated FULL-RESULT.json after a fresh normal full replay. The registered replay then checked quick source/word reconstruction, isolated optimized full replay against that saved receipt, and the separately implemented reverse-order composition audit. Both full runs include actual native-map and physical-caller checks; the earlier PRICE-CHECKPOINT.json reused source boundary receipts and is historical pricing-only evidence.

Normal/registered logs record the outcomes. The complete receipt includes:

- 743 independent public inputs, nine owned roles, eleven owned lifetimes and peak occupancy two; every productive target retained.
- 752 exact dense transpose columns / 565,504 coefficients.
- 2,916 signed native maps with exact phases and rejected wrong-phase control.
- 7,488 physical contacts and 53,248 central-square columns; full main action and all 3,120 whole idle jobs.
- Two exact rational moment engines, proved negative derivative through [0, 0.0034], strict compiler/floor/tail/rounding tests, BIT stock and all 54 strict plus four functional outer predicates.
- 66,492 paid calls, 12,958 productive targets and surplus 760. Ordinary local allowance 220,220; complete nonrecursive upper bound 184,647,552 < 1e9.
- 29 scoped rejection controls in FULL-RESULT.json, including source-hash checks. These controls differ in scope; source-hash function tests alone are not import-order tests.

The tighter claim is κ = 0.00310644468, tested at 0.003106444685. The raw crossing is (0.00310644469581, 0.00310644469582). Compiler gap 1/1400000000000, logarithm/tensor power 1024, reserve 1e-12 and finite threshold N = 2^80511200000000000 all pass unchanged mathematical predicates.

## Source authentication and actual corruption controls

The verifier authenticates the frozen 19-file input inventory by size, SHA256 and Git blob before importing retained code. PR5644's original source reader then authenticates all 36 PR5627 export payloads. All 19 available original source-manifest rows match their declared SHA256 values. Runtime imports use a fresh private Python bytecode-cache directory.

SOURCE-CONTROLS.json records three actual copied-package controls. One byte was independently changed in the retained PR5643 constructor, PR5644 constructor and PR5627 source archive in a temporary copy, then the real verifier ran with `-I -O -B --quick`. Every run rejected the exact source hash before any retained-code import. Original source bytes were never modified.

## Separate scoped checks

`audit_composition.py` proves reverse construction order reproduces the identical complete program, not only its histogram. The separate triage interpreter verifies every scalar endpoint row and owned zero exit on the common word. All eight H7 first-delivery same-frame public-span reconstructions fail in that stated model. The complete common-chart helper-cut scanner covers 8,847 event/chart states at 7,253 cuts for 411 ZERO-to-FULL helpers; all full rational boundary pairings vanish. Its 18 nontrivial states pass a separate backward-prefix/forward-suffix witness check. Portable copies reproduce the original saved JSON receipts.

Read COMPONENT-TRIAGE.md and the analysis subdirectory for exact domain and completeness limitations. The source helper-cut scanner intentionally regenerates its own receipt; the independent witness checker does not regenerate it.

## Signed-invoice preflight

`export_invoices.py` extracts both complete paid/target histograms from the frozen PR5644 receipt and FULL-RESULT.json. The shared `scripts/compare_recursive_invoices.py` reports `uniformly_better`, Δpaid = 18(H2 + H6 − H3 − H5), and Δtargets = 0; the exact inputs and output are in invoices/. This is a uniform concave-tariff arithmetic check, separate from physical legality and supplier admission.

## Publication and remaining obligations

The local package metadata/source-pin check and final committed-byte check are separate from scientific replay. The optional full-history preflight cannot run because the shared repository is shallow. Pending scientific dependencies are retained as authenticated bytes and an archive, not supplied only by cached unmerged Git objects.

No hosted CI, independent human review, Lean/proof-kernel check, historical all-suite replay or selected-frontier change is claimed. The same native all-width, owned erasure, compiler, precision/fixed-tape, analytic recovery and helper-endpoint hypotheses remain. The complete huge uniform program and rounded multiplier are not materialized. Agent cross-checks are author-side evidence.
