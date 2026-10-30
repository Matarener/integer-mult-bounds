# PR6030's local P104 word has no chart-only headroom (no new κ)

**Negative scoped result; no new κ.** On the exact local word of the selected
PR6030 construction (and, for comparison, the PR5907 and PR5827 words), five
classes of edits find **no** gain in the paid moment. Each class keeps every
scalar event and changes only frames, MOVEs or commuting event order. Three
synthetic controls on the PR6030 word are found. This does not prove that no
chart-only edit exists. It does say that the simple ones (merging a rung,
re-charting a meeting or a linked pair) are gone, so the next complex step should
start from a change to the scalar program, as PR5827, PR5907 and PR6030 each did.

## Why this is the remaining packing question

The fixed PR6030 invoice is already packed to its root: the selected
[review](../../docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md)
encloses the raw crossing in (0.00312581155791, 0.00312581155792) and tests the
claim just below it. Further packing needs a changed paid profile. In PR5827's
[local.py](../p104-unread-path-resynthesis/local.py), the profile has one free
parameter that does not touch the scalar program:

- a MOVE from frame `a` to frame `b` is a paid call of rank `|dim b - dim a|`;
- a helper's productive rank is `dim(final) - dim(initial)`;
- a scalar event needs its registers in a common frame, but any common frame will do.

Merging two moves of ranks `x, y` into one of rank `x+y` gains
`x^t + y^t - (x+y)^t` per LOCAL call at unchanged targets. That is about
`2.25·C` for PR6030's own 1+3 merge and `1.39·C` for a 1+1 merge, either of which
would have been a hill-climbing step. This package checks whether any such merge,
or any other re-chart, is available without rewriting the scalar program.

## Classes searched (exhaustive within each class)

A *stay* is a maximal interval during which one register occupies one frame. A
*meeting* is a connected set of stays at one frame joined by scalar events.

| Class | Edit | PR6030 word |
|---|---|---|
| A. rung skip by retiming | Delete one stay `a -> b -> c`, with one MOVE `a -> c` at any slot in `[i, j]`. Each of its scalar events (SCALEs included) moves, commuting past every other event, to a slot where its partner is at `a` (before) or `c` (after). The stay's own events are not treated as barriers; the replay rejects any non-equivalent order. | 2,664 stays; none admits a retiming |
| B. re-chart to a listed frame | Move a whole meeting to any of the 1,093 listed frames that nests between every member's neighbours. A rank-0 move disappears. Optionally, helper (not main) endpoints may follow. | 41 nesting-legal re-charts (19,312 with helper endpoints); none gains |
| C. re-chart to any subspace | As B, but the frame can be any subspace between the span of the lower neighbours and the intersection of the upper ones. The cost depends only on dimension, so every dimension in that interval is checked. | 743 free meetings (834 with helper endpoints); 87 (163) have dimension slack; none gains |
| D. split skip | Delete a stay `a -> b -> c` and re-chart each partner sub-meeting as a whole: to `a` for events before a threshold, to `c` after it. Event order is fixed. | 80 legal thresholds out of 2,664 stays, all losing |
| E. joint pair re-chart | Re-chart two meetings joined by at least one MOVE together, each to a listed frame, against all their other neighbours. | 1,238 linked pairs, 209 legal joint re-charts; none gains |

The same five classes find nothing on the PR5907 and PR5827 words either.
PR5907's and PR6030's frame-593 rung removals are therefore *outside* these
classes. PR6030's README says its edit also rewrote the ordinary ADD/SCALE events
(ADD 21,706 -> 18,404) and rerouted reads through other helpers.

Gains are ranked with the per-LOCAL proxy `t = 1 - 0.0031258`. Every proposal
from A, and every B proposal with positive proxy gain, is replayed by the
unmodified PR5827 `local.py` replay (all public and owned rows, nesting,
ownership and frame tags). Class E proposals are priced by the nesting rule only;
none is positive on the real words. Class C is an exact dimension argument: subspaces of
every intermediate dimension exist between nested subspaces.

**Controls (on the PR6030 word).** (1) Split the first public rank-2 move
(register 76, event 9934, frames 3 -> 252) through listed frame 81, adding an
unread rung. A, B, C and D all find it, with gain `2 - 2^t = 0.004328588`.
(2) Re-chart meeting 2620 from frame 1057 (dim 5) to frame 782 (dim 4), which
worsens the paid moment by 0.001055287. B, C and E find the reverse move.
(3) As (1), with two `SCALE -1` events of register 76 inside the new rung. A must
relocate both, in order, and does; B also finds it. All three perturbed words pass
the PR5827 replay before the census runs.

## Scope and limits

- This is a finite search over the stated classes, not an optimality proof for
  the word. Class A retimes one register's events with partners fixed. Class C
  moves one meeting at a time with its neighbours fixed (coordinate-wise
  optimality). Class E covers pairs of linked meetings over listed frames only;
  larger groups, and pairs over arbitrary subspaces, are not covered.
- Class A's controls exercise SCALE relocation, not an ADD whose partner must
  be met at another slot. No such control was built in the session budget.
- Native maps for new (a, c) frame pairs, the compiler, the physical caller and
  the outer rows are not exercised, because no proposal reached them. A positive
  find would need the full PR5827 chain as used in PR6030's `verify.py`.
- All five inherited framework assumptions and the selected record are unchanged.

## Reproduce

```sh
python3 scripts/research_package.py --package research/p104-chart-assignment-rigidity --check-only
python3.12 scripts/research_package.py --package research/p104-chart-assignment-rigidity
```

The direct command is `python3.12 -I -B research/p104-chart-assignment-rigidity/verify.py`.
It prints `PASS_P104_CHART_ASSIGNMENT_RIGIDITY` and compares the regenerated
`RESULT.json` byte for byte (under 90 s, standard library only).

## Open next questions

- **Read rerouting, then re-chart.** In PR6030, helper 268 reads `2·704` at frame
  714 and helper 560 no longer reads 704 at frame 612. Can rewrites of this kind,
  where a register reads a source directly instead of through an intermediate
  register, be enumerated? Classes A-E could then run on each rewritten word.
  First step: from the local.py row replay, list each ADD whose source carries a
  single-source term received at a frame the destination never visits. Then test
  whether the destination and the original source share a frame at a commuting
  slot. Blocker: a rewrite engine that keeps every row identity; local.py can serve
  as the exact checker.
- **Larger joint re-charts.** Concave rank costs can reward moving several linked
  meetings together even when no single move or listed-frame pair gains. First
  step: extend class E to arbitrary subspaces, or to chains of three meetings,
  by searching the subspace lattice between the group's outer bounds. No blocker.

## Credit

The words are DreamingOfClouds' (PR6030, PR5907) and Ali Romman's (PR5827, with
substantial OpenAI Codex assistance). They rest on PR5811 (Mason Hale) and the
lineage back to PR5565 (Pierre-Loic Doulcet). The replay checker is PR5827's
`local.py` (Ali Romman, adapted from PR5544/5545), imported unchanged. This
package adds only the census and controls.

Prepared by Josie Elliston with Claude Opus 5.5 (Anthropic) via Claude Code, in
an unattended session. Apache-2.0.
