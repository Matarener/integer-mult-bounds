# Master handoff — `research/p104-present-head-flag9-audit/`

## Candidate

- Branch: `cursor/p104-present-head-flag9-60b9`
- Content tip: `ae18b8db189f777bef159530d5395ebfe024f7b1` (scientific package commit)
- Package: `research/p104-present-head-flag9-audit/`
- Base: `6f100d4bb5083f8c35d96fd95a539811c62f245c`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged `0.001672660197076918`

## Claim

On published matched flag 9 (`X4`→`Y23`, basis head `196`), the channel drops
the head from the source at event 500 and introduces it on the matched target
only at the terminal transport after-frame at event 3489 (gap 2989), with zero
preterminal target hosting, zero joint endpoint events, and unrestored frames —
so chronological dirty restoration cannot use co-hosted basis-head geometry.

## Closest priors

- #3349 `p104-channel-touch-restoration-audit` — full restoration census; names
  present-head class `(0,1,9,43)`; leaves coefficient/dirty restoration open.
- #3392 `p104-absent-head-flag2-audit` — complementary absent-head obstruction
  on flag 2 (leave alone).
- #3363/#3365/#3371/#3372 — algebraic coefficient delivery (flag-0 cascade);
  soft-overlap checked; different obligation.
- #3242 — chronology receipt for worked pair X0/Y34.

## New checkable fact

Present-head flag 9 has `preterminal_hosting=0`, `drop_event=500`,
`arrive_event=3489`, `hosting_gap_events=2989`. A maintainer can replay without
reopening #3349's census or #3392's absent-head path.

## Evidence commands

```sh
python3.12 -I -B research/p104-present-head-flag9-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag9-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag9-audit/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-flag9-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-flag9-audit
```

Expected markers:

```text
PASS_P104_PRESENT_HEAD_FLAG9 flag=9 head=196 preterminal_hosting=0 drop_event=500 arrive_event=3489 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG9_INDEPENDENT flag=9 head=196 preterminal_hosting=0 drop_event=500 arrive_event=3489 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG9_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-present-head-flag9-audit outcome=completed
```

## Soft-overlap risks

- Flag-0 cascade (#3363–#3412) stays clear: this package pins flag 9 / Y23 / X4.
- Do not extend to flags 0/1/43 in the same PR without a new fact.
- Do not reopen #3349 restoration census or #3392 flag-2 path.
- Coefficient delivery is deliberately not claimed (already open elsewhere).

## Open questions

Can a changed schedule co-host 196 on X4 and Y23 long enough to dirty-restore,
and at what cost?

## Disposition note for master

Worker produces fork branch + package only. Do **not** open a CrocSwap PR from
this worker. Master decides publish/defer after independent skeptical review.
