# Maximum-mass destination channels at n = 2^g - 1

Status: a written proof with exact finite corroboration (`verify.py`). It has not been
independently reviewed.

## Setting

Use PR2177's model ([PROOF.md](../leaf-destination-transport-bound/PROOF.md) section 1 and
[PROOF3.md](../leaf-destination-transport-bound/PROOF3.md) Part B). PR628's balanced
reserved-depth dirty word on n free noncommuting contractive factors splits a call of size m
into U (the floor half, size b) and V (the ceil half, size a). Sign + runs U, V, U', V'; sign -
runs V, U, V', U'. Inject separate unit errors at the destinations of distinct completed
leaves and read one register w at one later cut. A channel is the free-algebra entry carrying
one error to w, and its mass is its absolute coefficient sum. H = fl(n) = floor(log2 n).

Every channel has mass at most max(1, H) (PR2177 Theorem 1). PROOF3 Theorem M3 counts the
channels of mass H when n + 1 is **not** a power of two: at most 2F(floor(n/2)) at any cut and
register. For n = 2^g - 1 it records only a census value, 4g - 3 for g = 3..7. This note
proves that value as an upper bound for every g >= 3.

**Theorem.** Let n = 2^g - 1 with g >= 3, so H = g - 1. In either orientation, at any cut and
in any register, at most 4g - 3 channels have mass H. Consequently

  E_k(2^g - 1) <= k(g - 1) - max(0, k - (4g - 3))   for every k >= 1.

For g = 3..6 the count 4g - 3 is attained (finite check), so there E_k = k(g - 1) for
k <= 4g - 3.

Here a = 2^(g-1), b = 2^(g-1) - 1, fl(a) = H and fl(b) = H - 1. By PROOF3 Lemma F,
F(b) = 2(g - 1) - 1 = 2g - 3, so 2F(b) + 3 = 4g - 3.

## Cited premises

From PR2177 (Philippe Van Velzen), used unchanged:

- (T1) Theorem 1 and its section 3 case table, including Corollary I.
- (X) Lemma X: the exit column of a leaf of a size-k call has at most fl(k) + 1 nonzero
  entries, at most fl(k) on scratch. For a V-type phase, S_z = S_z(child); for a U-type phase,
  S_z = S(child).
- (F) PROOF3 Lemma F: a size-k call has F(k) leaves whose exit support has size fl(k) + 1.
- (M3-arg) The source-dirty part of the M3 proof: when the lowest common call K has a U-type
  injection phase alpha and a V-type cut phase beta, the channel mass is at most
  |exit(alpha)| <= fl(b) + 1. Mass fl(b) + 1 forces a full-exit leaf of alpha. The
  source-dirty pairs are (U,V)+, (U,V')+, (U',V')+ and (U,V')-.

## Lemma G (full scratch exits in a power-of-two call)

A call of size 2^h (h >= 1) has exactly two leaves whose exit column has h nonzero scratch
entries.

*Proof.* By (X), a leaf in a V-type phase has at most fl(2^(h-1)) = h - 1 scratch entries.
In a U-type phase S_z = S(child), so h entries means a full exit of the size-2^(h-1) child.
By (F) there are F(2^(h-1)) = 1 such leaves in each of the two U-type phases. ∎

## Lemma P2 (mass-h channels in a power-of-two call)

In a call C of size 2^h, h >= 2, a channel of mass h exists only at cuts in these top phases,
with at most this many at one cut and register: V of sign + (1), V' of sign + (2), V' of
sign - (1). At a cut after C's first phase is complete but before its second phase has a
completed leaf, there is none.

