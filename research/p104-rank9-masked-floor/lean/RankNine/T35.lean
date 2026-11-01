import RankNine.T3
import BForm

set_option linter.unusedSectionVars false

/-!
# T3.5: the T3 output as a B-form

Ports `Fin 104`; BForm roots `r : Fin 104 → Fin 8 → K` with `ρ_a·ρ_b = (9/4) r_a·r_b` (`hr`; for `r = rK`, the
E8 coordinates of #6188, this is a finite check).  If every row is `P v = a_v ρ_v + λ_v Λ` and every column is
`c s = b_s ρ_s`, then `M v s = α_v α'_s r_v·r_s + λ_v β_s` with `α = (9/4) a`, `α' = b`,
`β_s = b_s Λ·ρ_s + η_s`: the ordinary B-form, with the diagonal and biclique conditions of `bform_floor`
(`bform_F1`).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] [CharZero K]

theorem bX_bX_apply (r : Fin 104 → Fin 8 → K) (α c α' β : Fin 104 → K) (t s : Fin 104) :
    (BForm.bX r α c * (BForm.bX r α' β)ᵀ) t s = c t * β s + α t * α' s * (r t ⬝ᵥ r s) := by
  simp only [Matrix.mul_apply, Matrix.transpose_apply, BForm.bX, Fintype.sum_option, Option.elim, dotProduct,
    Finset.mul_sum]
  congr 1
  refine Finset.sum_congr rfl fun k _ => ?_
  ring

/-- **(F1)** the ordinary B-form from glued rows and gramm columns -/
theorem bform_F1 (r : Fin 104 → Fin 8 → K) (hr : ∀ a b : Fin 104, ((dot a b : ℤ) : K) = 9 / 4 * (r a ⬝ᵥ r b))
    (N : Matrix (Fin 104) (Fin 104) K) (P c : ℕ → Fin 9 → K) (lam eta : ℕ → K) (Λ : Fin 9 → K)
    (hN : ∀ v s : Fin 104, N v s = P v ⬝ᵥ c s + lam v * eta s)
    (hrow : ∀ v < 104, ∃ a : K, P v = a • rho K v + lam v • Λ) (hcol : ∀ s < 104, ∃ b : K, c s = b • rho K s)
    (hdiag : ∀ t, N t t ≠ 0) (hmask : ∀ u s : Fin 104, dot u s = 0 → N u s = 0) :
    ∃ α α' cc β : Fin 104 → K, (∀ t, (cc t = 0 ∨ β t = 0) → α t ≠ 0 ∧ α' t ≠ 0) ∧
      (∀ u s, cc u ≠ 0 → β s ≠ 0 → u ≠ s → ¬ BForm.Orth r u s) ∧
      BForm.Pattern r (BForm.bX r α cc * (BForm.bX r α' β)ᵀ) ∧ N = BForm.bX r α cc * (BForm.bX r α' β)ᵀ := by
  choose! a ha using hrow
  choose! b hb using hcol
  set α : Fin 104 → K := fun t => 9 / 4 * a t
  set α' : Fin 104 → K := fun t => b t
  set cc : Fin 104 → K := fun t => lam t
  set β : Fin 104 → K := fun t => b t * (Λ ⬝ᵥ rho K t) + eta t
  have hform : N = BForm.bX r α cc * (BForm.bX r α' β)ᵀ := by
    ext t s
    rw [bX_bX_apply, hN, ha t t.2, hb s s.2]
    simp only [add_dotProduct, smul_dotProduct, dotProduct_smul, smul_eq_mul, rho_dot, hr, α, α', cc, β]
    ring
  have hent : ∀ t s : Fin 104, N t s = cc t * β s + α t * α' s * (r t ⬝ᵥ r s) := by
    intro t s; rw [hform, bX_bX_apply]
  have hrr : ∀ t : Fin 104, r t ⬝ᵥ r t = 8 := by
    intro t
    have h := hr t t
    rw [dot_self t.2] at h
    have : (9 / 4 : K) * (r t ⬝ᵥ r t) = 18 := by rw [← h]; norm_num
    linear_combination (4 / 9 : K) * this
  refine ⟨α, α', cc, β, fun t ht => ?_, fun u s hu hs hus ho => ?_, ⟨fun t => ?_, fun u s hus ho => ?_⟩, hform⟩
  · have e := hdiag t
    rw [hent, hrr] at e
    rcases ht with h0 | h0 <;> rw [h0] at e <;> simp only [zero_mul, mul_zero, zero_add] at e <;>
      exact ⟨left_ne_zero_of_mul (left_ne_zero_of_mul e), right_ne_zero_of_mul (left_ne_zero_of_mul e)⟩
  · have hd : dot u s = 0 := by
      have h := hr u s
      unfold BForm.Orth at ho
      rw [ho, mul_zero] at h
      exact_mod_cast h
    have e := hmask u s hd
    rw [hent] at e
    unfold BForm.Orth at ho
    rw [ho, mul_zero, add_zero] at e
    exact mul_ne_zero hu hs e
  · rw [← hform]; exact hdiag t
  · rw [← hform]
    apply hmask
    have h := hr u s
    unfold BForm.Orth at ho
    rw [ho, mul_zero] at h
    exact_mod_cast h

/-- the product of a `bX` with an arbitrary second factor -/
theorem bX_mul_tr_apply (r : Fin 104 → Fin 8 → K) (α c : Fin 104 → K) (Y : Matrix (Fin 104) BForm.C9 K)
    (t s : Fin 104) :
    (BForm.bX r α c * Yᵀ) t s = c t * Y s none + α t * (r t ⬝ᵥ fun k => Y s (some k)) := by
  simp only [Matrix.mul_apply, Matrix.transpose_apply, BForm.bX, Fintype.sum_option, Option.elim, dotProduct,
    Finset.mul_sum]
  congr 1
  refine Finset.sum_congr rfl fun k _ => ?_
  ring

/-- a linear map `F` with `F ρ_x = r_x` turns `ρ`-dot products into `(9/4) r`-dot products on the span of roots -/
theorem F_dot (r : Fin 104 → Fin 8 → K) (hr : ∀ a b : Fin 104, ((dot a b : ℤ) : K) = 9 / 4 * (r a ⬝ᵥ r b))
    (F : Matrix (Fin 8) (Fin 9) K) (hF : ∀ x : Fin 104, F *ᵥ rho K x = r x) {n : ℕ} (co : Fin n → K)
    (g : Fin n → Fin 104) (s : Fin 104) :
    9 / 4 * (r s ⬝ᵥ (F *ᵥ ∑ k, co k • rho K (g k))) = rho K s ⬝ᵥ ∑ k, co k • rho K (g k) := by
  rw [Matrix.mulVec_sum, dotProduct_sum, dotProduct_sum, Finset.mul_sum]
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [Matrix.mulVec_smul, hF, dotProduct_smul, dotProduct_smul, smul_eq_mul, smul_eq_mul, rho_dot, hr]
  ring

theorem card_ge_five {S : Finset (Fin 104)} (h : 5 ≤ S.card) :
    ∃ x1 ∈ S, ∃ x2 ∈ S, ∃ x3 ∈ S, ∃ x4 ∈ S, ∃ x5 ∈ S, x1 ≠ x2 ∧ x1 ≠ x3 ∧ x1 ≠ x4 ∧ x1 ≠ x5 ∧ x2 ≠ x3 ∧
      x2 ≠ x4 ∧ x2 ≠ x5 ∧ x3 ≠ x4 ∧ x3 ≠ x5 ∧ x4 ≠ x5 := by
  set l := S.toList with hl
  have hn : l.Nodup := Finset.nodup_toList S
  have hlen : 5 ≤ l.length := by rw [hl, Finset.length_toList]; exact h
  have mem : ∀ i (hi : i < l.length), l[i] ∈ S := fun i hi => (Finset.mem_toList).mp (List.getElem_mem hi)
  have ne : ∀ i j (hi : i < l.length) (hj : j < l.length), i ≠ j → l[i] ≠ l[j] := fun i j hi hj hij e =>
    hij ((List.Nodup.getElem_inj_iff hn).mp e)
  exact ⟨_, mem 0 (by omega), _, mem 1 (by omega), _, mem 2 (by omega), _, mem 3 (by omega), _, mem 4 (by omega),
    ne 0 1 (by omega) (by omega) (by omega), ne 0 2 (by omega) (by omega) (by omega),
    ne 0 3 (by omega) (by omega) (by omega), ne 0 4 (by omega) (by omega) (by omega),
    ne 1 2 (by omega) (by omega) (by omega), ne 1 3 (by omega) (by omega) (by omega),
    ne 1 4 (by omega) (by omega) (by omega), ne 2 3 (by omega) (by omega) (by omega),
    ne 2 4 (by omega) (by omega) (by omega), ne 3 4 (by omega) (by omega) (by omega)⟩

/-- **(F3)** at most four live rows: the transpose is a generalized B-form with `B` = the live rows -/
theorem bform_F3 (r : Fin 104 → Fin 8 → K) (hr : ∀ a b : Fin 104, ((dot a b : ℤ) : K) = 9 / 4 * (r a ⬝ᵥ r b))
    (F : Matrix (Fin 8) (Fin 9) K) (hF : ∀ x : Fin 104, F *ᵥ rho K x = r x)
    (N : Matrix (Fin 104) (Fin 104) K) (P c : ℕ → Fin 9 → K) (lam eta : ℕ → K)
    (hN : ∀ v s : Fin 104, N v s = P v ⬝ᵥ c s + lam v * eta s)
    (hcol : ∀ s < 104, ∃ b : K, c s = b • rho K s)
    (hrowd : ∀ v < 104, lam v = 0 → ∃ a : K, P v = a • rho K v)
    (hPs : ∀ v s : Fin 104, 9 / 4 * (r s ⬝ᵥ (F *ᵥ P v)) = rho K s ⬝ᵥ P v)
    (hdiag : ∀ t, N t t ≠ 0) (hmask : ∀ u s : Fin 104, dot u s = 0 → N u s = 0)
    (hL : (Finset.univ.filter fun v : Fin 104 => lam v ≠ 0).card ≤ 4) :
    ∃ (α cc α' : Fin 104 → K) (Y : Matrix (Fin 104) BForm.C9 K),
      BForm.GenRows r Y (Finset.univ.filter fun v : Fin 104 => lam v ≠ 0) α' ∧
      (Finset.univ.filter fun t => α t = 0).card ≤ 4 ∧ BForm.IsClique r (Finset.univ.filter fun t => α t = 0) ∧
      BForm.Pattern r (BForm.bX r α cc * Yᵀ) ∧ Nᵀ = BForm.bX r α cc * Yᵀ := by
  choose! b hb using hcol
  choose! a ha using hrowd
  set α : Fin 104 → K := fun s => 9 / 4 * b s
  set cc : Fin 104 → K := fun s => eta s
  set α' : Fin 104 → K := fun v => a v
  set Y : Matrix (Fin 104) BForm.C9 K := fun v i => Option.elim i (lam v) (fun k => (F *ᵥ P v) k)
  have hform : Nᵀ = BForm.bX r α cc * Yᵀ := by
    ext s v
    rw [Matrix.transpose_apply, bX_mul_tr_apply, hN, hb s s.2]
    have e := hPs v s
    simp only [Y, Option.elim, α, cc, dotProduct_smul, smul_eq_mul]
    rw [dotProduct_comm (P v) (rho K s)]
    linear_combination (-(b s)) * e
  have hrr : ∀ t : Fin 104, rho K t ⬝ᵥ rho K t = 18 := by
    intro t; rw [rho_dot, dot_self t.2]; norm_num
  have hzero : ∀ s : Fin 104, b s = 0 → lam s ≠ 0 ∧ eta s ≠ 0 := by
    intro s h0
    have e := hdiag s
    rw [hN, hb s s.2, h0, zero_smul, dotProduct_zero, zero_add] at e
    exact ⟨left_ne_zero_of_mul e, right_ne_zero_of_mul e⟩
  refine ⟨α, cc, α', Y, fun v hv => ?_, ?_, fun u hu s hs hus ho => ?_, ⟨fun t => ?_, fun u s hus ho => ?_⟩,
    hform⟩
  · simp only [Finset.mem_filter, Finset.mem_univ, true_and, not_not] at hv
    have hP := ha v v.2 hv
    refine ⟨fun h0 => ?_, fun i => ?_⟩
    · have e := hdiag v
      rw [hN, hP, hv, zero_mul, add_zero, hb v v.2, smul_dotProduct, dotProduct_smul, hrr] at e
      exact e (by simp only [α'] at h0; rw [h0]; simp)
    · cases i with
      | none => simp [Y, BForm.bX, hv]
      | some k => simp only [Y, BForm.bX, Option.elim, α']; rw [hP, Matrix.mulVec_smul, hF]; rfl
  · refine le_trans (Finset.card_le_card fun s hs => ?_) hL
    simp only [Finset.mem_filter, Finset.mem_univ, true_and, α] at hs ⊢
    have : b s = 0 := by
      rcases mul_eq_zero.mp hs with h | h
      · norm_num at h
      · exact h
    exact (hzero s this).1
  · have hbu : b u = 0 := by
      simp only [Finset.mem_filter, Finset.mem_univ, true_and, α] at hu
      rcases mul_eq_zero.mp hu with h | h
      · norm_num at h
      · exact h
    have hbs : b s = 0 := by
      simp only [Finset.mem_filter, Finset.mem_univ, true_and, α] at hs
      rcases mul_eq_zero.mp hs with h | h
      · norm_num at h
      · exact h
    have hd : dot s u = 0 := by
      have h := hr s u
      unfold BForm.Orth at ho
      rw [dotProduct_comm, ho, mul_zero] at h
      exact_mod_cast h
    have e := hmask s u hd
    rw [hN, hb u u.2, hbu, zero_smul, dotProduct_zero, zero_add] at e
    exact mul_ne_zero (hzero s hbs).1 (hzero u hbu).2 e
  · rw [← hform, Matrix.transpose_apply]; exact hdiag t
  · rw [← hform, Matrix.transpose_apply]
    apply hmask
    have h := hr s u
    unfold BForm.Orth at ho
    rw [dotProduct_comm, ho, mul_zero] at h
    exact_mod_cast h

/-- **(F2)** glued rows, columns gramm off a set `Bs` of at most 4 ports, and every column off `Bs` orthogonal to a
live row: a generalized B-form with `B = Bs` (the bent column `U` lies in `Bs`) -/
theorem bform_F2 (r : Fin 104 → Fin 8 → K) (hr : ∀ a b : Fin 104, ((dot a b : ℤ) : K) = 9 / 4 * (r a ⬝ᵥ r b))
    (F : Matrix (Fin 8) (Fin 9) K) (hF : ∀ x : Fin 104, F *ᵥ rho K x = r x)
    (N : Matrix (Fin 104) (Fin 104) K) (P c : ℕ → Fin 9 → K) (lam eta : ℕ → K) (Λ : Fin 9 → K)
    (hN : ∀ v s : Fin 104, N v s = P v ⬝ᵥ c s + lam v * eta s)
    (hrow : ∀ v < 104, ∃ a : K, P v = a • rho K v + lam v • Λ)
    (Bs : Finset (Fin 104)) (hB : Bs.card ≤ 4) (hcol : ∀ s : Fin 104, s ∉ Bs → ∃ b : K, c s = b • rho K s)
    (hcov : ∀ s : Fin 104, s ∉ Bs → ∃ v : Fin 104, lam v ≠ 0 ∧ dot v s = 0)
    (hcs : ∀ v s : Fin 104, 9 / 4 * (r v ⬝ᵥ (F *ᵥ c s)) = rho K v ⬝ᵥ c s)
    (hdiag : ∀ t, N t t ≠ 0) (hmask : ∀ u s : Fin 104, dot u s = 0 → N u s = 0) :
    ∃ (α cc α' : Fin 104 → K) (Y : Matrix (Fin 104) BForm.C9 K), BForm.GenRows r Y Bs α' ∧
      (Finset.univ.filter fun t => α t = 0).card ≤ 4 ∧ BForm.IsClique r (Finset.univ.filter fun t => α t = 0) ∧
      BForm.Pattern r (BForm.bX r α cc * Yᵀ) ∧ N = BForm.bX r α cc * Yᵀ := by
  choose! a ha using hrow
  set α : Fin 104 → K := fun v => 9 / 4 * a v
  set cc : Fin 104 → K := fun v => lam v
  set Y : Matrix (Fin 104) BForm.C9 K := fun s i => Option.elim i (Λ ⬝ᵥ c s + eta s) (fun k => (F *ᵥ c s) k)
  have hform : N = BForm.bX r α cc * Yᵀ := by
    ext v s
    rw [bX_mul_tr_apply, hN, ha v v.2]
    have e := hcs v s
    simp only [Y, Option.elim, α, cc, add_dotProduct, smul_dotProduct, smul_eq_mul]
    linear_combination (-(a v)) * e
  have hent : ∀ v s : Fin 104, N v s = lam v * (Λ ⬝ᵥ c s + eta s) + α v * (r v ⬝ᵥ (F *ᵥ c s)) := by
    intro v s; simp only [hform, bX_mul_tr_apply, Y, Option.elim, cc]
  -- a row with `a = 0`
  have hrow0 : ∀ v s : Fin 104, a v = 0 → N v s = lam v * (Λ ⬝ᵥ c s + eta s) := by
    intro v s h0
    rw [hent]; simp only [α, h0, mul_zero, zero_mul, add_zero]
  -- off `Bs`: the lift coordinate of the column vanishes
  have hY0 : ∀ s : Fin 104, s ∉ Bs → Λ ⬝ᵥ c s + eta s = 0 := by
    intro s hs
    obtain ⟨b, hb⟩ := hcol s hs
    obtain ⟨v, hv, hvs⟩ := hcov s hs
    have e := hmask v s hvs
    rw [hN, ha v v.2, hb] at e
    simp only [add_dotProduct, smul_dotProduct, dotProduct_smul, smul_eq_mul, rho_dot, hvs, Int.cast_zero] at e
    have : lam v * (b * (Λ ⬝ᵥ rho K s) + eta s) = 0 := by linear_combination e
    rw [hb, dotProduct_smul, smul_eq_mul]
    exact (mul_eq_zero.mp this).resolve_left hv
  refine ⟨α, cc, fun s => (c s ⬝ᵥ rho K s) / 18, Y, fun s hs => ?_, ?_, fun u hu s hs hus ho => ?_,
    ⟨fun t => ?_, fun u s hus ho => ?_⟩, hform⟩
  · obtain ⟨b, hb⟩ := hcol s hs
    have hbe : (c s ⬝ᵥ rho K s) / 18 = b := by
      rw [hb, smul_dotProduct, rho_dot, dot_self s.2, smul_eq_mul]; push_cast
      exact mul_div_cancel_right₀ b (by norm_num)
    refine ⟨fun h0 => ?_, fun i => ?_⟩
    · have h0' : b = 0 := by rw [← hbe]; exact h0
      apply hdiag s
      rw [hN, hb, h0', zero_smul, dotProduct_zero, zero_add]
      have := hY0 s hs
      rw [hb, h0', zero_smul, dotProduct_zero, zero_add] at this
      rw [this, mul_zero]
    · cases i with
      | none => simp only [Y, BForm.bX, Option.elim]; exact hY0 s hs
      | some k =>
        simp only [Y, BForm.bX, Option.elim]
        rw [hbe, hb, Matrix.mulVec_smul, hF]; rfl
  · refine le_trans (Finset.card_le_card fun v hv => ?_) hB
    simp only [Finset.mem_filter, Finset.mem_univ, true_and, α] at hv
    have h0 : a v = 0 := by
      rcases mul_eq_zero.mp hv with h | h
      · norm_num at h
      · exact h
    by_contra hvB
    apply hdiag v
    rw [hrow0 v v h0, hY0 v hvB, mul_zero]
  · simp only [Finset.mem_filter, Finset.mem_univ, true_and, α] at hu hs
    have hu0 : a u = 0 := by
      rcases mul_eq_zero.mp hu with h | h
      · norm_num at h
      · exact h
    have hs0 : a s = 0 := by
      rcases mul_eq_zero.mp hs with h | h
      · norm_num at h
      · exact h
    have hd : dot u s = 0 := by
      have h := hr u s
      unfold BForm.Orth at ho
      rw [ho, mul_zero] at h
      exact_mod_cast h
    have e := hmask u s hd
    rw [hrow0 u s hu0] at e
    have hlu : lam u ≠ 0 := by
      intro hl; apply hdiag u; rw [hrow0 u u hu0, hl, zero_mul]
    have hz : Λ ⬝ᵥ c s + eta s = 0 := (mul_eq_zero.mp e).resolve_left hlu
    apply hdiag s
    rw [hrow0 s s hs0, hz, mul_zero]
  · rw [← hform]; exact hdiag t
  · rw [← hform]
    apply hmask
    have h := hr u s
    unfold BForm.Orth at ho
    rw [ho, mul_zero] at h
    exact_mod_cast h

end RankNine
