import RankNine.Glue

/-!
# T3.4: per-type gluing data

For a type with reduced dead set `Zm` (bit mask) and outer lines `O` the data are a list `bad` of bad pairs and a
list `T` of pair certificates.  The Boolean checks
* `pcOK`: a pair certificate (rank 6 on `ρ(Z ∩ O_v ∩ O_w)` with pivots `k0, k1`),
* `coverOK`: every pair of distinct outer lines is bad or has a certificate,
* `matchOK`: bad pairs form a matching on `O`,
* `fiveOK`: every five outer lines with two disjoint bad pairs have a plan (`planB`),
give `glue_of_data`: if the rows `h v` (`v ∈ O` live) satisfy `h v ⬝ 𝟙 = 0` and `h v ⬝ ρ_s = τ s` for `s ∈ Z ∩ O_v`
and at least five rows are live, then all live rows have a common centre.
-/

namespace RankNine

open Matrix

def isBad (bad : List (ℕ × ℕ)) (x y : ℕ) : Bool :=
  bad.any fun p => (p.1 == x && p.2 == y) || (p.1 == y && p.2 == x)

theorem isBad_symm (bad : List (ℕ × ℕ)) (x y : ℕ) : isBad bad x y = isBad bad y x := by
  unfold isBad
  congr 1
  funext p
  rw [Bool.or_comm]

theorem isBad_mem {bad : List (ℕ × ℕ)} {x y : ℕ} (h : isBad bad x y = true) :
    ∃ p ∈ bad, (p.1 = x ∧ p.2 = y) ∨ (p.1 = y ∧ p.2 = x) := by
  simp only [isBad, List.any_eq_true, Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq] at h
  exact h

structure PCert where
  v : ℕ
  w : ℕ
  k0 : ℕ
  k1 : ℕ
  C : RCert

def pcOK (Zm : ℕ) (p : PCert) : Bool :=
  certOK p.C.X p.C.N p.C.No p.C.D p.C.pm && decide (p.v < 104) && decide (p.w < 104) && decide (p.k0 < 9) &&
    decide (p.k1 < 9) && (List.range 9).all (fun i => !p.C.pm.testBit i || i == p.k0 || i == p.k1) &&
    ((root p.v).getD p.k0 0 * (root p.w).getD p.k1 0 - (root p.v).getD p.k1 0 * (root p.w).getD p.k0 0 != 0) &&
    (List.range p.C.X.length).all (fun t => Zm.testBit (p.C.X.getD t 0) && dot p.v (p.C.X.getD t 0) == 0 &&
      dot p.w (p.C.X.getD t 0) == 0)

def coverOK (O : List ℕ) (bad : List (ℕ × ℕ)) (T : List PCert) : Bool :=
  O.all fun v => O.all fun w => v == w || isBad bad v w ||
    T.any fun p => (p.v == v && p.w == w) || (p.v == w && p.w == v)

def matchOK (O : List ℕ) (bad : List (ℕ × ℕ)) : Bool :=
  O.all fun v => O.all fun w => O.all fun w' =>
    v == w || v == w' || w == w' || !isBad bad v w || !isBad bad v w'

def dist5B (a b c d e : ℕ) : Bool :=
  a != b && a != c && a != d && a != e && b != c && b != d && b != e && c != d && c != e && d != e

def fiveOK (O : List ℕ) (bad : List (ℕ × ℕ)) : Bool :=
  bad.all fun p => bad.all fun q => O.all fun e => !dist5B p.1 p.2 q.1 q.2 e || planB p.1 p.2 q.1 q.2 e

section data

variable {K : Type*} [Field K] [CharZero K]

/-- the row hypothesis on the live rows -/
def RowHyp (Zm : ℕ) (h : ℕ → Fin 9 → K) (τ : ℕ → K) (Live : ℕ → Prop) : Prop :=
  ∀ v, Live v → h v ⬝ᵥ vK K ones9L = 0 ∧ ∀ s, Zm.testBit s = true → dot v s = 0 → h v ⬝ᵥ rho K s = τ s

