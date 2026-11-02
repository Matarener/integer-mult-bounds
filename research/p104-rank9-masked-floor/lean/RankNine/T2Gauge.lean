import RankNine.T2Close

/-!
# T2.3 gauge: row/column scalings and one diagonal scale

Edge `e` of the bipartite block graph joins row `er e` and column `ec e`; `dg e` marks diagonal edges `(x, x)`.
Rescaling `v e ↦ v e * p (er e) * q (ec e) * λ^[dg e]` does not change the product of a *balanced* relation (every row,
every column and the diagonal flag cancel, checked as `nrm … = []`).  Along a spanning tree given in BFS order
(`bfsOK`) the scalings can be chosen so that all tree edges and one diagonal edge become `1`: these are the gauge
edges of the closure certificates.
-/

namespace RankNine.T2

variable {K : Type*} [Field K]

def rowL (er : ℕ → ℕ) (r : List ℕ) : List ℕ := r.map fun q => 2 * er (q / 2) + q % 2

def diagL (dg : ℕ → Bool) (r : List ℕ) : List ℕ := (r.filter fun q => dg (q / 2)).map fun q => q % 2

/-- rescaled values -/
def gv (v p q : ℕ → K) (l : K) (er ec : ℕ → ℕ) (dg : ℕ → Bool) (e : ℕ) : K :=
  v e * p (er e) * q (ec e) * (if dg e then l else 1)

theorem sv_shift (f : ℕ → K) (x q : ℕ) : sv f (2 * x + q % 2) = if q % 2 = 0 then f x else (f x)⁻¹ := by
  unfold sv
  have h1 : (2 * x + q % 2) / 2 = x := by omega
  by_cases h : q % 2 = 0
  · rw [if_pos (by omega), if_pos h, h1]
  · rw [if_neg (by omega), if_neg h, h1]

theorem rp_gv (v p q : ℕ → K) (l : K) (er ec : ℕ → ℕ) (dg : ℕ → Bool) (r : List ℕ) :
    rp (gv v p q l er ec dg) r =
      rp v r * rp p (rowL er r) * rp q (rowL ec r) * rp (fun _ => l) (diagL dg r) := by
  induction r with
  | nil => simp [rp, rowL, diagL]
  | cons a r ih =>
    unfold rp rowL diagL at ih ⊢
    simp only [List.map_cons, List.prod_cons, List.filter_cons]
    rw [ih, sv_shift, sv_shift]
    by_cases hd : dg (a / 2) = true
    · simp only [hd, if_true, List.map_cons, List.prod_cons]
      unfold sv gv
      by_cases ha : a % 2 = 0
      · simp only [ha, if_true, hd]; ring
      · simp only [ha, if_false, hd, mul_inv, if_true, Nat.mod_mod]; ring
    · simp only [hd, Bool.false_eq_true, if_false]
      unfold sv gv
      by_cases ha : a % 2 = 0
      · simp only [ha, if_true, hd, Bool.false_eq_true, if_false]; ring
      · simp only [ha, if_false, hd, Bool.false_eq_true, mul_inv, inv_one]; ring

/-- a balanced relation keeps its product under rescaling -/
theorem rp_gauge (v p q : ℕ → K) (l : K) (er ec : ℕ → ℕ) (dg : ℕ → Bool) (hp : ∀ x, p x ≠ 0)
    (hq : ∀ x, q x ≠ 0) (hl : l ≠ 0) (r : List ℕ) (h1 : nrm (rowL er r) = []) (h2 : nrm (rowL ec r) = [])
    (h3 : nrm (diagL dg r) = []) : rp (gv v p q l er ec dg) r = rp v r := by
  rw [rp_gv, ← rp_nrm p hp (rowL er r), h1, ← rp_nrm q hq (rowL ec r), h2,
    ← rp_nrm (fun _ => l) (fun _ => hl) (diagL dg r), h3]
  simp [rp]

/-- BFS order of a spanning tree: `(e, false)` reaches the column of `e`, `(e, true)` its row -/
def bfsOK (er ec : ℕ → ℕ) (dg : ℕ → Bool) : List (ℕ × Bool) → List ℕ → List ℕ → Bool
  | [], _, _ => true
  | (e, false) :: T, Rr, Rc =>
    !dg e && Rr.contains (er e) && !Rc.contains (ec e) && bfsOK er ec dg T Rr (ec e :: Rc)
  | (e, true) :: T, Rr, Rc =>
    !dg e && Rc.contains (ec e) && !Rr.contains (er e) && bfsOK er ec dg T (er e :: Rr) Rc

