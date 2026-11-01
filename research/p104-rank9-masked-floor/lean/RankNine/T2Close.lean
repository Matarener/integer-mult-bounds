import Mathlib

/-!
# T2.3: exact closure certificates for a ratio cocycle (any field)

Edge values `v : ℕ → K`, all non-zero.  A relation is a list of signed edges `q` (edge `q / 2`, inverted when `q` is
odd) whose product is `1`.  The gauge edges (a spanning tree and one diagonal) have value `1`.  A certificate is a
list of steps; step `i` (from `1`) assigns edges or classes:
* **peel** `[0, r₁, r₂, e]`: in the relation `RS r₁ ++ RS r₂` only `e` is unassigned (once); then `v e` is the
  product of the assigned part;
* **class** `[1, k, root, o₁, o₂, m₁, p₁, a₁, b₁, s₁, …]`: members `m` linked to an earlier member `p` by the
  relation `RS a ++ RS b` (only `m`, `p` unassigned, assigned part trivial), sign `s` (`v m = v root ^ (±1)`);
  the odd relation `RS o₁ ++ RS o₂` gives `v root ^ 2 = 1`; the class value is `c k = v root`;
* **fix** `[2, k, r₁, r₂]`: a fully assigned relation whose class mask, up to classes fixed earlier, is `{k}`:
  `c k = 1`.
Invariant: every assigned edge has `v e = Π_{k ∈ MK e} c k` (`cval`), every created class has `c k ^ 2 = 1`, every
fixed class has `c k = 1`.  At the end every needed edge has a mask made of fixed classes, so `v e = 1`.
-/

namespace RankNine.T2

variable {K : Type*} [Field K]

/-- value of a signed edge -/
def sv (v : ℕ → K) (q : ℕ) : K := if q % 2 = 0 then v (q / 2) else (v (q / 2))⁻¹

/-- product of a relation -/
def rp (v : ℕ → K) (r : List ℕ) : K := (r.map (sv v)).prod

/-- class value of a mask -/
def cval (c : ℕ → K) (n m : ℕ) : K := ((List.range n).map fun k => if m.testBit k then c k else 1).prod

theorem prod_split (f : ℕ → K) (p : ℕ → Bool) (l : List ℕ) :
    (l.map f).prod = ((l.filter p).map f).prod * ((l.filter fun q => !p q).map f).prod := by
  induction l with
  | nil => simp
  | cons a l ih =>
    by_cases h : p a = true
    · simp [List.filter_cons, h, ih, mul_assoc]
    · simp [List.filter_cons, h, ih]; ring

theorem cval_xor (c : ℕ → K) (n m₁ m₂ : ℕ)
    (hc : ∀ k < n, (m₁.testBit k = true ∨ m₂.testBit k = true) → c k * c k = 1) :
    cval c n (m₁ ^^^ m₂) = cval c n m₁ * cval c n m₂ := by
  unfold cval
  rw [← List.prod_map_mul]
  congr 1
  apply List.map_congr_left
  intro k hk
  have hn := hc k (List.mem_range.mp hk)
  rw [Nat.testBit_xor]
  cases h1 : m₁.testBit k <;> cases h2 : m₂.testBit k <;> simp [h1, h2] at hn ⊢
  exact hn.symm

theorem cval_zero (c : ℕ → K) (n : ℕ) : cval c n 0 = 1 := by
  simp [cval]

theorem cval_sq (c : ℕ → K) (n m : ℕ) (hc : ∀ k < n, m.testBit k = true → c k * c k = 1) :
    cval c n m * cval c n m = 1 := by
  rw [← cval_xor c n m m (fun k hk h => hc k hk (by tauto)), Nat.xor_self, cval_zero]

theorem cval_fix (c : ℕ → K) (n m₁ m₂ : ℕ) (hc : ∀ k < n, (m₁ ^^^ m₂).testBit k = true → c k = 1) :
    cval c n m₁ = cval c n m₂ := by
  unfold cval
  congr 1
  apply List.map_congr_left
  intro k hk
  have hk' := List.mem_range.mp hk
  have := hc k hk'
  rw [Nat.testBit_xor] at this
  cases h1 : m₁.testBit k <;> cases h2 : m₂.testBit k <;> simp_all

theorem cval_single (c : ℕ → K) (n k : ℕ) (hk : k < n) : cval c n (2 ^ k) = c k := by
  unfold cval
  induction n with
  | zero => omega
  | succ n ih =>
    rw [List.range_succ, List.map_append, List.prod_append]
    by_cases e : k = n
    · subst e
      have : ∀ j ∈ List.range k, (2 ^ k).testBit j = false := by
        intro j hj; rw [Nat.testBit_two_pow]; have := List.mem_range.mp hj; simp; omega
      rw [List.map_congr_left (fun j hj => by rw [this j hj])]
      simp [Nat.testBit_two_pow]
    · rw [ih (by omega)]
      simp [Nat.testBit_two_pow, e]

/-! ## Binary tables -/

/-- a binary table (index read from its low bits) -/
inductive BT (α : Type) where
  | em : BT α
  | lf : α → BT α
  | nd : BT α → BT α → BT α

def BT.get {α : Type} (d : α) : BT α → ℕ → α
  | .em, _ => d
  | .lf a, e => if e = 0 then a else d
  | .nd l r, e => if e % 2 = 0 then l.get d (e / 2) else r.get d (e / 2)

def BT.dp {α : Type} : BT α → ℕ
  | .em => 0
  | .lf _ => 0
  | .nd l r => max l.dp r.dp + 1

