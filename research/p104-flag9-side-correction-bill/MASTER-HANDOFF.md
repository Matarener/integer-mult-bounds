# MASTER-HANDOFF — flag-9 end-cut side-correction bill

## Claim (one sentence)

On the published P104 native word, flag 9's `I−G/2` entry `(23,4)` (`G=−1` ⇒ `+1/2·X4` into `Y23`) costs exactly **+2** non-private rank mass at the end-cut (attained by T/S/T48); private-copy P costs **+1**; feeder `X58:333` at leave 745 blocks all 25 zero-mass insertion classes (consistent with open #3614).

## Tip / base

- Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap `main`)
- Branch: `cursor/flag9-side-correction-bill-30d6` (VictorLiwentao fork)
- Tip: `89dbb7ced3b892ce030d31e4027eb9cba73af173`
- Content tip: `f2c20bc4d82558bb4ff280a49814e70778816e96` (package body)
- Package: `research/p104-flag9-side-correction-bill/`
- All VERIFY commands PASS (including `PASS_REGISTERED_RESEARCH_PACKAGE`).

## PASS lines

```text
PASS_P104_FLAG9_SIDE_CORRECTION_BILL flag=9 entry=(23,4) gram=-1 coefficient=+1/2 zero_mass_placements=0/25 forcing=X58(333)@leave745 strict_min_added_rank=2 T=+1transport+1add+2rank(H1-H5+H6) S=+2transport+1add+2rank(2H1) P=+1transport+1add+1rank(H1)+1private_lifetime T48=+1transport+48add+2rank row23=identity native_validate=4/4 published_end_cut no_new_kappa
PASS_P104_FLAG9_SIDE_CORRECTION_BILL_INDEPENDENT entry=(23,4) coefficient=+1/2 zero_mass_placements=0/25 early_private_deliveries_obstructed=7/7 forcing_head=333(X58)@leave745 T=+2rank S=+2rank P=+1rank T48=+2rank rows_changed=Y23_only row23=identity new_recipes=3 no_new_kappa
PASS_P104_FLAG9_SIDE_CORRECTION_BILL_TESTS cases=14 clean_read_only=1 scanners=2
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag9-side-correction-bill outcome=completed
```

## Commands

```sh
python3.12 -I -B research/p104-flag9-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-side-correction-bill/independent.py
python3.12 -I -O -Werror -B research/p104-flag9-side-correction-bill/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag9-side-correction-bill
```

## Soft-overlap risks

- Template kinship with open [#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601) / [#3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610) (T/S/P/T48 / Tend bill shape). **Novelty bar met:** flag-9-specific attaining words on the published chronology, coefficient `+1/2`, cut 3489 / A3, three new recipes `A3→FULL` + `FULL↔F23`, feeder `X58:333@745` with 25/25 obstruction recomputed, private 7/7 early blocks. Not a rename-only clone.
- Open [#3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614): feeder/obstruction cited as leave-alone and recomputed; no certificate import; does not reopen deferred head-step repair.
- Leave-alone: #3601, #3610, #3614, #3532, #3508, #3443 (chronology cited only).

## Open questions

1. Is private-copy P admissible, or must correction lifetimes be uncomputed?
2. If a co-hosted flag-9 repair later lands, does +2 discount?
3. Full-row (~48) forcing census on Y7/Y23/Y59 — #3614 OQ1.

## Attribution

Prepared by Wentao Li <wentaol4@illinois.edu> with substantial AI assistance.
No CrocSwap PR opened by this worker; master publishes.
