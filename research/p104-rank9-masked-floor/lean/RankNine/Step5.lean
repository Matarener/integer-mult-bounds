import RankNine.Signs

/-!
# T1 step 5: signs ⇒ Gram rows (gauge by a spanning tree, then peeling)

`μ x y = M x y / M x x`, `γ x y = (ρ_x · ρ_y) / 18` (Gram entry of the normalised roots, `±1/2` on non-orthogonal
pairs).  A gauge `g` (nonzero) is fixed along a spanning tree of the covered pairs; the claim for an ordered pair is
`Gf x y : μ x y * g x = γ x y * g y`.  New pairs follow from
* 4-cycles (R1): dead `t ⊥ s`, frame inside the dead set, common pair `{a, b}`: `μ_ta μ_as = -(μ_tb μ_bs)`;
* 3-cycles: dead `t, y` not orthogonal, common pair `{a, b}`, `N = 1/4` on the five pairs: `μ_ta μ_ay = μ_ty / 2`;
* reversal: `μ x y μ y x = N = 1/4 = γ x y γ y x`;
and the same identities for `γ` (integer checks on dot products).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K]

def mu (A B : ℕ → Fin 9 → K) (x y : ℕ) : K := Mx A B x y / Mx A B x x

def gam (x y : ℕ) : K := (dot x y : K) / 18

def Gf (A B : ℕ → Fin 9 → K) (g : ℕ → K) (x y : ℕ) : Prop := mu A B x y * g x = gam x y * g y

theorem dot_comm (x y : ℕ) : dot x y = dot y x := by unfold dot; exact dotL_comm _ _

theorem Nq_mu (A B : ℕ → Fin 9 → K) (x y : ℕ) : Nq A B x y = mu A B x y * mu A B y x := by
  unfold Nq mu; ring

/-! ## Algebra -/

theorem tri_alg [CharZero K] {Mta May Mtb Mby Mya Mat Myb Mbt Maa Mbb Mtt Myy Mty Myt : K}
    (e1 : Mty = Mta * May / Maa + Mtb * Mby / Mbb) (e2 : Myt = Mya * Mat / Maa + Myb * Mbt / Mbb)
    (nta : Mta * Mat / (Mtt * Maa) = 1/4) (nay : May * Mya / (Maa * Myy) = 1/4)
    (ntb : Mtb * Mbt / (Mtt * Mbb) = 1/4) (nby : Mby * Myb / (Mbb * Myy) = 1/4)
    (nty : Mty * Myt / (Mtt * Myy) = 1/4) :
    Mta / Mtt * (May / Maa) = Mty / Mtt / 2 := by
  have hX : (Mta / Mtt * (May / Maa)) * (Mya / Myy * (Mat / Maa)) = 1/16 := by
    have h : (Mta / Mtt * (May / Maa)) * (Mya / Myy * (Mat / Maa)) =
        (Mta * Mat / (Mtt * Maa)) * (May * Mya / (Maa * Myy)) := by ring
    rw [h, nta, nay]; norm_num
  have hY : (Mtb / Mtt * (Mby / Mbb)) * (Myb / Myy * (Mbt / Mbb)) = 1/16 := by
    have h : (Mtb / Mtt * (Mby / Mbb)) * (Myb / Myy * (Mbt / Mbb)) =
        (Mtb * Mbt / (Mtt * Mbb)) * (Mby * Myb / (Mbb * Myy)) := by ring
    rw [h, ntb, nby]; norm_num
  have hs1 : Mty / Mtt = Mta / Mtt * (May / Maa) + Mtb / Mtt * (Mby / Mbb) := by rw [e1]; ring
  have hs2 : Myt / Myy = Mya / Myy * (Mat / Maa) + Myb / Myy * (Mbt / Mbb) := by rw [e2]; ring
  have hXY : (Mta / Mtt * (May / Maa) + Mtb / Mtt * (Mby / Mbb)) *
      (Mya / Myy * (Mat / Maa) + Myb / Myy * (Mbt / Mbb)) = 1/4 := by
    rw [← hs1, ← hs2, ← nty]; ring
  have hsq : (Mta / Mtt * (May / Maa) - Mtb / Mtt * (Mby / Mbb)) ^ 2 = 0 := by
    linear_combination (16 * (Mta / Mtt * (May / Maa)) * (Mtb / Mtt * (Mby / Mbb))) * hXY -
      (16 * ((Mta / Mtt * (May / Maa)) * (Mtb / Mtt * (Mby / Mbb)) + (Mtb / Mtt * (Mby / Mbb)) ^ 2)) * hX -
      (16 * ((Mta / Mtt * (May / Maa)) ^ 2 + (Mta / Mtt * (May / Maa)) * (Mtb / Mtt * (Mby / Mbb)))) * hY
  have h0 := (pow_eq_zero_iff (n := 2) (by norm_num)).mp hsq
  linear_combination (-1/2 : K) * hs1 + (1/2 : K) * h0

