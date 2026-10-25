# Proofs and certificates

Tags: **PROVED** (hand proof, every step stated), **EXACT** (exhaustive finite computation in exact arithmetic, recomputed by
`verify.py`), **CHECKED** (kissat UNSAT plus a drat-trim VERIFIED proof, recomputed by `verify.py`), **CONDITIONAL** (depends on
something listed explicitly, or on a computation whose certificate is not shipped).

## 0. Model and notation

`L` is the set of 112 lines of P112 (the 120 root lines of E8 minus the eight lines of one orthogonal frame, coordinates `C` doubled
to be integral). `Bd[t,s] = 1` iff `t = s` or `t ⟂ s` ("masked pair"). A **decoder** with `m` terms is a pair of matrices
`P, Q ∈ K^{112×m}` over a field `K` of characteristic 0 with `(P Qᵀ)[t,s] = δ_ts` on every masked pair. Term `k` has supports
`R_k = supp P[:,k]`, `A_k = supp Q[:,k]` (any subsets) and cost `rank_F2 Bd[R_k, A_k]`. The cost of a decoder is the sum over
terms. The coordinate decoder (8 terms `Off_i`, price 8 each) has cost 64. A **frame** is an orthogonal 8-clique of `L`; there are
1,260. Put `M = P Qᵀ` (rank at most `m`).

*F2 structure (PROVED + EXACT).* `Bd = labᵀ Φ lab` over F2 with labels `lab(t) ∈ F2^9` (bit 0 = 1) and `Φ` a nondegenerate
form, rank 9. So `cost(R,A) = rank Φ|_{span lab(R) × span lab(A)}`. Every maximal rectangle of cost `c` is
`(L(X), {a : img_X(a) ∈ Z})` with `X` a label-closed subspace and `Z` a `c`-dimensional subspace of `X*`.

## 1. (a) FULLWALL: `m ≤ 8` ⇒ cost ≥ 64 (PROVED + EXACT)

**Algebra (any field of characteristic 0, any supports).**
(0) `m ≤ 7` is impossible: on a frame `F`, `P_F Q_Fᵀ = I_8` needs rank 8.
(1) `m = 8`: `P_F`, `Q_F` are invertible 8×8 and `Q_Fᵀ P_F = I`.
**R1 (frame expansion).** For `t ∉ F`, `P_t = Σ_{g∈F} ⟨P_t, Q_g⟩ P_g`, and `⟨P_t,Q_g⟩ = 0` for `g ⟂ t`, so
`P_t ∈ span{P_g : g ∈ w_F(t)}` with `w_F(t)` the four lines of `F` not orthogonal to `t` (E8 Parseval: always four). The same
holds for `Q`. Hence every zero set `Z_k = L∖R_k` and `Z'_k = L∖A_k` is closed under the rule "`w_F(t) ⊆ Z ⇒ t ∈ Z`"
(477 distinct 4-sets per line over all frames).
**R2.** The diagonal of `Q_Fᵀ P_F = I` gives `Σ_{f∈F} P_f[k] Q_f[k] = 1`, so `R_k ∩ A_k` meets every frame.

**Finite step (EXACT).** Let `cl` be the R1-closure. If a term has supports inside a rectangle `(R,A)` then `Z_k ⊇ cl(L∖R)` and
`Z'_k ⊇ cl(L∖A)`, so `R_k∩A_k ⊆ L ∖ (cl(L∖R) ∪ cl(L∖A))`. For each of the 46,807 maximal rectangles of cost ≤ 7 (up to
`Aut × transpose`; census in `verify.py` output) this set misses some frame, contradicting R2. So every term of an 8-term decoder
costs ≥ 8 and the total is ≥ 64. Tight: the coordinate decoder.
*Completeness of the census.* label-closed subspace orbit representatives come from pynauty certificates (`xorb.py`:
1/5/24/98/193/141/50/10/1 orbits by dimension, orbit-size sums 112, 6216, 155092, 1557690, 2783900, 763987, 43173, 510, 1); an
**independent C program** (`cntsub.c`, no orbit machinery) counts all 8.3 million label-spanned subspaces and must reproduce each sum.
Maximal-rectangle enumeration is `rect2.py`. **Independent cross-check** `xcheck_m8.py` (separate numpy code, own frame
enumeration and closure) tests every raw `(X, Z)` pair of cost ≤ 7 with no canonicalisation and no maximality filter
(510,583 rectangles) and finds 0 survivors.

