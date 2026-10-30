# PR3335 rank-34 fit: exact rational triple-gauge screen

**Scoped exact negative; no new supplier or kappa.** For the published PR3335 rank-34 scalar factorization, no single arbitrary rational change of basis on any three of its 34 channels lowers the complete-plane one-total invoice below **224**. Unlike a coefficient census, the search classifies every possible support pattern of a rational 3-by-3 matrix together with its inverse.

The exact classification has **487** feasible matrix/inverse support maps. Pricing all 487 maps on all `binom(34,3) = 5,984` channel triples checks **2,914,208** cases. Every triple's minimum invoice equals its old three-term subtotal, so the global invoice remains 224. This closes one simultaneous `GL3(Q)` move from the published basis; it does not close sequences of overlapping moves or larger blocks.

## Why 487 maps cover all rational matrices

Fix a 3-by-3 zero pattern `P` for a candidate gauge matrix `G`. An invertible matrix must have at least one supported determinant matching. Every entry of `G^-1` is a cofactor divided by `det(G)`. A 2-by-2 cofactor has zero, one or two available product monomials:

- zero products force the inverse entry to zero;
- one product forces it nonzero;
- two products permit either status, with a zero exactly when the two rational products agree.

For each chosen set of zero cofactors, the checker records the exponent-difference rows `D` of those binomial equalities and the corresponding sign-parity equations. Any rational witness's prime-valuation vector lies in `ker(D)`. For a requested nonzero cofactor, if its product-difference vector lies in the row space of `D`, equal magnitudes are forced and the signs must differ. Otherwise a generic vector in `ker(D)` separates the two exponents.

The determinant has at most six matching monomials. The checker groups them when their exponent difference lies in the row space of `D`; within each group the magnitudes are forced equal. It tests every sign assignment and retains one only when the zero cofactors have matching signs and at least one determinant group has nonzero signed sum. A generic integer valuation vector separates all other cofactor and determinant exponents. There are at most nine cofactor forms and fifteen determinant-term differences; using an integer nullspace basis, the checker tests at most 193 values of `N` in `(1, N, N^2, ...)`, which exceeds the root bound for all forbidden forms. It then constructs explicit witnesses with nonzero entries `±7^z`. Base 7 makes the highest distinct determinant exponent dominate the at most six lower terms.

This is a finite exact classification, not sampling. The certificate stores a rational witness for every feasible support map; the verifier checks each matrix, its exact inverse, and both support patterns. The 396 maps from the earlier signed-ternary 3-by-3 census are independently reconstructed and shown to be a subset of these 487.

## Invoice result

The sources are the SHA256-pinned selected-label archive and PR3335's exact rematching/support certificate. The checker reconstructs the strict scalar mask and rank-34 support minor, then confirms the base complete-plane ranks are `8*4 + 8*6 + 18*8 = 224`.

For each rational support map and each triple, the source columns are unions of the original channel supports selected by the columns of `G`; the inverse-reader rows are the unions selected by rows of `G^-1`. Each changed term is charged the exact `F2` pairing rank on the complete planes touched by its source and reader. All other 31 terms retain their original invoice. The minimum local delta is zero for every triple: histogram `{0: 5,984}`.

A separate determinant-two 3-by-3 gauge with half-integer inverse checks exact preservation of all 12,544 entries of the 112-by-112 scalar matrix. Deliberately using the wrong inverse is rejected.

## Scope and overlap

This result applies to one arbitrary rational `GL3(Q)` change on one triple of the fixed PR3335 factorization. It does not prove that every sequence of overlapping triples costs at least 224; a product of several local moves can mix more than three original channels. It also does not cover other scalar factorizations or establish a physical decoder. The inherited ideal plane-port allowance is 160, so a lower tariff would still be only a necessary screening milestone.

Related results: [PR3335](https://github.com/CrocSwap/integer-mult-bounds/pull/3335) supplies the rank-34 factorization; [PR3345](https://github.com/CrocSwap/integer-mult-bounds/pull/3345) and the retained paired-plane copy audit establish the base invoice and its orthogonal-local floor; [PR4004](https://github.com/CrocSwap/integer-mult-bounds/pull/4004) exhausts signed-ternary triple gauges; and [PR4020](https://github.com/CrocSwap/integer-mult-bounds/pull/4020) exhausts arbitrary rational pair gauges. This contribution combines a complete rational cofactor-pattern classification with a full all-triples price census. Pair-span gauges in PR3463 and common external-query perturbations in PR3472 concern different objects.

No kappa, supplier or selected-frontier change is claimed. Physical gathering, dirty-helper restoration, chronology, consumers, precision, compilation and all-size admission remain open.

## Reproduce

With Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/paired-plane-rank34-rational-triple-gauge/verify.py
python3 -O -B research/paired-plane-rank34-rational-triple-gauge/verify.py
python3 -B -m unittest discover -s research/paired-plane-rank34-rational-triple-gauge -p 'test_verify.py'
python3 scripts/research_package.py --package research/paired-plane-rank34-rational-triple-gauge
```

The registered replay reconstructs `CERTIFICATE.json` and `RESULT.json`; it does not trust the recorded map count or tariff. `SOURCES.json` pins both live inputs. `TASK.json` records the changed scope, boundary, overlap and remaining larger-block question.

## Open next questions

Can a sequence of overlapping triple gauges, or one rational block of size four or more, lower the invoice? Build an interaction graph from the 487 exact triple maps and screen a discriminating overlapping four-channel composition; alternatively derive the coupled cofactor constraints for `GL4(Q)`. A tariff below 160 would still need a legal physical decoder, consumer and complete supplier before it could affect kappa.

## Credit

Matarener/Mark and Claude via Claude Code supplied PR3335's rematching and rank-34 factorization. Arham Tahir's paired-plane copy audit and its credited predecessors supply the full-plane tariff and 224 base invoice. Their attribution and scope remain intact. This rational support-pattern census was prepared by OpenAI Codex with substantial AI assistance in the valuation argument, classifier, exact verifier and validation. No independent human review or formal proof assistant is claimed. Apache-2.0.
