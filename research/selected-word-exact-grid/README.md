# Exact internal grid of the selected complex word

**Positive scoped result; no new κ.** Part 2 extends it to the complete #5413 body and the controller level. The selected chain runs the eight-relation body of
[PR #5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383) (Ali Romman), on Cao Yifan's #4610 word,
through #5392, #5398 and #5413. Public physical inputs, including dirty helpers and owned entries, are arbitrary
arrays on `2^-f Z[i]`. At payload tensor depth `lambda`, every atomic cut of this body is exact with

```text
backward program: ceil(9 lambda / 2) + 6 extra fractional bits      (11, 15, 20, 24 at lambda = 1..4)
forward program:  ceil(9 lambda / 2) + 5 extra fractional bits
stored component magnitude < H * 457 * 2^(9 lambda / 2)
```

Both guards are **attained**, so they are the exact minimum for one uniform grid. The #4610 source word gives the
same numbers. Until now the repository checked only that formal prefix norms and denominators of this word stay
below `2^192` ([eight-owned-relations/native.py](../eight-owned-relations/native.py)). For comparison, the P104
words have the sharp guard `ceil(9 lambda/2) + 2` ([p104-retimed-internal-grid](../p104-retimed-internal-grid/README.md)).
This is step 1 of target 7 in [PR #5428](https://github.com/CrocSwap/integer-mult-bounds/pull/5428).

## Model and proof

The model is the one of PR2772, PR2813 and [p104-joint-prefix-grid](../p104-joint-prefix-grid/README.md).
At an atomic cut a field standing in frame `F` holds

```text
sum_s c_s U_s^(tensor lambda) V_s(0),
```

with exact rational coefficients `c_s`, one per input `s` and native warp word. For a term without a warp word,
`U_s = Delta_F Delta_{I_s}^-1`. All charts and native maps are exact dyadic Gaussian Cliffords on nine binary
coordinates. This is inherited from the exact Clifford admission in
[kappa-round3-warp-20261022](../kappa-round3-warp-20261022/README.md). A Clifford column of Fourier rank `r` has
`2^r` nonzero entries, each a Gaussian unit times `2^(-r/2)`, so its reduced denominator is exactly
`2^ceil(r/2)` (Ross Richardson's lemma, as retained in p104-retimed-internal-grid). Under the payload lift the
rank becomes `r lambda`.

[verify.py](verify.py) replays both programs exactly over Q and records three things:

- **Dyadic coefficients.** Every scalar coefficient is dyadic; there is no odd division anywhere.
- **Fourier ranks.** For each term it computes the rank of `Delta_F Delta_{I_s}^-1` with the repository's
  Clifford compiler. As a check, that rank equals the paid rank on every one of the 3,282 to 3,290 climbs per
  program. Warp-word and owned-entry terms get the universal rank 9.
- **Pareto front.** The front of `(v2(den c_s), r)` over all terms of all cuts is `{(6, 9)}` backward and
  `{(5, 9)}` forward, so the guard is the maximum of `v2 + ceil(r lambda/2)`.

**Attainment.** Backward event 19537 adds `L321/4` into `L532`. Input `L470` occurs exactly once in the resulting
row, with coefficient `-1/64` and rank 9. Inputs are independent, so no other term cancels it: for `lambda = 1` an
input basis vector produces a component with denominator exactly `2^(6+5)`. The forward witness is event 19466,
with coefficient `-1/32` and rank 9. The largest coefficient sum `sum_s |c_s|` is 457. Since each row of a
`2^(9 lambda)`-dimensional unitary has l1 norm at most `2^(9 lambda/2)`, this gives the magnitude bound.

## Part 2: the complete #5413 body and the controller

The selected caller runs only backward bodies: 18 calls, with no forward macro calls.
[caller.py](caller.py) executes the literal `NEUTRAL-BACKWARD-v16c` body. Inside it, `PROVIDER_5402` is expanded
according to the provider's own schedule:

- main input and output wrappers;
- mode `input_K` and scalar 2;
- the 834-instruction input and output basis programs;
- the 21,473-event provider word;
- cache scalar, `output_N`, SWAP and CLEAR.

The body's 456 ADDs, 1,072 monomial maps and 8 rank-8 Gaussian jobs are executed as well. Every monomial, Gaussian
and native warp stays a symbol in its term's word. Terms reached through different operator paths therefore never
merge, which can only overstate the 2-adic exponents.

| Check | Result |
|---|---|
| Odd denominators in the whole body | none, including the `ZW = 14 I` provider |
| Owned fields at exit | all 17 zero |
| Maximum `v2` | 6, attained: provider event 19465, input 470 once, coefficient `-1/64`, one alias monomial, Fourier rank 9 |
| Body guard | `ceil(9 lambda/2) + 6`, as in part 1 |
| Main-data terms | `v2 <= 4`; Pareto front `{(3, 9), (4, 0)}` in `(v2, local rank)`, single-occurrence witnesses |
| Helper terms | `v2 <= 6`, local rank `<= 9`, fresh helper fields in each of the 18 calls |

The controller's own bank-level coefficients are all integers: ADD `+-1`, SCALE `-1`, SWAPs and 0/1 boundaries.
The global data live on 145 axes, and 224 productive targets have rank 145.

- **Lower bound 73.** A rank-145 target with unit coefficient needs `ceil(145/2) = 73` bits.
- **Upper bound 77.** A main-data term has `v2 <= 4` and rank at most 145, giving `4 + 73 = 77`. A helper term needs
  at most `6 + ceil(9/2) = 11`.

**One controller level therefore needs between 73 and 77 extra bits.** For comparison, #5413's
`FRESH-PRECISION.json` records only crude heights: about 19,452 bits per local body and 377,688 for the global word.
Pinning the exact value needs the global 145-axis charts; it is the first open question below.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/selected-word-exact-grid
python3.12 -I -B research/selected-word-exact-grid/verify.py
python3.12 -I -B research/selected-word-exact-grid/caller.py
python3.12 -I -B research/selected-word-exact-grid/test_verify.py
```

The verifier uses only the standard library and the pinned repository Clifford compiler. It takes about a minute
and prints `PASS_SELECTED_WORD_EXACT_GRID_CEIL_9L_2_PLUS_6`. Part 2 prints
`PASS_SELECTED_CALLER_BODY_GRID_6_CONTROLLER_73_TO_77` in about fifteen seconds. The controls reject a drifted input, an odd division,
a corrupted climb rank, a smaller guard claim and a tampered RESULT.json. Three more reject an odd division in a
body ADD, a missing owned CLEAR and a tampered RESULT-CALLER.json.

## Scope

Part 1 covers the eight-relation body and its #4610 source, in both programs. Part 2 covers the complete #5413
runtime body and brackets the controller level. Native operator correctness, the
canonical-chart convention and the tensor-lift convention stay inherited premises. It is an exact-grid statement,
not a rounded execution, a paid recursive implementation or a supplier admission. The selected record is unchanged.

## Open next questions

- **Controller exact value.** What is the exact controller-level guard inside 73..77? First build the global
  145-axis charts from the #5413 plan files and compute the Fourier rank of every main-data term with `v2 >= 1`.
- **Recursive price.** What does the attained guard cost in the recursive invoice? #5419 shows that a uniform
  paid-precision factor above about 1.0046 removes the 0.0033 margin. First compare the guard with the retained
  precision_tape packing.

## Credit

Cao Yifan (#4610) supplied the word. Ali Romman (#5377, #5383) and the eight-owned-relations package supplied the
relation body. Ross Richardson supplied the Clifford denominator lemma. The P104 grid packages (PR2674, PR2772,
PR2813) supplied the model. zxv's #5428 named precision composition as a target. Prepared by Mark (Matarener)
with substantial Claude Code assistance. New work is Apache-2.0.
