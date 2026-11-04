import RankNine.T2Glue

/-!
# Rule (c) of the hand route (NOTE §13.21)

Three frame expansions of the same entry `M t s` (`t` not orthogonal to `s`), each with exactly two non-zero
products, with term pairs `{f, g}`, `{f, h}`, `{g, h}`:
  `M t s = P f + P g = P f + P h = P g + P h`,  `P x = M t x * M x s / M x x`.
Then `P f = M t s / 2` (char `≠ 2`).  The Gram matrix satisfies the same identity (checked on integers), so the
ratios `v = M / γ` satisfy `v t f * v f s = v t s * v f f`: a four-edge relation of product `1`, which the closure
certificates (`T2Close`) use exactly like the six-edge relations of rule (a) (`T2Glue.relOf`).

Descriptor `d = [t, s, f, g, h] ++ F₁ ++ F₂ ++ F₃` (three 8-line frames; `F₁ ∋ f, g`, `F₂ ∋ f, h`, `F₃ ∋ g, h`).
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

/-- the frame of a rule (c) descriptor -/
def fr3 (d : List ℕ) (i : ℕ) : List ℕ := (d.drop (5 + 8 * i)).take 8

/-- one frame of the descriptor: lines `< 104`, distinct, `x, y` dead members, `t` dead, every line dead or
orthogonal to `t`, every other dead line orthogonal to `t` or to `s` -/
def pairOK3 (m t s x y : ℕ) (F : List ℕ) : Bool :=
  F.all (· < 104) && F.Nodup && F.contains x && F.contains y && decide (x ≠ y) &&
  m.testBit x && m.testBit y && m.testBit t &&
  F.all (fun f => m.testBit f || orthB t f) &&
  F.all (fun f => !m.testBit f || f == x || f == y || orthB t f || orthB f s)

