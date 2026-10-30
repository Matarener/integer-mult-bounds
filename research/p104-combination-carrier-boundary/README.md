# Combination carriers cannot repair the PR6030 helper splits

**Scoped exact certificate and written information-loss proof; no new κ.**
This answers open question 1 of JosieElliston's [PR6045](https://github.com/CrocSwap/integer-mult-bounds/pull/6045):
combinations can carry the retired-helper defect even when no individual field
can. Exactly **2 of its 4,033 leak classes** have such a combination on the
uncorrected split word. Both use `field_778 - field_572` at chart 595, immediately
after cuts 13637 and 13639. A closed residual-line/output-span invariant proves
that even these cannot support a successful finite program of combination-carrier
updates. **All 4,033 classes are excluded for that enlarged correction class.**
Indices are zero based.

| Classes | New result |
| ---: | --- |
| 4,009 | A global information-loss certificate rules out every post-cut repair using only the available scalar state. |
| 22 | Information survives globally, but no chart-local combination carrier occurs at any later original event. General multi-step corrections remain open. |
| 2 | A same-chart retained copy supplies a combination carrier. A dynamic invariant proves every finite combination-carrier program that clears the outside leak also erases the new helper from all public outputs. |

The source word is DreamingOfClouds' selected PR6030 word, SHA256
`7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`.
Base is canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision
8, selected κ=0.003125804. The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19233068)
was posted before substantial computation.

## Method and decision changed

Write the prefix state as `RX`, overwrite helper p by independent z, and let
`M=SR` be the original final public map. The exact test
`R M^{-1} S e_p = e_p` identifies a lost original-input direction. Two original
inputs then give the same overwritten state but different required outside
outputs. This both excludes every later combination carrier and proves the
stronger repair obstruction for the 4,009 passing classes.

For the remaining 24, propagate the small residual `R M^{-1} S e_p - e_p`.
Only charts meeting its support can contain a carrier; only touched charts
need their exact left kernel recomputed. The resulting 196 eliminations and
1,814 class/chart checks replace the predecessor's unfinished repeated rank
scan. [PROOF.md](PROOF.md) gives the theorem, coverage argument, positive
witnesses and the dynamic correction obstruction.

This closes the uncorrected-word combination-carrier question on the selected
word and reduces general post-cut repair work to 24 explicit residual cases.
It closes carrier-based corrections even with dynamically created combination
sources, but does not close arbitrary non-carrier edits in those cases. The global
obstruction assumes an unchanged prefix and no external copy of the retired
input. Re-encoding before the cut is a different problem.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3 -I -W error -B research/p104-combination-carrier-boundary/verify.py
python3 -I -W error -O -B research/p104-combination-carrier-boundary/verify.py
python3 -B scripts/research_package.py --package research/p104-combination-carrier-boundary
```

Both registered modes have a 120-second limit. Direct execution is read-only,
uses no Git or network, and prints all 24 residual cases, the two carriers,
the dynamic projection/span certificate and outside minor, control counts and `PASS_P104_COMBINATION_CARRIER_BOUNDARY`.
The full information-test transcript digest is
`d4a1ba5ddfc72cdc34425f3849b2a00128fad3833ef8c6ab04a905181c8e748c`.

The verifier reuses the authenticated, unmodified PR6040 class census retained
in PR6045. It does not rerun or import PR6045's correction engine. The new
state/suffix replay and algebraic controls are separate implementations.
`controls.py` compares 4,410 decoding cases and 3,780 endpoint/pivot cases with
independent exact linear-algebra oracles. The production kernel also agrees
with a dense rank oracle on 154 small matrices. Four local implementation
mutations are rejected. An independent AI-assisted scan with touched-chart
pruning disabled made 61,838 checks and reproduced the same 2/22 classification;
that second full scan is local corroboration, not a registered second engine. This evidence is agent-checked,
not independent human or formal proof-kernel acceptance.

## Sources, overlap and contribution scope

The full original task card is retained in TASK.json. Scope is explicitly
changed from its historical complete-budget experiment to this released scalar
side question on the currently selected word. Selected baseline source bindings
passed; no full selected cold replay, Lean, Docker or native/caller audit was
run because the selected construction and shared implementation are unchanged.

PR6045 is pinned at `23abc00773a72d8e2b4e733b46c453b0f71f6368`; its immediate
predecessor PR6040 is `1889253fdbfd37e0f984ac412cf0ada4f36fa676`.
The exact census bytes were retained in this branch's first commit
`84b4202fe8bbb275cd03ca97b8a870ac419e8365`, before the new checker. SOURCES.json
binds that ancestor and the main word; the upstream origin is recorded separately.
No pending PR ancestry is silently assumed available in a clean checkout.

Live all-state PR body searches and recent #1166 handoffs were checked, including
6040,6045 and adjacent selected-word audit6043 and carrier-pricing6033. Those
scopes concern class enumeration, single-field carriers, application audit and
paid overhead respectively. No competing combination-carrier classification
was found. The local overlap helper searched 41/8,348 notes and had no usable
remote cache (`gh` unavailable); connector searches and the live board supplement
that incomplete coverage. This is not an exhaustive novelty certificate.

The family expansion decision is **narrow**: resolve one scalar acceptance gap
before any construction search. The unchanged word and original input domain
are fixed. Native realization, ownership after changed operations, pairing,
producer/consumer normalization, all added routes and complete paid/ordinary/
precision/outer costs remain unknown. Unknown costs are not zero, and no
supplier admission or new exponent follows from these carriers.

## Open next questions

1. Can a correction that changes original rows temporarily legalize either of
   the two carrier classes? Start at cuts 13637/13639, helper572/chart595,
   and keep a full symbolic endpoint map. Every finite carrier-only update
   program is excluded; the first useful proposal must leave that class.
   Lifetime legality, pairing and the complete invoice remain blockers.
2. Can non-carrier corrections exploit any of the other 22 retained-information
   cases? Start with a single explicit residual from the verifier, specify a
   concrete changed suffix and check its entire map. Absence of a carrier in
   the uncorrected word is not a universal obstruction to such sequences.

The structured questions and stop rules are in [TASK.json](TASK.json).
No broader search or paid implementation is supplied here.

## Credit

New proof, residual reduction and checker by **apoursh**, with substantial
OpenAI Codex assistance in derivation, implementation, separate subagent review,
verification and writing. Apache-2.0.

JosieElliston supplied PR6045's question, defect model and single-carrier result.
Nick Petalas supplied PR6040's class census, retained unmodified as
`inputs/shapesplit.py`. Matarener supplied PR5994's pure-subspace criterion;
flyingviper supplied PR5718's split shape; Ali Romman supplied PR5599 and the
P104 construction lineage; DreamingOfClouds supplied PR5907/6030's words.
Retain their named predecessor, native/controller, BIT and analytic credits.
The previous 4,033-class count and absence of individual carriers are theirs;
the new result is the information boundary, exact combination classification
and dynamic correction obstruction.
