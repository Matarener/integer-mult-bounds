import RankNine.Transport
import RankNine.GrpData
import RankNine.Zero
import RankNine.FLData

/-!
# Finite facts, frame case (Mark 2026-11-02: finite facts as certified logs)

Finite facts are Boolean functions of stored data; the main theorem takes `fact = true` as hypotheses.  They are
evaluated by `#eval` (compiled code, not the kernel) and by independent Python checks; see `MAIN-PLAN.md`.

* `grpOK`: the 384 stored permutations (with inverses) preserve orthogonality and the label products.
* `orbOK FL`: for every pair of distinct non-zero `z₁, z₂ ∈ F₂⁹` the dead set `C(z₁, z₂)` either is in the list `FL`
  (frameless sets, T2) or contains the image of a framed type representative `typeMask k` under a group element.
  The witness is found by a hash table (`findW`); only the check `imgOK` of the witness matters for soundness.

`floor_framed`: a decoder term with a big dead side `C(z₁, z₂)` gives the floor, or `C(z₁, z₂) ∈ FL`.
-/

namespace RankNine.Facts

open Matrix BForm BForm.E8

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

/-! ## Data access -/

def lmask : List ℕ → ℕ
  | [] => 0
  | x :: l => 2 ^ x ||| lmask l

theorem lmask_bit (l : List ℕ) (i : ℕ) : (lmask l).testBit i = true ↔ i ∈ l := by
  induction l with
  | nil => simp [lmask, bit_zero]
  | cons x l ih =>
    simp only [lmask, bit_or, Bool.or_eq_true, bit_pow, ih, List.mem_cons]

def gl (g x : ℕ) : ℕ := (grpData.getD g []).getD x 0
def gi (g x : ℕ) : ℕ := (grpInvData.getD g []).getD x 0

/-- **finite fact GRP** -/
def grpOK : Bool :=
  (List.range 384).all fun g => (List.range 104).all fun x =>
    decide (gl g x < 104) && decide (gi g x < 104) && gi g (gl g x) == x && gl g (gi g x) == x &&
    (List.range 104).all fun y => orth (gl g x) (gl g y) == orth x y && par (gl g x) (pbits (gl g y)) == par x (pbits y)

theorem grp_facts (h : grpOK = true) {g : ℕ} (hg : g < 384) {x : ℕ} (hx : x < 104) :
    gl g x < 104 ∧ gi g x < 104 ∧ gi g (gl g x) = x ∧ gl g (gi g x) = x ∧
      ∀ y < 104, orth (gl g x) (gl g y) = orth x y ∧ par (gl g x) (pbits (gl g y)) = par x (pbits y) := by
  have h1 := List.all_eq_true.mp (List.all_eq_true.mp h g (List.mem_range.mpr hg)) x (List.mem_range.mpr hx)
  simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, List.all_eq_true, List.mem_range] at h1
  obtain ⟨⟨⟨⟨⟨a, b⟩, c⟩, d⟩, e⟩⟩ := h1
  exact ⟨a, b, c, d, fun y hy => ⟨(e y hy).1, (e y hy).2⟩⟩

/-- the group element `g` as a permutation of `Fin 104` -/
def permOf (h : grpOK = true) {g : ℕ} (hg : g < 384) : Equiv.Perm (Fin 104) where
  toFun x := ⟨gl g x, (grp_facts h hg x.2).1⟩
  invFun x := ⟨gi g x, (grp_facts h hg x.2).2.1⟩
  left_inv x := Fin.ext (grp_facts h hg x.2).2.2.1
  right_inv x := Fin.ext (grp_facts h hg x.2).2.2.2.1

theorem permOf_val (h : grpOK = true) {g : ℕ} (hg : g < 384) (x : Fin 104) : (permOf h hg x : ℕ) = gl g x := rfl

theorem zl_labK (s : Fin 104) : zl (labK s) = pbits s := by
  apply List.ext_getElem (by rw [zl_len, pbits_len])
  intro k h1 h2
  rw [zl_len] at h1
  simp only [zl, List.getElem_map, List.getElem_finRange, labK, pbits, List.getElem_range,
    List.getD_eq_getElem?_getD, List.getElem?_map, List.getElem?_range h1, Option.map_some, Option.getD_some]
  split_ifs <;> rfl

