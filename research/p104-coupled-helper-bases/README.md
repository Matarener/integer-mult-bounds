# Conditional kappa 0.00309980 from coupled helper bases

This construction increases complete conditional kappa from 0.00308189 in
[PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580) to
**0.00309980**, a gain of **0.00001791**. The exact raw crossing is in
(0.00309980120533, 0.00309980120534). The selected record remains
0.003027288235.

Six helper boundary basis changes remove seven paid transports per local
call. Nine coupled handoffs split independent helper channels at common
interior frames. The new word has nine more arbitrary helper inputs and
no added paid transport. The input, cut and output bases isolate each new
channel and restore every main and helper input. All eight owned paths
remain fully charged.

Read [the proof](PROOF.md), [the fixed witness](WITNESS.json),
[the constructor](construct.py), [the complete receipt](RESULT.json),
[the source pins](SOURCES.json) and [the verification record](VALIDATION.md).
The complete bill has **66726 paid jobs and 12976 productive fields**.
This is a changed invoice. Its rank-mass surplus remains 760.

The final overlap refresh found parallel helper splitting in
[PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599), head
`0644592d421b375c221045954fdf13932575ffa8`, with complete claim 0.00309839.
Its author [released the 15 splits for composition](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19183908)
and left the paid-boundary work with this claim. This package credits the
shared mechanism and claims no exclusive discovery of it.

Against that pinned word, the new complete moment improves by exactly
`18 * g(4,5)`, where `g(a,b) = a^(1-k) + b^(1-k) - (a+b)^(1-k)`.
The claimed gain is **0.00000141**. It uses **126 fewer paid calls and
108 fewer productive fields**. The source word is retained for an exact
arbitrary-input and complete-invoice comparison. It is not a constructor
input. A direct composition screen gave the same raw moment with more
fields and calls, so this package retains the smaller complete construction.

