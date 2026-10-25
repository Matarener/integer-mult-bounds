/-
Copyright (c) 2026 Sagar Thakrar. All rights reserved.
Released under the Apache 2.0 license, as described in the repository LICENSE.
Prepared with OpenAI Codex assistance. This is not independent human review.
Uses DreamingOfClouds's LemmaG semantics, Nick Petalas's PR2944 complete typed
word and source-bound labels, and the exact selected source lineage including
Hanson Sun's PR1611 binding. All used child equations remain explicit premises.
-/

import RecipeChecks12

namespace K8.RecipeBinding
open K8RecipeDispatch
set_option maxRecDepth 10000
set_option maxHeartbeats 0

def rawBlocks : List (List Raw) := [raw0, raw1, raw2, raw3, raw4, raw5, raw6, raw7, raw8, raw9, raw10, raw11, raw12, raw13, raw14, raw15, raw16, raw17, raw18, raw19, raw20, raw21, raw22, raw23, raw24, raw25, raw26, raw27, raw28, raw29, raw30, raw31, raw32, raw33, raw34, raw35, raw36, raw37, raw38, raw39, raw40, raw41, raw42, raw43, raw44, raw45, raw46, raw47, raw48, raw49, raw50, raw51, raw52, raw53, raw54, raw55, raw56, raw57, raw58, raw59, raw60, raw61, raw62, raw63, raw64, raw65, raw66, raw67, raw68, raw69, raw70, raw71, raw72, raw73, raw74, raw75, raw76, raw77, raw78, raw79, raw80, raw81, raw82, raw83, raw84, raw85, raw86, raw87, raw88, raw89, raw90, raw91, raw92, raw93, raw94, raw95, raw96]

theorem used_child_count : tables.children.size = 2888 := by decide +kernel

