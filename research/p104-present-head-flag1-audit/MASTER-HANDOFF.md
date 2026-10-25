# Master handoff — `research/p104-present-head-flag1-audit/`

## Candidate

- Branch: `cursor/p104-present-head-flag1-60b9` (VictorLiwentao fork)
- Content tip: `112436d9be29b668c9306901843c440dafac3755` (scientific package
  commit; parent is the pinned base)
- Packaging tip: the child commit that adds only this handoff file. Read its SHA
  from `git rev-parse origin/cursor/p104-present-head-flag1-60b9`.
- Package: `research/p104-present-head-flag1-audit/`
- Base: CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged `0.001672660197076918`

## Claim

On published present-head flag 1 (`X0` → `Y7`, basis head `232`), the head
enters `Y7`'s frame, listed and in GF(2) span, only at `Y7`'s terminal transport
after-frame (event 3473). All six `Y7` adds (last one at event 2797) run in
head-free charts. `X0`'s literal drop at event 591 is a nested chart change that
keeps `232` in span (`8 ^ 32 ^ 64 ^ 128`). No `Y7` event occurs while both
endpoints host the head direction, so chronological dirty restoration cannot use
co-hosted basis-head geometry on this word.

## Why flag 1 and not flag 43

The brief said to switch to flag 43 only if flag 1 reprinted flag 9's numbers.
It does not. Flag 1 has drop 591, arrive 3473 and gap 2882. Flag 9 has drop 500,
arrive 3489 and gap 2989. The target, the head and the frames also differ. Flag
43 (`X21` → `Y59`, head `15`, drop 570, arrive 3525) is uncertified and remains
available.

## New checkable facts beyond #3443's method

- Span-level hosting: zero source span drops (22 of 22 `X0` annotations span
  `232`), and zero preterminal `Y7` span hosting (largest preterminal span
  `{0, 95, 441, 486}`).
- Target-update chronology: 6 of 6 `Y7` row updates run in head-free charts,
  and there are 0 `Y7` events after the head enters `Y7`'s span.
- Frame semantics check: all 8 endpoint transports are nested upward, and each
  paid rank equals the rank increase.
- Literal facts mirroring #3443: `preterminal_hosting=0`, `drop_event=591`,
  `arrive_event=3473`, `hosting_gap_events=2882`, zero joint events, both frames
  unrestored.

## Evidence commands

```sh
python3.12 -I -B research/p104-present-head-flag1-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag1-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag1-audit/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-flag1-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-flag1-audit
```

Expected markers:

```text
PASS_P104_PRESENT_HEAD_FLAG1 flag=1 head=232 preterminal_hosting=0 preterminal_span_hosting=0 drop_event=591 arrive_event=3473 source_span_drops=0 head_free_target_updates=6/6 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG1_INDEPENDENT flag=1 head=232 preterminal_hosting=0 preterminal_span_hosting=0 drop_event=591 arrive_event=3473 source_span_drops=0 head_free_target_updates=6/6 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG1_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-present-head-flag1-audit outcome=completed
```

## Closest priors

- #3443 `p104-present-head-flag9-audit`: the method mirrored here, on flag 9
  (leave alone).
- #3349 `p104-channel-touch-restoration-audit`: names the present-head class
  `(0, 1, 9, 43)`, including `(X0, Y7, 232)`. It does not give `Y7`'s
  chronology.
- #3392 `p104-absent-head-flag2-audit`: the complementary absent-head case
  (leave alone).
- Merged #3242 `p104-flag-channel-schedule`: already records `X0` first touched
  at 591 on `[232]` and zero joint events for every matched pair.

## Soft-overlap risks

- Flag 1 shares source `X0` and head `232` with flag 0. So the source-side drop
  event 591 is the same one #3242 records for flag 0. The flag-0 coefficient
  cascade (#3363/#3365/#3371/#3372/#3412) is about coefficients and `Y34`. This
  package recomputes no coefficient and says nothing about `Y34`. #3363's census
  of relay deliveries over all 208 flags implicitly includes flag 1's delivery
  coefficient. This package does not restate it.
- The span reading cuts against #3443's wording. A one-line check (`196 = 132 ^
  64`, with both in the event-500 after-frame `[8, 64, 132, 260]`) suggests
  flag 9's "source drop" is also only a chart change. Consider adding a limits
  note to #3443 before publishing either package. This package does not certify
  flag 9.
- Do not extend this to flags 0, 9 or 43 in the same PR without a new fact.

## Open questions

1. Can a changed schedule bring `232` into `Y7`'s span before the add at event
   2797, while `X0` is still live, and what does that add to the channel bill?
   The common-chart rule means `D17`'s frame at that add must move too.
2. Do flags 9 and 43 show the same span pattern (the source keeps the head and
   the target gains it only at its terminal transport)? If so, the present-head
   obstruction is a target-side property.

## Disposition note for master

The worker produces a fork branch and package only. Do **not** open a CrocSwap
PR from this worker. Master decides publish or defer after independent
skeptical review.