The separate commuting-contact result in
[PR #5565](https://github.com/CrocSwap/integer-mult-bounds/pull/5565)
claims 0.00308520. Composition with that scalar-order change is not checked.

## Reproduction

Python 3.12 and the standard library suffice. No solver, network or Git
command is needed by the scientific replay.

```sh
python3.12 -B scripts/research_package.py --package research/p104-coupled-helper-bases
```

Both registered modes must print:

```text
PASS_P104_COUPLED_HELPER_KAPPA_00309980
```

The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. Each replay
reconstructs all 15 changes, checks arbitrary-input endpoints after every
step, checks 565504 dense transpose coefficients, checks 2926 exact native
maps, and replays the complete physical caller. It derives the invoice
three ways, checks two exact moment engines, the full compiler bounds and
all 58 outer predicates, then compares the complete committed receipt.

The negative controls reject a missing input basis operation, a wrong
new-helper coefficient, the old retired exit, an independent input treated
as an owned zero, a false cut witness, a missing central translation, a
wrong native phase, the old invoice at the new claim, the old logarithm
power, the old cutoff and an insufficient BIT contract.

The PR5545 source capsule is unchanged. Its SHA256, export manifest and
all 33 payload files are checked before import. The PR5580 word and price
source and the PR5599 comparison word are checked by SHA256 and Git blob ID. The caller is unchanged.
[VERIFIER-CHANGES.diff](VERIFIER-CHANGES.diff) shows the explicit public
width change and removal of the unused old constructor. It does not change
the endpoint, frame, native-phase or scalar-cost rules. The old and new
checkers must agree on the predecessor word.

[PRICING-CHANGES.diff](PRICING-CHANGES.diff) records the new counts and
claim, plus the logarithm-power increase from 1000 to 1024. This increase
is required to fund the compiler at the new endpoint. The native engines,
both moment engines and outer ledger remain unchanged.

## Limits and ceiling

The five framework assumptions remain: native all-column realization,
owned erasure, uniform compiler closure, precision and fixed-tape execution,
and analytic recovery. The source's free helper endpoint contract remains
inherited. This construction changes helper endpoints and adds independent
helper targets within that contract. No independent human or proof-kernel
acceptance is claimed. The enormous uniform word and a complete rounded
multiplier are not materialized.

The fixed invoice has a strictly decreasing signed moment on [0,0.0034].
Its raw funding ceiling is the crossing interval above. The headroom above
the claimed endpoint is between 1.20533e-9 and 1.20534e-9. This is not a
ceiling for other words, bases, helper inventories or controllers.

The claim concerns the complete P104 caller line. It does not resolve
the additional native-compiler premise in the larger p19 numerical
proposals. A local construction, a complete conditional price and an
accepted integer multiplication theorem are distinct claims.

## Coordination and credit

The branch starts at canonical main
`5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority revision 7.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154639)
reserves the coupled helper basis scope. [TASK.json](TASK.json) records
the overlap checkpoint and exclusions. The final refresh covers 338 open PRs and all Discussion records listed
in TASK.json, with complete remote pagination.
Local note coverage is sparse; this is not an exhaustive novelty claim.

The fixed-contact price floor in
[PR #5590](https://github.com/CrocSwap/integer-mult-bounds/pull/5590)
keeps scalar contacts fixed. This construction changes scalar bases,
independent input expressions and target inventory. The owned recoding
work in [PR #5591](https://github.com/CrocSwap/integer-mult-bounds/pull/5591)
and the native-history, changed-contact and global controller claims
remain separate. The former private-fanout claim changed scope to the
released PR5599 helper-split component and is credited above. No other contributor's files are edited.

- Ali Romman supplied the complete caller and source closure in
  [PR #5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544) and
  [PR #5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545), and
  the consumed contact step in PR #5580 linked above.
- Joel Pulikkan, @GamingPuzzled, supplied the priced helper-706 handoff in
  [PR #5569](https://github.com/CrocSwap/integer-mult-bounds/pull/5569)
  and the successor-handoff method in
  [PR #5472](https://github.com/CrocSwap/integer-mult-bounds/pull/5472).
- @DreamingOfClouds supplied free helper endpoints in
  [PR #5561](https://github.com/CrocSwap/integer-mult-bounds/pull/5561)
  and earlier single-helper handoffs in
  [PR #5553](https://github.com/CrocSwap/integer-mult-bounds/pull/5553).
- @thu-nmrc supplied the coupled contacts in
  [PR #5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551).
- Gareth Davidson supplied the composed P104 word in
  [PR #2305](https://github.com/CrocSwap/integer-mult-bounds/pull/2305).
  David Arias supplied coalescing in
  [PR #2152](https://github.com/CrocSwap/integer-mult-bounds/pull/2152).
  Cinna Davis supplied private reuse in
  [PR #2219](https://github.com/CrocSwap/integer-mult-bounds/pull/2219)
  and the retained controller. Jacob Alan Sussman supplied productive
  recursion. The source notices credit zxv and Cao Yifan for the interval,
  compiler and native framework. The capsule preserves the earlier
  geometry, BIT and analytic notices.

Credit the parallel PR5599 helper-split construction and public composition
handoff. The paid-boundary changes and the cheaper complete construction
are this package's contribution. The elementary scalar basis identity is
not claimed as a new general theorem.

New coupled-basis construction, proof and verification by Ali Romman with
substantial OpenAI Codex assistance. Apache-2.0. The same assistant performed
the search, proof and checks. No subagent or independent reviewer was used.

## Open next questions

Independently review the coupled handoff lemma and its free boundary
operations, then replay the complete price. A further gain needs a changed
word or a compatible composition, with live overlap checked first. The
fixed 15-step witness does not prove optimality of the larger basis class.
Composition with PR #5565 or the active coupled-frame witness needs a new
source-bound construction and full replay. Structured questions are in
[TASK.json](TASK.json).