*Why testing maximal rectangles is enough.* R1/R2 are monotone under support growth in the right direction (sec. 0 of the notes: a
term inside `(R,A)` has `Z_k ⊇ L∖R`, a closed set contains the closure). The weaker row "every masked off-diagonal cell is covered
0 or ≥ 2 times" is **not** monotone and is not used at this step.

**Scope.** Single-wire rank-1 terms, any supports. Not interleaved atoms (R1 needs rank-1 terms), not multi-wire terms.
**Audit.** An independent read-only reviewer re-derived R1/R2, the census completeness (`x + y ≤ 9 + c` gives the transpose WLOG; Φ is
unique because label outer products have F2 rank 81) and re-ran `m8.py`: sound. Control: `P = C, Q = C/8` (plain E8 coordinates,
`|R| = 76`, cost 9 each) passes R1/R2.

**Why the cheaper arguments fail (EXACT, context only).** With *all* supports the monotone LP (frames + lines + global
`rank_Q`) is only 18.886, and the exact-support cover relaxation (every masked cell covered 0 or ≥ 2 times, every frame hit
≥ 8 times, every line covered, `Σ rank_Q ≥ 112`) is satisfiable at cost 42. Only coefficient algebra (R1) reaches 64.

## 2. (b) INT-M8 / MIX-8: pieces, not terms (PROVED + CHECKED)

A term may be an interleaved (Ferrers) atom `D(x) S D(y)`, `S(t,s) = [λ(s) ≤ μ(t)]`, priced at the Theorem-A floor
`rank_F2 (Bd∘S)[R,A]` (a lower bound for the true wire loss, so every bound below also holds at the true loss).

**Level split (PROVED, numeric spot-check in `lsplit.py`).** `D(x) S D(y) = Σ_j (x ∘ 1[μ ≥ j]) (y ∘ 1[λ = j])ᵀ`: `L` rank-1
rectangle pieces with nested row supports, the same coefficients, disjoint column blocks. A decoder with `m` terms is a rectangle
decoder with `M = Σ L_k` pieces, and the algebra of sec. 1 holds verbatim for pieces.

**Theorem MIX-8.** If `M ≤ 8` then every atom is a rectangle (so `m = M = 8` and sec. 1 gives ≥ 64).
(a) `M ≤ 7` is impossible (frame argument). (b) `M = 8`; put `M := P Qᵀ` for the piece matrices.
*Step A (no extra zero, CHECKED).* `M_ts ≠ 0` for every non-orthogonal pair. For each frame `F`, `M[F,F] = I` and rank 8 give
`M_us = Σ_{g∈w_F(u)∩w_F(s)} M_ug M_gs`. The zero-pattern CNF (`rigz.py`, 50 frames, seed 1: 303,264 variables, 2,207,921 clauses,
goal "some `M_ts = 0`") is UNSAT; the shipped proof is checked by drat-trim (VERIFIED); the CNF is regenerated and pinned by
SHA-256. Using only 50 of the 1,260 frames is sound (every clause is a necessary condition).
*Step B (frame expansion with full support).* For `t ∉ F`, `P_t = Σ_{g∈w_F(t)} M_tg P_g` with all four coefficients nonzero. So for
any functional `φ` the support `X = {t : ⟨P_t,φ⟩ ≠ 0}` meets every frame, `t ∈ X ⇒ X ∩ w_F(t) ≠ ∅`, and
`t ∉ X ⇒ |X ∩ w_F(t)| ≠ 1` (near-miss rule).
*Step C (the tie).* A genuine atom has piece columns `x` and `x∘1[R²]`; `φ₁ = e₁ − e₂`, `φ₂ = e₂` give supports `X₁ = R¹∖R²`
and `X₂ = R²`: **disjoint and both nonempty**. Two disjoint nonempty sets each obeying Step B are impossible: CNF (224
variables, 536,873 clauses) kissat UNSAT, drat-trim VERIFIED (`tie8.py`, line 0 ∉ X₂ by a sound symmetry), and an
**independent generator** (`xtie8.py`, own E8, own frames, no symmetry breaking) UNSAT, VERIFIED. Control: dropping the
disjointness clauses is SAT, and dropping the near-miss rule is SAT (|X₁| = |X₂| = 44), so Step A is essential.

