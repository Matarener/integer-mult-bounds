# Conditional kappa 0.003128386: owned registers 770, 771 and 772 descend through the frames of helpers 705, 706 and 731, which no longer relay them; helper 732 reads 771 at frame 117

This package edits the word of [PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030)
(DreamingOfClouds, merged on main, conditional kappa 0.003125804) and re-certifies it with the chain PR #6030 used:
PR #5827's own verifier (aliromman, head `05cd36e5af06d7a3790e30ce3f449fa89b853768`), loaded unmodified apart from the declared pricing literals.
The complete conditional kappa is **0.003128386**, tested at 0.0031283910; the exact raw crossing lies in
(0.00312839320327, 0.00312839320328) = (312839320327/100000000000000, 39104915041/12500000000000),
which is +2.582e-06 above PR #6030's raw crossing (0.00312581155791). The paid bill falls to
**66762 calls** (PR #6030: 66,834) at an unchanged 13444 productive targets and rank-mass surplus
760. Public inputs, owned fields, owned lifetimes and peak occupancy (770, 29, 31, 13) are unchanged;
the word has 22,818 events (PR #6030: 22,803; retained cap 26,000).

## The edit

The edit removes three relays and moves one read. In PR #6030's word, the owned registers 770, 771 and 772 are each loaded at one frame, moved once to a neighbouring frame and cleared there (770: 549 -> 593; 771: 541 -> 594; 772: 529 -> 595). A public helper then reads each of them at the landing frame and carries its content back up through the intermediate frames (helper 705: 593 -> 1047 -> 553 -> 549; helper 706: 594 -> 117 -> 534 -> 541; helper 731: 595 -> 737 -> 520 -> 529), delivering at each frame.

In the edited word the owned registers walk those frames themselves, downwards, and the helpers no longer carry the content:
- 770 runs 549 -> 553 -> 1047 -> 593; 771 runs 541 -> 534 -> 117 -> 594; 772 runs 529 -> 520 -> 737 -> 595.
- Helpers 705, 706 and 731 keep a single hop, 3 -> 549, 3 -> 541 and 3 -> 529, to their unchanged final frames.
- The readers that took their content from the relays now read the owned registers at the same frames. The frame-3 reads that paired against the relays' initial values are re-solved against other registers.

Two further changes keep the occupancy and the values exact:
- **Owned lifetimes.** To keep peak occupancy at 13, the lifetimes of 770 and 771 are placed after the peak window: their INIT/COPY events move from 13452-13456 and 13463-13465 to 13658-13659 and 13637-13638, and their CLEARs from 13462 and 13471 to 15424 and 15427. Register 772 keeps an early lifetime (INIT/COPY at 13478-13481) and its CLEAR moves from 13482 to 13624. Six readers of frame 595 (helpers 134, 450, 496, 572, 581, 582) take their frame-3 -> 595 hop before the root lands, which moves their MOVE events earlier.
- **Helper 732.** Helper 732 reads owned register 771 at frame 117, on 771's way down, instead of at frame 594. It therefore goes 3 -> 117 -> 222 -> 127 and drops its stop at 594. Its pre-reads (helpers 569, 575, 576) are placed before the owned peak window.

The INIT, CLEAR, COPY and SCALE events are identical as multisets; 52 ADD events are removed and 71 are added, 17 MOVE events are removed and 13 are added, and the event list grows from 22,803 to 22,818 events.

Boundary charts changed by the edit: none. Paid-profile change vs PR #6030: rank 1: -4, rank 4: -1, rank 5: +1, rank 6: -3, rank 7: +3.
Credited helper ranks: unchanged.
Every public input column, every signed native map and the physical caller are re-checked in full (see Verification).

`EDIT.json.gz` is the explicit edit list: boundary changes plus the new event list as copy segments of
PR #6030's program and literal events. `construct.py` (standard library only) applies it to PR #6030's word, taken from
`inputs/pr6030-WORD.json.gz` (authenticated against main's `research/p104-helper470-twin-rung-removal/WORD.json.gz`, Git blob and SHA256 in `SOURCES.json`), and regenerates
the complete decompressed `WORD.json.gz` payload byte for byte (gzip-container bytes may differ by platform; this comparison is
PR #6030's merged portability repair, kept with its `test_portability.py`):

```sh
python3.12 -I -B research/p104-root-relay-descent-2/construct.py
```

## Verification

```sh
python3.12 -I -O -B research/p104-root-relay-descent-2/test_portability.py
python3.12 -I -B research/p104-root-relay-descent-2/verify.py
```

`verify.py` authenticates PR #6030's word and the pinned PR #5827 package (`inputs/pr5827-source.tar`, per-file SHA256 and Git blob;
byte-identical to the archive in PR #6030's package) and its seven-deep source chain, asserts that the shipped `pricing.py` equals
PR #5827's `pricing.py` plus the literal edits in `PRICING-EDITS.json` (claim, previous claim = PR #6030's, the paid-call count and two labels),
regenerates the word, and runs PR #5827's chain unchanged: exact replay and storage inventory, all 799 input columns with a separate
transpose, every signed native map, 208 main adapters, 1,124 helper normalizers, the exact physical caller, the complete invoice, both
interval engines, compiler and 54 strict plus 4 functional outer checks, a check that PR #6030's full profile fails at the new claim,
rejection controls, and the committed `RESULT.json`. `--part build` runs the authentication, regeneration and replay only.

## Conditions inherited

The five framework assumptions retained by the P104 line (native all-column implementation, owned erasure, uniform compiler closure,
precision and fixed-tape costs, claim accounting) and PR #5827's own checker are inherited unchanged. Author checks are not
independent human acceptance. The finite local word is materialized; the large uniform word and rounded multiplier are not. No merge,
closure or selected-frontier change is requested.

## Credits

The base word is PR #6030's (DreamingOfClouds, helper 470's frame-593 rung removal), an edit of PR #5907's word (DreamingOfClouds,
helper 468's frame-593 rung removal), itself an edit of PR #5827's word. The payload comparison in `construct.py`/`verify.py` and
`test_portability.py` are the maintainer portability repair merged with PR #6030 (Douglas Colkitt, with OpenAI Codex assistance).
The verifier chain is Ali Romman's (aliromman, PR #5827, with substantial OpenAI Codex assistance), built on PR #5811
(Mason Hale), PR #5786 and the earlier lineage back to PR #5565 (Pierre-Loic Doulcet), with all retained source notices in the pinned
archive. This package contributes only the edit above and its packaging.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Open next questions

- Does an independent reviewer confirm the edit list, the regenerated word and the full chain? First step: run `construct.py` and
  `verify.py` as above, then compare the changed itineraries with PR #6030's word.
