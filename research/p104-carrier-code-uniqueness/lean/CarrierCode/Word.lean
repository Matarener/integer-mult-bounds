import Mathlib

/-!
# Frame decomposition of a P104 local word (Lemma 1 and Corollary 2 of PROOF.md)

A word acts on public roles `P` and owned roles `O`.  Every role sits in a frame, a subspace of `F₂⁹`, and carries a
row; we keep only the live coordinates of rows (functions `L → R`), which is legitimate because every operation is
linear.  Public roles only move up, operations act only between roles in the same frame, and `COPY` only targets
owned roles.

The decomposition splits a public row into a *lives-in-frame* part `lp`, which only grows by ADDs between public
roles, and an *owned-delivered* part `od`, which collects everything received from owned roles.  We prove:

* `row = lp + od` on public roles, and `lp r m ≠ 0 → port m ∈ frame r` (Lemma 1);
* `od r` lies in the span of the owned rows delivered so far;
* at a partner whose final row is `e_ℓ` and whose final frame is `q_ℓ^⊥`, the owned part is `1` at `ℓ` and `0` at
  every port conflicting with `ℓ` (Corollary 2).
-/

namespace CarrierCode

/-- The space `F₂⁹` of port vectors. -/
abbrev V9 := Fin 9 → ZMod 2

/-- The frames: subspaces of `F₂⁹`. -/
abbrev Frame := Submodule (ZMod 2) V9

/-- Port vectors `q_i, q_j` conflict when their dot product is one. -/
def Conflict (x y : V9) : Prop := x ⬝ᵥ y = 1

/-- The hyperplane `q^⊥`. -/
def perp (q : V9) : Frame where
  carrier := {x | x ⬝ᵥ q = 0}
  add_mem' {a b} ha hb := by simp_all [add_dotProduct]
  zero_mem' := by simp
  smul_mem' c x hx := by simp_all [smul_dotProduct]

variable {R : Type*} [CommRing R] {L P O : Type*} [DecidableEq P] [DecidableEq O]

/-- Events of a word (live projections of the checker's operations). -/
inductive Event (R P O : Type*)
  | moveP (r : P) (F : Frame)
  | moveO (o : O) (F : Frame)
  | init (o : O) (F : Frame)
  | clear (o : O)
  | scaleP (r : P) (c : R)
  | scaleO (o : O) (c : R)
  | addPP (r s : P) (c : R)
  | addOP (r : P) (o : O) (c : R)
  | addPO (o : O) (s : P) (c : R)
  | addOO (o o' : O) (c : R)
  | copyPO (o : O) (s : P) (c : R)
  | copyOO (o o' : O) (c : R)

/-- State: frames, the decomposed public rows, the owned rows and the list of delivered owned rows. -/
structure State (R L P O : Type*) where
  fP : P → Frame
  fO : O → Frame
  lp : P → L → R
  od : P → L → R
  ow : O → L → R
  delivered : List (L → R)

namespace State

/-- The actual public row. -/
def row (S : State R L P O) (r : P) : L → R := S.lp r + S.od r

/-- Legality of an event in a state (frame rules of the checker). -/
def Legal (S : State R L P O) : Event R P O → Prop
  | .moveP r F => S.fP r ≤ F
  | .moveO o F => F ≤ S.fO o
  | .init _ _ => True
  | .clear _ => True
  | .scaleP _ _ => True
  | .scaleO _ _ => True
  | .addPP r s _ => S.fP r = S.fP s
  | .addOP r o _ => S.fP r = S.fO o
  | .addPO o s _ => S.fO o = S.fP s
  | .addOO o o' _ => S.fO o = S.fO o'
  | .copyPO o s _ => S.fO o = S.fP s
  | .copyOO o o' _ => S.fO o = S.fO o'

/-- One step of the decomposed semantics. -/
def step (S : State R L P O) : Event R P O → State R L P O
  | .moveP r F => { S with fP := Function.update S.fP r F }
  | .moveO o F => { S with fO := Function.update S.fO o F }
  | .init o F => { S with fO := Function.update S.fO o F, ow := Function.update S.ow o 0 }
  | .clear o => { S with ow := Function.update S.ow o 0 }
  | .scaleP r c => { S with lp := Function.update S.lp r (c • S.lp r), od := Function.update S.od r (c • S.od r) }
  | .scaleO o c => { S with ow := Function.update S.ow o (c • S.ow o) }
  | .addPP r s c =>
      { S with lp := Function.update S.lp r (S.lp r + c • S.lp s),
               od := Function.update S.od r (S.od r + c • S.od s) }
  | .addOP r o c =>
      { S with od := Function.update S.od r (S.od r + c • S.ow o), delivered := S.ow o :: S.delivered }
  | .addPO o s c => { S with ow := Function.update S.ow o (S.ow o + c • S.row s) }
  | .addOO o o' c => { S with ow := Function.update S.ow o (S.ow o + c • S.ow o') }
  | .copyPO o s c => { S with ow := Function.update S.ow o (c • S.row s) }
  | .copyOO o o' c => { S with ow := Function.update S.ow o (c • S.ow o') }

