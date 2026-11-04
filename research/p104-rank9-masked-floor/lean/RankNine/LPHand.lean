import RankNine.Census
import RankNine.Cap6True
import RankNine.LPData

set_option linter.unusedSectionVars false

/-!
# Lemma P by hand, weak form: no six label planes are pairwise compatible (CENSUS-PLAN §14)

The census counting needs only "no six bigs" (`censusFact_of_facts6`: weights `7 ≤ r + 2 [lspan ≤ 6] + [lspan ≤ 7]`,
so `Σ r ≥ 63 − 2 − 5 = 56`).  The planes of the bigs are pairwise compatible with the **common** exception set
`E = Zr` (`compatE_of`).  Proof of "no six" (`lp6_of`):

1. **Mod 2** (`mc_of_compat`).  A set `F` of integer rank `≤ 7` has its E8 coordinates (`cZ`, basis `Bm`, det 256)
   of rank `≤ 7` mod 2 (`minor_cb`, `perp_of_minors`); the linear map `Am` (`labK t ᵥ* Am = cb t`, `jv ᵥ* Am = 0`,
   `Nm * Am = 1`) turns the normal into an even `s ≠ 0` with `labK t · s = 0` on `F`.  So for a compatible pair, every
   port of the slab `Σ_s = {t : labK t · s ≠ 0}` (`= {t : labK t · u = 0}`, `u = s + j` odd) outside `L(Z) ∪ L(Z')`
   lies in `E`.  Slabs have `≥ 48` ports (`evOK`).
2. **Type 0** (`u` in neither plane, `not_type0`): `Σ ⊆ L(⟨Z, u⟩) ∪ L(⟨Z', u⟩) ∪ E`, `≤ 20 + 20 + 4` (`f(6) = 20`).
3. **Type 1** (`u` in exactly one plane, `not_type1`): excluded by the table `t1xOK` (for every odd `u ≠ j`, plane
   `⟨u, a⟩` and 3-space `⟨u, c, d⟩` the uncovered ports are not a clique of size `≤ 4`; #eval + Python
   `lphand/t1x_check.py`; hand proof CENSUS-PLAN §12, to be formalized).
4. **Type 2 for all pairs** ⇒ the odd points `O_k` (two per plane) are pairwise intersecting and distinct
   (equal ones give equal live sets, `Σ ⊆ L(Z) ∪ E`, `48 ≤ 36 + 4`), so they form a star at one `u` (`star6`) and all
   pairs use the same slab.  Then the sets `(Σ ∖ E) ∖ L(Z_k)` are pairwise disjoint of size `≥ |Σ ∖ E| − 36`:
   `6 (M − 36) ≤ M` with `M ≥ 44`, impossible (`f(7) = 36`).
-/

namespace RankNine.LP

open Matrix Finset Module BForm BForm.E8 RankNine.Census RankNine.Facts

attribute [local instance] Classical.propDecidable

/-! ## Label bounds for planes and 3-spaces -/

