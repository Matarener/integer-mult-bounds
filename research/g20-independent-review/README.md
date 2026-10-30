# Independent review of the G20 BIT chain PR5679 / PR5708

**Review result; no new bound claimed.** This is a non-author review of
[PR5679](https://github.com/CrocSwap/integer-mult-bounds/pull/5679) (ordinary BIT
component .003507410738409) and
[PR5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708) (.003507719059749),
answering the revision-8 request to review this chain before another G20 search.
Four new checkers, written from scratch, import no code from either package or its
predecessors. **No discrepancy was found.** One structural finding reduces what an
admission of PR5708 must depend on.

## What is checked independently

| Claim | Checker | PR5679 | PR5708 |
|---|---|---|---|
| Every used frame: exact rank(B)=dim, rank(A)=8−dim, A·Bᵀ=0 | `audit_local.py` | 636 frames | 636 frames |
| Every query: nesting by **subspace inclusion** (rank of stacked bases), rank = dim difference in 1..7, R_s·R_t = I−2(P_hi−P_lo) | `audit_local.py` | 2,367 kinds | 2,367 kinds |
| Local word legality: common-frame ADD, free moves only on zero payloads, ERASE/INIT only on owned wires | `audit_local.py` | 21,807 events | 14,794 events |
| GF(2) endpoint on all 685 columns | `audit_local.py` | pass | pass |
| **Operator endpoint with exact 8×8 rational matrices** per input symbol, no moduli or probe points | `audit_local.py` | pass | pass |
| Global GF(2) replay: identity on 11,022 originals, 48 owned registers return zero | `audit_global.py` | 443,238 events | 317,004 events |
| Paid histogram recounted from QUERY events equals INVOICE (56,223 queries) | `audit_global.py` | pass | pass |
| All 18 calls equal the local word under one consistent injective wire map | `audit_global.py` | pass | pass |
| Target owners are all originals once; histogram equals INVOICE; rank-8 targets in 8-dim frames; split targets 1→508 and 508→0 have rank 4 | `audit_global.py` | pass | pass |
| Raw crossing, tested margin, α/γ/δ tails, H0/H1 cutoffs, rank-mass tails (stdlib Decimal, 60 digits) | `audit_admission.py` | .0035074107384692 | .0035077190598115 |
| PR5679→PR5708 delta: paid +36H1−72H2+36H3, targets unchanged | `verify.py` | — | pass |
| Twelve negative controls (wrong rank, dropped or duplicated ADD, wrong ADD frame, free move of a payload, erased original, wrong exit frame, global rank change, dropped global ADD, lost target debit, understated invoice); a legal over-payment is accepted and visible in the bill | `controls.py` | — | pass |

The local endpoint check is exact over Q. PR5782's modulus guard (odd moduli coprime
to 12) is not rederived here.

## Finding: the predecessor chain need not be admitted first

PR5708 seeds its five finite ordinary levels with PR5679's value as the completed
backend. PR5679 seeds from PR5665's value, and so on. Read literally, admitting PR5708
would require admitting each predecessor value. `chain_levels.py` reruns the same
recursion `a=(1−ρ)C1+ρ·backend` (ρ=1/100, strict 10⁻¹⁵ grid) from other seeds:

- seeded with the **selected admitted ordinary backend .0034363538396**, six levels
  reach exactly .003507719059749;
- seeded with .0034, six levels also reach it;
- `audit_admission.py` shows that the uniform tail guards hold on
  [.0034363538396, .00351] (γ ≤ 0.96106 < 31/32, δ ≤ 0.92956 < 19/20).

The same holds for PR5679's value. If the PR4814 levels accept any completed ordinary
backend of this type as a seed, PR5708's component can be admitted from the selected
backend directly. Maintainers should confirm this reading.

## Not covered

- The five framework assumptions, including the native contract over the source-admissible
  prime domain, ROW/spectator, owned erasure, compiler, precision and fixed tape.
- Inputs used as given: FRAMES.json, the controller, the local endpoint specification, the
  paid ranks of WHOLE_IDLE (7 per stage) and THIN (1) controller queries, and the ranks of the
  3,552 MAIN-bank targets. These are unchanged since the G20 baseline and are not part of the
  PR5679/PR5708 delta. The controller's formal MAIN polynomial was not replicated.
- The finite fee, stock and compiler schema, apart from recomputing H0/H1.
- Converting the ordinary component into admitted BIT and its use in the nine outer rows.
- Later ADD-only successors (PR5807, PR5828/5835).

## Reproduce

```sh
python3 scripts/research_package.py --package research/g20-independent-review --check-only
python3.12 scripts/research_package.py --package research/g20-independent-review
```

Python 3.12 and the standard library are enough. The expected final token is
`PASS_G20_INDEPENDENT_REVIEW_5679_5708`. A full run takes about 90 seconds,
mostly for the controls. [RESULT.json](RESULT.json) records every compared value.

## Open next questions

- **Can the ordinary levels be reseeded from the selected backend under PR4814?**
  This would separate PR5708's admission from its unadmitted predecessors. First step:
  check the PR4814 level statement for any requirement on the seed backend.
  Blocked by: a maintainer reading of the framework.
- **Do the 3,552 MAIN-bank target ranks follow from the controller?** This is the
  largest input still taken as given. First step: derive 7·(stages)+1 from
  CONTROLLER.json thick stages for each bank. Blocked by: nothing.

## Credit

Review and checkers by Matarener, with substantial Anthropic Claude assistance.
All G20 constructions, packages and credit belong to their authors: Ali Romman,
Dugongue, ai-nanachi and the retained lineage named in those packages. Apache-2.0.
