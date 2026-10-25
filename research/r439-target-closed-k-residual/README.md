# R439 literal K defect: target reads versus helper wraps

**Finite certificate on nine named words. No new κ.** The selected κ stays
0.001672660197076918. This adopts no replacement `K_equals_D` contract, admits
no supplier and changes no paid profile.

## Question

PR #4092 counted the literal `K_equals_D` defect on the three helper-star words
(17,636 / 17,636 / 17,653 bits, all 439 helper sectors defective). It asked
whether that pattern persists on other helper-mixing lineages. The merged
`r439-k-cross-term-tally` package identified the defect with
executed-versus-named columns inside `D`, but did not split it. This package
asks which part comes from the 612 target-to-target reads and which part comes
from helper-to-helper gates (helper wraps). Card `bit-helper-contract`, scope
refined to that split.

## Definitions

Over GF(2), register `r` starts as column `e_r`. Helper columns are registers
`2v .. 2v+R-1` (`v = 111`, `R = 439`).

- `K_t`: helper part of target `t` after the frame-free replay of `(A, scatter, B)`.
- `N_t`: helper columns named by `D` gates that write target `t` (the literal mask).
- `N*_t`: helper columns reaching target `t` when `D` is replayed with every
  helper-to-helper gate skipped (the *target-read-closed* named mask).
- `E_t`: helper columns reaching target `t` when `D` is replayed in full.
- `T_t = N*_t + N_t`: the part carried by target-to-target reads.
- `H_t = K_t + N*_t`: the residual left by helper wraps.

The literal defect is `K_t + N_t = T_t + H_t`. On every word below `E = K`, so
`H_t = E_t + N*_t`: exactly the extra columns that wrapped helpers deliver.

## Result

| word | D gates | helper gates | literal \|K+N\| | target-read \|T\| | residual \|H\| | \|T∧H\| | residual sectors = donors | sectors passing after closure |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PR915 target basis | 723 | 0 | 17,095 | 17,095 | **0** | 0 | 0 | 439 / 439 |
| PR926 disjoint pairs | 1,107 | 384 | 17,485 | 13,148 | 7,447 | 1,555 | 192 | 247 / 439 |
| PR941 matching candidate | 1,121 | 398 | 17,514 | 13,008 | 7,786 | 1,640 | 199 | 240 / 439 |
| PR941 floor word | 1,121 | 398 | 17,505 | 12,885 | 7,776 | 1,578 | 199 | 240 / 439 |
| helper triples | 1,191 | 468 | 17,541 | 12,444 | 8,685 | 1,794 | 232 | 207 / 439 |
| PR1062 pair control | 1,099 | 376 | 17,504 | 13,110 | 7,424 | 1,515 | 188 | 251 / 439 |
| PR967 helper stars | 1,165 | 442 | 17,636 | 12,275 | 8,767 | 1,703 | 221 | 218 / 439 |
| PR1062 composition | 1,165 | 442 | 17,636 | 12,275 | 8,767 | 1,703 | 221 | 218 / 439 |
| PR1062 candidate | 1,195 | 472 | 17,653 | 12,092 | 9,163 | 1,801 | 236 | 203 / 439 |

Bit counts satisfy `|K+N| = |T| + |H| − 2|T∧H|` on every word. Each word has
612 `D` gates that write a target and read another target. The literal defect
touches all 439 helper sectors on every word.

What this establishes on these nine words:

1. **Target reads, not helper mixing, account for the whole literal defect of
   the helper-free base.** PR915's `D` has no helper-to-helper gate, yet its
   literal defect is 17,095 bits across all 439 sectors. Closing the named mask
   under target reads removes all of it: `K = N*` exactly.
2. **On every helper-mixing word, the residual support is exactly the donor
   set.** Call a helper a donor when some helper-to-helper gate reads it. The
   helper sectors carrying residual bits are exactly the donors: 192, 199, 199,
   232, 188, 221, 221 and 236. On the star words the donors are the 221 / 236
   star leaves and the 157 / 162 written helpers are the centres. Donors and
   written helpers are disjoint except for 28 helpers in the triple word.
3. **The "every sector is defective" reading of PR #4092 comes from target
   reads.** After target-read closure, 203–251 helper sectors per mixing word
   satisfy the sector-local condition (no residual bit in that column). The
   defect left to forgive is concentrated on donor columns: 7,424–9,163 bits,
   versus 17,485–17,653 literal bits.
