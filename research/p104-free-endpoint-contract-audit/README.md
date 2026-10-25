# Free helper endpoints of #5561 under the audited P104 endpoint contract

**Result (scoped audit, no new κ).** The "free helper start and final frames" hypothesis (c) of
[#5561](https://github.com/CrocSwap/integer-mult-bounds/pull/5561) is the general helper-endpoint
contract that the unmodified P104 `local.py` already implements. Chris R's independent caller audit
[#5550](https://github.com/CrocSwap/integer-mult-bounds/pull/5550) checked that contract on the
[#5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545) word. The same checker passes on
both #5561 words when only the word and its invoice are swapped in.

Base: canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`. Audited source: #5561 head
`452d27dde67ee9f772dbbd3be129db97a8ecb9c1`. The words are byte copies in `inputs/` (SHA-256 in SOURCES.json).

## What is checked

| Check | Result |
|---|---|
| #5545 word (audited by #5550) | 192 of 527 helpers start at a nonzero frame (dims 1, 4, 5); 65 end below FULL; 40 distinct endpoint pairs |
| Positive control | The patched #5550 checker on the #5545 word and invoice reproduces #5550's complete frozen output, SHA-256 `b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009`, byte for byte |
| #5561 headline word | PASS: 527 helper endpoints, 272 exact signed-Pauli and phase-anchor checks, invoice 66,852 paid / 12,814 productive, ordinary passes 124,232,680 ≤ 184,647,552 |
| #5561 starts-only word | PASS: 278 exact checks, invoice 67,374 / 12,814, ordinary passes 124,754,680 ≤ 184,647,552 |
| Negative controls | Changed helper endpoint rejected; changed invoice rejected; all ten #5550 controls reject on each word |

For comparison, the #5561 headline word has fewer nonzero helper starts (58) than the already audited #5545 word (192).
Its 44 below-FULL finals are also fewer than #5545's 65. The starts-only word has 59 and 65.

## Why this is the existing contract

`native()` in `research/p104-productive-controller/local.py` credits each helper with the rank of
`chart(initial)⁻¹·chart(final)` for any nested pair of frames. It also charges two normalizers per helper as
ordinary routes. #5550 ([PROOF.md](../p104-caller-independent-audit/PROOF.md), "Helpers, scratch and
paid jobs") makes the mechanism explicit. Each endpoint lowers to U = M_left·G_r·M_right. M_right⁻¹ acts on the
fresh helper input before its LOCAL call and M_left⁻¹ after it. This relies on the local all-input ABI, which
`replay()` checks row by row. A helper from E to B therefore delivers the native Gaussian G_r, with
r = dim B − dim E, on an arbitrary fresh input. Only r is credited. Starting higher lowers the credited rank by
exactly the climb it removes.

The same wrapper mechanism appears in the T74 lineage. Entering helpers use paid residual wrappers
R_E⁻¹/L_E⁻¹ (#458, Lemma A in `hpe_emit_local.py`). Hyperplane-ended helpers use pair wrappers R_(E,U), L_(E,U)
([review](../../docs/research/community-hyperplane599-review.md)). The canonical start rule cited in #5561 belongs to the
#4610/#5413 neutral caller, whose helper adapters J are pure coordinate permutations. It is not a
predicate of the P104 contract. [PROOF.md](PROOF.md) gives the argument.

## What the verifier changes

`verify.py` copies the authenticated #5550 capsule to a temporary directory. It then replaces exactly four literal lines of
its checker, each of which must occur once:

1. Read the word from the given path, not the pinned #5545 word.
2. Take the expected helper profile as a parameter, not the #5545 literal.
3. Take the invoice from `inputs/INVOICE.json`, a byte extract of #5561's `RESULT.json`. The checker
   recounts paid MOVEs and native target ranks and requires equality.
4. Recompute `local_routes` from the MOVE count with the source formula (paid + 2·527 + 208 + 4·104 + 4·8)·1000.

The canonical capsule is never edited. The positive control shows the four changes are faithful.

## Reproduce

Python 3.12+, standard library only:

```sh
python3 -B research/p104-free-endpoint-contract-audit/verify.py
```

The run takes about three minutes and should end with the marker `PASS_P104_FREE_ENDPOINT_CONTRACT_AUDIT`. `RESULT.json` holds the complete result.

## Scope and limits

This addresses only hypothesis (c) of #5561, and therefore also the mid-frame start hypothesis of
[#5553](https://github.com/CrocSwap/integer-mult-bounds/pull/5553). It does not check the retime
legality (#5561's own `retime.py`), the pricing or strictification, the outer conjunction, or the
validity of the #5551 parent word. Those checks belong to #5561's verifier and the pending #5551 admission.
The certified endpoints of the source are its checker constants KAPPA = .00308142 (headline) and
.003076879 (starts-only), as noted in the intake record. Inherited local all-input native semantics,
the five framework assumptions and maintainer acceptance remain. This is an agent check, not human
or proof-kernel acceptance.

## Open next questions

- Admission of the #5551 parent word, on which #5561 and #5553 build (pending, with #5548/#5550/#5557 support).
- Correction of #5561's claim lines to its certified endpoints .00308142 and .003076879.
- A deterministic generator for the #5561 retime, so that a checker is not the only reproduction route.

## Credit

Chris R / Clear1nsight (#5550 checker, used unchanged except the four input lines). DreamingOfClouds
(#5561, #5553). thu-nmrc (#5551). Ali Romman (#5544/#5545 and the P104 caller). chafreaky (#458
wrappers). The P104 lineage (#2305, #2152, #2219) and all retained native, Clifford, compiler and analytic
contributors are credited in the cited packages. This package was prepared for Matarener with Claude (Anthropic), via
Claude Code. Apache-2.0.
