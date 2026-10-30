# Beatty-run Gaussian inversion and coded convolution

Four connected informal mathematical notes for a stronger native Word RAM route. Dugongue, with substantial OpenAI Codex assistance from four workers. The collection consists entirely of mathematical statements, proofs, source attribution and precise research questions. No experiments, numerical searches, executable verifiers, Lean formalizations or external searches were used to establish these results.

## Main result: an improved actual inverse-adapter bound

The principal construction is A11 in `analysis.md`. Let S < T ≤ 2S be integers, ρ = T/S, θ = ρ−1, q_i = floor(ρi+1/2), and β_i = ρi−q_i. For a > 0 define the actual bilateral kernel and its periodic section by

    G_ij = exp(−a[(ρj−q_i)^2−β_j^2]),
    N_ij = sum_(k in Z) G_(i,j+kS).

On every maximal run where q_i−i is constant, the complete principal block of G is an explicit diagonal similarity of a uniform Gaussian Toeplitz matrix. The latter inverse factors into two ordinary convolutions and three bounded diagonal maps. Keep these full run blocks, truncate only the cross-run interaction, and solve the remaining cyclic block-tridiagonal boundary system. Two applications of the same prepared run inverse recover the answer, avoiding a dense product with a matrix of inverse-update columns.

In the explicit arithmetic Word RAM of A11.9, assume target accuracy 2^(−p), θ = Θ(p^(−1/4)), a = Θ(p^(3/4)), log(S+1) = O(p^(3/4)), and input magnitude exp(O(p)). The construction uses O(S log p) operations per right-hand side and O(p)-bit words after input-independent preparation of size and cost exp(o(p)). Parameters used by that preparation have certified computable descriptions, as detailed in the note. The native model includes bounded-word multiplication, integer division and power-of-two rescaling; this is more than the minimal tcslib instruction set.

For D = Θ(p^(1/4)) axes in an array of volume V, the corresponding complete inverse-adapter upper bound is

    O(V p^(1/4) log p) + exp(o(p)) preparation.

At the same axis count, the inherited reused-band upper bound was O(V p^(3/8)). The new construction removes a factor p^(1/8)/log p from those displayed bounds. This is a fixed-power improvement for the stated actual inverse adapter, rather than a new numerical multiplication κ. The complete transform, native supplier and outer multiplier must still be joined before any larger κ follows. Classical q-binomial, Gaussian elimination, Fourier and Woodbury identities retain their classical status; no historical novelty claim is made.

## The four proof notes

1. `analysis.md` — Exact finite Gaussian LDU, a two-convolution inverse with dimension-independent bounds, exact missing-node interpolation, and the complete Beatty-run construction for the actual periodic inverse. It includes truncation, boundary solve, precision, preparation and the explicit convolution implementation theorem.
2. `algebra.md` — An exact carry tensor of bond dimension 2, gauge transport, owner-controlled codes, a positive matrix-product-input contraction theorem, and an associative common-gauge convolution algebra. These constructions give a different consumer architecture. Low tensor bond dimension alone is not a cheap algorithm for arbitrary dense inputs.
3. `synthesis.md` — Geometric-annihilator coefficient and reciprocal bounds, finite scaled division, perturbation and local-tail bounds, normalized sample/derivative weights, and one ordinary convolution producing all logarithmic nodal weights. It explicitly credits the inherited bilateral-LDU partition estimates and distinguishes the different scales used by the constructions.
4. `complexity.md` — Complete native cost and tensor assembly theorems, exact recovery, shared preparation, literal circuit transposition, scalar and multitype recurrences, and a precision theorem for chains of normalized reciprocal maps. Every recurrence applies only to actual constructed services with their full costs.

Each result has its hypotheses and proof in its own note. The principal inverse result does not depend on assuming that the missing-node interpolation algorithm is already fast, or that coded dense convolution is already cheap. Those are independent longer-range routes.

## Reused mathematical sources and credit

The shared DAG and linked Lean tree supplied the following concrete precedents:

- `Mathproof/GenVandermonde.lean`, `ExpSumRoots.lean`, and `TotalPositivity.lean`: classical exponential/Gaussian total positivity and nonvanishing. Historical checked entries and current source-only entries were distinguished; no fresh kernel check was made.
- `Mathproof/SymplecticTI.lean` and `SymplecticTITOCIBalancedCoevaluation20260901.lean`: mode support, the symplectic Levi action and reciprocal primal/dual gauge cancellation. The source's classical Levi and Lysikov–Walter predecessor credits remain in force.
- `Mathproof/External/IntegerMultBounds20261008/Matrix/GaussianTensorExecution.lean`: exact tensor arithmetic composition; it is not a runtime theorem.
- `Mathproof/Meta/Problem18PolynomialToeplitzProduct20261002.lean`: exact polynomial coefficient production and full recovery from the actual Toeplitz row map.
- FastPoly, by Thomas Ahle and retained contributors: fixed shared circuit syntax and algebraic operation accounting. The notes explicitly add native costs omitted by that algebraic model.
- tcslib, by Shilun-Allan-Li and its retained formal-math contributors: concrete machine semantics and framing. The stronger instruction set needed by the main inverse corollary is stated separately.
- Mpfx, by bksaiki and retained contributors: sufficient nearest-integer recovery; CatCrypt, by its contributors: cyclic convolution, transform inversion and radix-two identities.

The local registered proof notes `research/native-word-fft/GAUSSIAN-CHIRP.md`, `NATIVE-BANDED-INVERSE.md`, and `research/native-kappa-30201655/modern-sources/BILATERAL-LDU.md` supply the inherited actual Gaussian formulas, native arithmetic/precision conventions, reused-band comparison, and finite/bilateral factorization. Their Harvey–van der Hoeven, source08 and retained contributor lineage is preserved. The proof here expands those constructions by using complete Beatty runs and a boundary-only correction.

The coded-interface discussion credits THU New Media Research Center, Ali Romman, Dugongue, Dillon Amburgey, Cinna Davis, Ryanson Jonathan, Cao Yifan, Jacob Alan Sussman, Chris R/Clear1nsight, zxv and the retained native/Clifford/compiler/analytic lineage. It builds on the whole-K, central-Q and native-stage results already described in the local proof tree. It does not claim to have replaced their missing dense-input consumer by an unproved oracle.

These attributions identify the sources actually reused, not an exhaustive audit of all prior mathematics or unpublished project work.

## Precise research directions following the proofs

The inverse-adapter construction is a completed sufficient result on its displayed domain. Its next mathematical assembly task is to combine its real operator costs and error bounds with the forward maps, arbitrary twiddles, native supplier and outer recurrence. All of those costs must be included before claiming a larger multiplier κ.

The independent coded-consumer route asks for a fast contraction on the full dense input family, or a proof that the actual caller supplies structured operands to which the positive contraction theorem applies. The annihilator route asks for a complete stable conversion between its coefficient and point normalizations. Neither unproved task is used as a premise of the completed inverse theorem.
