import RankNine.RuleC
import RankNine.Rows

/-!
# T1 by hand: closure with rules (a) and (c), glued to the matrix (NOTE §13.25, SCHEME §3.2)

Same closure certificates as T2 (`T2Close.check`), but the stored relations come from two kinds of descriptors:
* rule (a) (`descOK`, 13 entries): `t ⊥ s`, two terms: six-edge relation `relOf`;
* rule (c) (`desc3OK`, 29 entries): three two-term expansions of `M t s`: four-edge relation `rel3Of`.
Rule (c) relations are not balanced on the diagonal, so there is **no separate diagonal scale** here (it is killed
by rule (c)): the gauge is rows `p` and columns `q` only (`dg = false`).  Result: `M x y = γ x y / (p x q y)` on
every needed edge, which is `GramP` with `g = 1 / q`.
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

def noDg : ℕ → Bool := fun _ => false

/-- stored relation `a`: rule (a) or rule (c) descriptor (or empty), balanced in rows and columns -/
def rs1OK (C : Cert) (EI ER EC : BT ℕ) (DS : BT (List ℕ)) (nE m a : ℕ) : Bool :=
  (if (DS.get [] a).length = 29 then
      decide (C.RS.get [] a = rel3Of EI (DS.get [] a)) && desc3OK EI ER EC nE m (DS.get [] a)
    else
      decide (C.RS.get [] a = relOf EI (DS.get [] a)) &&
        (decide (DS.get [] a = []) || descOK EI ER EC nE m (DS.get [] a))) &&
  decide (nrm (rowL (erF ER) (C.RS.get [] a)) = []) && decide (nrm (rowL (erF EC) (C.RS.get [] a)) = [])

/-- all checks of one T1 closure besides `check C` -/
def glue1OK (C : Cert) (EI ER EC : BT ℕ) (DS : BT (List ℕ)) (nE m : ℕ) (T : List (ℕ × Bool)) (r0 : ℕ) : Bool :=
  (List.range (2 ^ max C.RS.dp DS.dp)).all (rs1OK C EI ER EC DS nE m) &&
  (List.range nE).all (fun e => decide (dot (ER.get 0 e) (EC.get 0 e) ≠ 0)) &&
  bfsOK (erF ER) (erF EC) noDg T [r0] [] &&
  C.GA.all (fun e => (T.map Prod.fst).contains e)

theorem rs1OK_all (C : Cert) (EI ER EC : BT ℕ) (DS : BT (List ℕ)) (nE m : ℕ)
    (h : (List.range (2 ^ max C.RS.dp DS.dp)).all (rs1OK C EI ER EC DS nE m) = true) (a : ℕ) :
    rs1OK C EI ER EC DS nE m a = true := by
  by_cases ha : a < 2 ^ max C.RS.dp DS.dp
  · exact List.all_eq_true.mp h a (List.mem_range.mpr ha)
  · have h1 : C.RS.get [] a = [] :=
      BT.get_big _ _ _ (le_trans (Nat.pow_le_pow_right (by norm_num) (le_max_left _ _)) (Nat.not_lt.mp ha))
    have h2 : DS.get [] a = [] :=
      BT.get_big _ _ _ (le_trans (Nat.pow_le_pow_right (by norm_num) (le_max_right _ _)) (Nat.not_lt.mp ha))
    unfold rs1OK; rw [h1, h2]; unfold relOf; simp [nrm, rowL]

