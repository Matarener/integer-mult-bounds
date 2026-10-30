# Seven prime classes for the complete retuned scalar selector

For the retained original-width selector with profile `(1,577,64,42,269241600)`, the complete scalar fit decision has exactly **seven possible cutoff values**, each attained by a certified prime `q>2^80`:

| Class m | Complete selector fits exactly for |
| ---: | ---: |
| 1 | e ≥ 311299 |
| 2 | e ≥ 311301 |
| 3 | e ≥ 311303 |
| 4 | e ≥ 311305 |
| 5 | e ≥ 311307 |
| 6 | e ≥ 311309 |
| 7 | e ≥ 311311 |

The written [proof](PROOF.md) covers **every integer original width e≥1 and every prime q>2^80**, under the explicit scalar abstraction of the inherited Count operations. It includes both the strict borrowing test and the body-size guard, all lower-width rejections and the infinite tail across every later ceiling/depth jump. It does not infer monotonicity from a finite search.

Define `R=269241600`, `P(q)=product(i=1..64,1-q^-i)` and `m(q)=ceil(log_q(R^19 P(q)^19))`. Then `1≤m(q)≤7` and the exact cutoff is `311297+2m(q)`. PROOF.md gives equivalent strict-lower/weak-upper **integer polynomial comparisons**, so the statement needs no floating-point logarithm. Its seven prime witnesses are `q=h*2^n+1`, with exact modular half-power certificates and an elementary prime-divisor order proof. These are primality certificates, not probable-prime tests.

## What is new, and what is credited

Aakash (@aakashthakkar), with substantial OpenAI Codex assistance, already proved the **uniform311311 strict borrowing cutoff at the older17/10000 coupling** in `research/bit2234-stock-threshold/README.md`. That predecessor supplies the depth staircase, uniform bound, proof method and selected-prime witness; all receive explicit credit. This package does not claim that uniform constant or selected prime as new.

The new result classifies the **complete retuned selector across all permitted primes and all original widths**, including the body guard, all smaller-width rejection and all seven attainable prime classes. The production prime `213*2^80+1` is class7. Its retuned full scalar fit decision is therefore exactly `e≥311311`; no selected exponent or frontier changes.

This takes one narrow source-fit premise of the [PR4332 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19094382). PR4338/4340 cover conservative B2 fit arithmetic. Their checks do not derive this complete selector classification. The broader tau and beta source obligations remain open.

## Source binding and replay evidence

All12 inputs are exact current-main bytes at `12fa8c5c844be21bfefb38a19503fbd867a11244`. The retained backend archive has36 regular members, all read and authenticated against its35-file manifest. Its encoded/ordinary members match the actual canonical files. The archive is an uncompressed tar despite its `.tar.gz` filename; format is detected without altering the frozen bytes.

`binding.py` imports no predecessor executable. It checks11 binding inputs,9 whole Python-module ASTs,12 complete declaration contracts, source-specific loop invariants, original-width dispatch and the literal guards. Its16 AST mutations bypass the byte-pin gate and reject at the intended declaration contract. These are **version/control-flow binding controls**; they do not execute mutated native programs or independently prove Count arithmetic.

`engine.py` builds exact depth intervals, stock-log correction certificates, seven prime witnesses and threshold seams. Its21 behavioral scalar controls distinguish weakening strictness, omitting the row factor and computing depth from a reduced width. Rejected bounded prime-search candidates are retained, not treated as proofs of compositeness.

`oracle.py` is a separate bottom-up implementation: it checks **7,340,032 complete decisions**, all1,048,576 original widths through2^20 for all seven prime witnesses. It independently checks the modular certificates and agrees on every depth boundary and full fit/fallback decision. The two arithmetic implementations share the elementary stock inequality and source specification; their distinct coverage is complete width enumeration versus primary interval/end-point certificates. The universal quantifiers rest on PROOF.md, not this finite census.

`verify.py` regenerates and compares the **complete typed binding, primary and oracle payloads**, including the search traces and branch runs. Stdout gives canonical SHA256 commitments to all three. It also rejects a forged prime certificate and three altered stored-evidence records, preserving integer/Boolean distinctions. `VERIFY.json` registers isolated Python3.12 normal and optimized runs, warnings as errors and bytecode disabled, with no dependencies. No producer, active loader, native factory or GL64 catalogue runs.

## Scope and remaining obligations

**Established here:** a scoped mathematical proof of the conditional scalar selector decision, source-specific control-flow binding, exact prime-class witnesses and independent finite arithmetic evidence.

**Inherited or UNKNOWN:** correctness and lifetime semantics of Count/Counter primitives, active source/cohort execution, all-q denominator/chart hypotheses of the native factory, SOURCE/history/restoration, physical time/space/stock/cleanup, complete tau or beta invoices, and the multiplication join. A scalar body fitting does not certify the body payload. No human or proof-kernel acceptance is claimed.

## Open next questions

1. Do the inherited Count/Counter operations implement this scalar abstraction at the actual tape boundary? Pin one complete arithmetic/lifetime contract and its caller, then verify it with source-sensitive rejection controls. Successful native execution and resource/cleanup accounting remain the blockers.
2. Which additional denominator/chart/source conditions restrict native realization of the seven prime classes? Start from the exact production factory predicates and one proposed prime; this scalar theorem does not prove those hypotheses.
3. Can the remaining tau and full-support beta source obligations close the multiplication join? Choose one actual history/restoration or invoice implication from the4332 handoff. This package closes only the scalar selector decision.

## Credit

Aakash (@aakashthakkar)/Codex supplied the earlier stock-threshold theorem. Jose Manuel (@jmbarrancoml) supplied the PR2234 reserve/borrowing definitions, PR2899 ordinary backend and PR3562/3599 coupling; Nick Petalas supplied PR2808 and related ordinary/stock work. The retained archive preserves the selected PR589/555 word, alephnan1627, eumemic GL framework, source527 and routing/parking lineage, including Josie Elliston, Adam Gall, ToikY and Sricharan Vagvala. Ryanson Jonathan (pinterbanget)/PR4332/4340 and Ross Richardson/PR4338 retains credit for their arithmetic checks and handoff. New work by ToikY with substantial OpenAI Codex assistance and separate implementation/proof/review contexts; these are AI contexts, not independent human acceptance.