/-- `f(7) = 36` for a plane: two distinct non-zero vectors kill at most 36 ports -/
theorem card_two (z1 z2 : V9) (h1 : z1 ≠ 0) (h2 : z2 ≠ 0) (h12 : z1 ≠ z2) :
    (univ.filter fun t : Fin 104 => labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0).card ≤ 36 := by
  have h3 : z1 + z2 ≠ 0 := fun e => h12 (v9_eq_of_add e)
  have hid := count_id z1 z2
  rw [nOdd_card, nOdd_card, nOdd_card] at hid
  obtain ⟨a1, b1, c1⟩ := fact44 h1
  obtain ⟨a2, b2, c2⟩ := fact44 h2
  obtain ⟨a3, b3, c3⟩ := fact44 h3
  have hnot : ¬ (nOdd (zl z1) = 44 ∧ nOdd (zl z2) = 44 ∧ nOdd (zl (z1 + z2)) = 44) := by
    rintro ⟨e1, e2, e3⟩
    have m1 := c1 e1
    have m2 := c2 e2
    have m3 := c3 e3
    have h := (List.all_eq_true.mp e44OK_true) _ m1
    have h' := (List.all_eq_true.mp h) _ m2
    simp only [Bool.or_eq_true, beq_iff_eq, Bool.not_eq_true', decide_eq_false_iff_not] at h'
    rcases h' with h' | h'
    · exact h12 (Facts.zl_inj h')
    · rw [zl_add] at m3; exact h' m3
  omega

/-- `f(6) = 20` for a 3-space: three independent vectors kill at most 20 ports -/
theorem card_three (z1 z2 z3 : V9) (h1 : z1 ≠ 0) (h2 : z2 ≠ 0) (h3 : z3 ≠ 0) (h12 : z1 ≠ z2) (h13 : z1 ≠ z3)
    (h23 : z2 ≠ z3) (h312 : z3 ≠ z1 + z2) :
    (univ.filter fun t : Fin 104 => labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0 ∧ labK t ⬝ᵥ z3 = 0).card ≤ 20 := by
  have hc := cap6OK_true
  obtain ⟨a, ha, ea⟩ := exists_lz z1
  obtain ⟨b, hb, eb⟩ := exists_lz z2
  obtain ⟨c, hcc, ec⟩ := exists_lz z3
  have zne : ∀ {n : ℕ} {z : V9}, n < 512 → lz n = zl z → z ≠ 0 → n ≠ 0 := by
    intro n z hn e hz h0; subst h0; rw [lz_zero] at e; exact hz (zl_zero e.symm)
  have xab : lz (a ^^^ b) = zl (z1 + z2) := by rw [lz_xor, ea, eb, zl_add]
  have xac : lz (a ^^^ c) = zl (z1 + z3) := by rw [lz_xor, ea, ec, zl_add]
  have xbc : lz (b ^^^ c) = zl (z2 + z3) := by rw [lz_xor, eb, ec, zl_add]
  have xabc : lz ((a ^^^ b) ^^^ c) = zl (z1 + z2 + z3) := by rw [lz_xor, xab, ec, ← zl_add]
  have s0 : ∀ {p q : V9}, p ≠ q → p + q ≠ 0 := fun hpq e => hpq (v9_eq_of_add e)
  have n123 : z1 + z2 + z3 ≠ 0 := fun e => h312 (v9_eq_of_add e).symm
  have hP := count7 labK z1 z2 z3
  have hQ := count7 rlab z1 z2 z3
  simp only [nOdd_card, nRm_card, Fintype.card_fin] at hP hQ
  rw [← ea, ← eb, ← ec, ← xab, ← xac, ← xbc, ← xabc] at hP hQ
  obtain ⟨g1, p1⟩ := fact56 hc ha (zne ha ea h1)
  obtain ⟨g2, p2⟩ := fact56 hc hb (zne hb eb h2)
  obtain ⟨g3, p3⟩ := fact56 hc hcc (zne hcc ec h3)
  obtain ⟨g4, p4⟩ := fact56 hc (x512 ha hb) (zne (x512 ha hb) xab (s0 h12))
  obtain ⟨g5, p5⟩ := fact56 hc (x512 ha hcc) (zne (x512 ha hcc) xac (s0 h13))
  obtain ⟨g6, p6⟩ := fact56 hc (x512 hb hcc) (zne (x512 hb hcc) xbc (s0 h23))
  obtain ⟨g7, p7⟩ := fact56 hc (x512 (x512 ha hb) hcc) (zne (x512 (x512 ha hb) hcc) xabc n123)
  have hsum : 400 ≤ nOdd (lz a) + nRm (lz a) + (nOdd (lz b) + nRm (lz b)) + (nOdd (lz c) + nRm (lz c)) +
      (nOdd (lz (a ^^^ b)) + nRm (lz (a ^^^ b))) + (nOdd (lz (a ^^^ c)) + nRm (lz (a ^^^ c))) +
      (nOdd (lz (b ^^^ c)) + nRm (lz (b ^^^ c))) + (nOdd (lz ((a ^^^ b) ^^^ c)) + nRm (lz ((a ^^^ b) ^^^ c))) := by
    by_contra hs
    exact no_plane3o 1 (Or.inl rfl) a b c (p1 (by omega)) (p2 (by omega)) (p3 (by omega)) (p4 (by omega))
      (p5 (by omega)) (p6 (by omega)) (p7 (by omega))
  omega

/-! ## Part R: integer rank `≤ 7` gives an even mod-2 normal -/

def Bm : Matrix (Fin 8) (Fin 8) ℤ := Matrix.of fun i k => (bZd.getD i []).getD k 0

def cZ (t : Fin 104) (i : Fin 8) : ℤ := (cZd.getD t []).getD i 0

set_option maxRecDepth 100000 in
theorem rZ_eq_aux : ∀ t : Fin 104, ∀ k : Fin 8, rZ t k = cZ t 0 * Bm 0 k + cZ t 1 * Bm 1 k + cZ t 2 * Bm 2 k +
    cZ t 3 * Bm 3 k + cZ t 4 * Bm 4 k + cZ t 5 * Bm 5 k + cZ t 6 * Bm 6 k + cZ t 7 * Bm 7 k := by
  decide +kernel

theorem rZ_eq (t : Fin 104) (k : Fin 8) : rZ t k = ∑ i, cZ t i * Bm i k := by
  rw [Fin.sum_univ_eight]; exact rZ_eq_aux t k

theorem Bm_low : ∀ i j : Fin 8, j < i → Bm i j = 0 := by
  intro i j h
  fin_cases i <;> fin_cases j <;> first | rfl | (simp [Fin.lt_def] at h) | omega

theorem Bm_tri : Bm.BlockTriangular id := by
  intro i j h
  exact Bm_low i j h

theorem Bm_det : Bm.det = 256 := by
  rw [Matrix.det_of_upperTriangular Bm_tri, Fin.prod_univ_eight]
  decide +kernel

/-- coordinates mod 2 -/
def cb (t : Fin 104) : Fin 8 → ZMod 2 := fun i => ((cZ t i : ℤ) : ZMod 2)

theorem minor_cb (F : Finset (Fin 104)) (hF : IntRk7 F) (g : Fin 8 → Fin 104) (hg : ∀ i, g i ∈ F) :
    (Matrix.of fun i j => cb (g i) j).det = 0 := by
  have h1 := hF g hg
  have e : (Matrix.of fun i k => rZ (g i) k) = (Matrix.of fun i j => cZ (g i) j) * Bm := by
    ext i k
    simp only [Matrix.of_apply, Matrix.mul_apply, rZ_eq]
  rw [e, Matrix.det_mul, Bm_det] at h1
  have h2 : (Matrix.of fun i j => cZ (g i) j).det = 0 := by
    rcases mul_eq_zero.mp h1 with h | h
    · exact h
    · norm_num at h
  have e2 : (Matrix.of fun i j => cb (g i) j) =
      (Matrix.of fun i j => cZ (g i) j).map (Int.castRingHom (ZMod 2)) := by
    ext i j
    simp [cb]
  rw [e2, ← RingHom.mapMatrix_apply, ← RingHom.map_det, h2, map_zero]

/-- the dot product with `v` as a linear functional on `K⁸` -/
def dotR {K : Type*} [Field K] (v : Fin 8 → K) : (Fin 8 → K) →ₗ[K] K where
  toFun x := v ⬝ᵥ x
  map_add' x y := dotProduct_add v x y
  map_smul' c x := by simp [dotProduct_smul]

/-- all `8 × 8` minors of the rows `w t` (`t ∈ S`) vanish ⇒ a non-zero vector is orthogonal to all of them -/
theorem perp_of_minors {K : Type*} [Field K] (w : Fin 104 → Fin 8 → K) (S : Finset (Fin 104))
    (h : ∀ g : Fin 8 → Fin 104, (∀ i, g i ∈ S) → (Matrix.of fun i j => w (g i) j).det = 0) :
    ∃ y : Fin 8 → K, y ≠ 0 ∧ ∀ t ∈ S, w t ⬝ᵥ y = 0 := by
  by_cases hr : rootRank w S ≤ 7
  · exact perp_of_rank w S hr
  exfalso
  set T : Set (Fin 8 → K) := Set.range fun t : S => w t with hT
  have hrk : rootRank w S = Module.finrank K (Submodule.span K T) := by
    unfold rootRank
    rw [Matrix.rank_eq_finrank_span_row]
    rfl
  have hle : Module.finrank K (Submodule.span K T) ≤ 8 := by
    have := Submodule.finrank_le (Submodule.span K T)
    rwa [Module.finrank_fin_fun] at this
  have htop : Submodule.span K T = ⊤ :=
    Submodule.eq_top_of_finrank_eq (by rw [Module.finrank_fin_fun]; omega)
  obtain ⟨b, hbT, hbspan, hbli⟩ := exists_linearIndependent K T
  have hbtop : Submodule.span K b = ⊤ := hbspan.trans htop
  have hbfin : b.Finite := (Set.finite_range _).subset hbT
  haveI : Fintype b := hbfin.fintype
  have hbcard : hbfin.toFinset.card = 8 := by
    have h1 := finrank_span_set_eq_card hbli
    rw [hbtop, finrank_top, Module.finrank_fin_fun] at h1
    rw [Set.toFinset_card] at h1
    first
    | exact h1.symm
    | (rw [Set.Finite.card_toFinset, Set.ncard_eq_toFinset_card']; convert h1.symm)
  let e : Fin 8 ≃ hbfin.toFinset := (Fintype.equivFinOfCardEq (by simp [hbcard])).symm
  have hrow : ∀ i : Fin 8, ∃ t : S, w t = (e i).1 := by
    intro i
    have h1 : (e i).1 ∈ b := (Set.Finite.mem_toFinset hbfin).mp (e i).2
    obtain ⟨t, ht⟩ := hbT h1
    exact ⟨t, ht⟩
  choose g hg using hrow
  have hdet := h (fun i => (g i).1) (fun i => (g i).2)
  obtain ⟨v, hv0, hMv⟩ := Matrix.exists_mulVec_eq_zero_iff.mpr hdet
  have hrv : ∀ i : Fin 8, (e i).1 ⬝ᵥ v = 0 := by
    intro i
    have := congrFun hMv i
    rw [← hg i]
    simpa [Matrix.mulVec, dotProduct] using this
  have hbv : ∀ x ∈ b, x ⬝ᵥ v = 0 := by
    intro x hx
    have hx' : x ∈ hbfin.toFinset := (Set.Finite.mem_toFinset hbfin).mpr hx
    have := hrv (e.symm ⟨x, hx'⟩)
    simpa using this
  have hker : Submodule.span K b ≤ LinearMap.ker (dotR v) := by
    rw [Submodule.span_le]
    intro x hx
    show v ⬝ᵥ x = 0
    rw [dotProduct_comm]
    exact hbv x hx
  rw [hbtop] at hker
  apply hv0
  funext m
  have := hker (Submodule.mem_top (x := Pi.single m 1))
  simpa [dotR, dotProduct_single] using this

def Am : Matrix (Fin 9) (Fin 8) (ZMod 2) := Matrix.of fun k j => (((aMd.getD k []).getD j 0 : ℕ) : ZMod 2)

def Nm : Matrix (Fin 8) (Fin 9) (ZMod 2) := Matrix.of fun i k => (((nMd.getD i []).getD k 0 : ℕ) : ZMod 2)

set_option maxRecDepth 100000 in
theorem labA_sum : ∀ t : Fin 104, ∀ j : Fin 8, ∑ k : Fin 9, labK t k * Am k j = cb t j := by
  simp only [Fin.sum_univ_succ, Fin.sum_univ_zero]
  decide +kernel

theorem labA (t : Fin 104) (j : Fin 8) : (labK t ᵥ* Am) j = cb t j := labA_sum t j

theorem jA_sum : ∀ j : Fin 8, ∑ k : Fin 9, jv k * Am k j = 0 := by
  simp only [Fin.sum_univ_succ, Fin.sum_univ_zero]
  decide +kernel

theorem jA (j : Fin 8) : (jv ᵥ* Am) j = 0 := jA_sum j

theorem NA_sum : ∀ i j : Fin 8, ∑ k : Fin 9, Nm i k * Am k j = if i = j then 1 else 0 := by
  simp only [Fin.sum_univ_succ, Fin.sum_univ_zero]
  decide +kernel

theorem NA : Nm * Am = 1 := by
  ext i j
  rw [Matrix.mul_apply, Matrix.one_apply]
  exact NA_sum i j

/-- **Reduction lemma**: a set of integer rank `≤ 7` has an even mod-2 normal -/
theorem mod2_of_intRk (F : Finset (Fin 104)) (hF : IntRk7 F) :
    ∃ s : V9, s ≠ 0 ∧ s ⬝ᵥ jv = 0 ∧ ∀ t ∈ F, labK t ⬝ᵥ s = 0 := by
  obtain ⟨y, hy, hyF⟩ := perp_of_minors cb F (minor_cb F hF)
  refine ⟨Am *ᵥ y, ?_, ?_, ?_⟩
  · intro h0
    apply hy
    have : Nm *ᵥ (Am *ᵥ y) = y := by rw [Matrix.mulVec_mulVec, NA, Matrix.one_mulVec]
    rw [← this, h0, Matrix.mulVec_zero]
  · rw [dotProduct_comm, Matrix.dotProduct_mulVec]
    have : jv ᵥ* Am = 0 := funext jA
    rw [this, zero_dotProduct]
  · intro t ht
    rw [Matrix.dotProduct_mulVec]
    have : labK t ᵥ* Am = cb t := funext (labA t)
    rw [this]
    exact hyF t ht

/-! ## Compatibility with a common exception set, mod 2 -/

/-- compatible planes with the common exception set `E` -/
def CompatE (E : Finset (Fin 104)) (a b c d : V9) : Prop :=
  ∃ F : Finset (Fin 104), IntRk7 F ∧ ∀ t, t ∉ Lv a b → t ∉ Lv c d → t ∈ F ∨ t ∈ E

/-- mod-2 compatibility: an even `s ≠ 0` whose slab is covered by the two live sets and `E` -/
def MC (E : Finset (Fin 104)) (a b c d : V9) : Prop :=
  ∃ s : V9, s ≠ 0 ∧ s ⬝ᵥ jv = 0 ∧ ∀ t, labK t ⬝ᵥ s ≠ 0 → t ∉ Lv a b → t ∉ Lv c d → t ∈ E

theorem mc_of_compat {E : Finset (Fin 104)} {a b c d : V9} (h : CompatE E a b c d) : MC E a b c d := by
  obtain ⟨F, hF, hcov⟩ := h
  obtain ⟨s, hs, he, hsF⟩ := mod2_of_intRk F hF
  refine ⟨s, hs, he, fun t hts ha hc => ?_⟩
  rcases hcov t ha hc with h | h
  · exact absurd (hsF t h) hts
  · exact h

/-! ## Mod-2 helpers -/

theorem z2 (x : ZMod 2) : x ≠ 0 ↔ x = 1 := by revert x; decide

theorem z2c (x : ZMod 2) : x = 0 ∨ x = 1 := by revert x; decide

theorem zz (p q : ZMod 2) : p = p + (q + q) := by revert p q; decide

theorem jv_jv : jv ⬝ᵥ jv = 1 := by
  first | decide +kernel | (simp [jv, dotProduct]; decide) | rfl

/-- parity of a 0/1 list -/
def pj (l : List ℕ) : Bool := (List.zipWith (· * ·) l (List.replicate 9 1)).sum % 2 == 1

theorem rep_getD_all : ∀ k : Fin 9, (List.replicate 9 1).getD k 0 = 1 := by decide

theorem rep_getD (k : Fin 9) : (List.replicate 9 1).getD k 0 = 1 := rep_getD_all k

theorem dot_jv (z : V9) : z ⬝ᵥ jv ≠ 0 ↔ pj (zl z) = true := by
  have h : z ⬝ᵥ jv = (((List.zipWith (· * ·) (zl z) (List.replicate 9 1)).sum : ℕ) : ZMod 2) := by
    rw [sumNat_eq _ _ 9 (zl_len z) (by simp)]
    simp only [dotProduct, jv, Nat.cast_sum, Nat.cast_mul, zl_getD, ZMod.natCast_zmod_val, rep_getD,
      Nat.cast_one]
  rw [h, Ne, ZMod.natCast_eq_zero_iff, pj]
  simp only [beq_iff_eq]
  omega

/-- **finite fact**: every slab of an even `s ≠ 0` has at least 48 ports -/
def evOK : Bool := lists9.all fun l => l == zero9 || pj l || decide (48 ≤ nOdd l)

set_option maxRecDepth 100000 in
theorem evOK_true : evOK = true := by decide +kernel

/-- the slab of `s` -/
def Sl (s : V9) : Finset (Fin 104) := univ.filter fun t => labK t ⬝ᵥ s ≠ 0

theorem slab48 {s : V9} (hs : s ≠ 0) (he : s ⬝ᵥ jv = 0) : 48 ≤ (Sl s).card := by
  have h := (List.all_eq_true.mp evOK_true) (zl s) (zl_mem s)
  have hne : ¬ zl s = zero9 := fun e => hs (zl_zero e)
  have hp : ¬ pj (zl s) = true := fun h' => (dot_jv s).mpr h' he
  simp only [Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq] at h
  unfold Sl
  rw [nOdd_card]
  rcases h with (h | h) | h
  · exact absurd h hne
  · exact absurd h hp
  · exact h

theorem slab_iff (s : V9) (t : Fin 104) : labK t ⬝ᵥ s ≠ 0 ↔ labK t ⬝ᵥ (s + jv) = 0 := by
  have h1 : labK t ⬝ᵥ jv = 1 := (z2 _).mp (labK_odd t)
  rw [dotProduct_add, h1]
  generalize labK t ⬝ᵥ s = x
  revert x; decide

theorem u_odd {s : V9} (he : s ⬝ᵥ jv = 0) : (s + jv) ⬝ᵥ jv ≠ 0 := by
  rw [add_dotProduct, he, jv_jv]; decide

theorem u_ne0 {s : V9} (he : s ⬝ᵥ jv = 0) : s + jv ≠ 0 := by
  intro h; apply u_odd he; rw [h, zero_dotProduct]

theorem u_nej {s : V9} (hs : s ≠ 0) : s + jv ≠ jv := by
  intro h; apply hs; simpa using h

/-! ## Points of a plane -/

/-- `x` is a non-zero point of the plane `⟨a, b⟩` -/
def IsPt (a b x : V9) : Prop := x ∈ ({a, b, a + b} : Finset V9)

theorem isPt_iff {a b x : V9} : IsPt a b x ↔ x = a ∨ x = b ∨ x = a + b := by
  simp [IsPt]

theorem lv_pt {a b x : V9} (hx : IsPt a b x) {t : Fin 104} (ht : t ∈ Lv a b) : labK t ⬝ᵥ x = 0 := by
  simp only [Lv, mem_filter, mem_univ, true_and] at ht
  rcases isPt_iff.mp hx with rfl | rfl | rfl
  · exact ht.1
  · exact ht.2
  · rw [dotProduct_add, ht.1, ht.2, add_zero]

/-- two distinct points determine the live set -/
theorem lv_two {a b x y : V9} (hx : IsPt a b x) (hy : IsPt a b y) (hxy : x ≠ y) (t : Fin 104) :
    t ∈ Lv a b ↔ labK t ⬝ᵥ x = 0 ∧ labK t ⬝ᵥ y = 0 := by
  simp only [Lv, mem_filter, mem_univ, true_and]
  have hxy' := hxy
  rcases isPt_iff.mp hx with ex | ex | ex <;> rcases isPt_iff.mp hy with ey | ey | ey <;>
    rw [ex, ey] at hxy' ⊢ <;> (try simp only [dotProduct_add]) <;>
    first
      | exact absurd rfl hxy'
      | (generalize labK t ⬝ᵥ a = p; generalize labK t ⬝ᵥ b = q; revert p q; decide)

theorem ne_add_left {a b : V9} (hb : b ≠ 0) : a ≠ a + b := by
  intro e; apply hb; funext k
  have := congrFun e k
  simp only [Pi.add_apply, Pi.zero_apply] at this ⊢
  revert this; generalize a k = p; generalize b k = q; revert p q; decide

theorem ne_add_right {a b : V9} (ha : a ≠ 0) : b ≠ a + b := by
  intro e; apply ha; funext k
  have := congrFun e k
  simp only [Pi.add_apply, Pi.zero_apply] at this ⊢
  revert this; generalize a k = p; generalize b k = q; revert p q; decide

/-! ## Types 0 and 1 -/

theorem not_type0 {E : Finset (Fin 104)} (hE : E.card ≤ 4) {a b c d s : V9}
    (hab : a ≠ 0 ∧ b ≠ 0 ∧ a ≠ b) (hcd : c ≠ 0 ∧ d ≠ 0 ∧ c ≠ d) (hs : s ≠ 0) (he : s ⬝ᵥ jv = 0)
    (hcov : ∀ t, labK t ⬝ᵥ s ≠ 0 → t ∉ Lv a b → t ∉ Lv c d → t ∈ E)
    (h1 : ¬ IsPt a b (s + jv)) (h2 : ¬ IsPt c d (s + jv)) : False := by
  set u := s + jv with hu
  have hu0 : u ≠ 0 := u_ne0 he
  rw [isPt_iff] at h1 h2
  push_neg at h1 h2
  have hsub : Sl s ⊆ (univ.filter fun t : Fin 104 => labK t ⬝ᵥ a = 0 ∧ labK t ⬝ᵥ b = 0 ∧ labK t ⬝ᵥ u = 0) ∪
      (univ.filter fun t : Fin 104 => labK t ⬝ᵥ c = 0 ∧ labK t ⬝ᵥ d = 0 ∧ labK t ⬝ᵥ u = 0) ∪ E := by
    intro t ht
    simp only [Sl, mem_filter, mem_univ, true_and] at ht
    have htu : labK t ⬝ᵥ u = 0 := (slab_iff s t).mp ht
    by_cases hA : t ∈ Lv a b
    · simp only [Lv, mem_filter, mem_univ, true_and] at hA
      exact mem_union_left _ (mem_union_left _ (by simp [hA.1, hA.2, htu]))
    by_cases hC : t ∈ Lv c d
    · simp only [Lv, mem_filter, mem_univ, true_and] at hC
      exact mem_union_left _ (mem_union_right _ (by simp [hC.1, hC.2, htu]))
    exact mem_union_right _ (hcov t ht hA hC)
  have k1 := card_three a b u hab.1 hab.2.1 hu0 hab.2.2 (Ne.symm h1.1) (Ne.symm h1.2.1) h1.2.2
  have k2 := card_three c d u hcd.1 hcd.2.1 hu0 hcd.2.2 (Ne.symm h2.1) (Ne.symm h2.2.1) h2.2.2
  have h48 := slab48 hs he
  have hc := card_le_card hsub
  have hu1 := card_union_le ((univ.filter fun t : Fin 104 => labK t ⬝ᵥ a = 0 ∧ labK t ⬝ᵥ b = 0 ∧
      labK t ⬝ᵥ u = 0) ∪ (univ.filter fun t : Fin 104 => labK t ⬝ᵥ c = 0 ∧ labK t ⬝ᵥ d = 0 ∧
      labK t ⬝ᵥ u = 0)) E
  have hu2 := card_union_le (univ.filter fun t : Fin 104 => labK t ⬝ᵥ a = 0 ∧ labK t ⬝ᵥ b = 0 ∧
      labK t ⬝ᵥ u = 0) (univ.filter fun t : Fin 104 => labK t ⬝ᵥ c = 0 ∧ labK t ⬝ᵥ d = 0 ∧ labK t ⬝ᵥ u = 0)
  omega

/-! ### The type-1 table -/

/-- the mask of a list of ports -/
def lmk (l : List ℕ) : ℕ := l.foldr (fun s a => a ||| 2 ^ s) 0

theorem lmk_bit (l : List ℕ) (s : ℕ) : (lmk l).testBit s = true ↔ s ∈ l := by
  induction l with
  | nil => simp [lmk]
  | cons a l ih =>
    show (lmk l ||| 2 ^ a).testBit s = true ↔ s ∈ a :: l
    rw [Nat.testBit_or, Bool.or_eq_true, ih, Nat.testBit_two_pow, decide_eq_true_eq, List.mem_cons]
    exact ⟨fun h => h.elim Or.inr (fun h => Or.inl h.symm), fun h => h.elim (fun h => Or.inr h.symm) Or.inl⟩

/-- ports with odd product against the label number `n` -/
def ppm (n : ℕ) : ℕ := lmk ((List.range 104).filter fun t => BForm.E8.par t (lz n))

def pmP : List (ℕ × ℕ) := (List.range 512).map fun n => (n, ppm n)

theorem ppm_bit (n : ℕ) (t : Fin 104) {z : V9} (hz : lz n = zl z) : (ppm n).testBit t = true ↔ labK t ⬝ᵥ z ≠ 0 := by
  rw [ppm, lmk_bit, List.mem_filter, List.mem_range, hz]
  have := lab_dot t z
  exact ⟨fun h => this.mpr h.2, fun h => ⟨t.2, this.mp h⟩⟩

theorem mem_pmP {n : ℕ} (hn : n < 512) : (n, ppm n) ∈ pmP := List.mem_map.mpr ⟨n, List.mem_range.mpr hn, rfl⟩

/-- the ports of a mask -/
def bitsY (m : ℕ) : List ℕ := (List.range 104).filter fun t => m.testBit t

theorem bitsY_count (m : ℕ) (q : ℕ → Bool) :
    (bitsY m).countP q = (univ.filter fun t : Fin 104 => m.testBit t = true ∧ q t = true).card := by
  rw [bitsY, List.countP_filter, countP_range]
  congr 1
  ext t
  simp only [mem_filter, mem_univ, true_and, Bool.and_eq_true]
  tauto

theorem bitsY_len (m : ℕ) : (bitsY m).length = (univ.filter fun t : Fin 104 => m.testBit t = true).card := by
  have := bitsY_count m (fun _ => true)
  rw [List.countP_true] at this
  rw [this]
  congr 1
  ext t
  simp

theorem mem_bitsY {m t : ℕ} : t ∈ bitsY m ↔ t < 104 ∧ m.testBit t = true := by
  simp [bitsY]

/-- integer dot product of two port roots -/
def dZ (x z : ℕ) : ℤ := (List.zipWith (· * ·) (r8 x) (r8 z)).sum

/-- pairwise non-orthogonal -/
def clq (L : List ℕ) : Bool := L.all fun x => L.all fun z => x == z || dZ x z != 0

theorem sumInt_eq (a b : List ℤ) (n : ℕ) (ha : a.length = n) (hb : b.length = n) :
    (List.zipWith (· * ·) a b).sum = ∑ k : Fin n, a.getD k 0 * b.getD k 0 := by
  induction a generalizing b n with
  | nil => subst ha; simp
  | cons x a ih =>
    cases b with
    | nil => simp at hb; subst hb; simp at ha
    | cons y b =>
      cases n with
      | zero => simp at ha
      | succ n =>
        simp only [List.length_cons, add_left_inj] at ha hb
        rw [Fin.sum_univ_succ]
        have := ih b n ha hb
        simp only [List.zipWith_cons_cons, List.sum_cons] at this ⊢
        rw [this]; simp

theorem r8_len : ∀ p : Fin 104, (r8 p).length = 8 := by decide +kernel

theorem dZ_eq (p q : Fin 104) : rZ p ⬝ᵥ rZ q = dZ p q := by
  rw [dZ, sumInt_eq _ _ 8 (r8_len p) (r8_len q)]
  rfl

/-- the type-1 check for an odd `u` (number `nu`, mask `pu`) and a second point `a` of the plane through `u` -/
def t1At (nu pu pa : ℕ) : Bool :=
  let YL := bitsY (pa ^^^ (pa &&& pu))
  decide (24 < YL.length) || pmP.all fun pc => pc.1 == 0 || pc.1 == nu ||
    decide (4 < YL.countP fun t => pc.2.testBit t) || pmP.all fun pd => pd.1 == 0 || pd.1 == nu ||
      pd.1 == pc.1 || pd.1 == (pc.1 ^^^ nu) || decide (4 < YL.countP fun t => pd.2.testBit t) ||
      (decide (4 < (YL.filter fun t => pc.2.testBit t || pd.2.testBit t).length) ||
        !clq (YL.filter fun t => pc.2.testBit t || pd.2.testBit t))

/-- **finite fact (type 1)**, checked by `#eval` (`LPCheck.lean`) and Python (`lphand/t1x_check.py`) -/
def t1xOK : Bool :=
  pmP.all fun pu => !pj (lz pu.1) || pu.1 == 511 || pmP.all fun pa => pa.1 == 0 || pa.1 == pu.1 ||
    t1At pu.1 pu.2 pa.2

theorem ybit (pa pu t : ℕ) : (pa ^^^ (pa &&& pu)).testBit t = (pa.testBit t && !pu.testBit t) := by
  rw [Nat.testBit_xor, Nat.testBit_land]
  cases pa.testBit t <;> cases pu.testBit t <;> rfl

theorem lz_jv : lz 511 = zl jv := by decide +kernel

theorem andnot (x y : Bool) : (x && !y) = true ↔ x = true ∧ ¬ y = true := by cases x <;> cases y <;> decide

theorem not_type1 (ht : t1xOK = true) {E : Finset (Fin 104)} (hE : E.card ≤ 4)
    (hcl : ∀ x ∈ E, ∀ z ∈ E, x ≠ z → rZ x ⬝ᵥ rZ z ≠ 0) {a b c d s : V9}
    (hab : a ≠ 0 ∧ b ≠ 0 ∧ a ≠ b) (hcd : c ≠ 0 ∧ d ≠ 0 ∧ c ≠ d) (hs : s ≠ 0) (he : s ⬝ᵥ jv = 0)
    (hcov : ∀ t, labK t ⬝ᵥ s ≠ 0 → t ∉ Lv a b → t ∉ Lv c d → t ∈ E)
    (h1 : IsPt a b (s + jv)) (h2 : ¬ IsPt c d (s + jv)) : False := by
  set u := s + jv with hu
  have hu0 : u ≠ 0 := u_ne0 he
  have huj : u ≠ jv := u_nej hs
  have huo : u ⬝ᵥ jv ≠ 0 := u_odd he
  rw [isPt_iff] at h2
  push_neg at h2
  -- the second point `a'` of the plane through `u`
  obtain ⟨a', ha'pt, ha'u, ha'0⟩ : ∃ a', IsPt a b a' ∧ a' ≠ u ∧ a' ≠ 0 := by
    rcases isPt_iff.mp h1 with e | e | e
    · exact ⟨b, isPt_iff.mpr (Or.inr (Or.inl rfl)), fun h => hab.2.2 (e.symm.trans h.symm), hab.2.1⟩
    · exact ⟨a, isPt_iff.mpr (Or.inl rfl), fun h => hab.2.2 (h.trans e), hab.1⟩
    · exact ⟨a, isPt_iff.mpr (Or.inl rfl), fun h => ne_add_left hab.2.1 (h.trans e), hab.1⟩
  have hlv : ∀ t, t ∈ Lv a b ↔ labK t ⬝ᵥ u = 0 ∧ labK t ⬝ᵥ a' = 0 :=
    lv_two h1 ha'pt (Ne.symm ha'u)
  -- the uncovered region `Y = {t : t·u = 0, t·a' = 1}` lies in `L(c, d) ∪ E`
  have hY : ∀ t : Fin 104, labK t ⬝ᵥ u = 0 → labK t ⬝ᵥ a' ≠ 0 → t ∈ Lv c d ∨ t ∈ E := by
    intro t htu hta
    have hts : labK t ⬝ᵥ s ≠ 0 := (slab_iff s t).mpr htu
    have hA : t ∉ Lv a b := fun h => hta ((hlv t).mp h).2
    by_cases hC : t ∈ Lv c d
    · exact Or.inl hC
    · exact Or.inr (hcov t hts hA hC)
  obtain ⟨nu, hnu, eu⟩ := exists_lz u
  obtain ⟨na, hna, ea⟩ := exists_lz a'
  obtain ⟨nc, hnc, ec⟩ := exists_lz c
  obtain ⟨nd, hnd, ed⟩ := exists_lz d
  have neq : ∀ {n m : ℕ} {x y : V9}, lz n = zl x → lz m = zl y → x ≠ y → n ≠ m := by
    intro n m x y hx hy hxy e; subst e; exact hxy (Facts.zl_inj (hx.symm.trans hy))
  have n0 : ∀ {n : ℕ} {x : V9}, lz n = zl x → x ≠ 0 → n ≠ 0 := by
    intro n x hx h0 e; subst e; rw [lz_zero] at hx; exact h0 (zl_zero hx.symm)
  have hYbit : ∀ t : Fin 104, (ppm na ^^^ (ppm na &&& ppm nu)).testBit t = true ↔
      labK t ⬝ᵥ a' ≠ 0 ∧ labK t ⬝ᵥ u = 0 := by
    intro t
    simp only [ybit, andnot, ppm_bit na t ea, ppm_bit nu t eu, ne_eq, not_not]
  -- unpack the table
  have hu1 := (List.all_eq_true.mp ht) (nu, ppm nu) (mem_pmP hnu)
  simp only [Bool.or_eq_true, Bool.not_eq_true', beq_iff_eq] at hu1
  have hpj : pj (lz nu) = true := by rw [eu]; exact (dot_jv u).mp huo
  have hn511 : nu ≠ 511 := neq eu lz_jv huj
  rcases hu1 with (hu1 | hu1) | hu1
  · rw [hpj] at hu1; exact absurd hu1 (by decide)
  · exact hn511 hu1
  have ha1 := (List.all_eq_true.mp hu1) (na, ppm na) (mem_pmP hna)
  simp only [Bool.or_eq_true, beq_iff_eq] at ha1
  rcases ha1 with (ha1 | ha1) | ha1
  · exact n0 ea ha'0 ha1
  · exact neq ea eu ha'u ha1
  unfold t1At at ha1
  simp only [Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq] at ha1
  set YL := bitsY (ppm na ^^^ (ppm na &&& ppm nu)) with hYL
  have hcnt : ∀ q : ℕ → Bool, YL.countP q =
      (univ.filter fun t : Fin 104 => (labK t ⬝ᵥ a' ≠ 0 ∧ labK t ⬝ᵥ u = 0) ∧ q t = true).card := by
    intro q
    rw [hYL, bitsY_count]
    refine congrArg Finset.card ?_
    ext t
    simp only [mem_filter, mem_univ, true_and, hYbit]
  -- `|Y| ≤ 24`
  have hYlen : ¬ 24 < YL.length := by
    have e1 := hcnt (fun _ => true)
    rw [List.countP_true] at e1
    beta_reduce at e1
    have hsub : (univ.filter fun t : Fin 104 => (labK t ⬝ᵥ a' ≠ 0 ∧ labK t ⬝ᵥ u = 0) ∧ true = true) ⊆
        (univ.filter fun t : Fin 104 => labK t ⬝ᵥ c = 0 ∧ labK t ⬝ᵥ d = 0 ∧ labK t ⬝ᵥ u = 0) ∪ E := by
      intro t ht
      simp only [mem_filter, mem_univ, true_and, eq_self_iff_true, and_true] at ht
      rcases hY t ht.2 ht.1 with h | h
      · simp only [Lv, mem_filter, mem_univ, true_and] at h
        exact mem_union_left _ (by simp [h.1, h.2, ht.2])
      · exact mem_union_right _ h
    have k := card_three c d u hcd.1 hcd.2.1 hu0 hcd.2.2 (Ne.symm h2.1) (Ne.symm h2.2.1) h2.2.2
    have := card_le_card hsub
    have := card_union_le (univ.filter fun t : Fin 104 => labK t ⬝ᵥ c = 0 ∧ labK t ⬝ᵥ d = 0 ∧
      labK t ⬝ᵥ u = 0) E
    omega
  -- a non-zero `z` that is odd on some uncovered ports: those ports lie in `E`
  have hcz : ∀ (n : ℕ) (z : V9), lz n = zl z → (∀ t : Fin 104, labK t ⬝ᵥ z ≠ 0 → t ∉ Lv c d) →
      ¬ 4 < YL.countP (fun t => (ppm n).testBit t) := by
    intro n z hz hzc
    have e := hcnt (fun t => (ppm n).testBit t)
    beta_reduce at e
    have hsub : (univ.filter fun t : Fin 104 => (labK t ⬝ᵥ a' ≠ 0 ∧ labK t ⬝ᵥ u = 0) ∧
        (ppm n).testBit t = true) ⊆ E := by
      intro t ht
      simp only [mem_filter, mem_univ, true_and] at ht
      rcases hY t ht.1.2 ht.1.1 with h | h
      · exact absurd h (hzc t ((ppm_bit n t hz).mp ht.2))
      · exact h
    have := card_le_card hsub
    omega
  have hcC : ∀ t : Fin 104, labK t ⬝ᵥ c ≠ 0 → t ∉ Lv c d := by
    intro t h hl; simp only [Lv, mem_filter, mem_univ, true_and] at hl; exact h hl.1
  have hdC : ∀ t : Fin 104, labK t ⬝ᵥ d ≠ 0 → t ∉ Lv c d := by
    intro t h hl; simp only [Lv, mem_filter, mem_univ, true_and] at hl; exact h hl.2
  rcases ha1 with ha1 | ha1
  · exact hYlen ha1
  have hc1 := (List.all_eq_true.mp ha1) (nc, ppm nc) (mem_pmP hnc)
  simp only [Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq] at hc1
  rcases hc1 with ((hc1 | hc1) | hc1) | hc1
  · exact n0 ec hcd.1 hc1
  · exact neq ec eu (Ne.symm h2.1) hc1
  · exact hcz nc c ec hcC hc1
  have hd1 := (List.all_eq_true.mp hc1) (nd, ppm nd) (mem_pmP hnd)
  simp only [Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq, Bool.not_eq_true'] at hd1
  have hxor : lz (nc ^^^ nu) = zl (c + u) := by rw [lz_xor, ec, eu, ← zl_add]
  have hdcu : d ≠ c + u := by
    intro e
    apply h2.2.2
    rw [e]
    funext k
    simp only [Pi.add_apply]
    generalize c k = p; generalize u k = q; revert p q; decide
  rcases hd1 with (((((hd1 | hd1) | hd1) | hd1) | hd1) | hd1 | hd1)
  · exact n0 ed hcd.2.1 hd1
  · exact neq ed eu (Ne.symm h2.2.1) hd1
  · exact neq ed ec (Ne.symm hcd.2.2) hd1
  · exact neq ed hxor hdcu hd1
  · exact hcz nd d ed hdC hd1
  · -- `|U| ≤ 4`
    have e2 := hcnt (fun t => (ppm nc).testBit t || (ppm nd).testBit t)
    rw [List.countP_eq_length_filter] at e2
    beta_reduce at e2
    have hsub : (univ.filter fun t : Fin 104 => (labK t ⬝ᵥ a' ≠ 0 ∧ labK t ⬝ᵥ u = 0) ∧
        ((ppm nc).testBit t || (ppm nd).testBit t) = true) ⊆ E := by
      intro t ht
      simp only [mem_filter, mem_univ, true_and, Bool.or_eq_true] at ht
      rcases hY t ht.1.2 ht.1.1 with h | h
      · rcases ht.2 with h' | h'
        · exact absurd h (hcC t ((ppm_bit nc t ec).mp h'))
        · exact absurd h (hdC t ((ppm_bit nd t ed).mp h'))
      · exact h
    have := card_le_card hsub
    omega
  · -- `U` is a clique
    have hcl' : clq (YL.filter fun t => (ppm nc).testBit t || (ppm nd).testBit t) = true := by
      unfold clq
      rw [List.all_eq_true]
      intro x hx
      rw [List.all_eq_true]
      intro z hz
      simp only [Bool.or_eq_true, beq_iff_eq, bne_iff_ne, ne_eq]
      by_cases hxz : x = z
      · exact Or.inl hxz
      right
      have mE : ∀ y ∈ YL.filter (fun t => (ppm nc).testBit t || (ppm nd).testBit t),
          ∃ hy : y < 104, (⟨y, hy⟩ : Fin 104) ∈ E := by
        intro y hy
        rw [List.mem_filter, hYL, mem_bitsY] at hy
        obtain ⟨⟨hy1, hy2⟩, hy3⟩ := hy
        refine ⟨hy1, ?_⟩
        have hyb := (hYbit ⟨y, hy1⟩).mp hy2
        rcases hY ⟨y, hy1⟩ hyb.2 hyb.1 with h | h
        · simp only [Bool.or_eq_true] at hy3
          rcases hy3 with h' | h'
          · exact absurd h (hcC _ ((ppm_bit nc ⟨y, hy1⟩ ec).mp h'))
          · exact absurd h (hdC _ ((ppm_bit nd ⟨y, hy1⟩ ed).mp h'))
        · exact h
      obtain ⟨hx1, hxE⟩ := mE x hx
      obtain ⟨hz1, hzE⟩ := mE z hz
      have hne : (⟨x, hx1⟩ : Fin 104) ≠ ⟨z, hz1⟩ := fun e => hxz (congrArg Fin.val e)
      have := hcl _ hxE _ hzE hne
      rw [dZ_eq] at this
      exact this
    have := hcl'.symm.trans hd1
    exact absurd this (by decide)

/-! ## Odd points and the star -/

/-- the odd points of the plane `⟨a, b⟩` -/
def Od (a b : V9) : Finset V9 := ({a, b, a + b} : Finset V9).filter fun y => y ⬝ᵥ jv ≠ 0

theorem mem_Od {a b x : V9} : x ∈ Od a b ↔ IsPt a b x ∧ x ⬝ᵥ jv ≠ 0 := by
  simp [Od, IsPt]

theorem Od_card {a b x : V9} (hab : a ≠ 0 ∧ b ≠ 0 ∧ a ≠ b) (hx : x ∈ Od a b) : (Od a b).card = 2 := by
  have h1 : a ≠ a + b := ne_add_left hab.2.1
  have h2 : b ≠ a + b := ne_add_right hab.1
  have hs : (a + b) ⬝ᵥ jv = a ⬝ᵥ jv + b ⬝ᵥ jv := add_dotProduct _ _ _
  have hx' := mem_Od.mp hx
  rcases z2c (a ⬝ᵥ jv) with pa | pa <;> rcases z2c (b ⬝ᵥ jv) with pb | pb
  · exfalso
    rcases isPt_iff.mp hx'.1 with e | e | e <;> rw [e] at hx'
    · exact hx'.2 pa
    · exact hx'.2 pb
    · exact hx'.2 (by rw [hs, pa, pb, add_zero])
  · have e : Od a b = {b, a + b} := by
      ext y
      rw [mem_Od, isPt_iff]
      simp only [mem_insert, mem_singleton]
      constructor
      · rintro ⟨h | h | h, hy⟩
        · exact (hy (by rw [h]; exact pa)).elim
        · exact Or.inl h
        · exact Or.inr h
      · rintro (h | h)
        · exact ⟨Or.inr (Or.inl h), by rw [h, pb]; decide⟩
        · exact ⟨Or.inr (Or.inr h), by rw [h, hs, pa, pb]; decide⟩
    rw [e, card_pair h2]
  · have e : Od a b = {a, a + b} := by
      ext y
      rw [mem_Od, isPt_iff]
      simp only [mem_insert, mem_singleton]
      constructor
      · rintro ⟨h | h | h, hy⟩
        · exact Or.inl h
        · exact (hy (by rw [h]; exact pb)).elim
        · exact Or.inr h
      · rintro (h | h)
        · exact ⟨Or.inl h, by rw [h, pa]; decide⟩
        · exact ⟨Or.inr (Or.inr h), by rw [h, hs, pa, pb]; decide⟩
    rw [e, card_pair h1]
  · have e : Od a b = {a, b} := by
      ext y
      rw [mem_Od, isPt_iff]
      simp only [mem_insert, mem_singleton]
      constructor
      · rintro ⟨h | h | h, hy⟩
        · exact Or.inl h
        · exact Or.inr h
        · exact (hy (by rw [h, hs, pa, pb]; decide)).elim
      · rintro (h | h)
        · exact ⟨Or.inl h, by rw [h, pa]; decide⟩
        · exact ⟨Or.inr (Or.inl h), by rw [h, pb]; decide⟩
    rw [e, card_pair hab.2.2]

theorem two_of_mem {α : Type*} [DecidableEq α] {S : Finset α} (h : S.card = 2) {x : α} (hx : x ∈ S) :
    ∃ y, y ≠ x ∧ S = {x, y} := by
  obtain ⟨p, q, hpq, e⟩ := Finset.card_eq_two.mp h
  rw [e] at hx
  simp only [mem_insert, mem_singleton] at hx
  rcases hx with rfl | rfl
  · exact ⟨q, Ne.symm hpq, e⟩
  · exact ⟨p, hpq, by rw [e, Finset.pair_comm]⟩

theorem eq_of_two {α : Type*} [DecidableEq α] {S T : Finset α} (hS : S.card = 2) (hT : T.card = 2) {x y : α}
    (hxy : x ≠ y) (hxS : x ∈ S) (hyS : y ∈ S) (hxT : x ∈ T) (hyT : y ∈ T) : S = T := by
  have s1 : ({x, y} : Finset α) ⊆ S := by
    intro z hz
    simp only [mem_insert, mem_singleton] at hz
    rcases hz with rfl | rfl <;> assumption
  have s2 : ({x, y} : Finset α) ⊆ T := by
    intro z hz
    simp only [mem_insert, mem_singleton] at hz
    rcases hz with rfl | rfl <;> assumption
  have e1 : ({x, y} : Finset α) = S := Finset.eq_of_subset_of_card_le s1 (by rw [hS, card_pair hxy])
  have e2 : ({x, y} : Finset α) = T := Finset.eq_of_subset_of_card_le s2 (by rw [hT, card_pair hxy])
  rw [← e1, e2]

theorem third : ∀ i j : Fin 6, ∃ k : Fin 6, k ≠ 0 ∧ k ≠ i ∧ k ≠ j := by decide

/-- six distinct pairwise intersecting 2-sets have a common point -/
theorem star6 {α : Type*} [DecidableEq α] (O : Fin 6 → Finset α) (hc : ∀ k, (O k).card = 2)
    (hd : ∀ k l, k ≠ l → O k ≠ O l) (hi : ∀ k l, ∃ x, x ∈ O k ∧ x ∈ O l) : ∃ u, ∀ k, u ∈ O k := by
  obtain ⟨p, q, hpq, e0⟩ := Finset.card_eq_two.mp (hc 0)
  have hp0 : p ∈ O 0 := by rw [e0]; simp
  have hq0 : q ∈ O 0 := by rw [e0]; simp
  by_contra hno
  push_neg at hno
  obtain ⟨i, hpi⟩ := hno p
  obtain ⟨j, hqj⟩ := hno q
  have hqi : q ∈ O i := by
    obtain ⟨x, hx0, hxi⟩ := hi 0 i
    rw [e0] at hx0
    simp only [mem_insert, mem_singleton] at hx0
    rcases hx0 with rfl | rfl
    · exact absurd hxi hpi
    · exact hxi
  have hpj : p ∈ O j := by
    obtain ⟨x, hx0, hxj⟩ := hi 0 j
    rw [e0] at hx0
    simp only [mem_insert, mem_singleton] at hx0
    rcases hx0 with rfl | rfl
    · exact hxj
    · exact absurd hxj hqj
  obtain ⟨r, hrq, ei⟩ := two_of_mem (hc i) hqi
  have hrp : r ≠ p := fun e => hpi (by rw [ei, e]; simp)
  have hrj : r ∈ O j := by
    obtain ⟨x, hxj, hxi⟩ := hi j i
    rw [ei] at hxi
    simp only [mem_insert, mem_singleton] at hxi
    rcases hxi with rfl | rfl
    · exact absurd hxj hqj
    · exact hxj
  have hi0 : i ≠ 0 := fun e => hpi (e ▸ hp0)
  have hj0 : j ≠ 0 := fun e => hqj (e ▸ hq0)
  have hij : i ≠ j := fun e => hqj (e ▸ hqi)
  have hri : r ∈ O i := by rw [ei]; simp
  obtain ⟨k, hk0, hki, hkj⟩ := third i j
  obtain ⟨w1, hw1k, hw10⟩ := hi k 0
  obtain ⟨w2, hw2k, hw2i⟩ := hi k i
  obtain ⟨w3, hw3k, hw3j⟩ := hi k j
  rw [e0] at hw10
  rw [ei] at hw2i
  simp only [mem_insert, mem_singleton] at hw10 hw2i
  have hpjj : O j = {p, r} := eq_of_two (hc j) (by rw [card_pair (Ne.symm hrp)]) (Ne.symm hrp) hpj hrj
    (by simp) (by simp)
  rw [hpjj] at hw3j
  simp only [mem_insert, mem_singleton] at hw3j
  rcases hw10 with rfl | rfl
  · rcases hw2i with rfl | rfl
    · exact hd k 0 hk0 (eq_of_two (hc k) (hc 0) hpq hw1k hw2k hp0 hq0)
    · exact hd k j hkj (eq_of_two (hc k) (hc j) (Ne.symm hrp) hw1k hw2k hpj hrj)
  · rcases hw3j with rfl | rfl
    · exact hd k 0 hk0 (eq_of_two (hc k) (hc 0) hpq hw3k hw1k hp0 hq0)
    · exact hd k i hki (eq_of_two (hc k) (hc i) (Ne.symm hrq) hw1k hw3k hqi hri)

theorem card_sd (X B : Finset (Fin 104)) : X.card ≤ (X \ B).card + B.card := by
  calc X.card ≤ ((X \ B) ∪ B).card := Finset.card_le_card (fun t ht => by
          by_cases h : t ∈ B
          · exact Finset.mem_union_right _ h
          · exact Finset.mem_union_left _ (Finset.mem_sdiff.mpr ⟨ht, h⟩))
    _ ≤ _ := Finset.card_union_le _ _

/-! ## No six pairwise mod-2 compatible planes -/

theorem no_six_mod2 (ht : t1xOK = true) (E : Finset (Fin 104)) (hE : E.card ≤ 4)
    (hcl : ∀ x ∈ E, ∀ z ∈ E, x ≠ z → rZ x ⬝ᵥ rZ z ≠ 0) (a b : Fin 6 → V9)
    (hnd : ∀ k, a k ≠ 0 ∧ b k ≠ 0 ∧ a k ≠ b k) (hmc : ∀ k l, k ≠ l → MC E (a k) (b k) (a l) (b l)) : False := by
  simp only [MC] at hmc
  choose! sf hsf using hmc
  -- every pair has its `u` in both planes
  have hboth : ∀ k l, k ≠ l → IsPt (a k) (b k) (sf k l + jv) ∧ IsPt (a l) (b l) (sf k l + jv) := by
    intro k l hkl
    obtain ⟨hs, he, hcov⟩ := hsf k l hkl
    have hcov' : ∀ t, labK t ⬝ᵥ sf k l ≠ 0 → t ∉ Lv (a l) (b l) → t ∉ Lv (a k) (b k) → t ∈ E :=
      fun t h1 h2 h3 => hcov t h1 h3 h2
    by_cases h1 : IsPt (a k) (b k) (sf k l + jv) <;> by_cases h2 : IsPt (a l) (b l) (sf k l + jv)
    · exact ⟨h1, h2⟩
    · exact (not_type1 ht hE hcl (hnd k) (hnd l) hs he hcov h1 h2).elim
    · exact (not_type1 ht hE hcl (hnd l) (hnd k) hs he hcov' h2 h1).elim
    · exact (not_type0 hE (hnd k) (hnd l) hs he hcov h1 h2).elim
  have hodd : ∀ k l, k ≠ l → sf k l + jv ∈ Od (a k) (b k) ∧ sf k l + jv ∈ Od (a l) (b l) := by
    intro k l hkl
    have ho := u_odd (hsf k l hkl).2.1
    exact ⟨mem_Od.mpr ⟨(hboth k l hkl).1, ho⟩, mem_Od.mpr ⟨(hboth k l hkl).2, ho⟩⟩
  have hnext : ∀ k : Fin 6, ∃ l, k ≠ l := fun k => ⟨k + 1, by revert k; decide⟩
  have hc : ∀ k, (Od (a k) (b k)).card = 2 := by
    intro k
    obtain ⟨l, hkl⟩ := hnext k
    exact Od_card (hnd k) (hodd k l hkl).1
  -- equal odd points force equal live sets: impossible
  have hd : ∀ k l, k ≠ l → Od (a k) (b k) ≠ Od (a l) (b l) := by
    intro k l hkl e
    obtain ⟨hs, he, hcov⟩ := hsf k l hkl
    obtain ⟨x, y, hxy, exy⟩ := Finset.card_eq_two.mp (hc k)
    have hxk : x ∈ Od (a k) (b k) := by rw [exy]; simp
    have hyk : y ∈ Od (a k) (b k) := by rw [exy]; simp
    have hxl : x ∈ Od (a l) (b l) := e ▸ hxk
    have hyl : y ∈ Od (a l) (b l) := e ▸ hyk
    have hLv : ∀ t, t ∈ Lv (a l) (b l) → t ∈ Lv (a k) (b k) := by
      intro t htl
      rw [lv_two (mem_Od.mp hxk).1 (mem_Od.mp hyk).1 hxy]
      exact (lv_two (mem_Od.mp hxl).1 (mem_Od.mp hyl).1 hxy t).mp htl
    have hsub : Sl (sf k l) ⊆ Lv (a k) (b k) ∪ E := by
      intro t ht
      simp only [Sl, mem_filter, mem_univ, true_and] at ht
      by_cases hk : t ∈ Lv (a k) (b k)
      · exact mem_union_left _ hk
      · exact mem_union_right _ (hcov t ht hk (fun h => hk (hLv t h)))
    have h48 := slab48 hs he
    have h36 := card_two (a k) (b k) (hnd k).1 (hnd k).2.1 (hnd k).2.2
    have := card_le_card hsub
    have := card_union_le (Lv (a k) (b k)) E
    have e36 : (Lv (a k) (b k)).card ≤ 36 := h36
    omega
  have hi : ∀ k l, ∃ x, x ∈ Od (a k) (b k) ∧ x ∈ Od (a l) (b l) := by
    intro k l
    by_cases hkl : k = l
    · rw [← hkl]
      obtain ⟨m, hm⟩ := hnext k
      exact ⟨_, (hodd k m hm).1, (hodd k m hm).1⟩
    · exact ⟨_, (hodd k l hkl).1, (hodd k l hkl).2⟩
  obtain ⟨u0, hu0⟩ := star6 (fun k => Od (a k) (b k)) hc hd hi
  -- all pairs use the slab of `s0 = u0 + j`
  have hsame : ∀ k l, k ≠ l → sf k l = u0 + jv := by
    intro k l hkl
    have hu := hodd k l hkl
    by_contra hne
    have hne' : sf k l + jv ≠ u0 := by
      intro e; apply hne; rw [← e, add_assoc]
      funext m
      simp only [Pi.add_apply]
      exact zz _ _
    exact hd k l hkl (eq_of_two (hc k) (hc l) hne' hu.1 (hu0 k) hu.2 (hu0 l))
  obtain ⟨hs0, he0, -⟩ := hsf 0 1 (by decide)
  rw [hsame 0 1 (by decide)] at hs0 he0
  set s0 := u0 + jv with hs0def
  set X := Sl s0 \ E with hX
  have hX44 : 44 ≤ X.card := by
    have := slab48 hs0 he0
    have := card_sd (Sl s0) E
    rw [← hX] at this
    omega
  set Y : Fin 6 → Finset (Fin 104) := fun k => X \ Lv (a k) (b k) with hY
  have hYk : ∀ k ∈ (univ : Finset (Fin 6)), X.card - 36 ≤ (Y k).card := by
    intro k _
    have h36 := card_two (a k) (b k) (hnd k).1 (hnd k).2.1 (hnd k).2.2
    have e36 : (Lv (a k) (b k)).card ≤ 36 := h36
    have := card_sd X (Lv (a k) (b k))
    simp only [hY]
    omega
  have hdisj : ∀ k ∈ (univ : Finset (Fin 6)), ∀ l ∈ (univ : Finset (Fin 6)), k ≠ l → Disjoint (Y k) (Y l) := by
    intro k _ l _ hkl
    rw [Finset.disjoint_left]
    intro t htk htl
    simp only [hY, hX, mem_sdiff, Sl, mem_filter, mem_univ, true_and] at htk htl
    obtain ⟨-, -, hcov⟩ := hsf k l hkl
    rw [hsame k l hkl] at hcov
    exact htk.1.2 (hcov t htk.1.1 htk.2 htl.2)
  have hU : (univ.biUnion Y).card = ∑ k, (Y k).card := by
    first
      | exact Finset.card_biUnion hdisj
      | exact Finset.card_biUnion (fun ⦃k⦄ hk ⦃l⦄ hl hkl => hdisj k hk l hl hkl)
      | exact Finset.card_biUnion (by intro k hk l hl hkl; exact hdisj k hk l hl hkl)
  have hUX : univ.biUnion Y ⊆ X := by
    intro t ht
    rw [Finset.mem_biUnion] at ht
    obtain ⟨k, -, hk⟩ := ht
    simp only [hY] at hk
    exact (Finset.mem_sdiff.mp hk).1
  have hsum := Finset.card_nsmul_le_sum (univ : Finset (Fin 6)) (fun k => (Y k).card) (X.card - 36) hYk
  rw [Finset.card_univ, Fintype.card_fin, smul_eq_mul] at hsum
  have := card_le_card hUX
  omega

/-! ## Lemma P (no six) and the census -/

/-- **Lemma P, weak form**: no six planes are pairwise compatible with a common clique exception set. -/
def LP6 : Prop := ∀ E : Finset (Fin 104), E.card ≤ 4 → (∀ x ∈ E, ∀ z ∈ E, x ≠ z → rZ x ⬝ᵥ rZ z ≠ 0) →
  ∀ a b : Fin 6 → V9, (∀ k, a k ≠ 0 ∧ b k ≠ 0 ∧ a k ≠ b k) → ∃ k l, k ≠ l ∧ ¬ CompatE E (a k) (b k) (a l) (b l)

theorem lp6_of (ht : t1xOK = true) : LP6 := by
  intro E hE hcl a b hnd
  by_contra hno
  push_neg at hno
  exact no_six_mod2 ht E hE hcl a b hnd (fun k l hkl => mc_of_compat (hno k l hkl))

theorem compatE_of {K : Type*} [Field K] [CharZero K] (Zr : Finset (Fin 104)) (Ri Rj : Finset (Fin 104))
    (y : Fin 8 → K) (hy : y ≠ 0) (hT : ∀ t, t ∉ Ri → t ∉ Rj → t ∉ Zr → rK K t ⬝ᵥ y = 0)
    (a b c d : V9) (hi : Ri ⊆ Lv a b) (hj : Rj ⊆ Lv c d) : CompatE Zr a b c d := by
  refine ⟨Finset.univ.filter fun t => rK K t ⬝ᵥ y = 0, intRk_of_perp y hy, ?_⟩
  intro t ha hc
  by_cases hz : t ∈ Zr
  · exact Or.inr hz
  · exact Or.inl (Finset.mem_filter.mpr
      ⟨Finset.mem_univ _, hT t (fun h => ha (hi h)) (fun h => hc (hj h)) hz⟩)

/-- **CensusFact for P104** from the label bounds and Lemma P in the weak form "no six". -/
theorem censusFact_of_facts6 {K : Type*} [Field K] [CharZero K] (hcap : Capacity labK) (h6 : Cap6)
    (h4 : Cap4) (hlp : LP6) : CensusFact labK (rK K) := by
  intro Zr P Q hZr hcl _hpat hM hcol
  have hrk : ∀ j, lspan labK (rowSupp P j) ≤ (block labK (rowSupp P j) (rowSupp Q j)).rank + 1 := by
    intro j
    have := block_rank_ge labK (rowSupp P j) (rowSupp Q j)
    have := (hcol j).1
    omega
  have hun : ∀ i j, i ≠ j → 45 ≤ (rowSupp P i).card + (rowSupp P j).card := by
    intro i j hij
    obtain ⟨y, hy, hT⟩ := pair_perp Zr P hM i j hij
    have := union45 Zr hZr _ _ y hy hT
    have := Finset.card_union_le (rowSupp P i) (rowSupp P j)
    omega
  have s6 : ∀ j, lspan labK (rowSupp P j) ≤ 6 → (rowSupp P j).card ≤ 20 := by
    intro j h
    by_contra hc
    have := h6 (rowSupp P j) (by omega)
    omega
  have s4 : ∀ j, lspan labK (rowSupp P j) ≤ 4 → (rowSupp P j).card ≤ 8 := by
    intro j h
    by_contra hc
    have := h4 (rowSupp P j) (by omega)
    omega
  have hclZ : ∀ x ∈ Zr, ∀ z ∈ Zr, x ≠ z → rZ x ⬝ᵥ rZ z ≠ 0 := by
    intro x hx z hz hxz e
    apply hcl x hx z hz hxz
    show rK K x ⬝ᵥ rK K z = 0
    rw [dot_cast, e, Int.cast_zero]
  unfold cost
  by_cases hA : ∃ j0, lspan labK (rowSupp P j0) ≤ 4
  · obtain ⟨j0, hj0⟩ := hA
    have hge : ∀ i ∈ Finset.univ.erase j0, 7 ≤ (block labK (rowSupp P i) (rowSupp Q i)).rank := by
      intro i hi
      have hne := Finset.ne_of_mem_erase hi
      have h1 := hun i j0 hne
      have h2 := s4 j0 hj0
      have h3 : 8 ≤ lspan labK (rowSupp P i) := hcap _ (by omega)
      have := hrk i
      omega
    have hc : (Finset.univ.erase j0).card = 8 := by
      rw [Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ]
      rfl
    have hsum := Finset.card_nsmul_le_sum _ _ 7 hge
    rw [hc, smul_eq_mul] at hsum
    have hsplit := Finset.add_sum_erase (Finset.univ : Finset C9)
      (fun j => (block labK (rowSupp P j) (rowSupp Q j)).rank) (Finset.mem_univ j0)
    try dsimp only at hsplit
    rw [← hsplit]
    omega
  · push_neg at hA
    let S7 := Finset.univ.filter fun j : C9 => lspan labK (rowSupp P j) ≤ 7
    let S6 := Finset.univ.filter fun j : C9 => lspan labK (rowSupp P j) ≤ 6
    have hS6 : S6.card ≤ 1 := by
      rw [Finset.card_le_one]
      intro a ha b hb
      by_contra hab
      simp only [S6, Finset.mem_filter, Finset.mem_univ, true_and] at ha hb
      have := hun a b hab
      have := s6 a ha
      have := s6 b hb
      omega
    have hS7 : S7.card ≤ 5 := by
      by_contra hc
      push_neg at hc
      obtain ⟨s, hs, hsc⟩ := Finset.exists_subset_card_eq (show 6 ≤ S7.card by omega)
      have hpl : ∀ j, lspan labK (rowSupp P j) ≤ 7 → ∃ z1 z2 : V9, z1 ≠ 0 ∧ z2 ≠ 0 ∧ z1 ≠ z2 ∧
          ∀ t ∈ rowSupp P j, labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0 :=
        fun j h => RankNine.Red.two_dual labK (rowSupp P j) h
      choose! A B hAB using hpl
      let e : Fin 6 ≃ s := (Fintype.equivFinOfCardEq (by simp [hsc])).symm
      let f : Fin 6 → C9 := fun k => (e k).1
      have hf : ∀ k, lspan labK (rowSupp P (f k)) ≤ 7 := fun k => by
        have := hs (e k).2
        simpa [S7] using this
      have hinj : Function.Injective f := fun k l h => e.injective (Subtype.ext h)
      obtain ⟨k, l, hkl, hnc⟩ := hlp Zr hZr hclZ (fun k => A (f k)) (fun k => B (f k))
        (fun k => ⟨(hAB _ (hf k)).1, (hAB _ (hf k)).2.1, (hAB _ (hf k)).2.2.1⟩)
      apply hnc
      obtain ⟨y, hy, hT⟩ := pair_perp Zr P hM (f k) (f l) (fun h => hkl (hinj h))
      refine compatE_of Zr _ _ y hy hT _ _ _ _ ?_ ?_
      · intro t ht
        have := (hAB _ (hf k)).2.2.2 t ht
        simp [Lv, this.1, this.2]
      · intro t ht
        have := (hAB _ (hf l)).2.2.2 t ht
        simp [Lv, this.1, this.2]
    have hge : ∀ j ∈ (Finset.univ : Finset C9), 7 ≤ (block labK (rowSupp P j) (rowSupp Q j)).rank
        + 2 * (if j ∈ S6 then 1 else 0) + (if j ∈ S7 then 1 else 0) := by
      intro j _
      have := hrk j
      have := hA j
      by_cases h7 : lspan labK (rowSupp P j) ≤ 7
      · have m7 : j ∈ S7 := by simp [S7, h7]
        by_cases h6' : lspan labK (rowSupp P j) ≤ 6
        · have m6 : j ∈ S6 := by simp [S6, h6']
          simp only [m6, m7, if_true]
          omega
        · have m6 : j ∉ S6 := by simp [S6, h6']
          simp only [m6, m7, if_true, if_false]
          omega
      · have m7 : j ∉ S7 := by simp [S7, h7]
        have m6 : j ∉ S6 := by
          simp only [S6, Finset.mem_filter, Finset.mem_univ, true_and]
          omega
        simp only [m6, m7, if_false]
        omega
    have hsum := Finset.card_nsmul_le_sum _ _ 7 hge
    have e : ∑ j, ((block labK (rowSupp P j) (rowSupp Q j)).rank + 2 * (if j ∈ S6 then 1 else 0) +
        (if j ∈ S7 then 1 else 0)) =
        ∑ j, (block labK (rowSupp P j) (rowSupp Q j)).rank + 2 * S6.card + S7.card := by
      rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum, sum_ind, sum_ind]
    rw [e, Finset.card_univ, smul_eq_mul] at hsum
    have h9 : Fintype.card C9 = 9 := by first | rfl | simp | decide
    rw [h9] at hsum
    omega

/-- **CensusFact for P104**, all inputs by hand except the type-1 table `t1xOK`. -/
theorem censusFact_P104 {K : Type*} [Field K] [CharZero K] (ht : t1xOK = true) : CensusFact labK (rK K) :=
  censusFact_of_facts6 capacity_P104 cap6_P104 cap4_hand (lp6_of ht)

end RankNine.LP