theorem pc_sound {Zm : ℕ} {p : PCert} (hp : pcOK Zm p = true) {h : ℕ → Fin 9 → K} {τ : ℕ → K}
    {Live : ℕ → Prop} (R : RowHyp Zm h τ Live) (lv : Live p.v) (lw : Live p.w) : PR h p.v p.w := by
  simp only [pcOK, Bool.and_eq_true, decide_eq_true_eq] at hp
  obtain ⟨⟨⟨⟨⟨⟨⟨hc, hv⟩, hw⟩, hk0⟩, hk1⟩, hpm⟩, hdet⟩, hX⟩ := hp
  have hx : ∀ t < p.C.X.length, Zm.testBit (p.C.X.getD t 0) = true ∧ dot p.v (p.C.X.getD t 0) = 0 ∧
      dot p.w (p.C.X.getD t 0) = 0 := by
    intro t ht
    have := (List.all_eq_true.mp hX) t (List.mem_range.mpr ht)
    simp only [Bool.and_eq_true, beq_iff_eq] at this
    exact ⟨this.1.1, this.1.2, this.2⟩
  have hpiv : ∀ i : Fin 9, p.C.pm.testBit i = true → (i : ℕ) = p.k0 ∨ (i : ℕ) = p.k1 := by
    intro i hi
    have := (List.all_eq_true.mp hpm) i (List.mem_range.mpr i.2)
    simp only [Bool.or_eq_true, Bool.not_eq_true', beq_iff_eq] at this
    rcases this with (e | e) | e
    · rw [hi] at e; exact absurd e (by simp)
    · exact Or.inl e
    · exact Or.inr e
  have hdet' : (root p.v).getD p.k0 0 * (root p.w).getD p.k1 0 - (root p.v).getD p.k1 0 * (root p.w).getD p.k0 0
      ≠ 0 := by simpa using hdet
  obtain ⟨a, b, e⟩ := pair_of_cert p.C hc hv hw hk0 hk1 hpiv hdet' (fun t ht => ⟨(hx t ht).2.1, (hx t ht).2.2⟩)
    (h p.v - h p.w) (fun t ht => by
      rw [sub_dotProduct, (R _ lv).2 _ (hx t ht).1 (hx t ht).2.1, (R _ lw).2 _ (hx t ht).1 (hx t ht).2.2, sub_self])
    (by rw [sub_dotProduct, (R _ lv).1, (R _ lw).1, sub_zero])
  exact ⟨a, b, e⟩

theorem glue_of_data {Zm : ℕ} {O : List ℕ} {bad : List (ℕ × ℕ)} {T : List PCert} (hO : O.all (· < 104) = true)
    (hT : T.all (pcOK Zm) = true) (hc : coverOK O bad T = true) (hm : matchOK O bad = true)
    (hf : fiveOK O bad = true) {h : ℕ → Fin 9 → K} {τ : ℕ → K} {L : ℕ → Prop}
    (R : RowHyp Zm h τ (fun v => v ∈ O ∧ L v))
    (five : ∃ x1 x2 x3 x4 x5, (x1 ∈ O ∧ L x1) ∧ (x2 ∈ O ∧ L x2) ∧ (x3 ∈ O ∧ L x3) ∧ (x4 ∈ O ∧ L x4) ∧
      (x5 ∈ O ∧ L x5) ∧ dist5B x1 x2 x3 x4 x5 = true) :
    ∃ Λ, ∀ v, v ∈ O → L v → Gl h Λ v := by
  have G : GoodRel h (fun v => v ∈ O ∧ L v) (fun v w => !isBad bad v w) := by
    refine ⟨fun v lv => ?_, fun v w => by rw [isBad_symm], fun v w lv lw dvw g => ?_, fun v w w' lv lw lw' d1 d2 d3 => ?_⟩
    · have := (List.all_eq_true.mp hO) v lv.1
      simpa using this
    · have := (List.all_eq_true.mp ((List.all_eq_true.mp hc) v lv.1)) w lw.1
      simp only [Bool.or_eq_true, beq_iff_eq] at this
      rcases this with (e | e) | e
      · exact absurd e dvw
      · simp [e] at g
      · obtain ⟨p, hpT, hp⟩ := List.any_eq_true.mp e
        have hpk := (List.all_eq_true.mp hT) p hpT
        simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq] at hp
        rcases hp with ⟨e1, e2⟩ | ⟨e1, e2⟩
        · have q := pc_sound hpk R (by rw [e1]; exact lv) (by rw [e2]; exact lw)
          rw [e1, e2] at q; exact q
        · have q := pc_sound hpk R (by rw [e1]; exact lw) (by rw [e2]; exact lv)
          rw [e1, e2] at q; exact PR_symm q
    · have := (List.all_eq_true.mp ((List.all_eq_true.mp ((List.all_eq_true.mp hm) v lv.1)) w lw.1)) w' lw'.1
      simp only [Bool.or_eq_true, beq_iff_eq] at this
      rcases this with (((e | e) | e) | e) | e
      · exact absurd e d1
      · exact absurd e d2
      · exact absurd e d3
      · exact Or.inl e
      · exact Or.inr e
  have H : PlanHyp (fun v => v ∈ O ∧ L v) (fun v w => !isBad bad v w) := by
    intro a a' b b' e la la' lb lb' le daa' dab dab' dae da'b da'b' da'e dbb' dbe db'e ba bb
    have ba1 : isBad bad a a' = true := by simpa using ba
    have bb1 : isBad bad b b' = true := by simpa using bb
    obtain ⟨p, hp, hpe⟩ := isBad_mem ba1
    obtain ⟨q, hq, hqe⟩ := isBad_mem bb1
    have hf' := (List.all_eq_true.mp ((List.all_eq_true.mp ((List.all_eq_true.mp hf) p hp)) q hq)) e le.1
    simp only [Bool.or_eq_true, Bool.not_eq_true'] at hf'
    have hd : dist5B p.1 p.2 q.1 q.2 e = true := by
      simp only [dist5B, Bool.and_eq_true, bne_iff_ne, ne_eq]
      rcases hpe with ⟨e1, e2⟩ | ⟨e1, e2⟩ <;> rcases hqe with ⟨e3, e4⟩ | ⟨e3, e4⟩ <;> rw [e1, e2, e3, e4] <;> omega
    rcases hf' with e0 | e0
    · rw [hd] at e0; exact absurd e0 (by simp)
    · rcases hpe with ⟨e1, e2⟩ | ⟨e1, e2⟩ <;> rcases hqe with ⟨e3, e4⟩ | ⟨e3, e4⟩ <;> rw [e1, e2, e3, e4] at e0
      · exact e0
      · rw [planB_swap2] at e0; exact e0
      · rw [planB_swap1] at e0; exact e0
      · rw [planB_swap1, planB_swap2] at e0; exact e0
  obtain ⟨x1, x2, x3, x4, x5, l1, l2, l3, l4, l5, hd⟩ := five
  simp only [dist5B, Bool.and_eq_true, bne_iff_ne, ne_eq] at hd
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨d12, d13⟩, d14⟩, d15⟩, d23⟩, d24⟩, d25⟩, d34⟩, d35⟩, d45⟩ := hd
  obtain ⟨Λ, hΛ⟩ := glue_five G H l1 l2 l3 l4 l5 d12 d13 d14 d15 d23 d24 d25 d34 d35 d45
  exact ⟨Λ, fun v hv hL => hΛ v ⟨hv, hL⟩⟩

end data

/-- line certificate entry `(v, k0, C)`: rank 7 on `ρ(Z ∩ O_v)` with pivot `k0` -/
def lcOK (Zm : ℕ) (v k0 : ℕ) (C : RCert) : Bool :=
  certOK C.X C.N C.No C.D C.pm && decide (v < 104) && decide (k0 < 9) &&
    (List.range 9).all (fun i => !C.pm.testBit i || i == k0) && ((root v).getD k0 0 != 0) &&
    (List.range C.X.length).all (fun t => Zm.testBit (C.X.getD t 0) && dot v (C.X.getD t 0) == 0)

def lineOK (Zm : ℕ) (O : List ℕ) (LT : List (ℕ × ℕ × RCert)) : Bool :=
  O.all fun v => LT.any fun e => e.1 == v && lcOK Zm e.1 e.2.1 e.2.2

theorem lc_sound {K : Type*} [Field K] [CharZero K] {Zm v k0 : ℕ} {C : RCert} (hp : lcOK Zm v k0 C = true)
    (d : Fin 9 → K) (h1 : d ⬝ᵥ vK K ones9L = 0)
    (hd : ∀ s, Zm.testBit s = true → dot v s = 0 → d ⬝ᵥ rho K s = 0) : ∃ a : K, d = a • rho K v := by
  simp only [lcOK, Bool.and_eq_true, decide_eq_true_eq] at hp
  obtain ⟨⟨⟨⟨⟨hc, hv⟩, hk0⟩, hpm⟩, hρ⟩, hX⟩ := hp
  have hx : ∀ t < C.X.length, Zm.testBit (C.X.getD t 0) = true ∧ dot v (C.X.getD t 0) = 0 := by
    intro t ht
    have := (List.all_eq_true.mp hX) t (List.mem_range.mpr ht)
    simp only [Bool.and_eq_true, beq_iff_eq] at this
    exact this
  have hpiv : ∀ i : Fin 9, C.pm.testBit i = true → (i : ℕ) = k0 := by
    intro i hi
    have := (List.all_eq_true.mp hpm) i (List.mem_range.mpr i.2)
    simp only [Bool.or_eq_true, Bool.not_eq_true', beq_iff_eq] at this
    rcases this with e | e
    · rw [hi] at e; exact absurd e (by simp)
    · exact e
  have hρ' : (root v).getD k0 0 ≠ 0 := by simpa using hρ
  exact ⟨_, line_of_cert C hc hv hk0 hpiv hρ' (fun t ht => (hx t ht).2) d
    (fun t ht => hd _ (hx t ht).1 (hx t ht).2) h1⟩

theorem line_of_data {K : Type*} [Field K] [CharZero K] {Zm : ℕ} {O : List ℕ} {LT : List (ℕ × ℕ × RCert)}
    (hL : lineOK Zm O LT = true) {v : ℕ} (hv : v ∈ O) (d : Fin 9 → K) (h1 : d ⬝ᵥ vK K ones9L = 0)
    (hd : ∀ s, Zm.testBit s = true → dot v s = 0 → d ⬝ᵥ rho K s = 0) : ∃ a : K, d = a • rho K v := by
  obtain ⟨e, -, he⟩ := List.any_eq_true.mp ((List.all_eq_true.mp hL) v hv)
  simp only [Bool.and_eq_true, beq_iff_eq] at he
  obtain ⟨e1, he⟩ := he
  rw [← e1]
  exact lc_sound he d h1 (by rw [e1]; exact hd)

end RankNine
