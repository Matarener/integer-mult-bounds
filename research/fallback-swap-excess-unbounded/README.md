# Fallback same-bank swaps add over direct sums, so the excess over 2(m − r) is unbounded

#4237 (`research/fallback-child-count`) proves that the retained BIT fallback
elimination makes exactly r opposite-bank swaps on a rank-r projector header,
and s ≤ 2m − 1 − r same-bank swaps; with f ≥ 2, `paid_children` then pays
`8m² + 2m − 6 + r + 3s` children. #4247 (`research/fallback-swap-rank-bound`)
refutes the conjecture s ≤ 2(m − r) with an m = 6, rank-3 header, but every
violation it found has excess e = s − 2(m − r) = 1. Its open question 2 asks
whether the excess can exceed one. This package answers yes, and shows the
excess grows linearly in m:

```text
direct-sum law (proof):   opposite, same-bank and tail-phase swap counts add over P1 ⊕ P2
new atom H8 (m = 8,  r = 4):   s = 10 = 2(m − r) + 2
new atom K13 (m = 13, r = 7):  s = 17 = 2(m − r) + 5
K13^{⊕k} ⊕ I:                  excess 5⌊m/13⌋ for every 13 ≤ m ≤ 64 (retained code)
m = 64, K13^{⊕4} ⊕ H8 ⊕ I4:    r = 36, s = 78, excess 22, 33160 children = conjecture + 66
```

Claim types, kept separate:

- **Scoped proof.** Direct-sum additivity of the three swap counts, for the
  first-unit elimination over F_q (below). It also holds for the retained
  program over Z/q^w through #4237's reduction to F_q, which this package
  cites and does not reprove.