theorem gf_r1 {mta mas mtb mbs gta gas gtb gbs pt pa pb ps : K}
    (F1 : mta * pt = gta * pa) (F2 : mas * pa = gas * ps) (F3 : mtb * pt = gtb * pb)
    (h : mta * mas = -(mtb * mbs)) (hg : gta * gas = -(gtb * gbs)) (hgtb : gtb ≠ 0) (hpa : pa ≠ 0) :
    mbs * pb = gbs * ps := by
  have e : (gtb * pa) * (mbs * pb) = (gtb * pa) * (gbs * ps) := by
    linear_combination (-(gta * pa)) * F2 + (-(pa * mas)) * F1 + (pa * pt) * h + (-(pa * mbs)) * F3 +
      (-(pa * ps)) * hg
  exact mul_left_cancel₀ (mul_ne_zero hgtb hpa) e

theorem gf_ty [CharZero K] {mta may mty gta gay gty pt pa py : K}
    (F1 : mta * pt = gta * pa) (F2 : may * pa = gay * py) (h : mta * may = mty / 2) (hg : gta * gay = gty / 2)
    (hpa : pa ≠ 0) : mty * pt = gty * py := by
  have e : pa * (mty * pt) = pa * (gty * py) := by
    linear_combination (-2 * pa * pt) * h + (2 * pa * py) * hg + (2 * gta * pa) * F2 + (2 * may * pa) * F1
  exact mul_left_cancel₀ hpa e

theorem gf_ay [CharZero K] {mta may mty gta gay gty pt pa py : K}
    (F1 : mta * pt = gta * pa) (F3 : mty * pt = gty * py) (h : mta * may = mty / 2) (hg : gta * gay = gty / 2)
    (hgta : gta ≠ 0) (hpa : pa ≠ 0) : may * pa = gay * py := by
  have e : (gta * pa) * (may * pa) = (gta * pa) * (gay * py) := by
    linear_combination (pa / 2) * F3 + (pt * pa) * h - (may * pa) * F1 - (pa * py) * hg
  exact mul_left_cancel₀ (mul_ne_zero hgta hpa) e

theorem gf_rev [CharZero K] {mxy myx gxy gyx px py : K} (F : mxy * px = gxy * py) (hN : mxy * myx = 1/4)
    (hg : gxy * gyx = 1/4) (hgxy : gxy ≠ 0) : myx * py = gyx * px := by
  have e : (4 * gxy) * (myx * py) = (4 * gxy) * (gyx * px) := by
    linear_combination (4 * px) * hN - (4 * myx) * F - (4 * px) * hg
  exact mul_left_cancel₀ (mul_ne_zero (by norm_num) hgxy) e

section gam

variable [CharZero K]

theorem gam_sq {x y : ℕ} (h : dot x y * dot x y = 81) : gam x y * gam y x = (1/4 : K) := by
  unfold gam
  rw [dot_comm y x]
  have h' : (dot x y : K) * (dot x y : K) = 81 := by exact_mod_cast h
  linear_combination h' / 324

theorem dot_ne_of_sq {x y : ℕ} (h : dot x y * dot x y = 81) : dot x y ≠ 0 := by
  intro h0; rw [h0] at h; norm_num at h

theorem gam_ne {x y : ℕ} (h : dot x y ≠ 0) : gam x y ≠ (0 : K) := by
  unfold gam; exact div_ne_zero (Int.cast_ne_zero.mpr h) (by norm_num)

