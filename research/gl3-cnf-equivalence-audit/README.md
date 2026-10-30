# Independent audit of positive-length GL3 direct-CNF equivalence

This audits the compiler-equivalence implication in Brian Ross's PR4211 at **ca0002008b497428f0b651501c4a220a9d2785e7**, following the named remaining obligation in PR4214 and PR4223. The predecessor already states the encoding argument. This adds an independently frozen Boolean/group-algebra oracle, a quantified written proof and literal binding of the actual complete clause multiset and coefficient graph. It does not invent a new encoder, establish UNSAT or recertify minimum nine.

## Exact claim and domain

For every integer n>=1, the stated direct-CNF schema is satisfiable exactly when a length-n legal normalized paid word attains the full monomial-diagonal target diag([A],[B],[I]) over F2[GL3(F2)]. All nine matrix entries and168 group coefficients matter, including arbitrary dirty third-input dependencies. Every step chooses exactly one of six CNOT labels and binary u,v satisfying vTu=1. Necessary support bounds preserve every attaining word; constraints are still emitted for outputs excluded by those bounds. The published CLI admits lengths1..9; saved lengths7/8 are the certificate focus.

The initial and terminal branches are distinct only for positive lengths. A library build(0) calibration yields a true-unit formula even for a nonidentity target, while the published CLI rejects0. This excluded case is not reported as a defect in the saved instances; no n>=0 compiler theorem is claimed.

The proof separates legal choices, exact full-coefficient recurrence, support necessity, and total bidirectional Tseitin extension/decoding. The finite oracle and source binding corroborate and bind the written argument. Gate-clause checks alone would not certify the caller's graph; graph evaluation alone would not exclude other auxiliary assignments. Both directions are required.

## Evidence and reproduction

The independent oracle is frozen before predecessor/source or generated source-query access. The separate adapter intentionally reuses unchanged source modules for actual construction and authenticated positive replay. It compares the complete actual clause multiset to independent gate/selector/equality semantics, then compares every actual transition output with the independent coefficient recurrence under one-hot label constraints. Variable1's true unit, signed constants, empty/unit clauses, boundary coefficients and support-fixed outputs remain explicit. Retained receipts give literal instance counts, hashes and controls.

Actual mechanical coverage is all nine pruned CLI lengths1..9 plus unpruned9:680,919 clause entries,81,648 complete next-state equations,680,724 helper calls,27,216 each q/shift/delta coefficients, and complete allocated-variable partitions. Source group rows, all six pullbacks, distances and support masks first bind to independent data. Direct9 has zero failed clauses in both actual formulas, and all ten full prefixes match independent dense recurrence and separate convolution. The independent core retains432 primitive rows,576 signed gate rows,256 normalization rows,4096 selector rows,1512 generic coefficient ANFs and1512 each coefficient/endpoint omission witnesses, grouped into35 controls. Counts corroborate the quantified proof; they are not a SAT proof.

Python3.12, stdlib only, four registered normal/optimized warning-strict commands:

```sh
python3.12 -B scripts/research_package.py --package research/gl3-cnf-equivalence-audit
```

Default commands write no package files. SOURCE-PINS and SOURCES bind nine unchanged exports through a public input ancestor, retaining NOTICE/license and original CRLF containers. Regenerated formulas match the authenticated predecessor certificates declared byte counts and SHA256 hashes. Saved .cnf blobs were not separately downloaded for a direct file comparison in this session; no RUP proof was executed. PACKAGE-REVIEW seals final files; cold committed and hosted typed-payload checks are separate publication evidence.

## Open next questions

The smallest useful next task is a separately resource-budgeted another-platform replay of the saved length7/8 RUP certificates after fresh overlap. Authenticate checker and decompressed proof bytes, require decisive success and failure controls, and state remaining checker trust. This matters because compiler equivalence does not prove formula UNSAT. Explicit model lower-bound admission, independent-human/formal-kernel acceptance, changed models, physical compiler/caller/invoice, supplier/native outer theorem remain separate. No new kappa, selected-frontier change or merge.

## Sources and credit

Brian Ross supplied the conceptual strategy, direction, oversight, original encoding-equivalence argument and implementations, with substantial OpenAI Codex assistance. Retain Hanson Sun seed18 and Josie Elliston length10/three-register lineage, original NOTICE/license, James Reed's finite pin/seal review, PR4214's separate support audit and PR4223's separate normalization audit. Classical Tseitin, Boolean and group-algebra arguments are not new general mathematics. ToikY used substantial OpenAI Codex assistance for the independently frozen oracle, source-reusing integration and separate proof/code review. These are written/mechanical checks, not independent-human or formal-kernel acceptance. Apache-2.0.
