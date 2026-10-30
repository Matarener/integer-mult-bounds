# Audit of PR6122's four-query capacity, and the exact capacity for every call count

Josie Elliston, prepared with Claude Code (Opus 5.5). Apache-2.0.

**Independent audit plus scoped extension; no new κ.** This audits
[PR6122](https://github.com/CrocSwap/integer-mult-bounds/pull/6122) (Nick Petalas,
head `e4fb5699c1c390ada0e6ac738d48548c462448b1`, package
`research/four-block-query-capacity/`) and answers its Open next question 2.
It uses the same model as PR6122. K has characteristic two, Q is a central
involution, the free maps are constant matrices in GL_n(K), and each paid call
is I + Q N with N² = 0 and rank N ≤ r. There is no workspace, and the target is
Q I_n.

## Findings

1. **The theorem holds.** I re-derived every step of PR6122's PROOF.md: the
   ε = Q + 1 normalization to Σ R_i = I_n, the trace parity, the Gram
   factorization UV = I_n, the complement C = AB with BA = I_c, the block
   idempotents E_i with Σ E_i = I_c, and the rank count c ≤ Σ (c − r_i). I found
   no gap. The construction attains the bound.

2. **PR6122's finite check never reaches the new step.** Its exhaustive control
   covers n ≤ 4. Every case it decides there is already settled by trace parity
   (n = 3) or by the elementary bound n ≤ 3r (n = 4, r = 1). The first case
   where the new bound 3n ≤ 2S is needed is n = 6, r = 2 (6 ≤ 3r, but
   6 > 2⌊4r/3⌋ = 4). The Gram fixtures run only on feasible constructions. So
   the headline exclusion "four rank-two queries cannot twist six" had no finite
   evidence. It has some now: `verify.py` decides it by exhaustion over F2.

3. **Exhaustion over F2, n = 2..6, every cap profile.** Here (c1, c2, c3, c4)
   are per-call rank caps, 0 ≤ c_j ≤ n/2, giving 75 sorted profiles. The search
   finds a witness exactly when

       n is even and Σ_j min(c_j, n/2) ≥ 3n/2.

   This covers n = 6 at uniform caps 2 (infeasible) and 3 (feasible). It also
   covers n = 5, where both rank bounds allow uniform cap 2 and only parity
   excludes it. The method does not use the Gram argument. R1 is put in
   normal form, which conjugation invariance allows, and every square-zero R2
   is enumerated. Y = I + R1 + R2 must have rank ≤ c3 + c4. Membership of Y in
   {R3 + R4} is a class function, so it is decided once per similarity class.
   The complete invariant is rank p(Y)^k for each irreducible p over F2.
   Membership is decided by enumerating every R3 and testing Y + R3.

4. **Corollary: heterogeneous caps (proved, all fields).** With per-call caps
   c_j, four calls reach Q I_n iff n is even and Σ min(c_j, n/2) ≥ 3n/2.
   Necessity: PR6122 gives S ≥ 3n/2, and a square-zero R_j has rank at most
   n/2. Sufficiency: put o_j = n/2 − min(c_j, n/2). These are nonnegative and
   sum to at most n/2, so they can be topped up to omission counts summing to
   exactly n/2. Running PR6122's omission schedule with those counts gives
   rank n/2 − o_j ≤ c_j at call j. `verify.py` builds and replays 16,559 such
   words (every even n ≤ 24 and every ordered cap profile with c_j ≤ n/2 + 1)
   in F2[Q]/(Q²−1).

