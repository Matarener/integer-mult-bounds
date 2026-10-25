# Dyadic factorization and a one-temporary compiler

Let D = ℤ[1/2] ⊂ ℚ. All matrix ranks in this note are over ℚ. Vectors may lie in any vector space over a characteristic-zero field containing these dyadic scalars. The arguments are informal proofs, not Lean formalizations.

## Theorem 1: legal rank factors always exist

For every nonempty finite m × n matrix M over D, with rational rank r, the algorithm in `compiler.factor` returns M = U V, where U has shape m × r over D and V has shape r × n over ℤ. It terminates using integer column operations; it never divides a scalar coefficient by an odd integer.

Proof. Choose a power of two s clearing every denominator and initialize A = s M and S = I_n. Maintain the invariant A S = s M, with A and S integral and S unimodular.

Swapping columns p,j of A and rows p,j of S preserves A S. Replacing column j of A by column j − q column p corresponds to A ← A E, with E = I − q e_p e_jᵀ. Since j ≠ p, E⁻¹ = I + q e_p e_jᵀ. The inverse row operation S ← E⁻¹ S replaces row p by row p + q row j, exactly as in the code. Negating column p and row p likewise preserves the invariant. Every operation is integral and unimodular.

At pivot row i, choose a nonzero remaining column p. For each other remaining column j, divide the integer A[i,j] by the nonzero pivot A[i,p], subtract the quotient multiple and, if the remainder is nonzero, swap it into the pivot position. Every such swap strictly decreases the absolute nonzero pivot. Hence the Euclidean loop terminates and clears row i in every later column. Earlier pivot rows have zeros in all remaining columns, so these operations preserve all earlier clearances.

Process successive rows. At termination, the first r columns H have distinct increasing pivot rows and a triangular nonsingular pivot minor; all later columns are zero. Thus A = [H 0] has rank r. Because S is invertible, rank A = rank M. The invariant gives M = (H/s) S[0:r,:]. Set U = H/s and V = S[0:r,:]. U is dyadic and V is integral, establishing every claimed property. If M = 0, r = 0 and the empty factor product is zero. No coefficient-size or polynomial bit-complexity bound is claimed. ∎

Why the alphabet condition matters: choosing the first column of [[3,1],[6,2]] as a rational rank basis gives the right factor [1,1/3], which is not native-dyadic. The integer column algorithm instead gives [[1],[2]] · [3,1]. This is an application of classical unimodular column reduction, not a new normal-form theorem or a claim of a canonical Hermite form.

## Theorem 2: r physical bridge episodes suffice

Let X_1,…,X_n and Y_1,…,Y_m be disjoint persistent fields. Let the sources use one invertible linear chart B and the destinations one chart A. Suppose the actual exact physical operator Q = A B⁻¹ is supplied, with its correct independently verified implementation. Then M = U V yields the shear

Y_j ← Y_j + Σ_i M[j,i] X_i

using r sequential invocations of Q and one reusable owned temporary, with zero productive credit for that temporary. The compiler does not certify a user-declared query rank; a rank bill for a nonidentity query remains conditional on its actual physical implementation. In the four source applications below A = B, so Q is exactly the identity and has no recursive cost or monomial wrapper.

Proof. For each k, clear the temporary, add Σ_i V[k,i] B X_i into it, apply Q, add U[j,k] times its value to each physical A Y_j, then clear it. Linearity makes the transformed temporary A Σ_i V[k,i] X_i. Summing the updates over k gives A(Y_j + Σ_i M[j,i] X_i). Sources are never written. Both clears are emitted; arbitrary dirty owned entry is removed, and the owned return is zero. Only one temporary is live because the episodes run sequentially. All coefficients remain dyadic by Theorem 1, so the native scalar alphabet is respected. For r = 0, emit the identity and allocate no temporary. ∎

Write a(q) for the retained source `primitive_allowance` of a nonzero dyadic ADD. The complete scalar allowance is 4r + Σ a(U[j,k]) + Σ a(V[k,i]): each of the two clears per episode has allowance 2. Scalar ADDs with zero coefficient are omitted. A physical query of verified Fourier rank d would add r whole rank-d jobs when d > 0, plus its actual monomial factors and nonrecursive work; none are silently free. The new owned field must not alias any persistent field or a live source C0. This is a local sufficient construction, not admission of an arbitrary declared native job.

## Corollary: both inverse-transpose orientations

The persistent block matrix is [[I,0],[M,I]]. Its inverse transpose has the same form after exchanging source and target groups and replacing M by −Mᵀ. Factor −Mᵀ = (−Vᵀ) Uᵀ and apply Theorem 2. The factors remain dyadic and have the same multiset of coefficient magnitudes. Because the retained ADD allowance depends on magnitude and denominator, the scalar allowance is identical in both orientations, including every clear. Owned erasure is proved afresh; it is not obtained by formally inverting a destructive clear. ∎

## Four authenticated native applications

The live source is canonical main's `THREE-base-FULL-IDENTITY-NATIVE.json.gz`, pinned in SOURCES.json. CASES.json selects four disjoint windows by phase and persistent-scalar ordinal. The verifier finds those selectors in the actual forward and backward programs, checks that each whole window consists solely of common-frame ADDs, derives its coefficient matrix and disjoint source/target sets, and compares all source coefficients. There is no hidden warp, scale, climb, owned action or source permutation between selected instructions.

| Phase | Scalar ordinals | Rank | Old allowance | New allowance |
|---|---:|---:|---:|---:|
| full_frame_cleanup | 4727–4764 | 1 | 418 | 366 |
| full_frame_cleanup | 1615–1620 | 1 | 52 | 46 |
| full_frame_cleanup | 2900–2905 | 1 | 52 | 46 |
| full_frame_cleanup | 4251–4276 | 2 | 244 | 240 |
| Total, each orientation | | | 766 | 698 |

Each old allowance already equals the allowance after repeated-edge coalescing. Thus the certified 68-unit reduction is not merely cancellation or duplicate ADD consolidation. The rank-two window is included; this is not only the one-source/rank-one special case.

The verifier executes every emitted instruction on independent formal persistent and dirty-owned input columns. It checks all 160 local columns across both orientations. All other persistent fields, including the original C0, are untouched because their roles never appear. Theorem 2 therefore permits substitution in any surrounding program with the same common chart and a fresh owned field. It adds at most one owned field, reused across all four windows, and adds no productive credit or recursive jobs. Caller allocation, finite normalization, full stock and analytic admission remain separate obligations.

The local allowance decreases by 68 per orientation. No new κ, asymptotic exponent, global runtime speedup, full 632-column native replay, selected-frontier update or new mathematical priority claim follows. The universal dyadic construction, exact source binding and emitted local programs are the deliverable.