**Corollary (PROVED).** Any decoder containing a genuine interleaved atom has `M ≥ 9` pieces, whatever its term count; an
8-term decoder with an atom lies in the open `M ≥ 9` class. Rectangle results (sec. 1, 3, 4) bound piece sums, **not atom floors**,
and are not claimed for the mixed case.
Side result (EXACT, one family): on the coordinate decoder, a Ferrers hole whose masked cells are diagonal only raises the floor
(rank 8 → 8 + |D| for a clique hole of size `|D| ≤ 6`); this is not part of the replay.

## 3. (c) Nine terms, rank M = 8 (PROVED mod the inputs in sec. 3.1; finite facts EXACT)

Setting. `rank M = 8` iff `rank P = 8` or `rank Q = 8` (the other orientation is the transpose, and cost is transpose-invariant).

### 3.1 Inherited inputs (not re-proved here)

1. **FULLWALL (sec. 1)**: any 8-term decoder on a sub-pattern costs ≥ 8 per term (the "merged term" argument).
2. **FULLWALL-9 sec. 3 (hand proof, audited sound)**: if `rank Q = 8` with kernel vector `v`, then every term outside `S = supp v`
   costs ≥ 8; for `|S| ≤ 2` the total is ≥ 64.
3. **Rank-8 core form** (S9 sec. 4, a hand derivation): `P = C A`, `Q = C A'/8 + b βᵀ`, `A A'ᵀ = I`, `A β = 0`; for `k ∈ S = supp β`:
   `R_k = Hᶜ(a_k)`, `Q_k = β_k(b − C p_k)`, the `p_k` are affinely independent (a simplex) and `a_k` is orthogonal to the
   directions of the opposite facet. The fiber rule `A_j ⊇ T_jk ∖ A_k`, `T_jk = Hᶜ(p_j − p_k)`, follows.
4. **R8: every rank-8 completion of the P112 mask is `D G8 D⁻¹`** (sec. 3.2), which removes the hypothesis "R8" from the hand
   derivation of item 3 (CORE-RES NOTES sec. 1: rank M = 8 iff rank-8 core form, S9 sec. 4 + R8). The core form itself is still the hand
   derivation of item 3 (audited as an input, not recomputed here); after R8 the only extra input beyond it is Step A of sec. 2.
5. **Step A** (sec. 2, CHECKED).

### 3.2 R8 (PROVED mod Step A; EXACT lattice computation, two codes)

