# Master handoff — `research/p104-present-head-flag43-audit/`

## Candidate

- Branch: `cursor/p104-present-head-flag43-1d68` (VictorLiwentao fork). The
  suffix is this worker's required branch suffix, not `-60b9`.
- Content tip: `5889fe1591f689c3003e2f92c9258d79c97bdee3` (scientific package
  commit; parent is the pinned base)
- Packaging tip: the child commit that adds only this handoff file. Read its SHA
  from `git rev-parse origin/cursor/p104-present-head-flag43-1d68`.
- Package: `research/p104-present-head-flag43-audit/`
- Base: CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged `0.001672660197076918`

## Claim

On published present-head flag 43 (`X21` → `Y59`, basis head `15`), the head
enters `Y59`'s frame, listed and in GF(2) span, only at `Y59`'s terminal rank-3
transport after-frame (event 3525). All 15 `Y59` adds (last one at event 3364)
run in head-free charts; ten run in the empty chart. `X21`'s literal drop at
event 570 is a nested chart change that keeps `15` in span (`3 ^ 4 ^ 8`). No
`Y59` event occurs while both endpoints host the head direction, so
chronological dirty restoration cannot use co-hosted basis-head geometry on this
word.

New on this flag: `Y59`'s last two updates (3231, 3364) run in charts that
already span the flag's non-head basis vectors `{32}` and `{6, 18, 32}`, and
`X21`'s live rank-9 frame spans them too. Both endpoints co-host part of the
flag basis while the target is still updated; only the head is missing.

## Why flag 43 and no DEFER

The brief said to defer to the ordinary-leaf fallback only if flag 43 reprinted
flag 1 or flag 9. It does not: drop/arrive/gap is 570/3525/2955 against
591/3473/2882 (#3451) and 500/3489/2989 (#3443). Both scanners carry those two
tuples and refuse to admit an equal one (`test_reprint_guard` checks this). The
target has 15 updates and 6 transports (flag 1's `Y7`: 6 and 3). Flag 43 is also
the only present-head flag with `arrival_choice = 0` in the #2981 certificate
(flags 0, 1 and 9 have 1); this is context and is not certified here.

Honest caveat: `X21`'s source schedule has the same shape as #3451's `X0`
(17 events, 22 annotations, five transports, rank 1 to 9). The source-span fact
is therefore close to a template repeat; the new content is the target-side
chronology and the tail co-hosting.

## New checkable facts beyond #3451's method

- Span-level hosting: zero source span drops (22 of 22 `X21` annotations span
  `15`), zero preterminal `Y59` span hosting (largest preterminal span has 32
  elements and excludes `15`).
- Target-update chronology: 15 of 15 `Y59` updates in head-free charts (10 empty,
  5 non-empty of ranks 1–5), 0 `Y59` events after the head enters `Y59`'s span.
- Tail co-hosting: first tail vector in `Y59`'s span at event 3230 (after);
  updates 3231 and 3364 co-host `{32}` and `{6, 18, 32}` with `X21`'s live
  frame, which is replayed with a before-frame continuity check.
- Source discipline: `X21` is never an add destination; its four events after
  3525 are reads; no endpoint `zero`/`copy`/`erase` event.
- Frame semantics: all 11 endpoint transports nested upward with paid rank equal
  to the rank increase; `Y59` steps `1, 1, 1, 1, 1, 3`.
- Reprint guard: both scanners need the flag-43 tuple to differ from the
  published flag-1 and flag-9 tuples.

## Evidence commands

```sh
python3.12 -I -B research/p104-present-head-flag43-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag43-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag43-audit/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-flag43-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-flag43-audit
```

Expected markers:

```text
PASS_P104_PRESENT_HEAD_FLAG43 flag=43 head=15 preterminal_hosting=0 preterminal_span_hosting=0 drop_event=570 arrive_event=3525 source_span_drops=0 head_free_target_updates=15/15 tail_cohosting_updates=2 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG43_INDEPENDENT flag=43 head=15 preterminal_hosting=0 preterminal_span_hosting=0 drop_event=570 arrive_event=3525 source_span_drops=0 head_free_target_updates=15/15 tail_cohosting_updates=2 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG43_TESTS groups=7
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-present-head-flag43-audit outcome=completed
```

The worker ran all five on the content tip in the working tree and again in a
fresh detached checkout of the pushed branch. Runs leave the package and pinned
inputs byte-identical. `research_package.py --changed-since <base>` selects only
this package.

## Closest priors

- #3451 `p104-present-head-flag1-audit`: the span method mirrored here, on flag 1
  (leave alone). Its second open question asked whether flag 43 follows the same
  span pattern; this package answers yes for flag 43.
- #3443 `p104-present-head-flag9-audit`: the literal method, on flag 9 (leave
  alone).
- #3349 `p104-channel-touch-restoration-audit`: names `(21, Y59, 15)` as a
  present-head triple and records unrestored endpoint frames. It gives no `Y59`
  chronology.
- #3392 `p104-absent-head-flag2-audit`: the complementary absent-head case
  (leave alone).
- Merged #3242 `p104-flag-channel-schedule`: zero joint events for every matched
  pair; its worked receipt is flag 0 only.

## Soft-overlap risks

- #3363 (relay census over all 208 flags) implicitly includes flag 43's delivery
  coefficient. This package recomputes no coefficient and does not name the
  delivering add. PROOF.md states, conditionally and uncertified, that any
  delivery into `Y59` must occur at one of the 15 head-free adds. A reviewer may
  prefer that remark removed.
- #3365/#3371/#3372/#3412 (flag-0 cascade on `Y34`): untouched; flag 43 shares
  neither source nor target with flag 0.
- #3349: items on unrestored frames and the present-head triple are reused, not
  re-derived as new.
- #3451/#3443: the reprint guard hard-codes their published tuples as constants.
  It does not recompute flags 1 or 9. The tail-co-hosting contrast with flag 1
  reads #3451's certificate (`{0, 95, 441, 486}`) and is not re-derived.
- Do not extend this to flags 0, 1 or 9 in the same PR.

## Open questions

1. Can a changed schedule bring `15` into `Y59`'s span at or before the add at
   event 3364, while `X21` is still live, and what does that add to the channel
   bill? The head is one rank step from the chart at 3364, and the common-chart
   rule means `D17`'s frame at that add must move too.
2. Is tail-before-head hosting specific to flag 43 among the present-head flags,
   and does it occur on absent-head flags? A separate census should cite
   #3451/#3443/#3392 rather than re-certify them.

## Disposition note for master

The worker produces a fork branch and package only. Do **not** open a CrocSwap
PR from this worker. Master decides publish or defer after independent
skeptical review.
