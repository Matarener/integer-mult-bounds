# Master handoff — `research/p104-flag0-tail-owner-host/`

## Candidate

- Branch: `cursor/flag0-tail-owner-host-60b9` (VictorLiwentao fork).
- Content tip: `01cbbe345` (scientific package commit; parent = pinned base).
- Packaging tip: branch HEAD (`git rev-parse HEAD` on this branch).
- Package: `research/p104-flag0-tail-owner-host/`
- Base: CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no
  `Co-authored-by: Victor Li` trailer (`git -c core.hooksPath=/dev/null commit`).
- **Do not open a CrocSwap PR** — master publishes.

## Claim

On present-head flag 0, the published promote/add/restore at 5758/5759/5807
admits self-owned host schedule S0 (`owner=X0` on `FULL`) for the `X0` read:
unique among event-named registers, zero dirty-helper touches in the window,
zero endpoint repayment toward initials, and pre-read `X0` restoration blocked
by the published common-chart annotation. Answers #3669 OQ2. No new kappa.

## Why this is not a chronology / repair-template reprint

Headline is an owner/host **assignment** plus dirt and endpoint-repayment
checks on the #2089 tail word. It does not reprint #3669's drop/arrive
chronology, does not retarget the #3532/+2 head-span repair template, and does
not price event-3369 co-hosting. Prior jwr404 packages show frames/coefficient
and that no owner field is named; this package fills the owner gap with S0.

## Evidence commands

```sh
python3.12 -I -B research/p104-flag0-tail-owner-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-owner-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-owner-host/independent.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-owner-host/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-tail-owner-host
```

Expected markers:

```text
PASS_P104_FLAG0_TAIL_OWNER_HOST flag=0 owner=X0 promote=5758 add=5759 restore=5807 dirty_helper_touches=0 endpoint_repay=0 pre_read_restore_blocks=1 unique_owner=1 no_new_kappa
PASS_P104_FLAG0_TAIL_OWNER_HOST_INDEPENDENT flag=0 owner=X0 promote=5758 add=5759 restore=5807 dirty_helper_touches=0 endpoint_repay=0 pre_read_restore_blocks=1 unique_owner=1 no_new_kappa
PASS_P104_FLAG0_TAIL_OWNER_HOST_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag0-tail-owner-host outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Duplicate JSON keys are rejected. On-disk certificate / witness corruption is
rejected in temp copies.

## Soft overlap

- Soft vs #3669 (chronology leave-alone): cites OQ2 only; no drop/arrive reprint.
- Soft vs deferred `p104-flag0-head-span-schedule` / #3532: different cut
  (5758/5759/5807 vs 3369 co-host repair); not a FLAG_INDEX retarget.
- Soft vs jwr404 `p104-tail-flag0-*`: those are partial readings; this assigns
  the schedule and adds dirt/repay/obstruction checks.
- Leave-alones listed in the worker brief are untouched.

## Disposition

Fork branch for master publish decision. Do not open a CrocSwap PR from this
worker.
