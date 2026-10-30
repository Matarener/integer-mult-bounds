# R11 notes: systematic local-rewrite census on the #4088 staged544 words (no new kappa)

Base: PR4088 head `72d7efc181edb21806a878f174847c96dd410ab0` (1337isnot1337, mixed fourth entry,
root 0.001730979115670792472760), built on #4085 (zxv receiver sharing) / #4076 (rohanarun, three
staged entries) / #3945 / #3949. Words: `research/staged544-mixed-fourth-entry/inputs/{THREE,FOUR}-{base,extra}.json.gz`.

Pricing logic: the moment is sum n_r r^(1-k) - 896*360*73^(1-k); at fixed rank mass, merging climbs
(H1+H2 -> H3) raises the root. A width-neutral local change applies to all 3240 calls with an
unchanged owner fill (≈ +1.6e-7 per H1+H2->H3, cf. #4085), so local-profile rewrites dominate any
fill-only gain (#4091 caps fill-only gains on the #4088 invoice at ≈ +1.14e-9).

## 1. Frame optimality of the current words
`opt_frames.py` (#4085 / Nick Petalas min-sum elimination) re-solves every frame of THREE-base and
FOUR-base: delta {} (691/701 variable nodes, 232/231 components). No free re-annotation gain.

## 2. Receiver/source sharing census (joint_fanout_search.py from #4085, max_gap 150, clusters <= 8)
Every candidate: exact covector identity over arbitrary dirty inputs, then full joint frame re-solve.

| word | section | family | candidates | frame-feasible | strict gain |
|---|---|---|---:|---:|---:|
| THREE-base | B | transposed (receiver sharing, `a+=b; c-=b -> a+=c; c-=b; a-=c` and ratios ±2^j) | 1346 | 940 | 0 |
| THREE-base | B | source sharing | 728 | 368 | 0 |
| THREE-base | restore | source sharing | 243 | 241 | 0 |
| THREE-base | restore | transposed | 32 | 32 | 0 |
| FOUR-base | B | transposed | 1326 | 920 | 0 |
| THREE-base | A (post-prelude) | transposed | 5,850 tried (stopped at time budget; index prefix only) | 5,813 | 0 |
| THREE-base | A (post-prelude) | source sharing | 2733 | 2630 | 0 |

The only receiver pair that pays on the PR3734 lineage (672/676 via 544, four variants of one stop)
is already used by #4085; the staged entries 600/608/609/601 created no new payable pair.

## 3. Retiming census (new: swap_search.py)
Move one add gate across a block of gates it commutes with exactly (t1!=s2, t2!=s1; warps/scales
only across disjoint registers), past the next 1..k gates that share a register (so some register's
frame chain is reordered), then re-solve all frames.

| word | section | k | moves | attempted (dedup) | frame-infeasible | strict gain |
|---|---|---:|---:|---:|---:|---:|
| THREE-base | restore | 3 | 269 | 211 | 4 | 0 |
| THREE-base | B | 3 | 3300 | 2909 | 1496 | 0 |
| THREE-base | A | 1 | 4038 | 3459 | 279 | 0 |

In a 100-move sample of B, every failure was graph infeasibility (fixed warp/centre/terminal anchors leave lo ⊄ hi), not solver capacity.

## 4. Staged entries (lever 1), why not pursued further
Helpers with four early ±1/4 target reads form Hadamard quads: {592,593,594,596}, {600,601,602,604},
{608,609,610,612}, {616,617,618}, {624,625,626}, {632,633,634}, {640,641,642} (+ 644/660 already staged
[429,30]). Each quad admits at most two stacked entries (release triads, #4076). More 8->7 narrowings
lose in the window-free LP (#4076: k=4 prices -9.06e-8; sink capacity ≈3.33 helpers); #4088 uses the
fractional 1/3 and #4091 proves that pooled ceiling. #4097 excludes 544 7->6 at its cut. A gain needs
a different width move (9->8 into a different sink) — not attempted here.

## Reproduce
```
python3.11 -B na/joint_fanout_search.py --word <word> --section B --transpose --out s/T-B-tr
python3.11 -B na/swap_search.py --word <word> --section B --out s/SW-B
```

## Credits and disclosure
Words, frame optimiser and fan-out search method from #4085 (zxv; Nick Petalas's joint fan-out search), #4076 and #3945 (rohanarun), #3949, and #4088 (1337isnot1337); #4091 (RossRichardson) gives the pooled-fill ceiling. `scripts/opt_frames2.py` adapts #4085's `opt_frames.py`; `scripts/swap_search.py` is new here. Search logs are in `logs/` (renamed `.txt` because the repository ignores `*.log`). Prepared by Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic) via Claude Code. Apache-2.0.
