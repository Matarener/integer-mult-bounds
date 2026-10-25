# Independent check: the UT3(F4) central-triple register model

**Result class: independent reproduction plus a bounded search failure.** No new
kappa. The selected conditional result stays
`kappa = 0.001672660197076918`.

## What was checked, and how

Two open results use one formal register model. In `F_2[UT_3(F_4)]` with
`F_4 = F_2[w]/(w^2+w+1)`, a paid call is

```text
D_N(g) = I + ([g] + [1]) N,
```

with `g` one of the six axis involutions `X_1, X_w, X_{w^2}, Y_1, Y_w, Y_{w^2}`
and `N` a rank-one idempotent in `M_r(F_2)`. The target on `r >= 3` registers is

```text
diag([Z_1], [Z_w], [Z_{w^2}], [1], ..., [1]),   Z_c = (0,0,c).
```

[PR #3774](https://github.com/CrocSwap/integer-mult-bounds/pull/3774) proves the
four-label minimum 12; [PR #3788](https://github.com/CrocSwap/integer-mult-bounds/pull/3788)
extends it to six labels. [PR #3784](https://github.com/CrocSwap/integer-mult-bounds/pull/3784),
[#3785](https://github.com/CrocSwap/integer-mult-bounds/pull/3785),
[#3786](https://github.com/CrocSwap/integer-mult-bounds/pull/3786) and
[#3783](https://github.com/CrocSwap/integer-mult-bounds/pull/3783) record the
same floor and its finite counts in a second, separately written form.

This package rebuilds the model from the stated definition, using no code from
those packages, and checks it. `model.py` carries two layers: the group algebra
`F_2[H]` as 64-bit masks over an explicit product table, and the regular
representation `rho tensor id`, which is injective, so matrix equality in
`M_{6r}(F_2)` is equivalent to word equality in `F_2[H] tensor M_r(F_2)`.
Everything below is measured on this implementation.

| Check | Result |
|---|---|
| Group law: closure, full associativity, identity, inverses | order 64, all pass |
| Six paid labels involutions; nine commutators | 6 and 3 distinct `Z` labels, all equal to `(0,0,alpha beta)` |
| Rank-one matrices of `M_3(F_2)` (exhaustive over 512) | 49 rank-one, 28 rank-one idempotent, 21 trace-zero |
| `u v^T` enumeration against exhaustive rank-one idempotents | identical 28-element set |
| Mixed twelve-call word on `r = 3, 4, 5` | realizes the target; every extra register fixed |
| Both-new twelve-call word on `r = 3, 4, 5` | realizes the target; every extra register fixed |
| Single-deletion controls, both words | 24 of 24 deletions fail |
| Block collapse versus the direct matrix product, 40 random words | 0 mismatches |
| Block relation on the class sums, kernel dimension | rank 18 of 27, kernel 9 = the equal triples |
| Stacked corner: block ranks, total rank | 2, 2, 2 and rank 6 |
| Uniform random words, length 6-11, `r = 3` | 20000 trials, 0 realizing |
| Class-sum-feasible words, shapes 4+4 to 6+5, `r = 3` | 18734 tested, 0 realizing |

The class-sum-feasible family is the useful part of the search. Expanding the
product of the calls gives `I + sum_k E(g_k) tensor N_k` plus the surviving
second-order corners; the vanishing of the `(0,1)` and `(1,2)` blocks then
forces the three per-letter-class idempotent sums on each side to agree, and
that relation is checked here as a linear map: rank 18 on a 27-dimensional
domain, so its kernel is exactly the nine-dimensional space of equal triples.
The
search samples that family shape by shape, with class multisets built from
cancellation pairs plus one unpaired idempotent where the parity requires it.
All eight call-count shapes from `4+4` to `6+5` were drawn at least 1150 times
each (`4+4: 1249`, `4+5: 2541`, `4+6: 1273`, `5+4: 2519`, `5+5: 4928`,
`5+6: 2596`, `6+4: 1150`, `6+5: 2478`). No word of length at most eleven
realizes the target.

## What this does not establish

- **No machine-verified lower bound.** The step from the finite corner,
  row-space and diagonal-lift inequalities to every `r >= 3` is a written
  argument in the checked results. This package reproduces the finite pieces
  and a witness half; it does not verify that step, so "minimum 12" remains
  author-proved, not independently proved.
- **A bounded search failure is not a lower bound.** The search covers one
  subfamily exhaustively in shape but only by sampling, and it excludes even
  call counts with a nonzero common value, which the cancellation-pair
  construction does not reach.
- **The `82160`-subset diagonal-lift census of PR #3788 was not reproduced.**
- **No physical content.** Twelve calls are a formal per-call price in this
  alphabet: no supplier, hosting, restoration or kappa claim is made, and none
  of these calls is priced against the selected construction.
- Two real defects were found in this package's own first draft by its own
  checks (a trace parity test and the surviving-pair order); both are fixed in
  the committed code and the checks that caught them are retained.

## Reproduce

```sh
python3.12 -I -O -Werror -B research/ut3-central-triple-independent/verify.py
```

Expected: `PASS_UT3_CENTRAL_TRIPLE_INDEPENDENT order=64 involutions=6
idempotents=28 trace_zero=21 witnesses=2 deletions=24 uniform_trials=20000
class_sum_tested=18734 shorter_words=0`

The run is deterministic (seeded `20261018`) and takes a few seconds. It writes
`RESULT.json` with a SHA-256 receipt over its own sorted payload.

## Open next questions

1. **Can the all-`r` step be machine-verified instead of inspected?** It is the
   only part a formal kernel could still reject. First step: encode the corner
   and row-space inequalities as a finite linear-algebra statement with symbolic
   `r`, or prove a residual bound by hand.
2. **Is the minimum decided without the four-label split, on even call counts
   with a nonzero class sum?** The sampled family does not reach those shapes.
   First step: extend the class-sum-feasible construction with sums of three
   idempotents that are not a cancellation pair.
3. **Can one of the twelve formal calls be embedded in a pinned bit supplier
   below the complete price of a rank-one factor?** Without an embedding the
   count carries no physical saving. First step: price one legal physical
   commutator pair including frames, hosting and restoration.

## Credit

Credit the authors and predecessors of PR #3774, PR #3788, PR #3784, PR #3785,
PR #3786, PR #3783, and of the earlier UT3/D8 central-commutator line
(#2261 and its lineage) for the model, the witnesses and the floor claims this
package checks. Package produced by Nick Petalas with AI assistance. Independent
human and formal proof-kernel review are unclaimed. Apache-2.0.
