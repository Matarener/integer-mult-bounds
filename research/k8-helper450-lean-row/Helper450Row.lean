/-
Copyright (c) 2026 Sagar Thakrar. Released under the Apache 2.0 license.
Prepared with substantial OpenAI Codex assistance.

Coordinate preservation and two-ADD restoration for LemmaG.Stream (PR484,
DreamingOfClouds), using the append theorem of StreamShadowRowUpdate (PR3331,
1337isnot1337). The predecessor event semantics and append theorem retain
their attribution; this file proves the new preservation/cancellation interface.
-/
import StreamShadowRowUpdate

namespace Helper450Row

open LemmaG LemmaG.Stream StreamShadowRowUpdate

variable {ι Λ K : Type*} [DecidableEq ι]

/-- Relabels have no scalar effect, even when they name the protected coordinate.
All four scalar constructors are checked by their target coordinate. -/
def avoidsCoord (r : ι) : Event ι Λ K → Bool
  | .relabel .. => true
  | .add t _ _ => decide (r ≠ t)
  | .scale t _ => decide (r ≠ t)
  | .copy t _ _ => decide (r ≠ t)
  | .clear t _ => decide (r ≠ t)

def avoids (r : ι) (es : List (Event ι Λ K)) : Bool := es.all (avoidsCoord r)

theorem avoids_append (r : ι) (a b : List (Event ι Λ K)) :
    avoids r (a ++ b) = (avoids r a && avoids r b) := by
  simp [avoids, List.all_append]

theorem avoids_flatten (r : ι) (blocks : List (List (Event ι Λ K))) :
    avoids r blocks.flatten = blocks.all (avoids r) := by
  induction blocks with
  | nil => rfl
  | cons block blocks ih =>
      change avoids r (block ++ blocks.flatten) = (avoids r block && blocks.all (avoids r))
      rw [avoids_append, ih]

section Preserve

variable [Semiring K] {M : Type*} [AddCommMonoid M] [Module K M]

theorem event_preserves (e : Event ι Λ K) (r : ι)
    (h : avoidsCoord r e = true) (x : ι → M) : e.scal x r = x r := by
  cases e with
  | relabel t A B =>
      by_cases hr : r = t
      · subst r
        simp [Event.scal, Event.phys]
      · simp [Event.scal, Event.phys, Function.update_apply, hr]
  | add t s q =>
      have hr : r ≠ t := of_decide_eq_true h
      simp [Event.scal, Event.phys, Function.update_apply, hr]
  | scale t q =>
      have hr : r ≠ t := of_decide_eq_true h
      simp [Event.scal, Event.phys, Function.update_apply, hr]
  | copy t s F =>
      have hr : r ≠ t := of_decide_eq_true h
      simp [Event.scal, Event.phys, Function.update_apply, hr]
  | clear t F =>
      have hr : r ≠ t := of_decide_eq_true h
      simp [Event.scal, Event.phys, Function.update_apply, hr]

theorem block_preserves (es : List (Event ι Λ K)) (r : ι) :
    ∀ (x : ι → M), avoids r es = true → scalRun es x r = x r := by
  induction es with
  | nil =>
      intro x h
      rfl
  | cons e es ih =>
      intro x h
      have hh : avoidsCoord r e = true ∧ avoids r es = true := by
        simpa [avoids] using h
      change scalRun es (e.scal x) r = x r
      rw [ih (e.scal x) hh.2]
      exact event_preserves e r hh.1 x

end Preserve

section Cancel

variable [Ring K] {M : Type*} [AddCommGroup M] [Module K M]

/-- Two inverse additions restore the protected coordinate across arbitrary
intervening programs satisfying the four explicit target-avoidance premises.
Other coordinates and every label may change. Initial scalar contents are
arbitrary; in particular, no private coordinate is assumed to start at zero. -/
theorem inverse_adds_restore
    (pre middle suffix : List (Event ι Λ K)) (h p : ι) (q : K)
    (hp : h ≠ p)
    (hpre : avoids h pre = true)
    (hmid : avoids h middle = true)
    (pmid : avoids p middle = true)
    (hpost : avoids h suffix = true)
    (x : ι → M) :
    scalRun (pre ++ [Event.add h p q] ++ middle ++
      [Event.add h p (-q)] ++ suffix) x h = x h := by
  let before := scalRun pre x
  let raised := (Event.add h p q : Event ι Λ K).scal before
  let between := scalRun middle raised
  have eh : raised h = before h + q • before p := by
    simp [raised, Event.scal, Event.phys]
  have ep : raised p = before p := by
    simp [raised, Event.scal, Event.phys, Function.update_apply, hp, Ne.symm hp]
  have mh : between h = raised h := block_preserves middle h raised hmid
  have mp : between p = raised p := block_preserves middle p raised pmid
  have cancel : (Event.add h p (-q) : Event ι Λ K).scal between h = before h := by
    simp only [Event.scal, Event.phys, Function.update_self]
    rw [mh, mp, eh, ep]
    simp [neg_smul]
  calc
    scalRun (pre ++ [Event.add h p q] ++ middle ++
        [Event.add h p (-q)] ++ suffix) x h =
        scalRun suffix ((Event.add h p (-q) : Event ι Λ K).scal between) h := by
          simp only [scalRun_append]
          rfl
    _ = (Event.add h p (-q) : Event ι Λ K).scal between h :=
      block_preserves suffix h _ hpost
    _ = before h := cancel
    _ = x h := block_preserves pre h x hpre

theorem inverse_adds_unit_row
    (pre middle suffix : List (Event ι Λ K)) (h p : ι) (q : K)
    (hp : h ≠ p)
    (hpre : avoids h pre = true)
    (hmid : avoids h middle = true)
    (pmid : avoids p middle = true)
    (hpost : avoids h suffix = true) (j : ι) :
    S (K := K) (pre ++ [Event.add h p q] ++ middle ++
      [Event.add h p (-q)] ++ suffix) h j = (Pi.single j (1 : K) : ι → K) h := by
  exact inverse_adds_restore pre middle suffix h p q hp hpre hmid pmid hpost
    (Pi.single j (1 : K))

end Cancel

end Helper450Row