theorem BT.get_big {α : Type} (d : α) : ∀ (t : BT α) (e : ℕ), 2 ^ t.dp ≤ e → t.get d e = d
  | .em, _, _ => rfl
  | .lf _, e, h => by
    have : e ≠ 0 := by simp [BT.dp] at h; omega
    simp [BT.get, this]
  | .nd l r, e, h => by
    unfold BT.dp at h
    rw [pow_succ] at h
    have hl : 2 ^ l.dp ≤ e / 2 := by
      rw [Nat.le_div_iff_mul_le (by norm_num)]
      exact le_trans (Nat.mul_le_mul_right 2 (Nat.pow_le_pow_right (by norm_num) (le_max_left _ _))) h
    have hr : 2 ^ r.dp ≤ e / 2 := by
      rw [Nat.le_div_iff_mul_le (by norm_num)]
      exact le_trans (Nat.mul_le_mul_right 2 (Nat.pow_le_pow_right (by norm_num) (le_max_right _ _))) h
    unfold BT.get
    split_ifs
    · exact BT.get_big d l _ hl
    · exact BT.get_big d r _ hr

/-! ## Normalised products: cancel `q` against its inverse -/

def opp (q : ℕ) : ℕ := if q % 2 = 0 then q + 1 else q - 1

def ins (acc : List ℕ) (q : ℕ) : List ℕ := if opp q ∈ acc then acc.erase (opp q) else q :: acc

def nrm (l : List ℕ) : List ℕ := l.foldl ins []

theorem sv_opp (v : ℕ → K) (hv : ∀ e, v e ≠ 0) (q : ℕ) : sv v (opp q) * sv v q = 1 := by
  unfold sv opp
  by_cases h : q % 2 = 0
  · have h1 : (q + 1) % 2 ≠ 0 := by omega
    have h2 : (q + 1) / 2 = q / 2 := by omega
    rw [if_pos h, if_neg h1, h2, if_pos h]
    exact inv_mul_cancel₀ (hv _)
  · have h1 : (q - 1) % 2 = 0 := by omega
    have h2 : (q - 1) / 2 = q / 2 := by omega
    rw [if_neg h, if_pos h1, h2, if_neg h]
    exact mul_inv_cancel₀ (hv _)

theorem rp_ins (v : ℕ → K) (hv : ∀ e, v e ≠ 0) (acc : List ℕ) (q : ℕ) :
    rp v (ins acc q) = rp v acc * sv v q := by
  unfold ins rp
  split_ifs with h
  · rw [((List.perm_cons_erase h).map (sv v)).prod_eq, List.map_cons, List.prod_cons,
      mul_comm (sv v (opp q)), mul_assoc, sv_opp v hv q, mul_one]
  · rw [List.map_cons, List.prod_cons, mul_comm]

theorem rp_foldl (v : ℕ → K) (hv : ∀ e, v e ≠ 0) :
    ∀ (l acc : List ℕ), rp v (l.foldl ins acc) = rp v acc * rp v l := by
  intro l
  induction l with
  | nil => intro acc; simp [rp]
  | cons q l ih =>
    intro acc
    rw [List.foldl_cons, ih, rp_ins v hv]
    unfold rp
    rw [List.map_cons, List.prod_cons, mul_assoc]

theorem rp_nrm (v : ℕ → K) (hv : ∀ e, v e ≠ 0) (l : List ℕ) : rp v (nrm l) = rp v l := by
  unfold nrm; rw [rp_foldl v hv]; simp [rp]

/-! ## Certificate data and checks -/

/-- the data: relations `RS`, order `OD` (step index of each edge, gauge edges 0), masks `MK`, class roots `RT`,
class creation steps `CO`, fix steps `FO`, number of classes `n`. -/
structure Cert where
  RS : BT (List ℕ)
  OD : BT ℕ
  MK : BT ℕ
  RT : List ℕ
  CO : List ℕ
  FO : List ℕ
  PD : BT ℕ
  PR : BT ℕ
  SG : BT ℕ
  ST : BT (List ℕ)
  L : ℕ
  GA : List ℕ
  NE : List ℕ
  n : ℕ

def od (C : Cert) (e : ℕ) : ℕ := C.OD.get 1000000000 e
def mk (C : Cert) (e : ℕ) : ℕ := C.MK.get 0 e
/-- the product relation of a list of relation indices -/
def relL (C : Cert) (l : List ℕ) : List ℕ := nrm (l.flatMap fun a => C.RS.get [] a)


/-- `x` uses only classes fixed before step `i` -/
def trivB (C : Cert) (i x : ℕ) : Bool :=
  (List.range C.n).all fun k => !x.testBit k || decide (C.FO.getD k 1000000000 < i)

/-- xor of the masks of a list of signed edges, from `a` -/
def xm (C : Cert) (a : ℕ) (l : List ℕ) : ℕ := l.foldl (fun a q => a ^^^ mk C (q / 2)) a

def asg (C : Cert) (i q : ℕ) : Bool := decide (od C (q / 2) < i)

def unas (C : Cert) (i : ℕ) (r : List ℕ) : List ℕ := r.filter fun q => !asg C i q

/-- peel `[0, e, r₁, r₂, …]` -/
def peelOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  match unas C i (relL C (s.drop 2)) with
  | [q] => decide (q / 2 = s.getD 1 0) && decide (od C (s.getD 1 0) = i) &&
      trivB C i (xm C 0 ((relL C (s.drop 2)).filter (asg C i)) ^^^ mk C (s.getD 1 0))
  | _ => false

/-- fix `[2, k, r₁, r₂, …]` -/
def fixOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  decide (C.FO.getD (s.getD 1 0) 1000000000 = i) && decide (s.getD 1 0 < C.n) &&
    (unas C i (relL C (s.drop 2))).isEmpty &&
    trivB C i (xm C 0 (relL C (s.drop 2)) ^^^ 2 ^ (s.getD 1 0))

