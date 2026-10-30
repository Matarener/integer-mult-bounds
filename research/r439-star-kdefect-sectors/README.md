# R439 star K-defect sectors: a complete per-helper census of the literal `K_equals_D` failure

**Finite certificate on three named words; no new κ.** The selected result, the selected
bit supplier and `upstream/` are unchanged; the bit side does not bind.

The retained R439 helper-star words all carry the two false syntactic flags
`H2_D_frame0_targets_from_helpers` and `K_equals_D` (see PR967 lineage
`research/r439-helper-stars-seed19` and PR1062 `research/r439-bsection-stars-seed01`).
PR1194 retains a semantic replacement that proves `N = K` globally for a virtual spliced D.
This package quantifies the exact size and shape of the syntactic failure those words carry,
under the pinned owner checker's own definitions
(`research/e8-bit-p111-tuned/code/xcheck_p.py`, sections quoted below), with an
independent GF(2) replay that cross-agrees with the checker on every derived boolean.

| word (v = 111, R = 439, 661 columns) | D gates | defect bits (K ⊕ N) | defective helper sectors | KS(h) pass | single-gate repairs | single-bit repair |
|---|---:|---:|---:|---:|---:|---:|
| `helper_star` = seed19 candidate (PR967 lineage) | 1,165 | **17,636** | 439 / 439 | 0 / 439 | 0 | no |
| `composition` (PR1062, +spliced phase-B blocks) | 1,165 | **17,636** | 439 / 439 | 0 / 439 | 0 | no |
| `candidate` (PR1062, star rerun) | 1,195 | **17,653** | 439 / 439 | 0 / 439 | 0 | no |

`K` = helper-column part of each target's raw-word (A, scatter, B) output under symbolic
all-column replay; `N` = helper columns named by D's target writes; defect = `K ⊕ N`;
`KS(h)` = sector-local condition "no target carries a defect in helper column h".

## What this establishes (finite, scoped to the three words)

1. **The failure is global, not local.** All 439 helper sectors are defective; the
   per-operation condition `KS(h)` passes for **zero** star helpers on every word
   (sector sizes range from 4 to 68 defective targets, 17,636–17,653 bits total). A
   per-helper
   sector-local replacement of H2/K cannot lift to the global `K_equals_D`: any such
   replacement must account for cross-sector terms — consistent with the retained
   PR1194 route, which proves `N = K` globally rather than per star.
2. **No single-operation edit repairs it.** Exhaustive enumeration over all 1,165/1,195
   single-D-gate removals, and over all single-bit toggles (possible only at defect size
   one), yields zero repairs on every word.
3. **Localization of the failure source.** The raw helper part `K` is bit-identical across
   all three words (0 differing bits), even though the phase-B splice rewrites B
   (712 → 578 gates) and cleanup C (2,574 → 2,440 gates), and identical D (byte-equal N)
   between `helper_star` and `composition` leaves the defect profile exactly equal at
   17,636 bits. The star rerun (+30 D gates, N differing in 173 bits) shifts the defect
   by 17 bits (17,636 → 17,653). The literal-K failure lives entirely in D versus the
   fixed raw helper component; phase-B replacement neither creates nor removes it.
4. **H2 clause decomposition.** On all three words the frame clauses are clean (0 D gates
   at nonzero frame, 0 target/helper start-frame violations) and every uncanceled N entry
   is helper-column-only; H2 fails purely through destination/read clauses: 442 D gates
   write non-target registers (472 on the rerun candidate) and 612 D gates read non-helper
   registers.

## Relationship to adjacent open work

PR #3533 gives the abstract three-gate restored-edge mechanism (the literal mask names
`h0` while `y` receives `h0 ⊕ h1`); this package counts the consequence across a full
retained word. PR #3904 pins one per-target example (target 112, helper 260) measured on
a **D-inclusive** replay against the literal mask. Under the pinned checker's official
definition — raw `W0 = (A, scatter, B)` with D excluded, used here and cross-agreeing
with the checker flag — that particular bit pair is **not** in the defect set (sector of
column 260 has 57 defective targets, not including 112). The two statements use different
raw-word definitions; neither contradicts the other, and the census here is on the
official W0 definition.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B research/r439-star-kdefect-sectors/verify.py
python3 -I -O -B research/r439-star-kdefect-sectors/verify.py
```

Expected (~2 s each):

```text
PASS_R439_STAR_KDEFECT_SECTORS words=3 defect_bits=17636/17636/17653 defective_sectors=439/439/439 KS_pass=0/439/0/439/0/439 single_op_repairs=0 controls=5 no_new_kappa
```

`verify.py --json OUT` additionally writes the full sector/target table, per-word flag
maps and cross-word bit counts. Five controls run: SHA-256 source bindings; the
checker-agreement and retained-flag-pattern control on all three words; the multi-defect
no-single-repair control; a one-bit-flip localization sanity control; and a substitution
control showing
`N := K` satisfies the flag trivially (the honest claim is only that no N derived from D
does). Inputs are bound by SHA-256 in `SOURCES.json`.

## Open next questions

1. **Which weakened K contract admits these words?** Per sector, test whether the defect
   equals the sum of restored-edge cross terms introduced inside D (the PR3533 mechanism
   counted on the real word). First step: compare the JSON sector table against a D-internal
   propagation tally; blocker: a maintained policy decision on admissible weakened K
   contracts; no paid-profile gain is implied by either answer.
2. **Does the census pattern persist on other helper-mixing lineages?** The claim here is
   scoped to three named words; extension requires rerunning `verify.py`'s census function
   against new pinned words, one lineage per bounded experiment.

## Scope — what this is not

A finite certificate on three named words at the stated base. Not a proof that no
per-operation replacement can ever satisfy a weakened interface (a changed contract with
named cross-sector hypotheses escapes this census); not a supplier admission; no κ,
profile or selected-frontier change; no native, hosted or all-size replay. Full exact
legality replay (`full()`) runs as a positive control, so the words are confirmed legal
while carrying the quantified syntactic failure.

## Credit and disclosure

Credit: Nick Petalas. Produced by Nick Petalas with AI assistance.
Predecessor results retained and unchanged: PR967 (helper-star word), PR1062
(composition line), the retained PR1194 semantic route, and the pinned e8-bit-p111-tuned
owner checker, each with their own attribution. Apache-2.0.
