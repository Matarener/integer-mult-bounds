# Independent B13 accounting review

**Pass for the fixed optimistic accounting model, subject to the explicit scope
below.** Native entrance, scalar endpoint replay and literal target-cut
reconstruction are separate review obligations. This review does not mark the
whole B13 package or its publication complete.

Files were read from the immutable changed-endpoints source package. Only this
review directory was written. No original input, primary checkout, worktree,
public discussion or pull request was changed.

## Mathematical findings

1. The actual selected binary column basis has globally minimum source-plus-
   target MOVE event count 44. The independent threshold-span certificate is
   rank 1 at weight four and rank 9 at weight five. Exhausting 512 combinations
   of the nine selected columns supplies the inverse map; a further 470
   fundamental-circuit inequalities independently certify optimality.
2. The entire systematic encoder agrees coefficient by coefficient. Its
   parity weights are 48,49,58,58,51,51,53,52,50, totaling 470 ADDs per bank.
   Preparing/unpreparing two banks separately costs 1880 ADDs. This is the
   literal code's cost, not a lower bound on all XOR programs or a native cost.
3. Every one of 222 source/target paths has rank mass seven, and every one of
   429 dirty-helper paths has rank mass eight. The actual private parity
   histogram has 44 events and rank mass 126. The complete one-call histogram
   has mass 4986. No nine-column basis improves the 126 rank-mass charge in
   this fixed word merely by selecting different dependent ports.
4. For the retained ordinary paired topology, **odd L>=3** is the valid domain.
   `PROOF-ACCOUNTING.md` derives all public idle mass, every fractional
   width-eight bank and its padding, then proves `D=-24L-102` for all such L.
   Every positive child exponent fails because every child strictly contracts
   and the zero-exponent bill already exceeds stock. This proof does not
   depend on the seven saved numerical examples.
5. All seven serialized invoices match independently, including every
   histogram coefficient, stock and mass. Actual controls delete a parity ADD,
   delete the 18 parity MOVE paths, or add endpoint stock together with its
   idle cost. They change the claimed invariant as expected; no changed
   schedule is asserted to pass admission.

## Clarifications required in the published presentation

* State odd L>=3 at the invoice theorem, rather than leaving the lower endpoint
  implicit in the seven examples. L=1 has m=8 and q=1; its failure is the lack
  of the stipulated paired public topology and idle formula, not division by
  zero. The checker now rejects that domain explicitly.
* Keep “minimum weight” tied to MOVE **event count**. The number 470 does not
  inherit a global optimality theorem from the column matroid. All chosen
  bases have the same rank-mass charge 126 in this bulk.
* Describe completeness relative to the declared optimistic invoice. It
  grants fractional helper banks and free private zero storage/preparation,
  encoders, native entrances, controllers and primitive work. It neither
  supplies integral owners nor excludes a changed stock/endpoint contract.
* Do not conflate scalar `RE=0` with native invariance, integer-zero cleanup,
  the separate reader floor, or a universal encoded-supplier obstruction.

These are scope clarifications, not a discovered counterexample to the fixed
L>=3 accounting identity. The producer's saved examples lie in the valid
domain and passed the independent check.

## Related published work

The proof credits the frozen R438/R429/full-compensation/native sources and
the inherited ordinary paired idle accounting. Prior PR3850 uses that retained
paired schedule. PR4033 has a full-input cold-factor/reader contract; PR4039
has a FULL-target interface and its own caller hypotheses. Restricting a bank
to 102 independent input fields changes those premises.

Read-only targeted PR searches found Ali Romman's prior PR1136, exact head
`e6a8003673d55929be6925b22f9ee645d03c33c3`. Its proof is retained as
`PR1136-PROOF.md`; metadata and author credit are in `PR1136.json`.
It proves general native-query encoding/boundary obstructions for the PR840
operator and is relevant prior work. Those full VALUE-domain conjugacy and
orbit premises differ from this specific R429 code and invoice. No duplicate
of the exact accounting certificate was identified in this bounded lookup;
this is not a novelty guarantee or an exhaustive PR/literature review. No
historical verification suite was rerun for the overlap review.

## Reproduction and evidence

From this directory:

```sh
python3 independent_check.py --output INDEPENDENT-RESULT.json
python3 -O independent_check.py --output INDEPENDENT-RESULT-O.json
```

Both modes use exception checks rather than removable assertions and produce
byte-identical results. `VALIDATION.json` records command outcomes, timings
and checker/result hashes. The checker uses reverse adjoints, enumerated
binary spans and inverse maps, and a collected idle-slot multiset; it does not
import or run the historical producer. It performs no native geometry search
or physical ownership search. `FINAL-CHECK.json` freezes the review files and
their source pins for the parent integrator.

This is an independent computational cross-check plus written all-parameter
argument, with substantial OpenAI Codex assistance. It is not independent
human or formal-kernel proof. No new kappa claim is supported.