/-- the expansion of `M t s` along a checked frame has exactly the two terms `x`, `y` -/
theorem pair_exp (A B : ℕ → Fin 9 → K) (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    {m t s x y : ℕ} {F : List ℕ} (ht : t < 104) (hs : s < 104) (h : pairOK3 m t s x y F = true)
    (hE : ExpOK A B m F) :
    Mx A B t s = Mx A B t x * Mx A B x s / Mx A B x x + Mx A B t y * Mx A B y s / Mx A B y y := by
  unfold pairOK3 at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.contains_iff_mem, Bool.or_eq_true,
    Bool.not_eq_true', beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨hF, -⟩, hxF⟩, hyF⟩, hxy⟩, hmx⟩, hmy⟩, hmt⟩, hout⟩, hz⟩ := h
  have hexp := hE t hmt (fun f hf hdf => by
    rcases hout f hf with h | h
    · rw [hdf] at h; exact absurd h (by simp)
    · exact orthB_M A B hmask ht (hF f hf) h) s
  have hsub : ({x, y} : Finset ℕ) ⊆ F.toFinset.filter (fun f => m.testBit f = true) := by
    intro k hk
    simp only [Finset.mem_insert, Finset.mem_singleton] at hk
    rcases hk with rfl | rfl
    · simp [hxF, hmx]
    · simp [hyF, hmy]
  rw [← Finset.sum_subset hsub (fun k hk hk' => by
    simp only [Finset.mem_insert, Finset.mem_singleton, not_or] at hk'
    simp only [Finset.mem_filter, List.mem_toFinset] at hk
    have hk0 := hF k hk.1
    rcases hz k hk.1 with ((((h | h) | h) | h) | h)
    · rw [hk.2] at h; exact absurd h (by simp)
    · exact absurd h hk'.1
    · exact absurd h hk'.2
    · rw [orthB_M A B hmask ht hk0 h, zero_mul, zero_div]
    · rw [orthB_M A B hmask hk0 hs h, mul_zero, zero_div]), Finset.sum_pair hxy] at hexp
  exact hexp

/-- rule (c), pure algebra -/
theorem rule_c_alg {μ a b c : K} (h1 : μ = a + b) (h2 : μ = a + c) (h3 : μ = b + c) : 2 * a = μ := by
  linear_combination -h1 - h2 + h3

def desc3OK (EI ER EC : BT ℕ) (nE m : ℕ) (d : List ℕ) : Bool :=
  let t := d.getD 0 0; let s := d.getD 1 0; let f := d.getD 2 0; let g := d.getD 3 0; let h := d.getD 4 0
  decide (d.length = 29) && decide (t < 104) && decide (s < 104) && decide (f < 104) &&
  pairOK3 m t s f g (fr3 d 0) && pairOK3 m t s f h (fr3 d 1) && pairOK3 m t s g h (fr3 d 2) &&
  decide (2 * (dot t f * dot f s) = dot t s * dot f f) &&
  edgeOK EI ER EC nE t f && edgeOK EI ER EC nE f s && edgeOK EI ER EC nE t s && edgeOK EI ER EC nE f f

/-- signed four-edge list of a rule (c) descriptor: `v t f * v f s * (v t s)⁻¹ * (v f f)⁻¹` -/
def rel3Of (EI : BT ℕ) (d : List ℕ) : List ℕ :=
  let t := d.getD 0 0; let s := d.getD 1 0; let f := d.getD 2 0
  [2 * eid EI t f, 2 * eid EI f s, 2 * eid EI t s + 1, 2 * eid EI f f + 1]

theorem desc3_relation (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (EI ER EC : BT ℕ) (nE m : ℕ)
    (d : List ℕ) (hd : desc3OK EI ER EC nE m d = true)
    (hE : ∀ i < 3, ExpOK A B m (fr3 d i)) :
    2 * (Mx A B (d.getD 0 0) (d.getD 2 0) * Mx A B (d.getD 2 0) (d.getD 1 0)) =
      Mx A B (d.getD 0 0) (d.getD 1 0) * Mx A B (d.getD 2 0) (d.getD 2 0) := by
  unfold desc3OK at hd
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hd
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨-, ht⟩, hs⟩, hf⟩, p1⟩, p2⟩, p3⟩, -⟩, -⟩, -⟩, -⟩, -⟩ := hd
  set t := d.getD 0 0; set s := d.getD 1 0; set f := d.getD 2 0
  have e1 := pair_exp A B hmask ht hs p1 (hE 0 (by norm_num))
  have e2 := pair_exp A B hmask ht hs p2 (hE 1 (by norm_num))
  have e3 := pair_exp A B hmask ht hs p3 (hE 2 (by norm_num))
  have key := rule_c_alg e1 e2 e3
  have hff : Mx A B f f ≠ 0 := hdiag f hf
  calc 2 * (Mx A B t f * Mx A B f s) = 2 * (Mx A B t f * Mx A B f s / Mx A B f f) * Mx A B f f := by
        field_simp
    _ = Mx A B t s * Mx A B f f := by rw [key]

/-- a checked rule (c) descriptor gives a relation of product `1` for `v = M / γ` -/
theorem rp_rel3Of (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (EI ER EC : BT ℕ) (nE m : ℕ)
    (hMnz : ∀ e < nE, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0)
    (hGnz : ∀ e < nE, gam (K := K) (ER.get 0 e) (EC.get 0 e) ≠ 0)
    (d : List ℕ) (hd : desc3OK EI ER EC nE m d = true) (hE : ∀ i < 3, ExpOK A B m (fr3 d i)) :
    rp (vM A B ER EC nE) (rel3Of EI d) = 1 := by
  have hrel := desc3_relation A B hdiag hmask EI ER EC nE m d hd hE
  unfold desc3OK at hd
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hd
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨-, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, hG⟩, e1⟩, e2⟩, e3⟩, e4⟩ := hd
  set t := d.getD 0 0; set s := d.getD 1 0; set f := d.getD 2 0
  have hGK : 2 * (gam (K := K) t f * gam f s) = gam t s * gam f f := by
    have q1 : 2 * (gam (K := K) t f * gam f s) = ((2 * (dot t f * dot f s) : ℤ) : K) / 324 := by
      unfold gam; push_cast; ring
    have q2 : gam (K := K) t s * gam f f = ((dot t s * dot f f : ℤ) : K) / 324 := by
      unfold gam; push_cast; ring
    rw [q1, q2, hG]
  have m1 := edge_nz EI ER EC nE t f e1 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m2 := edge_nz EI ER EC nE f s e2 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m3 := edge_nz EI ER EC nE t s e3 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m4 := edge_nz EI ER EC nE f f e4 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have g1 := edge_nz EI ER EC nE t f e1 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g2 := edge_nz EI ER EC nE f s e2 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g3 := edge_nz EI ER EC nE t s e3 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g4 := edge_nz EI ER EC nE f f e4 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  unfold rel3Of rp
  simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one, sv_two, sv_two_one]
  rw [vM_edge A B EI ER EC nE _ _ e1, vM_edge A B EI ER EC nE _ _ e2, vM_edge A B EI ER EC nE _ _ e3,
    vM_edge A B EI ER EC nE _ _ e4]
  field_simp
  linear_combination (gam t s * gam f f) * hrel - (Mx A B t s * Mx A B f f) * hGK

/-! ## Rule (b): two expansions of `M t s` sharing the term `f` (`{f, g}`, `{f, h}`) give `P g = P h` -/

def desc2OK (EI ER EC : BT ℕ) (nE m : ℕ) (d : List ℕ) : Bool :=
  let t := d.getD 0 0; let s := d.getD 1 0; let f := d.getD 2 0; let g := d.getD 3 0; let h := d.getD 4 0
  decide (d.length = 21) && decide (t < 104) && decide (s < 104) && decide (g < 104) && decide (h < 104) &&
  pairOK3 m t s f g (fr3 d 0) && pairOK3 m t s f h (fr3 d 1) &&
  decide (dot t g * dot g s * dot h h = dot t h * dot h s * dot g g) &&
  edgeOK EI ER EC nE t g && edgeOK EI ER EC nE g s && edgeOK EI ER EC nE h h &&
  edgeOK EI ER EC nE t h && edgeOK EI ER EC nE h s && edgeOK EI ER EC nE g g

/-- `v t g * v g s * v h h * (v t h)⁻¹ * (v h s)⁻¹ * (v g g)⁻¹` -/
def rel2Of (EI : BT ℕ) (d : List ℕ) : List ℕ :=
  let t := d.getD 0 0; let s := d.getD 1 0; let g := d.getD 3 0; let h := d.getD 4 0
  [2 * eid EI t g, 2 * eid EI g s, 2 * eid EI h h, 2 * eid EI t h + 1, 2 * eid EI h s + 1, 2 * eid EI g g + 1]

theorem desc2_relation (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (EI ER EC : BT ℕ) (nE m : ℕ)
    (d : List ℕ) (hd : desc2OK EI ER EC nE m d = true) (hE : ∀ i < 2, ExpOK A B m (fr3 d i)) :
    Mx A B (d.getD 0 0) (d.getD 3 0) * Mx A B (d.getD 3 0) (d.getD 1 0) * Mx A B (d.getD 4 0) (d.getD 4 0) =
      Mx A B (d.getD 0 0) (d.getD 4 0) * Mx A B (d.getD 4 0) (d.getD 1 0) * Mx A B (d.getD 3 0) (d.getD 3 0) := by
  unfold desc2OK at hd
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hd
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨-, ht⟩, hs⟩, hg⟩, hh⟩, p1⟩, p2⟩, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩ := hd
  set t := d.getD 0 0; set s := d.getD 1 0; set f := d.getD 2 0; set g := d.getD 3 0; set h := d.getD 4 0
  have e1 := pair_exp A B hmask ht hs p1 (hE 0 (by norm_num))
  have e2 := pair_exp A B hmask ht hs p2 (hE 1 (by norm_num))
  have hgg : Mx A B g g ≠ 0 := hdiag g hg
  have hhh : Mx A B h h ≠ 0 := hdiag h hh
  have key : Mx A B t g * Mx A B g s / Mx A B g g = Mx A B t h * Mx A B h s / Mx A B h h := by
    linear_combination e2 - e1
  field_simp at key
  linear_combination key

theorem rp_rel2Of (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (EI ER EC : BT ℕ) (nE m : ℕ)
    (hMnz : ∀ e < nE, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0)
    (hGnz : ∀ e < nE, gam (K := K) (ER.get 0 e) (EC.get 0 e) ≠ 0)
    (d : List ℕ) (hd : desc2OK EI ER EC nE m d = true) (hE : ∀ i < 2, ExpOK A B m (fr3 d i)) :
    rp (vM A B ER EC nE) (rel2Of EI d) = 1 := by
  have hrel := desc2_relation A B hdiag hmask EI ER EC nE m d hd hE
  unfold desc2OK at hd
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hd
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨-, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, hG⟩, e1⟩, e2⟩, e3⟩, e4⟩, e5⟩, e6⟩ := hd
  set t := d.getD 0 0; set s := d.getD 1 0; set g := d.getD 3 0; set h := d.getD 4 0
  have hGK : gam (K := K) t g * gam g s * gam h h = gam t h * gam h s * gam g g := by
    have q1 : gam (K := K) t g * gam g s * gam h h = ((dot t g * dot g s * dot h h : ℤ) : K) / 5832 := by
      unfold gam; push_cast; ring
    have q2 : gam (K := K) t h * gam h s * gam g g = ((dot t h * dot h s * dot g g : ℤ) : K) / 5832 := by
      unfold gam; push_cast; ring
    rw [q1, q2, hG]
  have m1 := edge_nz EI ER EC nE t g e1 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m2 := edge_nz EI ER EC nE g s e2 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m3 := edge_nz EI ER EC nE h h e3 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m4 := edge_nz EI ER EC nE t h e4 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m5 := edge_nz EI ER EC nE h s e5 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m6 := edge_nz EI ER EC nE g g e6 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have g1 := edge_nz EI ER EC nE t g e1 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g2 := edge_nz EI ER EC nE g s e2 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g3 := edge_nz EI ER EC nE h h e3 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g4 := edge_nz EI ER EC nE t h e4 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g5 := edge_nz EI ER EC nE h s e5 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g6 := edge_nz EI ER EC nE g g e6 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  unfold rel2Of rp
  simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one, sv_two, sv_two_one]
  rw [vM_edge A B EI ER EC nE _ _ e1, vM_edge A B EI ER EC nE _ _ e2, vM_edge A B EI ER EC nE _ _ e3,
    vM_edge A B EI ER EC nE _ _ e4, vM_edge A B EI ER EC nE _ _ e5, vM_edge A B EI ER EC nE _ _ e6]
  field_simp
  linear_combination (gam t h * gam h s * gam g g) * hrel - (Mx A B t h * Mx A B h s * Mx A B g g) * hGK

/-! ## Inverted relations -/

theorem rp_opp (v : ℕ → K) (hv : ∀ e, v e ≠ 0) (l : List ℕ) : rp v (l.map opp) * rp v l = 1 := by
  induction l with
  | nil => simp [rp]
  | cons a l ih =>
    have h1 := sv_opp v hv a
    unfold rp at ih ⊢
    simp only [List.map_cons, List.prod_cons] at ih ⊢
    calc sv v (opp a) * (List.map (sv v) (List.map opp l)).prod * (sv v a * (List.map (sv v) l).prod)
        = (sv v (opp a) * sv v a) * ((List.map (sv v) (List.map opp l)).prod * (List.map (sv v) l).prod) := by ring
      _ = 1 := by rw [h1, ih, one_mul]

theorem rp_opp_one (v : ℕ → K) (hv : ∀ e, v e ≠ 0) {l : List ℕ} (h : rp v l = 1) : rp v (l.map opp) = 1 := by
  have := rp_opp v hv l; rwa [h, mul_one] at this

end RankNine.T2
