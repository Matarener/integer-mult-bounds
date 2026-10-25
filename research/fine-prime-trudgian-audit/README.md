# Fine-prime interval step of #4100 holds at its caller

**Scoped audit; no new κ, no scientific acceptance of #4100.** Selected κ stays
0.001672660197076918 (#1094).

## Proposition and caller

[#4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) (Cinna Davis) selects the
source lengths in PROOF.md "Sizes, setup and elementary fallback". The caller has
`d=Theta(p^epsilon)`, `epsilon=1-10^-30`, targets `t=2^ell` or `2^(ell-1)` with
`ell=Theta(p^(1-epsilon))`, and distinct odd primes `s_i` with `theta_i=t_i/s_i-1` in
`[1/(4p^2),1/p^2]`. The supporting argument is `vendor/FINE-PRIME.md` §1, restated in
GAUSSIAN.md lines 13–19. With `eta=1/(4p^2)` it takes `s` in `((1-2eta)t,(1-eta)t]`. It then
applies Trudgian's Theorem 2 ([arXiv:1401.2689v2](https://arxiv.org/abs/1401.2689v2)):

    |pi(x)-li(x)| <= 0.2795 x (log x)^(-3/4) exp(-sqrt(log x/6.455)),   x >= 229.

The claim is that the interval eventually holds at least `t/(8p^2 log t)` primes. This is more
than `d`, and the trial-division search costs `2^o(p)`.

The [#4311 coverage map](https://github.com/CrocSwap/integer-mult-bounds/pull/4311) listed
"the fine-prime interval at #4100's parameters" with no audit found.

## Result

The step holds as stated. No correction is needed.

1. **Citation.** The statement, its constants and the range `x>=229` match Theorem 2 of the arXiv HTML v2.
2. **Theta range.** For `s` in the interval, `1/(4p^2) < theta < 1/(2p^2-1) <= 1/p^2`. The lower
   end is attained at `s=(1-eta)t`. The open end corresponds to `s -> (1-2eta)t`. This is checked
   exactly for `p=2..199`, and the algebra is uniform in `p`. Each `s_i/t_i > 1-1/(2p^2)`, so
   `S/T > 1-d/(2p^2) > 1/2` whenever `d<=p`.
3. **Dominance.** `li((1-eta)t)-li((1-2eta)t) >= eta t/log t`. The function
   `x(log x)^(-3/4)exp(-sqrt(log x/R))` increases for `x>=229`, so both endpoint errors are at most
   its value at `t`. If `16 p^2 * 0.2795 * L^(1/4) * exp(-sqrt(L/6.455)) <= 1` with `L=log t`, the
   count is at least `eta t/(2L) = t/(8p^2 log t)`. Here `L=Theta(p^(10^-30))`, which outgrows
   `(2 log p)^2`, so the test holds for all large `p`. The count then exceeds `d`, because `t` is
   exponential in `p^(10^-30)` while `d p^2 log t` is polynomial in `p`.
4. **Explicit threshold.** The required `ell` is about `6.455 (2 ln p)^2 / ln 2`. With the caller
   constant taken as `ell ≈ p^(10^-30)/6`, the test first holds at `ln p ≈ 1.5·10^32`. Smaller
   inputs use the elementary fallback that PROOF.md already specifies, which affects only finitely
   many lengths. The value is legitimate but astronomical. It depends on the unspecified constant
   in `d=Theta(p^epsilon)` and is reported for orientation, not as a claim.
5. **Search cost.** The interval has `eta t` candidates and each needs `O(sqrt t)` trial divisions,
   so the total is `d 2^(1.5 ell) poly(p)`. Its logarithm is `O(p^(10^-30)+log p)=o(p)`, which
   gives setup `2^o(p)=o(V)`.
6. **Small exact counts.** For `p` in {2,3,4,6,8,12} and `ell` in {24,28}, a segmented sieve finds
   about twice `t/(8p^2 log t)` primes in the interval. Trudgian's test does not yet apply at these
   sizes, so these counts are sanity checks only.

**Relation to #4029.** [#4029](https://github.com/CrocSwap/integer-mult-bounds/pull/4029) (ToikY)
proves prime supply in `(t(1-1/(3d)), t(1-1/(4d))]` for `2<=d<=ell^334`. At `epsilon=1-10^-30`,
`log d/log ell ≈ 10^30`, so that domain does not reach #4100's caller. #4100 therefore needs its
own Trudgian argument, which is the one checked here. #1797 audited the older conditional
PR1786 interval with `theta>=1/(4d)`.

## Reproduce

```sh
python3.12 -B research/fine-prime-trudgian-audit/verify.py
python3.12 -B research/fine-prime-trudgian-audit/test_verify.py
python3.12 scripts/research_package.py --package research/fine-prime-trudgian-audit
```

Each run takes under a second. The rejecting controls are:

- `log t=Theta(log p)` never passes dominance.
- The #4029 domain excludes the caller.
- `eta=0` gives no admissible `theta`.
- A direct sieve sanity count.

## Open next questions

- **FINE-PRIME §2 conditioning at the smaller theta.** Does
  `||K^-1|| <= O(alpha^5 rho^2 theta^-2 exp(a rho/3))` stay polynomial at the GAUSSIAN.md caller
  when `theta=1/(4p^2)`? The fine primes help only if it does. First step: compare it against
  PR1758's explicit symbol bound. Nothing blocks it. See `open_questions` in [TASK.json](TASK.json).

## Credit

The construction and argument are by Cinna Davis (#4100). The cited prime theorem is due to Tim
Trudgian. The neighbouring prime-supply lemma is ToikY's #4029, and the coverage map is #4311.
This audit was prepared for Mark (Matarener) with substantial Claude Code assistance. Apache-2.0.
