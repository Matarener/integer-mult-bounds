import BForm.E8.Labels
import BForm.Main

/-!
# BicliqueFact for P104: no 13 ports are non-orthogonal to 5 ports

A depth-first search with pruning (`go`) over 5-subsets of the ports in increasing order, keeping the list of
ports non-orthogonal to all chosen ones and cutting a branch as soon as fewer than 13 remain (about 1.1 million
calls, 18 million filter steps; the same search in Python: Internal rank9-p104-2026-10-29/t3scan).  The fact holds
for all 120 lines of E8 (at most 11 common lines), so no frame of P104 is special; no hand proof is known.
-/

namespace BForm.E8

open Matrix Finset

set_option linter.unusedSectionVars false

/-- `r8` dot product over 8 coordinates -/
def d8 (a b : ℕ) : ℤ := ((List.range 8).map fun k => (r8 a).getD k 0 * (r8 b).getD k 0).sum

/-- bit `u` of `NBL[s]`: ports `s` and `u` are not orthogonal -/
def NBL : List ℕ := [
  38452902102132865683614087231, 595486624826015653042466308191, 4478980680042112317780717226143, 6506951268138746105719132324383,
  13013863852497094124287137293343, 39537911844640888639033720801, 596650214746798734619537819618, 4479991945309624819121631023076,
  15930862336957249211861814515680, 6507512813001366927611985201128, 13013825770153187536854037178352, 4512410799956825900286382209189,
  15958484173953522937487332784417, 13012665501238143974226722438193, 4995169329281254940123645593798, 16366966301002542492255499571522,
  6785469937106367157672256455242, 12975489214266924583894400623698, 8450577861066082016805576854156, 12295699392696749809951666180872,
  8661426518374995430516526331152, 19520796083745840460987912627736, 39574196147512017012568080417, 596685299568583214130026788930,
  4480024631169236000929115517060, 15930890224892513798450118617344, 6507531105087938323331360684552, 13013824870542372550547797302288,
  631424692048595676110738163587, 15958511462148244199632422786753, 6525558307040519668344397415881, 4995200215919236148620001048358,
  6785486429971308580074211589546, 12975486515434479624258057018290, 19141292189396784335271797925476, 12422203490290982482765582799732,
  12295708688675171339238239792360, 8661416622656030577571529050864, 19520776592178182416761773677048, 632512122003926292325079974012,
  4513377991377953791980324227258, 6526043691937688019929134187062, 13012549759577426599137673864238, 16367856168394882509709099968861,
  6786050395046751944110775548501, 12975450853303395526204994755661, 19142003643422218974539158856091, 8451003595391022555869052580499,
  12422015503506627065681858368651, 12295970422295712821468530895639, 8661078729070042961832165330191, 19520138884988929409977031908871,
  5026156880690689522404496527128, 16393002130035059947289018930844, 6801602321383753330313451865492, 12971814709032174689903625249676,
  8464234384154507476662606007634, 12416058221661728003820687567690, 12304404193407623135013905257686, 8650324429572922041013869310670,
  19499790550186933428433788658118, 19499034201650630542532255213113, 8649887313672223755607326684465, 12304605541782730446557407761193,
  12415780720609073273070024240309, 8464595347336801687042482670253, 19165508663204717998111398762917, 12971694388645917071701363795059,
  6802120464845225157280415154795, 16393839505255312548899701690723, 38684445636047965935108064, 1199857695380401788624566303,
  38415732360148894567744128990, 595450669018286535508129234877, 4478947153338843422358844979067, 15929972305284569190958564339455,
  6506932304787449638747964112375, 13013864307858798034355414227951, 1237641349609842369198295039, 38453216144106672922608810046,
  595487553061700989391200305245, 4478982837901171227275242522779, 15930005590884723697754786271519, 6506960792463257549734402654743,
  13013883199685912754010044113935, 39576309411124770154790010817, 4480069058930690107552443944804, 15931016858513423922695578883808,
  6507822153290323146380178949608, 13014444746909712475875792004080, 632627873404387823441267652707, 4514886427130086049882738815141,
  15963435717885400947717255506209, 6535443995008756681873910741545, 13032472553322929152063194668081, 5034783167300179311075759982790,
  16446194256795219469238452048194, 6943926131484350748078921138762, 13292401885038881270239352448082, 19775093612185913598796696967556,
  9718228348758559456526571489932, 14957509826855026502603663371412, 17366301720061551266595014546184, 18802631397445226802013553734928]

def nbOK : Bool := NBL.length == 104 &&
  (List.range 104).all fun s => (List.range 104).all fun u => (NBL.getD s 0).testBit u == (d8 s u != 0)

set_option maxRecDepth 100000 in
theorem nbOK_true : nbOK = true := by decide +kernel

/-- `go k C L`: no choice of `k ≥ 1` masks from `L` (in order) leaves `13` elements of `C` in all of them -/
def go : ℕ → List ℕ → List ℕ → Bool
  | 0, _, _ => true
  | _ + 1, _, [] => true
  | k + 1, C, m :: ms =>
    (decide ((C.filter fun u => m.testBit u).length < 13) || (k != 0 && go k (C.filter fun u => m.testBit u) ms)) &&
      go (k + 1) C ms

set_option maxRecDepth 100000 in
theorem bic_true : go 5 (List.range 104) NBL = true := by decide +kernel

