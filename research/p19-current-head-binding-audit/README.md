# PR5270's p19 address protocol fails its claimed complete-controller identity

**Exact current-head complete-word counterexample, with reproduced price gates. No new κ or supplier admission.**

Audited [PR #5270](https://github.com/CrocSwap/integer-mult-bounds/pull/5270) at `225a19a184296d12120203a1f43b981d55465241`. Applying its submitted address-loop protocol to its emitted 241-gate p19 trace changes **72 entries** of the complete 38-by-38 controller matrix. With Q=1, D37=i and every other stage eigenvalue 1, input role 36 should contribute zero to output role 0; the submitted protocol contributes **i−1**. This is an exact realizable Gaussian eigencharacter, not a random-state or floating-point discrepancy.

The invoice arithmetic is favorable separately. Adding **2,016 H1 jobs**, while retaining every target, makes its signed moment strictly negative for **every 0<C<1**. This threshold is sharp: 2,015 extra H1 jobs leave a positive moment at some sufficiently small positive C. At C=.0034, only **1,103** extra H1 jobs fit. The discussed 2,128-job and 4,256-job repairs exceed the all-exponent threshold. These statements concern those named fixed bills, not a universal decoder lower bound.

## What the numbers mean

The remembered .0039 BIT result resolves to this PR's proposed **outer κ=.003399996428…**, with inherited admitted BIT **.0034**. It proposes no new BIT construction.

| Quantity at the audited head | Value | Scope |
|---|---:|---|
| Raw complex moment crossing | between .007578535189 and .007578535191 | Exact rational sign enclosure for an optimistic invoice; not an admitted uniform supplier or universal ceiling |
| Tested complex saving | 2380001/700000000 = .003400001428… | The arithmetic tested by `p19_claim.py` |
| Candidate covered uniform complex saving | 4760001/1400000000 = .003400000714… | The saving that compiler instance attempts to cover; actual physical/closure hypotheses remain necessary |
| Inherited ordinary BIT saving | .0034363538396 | Reused source cover/bootstrap arithmetic |
| Inherited admitted BIT saving | 17/5000 = .0034 | Unchanged |
| Proposed outer κ | 951999/280000000 = .003399996428… | Five grid steps below admitted BIT, conditional on the missing supplier |

Canonical main at entry was `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8. Its selected record admits κ=.003125804 under five retained assumptions. Neither the raw .0075785 figure nor a hypothetical .0039 BIT component changes that selected complex-limited result. The proposed endpoint would improve that value by about 8.772% if its new physical obligations were closed; the percentages in PR5270 compare older records.

## Complete-word decoder counterexample

The current emitter stores an IDLE as **literal stage indices**, while the formal `term` converts that list to an indicator vector. The actual address loop runs `for s, bit in enumerate(sel)` and applies block **s** when `bit` is nonzero. It confuses a position with a stage label. The p19 terminal event on pair 17 has `sel=(37,38)`: correct thinning requires D37; the submitted protocol applies D1. All nine retained terminal events of I⁹T⁹ are displaced.

`p19_bank.py` itself fixes p=2, pattern I. This audit instantiates its **unmodified gate-loop AST** on the actual emitted p19 gates with the intended fresh-block map. It does not claim that the original default command runs p19. The default control omits terminal IDLEs, hiding this case.

For the canonical Gaussian,

```text
G = 1/2 [[1+i,1−i],[1−i,1+i]],
G(1,1)=(1,1),     G(1,−1)=i(1,−1).
```

Take the tensor-product character negative on one axis of stage 37 and positive on every other axis, including the shared centre. Its 2^153 conceptual addresses are specified by one character mask. Every ideal address gate preserves this one-dimensional address subspace. A 38-by-38 coefficient calculation therefore computes its complete action without approximating or enumerating the addresses. Coefficient vectors represent independent **input roles**, not truncated address arrays.

The intended authenticated controller and emitted trace are evaluated over exact Gaussian integers. The literal submitted address loop is evaluated over F65537 with i=256. A separate execution with only residue reductions removed recovers the exact Gaussian-integer outputs, agreeing with the residue loop on every entry. In particular i−1 has nonzero residue 255, refuting exact equality.

| Test | Submitted decoder | Literal-stage IDLE repair |
|---|---:|---:|
| p2 I, all 32 physical central/block eigenvalue triples | 0 failures | 0 failures |
| p2 T, same 32 triples | 24 failures | 0 failures |
| p2 T: Q=1, D3=i, others 1 | 4 differing entries | 0 |
| p3 IT: Q=1, D5=i, others 1 | 8 differing entries | 0 |
| p19 I⁹T⁹: Q=1, D37=i, others 1 | 72 differing entries | 0 |

At f=1 the central Gaussian has eigenvalues 1 and i; an eight-axis block has all four fourth roots. Thus the p2 grid has 2·4·4=32 physical triples. The repair is an **in-memory positive control** consuming literal stage labels. Frozen sources are never edited. Unchanged invertible factorization boundaries cannot make two unequal complete controller matrices equal; a changed boundary or caller requires its own proof.

## The ideal lift does not supply the priced native call

A genuine homomorphism for the correctly assigned commuting Gaussian variables preserves polynomial identities. The lifting script's sampled checks neither consume the emitted IDLE tuples nor identify the uncoded ideal shear with the coupled native producer. These are separate bindings.

The PR's pinned historical `PHYSICAL.md` gives

```text
B = diag(D,D) [[I,−Q C],[0,I]],    C_ij=A_ij K_i^-1 K_j.
```

The all-ones uncoded trace requires C=I. All 112 diagonal entries of the pinned A are zero, hence C_jj=0. Put nonzero v in Y_j only, with all other main inputs zero. The inherited native reverse returns X_j=0, while the ideal uncoded reverse returns X_j=−DQv≠0. This local substitution failure holds at every positive width since D and Q are invertible.

This corroborates the existing exact-head review; it does not exclude a newly proved adapter or whole-word cancellation. The signature `invoice(p,pattern,thick,profile)` does not prove that its supplied profile implements an arbitrary desired operator. Removing a coding argument does not turn C into I for free. Correcting IDLE indices alone leaves this native-to-invoice obligation open.

A model control substitutes the source's pre-PR4929 profile `{1:2237,2:388,3:494,4:147,5:36,8:8}` into the same optimistic p19 targets. Its raw crossing lies in (.003004145206,.003004145208), below selected κ=.003125804. This does not construct that alternative caller or exclude other uncoded producers.

## Reproduced fee theorem and its sharpness

[Ali Romman](https://github.com/aliromman) already proves the 2,016 all-exponent bound, with an integer hinge certificate and the same .0034 budget, in the [physical-boundary cost finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19149724). The calculation below independently reproduces that result with the equivalent truncated-mass certificate. The observation that one fewer H1 fee admits a positive moment near t=1 is the elementary continuity sharpness check, not a new general theorem.

Independent enumeration reproduces 12,008 targets and 68,782 paid jobs, with rank masses 265,533 and 263,517. Let T and P be these multisets and define

```text
A_h(u) = sum_{r in P} min(r,u) + h min(1,u) − sum_{r in T} min(r,u).
```

For h=2016, exact integers in `RESULT.json` give A_h≥0 at every rank breakpoint, strictly positive below the largest rank 153 and zero from 153 onward. Between breakpoints A_h is linear; its slope near zero is 58,790. Therefore A_h is nonnegative everywhere and positive on an interval. For 0<t<1,

```text
x^t = t(1−t) integral_0^infinity min(x,u) u^(t−2) du.
```

Integrating proves `sum(P r^t)+2016 > sum(T r^t)` for every such t. Thus every positive saving C=1−t fails after 2,016 or more extra H1 jobs. At h=2015 the target-minus-paid moment is 1 at t=1, so continuity makes it positive for some t<1 sufficiently close to 1. This proves sharpness, extending the earlier endpoint rank-mass screen to the whole exponent interval.

At C=.0034, exact interval arithmetic bounds the unfunded surplus strictly between 1103 and 1104. A separate 90-digit Decimal sum gives approximately **1103.2761222689533**. This is the integer H1 budget at that saving, distinct from the all-exponent threshold 2,016.

The earlier 2,128-H1 repair loses even if every original target remains credited. Losing a central target rank only worsens that bill; 2,128 H2 jobs cost at least as much for 0<t<1; the 4,256-H1 full-R-letter repair also loses. These implications price named additive bills and do not establish that every possible physical repair costs that much.

## Relation to previous and later work

[ahrazzle](https://github.com/ahrazzle)'s [PR #5349](https://github.com/CrocSwap/integer-mult-bounds/pull/5349) and [PR #5385](https://github.com/CrocSwap/integer-mult-bounds/pull/5385) audit and repair the older hand-transcribed reference. The current head replaces it with an emitted trace. This audit does not transfer the old three transcription failures to that revised emitter.

[Chris R](https://github.com/Clear1nsight)'s [exact-head handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/5270#issuecomment-6378014056) already identifies the local IDLE mismatch and zero-diagonal native witness. The new contribution is the **complete-word** literal-decoder check, p19 pulse output and controls, plus independent reproduction of the **prior all-exponent fee bound**. [Matarener](https://github.com/Matarener)'s [terminal-gauge review](https://github.com/CrocSwap/integer-mult-bounds/pull/5270#issuecomment-6374430946) supplies the earlier repair charges and budget observations. [James Reed](https://github.com/jwr404)'s compiler review and [zxv](https://github.com/zxv)'s geometry review retain their separate credit.

The central ledger leaves [PR #5440](https://github.com/CrocSwap/integer-mult-bounds/pull/5440), head `c0f52b5b18bba78a6a5e8057edf9571bade88549`, open over its full-R/D binding and missing charges. It is a different coded word, not replayed here; the tuple counterexample is not automatically transferred to it.

[PR #5027](https://github.com/CrocSwap/integer-mult-bounds/pull/5027) already provides conditional p19 compiler arithmetic. [PR #5069](https://github.com/CrocSwap/integer-mult-bounds/pull/5069) provides a priced physical pair, and [PR #5563](https://github.com/CrocSwap/integer-mult-bounds/pull/5563) provides paid central-Q decoders with losing complete bills. They retain constructive alternatives and the distinction between a correct paid repair and a profitable supplier. Their full replays are not repeated.

## Reproduction and verification limits

```sh
python3.12 -I -B research/p19-current-head-binding-audit/verify.py
python3.12 -I -O -B research/p19-current-head-binding-audit/verify.py
python3.12 -B scripts/research_package.py --package research/p19-current-head-binding-audit
```

The default verifier is read-only and compares a freshly calculated mathematical receipt. `--write` explicitly regenerates it. Small exact exports from the unmerged head retain their paths, commit/blob IDs and SHA256 values in `SOURCE_EXPORTS.json`. Canonical inputs and historical guidance are pinned in `SOURCES.json`. No external PR-head availability is required for replay; exports are retained evidence, not edits to the predecessor.

`VALIDATION.json` separates fresh normal/optimized scoped checks, author arithmetic runs, source-corruption controls and original bank runs. The original one-dense-seed p2 pattern-I bank control passes freshly in CPython 3.12 in 131.23 seconds under the 360-second/1-GiB guard (203120 KiB peak sampled descendant RSS). An earlier CPython 3.11 attempt timed out at 180 seconds; both outcomes are preserved separately. A timeout is not a pass. The optional full source-history preflight is unavailable in this shallow checkout; metadata/pins and exact committed bytes pass. No full p19 Laurent factorization, native archive replay, enormous address enumeration, Lean, Docker, machine compiler, precision/tape/stock closure or analytic recovery theorem is newly verified. The selected five assumptions remain unchanged. The selected-baseline helper could not authenticate its full certificate closure in the intentionally sparse checkout; selected values were instead read directly from the pinned Git record, certificate and maintainer review.

## Significance for researchers

The favorable raw price survives arithmetic checks, while its asserted implementation bridge fails on an exact complete-word input. This identifies the useful next task: an actual compatible physical caller with every correction and target change charged. The independently reproduced fee certificate supplies an early stopping test for this fixed invoice. Its all-exponent force was already established in the credited boundary-budget finding; this package adds a different exact certificate and the elementary sharpness control.

## Open next questions

The structured questions in `TASK.json` concern a physical producer/adapter for the uncoded trace and a changed current-query/terminal contract meeting the complete budget. Start with arbitrary owner inputs and the exact causal source version. The IDLE patch is a control, not a profitable construction. A changed profile, reused query, joint target or different operator is outside the fixed-fee theorem and needs its own source-bound bill.

## Credit and assistance

Prepared for [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance in mathematics, implementation, verification and writing. One worker, no subagents. Retained source credit: [DaysSky](https://github.com/DaysSky); [Seth Burkart](https://github.com/SethBurkart123), as credited in [PR #4940](https://github.com/CrocSwap/integer-mult-bounds/pull/4940); [Dillon Amburgey](https://github.com/dillona), [PR #4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933); [David Ganz](https://github.com/Dugongue), [PR #4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929); [Cinna Davis](https://github.com/1337isnot1337), [Cao Yifan](https://github.com/intqwq), and their retained native, helper, Clifford, compiler, BIT and analytic predecessors. Original source notices remain intact. New work is Apache-2.0; no independent human or proof-kernel acceptance is implied.
