# Every plane-port decoder costs at least 141, over every field

**Exact finite certificate for a scoped lower bound. No new κ.**
Take the strict 112-port mask with its 56 matched planes (PR1825, PR1889) and CubeJerry's
additive full-plane COPY tariff (#4365). Every finite rank-one decoder of this mask, over any
coefficient field, costs at least

    36732955/262144 = 140.1251...,   hence  >= 141.

This raises the all-field floor of Mark (Matarener)'s
[PR #5560](https://github.com/CrocSwap/integer-mult-bounds/pull/5560)
(`research/plane-port-global-rank-dual`) from 140 to 141. It answers that package's Open next
question 2 ("Can a stronger functional beat the clique programme?") with a better point of the
same programme. It does not reach the break-even value 164 or the 224 conjecture.

## What is new

The proof is #5560's, unchanged. Lemma 1 says a clique `Q` of pairwise non-orthogonal planes
carries an identity block, so at least `2|Q|` terms touch it on both sides. Lemma 2 is weak
duality, and Lemma 3 reduces condition (F) to ordered pairs of plane-generated subspaces. Any
nonnegative clique weights that satisfy

    sum over cliques Q with a plane inside A and a plane inside R of w_Q  <=  t(A, R)

for every ordered pair `(A, R)` of the 39,087 generated subspaces therefore bound every decoder
by `sum_Q 2|Q| w_Q`. See #5560's [PROOF.md](../plane-port-global-rank-dual/PROOF.md).

The new part is the weight vector. #5560's 443 columns give 139.11. This
[CERTIFICATE.json](CERTIFICATE.json) has 425 clique columns, of sizes 1 to 24, with integer
weights over `2^20`. Their value is 140.1251. The columns came from fresh row-and-column
generation. The pricing step is a local search over cliques, against duals of
the active span-pair rows. Every round separated exhaustively over all 1,527,793,569 ordered pairs.

## Evidence

[verify.py](verify.py) was written separately from the generator. It checks, in exact arithmetic:

- the 56 planes from the pinned archive and matching, each nondegenerate, with 109 orthogonal pairs;
- an independent closure census by reduced echelon bases: 39,087 subspaces;
- the tariff `dim A - dim(A meet R^perp)`, compared with Gaussian elimination of the pairing
  matrix on 4,000 random pairs;
- every column is a clique with a positive integer weight;
- feasibility on **all** 39,087² ordered pairs. The minimum slack is 0. It is attained exactly
  on the 1,732 pairs with tariff 0, which no clique can touch, and every positive-tariff pair
  has positive slack;
- the recorded bound 36732955/262144 > 140;
- four rejecting controls: an overweight column, an orthogonal pair as a clique, a wrong
  recorded bound, and #5560's own certificate, which passes feasibility but stays at 139.11 < 140.

Load sums stay below 2^40 and census counts are at most 512, so the floating-point matrix
products are exact. The full run takes about 30 seconds on a 2026 Apple laptop.

## Reproduce

From the repository root, with CPython 3.12 and numpy 2:

```sh
python3.12 -B research/plane-port-clique-floor-141/verify.py             # full check, prints PASS_PLANE_PORT_CLIQUE_FLOOR_141
python3.12 -B research/plane-port-clique-floor-141/verify.py --sampled   # every 97th row only
python3.12 -B scripts/research_package.py --package research/plane-port-clique-floor-141
```

Optional regeneration, which needs scipy and is not part of the proof:

```sh
PLANE_PORT_CACHE=/tmp/ppcf python3.12 -B research/plane-port-clique-floor-141/generate/colgen.py 1 40
PLANE_PORT_CACHE=/tmp/ppcf python3.12 -B research/plane-port-clique-floor-141/generate/roundcert.py
```

`colgen.py` starts from #5560's columns and all singletons. It stops at the first point
certified above 140. `roundcert.py` floors the weights onto the `2^20` grid and checks them
exactly. It writes the certificate into the cache directory. The cache holds a 1.5 GB tariff
matrix. On macOS with CPython 3.12.15, numpy 2.5.4 (Accelerate) and scipy 1.18.1, the generator
stopped after 14 rounds, in about 6 minutes. It reproduced this CERTIFICATE.json byte for byte.
Other BLAS or HiGHS builds may produce a different valid certificate, and verify.py checks
whichever certificate is present.

## Not covered

- The optimum of the clique programme. #5560 reports a floating-point pricing estimate of
  about 167. This run did not price exactly, so no upper bound is certified here.
- The conjecture that 224 holds over every field. The interval [141, 224] stays open for
  characteristic-0 coefficients with even denominators.
- Native realization, hosting, routing, the coverage law and concave pricing. These are
  #4365's and #5560's caveats. No supplier, κ or selected-frontier change follows.

## Open next questions

1. **What is the optimum of the clique programme, and is it above 164?** A certified value
   above 164 would close the plane-port lever in #4365's contract for every field. *First step:*
   raise `STOP` in `generate/colgen.py` and add an exact MILP pricer, which also certifies an
   upper bound. *Blocked by:* local-search pricing found fewer than ten new columns per round
   near 140.
2. **Can non-clique columns do better?** #5560's estimate of about 167 leaves little room above
   164. *First step:* add the sharp C5 covers of `c5-residual-weighted-cover` and the three- and
   four-plane rank duals as columns, with the same exhaustive separation. *Blocked by:* nothing.
   One separation pass takes about 15 seconds.
3. **Does every decoder cost at least 224 over Q?** This is #5560's conjecture. *First step:*
   #5560 THEORY.md E2, induction on the top 2-adic valuation. *Blocked by:* there is no known
   bound for zero-mask binary layers.

## Credit

The clique programme, Lemmas 1-3 and the 140 certificate are Mark (Matarener)'s
([#5560](https://github.com/CrocSwap/integer-mult-bounds/pull/5560)). That package's own credits
also apply. The contract and two-plane theorem are CubeJerry's (#4365). The rank-dual
functional is pinterbanget's (#4421). The 224 bound for 2-integral decoders is Philippe Van
Velzen's (Discussion 1587, #2532). The plane-port budgets are josie's (#1808). The labels and
matching come from PR1825/2126 (Cinna Davis). The new certificate, generator and verifier were
produced by Nick Petalas. Apache-2.0.