theorem go_sound : ∀ (L : List ℕ) (k : ℕ) (C : List ℕ), go (k + 1) C L = true → ∀ l : List ℕ, l.Sublist L →
    l.length = k + 1 → (C.filter fun u => l.all fun m => m.testBit u).length < 13 := by
  intro L
  induction L with
  | nil =>
    intro k C _ l hl hlen
    rw [List.sublist_nil.mp hl] at hlen
    simp at hlen
  | cons m ms ih =>
    intro k C hg l hl hlen
    simp only [go, Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq] at hg
    obtain ⟨hA, hB⟩ := hg
    cases hl with
    | cons _ h => exact ih k C hB l h hlen
    | cons₂ _ h =>
      rename_i l'
      have hf : (C.filter fun u => (m :: l').all fun m => m.testBit u) =
          (C.filter fun u => m.testBit u).filter fun u => l'.all fun m => m.testBit u := by
        rw [List.filter_filter]
        congr 1
        funext u
        simp only [List.all_cons, Bool.and_comm]
      rw [hf]
      simp only [List.length_cons, add_left_inj] at hlen
      rcases hA with hA | ⟨hk, hA⟩
      · exact lt_of_le_of_lt (List.length_filter_le _ _) hA
      · obtain ⟨k', rfl⟩ : ∃ k', k = k' + 1 := ⟨k - 1, by omega⟩
        exact ih k' _ hA l' h hlen

theorem rK_d8 {K : Type*} [Field K] (a b : Fin 104) : rK K a ⬝ᵥ rK K b = ((d8 a b : ℤ) : K) := by
  unfold d8
  rw [sum_range_fin]
  simp only [dotProduct, rK, Int.cast_sum, Int.cast_mul]

theorem nb_bit {K : Type*} [Field K] [CharZero K] {u s : Fin 104} (h : ¬ BForm.Orth (rK K) u s) :
    (NBL.getD s 0).testBit u = true := by
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, all_range, beq_iff_eq] at hb
  rw [hb.2 s s.2 u u.2]
  have hne : rK K u ⬝ᵥ rK K s ≠ 0 := h
  rw [dotProduct_comm, rK_d8] at hne
  have : d8 s u ≠ 0 := fun e => hne (by rw [e]; simp)
  simpa using this

theorem self_nonorth {K : Type*} [Field K] [CharZero K] (s : Fin 104) : ¬ BForm.Orth (rK K) s s := by
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, all_range, beq_iff_eq] at hb
  intro h
  have e : rK K s ⬝ᵥ rK K s = 0 := h
  rw [rK_d8] at e
  have hd : d8 s s = 0 := by exact_mod_cast e
  have : d8 s s ≠ 0 := by
    have := (List.all_eq_true.mp (show (List.range 104).all (fun s => d8 s s != 0) = true by decide +kernel)) s
      (List.mem_range.mpr s.2)
    simpa using this
  exact this hd

/-- **BicliqueFact for P104.** -/
theorem biclique_P104 {K : Type*} [Field K] [CharZero K] : BForm.BicliqueFact (rK K) := by
  intro A B hAB hA
  by_contra hB
  rw [not_le] at hB
  obtain ⟨T, hTB, hT⟩ := Finset.exists_subset_card_eq (show 5 ≤ B.card by omega)
  set l : List ℕ := (T.map Fin.valEmbedding).sort (· ≤ ·) with hl
  have hlen : l.length = 5 := by rw [hl, Finset.length_sort, Finset.card_map, hT]
  have hlt : ∀ x ∈ l, x < 104 := by
    intro x hx
    rw [hl, Finset.mem_sort, Finset.mem_map] at hx
    obtain ⟨y, -, rfl⟩ := hx
    exact y.2
  have hsub : l.Sublist (List.range 104) := by
    apply List.sublist_of_subperm_of_sorted (r := (· ≤ ·)) _ (Finset.sort_sorted _ _)
      ((List.pairwise_lt_range 104).imp le_of_lt)
    exact List.subperm_of_subset (Finset.sort_nodup _ _) fun x hx => List.mem_range.mpr (hlt x hx)
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, beq_iff_eq] at hb
  have hNB : NBL = (List.range 104).map fun i => NBL.getD i 0 := by
    have h := list_eq_map_range NBL 0
    rw [hb.1] at h
    exact h
  have hs' : (l.map fun i => NBL.getD i 0).Sublist NBL := by
    have := hsub.map (fun i => NBL.getD i 0)
    rwa [← hNB] at this
  have hgo := go_sound NBL 4 _ bic_true _ hs' (by simp [hlen])
  apply absurd hgo
  rw [not_lt]
  calc 13 ≤ A.card := hA
    _ = (A.map Fin.valEmbedding).card := (Finset.card_map _).symm
    _ ≤ ((List.range 104).filter fun u => (l.map fun i => NBL.getD i 0).all fun m => m.testBit u).toFinset.card := by
        apply Finset.card_le_card
        intro x hx
        rw [Finset.mem_map] at hx
        obtain ⟨a, ha, rfl⟩ := hx
        rw [List.mem_toFinset, List.mem_filter]
        refine ⟨List.mem_range.mpr a.2, ?_⟩
        rw [List.all_eq_true]
        intro m hm
        rw [List.mem_map] at hm
        obtain ⟨x, hx, rfl⟩ := hm
        rw [hl, Finset.mem_sort, Finset.mem_map] at hx
        obtain ⟨s, hs, rfl⟩ := hx
        show (NBL.getD (s : ℕ) 0).testBit (a : ℕ) = true
        by_cases e : a = s
        · subst e; exact nb_bit (K := K) (self_nonorth a)
        · exact nb_bit (K := K) (hAB a ha s (hTB hs) e)
    _ ≤ _ := List.toFinset_card_le _

end BForm.E8