Fix a frame `F`. `M_FF = I` and rank 8 give `M = M[:,F] M[F,:]`. Unknowns `u_t(g) = M_tg`, `v_t(g) = M_gt` (`g ∈ w(t)`), nonzero by
Step A. For `t ⟂ t'` outside `F`, `|w(t)∩w(t')| ∈ {0,2,4}`; when it is 2 the equation `M_tt' = 0` is the **binomial**
`u_t(g₁) v_t'(g₁) = −u_t(g₂) v_t'(g₂)`. With `N = 832` unknowns and 4,608 binomials, the exponent lattice `Λ ⊆ Z^832` has rank
617 and `Z^832/Λ` is torsion-free (unit-pivot Gauss–Jordan over Z, no leftover rows). The independent scalings
(`u_t → α_t u_t`, `v_t → β_t v_t`, frame torus `τ_g`) give 216 exponent vectors with one relation, rank 215 = 832 − 617, all
orthogonal to `Λ`. Both lattices are saturated of equal rank, so over any characteristic-0 field the solution set is exactly the
G8 point times this torus: `M = D G8 D⁻¹`. The 312 same-tetrad four-term equations are never used. Checked by `r8bin.py`
and by `xr8.py` (own geometry, a different frame, 4,656 binomials, an explicit 617×617 minor with determinant 1 against the
Hadamard bound 2^473).

### 3.3 The case analysis on `s = |supp β|`

Notation: `y_k = dim span lab(A_k)`, `eps_k = 9 − dim span lab(R_k)` (`eps_k = 1` iff `a_k` is a frame root, else 0), `loss(T,Y)` =
drop of `dim span lab(T∖L(Y))`. Every term outside `S` is pure (cost ≥ 8, input 2). Goal: `Σ_{k∈S} cost_k ≥ 8(s−1)`.

* **s ≤ 2**: input 2.
* **s = 3** (audited by hand): `Σ cost ≥ 16`. Finite facts V1–V3 (EXACT, two codes): (V2) `dim span lab(Hᶜ(q)) = 9` except on the
  56-line flat of a frame root, where it is 8; (V1) `Hᶜ(q)` has at most one coloop in its label matroid, only on the 59-line
  flat of a P112 root, and after deleting it every cocircuit spans ≥ 7 label dimensions; (V3) in the two-loss configuration
  `rank_F2 Bd[Hᶜ(a), {r_j, r_l}] = 2` for all 172,032 configurations and all ratios (re-proved in the stronger form G2 over
  all 3,304 orthogonal root-line pairs). Then (a) `y_k ≥ 7` gives each cost ≥ 6; (b) `y_k ≤ 6` gives, by the fiber rule and V1, either
  no loss (sum ≥ 16) or a loss of 1 only when `a_i` is a frame root and `line(r_i) ∈ A_k` (then `cost_k ≥ 1` or `≥ 2` by V3).
* **4 ≤ s ≤ 7**: cases (i) some `y_k ≤ 6`; (ii) all `y ≥ 8` (`Σ ≥ 8s − 8`); (iii) min `y = 7` (`Σ ≥ 6 + 7(s−1) ≥ 8(s−1)` iff `s ≤ 7`).
  Case (i) needs **Part A** (EXACT): for all 28,672 / 229,376 / 229,376 hurt configurations with `h = 2/3/4` (none for `h = 5`)
  and every `a` with `a·r_i ≠ 0`, `rank_F2 Bd[Hᶜ(a) ∪ D, D] = h` (0 failures; `s4.py` and the independent stdlib `xpartA.py`).
  Case (iii) needs **Part B** (EXACT): over every flat and every 7-dimensional `Y` the loss is ≤ 1 (`s4.py`; `lossy.py` re-verifies on the
  special flats).
* **s = 8, 9** (residual cases, audited): Lemma 1 (`|K7| ≥ 2 ⇒ d_i ≤ 1` for all `i`; `K7 = {k} ⇒ …`) with `d_k = 8 − cost_k`.
  `s = 8`: closed by a short argument (eight frame roots are orthogonal, `Σ β_i a_i = 0` forces each used line twice, span ≤ 4, `rank A ≤ 5`).
  `s = 9`, `K7 = {k}`: the eight frame terms are the frame roots once each, so `p_i = p_j + λ_i f_i`; a 7-dimensional `Y` has at most two
  lossy frame-root flats; sum of `d` ≤ 3. `s = 9`, `|K7| = m ≥ 2`: `K7` is an `A_{m−1}` root simplex (flats with ≥ 40 lines are only the 42-, 56-,
  59-line flats); `star.py` and the independent `xa2.py` leave only `h ∈ {0,1}`; for those, an arc-consistency CSP
  (`kcsp.py`, `a8star.py`, `xa2.py`: three codes, 960 `A8` simplices and 8×36 `A7` simplices) is empty.
  Conclusion: `Σ_{k∈S} cost_k ≥ 8(s−1)` for every `s`, hence **a decoder with 9 terms and `rank M = 8` costs ≥ 64**.

