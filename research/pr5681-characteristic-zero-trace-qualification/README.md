# Two source-bound characteristic-zero trace qualifications

Two specific characteristic-zero contracts suggested by [PR5681](https://github.com/CrocSwap/integer-mult-bounds/pull/5681)'s static connector fixture cannot satisfy its retained scalar endpoint. With every query derivative square zero, the necessary trace equation is 0=128. With the verbatim full-stage kernel and full resolutions, the thin derivatives must instead have total trace −120, whereas square-zero thin derivatives have total trace zero. The [proof](PROOF.md) states the exact additional hypotheses and derives each qualification.

This applies a classical trace identity to specified contracts. It does not identify an error or contradiction in the source author's characteristic-two construction. The valid F2 witness is unaffected, and [PR5673](https://github.com/CrocSwap/integer-mult-bounds/pull/5673)'s arbitrary-thin-matrix class is not excluded. No general complex/native/caller exclusion, chronological construction, physical tariff or κ result is claimed. The selected frontier is unchanged.

## Exact source and version provenance

The primary source object is PR5681 head `67f07448eec5ad8d84bdf96b46981ac0b893592f`, package `research/one-sided-connector-audit`. Two unchanged source proofs are supplied locally:

- [PR5681-PROOF.md](inputs/PR5681-PROOF.md), sections 2–3: characteristic-two static square-zero maps, including the 31-leaf fixture with block dimension four and five rank-two thin maps.
- [PR5673-PROOF.md](inputs/PR5673-PROOF.md), section 1: stage kernels, full resolutions, arbitrary thin matrices, independent stage variables and the complete ordered target. PR5681 retains this proof from source commit `c10f75f09e41803ae8efe478331a7509b7379b2f`.

[SOURCES.json](SOURCES.json) records immutable public paths, Git blobs, SHA256 hashes and exact preparation provenance. The two source copies preserve original text and credit. Their scientific execution statements are source-author evidence; no source checker was run here.

The new PROOF.md is a standalone adaptation of the locally frozen, independently reviewed V2 trace tuple. That tuple comprises proof SHA256 `37d13fa8d60115fdf4ff62c89ed2361d7a898aa99ed7f0931cc31d8711149469` and contract SHA256 `65bd829e2b17382029b6d1ee16d248e2116a059e5de47824a8099029789c7b02`. Its separate V2 review has SHA256 `9f168e80009239a6a6de23e82e75e10e698f5779024a88320df2d71236f3c956`. The review accepted the specified conditional paper arguments. It is not an acceptance of these adapted package bytes. The adapted package has a separate review obligation; acceptance of an earlier tuple is not silently transferred to changed bytes.

The original and clarified argument versions retain separate immutable provenance. The source-specific contribution is the two explicit conditional trace budgets; no exhaustive novelty claim follows from source or overlap qualification.

## Evidence and qualification boundary

The argument works over ordinary matrices in the free ring F[e,x₁,…,x₃₁]/(e²), with F of characteristic zero, independent central x_j=D_j+1, and constant query coefficients. The elements 1,e must remain linearly independent over F[x]. Specializing x=0 means D=−1 in characteristic zero. Faithful preservation of that normalized first-order coefficient identity is required before transferring the argument to a physical representation.

Both qualifications concern derivative matrices Q satisfying Q²=0 over F. Automatic (eQ)²=0 and invertibility of I+eQ hold for arbitrary Q and do not supply this hypothesis. Case A may change the full kernel; Case B keeps the verbatim T, for which T²=2T, and assumes no full-query nilpotence. Thin rank two is fixture context rather than a trace-proof premise.

This is an unregistered static proof package. Its explicitly named custom custody manifest is not generic research-runner metadata. No verifier, `TASK.json`, `VERIFY.json`, synthetic `RESULT.json` or CI receipt is supplied. Local source-copy hashes were checked only as packaging bookkeeping against existing authenticated pins. No new source query, numeric or scientific run, source import, matrix/WORD generation, constructor, chronological search or native replay occurred.

## Credit

Credit Ali Romman for PR5681's static construction/audit and the retained PR5673 proof and source bounds; Cinna Davis's controller and simplex lineage; [PR5617](https://github.com/CrocSwap/integer-mult-bounds/pull/5617), [PR5631](https://github.com/CrocSwap/integer-mult-bounds/pull/5631) and [PR5649](https://github.com/CrocSwap/integer-mult-bounds/pull/5649) for the query-frame/fixed-star line; and the complete retained P104/native/helper/compiler lineage. Formulation B was independently identified during review of formulation A. The source's existing caveat that a characteristic-two static witness supplies no native lift remains predecessor work.

The trace identity is classical. No novelty of that identity or source-author contradiction is claimed. Prepared with substantial OpenAI Codex assistance, including separate local AI paper reviews; these are not human scientific acceptance or formal proof-kernel validation. Source notices and Apache-2.0 terms are retained; see [NOTICE](NOTICE).

## Open next questions

1. **Which additional contract could support a characteristic-zero construction?** The exact trace budgets show that either derivative nilpotence, verbatim full-stage structure/resolutions, scalar target/dimension, or the faithful coefficient model must change. First specify one concrete revised contract and derive its necessary coefficient equation. No changed family is nominated here, and its endpoint/native/cost obligations would need separate scope and source review.
2. **Can arbitrary thin derivatives satisfy the full ordered endpoint?** PR5673 permits them, and the verbatim-full-T case only imposes total thin trace −120. That necessary condition is not a construction. A useful first step is a specified source-bound candidate with the exact polynomial endpoint; no synthesis or search is authorized by this note.
3. **Can a physical representation faithfully preserve the normalized coefficient identity?** That is required before either qualification transfers. Begin with an explicit representation and proof of the relevant coefficient binding. A physical first-order shear or invertible I+eQ alone does not prove Q²=0.

The smallest useful follow-up is review of the exact source contracts and paper argument before proposing a revised lift. No new scientific execution is needed to inspect the two paper arguments.
