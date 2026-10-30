# Independent replay, delta, invoice, native and funding audit of PR6030

**Result (scoped corroborating audit, no new κ).** An independent check of
[PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030) (DreamingOfClouds, helper 470's frame-593 rung
removal, conditional κ 0.003125804) finds no error. On canonical main, an own exact replay, an exact structural
PR #5907 → PR #6030 delta, an own invoice recount, a fresh dense all-column native check with absolute phase of
**every** operator in the PR6030 inventory and an own decimal funding engine all reproduce the author's claims.
That includes the raw crossing (0.00312581155791, 0.00312581155792). The per-LOCAL margin change is H1 + H3 − H4,
the same as PR #5907's gain over PR #5827.

**Relation to the admission audit.** This work started from `a2b4b039`, where the maintainer
[repair review](../../docs/research/pr-intake-evidence/pr6030-repair/REVIEW.md) left an independent check of the
changed word open. While it ran, the maintainer admitted PR6030 at `721c0382`, after an independent application
audit (`docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md`). That audit also uses Matarener's
interpreter and dense inventory code. So this package is a second execution of largely the same checks, not new
coverage, and it changes no decision. It adds three things. First, `--full` recomputes the dense digest of all 3,163
operators. The admission review checks only the 7 new tasks densely and says it "is not a fresh independent dense
replay of every unchanged predecessor map". Second, an itinerary-level delta: exactly six register itineraries
change, and every other MOVE is unchanged as a multiset. Third, five tamper controls on the PR6030 word.

Base: canonical main `721c03822c421b7f7fcbb2598993b947c4d88419` (the work ran at `a2b4b039`; no input changed between the two). This contains PR #6030's package
(`research/p104-helper470-twin-rung-removal`, construction head `772dd10a`, with the maintainer portability repair
`746ee5e1`) and PR #5907's (`research/p104-helper468-rung-removal`). Live inputs are pinned in
[SOURCES.json](SOURCES.json).

## What is checked

