# Conditional kappa 0.003125282: remove helper 468's frame-593 rung with rerouted reads

This package edits the word of [PR #5827](https://github.com/CrocSwap/integer-mult-bounds/pull/5827)
(aliromman, head `05cd36e5af06d7a3790e30ce3f449fa89b853768`, conditional kappa 0.00312476680) and re-certifies it with PR #5827's own chain. The complete
conditional kappa is **0.003125282**, tested at 0.0031252870; the exact raw crossing lies in
(0.00312528909884, 0.00312528909885) = (78132227471/25000000000000, 62505781977/20000000000000),
which is +5.223e-07 above PR #5827's raw crossing (.00312476681507). The paid bill falls to
**66852 calls** (PR #5827: 66,870) at an unchanged 13444 productive targets and rank-mass surplus
760. Public inputs, owned fields, owned lifetimes and peak occupancy (770, 29, 31, 13) are unchanged;
the word has 25998 events (retained cap 26,000).

## The edit

The edit removes helper 468's rung at frame 593: its itinerary 3 -> 593 -> 712 becomes 3 -> 712. Helper 703's
chain 593 -> 859 -> 127 now runs 593 -> 712 -> 127. Three one-hop helpers are retargeted: helper 455 goes from
3 -> 105 to 3 -> 925, helper 557 from 3 -> 105 to 105 -> 925, and helper 765 from 245 -> 127 to 263 -> 742. Their
helper spans rise (1 to 7, 6 and 3), which moves paid ranks as listed below. Every other change is the induced
rewrite of read and write windows: about 650 registers carry a different event sequence, with 1 MOVE fewer and
15 ADDs more (SCALE, COPY, INIT and CLEAR counts are equal).

Boundary charts changed by the edit: initial 557: 3 -> 105; initial 765: 245 -> 263; final 455: 105 -> 925; final 557: 105 -> 925; final 765: 127 -> 742. Paid-profile change vs PR #5827: rank 1: -4, rank 4: +1, rank 6: +1, rank 7: +1.
Every public input column, every signed native map and the physical caller are re-checked in full (see Verification).

`EDIT.json.gz` is the explicit edit list: boundary changes plus the new event list as copy segments of
PR #5827's program and literal events. `construct.py` (standard library only) applies it to PR #5827's word, taken from
the pinned archive, and regenerates `WORD.json.gz` byte for byte:

```sh
python3.12 -I -B research/p104-helper468-rung-removal/construct.py
```

## Verification

```sh
python3.12 -I -B research/p104-helper468-rung-removal/verify.py
```

`verify.py` authenticates the pinned PR #5827 package (`inputs/pr5827-source.tar`, per-file SHA256 and Git blob) and its seven-deep source
chain, asserts that the shipped `pricing.py` equals PR #5827's `pricing.py` plus the literal edits in `PRICING-EDITS.json` (claim,
previous claim, the paid-call count and two labels), regenerates the word, and runs PR #5827's chain unchanged: exact replay and storage
inventory, all 799 input columns with a separate transpose, every signed native map (2,921), 208 main adapters, 1,124 helper
normalizers, the exact physical caller, the complete invoice, both interval engines, compiler and 54 strict plus 4 functional outer
checks, rejection controls, and the committed `RESULT.json`. `--part build` runs the authentication, regeneration and replay only.

## Conditions inherited

The five framework assumptions retained by the P104 line (native all-column implementation, owned erasure, uniform compiler closure,
precision and fixed-tape costs, claim accounting) and PR #5827's own checker are inherited unchanged. Author checks are not
independent human acceptance. The finite local word is materialized; the large uniform word and rounded multiplier are not. No merge,
closure or selected-frontier change is requested.

## Credits

The base word and verifier are Ali Romman's (aliromman, PR #5827, with substantial OpenAI Codex assistance), built on PR #5811
(Mason Hale), PR #5786 and the earlier lineage back to PR #5565 (Pierre-Loic Doulcet), with all retained source notices in the pinned
archive. This package contributes only the edit above and its packaging.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Open next questions

- Does an independent reviewer confirm the edit list, the regenerated word and the full chain? First step: run `construct.py` and
  `verify.py` as above, then compare the changed boundary charts with PR #5827's.
- Do other helpers with the same rung structure admit the same removal, and does any combination fit the 25998-of-26,000
  event cap? First step: list helpers whose itinerary passes through a frame used by no other reader, then compare event counts.