/-! ## Soundness -/

variable (C : Cert) (v : ℕ → K)

def cls (k : ℕ) : K := v (C.RT.getD k 0)

/-- the invariant before step `i` -/
abbrev Inv (i : ℕ) : Prop :=
  (∀ e, od C e < i → v e = cval (cls C v) C.n (mk C e)) ∧
  (∀ k < C.n, C.CO.getD k 1000000000 < i → cls C v k * cls C v k = 1) ∧
  (∀ k < C.n, C.FO.getD k 1000000000 < i → cls C v k = 1)

/-- masks only use classes created no later than the edge -/
abbrev WF : Prop := ∀ e k, (mk C e).testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 ≤ od C e

/-- the stored relations hold and all values are non-zero -/
abbrev RelOK : Prop := (∀ a, rp v (C.RS.get [] a) = 1) ∧ ∀ e, v e ≠ 0

theorem rp_relL (hrel : RelOK C v) (l : List ℕ) : rp v (relL C l) = 1 := by
  unfold relL
  rw [rp_nrm v hrel.2]
  induction l with
  | nil => simp [rp]
  | cons a l ih =>
    rw [List.flatMap_cons]
    unfold rp at ih ⊢
    rw [List.map_append, List.prod_append, ih, mul_one]
    exact hrel.1 a

theorem triv_cval {i x : ℕ} (hI : Inv C v i) (h : trivB C i x = true) : cval (cls C v) C.n x = 1 := by
  rw [← cval_zero (cls C v) C.n]
  apply cval_fix
  intro k hk hb
  rw [Nat.xor_zero] at hb
  have := List.all_eq_true.mp h k (List.mem_range.mpr hk)
  rw [hb] at this
  simp at this
  exact hI.2.2 k hk this

theorem cval_sq_of {i x : ℕ} (hI : Inv C v i) (hx : ∀ k, x.testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 < i) :
    cval (cls C v) C.n x * cval (cls C v) C.n x = 1 :=
  cval_sq _ _ _ fun k _ hb => hI.2.1 k (hx k hb).1 (hx k hb).2

theorem inv_eq_self {a : K} (h : a * a = 1) : a⁻¹ = a := inv_eq_of_mul_eq_one_right h

theorem sv_asg {i q : ℕ} (hI : Inv C v i) (hW : WF C) (hq : od C (q / 2) < i) :
    sv v q = cval (cls C v) C.n (mk C (q / 2)) := by
  have hv := hI.1 _ hq
  have hs := cval_sq_of C v hI (x := mk C (q / 2)) fun k hb => ⟨(hW _ k hb).1, lt_of_le_of_lt (hW _ k hb).2 hq⟩
  unfold sv; split_ifs
  · exact hv
  · rw [hv, inv_eq_self hs]

theorem prod_asg {i : ℕ} (hI : Inv C v i) (hW : WF C) : ∀ (l : List ℕ) (a : ℕ),
    (∀ q ∈ l, asg C i q = true) → (∀ k, a.testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 < i) →
    cval (cls C v) C.n a * (l.map (sv v)).prod = cval (cls C v) C.n (xm C a l) := by
  intro l
  induction l with
  | nil => intro a _ _; simp [xm]
  | cons q l ih =>
    intro a hl ha
    have hq : od C (q / 2) < i := by simpa [asg] using hl q (by simp)
    have hb : ∀ k, (a ^^^ mk C (q / 2)).testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 < i := by
      intro k h
      rw [Nat.testBit_xor] at h
      cases h1 : a.testBit k
      · rw [h1] at h; simp at h
        exact ⟨(hW _ k h).1, lt_of_le_of_lt (hW _ k h).2 hq⟩
      · exact ha k h1
    have := ih (a ^^^ mk C (q / 2)) (fun q' h' => hl q' (by simp [h'])) hb
    rw [List.map_cons, List.prod_cons, ← mul_assoc, sv_asg C v hI hW hq, ← cval_xor]
    · simpa [xm] using this
    · intro k hk h
      rcases h with h | h
      · exact hI.2.1 k hk (ha k h).2
      · exact hI.2.1 k hk (lt_of_le_of_lt (hW _ k h).2 hq)


/-- every set bit of `x` is a class `< n` created before step `i` -/
def bitsB (C : Cert) (i x : ℕ) : Bool :=
  (List.range C.n).all (fun k => !x.testBit k || decide (C.CO.getD k 1000000000 < i)) && decide (x < 2 ^ C.n)

theorem bits_of {i x : ℕ} (h : bitsB C i x = true) :
    ∀ k, x.testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 < i := by
  unfold bitsB at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range] at h
  intro k hk
  have hkn : k < C.n := by
    by_contra hc
    have : x < 2 ^ k := lt_of_lt_of_le h.2 (Nat.pow_le_pow_right (by norm_num) (by omega))
    rw [Nat.testBit_lt_two_pow this] at hk
    exact absurd hk (by simp)
  have := h.1 k hkn
  rw [hk] at this
  simp at this
  exact ⟨hkn, this⟩

/-- peel `[0, r₁, r₂, e]`, with the bit check of the new mask -/
def peelB (C : Cert) (i : ℕ) (s : List ℕ) : Bool := peelOK C i s && bitsB C i (mk C (s.getD 1 0))

theorem filter_not_asg_nil {i : ℕ} {r : List ℕ} (h : r.filter (fun q => !asg C i q) = []) :
    ∀ q ∈ r, asg C i q = true := by
  intro q hq
  by_contra hc
  have : q ∈ r.filter (fun q => !asg C i q) := List.mem_filter.mpr ⟨hq, by simpa using hc⟩
  rw [h] at this
  simp at this