/-- Run a list of events. -/
def run (S : State R L P O) : List (Event R P O) → State R L P O
  | [] => S
  | e :: es => (S.step e).run es

/-- Every event of the list is legal when it is applied. -/
def LegalRun (S : State R L P O) : List (Event R P O) → Prop
  | [] => True
  | e :: es => S.Legal e ∧ (S.step e).LegalRun es

/-- The real row semantics (no decomposition), to check that `row = lp + od` is the checker's row. -/
def stepRow (fP : P → Frame) (fO : O → Frame) (pr : P → L → R) (ow : O → L → R) :
    Event R P O → (P → Frame) × (O → Frame) × (P → L → R) × (O → L → R)
  | .moveP r F => (Function.update fP r F, fO, pr, ow)
  | .moveO o F => (fP, Function.update fO o F, pr, ow)
  | .init o F => (fP, Function.update fO o F, pr, Function.update ow o 0)
  | .clear o => (fP, fO, pr, Function.update ow o 0)
  | .scaleP r c => (fP, fO, Function.update pr r (c • pr r), ow)
  | .scaleO o c => (fP, fO, pr, Function.update ow o (c • ow o))
  | .addPP r s c => (fP, fO, Function.update pr r (pr r + c • pr s), ow)
  | .addOP r o c => (fP, fO, Function.update pr r (pr r + c • ow o), ow)
  | .addPO o s c => (fP, fO, pr, Function.update ow o (ow o + c • pr s))
  | .addOO o o' c => (fP, fO, pr, Function.update ow o (ow o + c • ow o'))
  | .copyPO o s c => (fP, fO, pr, Function.update ow o (c • pr s))
  | .copyOO o o' c => (fP, fO, pr, Function.update ow o (c • ow o'))

/-- The decomposed step projects to the real step. -/
theorem step_row (S : State R L P O) (e : Event R P O) :
    stepRow S.fP S.fO S.row S.ow e = ((S.step e).fP, (S.step e).fO, (S.step e).row, (S.step e).ow) := by
  cases e with
  | moveP r F => rfl
  | moveO o F => rfl
  | init o F => rfl
  | clear o => rfl
  | scaleP r c =>
      simp only [stepRow, step, Prod.mk.injEq, true_and, and_true]
      funext x; by_cases h : x = r
      · subst h; simp [row, smul_add]
      · simp [row, Function.update_of_ne h]
  | scaleO o c => rfl
  | addPP r s c =>
      simp only [stepRow, step, Prod.mk.injEq, true_and, and_true]
      funext x; by_cases h : x = r
      · subst h; simp only [row, Function.update_self]; module
      · simp [row, Function.update_of_ne h]
  | addOP r o c =>
      simp only [stepRow, step, Prod.mk.injEq, true_and, and_true]
      funext x; by_cases h : x = r
      · subst h; simp only [row, Function.update_self]; abel
      · simp [row, Function.update_of_ne h]
  | addPO o s c => rfl
  | addOO o o' c => rfl
  | copyPO o s c => rfl
  | copyOO o o' c => rfl

variable (port : L → V9)

/-- Lemma 1 invariant: the lives-in-frame part sits on ports of the current frame; owned parts lie in the span of
the delivered owned rows. -/
def Inv (S : State R L P O) : Prop :=
  (∀ r m, S.lp r m ≠ 0 → port m ∈ S.fP r) ∧ ∀ r, S.od r ∈ Submodule.span R {v | v ∈ S.delivered}