theorem zmod2_eq {a b : ZMod 2} (h : a ≠ 0 ↔ b ≠ 0) : a = b := by
  revert a b; decide

theorem lab_perm (h : grpOK = true) {g : ℕ} (hg : g < 384) (t s : Fin 104) :
    labK (permOf h hg t) ⬝ᵥ labK (permOf h hg s) = labK t ⬝ᵥ labK s := by
  apply zmod2_eq
  rw [lab_dot, lab_dot, zl_labK, zl_labK, permOf_val, permOf_val]
  rw [((grp_facts h hg t.2).2.2.2.2 s s.2).2]

theorem orth_perm (h : grpOK = true) {g : ℕ} (hg : g < 384) (x y : Fin 104) :
    orth (permOf h hg x) (permOf h hg y) = orth x y := by
  rw [permOf_val, permOf_val]
  exact ((grp_facts h hg x.2).2.2.2.2 y y.2).1

theorem pn_permOf (h : grpOK = true) {g : ℕ} (hg : g < 384) {x : ℕ} (hx : x < 104) :
    Tr.pn (permOf h hg) x = gl g x := by
  simp [Tr.pn, hx, permOf_val]

/-! ## Orbit fact -/

/-- the dead set `C(z₁, z₂)` as a bit mask (labels as 0/1 lists) -/
def cmask (l1 l2 : List ℕ) : ℕ := lmask ((List.range 104).filter fun t => par t l1 || par t l2)

def tmask (k : ℕ) : ℕ := typeMask.getD k 0

/-- witness check: `g (typeMask k) ⊆ c` -/
def imgOK (g k c : ℕ) : Bool :=
  decide (g < 384) && decide (k < 387) && decide (tmask k < 2 ^ 104) &&
  (List.range 104).all fun x => !(tmask k).testBit x || c.testBit (gl g x)

def imgMask (g k : ℕ) : ℕ := lmask (((List.range 104).filter fun x => (tmask k).testBit x).map (gl g))

/-- hash table of the images `g (typeMask k)` (computation only; soundness uses `imgOK`) -/
def imgTable : Std.HashMap ℕ (ℕ × ℕ) :=
  ((List.range 384).flatMap fun g => (List.range 387).map fun k => (g, k)).foldl
    (fun m p => if m.contains (imgMask p.1 p.2) then m else m.insert (imgMask p.1 p.2) p) {}

def findW (c : ℕ) : Option (ℕ × ℕ) := imgTable.get? c

def wOK (c : ℕ) : Bool :=
  match findW c with
  | some p => imgOK p.1 p.2 c
  | none => false

/-- **finite fact ORB** (frameless list `FL`) -/
def orbOK (FL : List ℕ) : Bool :=
  lists9.all fun l1 => lists9.all fun l2 =>
    l1 == zero9 || l2 == zero9 || l1 == l2 || FL.contains (cmask l1 l2) || wOK (cmask l1 l2)

theorem cmask_bit {l1 l2 : List ℕ} {y : ℕ} (h : (cmask l1 l2).testBit y = true) :
    y < 104 ∧ (par y l1 = true ∨ par y l2 = true) := by
  rw [cmask, lmask_bit, List.mem_filter, List.mem_range, Bool.or_eq_true] at h
  exact h

theorem zl_inj {z1 z2 : V9} (h : zl z1 = zl z2) : z1 = z2 := by
  funext k
  have := congrArg (fun l => l.getD k 0) h
  simp only [zl_getD] at this
  exact ZMod.val_injective _ this

theorem testBit_big {n x : ℕ} (hn : n < 2 ^ 104) (hx : 104 ≤ x) : n.testBit x = false :=
  Nat.testBit_eq_false_of_lt (lt_of_lt_of_le hn (Nat.pow_le_pow_right (by norm_num) hx))