/-- **T1 closure for one type.** -/
theorem t1_close (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (C : Cert) (EI ER EC : BT ℕ)
    (DS : BT (List ℕ)) (nE m : ℕ) (T : List (ℕ × Bool)) (r0 : ℕ) (hc : check C = true)
    (hg : glue1OK C EI ER EC DS nE m T r0 = true)
    (hExp : ∀ a, (DS.get [] a).length ≠ 29 → DS.get [] a ≠ [] → ExpOK A B m (dfr (DS.get [] a)))
    (hExp3 : ∀ a, (DS.get [] a).length = 29 → ∀ i < 3, ExpOK A B m (fr3 (DS.get [] a) i))
    (hMnz : ∀ e < nE, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0) :
    ∃ (p q : ℕ → K), (∀ x, p x ≠ 0) ∧ (∀ x, q x ≠ 0) ∧
      ∀ e ∈ C.NE, vM A B ER EC nE e * p (erF ER e) * q (erF EC e) = 1 := by
  unfold glue1OK at hg
  simp only [Bool.and_eq_true, List.all_eq_true, List.mem_range, decide_eq_true_eq] at hg
  obtain ⟨⟨⟨hrs, hdot⟩, hbfs⟩, hGA⟩ := hg
  have hrs' := rs1OK_all C EI ER EC DS nE m (List.all_eq_true.mpr fun a ha => hrs a (List.mem_range.mp ha))
  have hGnz : ∀ e < nE, gam (K := K) (ER.get 0 e) (EC.get 0 e) ≠ 0 := by
    intro e he; unfold gam
    exact div_ne_zero (by exact_mod_cast hdot e he) (by norm_num)
  have hv : ∀ e, vM A B ER EC nE e ≠ 0 := by
    intro e; unfold vM; split_ifs with he
    · exact div_ne_zero (hMnz e he) (hGnz e he)
    · exact one_ne_zero
  obtain ⟨p, q, hp, hq, -, -, hT⟩ := bfs_gauge (vM A B ER EC nE) hv (erF ER) (erF EC) noDg T [r0] []
    (fun _ => 1) (fun _ => 1) hbfs (fun _ => one_ne_zero) (fun _ => one_ne_zero)
  have hgv : ∀ e, gv (vM A B ER EC nE) p q 1 (erF ER) (erF EC) noDg e =
      vM A B ER EC nE e * p (erF ER e) * q (erF EC e) := by
    intro e; simp [gv, noDg]
  refine ⟨p, q, hp, hq, fun e he => ?_⟩
  rw [← hgv e]
  refine closure_sound C _ hc ?_ ?_ ?_ e he
  · intro a
    have ha := hrs' a
    unfold rs1OK at ha
    simp only [Bool.and_eq_true, decide_eq_true_eq] at ha
    obtain ⟨⟨hsel, b1⟩, b2⟩ := ha
    rw [rp_gauge _ p q 1 _ _ _ hp hq one_ne_zero _ b1 b2 (by simp [diagL, noDg, nrm])]
    split_ifs at hsel with hl
    · simp only [Bool.and_eq_true, decide_eq_true_eq] at hsel
      rw [hsel.1]
      exact rp_rel3Of A B hdiag hmask EI ER EC nE m hMnz hGnz _ hsel.2 (hExp3 a hl)
    · simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at hsel
      obtain ⟨hra, hdesc⟩ := hsel
      rw [hra]
      rcases hdesc with h0 | hok
      · rw [h0]; unfold relOf; simp [rp]
      · by_cases h0 : DS.get [] a = []
        · rw [h0]; unfold relOf; simp [rp]
        · exact rp_relOf A B hdiag hmask EI ER EC nE m hMnz hGnz _ hok (hExp a hl h0)
  · intro e
    unfold gv; simp only [noDg]
    exact mul_ne_zero (mul_ne_zero (mul_ne_zero (hv e) (hp _)) (hq _)) (by simp)
  · intro e he
    have hge := hGA e he
    obtain ⟨eb, heb, hee⟩ := List.mem_map.mp (List.contains_iff_mem.mp hge)
    rw [← hee]
    have := (hT eb heb).2
    simpa [gv, noDg] using this

/-- every pair of the mask `zm` is orthogonal or a needed edge -/
def cov1OK (EI ER EC : BT ℕ) (nE zm : ℕ) (NE : List ℕ) : Bool :=
  (List.range 104).all fun x => (List.range 104).all fun y =>
    !zm.testBit x || !zm.testBit y || (decide (x ≠ y) && orthB x y) ||
      (edgeOK EI ER EC nE x y && NE.contains (eid EI x y))

/-- **T1 output.** The closure on a covering edge table gives `GramP` on `zm × zm` (with `g = 1 / q`). -/
theorem t1_gram (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (C : Cert) (EI ER EC : BT ℕ)
    (DS : BT (List ℕ)) (nE m zm : ℕ) (T : List (ℕ × Bool)) (r0 : ℕ) (hc : check C = true)
    (hg : glue1OK C EI ER EC DS nE m T r0 = true) (hcov : cov1OK EI ER EC nE zm C.NE = true)
    (hExp : ∀ a, (DS.get [] a).length ≠ 29 → DS.get [] a ≠ [] → ExpOK A B m (dfr (DS.get [] a)))
    (hExp3 : ∀ a, (DS.get [] a).length = 29 → ∀ i < 3, ExpOK A B m (fr3 (DS.get [] a) i))
    (hMnz : ∀ e < nE, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0) :
    ∃ g : ℕ → K, (∀ x, g x ≠ 0) ∧
      ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y := by
  obtain ⟨p, q, hp, hq, hNE⟩ := t1_close A B hdiag hmask C EI ER EC DS nE m T r0 hc hg hExp hExp3 hMnz
  have hGnz : ∀ e < nE, gam (K := K) (ER.get 0 e) (EC.get 0 e) ≠ 0 := by
    unfold glue1OK at hg
    simp only [Bool.and_eq_true, List.all_eq_true, List.mem_range, decide_eq_true_eq] at hg
    intro e he; unfold gam
    exact div_ne_zero (by exact_mod_cast hg.1.1.2 e he) (by norm_num)
  -- value on an edge
  have hval : ∀ x y, edgeOK EI ER EC nE x y = true → eid EI x y ∈ C.NE →
      Mx A B x y = gam x y / (p x * q y) := by
    intro x y he hin
    have h1 := hNE _ hin
    rw [vM_edge A B EI ER EC nE x y he] at h1
    have hx : erF ER (eid EI x y) = x := by
      unfold edgeOK at he; simp only [Bool.and_eq_true, decide_eq_true_eq] at he; exact he.1.2
    have hy : erF EC (eid EI x y) = y := by
      unfold edgeOK at he; simp only [Bool.and_eq_true, decide_eq_true_eq] at he; exact he.2
    rw [hx, hy] at h1
    have hg0 := edge_nz EI ER EC nE x y he (P := fun x y => gam (K := K) x y ≠ 0) hGnz
    have hpx := hp x; have hqy := hq y
    field_simp at h1 ⊢
    linear_combination h1
  refine ⟨fun y => (q y)⁻¹, fun y => inv_ne_zero (hq y), ?_⟩
  intro x hx y hy hzx hzy
  have hc1 := List.all_eq_true.mp (List.all_eq_true.mp hcov x (List.mem_range.mpr hx)) y (List.mem_range.mpr hy)
  have hc0 := List.all_eq_true.mp (List.all_eq_true.mp hcov x (List.mem_range.mpr hx)) x (List.mem_range.mpr hx)
  simp only [hzx, hzy, Bool.not_true, Bool.false_or, Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq,
    List.contains_iff_mem] at hc1 hc0
  have hxx : Mx A B x x = gam x x / (p x * q x) := by
    rcases hc0 with ⟨h, -⟩ | ⟨he, hin⟩
    · exact absurd rfl h
    · exact hval x x he hin
  have hgxx : gam (K := K) x x = 1 := by unfold gam; rw [dot_self hx]; norm_num
  unfold GramP dS
  rw [hxx, hgxx]
  have hpx := hp x; have hqx := hq x; have hqy := hq y
  rcases hc1 with ⟨-, ho⟩ | ⟨he, hin⟩
  · have h0 : Mx A B x y = 0 := orthB_M A B hmask hx hy ho
    have hd : dot x y = 0 := by
      have := orth_of_orthB hx hy ho; simpa [orth] using this
    rw [h0]; unfold gam; rw [hd]; simp
  · rw [hval x y he hin]
    field_simp

end RankNine.T2