theorem forward_dispatch_bound :
    rawRelabels tables K8.Forward.events = rawBlocks.flatten := by
  change rawRelabels tables K8.Forward.blocks.flatten = rawBlocks.flatten
  rw [rawRelabels_flatten]
  have hm : K8.Forward.blocks.map (rawRelabels tables) = rawBlocks := by
    simp only [K8.Forward.blocks, rawBlocks, List.map_cons, List.map_nil,
      block_raw_binding tables K8.Forward.block0 raw0 check0,
      block_raw_binding tables K8.Forward.block1 raw1 check1,
      block_raw_binding tables K8.Forward.block2 raw2 check2,
      block_raw_binding tables K8.Forward.block3 raw3 check3,
      block_raw_binding tables K8.Forward.block4 raw4 check4,
      block_raw_binding tables K8.Forward.block5 raw5 check5,
      block_raw_binding tables K8.Forward.block6 raw6 check6,
      block_raw_binding tables K8.Forward.block7 raw7 check7,
      block_raw_binding tables K8.Forward.block8 raw8 check8,
      block_raw_binding tables K8.Forward.block9 raw9 check9,
      block_raw_binding tables K8.Forward.block10 raw10 check10,
      block_raw_binding tables K8.Forward.block11 raw11 check11,
      block_raw_binding tables K8.Forward.block12 raw12 check12,
      block_raw_binding tables K8.Forward.block13 raw13 check13,
      block_raw_binding tables K8.Forward.block14 raw14 check14,
      block_raw_binding tables K8.Forward.block15 raw15 check15,
      block_raw_binding tables K8.Forward.block16 raw16 check16,
      block_raw_binding tables K8.Forward.block17 raw17 check17,
      block_raw_binding tables K8.Forward.block18 raw18 check18,
      block_raw_binding tables K8.Forward.block19 raw19 check19,
      block_raw_binding tables K8.Forward.block20 raw20 check20,
      block_raw_binding tables K8.Forward.block21 raw21 check21,
      block_raw_binding tables K8.Forward.block22 raw22 check22,
      block_raw_binding tables K8.Forward.block23 raw23 check23,
      block_raw_binding tables K8.Forward.block24 raw24 check24,
      block_raw_binding tables K8.Forward.block25 raw25 check25,
      block_raw_binding tables K8.Forward.block26 raw26 check26,
      block_raw_binding tables K8.Forward.block27 raw27 check27,
      block_raw_binding tables K8.Forward.block28 raw28 check28,
      block_raw_binding tables K8.Forward.block29 raw29 check29,
      block_raw_binding tables K8.Forward.block30 raw30 check30,
      block_raw_binding tables K8.Forward.block31 raw31 check31,
      block_raw_binding tables K8.Forward.block32 raw32 check32,
      block_raw_binding tables K8.Forward.block33 raw33 check33,
      block_raw_binding tables K8.Forward.block34 raw34 check34,
      block_raw_binding tables K8.Forward.block35 raw35 check35,
      block_raw_binding tables K8.Forward.block36 raw36 check36,
      block_raw_binding tables K8.Forward.block37 raw37 check37,
      block_raw_binding tables K8.Forward.block38 raw38 check38,
      block_raw_binding tables K8.Forward.block39 raw39 check39,
      block_raw_binding tables K8.Forward.block40 raw40 check40,
      block_raw_binding tables K8.Forward.block41 raw41 check41,
      block_raw_binding tables K8.Forward.block42 raw42 check42,
      block_raw_binding tables K8.Forward.block43 raw43 check43,
      block_raw_binding tables K8.Forward.block44 raw44 check44,
      block_raw_binding tables K8.Forward.block45 raw45 check45,
      block_raw_binding tables K8.Forward.block46 raw46 check46,
      block_raw_binding tables K8.Forward.block47 raw47 check47,
      block_raw_binding tables K8.Forward.block48 raw48 check48,
      block_raw_binding tables K8.Forward.block49 raw49 check49,
      block_raw_binding tables K8.Forward.block50 raw50 check50,
      block_raw_binding tables K8.Forward.block51 raw51 check51,
      block_raw_binding tables K8.Forward.block52 raw52 check52,
      block_raw_binding tables K8.Forward.block53 raw53 check53,
      block_raw_binding tables K8.Forward.block54 raw54 check54,
      block_raw_binding tables K8.Forward.block55 raw55 check55,
      block_raw_binding tables K8.Forward.block56 raw56 check56,
      block_raw_binding tables K8.Forward.block57 raw57 check57,
      block_raw_binding tables K8.Forward.block58 raw58 check58,
      block_raw_binding tables K8.Forward.block59 raw59 check59,
      block_raw_binding tables K8.Forward.block60 raw60 check60,
      block_raw_binding tables K8.Forward.block61 raw61 check61,
      block_raw_binding tables K8.Forward.block62 raw62 check62,
      block_raw_binding tables K8.Forward.block63 raw63 check63,
      block_raw_binding tables K8.Forward.block64 raw64 check64,
      block_raw_binding tables K8.Forward.block65 raw65 check65,
      block_raw_binding tables K8.Forward.block66 raw66 check66,
      block_raw_binding tables K8.Forward.block67 raw67 check67,
      block_raw_binding tables K8.Forward.block68 raw68 check68,
      block_raw_binding tables K8.Forward.block69 raw69 check69,
      block_raw_binding tables K8.Forward.block70 raw70 check70,
      block_raw_binding tables K8.Forward.block71 raw71 check71,
      block_raw_binding tables K8.Forward.block72 raw72 check72,
      block_raw_binding tables K8.Forward.block73 raw73 check73,
      block_raw_binding tables K8.Forward.block74 raw74 check74,
      block_raw_binding tables K8.Forward.block75 raw75 check75,
      block_raw_binding tables K8.Forward.block76 raw76 check76,
      block_raw_binding tables K8.Forward.block77 raw77 check77,
      block_raw_binding tables K8.Forward.block78 raw78 check78,
      block_raw_binding tables K8.Forward.block79 raw79 check79,
      block_raw_binding tables K8.Forward.block80 raw80 check80,
      block_raw_binding tables K8.Forward.block81 raw81 check81,
      block_raw_binding tables K8.Forward.block82 raw82 check82,
      block_raw_binding tables K8.Forward.block83 raw83 check83,
      block_raw_binding tables K8.Forward.block84 raw84 check84,
      block_raw_binding tables K8.Forward.block85 raw85 check85,
      block_raw_binding tables K8.Forward.block86 raw86 check86,
      block_raw_binding tables K8.Forward.block87 raw87 check87,
      block_raw_binding tables K8.Forward.block88 raw88 check88,
      block_raw_binding tables K8.Forward.block89 raw89 check89,
      block_raw_binding tables K8.Forward.block90 raw90 check90,
      block_raw_binding tables K8.Forward.block91 raw91 check91,
      block_raw_binding tables K8.Forward.block92 raw92 check92,
      block_raw_binding tables K8.Forward.block93 raw93 check93,
      block_raw_binding tables K8.Forward.block94 raw94 check94,
      block_raw_binding tables K8.Forward.block95 raw95 check95,
      block_raw_binding tables K8.Forward.block96 raw96 check96]
  rw [hm]

