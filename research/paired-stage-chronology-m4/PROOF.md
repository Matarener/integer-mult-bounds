# Exact paired-stage loss at m = 4 under the mixed chronology cut

## Model

This is the binary normalized paired-stage controller of
[PR #5631](https://github.com/CrocSwap/integer-mult-bounds/pull/5631)
(`research/paired-stage-chronology-cut`), which builds on PR #5617. Work
over F2. There are n main fields and L = n + 2 = 2m full calls, listed in
chronological order. Call i has a query

    R_i = u_i v_i,   v_i u_i = 0,   sum_i R_i = I_n,

and a rank-two idempotent P_i with P_i R_i = R_i P_i = R_i. The calls are
partitioned into m stages of two calls each. Stage c with calls i, j has
target derivative E_c = P_i + P_j. The targets must be idempotent and
diagonal in one common output basis, and every stage must satisfy the mixed
coefficient condition of PR #5631 Section 4:

    [P_i, S_i] + [P_j, S_j] = 0,   S_i = sum_(l > i) R_l.          (*)

Put r_c = rank E_c and D = 4m - sum_c r_c. PR #5631 proves D >= 2 for
m >= 4 from the rank and pairing cuts, and asks whether a family of bounded
loss can satisfy (*) at all sizes.

## Theorem (finite, m = 4)

At m = 4 (n = 6, L = 8), every query system, chronological order, stage
pairing and projector choice that satisfies the conditions above has
D >= 10. Equivalently sum_c r_c <= 6. The bound is attained.

Of the 35,008 query Gram systems, 23,564 admit no assignment at all. The
remaining 11,444 have minimum loss distributed as
`{10: 2400, 12: 4760, 14: 3084, 16: 1200}`. The previous lower bound at
m = 4 was D >= 2.

These are necessary conditions only. The theorem is a lower bound for any
complete word in this model. A system that passes is not a caller: the
other word coefficients, native realization and price are not checked.

## Reduction to a finite enumeration

**Lemma 1 (Gram normal form).** Put U = [u_0 ... u_(L-1)] and let V have
rows v_i. Then UV = I_n, and K = VU is an L x L idempotent of rank n with
zero diagonal. If two systems have the same K, they are conjugate by an
element of GL(n, F2). Proof: set G = U V'. Then G U' = U K = U and
V G = K V' = V', and G (U' V) = U K V = I. So u_i = G u'_i and
v'_i = v_i G, and R'_i = G^-1 R_i G. Conjugation preserves compatibility,
ranks, commutation, idempotence and (*). Conversely every such K arises:
take V a basis matrix of its column space and U the coordinates of its
columns.

I + K is a rank-two idempotent with all diagonal entries one. Every
rank-two idempotent factors as XY with X of size L x 2, Y of size 2 x L
and YX = I_2. Its diagonal is x_i . y_i. The verifier therefore enumerates
all sequences of pairs (x_i, y_i), x_i nonzero in F2^2 and x_i . y_i = 1,
with sum y_i x_i^T = I_2, and keeps the distinct K. There are 35,008 at
L = 8 and 976 at L = 6. Order is part of K, so every chronology is covered.

**Lemma 2 (projectors).** PR #5617 Section 2 shows that the compatible
rank-two idempotents for call i are exactly P = u_i b + a v_i with
v_i a = b u_i = 1 and b a = 0. The verifier enumerates all such (a, b). Each P arises from exactly two
parameter pairs, (a, b) and (a + u_i, b + v_i), so candidates are deduplicated.

**Lemma 3 (reversal).** Since sum R = I and [P_i, R_i] = 0,
[P_i, sum_(l < i) R_l] = [P_i, sum_(l > i) R_l]. Hence reversing the call
order and transposing every matrix maps a valid assignment to a valid one
with the same ranks. In Gram terms this is K -> J K^T J, with J the
reversal. The census computes one representative per orbit and weights
it by orbit size. The m = 3 weighted census reproduces an unreduced run.

**Stage algebra.** In characteristic two, (P_i + P_j)^2 = P_i + P_j exactly
when P_i and P_j commute. A family of commuting idempotents is diagonal in a
common basis, and the converse is immediate. For each call pair the
verifier groups projectors by the value of [P_i, S_i], so (*) becomes
equality of keys. It keeps all commuting pairs, records each distinct E and
its rank, then takes the maximum of sum r_c over all 105 pairings and all
pairwise commuting choices of E, by exhaustive branch and bound. The bound
4 per remaining stage is exact because r_c <= 4.

## Controls

- m = 3: the same code finds D = 0 on 146 Gram systems, so the program is
  not vacuous. PR #5631 reports a genuine six-query word that passes.
- An optimal m = 4 word is rebuilt and passed to PR #5631's own
  `chronology.mixed` routine, unchanged. It reports no defect. Exchanging
  the first two calls makes it report a defect.
- Reversing the call order of the witness keeps every mixed coefficient,
  as Lemma 3 predicts.

A separate implementation using NumPy and no orbit reduction reproduced the
m = 4 histogram over all 35,008 systems. That run is local evidence and is
not registered.

## What this does and does not settle

The data show (*) is strong at m = 4: the best target mass is 6 of 16.
This does not prove that D grows with m. The m = 5 census is larger
(n = 8 gives 2^13 projectors per call) and was not run. No asymptotic
lemma is proved. The theorem does not cover thin calls, idle maps, coupled
ports, characteristic other than two or other word coefficients. It changes
no price exclusion: PR #5631 already rejects m <= 47 with D >= 2.
