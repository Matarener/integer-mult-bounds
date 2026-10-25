# A separately written checker for the fixed GL3 length-seven refutation

**Result: the unchanged 18,882-variable, 61,138-clause length-seven formula is
unsatisfiable under a separately written positive-hint LRAT interpreter.** The
fresh replay checks 8,558 additions and 2,420,732 hints, deriving empty clause
72867. This takes the separate-checker handoff from
[PR4242](https://github.com/CrocSwap/integer-mult-bounds/pull/4242), after its
another-platform execution of the same drat-trim implementation. No new kappa.

`checker.py` does not import or execute drat-trim, a solver, or another checker.
It parses the actual CNF and the complete saved LRAT stream. Every addition must
have live unit reasons ending in conflict under the negated proposed clause;
fresh IDs and deletion semantics prevent circular dependencies. See
[PROOF.md](PROOF.md) for the entailment argument and exact supported subset.
The pinned native converter is an **untrusted hint producer**: its success
message and logs play no role in acceptance. The implementation uses explicit
checks, so optimization does not remove proof obligations.

The exact CNF SHA256 is
`2f1b925d8cc84ce36f35ac8033d6e4afffe373a2ab37fe5f52d6e29884c1ed0c`.
`length7.lrat.gz` contains 15,470,341 checked payload bytes, SHA256
`e9dc28fd07c4a2db004601474b3d83ea7d00435c496bf443cb828af228a83be3`;
its compressed container has 4,858,637 bytes, SHA256
`2074fb6f25423014fd6b0e95cd90ea9c661457cd727b84a4d055cce7e466d3ff`.
All receipt fields are reproduced, not merely inspected. The original fourteen
formula/proof/declaration/checker/notice exports are retained unchanged at input
ancestor `f0a2ca795d9ad0b8cb26b70e75ad5f679ab88094`, with original source
`ca0002008b497428f0b651501c4a220a9d2785e7` and exact Git/SHA pins.

## Reproduce

Use Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/gl3-lrat-independent-check
python3.12 -I -B research/gl3-lrat-independent-check/checker.py research/gl3-lrat-independent-check/source/length7.cnf research/gl3-lrat-independent-check/length7.lrat.gz
```

Both registered normal and optimized warning-strict commands freshly check the
full certificate. They also run 21 separately authored tiny tests: a direct
Boolean-model oracle over 138 formulas and 1,581 candidate empty proofs, 1,034
forged intermediate-clause attacks on satisfiable inputs, nontrivial implication
and sign controls, deletions/stale/future IDs, malformed syntax, gzip/hash and
resource boundaries. This finite calibration is not a proof-kernel theorem.
Expected full typed receipt: `EXPECTED.json`. Local timings are recorded in the
handoff, not promised as portable performance bounds.

## Failed larger conversion and limits

The length-eight conversion was stopped by its 512 MiB output-file limit
(`SIGXFSZ`, exit -25), leaving exactly 536,870,912 incomplete bytes, SHA256
`c3236d89355ede8a7d6d19c1335678f8b78caa69d117a5e7a80c699ab7c9e93f`.
It was not replayed by this interpreter and supplies **no independent
length-eight acceptance**. `GENERATION.json` preserves the bounded result; raw
generation logs and the incomplete trace are session evidence, not advertised
as a certificate. No larger retry or SAT search was run.

Hint generation used the unchanged source C at the retained predecessor pin,
compiled with `cc -std=c99 -O2 -Dgetc_unlocked=getc`, then
`drat-trim CNF SAVED-RUP -U -L OUTPUT-LRAT -t 300`. One process ran at a time,
with CPU 300 s, external wall 420 s, file 512 MiB limits and an 8 GiB disk
reserve. The complete shorter conversion, including exact generator commands,
and failure records are retained in the session handoff. Reproducing conversion
is optional: the published checker needs neither C nor the generator.

The checker deliberately accepts only a strict positive-hint subset. It rejects
RAT hints, tautological additions, malformed or noncanonical integers, dead
deletions and additions after empty. Raw/decompressed streams, lines, variables,
clauses and hints have finite bounds. These are not a hard RSS or runtime
guarantee. Interpreter, standard-library and implementation soundness remain
trust links; no independent human or formal-kernel acceptance is claimed.

The existing support, free-mixing normalization and CNF semantics audits
(PR4214/4223/4230) are credited dependencies, not rerun results. This package does
not assemble a full minimum-nine model theorem, provide physical compiler or
caller costs, admit a supplier or change the selected multiplication frontier.

## Open next questions

1. Budget a separately checked length-eight certificate with a different bounded
   hint/transport plan. Its conversion exceeded the stated limit; raising an
   allocation without a measured plan is not an acceptance result.
2. Assemble the exact model lower-bound dependencies, including normalization,
   support, compiler equivalence, both refutations, padding and the nine-call
   witness. A shorter formula alone cannot close that theorem.
3. Translate this supported subset to a formal proof kernel or formally verify
   its parser/entailment connection. Ordinary Python execution leaves that trust
   boundary open. `TASK.json` records the structured follow-up and stop rules.

## Credit

Brian Ross supplied the conceptual strategy, research direction, oversight,
encodings, original certificates and integration with substantial OpenAI Codex
assistance. Retain Hanson Sun seed18 and Josie Elliston's length10/three-register
lineage, James Reed's prior pin/seal review, and the distinct PR4214/4223/4230/4242
audits. Marijn Heule/Nathan Wetzler's drat-trim retains its MIT notice;
Glucose4/PySAT supplied original proof production. Original source notices and
licenses are unchanged. ToikY used substantial OpenAI Codex assistance for the
new checker, separately authored controls, integration and separate AI review.
LRAT/RUP and elementary entailment are established techniques. New material is
Apache-2.0. Maintainer edits disabled; no merge or frontier change.
