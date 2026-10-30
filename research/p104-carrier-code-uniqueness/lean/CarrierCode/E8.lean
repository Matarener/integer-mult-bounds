import Mathlib

/-!
# Search-free uniqueness of the length-8 decoding code: the general steps (E8-PROOF.md)

This file proves the steps of the E8 argument that do not depend on the concrete port data.

* `frame_factor` (step 1): if `M = A * B` with inner dimension 8 and `M` is the identity on a frame `f`, then
  `M = M[:, f] * M[f, :]`.
* `frame_sum` (step 2): consequently the diagonal entry gives `∑_{x ∈ f} M t x * M x t = M t t`.
* `a2_trick` (step 4): in characteristic 3, symmetry along an A2 triangle forces `r_x ⬝ v_t = 0`.
* `coboundary` (step 5): a ±1 function on pairs of `Fin n` with trivial triangle products is a coboundary.
-/

namespace CarrierCode.E8

open Matrix

variable {K : Type*} [Field K] {L : Type*}

/-- Step 1. A rank-8 factorisation that is the identity on a frame factors through that frame. -/
theorem frame_factor (A : Matrix L (Fin 8) K) (B : Matrix (Fin 8) L K) (f : Fin 8 → L)
    (hf : (A * B).submatrix f f = 1) :
    A * B = (A * B).submatrix id f * (A * B).submatrix f id := by
  have h1 : A.submatrix f id * B.submatrix id f = 1 := by
    rw [← hf]; ext i j; simp [Matrix.mul_apply]
  have h2 : B.submatrix id f * A.submatrix f id = 1 := mul_eq_one_comm.mp h1
  have e1 : (A * B).submatrix id f = A * B.submatrix id f := by ext i j; simp [Matrix.mul_apply]
  have e2 : (A * B).submatrix f id = A.submatrix f id * B := by ext i j; simp [Matrix.mul_apply]
  rw [e1, e2, Matrix.mul_assoc, ← Matrix.mul_assoc (B.submatrix id f), h2, Matrix.one_mul]

/-- Step 2. The frame sums of `N t x = M t x * M x t`. -/
theorem frame_sum (A : Matrix L (Fin 8) K) (B : Matrix (Fin 8) L K) (f : Fin 8 → L)
    (hf : (A * B).submatrix f f = 1) (t : L) :
    ∑ k, (A * B) t (f k) * (A * B) (f k) t = (A * B) t t := by
  conv_rhs => rw [frame_factor A B f hf]
  simp [Matrix.mul_apply]

/-- Step 4. The A2 trick: `r_y = r_t - r_x`, each `v_a ⟂ r_a`, and the symmetry relations along the triangle force
`r_x ⬝ v_t = 0` in characteristic 3. -/
theorem a2_trick {n : Type*} [Fintype n] (rt rx ry vt vx vy : n → ZMod 3) (hy : ry = rt - rx)
    (ht : rt ⬝ᵥ vt = 0) (hx : rx ⬝ᵥ vx = 0) (hyy : ry ⬝ᵥ vy = 0)
    (stx : rx ⬝ᵥ vt = rt ⬝ᵥ vx) (sty : ry ⬝ᵥ vt = rt ⬝ᵥ vy) (sxy : rx ⬝ᵥ vy = ry ⬝ᵥ vx) :
    rx ⬝ᵥ vt = 0 := by
  subst hy
  have a : (rt - rx) ⬝ᵥ vt = -(rx ⬝ᵥ vt) := by rw [sub_dotProduct, ht, zero_sub]
  have b : rt ⬝ᵥ vy = rx ⬝ᵥ vy := by
    have : rt = (rt - rx) + rx := by abel
    rw [this, add_dotProduct, hyy, zero_add]
  have c : (rt - rx) ⬝ᵥ vx = rt ⬝ᵥ vx := by rw [sub_dotProduct, hx, sub_zero]
  have key : -(rx ⬝ᵥ vt) = rx ⬝ᵥ vt := by rw [← a, sty, b, sxy, c, ← stx]
  have h2 : (2 : ZMod 3) * (rx ⬝ᵥ vt) = 0 := by linear_combination -key
  have h2' : (2 : ZMod 3) ≠ 0 := by decide
  exact (mul_eq_zero.mp h2).resolve_left h2'

/-- Step 5. On a complete graph, a sign function with trivial triangle products is a coboundary. -/
theorem coboundary {n : ℕ} (ρ : Fin (n + 1) → Fin (n + 1) → ℤˣ) (hsym : ∀ a b, ρ a b = ρ b a)
    (htri : ∀ a b c, ρ a b * ρ b c * ρ c a = 1) :
    ∃ d : Fin (n + 1) → ℤˣ, ∀ a b, ρ a b = d a * d b := by
  refine ⟨fun a => ρ 0 a, fun a b => ?_⟩
  have hu : ∀ u : ℤˣ, u * u = 1 := fun u => Int.units_mul_self u
  have h := htri 0 a b
  rw [hsym b 0] at h
  calc ρ a b = (ρ 0 a * ρ 0 a) * ρ a b * (ρ 0 b * ρ 0 b) := by rw [hu, hu, one_mul, mul_one]
    _ = ρ 0 a * (ρ 0 a * ρ a b * ρ 0 b) * ρ 0 b := by group
    _ = ρ 0 a * ρ 0 b := by rw [h, mul_one]

end CarrierCode.E8
