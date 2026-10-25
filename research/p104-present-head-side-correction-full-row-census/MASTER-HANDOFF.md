# Master handoff — `research/p104-present-head-side-correction-full-row-census/`

## Candidate

- Branch: `cursor/present-head-full-row-census-ad52`
- Package: `research/p104-present-head-side-correction-full-row-census/`
- Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap `main`)
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged `0.001672660197076918`
- Content tip: `42e62a310eb3a4cf80488506ff6baff1d53addd6` (scientific package; dual scanners + certificate)
- Branch tip at handoff write: `6144f5736a8d6a79a934f4429fc7cf086f58b9ca` (re-read `git rev-parse origin/cursor/present-head-full-row-census-ad52`)

## Claim

On the published native-channel word, all 144 off-diagonal nonzero Gram
strict `I−G/2` side-correction entries on present-head rows `Y7`/`Y23`/`Y59`
(flags `{1,9,43}`; 48 sources per row) have every insertion-class
zero-mass placement obstructed and therefore need non-private floor `+2`.
No counterexample. Primary feeders unchanged from #3614:
`X7:387` (flag 1), `X58:333` (flag 9), `X12:131` (flag 43). Answers OQ1
of open [#3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614).

## Closest priors (leave alone)

- [#3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614) 18-entry sample + primary feeders — cite; method extended to full rows; do not clone package.
- [#3618](https://github.com/CrocSwap/integer-mult-bounds/pull/3618) flag-9 side-correction bill — leave alone; do not reprint.
- [#3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610) / [#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601) primary bills — leave alone.
- [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) / [#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) head-step repairs — leave alone.
- Deferred `research/p104-flag9-head-step-repair/` — do not reopen.

## New checkable fact

Row-complete obstruction census: 144/144 need `+2`, covering the #3614
18-entry sample as a named subset (`in_pr3614_sample`) and the remaining
126 off-diagonal nonzero Gram sources on the three present-head rows.

## Evidence commands

```sh
python3.12 -I -B research/p104-present-head-side-correction-full-row-census/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-full-row-census/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-full-row-census/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-full-row-census/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-side-correction-full-row-census
```

Expected markers:

```text
PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FULL_ROW_CENSUS flags={1,9,43} entries=144/144 need_plus_two primary_feeders=X7:387,X58:333,X12:131 no_new_kappa
PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FULL_ROW_CENSUS_INDEPENDENT flags={1,9,43} entries=144/144 need_plus_two primary_feeders=X7:387,X58:333,X12:131 no_new_kappa
PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FULL_ROW_CENSUS_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-present-head-side-correction-full-row-census outcome=completed
```

## Soft-overlap risks

- Soft-overlap with #3614 is intentional method extension (row-complete
  coverage). Novelty is the 144-entry theorem, not a file clone of the
  18-entry package. Scanners share frame/`need` idiom only.
- Do not edit open #3614/#3618/#3610/#3601/#3532/#3508 packages.
- Do not reopen deferred `research/p104-flag9-head-step-repair/`.
- Independent of bill builders (no import of their verify modules).

## Open questions

1. Private-copy / co-hosted discount on any of the 126 non-primary
   full-row entries.
2. Same row-complete floor for present-head flag 0 once the cascade
   commits a cut (absent-head flag 2 remains leave-alone #3392).

## Disposition note for master

Worker produces fork branch + package only. Do **not** open a CrocSwap PR
from this worker. Master decides publish/defer after independent skeptical
review.
