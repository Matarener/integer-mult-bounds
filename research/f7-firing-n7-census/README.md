# The fixed L/2 firing census at n = 7, L = 18 and 20

**Claim type: an exhaustive finite census. No new κ.** It answers #4322's
open question 2. The selected conditional κ stays `0.001672660197076918`.

## Object

[PR #4322](https://github.com/CrocSwap/integer-mult-bounds/pull/4322)
(unpaidmoon) asks which functionals of the fixed `L/2` substitution fire at
`(7, 18)` and `(7, 20)`. #1166 comment 19021170 names that census as the one
that "can change a maintained exclusion". #4322 left it open because of the
size of the seven-label state space.

The model is #4322's:

- canonical first-occurrence words;
- simple restored prefix walks on `F_2^n`, universal when the difference set
  of the prefix states is all of `F_2^n`;
- a mask fires on a universal word when `base < excess ≤ base + d²`.

**A mask can fire only on a universal word.**

## Results

| n | L | closed canonical words | universal | false prunes | firing masks |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 14 | 161,936 | 0 | 0 | 0 |
| 7 | 16 | 4,578,096 | 0 | 0 | 0 |
| **7** | **18** | **133,421,988** | **0** | 0 | **0** |
| **7** | **20** | **3,857,028,444** | **0** | 0 | **0** |
| 6 | 16 | 2,262,380 | 6,744 | 57,456 | 54 of 63 |
| 6 | 18 | 39,195,780 | 1,854,738 | 7,788,600 | 59 of 63 |

**Answer to #4322's open question 2.** No functional fires at `(7, 18)` or
`(7, 20)`, because neither domain has a single universal word. The fixed
substitution therefore cannot falsely prune at those lengths, so it cannot
have affected an exclusion made there.

**Corroboration and a positive control.**

- **Random walks at length 20.** Seeded random closed walks find no universal
  word in 20,000 samples, and none in about 800,000 at lengths 20 to 24.
- **Random walks at length 26.** They do find universal words (10 in 20,000).
  So the universality test can fire at `n = 7`, and the universal domain at
  `n = 7` starts somewhere between 22 and 26.

**Agreement.** Every overlapping published row is reproduced exactly:

- #3699's closed and universal counts at `(6,12)`, `(6,14)` and `(7,14)`;
- #3733's `(5,14)`;
- #4322's 2,262,380 closed words at `(6,16)`.

The Python port reruns `(6,12)`, `(6,14)` and `(7,14)` in CI.

## Method

`census.c` extends my #4348 enumerator to 128-bit state and difference masks.
`verify.py`:

- checks that `evidence/CENSUS-RUNS.txt` was recorded for this `census.c`, by
  SHA256;
- compares every published row;
- reruns the small domains in Python;
- runs the seeded random controls.

The large runs are local evidence that CI does not repeat. `(7, 20)` took 36
minutes.

## Not covered

- **`(7, 22)` and `(7, 24)`.** They are too large for a plain census. The
  random search found no universal word there in about 500,000 samples, but
  that is not a proof.
- **`(6, 20)` and longer.** Also any change to a retained exclusion: this
  only shows the substitution cannot have pruned falsely at `(7, 18)` or
  `(7, 20)`.

## Reproduce

```sh
python3.12 -B research/f7-firing-n7-census/verify.py
cc -O2 -o census research/f7-firing-n7-census/census.c && ./census 7 18
```

The first prints `PASS_F7_FIRING_N7_CENSUS` in about 9 seconds, using only
the standard library.

## Open next questions

1. **Find the first `n = 7` length with a universal word, 22, 24 or 26.**
   - *Why it matters:* below that length the substitution is vacuously sound
     at `n = 7`.
   - *First step:* a census of `(7, 22)` restricted to walks using all seven
     labels, with symmetry pruning.
   - *Blocked by:* the size of a plain census.

## Credit

The model and question are unpaidmoon's (#4322), building on Nick Petalas's
#3699 and #3733 and the PR943 walk. Prepared by Ryanson Jonathan with
substantial Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