/-- per-type floor (from the 387 kernel-checked `Fl<k>.floor`) -/
def FloorType (K : Type) [Field K] [CharZero K] (k : ℕ) : Prop :=
  ∀ (A B : ℕ → Fin 9 → K) (u : Fin 9 → K), u ≠ 0 → (∀ x, (tmask k).testBit x = true → A x ⬝ᵥ u = 0) →
    (∀ x < 104, A x ⬝ᵥ B x ≠ 0) → (∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) →
    ∀ (Al Bl : Matrix (Fin 9) (Fin 104) K), Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1 →
    Bl * Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i) = 1 →
    ∀ (P Q : Matrix (Fin 104) C9 K), Matrix.of (fun v s : Fin 104 => Mx A B v s) = P * Qᵀ →
      56 ≤ cost labK P Q

/-- **Frame case.** Rows dead on `C(z₁, z₂)` (distinct non-zero `z₁, z₂`): the floor holds, or `C(z₁, z₂) ∈ FL`. -/
theorem floor_framed {K : Type} [Field K] [CharZero K] (hFT : ∀ k < 387, FloorType K k)
    (hgrp : grpOK = true) (FL : List ℕ) (horb : orbOK FL = true)
    (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (z1 z2 : V9) (h1 : z1 ≠ 0) (h2 : z2 ≠ 0) (h12 : z1 ≠ z2)
    (hZ : ∀ x : Fin 104, (labK x ⬝ᵥ z1 ≠ 0 ∨ labK x ⬝ᵥ z2 ≠ 0) → A x ⬝ᵥ u = 0)
    (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (Al Bl : Matrix (Fin 9) (Fin 104) K) (hA : Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1)
    (hB : Bl * Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i) = 1)
    (P Q : Matrix (Fin 104) C9 K) (h : Matrix.of (fun v s : Fin 104 => Mx A B v s) = P * Qᵀ) :
    56 ≤ cost labK P Q ∨ FL.contains (cmask (zl z1) (zl z2)) = true := by
  have ho := List.all_eq_true.mp (List.all_eq_true.mp horb _ (zl_mem z1)) _ (zl_mem z2)
  simp only [Bool.or_eq_true, beq_iff_eq] at ho
  rcases ho with ((((e | e) | e) | e) | e)
  · exact absurd (zl_zero e) h1
  · exact absurd (zl_zero e) h2
  · exact absurd (zl_inj e) h12
  · exact Or.inr e
  left
  set c := cmask (zl z1) (zl z2)
  unfold wOK at e
  rcases hw : findW c with _ | ⟨g, k⟩
  · rw [hw] at e; exact absurd e (by simp)
  rw [hw] at e
  simp only [imgOK, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true,
    Bool.not_eq_true'] at e
  obtain ⟨⟨⟨hg, hk⟩, htm⟩, himg⟩ := e
  set π := permOf hgrp hg
  have hZ' : ∀ x, (tmask k).testBit x = true → (fun y => A (Tr.pn π y)) x ⬝ᵥ u = 0 := by
    intro x hx
    have hx104 : x < 104 := by
      by_contra hc
      rw [testBit_big htm (by omega)] at hx; exact absurd hx (by simp)
    have hc := (himg x hx104).resolve_left (by rw [hx]; simp)
    obtain ⟨hy, hpar⟩ := cmask_bit hc
    show A (Tr.pn π x) ⬝ᵥ u = 0
    rw [pn_permOf hgrp hg hx104]
    have := hZ ⟨gl g x, hy⟩
    apply this
    rcases hpar with p | p
    · exact Or.inl ((lab_dot _ _).mpr p)
    · exact Or.inr ((lab_dot _ _).mpr p)
  have hfl := hFT k hk (fun x => A (Tr.pn π x)) (fun x => B (Tr.pn π x)) u hu hZ'
    (Tr.diag_perm π A B hdiag) (Tr.mask_perm π (orth_perm hgrp hg) A B hmask)
    (Al.submatrix id π) (Bl.submatrix id π) (Tr.inv_perm π A Al hA) (Tr.inv_perm π B Bl hB)
    (P.submatrix π id) (Q.submatrix π id) (Tr.dec_perm π A B P Q h)
  rwa [Tr.cost_perm π (lab_perm hgrp hg) P Q] at hfl

end RankNine.Facts
