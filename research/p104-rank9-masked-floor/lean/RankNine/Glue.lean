import RankNine.Plane

set_option linter.unusedSectionVars false

/-!
# T3.4: gluing live rows

For a family `h v ∈ K⁹` (live rows `h v = P v / λ v`) write `PR h v w` if `h v - h w ∈ span(ρ_v, ρ_w)` (from a
rank-6 certificate on `O_v ∩ O_w ∩ Z`) and `Gl h Λ v` if `h v ∈ Λ + K ρ_v`.
* `tri_glue`: three lines with pairwise `PR` and independent roots are glued by one centre;
* `glue_merge`: two centres gluing the same two distinct lines coincide;
* `glue_join`: a line in a good independent triangle with two glued lines is glued;
* `glue_four`: four lines with pairwise `PR` are glued (an A2 plane holds at most three lines);
* `glue_ext`: a glued 4-set extends to every further line, if bad pairs (no `PR`) form a matching.
-/

namespace RankNine

open Matrix

section glue

variable {K : Type*} [Field K] [CharZero K]

/-- `h v - h w ∈ span(ρ_v, ρ_w)` -/
def PR (h : ℕ → Fin 9 → K) (v w : ℕ) : Prop := ∃ a b : K, h v - h w = a • rho K v + b • rho K w

/-- the centre `Λ` glues line `v` -/
def Gl (h : ℕ → Fin 9 → K) (Λ : Fin 9 → K) (v : ℕ) : Prop := ∃ a : K, h v = Λ + a • rho K v

theorem PR_symm {h : ℕ → Fin 9 → K} {v w : ℕ} (p : PR h v w) : PR h w v := by
  obtain ⟨a, b, e⟩ := p
  refine ⟨-b, -a, ?_⟩
  ext i
  have q := congrFun e i
  simp only [Pi.add_apply, Pi.sub_apply, Pi.smul_apply, smul_eq_mul] at q ⊢
  linear_combination -q

theorem gram2_ne {x y : ℕ} (hx : x < 104) (hy : y < 104) (hxy : x ≠ y) : gram2 x y ≠ 0 := by
  unfold gram2
  rcases dot_vals hx hy hxy with e | e | e <;> rw [e] <;> norm_num

theorem gram3_swap12 (a b c : ℕ) : gram3 a b c = gram3 b a c := by
  simp only [gram3, dot_comm b a]; ring

theorem gram3_swap23 (a b c : ℕ) : gram3 a b c = gram3 a c b := by
  simp only [gram3, dot_comm c b]; ring

theorem tri_glue {h : ℕ → Fin 9 → K} {u v w : ℕ} (hu : u < 104) (hv : v < 104) (hw : w < 104)
    (h3 : gram3 u v w ≠ 0) (puv : PR h u v) (pvw : PR h v w) (puw : PR h u w) :
    ∃ Λ, Gl h Λ u ∧ Gl h Λ v ∧ Gl h Λ w := by
  obtain ⟨a1, b1, e1⟩ := puv
  obtain ⟨a2, b2, e2⟩ := pvw
  obtain ⟨a3, b3, e3⟩ := puw
  have E : (a1 - a3) • rho K u + (b1 + a2) • rho K v + (b2 - b3) • rho K w = 0 := by
    ext i
    have q1 := congrFun e1 i
    have q2 := congrFun e2 i
    have q3 := congrFun e3 i
    simp only [Pi.add_apply, Pi.sub_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply] at q1 q2 q3 ⊢
    linear_combination q3 - q1 - q2
  obtain ⟨c1, -, -⟩ := indep3 hu hv hw h3 E
  refine ⟨h u - a1 • rho K u, ⟨a1, (sub_add_cancel _ _).symm⟩, ⟨-b1, ?_⟩, ⟨-b3, ?_⟩⟩
  · ext i
    have q1 := congrFun e1 i
    simp only [Pi.add_apply, Pi.sub_apply, Pi.smul_apply, smul_eq_mul] at q1 ⊢
    linear_combination -q1
  · ext i
    have q3 := congrFun e3 i
    simp only [Pi.add_apply, Pi.sub_apply, Pi.smul_apply, smul_eq_mul] at q3 ⊢
    linear_combination -q3 + rho K u i * c1

