import Mathlib.Data.Rat.BigOperators
import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Fin.VecNotation
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases

/-! Certificate transfer extracted, with unchanged proof bodies, from Dugongue's
MathProof IntegerKappaMomentTransfer20261015.lean. Substantial OpenAI Codex
assistance. Apache-2.0. This proves only the stated conditional real-weight
admission, not the logarithm/exponential bounds or the multiplication theorem. -/

namespace IntegerMultBounds.MomentTransfer
open scoped BigOperators
variable {ι : Type*}
noncomputable def weighted (s : Finset ι) (c w : ι → ℝ) : ℝ :=
  ∑ i ∈ s, c i * w i

theorem weighted_mono_weights (s : Finset ι) (c u v : ι → ℝ)
    (hc : ∀ i ∈ s, 0 ≤ c i) (huv : ∀ i ∈ s, u i ≤ v i) :
    weighted s c u ≤ weighted s c v := by
  exact Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_left (huv i hi) (hc i hi)

theorem rational_upper_certificate (s : Finset ι) (c upper : ι → ℚ) (w : ι → ℝ)
    (budget : ℚ) (hc : ∀ i ∈ s, 0 ≤ c i)
    (hupper : ∀ i ∈ s, w i ≤ (upper i : ℝ))
    (hcertificate : (∑ i ∈ s, c i * upper i) < budget) :
    weighted s (fun i => (c i : ℝ)) w < (budget : ℝ) := by
  have h := weighted_mono_weights s (fun i => (c i : ℝ)) w (fun i => (upper i : ℝ))
    (fun i hi => by exact_mod_cast hc i hi) hupper
  have hcast : weighted s (fun i => (c i : ℝ)) (fun i => (upper i : ℝ)) < (budget : ℝ) := by
    change (∑ i ∈ s, (c i : ℝ) * (upper i : ℝ)) < (budget : ℝ)
    exact_mod_cast hcertificate
  exact h.trans_lt hcast

/-- Dividing by a positive budget connects paid sums to moment < 1. -/
theorem normalized_admission (cost budget : ℝ) (hbudget : 0 < budget) :
    cost / budget < 1 ↔ cost < budget := by
  rw [div_lt_one hbudget]

end IntegerMultBounds.MomentTransfer

namespace Staged544Certificate
open scoped BigOperators
open IntegerMultBounds.MomentTransfer
def coefficient : Fin 7 → ℚ := ![7989840, 4698000, 2247264, 1321920, 345600, 207360, 6621696]
def upper : Fin 7 → ℚ := ![(13507731094523807383566475123716226262821080735013659937896950134837434477991620304205855756237792292311750260853556038594859174301966598591383088728416915 / 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096), (13491537669919590444070783937941464752554609528295312364120075762630530816279756695957039929900401848255443706168261710262397613766253017942706209006837203 / 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096), (13482074124629314266984853423762132196619008555772618820195884044083409682596544977661357694011530838439984600059835445921466208152729089541843752149002581 / 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096), (13475363658420252292726653566578878147646435678341933346136213519761447932248379861556076157777577929289644834201241414284156073003775118317955380101246497 / 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096), (13470160916654698189586785076891163906547046740939775262388900537080309894800792109484478840209598056770772511656870622915958070296415813340584899035271269 / 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096), (13459209036752850346611399332698520957888451347969204958854153028399849634185585362065661352009007298720371270575038487256688169510878983253236696889686637 / 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096), (13417539623722925629684767919185678866775428178768770102551675998974478591678481675509425432160414596693798883228869483043188943937259390146824381395561924 / 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096)]

theorem coefficient_nonnegative (i : Fin 7) : 0 ≤ coefficient i := by
  fin_cases i <;> norm_num [coefficient]

set_option maxRecDepth 4096 in
set_option maxHeartbeats 2000000 in
theorem exact_certificate : (∑ i : Fin 7, coefficient i * upper i) < (73 * (896 * 360) : ℚ) := by
  norm_num [Fin.sum_univ_succ, coefficient, upper]

/-- All seven actual real weights below the published rational bounds suffice. -/
theorem admission (w : Fin 7 → ℝ) (hw : ∀ i, w i ≤ (upper i : ℝ)) :
    (∑ i : Fin 7, (coefficient i : ℝ) * w i) / (73 * (896 * 360)) < 1 := by
  apply (normalized_admission _ _ (by norm_num)).2
  have h := rational_upper_certificate Finset.univ coefficient upper w
    (73 * (896 * 360)) (fun i _ => coefficient_nonnegative i)
    (fun i _ => hw i) exact_certificate
  simpa [weighted] using h

end Staged544Certificate

#print axioms Staged544Certificate.exact_certificate
#print axioms Staged544Certificate.admission
