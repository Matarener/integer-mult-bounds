# The fixed #4467 leaf deficit saturates, uniformly across lockstep levels

This package proves the saturation predicted by Ryanson Jonathan / pinterbanget's [#4467](https://github.com/CrocSwap/integer-mult-bounds/pull/4467). For its fixed raw-p7 paid-rank law, the conditional deficit `B_G−S_G` converges to `Exp(λ)`, **including convergence of the mean**, uniformly for `B_G=G log5+δ`, `0≤δ<log5`. The actual source has **G conditioned paid ranks plus one unconditioned terminal rank**.

The exact rational certificate encloses `λ ∈ [0.00749912850515, 0.00749912850519]`, limiting mean deficit in `[133.34882837,133.34882838]`, and limiting actual leaf log-depth in **`[136.51870330,136.51870331]`**. The added value over #4467's numerical conjecture is the proof, bounded-offset uniformity and certified numerical hypotheses.

This resolves the qualitative leaf-saturation question. It supplies **no explicit finite-depth error rate**, stable-share theorem, full-flow log-gap limit, numerical refined-induction ceiling, new κ or supplier admission. The raw-p7 profile is historical; the selected #6030 record and its five assumptions are unchanged. The predecessor's estimated `.0025–.0026` ceiling and astronomical finite-rank thresholds remain unproved here.

## Start here

