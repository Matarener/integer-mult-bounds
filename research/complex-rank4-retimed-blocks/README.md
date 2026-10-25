# Rank-4 retimed block calls in the selected gauge44 word

**Scoped zero-charge screen. No physical supplier or new κ is claimed.**

## Finding

The selected gauge44 local word has 142 rank-4 child calls per orientation. Fourteen target frames expose a useful grouping: frames 415–422 each contain seven rank-4 calls, while frames 431–434, 436 and 437 each contain four. The verifier partitions each seven-call frame into one four-call block and one three-call block, and each four-call frame into one four-call block. This yields 22 direct sums covering 80 calls: fourteen rank-16 children and eight rank-12 children. The grouped rank mass remains 320, so the full local mass remains 5,586.

The forward and backward traces have the same groups. Every proposed block has distinct output registers, one target frame and one operand phase. Between its calls, the only events are scalar additions on L registers. The verifier checks that no such addition reads or writes a later call's register, then symbolically compares the original and retimed rational linear maps on arbitrary initial register values. The block identity is

\[
\operatorname{diag}(A_1,\ldots,A_t)\operatorname{diag}(B_1,\ldots,B_t)
=\operatorname{diag}(A_1B_1,\ldots,A_tB_t),
\qquad t\in\{3,4\}.
\]

The standalone profile changes from `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` to `{1:2412, 2:418, 3:432, 4:62, 5:82, 8:8, 12:8, 16:14}`. At the retained fixed-word ceiling, this raises the ideal exponent-saving ceiling by **2.0187%**, below the rank-shape card's 5% screen. Its corresponding ideal κ cap is about 0.00172120. This is a relaxation with gathering, output routing, frame/interface conversion, hosting, precision and arbitrary-dirty restoration all waived; it is not an attained κ.

For context, the package also composes this disjoint rank-4 profile delta arithmetically with the pinned rank-2/rank-3 zero-charge profile from [`complex-mixed-rank-diagonal-seed8433`](../complex-mixed-rank-diagonal-seed8433/README.md). The resulting hypothetical profile has an ideal ceiling gain of **6.6289%** and a κ cap of about 0.00179884. The registered replay runs that predecessor's verifier first. This composition crosses 5% only under the same zero-charge relaxation and admits no supplier or new κ.

## Scope and wall

This screen tests the rank-4 same-target-frame pattern beyond the selected-word rank-1 batching of [PR #1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779) and the strict chronological rank-2/rank-3 blocks of [PR #1960](https://github.com/CrocSwap/integer-mult-bounds/pull/1960) and [PR #2014](https://github.com/CrocSwap/integer-mult-bounds/pull/2014). It does not generalize those results or certify a full recursive interface.

The frozen local trace provides ranks, registers, source/target frames and scalar references. It does not identify the physical left/right operand banks, block-input layout, output ownership, scratch lifetime or dirty-state restoration contract for a fused rank-12/rank-16 call. Those costs remain unknown. The standalone rank-4 screen misses 5%, and the joint profile is only an optimistic composition, so this contribution stops at the exact local handoff rather than starting another implementation round.

## Reproduce

From the repository root, the registered replay runs both the predecessor screen and this package:

```sh
python3 scripts/research_package.py --package research/complex-rank4-retimed-blocks --check-only
python3.12 scripts/research_package.py --package research/complex-rank4-retimed-blocks
```

The source archive, exact program member and canonical word are pinned in [SOURCES.json](SOURCES.json). The verifier checks both orientations, symbolic retiming, rank-mass preservation and exact rational ceiling brackets. `RESULT.json` is recomputed byte-for-byte by the verifier.

## Open next questions

Can one concrete rank-4 group (for example target frame 431) be emitted as an actual rank-16 child with its left/right operands, output owners, scratch lifetime and arbitrary-dirty restoration fully specified? The next step is to trace its four child recipes through the producer and consumer, materialize the 16-by-16 block inputs and output map, and price every copy, frame conversion, hosted slot, precision term and restoration operation. The current trace lacks the physical ownership and lifetime contract needed for that invoice.

## Credit

The selected word, source archive and predecessor constructions retain their original authorship and citation chain. This scoped verifier and screen were prepared by Gonzalo Mier with substantial OpenAI Codex assistance; no independent human review is claimed. New work is Apache-2.0.
