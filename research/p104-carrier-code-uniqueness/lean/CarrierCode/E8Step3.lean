import CarrierCode.E8
import CarrierCode.E8Defs

/-!
# Steps 1–3 for the concrete ports

For a matrix `M = A * B` (inner dimension 8) with unit diagonal and zeros on orthogonal pairs, every frame gives
`∑_{x ∈ F} N t x = 1` with `N t x = M t x * M x t`; with the checked certificates this yields
`N t x = 1 + Gm t x * (r x ⬝ᵥ v t)` for an explicit `v t ⟂ r t` (step 3 of E8-PROOF.md).
-/

namespace CarrierCode.E8

open Matrix

variable (M : Matrix ι ι (ZMod 3)) (A : Matrix ι (Fin 8) (ZMod 3)) (B : Matrix (Fin 8) ι (ZMod 3))

/-- The hypotheses on a decoding matrix. -/
structure Hyp : Prop where
  fac : M = A * B
  diag : ∀ i, M i i = 1
  conf : ∀ i j, i ≠ j → Gm i j = 0 → M i j = 0

/-- `N t x = M t x * M x t`. -/
def Nm (t x : ι) : ZMod 3 := M t x * M x t

variable {M A B}

theorem frame_mat (h : Hyp M A B) (hF : framesOK) (f : Fin 759) : M.submatrix (fr f) (fr f) = 1 := by
  ext k l
  obtain ⟨_, hf⟩ := hF f
  simp only [submatrix_apply, one_apply]
  by_cases hkl : k = l
  · subst hkl; simp [h.diag]
  · obtain ⟨hk, hd⟩ := hf k l
    obtain ⟨hdot, hne⟩ := hd hkl
    have hl := (hf l k).1
    rw [if_neg hkl]
    apply h.conf
    · intro e; apply hne
      have := congrArg Fin.val e
      simpa [fr, toι_val hk, toι_val hl] using this
    · show r (fr f k).val ⬝ᵥ r (fr f l).val = 0
      rw [← dotN_cast]
      simp only [fr, toι_val hk, toι_val hl]
      exact (cast_eq_zero_iff _).mpr hdot

theorem frame_sum_N (h : Hyp M A B) (hF : framesOK) (f : Fin 759) (t : ι) :
    ∑ k : Fin 8, Nm M t (fr f k) = 1 := by
  have hm := frame_mat h hF f
  rw [h.fac] at hm
  have := CarrierCode.E8.frame_sum A B (fr f) hm t
  rw [← h.fac] at this
  rw [← h.diag t, ← this]; rfl

theorem frame_sum_count (h : Hyp M A B) (hF : framesOK) (f : Fin 759) (t : ι) :
    ∑ i : ι, (((frL f).count i.val : ℕ) : ZMod 3) * Nm M t i = 1 := by
  obtain ⟨hlen, hf⟩ := hF f
  have hl : ∀ a ∈ frL f, a < 104 := by
    intro a ha
    obtain ⟨k, hk, rfl⟩ := List.getElem_of_mem ha
    have := (hf ⟨k, hlen ▸ hk⟩ ⟨k, hlen ▸ hk⟩).1
    simpa [frN, List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hk] using this
  rw [sum_count _ hl, ← sum_fin8 _ hlen]
  exact frame_sum_N h hF f t

