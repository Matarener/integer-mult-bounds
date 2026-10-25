# Master handoff — `research/p104-flag1-side-correction-bill/`

## Candidate

- Branch: `cursor/flag1-side-correction-bill-988a` (VictorLiwentao fork). The
  `-988a` suffix is this worker's environment-required branch suffix, not
  `-60b9`.
- Content tip: `f5c09d4688c848f02d546a08191b047cd7b3687f`. This commit holds the
  full scientific package.
- Packaging tip: the child commit that adds only this handoff file. Read its SHA
  with `git rev-parse origin/cursor/flag1-side-correction-bill-988a`.
- Package: `research/p104-flag1-side-correction-bill/`
- Base: CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. It contains
  merged #3508 and #3451. The requested pin `6f100d4bb5083f8c35d96fd95a539811c62f245c`
  is an ancestor.
- #3532 inputs: open #3532 is not on any main. Its `CERTIFICATE.json` and
  `REPAIR-RECIPES.json` are vendored byte-identically under `inputs/pr3532/`
  from head `8fecbf7df7b48c9004bd10a0da6a81f33d455737`. `SOURCES.json` carries
  `head:` provenance pins for those files and #3601's README, and both scanners
  check the vendored SHA-256. The registry pin check needs those head commits
  in the local object store.
- Card: `p104-side-correction` (refined), priority revision 6. The card is
  byte-identical to the catalogue at the base.
