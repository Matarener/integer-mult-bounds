# Independent exact covariance for every PR2586 native recipe

All 1,245 archived native recipes equal their canonical physical change of
chart, including exact global phase, on every input in Q(i)^512. Every one
of their 2,070 literal word occurrences has the matching old frame, new frame
and positive rank. The rank mass remains 3,542.

This closes the explicit native-identity premise in
[PR3406](https://github.com/CrocSwap/integer-mult-bounds/pull/3406), exact
`18a054fd585ab4b2010770ec83cba0c9f28184e3`. Its sharp global Gaussian Newton
entrance theorem retains its other hypotheses and proof obligations. The
entrance is unchanged, with 104 Y inputs in 4 B_9, 78 N inputs in 2 B_9 and
176 other public inputs in B_9. No actual caller, physical saving, supplier
admission, improved kappa or selected-frontier change follows from this audit.

## What this adds

[ywz65's PR2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586)
already checks these native identities with its retained compiler and native
machinery. This is a separate source-bound implementation that imports none
of that executable code. It reconstructs canonical charts from binary frame
columns, checks exact signed Pauli action and a complete exact nonzero column,
and binds all records to the chronological word. It addresses PR3406's third
open question, rather than repeating its dense fixture as evidence for a
universal operator identity.

[PROOF.md](PROOF.md) gives the exact canonical convention and finite all-input
argument. [RECEIPT.json](RECEIPT.json) records all 1,245 comparisons, their frames,
occurrences, ranks, and tableau/column digests. Ordinary replay recomputes and
compares the complete receipt, including JSON numeric types. It writes no
scientific artifact. The hashes summarize exact comparisons already performed.

The comparison criterion is credited to the native Clifford lineage and
[Tekalign's PR3218](https://github.com/CrocSwap/integer-mult-bounds/pull/3218).
The narrower PR3400/3402 audits check a different forward-tail promote/restore
pair through the retained checker. They are complementary prior coverage.
The [active actual-producer/consumer investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19008790)
remains distinct. This package does not price or prepare its entrance.

## Evidence and replay

The complete census compares 18 signed Pauli generator images and all 512
entries of one nonzero column per recipe. It reconstructs 445 distinct charts.
Every one of the 2,621 distinct monomial maps encountered has all 18 generator
relations checked on all 512 basis columns. The recipe occurrence profile is
1,632 H1, 74 H2, 86 H3, 104 H4, 48 H5, 42 H6, 76 H7 and eight H8.

The separate Fraction evaluator checks all four columns of every word of length
at most three in five two-bit generators. Its 156 words give 624 full-column
checks and 75 distinct matrices. Each also has an exact inverse check, and its signed tableau is checked in
2,496 direct dense intertwining relations. Thirty-two one-bit signed Pauli relations are checked directly. Three scalar
phase mutants have unchanged tableaux and are rejected by their exact anchors.
Wrong-stage, missing-stage, wrong-frame, occurrence-binding, omitted-record,
singular-map, dependent-frame, non-Clifford-phase and capacity controls reject.
An anchor-only collision is distinguished by the tableau. The receipt comparison
also distinguishes integer 1 from Boolean true. These controls do not constitute
an independent human or formal-kernel review.

Use standard-library Python 3.12 or later from the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p104-native-covariance
```

The registered commands run the full census normally and with `-O`, and the
controls under `-O`. For a source-complete Git-free export:

```sh
python3.12 -I -Werror -B research/p104-native-covariance/verify.py
python3.12 -I -O -Werror -B research/p104-native-covariance/verify.py
python3.12 -I -O -Werror -B research/p104-native-covariance/test_verify.py
```

SOURCES.json authenticates the two frozen live inputs before mathematical
execution. VERIFY.json declares them for CI and export invalidation. Explicit
receipt regeneration uses `verify.py --write-receipt /path/to/RECEIPT.json`.
The selected-construction cold replay, tensor-depth transfer and proof-kernel
formalization are unrun because they are outside this finite native identity.
The card's baseline orientation command stopped at a selected certificate
omitted by sparse checkout; no baseline PASS or selected-result failure is claimed.

## Open next questions

1. Can an actual caller provide the sharp whole-word Newton entrance and an
   affordable consumer? Compare this proof dependency with the active interface
   investigation linked above. Input preparation, physical availability and
   the complete paid bill remain blockers. Do not duplicate that active scope.
2. Can a proof kernel connect the native and scalar certificates? Start with
   the signed-Pauli commutant argument and exact-anchor lemma, then instantiate
   this fixed corpus. Formal native semantics and source-to-kernel refinement
   remain open. Another dense fixture alone would not close them.

## Scope and credit

Task `p104-side-correction`, changed to PR3406's explicit independent native
covariance handoff. Scientific base is canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6. The advance
[scope and coordination record](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19009154)
separates this audit from the active actual interfaces. Entry overlap covered
324 open PRs and 2,252 Discussion records with complete reported pagination
and no warnings. Sparse local notes and unsearched code diffs limit that search.
Claims and pending PRs are provisional evidence.

Credit ywz65 for the unchanged PR2586 word, recipes and original all-input
checks; Clear1nsight for PR3382's Newton domain; Tekalign for PR3025's literal
lifting and PR3218's comparator; Ross Richardson for the Clifford precision and
P104 work; and Chafik Boukhalfa, Charles Bethin, Ali Romman, Josie Elliston,
Rohan Arun, Hiroki Kumazaki, commdata2338, Nick Petalas and the retained native,
geometry and compiler lineage. Source notices and frozen archives remain
unchanged. Exact pins and attribution are in SOURCES.json. Nick Petalas.
Apache-2.0. Review status is recorded in TASK.json.

## Implementation bounds

This is a bounded Python reference verifier. Power-of-Ten rule 3 has a managed
allocation deviation. Fixed authenticated inputs contain 5,398 events, 1,245
recipes and 358 initial roles. Address arrays have at most 512 Gaussian pairs;
programs have at most 22 stages and denominators at most 36 binary powers.
The chart cache is capped at 500 entries and the monomial cache at 5,000 maps.
Integer growth is bounded by these gate counts and unit-magnitude initial
columns. No recursive code or predecessor executable is used. Every function
is below 60 lines, and explicit contracts remain active under `-O`.

The test harness uses Python's `runpy.run_path` on the single fixed local
`verify.py` source. This is the bounded rule-8/9 deviation for loading the
checked implementation without a stale import bytecode cache. It constructs
no code and has one possible target. A production or formal backend would
need its own fixed-capacity storage and source-refinement proof. Maximum
available Python warnings and the scoped Ruff diagnostics are run locally;
no repository-wide lint configuration is changed.
