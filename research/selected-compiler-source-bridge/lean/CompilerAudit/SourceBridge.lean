/-
SPDX-License-Identifier: Apache-2.0

Source-to-model transport for `CompilerAudit.Result.selected_compiler_model`,
built against the unchanged PR3391 modules (Lean 4.34.1, pinned mathlib).

Status: the formal text below (definitions, statements and proofs) was checked
in a prior local review run: fresh compilation, exact main-theorem type, full
axiom inventory and a leaf kernel replay. Execution evidence for this
candidate package is recorded in `../VALIDATION.md` (relative to `lean/`);
rerun `check.py` before relying on it in a new environment.

What this adds over the package: the package *defines* the model word
`visitWord groups replicas N` and the fresh-ID stream `emitFrom 0 budgets`.
Here a separately specified *source-shaped* trace is written as a literal
transcription of the loop nesting of `macro_code.compile_node` (schedule
event -> replica -> LOW -> local position for sweeps; schedule event ->
replica -> request id -> LOW for idles; no residual for bridge/exchange), over
an ABSTRACT LOW type `α` with a separate rank function, and a source-shaped op
stream with arbitrary wrapper identities `W` interleaved with wrapper-free
non-residual ops. From primitive per-event / per-LOW / per-visit hypotheses
(NOT from trace or count equality) we derive:
* the renamed source trace equals `Selected.word N`;
* the number of distinct source keys (in the LOW type, before ranking) is 28278*N;
* the number of distinct retained wrapper identities is 904896*N;
* the number of direct wrapper references is 1809792*N + blockTotal.

Not claimed: Python semantics, that the hypotheses hold for the pinned
sources, realizability of complete execution on CPython (for GL64(F_q),
q >= 3, a complete list representation of the selected trace exceeds the
capacity of conventional 32-bit and 64-bit CPython builds; the source trace
here is denotational/unbounded), native/stock/space results, or multiplication.
-/
import CompilerAudit.Result

namespace CompilerAudit.SourceBridge

open CompilerAudit

/-- Source-level residual key: (request id, common view flag, LOW object). -/
abbrev SKey (α : Type) := Nat × Bool × α

/-- One local event as seen by `LocalState.accept(position)`: `op = event[0]`
(0 MOVE, 1 XOR, 2 COPY, 3 ERASE) and `request = call.requests[position]`. -/
structure LocalEvent where
  op : Nat
  request : Option Nat

/-- Residual factory requests issued at one local position: only MOVE (0) and
COPY (2) call `residual(..., call.requests[position], True, low)`. -/
def LocalEvent.emits (e : LocalEvent) : List Nat :=
  if e.op = 0 ∨ e.op = 2 then e.request.toList else []

/-- A schedule event after dispatch on `event["kind"]`.
`sweep calls`: `calls r` is the event list of `topology.call(stage, r)`.
`idle ids`: `topology.idles[event["idx"]]` (replica independent by construction).
`silent`: bridge/exchange, which issue no residual call. -/
inductive Event where
  | sweep (calls : Nat → List LocalEvent)
  | idle (ids : List Nat)
  | silent

section Trace

variable {α : Type}

/-- Innermost sweep loop: positions of one call at one LOW. -/
def lowPass (evs : List LocalEvent) (l : α) : List (SKey α) :=
  evs.flatMap fun e => e.emits.map fun i => (i, true, l)

/-- One replica of a sweep: `for low in low_classes(): for position ...`. -/
def replicaPass (lows : List α) (evs : List LocalEvent) : List (SKey α) :=
  lows.flatMap (lowPass evs)

/-- One replica of an idle event: `for identifier in idles: for low in ...`. -/
def idlePass (lows : List α) (ids : List Nat) : List (SKey α) :=
  ids.flatMap fun i => lows.map fun l => (i, false, l)

/-- `for replica in range(topology.replicas)` around each event body. -/
def eventTrace (lows : List α) (replicas : Nat) : Event → List (SKey α)
  | .sweep calls => (List.range replicas).flatMap fun r => replicaPass lows (calls r)
  | .idle ids => (List.range replicas).flatMap fun _ => idlePass lows ids
  | .silent => []

/-- `for event in topology.schedule`. -/
def sourceTrace (lows : List α) (replicas : Nat) (sched : List Event) : List (SKey α) :=
  sched.flatMap (eventTrace lows replicas)

