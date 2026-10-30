# Master handoff — `research/p104-flag43-head-step-repair/`

## Candidate

- Branch: `cursor/dirty-restoration-repair-bill-eed4` (VictorLiwentao fork). The
  `-eed4` suffix is this worker's environment-required branch suffix, not `-60b9`.
- Content tip: `cc77db2b62d1eaa6a1f7b9ffec7e694a910bba54`. This is the scientific
  package commit, and its parent is the pinned base.
- Packaging tip: the child commit that adds only this handoff file. Read its SHA
  with `git rev-parse origin/cursor/dirty-restoration-repair-bill-eed4`.
- Package: `research/p104-flag43-head-step-repair/`
- Base: CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author: Wentao Li `<wentaol4@illinois.edu>`, with no co-author trailer.

## Claim

On present-head flag 43 (`X21` → `Y59`, head `15`), a changed schedule R0 makes
`Y59`'s last update co-host the basis head. That update is event 3364,
`Y59 += D17/4`, the ADD that settles `Y59`'s final `X21` coefficient `1/2`. It now
runs in the chart `[95,447,6,32,20,15]` while `X21` is in the full chart and still
has four later reads.

R0 keeps every published event in order, with the same ADDs and coefficients. It
retargets nine transports of `Y59`, `D17`, `Y103` and `D28`: each changed frame is
the published frame plus `15`. It also relabels three ADD charts.

The published `check_native.validate()` passes on the repaired word. Eight
published native edges are swapped for eight newly lowered ones. All 280 framed
rows, the 72 dirty-helper restorations and the 208 endpoint adapters hold.

**Bill.** Events (4,058), ADDs (2,624), transport occurrences (1,410), rank mass
(2,368) and distinct native edges (740) are all unchanged. The paid profile delta
is `-3H1 + 5H2 - H3 - H4`. The published ranks of the changed transports
majorize the repaired ranks, so the delta is at most zero under any convex
per-rank price and exactly zero under any affine one.

**Comparison R1.** R1 moves `Y103`'s 3365–3366 ahead of `Y59`'s update and adds
one rank-1 lift to `D17`. It changes only `Y59` and `D17`, at a cost of +1 event,
+1 transport occurrence and a `+2H2 - H4` profile delta. R1 is also natively
validated.

**Obstruction.** Consider repairs that keep the published event order and ADDs,
keep endpoint frames and add no rank mass; inserted refinement transports are
allowed. All 280 non-private registers sit at their rank floor, so every path in
this class stays monotone.

- 14 of `Y59`'s 15 updates force the head into a register whose final frame
  excludes it.
- 3364 is the only admissible update. It forces exactly `D17` and `Y59` (from
  3364), `Y103` (from 3366) and `D28` (from 3462).

Without inserted events, all nine retargeted transports are forced.

## Why this is not a chronology reprint

The headline is a constructed repaired word, its native validation and its bill.
The package cites, and does not re-derive, the drop/arrive chronologies of
#3456/#3451/#3443/#3392. The only fact it rechecks from #3456 is "no published
`Y59` update hosts the head", because the before/after comparison needs it.

## Evidence commands

```sh
python3.12 -I -B research/p104-flag43-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag43-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag43-head-step-repair/independent.py
python3.12 -I -O -Werror -B research/p104-flag43-head-step-repair/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag43-head-step-repair
```

Expected markers:

```text
PASS_P104_FLAG43_HEAD_STEP_REPAIR flag=43 head=15 repaired_update=3364 added_events=0 added_adds=0 added_transports=0 added_rank_mass=0 retargeted_transports=9 forced_registers=4 profile_delta=-3H1+5H2-H3-H4 native_validate=PASS earlier_updates_obstructed=14/14 no_new_kappa
PASS_P104_FLAG43_HEAD_STEP_REPAIR_INDEPENDENT flag=43 head=15 repaired_update=3364 added_events=0 added_adds=0 added_transports=0 added_rank_mass=0 retargeted_transports=9 forced_registers=4 profile_delta=-3H1+5H2-H3-H4 rows_equal=280/280 earlier_updates_obstructed=14/14 no_new_kappa
PASS_P104_FLAG43_HEAD_STEP_REPAIR_TESTS cases=14 clean_read_only=1 scanners=2
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag43-head-step-repair outcome=completed
```

The worker ran all five commands on the content tip in the working tree. It ran
the registered package command again in a fresh detached worktree of the pushed
content tip. The runs leave the package and the pinned inputs byte-identical.
`research_package.py --changed-since <base> --check-only` selects only this
package.

## Closest priors

- #3456 `p104-present-head-flag43-audit`: flag 43's published obstruction. Its
  first open question is answered here, following its suggested first step at
  3363/3364 and the `D17` common-chart constraint. Leave its chronology alone.
- #3451 (flag 1) and #3443 (flag 9): the same open question on other flags. Not
  touched.
- #3349: present-head census. Reused, not re-derived.
- #3363: relay census and final coefficients. This package reports only the `X21`
  entries of the three `Y59` reads, which the co-hosting statement needs.
- Merged `p104-refinement-rank-budget` and `p104-single-target-acquisition`:
  priced added transports and refinements in a different model, namely identity
  completion. They are not reused for any number here.

## Soft-overlap risks

- #3363: the event-level delivery split (`+1/2` at 3076, `-1/2` at 3231, `+1/2`
  at 3364) is a coefficient fact on #3363's turf. A reviewer may ask that the
  `R0_source_delivery_into_target` field be cited to #3363 or trimmed.
- #3456: R0 changes four registers' published frames. Any statement in #3456
  about the published word stays true, because only the repaired word differs.
- `Y103` and `D28` are not flag-43 endpoints. Changing their frames could matter
  to a future package about flags that target `Y103`. The class-Z table shows that
  these changes are forced, not chosen.
- `H_r` is left symbolic. If the repo's actual per-rank weights are strictly
  concave on `{1,...,4}`, R0 costs `5H2 - 3H1 - H3 - H4 > 0`. The package does
  not evaluate those weights.
- R1 reorders two reads of `D17`. That is legal under the checker, but it sits
  outside the class-Z obstruction by design.

## Open questions

1. Do flags 1 and 9 admit an event-preserving head-step repair, or are their
   closures obstructed? Use a separate package and cite #3451/#3443.
2. Can a side correction exploit R0's co-hosted head chart at 3364, and what
   does `I - G/2` cost at that cut?
3. Is R0's profile majorization-minimal among class-Z repairs?

## Disposition note for master

This worker produces a fork branch and package only. Do **not** open a CrocSwap
PR from this worker. Master decides whether to publish or defer after an
independent skeptical review.
