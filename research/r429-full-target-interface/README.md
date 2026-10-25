# R429 with FULL targets and no private field

This package replaces the fixed R429 source-code/private-repair boundary by nine source-pivot totals scattered after all 111 targets have been lifted to FULL. The complete local word has 12,932 signed ADDs, 2,984 MOVE queries and no COPY, ERASE or private field. Its full paid histogram is

`{1:1406,2:1342,3:79,4:44,5:93,6:11,7:9}`, with rank mass 5,097.

All 651 arbitrary logical integer inputs are covered. Sources and 429 helpers return their original logical values exactly; old target values retain coefficient1, and target update is x modulo2 with even helper leakage. The literal integer inverse returns every input. Helpers start at ZERO and finish at FULL, so their physical outputs are F8*d. The physical binary data block is `[[S,0],[S,T]]`, with source operator S of native rank7 and T=F8 of rank8. An additional 111 common-FULL ADDs diagonalize the data block. Those additional ADDs are explicitly outside the emitted shear word's 12,932 count.

The target lifts use 111 rank-one queries, all paid. They make local mass equal local native coverage: `111*(7+8)+429*8=5097`. In the stated L-bank diagonal topology the complete rank deficit is zero, conditional on each bank serving once as source and once as target in distinct calls and on legal helper hosting. Aggregate capacity already requires L>=7; this is not a hosting construction. A different three-old-seed/six-new-fanout word closes algebraically on eight independent banks, but its favorable complete-invoice ceiling D<=33 still cannot support primitive exponent a>=1/500. Native admission at its changed cuts is a separate premise.

## Proof and validation

[PROOF.md](PROOF.md) gives the local contract and physical interpretation; [PROOF-CALLER.md](PROOF-CALLER.md) gives the exact caller algebra, paid diagonal bill and all-L conditional pressure bound. Separate AI [native](REVIEW-NATIVE.md), [caller](REVIEW-CALLER.md) and [source-integrity](REVIEW-PORTABILITY.md) reviews accompany the package. Independent implementations consume the fixed word and reconstruct the caller in a different representation.

```sh
python3.12 -B scripts/research_package.py --package research/r429-full-target-interface
```

See [VALIDATION.md](VALIDATION.md) for the exact local replay evidence. The portable replay uses only Python's standard library. It authenticates all frozen bytes before compiling them, keeps checks active under optimized callers, bypasses matching nested bytecode caches and compares every receipt field. Regeneration compares the complete decompressed word bytes; frozen gzip hashes retain provenance, while regenerated compression headers and zlib choices may differ. No mathematical receipt field is dropped. Original workstation paths are normalized only for relocation, with colliding keys rejected.

## Corrected historical statement

The frozen predecessor receipt incorrectly says every scalar ADD is at ZERO or FULL. In fact 3,027 inherited ADDs use 626 other common frames; 5,758 use ZERO and 4,147 use FULL. The correct contract is that every ADD uses its actual common frame, while all NEW nine-total compensation ADDs are at FULL. The declared prose-only adapter corrects this sentence in the current expected receipt; the original source and receipt remain byte-for-byte preserved. The verifier checks that this is the only changed receipt field. No arithmetic, loop domain, cost, frame test or defect control changes.

An unused historical `inverse_event` helper incorrectly comments that every primitive is involutive. A comment-only adapter states that `new_F` needs `new_F_inverse`; the executed main already uses the correct inverse.

The historical seeded-star receipt uses six earlier fanouts with private cost 3 and nominal D15. Substituting the later zero-private interface raises that favorable ceiling to D33, conditional on the same native interface being admitted at the changed cuts. The caller proof states this substitution; the earlier receipt is retained for its exact algebra and chronology, not as a current cost invoice.

## Limits

The inherited internal MOVE compiler contract is not re-proved over every odd ADDRESS modulus. New cap-to-FULL lift operators are checked exactly over the dyadic rationals; all frame labels and strict containment steps are checked. The 874 forward/reverse row-L1 bound is an integer-prefix bound, not a rounded-child precision theorem. Physical owner allocation, copied-total alternatives, source access, routing, tape, all-size recursive lowering and a favorable complete joint recurrence remain open. No selected-frontier change or new κ is claimed.

## Open next questions

A useful next question is whether a changed multi-output native compensation interface can avoid the 111 target lifts without replacing them by unpriced copies or source restoration. First specify its actual source/target cuts and arbitrary-dirt endpoint. A different caller must rederive its complete histogram and coverage before using a moment test.

## Sources and credit

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The input R429 word has canonical SHA256 `ebc33ee086f610c1fd540fa56bb99b2b96a768e4aed4a18defcb0e1f507fca89`, exactly the word already published in [PR3645](https://github.com/CrocSwap/integer-mult-bounds/pull/3645). Its helper deletions, three-row minimality and earlier cap-copy audit are prior work. This contribution changes the endpoint and compensates directly with nine FULL source totals.

Sagar Thakrar supplied the transported R438 word; Ali Romman supplied the construction, boundary-persistence and source-code lineage, with antecedents from DreamingOfClouds and eumemic. Related restored mutable-source query tours include Hanson Sun / bbMisk's PR1522. Detailed canonical pins are in SOURCES.json; ORIGINS.json and FROZEN-SHA256.json retain unpublished-source and review provenance.

Prepared by Ross Richardson with substantial OpenAI Codex assistance, including separate AI reviews. Original notices retained; Apache-2.0. No independent human or formal-kernel certification is claimed.

James Reed / [PR3850](https://github.com/CrocSwap/integer-mult-bounds/pull/3850), based on Gonzalo-Mier / PR3772, prices a different retained FULL-target schedule with L-1 public banks and negative deficit. The direct topology here has L banks; PROOF-CALLER.md compares both complete invoices. The fresh overlap snapshot covered735 open PRs and2597 Discussion records; it is search coverage, not a novelty certificate.