theorem glue_merge {h : ℕ → Fin 9 → K} {x y : ℕ} (hx : x < 104) (hy : y < 104) (hxy : x ≠ y)
    {Λ Λ' : Fin 9 → K} (g1 : Gl h Λ x) (g2 : Gl h Λ' x) (g3 : Gl h Λ y) (g4 : Gl h Λ' y) : Λ = Λ' := by
  obtain ⟨a, ea⟩ := g1
  obtain ⟨a', ea'⟩ := g2
  obtain ⟨b, eb⟩ := g3
  obtain ⟨b', eb'⟩ := g4
  have E : (a' - a) • rho K x + (b - b') • rho K y = 0 := by
    ext i
    have q1 := congrFun ea i
    have q2 := congrFun ea' i
    have q3 := congrFun eb i
    have q4 := congrFun eb' i
    simp only [Pi.add_apply, Pi.sub_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply] at q1 q2 q3 q4 ⊢
    linear_combination q1 - q2 - q3 + q4
  obtain ⟨c1, -⟩ := indep2 hx hy (gram2_ne hx hy hxy) E
  ext i
  have q1 := congrFun ea i
  have q2 := congrFun ea' i
  simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul] at q1 q2
  linear_combination q2 - q1 + rho K x i * c1

theorem glue_join {h : ℕ → Fin 9 → K} {v x y : ℕ} (hv : v < 104) (hx : x < 104) (hy : y < 104) (hxy : x ≠ y)
    (h3 : gram3 v x y ≠ 0) (pvx : PR h v x) (pvy : PR h v y) (pxy : PR h x y) {Λ : Fin 9 → K}
    (gx : Gl h Λ x) (gy : Gl h Λ y) : Gl h Λ v := by
  obtain ⟨Λ', g1, g2, g3⟩ := tri_glue hv hx hy h3 pvx pxy pvy
  rw [glue_merge hx hy hxy gx g2 gy g3]
  exact g1

theorem glue_four {h : ℕ → Fin 9 → K} {x1 x2 x3 x4 : ℕ} (h1 : x1 < 104) (h2 : x2 < 104) (h3 : x3 < 104)
    (h4 : x4 < 104) (d12 : x1 ≠ x2) (d13 : x1 ≠ x3) (d14 : x1 ≠ x4) (d23 : x2 ≠ x3) (d24 : x2 ≠ x4)
    (d34 : x3 ≠ x4) (p12 : PR h x1 x2) (p13 : PR h x1 x3) (p14 : PR h x1 x4) (p23 : PR h x2 x3)
    (p24 : PR h x2 x4) (p34 : PR h x3 x4) :
    ∃ Λ, Gl h Λ x1 ∧ Gl h Λ x2 ∧ Gl h Λ x3 ∧ Gl h Λ x4 := by
  by_cases h123 : gram3 x1 x2 x3 = 0
  · have h124 : gram3 x1 x2 x4 ≠ 0 := fun e =>
      plane_unique h1 h2 h3 h4 d12 (Ne.symm d13) (Ne.symm d23) (Ne.symm d14) (Ne.symm d24) d34 h123 e
    obtain ⟨Λ, g1, g2, g4⟩ := tri_glue h1 h2 h4 h124 p12 p24 p14
    have h314 : gram3 x3 x1 x4 ≠ 0 := by
      intro e
      exact plane_unique h1 h3 h2 h4 d13 (Ne.symm d12) d23 (Ne.symm d14) (Ne.symm d34) d24
        (by rw [← gram3_swap23]; exact h123) (by rw [gram3_swap12]; exact e)
    exact ⟨Λ, g1, g2, glue_join h3 h1 h4 d14 h314 (PR_symm p13) p34 p14 g1 g4, g4⟩
  · obtain ⟨Λ, g1, g2, g3⟩ := tri_glue h1 h2 h3 h123 p12 p23 p13
    by_cases h412 : gram3 x4 x1 x2 = 0
    · have h413 : gram3 x4 x1 x3 ≠ 0 := by
        intro e
        exact plane_unique h1 h4 h2 h3 d14 (Ne.symm d12) d24 (Ne.symm d13) d34 d23
          (by rw [gram3_swap12]; exact h412) (by rw [gram3_swap12]; exact e)
      exact ⟨Λ, g1, g2, g3, glue_join h4 h1 h3 d13 h413 (PR_symm p14) (PR_symm p34) p13 g1 g3⟩
    · exact ⟨Λ, g1, g2, g3, glue_join h4 h1 h2 d12 h412 (PR_symm p14) (PR_symm p24) p12 g1 g2⟩

