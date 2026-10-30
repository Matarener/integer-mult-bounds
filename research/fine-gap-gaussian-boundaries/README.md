# Fine-grid inversion and rank-batched coded boundaries

Dugongue, with substantial OpenAI Codex assistance from four workers. This is a collection of informal mathematical proofs, constructions and precisely stated research directions, using only local DAG and linked proof-tree sources. No numerical experiment, solver, web search or Lean check was used.

**No higher complete multiplication κ is proved in this release.** The previous inverse-adapter improvement cannot by itself raise a provider-limited full bound. The positive contributions below widen the actual inverse algorithm and construct new ways to implement coded boundaries and consumers. An uncompleted stronger provider is not assumed as an input to a claimed new best exponent.

## 1. A completed fine-grid inverse without the huge gauge

Let ρ=T/S, θ=ρ−1, q_i=floor(ρi+1/2), β_i=ρi−q_i, and

    G_ij=exp(−a[(ρj−q_i)^2−β_j^2]),
    N_ij=sum_(k in Z) G_(i,j+kS).

For θ=Θ(p^(−2)), a=Θ(log p) with a sufficiently large fixed lower coefficient, log(S+1)=O(p), target precision O(p) and input magnitude exp(O(p)), the exact periodic N inverse has a constructive O(S log p) application algorithm, after charged polynomial(S,p) input-independent preparation, using O(p)-bit words in the stated extended Word RAM.

The key exact identity is

    (1+qz) H(z)=H(q²z),
    H(z)=sum_(r≥0) (−q)^r z^r / product_(j=1)^r(1−q^(2j)).

After the actual run similarity, the first factor is a stable bidiagonal recurrence. The remaining kernel decays rapidly, so it is evaluated in short locally recentered convolution blocks. This avoids ever applying the huge full-run diagonal exp(aβ_i²/θ). A physical boundary Schur complement, with its diagonal-dominance margin proved, completes the periodic inverse.

`inverse.md` proves the local identities, finite tails, recurrence stability, boundary solve, precision and actual inverse theorem. This extends the previous construction beyond its d≤O(p^(1/4)) precision restriction. It uses ordinary complete line solves, and does not assume that a low-rank tensor description is already a cheap contraction.

The native model explicitly includes bounded-word multiplication/division, fixed-point rescaling shifts and indexed memory. Parameters have effective certified descriptions. The mathematical statements do not claim an instruction-level implementation in a smaller ISA.

## 2. A completed rank-based boundary construction

Let M be an invertible scalar matrix between independent role fields. Let a,b be binary input/output gauge labels for a central Gaussian Q. The actual boundary is G_b M G_a^(-1). Its only nonordinary blocks are

    M_01 Q^(-1) and M_10 Q.

Rank-factor those two scalar blocks, compute their linear combinations on one immutable input snapshot, query each rank component once, and distribute the results. The complete boundary therefore has the sufficient Gaussian tariff

    rank(M_01)+rank(M_10).

Owned buffers, all-input correctness, coefficient generation and cleanup are explicit. The reciprocal-dual boundary has the same total tariff, proved by an inverse-block nullity identity. When a completed provider's literal boundary uses more queries than this, replacing it preserves the exact independent endpoint and strictly reduces the paid rank-one count. The paper does not assert that such a strict reduction has already been found in the selected provider.

`boundary.md` gives the construction and its eight proofs, including a dense rank-one sharing example and a safe multiaxis extension. This is whole-matrix sharing, so it never reuses a query after its source snapshot has changed.

## 3. New positive coded-consumer interfaces

`consumer.md` proves how a paid Gaussian correction at an ADD can be redirected onto the target without increasing its Gaussian rank, including the correct restricted multiaxis version. It constructs exact B/C gauge incidences and a completely priced alternating schedule. That simple schedule does not fund a higher κ.

A separate dense consumer computes a common-frame orthogonal-code invariant in an XOR-convolution algebra, with reciprocal Gaussian filters cancelled inside the product. Its actual output is one sum of products; it is not credited as many independent Gaussian transforms. The note supplies the ordinary Walsh algorithm and states exactly why a changing code itinerary or a cyclic-convolution caller needs an additional proved interface.

## 4. Exact implications for a full κ

`assembly.md` reconstructs the complete native cost rows and proves their sufficient transfers. For an actually admitted provider saving q_C, the inherited fused route already gives every strict κ<min(q_C,3/32). The new simpler unfused line route gives every strict κ<q/(1+q), once all its retained actual forward/outer contracts are used. The second is not a larger exponent than the first with the same provider.

The seemingly much larger complex-only quotient claim is not inserted for q_C. Its repaired local B/C interfaces require a complete compatible controller and paid boundaries before they are independent productive jobs. Monomial normalization of an independent Clifford target does not diagonalize a coupled coefficient-field shear.

Thus the completed results are the fine-grid inverse, the rank-batched boundaries and the explicit coded-consumer interfaces. A new best κ still requires instantiating them in a stronger complete provider or changing the dominant main-transform recurrence. The notes give exact positive constructions to use in that work, rather than a claimed profitable instance that has not been proved.

## Reading order and inherited proof appendix

1. `inverse.md`: actual fine-grid Gaussian inverse and its full application bound.
2. `boundary.md`: complete rank-batched gauge boundaries and equal dual tariffs.
3. `consumer.md`: chronological gauge redirection and exact dense coded consumers.
4. `assembly.md`: full cost conversion, valid provider interfaces and precise κ transfers.
5. `precedents/gaussian-convolution.md`: inherited finite q-LDU and explicit bounded-word convolution proofs from the preceding mathematical deliverable. These are reproduced as credited prerequisites, not claimed as new findings in this release.

## Attribution and mathematical status

The preceding Beatty-run Gaussian notes and the actual Gaussian/Poisson, banded-inverse, bilateral-LDU and native assembly sources retain their Harvey–van der Hoeven, source08 and project contributor lineage. The DAG and linked Lean tree supplied classical total-positivity, symplectic support/coevaluation, exact tensor-execution, polynomial Toeplitz and machine/rounding precedents. Source inspection is not a fresh kernel check.

Credit Cinna Davis, Cao Yifan, DaysSky, Nick Petalas, Ryanson Jonathan, Rohan Arun, Dugongue, Dillon Amburgey, zxv, Jacob Alan Sussman, Chafik Boukhalfa, Vlado Vojdanovski, Jeremy Kothe, Ali Romman, THU New Media Research Center and the retained native/Clifford/compiler/analytic contributors identified in the individual notes. FastPoly, tcslib, Mpfx, CatCrypt and the symplectic proof-tree sources retain their source-specific attributions. No source code is redistributed here.

Geometric recurrences, q-binomial identities, rank factorization, nullity identities, Schur complements and Fourier convolution are classical mathematical tools. The contributions are the displayed constructive combinations and their exact stated interfaces. No historical or exhaustive project-novelty claim, independent human review or formal proof acceptance is asserted.
