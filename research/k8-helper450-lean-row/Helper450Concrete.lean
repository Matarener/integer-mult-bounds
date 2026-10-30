/-
Copyright (c) 2026 Sagar Thakrar. Released under the Apache 2.0 license.
Prepared with substantial OpenAI Codex assistance.

The complete K8.Forward.events word is generated unchanged by PR2944's pinned
translation and generator. This file adds its concrete helper450 scalar row;
the original program, translator and label proof retain predecessor credit.
See SOURCES.json and README.md for the exact provenance and scope.
-/
import ForwardResult
import Helper450Row
import Mathlib.Algebra.Field.Rat

namespace Helper450Concrete

open LemmaG LemmaG.Stream Helper450Row

set_option maxRecDepth 10000
set_option maxHeartbeats 0

abbrev Reg := Fin (2 ^ 10)
abbrev Word := List (Event Reg Nat Rat)

def preBlocks := K8.Forward.blocks.take 54
def middleBlocks := (K8.Forward.blocks.drop 55).take 9
def postBlocks := K8.Forward.blocks.drop 65

def preWord : Word := preBlocks.flatten ++ K8.Forward.block54.take 120
def middleWord : Word := K8.Forward.block54.drop 121 ++ middleBlocks.flatten ++
  K8.Forward.block64.take 117
def postWord : Word := K8.Forward.block64.drop 118 ++ postBlocks.flatten

theorem blocks_decomposition :
    K8.Forward.blocks = preBlocks ++ [K8.Forward.block54] ++ middleBlocks ++
      [K8.Forward.block64] ++ postBlocks := by
  rfl

theorem first_gate :
    K8.Forward.block54.drop 120 =
      Event.add (450 : Reg) (230 : Reg) (1 : Rat) :: K8.Forward.block54.drop 121 := by
  have raw : K8.Forward.block54.drop 120 =
      Event.add (450 : Reg) (230 : Reg) ((1 : Rat) / 1) :: K8.Forward.block54.drop 121 := by rfl
  simpa only [div_one] using raw

theorem second_gate :
    K8.Forward.block64.drop 117 =
      Event.add (450 : Reg) (230 : Reg) (-1 : Rat) :: K8.Forward.block64.drop 118 := by
  have raw : K8.Forward.block64.drop 117 =
      Event.add (450 : Reg) (230 : Reg) ((-1 : Rat) / 1) :: K8.Forward.block64.drop 118 := by rfl
  simpa only [div_one] using raw

theorem first_block : K8.Forward.block54 = K8.Forward.block54.take 120 ++
    [Event.add (450 : Reg) (230 : Reg) (1 : Rat)] ++ K8.Forward.block54.drop 121 := by
  calc
    K8.Forward.block54 = K8.Forward.block54.take 120 ++ K8.Forward.block54.drop 120 :=
      (List.take_append_drop 120 K8.Forward.block54).symm
    _ = K8.Forward.block54.take 120 ++
        (Event.add (450 : Reg) (230 : Reg) (1 : Rat) :: K8.Forward.block54.drop 121) :=
      congrArg (List.append (K8.Forward.block54.take 120)) first_gate
    _ = _ := by rw [List.append_assoc]; rfl

theorem second_block : K8.Forward.block64 = K8.Forward.block64.take 117 ++
    [Event.add (450 : Reg) (230 : Reg) (-1 : Rat)] ++ K8.Forward.block64.drop 118 := by
  calc
    K8.Forward.block64 = K8.Forward.block64.take 117 ++ K8.Forward.block64.drop 117 :=
      (List.take_append_drop 117 K8.Forward.block64).symm
    _ = K8.Forward.block64.take 117 ++
        (Event.add (450 : Reg) (230 : Reg) (-1 : Rat) :: K8.Forward.block64.drop 118) :=
      congrArg (List.append (K8.Forward.block64.take 117)) second_gate
    _ = _ := by rw [List.append_assoc]; rfl

