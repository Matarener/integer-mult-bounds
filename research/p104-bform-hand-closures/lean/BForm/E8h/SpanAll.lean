import BForm.E8h.RootSpan0
import BForm.E8h.RootSpan1
import BForm.E8h.RootSpan2
import BForm.E8h.RootSpan3
import BForm.E8h.D7Span0
import BForm.E8h.D7Span1
import BForm.E8h.D7Span2
import BForm.E8h.D7Span3

namespace BForm.E8h

theorem rootSpan_all : ∀ j < 120, rootSpanJ j = true := by
  intro j hj; interval_cases j
  exacts [rootSpan_0, rootSpan_1, rootSpan_2, rootSpan_3, rootSpan_4, rootSpan_5, rootSpan_6, rootSpan_7, rootSpan_8, rootSpan_9, rootSpan_10, rootSpan_11, rootSpan_12, rootSpan_13, rootSpan_14, rootSpan_15, rootSpan_16, rootSpan_17, rootSpan_18, rootSpan_19, rootSpan_20, rootSpan_21, rootSpan_22, rootSpan_23, rootSpan_24, rootSpan_25, rootSpan_26, rootSpan_27, rootSpan_28, rootSpan_29, rootSpan_30, rootSpan_31, rootSpan_32, rootSpan_33, rootSpan_34, rootSpan_35, rootSpan_36, rootSpan_37, rootSpan_38, rootSpan_39, rootSpan_40, rootSpan_41, rootSpan_42, rootSpan_43, rootSpan_44, rootSpan_45, rootSpan_46, rootSpan_47, rootSpan_48, rootSpan_49, rootSpan_50, rootSpan_51, rootSpan_52, rootSpan_53, rootSpan_54, rootSpan_55, rootSpan_56, rootSpan_57, rootSpan_58, rootSpan_59, rootSpan_60, rootSpan_61, rootSpan_62, rootSpan_63, rootSpan_64, rootSpan_65, rootSpan_66, rootSpan_67, rootSpan_68, rootSpan_69, rootSpan_70, rootSpan_71, rootSpan_72, rootSpan_73, rootSpan_74, rootSpan_75, rootSpan_76, rootSpan_77, rootSpan_78, rootSpan_79, rootSpan_80, rootSpan_81, rootSpan_82, rootSpan_83, rootSpan_84, rootSpan_85, rootSpan_86, rootSpan_87, rootSpan_88, rootSpan_89, rootSpan_90, rootSpan_91, rootSpan_92, rootSpan_93, rootSpan_94, rootSpan_95, rootSpan_96, rootSpan_97, rootSpan_98, rootSpan_99, rootSpan_100, rootSpan_101, rootSpan_102, rootSpan_103, rootSpan_104, rootSpan_105, rootSpan_106, rootSpan_107, rootSpan_108, rootSpan_109, rootSpan_110, rootSpan_111, rootSpan_112, rootSpan_113, rootSpan_114, rootSpan_115, rootSpan_116, rootSpan_117, rootSpan_118, rootSpan_119]

theorem d7Span_all : ∀ a < 120, d7SpanA a = true := by
  intro a ha; interval_cases a
  exacts [d7Span_0, d7Span_1, d7Span_2, d7Span_3, d7Span_4, d7Span_5, d7Span_6, d7Span_7, d7Span_8, d7Span_9, d7Span_10, d7Span_11, d7Span_12, d7Span_13, d7Span_14, d7Span_15, d7Span_16, d7Span_17, d7Span_18, d7Span_19, d7Span_20, d7Span_21, d7Span_22, d7Span_23, d7Span_24, d7Span_25, d7Span_26, d7Span_27, d7Span_28, d7Span_29, d7Span_30, d7Span_31, d7Span_32, d7Span_33, d7Span_34, d7Span_35, d7Span_36, d7Span_37, d7Span_38, d7Span_39, d7Span_40, d7Span_41, d7Span_42, d7Span_43, d7Span_44, d7Span_45, d7Span_46, d7Span_47, d7Span_48, d7Span_49, d7Span_50, d7Span_51, d7Span_52, d7Span_53, d7Span_54, d7Span_55, d7Span_56, d7Span_57, d7Span_58, d7Span_59, d7Span_60, d7Span_61, d7Span_62, d7Span_63, d7Span_64, d7Span_65, d7Span_66, d7Span_67, d7Span_68, d7Span_69, d7Span_70, d7Span_71, d7Span_72, d7Span_73, d7Span_74, d7Span_75, d7Span_76, d7Span_77, d7Span_78, d7Span_79, d7Span_80, d7Span_81, d7Span_82, d7Span_83, d7Span_84, d7Span_85, d7Span_86, d7Span_87, d7Span_88, d7Span_89, d7Span_90, d7Span_91, d7Span_92, d7Span_93, d7Span_94, d7Span_95, d7Span_96, d7Span_97, d7Span_98, d7Span_99, d7Span_100, d7Span_101, d7Span_102, d7Span_103, d7Span_104, d7Span_105, d7Span_106, d7Span_107, d7Span_108, d7Span_109, d7Span_110, d7Span_111, d7Span_112, d7Span_113, d7Span_114, d7Span_115, d7Span_116, d7Span_117, d7Span_118, d7Span_119]

end BForm.E8h
