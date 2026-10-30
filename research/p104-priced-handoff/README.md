# One priced successor hand-off on PR5561's P104 word (conditional kappa .00308181)

Complete conditional kappa **.00308181** (certified claim line; tested at .0030818105). The raw crossing is
.0030818185, which is **+3.94e-7** (+0.0128%) over the raw crossing .0030814243 of
[PR5561](https://github.com/CrocSwap/integer-mult-bounds/pull/5561) (claim line .00308142). The exact raw crossing lies in
(154090925761/50000000000000, 308181851523/100000000000000) = (.00308181851522, .00308181851523).

**Conditional on** the same assumptions as PR5561:
(a) the five framework assumptions retained by PR5544/5545/5551;
(b) the validity of PR5551 and PR5561, neither independently reproduced at the time of writing;
(c) free helper FINAL frames. The edit lowers one helper final frame from dim 9 to dim 8, as PR5561's headline
word does for 23 helpers. It needs no new start frame.
The selected record is not changed. No independent human or proof-kernel acceptance is claimed.

## Mechanism (successor hand-off with one co-framed partner)

This is the successor hand-off of PR5472 with **co-framed cancellation** (R18 notation), priced with the
re-flagging cost of the R19 addendum. Helper 706 has initial dim 0 and final dim 9 in PR5561's headline word.
- **Last read.** Event 15443 (`ADD 121 += -2*706`, frame 549, dim 7) is its last read. From then on its row is
  `706 + D`, and no other register holds symbol 706.
- **The only remaining use.** `MOVE 706 549->127` (rank 2), then the uncompute `ADD 706 += -1/2*173` at frame
  127 (dim 9).
- **The partner.** Main register 173 (Y target of port 61) sits at frame 559 (dim 8, 549 < 559 < 127) from event
  13089 until event 17248. Its row is constant after event 13097, so `-1/2*row(173) = -D` already holds at
  event 15443.

The successor hand-off at F = 559:
1. 706 climbs to F (`MOVE 549->559`, rank 1).
2. 706 cancels D against the co-framed partner (`ADD 706 += -1/2*173 @559`).
3. 706 retires at F.

The successor would start at F and carry nothing up to dim 9. It would be a rank-1 spectator: one rank-1 target
and one rank-1 climb, which is moment-neutral, like PR5553's "Variant A". It is therefore omitted. The literal
edit (`handoff.py`) is:

| | PR5561 headline word | this word |
|---|---|---|
| after event 15443 | (idle) | `MOVE 706 549->559`, `ADD 706 += -1/2*173 @559` |
| events 17251/17252 | `MOVE 706 549->127`, `ADD 706 += -1/2*173 @127` | deleted (moved) |
| `final[706]` | frame 127 (dim 9) | frame 559 (dim 8) |
| events / public inputs | 25,140 / 735 | 25,140 / 735 (same scalar events; one ADD moved and relabelled) |

Per call, credited helper 706 drops from rank 9 to rank 8, and one paid rank-2 climb becomes rank 1. The
rank-mass surplus stays 760, productive fields stay 12,814 and paid calls stay 66,852.

Seen as a hand-off, the gain is g(8,1) = f(8)+f(1)−f(9) = 0.009632 and the re-flagging cost (the helper's own
new stop 7->8->9) is g(1,1) = 0.004267. That leaves a net +0.005365 per call at f(x) = x^(1−C), C = .0030814,
which is strict at all 18 calls.

## Exhaustive screen (tools/, outputs `tools/*.txt`)

All screens run on PR5561's headline word and cover every non-main helper (527), every event and every mid frame
F with dim strictly between the helper's initial and final dims.

| family | tool | result |
|---|---|---|
| free hand-off (helper pure, no other holder; PR5553's form) | `screen.py` | 0 on PR5561. Control: exactly PR5553's two (473 at ev 13725, 531 at ev 13941) on PR5551's word |
| co-framed span hand-off at existing frames | `screen2.py` | 0 (800 holder-co-framed points; span fails) |
| frame-independent mid-life pure windows | `windows.py` | 0: on this scalar program, free hand-offs are only endpoint retimes, which PR5561's free starts and finals already absorb |
| priced: all holders co-framed with lifts at any nested F, plus span closure over co-frameable registers | `lift21.py` | 589,992 (helper, event) points. 81 span-feasible with holders only: all net < 0 (best −0.00051; each needs a new stop on the helper, so cost ≥ gain). 24 more span-feasible after closure: exact frame-identity pricing leaves 1 net > 0 (this one) |
| priced single partner (row(j) ∝ carried D), every event and any nested F, both via chain frames and via generic F | `partner.py` | 1,086 matches; **1 net > 0** (706/173 at F = 559) |

Scope of the screen:
- 2,832 points where an owned private scratch register (735..742) holds the helper symbol were skipped.
- Multi-partner closures are priced greedily (`lift21.py`), so they give an upper bound on the minimal-cost
  closure.
- The same single candidate is also present on PR5561's starts-only word and on PR5551's word. PR5553 found only
  the free ones.

The orientation is forward only. The P104 caller invokes every source forward (`pricing.py` requires it).

**Independent second check (outside the package).** The checker of PR5550 (Chris R / Clear1nsight) was patched
exactly as in PR5567 (Matarener: four literal input lines, temporary copy) and run on `WORD.json.gz` with this
package's invoice. It returns `PASS_SCOPED_CALLER_AND_TARGET_BINDING`:
- 66,852 paid / 12,814 productive;
- 527 helper normalizers and 274 exact signed-Pauli and phase anchors;
- all 10 controls reject;
- 124,232,680 ordinary passes ≤ 184,647,552.

The unchanged PR5561 paid invoice is rejected on this word. PR5567 also argues that free helper endpoints are the
contract the unmodified P104 `local.py` implements, which bears on condition (c).

## Files
- `handoff.py`: derives `WORD.json.gz` from `inputs/pr5561-WORD.json.gz`, with byte-exact regeneration checked.
- `pricing.py`: PR5561's `pricing.py` (`inputs/pr5561-pricing.py`) with only the KAPPA/TESTED claim line and the
  `kappa_decimal` label changed (`LITERAL-CHANGES.diff`). The unmodified PR5545 `local.py` is used from the
  byte-pinned capsule (735 public inputs).
- `verify.py` / `verify.sh` (stdlib, Python 3.12, about 4 minutes):
  - input pins and regeneration;
  - the edit inventory against PR5561's word;
  - the exact hand-off condition (rational rows: sole holder, `row(706) = 706 + 1/2 row(173)`, partner row
    constant until the original uncompute, frames 549 < 559 < 127);
  - the unmodified PR5545 replay, transposed columns and native maps;
  - the physical caller;
  - both moment engines;
  - all 54 strict + 4 functional outer checks;
  - the exact crossing interval;
  - four mutation controls, each rejected by `local.py`: no stop, wrong coefficient, final not lowered, and the
    hand-off placed before the last read.
- `tools/`: the screens above, with `run_screens.sh` and the recorded outputs.
- `inputs/`: PR5561's headline word and pricing, and the PR5545 capsule. All are byte-pinned (`SOURCES.json`).

## Reproduce
```sh
python3.12 -B scripts/research_package.py --package research/p104-priced-handoff
sh research/p104-priced-handoff/verify.sh          # PASS P104_PRICED_HANDOFF
sh research/p104-priced-handoff/tools/run_screens.sh
```

## Credits
- DreamingOfClouds: PR5561 (free helper endpoints, the base word) and PR5553 (free hand-offs on PR5551).
- thu-nmrc: PR5551 (coupled P104 contacts).
- aliromman: PR5544/5545 (P104 word line, `local.py`).
- Lineage: PR2305/2152/2219. The credits in `local.py` (David Arias, Cinna Davis, Gareth Davidson) are retained.
- zxv: productive-helper paradigm #4359; PR5554 regime limits.
- Cao Yifan: #4610 native semantics.
- PR5472 (GamingPuzzled): the successor hand-off and its R18/R19 pricing.
All predecessor credit is retained.

AI disclosure: Claude Opus 5.5 (Anthropic) via Claude Code, directed by Joel Pulikkan (GamingPuzzled). Apache-2.0.

## Open next questions

- Are free helper final frames admissible? This package inherits PR5561's condition (c).
- Do owned private scratch holders (registers 735..742) admit further priced hand-offs? The screen skipped 2,832
  such points.
- Can a joint retime and hand-off solve, in which PR5561's CP-SAT lattice also lets ADDs move within their idle
  windows, find more co-framed partners? On the fixed PR5561 frames, only one net-positive hand-off exists.
