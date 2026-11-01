import RankNine.Gram

/-!
# T3.2: every row along a frame of the dead set, dead rows and dead columns

Fix a frame `f` inside the reduced dead set `Z` (bits of `zm`, `GramP` on `Z × Z` from T3.1).  With
`c s = Σ_k (M f_k s / d f_k / 18) ρ_{f_k}` and `P v = Σ_k (M v f_k / g f_k) ρ_{f_k}` (vectors in `K⁹`, roots `ρ` in A8
coordinates) every entry is
  `M v s = P v ⬝ c s + λ v η s`  (`λ = 0` on dead rows),
and `P x = d x ρ x`, `c s = (g s / 18) ρ s` for `x, s ∈ Z`.  Only the frame expansion of a vector orthogonal to `u`
and to the frame columns (`orth_frame_eq_zero`) and the integer frame identity `18 ρ_x = Σ_k (ρ_x·ρ_{f_k}) ρ_{f_k}`
are used.
-/

namespace RankNine

open Matrix

theorem root_length (x : ℕ) : (root x).length = 9 := by
  unfold root rootOf; dsimp only; split <;> simp

theorem dotL_sum : ∀ (a b : List ℤ) (n : ℕ), a.length = n → b.length = n →
    dotL a b = ∑ i : Fin n, a.getD i 0 * b.getD i 0
  | [], _, n, ha, _ => by subst ha; show (0 : ℤ) = _; simp
  | _ :: _, [], n, ha, hb => by simp only [List.length_cons, List.length_nil] at ha hb; omega
  | x :: a, y :: b, n, ha, hb => by
    cases n with
    | zero => simp at ha
    | succ n =>
      simp only [List.length_cons, Nat.add_right_cancel_iff] at ha hb
      rw [Fin.sum_univ_succ, show dotL (x :: a) (y :: b) = x * y + dotL a b from rfl, dotL_sum a b n ha hb]
      simp

variable (K : Type*) [Field K]

/-- an integer list as a vector of `K⁹` -/
def vK (a : List ℤ) : Fin 9 → K := fun i => ((a.getD i 0 : ℤ) : K)

/-- root of line `x` as a vector of `K⁹` -/
def rho (x : ℕ) : Fin 9 → K := vK K (root x)

variable {K}

theorem vK_dot (a b : List ℤ) (ha : a.length = 9) (hb : b.length = 9) :
    vK K a ⬝ᵥ vK K b = ((dotL a b : ℤ) : K) := by
  simp only [dotProduct, vK, dotL_sum a b 9 ha hb, Int.cast_sum, Int.cast_mul]

theorem rho_dot (x y : ℕ) : rho K x ⬝ᵥ rho K y = ((dot x y : ℤ) : K) :=
  vK_dot _ _ (root_length x) (root_length y)

def dotSelfOK : Bool := (List.range 104).all fun x => dot x x == 18

theorem dotSelf_ok : dotSelfOK = true := by decide +kernel

theorem dot_self {x : ℕ} (hx : x < 104) : dot x x = 18 := by
  have h := dotSelf_ok
  simp only [dotSelfOK, List.all_eq_true, List.mem_range, beq_iff_eq] at h
  exact h x hx

theorem frame_rho_dot (f : ℕ) (k l : Fin 8) :
    rho K (frL f k) ⬝ᵥ rho K (frL f l) = if k = l then 18 else 0 := by
  rw [rho_dot]
  split_ifs with h
  · subst h; rw [dot_self (frame_lt f k.2)]; norm_num
  · have ho := frame_orth f k.2 l.2 (fun e => h (Fin.ext e))
    have : dot (frL f k) (frL f l) = 0 := by simpa [orth] using ho
    rw [this]; simp

/-- frame identity `18 ρ_x = Σ_k (ρ_x·ρ_{f_k}) ρ_{f_k}` for every line, coordinatewise -/
def fvecOK (f : ℕ) : Bool :=
  (List.range 104).all fun x => (List.range 9).all fun i =>
    18 * (root x).getD i 0 == s8 (fun k => dot x (frL f k) * (root (frL f k)).getD i 0)

theorem fvec {f : ℕ} (h : fvecOK f = true) {x : ℕ} (hx : x < 104) :
    ∑ k : Fin 8, ((dot x (frL f k) : ℤ) : K) • rho K (frL f k) = (18 : K) • rho K x := by
  simp only [fvecOK, List.all_eq_true, List.mem_range, beq_iff_eq] at h
  funext i
  have hi := h x hx i i.2
  simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, rho, vK]
  rw [← s8_eq] at hi
  have hc := congrArg (fun z : ℤ => (z : K)) hi
  simp only [Int.cast_mul, Int.cast_sum, Int.cast_ofNat] at hc
  exact hc.symm

section rep

variable [CharZero K]

