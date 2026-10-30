# R439 K defect equals the D-internal cross-term tally

**Finite certificate. No new kappa.** Selected κ stays
0.001672660197076918. This does not adopt a weakened `K_equals_D` contract
and does not change a paid profile.

## Question

PR #4092 left this comparison open on the three retained R439 helper-star
words: does the syntactic `K_equals_D` defect equal the restored-edge cross
terms introduced inside `D`? The first step named there is to compare the
sector table with a D-internal propagation tally. Card `bit-helper-contract`,
scope refined to that comparison.

## Statement

Fix a word with target count `v` and helper count `R`. Helper columns are the
bits of registers `2v .. 2v+R-1`.

- `K_t` is the helper-column mask on target `t` after the frame-free symbolic
  replay of `(A, scatter, B)`. Register `r` starts as column `e_r`.
- `N_t` is the XOR of the register ids named by `D`-gates whose destination
  is target `t`.
- `E_t` is the helper-column mask actually xored into target `t` when `D` is
  executed alone from those same identity columns.
- The cross-term tally is `C_t = E_t XOR (N_t restricted to helper columns)`.

For an arbitrary `D` section, `C_t` also equals the XOR, over target writes,
of (helper columns delivered by that write) XOR (helper registers that write
names). Helper-to-helper gates affect `C` only by changing a later delivery.
The syntactic defect `K_t XOR (N_t restricted to helper columns)` equals `C_t`
exactly when `E_t = K_t`.

## Result

On all three pinned words, `E_t = K_t` for every one of the 111 targets, and
every helper register is back to its own column at the end of `D`. Therefore
the defect table and the cross-term tally are the same bit set:

| word | `D` gates | targets | defect bits | sectors |
|---|---:|---:|---:|---:|
| `r439-helper-stars-seed19` candidate | 1,165 | 111 | 17,636 | 439 |
| `r439-bsection-stars-seed01` composition | 1,165 | 111 | 17,636 | 439 |
| `r439-bsection-stars-seed01` candidate | 1,195 | 111 | 17,653 | 439 |

The owner checker agrees on the raw helper part and reports syntactic
`K_equals_D` false on each word. Deleting the first helper-to-helper gate
makes `E` differ from `K` on each word, so the match is not a property of
`K` alone. A three-gate restored edge `h0 ^= h1`, `y ^= h0`, `h0 ^= h1`
with an empty raw word has nonzero cross term `h1` and defect equal to the
named column `h0`, so the equality is not true for every `D` section.

The 17,636 and 17,653 figures are the same defect totals PR #4092 counted.
This package adds the identification of those bits with executed-versus-named
columns inside `D`, including target-to-target reads that carry helper
columns written earlier in `D`. It does not re-derive the single-gate or
single-bit repair census.

## What is not established

`E = K` is a certificate for these three words, not a replacement lemma.
The synthetic edge is a counterexample to adopting "compare `K` with executed
delivery" with no extra hypothesis. The 612 target-to-target reads inside
`D` remain a separate H2 read-kind failure; matching the masks does not erase
them. No supplier, native schedule, all-size transfer, or selected-frontier
change is claimed. The bit side does not bind the selected exponent.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3 -B research/r439-k-cross-term-tally/verify.py
python3 -I -O -Werror -B research/r439-k-cross-term-tally/verify.py
python3 scripts/research_package.py --package research/r439-k-cross-term-tally
```

Expected:

```text
PASS_R439_K_CROSS_TERM_TALLY words=3 targets=111/111/111 equal_targets=111/111/111 defect_bits=17636/17636/17653 cross_bits=17636/17636/17653 sectors=439/439/439 helpers_restored=3/3 checker_K_equals_D=false/false/false mutation_breaks=3/3 synthetic_unequal=1 no_new_kappa
```

The verifier exits nonzero on a pin mismatch, a target mismatch, a checker
disagreement, a mutation that still matches, or a synthetic edge that fails
to separate the two masks. Runtime is well under a minute.

## Open next questions

1. Which extra hypothesis makes `E = K` true outside this triple? The
   synthetic edge shows an unconditional reading is false. One further pinned
   helper-mixing word would separate a construction accident from a legal-word
   identity. Admitting that hypothesis as the H2/K contract is a policy
   decision, not a consequence of this tally.
2. After the mask comparison is read as executed delivery, which H2 clauses
   still fail on these words? The read-kind clause is the obvious candidate
   and is not settled by the mask equality.

## Credit

The three words and the syntactic flag are the retained R439 helper-star
lineage (PR #967 and PR #1062) checked by `research/e8-bit-p111-tuned`.
PR #3533 isolates one restored helper edge whose literal mask misses the
delivered column. PR #4092 (Nick Petalas) counts the resulting defect by
helper sector on these words and leaves the propagation comparison open.
This package answers that comparison only.

Prepared by unpaidmoon with substantial AI assistance (Cursor Grok).
Apache-2.0. Predecessor packages keep their own notices.