*Proof.* Both children have size 2^(h-1) and floor log h - 1, so a channel whose lowest common
call is a child has mass at most h - 1 by (T1). With lowest common call C, (T1) bounds
(U,U') by h - 1 and every V-start case by fl(2^(h-1)) = h - 1. Only the source-dirty pairs
remain. By (M3-arg) each needs a full-exit leaf of its U-type injection phase, and (F) gives
F(2^(h-1)) = 1 per phase. Count the U-type phases before each V-type cut phase in the pairs
listed above. A cut at the end of the first phase has its read phase complete, and every
completed-phase column has entries of mass at most 1 by PR2177 Lemma L1. ∎

## Proof of the theorem

Fix an orientation, a cut in top phase beta and a register w. Split the mass-H channels by
their injection phase alpha.

1. *alpha = beta (lowest common call is a child).* A U-type child has floor log H - 1, so it
   contributes nothing. A V-type child has size a = 2^(g-1) with g - 1 >= 2, and Lemma P2 gives
   at most 2 (sign +) or 1 (sign -). In the top call the phases V and V' have signs + and -.
2. *alpha U-type, beta V-type.* By (M3-arg), with fl(b) + 1 = H, each such channel comes from
   one of the F(b) full-exit leaves of alpha. There are 2F(b) when beta = V' (sign +), and
   F(b) when beta = V (sign +) or beta = V' (sign -).
3. *alpha U-type, beta U-type.* This is (U,U'), with mass at most max(1, fl(b)) = H - 1.
4. *alpha V-type, beta U-type.* By the (T1) row for (V,U'), (V,U), (V',U'), the mass is at most
   the number of nonzero scratch entries of exit(alpha), which is at most fl(a) = H. Mass H
   needs H = fl(a) entries. Lemma G allows two leaves per V-type phase. There is one earlier
   V-type phase for (+, U') and (-, U), and two for (-, U').
5. *alpha = V, beta = V'.* This occurs in both orientations, with C = V of sign + and its
   inverse C' = V' of sign -. Let C have N leaves, and let the cut follow j leaves of C'.
   Put t = N - j. Corollary I identifies each channel from leaf L_i of C. If i <= t, it is the
   channel of C from L_i to C's cut after t leaves. If i > t, it is the channel of C' from
   L_i^(-1) to the present cut, and the leaves L_i^(-1) with i > t are exactly the completed
   leaves of C'. The column identities hold entrywise, so they hold at the same register w.
   So the mass-H channels of cases 1 and 5 number A + 2c'. Here A counts mass-H channels of C at
   its cut t, and c' counts those of C' at its present cut.

   Apply Lemma P2 with h = g - 1. Since C' has sign -, c' <= 1. If c' = 1, the cut lies in C''s
   third phase after at least one of its leaves. That phase is the inverse of C's second phase,
   so j = |u| + |v| + r with 1 <= r <= |v|, where u and v are C's children. Then
   t = |u| + |v| - r. C's cut is at the end of its first phase or inside its second phase V of
   sign +, and Lemma P2 gives A <= 1. If c' = 0, then A <= 2. In either case A + 2c' <= 3.

Collect the cases by beta:

| orientation | beta | case 2 | cases 1 and 5 | case 4 | total |
|---|---|---|---|---|---|
| + | U | 0 | 0 | 0 | 0 |
| + | V | F(b) | 2 | 0 | 2g - 1 |
| + | U' | 0 | 0 | 2 | 2 |
| + | V' | 2F(b) | 3 | 0 | 4g - 3 |
| - | V | 0 | 2 | 0 | 2 |
| - | U | 0 | 0 | 2 | 2 |
| - | V' | F(b) | 3 | 0 | 2g |
| - | U' | 0 | 0 | 4 | 4 |

For g >= 3 the largest entry is 4g - 3. Every other channel has mass at most H - 1, so the k
largest channel masses sum to at most k H - max(0, k - (4g - 3)). ∎

Within case 5 and the (+, V') total, the bound of 3 is the new step. Bounding A and c' separately
by M3 for size a gives only 2 + 2 + 2 = 6, hence 4g.

## Finite corroboration

`verify.py` checks every cut, register and injection exactly in the free algebra:

- WORD: the generator equals PR2177's `check2.gen` leaf order for n = 1..64 and both signs.
- G: Lemma G for h = 1..5 in both signs.
- P2: Lemma P2 for h = 2..5, where each listed phase attains its bound.
- CLASS/MAIN: for g = 3..6 (n = 7, 15, 31, 63), every channel has mass at most g - 1. Each
  (orientation, beta) class respects the table, case 4 and cases 1+5 separately, and the
  maximum count is exactly 4g - 3 (9, 13, 17, 21).
- Controls: a bound of 4g - 4 is rejected for each g. The ceil-half split mutation violates
  the class or total bounds at all of n = 7, 15, 31.

These checks support the written proof. They do not replace it. Attainment of 4g - 3 for
g >= 7 is not proved here. PR2177's census reports it for g = 7.
