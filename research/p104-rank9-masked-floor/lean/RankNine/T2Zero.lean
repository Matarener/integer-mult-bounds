import RankNine.T2Exp
import RankNine.Zero

/-!
# T2 zero step (RUP certificate)

The gluing step `t2_close` needs `M x y ≠ 0` on every edge of the case's edge table.  Variables of the CNF have a
meaning given by the table `VT`: `[0, t, s]` is `M t s = 0`, `[1, t, f, s]` is `M t f * M f s ≠ 0`.  Clauses
(entries of `EN`, kind first):
* `[0, k, p, a, b]`: definitions of a product variable `p = [1, t, f, s]` (`a = [0, t, f]`, `b = [0, f, s]`):
  `k = 0`: `¬p ∨ ¬a`, `k = 1`: `¬p ∨ ¬b`, `k = 2`: `p ∨ a ∨ b`;
* `[1, fi, t, s, z, p₁, …]`: expansion of `M t s` along the admissible frame `FT fi`: `M t s ≠ 0` (or `t = s`) gives a
  non-zero term (`z = 0` when `t = s`);
* `[2, fi, t, s, z, i, p₁, …]`: `M t s = 0` (variable `z`, or `z = 0` when `t ⊥ s` or `s = s₀`) and term `i` non-zero
  give another non-zero term;
* `[3]`: the goal: some off-diagonal edge is zero (bit mask `G`);
* `[4, nl, lits…, hints…]`: a lemma (literal `2 c + 1` is `c`, `2 c` is `¬ c`) with RUP hints (entry, unit variable).
The terms of an expansion are recomputed here: the dead frame lines `f` with `t ̸⊥ f`, `f ̸⊥ s`, `s ≠ s₀`
(`terms`).  Frames are admissible by `ExpOK` (`T2Exp`: branch (a) non-degeneracy, branch (b) frames in the dead set);
`s₀` is the vanishing column of branch (b) (`s₀ ≥ 104` for no column).
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

/-- meaning of a variable -/
def zSem (A B : ℕ → Fin 9 → K) (VT : BT (List ℕ)) (i : ℕ) : Prop :=
  if (VT.get [] i).length = 3 ∧ (VT.get [] i).getD 0 9 = 0 then
    Mx A B ((VT.get [] i).getD 1 0) ((VT.get [] i).getD 2 0) = 0
  else if (VT.get [] i).length = 4 ∧ (VT.get [] i).getD 0 9 = 1 then
    Mx A B ((VT.get [] i).getD 1 0) ((VT.get [] i).getD 2 0) *
      Mx A B ((VT.get [] i).getD 2 0) ((VT.get [] i).getD 3 0) ≠ 0
  else False

theorem zSem_z (A B : ℕ → Fin 9 → K) (VT : BT (List ℕ)) (i t s : ℕ) (h : VT.get [] i = [0, t, s]) :
    zSem A B VT i ↔ Mx A B t s = 0 := by
  unfold zSem; rw [h]; simp

theorem zSem_p (A B : ℕ → Fin 9 → K) (VT : BT (List ℕ)) (i t f s : ℕ) (h : VT.get [] i = [1, t, f, s]) :
    zSem A B VT i ↔ Mx A B t f * Mx A B f s ≠ 0 := by
  unfold zSem; rw [h]; simp

theorem list4 (w : List ℕ) (hl : w.length = 4) (h1 : w.getD 0 9 = 1) :
    w = [1, w.getD 1 0, w.getD 2 0, w.getD 3 0] := by
  match w, hl with
  | [a, b, c, d], _ => simp_all

/-- bit mask of a list of variables -/
def mk : List ℕ → ℕ
  | [] => 0
  | x :: l => 2 ^ x ||| mk l

theorem mk_bit (l : List ℕ) (i : ℕ) : (mk l).testBit i = true ↔ i ∈ l := by
  induction l with
  | nil => simp [mk, bit_zero]
  | cons x l ih =>
    simp only [mk, bit_or, Bool.or_eq_true, bit_pow, ih, List.mem_cons]

def kz (s0 x y : ℕ) : Bool := orthB x y || y == s0

/-- the terms of the expansion of `M t s` along the frame `F` -/
def terms (m s0 : ℕ) (F : List ℕ) (t s : ℕ) : List ℕ :=
  F.filter fun f => m.testBit f && !kz s0 t f && !kz s0 f s

