# The fixed-point exponential is sound but not identical to the pinned series

**Scoped written proof with an exact finite certificate. No new κ.** This
contribution was produced by Nick Petalas. Apache-2.0.

[PR #3662](https://github.com/CrocSwap/integer-mult-bounds/pull/3662)
(`research/ceiling-exp-fixed-point`) added an opt-in fixed-point kernel for the
exponential of the pinned ceiling engine
(`research/complex-local-word-ceiling/ceiling.py`). It showed equal bounds on
every argument the selected ceiling search visits. Its Open next question 1
asks whether the bounds are equal for every rational argument in `[0, 1/2]`.
The answer is no, with an exact description of how far they can differ:

For every rational y in [0, 1/2], both fixed-point bounds enclose exp(y); the fixed-point lower bound equals the pinned one or is one 2^-256 step below it; the fixed-point upper bound is within one 2^-256 step of the pinned one in either direction. All three differences occur.

The upper bound can be one step **tighter** than the pinned bound. That case
needs the fixed-point loop to take one more Taylor term than the pinned loop.
Its rounded-up product stays above the stopping threshold `2^-264` where the
exact product has just fallen below it. One more term then replaces part of
the pinned tail allowance `2 t_K y/(K+1)` by the smaller `t_(K+1)`. So the
fixed-point kernel is not a uniformly more conservative version of the pinned
series. Its brackets can be wider or narrower by one step, and they remain
valid enclosures.

Explicit witnesses, all dyadic rationals in `(0, 1/2]`:

| Witness | Denominator | `y` ≈ | lower bound | upper bound |
|---|---:|---|---|---|
| `lower_below` | `2^417` | 1/3 + 5.8e-78 | one step below pinned | equal |
| `upper_above` | `2^419` | 1/3 + 5.8e-78 | equal | one step above pinned |
| `upper_below` | `2^400` | 0.0303609 | equal | one step below pinned |

[PROOF.md](PROOF.md) gives the stopping-index relations `J <= K` and
`J' ∈ {K, K+1}`, explicit rounding-error bounds below `270 · 2^-304`, and the
three-way comparison. The witnesses show that none of the allowed differences
can be removed from the theorem.

## Consequence for callers

The #3662 kernel stays a sound enclosure on its whole stated domain. It cannot
replace the pinned series byte for byte: an opt-in caller can certify a
different 256-bit bracket. The pinned file remains the authority for any
result whose published bracket must reproduce exactly. A caller that needs
only valid enclosures, rather than identical bounds, can rely on item 1 of the
theorem. This note does not check whether the selected ceiling search reaches
a differing argument beyond the screen #3662 already compared.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/fixed-point-exp-identity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/fixed-point-exp-identity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fixed-point-exp-identity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fixed-point-exp-identity --check-source-history
```

Any CPython 3.12 path can replace the local path. Expected marker:
`PASS_FIXED_POINT_EXP_IDENTITY witnesses=3 general=987 threshold=391 controls=13 no_new_kappa`.
The verifier loads both engines unchanged from their pinned paths. It checks
their SHA-256 values and writes no files. It prints a generated receipt bound
to every package file and both inputs. It checks:

- the three witnesses, with their exact step differences;
- 987 general arguments (every `a/b <= 1/2` with `b <= 60`, dyadic edge cases
  and 400 deterministic pseudo-random `2^-400` rationals) and 391 arguments
  straddling every stopping threshold `t_k y = 2^-264` with `y <= 1/2`. At
  each one, it checks the theorem's three items and the index relations, and
  checks soundness of both engines against an independent `2^-420` enclosure;
- integer replicas of both loops, which must reproduce each engine's bounds
  exactly on every argument and expose `K`, `J` and `J'`;
- 13 rejected controls: a one-term truncated series outside the one-step
  comparison, a lower series offered as an upper enclosure, six altered
  witness claims, a replica with a shifted stop rule, and four out-of-range
  arguments for the two engines.

Outcome counts over the 1,378 swept arguments, as printed: 997 equal with
equal indices, 233 equal with `J' = K+1`, 144 equal with `J = K-1`, and 4 with
the fixed-point upper bound one step tighter (all with `J' = K+1`). The sweep
counts are enumerated, not estimated, and the theorem does not depend on them.
Each direct run takes about 23 seconds locally (CPython 3.12.15, macOS 27.0.1
arm64), below the registered 300-second limit.

## Related open work

- #3729 computes an integer idle-histogram ceiling on top of the same pinned
  `ceiling.py` engine. It uses that engine's enclosures and does not compare
  them with the fixed-point kernel, so no shared number is compared here.

No other open PR touches `research/complex-local-word-ceiling` or
`research/ceiling-exp-fixed-point`.

## Open next questions

1. Does the selected ceiling search, or any registered caller of
   `ceiling.py`, visit an argument where the engines differ? A first step is
   to log the arguments of every registered caller and test each one against
   the stopping-threshold and grid-proximity conditions of PROOF.md. This
   decides whether the kernel can be used there without a separate
   bracket-equality check.
2. Can a fixed-point kernel reproduce the pinned bounds exactly, for example
   by a final exact-rational correction near a grid point or a stopping
   threshold? Both conditions are cheap to detect from the integer state, so
   a fast path plus an exact fallback may give byte identity with most of the
   speedup.
3. The same comparison applies to the `atanh` and `ln` enclosures if a
   fixed-point kernel replaces them. Their stopping rules have the same
   threshold form.

## Credit

The pinned interval engine is Douglas Colkitt's
`research/complex-local-word-ceiling`. The fixed-point kernel, its selected-word
equality check and the open question are Riquelme Soares's (hevlyo)
`research/ceiling-exp-fixed-point`, merged in #3662. This package does not
modify either file. The new contribution is the all-argument comparison
theorem and the witnesses. Independent human and formal proof-kernel review
are unclaimed.