theorem inv_step (S : State R L P O) (e : Event R P O) (h : Inv port S) (hl : S.Legal e) :
    Inv port (S.step e) := by
  obtain ⟨h1, h2⟩ := h
  have mono : ∀ (S' : State R L P O), S.delivered ⊆ S'.delivered →
      Submodule.span R {v | v ∈ S.delivered} ≤ Submodule.span R {v | v ∈ S'.delivered} :=
    fun S' hs => Submodule.span_mono (fun v hv => hs hv)
  cases e with
  | moveP r F =>
      refine ⟨fun x m hm => ?_, h2⟩
      by_cases hx : x = r
      · subst hx; simp only [step, Function.update_self]; exact hl (h1 x m hm)
      · simpa [step, Function.update_of_ne hx] using h1 x m hm
  | moveO o F => exact ⟨h1, h2⟩
  | init o F => exact ⟨h1, h2⟩
  | clear o => exact ⟨h1, h2⟩
  | scaleP r c =>
      refine ⟨fun x m hm => ?_, fun x => ?_⟩
      · by_cases hx : x = r
        · subst hx
          simp only [step, Function.update_self, Pi.smul_apply, smul_eq_mul] at hm ⊢
          exact h1 x m (right_ne_zero_of_mul hm)
        · simpa [step, Function.update_of_ne hx] using h1 x m (by simpa [step, Function.update_of_ne hx] using hm)
      · by_cases hx : x = r
        · subst hx; simp only [step, Function.update_self]; exact Submodule.smul_mem _ c (h2 x)
        · simpa [step, Function.update_of_ne hx] using h2 x
  | scaleO o c => exact ⟨h1, h2⟩
  | addPP r s c =>
      refine ⟨fun x m hm => ?_, fun x => ?_⟩
      · by_cases hx : x = r
        · subst hx
          simp only [step, Function.update_self, Pi.add_apply, Pi.smul_apply, smul_eq_mul] at hm ⊢
          by_cases ha : S.lp x m = 0
          · rw [ha, zero_add] at hm
            have := h1 s m (right_ne_zero_of_mul hm)
            rwa [show S.fP x = S.fP s from hl]
          · exact h1 x m ha
        · simpa [step, Function.update_of_ne hx] using h1 x m (by simpa [step, Function.update_of_ne hx] using hm)
      · by_cases hx : x = r
        · subst hx; simp only [step, Function.update_self]
          exact Submodule.add_mem _ (h2 x) (Submodule.smul_mem _ c (h2 s))
        · simpa [step, Function.update_of_ne hx] using h2 x
  | addOP r o c =>
      refine ⟨h1, fun x => ?_⟩
      have hsub : Submodule.span R {v | v ∈ S.delivered} ≤
          Submodule.span R {v | v ∈ (S.step (.addOP r o c)).delivered} :=
        mono _ (fun v hv => List.mem_cons_of_mem _ hv)
      have hnew : S.ow o ∈ Submodule.span R {v | v ∈ (S.step (.addOP r o c)).delivered} :=
        Submodule.subset_span (by simp [step])
      by_cases hx : x = r
      · subst hx; simp only [step, Function.update_self]
        exact Submodule.add_mem _ (hsub (h2 x)) (Submodule.smul_mem _ c hnew)
      · simp only [step, Function.update_of_ne hx]; exact hsub (h2 x)
  | addPO o s c => exact ⟨h1, h2⟩
  | addOO o o' c => exact ⟨h1, h2⟩
  | copyPO o s c => exact ⟨h1, h2⟩
  | copyOO o o' c => exact ⟨h1, h2⟩

omit [DecidableEq O] in
/-- The initial state satisfies the invariant: live `ℓ` holds `e_ℓ` in a frame containing its port, every other
public row is empty, and nothing has been delivered. -/
theorem inv_init [DecidableEq L] (fP : P → Frame) (fO : O → Frame) (ow : O → L → R) (live : L → P)
    (hlive : ∀ ℓ, port ℓ ∈ fP (live ℓ)) :
    Inv port (⟨fP, fO, fun r m => if live m = r then 1 else 0, fun _ => 0, ow, []⟩ : State R L P O) := by
  refine ⟨fun r m hm => ?_, fun r => Submodule.zero_mem _⟩
  by_cases h : live m = r
  · subst h; exact hlive m
  · simp [h] at hm

/-- Lemma 1 along a legal run. -/
theorem inv_run (S : State R L P O) (es : List (Event R P O)) (h : Inv port S) (hl : S.LegalRun es) :
    Inv port (S.run es) := by
  induction es generalizing S with
  | nil => exact h
  | cons e es ih => exact ih _ (inv_step port S e h hl.1) hl.2

/-- Corollary 2.  At the end of a legal run from an invariant state, let partner `p` of live `ℓ` sit in the frame
`q_ℓ^⊥` with row `e_ℓ`, where `q_ℓ` has odd weight (`q_ℓ ⬝ᵥ q_ℓ = 1`) and `port = q`.  Then its owned-delivered part
`w` lies in the span of the delivered owned rows, `w ℓ = 1`, and `w m = 0` for every `m ≠ ℓ` conflicting with `ℓ`. -/
theorem decoding_vector [DecidableEq L] (S : State R L P O) (es : List (Event R P O)) (h : Inv port S)
    (hl : S.LegalRun es) (ℓ : L) (p : P) (hodd : port ℓ ⬝ᵥ port ℓ = 1)
    (hframe : (S.run es).fP p = perp (port ℓ)) (hrow : (S.run es).row p = Pi.single ℓ 1) :
    (S.run es).od p ∈ Submodule.span R {v | v ∈ (S.run es).delivered} ∧
      (S.run es).od p ℓ = 1 ∧ ∀ m, m ≠ ℓ → Conflict (port m) (port ℓ) → (S.run es).od p m = 0 := by
  obtain ⟨h1, h2⟩ := inv_run port S es h hl
  set T := S.run es
  have hlp : ∀ m, Conflict (port m) (port ℓ) → T.lp p m = 0 := by
    intro m hm
    by_contra hne
    have := h1 p m hne
    rw [hframe] at this
    change port m ⬝ᵥ port ℓ = 0 at this
    rw [show port m ⬝ᵥ port ℓ = 1 from hm] at this
    exact one_ne_zero this
  have hrm : ∀ m, T.od p m = (Pi.single ℓ (1 : R) : L → R) m - T.lp p m := by
    intro m; rw [← hrow]; simp [row]
  refine ⟨h2 p, ?_, fun m hm hc => ?_⟩
  · rw [hrm, hlp ℓ hodd]; simp
  · rw [hrm, hlp m hc]; simp [hm]

section Map

variable {S' : Type*} [CommRing S'] (f : R →+* S')

/-- Map the scalars of an event along a ring hom (e.g. dyadic rationals to `ZMod 3`). -/
def _root_.CarrierCode.Event.map : Event R P O → Event S' P O
  | .moveP r F => .moveP r F
  | .moveO o F => .moveO o F
  | .init o F => .init o F
  | .clear o => .clear o
  | .scaleP r c => .scaleP r (f c)
  | .scaleO o c => .scaleO o (f c)
  | .addPP r s c => .addPP r s (f c)
  | .addOP r o c => .addOP r o (f c)
  | .addPO o s c => .addPO o s (f c)
  | .addOO o o' c => .addOO o o' (f c)
  | .copyPO o s c => .copyPO o s (f c)
  | .copyOO o o' c => .copyOO o o' (f c)

/-- Map every row of a state along a ring hom. -/
def map (S : State R L P O) : State S' L P O :=
  ⟨S.fP, S.fO, fun r => f ∘ S.lp r, fun r => f ∘ S.od r, fun o => f ∘ S.ow o, S.delivered.map (f ∘ ·)⟩

omit [DecidableEq P] [DecidableEq O] in
theorem comp_update {X : Type*} [DecidableEq X] (g : X → L → R) (x : X) (v : L → R) :
    (fun y => (f : R → S') ∘ Function.update g x v y) = Function.update (fun y => (f : R → S') ∘ g y) x (f ∘ v) := by
  funext y; by_cases h : y = x
  · subst h; simp
  · simp [Function.update_of_ne h]

theorem step_map (S : State R L P O) (e : Event R P O) : (S.step e).map f = (S.map f).step (e.map f) := by
  cases e <;> simp only [step, map, Event.map, row, comp_update] <;> congr 1 <;>
    (try (congr 1; funext m; simp; try ring))

omit [DecidableEq P] [DecidableEq O] in
theorem legal_map (S : State R L P O) (e : Event R P O) : (S.map f).Legal (e.map f) ↔ S.Legal e := by
  cases e <;> rfl

theorem run_map (S : State R L P O) (es : List (Event R P O)) :
    (S.run es).map f = (S.map f).run (es.map (Event.map f)) := by
  induction es generalizing S with
  | nil => rfl
  | cons e es ih => simp only [run, List.map_cons]; rw [ih, step_map]

theorem legalRun_map (S : State R L P O) (es : List (Event R P O)) :
    (S.map f).LegalRun (es.map (Event.map f)) ↔ S.LegalRun es := by
  induction es generalizing S with
  | nil => rfl
  | cons e es ih => simp only [LegalRun, List.map_cons, legal_map, ← step_map, ih]

omit [DecidableEq P] [DecidableEq O] in
theorem row_map (S : State R L P O) (r : P) : (S.map f).row r = f ∘ S.row r := by
  funext m; simp [row, map]

end Map

end State

end CarrierCode