Audits: the `s = 3` argument, the `s = 4..7` case logic (`Part A` recomputed independently over `h = 1..6`, `Part B` partly sampled),
the R8 lattice argument and the `s = 8,9` residuals were each re-derived by an independent read-only reviewer (sound; caveats below).

## 4. (d) COVERSAT: `C(T) = 8` on the interleaved (Ferrers) menu (CHECKED-EXACT with certificates; exact cost, not border cost)

`T` is one of the five orbits (0–4) of cancelled 8-line sets of the KFAM (4,4) family; `B = Bd[T,T]`. A decoder uses terms
`D(q_k) S_k D(p_k)`, `S_k` a Ferrers 0/1 pattern, coefficients over a field of characteristic 0, priced at `Σ rank_F2(B∘S_k)`.
**Soundness of the cover model (PROVED, audited).** Pass to exact supports `S'_k = S_k ∘ [q_k≠0][p_k≠0]`: still Ferrers, F2 rank not larger.
Drop terms with `B∘S'_k = 0`; a cost ≤ 7 decoder then has at most 7 terms with ranks `r_k` summing to ≤ 7, and a partition `λ` of 7
with `r_k ≤ λ_k`. A diagonal masked cell with sum 1 is covered ≥ 1 time; an off-diagonal masked cell with sum 0 is covered 0 or ≥ 2
times. These, with Ferrers and `rank_F2(B∘S_k) ≤ λ_k`, define 15 shards per orbit; the singular-sum row and the symmetry
breaking (`Aut(B) × transpose`, lex-min, equal-size terms sorted) are sound (checked by the reviewer, and by `check.py`
self-tests). UNSAT of all 15 shards of an orbit proves `C(T) = 8` for that orbit; the construction with cost 8 exists.

* **Stage 1 (pure cover model), CHECKED.** 15/15 shards UNSAT with drat-trim VERIFIED for orbit 0; for orbits 1, 3, 4 stage 1 closes 5, 3
  and 8 shards (orbit 2: 3, not claimed). `verify.py` regenerates every CNF and checks kissat UNSAT plus drat-trim VERIFIED.
* **Stage 2 (orbits 1, 3, 4, remaining shards).** The pure cover model is satisfiable on the other shards, but those models fail exact
  Lemma-B rank cuts over Q. The cut model adds (i) the cuts `Σ_k rank_Q A_k[X,Y] ≥ |X∩Y|` (valid because `Σ_k D(q_k)(B∘S_k)D(p_k) = I`
  on exact supports; encoded with finite-field rank witnesses over F2, F3, F5, F7 and a counter) and (ii) the **ratio lemma** (a
  consistency condition on ratios of coefficients across two lines). When the cut model is still satisfiable, a candidate pattern can be
  killed by a **no-good**:
  *No-good lemma (PROVED).* Fix patterns `S_0..S_{m-1}` and a set `C` of masked cells. A decoder with exact supports whose pattern agrees
  with the candidate on `C` satisfies `Σ_{k : S_k(t,s)=1} q_k(t) p_k(s) = δ_ts` for `(t,s) ∈ C`, with every unknown nonzero; rescaling term `k`
  fixes `p_k = 1` at its first column met in `C`. If `1` lies in the ideal of this system together with `v·w − 1` for each unknown `v`,
  no such decoder exists, so the clause "the pattern differs from the candidate on `C`" (and its images under `Aut(B) × transpose ×
  reorderings of equal-size terms`) may be added. A **certificate** is a list of cofactors with `Σ_i cof_i eq_i = 1`.
  `src/coversat/nogoods.py` rebuilds the system from `(orbit, patterns, C)`, checks it equals the certificate's, and checks the identity in exact
  `Fraction` polynomial arithmetic; `shard.py --certs` then adds the clauses, solves, and checks the DRAT proof.
  `data/coversat_snapshot.json` has the shard-by-shard status and `data/coversat_cut_shards.json` what `verify.py` re-solves. A shard is one of:
  **stage1-DRAT** (pure model), **cut-DRAT** (cut model, no no-goods; CNF pinned by SHA-256), **cut+certified-nogood** (cut model plus
  checked certificates; proof too large to ship, CNF regenerated), **CONDITIONAL-v1** (closed in the first run with sympy Groebner no-goods whose
  certificates were not kept), or **OPEN**. Shipped proofs are never trusted: every UNSAT is re-found and re-checked.

