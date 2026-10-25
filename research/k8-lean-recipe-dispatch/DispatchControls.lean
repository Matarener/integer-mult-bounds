/-
Copyright (c) 2026 Sagar Thakrar. All rights reserved.
Released under the Apache 2.0 license, as described in the repository LICENSE.
Prepared with OpenAI Codex assistance. This is not independent human review.
Uses DreamingOfClouds's LemmaG stream semantics and Nick Petalas's PR2944
source-bound Nat labels and complete typed forward word. The independently
supplied operator model retains all used native child equations as hypotheses.
-/

import K8RecipeDispatch
import Mathlib.Algebra.Field.Rat
import Mathlib.LinearAlgebra.Prod

namespace DispatchControls
open K8RecipeDispatch

abbrev V := Rat × Rat

def shear : V ≃ₗ[Rat] V where
  toFun x := (x.1 + x.2, x.2)
  invFun x := (x.1 - x.2, x.2)
  left_inv x := by ext <;> simp
  right_inv x := by ext <;> simp
  map_add' x y := by ext <;> simp [add_assoc, add_left_comm, add_comm]
  map_smul' a x := by ext <;> simp [mul_add]

def flip : V ≃ₗ[Rat] V where
  toFun x := (x.2, x.1)
  invFun x := (x.2, x.1)
  left_inv x := by cases x; rfl
  right_inv x := by cases x; rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

def model : Model Rat V := ⟨fun _ => flip, fun _ => shear, fun _ => flip⟩

def tables : Tables := {
  children := .nil
  source := .node 0 7 .nil .nil
  target := .node 112 7 .nil .nil
  pre := .node 450 7 .nil .nil
  post := .node 450 7 .nil .nil }

theorem source_route : checkBlock tables [.relabel 0 1006 2]
    [(0, 1006, 2, .source 7)] = true := by decide +kernel

theorem source_inverse_descriptor_rejected : checkBlock tables [.relabel 0 1006 2]
    [(0, 1006, 2, .target 7)] = false := by decide +kernel

theorem unbound_child_rejected : checkBlock tables [.relabel 0 2 3]
    [(0, 2, 3, .identity)] = false := by decide +kernel

theorem identity_route : checkBlock tables [.relabel 0 2 2]
    [(0, 2, 2, .identity)] = true := by decide +kernel

theorem prew450_codec :
    (decode (2 + 1004 * (1 + 450 + 712 * 2))).frame = 2 ∧
    (decode (2 + 1004 * (1 + 450 + 712 * 2))).owner = 450 ∧
    (decode (2 + 1004 * (1 + 450 + 712 * 2))).tag = 3 := by decide +kernel

theorem wrong_stride_rejected :
    transitionOK tables (decode (2 + 1004 * (1 + 450 + 1024 * 2))) (decode 2) = false := by
  decide +kernel

theorem wrong_terminal_rejected :
    transitionOK tables (decode 2) (decode (999 + 1004 * (1 + 450 + 712 * 3))) = false := by
  decide +kernel

theorem source_value : dispatch tables model 1006 2 (1, 2) = (3, 2) := by
  norm_num [dispatch, dispatchCode, recipeFor, decode, monoId, LookupTree.find,
    tables, evalRecipe, model, shear]

theorem inverse_value : shear.symm (1, 2) = (-1, 2) := by
  norm_num [shear]

theorem pre_order_value : tagOp tables model 1006 (1, 2) = (1, 1) := by
  norm_num [tagOp, decodedOp, decode, monoId, LookupTree.find, tables,
    model, shear, flip, LinearEquiv.trans_apply]

theorem reversed_order_value : flip (shear.symm (1, 2)) = (2, -1) := by
  norm_num [shear, flip]

def childModel : Model Rat V := {
  frame := fun _ => flip
  monomial := fun i => if i = 7 then shear else flip
  core := fun _ => LinearEquiv.refl Rat V }

theorem child_order_value :
    evalRecipe childModel (.child ⟨0, 2, 7, 8⟩) (1, 2) = (3, 1) := by
  norm_num [evalRecipe, childModel, shear, flip]

theorem reversed_child_order_value : flip (shear (1, 2)) = (2, 3) := by
  norm_num [shear, flip]

end DispatchControls
