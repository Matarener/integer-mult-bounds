# Audit of PR6134's stochastic rank-power frontier

Audit by Josie Elliston with Claude Opus 5.5 (Anthropic) assistance. Apache-2.0.
Claim type: independent proof review with exact finite corroboration. No new
κ, supplier or selected-frontier change.

Audited: [PR6134](https://github.com/CrocSwap/integer-mult-bounds/pull/6134)
by Nick Petalas, head `b7889209ef72f7086d49024cd7c35c1d55ed61d8`, package
`research/randomized-query-power-frontier/` (hashes in [SOURCES.json](SOURCES.json)).
Base main `721c03822c421b7f7fcbb2598993b947c4d88419`.

## Verdict

**No error.** Every step of PROOF.md holds as written for complex matrices,
`1 <= R <= k`, `0 < t < 1` and `0 < B <= R^t`:

```
inf omega(A) = k/(bR) - 1,   b = B/R^t,
```

attained by the stated thinned coordinate law. The `R = k` uniqueness
statement and the saving corollary `epsilon^2/(1+epsilon^2)` (`1/4097` at
`epsilon = 2^-6`) are correct. PR6134's verifier replays `PASS` under
CPython 3.12.14, normal and `-O` (about 7 s each).

## Step-by-step review

1. **Pointwise trace bound.** `PA = A` for the orthogonal projection `P`
   onto the image, so `tr A = <P, A>_F`, and `|tr A| <= sqrt(r) ||A||_F`
   by Cauchy-Schwarz with `||P||_F = sqrt(r)`. Valid for nonnormal `A`.
2. **Inequality (3).** `k = E tr A`, then `|E tr A| <= E |tr A| <=
   E[sqrt(r) ||A||_F] <= sqrt(E r) sqrt(E ||A||_F^2)`. Correct; the finite
   second moment makes every term finite.
3. **Price step.** `r <= R^(1-t) r^t` for integer `0 <= r <= R` is
   `(r/R)^(1-t) <= 1`, strict for `0 < r < R` when `t < 1`. So
   `E r <= R^(1-t) B`.
4. **Error identity.** `E ||A - I||_F^2 = E ||A||_F^2 - 2 Re tr E A + k
   = E ||A||_F^2 - k` by unbiasedness.
5. **Worst input.** `omega = lambda_max(C)` for `C = E (A-I)^*(A-I)`, and
   `lambda_max(C) >= tr C / k`. Combining: `omega >= k/E r - 1 >= k/(R^(1-t) B) - 1`.
   Note that `E r > 0` because `E A = I`.
6. **Attainment.** With probability `b`, `A = (k/(bR)) P_S` for a uniform
   `R`-subset `S`: `E A = I`, `E (rank A)^t = b R^t`, `C = (k/(bR) - 1) I`.
7. **Uniqueness at `R = k`.** Equality forces `r` into `{0, k}`, then
   `A = alpha I` on each nonzero branch, one common `alpha` (Cauchy-Schwarz
   equality fixes `|alpha|`; `|E tr A| = E |tr A|` fixes its phase), and
   `alpha = 1/b` with probability `b`. Correct.
8. **Corollary.** `k/(bk) - 1 <= epsilon^2` gives `1 - b <= epsilon^2/(1+epsilon^2)`.

## Findings

**F1 (strengthening, proper cap `R < k`).** PROOF.md states the general
attaining family only as a sufficient construction. The converse also holds,
which completes the equality set for every cap:

> For `R < k`, `omega(A) = k/(bR) - 1` holds exactly for the laws with
> `A = 0` with probability `1 - b` and, otherwise, `A = (k/(bR)) P` for a random
> rank-`R` orthogonal (Hermitian) projection `P` with `E[P | A != 0] = (R/k) I`.

*Proof.* Equality forces equality in steps 1-5. Step 3 forces `r` into
`{0, R}`, and `E r^t = B` (otherwise step 3 is strict), so `P(r = R) = b`.
Step 1 forces `A = alpha P` with `P` the image projection. Step 2's two
equalities force `|alpha|` and the phase of `tr A = alpha R` to be common,
so `alpha` is common. Then `E A = b alpha E[P | r = R] = I`, and the trace
gives `alpha = k/(bR)` and `E[P | r = R] = (R/k) I`. Conversely, every such law
has `C = b alpha^2 (R/k) I - I = (k/(bR) - 1) I`, so step 5 is an equality too.
At `R = k` the only such `P` is `I`, which recovers (2). ∎

So the optimal laws for a proper cap are exactly the rank-`R` projection
designs that are isotropic in mean, scaled and thinned. Coordinate and Walsh
subsets (PR6134's verifier) are two instances; the tetrahedral and
Pythagorean frames checked here are others.

**F2 (precision, not an error).** Equality in (3) alone does not force one
common rank: a law with one common scale and ranks `1` and `2` attains (3)
exactly (checked at `k = 3`). The endpoint-rank conclusion comes only from
the strict concave price in step 3, which PROOF.md uses correctly. Hence
`t < 1` is essential to the uniqueness statement; at `t = 1` mixed-rank
laws are also optimal.

**F3 (wording).** PROOF.md says "An arbitrary dirty auxiliary state cannot
defeat the stated lower bound: restrict it to zero." The analyst cannot
restrict an implementation's random auxiliary state. The conclusion still
holds by another route: if the response is `A x + c` with `c` independent of
`x` (and possibly correlated with `A`), unbiasedness at `x = 0` gives
`E c = 0`. Averaging the inputs `x` and `-x` gives
`E ||(A-I)x||^2 + E ||c||^2`, so the worst input is never below the
linear-part error. The verifier exhibits an offset that lowers the error at one
input (`0` instead of `1`) while the opposite input pays `4`. The suggested fix is
to replace that sentence with the `±x` argument.

**F4 (verifier coverage, not an error).** PR6134's check "only endpoint
ranks attain" runs only on laws that it built with endpoint ranks, so it is
tautological. Its verifier never tests the lower bound on a non-attaining
law. This package adds that coverage for the trace steps (1, 2, 4, 5); see below.

Remark (not checked beyond the proof sketch): if inputs are promised to lie in
a known `d`-dimensional subspace with `R <= d`, the same argument applied to
`tr(QAQ)` with `Q` the subspace projector gives `d/(bR) - 1`. Coordinate
sparsification inside the subspace attains it. This quantifies one of
PR6134's listed escapes as "replace `k` by `d`", not as a new saving.

## Independent exact checks

[verify.py](verify.py) is standard-library Python. It was written from
PROOF.md's statement and imports no code from PR6134. It works over real
rational matrices; the complex case rests on the written proof.

- **Random unbiased laws.** The verifier builds 2,631 seeded laws as `A_i = M_i M^{-1}`
  (`M = sum p_i M_i`, entries in `{-1, 0, 1, 2}`, `k <= 3`, up to three
  outcomes). These have oblique, nonsymmetric and mixed-rank outcomes.
  On every law, inequality (3) and `tr C/k >= k/E r - 1` hold, and some
  basis input `e_i` already has error `C_ii >= k/E r - 1`. The last step
  `E r <= R^(1-t) E r^t` is a per-outcome elementary inequality and is not
  evaluated (`E r^t` is irrational). Each of the
  1,343 exact equalities has every nonzero outcome equal to `alpha P` with
  one common `alpha`. Most are trivial (`A = I` or `k = 1`); four have `k >= 2`
  and two distinct nonzero outcomes, and one has mixed ranks (F2).
- **Non-coordinate attainers.** The verifier checks four rank-one frames in `k = 2, 3`
  at `b` in `{1, 1/2, 3/7}`, plus a rank-two tetrahedral-complement law at
  `b = 2/3`. Each has exactly isotropic `C = (k/(bR) - 1) I`.
- **Necessity controls.** An oblique rank-one idempotent law, an
  unequal-scale law and a mixed-rank, mixed-scale law are all strict.
  A mixed-rank law with one common scale attains (3) (F2).
- **Auxiliary offsets.** The `±x` identity of F3 is checked exactly.

```
python3.12 -I -W error -B research/audit-pr6134-query-power-frontier/verify.py
python3.12 -I -O -W error -B research/audit-pr6134-query-power-frontier/verify.py
```

Both commands print `PASS_AUDIT_PR6134` in about 0.3 s. They also pass under
CPython 3.10.

## Remaining obligations

These are unchanged from PR6134. The response-rank-to-price bridge to any
actual supplier is unproved, so this relaxation is not attached to any
invoice, compiler or multiplication theorem. Biased, adaptive, nonlinear and
retry-based schemes are outside its contract. This audit covers PR6134's head
above only.

## Open next questions

1. Does the frontier survive a bridge that charges `r^t` only up to constants
   (`c r^t <= price <= C r^t`)? A real supplier bridge is unlikely to be
   exact, so the saving corollary would then become a ratio statement.
   First step: rerun step 3 with `E price >= c E r^t` and record the saving
   fraction at `epsilon = 2^-g`. Not blocked.

## Credit

The theorem, attaining law and corollary are Nick Petalas's (PR6134). The
trace/rank inequality and coordinate sparsification are classical; PR6134
credits Safaryan, Shulgin and Richtárik for the latter.