5. **Extension: exact capacity for every call count k ≥ 3 (proved, all
   fields).** Let m_k = 2⌊(k−1)/2⌋, so m_k = k−1 for odd k and k−2 for even k.
   Then k paid calls of rank ≤ r reach Q I_n iff

       n is even and n + ⌈n/m_k⌉ ≤ k r.

   The least total paid rank is n + ⌈n/m_k⌉. For k = 4 this is PR6122's
   n ≤ 2⌊4r/3⌋; the verifier checks that for r < 200. Five calls reach
   n = 4r: five rank-two calls twist eight coordinates, while four can twist
   only four. Six calls reach 4, 8, 14, 18, 24, 28 for r = 1..6. With
   rank-one calls, the minimum number of calls for n coordinates is n + 1. That
   is Cinna Davis's minimum-query simplex bound, which this reproduces as a
   consistency check.

   The extreme odd case is already known. When k is odd and n = (k−1) r, this
   is Ali Romman's block simplex at the shortest count (#5617 PROOF.md §9:
   L = n+1 calls of rank q on N = nq). That section leaves N ≠ q(L−1) and
   other call counts open. Finding 5 covers every n and k for uniform caps.
   Mixed caps are covered only for k = 4 (finding 4).

   *Lower bound.* Normalize as in PR6122 §1, so Σ_{i≤k} R_i = I_n. For odd k,
   append R_{k+1} = 0. The number K of summands is then even. PR6122 §2 never
   uses K = 4 until its last line. It gives idempotents E_i of rank r_i on K^c,
   with c = S − n and Σ E_i = I_c. So Σ (I_c − E_i) = (K−1) I_c = I_c, because
   K − 1 is odd. Rank subadditivity gives c ≤ Kc − S, so (K−1) n ≤ (K−2) S.
   Since K − 2 = m_k, this says S ≥ n + n/m_k. S is an integer, so
   S ≥ n + ⌈n/m_k⌉, and S ≤ k r.

   For odd k the Gram step is not needed. The elementary bound gives the same
   inequality. Σ_{j≠i} R_j = I + R_i is invertible, so n ≤ S − r_i. Summing
   over i gives (k−1) S ≥ k n, which is S ≥ n + n/(k−1). PR6122's new step
   matters exactly for even k, where it improves k n/(k−1) to
   (k−1) n/(k−2).

   *Construction.* For even d, I_d is the sum of d + 1 rank-one square-zero
   matrices over F2:
   R_i = e_i (1 − e_i)^T for i < d, and R_d = J, the all-ones matrix. The rows
   of the first d sum to J − I, and J² = dJ = 0. This is the n + 1 simplex of
   Cinna Davis's GLOBAL-PROOF.md, written explicitly. Split n into ⌈n/m_k⌉
   even blocks of dimension ≤ m_k. A block of dimension d contributes d + 1
   rank-one terms, at most k of them. Lay all the terms on call positions
   1..k in cyclic order, wrapping around (McNaughton's rule). Each block then
   uses distinct positions, and each position receives at most
   ⌈(n + ⌈n/m_k⌉)/k⌉ ≤ r terms. Call j pays I + Q N_j, where N_j is the
   direct sum of its terms, and is preceded by the free constant I + N_j. Then
   (I + N)(I + Q N) = I + εN, and Π_j (I + εN_j) = I + ε I_n = Q I_n in any
   order. `verify.py` replays 353 such words, for k = 3..9 and r = 1..6, with
   literal F2[Q]/(Q²−1) arithmetic. Controls show that the constants are
   required and that reversing the call order still works.

## Evidence

```sh
python3.12 -B research/four-block-query-capacity-audit/verify.py
python3.12 -B scripts/research_package.py --package research/four-block-query-capacity-audit
```

The verifier uses only the standard library. It imports nothing from PR6122 or
the repository, takes about 30 s and prints `PASS_FOUR_BLOCK_QUERY_CAPACITY_AUDIT`.
It compares its output with `RESULT.json` in full. Thirteen positive and
negative controls must all hold. They cover planted false witnesses, an
odd-trace target, a dropped layer, swapped layers, a rank-cap violation and
missing constants. The constructor must refuse (n, r) = (6, 2) and (10, 3)
at four calls, and n = 10 at five calls of rank 2. The verifier passes with
Python 3.10, 3.12 and 3.14, in both normal and `-O` modes.

*Local search evidence only (shared venv, python-sat, not submitted).* A
separate SAT encoding uses R_j = U_j V_j with V_j U_j = 0. It agrees on the
positive cases n = 4, 6, 8 at four calls, on GF(4) with n = 6 and caps
(3, 2, 2, 2), and on k = 5, 6 witnesses at n = 4, 6, 8. Without symmetry
breaking, the n = 6, r = 2 UNSAT case did not finish within 300 s. That is why
the exclusion evidence here is the stdlib exhaustion.

PR6122's own `verify.py` was read and run (Python 3.12): it passes, with 392
construction fixtures and 170 Gram fixtures.

An independent read-only OpenAI Codex review found no error in either
capacity proof or in the identity-target exhaustion. It found one verifier
defect. The decider also accepted a non-identity target but still fixed R1
in normal form, which is valid only for a conjugation-invariant target. That
path now enumerates every R1, and its controls were moved to n = 2 and n = 3.

## Limits

The exhaustion is over F2 and n ≤ 6 only. For other fields and larger n, the
written proofs are the evidence. The model is PR6122's abstract interface: free
constant bases, square-zero constant paid matrices, no workspace, and the target
Q I_n. Nothing here supplies a native realization of a rank-r query, a physical
multi-bank primitive, a signed invoice, a supplier, or a κ change. No
literature search was made for the rank-capped "sum of square-zero matrices
equals I" statement, which is a rank-constrained case of the classical
sums-of-square-zero-matrices question. Priority for findings 4 and 5 is not
claimed beyond this repository. The merged package
`research/square-zero-idempotent-compiler/` is related but different: its
paid alphabet is rank-one idempotent couplings, and its target is I + (1+g)N.

## Open next questions

- **Do more calls actually pay?** Five calls twist 4r coordinates at rank r,
  where four calls twist about 8r/3. The paid rank per twisted coordinate falls
  from 3/2 to 5/4 and tends to 1 as k grows. Whether the extra calls cost less
  than they save depends on the per-call charge in a real invoice. A first step
  is to price the k = 5, n = 8, r = 2 word under the cost rule used by #6114 or
  #5617. This needs a per-call price for a rank-2 query.
- **Can workspace or a non-square-zero paid matrix beat n + ⌈n/m_k⌉?** Both
  are outside this model. The Gram step uses Σ R_i = I_n exactly, so dirty
  workspace changes the equation that the argument starts from.

## Credit

The four-call theorem, its proof and the omission schedule are by Nick Petalas
(PR6122). The n + 1 rank-one simplex is from Cinna Davis / 1337isnot1337,
`research/productive-controller-basis-search/GLOBAL-PROOF.md`. The
coupled-port Gram framework and the block simplex at the shortest count are
by Ali Romman (#5617, PROOF.md §9). The source question is
Matarener's #6114. Session claim and handoff:
[discussion 1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166).