theorem bfs_gauge (v : ℕ → K) (hv : ∀ e, v e ≠ 0) (er ec : ℕ → ℕ) (dg : ℕ → Bool) :
    ∀ (T : List (ℕ × Bool)) (Rr Rc : List ℕ) (p q : ℕ → K), bfsOK er ec dg T Rr Rc = true →
      (∀ x, p x ≠ 0) → (∀ x, q x ≠ 0) →
      ∃ p' q' : ℕ → K, (∀ x, p' x ≠ 0) ∧ (∀ x, q' x ≠ 0) ∧ (∀ x ∈ Rr, p' x = p x) ∧ (∀ y ∈ Rc, q' y = q y) ∧
        ∀ eb ∈ T, dg eb.1 = false ∧ v eb.1 * p' (er eb.1) * q' (ec eb.1) = 1 := by
  intro T
  induction T with
  | nil => intro Rr Rc p q _ hp hq; exact ⟨p, q, hp, hq, fun _ _ => rfl, fun _ _ => rfl, by simp⟩
  | cons eb T ih =>
    intro Rr Rc p q hok hp hq
    obtain ⟨e, b⟩ := eb
    cases b with
    | false =>
      simp only [bfsOK, Bool.and_eq_true, Bool.not_eq_true'] at hok
      obtain ⟨⟨⟨hd, hr0⟩, hc0⟩, hT⟩ := hok
      have hr : er e ∈ Rr := List.contains_iff_mem.mp hr0
      have hc : ec e ∉ Rc := fun h => by rw [List.contains_iff_mem.mpr h] at hc0; cases hc0
      set q1 := Function.update q (ec e) (v e * p (er e))⁻¹ with hq1
      have hq1n : ∀ x, q1 x ≠ 0 := by
        intro x; rw [hq1, Function.update_apply]; split_ifs
        · exact inv_ne_zero (mul_ne_zero (hv e) (hp _))
        · exact hq x
      obtain ⟨p', q', hp', hq', hpR, hqR, hall⟩ := ih Rr (ec e :: Rc) p q1 hT hp hq1n
      refine ⟨p', q', hp', hq', hpR, fun y hy => ?_, ?_⟩
      · rw [hqR y (List.mem_cons_of_mem _ hy), hq1, Function.update_of_ne]
        intro h; rw [h] at hy; exact hc hy
      · intro eb' heb
        rcases List.mem_cons.mp heb with h | h
        · subst h
          refine ⟨hd, ?_⟩
          rw [hpR _ hr, hqR _ (List.mem_cons_self), hq1, Function.update_self]
          exact mul_inv_cancel₀ (mul_ne_zero (hv e) (hp _))
        · exact hall eb' h
    | true =>
      simp only [bfsOK, Bool.and_eq_true, Bool.not_eq_true'] at hok
      obtain ⟨⟨⟨hd, hc0⟩, hr0⟩, hT⟩ := hok
      have hc : ec e ∈ Rc := List.contains_iff_mem.mp hc0
      have hr : er e ∉ Rr := fun h => by rw [List.contains_iff_mem.mpr h] at hr0; cases hr0
      set p1 := Function.update p (er e) (v e * q (ec e))⁻¹ with hp1
      have hp1n : ∀ x, p1 x ≠ 0 := by
        intro x; rw [hp1, Function.update_apply]; split_ifs
        · exact inv_ne_zero (mul_ne_zero (hv e) (hq _))
        · exact hp x
      obtain ⟨p', q', hp', hq', hpR, hqR, hall⟩ := ih (er e :: Rr) Rc p1 q hT hp1n hq
      refine ⟨p', q', hp', hq', fun x hx => ?_, hqR, ?_⟩
      · rw [hpR x (List.mem_cons_of_mem _ hx), hp1, Function.update_of_ne]
        intro h; rw [h] at hx; exact hr hx
      · intro eb' heb
        rcases List.mem_cons.mp heb with h | h
        · subst h
          refine ⟨hd, ?_⟩
          rw [hpR _ List.mem_cons_self, hqR _ hc, hp1, Function.update_self]
          have h0 := hv e
          have h1 := hq (ec e)
          field_simp
        · exact hall eb' h

/-- **Gauge.** Tree edges in BFS order from row `r0` and one diagonal edge `d` can all be made `1`. -/
theorem gauge_exists (v : ℕ → K) (hv : ∀ e, v e ≠ 0) (er ec : ℕ → ℕ) (dg : ℕ → Bool) (T : List (ℕ × Bool))
    (r0 d : ℕ) (hT : bfsOK er ec dg T [r0] [] = true) (hd : dg d = true) :
    ∃ (p q : ℕ → K) (l : K), (∀ x, p x ≠ 0) ∧ (∀ x, q x ≠ 0) ∧ l ≠ 0 ∧
      (∀ e, gv v p q l er ec dg e ≠ 0) ∧ (∀ eb ∈ T, gv v p q l er ec dg eb.1 = 1) ∧
      gv v p q l er ec dg d = 1 := by
  obtain ⟨p, q, hp, hq, -, -, hall⟩ := bfs_gauge v hv er ec dg T [r0] [] (fun _ => 1) (fun _ => 1) hT
    (fun _ => one_ne_zero) (fun _ => one_ne_zero)
  have hpq : v d * p (er d) * q (ec d) ≠ 0 := mul_ne_zero (mul_ne_zero (hv d) (hp _)) (hq _)
  refine ⟨p, q, (v d * p (er d) * q (ec d))⁻¹, hp, hq, inv_ne_zero hpq, ?_, ?_, ?_⟩
  · intro e; unfold gv
    refine mul_ne_zero (mul_ne_zero (mul_ne_zero (hv e) (hp _)) (hq _)) ?_
    split_ifs
    · exact inv_ne_zero hpq
    · exact one_ne_zero
  · intro eb heb
    obtain ⟨hd', h1⟩ := hall eb heb
    unfold gv; rw [hd']; simp [h1]
  · unfold gv; rw [hd, if_pos rfl]; exact mul_inv_cancel₀ hpq

end RankNine.T2