def zl (z : ℕ) : List ℕ := if z = 0 then [] else [z]

def litsP (L : List ℕ) : List ℕ := (L.filter (fun x => x % 2 = 1)).map (· / 2)
def litsN (L : List ℕ) : List ℕ := (L.filter (fun x => x % 2 = 0)).map (· / 2)

def hp : List ℕ → List (ℕ × ℕ)
  | a :: b :: r => (a, b) :: hp r
  | _ => []

/-- the clause of an entry -/
def clOf (G : ℕ) (e : List ℕ) : ℕ × ℕ :=
  if e.getD 0 9 = 0 then
    (if e.getD 1 0 = 0 then (0, mk [e.getD 2 0, e.getD 3 0])
     else if e.getD 1 0 = 1 then (0, mk [e.getD 2 0, e.getD 4 0])
     else (mk [e.getD 2 0, e.getD 3 0, e.getD 4 0], 0))
  else if e.getD 0 9 = 1 then (mk (zl (e.getD 4 0) ++ e.drop 5), 0)
  else if e.getD 0 9 = 2 then
    (mk ((e.drop 6).eraseIdx (e.getD 5 0)), mk (zl (e.getD 4 0) ++ [(e.drop 6).getD (e.getD 5 0) 0]))
  else if e.getD 0 9 = 3 then (G, 0)
  else (mk (litsP ((e.drop 2).take (e.getD 1 0))), mk (litsN ((e.drop 2).take (e.getD 1 0))))

/-- frame, rows and term variables of an expansion entry -/
def tOK (m s0 : ℕ) (VT FT : BT (List ℕ)) (fi t s : ℕ) (ps : List ℕ) : Bool :=
  decide (FT.get [] fi ≠ []) && (FT.get [] fi).all (· < 104) && decide (t < 104) && decide (s < 104) &&
  m.testBit t && (FT.get [] fi).all (fun f => m.testBit f || orthB t f) &&
  decide (ps.length = (terms m s0 (FT.get [] fi) t s).length) &&
  (List.range ps.length).all (fun j => VT.get [] (ps.getD j 0) == [1, t, (terms m s0 (FT.get [] fi) t s).getD j 0, s])

def entryOK (m s0 G : ℕ) (VT FT EN : BT (List ℕ)) (j : ℕ) : Bool :=
  let e := EN.get [] j
  if e.getD 0 9 = 0 then
    decide (e.getD 1 0 < 3) &&
    (let w := VT.get [] (e.getD 2 0)
     decide (w.length = 4) && decide (w.getD 0 9 = 1) &&
     VT.get [] (e.getD 3 0) == [0, w.getD 1 0, w.getD 2 0] && VT.get [] (e.getD 4 0) == [0, w.getD 2 0, w.getD 3 0])
  else if e.getD 0 9 = 1 then
    tOK m s0 VT FT (e.getD 1 0) (e.getD 2 0) (e.getD 3 0) (e.drop 5) &&
    (if e.getD 4 0 = 0 then decide (e.getD 2 0 = e.getD 3 0)
     else VT.get [] (e.getD 4 0) == [0, e.getD 2 0, e.getD 3 0])
  else if e.getD 0 9 = 2 then
    tOK m s0 VT FT (e.getD 1 0) (e.getD 2 0) (e.getD 3 0) (e.drop 6) && decide (e.getD 5 0 < (e.drop 6).length) &&
    (if e.getD 4 0 = 0 then kz s0 (e.getD 2 0) (e.getD 3 0)
     else VT.get [] (e.getD 4 0) == [0, e.getD 2 0, e.getD 3 0])
  else if e.getD 0 9 = 3 then true
  else
    decide (e.getD 0 9 = 4) && (hp ((e.drop 2).drop (e.getD 1 0))).all (fun h => decide (h.1 < j)) &&
    rupRun (fun i => clOf G (EN.get [] i)) (hp ((e.drop 2).drop (e.getD 1 0))) (clOf G e).2 (clOf G e).1

/-! ## Soundness -/