theorem peel_sound {i : ℕ} (hrel : RelOK C v) (hW : WF C) (hI : Inv C v i) {s : List ℕ}
    (hok : peelB C i s = true) : v (s.getD 1 0) = cval (cls C v) C.n (mk C (s.getD 1 0)) := by
  unfold peelB at hok
  rw [Bool.and_eq_true] at hok
  obtain ⟨hp, hbits⟩ := hok
  unfold peelOK at hp
  split at hp
  next q hq =>
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hp
    obtain ⟨⟨he, _⟩, htr⟩ := hp
    have h1 := rp_relL C v hrel (s.drop 2)
    unfold rp at h1
    rw [prod_split (sv v) (asg C i)] at h1
    have hq' : (relL C (s.drop 2)).filter (fun q => !asg C i q) = [q] := hq
    rw [hq'] at h1
    simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one] at h1
    have hpa := prod_asg C v hI hW ((relL C (s.drop 2)).filter (asg C i)) 0
      (fun q hq => (List.mem_filter.mp hq).2) (by simp)
    rw [cval_zero, one_mul] at hpa
    rw [hpa] at h1
    set X := xm C 0 ((relL C (s.drop 2)).filter (asg C i))
    set e := s.getD 1 0
    have hX : cval (cls C v) C.n X = cval (cls C v) C.n (mk C e) := by
      apply cval_fix
      intro k hk hb
      have := List.all_eq_true.mp htr k (List.mem_range.mpr hk)
      rw [hb] at this
      simp at this
      exact hI.2.2 k hk this
    rw [hX] at h1
    have hsq := cval_sq_of C v hI (bits_of C hbits)
    have hsv : sv v q = cval (cls C v) C.n (mk C e) := by
      have := eq_inv_of_mul_eq_one_right h1
      rw [this, inv_eq_self hsq]
    unfold sv at hsv
    rw [he] at hsv
    split_ifs at hsv
    · exact hsv
    · rw [← inv_inv (v e), hsv, inv_eq_self hsq]
  next => simp at hp