theorem forward_recipes_exact {M : Type*} [AddCommMonoid M] [Module Rat M]
    (model : Model Rat M) (hc : ChildExact tables model) :
    LemmaG.Stream.RecipesExact (tagOp tables model) (dispatch tables model) K8.Forward.events := by
  apply recipes_flatten
  intro es hes
  simp only [K8.Forward.blocks, List.mem_cons, List.not_mem_nil, or_false] at hes
  rcases hes with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact block_recipes_exact tables model hc _ _ check0
  · exact block_recipes_exact tables model hc _ _ check1
  · exact block_recipes_exact tables model hc _ _ check2
  · exact block_recipes_exact tables model hc _ _ check3
  · exact block_recipes_exact tables model hc _ _ check4
  · exact block_recipes_exact tables model hc _ _ check5
  · exact block_recipes_exact tables model hc _ _ check6
  · exact block_recipes_exact tables model hc _ _ check7
  · exact block_recipes_exact tables model hc _ _ check8
  · exact block_recipes_exact tables model hc _ _ check9
  · exact block_recipes_exact tables model hc _ _ check10
  · exact block_recipes_exact tables model hc _ _ check11
  · exact block_recipes_exact tables model hc _ _ check12
  · exact block_recipes_exact tables model hc _ _ check13
  · exact block_recipes_exact tables model hc _ _ check14
  · exact block_recipes_exact tables model hc _ _ check15
  · exact block_recipes_exact tables model hc _ _ check16
  · exact block_recipes_exact tables model hc _ _ check17
  · exact block_recipes_exact tables model hc _ _ check18
  · exact block_recipes_exact tables model hc _ _ check19
  · exact block_recipes_exact tables model hc _ _ check20
  · exact block_recipes_exact tables model hc _ _ check21
  · exact block_recipes_exact tables model hc _ _ check22
  · exact block_recipes_exact tables model hc _ _ check23
  · exact block_recipes_exact tables model hc _ _ check24
  · exact block_recipes_exact tables model hc _ _ check25
  · exact block_recipes_exact tables model hc _ _ check26
  · exact block_recipes_exact tables model hc _ _ check27
  · exact block_recipes_exact tables model hc _ _ check28
  · exact block_recipes_exact tables model hc _ _ check29
  · exact block_recipes_exact tables model hc _ _ check30
  · exact block_recipes_exact tables model hc _ _ check31
  · exact block_recipes_exact tables model hc _ _ check32
  · exact block_recipes_exact tables model hc _ _ check33
  · exact block_recipes_exact tables model hc _ _ check34
  · exact block_recipes_exact tables model hc _ _ check35
  · exact block_recipes_exact tables model hc _ _ check36
  · exact block_recipes_exact tables model hc _ _ check37
  · exact block_recipes_exact tables model hc _ _ check38
  · exact block_recipes_exact tables model hc _ _ check39
  · exact block_recipes_exact tables model hc _ _ check40
  · exact block_recipes_exact tables model hc _ _ check41
  · exact block_recipes_exact tables model hc _ _ check42
  · exact block_recipes_exact tables model hc _ _ check43
  · exact block_recipes_exact tables model hc _ _ check44
  · exact block_recipes_exact tables model hc _ _ check45
  · exact block_recipes_exact tables model hc _ _ check46
  · exact block_recipes_exact tables model hc _ _ check47
  · exact block_recipes_exact tables model hc _ _ check48
  · exact block_recipes_exact tables model hc _ _ check49
  · exact block_recipes_exact tables model hc _ _ check50
  · exact block_recipes_exact tables model hc _ _ check51
  · exact block_recipes_exact tables model hc _ _ check52
  · exact block_recipes_exact tables model hc _ _ check53
  · exact block_recipes_exact tables model hc _ _ check54
  · exact block_recipes_exact tables model hc _ _ check55
  · exact block_recipes_exact tables model hc _ _ check56
  · exact block_recipes_exact tables model hc _ _ check57
  · exact block_recipes_exact tables model hc _ _ check58
  · exact block_recipes_exact tables model hc _ _ check59
  · exact block_recipes_exact tables model hc _ _ check60
  · exact block_recipes_exact tables model hc _ _ check61
  · exact block_recipes_exact tables model hc _ _ check62
  · exact block_recipes_exact tables model hc _ _ check63
  · exact block_recipes_exact tables model hc _ _ check64
  · exact block_recipes_exact tables model hc _ _ check65
  · exact block_recipes_exact tables model hc _ _ check66
  · exact block_recipes_exact tables model hc _ _ check67
  · exact block_recipes_exact tables model hc _ _ check68
  · exact block_recipes_exact tables model hc _ _ check69
  · exact block_recipes_exact tables model hc _ _ check70
  · exact block_recipes_exact tables model hc _ _ check71
  · exact block_recipes_exact tables model hc _ _ check72
  · exact block_recipes_exact tables model hc _ _ check73
  · exact block_recipes_exact tables model hc _ _ check74
  · exact block_recipes_exact tables model hc _ _ check75
  · exact block_recipes_exact tables model hc _ _ check76
  · exact block_recipes_exact tables model hc _ _ check77
  · exact block_recipes_exact tables model hc _ _ check78
  · exact block_recipes_exact tables model hc _ _ check79
  · exact block_recipes_exact tables model hc _ _ check80
  · exact block_recipes_exact tables model hc _ _ check81
  · exact block_recipes_exact tables model hc _ _ check82
  · exact block_recipes_exact tables model hc _ _ check83
  · exact block_recipes_exact tables model hc _ _ check84
  · exact block_recipes_exact tables model hc _ _ check85
  · exact block_recipes_exact tables model hc _ _ check86
  · exact block_recipes_exact tables model hc _ _ check87
  · exact block_recipes_exact tables model hc _ _ check88
  · exact block_recipes_exact tables model hc _ _ check89
  · exact block_recipes_exact tables model hc _ _ check90
  · exact block_recipes_exact tables model hc _ _ check91
  · exact block_recipes_exact tables model hc _ _ check92
  · exact block_recipes_exact tables model hc _ _ check93
  · exact block_recipes_exact tables model hc _ _ check94
  · exact block_recipes_exact tables model hc _ _ check95
  · exact block_recipes_exact tables model hc _ _ check96

end K8.RecipeBinding