/-- good-pair data: a symmetric Boolean relation on the live lines whose `true` pairs carry `PR`, whose `false`
pairs form a matching -/
structure GoodRel (h : ℕ → Fin 9 → K) (Live : ℕ → Prop) (good : ℕ → ℕ → Bool) : Prop where
  lt : ∀ v, Live v → v < 104
  symm : ∀ v w, good v w = good w v
  pr : ∀ v w, Live v → Live w → v ≠ w → good v w = true → PR h v w
  matching : ∀ v w w', Live v → Live w → Live w' → v ≠ w → v ≠ w' → w ≠ w' → good v w = true ∨ good v w' = true

/-- three lines good with `v`: one of their pairs is good and forms an independent triple with `v` -/
theorem tri3 {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    {v p q r : ℕ} (lv : Live v) (lp : Live p) (lq : Live q) (lr : Live r) (dvp : v ≠ p) (dvq : v ≠ q)
    (dvr : v ≠ r) (dpq : p ≠ q) (dpr : p ≠ r) (dqr : q ≠ r) :
    (good p q = true ∧ gram3 v p q ≠ 0) ∨ (good p r = true ∧ gram3 v p r ≠ 0) ∨
      (good q r = true ∧ gram3 v q r ≠ 0) := by
  have hv := G.lt v lv; have hp := G.lt p lp; have hq := G.lt q lq; have hr := G.lt r lr
  by_cases A : good p q = true ∧ gram3 v p q ≠ 0
  · exact Or.inl A
  by_cases B : good p r = true ∧ gram3 v p r ≠ 0
  · exact Or.inr (Or.inl B)
  right; right
  have nA : good p q = false ∨ gram3 v p q = 0 := by
    by_cases g : good p q = true
    · exact Or.inr (by by_contra hc; exact A ⟨g, hc⟩)
    · exact Or.inl (by simpa using g)
  have nB : good p r = false ∨ gram3 v p r = 0 := by
    by_cases g : good p r = true
    · exact Or.inr (by by_contra hc; exact B ⟨g, hc⟩)
    · exact Or.inl (by simpa using g)
  rcases nA with a | a <;> rcases nB with b | b
  · rcases G.matching p q r lp lq lr dpq dpr dqr with c | c
    · rw [a] at c; exact absurd c (by simp)
    · rw [b] at c; exact absurd c (by simp)
  · -- q's bad partner is p; v, r, p, q: (v, r) lies in the planes of p and of q at most once
    refine ⟨?_, fun e => ?_⟩
    · rcases G.matching q p r lq lp lr (Ne.symm dpq) dqr dpr with c | c
      · rw [G.symm, a] at c; exact absurd c (by simp)
      · exact c
    · exact plane_unique hv hr hp hq dvr (Ne.symm dvp) dpr (Ne.symm dvq) dqr dpq
        (by rw [← gram3_swap23]; exact b) (by rw [← gram3_swap23]; exact e)
  · refine ⟨?_, fun e => ?_⟩
    · rcases G.matching r p q lr lp lq (Ne.symm dpr) (Ne.symm dqr) dpq with c | c
      · rw [G.symm, b] at c; exact absurd c (by simp)
      · rw [G.symm]; exact c
    · exact plane_unique hv hq hp hr dvq (Ne.symm dvp) dpq (Ne.symm dvr) (Ne.symm dqr) dpr
        (by rw [← gram3_swap23]; exact a) e
  · exact (plane_unique hv hp hq hr dvp (Ne.symm dvq) (Ne.symm dpq) (Ne.symm dvr) (Ne.symm dpr) dqr a b).elim

/-- a line good with three glued lines is glued -/
theorem join3 {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    {Λ : Fin 9 → K} {v p q r : ℕ} (lv : Live v) (lp : Live p) (lq : Live q) (lr : Live r) (dvp : v ≠ p)
    (dvq : v ≠ q) (dvr : v ≠ r) (dpq : p ≠ q) (dpr : p ≠ r) (dqr : q ≠ r) (bp : good v p = true)
    (bq : good v q = true) (br : good v r = true) (gp : Gl h Λ p) (gq : Gl h Λ q) (gr : Gl h Λ r) :
    Gl h Λ v := by
  have hv := G.lt v lv; have hp := G.lt p lp; have hq := G.lt q lq; have hr := G.lt r lr
  rcases tri3 G lv lp lq lr dvp dvq dvr dpq dpr dqr with ⟨g, e⟩ | ⟨g, e⟩ | ⟨g, e⟩
  · exact glue_join hv hp hq dpq e (G.pr v p lv lp dvp bp) (G.pr v q lv lq dvq bq) (G.pr p q lp lq dpq g) gp gq
  · exact glue_join hv hp hr dpr e (G.pr v p lv lp dvp bp) (G.pr v r lv lr dvr br) (G.pr p r lp lr dpr g) gp gr
  · exact glue_join hv hq hr dqr e (G.pr v q lv lq dvq bq) (G.pr v r lv lr dvr br) (G.pr q r lq lr dqr g) gq gr

/-- a glued 4-set extends to every further live line -/
theorem glue_ext {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    {Λ : Fin 9 → K} {x1 x2 x3 x4 : ℕ} (l1 : Live x1) (l2 : Live x2) (l3 : Live x3) (l4 : Live x4)
    (d12 : x1 ≠ x2) (d13 : x1 ≠ x3) (d14 : x1 ≠ x4) (d23 : x2 ≠ x3) (d24 : x2 ≠ x4) (d34 : x3 ≠ x4)
    (g1 : Gl h Λ x1) (g2 : Gl h Λ x2) (g3 : Gl h Λ x3) (g4 : Gl h Λ x4) {v : ℕ} (lv : Live v) : Gl h Λ v := by
  by_cases e1 : v = x1
  · rw [e1]; exact g1
  by_cases e2 : v = x2
  · rw [e2]; exact g2
  by_cases e3 : v = x3
  · rw [e3]; exact g3
  by_cases e4 : v = x4
  · rw [e4]; exact g4
  have m := fun a b (la : Live a) (lb : Live b) (da : v ≠ a) (db : v ≠ b) (dab : a ≠ b) =>
    G.matching v a b lv la lb da db dab
  by_cases b1 : good v x1 = true
  · by_cases b2 : good v x2 = true
    · by_cases b3 : good v x3 = true
      · exact join3 G lv l1 l2 l3 e1 e2 e3 d12 d13 d23 b1 b2 b3 g1 g2 g3
      · have b4 : good v x4 = true := (m x3 x4 l3 l4 e3 e4 d34).resolve_left b3
        exact join3 G lv l1 l2 l4 e1 e2 e4 d12 d14 d24 b1 b2 b4 g1 g2 g4
    · have b3 : good v x3 = true := (m x2 x3 l2 l3 e2 e3 d23).resolve_left b2
      have b4 : good v x4 = true := (m x2 x4 l2 l4 e2 e4 d24).resolve_left b2
      exact join3 G lv l1 l3 l4 e1 e3 e4 d13 d14 d34 b1 b3 b4 g1 g3 g4
  · have b2 : good v x2 = true := (m x1 x2 l1 l2 e1 e2 d12).resolve_left b1
    have b3 : good v x3 = true := (m x1 x3 l1 l3 e1 e3 d13).resolve_left b1
    have b4 : good v x4 = true := (m x1 x4 l1 l4 e1 e4 d14).resolve_left b1
    exact join3 G lv l2 l3 l4 e2 e3 e4 d23 d24 d34 b2 b3 b4 g2 g3 g4

theorem good_of_bad {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    {v w w' : ℕ} (lv : Live v) (lw : Live w) (lw' : Live w') (dvw : v ≠ w) (dvw' : v ≠ w') (dww' : w ≠ w')
    (b : good v w = false) : good v w' = true :=
  (G.matching v w w' lv lw lw' dvw dvw' dww').resolve_left (by rw [b]; simp)

theorem good_symm {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    {v w : ℕ} (g : good v w = true) : good w v = true := (G.symm w v).trans g

/-- an independent good triangle `x y z` and a line `w` good with `y, z`, `w y z` independent: all glued -/
theorem tri_join {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    {x y z w : ℕ} (lx : Live x) (ly : Live y) (lz : Live z) (lw : Live w) (dxy : x ≠ y) (dxz : x ≠ z)
    (dyz : y ≠ z) (dwx : w ≠ x) (dwy : w ≠ y) (dwz : w ≠ z) (gxy : good x y = true) (gyz : good y z = true)
    (gxz : good x z = true) (gwy : good w y = true) (gwz : good w z = true) (h1 : gram3 x y z ≠ 0)
    (h2 : gram3 w y z ≠ 0) : ∃ Λ, ∀ v, Live v → Gl h Λ v := by
  have hx := G.lt x lx; have hy := G.lt y ly; have hz := G.lt z lz; have hw := G.lt w lw
  obtain ⟨Λ, g1, g2, g3⟩ := tri_glue hx hy hz h1 (G.pr x y lx ly dxy gxy) (G.pr y z ly lz dyz gyz)
    (G.pr x z lx lz dxz gxz)
  have g4 := glue_join hw hy hz dyz h2 (G.pr w y lw ly dwy gwy) (G.pr w z lw lz dwz gwz) (G.pr y z ly lz dyz gyz)
    g2 g3
  exact ⟨Λ, fun v lv => glue_ext G lx ly lz lw dxy dxz (Ne.symm dwx) dyz (Ne.symm dwy) (Ne.symm dwz) g1 g2 g3 g4 lv⟩

/-- four pairwise good lines: all glued -/
theorem four_good {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    {x1 x2 x3 x4 : ℕ} (l1 : Live x1) (l2 : Live x2) (l3 : Live x3) (l4 : Live x4) (d12 : x1 ≠ x2)
    (d13 : x1 ≠ x3) (d14 : x1 ≠ x4) (d23 : x2 ≠ x3) (d24 : x2 ≠ x4) (d34 : x3 ≠ x4) (g12 : good x1 x2 = true)
    (g13 : good x1 x3 = true) (g14 : good x1 x4 = true) (g23 : good x2 x3 = true) (g24 : good x2 x4 = true)
    (g34 : good x3 x4 = true) : ∃ Λ, ∀ v, Live v → Gl h Λ v := by
  obtain ⟨Λ, g1, g2, g3, g4⟩ := glue_four (G.lt _ l1) (G.lt _ l2) (G.lt _ l3) (G.lt _ l4) d12 d13 d14 d23 d24 d34
    (G.pr _ _ l1 l2 d12 g12) (G.pr _ _ l1 l3 d13 g13) (G.pr _ _ l1 l4 d14 g14) (G.pr _ _ l2 l3 d23 g23)
    (G.pr _ _ l2 l4 d24 g24) (G.pr _ _ l3 l4 d34 g34)
  exact ⟨Λ, fun v lv => glue_ext G l1 l2 l3 l4 d12 d13 d14 d23 d24 d34 g1 g2 g3 g4 lv⟩

end glue

/-- plan for five lines with bad pairs `a a'`, `b b'`: two independent triangles through `e` sharing two lines -/
def planB (a a' b b' e : ℕ) : Bool :=
  (gram3 a b e != 0 && gram3 a' b e != 0) || (gram3 a b e != 0 && gram3 a b' e != 0) ||
    (gram3 a' b' e != 0 && gram3 a' b e != 0) || (gram3 a' b' e != 0 && gram3 a b' e != 0)

theorem planB_swap1 (a a' b b' e : ℕ) : planB a' a b b' e = planB a a' b b' e := by
  unfold planB
  generalize (gram3 a b e != 0) = A; generalize (gram3 a' b e != 0) = B
  generalize (gram3 a b' e != 0) = C; generalize (gram3 a' b' e != 0) = D
  revert A B C D; decide

theorem planB_swap2 (a a' b b' e : ℕ) : planB a a' b' b e = planB a a' b b' e := by
  unfold planB
  generalize (gram3 a b e != 0) = A; generalize (gram3 a' b e != 0) = B
  generalize (gram3 a b' e != 0) = C; generalize (gram3 a' b' e != 0) = D
  revert A B C D; decide

section glue5

variable {K : Type*} [Field K] [CharZero K]

/-- the plan hypothesis: every five live lines with two disjoint bad pairs have a plan -/
def PlanHyp (Live : ℕ → Prop) (good : ℕ → ℕ → Bool) : Prop :=
  ∀ a a' b b' e, Live a → Live a' → Live b → Live b' → Live e → a ≠ a' → a ≠ b → a ≠ b' → a ≠ e → a' ≠ b →
    a' ≠ b' → a' ≠ e → b ≠ b' → b ≠ e → b' ≠ e → good a a' = false → good b b' = false → planB a a' b b' e = true

theorem core5 {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    (H : PlanHyp Live good) {a a' b b' e : ℕ} (la : Live a) (la' : Live a') (lb : Live b) (lb' : Live b')
    (le : Live e) (daa' : a ≠ a') (dab : a ≠ b) (dab' : a ≠ b') (dae : a ≠ e) (da'b : a' ≠ b) (da'b' : a' ≠ b')
    (da'e : a' ≠ e) (dbb' : b ≠ b') (dbe : b ≠ e) (db'e : b' ≠ e) (ba : good a a' = false)
    (bb : good b b' = false) : ∃ Λ, ∀ v, Live v → Gl h Λ v := by
  have hp := H a a' b b' e la la' lb lb' le daa' dab dab' dae da'b da'b' da'e dbb' dbe db'e ba bb
  have ba' : good a' a = false := by rw [G.symm]; exact ba
  have bb' : good b' b = false := by rw [G.symm]; exact bb
  have gab := good_of_bad G la la' lb daa' dab da'b ba
  have gab' := good_of_bad G la la' lb' daa' dab' da'b' ba
  have gae := good_of_bad G la la' le daa' dae da'e ba
  have ga'b := good_of_bad G la' la lb (Ne.symm daa') da'b dab ba'
  have ga'b' := good_of_bad G la' la lb' (Ne.symm daa') da'b' dab' ba'
  have ga'e := good_of_bad G la' la le (Ne.symm daa') da'e dae ba'
  have gbe := good_of_bad G lb lb' le dbb' dbe db'e bb
  have gb'e := good_of_bad G lb' lb le (Ne.symm dbb') db'e dbe bb'
  simp only [planB, Bool.or_eq_true, Bool.and_eq_true, bne_iff_ne, ne_eq] at hp
  rcases hp with ((⟨h1, h2⟩ | ⟨h1, h2⟩) | ⟨h1, h2⟩) | ⟨h1, h2⟩
  · exact tri_join G la lb le la' dab dae dbe (Ne.symm daa') da'b da'e gab gbe gae ga'b ga'e h1 h2
  · exact tri_join G lb la le lb' (Ne.symm dab) dbe dae (Ne.symm dbb') (Ne.symm dab') db'e (good_symm G gab) gae
      gbe (good_symm G gab') gb'e (by rw [gram3_swap12]; exact h1) (by rw [gram3_swap12]; exact h2)
  · exact tri_join G lb' la' le lb (Ne.symm da'b') db'e da'e dbb' (Ne.symm da'b) dbe (good_symm G ga'b') ga'e
      gb'e (good_symm G ga'b) gbe (by rw [gram3_swap12]; exact h1) (by rw [gram3_swap12]; exact h2)
  · exact tri_join G la' lb' le la da'b' da'e db'e daa' dab' dae ga'b' gb'e ga'e gab' gae h1 h2

theorem step4 {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    (H : PlanHyp Live good) {i j k l m : ℕ} (li : Live i) (lj : Live j) (lk : Live k) (ll : Live l) (lm : Live m)
    (dij : i ≠ j) (dik : i ≠ k) (dil : i ≠ l) (dim : i ≠ m) (djk : j ≠ k) (djl : j ≠ l) (djm : j ≠ m)
    (dkl : k ≠ l) (dkm : k ≠ m) (dlm : l ≠ m) (b : good i j = false) : ∃ Λ, ∀ v, Live v → Gl h Λ v := by
  have bji : good j i = false := by rw [G.symm]; exact b
  have gjk := good_of_bad G lj li lk (Ne.symm dij) djk dik bji
  have gjl := good_of_bad G lj li ll (Ne.symm dij) djl dil bji
  have gjm := good_of_bad G lj li lm (Ne.symm dij) djm dim bji
  by_cases gkl : good k l = true
  · by_cases gkm : good k m = true
    · by_cases glm : good l m = true
      · exact four_good G lj lk ll lm djk djl djm dkl dkm dlm gjk gjl gjm gkl gkm glm
      · exact core5 G H li lj ll lm lk dij dil dim dik djl djm djk dlm (Ne.symm dkl) (Ne.symm dkm) b
          (by simpa using glm)
    · exact core5 G H li lj lk lm ll dij dik dim dil djk djm djl dkm dkl (Ne.symm dlm) b (by simpa using gkm)
  · exact core5 G H li lj lk ll lm dij dik dil dim djk djl djm dkl dkm dlm b (by simpa using gkl)

/-- five distinct live lines force a common centre for all live lines -/
theorem glue_five {h : ℕ → Fin 9 → K} {Live : ℕ → Prop} {good : ℕ → ℕ → Bool} (G : GoodRel h Live good)
    (H : PlanHyp Live good) {x1 x2 x3 x4 x5 : ℕ} (l1 : Live x1) (l2 : Live x2) (l3 : Live x3) (l4 : Live x4)
    (l5 : Live x5) (d12 : x1 ≠ x2) (d13 : x1 ≠ x3) (d14 : x1 ≠ x4) (d15 : x1 ≠ x5) (d23 : x2 ≠ x3)
    (d24 : x2 ≠ x4) (d25 : x2 ≠ x5) (d34 : x3 ≠ x4) (d35 : x3 ≠ x5) (d45 : x4 ≠ x5) :
    ∃ Λ, ∀ v, Live v → Gl h Λ v := by
  by_cases g12 : good x1 x2 = true
  · by_cases g13 : good x1 x3 = true
    · by_cases g14 : good x1 x4 = true
      · by_cases g23 : good x2 x3 = true
        · by_cases g24 : good x2 x4 = true
          · by_cases g34 : good x3 x4 = true
            · exact four_good G l1 l2 l3 l4 d12 d13 d14 d23 d24 d34 g12 g13 g14 g23 g24 g34
            · exact step4 G H l3 l4 l1 l2 l5 d34 (Ne.symm d13) (Ne.symm d23) d35 (Ne.symm d14) (Ne.symm d24) d45
                d12 d15 d25 (by simpa using g34)
          · exact step4 G H l2 l4 l1 l3 l5 d24 (Ne.symm d12) d23 d25 (Ne.symm d14) (Ne.symm d34) d45 d13 d15 d35
              (by simpa using g24)
        · exact step4 G H l2 l3 l1 l4 l5 d23 (Ne.symm d12) d24 d25 (Ne.symm d13) d34 d35 d14 d15 d45
            (by simpa using g23)
      · exact step4 G H l1 l4 l2 l3 l5 d14 d12 d13 d15 (Ne.symm d24) (Ne.symm d34) d45 d23 d25 d35
          (by simpa using g14)
    · exact step4 G H l1 l3 l2 l4 l5 d13 d12 d14 d15 (Ne.symm d23) d34 d35 d24 d25 d45 (by simpa using g13)
  · exact step4 G H l1 l2 l3 l4 l5 d12 d13 d14 d15 d23 d24 d25 d34 d35 d45 (by simpa using g12)

end glue5

end RankNine