theorem fix_sound {i : ℕ} (hrel : RelOK C v) (hW : WF C) (hI : Inv C v i) {s : List ℕ}
    (hok : fixOK C i s = true) : cls C v (s.getD 1 0) = 1 := by
  unfold fixOK at hok
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.isEmpty_iff] at hok
  obtain ⟨⟨⟨_, hk⟩, hnil⟩, htr⟩ := hok
  have hall := filter_not_asg_nil C hnil
  have h1 := rp_relL C v hrel (s.drop 2)
  have hpa := prod_asg C v hI hW (relL C (s.drop 2)) 0 hall (by simp)
  rw [cval_zero, one_mul] at hpa
  unfold rp at h1
  rw [h1] at hpa
  have hfx : cval (cls C v) C.n (2 ^ (s.getD 1 0)) = cval (cls C v) C.n (xm C 0 (relL C (s.drop 2))) := by
    apply cval_fix
    intro k hk' hb
    have := List.all_eq_true.mp htr k (List.mem_range.mpr hk')
    rw [Nat.xor_comm, hb] at this
    simp at this
    exact hI.2.2 k hk' this
  rw [← cval_single (cls C v) C.n _ hk, hfx]
  exact hpa.symm

/-! ## Components: pending edges `v e = pw (v root) σ`, resolved by one equation -/

def pd (C : Cert) (e : ℕ) : ℕ := C.PD.get 1000000000 e
def pr (C : Cert) (e : ℕ) : ℕ := C.PR.get 0 e
def sg (C : Cert) (e : ℕ) : ℕ := C.SG.get 0 e

/-- signed power -/
def pw (r : K) (σ : ℕ) : K := if σ % 2 = 0 then r else r⁻¹

/-- root `[4, root]` -/
def rootOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  decide (pd C (s.getD 1 0) = i) && decide (pr C (s.getD 1 0) = s.getD 1 0) && decide (sg C (s.getD 1 0) % 2 = 0)

/-- link `[3, m, p, r₁, …]`: only `m` and `p` (pending, same root) are unknown; `σ m` from `σ p` -/
def linkOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  let m := s.getD 1 0; let p := s.getD 2 0; let R := relL C (s.drop 3)
  decide (pd C m = i) && decide (pd C p < i) && decide (pr C m = pr C p) &&
    trivB C i (xm C 0 (R.filter (asg C i))) &&
    match unas C i R with
    | [a, b] => (decide (a / 2 = m) && decide (b / 2 = p) && decide ((sg C m + a + sg C p + b + 1) % 2 = 0)) ||
                (decide (a / 2 = p) && decide (b / 2 = m) && decide ((sg C m + b + sg C p + a + 1) % 2 = 0))
    | _ => false

/-- exponent count of a pending part: `(#r, #r⁻¹)` -/
def cnt (C : Cert) (l : List ℕ) : ℕ × ℕ :=
  l.foldl (fun c q => if (sg C (q / 2) + q) % 2 = 0 then (c.1 + 1, c.2) else (c.1, c.2 + 1)) (0, 0)

/-- equation `[1, root, mode, k, r₁, …]`: the unknown part lies in the component of `root`; mode 0: exponent
`±1`, the root gets the mask of the assigned part; mode 1: exponent `±2`, trivial assigned part, new class `k`. -/
def eqOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  let root := s.getD 1 0; let R := relL C (s.drop 4); let U := unas C i R
  let X := xm C 0 (R.filter (asg C i)); let c := cnt C U
  decide (pd C root < i) && decide (pr C root = root) && decide (sg C root % 2 = 0) &&
    U.all (fun q => decide (pd C (q / 2) < i) && decide (pr C (q / 2) = root)) &&
    (if s.getD 2 0 = 0 then
      (decide (c.1 = c.2 + 1) || decide (c.2 = c.1 + 1)) && bitsB C i X
    else
      (decide (c.1 = c.2 + 2) || decide (c.2 = c.1 + 2)) && trivB C i X && decide (s.getD 3 0 < C.n) &&
        decide (C.CO.getD (s.getD 3 0) 1000000000 = i) && decide (C.RT.getD (s.getD 3 0) 0 = root))

/-! ## Soundness of links and equations -/

theorem pw_inv (r : K) (x : ℕ) : (pw r x)⁻¹ = pw r (x + 1) := by
  unfold pw; by_cases h : x % 2 = 0
  · rw [if_pos h, if_neg (by omega)]
  · rw [if_neg h, if_pos (by omega), inv_inv]

theorem pw_mod (r : K) (x y : ℕ) (h : x % 2 = y % 2) : pw r x = pw r y := by
  unfold pw; rw [h]

/-- value of a signed pending edge -/
theorem sv_pend {r : K} {q : ℕ} (h : v (q / 2) = pw r (sg C (q / 2))) : sv v q = pw r (sg C (q / 2) + q) := by
  unfold sv
  by_cases hq : q % 2 = 0
  · rw [if_pos hq, h]; exact pw_mod r _ _ (by omega)
  · rw [if_neg hq, h, pw_inv]; exact pw_mod r _ _ (by omega)

abbrev PInv (i : ℕ) : Prop := ∀ e, pd C e < i → v e = pw (v (pr C e)) (sg C e)

/-- the assigned part of a relation is trivial once its mask is -/
theorem asg_part_one {i : ℕ} (hW : WF C) (hI : Inv C v i) {R : List ℕ} (htr : trivB C i (xm C 0 (R.filter (asg C i))) = true) :
    ((R.filter (asg C i)).map (sv v)).prod = 1 := by
  have hpa := prod_asg C v hI hW (R.filter (asg C i)) 0 (fun q hq => (List.mem_filter.mp hq).2) (by simp)
  rw [cval_zero, one_mul] at hpa
  rw [hpa]; exact triv_cval C v hI htr

theorem link_sound {i : ℕ} (hrel : RelOK C v) (hW : WF C) (hI : Inv C v i) (hP : PInv C v i)
    {s : List ℕ} (hok : linkOK C i s = true) :
    v (s.getD 1 0) = pw (v (pr C (s.getD 1 0))) (sg C (s.getD 1 0)) := by
  unfold linkOK at hok
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
  obtain ⟨⟨⟨⟨hm, hp⟩, hpr⟩, htr⟩, hmt⟩ := hok
  set m := s.getD 1 0; set p := s.getD 2 0; set R := relL C (s.drop 3)
  have h1 := rp_relL C v hrel (s.drop 3)
  unfold rp at h1
  rw [prod_split (sv v) (asg C i), asg_part_one C v hW hI htr, one_mul] at h1
  have hvp := hP p hp
  rw [← hpr] at hvp
  set r := v (pr C m)
  have key : ∀ a b : ℕ, a / 2 = m → b / 2 = p → (sg C m + a + sg C p + b + 1) % 2 = 0 →
      sv v a * sv v b = 1 → v m = pw r (sg C m) := by
    intro a b ha hb hpar hab
    have hsb : sv v b = pw r (sg C p + b) := by rw [← hb] at hvp ⊢; exact sv_pend C v hvp
    rw [hsb] at hab
    have hsa : sv v a = pw r (sg C p + b + 1) := by rw [← pw_inv]; exact eq_inv_of_mul_eq_one_left hab
    unfold sv at hsa; rw [ha] at hsa
    by_cases hq : a % 2 = 0
    · rw [if_pos hq] at hsa; rw [hsa]; exact pw_mod r _ _ (by omega)
    · rw [if_neg hq] at hsa; rw [← inv_inv (v m), hsa, pw_inv]; exact pw_mod r _ _ (by omega)
  have hU : (R.filter fun q => !asg C i q) = unas C i R := rfl
  rw [hU] at h1
  split at hmt
  next a b hab =>
    rw [hab] at h1
    simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one] at h1
    simp only [Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq] at hmt
    rcases hmt with ⟨⟨ha, hb⟩, hpar⟩ | ⟨⟨ha, hb⟩, hpar⟩
    · exact key a b ha hb hpar h1
    · exact key b a hb ha hpar (by rw [mul_comm]; exact h1)
  next => simp at hmt

theorem cnt_prod {r : K} (hr : r ≠ 0) : ∀ (l : List ℕ) (c : ℕ × ℕ),
    (∀ q ∈ l, sv v q = pw r (sg C (q / 2) + q)) →
    r ^ c.1 * r⁻¹ ^ c.2 * (l.map (sv v)).prod =
      r ^ (l.foldl (fun c q => if (sg C (q / 2) + q) % 2 = 0 then (c.1 + 1, c.2) else (c.1, c.2 + 1)) c).1 *
      r⁻¹ ^ (l.foldl (fun c q => if (sg C (q / 2) + q) % 2 = 0 then (c.1 + 1, c.2) else (c.1, c.2 + 1)) c).2 := by
  intro l
  induction l with
  | nil => intro c _; simp
  | cons q l ih =>
    intro c hl
    rw [List.foldl_cons, ← ih _ (fun q' h' => hl q' (by simp [h']))]
    rw [List.map_cons, List.prod_cons, hl q (by simp)]
    unfold pw
    split_ifs with h
    · simp only; ring
    · simp only; ring