**Ratio lemma (proof).** Setting: a decoder with exact supports has terms `x_k y_kᵀ` and `S_k(t,s)=1` iff `x_k(t)y_k(s) ≠ 0`, with `Σ_k x_k(t)y_k(s) = δ_ts` on every masked cell `(t,s)`; terms with `S_k(t,s)=0` contribute exactly 0 there. Fix rows `a ≠ b` and let `ρ_k = x_k(a)/x_k(b)` when both are nonzero; `E[k,l]` is true iff `ρ_k, ρ_l` are both defined and equal (so `E` is transitive, as the clauses require). The column case is the same with the roles of `x` and `y` exchanged. Two clause families:

* *Seed.* Take `c ∉ {a,b}` with `(a,c),(b,c)` masked, both targets 0, and suppose every term covers both or neither of the two cells; let `K` be the set covering them. Every `i ∈ K` has `x_i(a),x_i(b),y_i(c)` nonzero, so `ρ_i` is defined. Let `j ≠ k` be in `K` and suppose every pair in `K∖{j}` is `E`-true (if `K∖{j}={k}` this is vacuous). Then all `ρ_i`, `i ∈ K∖{j}`, share one value `ρ`. Put `σ = Σ_{i∈K∖{j}} x_i(b)y_i(c)`. The two zero targets read `x_j(b)y_j(c) + σ = 0` and `x_j(a)y_j(c) + ρσ = 0`; the first gives `σ = −x_j(b)y_j(c) ≠ 0`, and then `x_j(a)y_j(c) = ρ x_j(b)y_j(c)`, so `ρ_j = ρ = ρ_k` and `E[j,k]` holds. This is the clause `(some term covers exactly one cell) ∨ ¬S_j ∨ ¬S_k ∨ (some pair in K∖{j} covers and is not E-equal) ∨ E[j,k]` (with `|K|=2` the plain seed). No nonzero-entry assumption beyond exact supports is used.
* *Contradiction.* Take `d ∈ {a,b}` with `(a,d),(b,d)` masked (exactly one of them diagonal, target 1; the other target 0), and suppose every term covers both or neither, with every pair in the common cover set `K` `E`-true. `K ≠ ∅` since the diagonal sum is 1; all `ρ_i` (`i∈K`) are defined and equal to a common `ρ ≠ 0`. Summing, `δ_ad = Σ_K x_i(a)y_i(d) = ρ Σ_K x_i(b)y_i(d) = ρ δ_bd`; exactly one of `δ_ad, δ_bd` is 1 and the other 0, which is impossible for `ρ ≠ 0`. So the clause `(some term covers exactly one cell) ∨ (some pair covering (a,d) is not E-equal)` holds in every real decoder.

Both orientations (rows, columns) and both choices of `d` are emitted by `ratio_lemma` in `cutenc.py`. Given the assignment `E := [ρ equal]` and the auxiliary variables set to their defining conditions, every emitted clause is satisfied by any real decoder, so the clauses never remove one.