4. `E = K` and all 439 helpers end `D` restored on all nine words. No
   non-helper column survives in any `N_t`. This extends the cross-term tally's
   `E = K` certificate from three words to nine.

## Controls

The verifier runs six controls:

- Two-target synthetic `y0 ^= h0; y1 ^= y0` with `K = (h0, h0)`. The literal
  defect is one bit; `T` is that bit and the residual is zero.
- Restored wrap `h0 ^= h1; y ^= h0; h0 ^= h1` with semantic `K = h0 + h1`.
  `E = K` and the residual is the single donor column `h1`.
- The same wrap against `K = h0` (the cross-term tally's synthetic edge).
  `E ≠ K`, yet the closed mask reports **zero** residual. Thus `K = N*` alone is
  **not** a sound replacement check once helper gates are present. A contract
  built on `N*` must still charge or check the wraps (for example `E = K` with
  restored helpers).
- Deleting the first helper-to-helper gate of the PR967 star word breaks both
  `E = K` and helper restoration.
- Deleting the first helper-carrying target-to-target read of PR915 leaves a
  nonzero residual, so PR915's zero residual is not a property of `K` alone.
- PR #3904's pair on the PR967 star word: target register 112, helper register
  260 (helper index 38), donor of `D` gate 0 `280 ^= 260`. The bit is in `K` and
  absent from `N` and `N*`, so it lies in both the literal defect and `H`.

## Correction to PR #4092

PR #4092 (`r439-star-kdefect-sectors`, same author) states that the #3904 pair
is **not** in the official W0 defect set, because the "sector of column 260"
has 57 defective targets that exclude 112. That statement is wrong. It mixed
register numbers with indices. Register 260 is helper index 38. Sector 38 has
57 defective targets, and they include target index 1, which is register 112.
#4092 searched for target index 112, which does not exist (`v = 111`). Running
#4092's own `verify.py --json` confirms this: sector `"38"` lists 57 targets
including `1`. So the #3904 pair is in the official W0 defect set, and #3904
agrees with #4092 on it. The two do not use different raw-word definitions for
this bit. #4092's census totals, sector counts and controls are unaffected. This
package does not edit #4092's files. The sixth control above pins the corrected
fact.

## What is not established

This is a finite certificate on nine named words. It does not adopt `K = N*`,
`E = K` or any other replacement for `K_equals_D` or H2; the third control
shows `K = N*` alone is unsound with helper gates. The 612 target-to-target
reads remain a literal H2 read-kind failure. No frame, native schedule, hosted
invoice, all-size transfer, supplier admission or selected-frontier change is
claimed. The bit side does not bind the selected exponent.

## Reproduce

From the repository root, CPython 3.12, standard library only (about 0.1 s):

```sh
python3.12 -B research/r439-target-closed-k-residual/verify.py
python3.12 scripts/research_package.py --package research/r439-target-closed-k-residual
```

Expected:

```text
PASS_R439_TARGET_CLOSED_K_RESIDUAL words=9 pr915_residual=0 star_residual=8767/8767/9163 sectors_equal_donors=9/9 controls=6 no_new_kappa
```

`verify.py --json OUT` writes the per-word record, including target-read counts,
donor and written-helper counts and sector-pass counts. All nine inputs are
bound by SHA-256 in [SOURCES.json](SOURCES.json).

## Open next questions

1. **Can a donor-sector contract replace `K_equals_D` on these words?** A
   candidate is "`K = N*` plus, for each restored wrap, the donor columns
   delivered while the wrap is open". It would be checkable from `D` alone and
   would reject the third control. First step: state it for well-nested
   restored wraps and test it on the nine words and the controls. Blocker:
   adopting it as the H2/K interface is a maintainer policy decision.
2. **Do target reads still fail H2 after closure?** Closing the mask removes
   the K mismatch from target reads but not H2's read-kind clause. First step:
   check whether the PR915 semantic substitution proof already covers
   target-read closure, so the 612 reads need no separate repair.

## Credit

Produced by Nick Petalas. Words and predecessor results are retained unchanged
with their own attribution: Gareth Davidson (PR915 target basis, PR926 helper
pairs, `r439-helper-matching` / PR941), Ross Richardson (`r439-helper-triples`),
Sricharan Vagvala (`r439-helper-stars-seed19`, PR967 lineage), Sagar Thakrar
(PR1062 `r439-bsection-stars-seed01`), the PR4092 sector census and the
`r439-k-cross-term-tally` package. Apache-2.0.