/-- expansion of an arbitrary row along a frame of dead rows and a vector `e` with `e ⬝ u ≠ 0` -/
theorem gen_expansion (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (F : Fin 8 → ℕ)
    (hdead : ∀ k, A (F k) ⬝ᵥ u = 0) (hdiag : ∀ k, A (F k) ⬝ᵥ B (F k) ≠ 0)
    (hoff : ∀ k l, k ≠ l → A (F k) ⬝ᵥ B (F l) = 0) (e : Fin 9 → K) (he : e ⬝ᵥ u ≠ 0) (v s : ℕ) :
    A v ⬝ᵥ B s = ∑ k, (A v ⬝ᵥ B (F k)) * (A (F k) ⬝ᵥ B s) / (A (F k) ⬝ᵥ B (F k)) +
      (A v ⬝ᵥ u) / (e ⬝ᵥ u) *
        (e ⬝ᵥ B s - ∑ k, (e ⬝ᵥ B (F k)) * (A (F k) ⬝ᵥ B s) / (A (F k) ⬝ᵥ B (F k))) := by
  set lam := (A v ⬝ᵥ u) / (e ⬝ᵥ u) with hlam
  set z := A v - lam • e with hz
  have hzu : z ⬝ᵥ u = 0 := by
    rw [hz, sub_dotProduct, smul_dotProduct, smul_eq_mul, hlam, div_mul_cancel₀ _ he, sub_self]
  set c : Fin 8 → K := fun k => (z ⬝ᵥ B (F k)) / (A (F k) ⬝ᵥ B (F k)) with hc
  have hw : z - ∑ k, c k • A (F k) = 0 := by
    apply orth_frame_eq_zero A B u hu F hdead hdiag hoff
    · rw [sub_dotProduct, sum_dotProduct]
      simp [smul_dotProduct, hdead, hzu]
    · intro l
      rw [sub_dotProduct, sum_dotProduct, Finset.sum_eq_single l]
      · rw [smul_dotProduct, smul_eq_mul, hc]
        field_simp [hdiag l]
        ring
      · intro k _ hk; rw [smul_dotProduct, hoff k l hk, smul_zero]
      · simp
  have hz' : z = ∑ k, c k • A (F k) := sub_eq_zero.mp hw
  have hAv : A v = lam • e + ∑ k, c k • A (F k) := by
    rw [← hz', hz]; abel
  have hzB : ∀ k, z ⬝ᵥ B (F k) = A v ⬝ᵥ B (F k) - lam * (e ⬝ᵥ B (F k)) := fun k => by
    rw [hz, sub_dotProduct, smul_dotProduct, smul_eq_mul]
  have key : ∑ k, c k * (A (F k) ⬝ᵥ B s) =
      ∑ k, (A v ⬝ᵥ B (F k)) * (A (F k) ⬝ᵥ B s) / (A (F k) ⬝ᵥ B (F k)) -
        lam * ∑ k, (e ⬝ᵥ B (F k)) * (A (F k) ⬝ᵥ B s) / (A (F k) ⬝ᵥ B (F k)) := by
    rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun k _ => ?_
    simp only [hc, hzB]
    ring
  calc A v ⬝ᵥ B s = (lam • e + ∑ k, c k • A (F k)) ⬝ᵥ B s := by rw [← hAv]
    _ = lam * (e ⬝ᵥ B s) + ∑ k, c k * (A (F k) ⬝ᵥ B s) := by
      rw [add_dotProduct, smul_dotProduct, smul_eq_mul, sum_dotProduct]
      simp only [smul_dotProduct, smul_eq_mul]
    _ = _ := by rw [key]; ring

/-- column vector `c s` along frame `f` -/
def cS (A B : ℕ → Fin 9 → K) (g : ℕ → K) (f s : ℕ) : Fin 9 → K :=
  ∑ k : Fin 8, (Mx A B (frL f k) s / dS A B g (frL f k) / 18) • rho K (frL f k)

/-- row vector `P v` along frame `f` -/
def PV (A B : ℕ → Fin 9 → K) (g : ℕ → K) (f v : ℕ) : Fin 9 → K :=
  ∑ k : Fin 8, (Mx A B v (frL f k) / g (frL f k)) • rho K (frL f k)

theorem PV_cS (A B : ℕ → Fin 9 → K) (g : ℕ → K) (f v s : ℕ) :
    PV A B g f v ⬝ᵥ cS A B g f s =
      ∑ k : Fin 8, Mx A B v (frL f k) / g (frL f k) * (Mx A B (frL f k) s / dS A B g (frL f k) / 18) * 18 := by
  unfold PV cS
  simp only [sum_dotProduct, dotProduct_sum, smul_dotProduct, dotProduct_smul, smul_eq_mul, frame_rho_dot,
    mul_ite, mul_zero, Finset.sum_ite_eq, Finset.mem_univ, ↓reduceIte]
  refine Finset.sum_congr rfl fun k _ => ?_
  ring

theorem dS_ne (A B : ℕ → Fin 9 → K) (g : ℕ → K) (hg : ∀ x, g x ≠ 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    {x : ℕ} (hx : x < 104) : dS A B g x ≠ 0 :=
  div_ne_zero (hdiag x hx) (hg x)

/-- **T3.2.** Every entry along a frame `f` of `Z`, dead rows and dead columns. -/
theorem rows_rep (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (g : ℕ → K) (hg : ∀ x, g x ≠ 0)
    (zm : ℕ) (hG : ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y)
    (f : ℕ) (hf : ∀ k < 8, m.testBit (frL f k) = true ∧ zm.testBit (frL f k) = true) (hfv : fvecOK f = true) :
    ∃ lam eta : ℕ → K, (∀ v s, Mx A B v s = PV A B g f v ⬝ᵥ cS A B g f s + lam v * eta s) ∧
      (∀ x, m.testBit x = true → lam x = 0) ∧
      (∀ x < 104, zm.testBit x = true → PV A B g f x = dS A B g x • rho K x) ∧
      (∀ s < 104, zm.testBit s = true → cS A B g f s = (g s / 18) • rho K s) := by
  obtain ⟨j, hj⟩ := Function.ne_iff.mp hu
  set e : Fin 9 → K := Pi.single j 1 with hed
  have he : e ⬝ᵥ u ≠ 0 := by rw [hed, single_dotProduct, one_mul]; exact hj
  have hdead : ∀ k : Fin 8, A (frL f k) ⬝ᵥ u = 0 := fun k => hZ _ (hf k k.2).1
  have hdF : ∀ k : Fin 8, A (frL f k) ⬝ᵥ B (frL f k) ≠ 0 := fun k => hdiag _ (frame_lt f k.2)
  have hoff : ∀ k l : Fin 8, k ≠ l → A (frL f k) ⬝ᵥ B (frL f l) = 0 := fun k l hkl =>
    hmask _ (frame_lt f k.2) _ (frame_lt f l.2) (frame_orth f k.2 l.2 (fun e => hkl (Fin.ext e)))
  have hMff : ∀ k : Fin 8, Mx A B (frL f k) (frL f k) = dS A B g (frL f k) * g (frL f k) := fun k =>
    (div_mul_cancel₀ _ (hg _)).symm
  refine ⟨fun v => (A v ⬝ᵥ u) / (e ⬝ᵥ u),
    fun s => e ⬝ᵥ B s - ∑ k : Fin 8, (e ⬝ᵥ B (frL f k)) * (A (frL f k) ⬝ᵥ B s) / (A (frL f k) ⬝ᵥ B (frL f k)),
    fun v s => ?_, fun x hx => ?_, fun x hx hzx => ?_, fun s hs hzs => ?_⟩
  · rw [PV_cS]
    have E := gen_expansion A B u hu (fun k => frL f k) hdead hdF hoff e he v s
    beta_reduce at E
    show A v ⬝ᵥ B s = _
    rw [E]
    congr 1
    refine Finset.sum_congr rfl fun k _ => ?_
    have h1 := hMff k
    have h2 := hg (frL f k)
    have h3 := dS_ne A B g hg hdiag (frame_lt f k.2)
    show Mx A B v (frL f k) * Mx A B (frL f k) s / Mx A B (frL f k) (frL f k) = _
    rw [h1]
    field_simp
    try ring
  · show (A x ⬝ᵥ u) / (e ⬝ᵥ u) = 0
    rw [hZ x hx, zero_div]
  · unfold PV
    have hc : ∀ k : Fin 8, Mx A B x (frL f k) / g (frL f k) = dS A B g x / 18 * ((dot x (frL f k) : ℤ) : K) := by
      intro k
      have G := hG x hx _ (frame_lt f k.2) hzx (hf k k.2).2
      unfold GramP gam at G
      rw [G, mul_div_assoc, div_self (hg _), mul_one]
      ring
    simp only [hc, mul_smul]
    rw [← Finset.smul_sum, fvec hfv hx, smul_smul, div_mul_cancel₀ _ (by norm_num : (18 : K) ≠ 0)]
  · unfold cS
    have hc : ∀ k : Fin 8, Mx A B (frL f k) s / dS A B g (frL f k) / 18 =
        g s / 18 / 18 * ((dot s (frL f k) : ℤ) : K) := by
      intro k
      have G := hG _ (frame_lt f k.2) s hs (hf k k.2).2 hzs
      unfold GramP gam at G
      rw [G, dot_comm (frL f k) s]
      have h3 := dS_ne A B g hg hdiag (frame_lt f k.2)
      field_simp
      try ring
    simp only [hc, mul_smul]
    rw [← Finset.smul_sum, fvec hfv hs, smul_smul, div_mul_cancel₀ _ (by norm_num : (18 : K) ≠ 0)]

end rep

end RankNine