- κ: unchanged at `0.001672660197076918`.
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`. A hook-injected
  co-author trailer was stripped with `git commit-tree`.
- No CrocSwap PR has been opened.

## Claim

This is the flag-1 analogue of #3601. Flag 1's entry is `(7, 0)`, and
`G[7,0] = −1`, so the `I − G/2` correction adds `+1/2·X0` into `Y7`. It is
priced at both of #3532's co-hosted charts:

| Word | Base | Δ events | Δ ADDs | Δ transports | Δ rank vs base | vs published |
|---|---|---:|---:|---:|---:|---:|
| E: one ADD in FULL after R1's relocated delivering ADD | R1 | +1 | +1 | 0 | 0 | +2 |
| Erow: all 48 row-7 entries there | R1 | +48 | +48 | 0 | 0 | +2 |
| T: `Y7: A3→FULL`, ADD, `FULL→F7` | R0 | +2 | +1 | +1 | +2 | +4 |
| S: `X0: FULL→F7→FULL` detour | R0 | +3 | +1 | +2 | +2 | +4 |
| P: one private-copy lifetime | R0 | +5 | +1 | +1 | +1 | +3 |
| Trow: all 48 entries on T's lift | R0 | +49 | +48 | +1 | +2 | +4 |
| Tend: end-cut control | published | +2 | +1 | +1 | +2 | +2 |

The co-host discount is **0 at R0**, as for flag 43, and **2 at R1**. The
discount at R1 is new for flag 1: R1's relocation already lifts `Y7` into the
full chart where `X0` sits, so the correction rides on R1's +2.

All seven words pass the unchanged `check_native.validate()` with coefficients
set to `0`. That includes three newly lowered recipes, 208 adapters, 280 rows
and 72 dirty helpers. On each real word the checker fails only at `Y7`'s
endpoint, and exact replay changes only `Y7`.

**Obstruction (flag-1-specific forcing).** `X7`'s own head `387` is outside
`F7` because `G[7,7] = 2` is even. It reaches `X0` at event 1074 along
`X7 –616– G11 –679– X20 –1070– G18 –1074– X0`. A least-frame sweep with the
delivering ADD dropped blocks all 18 insertion classes, so it covers every one
of the 1,116 placements of the delivering ADD. Per-register mass is even, so
the strict minimum is exactly 2.

**Joint theorem.** Consider words that both co-host the head and apply the
correction.

- With relocation, the minimum is exactly 2 (R1+E).
- Order-preserving strict words need at least 4 non-private rank, and R0+T and
  R0+S attain 4. Only `D17`'s freedom rescues co-hosting alone, and with `D17`
  free all 19 correction classes stay blocked.

The private route costs exactly 1: all 5 early delivery classes are blocked.

## PASS lines

```text
PASS_P104_FLAG1_SIDE_CORRECTION_BILL flag=1 entry=(7,0) gram=-1 coefficient=+1/2 zero_mass_placements=0/18(delivery_anywhere_in_1116_slots) forcing=X7(387)-616-G11-679-X20-1070-G18-1074-X0 strict_min_added_rank=2 R0:T=+1transport+1add+2rank S=+2transport+1add+2rank P=+1rank+1private_lifetime Trow=+48add+2rank R1:E=+0transport+1add+0rank Erow=+48add+0rank row7=identity cohost_discount_R0=0 cohost_discount_R1=2 joint_min_relocated=2 joint_min_order_preserving_strict=4 native_validate=7/7 no_new_kappa
PASS_P104_FLAG1_SIDE_CORRECTION_BILL_INDEPENDENT entry=(7,0) coefficient=+1/2 strict_classes_obstructed=18/18(delivery_dropped)+19/19(published_order) early_private_obstructed=5/5 forcing_head=387(X7) R0:T,S,Trow=+2rank P=+1rank R1:E,Erow=+0rank Tend=+2rank joint_order_preserving_single_rescue=none rows_changed=Y7_only row7=identity new_recipes=3 no_new_kappa
PASS_P104_FLAG1_SIDE_CORRECTION_BILL_TESTS cases=18 clean_read_only=1 scanners=2
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag1-side-correction-bill outcome=completed
```

## Commands

```sh
python3.12 -I -B research/p104-flag1-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-side-correction-bill/independent.py
python3.12 -I -O -Werror -B research/p104-flag1-side-correction-bill/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag1-side-correction-bill
```

Run times: `verify.py` about 60 s, `independent.py` about 6 s,
`test_package.py` about 200 s with 4 workers, and the registry check about
270 s. The default replay is read-only. Admission goes through `need()`, so it
still fires under `-O`, and the package contains no `assert` statements.
Duplicate JSON keys are rejected. Rejection reasons were spot-checked: E in the
wrong chart fails at the common-chart rule, an empty rescue list fails the
census, and the #3532 byte flip fails the pin.

## Closest priors (cite only)

- [#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601) (open).
  Flag 43's bill at #3508's cut, with co-host discount 0. Its format, class Z
  and sweep are reused here.
- [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) (open).
  R0, R1, the delivering-update window and the +2 co-host floor, used as
  vendored inputs. The late-slot open question 1 is untouched.
- [#3451](https://github.com/CrocSwap/integer-mult-bounds/pull/3451) (merged).
  Flag 1's chronology. It is not reprinted here.
- [#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) (merged).
  The method and class Z.
- `research/p104-side-correction-rank-obstruction`. Its end-cut +2 invoice
  matches Tend.

## Soft-overlap risks

- Code shape. `verify.py`, `independent.py` and `test_package.py` follow
  #3601's structure closely: same helpers, sweep and bill layout. A reviewer
  may read this as a template clone, the same pattern for which the flag-9
  repair was deferred. The new checkable facts are flag-1-specific:
  - the R1 free ride (discount 2, versus 0 for flag 43);
  - the joint theorem (2 with relocation versus 4 order-preserving), backed by
    the single-register census;
  - a different forcing chain (the self-head `387` via `G11`/`X20`/`G18`,
    instead of `X12`'s `131` via `G9`);
  - coverage of every delivering-ADD placement.
  If maintainers prefer, these facts could fold into #3601 or #3532 after merge
  together with a shared helper module.
- Dependency on open #3532. If #3532 changes its head, the vendored bytes and
  pins must be refreshed.
- The end-cut +2 (Tend) is not new on its own. It is a control.
- Open-PR searches for "flag 1 side correction", "I-G/2 flag-1" and "3532"
  found only #3532 and #3601. `scripts/find_overlap.py --task
  p104-side-correction` had no flag-1 side-correction hit.

## Open question

The headline open question is whether flag 1 has a co-hosted and corrected
word with joint added mass 1. That needs a zero-mass late relocation (#3532's
open question 1) plus a private-copy correction. The strict joint minimum with
relocation is 2. Two further questions are open:

- whether every present-head row needs +2 for its strict entry;
- the H-weighted comparison of R1+E (`H8 − H6`) against Tend
  (`H1 − H6 + H7`).

See `TASK.json`.

## Limits

This covers one entry and one target row on the charts of two repairs of one
finite word. The class keeps every published ADD and coefficient. Theorem 3
bounds non-private mass for strict words; R0+P reaches 3 under the inherited
private-copy discard. There is no global hosting, precision or supplier, and
no κ change.
