# Master handoff — `research/p104-flag43-side-correction-bill/`

## Candidate

- Branch: `cursor/flag43-side-correction-bill-6707` (VictorLiwentao fork). The
  `-6707` suffix is this worker's environment-required branch suffix, not
  `-60b9`.
- Content tip: `8838ce9049e3c0beb555b8e1b6d48c9e11be3685`. This commit holds the
  full scientific package. Its parent, `39ad54e9…`, adds the package. The content
  tip only lowers the test timeout to the 600 s registry cap.
- Packaging tip: the child commit that adds only this handoff file. Read its SHA
  with `git rev-parse origin/cursor/flag43-side-correction-bill-6707`.
- Package: `research/p104-flag43-side-correction-bill/`
- Base: CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The requested
  pin, `6f100d4bb5083f8c35d96fd95a539811c62f245c`, is an ancestor of this base.
  The newer main is required because #3508's R0 package, an input here, merged
  after the requested pin.
- Card: `p104-side-correction` (refined), priority revision 6. The card is
  byte-identical to the catalogue at the base.
- κ: unchanged at `0.001672660197076918`.
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`. A hook-injected
  co-author trailer was stripped with `git commit-tree`.
- No CrocSwap PR has been opened.

## Claim

This answers #3508's open question 2 for flag 43 (`X21` → `Y59`, head `15`).
Since `G[59,21] = 1`, the `I − G/2` entry is `−1/2·X21` into `Y59`. On R0, all
four corrections below replace `Y59`'s terminal transport at 3525, while the
head is still co-hosted:

- `Y59` is in `W6 = [95,447,6,32,20,15]`;
- `X21` is in FULL;
- both frames span `15`.

| Word | Δ events | Δ ADDs | Δ transports | Δ rank | Profile Δ vs R0 |
|---|---:|---:|---:|---:|---|
| T: target lift `W6→FULL`, ADD, `FULL→F59` | +2 | +1 | +1 | +2 | `H1 − H2 + H3` |
| S: source detour `X21: FULL→F59→FULL` | +3 | +1 | +2 | +2 | `2H1` |
| P: one private-copy lifetime | +5 | +1 | +1 | +1 | `H1` |
| T48: whole row 59 (48 entries) on T's lift | +49 | +48 | +1 | +2 | `H1 − H2 + H3` |

In T48, `Y59`'s final row becomes exactly `y59 + x59`.

Each word is checked in two ways:

- The unchanged `check_native.validate()` passes each coefficient-0 word. That
  covers the two newly lowered `FULL ↔ F59` recipes, 208 adapters, 280 rows and
  72 dirty helpers.
- On the real word, the same checker fails only at `Y59`'s endpoint. Exact
  replay confirms that only `Y59` changes.

**Obstruction.** The class keeps the published events, ADDs, endpoint frames and
`C` lifetimes, and allows transports to be retargeted or inserted. In this
class, no placement of the correction ADD has zero added rank mass:

- Events 625 and 884 (`G9 += 2·X12`, then `G9 −= 2·X21`) force `X12`'s head
  `131` into `X21`'s frame.
- `G[59,12] = 0` puts `131` outside `Y59`'s final hyperplane.
- A least-lower-bound sweep blocks all 28 insertion classes.
- Each non-private register's added mass is even.

So the strict minimum is exactly +2. The published end-cut detour also costs
+2, so co-hosting gives a rank-mass discount of 0. P's +1 is minimal for one
added private lifetime that copies `X21`, but only under the inherited
private-copy discard.

## PASS lines

```text
PASS_P104_FLAG43_SIDE_CORRECTION_BILL flag=43 entry=(59,21) coefficient=-1/2 zero_mass_placements=0/28 forcing=625:X12(131)->884:G9->X21 strict_min_added_rank=2 T=+1transport+1add+2rank(H1-H2+H3) S=+2transport+1add+2rank(2H1) P=+1transport+1add+1rank(H1)+1private_lifetime T48=+1transport+48add+2rank row59=identity cohost_discount=0 native_validate=4/4 no_new_kappa
PASS_P104_FLAG43_SIDE_CORRECTION_BILL_INDEPENDENT entry=(59,21) zero_mass_placements=0/28 early_private_deliveries_obstructed=11/11 T=+2rank S=+2rank P=+1rank T48=+2rank rows_changed=Y59_only row59=identity new_recipes=2 no_new_kappa
PASS_P104_FLAG43_SIDE_CORRECTION_BILL_TESTS cases=14 clean_read_only=1 scanners=2
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag43-side-correction-bill outcome=completed
```

## Commands

```sh
python3.12 -I -B research/p104-flag43-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag43-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag43-side-correction-bill/independent.py
python3.12 -I -O -Werror -B research/p104-flag43-side-correction-bill/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag43-side-correction-bill
```

Run times: `verify.py` about 31 s, `independent.py` about 2 s,
`test_package.py` about 96 s with 4 workers, and the registry check about 128 s.
The default replay is read-only. Admission goes through `need()`, so it still
fires under `-O`, and the package contains no `assert` statements. Duplicate
JSON keys are rejected.

## Closest priors (cite only)

- [#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) (merged).
  R0, the co-hosted chart and the class-Z closure. This package answers its
  open question 2.
- [#3456](https://github.com/CrocSwap/integer-mult-bounds/pull/3456). Flag 43's
  published chronology. It is not reprinted here.
- `research/p104-side-correction-rank-obstruction`. Its end-cut round-trip and
  snapshot invoices (+2 rank per target) are compared against T's +2, and found
  equal.
- `research/p104-channel-correction-absent` (the channel leaves `1/2`) and
  `research/p104-native-channel` (semantics and the private-copy contract).

## Soft-overlap risks

- [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) (open) is
  the flag-1 head-step repair. It is not touched or cited for content. Flags 1
  and 9 and the flag-0 cascade are untouched.
- `p104-side-correction-rank-obstruction` already prices a +2 per-target
  detour at the end cut. This package's new content is:
  - the co-hosted-cut placement on R0;
  - the zero-mass obstruction over every insertion point, together with its
    forcing chain;
  - the private-copy +1 route;
  - the native validation of the corrected words.
- An open-PR search for "side correction", "3508", "flag 43", "I-G/2" and
  "co-hosted" found no other PR pricing this entry.

## Open question

The headline open question is whether P's private-copy discard is admissible
for a correction. If `C` must be uncomputed, the strict +2 applies to every
corrected target. Two further questions are open:

- whether the 625/884-type forcing blocks a zero-mass entry for every pair with
  `G[t,s] ≠ 0`;
- whether a fused correction that retunes published ADD coefficients (outside
  the class) evades the bound.

See `TASK.json`.

## Limits

This covers one entry and one target row at one cut of one finite word. The
theorem covers a single inserted ADD between `X21` and `Y59`. Multi-register
routes that meet `X21` before 884 are not enumerated. There is no global
hosting, precision or supplier, and no κ change.