theorem mem_terms {m s0 : ℕ} {F : List ℕ} {t s f : ℕ} (h : f ∈ terms m s0 F t s) :
    f ∈ F ∧ m.testBit f = true ∧ kz s0 t f = false ∧ kz s0 f s = false := by
  unfold terms at h
  simp only [List.mem_filter, Bool.and_eq_true, Bool.not_eq_true'] at h
  exact ⟨h.1, h.2.1.1, h.2.1.2, h.2.2⟩

/-- the expansion restricted to its terms -/
theorem exp_terms (A B : ℕ → Fin 9 → K) (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (m s0 : ℕ) (hs0 : s0 < 104 → ∀ x, m.testBit x = true → Mx A B x s0 = 0) (F : List ℕ) (hE : ExpOK A B m F)
    (hF : F.all (· < 104) = true) (t s : ℕ) (ht : t < 104) (hs : s < 104) (hmt : m.testBit t = true)
    (hout : F.all (fun f => m.testBit f || orthB t f) = true) :
    Mx A B t s = ∑ f ∈ (terms m s0 F t s).toFinset, Mx A B t f * Mx A B f s / Mx A B f f := by
  have hF' : ∀ f ∈ F, f < 104 := fun f hf => of_decide_eq_true (List.all_eq_true.mp hF f hf)
  rw [hE t hmt (fun f hf hdf => by
    have h := List.all_eq_true.mp hout f hf
    rw [hdf, Bool.false_or] at h
    exact orthB_M A B hmask ht (hF' f hf) h) s]
  symm
  apply Finset.sum_subset
  · intro f hf
    have h := mem_terms (List.mem_toFinset.mp hf)
    simp only [Finset.mem_filter, List.mem_toFinset]
    exact ⟨h.1, h.2.1⟩
  · intro f hf hnf
    simp only [Finset.mem_filter, List.mem_toFinset] at hf
    have hf0 := hF' f hf.1
    have hnt : (m.testBit f && !kz s0 t f && !kz s0 f s) = false := by
      by_contra hc
      apply hnf
      rw [List.mem_toFinset]; unfold terms
      exact List.mem_filter.mpr ⟨hf.1, by simpa using hc⟩
    rcases Bool.eq_false_or_eq_true (kz s0 t f) with h1 | h1
    · simp only [kz, Bool.or_eq_true, beq_iff_eq] at h1
      rcases h1 with h | h
      · rw [orthB_M A B hmask ht hf0 h, zero_mul, zero_div]
      · rw [h, hs0 (h ▸ hf0) t hmt, zero_mul, zero_div]
    · simp only [hf.2, h1, Bool.not_false, Bool.true_and, Bool.not_eq_false'] at hnt
      simp only [kz, Bool.or_eq_true, beq_iff_eq] at hnt
      rcases hnt with h | h
      · rw [orthB_M A B hmask hf0 hs h, mul_zero, zero_div]
      · rw [h, hs0 (h ▸ hs) f hf.2, mul_zero, zero_div]

theorem tOK_facts {m s0 : ℕ} {VT FT : BT (List ℕ)} {fi t s : ℕ} {ps : List ℕ} (h : tOK m s0 VT FT fi t s ps = true) :
    FT.get [] fi ≠ [] ∧ (FT.get [] fi).all (· < 104) = true ∧ t < 104 ∧ s < 104 ∧ m.testBit t = true ∧
      (FT.get [] fi).all (fun f => m.testBit f || orthB t f) = true ∧
      ps.length = (terms m s0 (FT.get [] fi) t s).length ∧
      ∀ j < ps.length, VT.get [] (ps.getD j 0) = [1, t, (terms m s0 (FT.get [] fi) t s).getD j 0, s] := by
  unfold tOK at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8⟩ := h
  refine ⟨h1, ?_, h3, h4, h5, ?_, h7, h8⟩
  · exact List.all_eq_true.mpr fun f hf => decide_eq_true (h2 f hf)
  · exact List.all_eq_true.mpr h6

/-- a term variable is true iff its product is non-zero; the products of the terms -/
theorem term_sem (A B : ℕ → Fin 9 → K) {m s0 : ℕ} {VT FT : BT (List ℕ)} {fi t s : ℕ} {ps : List ℕ}
    (h : tOK m s0 VT FT fi t s ps = true) (j : ℕ) (hj : j < ps.length) :
    (zSem A B VT (ps.getD j 0) ↔ Mx A B t ((terms m s0 (FT.get [] fi) t s).getD j 0) *
      Mx A B ((terms m s0 (FT.get [] fi) t s).getD j 0) s ≠ 0) :=
  zSem_p A B VT _ _ _ _ ((tOK_facts h).2.2.2.2.2.2.2 j hj)

theorem getD_mem_of_lt {L : List ℕ} {j : ℕ} (h : j < L.length) : L.getD j 0 ∈ L := by
  rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem h, Option.getD_some]; exact List.getElem_mem _

theorem mem_getD {L : List ℕ} {f : ℕ} (h : f ∈ L) : ∃ j < L.length, L.getD j 0 = f := by
  obtain ⟨j, hj, rfl⟩ := List.getElem_of_mem h
  exact ⟨j, hj, by rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj, Option.getD_some]⟩

theorem csat_pos {z : ℕ → Prop} {P Q : ℕ} {i : ℕ} (hb : P.testBit i = true) (hz : z i) : CSat z (P, Q) :=
  ⟨i, Or.inl ⟨hb, hz⟩⟩

theorem csat_neg {z : ℕ → Prop} {P Q : ℕ} {i : ℕ} (hb : Q.testBit i = true) (hz : ¬ z i) : CSat z (P, Q) :=
  ⟨i, Or.inr ⟨hb, hz⟩⟩

/-- one entry is a true clause, given the earlier ones -/
theorem zentry_sound (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (m s0 G : ℕ)
    (hs0 : s0 < 104 → ∀ x, m.testBit x = true → Mx A B x s0 = 0) (VT FT EN : BT (List ℕ))
    (hFT : ∀ fi, FT.get [] fi ≠ [] → ExpOK A B m (FT.get [] fi))
    (hgoal : ∃ i, G.testBit i = true ∧ zSem A B VT i) (j : ℕ) (hok : entryOK m s0 G VT FT EN j = true)
    (hprev : ∀ i < j, CSat (zSem A B VT) (clOf G (EN.get [] i))) :
    CSat (zSem A B VT) (clOf G (EN.get [] j)) := by
  unfold entryOK at hok
  try dsimp only at hok
  set e := EN.get [] j with he
  unfold clOf
  by_cases k0 : e.getD 0 9 = 0
  · -- definitions of a product variable
    rw [if_pos k0] at hok ⊢
    simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hok
    obtain ⟨-, ⟨⟨hl, h1⟩, ha⟩, hb⟩ := hok
    obtain ⟨w, hw⟩ : ∃ w, VT.get [] (e.getD 2 0) = w := ⟨_, rfl⟩
    rw [hw] at hl h1 ha hb
    have sp := zSem_p A B VT _ _ _ _ (hw.trans (list4 w hl h1))
    have sa := zSem_z A B VT _ _ _ ha
    have sb := zSem_z A B VT _ _ _ hb
    by_cases hp0 : zSem A B VT (e.getD 2 0)
    · have hpr := sp.mp hp0
      by_cases k1 : e.getD 1 0 = 0
      · rw [if_pos k1]
        refine csat_neg (i := e.getD 3 0) ((mk_bit _ _).mpr (by simp)) (fun hz => hpr ?_)
        rw [sa.mp hz, zero_mul]
      · by_cases k2 : e.getD 1 0 = 1
        · rw [if_neg k1, if_pos k2]
          refine csat_neg (i := e.getD 4 0) ((mk_bit _ _).mpr (by simp)) (fun hz => hpr ?_)
          rw [sb.mp hz, mul_zero]
        · rw [if_neg k1, if_neg k2]
          exact csat_pos (i := e.getD 2 0) ((mk_bit _ _).mpr (by simp)) hp0
    · by_cases k1 : e.getD 1 0 = 0
      · rw [if_pos k1]; exact csat_neg (i := e.getD 2 0) ((mk_bit _ _).mpr (by simp)) hp0
      · by_cases k2 : e.getD 1 0 = 1
        · rw [if_neg k1, if_pos k2]; exact csat_neg (i := e.getD 2 0) ((mk_bit _ _).mpr (by simp)) hp0
        · rw [if_neg k1, if_neg k2]
          have hnz : ¬ (Mx A B (w.getD 1 0) (w.getD 2 0) * Mx A B (w.getD 2 0) (w.getD 3 0) ≠ 0) :=
            fun h => hp0 (sp.mpr h)
          push_neg at hnz
          rcases mul_eq_zero.mp hnz with h | h
          · exact csat_pos (i := e.getD 3 0) ((mk_bit _ _).mpr (by simp)) (sa.mpr h)
          · exact csat_pos (i := e.getD 4 0) ((mk_bit _ _).mpr (by simp)) (sb.mpr h)
  rw [if_neg k0] at hok ⊢
  by_cases k1 : e.getD 0 9 = 1
  · -- expansion: a non-zero entry has a non-zero term
    rw [if_pos k1] at hok ⊢
    simp only [Bool.and_eq_true] at hok
    obtain ⟨htok, hz⟩ := hok
    obtain ⟨hne, hF, ht, hs, hmt, hout, hlen, -⟩ := tOK_facts htok
    set t := e.getD 2 0; set s := e.getD 3 0; set L := terms m s0 (FT.get [] (e.getD 1 0)) t s
    have hexp := exp_terms A B hmask m s0 hs0 _ (hFT _ hne) hF t s ht hs hmt hout
    have hF' : ∀ f ∈ FT.get [] (e.getD 1 0), f < 104 := fun f hf => of_decide_eq_true (List.all_eq_true.mp hF f hf)
    by_contra hn
    have hall : ∀ v ∈ zl (e.getD 4 0) ++ e.drop 5, ¬ zSem A B VT v :=
      fun v hv hzv => hn (csat_pos (i := v) ((mk_bit _ _).mpr hv) hzv)
    have hts : Mx A B t s ≠ 0 := by
      by_cases hz0 : e.getD 4 0 = 0
      · rw [if_pos hz0] at hz
        have := of_decide_eq_true hz
        rw [this]; exact hdiag s hs
      · rw [if_neg hz0] at hz
        have := zSem_z A B VT (e.getD 4 0) t s (by simpa using hz)
        intro h0
        exact hall _ (by simp [zl, hz0]) (this.mpr h0)
    apply hts
    rw [hexp]
    refine Finset.sum_eq_zero fun f hf => ?_
    obtain ⟨jj, hjj, rfl⟩ := mem_getD (List.mem_toFinset.mp hf)
    have hj' : jj < (e.drop 5).length := by omega
    have hzj := hall _ (List.mem_append_right _ (getD_mem_of_lt hj'))
    rw [term_sem A B htok jj hj'] at hzj
    push_neg at hzj
    rw [hzj, zero_div]
  rw [if_neg k1] at hok ⊢
  by_cases k2 : e.getD 0 9 = 2
  · -- zero entry: never exactly one non-zero term
    rw [if_pos k2] at hok ⊢
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
    obtain ⟨⟨htok, hi⟩, hz⟩ := hok
    obtain ⟨hne, hF, ht, hs, hmt, hout, hlen, -⟩ := tOK_facts htok
    set t := e.getD 2 0; set s := e.getD 3 0; set L := terms m s0 (FT.get [] (e.getD 1 0)) t s
    set ps := e.drop 6; set i := e.getD 5 0
    have hexp := exp_terms A B hmask m s0 hs0 _ (hFT _ hne) hF t s ht hs hmt hout
    have hF' : ∀ f ∈ FT.get [] (e.getD 1 0), f < 104 := fun f hf => of_decide_eq_true (List.all_eq_true.mp hF f hf)
    by_contra hn
    have hP : ∀ v ∈ ps.eraseIdx i, ¬ zSem A B VT v := fun v hv hzv => hn (csat_pos (i := v) ((mk_bit _ _).mpr hv) hzv)
    have hQ : ∀ v ∈ zl (e.getD 4 0) ++ [ps.getD i 0], zSem A B VT v :=
      fun v hv => by_contra fun hzv => hn (csat_neg (i := v) ((mk_bit _ _).mpr hv) hzv)
    have hts : Mx A B t s = 0 := by
      by_cases hz0 : e.getD 4 0 = 0
      · rw [if_pos hz0] at hz
        simp only [kz, Bool.or_eq_true, beq_iff_eq] at hz
        rcases hz with h | h
        · exact orthB_M A B hmask ht hs h
        · rw [h]; exact hs0 (h ▸ hs) t hmt
      · rw [if_neg hz0] at hz
        exact (zSem_z A B VT (e.getD 4 0) t s (by simpa using hz)).mp (hQ _ (by simp [zl, hz0]))
    have hpi := (term_sem A B htok i hi).mp (hQ _ (by simp))
    have hiL : i < L.length := by omega
    have hfi := getD_mem_of_lt hiL
    have hfi0 : L.getD i 0 < 104 := hF' _ (mem_terms hfi).1
    rw [hexp, Finset.sum_eq_single_of_mem (L.getD i 0) (List.mem_toFinset.mpr hfi)] at hts
    · exact div_ne_zero hpi (hdiag _ hfi0) hts
    · intro f hf hfne
      obtain ⟨jj, hjj, rfl⟩ := mem_getD (List.mem_toFinset.mp hf)
      have hj' : jj < ps.length := by omega
      have hji : jj ≠ i := fun h => hfne (by rw [h])
      have hmem : ps.getD jj 0 ∈ ps.eraseIdx i := by
        rw [List.mem_eraseIdx_iff_getElem]
        exact ⟨jj, hj', hji, by rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj', Option.getD_some]⟩
      have hzj := hP _ hmem
      rw [term_sem A B htok jj hj'] at hzj
      push_neg at hzj
      rw [hzj, zero_div]
  rw [if_neg k2] at hok ⊢
  by_cases k3 : e.getD 0 9 = 3
  · rw [if_pos k3]
    obtain ⟨i, hb, hz⟩ := hgoal
    exact csat_pos (i := i) hb hz
  rw [if_neg k3] at hok ⊢
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hok
  obtain ⟨⟨-, hlt⟩, hrup⟩ := hok
  have h := rup_sound (zSem A B VT) (fun i => clOf G (EN.get [] i)) (clOf G e) _
    (fun h hh => hprev h.1 (hlt h hh)) hrup
  unfold clOf at h
  rw [if_neg k0, if_neg k1, if_neg k2, if_neg k3] at h
  exact h

/-- **T2 zero step.** A checked certificate whose last entry is the empty clause: every edge of the table is
non-zero. -/
theorem t2_zero (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (m s0 G : ℕ)
    (hs0 : s0 < 104 → ∀ x, m.testBit x = true → Mx A B x s0 = 0) (VT FT EN : BT (List ℕ))
    (hFT : ∀ fi, FT.get [] fi ≠ [] → ExpOK A B m (FT.get [] fi)) (n : ℕ)
    (hall : (List.range n).all (entryOK m s0 G VT FT EN) = true) (hlast : clOf G (EN.get [] (n - 1)) = (0, 0))
    (hn : 0 < n) (ER EC GV : BT ℕ) (nE : ℕ)
    (hG : (List.range nE).all (fun e => decide (ER.get 0 e < 104) && (decide (ER.get 0 e = EC.get 0 e) ||
      (G.testBit (GV.get 0 e) && VT.get [] (GV.get 0 e) == [0, ER.get 0 e, EC.get 0 e]))) = true) :
    ∀ e < nE, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0 := by
  intro e he hz
  have hge := List.all_eq_true.mp hG e (List.mem_range.mpr he)
  simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, beq_iff_eq] at hge
  obtain ⟨hlt, hge⟩ := hge
  rcases hge with hd | ⟨hb, hv⟩
  · rw [← hd] at hz; exact hdiag _ hlt hz
  have hgoal : ∃ i, G.testBit i = true ∧ zSem A B VT i := ⟨_, hb, (zSem_z A B VT _ _ _ hv).mpr hz⟩
  have key : ∀ j, j < n → CSat (zSem A B VT) (clOf G (EN.get [] j)) := by
    intro j
    induction j using Nat.strong_induction_on with
    | _ j ih =>
      intro hj
      exact zentry_sound A B hdiag hmask m s0 G hs0 VT FT EN hFT hgoal j
        (List.all_eq_true.mp hall j (List.mem_range.mpr hj)) (fun i hi => ih i hi (by omega))
  have := key (n - 1) (by omega)
  rw [hlast] at this
  exact csat_empty _ this

end RankNine.T2
