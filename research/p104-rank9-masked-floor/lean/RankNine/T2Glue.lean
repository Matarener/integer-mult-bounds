import RankNine.T2Gauge
import RankNine.Gram

/-!
# T2.3 gluing: closure certificates applied to the matrix

Edge table: edge `e < nE` joins row `ER e` and column `EC e`; `EI` maps the pair `(x, y)` (key `104 x + y`) back to its
edge.  Each stored relation is described by `d = [t, a, s, b, sgn, f₀, …, f₇]`: the frame lines `f`, of which the
dead ones (mask `m`) expand every dead row orthogonal to the others (`ExpOK`, supplied by the branch).  The checks
`descOK` (orthogonality pattern, which products vanish, Gram identity) make the relation
`M t a M a s M b b = - M t b M b s M a a` true, hence `rp v (relOf d) = 1` for `v = M / γ`.  With the gauge along
the BFS tree and `closure_sound`, every needed edge gets `M x y / γ x y * p x * q y (* λ) = 1`.
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

def eid (EI : BT ℕ) (x y : ℕ) : ℕ := EI.get 0 (104 * x + y)

def dfr (d : List ℕ) : List ℕ := d.drop 5

/-- signed six-edge list of a descriptor (empty for an empty descriptor) -/
def relOf (EI : BT ℕ) (d : List ℕ) : List ℕ :=
  if d.length < 5 then [] else
  let t := d.getD 0 0; let a := d.getD 1 0; let s := d.getD 2 0; let b := d.getD 3 0
  let o := if d.getD 4 0 = 1 then 0 else 1
  [2 * eid EI t a + o, 2 * eid EI a s + o, 2 * eid EI b b + o,
   2 * eid EI t b + (1 - o), 2 * eid EI b s + (1 - o), 2 * eid EI a a + (1 - o)]

/-- the pair `(x, y)` is an edge `< nE` of the table -/
def edgeOK (EI ER EC : BT ℕ) (nE x y : ℕ) : Bool :=
  decide (eid EI x y < nE) && decide (ER.get 0 (eid EI x y) = x) && decide (EC.get 0 (eid EI x y) = y)

def descOK (EI ER EC : BT ℕ) (nE m : ℕ) (d : List ℕ) : Bool :=
  let t := d.getD 0 0; let a := d.getD 1 0; let s := d.getD 2 0; let b := d.getD 3 0; let F := dfr d
  decide (5 ≤ d.length) && decide (t < 104) && decide (a < 104) && decide (s < 104) && decide (b < 104) &&
  F.all (· < 104) && F.Nodup && F.contains a && F.contains b && decide (a ≠ b) &&
  m.testBit a && m.testBit b && m.testBit t &&
  F.all (fun f => m.testBit f || orthB t f) && orthB t s &&
  F.all (fun f => !m.testBit f || f == a || f == b || orthB t f || orthB f s) &&
  decide (dot t a * dot a s * dot b b = -(dot t b * dot b s * dot a a)) &&
  edgeOK EI ER EC nE t a && edgeOK EI ER EC nE a s && edgeOK EI ER EC nE b b &&
  edgeOK EI ER EC nE t b && edgeOK EI ER EC nE b s && edgeOK EI ER EC nE a a

/-- dead rows expand along the dead lines of the frame `F` -/
def ExpOK (A B : ℕ → Fin 9 → K) (m : ℕ) (F : List ℕ) : Prop :=
  ∀ t, m.testBit t = true → (∀ f ∈ F, m.testBit f = false → Mx A B t f = 0) →
    ∀ s, Mx A B t s = ∑ f ∈ F.toFinset.filter (fun f => m.testBit f = true),
      Mx A B t f * Mx A B f s / Mx A B f f

theorem orthB_M (A B : ℕ → Fin 9 → K)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) {x y : ℕ} (hx : x < 104) (hy : y < 104)
    (h : orthB x y = true) : Mx A B x y = 0 :=
  hmask x hx y hy (orth_of_orthB hx hy h)

