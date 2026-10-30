# Earlier P104 answers need a different delivery protocol to save these centre charges

This combined contribution retains two exact source-bound results on [PR5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718), head `a1534ac45401c9a9c80c07aa65c89e00e33594f8`. No new κ, selected-frontier change or general P104 lower bound is claimed.

## Results and reading order

1. [Versioned query maps and separate delivery](../p104-cross-call-paid-reuse/README.md): extracts all 3,426 internal paid outputs at each of actual caller events 0 and 3, with different independent-helper namespaces. Exact certificates reject separately canonically delivered replacements for eight rank-seven centre queries, even granting old-call answers, main information and retention/cleanup free. The pure-main adjacent rank-one query cannot save its charge under its stated cache-delivery model.
2. [Shared gathering](README.md): for **one** of those centres, caller event 3/local 13660, allows preaggregation within 465 source coframes and one common gather frame followed by one final delivery. All 1,211 earlier paid outputs and 1,090 pinned candidate frames are covered. Only 478 frames occur before the cut; the other 612 are granted as an optimistic exclusion. Every protocol in this class costs at least H7 before ordinary and cleanup costs.

The eight-centre theorem must not be inferred for shared gathering: that extension is proved only for local 13660. Matrix-valued recombination, new frames, multilevel transport and changed consumers are outside these results. An absent scalar dependency and an unaffordable physical delivery are different conclusions; the supplied controls explicitly exercise scalar reconstruction.

## Reproduction

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-cross-call-paid-reuse
python3.12 -B scripts/research_package.py --package research/p104-shared-frame-gather
```

The first registration rederives maps, quotients, native phases and the complete invoice. The second rederives gather certificates and runs a separate certificate auditor. Normal and optimized commands are explicit. The added publication check compares every retained runtime input, the versioned maps and predecessor code byte-for-byte across the packages; frozen source and result bytes are unchanged. It is part of the second registered replay. See [publication validation](PUBLICATION-VALIDATION.md) for this assembly's actual runs.

The original README, TASK and validation records describe their historical local-only research sessions; their dates and publication statements are retained as provenance. This overview describes the combined submission. Earlier local-only investigations are context, not required external runtime dependencies. The combined packages include all consumed bytes and notices. The selected conditional κ at canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a` is .00310045; the source's archive merge does not admit its .00311024570 claim.

## Significance for researchers

Complete scalar information can coexist with a missing fresh-helper direction or an unaffordable native delivery. The maps and exact cost certificates let subsequent work test that distinction without repeating a duplicate-query census. The unchanged complete source invoice is 66,348 paid jobs and 12,976 productive fields; neither package earns a deletion or new productive target.

## Open next questions

A new construction must name a changed native combination, multilevel gather, frame catalogue or terminal consumer and price every ingress plus final delivery and cleanup. Start with a concrete source-bound contract and optimistic full bill. No surviving construction or positive forecast is supplied. Do not extend the closed separate-cache or canonical one-frame census solely by adding more coefficients.

Credit [flyingviper](https://github.com/flyingviper), [Ali Romman](https://github.com/aliromman), the native/controller/compiler and analytic authors retained in both `inputs/NOTICE5718` files, and the predecessor [G20 reconstruction](https://github.com/CrocSwap/integer-mult-bounds/pull/5647). Prepared for [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance. Apache-2.0. Exact finite/source-bound checks are not formal-kernel or independent human acceptance of the complete multiplication theorem.
