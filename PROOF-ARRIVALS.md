# Theorem (arrival pairs) and what it does and does not give — 2026-10-24

Scope: P112 complex local word, warp-free formal model (fields walk nested chains of subspaces of F2^9;
scalar contacts at a common current frame; centre transports of the eight selected reads S_k).
Inputs: pinned `research/coded-native-caller/NORMALIZERS.json` (M, labels q). Scripts in D:\Math\gn-theory.

## Setting and facts
F1 (locality). Without warps, a field standing at frame F holds local A_p-terms only for lines l_p ⊆ F: A_p only
stands at frames ⊇ l_p and every field's frames increase along its chain.
F2 (forced junk). The A-content of B_q is (centre part, in span{S_k} delivered by centre transports) + (local part).
B_q must end with e_q; on the 60 ports not orthogonal to q the local part vanishes (those lines never lie in a frame
⊆ P_q), so the centre part v satisfies v|N(q) = e_q|N(q); with the eight reads S_k this has the unique solution
v = row q of C = MMᵀ/4.  Hence the local part delivered to B_q is −J_q, whose support is exactly the 52 ports
orthogonal to q (all coefficients ±1/2).
F3. B_q walks 0 = H_0 < H_1 < ... < H_m = P_q.  Line p (p ⊥ q) can only be delivered locally at a hub H_i ∋ l_p.

## Theorem
Call an *arrival pair* any (p, H) such that local A_p-content is delivered into some B field at frame H.
Every warp-free word with the selected centre code has at least

        Σ_q f(q)  ≥  112 · 2689/78  ≈  3 861   distinct arrival pairs        (all 112 ports: see run logs),

whereas the 112 receivers need 5 824 (line, receiver) incidences.  Sharing frames between receivers therefore
saves at most 1 − 2689/(78·52) ≈ 33.7 % of arrival events.

Proof. Fix an arrival pair (p, H) used by receiver B_q.  Then H ⊆ P_q, i.e. q ∈ H^⊥, so the pair serves at most
n(H^⊥) receivers (n(Y) = #ports in Y).  Weighting each (p, q) incidence by 1/#receivers of its pair counts every
distinct pair exactly once, so #pairs ≥ Σ_q Σ_{p⊥q} 1/n(H(q,p)^⊥), with H(q,p) any hub of B_q's chain at which p
arrives.  Replacing H(q,p) by the smallest hub of the chain containing l_p only enlarges H^⊥, so the bound
still holds with that choice.  With Y_i = H_i^⊥ (a chain Y_m = <q> ⊂ ... ⊂ Y_1), p is charged 1/n(Y_i) for the
largest Y_i orthogonal to p; summing,  Σ_{p⊥q} = Σ_i (o_i − o_{i+1})/n_i  with o_i = #ports in Y_i^⊥.
f(q) is the minimum of this expression over all monotone sequences of achievable pairs (n(Y), o(Y)), Y ∋ q,
one per dimension (nestedness dropped — a relaxation, hence a valid lower bound).  All subspaces are enumerated:
Y of dimension 2–4 directly, dimension 5–8 through Z = Y^⊥ ⊆ P_q of dimension 4–1; no pair is pruned, so every
real chain is represented exactly.  Exact rational arithmetic.  ∎

## Calibration and what it means
- Greedy hub-sharing trees: ≈ 38.5 arrivals per line — close to the bound 34.5.
- **The selected word #4610 uses 9 824 arrival pairs (87.7 per line)** and reaches 8 324 (line, receiver)
  incidences, i.e. it delivers and cancels extra content.  So #4610 is far above this bound: arrivals are NOT the
  resource that makes #4610 expensive.  The theorem caps the benefit of frame sharing, but it does not turn into a
  Λ floor near the BIT gate.

## Directions tried to reach a Λ theorem
1. Arrival pairs (above): rigorous, but not binding for #4610.
2. Arrivals → Λ via provider levels: every arrival pair needs a holder of p standing at H; one holder level carries
   up to 36–64 lines, and a level costs ≥ 0.0104 → only Λ ≳ 0.6–1.
3. Per-q dedicated delivery at P_q (REPORT-LB, corrected): Λ ≥ 1.16 per call (earlier 2.3 was wrong: cheapest fields end on the hyperplane or cross it in one step).
4. LP relaxations of piece sharing: lose the exact-sum (assembly) constraint, which is where #4610's Λ sits.
5. Assembly lower bound (exact sums of pieces through nested chains) = a restricted linear-circuit lower bound
   problem; no method in hand.  This is the open "skeleton-free fragmentation floor" (format-limits-2, Q2).