theorem eq_sound {i : ℕ} (hrel : RelOK C v) (hW : WF C) (hI : Inv C v i) (hP : PInv C v i)
    (hv : ∀ e, v e ≠ 0) {s : List ℕ} (hok : eqOK C i s = true) :
    (s.getD 2 0 = 0 → v (s.getD 1 0) * v (s.getD 1 0) = 1 ∧
      v (s.getD 1 0) = cval (cls C v) C.n (xm C 0 ((relL C (s.drop 4)).filter (asg C i)))) ∧
    (s.getD 2 0 ≠ 0 → v (s.getD 1 0) * v (s.getD 1 0) = 1) := by
  unfold eqOK at hok
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hok
  obtain ⟨⟨⟨⟨hpd, hpr⟩, hsg⟩, hU⟩, hmode⟩ := hok
  set root := s.getD 1 0; set R := relL C (s.drop 4)
  set X := xm C 0 (R.filter (asg C i))
  set r := v root
  have hr : r ≠ 0 := hv root
  have h1 := rp_relL C v hrel (s.drop 4)
  unfold rp at h1
  rw [prod_split (sv v) (asg C i)] at h1
  have hpa := prod_asg C v hI hW (R.filter (asg C i)) 0 (fun q hq => (List.mem_filter.mp hq).2) (by simp)
  rw [cval_zero, one_mul] at hpa
  rw [hpa] at h1
  have hsvU : ∀ q ∈ unas C i R, sv v q = pw r (sg C (q / 2) + q) := by
    intro q hq
    obtain ⟨hq1, hq2⟩ := hU q hq
    have := hP _ hq1
    rw [hq2] at this
    exact sv_pend C v this
  have hc := cnt_prod C v hr (unas C i R) (0, 0) hsvU
  simp only [pow_zero, one_mul] at hc
  have hU' : (R.filter fun q => !asg C i q) = unas C i R := rfl
  rw [hU', hc] at h1
  set c := cnt C (unas C i R) with hcdef
  have hcc : c = (unas C i R).foldl (fun c q => if (sg C (q / 2) + q) % 2 = 0 then (c.1 + 1, c.2) else (c.1, c.2 + 1)) (0, 0) := rfl
  rw [← hcc] at h1
  -- h1 : cval X * (r ^ c.1 * r⁻¹ ^ c.2) = 1
  have hA : ∀ d x y : ℕ, x = y + d → r ^ x * r⁻¹ ^ y = r ^ d := by
    intro d x y h; subst h
    rw [pow_add, mul_comm (r ^ y) (r ^ d), mul_assoc, ← mul_pow, mul_inv_cancel₀ hr, one_pow, mul_one]
  have hB : ∀ d x y : ℕ, y = x + d → r ^ x * r⁻¹ ^ y = r⁻¹ ^ d := by
    intro d x y h; subst h
    rw [pow_add, ← mul_assoc, ← mul_pow, mul_inv_cancel₀ hr, one_pow, one_mul]
  split_ifs at hmode with hm0
  · simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at hmode
    obtain ⟨hc12, hbits⟩ := hmode
    have hsq := cval_sq_of C v hI (bits_of C hbits)
    have hrX : r = cval (cls C v) C.n X := by
      rcases hc12 with h | h
      · rw [hA 1 _ _ h, pow_one] at h1
        have := eq_inv_of_mul_eq_one_right h1
        rw [this, inv_eq_self hsq]
      · rw [hB 1 _ _ h, pow_one] at h1
        have := eq_inv_of_mul_eq_one_right h1
        rw [← inv_inv r, this, inv_inv]
    refine ⟨fun _ => ⟨by rw [hrX]; exact hsq, hrX⟩, fun h => absurd hm0 h⟩
  · simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at hmode
    obtain ⟨⟨⟨⟨hc12, htr⟩, _⟩, _⟩, _⟩ := hmode
    rw [triv_cval C v hI htr, one_mul] at h1
    refine ⟨fun h => absurd h hm0, fun _ => ?_⟩
    rcases hc12 with h | h
    · rw [hA 2 _ _ h] at h1; rw [← pow_two]; exact h1
    · rw [hB 2 _ _ h, inv_pow] at h1
      rw [← pow_two]; exact inv_eq_one.mp h1

/-! ## Steps, global checks and the closure theorem -/

theorem pw_sq {r : K} (h : r * r = 1) (σ : ℕ) : pw r σ = r := by
  unfold pw; split_ifs
  · rfl
  · exact inv_eq_self h


theorem eqOK_class {i : ℕ} {s : List ℕ} (h : eqOK C i s = true) (hm : s.getD 2 0 ≠ 0) :
    s.getD 3 0 < C.n ∧ C.RT.getD (s.getD 3 0) 0 = s.getD 1 0 := by
  unfold eqOK at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at h
  obtain ⟨_, hmode⟩ := h
  rw [if_neg hm] at hmode
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hmode
  exact ⟨hmode.1.1.2, hmode.2⟩

/-- step `i` (from 1) -/
def stp (C : Cert) (i : ℕ) : List ℕ := C.ST.get [] i

def eqX (C : Cert) (i : ℕ) (s : List ℕ) : ℕ := xm C 0 ((relL C (s.drop 4)).filter (asg C i))

/-- edge `e` is a gauge edge or is assigned by its step -/
def edgeJ (C : Cert) (e : ℕ) : Bool :=
  if od C e = 0 then C.GA.contains e && decide (mk C e = 0)
  else if od C e ≤ C.L then
    (decide ((stp C (od C e)).getD 0 9 = 0) && decide ((stp C (od C e)).getD 1 0 = e) &&
      peelB C (od C e) (stp C (od C e))) ||
    (decide ((stp C (od C e)).getD 0 9 = 1) && eqOK C (od C e) (stp C (od C e)) &&
      decide (pr C e = (stp C (od C e)).getD 1 0) && decide (pd C e < od C e) &&
      ((decide ((stp C (od C e)).getD 2 0 = 0) && decide (mk C e = eqX C (od C e) (stp C (od C e)))) ||
       (decide ((stp C (od C e)).getD 2 0 ≠ 0) && decide (mk C e = 2 ^ (stp C (od C e)).getD 3 0))))
  else true

/-- pending edge `e` is a root or linked by its step -/
def pendJ (C : Cert) (e : ℕ) : Bool :=
  if pd C e = 0 then false
  else if pd C e ≤ C.L then
    decide ((stp C (pd C e)).getD 1 0 = e) &&
      ((decide ((stp C (pd C e)).getD 0 9 = 4) && rootOK C (pd C e) (stp C (pd C e))) ||
       (decide ((stp C (pd C e)).getD 0 9 = 3) && linkOK C (pd C e) (stp C (pd C e))))
  else true

def coJ (C : Cert) (k : ℕ) : Bool :=
  if C.CO.getD k 1000000000 = 0 then false
  else if C.CO.getD k 1000000000 ≤ C.L then
    decide ((stp C (C.CO.getD k 1000000000)).getD 0 9 = 1) &&
      decide ((stp C (C.CO.getD k 1000000000)).getD 2 0 ≠ 0) &&
      decide ((stp C (C.CO.getD k 1000000000)).getD 3 0 = k) &&
      eqOK C (C.CO.getD k 1000000000) (stp C (C.CO.getD k 1000000000))
  else true

def foJ (C : Cert) (k : ℕ) : Bool :=
  if C.FO.getD k 1000000000 = 0 then false
  else if C.FO.getD k 1000000000 ≤ C.L then
    decide ((stp C (C.FO.getD k 1000000000)).getD 0 9 = 2) &&
      decide ((stp C (C.FO.getD k 1000000000)).getD 1 0 = k) &&
      fixOK C (C.FO.getD k 1000000000) (stp C (C.FO.getD k 1000000000))
  else true

def wfB (C : Cert) (e : ℕ) : Bool :=
  (List.range C.n).all (fun k => !(mk C e).testBit k || decide (C.CO.getD k 1000000000 ≤ od C e)) &&
    decide (mk C e < 2 ^ C.n)

/-- the whole check -/
def check (C : Cert) : Bool :=
  decide (C.L < 1000000000) &&
  (List.range (2 ^ (max C.OD.dp (max C.PD.dp C.MK.dp)))).all (fun e => edgeJ C e && pendJ C e && wfB C e) &&
  (List.range C.n).all (fun k => coJ C k && foJ C k) &&
  C.NE.all (fun e => decide (od C e ≤ C.L) && trivB C (C.L + 1) (mk C e))

theorem wf_of (h : ∀ e, wfB C e = true) : WF C := by
  intro e k hk
  have h1 := h e
  unfold wfB at h1
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range] at h1
  have hkn : k < C.n := by
    by_contra hc
    have : mk C e < 2 ^ k := lt_of_lt_of_le h1.2 (Nat.pow_le_pow_right (by norm_num) (by omega))
    rw [Nat.testBit_lt_two_pow this] at hk
    exact absurd hk (by simp)
  have := h1.1 k hkn
  rw [hk] at this
  simp at this
  exact ⟨hkn, this⟩