theorem dot_ne_of_not_orthB {x y : ℕ} (hx : x < 104) (hy : y < 104) (h : orthB x y = false) : dot x y ≠ 0 := by
  intro h0
  have : orth x y = true := by simp [orth, h0]
  have hb := orthB_table
  simp only [List.all_eq_true, List.mem_range, beq_iff_eq] at hb
  rw [hb x hx y hy, this] at h
  exact absurd h (by simp)

/-- the six-term relation of a checked descriptor -/
theorem desc_relation (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (EI ER EC : BT ℕ) (nE m : ℕ)
    (d : List ℕ) (hd : descOK EI ER EC nE m d = true) (hE : ExpOK A B m (dfr d)) :
    Mx A B (d.getD 0 0) (d.getD 1 0) * Mx A B (d.getD 1 0) (d.getD 2 0) * Mx A B (d.getD 3 0) (d.getD 3 0) =
      -(Mx A B (d.getD 0 0) (d.getD 3 0) * Mx A B (d.getD 3 0) (d.getD 2 0) *
        Mx A B (d.getD 1 0) (d.getD 1 0)) := by
  unfold descOK at hd
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.contains_iff_mem, Bool.or_eq_true,
    Bool.not_eq_true', beq_iff_eq] at hd
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨_, ht⟩, ha⟩, hs⟩, hb⟩, hF⟩, -⟩, haF⟩, hbF⟩, hab⟩, hma⟩, hmb⟩, hmt⟩, hout⟩, hts⟩, hz⟩, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩ := hd
  set t := d.getD 0 0; set a := d.getD 1 0; set s := d.getD 2 0; set b := d.getD 3 0
  have hexp := hE t hmt (fun f hf hdf => by
    rcases hout f hf with h | h
    · rw [hdf] at h; exact absurd h (by simp)
    · exact orthB_M A B hmask ht (hF f hf) h) s
  rw [orthB_M A B hmask ht hs hts] at hexp
  have hsub : ({a, b} : Finset ℕ) ⊆ (dfr d).toFinset.filter (fun f => m.testBit f = true) := by
    intro k hk
    simp only [Finset.mem_insert, Finset.mem_singleton] at hk
    rcases hk with rfl | rfl
    · simp [haF, hma]
    · simp [hbF, hmb]
  rw [← Finset.sum_subset hsub (fun k hk hk' => by
    simp only [Finset.mem_insert, Finset.mem_singleton, not_or] at hk'
    simp only [Finset.mem_filter, List.mem_toFinset] at hk
    have hk0 := hF k hk.1
    rcases hz k hk.1 with ((((h | h) | h) | h) | h)
    · rw [hk.2] at h; exact absurd h (by simp)
    · exact absurd h hk'.1
    · exact absurd h hk'.2
    · rw [orthB_M A B hmask ht hk0 h, zero_mul, zero_div]
    · rw [orthB_M A B hmask hk0 hs h, mul_zero, zero_div]), Finset.sum_pair hab] at hexp
  have ha0 : Mx A B a a ≠ 0 := hdiag a ha
  have hb0 : Mx A B b b ≠ 0 := hdiag b hb
  have key : Mx A B t a * Mx A B a s * Mx A B b b + Mx A B t b * Mx A B b s * Mx A B a a =
      (Mx A B t a * Mx A B a s / Mx A B a a + Mx A B t b * Mx A B b s / Mx A B b b) *
        (Mx A B a a * Mx A B b b) := by
    field_simp <;> ring
  rw [← hexp, zero_mul] at key
  linear_combination key

/-- edge values `M / γ` on the table (`1` outside it) -/
def vM (A B : ℕ → Fin 9 → K) (ER EC : BT ℕ) (nE : ℕ) (e : ℕ) : K :=
  if e < nE then Mx A B (ER.get 0 e) (EC.get 0 e) / gam (ER.get 0 e) (EC.get 0 e) else 1

theorem sv_two (v : ℕ → K) (e : ℕ) : sv v (2 * e) = v e := by
  unfold sv; rw [if_pos (by omega)]; congr 1; omega

theorem sv_two_one (v : ℕ → K) (e : ℕ) : sv v (2 * e + 1) = (v e)⁻¹ := by
  unfold sv; rw [if_neg (by omega)]; congr 2; omega

theorem vM_edge (A B : ℕ → Fin 9 → K) (EI ER EC : BT ℕ) (nE x y : ℕ)
    (h : edgeOK EI ER EC nE x y = true) : vM A B ER EC nE (eid EI x y) = Mx A B x y / gam x y := by
  unfold edgeOK at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨h1, h2⟩, h3⟩ := h
  unfold vM; rw [if_pos h1, h2, h3]

theorem edge_nz (EI ER EC : BT ℕ) (nE x y : ℕ) (h : edgeOK EI ER EC nE x y = true) {P : ℕ → ℕ → Prop}
    (hP : ∀ e < nE, P (ER.get 0 e) (EC.get 0 e)) : P x y := by
  unfold edgeOK at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨h1, h2⟩, h3⟩ := h
  have := hP _ h1
  rw [h2, h3] at this
  exact this

/-- a checked descriptor gives a relation of product `1` for `v = M / γ` -/
theorem rp_relOf (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (EI ER EC : BT ℕ) (nE m : ℕ)
    (hMnz : ∀ e < nE, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0)
    (hGnz : ∀ e < nE, gam (K := K) (ER.get 0 e) (EC.get 0 e) ≠ 0)
    (d : List ℕ) (hd : descOK EI ER EC nE m d = true) (hE : ExpOK A B m (dfr d)) :
    rp (vM A B ER EC nE) (relOf EI d) = 1 := by
  have hrel := desc_relation A B hdiag hmask EI ER EC nE m d hd hE
  unfold descOK at hd
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hd
  obtain ⟨⟨⟨⟨⟨⟨⟨hd0, hG⟩, e1⟩, e2⟩, e3⟩, e4⟩, e5⟩, e6⟩ := hd
  have hlen : 5 ≤ d.length := hd0.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1
  unfold relOf
  rw [if_neg (by omega)]
  set t := d.getD 0 0; set a := d.getD 1 0; set s := d.getD 2 0; set b := d.getD 3 0
  have hGK : gam (K := K) t a * gam a s * gam b b = -(gam t b * gam b s * gam a a) := by
    have q1 : gam (K := K) t a * gam a s * gam b b = ((dot t a * dot a s * dot b b : ℤ) : K) / 5832 := by
      unfold gam; push_cast; ring
    have q2 : gam (K := K) t b * gam b s * gam a a = ((dot t b * dot b s * dot a a : ℤ) : K) / 5832 := by
      unfold gam; push_cast; ring
    rw [q1, q2, hG]; push_cast; ring
  have m1 := edge_nz EI ER EC nE t a e1 (P := fun x y => Mx A B x y ≠ 0) hMnz; have m2 := edge_nz EI ER EC nE a s e2 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m3 := edge_nz EI ER EC nE b b e3 (P := fun x y => Mx A B x y ≠ 0) hMnz; have m4 := edge_nz EI ER EC nE t b e4 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have m5 := edge_nz EI ER EC nE b s e5 (P := fun x y => Mx A B x y ≠ 0) hMnz; have m6 := edge_nz EI ER EC nE a a e6 (P := fun x y => Mx A B x y ≠ 0) hMnz
  have g1 := edge_nz EI ER EC nE t a e1 (P := fun x y => gam (K := K) x y ≠ 0) hGnz; have g2 := edge_nz EI ER EC nE a s e2 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g3 := edge_nz EI ER EC nE b b e3 (P := fun x y => gam (K := K) x y ≠ 0) hGnz; have g4 := edge_nz EI ER EC nE t b e4 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  have g5 := edge_nz EI ER EC nE b s e5 (P := fun x y => gam (K := K) x y ≠ 0) hGnz; have g6 := edge_nz EI ER EC nE a a e6 (P := fun x y => gam (K := K) x y ≠ 0) hGnz
  by_cases ho : d.getD 4 0 = 1
  · simp only [ho, ↓reduceIte, Nat.add_zero, Nat.sub_zero]
    unfold rp
    simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one, sv_two, sv_two_one]
    rw [vM_edge A B EI ER EC nE _ _ e1, vM_edge A B EI ER EC nE _ _ e2, vM_edge A B EI ER EC nE _ _ e3,
      vM_edge A B EI ER EC nE _ _ e4, vM_edge A B EI ER EC nE _ _ e5, vM_edge A B EI ER EC nE _ _ e6]
    field_simp
    first
    | linear_combination (gam t b * gam b s * gam a a) * hrel - (Mx A B t b * Mx A B b s * Mx A B a a) * hGK
    | linear_combination (Mx A B t b * Mx A B b s * Mx A B a a) * hGK - (gam t b * gam b s * gam a a) * hrel
  · simp only [ho, ↓reduceIte, Nat.sub_self, Nat.add_zero]
    unfold rp
    simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one, sv_two, sv_two_one]
    rw [vM_edge A B EI ER EC nE _ _ e1, vM_edge A B EI ER EC nE _ _ e2, vM_edge A B EI ER EC nE _ _ e3,
      vM_edge A B EI ER EC nE _ _ e4, vM_edge A B EI ER EC nE _ _ e5, vM_edge A B EI ER EC nE _ _ e6]
    field_simp
    first
    | linear_combination (gam t b * gam b s * gam a a) * hrel - (Mx A B t b * Mx A B b s * Mx A B a a) * hGK
    | linear_combination (Mx A B t b * Mx A B b s * Mx A B a a) * hGK - (gam t b * gam b s * gam a a) * hrel