theorem word_decomposition :
    K8.Forward.events = preWord ++ [Event.add (450 : Reg) (230 : Reg) (1 : Rat)] ++
      middleWord ++ [Event.add (450 : Reg) (230 : Reg) (-1 : Rat)] ++ postWord := by
  calc
    K8.Forward.events = preBlocks.flatten ++ K8.Forward.block54 ++
        middleBlocks.flatten ++ K8.Forward.block64 ++ postBlocks.flatten := by
      change K8.Forward.blocks.flatten = _
      rw [blocks_decomposition]
      simp only [List.flatten_append, List.flatten_cons, List.flatten_nil,
        List.append_nil, List.append_assoc]
    _ = preBlocks.flatten ++
        (K8.Forward.block54.take 120 ++ [Event.add (450 : Reg) (230 : Reg) (1 : Rat)] ++
          K8.Forward.block54.drop 121) ++
        middleBlocks.flatten ++ K8.Forward.block64 ++ postBlocks.flatten :=
      congrArg (fun b => preBlocks.flatten ++ b ++ middleBlocks.flatten ++
        K8.Forward.block64 ++ postBlocks.flatten) first_block
    _ = preBlocks.flatten ++
        (K8.Forward.block54.take 120 ++ [Event.add (450 : Reg) (230 : Reg) (1 : Rat)] ++
          K8.Forward.block54.drop 121) ++ middleBlocks.flatten ++
        (K8.Forward.block64.take 117 ++ [Event.add (450 : Reg) (230 : Reg) (-1 : Rat)] ++
          K8.Forward.block64.drop 118) ++ postBlocks.flatten :=
      congrArg (fun b => preBlocks.flatten ++
        (K8.Forward.block54.take 120 ++ [Event.add (450 : Reg) (230 : Reg) (1 : Rat)] ++
          K8.Forward.block54.drop 121) ++ middleBlocks.flatten ++ b ++ postBlocks.flatten)
        second_block
    _ = _ := by simp only [preWord, middleWord, postWord, List.append_assoc]

theorem prefix_avoids : avoids (450 : Reg) preWord = true := by
  simp only [preWord, avoids_append, avoids_flatten]
  decide +kernel
theorem middle_avoids_helper : avoids (450 : Reg) middleWord = true := by
  simp only [middleWord, avoids_append, avoids_flatten]
  decide +kernel
theorem middle_avoids_partner : avoids (230 : Reg) middleWord = true := by
  simp only [middleWord, avoids_append, avoids_flatten]
  decide +kernel
theorem suffix_avoids : avoids (450 : Reg) postWord = true := by
  simp only [postWord, avoids_append, avoids_flatten]
  decide +kernel

/-- The complete retained word restores coordinate 450 for every initial scalar state. -/
theorem helper450_restored (x : Reg → Rat) :
    scalRun K8.Forward.events x (450 : Reg) = x (450 : Reg) := by
  rw [word_decomposition]
  exact inverse_adds_restore preWord middleWord postWord (450 : Reg) (230 : Reg)
    (1 : Rat) (by decide) prefix_avoids middle_avoids_helper middle_avoids_partner
    suffix_avoids x

/-- The exact `hS` unit-row hypothesis, with every one of the 1024 typed columns. -/
theorem helper450_unit_row (j : Reg) :
    S K8.Forward.events (450 : Reg) j = (Pi.single j (1 : Rat) : Reg → Rat) (450 : Reg) := by
  exact helper450_restored (Pi.single j (1 : Rat))

/-- The premise is stated in exactly the orientation expected by `Stream.row_unit`
and the hyperplane-ended helper theorems. -/
theorem helper450_hS : ∀ j : Reg,
    S K8.Forward.events (450 : Reg) j = if j = (450 : Reg) then 1 else 0 := by
  intro j
  by_cases hj : j = (450 : Reg)
  · subst j
    simpa using helper450_unit_row (450 : Reg)
  · simpa [Pi.single_apply, hj, Ne.symm hj] using helper450_unit_row j

end Helper450Concrete