theorem gam_r1 {t a s b : ℕ} (h : dot t a * dot a s = -(dot t b * dot b s)) :
    gam t a * gam a s = -(gam t b * gam b s : K) := by
  unfold gam
  have h' : (dot t a : K) * (dot a s : K) = -((dot t b : K) * (dot b s : K)) := by exact_mod_cast h
  linear_combination h' / 324

theorem gam_tri {t a y : ℕ} (h : dot t a * dot a y = 9 * dot t y) :
    gam t a * gam a y = (gam t y : K) / 2 := by
  unfold gam
  have h' : (dot t a : K) * (dot a y : K) = 9 * (dot t y : K) := by exact_mod_cast h
  linear_combination h' / 324

end gam

/-! ## Two-term expansions -/

theorem expand2 (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (t s f ka kb : ℕ) (ht : t < 104) (hs : s < 104) (hka : ka < 8) (hkb : kb < 8) (hab : ka ≠ kb)
    (hZt : m.testBit t = true) (hFZ : ∀ k < 8, m.testBit (frL f k) = true)
    (hoth : ∀ k < 8, k = ka ∨ k = kb ∨ orth t (frL f k) = true ∨ orth s (frL f k) = true) :
    Mx A B t s = Mx A B t (frL f ka) * Mx A B (frL f ka) s / Mx A B (frL f ka) (frL f ka) +
      Mx A B t (frL f kb) * Mx A B (frL f kb) s / Mx A B (frL f kb) (frL f kb) := by
  have hdead : ∀ k : Fin 8, A (frL f k) ⬝ᵥ u = 0 := fun k => hZ _ (hFZ k k.2)
  have hdF : ∀ k : Fin 8, A (frL f k) ⬝ᵥ B (frL f k) ≠ 0 := fun k => hdiag _ (frame_lt f k.2)
  have hoff : ∀ k l : Fin 8, k ≠ l → A (frL f k) ⬝ᵥ B (frL f l) = 0 := fun k l hkl =>
    hmask _ (frame_lt f k.2) _ (frame_lt f l.2) (frame_orth f k.2 l.2 (fun e => hkl (Fin.ext e)))
  have e1 : A t ⬝ᵥ B s = ∑ k : Fin 8, A t ⬝ᵥ B (frL f k) * (A (frL f k) ⬝ᵥ B s) / (A (frL f k) ⬝ᵥ B (frL f k)) :=
    frame_expansion A B u hu (fun k => frL f k) hdead hdF hoff t (hZ t hZt) s
  have hne : (⟨ka, hka⟩ : Fin 8) ≠ ⟨kb, hkb⟩ := Fin.ne_of_val_ne hab
  have s1 : ∀ x : Fin 8, x ≠ ⟨ka, hka⟩ ∧ x ≠ ⟨kb, hkb⟩ →
      A t ⬝ᵥ B (frL f x) * (A (frL f x) ⬝ᵥ B s) / (A (frL f x) ⬝ᵥ B (frL f x)) = 0 := by
    intro x hx
    rcases hoth x x.2 with h | h | h | h
    · exact (hx.1 (Fin.ext h)).elim
    · exact (hx.2 (Fin.ext h)).elim
    · rw [hmask t ht _ (frame_lt f x.2) h, zero_mul, zero_div]
    · rw [hmask _ (frame_lt f x.2) s hs (by rw [orth_comm]; exact h), mul_zero, zero_div]
  rw [Fintype.sum_eq_add _ _ hne s1] at e1
  exact e1

theorem r1_mu (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (t s f ka kb : ℕ) (ht : t < 104) (hs : s < 104) (hka : ka < 8) (hkb : kb < 8) (hab : ka ≠ kb)
    (hZt : m.testBit t = true) (hFZ : ∀ k < 8, m.testBit (frL f k) = true)
    (hoth : ∀ k < 8, k = ka ∨ k = kb ∨ orth t (frL f k) = true ∨ orth s (frL f k) = true)
    (hts : orth t s = true) :
    mu A B t (frL f ka) * mu A B (frL f ka) s = -(mu A B t (frL f kb) * mu A B (frL f kb) s) := by
  have e := expand2 A B u hu m hZ hdiag hmask t s f ka kb ht hs hka hkb hab hZt hFZ hoth
  rw [show Mx A B t s = 0 from hmask t ht s hs hts] at e
  unfold mu
  linear_combination (-1 / Mx A B t t) * e

theorem tri_mu [CharZero K] (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (t y f ka kb : ℕ) (ht : t < 104) (hy : y < 104) (hka : ka < 8) (hkb : kb < 8) (hab : ka ≠ kb)
    (hZt : m.testBit t = true) (hZy : m.testBit y = true) (hFZ : ∀ k < 8, m.testBit (frL f k) = true)
    (hoth : ∀ k < 8, k = ka ∨ k = kb ∨ orth t (frL f k) = true ∨ orth y (frL f k) = true)
    (n1 : Nq A B t (frL f ka) = 1/4) (n2 : Nq A B (frL f ka) y = 1/4) (n3 : Nq A B t (frL f kb) = 1/4)
    (n4 : Nq A B (frL f kb) y = 1/4) (n5 : Nq A B t y = 1/4) :
    mu A B t (frL f ka) * mu A B (frL f ka) y = mu A B t y / 2 := by
  have e1 := expand2 A B u hu m hZ hdiag hmask t y f ka kb ht hy hka hkb hab hZt hFZ hoth
  have e2 := expand2 A B u hu m hZ hdiag hmask y t f ka kb hy ht hka hkb hab hZy hFZ
    (fun k hk => by have := hoth k hk; tauto)
  exact tri_alg e1 e2 n1 n2 n3 n4 n5

/-! ## Gauge along a spanning tree -/

/-- gauge at vertex index `i`: product of `μ / γ` along the tree path (`PL[i] < i` is the parent) -/
noncomputable def gIdx (A B : ℕ → Fin 9 → K) (V PL : List ℕ) (nV : ℕ) (i : ℕ) : K :=
  if h : i < nV ∧ fld PL i < i then
    gIdx A B V PL nV (fld PL i) * mu A B (fld V (fld PL i)) (fld V i) / gam (fld V (fld PL i)) (fld V i)
  else 1
termination_by i
decreasing_by all_goals (try simp_wf); omega

noncomputable def gOf (A B : ℕ → Fin 9 → K) (V PL II : List ℕ) (nV : ℕ) (x : ℕ) : K :=
  gIdx A B V PL nV (fld II x)

theorem gIdx_ne (A B : ℕ → Fin 9 → K) (V PL : List ℕ) (nV : ℕ)
    (htree : ∀ i < nV, fld PL i < i →
      mu A B (fld V (fld PL i)) (fld V i) ≠ 0 ∧ gam (fld V (fld PL i)) (fld V i) ≠ (0 : K)) :
    ∀ i, gIdx A B V PL nV i ≠ 0 := by
  intro i
  induction i using Nat.strong_induction_on with
  | _ i ih =>
    rw [gIdx]
    split_ifs with h
    · exact div_ne_zero (mul_ne_zero (ih _ h.2) (htree i h.1 h.2).1) (htree i h.1 h.2).2
    · exact one_ne_zero

theorem gIdx_tree (A B : ℕ → Fin 9 → K) (V PL II : List ℕ) (nV : ℕ) (i : ℕ) (hi : i < nV) (hp : fld PL i < i)
    (hIi : fld II (fld V i) = i) (hIp : fld II (fld V (fld PL i)) = fld PL i)
    (hg : gam (fld V (fld PL i)) (fld V i) ≠ (0 : K)) :
    Gf A B (gOf A B V PL II nV) (fld V (fld PL i)) (fld V i) := by
  unfold Gf gOf
  rw [hIi, hIp]
  conv_rhs => rw [gIdx, dif_pos ⟨hi, hp⟩]
  rw [mul_div_assoc', mul_div_cancel_left₀ _ hg, mul_comm]

/-! ## Certificate steps -/

def fct (FS : List ℕ) (i : ℕ) : ℕ × ℕ := (fld FS (2 * i), fld FS (2 * i + 1))

/-- `N = 1/4` table entry `n` for `code` -/
def ntOK (nNT : ℕ) (NT : List ℕ) (n code : ℕ) : Bool := decide (n < nNT) && fld NT (3 * n) == code

/-- geometry shared by the expansions: dead `t`, frame `f` inside the dead set, `ka ≠ kb`, the other frame lines
orthogonal to `t` or `s` -/
def geomChk (m t s f ka kb : ℕ) : Bool :=
  decide (t < 104) && decide (s < 104) && decide (ka < 8) && decide (kb < 8) && decide (ka ≠ kb) &&
    m.testBit t && (List.range 8).all (fun k => m.testBit (frL f k)) &&
    (List.range 8).all (fun k => decide (k = ka) || decide (k = kb) || orthB t (frL f k) || orthB s (frL f k))

theorem geomChk_sound {m t s f ka kb : ℕ} (h : geomChk m t s f ka kb = true) :
    t < 104 ∧ s < 104 ∧ ka < 8 ∧ kb < 8 ∧ ka ≠ kb ∧ m.testBit t = true ∧ (∀ k < 8, m.testBit (frL f k) = true) ∧
      (∀ k < 8, k = ka ∨ k = kb ∨ orth t (frL f k) = true ∨ orth s (frL f k) = true) := by
  simp only [geomChk, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true,
    and_assoc] at h
  obtain ⟨ht, hs, hka, hkb, hab, hZt, hFZ, hoth⟩ := h
  refine ⟨ht, hs, hka, hkb, hab, hZt, hFZ, fun k hk => ?_⟩
  have hk' := frame_lt f hk
  have hr := hoth k hk
  by_cases g1 : k = ka
  · exact Or.inl g1
  by_cases g2 : k = kb
  · exact Or.inr (Or.inl g2)
  by_cases g3 : orthB t (frL f k) = true
  · exact Or.inr (Or.inr (Or.inl (orth_of_orthB ht hk' g3)))
  have g4 : orthB s (frL f k) = true := by tauto
  exact Or.inr (Or.inr (Or.inr (orth_of_orthB hs hk' g4)))

/-- step `i` (14 fields of `ST`): tag 0 tree `v`; 1 reversal `k n`; 2 R1 `t s f ka kb k1 k2 k3`;
3 three-cycle for `(t, y)`: `t y f ka kb k1 k2 n1 … n5`; 4 three-cycle for `(a, y)`: same with `k2` the fact `(t, y)` -/
def st (ST : List ℕ) (i j : ℕ) : ℕ := fld ST (14 * i + j)

def sa (ST : List ℕ) (i : ℕ) : ℕ := frL (st ST i 3) (st ST i 4)

def sb (ST : List ℕ) (i : ℕ) : ℕ := frL (st ST i 3) (st ST i 5)

def step5OK (m nV nNT : ℕ) (V PL NT FS ST : List ℕ) (i : ℕ) : Bool :=
  if st ST i 0 = 0 then
    decide (st ST i 1 < nV) && decide (fld PL (st ST i 1) < st ST i 1) &&
      fct FS i == (fld V (fld PL (st ST i 1)), fld V (st ST i 1))
  else if st ST i 0 = 1 then
    decide (st ST i 1 < i) && fct FS i == ((fct FS (st ST i 1)).2, (fct FS (st ST i 1)).1) &&
      ntOK nNT NT (st ST i 2) (pcode (fct FS (st ST i 1)).1 (fct FS (st ST i 1)).2) &&
      decide ((fct FS (st ST i 1)).1 < 104) && decide ((fct FS (st ST i 1)).2 < 104) &&
      dot (fct FS (st ST i 1)).1 (fct FS (st ST i 1)).2 * dot (fct FS (st ST i 1)).1 (fct FS (st ST i 1)).2 == 81
  else if st ST i 0 = 2 then
    geomChk m (st ST i 1) (st ST i 2) (st ST i 3) (st ST i 4) (st ST i 5) && orthB (st ST i 1) (st ST i 2) &&
      decide (st ST i 6 < i) && decide (st ST i 7 < i) && decide (st ST i 8 < i) &&
      fct FS (st ST i 6) == (st ST i 1, sa ST i) && fct FS (st ST i 7) == (sa ST i, st ST i 2) &&
      fct FS (st ST i 8) == (st ST i 1, sb ST i) && fct FS i == (sb ST i, st ST i 2) &&
      dot (st ST i 1) (sa ST i) * dot (sa ST i) (st ST i 2) == -(dot (st ST i 1) (sb ST i) * dot (sb ST i) (st ST i 2)) &&
      dot (st ST i 1) (sb ST i) != 0
  else if st ST i 0 = 3 then
    geomChk m (st ST i 1) (st ST i 2) (st ST i 3) (st ST i 4) (st ST i 5) && m.testBit (st ST i 2) &&
      decide (st ST i 6 < i) && decide (st ST i 7 < i) &&
      fct FS (st ST i 6) == (st ST i 1, sa ST i) && fct FS (st ST i 7) == (sa ST i, st ST i 2) &&
      fct FS i == (st ST i 1, st ST i 2) &&
      ntOK nNT NT (st ST i 8) (pcode (st ST i 1) (sa ST i)) && ntOK nNT NT (st ST i 9) (pcode (sa ST i) (st ST i 2)) &&
      ntOK nNT NT (st ST i 10) (pcode (st ST i 1) (sb ST i)) && ntOK nNT NT (st ST i 11) (pcode (sb ST i) (st ST i 2)) &&
      ntOK nNT NT (st ST i 12) (pcode (st ST i 1) (st ST i 2)) &&
      dot (st ST i 1) (sa ST i) * dot (sa ST i) (st ST i 2) == 9 * dot (st ST i 1) (st ST i 2)
  else
    geomChk m (st ST i 1) (st ST i 2) (st ST i 3) (st ST i 4) (st ST i 5) && m.testBit (st ST i 2) &&
      decide (st ST i 6 < i) && decide (st ST i 7 < i) &&
      fct FS (st ST i 6) == (st ST i 1, sa ST i) && fct FS (st ST i 7) == (st ST i 1, st ST i 2) &&
      fct FS i == (sa ST i, st ST i 2) &&
      ntOK nNT NT (st ST i 8) (pcode (st ST i 1) (sa ST i)) && ntOK nNT NT (st ST i 9) (pcode (sa ST i) (st ST i 2)) &&
      ntOK nNT NT (st ST i 10) (pcode (st ST i 1) (sb ST i)) && ntOK nNT NT (st ST i 11) (pcode (sb ST i) (st ST i 2)) &&
      ntOK nNT NT (st ST i 12) (pcode (st ST i 1) (st ST i 2)) &&
      dot (st ST i 1) (sa ST i) * dot (sa ST i) (st ST i 2) == 9 * dot (st ST i 1) (st ST i 2) &&
      dot (st ST i 1) (sa ST i) != 0

/-- vertex `i`: index map, line bound, and (if it has a parent) the tree edge has `N = 1/4` and `γ ≠ 0` -/
def vertOK (nNT : ℕ) (V PL II NT TN : List ℕ) (i : ℕ) : Bool :=
  fld II (fld V i) == i && decide (fld V i < 104) &&
    (decide (i ≤ fld PL i) || (ntOK nNT NT (fld TN i) (pcode (fld V (fld PL i)) (fld V i)) &&
      dot (fld V (fld PL i)) (fld V i) * dot (fld V (fld PL i)) (fld V i) == 81))

section sound

variable [CharZero K]

theorem nt_N (A B : ℕ → Fin 9 → K) (nNT : ℕ) (NT : List ℕ) (hNT : ∀ n < nNT, Nc A B (fld NT (3 * n)) = 1/4)
    {n x y : ℕ} (hx : x < 104) (hy : y < 104) (h : ntOK nNT NT n (pcode x y) = true) : Nq A B x y = 1/4 := by
  simp only [ntOK, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  rw [← Nc_code A B hx hy, ← h.2]; exact hNT n h.1

theorem step5_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (nV nNT nF : ℕ) (V PL II NT TN FS ST : List ℕ)
    (hNT : ∀ n < nNT, Nc A B (fld NT (3 * n)) = 1/4)
    (hvert : ∀ i < nV, vertOK nNT V PL II NT TN i = true)
    (hsteps : ∀ i < nF, step5OK m nV nNT V PL NT FS ST i = true) :
    (∀ x, gOf A B V PL II nV x ≠ 0) ∧ ∀ i < nF, Gf A B (gOf A B V PL II nV) (fct FS i).1 (fct FS i).2 := by
  have hv : ∀ i < nV, fld II (fld V i) = i ∧ fld V i < 104 ∧ (fld PL i < i →
      Nq A B (fld V (fld PL i)) (fld V i) = 1/4 ∧ dot (fld V (fld PL i)) (fld V i) * dot (fld V (fld PL i)) (fld V i) = 81) := by
    intro i hi
    have h := hvert i hi
    simp only [vertOK, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq, Bool.or_eq_true] at h
    obtain ⟨⟨h1, h2⟩, h3⟩ := h
    refine ⟨h1, h2, fun hp => ?_⟩
    rcases h3 with h3 | ⟨h3, h4⟩
    · omega
    · have hpl : fld PL i < nV := lt_trans hp hi
      have hb := (hvert _ hpl)
      simp only [vertOK, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at hb
      exact ⟨nt_N A B nNT NT hNT hb.1.2 h2 h3, h4⟩
  have hne : ∀ x, gOf A B V PL II nV x ≠ 0 := by
    intro x
    unfold gOf
    refine gIdx_ne A B V PL nV (fun i hi hp => ?_) _
    obtain ⟨hn, hd⟩ := (hv i hi).2.2 hp
    rw [Nq_mu] at hn
    exact ⟨left_ne_zero_of_mul (by rw [hn]; norm_num), gam_ne (dot_ne_of_sq hd)⟩
  refine ⟨hne, ?_⟩
  set g := gOf A B V PL II nV with hgdef
  intro i
  induction i using Nat.strong_induction_on with
  | _ i ih =>
    intro hi
    have h := hsteps i hi
    have prev : ∀ k < i, Gf A B g (fct FS k).1 (fct FS k).2 := fun k hk => ih k hk (lt_trans hk hi)
    unfold step5OK at h
    split_ifs at h with h0 h1 h2 h3
    · -- tree
      simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, and_assoc] at h
      obtain ⟨hv1, hp, hf⟩ := h
      rw [hf]
      obtain ⟨hI, _, hpt⟩ := hv _ hv1
      obtain ⟨hIp, _, _⟩ := hv _ (lt_trans hp hv1)
      exact gIdx_tree A B V PL II nV _ hv1 hp hI hIp (gam_ne (dot_ne_of_sq (hpt hp).2))
    · -- reversal
      simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, and_assoc] at h
      obtain ⟨hk, hf, hn, hx, hy, hd⟩ := h
      rw [hf]
      have F := prev _ hk
      have hN := nt_N A B nNT NT hNT hx hy hn
      rw [Nq_mu] at hN
      exact gf_rev F hN (gam_sq hd) (gam_ne (dot_ne_of_sq hd))
    · -- R1
      simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, bne_iff_ne, ne_eq, and_assoc] at h
      obtain ⟨hg, hts, hk1, hk2, hk3, f1, f2, f3, hf, hd, hd0⟩ := h
      obtain ⟨ht, hs, hka, hkb, hab, hZt, hFZ, hoth⟩ := geomChk_sound hg
      have F1 := prev _ hk1
      have F2 := prev _ hk2
      have F3 := prev _ hk3
      rw [f1] at F1
      rw [f2] at F2
      rw [f3] at F3
      rw [hf]
      exact gf_r1 F1 F2 F3
        (r1_mu A B u hu m hZ hdiag hmask _ _ _ _ _ ht hs hka hkb hab hZt hFZ hoth (orth_of_orthB ht hs hts))
        (gam_r1 hd) (gam_ne hd0) (hne _)
    · -- three-cycle, new (t, y)
      simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, and_assoc] at h
      obtain ⟨hg, hZy, hk1, hk2, f1, f2, hf, n1, n2, n3, n4, n5, hd⟩ := h
      obtain ⟨ht, hs, hka, hkb, hab, hZt, hFZ, hoth⟩ := geomChk_sound hg
      have fa := frame_lt (st ST i 3) hka
      have fb := frame_lt (st ST i 3) hkb
      have F1 := prev _ hk1
      have F2 := prev _ hk2
      rw [f1] at F1
      rw [f2] at F2
      rw [hf]
      exact gf_ty F1 F2
        (tri_mu A B u hu m hZ hdiag hmask _ _ _ _ _ ht hs hka hkb hab hZt hZy hFZ hoth
          (nt_N A B nNT NT hNT ht fa n1) (nt_N A B nNT NT hNT fa hs n2) (nt_N A B nNT NT hNT ht fb n3)
          (nt_N A B nNT NT hNT fb hs n4) (nt_N A B nNT NT hNT ht hs n5))
        (gam_tri hd) (hne _)
    · -- three-cycle, new (a, y)
      simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, bne_iff_ne, ne_eq, and_assoc] at h
      obtain ⟨hg, hZy, hk1, hk2, f1, f2, hf, n1, n2, n3, n4, n5, hd, hd0⟩ := h
      obtain ⟨ht, hs, hka, hkb, hab, hZt, hFZ, hoth⟩ := geomChk_sound hg
      have fa := frame_lt (st ST i 3) hka
      have fb := frame_lt (st ST i 3) hkb
      have F1 := prev _ hk1
      have F3 := prev _ hk2
      rw [f1] at F1
      rw [f2] at F3
      rw [hf]
      exact gf_ay F1 F3
        (tri_mu A B u hu m hZ hdiag hmask _ _ _ _ _ ht hs hka hkb hab hZt hZy hFZ hoth
          (nt_N A B nNT NT hNT ht fa n1) (nt_N A B nNT NT hNT fa hs n2) (nt_N A B nNT NT hNT ht fb n3)
          (nt_N A B nNT NT hNT fb hs n4) (nt_N A B nNT NT hNT ht hs n5))
        (gam_tri hd) (gam_ne hd0) (hne _)

end sound

end RankNine

namespace RankNine

open Matrix

variable {K : Type*} [Field K]

/-! ## `N = 1/4` table from quadruple rows -/

/-- code of slot `l` of quadruple row `j` -/
def qc (NQ : List ℕ) (j l : ℕ) : ℕ := pcode (qRow NQ j 0) (frL (qRow NQ j 1) (qRow NQ j (2 + l)))

/-- entry `n` of the table (code, quadruple row, slot) -/
def ntEntryOK (m nQ nK : ℕ) (T CR NQ NT : List ℕ) (nNQ n : ℕ) : Bool :=
  decide (fld NT (3 * n + 1) < nNQ) && qRowOK m nQ nK T CR NQ (fld NT (3 * n + 1)) &&
    decide (fld NT (3 * n + 2) < 4) && fld NT (3 * n) == qc NQ (fld NT (3 * n + 1)) (fld NT (3 * n + 2))

theorem nt_sound [CharZero K] (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK : ℕ) (T CR : List ℕ)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hmag : ∀ c < nK, magN (Nc A B (fld CR c)) = 0) (NQ NT : List ℕ) (nNQ nNT : ℕ)
    (h : ∀ n < nNT, ntEntryOK m nQ nK T CR NQ NT nNQ n = true) :
    ∀ n < nNT, Nc A B (fld NT (3 * n)) = 1/4 := by
  intro n hn
  have hh := h n hn
  simp only [ntEntryOK, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, and_assoc] at hh
  obtain ⟨_, hq, hl, hc⟩ := hh
  have Q := quad_quarter A B u hu m hZ hdiag hmask nQ nK T CR hT hmag _ _ _ _ _ _ _ _ _ _ _ hq
  rw [hc]
  have hl' : fld NT (3 * n + 2) = 0 ∨ fld NT (3 * n + 2) = 1 ∨ fld NT (3 * n + 2) = 2 ∨
      fld NT (3 * n + 2) = 3 := by omega
  rcases hl' with e | e | e | e <;> rw [qc, e]
  · exact Q.1
  · exact Q.2.1
  · exact Q.2.2.1
  · exact Q.2.2.2

end RankNine