/-! ## The glued statement -/

def erF (ER : BT ℕ) (e : ℕ) : ℕ := ER.get 0 e
def dgF (ER EC : BT ℕ) (e : ℕ) : Bool := decide (ER.get 0 e = EC.get 0 e)

/-- stored relation `a`: its descriptor's six-edge list, descriptor checked (or empty), balanced -/
def rsOK (C : Cert) (EI ER EC : BT ℕ) (DS : BT (List ℕ)) (nE m a : ℕ) : Bool :=
  decide (C.RS.get [] a = relOf EI (DS.get [] a)) &&
  (decide (DS.get [] a = []) || descOK EI ER EC nE m (DS.get [] a)) &&
  decide (nrm (rowL (erF ER) (C.RS.get [] a)) = []) && decide (nrm (rowL (erF EC) (C.RS.get [] a)) = []) &&
  decide (nrm (diagL (dgF ER EC) (C.RS.get [] a)) = [])

/-- all checks of one T2 case besides `check C` -/
def glueOK (C : Cert) (EI ER EC : BT ℕ) (DS : BT (List ℕ)) (nE m : ℕ) (T : List (ℕ × Bool)) (r0 d0 : ℕ) : Bool :=
  (List.range (2 ^ max C.RS.dp DS.dp)).all (rsOK C EI ER EC DS nE m) &&
  (List.range nE).all (fun e => decide (dot (ER.get 0 e) (EC.get 0 e) ≠ 0)) &&
  bfsOK (erF ER) (erF EC) (dgF ER EC) T [r0] [] && dgF ER EC d0 &&
  C.GA.all (fun e => decide (e = d0) || (T.map Prod.fst).contains e)