theorem check_all (hc : check C = true) :
    C.L < 1000000000 ∧ (∀ e, edgeJ C e = true ∧ pendJ C e = true ∧ wfB C e = true) ∧
    (∀ k < C.n, coJ C k = true ∧ foJ C k = true) ∧
    (∀ e ∈ C.NE, od C e ≤ C.L ∧ trivB C (C.L + 1) (mk C e) = true) := by
  unfold check at hc
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range] at hc
  obtain ⟨⟨⟨hL, hE⟩, hK⟩, hN⟩ := hc
  refine ⟨hL, ?_, hK, hN⟩
  intro e
  by_cases he : e < 2 ^ (max C.OD.dp (max C.PD.dp C.MK.dp))
  · exact ⟨(hE e he).1.1, (hE e he).1.2, (hE e he).2⟩
  · have hle : ∀ d, d ≤ max C.OD.dp (max C.PD.dp C.MK.dp) → 2 ^ d ≤ e := fun d hd =>
      le_trans (Nat.pow_le_pow_right (by norm_num) hd) (by omega)
    have h1 : od C e = 1000000000 := BT.get_big _ _ _ (hle _ (le_max_left _ _))
    have h2 : pd C e = 1000000000 :=
      BT.get_big _ _ _ (hle _ (le_trans (le_max_left _ _) (le_max_right _ _)))
    have h3 : mk C e = 0 := BT.get_big _ _ _ (hle _ (le_trans (le_max_right _ _) (le_max_right _ _)))
    refine ⟨?_, ?_, ?_⟩
    · unfold edgeJ; rw [h1, if_neg (by norm_num), if_neg (by omega)]
    · unfold pendJ; rw [h2, if_neg (by norm_num), if_neg (by omega)]
    · unfold wfB; rw [h3]; simp

theorem inv_base (hga : ∀ e ∈ C.GA, v e = 1) (hJ : ∀ e, edgeJ C e = true) (hPJ : ∀ e, pendJ C e = true)
    (hK : ∀ k < C.n, coJ C k = true ∧ foJ C k = true) : Inv C v 1 ∧ PInv C v 1 := by
  refine ⟨⟨?_, ?_, ?_⟩, ?_⟩
  · intro e he
    have h0 : od C e = 0 := by omega
    have := hJ e
    unfold edgeJ at this
    rw [if_pos h0] at this
    simp only [Bool.and_eq_true, decide_eq_true_eq, List.contains_iff_mem] at this
    rw [hga e this.1, this.2, cval_zero]
  · intro k hk hc
    have := (hK k hk).1
    unfold coJ at this
    rw [if_pos (by omega)] at this
    exact absurd this (by simp)
  · intro k hk hc
    have := (hK k hk).2
    unfold foJ at this
    rw [if_pos (by omega)] at this
    exact absurd this (by simp)
  · intro e he
    have := hPJ e
    unfold pendJ at this
    rw [if_pos (by omega)] at this
    exact absurd this (by simp)