/-- Drop the residual-free events. -/
def residualEvents : List Event → List Event
  | [] => []
  | .sweep calls :: es => .sweep calls :: residualEvents es
  | .idle ids :: es => .idle ids :: residualEvents es
  | .silent :: es => residualEvents es

/-- Primitive per-event correspondence with one model group. For sweeps this is
the emitted-request projection of every replica's call, which the census
checks; it does NOT mention LOWs, N, the trace, or any count. -/
def Matches (replicas : Nat) : Event → Group → Prop
  | .sweep calls, g => g.common = true ∧ g.lowMajor = true ∧
      ∀ r, r < replicas → (calls r).flatMap LocalEvent.emits = g.ids
  | .idle ids, g => g.common = false ∧ g.lowMajor = false ∧ ids = g.ids
  | .silent, _ => False

/-- LOW renaming by a rank function. -/
def rename (rank : α → Nat) (k : SKey α) : Key := (k.1, k.2.1, rank k.2.2)

end Trace

/-! ### Generic list lemmas -/

theorem flatMap_range'_const {β : Type} (f : Nat → List β) (xs : List β) :
    ∀ (s n : Nat), (∀ r, s ≤ r → r < s + n → f r = xs) →
      (List.range' s n).flatMap f = copies n xs
  | _, 0, _ => by simp [copies]
  | s, n + 1, h => by
      show f s ++ (List.range' (s + 1) n).flatMap f = xs ++ copies n xs
      rw [h s (Nat.le_refl s) (by omega),
        flatMap_range'_const f xs (s + 1) n (fun r h1 h2 => h r (by omega) (by omega))]

theorem flatMap_range_const {β : Type} (f : Nat → List β) (xs : List β) (n : Nat)
    (h : ∀ r, r < n → f r = xs) : (List.range n).flatMap f = copies n xs := by
  rw [List.range_eq_range']
  exact flatMap_range'_const f xs 0 n (fun r _ h2 => h r (by omega))

theorem product_map_swap (l₁ l₂ : List Nat) (c : Bool) :
    ((l₁ ×ˢ l₂).map fun p => ((p.2, c, p.1) : Key)) =
      l₁.flatMap fun o => l₂.map fun i => ((i, c, o) : Key) := by
  induction l₁ with
  | nil => rfl
  | cons a l ih =>
    show ((l₂.map fun b => (a, b)) ++ l ×ˢ l₂).map (fun p => ((p.2, c, p.1) : Key)) =
      (l₂.map fun i => ((i, c, a) : Key)) ++ l.flatMap fun o => l₂.map fun i => ((i, c, o) : Key)
    rw [List.map_append, ih, List.map_map]
    all_goals rfl

theorem product_map_keep (l₁ l₂ : List Nat) (c : Bool) :
    ((l₁ ×ˢ l₂).map fun p => ((p.1, c, p.2) : Key)) =
      l₁.flatMap fun i => l₂.map fun o => ((i, c, o) : Key) := by
  induction l₁ with
  | nil => rfl
  | cons a l ih =>
    show ((l₂.map fun b => (a, b)) ++ l ×ˢ l₂).map (fun p => ((p.1, c, p.2) : Key)) =
      (l₂.map fun o => ((a, c, o) : Key)) ++ l.flatMap fun i => l₂.map fun o => ((i, c, o) : Key)
    rw [List.map_append, ih, List.map_map]
    all_goals rfl

theorem groupWord_low (N : Nat) (g : Group) (hc : g.common = true) (hl : g.lowMajor = true) :
    groupWord N g = (List.range N).flatMap fun o => g.ids.map fun i => ((i, true, o) : Key) := by
  rw [groupWord, ite_eq_left hl, hc, product_map_swap]

theorem groupWord_idle (N : Nat) (g : Group) (hc : g.common = false) (hl : g.lowMajor = false) :
    groupWord N g = g.ids.flatMap fun i => (List.range N).map fun o => ((i, false, o) : Key) := by
  have hn : ¬ (g.lowMajor = true) := by rw [hl]; decide
  rw [groupWord, ite_eq_right hn, hc, product_map_keep]

theorem map_eq_self_of (f : Nat → Nat) :
    ∀ l : List Nat, (∀ x ∈ l, f x = x) → l.map f = l
  | [], _ => rfl
  | a :: l, h => by
      rw [List.map_cons, h a (by simp), map_eq_self_of f l (fun x hx => h x (by simp [hx]))]

/-! ### LOW enumeration premises -> renaming facts -/

section Low

variable {α : Type}

/-- `low_classes()` yields `unrank(o)` for `o in range(N)`; with `rank∘unrank = id`
on that range, ranking the enumerated LOWs gives `range N` in order. -/
theorem lows_rank (lows : List α) (rank : α → Nat) (unrank : Nat → α) (N : Nat)
    (hlows : lows = (List.range N).map unrank) (hinv : ∀ o, o < N → rank (unrank o) = o) :
    lows.map rank = List.range N := by
  rw [hlows, List.map_map]
  exact map_eq_self_of _ _ (fun x hx => hinv x (List.mem_range.mp hx))

theorem rank_injOn (lows : List α) (rank : α → Nat) (unrank : Nat → α) (N : Nat)
    (hlows : lows = (List.range N).map unrank) (hinv : ∀ o, o < N → rank (unrank o) = o) :
    ∀ x ∈ lows, ∀ y ∈ lows, rank x = rank y → x = y := by
  intro x hx y hy hxy
  rw [hlows] at hx hy
  obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hx
  obtain ⟨b, hb, rfl⟩ := List.mem_map.mp hy
  rw [hinv a (List.mem_range.mp ha), hinv b (List.mem_range.mp hb)] at hxy
  rw [hxy]

/-! ### Per-event transport -/

theorem lowPass_eq (evs : List LocalEvent) (l : α) :
    lowPass evs l = (evs.flatMap LocalEvent.emits).map fun i => ((i, true, l) : SKey α) := by
  unfold lowPass
  rw [List.map_flatMap]

theorem replicaPass_map (rank : α → Nat) (evs : List LocalEvent) :
    ∀ lows : List α, (replicaPass lows evs).map (rename rank) =
      (lows.map rank).flatMap fun o =>
        (evs.flatMap LocalEvent.emits).map fun i => ((i, true, o) : Key)
  | [] => rfl
  | l :: ls => by
      show (lowPass evs l ++ replicaPass ls evs).map (rename rank) = _
      rw [List.map_append, replicaPass_map rank evs ls, lowPass_eq, List.map_map]
      all_goals rfl

theorem idlePass_map (rank : α → Nat) (lows : List α) (ids : List Nat) :
    (idlePass lows ids).map (rename rank) =
      ids.flatMap fun i => (lows.map rank).map fun o => ((i, false, o) : Key) := by
  induction ids with
  | nil => rfl
  | cons i is ih =>
    show ((lows.map fun l => ((i, false, l) : SKey α)) ++ idlePass lows is).map (rename rank) =
      (lows.map rank).map (fun o => ((i, false, o) : Key)) ++
        is.flatMap fun i => (lows.map rank).map fun o => ((i, false, o) : Key)
    rw [List.map_append, ih, List.map_map, List.map_map]
    all_goals rfl

theorem sweep_transport (lows : List α) (rank : α → Nat) (N replicas : Nat)
    (hlow : lows.map rank = List.range N) (calls : Nat → List LocalEvent) (g : Group)
    (hm : Matches replicas (.sweep calls) g) :
    (eventTrace lows replicas (.sweep calls)).map (rename rank) =
      copies replicas (groupWord N g) := by
  have hm' : g.common = true ∧ g.lowMajor = true ∧
      ∀ r, r < replicas → (calls r).flatMap LocalEvent.emits = g.ids := hm
  obtain ⟨hc, hl, hp⟩ := hm'
  show ((List.range replicas).flatMap fun r => replicaPass lows (calls r)).map (rename rank) = _
  rw [List.map_flatMap, groupWord_low N g hc hl]
  apply flatMap_range_const
  intro r hr
  show (replicaPass lows (calls r)).map (rename rank) = _
  rw [replicaPass_map, hlow, hp r hr]

theorem idle_transport (lows : List α) (rank : α → Nat) (N replicas : Nat)
    (hlow : lows.map rank = List.range N) (ids : List Nat) (g : Group)
    (hm : Matches replicas (.idle ids) g) :
    (eventTrace lows replicas (.idle ids)).map (rename rank) =
      copies replicas (groupWord N g) := by
  have hm' : g.common = false ∧ g.lowMajor = false ∧ ids = g.ids := hm
  obtain ⟨hc, hl, hids⟩ := hm'
  show ((List.range replicas).flatMap fun _ => idlePass lows ids).map (rename rank) = _
  rw [List.map_flatMap, groupWord_idle N g hc hl]
  apply flatMap_range_const
  intro r _
  show (idlePass lows ids).map (rename rank) = _
  rw [idlePass_map, hlow, hids]

theorem sourceTrace_cons (lows : List α) (replicas : Nat) (e : Event) (es : List Event) :
    sourceTrace lows replicas (e :: es) =
      eventTrace lows replicas e ++ sourceTrace lows replicas es := by
  simp [sourceTrace]

/-- Main trace transport: literal loop nesting + per-event projections + LOW
enumeration order imply the renamed source trace IS the model word. -/
theorem trace_transport (lows : List α) (rank : α → Nat) (N replicas : Nat)
    (hlow : lows.map rank = List.range N) :
    ∀ (sched : List Event) (groups : List Group),
      List.Forall₂ (Matches replicas) (residualEvents sched) groups →
      (sourceTrace lows replicas sched).map (rename rank) = visitWord groups replicas N
  | [], groups, h => by
      have h' : List.Forall₂ (Matches replicas) [] groups := h
      cases h'
      rfl
  | .sweep calls :: es, groups, h => by
      have h' : List.Forall₂ (Matches replicas) (.sweep calls :: residualEvents es) groups := h
      cases h' with
      | cons hm hrest =>
        rw [sourceTrace_cons, List.map_append,
          sweep_transport lows rank N replicas hlow calls _ hm,
          trace_transport lows rank N replicas hlow es _ hrest]
        all_goals rfl
  | .idle ids :: es, groups, h => by
      have h' : List.Forall₂ (Matches replicas) (.idle ids :: residualEvents es) groups := h
      cases h' with
      | cons hm hrest =>
        rw [sourceTrace_cons, List.map_append,
          idle_transport lows rank N replicas hlow ids _ hm,
          trace_transport lows rank N replicas hlow es _ hrest]
        all_goals rfl
  | .silent :: es, groups, h => by
      rw [sourceTrace_cons]
      exact trace_transport lows rank N replicas hlow es groups h

/-! ### Distinct keys in the source LOW type (before ranking) -/

theorem mem_eventTrace_low (lows : List α) (replicas : Nat) (e : Event) (k : SKey α)
    (hk : k ∈ eventTrace lows replicas e) : k.2.2 ∈ lows := by
  cases e with
  | sweep calls =>
    have hk' : k ∈ (List.range replicas).flatMap fun r => replicaPass lows (calls r) := hk
    obtain ⟨r, -, hr⟩ := List.mem_flatMap.mp hk'
    have hr' : k ∈ lows.flatMap (lowPass (calls r)) := hr
    obtain ⟨l, hl, hl'⟩ := List.mem_flatMap.mp hr'
    have hl'' : k ∈ (calls r).flatMap fun e => e.emits.map fun i => ((i, true, l) : SKey α) := hl'
    obtain ⟨e, -, he⟩ := List.mem_flatMap.mp hl''
    obtain ⟨i, -, rfl⟩ := List.mem_map.mp he
    exact hl
  | idle ids =>
    have hk' : k ∈ (List.range replicas).flatMap fun _ => idlePass lows ids := hk
    obtain ⟨r, -, hr⟩ := List.mem_flatMap.mp hk'
    have hr' : k ∈ ids.flatMap fun i => lows.map fun l => ((i, false, l) : SKey α) := hr
    obtain ⟨i, -, hi⟩ := List.mem_flatMap.mp hr'
    obtain ⟨l, hl, rfl⟩ := List.mem_map.mp hi
    exact hl
  | silent => simp [eventTrace] at hk

theorem mem_sourceTrace_low (lows : List α) (replicas : Nat) (sched : List Event) (k : SKey α)
    (hk : k ∈ sourceTrace lows replicas sched) : k.2.2 ∈ lows := by
  obtain ⟨e, -, he⟩ := List.mem_flatMap.mp hk
  exact mem_eventTrace_low lows replicas e k he

end Low

theorem toFinset_map_card {β γ : Type} [DecidableEq β] [DecidableEq γ] (f : β → γ) (l : List β)
    (hinj : ∀ x ∈ l, ∀ y ∈ l, f x = f y → x = y) :
    (l.map f).toFinset.card = l.toFinset.card := by
  have h : (l.map f).toFinset = l.toFinset.image f := by
    ext y
    simp
  rw [h, Finset.card_image_of_injOn]
  intro x hx y hy hxy
  exact hinj x (by simpa using hx) y (by simpa using hy) hxy

/-- Distinct source keys (LOW objects, not ranks) equal distinct model keys. -/
theorem source_distinct {α : Type} [DecidableEq α] (lows : List α) (rank : α → Nat)
    (unrank : Nat → α) (N replicas : Nat)
    (hlows : lows = (List.range N).map unrank) (hinv : ∀ o, o < N → rank (unrank o) = o)
    (sched : List Event) (groups : List Group)
    (h : List.Forall₂ (Matches replicas) (residualEvents sched) groups) :
    (sourceTrace lows replicas sched).toFinset.card =
      (visitWord groups replicas N).toFinset.card := by
  have hinj : ∀ x ∈ sourceTrace lows replicas sched, ∀ y ∈ sourceTrace lows replicas sched,
      rename rank x = rename rank y → x = y := by
    intro x hx y hy hxy
    obtain ⟨i, c, l⟩ := x
    obtain ⟨j, d, m⟩ := y
    have hl := mem_sourceTrace_low lows replicas sched _ hx
    have hm := mem_sourceTrace_low lows replicas sched _ hy
    simp only [rename, Prod.mk.injEq] at hxy
    obtain ⟨rfl, rfl, hr⟩ := hxy
    rw [rank_injOn lows rank unrank N hlows hinv l hl m hm hr]
  rw [← trace_transport lows rank N replicas (lows_rank lows rank unrank N hlows hinv)
    sched groups h]
  exact (toFinset_map_card (rename rank) _ hinj).symm

/-! ### Source-shaped op stream with arbitrary wrapper identities -/

/-- `residual_begin`, `block`, `residual_end` carry a wrapper; every other
compile_node operation is `other` (obligation: it carries no Residual). -/
inductive SrcOp (W : Type) where
  | begin (w : W)
  | block (w : W)
  | finish (w : W)
  | other

def SrcOp.ref {W : Type} : SrcOp W → Option W
  | .begin w => some w
  | .block w => some w
  | .finish w => some w
  | .other => none

/-- One residual call: `pre` wrapper-free ops before it, its wrapper, its blocks. -/
structure Seg (W : Type) where
  pre : Nat
  wrapper : W
  blocks : Nat

def segOps {W : Type} (s : Seg W) : List (SrcOp W) :=
  List.replicate s.pre .other ++
    (.begin s.wrapper :: (List.replicate s.blocks (.block s.wrapper) ++ [.finish s.wrapper]))

def emitSrc {W : Type} (segs : List (Seg W)) (tail : Nat) : List (SrcOp W) :=
  segs.flatMap segOps ++ List.replicate tail .other

/-- Direct wrapper references in the operation list. -/
def srcRefs {W : Type} (ops : List (SrcOp W)) : List W := ops.filterMap SrcOp.ref

def srcRetained {W : Type} [DecidableEq W] (ops : List (SrcOp W)) : Finset W :=
  (srcRefs ops).toFinset

theorem fm_other {W : Type} (n : Nat) :
    (List.replicate n (SrcOp.other : SrcOp W)).filterMap SrcOp.ref = [] := by
  induction n with
  | zero => rfl
  | succ n ih => exact ih

theorem fm_block {W : Type} (n : Nat) (w : W) :
    (List.replicate n (SrcOp.block w)).filterMap SrcOp.ref = List.replicate n w := by
  induction n with
  | zero => rfl
  | succ n ih => exact congrArg (w :: ·) ih

theorem fm_seg {W : Type} (s : Seg W) :
    (segOps s).filterMap SrcOp.ref =
      s.wrapper :: (List.replicate s.blocks s.wrapper ++ [s.wrapper]) := by
  unfold segOps
  rw [List.filterMap_append, fm_other, List.nil_append]
  show s.wrapper :: (List.replicate s.blocks (SrcOp.block s.wrapper) ++
    [SrcOp.finish s.wrapper]).filterMap SrcOp.ref = _
  rw [List.filterMap_append, fm_block]
  all_goals rfl

theorem refs_emit {W : Type} (segs : List (Seg W)) (tail : Nat) :
    srcRefs (emitSrc segs tail) =
      segs.flatMap fun s => s.wrapper :: (List.replicate s.blocks s.wrapper ++ [s.wrapper]) := by
  unfold srcRefs emitSrc
  rw [List.filterMap_append, fm_other, List.append_nil]
  induction segs with
  | nil => rfl
  | cons s ss ih => rw [List.flatMap_cons, List.filterMap_append, ih, fm_seg, List.flatMap_cons]

theorem refs_length {W : Type} (segs : List (Seg W)) (tail : Nat) :
    (srcRefs (emitSrc segs tail)).length = 2 * segs.length + (segs.map Seg.blocks).sum := by
  rw [refs_emit]
  induction segs with
  | nil => rfl
  | cons s ss ih =>
    rw [List.flatMap_cons, List.length_append, ih]
    simp only [List.length_cons, List.length_append, List.length_replicate,
      List.length_nil, List.map_cons, List.sum_cons]
    all_goals omega

/-- Freshness (pairwise distinct wrappers) is a hypothesis, not derived. -/
theorem retained_emit {W : Type} [DecidableEq W] (segs : List (Seg W)) (tail : Nat)
    (hfresh : (segs.map Seg.wrapper).Nodup) :
    (srcRetained (emitSrc segs tail)).card = segs.length := by
  have h : srcRetained (emitSrc segs tail) = (segs.map Seg.wrapper).toFinset := by
    unfold srcRetained
    rw [refs_emit]
    ext w
    simp only [List.mem_toFinset, List.mem_flatMap, List.mem_map, List.mem_cons,
      List.mem_append, List.mem_replicate]
    constructor
    · rintro ⟨s, hs, hw⟩
      refine ⟨s, hs, ?_⟩
      rcases hw with h1 | h1 | h1 | h1 <;>
        first | exact h1.symm | exact h1.2.symm | simp at h1
    · rintro ⟨s, hs, rfl⟩
      exact ⟨s, hs, Or.inl rfl⟩
  rw [h, List.toFinset_card_of_nodup hfresh, List.length_map]

/-! ### Selected corollary -/

/-- Conditional transport to the package's selected model. Hypotheses are
primitive: LOW enumeration/inverse, per-event emitted projection matching the
19 certified groups, one segment per residual call with its block budget, and
wrapper freshness. Conclusions are derived, not assumed. -/
theorem selected_source_transport {α W : Type} [DecidableEq α] [DecidableEq W]
    (lows : List α) (rank : α → Nat) (unrank : Nat → α) (N : Nat)
    (hlows : lows = (List.range N).map unrank) (hinv : ∀ o, o < N → rank (unrank o) = o)
    (sched : List Event)
    (hsched : List.Forall₂ (Matches SelectedData.replicaCount) (residualEvents sched)
      Selected.groups)
    (blocks : Key → Nat) (segs : List (Seg W)) (tail : Nat)
    (hbud : segs.map Seg.blocks =
      (sourceTrace lows SelectedData.replicaCount sched).map fun k => blocks (rename rank k))
    (hfresh : (segs.map Seg.wrapper).Nodup) :
    (sourceTrace lows SelectedData.replicaCount sched).map (rename rank) = Selected.word N ∧
    (sourceTrace lows SelectedData.replicaCount sched).toFinset.card = 28278 * N ∧
    (srcRetained (emitSrc segs tail)).card = 904896 * N ∧
    (srcRefs (emitSrc segs tail)).length = 1809792 * N + Result.blockTotal N blocks := by
  have htr : (sourceTrace lows SelectedData.replicaCount sched).map (rename rank) =
      Selected.word N := trace_transport lows rank N SelectedData.replicaCount
    (lows_rank lows rank unrank N hlows hinv) sched Selected.groups hsched
  have hlen : segs.length = 904896 * N := by
    have h1 := congrArg List.length hbud
    rw [List.length_map, List.length_map] at h1
    have h2 := congrArg List.length htr
    rw [List.length_map] at h2
    rw [h1, h2]
    exact Selected.word_length N
  have hsum : (segs.map Seg.blocks).sum = Result.blockTotal N blocks := by
    rw [hbud]
    show _ = ((Selected.word N).map blocks).sum
    rw [← htr, List.map_map]
    all_goals rfl
  have hdist : (sourceTrace lows SelectedData.replicaCount sched).toFinset.card = 28278 * N :=
    (source_distinct lows rank unrank N SelectedData.replicaCount hlows hinv sched
      Selected.groups hsched).trans (Selected.word_distinct N)
  refine ⟨htr, hdist, ?_, ?_⟩
  · rw [retained_emit segs tail hfresh, hlen]
  · rw [refs_length, hlen, hsum]
    all_goals omega

end CompilerAudit.SourceBridge
