# Lossless scalar free-mixing normalization: independent model audit

This audits the original normalization implication in Brian Ross's PR4211, pinned at **ca0002008b497428f0b651501c4a220a9d2785e7**, and the named remaining obligation in PR4214. The predecessor already gives the normalization argument and 28-projector census. This adds a constructive independently frozen converter, all-length proof, full noncommuting tests, explicit converse bases and a separate binding to the actual source alphabet. It is not a new normalization method or minimum-nine recertification.

## Exact scope

For every finite n and r>=1 over F2[G], with arbitrary group G, allow fixed invertible binary scalar register maps W0,...,Wn interspersed with n paid coordinate address operations Cj. Define Pj=Wj...W0. The exact raw operator equals

```
Pn * Fn * ... * F1,    Fj=P(j-1)^(-1) Cj P(j-1).
```

Each Fj=I+([gj]+[e])uvT with vTu=1. A target with augmentationI, including the source's diagonal group-monomial target, forces Pn=I. Every normalized rank-one-idempotent word conversely has an explicit raw realization using precisely n paid calls and unchanged chronological addresses. Arbitrary nonidentity augmentation retains the residual Pn; it cannot be discarded. The n=0/r=1 cases are explicit. Equality of full group-algebra matrices covers arbitrary dirty input registers, without restricting initial vectors. Adaptive/nonlinear/address-dependent free maps are excluded.

PROOF.md gives the universal argument. Its independently written free-associative F2 interpreter retains complete parity polynomials in noncommuting words. All504 conjugacies of168 scalarGL3 frames and28 projectors/converse bases are retained; these scalar frames are not an address-group census. Finite cases corroborate the proof, not replace its quantifiers. Ten controls include wrong inverse order at a noninvolutory frame, reordered calls/factors, dropped residuals and invalid contracts.

The core retains672 raw and196 converse symbolic cases,25 positive checks and10 negative controls. Source integration compares504 complete conjugacy rows and504 converse witnesses, binds64 selector assignments to28 projectors/168 paid factors, and checks168 one-factor raw converses. Its five countercontrols expose inverse replacement, opposite conjugacy, dropped residual, scalar/address confusion and reversed calls. These are constructed diagnostics, not defects found in the predecessor.

The separate adapter intentionally reuses authenticated unchanged predecessor modules. It binds the independent table to the actual normalized paid alphabet and the direct-nine positive endpoint in the full168-basis address group algebra. The raw scalar interleaver is adapter-owned: the predecessor implements normalized paid steps only. Generic oracle identity-address diagnostics test the broader algebraic implementation; identity is not an extra label in the actual six-CNOT source alphabet. None of this certifies every emitted CNF transition, endpoint or Tseitin clause, any SAT/RUP proof, or the minimum-nine lower bound.

## Reproduction and frozen evidence

Python3.12, stdlib only, four registered normal/optimized commands:

```sh
python3.12 -B scripts/research_package.py --package research/gl3-free-mixing-normalization
```

Oracle core/proof/fulltable/selftest were frozen before predecessor/source access at18:58:58UTC. Their original receipt records the initial3.9.6 environment; the registered package is separately replayed under3.12. Default commands write no files. Source pins, unchanged NOTICE/license, byte-preserving attributes and the public input ancestor preserve original source containers. PACKAGE-REVIEW seals the exact final files; complete replay payloads and package immutability are checked again cold and in hostedCI.

## Open next questions

The smallest useful next task is an unclaimed proof of actual full CNF transition/boundary/Tseitin equivalence at the frozen generator, followed by separately budgeted another-platform RUP replay. The model lower bound still needs those links and explicit padding/lower-length admission. Physical compiler/caller/invoice, supplier/native outer theorem and changed models are separate. No new kappa, frontier change or merge. Written/mechanical AI-assisted checks are not independent-human or formal-kernel acceptance.

## Sources and credit

Brian Ross supplied the conceptual strategy, direction, oversight and original normalization argument, with substantial OpenAI Codex assistance. Retain Hanson Sun's seed18 and Josie Elliston's length10/three-register lineage, all original NOTICE/license text, James Reed's earlier finite pin/seal audit and PR4214's separate support-cone audit. Classical conjugation and augmentation are not new general mathematics. ToikY used substantial OpenAI Codex assistance for the independently frozen core, source-reusing adapter and separate proof/code review. Apache-2.0.