theorem inv_step (hrel : RelOK C v) (hv : ∀ e, v e ≠ 0) (hW : WF C)
    (hJ : ∀ e, edgeJ C e = true) (hPJ : ∀ e, pendJ C e = true) (hK : ∀ k < C.n, coJ C k = true ∧ foJ C k = true)
    {i : ℕ} (hi1 : 1 ≤ i) (hiL : i ≤ C.L) (hI : Inv C v i) (hP : PInv C v i) :
    Inv C v (i + 1) ∧ PInv C v (i + 1) := by
  refine ⟨⟨?_, ?_, ?_⟩, ?_⟩
  · intro e he
    rcases Nat.lt_or_eq_of_le (Nat.lt_succ_iff.mp he) with h | h
    · exact hI.1 e h
    have hj := hJ e
    unfold edgeJ at hj
    rw [h, if_neg (by omega), if_pos hiL] at hj
    simp only [Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq] at hj
    rcases hj with ⟨⟨_, he1⟩, hpe⟩ | ⟨⟨⟨⟨_, heq⟩, hpre⟩, hpde⟩, hmk⟩
    · have := peel_sound C v hrel hW hI hpe
      rw [he1] at this
      exact this
    · have hes := eq_sound C v hrel hW hI hP hv heq
      have hve := hP e hpde
      rw [hpre] at hve
      rcases hmk with ⟨hm, hx⟩ | ⟨hm, hx⟩
      · obtain ⟨hsq, hrx⟩ := hes.1 hm
        rw [hve, pw_sq hsq, hrx, hx]
        rfl
      · have hsq := hes.2 hm
        obtain ⟨hkn, hrt⟩ := eqOK_class C heq hm
        rw [hve, pw_sq hsq, hx, cval_single _ _ _ hkn]
        unfold cls
        rw [hrt]
  · intro k hk hc
    rcases Nat.lt_or_eq_of_le (Nat.lt_succ_iff.mp hc) with h | h
    · exact hI.2.1 k hk h
    have hj := (hK k hk).1
    unfold coJ at hj
    rw [h, if_neg (by omega), if_pos hiL] at hj
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hj
    obtain ⟨⟨⟨_, hm⟩, hk3⟩, heq⟩ := hj
    have hsq := (eq_sound C v hrel hW hI hP hv heq).2 hm
    obtain ⟨_, hrt⟩ := eqOK_class C heq hm
    unfold cls
    rw [← hk3, hrt]
    exact hsq
  · intro k hk hc
    rcases Nat.lt_or_eq_of_le (Nat.lt_succ_iff.mp hc) with h | h
    · exact hI.2.2 k hk h
    have hj := (hK k hk).2
    unfold foJ at hj
    rw [h, if_neg (by omega), if_pos hiL] at hj
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hj
    obtain ⟨⟨_, hk1⟩, hfx⟩ := hj
    have := fix_sound C v hrel hW hI hfx
    rw [hk1] at this
    exact this
  · intro e he
    rcases Nat.lt_or_eq_of_le (Nat.lt_succ_iff.mp he) with h | h
    · exact hP e h
    have hj := hPJ e
    unfold pendJ at hj
    rw [h, if_neg (by omega), if_pos hiL] at hj
    simp only [Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq] at hj
    obtain ⟨he1, ⟨_, hro⟩ | ⟨_, hl⟩⟩ := hj
    · unfold rootOK at hro
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hro
      rw [he1] at hro
      rw [hro.1.2]
      unfold pw
      rw [if_pos hro.2]
    · have := link_sound C v hrel hW hI hP hl
      rw [he1] at this
      exact this

theorem inv_all (hrel : RelOK C v) (hv : ∀ e, v e ≠ 0) (hga : ∀ e ∈ C.GA, v e = 1)
    (hc : check C = true) : ∀ j ≤ C.L, Inv C v (j + 1) ∧ PInv C v (j + 1) := by
  obtain ⟨_, hE, hK, _⟩ := check_all C hc
  have hW := wf_of C (fun e => (hE e).2.2)
  intro j
  induction j with
  | zero => intro _; exact inv_base C v hga (fun e => (hE e).1) (fun e => (hE e).2.1) hK
  | succ j ih =>
    intro hj
    obtain ⟨hI, hP⟩ := ih (by omega)
    exact inv_step C v hrel hv hW (fun e => (hE e).1) (fun e => (hE e).2.1) hK (by omega) hj hI hP

/-- **Closure theorem.** A checked certificate forces every needed edge to be `1`. -/
theorem closure_sound (hc : check C = true) (hrel : ∀ a, rp v (C.RS.get [] a) = 1) (hv : ∀ e, v e ≠ 0)
    (hga : ∀ e ∈ C.GA, v e = 1) : ∀ e ∈ C.NE, v e = 1 := by
  intro e he
  obtain ⟨_, _, _, hN⟩ := check_all C hc
  obtain ⟨hod, htr⟩ := hN e he
  have hI := (inv_all C v (And.intro hrel hv) hv hga hc C.L le_rfl).1
  rw [hI.1 e (by omega)]
  exact triv_cval C v hI htr

end RankNine.T2
