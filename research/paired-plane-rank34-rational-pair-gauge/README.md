# PR3335 rank-34 fit: exact rational two-channel gauge screen

**Scoped exact negative; no new supplier or kappa.** For the fixed PR3335 rank-34 scalar factorization, no single arbitrary rational change of basis on any pair of its 34 channels lowers the complete-plane one-total invoice below **224**. The census covers every matrix in `GL2(Q)`, including even denominators, rather than a bounded coefficient alphabet.

The result closes an isolated pairwise move at the published basis. It does not close sequential overlapping gauges, simultaneous changes on three or more channels, other scalar factorizations, or the physical implementation needed to affect the selected multiplication bound.

## Exact parameterization and result

Fix two channels with current source columns `s_i, s_j` and inverse-reader rows `r_i, r_j`. Up to nonzero rescaling, a column of a rational 2-by-2 basis change is a point of the projective line `P1(Q)`. Represent a finite direction by `(1,x)` and the point at infinity by `(0,1)`. Its source vector and dual reader vector are

```text
source(x) = s_i + x s_j,
reader(x) = r_j - x r_i,
```

with the evident limiting vectors at infinity. If the two new source directions are `x` and `y`, invertibility is exactly `x != y`. The two changed terms are paired crosswise with the inverse-reader basis, so their total tariff is

```text
rho(source(x), reader(y)) + rho(source(y), reader(x)).
```

The support of `source(x)` changes only at the rational roots of its coordinate linear forms. The support of `reader(x)` changes only at the rational roots of its own coordinate forms. Between this finite set of critical slopes, both supports are constant. Therefore the exact finite search is: every critical slope, infinity, and two distinct rational slopes outside the critical set. Two generic representatives matter because both basis directions can lie in the same generic support cell while still being distinct.

At the published basis each of the 561 unordered channel pairs has four representatives (`0`, two generic slopes, and infinity), giving six distinct direction pairs per channel pair and **3,366 total tariff cases**. Every pair's minimum invoice equals its original two-term charge: the minimum delta histogram is `{0: 561}`. There is no strict improvement.

A determinant-two fixture uses

```text
G = [[1, 1], [0, 2]],       G^-1 = [[1, -1/2], [0, 1/2]].
```

The verifier checks the exact scalar fitting matrix on all 12,544 entries after the change of basis and rejects a deliberately wrong inverse.

## Scope and consequence

The source labels are read from the SHA256-pinned selected replay archive; the matching and 34 supports are read from the pinned PR3335 certificate. The verifier reconstructs the scalar mask, rank-34 support minor, complete-plane pairings, and base invoice `8*4 + 8*6 + 18*8 = 224` before searching. It uses no predecessor Python implementation.

The invoice 224 already exceeds the inherited ideal plane-port allowance 160. This result does not show that all rational gauges cost at least 224: it rules out just one rational 2-channel move from the published basis. It does not claim a kappa change or supplier. Physical gathering, dirty-helper restoration, chronology, consumers, precision, compilation and the selected frontier remain open.

The nearest results are [PR3335](https://github.com/CrocSwap/integer-mult-bounds/pull/3335), which supplies the scalar fit; [PR3345](https://github.com/CrocSwap/integer-mult-bounds/pull/3345) and the retained paired-plane invoice audit, which establish the base price and orthogonal-local floor; and [PR4004](https://github.com/CrocSwap/integer-mult-bounds/pull/4004), which exhausts signed-ternary 3-by-3 gauges on every channel triple. This contribution changes the coefficient domain to all of `Q` and proves the complete finite reduction for pair gauges. PR3463 pair-span gauges and PR3472 common external-query perturbations concern different objects.

## Reproduce

With Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/paired-plane-rank34-rational-pair-gauge/verify.py
python3 -O -B research/paired-plane-rank34-rational-pair-gauge/verify.py
python3 -B -m unittest discover -s research/paired-plane-rank34-rational-pair-gauge -p 'test_verify.py'
python3 scripts/research_package.py --package research/paired-plane-rank34-rational-pair-gauge
```

The registered replay reconstructs `CERTIFICATE.json` and `RESULT.json`; it does not trust the recorded minimum. `SOURCES.json` pins both live inputs, and `TASK.json` records the changed scope, family boundary, current overlap and open three-channel question. The exact determinant-two control checks all scalar entries, not just a sample.

## Open next questions

Can an arbitrary rational simultaneous gauge on three channels, or an overlapping sequence outside the pairwise-local neighborhood, lower the tariff? First build the coupled source/inverse support arrangement for one interaction-selected triple and compare it with the bounded signed-ternary census. A result below 160 would pass only the optimistic copy screen; exact dirty-state native realization and supplier admission would still be required.

## Credit

Matarener/Mark and Claude via Claude Code supplied PR3335's rematching, supports and rank-34 result. Arham Tahir's paired-plane copy audit and its predecessors supply the full-plane tariff, scalar-mask conventions and 224 base invoice. Their attribution and scope remain intact. This rational pair-gauge census was prepared by OpenAI Codex with substantial AI assistance in the mathematical parameterization, verifier and checks. No independent human review or formal proof assistant is claimed. Apache-2.0.
