# Independent replay, delta, invoice, native, caller and funding audit of PR6144 and PR6167

**Result (scoped independent audit, no new κ).** An independent check of the two unadmitted conditional P104 words
above the selected record finds no error:
[PR #6144](https://github.com/CrocSwap/integer-mult-bounds/pull/6144) (DreamingOfClouds, owned registers 770, 771
and 772 descend through the frames of helpers 705, 706 and 731, κ 0.003128386) and
[PR #6167](https://github.com/CrocSwap/integer-mult-bounds/pull/6167) (Ali Romman, a retained operand removes one
stop of root 772, κ 0.003128645). On canonical main, an own exact replay, exact structural deltas
PR6030 → PR6144 → PR6167, an own invoice recount, a dense all-column absolute-phase check of every native operator
in both inventories, the maintainers' independent caller checker and an own decimal funding engine all reproduce
the authors' claims, including the raw crossings (0.00312839320327, …328) and (0.00312865201590, …591).

This package supplies, for both words, the same layers that the
[PR6030 admission review](../../docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md) used: Matarener's
PR5960 interpreter for the word and invoice, Clear1nsight's dense interpreter for every new native map, the
generalized independent caller checker with its positive control, and the authors' primary chain (rerun here on
Linux, both PASS). It changes no decision by itself.

Base: canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, which contains PR6030
(`research/p104-helper470-twin-rung-removal`), PR6144 (`research/p104-root-relay-descent-2`, head `5ec9b6da`) and
PR6167 (`research/p104-retained-operand-descent`, head `564a076b`). Inputs are pinned in [SOURCES.json](SOURCES.json).

## What is checked