theorem rsOK_all (C : Cert) (EI ER EC : BT ℕ) (DS : BT (List ℕ)) (nE m : ℕ)
    (h : (List.range (2 ^ max C.RS.dp DS.dp)).all (rsOK C EI ER EC DS nE m) = true) (a : ℕ) :
    rsOK C EI ER EC DS nE m a = true := by
  by_cases ha : a < 2 ^ max C.RS.dp DS.dp
  · exact List.all_eq_true.mp h a (List.mem_range.mpr ha)
  · have h1 : C.RS.get [] a = [] :=
      BT.get_big _ _ _ (le_trans (Nat.pow_le_pow_right (by norm_num) (le_max_left _ _)) (Nat.not_lt.mp ha))
    have h2 : DS.get [] a = [] :=
      BT.get_big _ _ _ (le_trans (Nat.pow_le_pow_right (by norm_num) (le_max_right _ _)) (Nat.not_lt.mp ha))
    unfold rsOK; rw [h1, h2]; unfold relOf; simp [nrm, rowL, diagL]

/-- **T2.3 for one case.** A checked closure certificate, glued to the matrix by checked descriptors, gives row and
column scalings (and one diagonal scale) under which every needed edge has `M x y / γ x y = 1`. -/
theorem t2_close (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (C : Cert) (EI ER EC : BT ℕ)
    (DS : BT (List ℕ)) (nE m : ℕ) (T : List (ℕ × Bool)) (r0 d0 : ℕ) (hc : check C = true)
    (hg : glueOK C EI ER EC DS nE m T r0 d0 = true)
    (hExp : ∀ a, DS.get [] a ≠ [] → ExpOK A B m (dfr (DS.get [] a)))
    (hMnz : ∀ e < nE, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0) :
    ∃ (p q : ℕ → K) (l : K), (∀ x, p x ≠ 0) ∧ (∀ x, q x ≠ 0) ∧ l ≠ 0 ∧
      ∀ e ∈ C.NE, gv (vM A B ER EC nE) p q l (erF ER) (erF EC) (dgF ER EC) e = 1 := by
  unfold glueOK at hg
  simp only [Bool.and_eq_true, List.all_eq_true, List.mem_range, decide_eq_true_eq] at hg
  obtain ⟨⟨⟨⟨hrs, hdot⟩, hbfs⟩, hd0⟩, hGA⟩ := hg
  have hrs' := rsOK_all C EI ER EC DS nE m (List.all_eq_true.mpr fun a ha => hrs a (List.mem_range.mp ha))
  have hGnz : ∀ e < nE, gam (K := K) (ER.get 0 e) (EC.get 0 e) ≠ 0 := by
    intro e he; unfold gam
    exact div_ne_zero (by exact_mod_cast hdot e he) (by norm_num)
  have hv : ∀ e, vM A B ER EC nE e ≠ 0 := by
    intro e; unfold vM; split_ifs with he
    · exact div_ne_zero (hMnz e he) (hGnz e he)
    · exact one_ne_zero
  obtain ⟨p, q, l, hp, hq, hl, hgv, hT, hd⟩ :=
    gauge_exists (vM A B ER EC nE) hv (erF ER) (erF EC) (dgF ER EC) T r0 d0 hbfs hd0
  refine ⟨p, q, l, hp, hq, hl, ?_⟩
  refine closure_sound C _ hc ?_ hgv ?_
  · intro a
    have ha := hrs' a
    unfold rsOK at ha
    simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at ha
    obtain ⟨⟨⟨⟨hra, hdesc⟩, b1⟩, b2⟩, b3⟩ := ha
    rw [rp_gauge _ p q l _ _ _ hp hq hl _ b1 b2 b3, hra]
    by_cases h0 : DS.get [] a = []
    · rw [h0]; unfold relOf; simp [rp]
    · rcases hdesc with h0' | hok
      · exact absurd h0' h0
      · exact rp_relOf A B hdiag hmask EI ER EC nE m hMnz hGnz _ hok (hExp a h0)
  · intro e he
    have hge := hGA e he
    simp only [Bool.or_eq_true, decide_eq_true_eq] at hge
    rcases hge with h | h
    · rw [h]; exact hd
    · obtain ⟨eb, heb, hee⟩ := List.mem_map.mp (List.contains_iff_mem.mp h)
      rw [← hee]; exact hT eb heb

end RankNine.T2