- **Finite certificates.** The atoms G6 (#4247's header), H8 and K13 through
  the unchanged retained `prepare`/`paid_children` path over Z/3^w for w = 1,
  2, 3; the families for every m ≤ 64, the retained program's header range.
- **Search output, not a claim.** H8 and K13 were found by hill climbing over
  charts. The search is not part of the evidence and its failure to find
  denser atoms proves nothing.

No new κ, no audit of other #4100 premises, no supplier admission and no
change to the selected frontier.

## Setting

As in #4237 and #4247: the retained `vendor/fallback_program.py` and
`vendor/descriptor.py` from `research/selected-bit-recursive-closure`,
unchanged. A header is an invertible chart G over Z/q^w and an axis set of
size r; its projector is P = G[:, axes] G⁻¹[axes, :]. `prepare` eliminates the
residual R = `[[I−P, PJ], [JP, I−JPJ]]`, J the reversal, column by column with
the first-unit pivot rule and full row clearing. A swap at step k with pivot
row p is opposite-bank when k < m ≤ p, otherwise same-bank; it is in the tail
phase when k ≥ m. s counts same-bank swaps.

## Direct-sum law

Let P = P₁ ⊕ P₂ with blocks of size a and b, m = a + b. Split the 2m residual
positions into

```text
S₁ = {0, …, a−1} ∪ {m+b, …, 2m−1},     S₂ = {a, …, m−1} ∪ {m, …, m+b−1}.
```

Since J reverses the block order, R[i][j] = 0 when i and j lie in different
parts, and the submatrix of R on S_t, with positions relabelled in increasing
order, is exactly the residual R_t of P_t. For example, for i < a and m + j
with j < b, R[i][m+j] = P[i][m−1−j] = 0, while for i, j < b,
R[a+i][m+j] = P₂[i][b−1−j] = (P₂J)[i][j].

**Invariant.** Before every step, a row sitting at a position in S_t is
supported in the columns of S_t. It holds initially. At step k ∈ S_t the
pivot row has a nonzero entry in column k, so it sits in S_t, and the swap
exchanges two S_t positions. Clearing adds a multiple of the pivot row only to
rows with a nonzero entry in column k, which also sit in S_t. So the invariant
is kept, and steps at positions outside S_t never touch rows in S_t.

Restricted to S_t, the elimination is therefore the first-unit elimination of
R_t: the pivot is the least S_t position at or after k with a nonzero entry,
and the increasing relabelling keeps "least". The relabelling also keeps the
bank side: positions below m are the first a (or b) positions of the part,
which are R_t's head. So every swap keeps its orientation and phase, and

```text
opposite(P₁ ⊕ P₂) = opposite(P₁) + opposite(P₂)
s(P₁ ⊕ P₂)        = s(P₁) + s(P₂)
tail(P₁ ⊕ P₂)     = tail(P₁) + tail(P₂).
```

Since m and r also add, so does the excess e = s − 2(m − r). This holds for
blocks of any rank, including 0 and full; a rank-0 block makes no swaps and
lowers the excess by twice its size.

## Consequences

Atoms, each checked through the retained code: G6 (m = 6, r = 3, e = 1),
H8 (m = 8, r = 4, e = 2, with 4 head-phase and 6 tail-phase same-bank swaps),
K13 (m = 13, r = 7, e = 5), the identity block I₁ (e = 0) and #4237's rank-one
witness W_k (e = 0). The charts are in `verify.py`.

1. **The excess is unbounded.** K13^{⊕k} has m = 13k, r = 7k and e = 5k. In
   the field model this holds for every k by the direct-sum law. Through the
   retained code it is checked for every 13 ≤ m ≤ 64 with k = ⌊m/13⌋ and an
   identity remainder.
2. **Linear growth.** Let E(m) be the largest excess over F₃ headers with
   1 ≤ r ≤ m − 1. Direct sums make E superadditive, so E(m)/m converges to
   sup E(m)/m, and that limit is at least 5/13. The #4237 ceiling gives
   e ≤ r − 1, so the limit is below 1. Over F₃, E(m) = 0 for m ≤ 5 (#4247's
   censuses) and E(6) ≥ 1, E(8) ≥ 2, E(13) ≥ 5.
3. **Rank-r lower bounds.** For every m, k ≥ 1 and r with 4k < r ≤ m − 4k
   (or r = 4k = m/2), H8^{⊕k} ⊕ W ⊕ I has rank r and excess 2k. The verifier
   checks this grid in the field model for 8 ≤ m ≤ 32 and, through the
   retained code, the two edge families r = m − 4⌊m/8⌋ and r = 4⌊m/8⌋ + 1
   for every m ≤ 64.
4. **Children.** At f ≥ 2 a header pays `8m² + 8m − 6 − 5r + 3e` children.
   A rank-dependent bill therefore cannot stay within a constant of the
   refuted formula. At m = 64 the header K13^{⊕4} ⊕ H8 ⊕ I₄ pays 33160
   children, 66 above the formula at r = 36. #4237's uniform maximum
   `8m² + 8m − 11` = 33269 is not contradicted.

## Evidence

`verify.py` checks the SHA256 pins in `SOURCES.json`, imports the unchanged
retained program and checks:

- G6, H8 and K13 over (q, w) ∈ {(3,1), (3,2), (3,3)} and f ∈ {1, 2, 3}: the
  rank law, #4237's swap and child closed forms, the 2m − 1 − r ceiling, the
  stated excess, three children per unit of excess, and agreement with an
  independent F_q elimination;
- the direct-sum law exhaustively on every ordered pair of idempotents
  (every rank, including 0 and full) with block sizes in {1, 2, 3} over F₃
  (63504 pairs) and {1, 2} over F₅ (1156 pairs), and with one block of
  size 4 and the other of size 1 or 2 over F₃ (406144 pairs, full run only);
- controls: H8 ⊕ W₃ keeps excess 2, H8 ⊕ 0₂ keeps s = 10 and loses 4 of
  excess;
- families H8^{⊕k} ⊕ I and H8^{⊕k} ⊕ W for every m ≤ 64, K13^{⊕k} ⊕ I for
  every 13 ≤ m ≤ 64, and the m = 64 header above, through the retained code;
- the field-model rank grid for 8 ≤ m ≤ 32 (m ≤ 24 with `--quick`).

Reproduce from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/fallback-swap-excess-unbounded/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/fallback-swap-excess-unbounded/verify.py --quick
```

Any CPython 3.12 works. The expected status is
`PASS_FALLBACK_SWAP_EXCESS_UNBOUNDED`. The full run takes about 30 seconds
and the quick run about 6.

## Limitations

- The exact rank-r maximum of s and the limit of E(m)/m remain open. The
  atoms are search output; denser ones may exist.
- The direct-sum law is proved for the field model of the elimination. Its
  transfer to the retained Z/q^w program uses #4237's reduction to F_q; the
  families are checked through the retained code directly for m ≤ 64.
- Atoms and families are checked over F₃ only.
- The package counts what `paid_children` charges. It does not decide which
  headers reach the fallback or audit BIT.md's recurrence or any other #4100
  premise.
- Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. What is lim E(m)/m? It lies in [5/13, 1). A better atom raises the lower
   bound at once by the direct-sum law. First step: search indecomposable
   headers at m = 9…16, seeded from sums of the known atoms.
2. Is the ceiling s ≤ 2m − 1 − r attained, that is e = r − 1, for any r ≥ 2?
   K13 has e = 5 against a ceiling of 6.
3. Which headers reach the fallback in the auxiliary BIT recurrence? If they
   are confined to small rank or to special shapes, the rank-dependent bill
   may still be tight there.

## Credit

This package was produced by Nick Petalas. It answers open question 2 of
#4247 and uses #4237's rank law, closed forms, reduction to F_q and rank-one
witness, and #4247's m = 6 header G6. The fallback program, descriptors and
covariance algebra are retained from source527, commdata2338, Ross Richardson
(PR2159/PR2188) and Jose Manuel's continuation. FALLBACK.md comes from #4100.
Apache-2.0.
