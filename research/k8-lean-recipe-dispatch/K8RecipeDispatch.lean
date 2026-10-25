/-
Copyright (c) 2026 Sagar Thakrar. All rights reserved.
Released under the Apache 2.0 license, as described in the repository LICENSE.
Prepared with OpenAI Codex assistance. This is not independent human review.
Uses DreamingOfClouds's LemmaG stream semantics and Nick Petalas's PR2944
source-bound Nat labels and complete typed forward word. The independently
supplied operator model retains all used native child equations as hypotheses.
-/

import LemmaG.Stream
import Mathlib.Tactic

namespace K8RecipeDispatch

inductive LookupTree (α : Type) where
  | nil
  | node (key : Nat) (value : α) (left right : LookupTree α)
  deriving Repr

def LookupTree.find (key : Nat) : LookupTree α → Option α
  | .nil => none
  | .node k v l r => if key = k then some v else if key < k then l.find key else r.find key

def LookupTree.size : LookupTree α → Nat
  | .nil => 0
  | .node _ _ l r => l.size + r.size + 1

structure Child where
  id : Nat
  rank : Nat
  left : Nat
  right : Nat
  deriving BEq, DecidableEq, Repr

inductive Recipe where
  | child (c : Child)
  | source (id : Nat)
  | target (id : Nat)
  | pre (id : Nat)
  | post (id : Nat)
  | identity
  deriving BEq, DecidableEq, Repr

structure Tables where
  children : LookupTree Child
  source : LookupTree Nat
  target : LookupTree Nat
  pre : LookupTree Nat
  post : LookupTree Nat

structure Label where
  frame : Nat
  owner : Nat
  tag : Nat

/-- The exact PR2944 codec: 1004 frames and owner stride 712. -/
def decode (n : Nat) : Label :=
  if n < 1004 then ⟨n, 0, 0⟩ else
    ⟨n % 1004, (n / 1004 - 1) % 712, (n / 1004 - 1) / 712 + 1⟩

def monoId (tree : LookupTree Nat) (owner : Nat) : Nat :=
  (tree.find owner).getD 0

def recipeFor (t : Tables) (a b : Label) : Recipe :=
  match a.tag, b.tag with
  | 0, 0 => match t.children.find (a.frame * 1004 + b.frame) with
      | some c => .child c
      | none => .identity
  | 1, 0 => .source (monoId t.source a.owner)
  | 0, 2 => .target (monoId t.target b.owner)
  | 3, 0 => .pre (monoId t.pre a.owner)
  | 0, 4 => .post (monoId t.post b.owner)
  | _, _ => .identity

def dispatchCode (t : Tables) (a b : Nat) : Recipe := recipeFor t (decode a) (decode b)

def transitionOK (t : Tables) (a b : Label) : Bool :=
  decide (a.frame < 1004) && decide (b.frame < 1004) &&
  match a.tag, b.tag with
  | 0, 0 => match t.children.find (a.frame * 1004 + b.frame) with
      | some _ => true
      | none => a.frame == b.frame
  | 1, 0 => (a.frame == b.frame) && (t.source.find a.owner).isSome
  | 0, 2 => (a.frame == b.frame) && (t.target.find b.owner).isSome
  | 3, 0 => (a.frame == b.frame) && (t.pre.find a.owner).isSome
  | 0, 4 => (a.frame == b.frame) && (t.post.find b.owner).isSome
  | _, _ => false

section Operators

variable {K M : Type*} [Semiring K] [AddCommMonoid M] [Module K M]

structure Model (K M : Type*) [Semiring K] [AddCommMonoid M] [Module K M] where
  frame : Nat → M ≃ₗ[K] M
  monomial : Nat → M ≃ₗ[K] M
  core : Nat → M ≃ₗ[K] M

def decodedOp (t : Tables) (m : Model K M) (a : Label) : M ≃ₗ[K] M :=
  match a.tag with
  | 1 => (m.frame a.frame).trans (m.monomial (monoId t.source a.owner)).symm
  | 2 => (m.frame a.frame).trans (m.monomial (monoId t.target a.owner)).symm
  | 3 => (m.frame a.frame).trans (m.monomial (monoId t.pre a.owner))
  | 4 => (m.frame a.frame).trans (m.monomial (monoId t.post a.owner)).symm
  | _ => m.frame a.frame

def tagOp (t : Tables) (m : Model K M) (a : Nat) : M ≃ₗ[K] M := decodedOp t m (decode a)

/-- This executes the stored descriptor; it is not defined by endpoint labels. -/
def evalRecipe (m : Model K M) : Recipe → M → M
  | .child c, v => m.monomial c.left (m.core c.rank (m.monomial c.right v))
  | .source id, v => m.monomial id v
  | .target id, v => (m.monomial id).symm v
  | .pre id, v => (m.monomial id).symm v
  | .post id, v => (m.monomial id).symm v
  | .identity, v => v

