# Conditional kappa 0.003125804: remove helper 470's frame-593 rung, the twin of PR5907's removal

This package edits the word of [PR #5907](https://github.com/CrocSwap/integer-mult-bounds/pull/5907)
(DreamingOfClouds, merged on main, conditional kappa 0.003125282) and re-certifies it with the chain PR #5907 used:
PR #5827's own verifier (aliromman, head `05cd36e5af06d7a3790e30ce3f449fa89b853768`), loaded unmodified apart from the declared pricing literals.
The complete conditional kappa is **0.003125804**, tested at 0.0031258090; the exact raw crossing lies in
(0.00312581155791, 0.00312581155792) = (312581155791/100000000000000, 19536322237/6250000000000),
which is +5.225e-07 above PR #5907's raw crossing (0.00312528909884). The paid bill falls to
**66834 calls** (PR #5907: 66,852) at an unchanged 13444 productive targets and rank-mass surplus
760. Public inputs, owned fields, owned lifetimes and peak occupancy (770, 29, 31, 13) are unchanged;
the word has 22,803 events (PR #5907: 25,998; retained cap 26,000).

## The edit

The edit removes helper 470's rung at frame 593: its itinerary 3 -> 593 -> 714 -> 875 -> 1001 -> 131 -> 127 becomes
3 -> 714 -> 875 -> 1001 -> 131 -> 127. Helper 704's chain 3 -> 593 -> 612 -> 127 now runs 3 -> 593 -> 714 -> 127, so helper 470
takes its read of 704 at frame 714. This is the twin of PR #5907's removal (helper 468's frame-593 rung, with helper 703 moved to
frame 712). Helper 560 no longer reads 704 at frame 612; helper 268, which received that content through its frame-612 read
of 560, now reads 2·704 directly at frame 714. Four further itineraries change: helper 115 ends at frame 189 instead of 105, Y main 127's second chart is 595
instead of 602, helper 713 starts at frame 76 instead of 3, and helper 736 starts at frame 749 instead of 424.
Every other change is a rewrite of the ordinary (ADD and SCALE) events. The INIT, CLEAR and COPY events are identical as a
multiset, every MOVE outside the six itineraries above is unchanged, and the chart list and every endpoint row are kept: the event list falls from 25,998 to 22,803 events (ADD 21,706 -> 18,404,
SCALE 753 -> 861, MOVE 3,454 -> 3,453), and about 795 registers carry a different event
sequence.

Boundary charts changed by the edit: initial 713: 3 -> 76; initial 736: 424 -> 749; final 115: 105 -> 189. Paid-profile change vs PR #5907: rank 1: -2, rank 2: +1, rank 3: -2, rank 4: +1, rank 6: +1, rank 7: -1, rank 8: +1.
Credited helper-rank change: rank 1: -1, rank 2: +1, rank 3: -1, rank 6: +1, rank 7: -1, rank 8: +1.
Every public input column, every signed native map and the physical caller are re-checked in full (see Verification).

`EDIT.json.gz` is the explicit edit list: boundary changes plus the new event list as copy segments of
PR #5907's program and literal events. `construct.py` (standard library only) applies it to PR #5907's word, taken from
`inputs/pr5907-WORD.json.gz` (authenticated against main's `research/p104-helper468-rung-removal/WORD.json.gz`, Git blob and SHA256 in `SOURCES.json`), and regenerates
the complete decompressed `WORD.json.gz` payload byte for byte (gzip-container
bytes may differ by platform):

```sh
python3.12 -I -B research/p104-helper470-twin-rung-removal/construct.py
```

## Verification

```sh
python3.12 -I -B research/p104-helper470-twin-rung-removal/verify.py
```

`verify.py` authenticates PR #5907's word and the pinned PR #5827 package (`inputs/pr5827-source.tar`, per-file SHA256 and Git blob;
byte-identical to the archive in PR #5907's package) and its seven-deep source chain, asserts that the shipped `pricing.py` equals
PR #5827's `pricing.py` plus the literal edits in `PRICING-EDITS.json` (claim, previous claim = PR #5907's, the paid-call count and two labels),
regenerates the word, and runs PR #5827's chain unchanged: exact replay and storage inventory, all 799 input columns with a separate
transpose, every signed native map, 208 main adapters, 1,124 helper normalizers, the exact physical caller, the complete invoice, both
interval engines, compiler and 54 strict plus 4 functional outer checks, a check that PR #5907's full profile fails at the new claim,
rejection controls, and the committed `RESULT.json`. `--part build` runs the authentication, regeneration and replay only.

## Conditions inherited

The five framework assumptions retained by the P104 line (native all-column implementation, owned erasure, uniform compiler closure,
precision and fixed-tape costs, claim accounting) and PR #5827's own checker are inherited unchanged. Author checks are not
independent human acceptance. The finite local word is materialized; the large uniform word and rounded multiplier are not. No merge,
closure or selected-frontier change is requested.

## Credits

The base word is PR #5907's (DreamingOfClouds, helper 468's frame-593 rung removal), itself an edit of PR #5827's word.
The verifier chain is Ali Romman's (aliromman, PR #5827, with substantial OpenAI Codex assistance), built on PR #5811
(Mason Hale), PR #5786 and the earlier lineage back to PR #5565 (Pierre-Loic Doulcet), with all retained source notices in the pinned
archive. This package contributes only the edit above and its packaging.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Open next questions

- Does an independent reviewer confirm the edit list, the regenerated word and the full chain? First step: run `construct.py` and
  `verify.py` as above, then compare the changed itineraries with PR #5907's word.
- Helpers 469 and 471 have the same frame-593 rung shape as 468 and 470, but their frame-593 reads come from the same two sources
  (703, 704) that the two removals now place at frames 712 and 714. Does any itinerary for 469 or 471 avoid frame 593 without a new
  carrier of that content? First step: list the holders of 469's and 471's frame-593 read content at frames shared with 469 and 471.

## Maintainer portability repair

The exact source head `772dd10a5859a1d15f4851feb371519789213ad8`
failed hosted Linux run [40597285594](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/40597285594)
at the generated gzip-container comparison. As independently reported for
PR5907 by Matarener in PR5960, the gzip OS header can differ across platforms.

The repaired comparison checks every byte of the complete regenerated JSON
payload after decompression. It does not use Python object equality (which can
confuse booleans with integers), omit fields, or alter the expected mathematical
result. Immutable source archives and the base word retain their exact size,
SHA256 and Git-blob checks. `test_portability.py` tests header, timestamp, filename
and compression variations, changed events/fields, boolean/integer substitutions,
corrupt containers and exact immutable-input authentication. It is also registered
in optimized Python mode. The original construction and committed data retain
DreamingOfClouds and predecessor credit; this repair is by Douglas Colkitt with
OpenAI Codex assistance. Replay evidence is recorded separately; this repair alone
does not promote the selected frontier or discharge inherited assumptions.
