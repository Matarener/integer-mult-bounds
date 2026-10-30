# Master handoff — `research/p104-present-head-side-correction-forcing-census/`

## Candidate

- Branch: `cursor/present-head-forcing-census-6ab7`
- Content tip: scientific package at `293b90598af0e7632cdd398da7171c509091f17e`; master path-fix commit is the packaging tip (read with `git rev-parse origin/cursor/present-head-forcing-census-6ab7`).
- Package: `research/p104-present-head-side-correction-forcing-census/`
- Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap `main`)
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged `0.001672660197076918`
- Master repair: `test_package.py` used a hardcoded `/workspace` root for pin/corruption fixtures; replaced with `HERE.parents[1]` so gates pass from any worktree.

## Claim

On the published native-channel word, all 18 checked present-head strict
`I−G/2` side-correction entries among flags `{1,9,43}` (primary + five
extra off-diagonal nonzero Gram sources per target row) have every
insertion-class zero-mass placement obstructed and therefore need
non-private floor `+2`. No counterexample. Primary feeders:
`X7:387` (flag 1), `X58:333` (flag 9), `X12:131` (flag 43).

## Closest priors (leave alone)

- [#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601) flag-43 side-correction bill — cite sample `(59,21)` / feeder 131; do not reprint bill.
- [#3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610) flag-1 side-correction bill — cite sample `(7,0)` / feeder 387; do not reprint bill.
- [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) / [#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) head-step repairs — leave alone.
- [#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443) flag-9 chronology — published word only; deferred head-step repair not reopened.

## New checkable fact

Cross-entry obstruction census: 18/18 need `+2`, including flag 9's
published-word feeder `X58` head `333` at leave event 745. Answers OQ2
of #3601/#3610 without cloning their verify bill builders.

## Evidence commands

```sh
python3.12 -I -B research/p104-present-head-side-correction-forcing-census/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-forcing-census/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-forcing-census/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-forcing-census/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-side-correction-forcing-census
```

Expected markers:

```text
PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FORCING_CENSUS flags={1,9,43} entries=18/18 need_plus_two primary_feeders=X7:387,X58:333,X12:131 no_new_kappa
PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FORCING_CENSUS_INDEPENDENT flags={1,9,43} entries=18/18 need_plus_two primary_feeders=X7:387,X58:333,X12:131 no_new_kappa
PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FORCING_CENSUS_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-present-head-side-correction-forcing-census outcome=completed
```

## Soft-overlap risks

- Scientific novelty is the multi-entry obstruction census + flag-9 feeder,
  not file clones of #3601/#3610 bill builders (those are not imported).
- Do not reopen deferred `research/p104-flag9-head-step-repair/`.
- Do not edit open #3610/#3601/#3532/#3508 packages.

## Open questions

1. Full-row extension beyond the 18-entry sample on Y7/Y23/Y59.
2. Flag-9 end-cut side-correction bill / private-copy discount on the
   published word (fallback card; still no co-hosted repair).

## Disposition note for master

Worker produces fork branch + package only. Do **not** open a CrocSwap PR
from this worker. Master decides publish/defer after independent skeptical
review.
