# Master handoff — `research/p104-present-head-flag0-audit/`

## Candidate

- Branch: `cursor/p104-present-head-flag0-audit-60b9` (VictorLiwentao fork)
- Content tip: `ebcc53a61625a0fea7f2b63dc6a4f124161513a9` (scientific package commit)
- Branch tip: this commit on `cursor/p104-present-head-flag0-audit-60b9` (`git rev-parse HEAD`)
- Package: `research/p104-present-head-flag0-audit/`
- Base: CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged `0.001672660197076918`

## Claim

On published present-head flag 0 (`X0` → `Y34`, basis head `232`), the head
enters `Y34`'s frame, listed and in GF(2) span, only at `Y34`'s terminal
transport after-frame (event 3500). All fifteen `Y34` adds (last one at event
3369) run in head-free charts. `X0`'s literal drop at event 591 is a nested
chart change that keeps `232` in span (`8 ^ 32 ^ 64 ^ 128`). No `Y34` event
occurs while both endpoints host the head direction, so chronological dirty
restoration cannot use co-hosted basis-head geometry on this coefficient-cascade
target ahead of the published `I-G/2` tail add.

## Why flag 0 now

#3451 leaves flag 0 to the coefficient cascade on `Y34`. Open #3575 already
pins the literal arrive at 3500 and the empty forward Q-relay, but does not
check GF(2) span hosting, head-free update counts, or nested-transport
semantics. The span reading is the dirty-restoration fact: at event 3500, `X0`
is already on the coordinate basis (does not list `232`) yet still spans it, and
all 15/15 `Y34` updates precede that first span co-hosting.

## New checkable facts beyond #3575's literal relay cut

- Span-level hosting: zero source span drops (22 of 22 `X0` annotations span
  `232`), and zero preterminal `Y34` span hosting.
- Target-update chronology: 15 of 15 `Y34` row updates run in head-free charts,
  and there are 0 `Y34` events after the head enters `Y34`'s span.
- Frame semantics check: all 11 endpoint transports are nested upward, and each
  paid rank equals the rank increase.
- Literal facts aligning with #3575: `preterminal_hosting=0`, `drop_event=591`,
  `arrive_event=3500`, `hosting_gap_events=2909`, zero joint events, both frames
  unrestored.

## Evidence commands

```sh
python3.12 -I -B research/p104-present-head-flag0-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag0-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag0-audit/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-flag0-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-flag0-audit
```

Expected markers:

```text
PASS_P104_PRESENT_HEAD_FLAG0 flag=0 head=232 preterminal_hosting=0 preterminal_span_hosting=0 drop_event=591 arrive_event=3500 source_span_drops=0 head_free_target_updates=15/15 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG0_INDEPENDENT flag=0 head=232 preterminal_hosting=0 preterminal_span_hosting=0 drop_event=591 arrive_event=3500 source_span_drops=0 head_free_target_updates=15/15 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG0_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-present-head-flag0-audit outcome=completed
```

## Closest priors / soft-overlap vs leave-alones

- Open #3575 `p104-flag0-relay`: literal relay cut; soft-overlap on drop/arrive
  numbers; this package adds the span/dirty-restoration obstruction and does not
  recompute Q-relay emptiness.
- #3451/#3443/#3456 present-head chronologies for flags 1/9/43: leave alone;
  method kinship only; different target/arrive/update counts.
- #3601/#3610/#3614/#3618/#3621 present-head side-correction bills: leave alone;
  this package prices no `I-G/2` rank mass.
- `research/p104-tail-flag0-*` coefficient cascade: leave alone as coefficient
  receipts; this package recomputes no coefficient and does not read the tail.
- C5 charging #3643/#3639 and deferred router-rho / class-only `S_leaf=1`:
  disjoint.

## Open questions

1. Can a changed schedule bring `232` into `Y34`'s span before the add at event
   3369, while `X0` is still live, and what does that add to the channel bill
   ahead of event 5759?
2. Does the published promote/add/restore at 5758/5759/5807 admit an owner/host
   schedule for the `X0` read that restores arbitrary dirt without repaying the
   unrestored channel endpoints?

## Disposition note for master

The worker produces a fork branch and package only. Do **not** open a CrocSwap
PR from this worker. Master decides publish or defer after independent
skeptical review.

## Attribution check

Author Wentao Li `<wentaol4@illinois.edu>`. Neutral disclosure: substantial AI
assistance. Tip commit message must not contain `Co-authored-by: Victor Li`.

## Verified PASS lines

Replayed on content tip `ebcc53a61625a0fea7f2b63dc6a4f124161513a9`:

```text
PASS_P104_PRESENT_HEAD_FLAG0 flag=0 head=232 preterminal_hosting=0 preterminal_span_hosting=0 drop_event=591 arrive_event=3500 source_span_drops=0 head_free_target_updates=15/15 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG0_INDEPENDENT flag=0 head=232 preterminal_hosting=0 preterminal_span_hosting=0 drop_event=591 arrive_event=3500 source_span_drops=0 head_free_target_updates=15/15 no_new_kappa
PASS_P104_PRESENT_HEAD_FLAG0_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-present-head-flag0-audit outcome=completed
PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)
```

`git log -1 --format=%B` on every tip commit of this branch has no
`Co-authored-by: Victor Li`. Author Wentao Li `<wentaol4@illinois.edu>`.