The replay, invoice, dense-comparison and funding functions are copied unchanged from Matarener's
[PR5827/PR5907 audit](../p104-unread-rung-independent-audit/README.md) (PR #5960). Its digests for 3,156 of the 3,163 PR6030
native operators are reused. Nothing is imported from the PR6030 package except its data files and, in layer 0
only, its `construct.py`. The PR #5827 verifier chain, which the author ran, is not used anywhere.

| Layer | Check | Result |
|---|---|---|
| 0. Sources | PR6030's `inputs/pr5907-WORD.json.gz` and `inputs/pr5827-source.tar` against canonical main's PR5907 word and PR5907's pinned archive; PR6030 `construct.py` applied to canonical PR5907 word with `EDIT.json.gz` | pinned word and archive byte-identical; own serialization of the regenerated word equals the decompressed shipped payload byte for byte |
| 1. Own replay | PR5907 and PR6030 words: strict span nesting of every MOVE, common chart of every ADD/COPY/SCALE, dyadic coefficients, owned INIT/CLEAR lifetimes, all 799 endpoint rows (identity on public registers plus X into Y for the 104 live ports), helper initial span strictly inside final span | PASS on both: 770 public, 29 owned fields, 31 lifetimes, peak 13; paid and helper histograms equal each author's `local` block |
| | PR5907 → PR6030 delta (structure) | all fields except `program`, `initial`, `final` unchanged; exactly the three declared boundary changes (initial 713: 3→76, 736: 424→749; final 115: 105→189); exactly the six declared itineraries change (registers 115, 127, 470, 704, 713, 736, as listed in the PR6030 README); INIT, CLEAR, COPY and every other MOVE unchanged as multisets; paid delta −2H1 + H2 − 2H3 + H4 + H6 − H7 + H8, helper delta −H1 + H2 − H3 + H6 − H7 + H8 (helper ranks 115: 1→8, 713: 3→2, 736: 7→6); 22,803 events ≤ 26,000. The rewritten ADD and SCALE events (ADD 21,706 → 18,404, SCALE 753 → 861) are not compared with a declared edit; they are checked only through their exact effect in the replay above, which is what the endpoint identity needs |
| | tamper controls | flipped ADD sign (helper 268), dropped ADD (helper 470), non-dyadic SCALE, restored final chart of 115 and a reinstated frame-593 MOVE for 470 are each rejected |
| 2. Invoice | own recount from the 51 physical caller events (18 LOCAL, 15 QUERY_SHEAR, 15 IDLE, diagonal terms) and separately from the closed formula in PR5827 PROOF.md | equal to each author `complete_cost`: 66,852 / 13,444 (PR5907) and 66,834 / 13,444 (PR6030); rank-mass surplus 760 |
| 3. Dense native | PR5548's credited exact Gaussian-dyadic interpreter compares the lowered recipe with the literal frame circuit on all 512 columns: exact equality, norm, support size 2^rank | PR6030 inventory: 3,163 operators (2,886 distinct MOVE maps, 69 distinct helper pairs, 208 main adapters). The 2,922 distinct signed maps and 1,124 helper normalizers equal the author's `native` block. The 7 maps new in PR6030 are computed here (helper 3→189, 76→394, 749→127; MOVE 3→189, 3→714, 595→637, 714→127) and pinned in [NEW-MAPS.json](NEW-MAPS.json). Every other map equals the predecessor's FULL-CHECK digest. A phase-only fault and a flipped child sign on the new map 3→189 are rejected |
| 4. Own funding | 80-digit decimal ln/exp with 10⁻⁷⁰ relative padding, bisection on a 10⁻¹⁴ grid | raw crossings of PR5907 and PR6030 equal the author intervals; tested saving .0031258090 positive; tail ratios α < 1 − 10⁻¹², γ, δ < 125/128; margin derivative negative on [0, .0034], so the crossing is unique there; claim gain 261/500000000 |

The gain over PR5907 per LOCAL call is H1 + H3 − H4 in the moment margin, with H_r = r^t and t = 1 − κ. It is
positive for every t in (0, 1), because (1/4)^t + (3/4)^t decreases in t and equals 1 at t = 1.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/p104-6030-independent-audit/verify.py
```

The default run is serial and takes about one minute (61 s on Python 3.12, Apple M-series; it also passes on 3.10, 3.11, 3.13 and 3.14). It checks layers 0, 1, 2 and 4 completely. For layer 3 it
computes all 7 new maps and a fixed subset of the old ones: every helper pair, every 8th main adapter and every
64th MOVE map, each matched against the predecessor's FULL-CHECK.json. The complete PR6030 inventory runs with

```sh
python3.12 -B research/p104-6030-independent-audit/verify.py --full --jobs 8
```

in about 4 minutes on eight cores (4 min 14 s, Python 3.12). It recomputes all 3,163 digests. The marker is `PASS_P104_6030_INDEPENDENT_AUDIT`.

## Scope and limits

This audits the finite 9-qubit local word and its complete invoice. The five inherited framework assumptions remain:
native_all_columns for the uniform word, owned_erasure, compiler, precision_tape and analytic_recovery. The physical
caller (`research/p104-productive-controller`) is recounted, not re-derived. That changing a helper's initial or
final chart (here 713, 736 and 115) is a free boundary choice is inherited from the P104 line; PR5907 used the same
freedom. The compiler threshold and the 54 strict and 4 functional outer conditions are checked only by the
author's chain. The maintainer ran that chain in full on macOS and hosted Linux; it is not rerun here. The layer 1
to 4 code is shared with the predecessor audit, so it is not independent of that audit, only of the PR6030 author.
This is an agent check, not human or proof-kernel acceptance. It changes no decision: the selected record was already PR6030 at `721c0382`.

## Open next questions

- Can the outer conditions and the compiler threshold be recomputed by code that does not descend from PR5827's
  `pricing.py`? This package and its predecessor check them only through the authors' chain. The admission review
  records that all 54 strict and 4 functional predicates pass, but does not say which code computes them. First step: write each named margin
  in `complete_cost.outer` as an exact rational at κ = 781451/250000000 from its source document. Blocked on finding
  the formula source for each margin.
- Does the uniform compiler preserve the checked finite native maps at every recursion level? This is blocked by
  the inherited native_all_columns premise.

## Credit

DreamingOfClouds (PR6030 and PR5907 edits and packaging). Ali Romman (PR5827 word, verifier and lineage, with
OpenAI Codex assistance), Mason Hale (PR5811) and the lineage back to Pierre-Loic Doulcet (PR5565). Matarener
(PR5960, the PR5827/PR5907 independent audit, whose verifier functions and FULL-CHECK digests this package reuses).
Chris R / Clear1nsight (PR5548 dense interpreter, imported unchanged). Douglas Colkitt with OpenAI Codex
(the PR6030 portability repair and primary replay). The P104 native, Clifford, controller, compiler and analytic
contributors are credited in the cited packages.

Prepared for JosieElliston with Claude Opus 5.5 (Anthropic), via Claude Code, in an unattended donated session.
Apache-2.0.
