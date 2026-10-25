# The rank-dependent fallback swap bound s ≤ 2(m − r) is false

#4237 (`research/fallback-child-count`) counts the children that
`paid_children` charges for the retained BIT fallback program. For a rank-r
projector header it proves that the elimination makes exactly r opposite-bank
swaps and s ≤ 2m − 1 − r same-bank swaps. With f ≥ 2 the program then pays
`8m² + 2m − 6 + r + 3s` children. Its first open question asks whether
s ≤ 2(m − r) for every header, which would make `8m² + 8m − 6 − 5r` the
exact rank-r maximum. This package answers it negatively:

```text
m = 6, r = 3 over Z/3^w:   s = 7 > 6 = 2(m − r),  318 children > 315
every 6 ≤ m ≤ 64, r = m − 3:  s = 7 > 6,          3 children above the formula
every 8 ≤ m ≤ 64, r = 4:      s = 2(m − 4) + 1,   3 children above the formula
```

The bound does hold on the complete idempotent censuses for (q, m) = (3, 2),
(3, 3), (3, 4), (3, 5) and (5, 3), where the maximum per rank is exactly
2(m − r). So over F₃ the smallest violating dimension is m = 6.

Claim type: **finite certificate** (explicit counterexamples through the
unchanged retained code). It refutes a conjectured formula; it does not give
the true rank-r maximum. No new κ, no audit of other #4100 premises, no
supplier admission and no change to the selected frontier.

## Setting

Use the retained `vendor/fallback_program.py` and `vendor/descriptor.py` from
`research/selected-bit-recursive-closure`, unchanged, exactly as #4237 does.
A header is an invertible chart G over R = Z/q^w and an axis set of size r;
its projector is P = G[:, axes] G⁻¹[axes, :]. `prepare` eliminates the
residual `[[I−P, PC], [CP, I−CPC]]` with the first-unit pivot rule. A swap
between positions on the same side of m is same-bank. s counts same-bank
elimination swaps.

## Counterexample

Over F₃ take the chart

```text
G6 = [[1,2,1,0,0,0],
      [2,0,0,0,2,0],
      [0,0,2,0,2,0],
      [1,2,0,0,0,2],
      [2,1,1,2,1,0],
      [1,2,0,0,2,2]]
```

with axes {0, 1, 2}, so r = 3 and m = 6. The elimination makes 3 opposite
swaps, as the rank law requires, and 7 same-bank swaps: 3 in the head phase
and 4 in the tail phase. The bound 2(m − r) = 6 fails by one. Through
`paid_children` this header pays 164 children at f = 1 and 318 at f ≥ 2,
against the conjectured 315. The same digits as a chart over Z/9 and Z/27,
with zero high digits, give the same counts. This follows from #4237's
reduction to F_q: every pivot decision depends only on the residue mod q, and
the residue of the projector is the F₃ projector.

A hill-climbing search over charts found this header. The search is not part
of the claim; the verifier only replays the fixed chart.

## Two families covering every dimension

- **Family A.** The block chart diag(G6, I_{m−6}) with axes
  {0, 1, 2, 6, …, m−1} has projector diag(P6, I) of rank m − 3. For every
  6 ≤ m ≤ 64 the retained program makes s = 7 > 6 same-bank swaps.
- **Family B.** The block chart diag(G6, I + (1 − e₀)e₀ᵀ) with axes
  {0, 1, 2, 6} has projector diag(P6, 1·e₀ᵀ) of rank 4, where the second block
  is #4237's rank-one witness on m − 6 coordinates. For every 8 ≤ m ≤ 64 it
  makes s = 2(m − 4) + 1 same-bank swaps.

Each member pays exactly 3 children more than `8m² + 8m − 6 − 5r` at f = 2.
These are finite checks for each m ≤ 64, the full header range of the
retained program, over F₃. They are not a proof for other q.

## What remains true

- The proved ceiling s ≤ 2m − 1 − r from #4237 is not contradicted. Every
  example here satisfies it, and the verifier checks it.
- The head phase makes at most m − r same-bank swaps. By #4237's rank law
  only its m − r head-pivot steps can swap within the head bank. So any
  excess comes from the tail phase. In the m = 6 example the head phase
  makes 3 swaps and the tail phase 4, checked by the verifier.
- The header diag(1·e₀ᵀ on m − r + 1 coordinates, I_{r−1}) attains
  s = 2(m − r) at every rank for q ∈ {3, 5} and m ≤ 12, in the verifier's
  independent field elimination. So for those (q, m) the rank-r maximum is
  at least 2(m − r). This is a finite check, not a proof for every m.
- Complete censuses: for (q, m) = (3, 2), (3, 3), (3, 4), (3, 5) and (5, 3),
  every rank-r idempotent is enumerated as an (image, kernel) pair. The count
  matches q^{r(m−r)}[m choose r]_q, and the maximum s per rank is exactly
  2(m − r). The first two repeat censuses of #4237 with a separate
  enumeration. Since every F₃ header with m ≤ 5 obeys the bound, m = 6 is the
  smallest violating dimension over F₃.

## Evidence

`verify.py` checks the SHA256 pins in `SOURCES.json`, then imports the
unchanged retained program. It checks:

- the m = 6 counterexample for (q, w) ∈ {(3,1), (3,2), (3,3)} and
  f ∈ {1, 2, 3}, including the rank law, #4237's swap and child closed forms,
  the 2m − 1 − r ceiling and the excess over the conjectured formula;
- families A and B for every m in their ranges;
- a rank-one control: #4237's witness at m = 6 attains 2(m − r) and does not
  exceed it;
- an independent F_q elimination, cross-checked against the vendor path on
  the counterexample, for the diag(W, I) lower-bound family and the five
  censuses.

Reproduce from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/fallback-swap-rank-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/fallback-swap-rank-bound/verify.py --quick
```

Any CPython 3.12 works. The expected status is
`PASS_FALLBACK_SWAP_RANK_BOUND_REFUTED`. `--quick` skips only the (3, 5)
census, which takes about 100 seconds. The quick run takes about 7 seconds.

## Limitations

- The true rank-r maximum of s is open for 2 ≤ r ≤ m − 2. Every checked
  violation has excess exactly one; whether it can be larger is not decided.
- Families A and B are checked over F₃ only. Other odd q are not claimed.
- At m = 6 only one violating header is checked; the (3, 6) census, with
  about 6.7 × 10⁸ rank-3 idempotents, was not run.
- The package counts what `paid_children` charges. It does not execute the
  physical reversals, decide which headers reach the fallback, or audit
  BIT.md's recurrence or any other #4100 premise. The uniform maximum
  `8m² + 8m − 11` of #4237 is unaffected.
- Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. What is the exact rank-r maximum of s for 2 ≤ r ≤ m − 2? Start by bounding
   the tail-phase swaps in terms of the displaced head rows.
2. Can the excess s − 2(m − r) exceed one? Every header in this package,
   and every header from the uncommitted local search, has excess at most
   one.
3. Which header ranks reach the fallback in the auxiliary BIT recurrence?
   Until the exact maximum is known, a rank-dependent bill can use only the
   proved ceiling 2m − 1 − r.

## Credit

This package was produced by Nick Petalas. It answers the first open
question of #4237, whose rank law, closed forms, reduction to F_q and
rank-one witness it uses. The fallback program, descriptors and covariance
algebra are retained from source527, commdata2338, Ross Richardson
(PR2159/PR2188) and Jose Manuel's continuation. FALLBACK.md comes from
#4100. Apache-2.0.