Status of stage 2 (audited): `cutenc.py`/`enc.py` were independently audited (WALL-AUDIT): a line-by-line re-derivation of the cut model, symmetry breaking, finite-field rank witnesses and this ratio lemma (all found sound), and about 560 pinned-pattern trials against exact rank (0 mismatches). The audit re-solved no shard; the DRAT proofs and certificate identities are machine-checked by `verify.py`. The cut validity is the identity `Σ_k D(q_k)(B∘S_k)D(p_k) = I`, which gives `Σ_k rank_Q A_k[X,Y] ≥ |X∩Y|`; its encoding is covered by the audit, not by a written proof here.

Scope: both the cover clause "0 or ≥ 2" and the AGLB rows of §5 hold only for exact decoders; they say nothing about border-rank decoders.

## 5. (e) CT8: `C(T) = 8` for rank-1 rectangles, all six KFAM orbits (EXACT)

**AGLB (acyclic generalised Lemma B, PROVED).** Let `M'` be the sum of the cost ≥ 1 terms; its free (unmasked) entries are unknown.
For any `B'`, `B'∘M' = Σ_k D(p_k) B' D(q_k)`, so `Σ_k rank B'[R_k,A_k] ≥ rank(B'∘M')`. If `B' = 1` on masked pairs and the diagonal and
`B'` is nonzero on free pairs only along an **acyclic** arc set, `B'∘M' = I + N` with `N` nilpotent, determinant 1, rank 8 for every
decoder. So `Σ_k rank_Q B'[R_k,A_k] ≥ 8` for every such `B'`; Lemma B's S-cuts (`B' = B|_{S×S}`) give `≥ |S|`.
WLOG each term is a maximal rectangle of its F2 cost. The question becomes an integer program over multisets of maximal rectangles
with cost ≤ 7.

* **Orbits 2 and 5: a single rational LP-dual certificate, stdlib check.** `data/ct8_orbit2_dual.json` is a `y ≥ 0` over three
  rows with `Σ_i y_i a_ij ≤ c_j` on all 115 maximal rectangles and `y·b = 22/3 > 7`; orbit 5 (`B = J`) needs one row, `y·b = 8`.
  `src/ct8/dual_check.py` recomputes the rectangles, exact ranks (rank mod `2^61−1` with a Hadamard-bound assertion) and the
  inequality in `Fraction`s.
* **Orbits 3, 4: LP bound, exact reduced-cost fixing and an exhaustive multiset DFS with certified LP bounds** (`certify.py`, scipy
  HiGHS; every bound used is recomputed in `Fraction`s). Orbit 3: 39 rectangles → 18, 37 nodes, 0 feasible. Orbit 4: 4,702 → 302,
  4,648 nodes, 0 feasible.
* **Orbits 0, 1** (hour-long DFS runs, 205,220 and 13.36 million nodes): not re-run by `verify.py`. They were reproduced by an
  independent auditor with their own code (orbit 0: 197,730 nodes, 575 s; orbit 1: 13.28 million nodes, all 99,040 relaxation-feasible
  multisets killed by exact branch-and-prune, 1,912 s). Logs are in `data/`.

Consequence: replacing the eight "low" terms of the all-cancel construction by shared or multi-line lows with any supports never
beats 64, for the rank-1 rectangle menu. Scope: the T-restriction and KFAM reduction come from the earlier TWOSIDE card and are
inherited; lows replaced jointly with S-term changes are not covered.

## 6. Rank-9 results taken from the RANK9 card (not replayed)

See README, "Further results": R7 (CHECKED, DRAT + exact lattice with Smith form), the gating criterion (PROVED), LOOSE/PAIR (PROVED mod R7; open sub-case Z0), the cost-64 rank-9 decoder (PROVED), and m = 9 gating (OPEN). They are context for the open part and are not claimed by `verify.py`.
