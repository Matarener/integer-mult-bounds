# Master handoff — `research/p104-flag1-head-step-repair/`

## Candidate

- Branch: `cursor/flag1-head-step-repair-0378` (VictorLiwentao fork). The
  `-0378` suffix is this worker's environment-required branch suffix, not
  `-60b9`.
- Content tip: `053bff9e760e05354687cc669461dd6d8effed18`. This is the
  scientific package commit. Its parent is the pinned base.
- Packaging tip: the child commit that adds only this handoff file. Read its SHA
  with `git rev-parse origin/cursor/flag1-head-step-repair-0378`.
- Package: `research/p104-flag1-head-step-repair/`
- Base: CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no co-author
  trailer (both commits were built with `git commit-tree`).
- Scratch branch `cursor/p104-flag1-head-step-repair-0378` holds an earlier
  agent-identity WIP commit of the same producer. It is superseded and should
  not be published.

## Claim

On present-head flag 1 (`X0` → `Y7`, head `232`), event 2797 (`Y7 += D17/4`) is
the only `Y7` update that carries `X0`. It brings `-1/2`, the final coefficient.

Two changed schedules make that ADD co-host the head while `X0` sits in its
rank-9 chart and still has four later reads. The published `check_native.validate()`
passes unchanged on both. That covers all native edges (six newly lowered), 208
adapters, 280 framed rows and 72 dirty-helper restorations.

| | Events | ADDs | Transports | Rank mass | Profile delta | Surcharge on |
|---|---:|---:|---:|---:|---|---|
| R0 (order-preserving) | +1 | 0 | +1 | +2 | `-H1 + 2H2 + H5 - H6` | `D17` |
| R1 (relocated into `D17`'s full window) | 0 | 0 | 0 | +2 | `H8 - H6` | `Y7` |

Under an affine price the extra cost is `a + 2b` for R0 and `2b` for R1, so it is
positive. Under a convex price R0's delta can be negative: it is `-4` at
`H = r²`.

**Obstruction.** All 280 non-private registers are at their rank floor, and the
excess over the floor is always even.

- The #3508 head closure blocks all six `Y7` updates. For 2797 the first
  obstruction is `Y8` at 2799.
- The exact least-frame sweep (with the private register `C` relaxed, so the
  verdicts are sound) says zero added non-private mass is infeasible for all six
  order-preserving updates.
- It is also infeasible for 868 of 1,115 relocation slots of the delivering ADD,
  namely every slot before `Y103`'s read at 3366.

So +2 is the floor there, and R0 is mass-optimal among order-preserving
repairs. The 247 later slots are relaxed-feasible and left open.

## Why this is not a chronology reprint

The headline is two constructed repaired words, their native validation, their
exact bill and a zero-mass obstruction that flag 43 does not have. #3451's
drop/arrive chronology is cited, not re-derived. The only published fact
rechecked is "no `Y7` update hosts the head", which the before/after comparison
needs.

## Evidence commands

```sh
python3.12 -I -B research/p104-flag1-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-head-step-repair/independent.py
python3.12 -I -O -Werror -B research/p104-flag1-head-step-repair/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag1-head-step-repair
```

Expected markers:

```text
PASS_P104_FLAG1_HEAD_STEP_REPAIR flag=1 head=232 delivering_update=2797 R0=order_preserving added_events=1 added_adds=0 added_transports=1 added_rank_mass=2 profile_delta=-H1+2H2+H5-H6 R1=relocated added_events=0 added_transports=0 added_rank_mass=2 profile_delta=-H6+H8 native_validate=PASS zero_mass_order_preserving=0/6 zero_mass_relocation_obstructed=868/1115 no_new_kappa
PASS_P104_FLAG1_HEAD_STEP_REPAIR_INDEPENDENT flag=1 head=232 delivering_update=2797 R0 added_events=1 added_transports=1 added_rank_mass=2 R1 added_events=0 added_transports=0 added_rank_mass=2 rows_equal=280/280 zero_mass_order_preserving=0/6 zero_mass_relocation_obstructed=868/1115 no_new_kappa
PASS_P104_FLAG1_HEAD_STEP_REPAIR_TESTS cases=17 clean_read_only=1 scanners=2
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag1-head-step-repair outcome=completed
```

The worker ran all five commands in the working tree. It ran them again,
together with `research_package.py --changed-since <base> --check-only`, in a
fresh detached worktree of the content tip. Those runs leave the tree
byte-identical. The test suite also checks this inside its temp tree.

## Closest priors

- #3508 `p104-flag43-head-step-repair`: the method prior. This package reuses
  three things from it: the splice/assemble/validate harness, the class-Z head
  closure, and the bill format. Flag 43 had a zero-cost event-preserving repair;
  flag 1 does not. #3508 itself is left alone.
- #3451 `p104-present-head-flag1-audit`: the published flag-1 obstruction. Its
  first open question is answered here. Cited only.
- #3443 (flag 9) and #3349 (census): cited only.
- #3363: relay census. Only the single `X0` entry delivered into `Y7` at 2797 is
  re-reported.

## Soft-overlap risks

- **Code reuse from #3508.** About 316 of `verify.py`'s 463 non-blank lines
  match #3508's `verify.py` line for line: the GF(2) helpers, splice and
  assemble, bill, and closure. About 132 of `independent.py`'s 287 non-blank
  lines match #3508's `independent.py`, mostly the replay and recipe check.
  `independent.py` changes the frame representation (reduced bases instead of
  XOR closures). The least-frame sweep and the relocation scan are new. A
  reviewer may ask for a shared helper instead of a copy.
- **#3451.** The package restates "no published `Y7` update hosts the head" and
  the `Y7` update list (19, 20, 2013, 2146, 2526, 2797). Both appear in #3451's
  PROOF items 3–5. They are rechecked only because the bill comparison needs
  them.
- **#3363.** The single coefficient fact (`-1/2` at 2797 via `D17`) is on #3363's
  turf. A reviewer may want it cited to #3363 or trimmed. It is load-bearing for
  "2797 is the delivering update".
- **Flag 0.** It shares source `X0`. No flag-0 or `Y34` coefficient is computed.
- **Relaxed sweep wording.** A reader could take "0 infeasible after 3366" as a
  claim that zero cost is achievable. It is not: the relaxation frees `C`, and
  the direct construction fails. The README and PROOF say so, and open
  question 1 carries it.
- `H_r` is left symbolic.

## Open questions

1. Is there a zero-added-mass co-hosting relocation after 3366?
2. Which +2 repair, R0 or R1, is cheaper under the repo's actual per-rank
   weights?
3. Does flag 9 (#3443) follow flag 1's pattern or flag 43's?

## Disposition note for master

This worker produces a fork branch and package only. Do **not** open a CrocSwap
PR from this worker. Master decides whether to publish or defer after an
independent skeptical review.