The replay, invoice and dense-comparison functions are imported unchanged from Matarener's
[PR5827/PR5907 audit](../p104-unread-rung-independent-audit/README.md) (PR #5960); its FULL-CHECK digests and the
[PR6030 audit](../p104-6030-independent-audit/README.md)'s NEW-MAPS digests are the reference for unchanged maps.
Nothing is imported from the PR6144 or PR6167 packages except their data files and, in layer 0 only, PR6144's
`construct.py`. PR6167's word is rebuilt from the five replacements stated in its PROOF.md, without its `construct.py`.

| Layer | Check | Result |
|---|---|---|
| 0. Sources | PR6144's pinned PR6030 word, PR6167's pinned PR6144 word and PR6144 `pricing.py` against canonical main; the PR5827 archive in all three packages; PR6144 `construct.py` on canonical PR6030 word with `EDIT.json.gz`; PR6167 PROOF.md replacements (events 12913, 12918, 13486–13488) on canonical PR6144 word | all pinned bytes equal canonical main; both regenerated words equal the shipped decompressed payloads byte for byte |
| 1. Own replay | PR6030, PR6144 and PR6167 words: strict span nesting of every MOVE, common chart of every ADD/COPY/SCALE, dyadic coefficients, owned INIT/CLEAR lifetimes, all 799 endpoint rows, helper nesting | PASS on all three; 770 public, 29 owned labels, lifetimes 31 / 31 / 32, peak 13; paid and helper histograms equal each author's `local` block |
| | PR6030 → PR6144 delta | only `program` changes (no boundary chart); exactly seven itineraries change, as in the PR6144 README: helpers 705, 706, 731 keep one hop (3→549, 3→541, 3→529), helper 732 goes 3→117→222→127, owned 770: 549→553→1047→593, 771: 541→534→117→594, 772: 529→520→737→595; INIT, CLEAR, COPY, SCALE and every other MOVE unchanged as multisets; 52 ADD removed, 71 added; paid delta −4H1 −H4 +H5 −3H6 +3H7, helper delta 0; 22,818 events ≤ 26,000 |
| | PR6144 → PR6167 delta | exactly three itineraries change: reader 451 3→595→737→…, root 772 529→520→595 and a new 770 lifetime at frame 737; exactly one INIT, one COPY (`770 ← 228` at 737) and one CLEAR are added; MOVE outside 451/772 unchanged; paid delta +H1 −H2 −H4 +H5, helper delta 0; 22,821 events |
| | margin signs | per-LOCAL margin change 4H1+H4−H5+3H6−3H7 (PR6144) and H2+H4−H1−H5 (PR6167): equal rank mass and the positive ranks are majorized by the negative ones, so by Karamata and strict concavity of r^t each is positive for 0<t<1 (also checked on a grid) |
| | tamper controls | PR6144: dropped 770 descent MOVE, flipped first read of 771, restored relay hop 705→593; PR6167: dropped cache COPY, flipped its sign, dropped late operand, dropped cache CLEAR, root coefficient −4→−2, COPY moved after helper 228 leaves frame 737: all nine rejected |
| 2. Invoice | own recount from the 51 physical caller events and separately from the closed formula | equal to each author `complete_cost`: 66,834 / 13,444 (PR6030), 66,762 / 13,444 (PR6144 and PR6167); paid rank mass 240,152, surplus 760 |
| 3. Dense native | PR5548's exact Gaussian-dyadic interpreter, all 512 columns, exact equality, norm, support 2^rank | union inventory 3,169 operators (PR6144: 3,167 tasks, 2,923 distinct signed maps; PR6167: 3,166 tasks, 2,922), equal to the authors' `native` blocks (1,124 helper normalizers, 208 main adapters). 13 maps are new after PR6030 and pinned in [NEW-MAPS.json](NEW-MAPS.json): 3→529, 3→541, 3→549 (rank 7), 117→594, 520→595, 520→737, 529→520, 534→117, 541→534, 549→553, 553→1047, 737→595, 1047→593. All 3,156 others equal the reference digests (`--full` recomputes all). Phase-only fault and flipped child sign on map 3→529 are rejected |
| 4. Own funding | 80-digit decimal ln/exp with 10⁻⁷⁰ padding, bisection on a 10⁻¹⁴ grid | raw crossings of PR6030, PR6144 and PR6167 equal the author intervals; tested savings .0031283910 and .0031286500 positive; tail ratios α < 1−10⁻¹², γ, δ < 125/128; derivative negative on [0, .0034]; compiler threshold integers (H+1)^1024 < 2^j with predecessor failing; PR6030's invoice fails at the PR6144 claim and PR6144's at the PR6167 claim (upper margins −0.62 and −0.061); claim gains 1291/500000000 and 259/1000000000 |
| 5. Caller | [caller.py](caller.py): the PR6030 admission review's generalized independent caller checker, prepared from its pinned inputs, positive control first | control digest `b51a7d19…` reproduced; `PASS_SCOPED_CALLER_AND_TARGET_BINDING` on both words: 346 signed-Pauli/phase anchors, 10,116 fresh helpers, owned peak 13, invoice equal to `complete_cost`, ten controls rejected ([CALLER.json](CALLER.json)) |

The authors' own verifiers (`PASS_P104_BASE6030_EDIT_KAPPA_312838600`, `PASS_P104_RETAINED_OPERAND_KAPPA_003128645`)
were also rerun on hosted Linux, Python 3.12.3, in about 4.6 minutes each, and pass; they run the compiler and the
54 strict plus 4 functional outer checks that this package does not recompute.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/p104-retained-operand-independent-audit/verify.py
python3.12 -B research/p104-retained-operand-independent-audit/caller.py
```

The default `verify.py` run is serial (2.5 minutes on hosted Linux): layers 0, 1, 2 and 4 completely, and for layer 3 all 13 new maps plus every
helper pair, every 8th main adapter and every 64th MOVE map against the reference digests. The complete inventory
runs with `verify.py --full --jobs 3` (15.6 minutes on three hosted Linux cores). `caller.py` takes about 2.5 minutes.
Markers: `PASS_P104_6144_6167_INDEPENDENT_AUDIT` and `PASS_P104_6144_6167_CALLER_BINDING`.

## Scope and limits

This audits the finite 9-qubit local words, their complete invoices and the caller binding. The five inherited
framework assumptions remain: native_all_columns for the uniform word, owned_erasure, compiler, precision_tape and
analytic_recovery. The compiler threshold is checked only through its integer statements; the 54 strict and
4 functional outer conditions are checked only by the authors' chain. The layer 1–4 code is shared with the PR5960
and PR6030 audits, and the caller checker is the maintainers', so this package is independent of the PR6144 and
PR6167 authors, not of those audits. This is an agent check, not human or proof-kernel acceptance.

Side note: PR #6154 (owned 770/791 coalescence) and PR #6169 (common-response coefficient reduction) each still
replay exactly when the PR6167 schedule is applied on top of them (with any free owned label for the retained
operand); neither changes the paid profile, so neither changes κ.

## Open next questions

- Can the outer conditions and the compiler threshold be recomputed by code that does not descend from PR5827's
  `pricing.py`? First step: write each margin in `complete_cost.outer` as an exact rational at κ = 625729/200000000.
- Can reader 497 also avoid its remaining stop at frame 520 (PR6167's own open question)?

## Credit

DreamingOfClouds (PR6144, PR6143, PR6030, PR5907). Ali Romman (PR6167, PR5827 word, verifier and lineage, with
OpenAI Codex assistance), Mason Hale (PR5811) and the lineage back to Pierre-Loic Doulcet (PR5565). Matarener
(PR5960, whose verifier functions and FULL-CHECK digests this package reuses). JosieElliston (PR6030 audit and its
NEW-MAPS digests). Chris R / Clear1nsight (PR5548 dense interpreter). Douglas Colkitt with OpenAI Codex (PR6030
admission review and its generalized caller checker). The P104 native, Clifford, controller, compiler and analytic
contributors are credited in the cited packages.

Prepared by Matarener with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
