# Ordinary-event compression of the PR5907 P104 word: 25,998 → 25,861 events, same invoice

**Result (tooling and a rewritten word, no new κ).** The latest conditional P104 word,
[PR #5907](https://github.com/CrocSwap/integer-mult-bounds/pull/5907) (DreamingOfClouds, κ 0.003125282), sits at
25,998 of the retained 26,000-event cap, which its author names as the main constraint on further steps. Three
semantics-preserving peephole passes over its ordinary events free **137 events** (25,861 remain) while every MOVE,
INIT and CLEAR event, every chart, every owned lifetime, every endpoint row and the complete paid and helper
profiles stay exactly the same. The rewritten word is shipped as [WORD.json.gz](WORD.json.gz) and is regenerated
by [compress.py](compress.py) from the pinned PR5907 word.

The passes: (M1) two `ADD r <- s` at the same chart with no intervening event that reads or writes `r` or writes
`s` become one ADD with the summed coefficient (deleted when the sum is zero); (M2) two consecutive `SCALE r`
become one SCALE; (D1) a write into an owned field that is CLEARed before being read again is deleted. The three
passes run to a fixed point: 98 merges and 3 dead writes. ADD count 21,706 → 21,599, SCALE 753 → 724, COPY 23 → 22.
Merged coefficients stay dyadic and within the author's growth bound; the author's scalar allowance falls from
228,664 to 227,372 units.

Base: canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`. Live inputs are pinned in [SOURCES.json](SOURCES.json).

## Why this matters

Every recent P104 step (helper hubs #5786, rung removal #5907) adds ordinary events, and the word had two events
of headroom left. The freed 137 events are room for about four more hubs or rung removals of the kind already
in the ladder. The rewrite does not change κ: the invoice is a function of the paid and helper profiles only.

It also records a negative result obtained with that headroom. A search for further #5786-style asynchronous
hubs on this word (one buffer, one frame, collection before and injection after the cut, over all 385 full-boundary
helpers, all frames of dimension 1–8 and the cut times where the available contacts change) found no hub using
only free contacts; every one of the 298 feasible (frame, helper, cut) triples needs paid subdivisions of other
queries, and the cheapest complete bills are all negative (best −0.00051 in the local concave moment at the PR5907
exponent, with two subdivisions costing 0.01028 against a split gain of 0.00977 at dimension 8). Rank-two blocks
in which two helpers share the same subdivided queries (the S09 route of the #5803 atlas) are feasible at frames
245 and 246 but no block with at most four shared subdivisions exists, and five or more subdivisions always exceed
the two-helper gain. The search code is not part of this package; its logs are available on request.

## Verification

```sh
python3.12 -B research/p104-ordinary-event-compression/verify.py
```

About six seconds, standard library only. It authenticates the pinned inputs; regenerates the word with
`compress.py` and compares the decompressed payload with the shipped file; replays both words with its own exact
checker and requires the identical sequence of MOVE/INIT/CLEAR events with identical rows of every moved field and
all 799 endpoint rows; loads PR5827's `local.py` unmodified and requires equal paid profile, helper profile,
storage inventory and rank mass plus a passing dense transpose; rejects two controls (a doubled merged coefficient,
a deleted live ADD); and compares [RESULT.json](RESULT.json) in full. Marker: `PASS_P104_ORDINARY_EVENT_COMPRESSION`.

## Scope and limits

Only the ordinary alphabet is rewritten. The native maps, the physical caller, the complete invoice, the compiler
and outer checks of PR5907 are untouched and were not rerun here; their inputs (profiles, inventory) are shown
equal. The five inherited framework assumptions remain. This is an agent check, not human acceptance. The selected
record is unchanged. The passes are local and greedy; a global re-synthesis of the ordinary events could free more.

## Open next questions

- Does a further-compressed word admit a positive-bill hub or rung removal that the 26,000 cap had blocked?
  First step: rerun the #5907 "same rung structure" search on this word with the 137 spare events.
  Blocked by: a search over itineraries, not by this package.
- Can a global ordinary re-synthesis (recomputing each register's reads from a minimal set of ADDs) free
  substantially more than the peephole passes? First step: count, per register and chart, the rank of the rows
  actually read against the number of ADDs spent. Blocked by: nothing; a bounded experiment.
- Should the event cap itself be revisited in the retained contract rather than worked around? First step: a
  maintainer statement on which allowance (events, scalar units, labels) is contractual. Blocked by: maintainers.

## Credit

DreamingOfClouds (PR5907 word), Ali Romman (PR5827 word, `local.py` checker and the P104 lineage, with OpenAI
Codex assistance), Mason Hale (PR5811), and the P104 native, controller, compiler and analytic contributors credited
in those packages. The hub-search negative result uses the mechanism of Ali Romman's PR5786. Prepared for
Matarener with Claude (Anthropic), via Claude Code. Apache-2.0.
