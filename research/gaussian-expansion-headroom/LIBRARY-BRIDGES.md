# Inspected library bridges and adaptations

This is a retrieval and mathematical-use record, not a claim that the new
result was Lean checked. Local paths and SHA-256 values are stored privately
and in LIBRARY-BRIDGES.json; public entries use portable module names.
Mathlib source revision: `db584cd6d46c92f209a44c0f1c829460d327499d`.
All definitions and hypotheses were inspected before use.

| Concept | Inspected source / declaration | Exact use and limit |
|---|---|---|
| Gaussian Fourier duality | `Mathlib.Analysis.SpecialFunctions.Gaussian.FourierTransform`, `fourierIntegral_gaussian`, `fourier_gaussian_pi'` | Supplies the Fourier transform of the normalized real Gaussian. We specialize to positive real width; no complex branch ambiguity remains. Sébastien Gouëzel's source and classical Gaussian analysis are credited. |
| Periodization on the integer lattice | `Mathlib.Analysis.Fourier.PoissonSummation`, `Real.tsum_eq_tsum_fourier` | Turns the shifted positive row sum into an absolutely convergent Fourier series. Gaussian decay verifies both compact-uniform summability and sampled Fourier summability. David Loeffler's source is credited. |
| Gaussian theta transformation | `Mathlib.Analysis.SpecialFunctions.Gaussian.PoissonSummation`, `Complex.tsum_exp_neg_quadratic` | A second explicit Gaussian specialization of Poisson with positive real quadratic part. It confirms the width/reciprocal-width convention used in PROOF.md; it is an alternative derivation, not an independent new mechanism. |
| Geometric theta tail | `Mathlib.NumberTheory.ModularForms.JacobiTheta.OneVariable`, `norm_jacobiTheta_sub_one_le` | Uses n² ≥ n to bound the dual tail by q/(1−q). We add the elementary rational certificate e³ > 20 and derive b(u), yielding a 0.6 contract. This is a source-bound application of classical estimates. |
| Positive Gaussian majorants with unit-modulus phases | `ErdosProblems.Erdos230.GaussianPoisson`, `norm_e`, `norm_cutoffChirpTerm`, `tsum_gaussianChirpAtom_eq_tsum_thetaAliasAtom` | Boris Alexeev/Codex's source shows how to separate phase from Gaussian mass. Here arbitrary complex input phases are bounded by the triangle inequality and the positive row mass. Their smoothed chirp theorem is not asserted to equal this expansion map; the specialized proof is written explicitly. |
| Tensor packing and axis isolation | `Mathproof.Meta.RobustRealTIRecovery20261006`, `indexEquiv`, `pack_index`; `Mathproof.External.IntegerMultBounds20261008.Matrix.GaussianTensorExecution`, `cubeMap_zip` | Motivates explicit coordinate enumeration and lifting scalar facts to every spectator line. We prove rectangular row-major completeness directly. The Gaussian-integer C tensor is a different map and is not a real-Gaussian norm theorem. |
| Ordered tensor error telescoping | `Mathproof.Meta.RobustRealTITensor20261006`, `three_mode_telescope` | Motivates adding/subtracting one mode at a time. That theorem assumes orthogonal maps and uses Frobenius norms; these hypotheses do not apply here. PROOF.md instead proves a positive rectangular sup-norm recurrence retaining all contraction factors. |
| Arbitrary exterior frames | `Mathproof.Computability.MultitapeFrameRule20261014`, `FootprintedRuns.frame`; `Mathproof.Computability.MultitapeLocality20261014`, `act_preserves_unscanned` | Motivates explicit disjoint read/write sets in the host window adapter. We prove the host frame property directly. A physical application still requires an actual run/footprint; no tape theorem is invoked on a dictionary. |

The Mathlib Gaussian/theta declarations were also queried in the authoritative
shared DAG. The returned rows have snapshot `source-catalog`, identifiers
`source:224908`, `source:224954`, `source:327247` and null `type_node`/`axioms`.
They are source evidence, not checked typed ports. Historical environments
were not combined or imported into a new Lean environment.

The complete bounded search packet includes 6 initial Mathproof queries
(70 results per query at most), followed by 9 theta/Fourier/rounding/tensor
queries (40 results per query at most), and 3 DAG name lookups (at most
3 hits each). Some source queries return no hits. Limits and lexical
ranking mean that unreturned results may exist. We inspected relevant
actual source text and rejected unrelated permutation-padding, F₂-only
and Euclidean-energy facts as substitutes for this sup-norm argument.

The project already contains Gaussian periodization, norm accounting and
inward rounding. Neither this search nor a missing PR-body match proves
that a concept has never been applied. The useful deliverable is the
complete specialized sufficient contract and executable reference, with
the above attribution and scope limits.
