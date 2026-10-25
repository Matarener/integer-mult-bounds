# Every plane-port decoder costs at least 140, over every field

**Scoped proof with an exact finite certificate and two Lean-checked lemmas. No new κ.**
For the selected 112 ports matched into 56 planes (PR1825) and the strict scalar mask (PR1889),
every finite rank-one decoder, over **any** coefficient field, has additive full-plane COPY mass

    sum of tariffs  >=  18233853/131072 = 139.113...,   hence  >= 140.

This is the first global bound for the whole 56-plane decoder that holds for arbitrary rational
coefficients, in particular with even denominators. Before it, the only all-field global bound was
the fitting rank 49. The value 224 is proved only for 2-integral coefficients and characteristic 2
(Philippe Van Velzen), and for decoders split into disjoint plane pairs (#4365).

The package also states the **conjecture that 224 holds over every field**, gives the structural
conditions an escape below 224 would have to meet, and reports a numerical search over real
coefficients on the open local cases left by the three- and four-plane rank duals. That search
found no escape. It is evidence, not proof.

## Contract

Unchanged from CubeJerry's #4365, as used by `three-plane-rank-dual` and `four-plane-rank-dual`:
a term `u vᵀ` costs the binary pairing rank between the spans of the complete planes touched by
`u` and by `v`; charges add; coefficients lie in any field. The endpoint here is the full strict
112-port mask: unit diagonal, zeros inside planes and between non-orthogonal planes, free entries
between orthogonal planes. [PROOF.md](PROOF.md) states it precisely.

## Why it matters

`plane-port-copy-budgets` (josie) prices the plane-port lever: a decoder must cost at most about
160-164 per call just to match the incumbent word, and the lever map in Discussion 2278 needs about
128 for doubling κ. The bound 140 excludes the doubling target for every coefficient field inside
this contract. The break-even window `[140, 164]` stays open, and only for characteristic-0
coefficients with essential even denominators ([THEORY.md](THEORY.md), E1).

## Proof in one paragraph

On a clique `Q` of pairwise non-orthogonal planes the mask is the identity on `2|Q|` ports, so at
least `2|Q|` terms touch `Q` on both sides, over every field. Weights `w_Q >= 0` with
`sum_{Q touched by a term} w_Q <= tariff` for every possible term then give
`total tariff >= sum_Q 2|Q| w_Q` by weak duality. Tariffs depend only on the generated spans, so
the feasibility condition is a finite check over all 39,087² ordered pairs of plane-generated
subspaces. [CERTIFICATE.json](CERTIFICATE.json) gives 443 cliques with integer weights `/2^20`.
The two abstract lemmas are kernel-checked in Lean ([lean/](lean/)); the finite check is
[verify.py](verify.py).

## Evidence for the conjecture

[EVIDENCE.md](EVIDENCE.md) has the tables. In short, a sparse real-coefficient search with exact
refits found no local decoder below 4 per plane on:

- all 6 open triple classes of `three-plane-rank-dual` (the classes with no all-field certificate);
- 40 random open quadruples of `four-plane-rank-dual`, plus 3 more open ones met by chance;
- the 60 most degenerate quadruples;
- 69 groups built from the 23 induced 5-cycles and their 6- and 7-plane extensions.

A real solution space contains every rational one, so a real minimum of `4|S|` excludes every
denominator. The search is local optimization from random starts, and on 5-7 plane groups it often
stops above the baseline, so these runs are weak evidence there.

## Reproduce

From the repository root, with Python 3.12 and numpy 2:

```sh
python3 -B research/plane-port-global-rank-dual/verify.py          # bounded: every 97th row, ~1 min
python3 -B research/plane-port-global-rank-dual/verify.py --full   # all 1.53e9 pairs, ~7 min
bash research/plane-port-global-rank-dual/lean/check.sh            # Lean v4.21.0 + Mathlib cache
```

The bounded run checks the census, 20,000 tariffs against Gaussian elimination, every clique and
weight, the bound, three rejecting controls, and feasibility on 403 of 39,087 rows. The full run
writes [FULL-CHECK.json](FULL-CHECK.json): all 1,527,793,569 ordered pairs, minimum slack 0 on
1,732 tight pairs. The searches need scipy:

```sh
python3 research/plane-port-global-rank-dual/search/real_escape.py triples-open 40
python3 research/plane-port-global-rank-dual/search/real_escape.py quads-open 40 30 2026
python3 research/plane-port-global-rank-dual/search/real_escape.py quads-degenerate 60 30
python3 research/plane-port-global-rank-dual/search/real_escape.py c5 15
```

## Not covered

- The conjecture itself: no bound between 140 and 224 is proved for characteristic 0.
- The optimum of the full clique programme. A floating-point column-generation estimate suggests it
  is at most about 167, so this method alone may not reach 164; that estimate is not certified.
- Native realization, hosting, routing and the coverage law, which are #4365's caveats.
- Non-additive or concave pricing.

## Open next questions

1. **Does every decoder cost at least 224 over Q?**
   - *Why it matters:* it would close the plane-port lever for every coefficient field.
   - *First step:* turn the 2-adic layering of THEORY.md E2 into an induction on the top valuation,
     bounding what a zero-mask binary layer can save on the integral layer.
   - *Blocked by:* no known lower bound for zero-mask layers.
2. **Can a stronger functional beat the clique programme?**
   - *Why it matters:* `[140, 164]` is the break-even window; a certified value above 164 would close
     the lever in this contract without settling the conjecture.
   - *First step:* add the sharp C5 covers of `c5-residual-weighted-cover` and the four-plane
     certificates as columns, with the same exhaustive span-pair separation.
   - *Blocked by:* nothing; the column-generation code is in the fork branch named in TASK.json.
3. **Is there an exact rational escape on an open four-plane class?**
   - *Why it matters:* a cost-15 decoder would be the first mixing gain under #4365's contract.
   - *First step:* exact search with forced half coefficients (THEORY.md E1) on the lowest LP class
     of `four-plane-rank-dual`.
   - *Blocked by:* nothing.

## Credit

The contract and the two-plane theorem are CubeJerry's (#4365). The rank-dual functional
`sum_X w_X rank(M_XX)` is pinterbanget's (Ryanson Jonathan: #4421 and the four-plane extension);
this package applies it to cliques of the whole 112-port mask. The 224 bound for 2-integral decoders is
Philippe Van Velzen's (Discussion 1587, #2532). The fitting rank 49 is from PR2471 (ywz65) and
PR2484 (Sagar Thakrar). The C5 results are Tekalign's, Sagar Thakrar's and Nick Petalas's.
The plane-port budgets are josie's. Labels and matching come from PR1825/2126 (Cinna Davis).

Prepared by Mark (Matarener) with substantial Claude Code assistance in derivation, code, Lean and
writing. The verifier was written separately from the code that generated the certificate, in the
same AI-assisted project. No independent human review is claimed. Apache-2.0.
