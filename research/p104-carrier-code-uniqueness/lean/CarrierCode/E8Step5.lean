import CarrierCode.E8Step4
import CarrierCode.E8Defs5

/-!
# Step 5: signs

With `M` symmetric, `±1` off the conflict pattern, and `M = M[:, T] M[T, :]` for the frame `T`, the frame
coordinates `X j s = M j (T s)` satisfy `X j s = c_j d_s E j s` where `E j s = 2 r_j ⬝ r_{T s}`.  The pair products
`P j s s'` are constant along the checked trees (orthogonality and opposite signs), their triangle products are `1`,
so they form a coboundary `d_s d_s'`.  Hence `M = D (2 Gm) D` with `D = ±1`.
-/

namespace CarrierCode.E8

open Matrix

variable {M : Matrix ι ι (ZMod 3)} {A : Matrix ι (Fin 8) (ZMod 3)} {B : Matrix (Fin 8) ι (ZMod 3)}

def fT' : Fin 759 := ⟨fT, by decide⟩
def T (s : Fin 8) : ι := fr fT s
def E (j : ι) (s : Fin 8) : ZMod 3 := 2 * Gm j (T s)
def X (M : Matrix ι ι (ZMod 3)) (j : ι) (s : Fin 8) : ZMod 3 := M j (T s)
def P (M : Matrix ι ι (ZMod 3)) (j : ι) (s s' : Fin 8) : ZMod 3 := X M j s * X M j s' * E j s * E j s'

theorem sq_one_of_ne (a : ZMod 3) (h : a ≠ 0) : a * a = 1 := by revert a; decide

theorem T_val (hF : framesOK) (s : Fin 8) : (T s).val = Tn s := toι_val ((hF fT').2 s s).1

theorem En_cast (hF : framesOK) (j : ι) (s : Fin 8) : ((En j s : ℕ) : ZMod 3) = E j s := by
  rw [En, cast_mod]; push_cast; rw [dotN_cast, E, Gm, T_val hF]

theorem E_ne (hF : framesOK) {j : ι} {s : Fin 8} (h : En j s ≠ 0) : E j s ≠ 0 := by
  rw [← En_cast hF]; intro e; apply h
  have := (cast_eq_zero_iff _).mp e
  unfold En at this ⊢; omega

theorem E_eq (hF : framesOK) {j : ι} {s : Fin 8} (h : En j s = 0) : E j s = 0 := by
  rw [← En_cast hF, h, Nat.cast_zero]

theorem M_symm (h : Hyp M A B) (hC : Checks3) (h4 : step4OK) (j k : ι) : M j k = M k j := by
  by_cases hjk : j = k
  · subst hjk; rfl
  by_cases hz : dotN j k % 3 = 0
  · have g : Gm j k = 0 := by rw [Gm, ← dotN_cast]; exact (cast_eq_zero_iff _).mpr hz
    rw [h.conf j k hjk g, h.conf k j (Ne.symm hjk) (by rw [Gm_comm]; exact g)]
  · exact (M_symm_pm h hC h4 hz).1.symm

theorem M_fac (h : Hyp M A B) (hC : Checks3) (h4 : step4OK) (j k : ι) :
    M j k = ∑ s, X M j s * X M k s := by
  have hm := frame_mat h hC.1 fT'
  rw [h.fac] at hm
  have e := frame_factor A B (fr fT') hm
  rw [← h.fac] at e
  rw [congrFun (congrFun e j) k, mul_apply]
  refine Finset.sum_congr rfl fun s _ => ?_
  simp only [submatrix_apply, id, X, T]
  rw [M_symm h hC h4 (fr fT' s) k]; rfl

theorem X_sq (h : Hyp M A B) (hC : Checks3) (h4 : step4OK) (h5 : check5) (j : ι) (s : Fin 8) :
    X M j s * X M j s = E j s * E j s := by
  simp only [X, E]
  by_cases hjt : j = T s
  · rw [hjt, h.diag]
    have hd := h5.1 (T s)
    have : Gm (T s) (T s) = 2 := by
      rw [Gm, ← dotN_cast, ← cast_mod, hd]; rfl
    rw [this]; decide
  by_cases hz : dotN j (T s) % 3 = 0
  · have g : Gm j (T s) = 0 := by rw [Gm, ← dotN_cast]; exact (cast_eq_zero_iff _).mpr hz
    rw [h.conf j (T s) hjt g, g]; ring
  · rw [(M_symm_pm h hC h4 hz).2]
    have := sq_one_of_ne _ (Gm_ne hz)
    have h3 : (3 : ZMod 3) = 0 := by decide
    linear_combination (-4 : ZMod 3) * this - h3

section
variable (h : Hyp M A B) (hC : Checks3) (h4 : step4OK) (h5 : check5)
include h hC h4 h5

theorem X_zero {j : ι} {s : Fin 8} (hE : E j s = 0) : X M j s = 0 := by
  have := X_sq h hC h4 h5 j s
  rw [hE, mul_zero] at this
  exact mul_self_eq_zero.mp this

theorem X_one {j : ι} {s : Fin 8} (hE : E j s ≠ 0) : X M j s * X M j s = 1 := by
  rw [X_sq h hC h4 h5, sq_one_of_ne _ hE]

omit h hC h4 h5 in
theorem edge_alg' (a b c d e1 e2 e3 e4 : ZMod 3) (H : a * c + b * d = 0) (Hs : e1 * e2 + e3 * e4 = 0)
    (hb : b * b = 1) (hc : c * c = 1) : a * b * e1 * e2 = c * d * e3 * e4 := by
  linear_combination e1 * e2 * (b * c * H - a * b * hc - c * d * hb) - c * d * Hs

/-- One tree edge: orthogonal ports sharing exactly `s, s'` with opposite signs have equal pair products. -/
theorem edge {j k : ι} {s s' : Fin 8} (hss : s ≠ s') (hjk : k ≠ j) (hort : dotN j k % 3 = 0)
    (hks : En k s ≠ 0) (_hks' : En k s' ≠ 0) (_hjs : En j s ≠ 0) (hjs' : En j s' ≠ 0)
    (hu : ∀ u : Fin 8, u.val ≠ s.val → u.val ≠ s'.val → (En j u * En k u) % 3 = 0)
    (hsg : (En j s * En j s' + En k s * En k s') % 3 = 0) :
    P M j s s' = P M k s s' := by
  have hF := hC.1
  have hM : M j k = 0 := h.conf j k (Ne.symm hjk) (by rw [Gm, ← dotN_cast]; exact (cast_eq_zero_iff _).mpr hort)
  rw [M_fac h hC h4] at hM
  rw [Fintype.sum_eq_add s s' hss] at hM
  · have hs := congrArg (fun n : ℕ => (n : ZMod 3)) hsg
    simp only [cast_mod] at hs
    push_cast at hs
    simp only [En_cast hF] at hs
    exact edge_alg' _ _ _ _ _ _ _ _ hM hs (X_one h hC h4 h5 (E_ne hF hjs')) (X_one h hC h4 h5 (E_ne hF hks))
  · intro u ⟨hu1, hu2⟩
    have e := hu u (fun e => hu1 (Fin.ext e)) (fun e => hu2 (Fin.ext e))
    have e' := congrArg (fun n : ℕ => (n : ZMod 3)) e
    simp only [cast_mod] at e'
    push_cast at e'
    simp only [En_cast hF] at e'
    rcases mul_eq_zero.mp e' with z | z
    · rw [X_zero h hC h4 h5 z, zero_mul]
    · rw [X_zero h hC h4 h5 z, mul_zero]

/-- Pair products are constant along the trees. -/
theorem P_const (s s' : Fin 8) (hss : s ≠ s') :
    ∀ n, ∀ j : ι, trD s s' j = n → En j s ≠ 0 → En j s' ≠ 0 → P M j s s' = P M (toι (rt5 s s')) s s' := by
  intro n
  induction n with
  | zero =>
    intro j hd hjs hjs'
    have e := (h5.2.2.1 s s' hss j hjs hjs').1 hd
    have : toι (rt5 s s') = j := by rw [← e]; exact Fin.ext (toι_val j.isLt)
    rw [this]
  | succ n ih =>
    intro j hd hjs hjs'
    obtain ⟨hk, hdk, hks, hks', hkj, hort, hu, hsg⟩ := (h5.2.2.1 s s' hss j hjs hjs').2 (by omega)
    have ek : ((toι (trP s s' j) : ι) : ℕ) = trP s s' j := toι_val hk
    rw [← ek] at hks hks' hkj hort hu hsg hdk
    rw [edge h hC h4 h5 hss (fun e => hkj (by rw [e])) hort hks hks' hjs hjs' hu hsg]
    exact ih _ (by omega) hks hks'

def ρ (M : Matrix ι ι (ZMod 3)) (s s' : Fin 8) : ZMod 3 := P M (toι (rt5 s s')) s s'

theorem P_rho {s s' : Fin 8} (hss : s ≠ s') {j : ι} (hjs : En j s ≠ 0) (hjs' : En j s' ≠ 0) :
    P M j s s' = ρ M s s' := P_const h hC h4 h5 s s' hss _ j rfl hjs hjs'

theorem P_sq {j : ι} {s s' : Fin 8} (hjs : En j s ≠ 0) (hjs' : En j s' ≠ 0) : P M j s s' * P M j s' s = 1 := by
  have hF := hC.1
  have a := X_one h hC h4 h5 (E_ne hF hjs); have b := X_one h hC h4 h5 (E_ne hF hjs')
  have c := sq_one_of_ne _ (E_ne hF hjs); have d := sq_one_of_ne _ (E_ne hF hjs')
  simp only [P]
  have : X M j s * X M j s' * E j s * E j s' * (X M j s' * X M j s * E j s' * E j s) =
    (X M j s * X M j s) * (X M j s' * X M j s') * (E j s * E j s) * (E j s' * E j s') := by ring
  rw [this, a, b, c, d]; ring

theorem P_tri {j : ι} {s s' s'' : Fin 8} (h1 : En j s ≠ 0) (h2 : En j s' ≠ 0) (h3 : En j s'' ≠ 0) :
    P M j s s' * P M j s' s'' * P M j s'' s = 1 := by
  have hF := hC.1
  have a := X_one h hC h4 h5 (E_ne hF h1); have b := X_one h hC h4 h5 (E_ne hF h2)
  have c := X_one h hC h4 h5 (E_ne hF h3)
  have a' := sq_one_of_ne _ (E_ne hF h1); have b' := sq_one_of_ne _ (E_ne hF h2)
  have c' := sq_one_of_ne _ (E_ne hF h3)
  simp only [P]
  have : X M j s * X M j s' * E j s * E j s' * (X M j s' * X M j s'' * E j s' * E j s'') *
      (X M j s'' * X M j s * E j s'' * E j s) =
    (X M j s * X M j s) * (X M j s' * X M j s') * (X M j s'' * X M j s'') *
      (E j s * E j s) * (E j s' * E j s') * (E j s'' * E j s'') := by ring
  rw [this, a, b, c, a', b', c']; ring

theorem rho_symm {s s' : Fin 8} (hss : s ≠ s') : ρ M s s' = ρ M s' s := by
  obtain ⟨hr, h1, h2⟩ := h5.2.1 s s' hss
  have e : ((toι (rt5 s s') : ι) : ℕ) = rt5 s s' := toι_val hr
  rw [← e] at h1 h2
  rw [ρ, ← P_rho h hC h4 h5 (Ne.symm hss) h2 h1]
  simp only [P]; ring

theorem rho_sq {s s' : Fin 8} (hss : s ≠ s') : ρ M s s' * ρ M s s' = 1 := by
  obtain ⟨hr, h1, h2⟩ := h5.2.1 s s' hss
  have e : ((toι (rt5 s s') : ι) : ℕ) = rt5 s s' := toι_val hr
  rw [← e] at h1 h2
  have := P_sq h hC h4 h5 h1 h2
  have hc : P M (toι (rt5 s s')) s' s = P M (toι (rt5 s s')) s s' := by simp only [P]; ring
  rw [hc] at this; exact this

def dd (M : Matrix ι ι (ZMod 3)) (s : Fin 8) : ZMod 3 := if s = 0 then 1 else ρ M 0 s

theorem dd_sq (s : Fin 8) : dd M s * dd M s = 1 := by
  unfold dd; split_ifs with hs
  · ring
  · exact rho_sq h hC h4 h5 (Ne.symm hs)

theorem rho_cob {s s' : Fin 8} (hss : s ≠ s') : ρ M s s' = dd M s * dd M s' := by
  have hF := hC.1
  by_cases h0 : s = 0
  · subst h0; simp [dd, Ne.symm hss]
  by_cases h0' : s' = 0
  · subst h0'
    rw [rho_symm h hC h4 h5 hss]
    show ρ M 0 s = (if s = 0 then 1 else ρ M 0 s) * (if (0 : Fin 8) = 0 then 1 else ρ M 0 0)
    rw [if_neg h0, if_pos rfl, mul_one]
  obtain ⟨hw, w0, ws, ws'⟩ := h5.2.2.2.1 s s' (fun e => h0 (Fin.ext e)) (fun e => h0' (Fin.ext e)) hss
  have e : ((toι (triW s s') : ι) : ℕ) = triW s s' := toι_val hw
  rw [← e] at w0 ws ws'
  have p1 := P_rho h hC h4 h5 (Ne.symm h0) w0 ws
  have p2 := P_rho h hC h4 h5 hss ws ws'
  have p3 := P_rho h hC h4 h5 (Ne.symm h0') w0 ws'
  have t := P_tri h hC h4 h5 (s := 0) (s' := s) (s'' := s') w0 ws ws'
  have c3 : P M (toι (triW s s')) s' 0 = P M (toι (triW s s')) 0 s' := by simp only [P]; ring
  rw [c3, p1, p2, p3] at t
  have hp := rho_sq h hC h4 h5 (Ne.symm h0)
  have hu := rho_sq h hC h4 h5 (Ne.symm h0')
  show ρ M s s' = (if s = 0 then 1 else ρ M 0 s) * (if s' = 0 then 1 else ρ M 0 s')
  rw [if_neg h0, if_neg h0']
  generalize ρ M 0 s = a at t hp ⊢
  generalize ρ M 0 s' = b at t hu ⊢
  generalize ρ M s s' = q at t ⊢
  linear_combination a * b * t - q * b * b * hp - q * hu

def s0 (j : ι) : Fin 8 := ⟨sup0 j % 8, Nat.mod_lt _ (by norm_num)⟩
def cc (M : Matrix ι ι (ZMod 3)) (j : ι) : ZMod 3 := X M j (s0 j) * E j (s0 j) * dd M (s0 j)

omit h hC h4 in
theorem s0_ne (j : ι) : En j (s0 j) ≠ 0 := by
  obtain ⟨hl, hne⟩ := h5.2.2.2.2.1 j
  simp only [s0, Nat.mod_eq_of_lt hl]; exact hne

theorem X_form (j : ι) (s : Fin 8) : X M j s = cc M j * dd M s * E j s := by
  have hF := hC.1
  by_cases hE : En j s = 0
  · rw [X_zero h hC h4 h5 (E_eq hF hE), E_eq hF hE, mul_zero]
  have he := sq_one_of_ne _ (E_ne hF hE)
  have hd := dd_sq h hC h4 h5 s
  by_cases hs : s0 j = s
  · rw [cc, hs]
    linear_combination (-(X M j s * dd M s * dd M s)) * he - X M j s * hd
  · have H := P_rho h hC h4 h5 hs (s0_ne h5 j) hE
    rw [rho_cob h hC h4 h5 hs] at H
    simp only [P] at H
    have hx0 := X_one h hC h4 h5 (E_ne hF (s0_ne h5 j))
    have he0 := sq_one_of_ne _ (E_ne hF (s0_ne h5 j))
    rw [cc]
    linear_combination (-(X M j s * E j (s0 j) * E j (s0 j) * E j s * E j s)) * hx0 -
      X M j s * E j s * E j s * he0 - X M j s * he + X M j (s0 j) * E j (s0 j) * E j s * H

theorem cc_sq (j : ι) : cc M j * cc M j = 1 := by
  have hF := hC.1
  have a := X_one h hC h4 h5 (E_ne hF (s0_ne h5 j))
  have b := sq_one_of_ne _ (E_ne hF (s0_ne h5 j))
  have c := dd_sq h hC h4 h5 (s0 j)
  simp only [cc]
  linear_combination (E j (s0 j) * E j (s0 j) * dd M (s0 j) * dd M (s0 j)) * a +
    dd M (s0 j) * dd M (s0 j) * b + c

omit h h4 in
theorem gram (j k : ι) : ∑ s, E j s * E k s = 2 * Gm j k := by
  have hF := hC.1
  have e := h5.2.2.2.2.2 j k
  rw [sum_range8] at e
  have e' := congrArg (fun n : ℕ => (n : ZMod 3)) e
  simp only [cast_mod] at e'
  push_cast at e'
  simp only [En_cast hF] at e'
  rw [e', dotN_cast]; rfl

/-- **Step 5.** Every decoding matrix is `D (2 Gm) D` with `D = ±1`. -/
theorem signs : ∃ D : ι → ZMod 3, (∀ j, D j * D j = 1) ∧ ∀ j k, M j k = D j * D k * (2 * Gm j k) := by
  refine ⟨cc M, cc_sq h hC h4 h5, fun j k => ?_⟩
  rw [M_fac h hC h4, ← gram hC h5, Finset.mul_sum]
  refine Finset.sum_congr rfl fun s _ => ?_
  rw [X_form h hC h4 h5 j s, X_form h hC h4 h5 k s]
  have hd := dd_sq h hC h4 h5 s
  linear_combination cc M j * cc M k * E j s * E k s * hd

end

end CarrierCode.E8