def dispatch (t : Tables) (m : Model K M) (a b : Nat) : M → M :=
  evalRecipe m (dispatchCode t a b)

/-- Exactly the child records in the used-only table are assumed exact.
The frame bounds make the pair key injective. Monomials and cores remain
independent operators; their source semantics are not proved here. -/
def ChildExact (t : Tables) (m : Model K M) : Prop :=
  ∀ a b, a < 1004 → b < 1004 → ∀ c,
    t.children.find (a * 1004 + b) = some c → ∀ v,
      m.monomial c.left (m.core c.rank (m.monomial c.right v)) =
        m.frame b ((m.frame a).symm v)

theorem decoded_exact (t : Tables) (m : Model K M) (hc : ChildExact t m)
    (a b : Label) (h : transitionOK t a b = true) (v : M) :
    evalRecipe m (recipeFor t a b) v = decodedOp t m b ((decodedOp t m a).symm v) := by
  rcases a with ⟨af, ao, ak⟩
  rcases b with ⟨bf, bo, bt⟩
  have hbounds : af < 1004 ∧ bf < 1004 := by
    simpa only [transitionOK, Bool.and_eq_true, decide_eq_true_eq] using
      (Bool.and_eq_true_iff.mp h).1
  rcases ak with _ | _ | _ | _ | _ | ak <;>
    rcases bt with _ | _ | _ | _ | _ | bt <;>
    simp_all [transitionOK, recipeFor, decodedOp, evalRecipe, LinearEquiv.trans_apply]
  cases he : t.children.find (af * 1004 + bf) with
  | none => simp_all
  | some c => simpa only [he] using hc af bf hbounds.1 hbounds.2 c he v

theorem dispatch_exact (t : Tables) (m : Model K M) (hc : ChildExact t m)
    (a b : Nat) (h : transitionOK t (decode a) (decode b) = true) (v : M) :
    dispatch t m a b v = tagOp t m b ((tagOp t m a).symm v) :=
  decoded_exact t m hc (decode a) (decode b) h v

end Operators

abbrev Reg := Fin (2^10)
abbrev Raw := Nat × Nat × Nat × Recipe

def rawRelabels (t : Tables) (es : List (LemmaG.Event Reg Nat Rat)) : List Raw :=
  es.filterMap fun e => match e with
    | .relabel r a b => some (r.val, a, b, dispatchCode t a b)
    | _ => none

def eventOK (t : Tables) : LemmaG.Event Reg Nat Rat → Bool
  | .relabel _ a b => transitionOK t (decode a) (decode b)
  | _ => true

def checkBlock (t : Tables) (es : List (LemmaG.Event Reg Nat Rat)) (raw : List Raw) : Bool :=
  es.all (eventOK t) && decide (rawRelabels t es = raw)

theorem block_raw_binding (t : Tables) (es : List (LemmaG.Event Reg Nat Rat))
    (raw : List Raw) (h : checkBlock t es raw = true) : rawRelabels t es = raw := by
  exact of_decide_eq_true (Bool.and_eq_true_iff.mp h).2

theorem rawRelabels_flatten (t : Tables) (blocks : List (List (LemmaG.Event Reg Nat Rat))) :
    rawRelabels t blocks.flatten = (blocks.map (rawRelabels t)).flatten := by
  induction blocks with
  | nil => rfl
  | cons es rest ih => simpa [rawRelabels, List.filterMap_append] using congrArg (rawRelabels t es ++ ·) ih

theorem block_recipes_exact {M : Type*} [AddCommMonoid M] [Module Rat M]
    (t : Tables) (m : Model Rat M) (hc : ChildExact t m)
    (es : List (LemmaG.Event Reg Nat Rat)) (raw : List Raw)
    (h : checkBlock t es raw = true) :
    LemmaG.Stream.RecipesExact (tagOp t m) (dispatch t m) es := by
  have hall : es.all (eventOK t) = true := (Bool.and_eq_true_iff.mp h).1
  intro r a b he v
  exact dispatch_exact t m hc a b ((List.all_eq_true.mp hall) _ he) v

theorem recipes_flatten {ι Λ K M : Type*} [DecidableEq ι] [Semiring K]
    [AddCommMonoid M] [Module K M]
    (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (blocks : List (List (LemmaG.Event ι Λ K)))
    (h : ∀ es ∈ blocks, LemmaG.Stream.RecipesExact T rec es) :
    LemmaG.Stream.RecipesExact T rec blocks.flatten := by
  intro r a b he v
  obtain ⟨es, hes, he⟩ := List.mem_flatten.mp he
  exact h es hes r a b he v

end K8RecipeDispatch
