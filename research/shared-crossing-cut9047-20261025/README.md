# Reject original-cut scalar purification for a shared helper crossing

**Scoped feasibility result; no new physical word, paid-profile gain or kappa.**

This package proposes one joint hand-off for the actual L19/L300/L301 slice of
the #4610 word and rejects immediate purification at original forward cut 9047,
frame 21. L300 and L301 read the same L19 version at events 9045 and 9047. The
complete coframed inventory is only those three owners. Their actual helper
rows contain foreign independent inputs; neither required pure original helper
coordinate is in the available rational scalar span, even with two independent
successors and zero scratch.

The exact witnesses are `(L300=u,L505=-4u)` and `(L301=u,L226=u)`, holding other
inputs fixed: every available row is unchanged while the respective required
pure output changes by u. [PROOF.md](PROOF.md) gives the coefficient table,
successor projection argument and retained-anchor restriction. The independent
checker and complete exact output are [cut9047.py](cut9047.py) and
[expected/RESULT.json](expected/RESULT.json).

## Source and scope

Base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`. The live native word and its
Git blob/SHA-256 pins are in [SOURCES.json](SOURCES.json). Catalogue and selected
record pins are historical provenance. The task is a **changed, negative scope**
under `complex-new-helper-inventory`, assigned directly by the user. The original
card's positive complete-supplier acceptance gate is not claimed satisfied;
[TASK.json](TASK.json) retains its exact card and explains the connection.

This is a fixed-original-prefix normalized native-row result, with rational
scalar recoding at one cut. Earlier prefix rewrites, new helper bases, other
cuts/anchors, operator-valued ordinary recoding and larger words are not tested.
The input witnesses must not be transferred to another caller's restricted or
owned input domain without checking admissibility there. A complete physical
phase/raw-dual/caller/compiler/outer result is not supplied. The proposed
`2H1+2H8-2H9` split receives no credit for this rejected local premise.

Nearest predecessors: [#5472](https://github.com/CrocSwap/integer-mult-bounds/pull/5472)
(successor hand-off and local re-flag neutrality),
[#5541](https://github.com/CrocSwap/integer-mult-bounds/pull/5541) (actual-word
balanced-J verification with coded-main restrictions), and the native/owned
relation lineage below. Unlike a padded toy example, the tested pair and dirty
input mixtures are taken from the actual word. This result is not a universal
obstruction to genuine shared re-flagging.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/shared-crossing-cut9047-20261025 --check-only
python3 -B scripts/research_package.py --package research/shared-crossing-cut9047-20261025
```

Direct source-export replay also works when the pinned native input is present:

```sh
python3 -B research/shared-crossing-cut9047-20261025/verify.py
```

Expected marker: `PASS_SHARED_CROSSING_CUT9047_SCALAR_OBSTRUCTION`.
The registered command has a 150-second timeout and invokes serial normal and
optimized checker subprocesses, each capped at 65 seconds. It compares their
complete bytes to the frozen exact result with zero scientific exclusions,
checks source/core hashes, the paper separators, input charts and anchor sets.
No source evaluator is imported. The child checkers use `-I -B` and import only
the Python standard library; no project bytecode dependency is used.

The original guarded pair took 0.906 seconds at 81.0625 MiB sampled peak RSS;
portable/hosted runtime is environment-dependent. [REVIEW.md](REVIEW.md)
distinguishes that historical run, independent agent review and admission.
The seven declared core controls include clean/poison span cases, independent
successors, wrong version, omitted pre-subtraction and dirty successor. The
duplicate-owner control is a synthetic distinct-label sanity check, not a
complete target-admission replay. No full changed candidate exists to replay.

## Open next questions

The structured questions in [TASK.json](TASK.json) name their relevance, first
step and blockers. A later design must either specify an earlier prefix/basis
rewrite that removes these witnesses, or relocate the anchors with a complete
transport/restoration bill. Neither is supplied here. Repeating this same cut
with more scalar coefficients or samples cannot evade the exact span result.
All research stopped after the one qualification result; this package starts
no new search or automatic continuation.

## Credit

Cao Yifan: #4610 native word. zxv: productive helpers and native semantics.
GamingPuzzled/Joel Pulikkan: #5472 hand-off and re-flag analysis. Cinna Davis:
scalar semantics/compression. Matarener: scoped boundary work. aliromman:
#5383 owned relations and later audits. Dillon Amburgey and Clear1nsight/Chris R:
provider/completion and #5413 caller lineage. Retain the further source authors
credited in those packages.

Prepared by Chris R (Clear1nsight) with substantial OpenAI Codex assistance:
GPT-6-astra/xhigh paper design; GPT-6.1-sol/high event extraction, independent
checker/physical and invoice review, source custody and guarded execution.
Agent independence is not independent human or formal theorem admission.
New material is Apache-2.0; the native input is not copied or modified.
