-- SPDX-License-Identifier: Apache-2.0
import CompilerAudit.SourceBridge
open CompilerAudit CompilerAudit.SourceBridge
-- Negative probe: the main theorem does not prove a perturbed retained coefficient.
example {α W : Type} [DecidableEq α] [DecidableEq W]
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
    (srcRetained (emitSrc segs tail)).card = 904897 * N ∧
    (srcRefs (emitSrc segs tail)).length = 1809792 * N + Result.blockTotal N blocks := by
  exact CompilerAudit.SourceBridge.selected_source_transport lows rank unrank N hlows hinv sched hsched blocks segs tail hbud hfresh