theorem comb_sum (h : Hyp M A B) (hF : framesOK) (t : ι) (L : List (ℕ × ℕ)) (hL : ∀ p ∈ L, p.1 < 759) :
    ∑ i : ι, ((accL L i.val : ℕ) : ZMod 3) * Nm M t i = (((L.map Prod.snd).sum : ℕ) : ZMod 3) := by
  induction L with
  | nil => simp [accL]
  | cons p L ih =>
    have ih' := ih (fun q hq => hL q (by simp [hq]))
    have hp := frame_sum_count h hF ⟨p.1, hL p (by simp)⟩ t
    simp only [accL, List.map_cons, List.sum_cons] at ih' ⊢
    push_cast at ih' ⊢
    have e : ∀ i : ι, ((p.2 : ZMod 3) * ((frL p.1).count i.val : ℕ) +
        (L.map fun q => (((q.2 * (frL q.1).count i.val : ℕ)) : ZMod 3)).sum) * Nm M t i =
        (p.2 : ZMod 3) * ((((frL p.1).count i.val : ℕ) : ZMod 3) * Nm M t i) +
        (L.map fun q => (((q.2 * (frL q.1).count i.val : ℕ)) : ZMod 3)).sum * Nm M t i := fun i => by ring
    simp only [List.map_map, Function.comp_def] at ih' ⊢
    rw [Finset.sum_congr rfl fun i _ => e i, Finset.sum_add_distrib, ← Finset.mul_sum, hp, mul_one]
    push_cast at ih' ⊢
    rw [ih']

/-- The vector `v_t` of step 3. -/
def vv (M : Matrix ι ι (ZMod 3)) (t : ι) : Fin 8 → ZMod 3 :=
  ∑ j : Fin 7, (Nm M t (toι (seedN t j)) - 1) • vec (wL t j)

theorem sum_range7 (g : ℕ → ℕ) : (((List.range 7).map g).sum : ℕ) = ∑ j : Fin 7, g j := by
  simp [List.sum_range_succ, Fin.sum_univ_seven]

theorem conf_N (h : Hyp M A B) (t i : ι) (hit : i ≠ t) (hG : dotN t i % 3 = 0) : Nm M t i = 0 := by
  have : M t i = 0 := h.conf t i (Ne.symm hit) (by rw [Gm, ← dotN_cast]; exact (cast_eq_zero_iff _).mpr hG)
  simp [Nm, this]

theorem rx_dot_vv (t x : ι) :
    Gm t x * (r x ⬝ᵥ vv M t) = ∑ j : Fin 7, (Nm M t (toι (seedN t j)) - 1) * ((eN t x j : ℕ) : ZMod 3) := by
  simp only [vv, dotProduct_sum, dotProduct_smul, smul_eq_mul, Finset.mul_sum, eN]
  refine Finset.sum_congr rfl fun j _ => ?_
  push_cast; rw [dotN_cast, dotW_cast]; simp only [Gm]; ring

theorem seed_mem {t x : ℕ} (hlen : (seedL t).length = 7) (hx : x ∈ seedL t) : ∃ i : Fin 7, seedN t i = x := by
  obtain ⟨k, hk, rfl⟩ := List.getElem_of_mem hx
  exact ⟨⟨k, hlen ▸ hk⟩, by simp [seedN, List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hk]⟩

/-- Step 3 at a seed. -/
theorem step3_seed {t x : ι} (hS : seedOK t.val) (i : Fin 7) (hx : seedN t i = x.val) :
    Nm M t x = 1 + Gm t x * (r x ⬝ᵥ vv M t) := by
  rw [rx_dot_vv]
  have hδ : ∀ j : Fin 7, ((eN t x j : ℕ) : ZMod 3) = if i = j then 1 else 0 := by
    intro j
    have := (hS.2 i j).2.2.1
    rw [hx] at this
    rw [← cast_mod, eN, this]; split_ifs <;> simp
  simp_rw [hδ, mul_ite, mul_one, mul_zero, Finset.sum_ite_eq, Finset.mem_univ, if_true]
  have : toι (seedN t i) = x := Fin.ext (by rw [hx, toι_val x.isLt])
  rw [this]; ring

/-- Step 3 away from the seeds, from the certificate. -/
theorem step3_cert {t x : ι} (h : Hyp M A B) (hF : framesOK) (hS : seedOK t.val) (hxt : x ≠ t)
    (hpos : ∀ p ∈ combL t x, p.1 < 759)
    (hacc : ∀ i : Fin 104, i.val = t.val ∨ dotN t i % 3 = 0 ∨ accL (combL t x) i % 3 = tgt t x i % 3)
    (hsc : (((combL t x).map Prod.snd).sum + 2 * accL (combL t x) t) % 3 =
      (1 + ((List.range 7).map fun j => 2 * eN t x j).sum) % 3) :
    Nm M t x = 1 + Gm t x * (r x ⬝ᵥ vv M t) := by
  have hc := comb_sum h hF t (combL t x) hpos
  -- tgt vanishes at t
  have htgt_t : tgt t x t = 0 := by
    have hxt' : t.val ≠ x.val := fun e => hxt (Fin.ext e.symm)
    simp only [tgt, if_neg hxt', zero_add]
    apply List.sum_eq_zero
    intro a ha
    obtain ⟨j, hj, rfl⟩ := List.mem_map.mp ha
    have := (hS.2 ⟨j, List.mem_range.mp hj⟩ ⟨0, by norm_num⟩).2.1
    simp [Ne.symm this]
  -- split the sum
  have hsplit : ∀ i : ι, ((accL (combL t x) i.val : ℕ) : ZMod 3) * Nm M t i =
      (if i = t then ((accL (combL t x) t.val : ℕ) : ZMod 3) else 0) + ((tgt t x i.val : ℕ) : ZMod 3) * Nm M t i := by
    intro i
    by_cases hit : i = t
    · subst hit; simp [htgt_t, Nm, h.diag]
    · rw [if_neg hit, zero_add]
      rcases hacc i with e | e | e
      · exact absurd (Fin.ext e) hit
      · rw [conf_N h t i hit e]; simp
      · rw [← cast_mod (accL _ _), e, cast_mod]
  rw [Finset.sum_congr rfl fun i _ => hsplit i, Finset.sum_add_distrib, Finset.sum_ite_eq'] at hc
  simp only [Finset.mem_univ, if_true] at hc
  -- evaluate the tgt sum
  have hterm : ∀ i : ι, ((tgt t x i.val : ℕ) : ZMod 3) * Nm M t i =
      (if i = x then Nm M t i else 0) +
        ∑ j : Fin 7, if i = toι (seedN t j) then 2 * ((eN t x j : ℕ) : ZMod 3) * Nm M t i else 0 := by
    intro i
    simp only [tgt]
    rw [sum_range7]
    push_cast [Nat.cast_ite]
    rw [add_mul, Finset.sum_mul]
    have hx : (i.val = x.val) ↔ i = x := ⟨Fin.ext, fun e => e ▸ rfl⟩
    have h1 : ((if i.val = x.val then (1 : ZMod 3) else 0)) * Nm M t i = if i = x then Nm M t i else 0 := by
      by_cases e : i = x
      · rw [if_pos (hx.mpr e), if_pos e, one_mul]
      · rw [if_neg (fun h => e (hx.mp h)), if_neg e, zero_mul]
    have h2 : ∀ j : Fin 7, ((if i.val = seedN t j then 2 * ((eN t x j : ℕ) : ZMod 3) else 0)) * Nm M t i =
        if i = toι (seedN t j) then 2 * ((eN t x j : ℕ) : ZMod 3) * Nm M t i else 0 := by
      intro j
      have hj := (hS.2 j j).1
      have hs : (i.val = seedN t ↑j) ↔ i = toι (seedN t j) :=
        ⟨fun e => Fin.ext (by rw [toι_val hj]; exact e), fun e => by rw [e, toι_val hj]⟩
      by_cases e : i = toι (seedN t j)
      · rw [if_pos (hs.mpr e), if_pos e]
      · rw [if_neg (fun h => e (hs.mp h)), if_neg e, zero_mul]
    exact congrArg₂ (· + ·) h1 (Finset.sum_congr rfl fun j _ => h2 j)
  have htsum : ∑ i : ι, ((tgt t x i.val : ℕ) : ZMod 3) * Nm M t i =
      Nm M t x + ∑ j : Fin 7, 2 * ((eN t x j : ℕ) : ZMod 3) * Nm M t (toι (seedN t j)) := by
    rw [Finset.sum_congr rfl fun i _ => hterm i, Finset.sum_add_distrib, Finset.sum_ite_eq',
      Finset.sum_comm]
    simp only [Finset.sum_ite_eq', Finset.mem_univ, if_true]
  rw [htsum] at hc
  rw [sum_range7] at hsc
  have hsc' := congrArg (fun n : ℕ => (n : ZMod 3)) hsc
  simp only [cast_mod] at hsc'
  push_cast at hsc' hc
  rw [rx_dot_vv]
  have h3 : (3 : ZMod 3) = 0 := by decide
  -- hc : acc_t + (N x + Σ 2 e_j N s_j) = Σ c ;  hsc' : Σ c + 2 acc_t = 1 + Σ 2 e_j
  have key : Nm M t x = 1 + ∑ j : Fin 7, 2 * ((eN t x j : ℕ) : ZMod 3) -
      ∑ j : Fin 7, 2 * ((eN t x j : ℕ) : ZMod 3) * Nm M t (toι (seedN t j)) := by
    linear_combination hc + hsc' - (accL (combL t x) t.val : ZMod 3) * h3
  rw [key, add_sub_assoc, ← Finset.sum_sub_distrib]
  refine congrArg (1 + ·) (Finset.sum_congr rfl fun j _ => ?_)
  linear_combination (((eN t x j : ℕ) : ZMod 3) * (1 - Nm M t (toι (seedN t j)))) * h3

theorem rt_dot_vv {t : ι} (hS : seedOK t.val) : r t ⬝ᵥ vv M t = 0 := by
  simp only [vv, dotProduct_sum, dotProduct_smul, smul_eq_mul]
  refine Finset.sum_eq_zero fun j _ => ?_
  rw [← dotW_cast, ← cast_mod, (hS.2 j j).2.2.2]; simp

/-- Step 3 (equation (3) of E8-PROOF.md) for every non-orthogonal pair, given the checks. -/
theorem step3 (h : Hyp M A B) (hF : framesOK) (hC : ∀ t : ι, seedOK t.val ∧ ∀ x : ι, check3 t.val x.val)
    (t x : ι) (hnz : dotN t x % 3 ≠ 0) :
    Nm M t x = 1 + Gm t x * (r x ⬝ᵥ vv M t) := by
  obtain ⟨hS, hc⟩ := hC t
  rcases hc x with e | e | e | ⟨hpos, hacc, hsc⟩
  · have : x = t := Fin.ext e
    subst this
    rw [rt_dot_vv hS, mul_zero, add_zero]; simp [Nm, h.diag]
  · exact absurd e hnz
  · obtain ⟨i, hi⟩ := seed_mem hS.1 e
    exact step3_seed hS i hi
  · by_cases hxt : x = t
    · subst hxt; rw [rt_dot_vv hS, mul_zero, add_zero]; simp [Nm, h.diag]
    · exact step3_cert h hF hS hxt hpos hacc hsc

end CarrierCode.E8