| Reader's goal | Read or run |
| --- | --- |
| Understand the theorem and source law | [PROOF.md §§1–2](PROOF.md#1-source-law-and-statement), then §§3–5 for the argument. |
| Reproduce the finite checks | The command below; [VERIFY.json](VERIFY.json) declares all four checks and five predecessor inputs. |
| Find the evidence for current code | [VALIDATION.md: current evidence index](VALIDATION.md#current-evidence-index), including source hashes, log links and historical/current distinctions. |
| Assess objections and independence | [REVIEW.md](REVIEW.md): current verdict, all six Claude findings and resolutions, shared dependencies, then review history. |
| Continue the research | [Open next questions](#open-next-questions); [TASK.json](TASK.json) retains the original card, actual scope and structured questions. |

From the repository root, using **Python 3.12** and the standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-leaf-saturation
```

This runs all four registered checks serially; the recorded run took about **75 seconds**. It verifies finite numerical/source evidence, not the analytic theorem. [VALIDATION.md](VALIDATION.md#reproduction-and-evidence-reuse) gives Git-free commands, optimized-mode receipts and when evidence must be rerun. The [contribution PR is #6118](https://github.com/CrocSwap/integer-mult-bounds/pull/6118); consult it for live review and CI status.

## What supports each claim

| Claim | Supporting evidence | Limit |
| --- | --- | --- |
| Conditional distribution and mean converge uniformly over offsets | [Written proof](PROOF.md), using Stone's interval local-limit theorem and a uniform expectation-tail bound | Classical theorem is an external dependency; no effective finite-G rate. |
| Root, tilt and limiting mean lie in the stated intervals | [verify.py](verify.py) and [RESULT.json](RESULT.json), using exact rational enclosures | Certifies this fixed source law, not a new supplier or multiplication bound. |
| The source emits G conditioned ranks and an unconditioned terminal rank | All-G source reading in [PROOF.md §2](PROOF.md#2-why-this-is-the-sources-measure); eight primary and ten independent complete-histogram fixtures against #4467 and #4436 | Fixtures overlap and stop at G=3; they corroborate the derivation rather than exhaust all G. |
| Specified source faults are rejected | [test_controls.py](test_controls.py): changed-byte checks plus re-pinned empty/truncated #4467 branches and an altered #4436 returned histogram, normal and optimized | Semantic rejection comes from the actual histogram comparisons; terminal-cut flags describe fixture sensitivity only. |
| Numerical enclosures contain independent bounds on the executed domain | [test_enclosures.py](test_enclosures.py): 16 log and 127 exp arguments; three targeted remainder faults rejected | Finite captured domain; shared exact arithmetic and exponential series, not all-input formal verification. |

The numerical certificate uses a 48-term `2 atanh(z)` series with a geometric tail for logarithms, and an 80-term exponential series with the Lagrange majorant `3^5` on `[0,5]`. The independent checker uses a different logarithm series and a geometric exponential-tail bound. Root isolation uses endpoint signs and a derivative lower bound; tilt uniqueness uses positive variance. Decimals are rounded outward; no predecessor floating-point root finder or data fit supplies the certificate. A lattice countermodel demonstrates the need for nonlattice support; the certificate also checks positive drift and rejects invalid interval-operation inputs.

## Sources and coordination

Scientific base: `721c03822c421b7f7fcbb2598993b947c4d88419`; priority revision 8. #4467's frozen source head is `5f5c1f98c62b9ce4f3db6c0ca47a850a0be577dc`. Its [completed investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19111052) and [request for a saturation proof](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19111508) are predecessor coordination references. The canonical coordination record is [#1166 comment 19240402](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19240402). [SOURCES.json](SOURCES.json) pins every live predecessor input to the base; no unmerged source history is needed.

The original direct flow is zxv's #4436 (`56003680aee2871773de408e5f01cc5dd46b144c`); the refined induction is Cinna Davis / 1337isnot1337's #4405; the lockstep construction is Jacob Alan Sussman's Theorem 1G. #4467, following #4465, already conjectured saturation and measured it numerically. The added value here is the proof, bounded-offset uniformity, certified hypotheses, and explicit separation of the leaf result from the whole-flow extrapolations.

## Open next questions

1. **Give a certified finite-G error bound.** Start by obtaining an effective interval local-limit estimate for this fixed tilted log-rank law, then combine it with the weighted-tail decomposition in PROOF.md §4. A useful result would give explicit constants and an onset for the conditional mean error, uniformly over the level offset. The present proof's concentration constant and onset are existential. Stone's stronger nonlattice refinements extend the allowed box sizes, but still provide no quantified remainder; their failure for finite support does not explain the missing error rate. Reuse the pinned law, tilt enclosure and tail decomposition, but review and certify any new quantitative estimates.
2. **Analyze the other flow components and the exact induction ratio.** Start from #4436's source and boundary sums at the same bounded level offset, retaining all terms. A useful first result would be a source-bound formula or bound for one component's normalized potential contribution, with any offset dependence explicit. Stable shares and the exact-ratio asymptotic remain blockers to a whole-flow ceiling; the leaf limit alone supplies neither. Reuse the source pins and leaf identity, not the predecessor's heuristic total ceiling.

Related pending work by Nick Petalas: [#6125](https://github.com/CrocSwap/integer-mult-bounds/pull/6125) (`f58e29052a0bbb4e123ea777b5e03321fde6f31f`) extends this framework to three power-tariff regimes; [#6128](https://github.com/CrocSwap/integer-mult-bounds/pull/6128) (`9be0bd96279cd66098a9d536ffd0092fd771550a`) reports an explicit finite-depth tail envelope and clipping bound. Both cite our `6310550e` scientific snapshot. These descriptions were checked, but their proofs and certificates were not audited here. A continuation should assess that work before duplicating it; a decreasing convergence-error estimate remains open in both descriptions.

Structured questions are in [TASK.json](TASK.json). A wider construction search needs a separate justification under the repository's family-expansion gate.

Prepared for DLamdata with substantial OpenAI Codex (GPT-6 Astra) assistance, including separate agents for independent mathematical/source checks and skeptical review. Claude Code (Opus 5.5) reviewed the initial published snapshot; [REVIEW.md](REVIEW.md) records its findings and the response. These are AI reviews, not human or formal verification or maintainer acceptance. Predecessor credit and Apache-2.0 licensing are retained.
