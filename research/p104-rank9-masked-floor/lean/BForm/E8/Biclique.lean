import BForm.E8.BicliqueDefs
import BForm.E8.BicliqueSound
import BForm.E8.BicliqueC0
import BForm.E8.BicliqueC1
import BForm.E8.BicliqueC2
import BForm.E8.BicliqueC3

/-!
# BicliqueFact for P104: no 13 ports are non-orthogonal to 5 ports

A depth-first search with pruning (`go`) over 5-subsets of the ports in increasing order, keeping the list of
ports non-orthogonal to all chosen ones and cutting a branch as soon as fewer than 13 remain (about 1.1 million
calls, 18 million filter steps; the same search in Python: Internal rank9-p104-2026-10-29/t3scan).  The fact holds
for all 120 lines of E8 (at most 11 common lines), so no frame of P104 is special; no hand proof is known.
-/

namespace BForm.E8

theorem bic_true : go 5 (List.range 104) NBL = true := by
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, beq_iff_eq] at hb
  rw [go_succ_iff]
  intro i hi
  rw [hb.1] at hi
  interval_cases i
  exacts [bic_0, bic_1, bic_2, bic_3, bic_4, bic_5, bic_6, bic_7, bic_8, bic_9, bic_10, bic_11, bic_12, bic_13, bic_14, bic_15, bic_16, bic_17, bic_18, bic_19, bic_20, bic_21, bic_22, bic_23, bic_24, bic_25, bic_26, bic_27, bic_28, bic_29, bic_30, bic_31, bic_32, bic_33, bic_34, bic_35, bic_36, bic_37, bic_38, bic_39, bic_40, bic_41, bic_42, bic_43, bic_44, bic_45, bic_46, bic_47, bic_48, bic_49, bic_50, bic_51, bic_52, bic_53, bic_54, bic_55, bic_56, bic_57, bic_58, bic_59, bic_60, bic_61, bic_62, bic_63, bic_64, bic_65, bic_66, bic_67, bic_68, bic_69, bic_70, bic_71, bic_72, bic_73, bic_74, bic_75, bic_76, bic_77, bic_78, bic_79, bic_80, bic_81, bic_82, bic_83, bic_84, bic_85, bic_86, bic_87, bic_88, bic_89, bic_90, bic_91, bic_92, bic_93, bic_94, bic_95, bic_96, bic_97, bic_98, bic_99, bic_100, bic_101, bic_102, bic_103, by rw [List.drop_eq_nil_of_le (by rw [hb.1])]; rfl]

/-- **BicliqueFact for P104.** -/
theorem biclique_P104 {K : Type*} [Field K] [CharZero K] : BForm.BicliqueFact (rK K) := biclique_of_go bic_true

end BForm.E8
