# Sparse feedback volume, conditioning, and the native-call cut

All logarithms are base2. Matrices act on complex column vectors. `M^{-*}`
means `(M^{-1})*`, with `*` the conjugate transpose. This is a linear-circuit
result, not an unrestricted arithmetic or native-runtime lower bound.

## 1. Boundary, operation model, and claim

Let A,B be V-by-V unitary matrices, C=BA, and suppose every row of B has
exactly 2^f nonzero entries, all of squared magnitude2^-f, for integer f>=1.
The required primary boundary is

    F = [[C, lambda B], [0,I]],       lambda=1/2.                 (1)

Thus `(x,y)` maps to `(Cx+By/2,y)`. The same proof works for any real
lambda>0. PR4009's exact selected195/521 tensor boundary supplies these
hypotheses: B_f is a tensor product of involutory-Pauli half kernels and C_f
is unitary. Its prior source/native identification is credited, not newly
claimed here. The present theorem changes full-array passes to actual scalar
coordinate-update volume.

The machine may have any finite number of coordinates, including arbitrary
dirty auxiliaries that must return unchanged and clean zero auxiliaries that
must return zero on every legal input. It is a fixed sequence of invertible
linear operations. Initially every machine coordinate is a formal independent
variable for defining its square matrix M, although legal clean inputs are
specialized to zero. No reset, erasure, nonlinear encoding or free input-dependent
preparation is allowed.

An arithmetic primitive is a coordinate shear `z_t += c z_s`, t!=s,
with any nonzero complex coefficient c. Its cost is one updated coordinate.
A masked shear on m disjoint source/target pairs is expanded into m such
primitives and charged m; variable block sizes are allowed. We separately
permit arbitrary invertible monomial maps. They are granted zero cost in the
lower bound; their actual routing/scaling cost remains payable in any upper
invoice. Preparation and recovery arithmetic are part of the program.
There is exactly one distinguished invertible native call, on its declared
operand, with no other native calls. Application to4009 uses its normalized
rank2f child on one V-sized payload, never a concatenated2V operand.

Let K>=1 bound the spectral condition number of EVERY full machine prefix,
including the intermediate primitive cuts of a masked operation. The bound is
on the full formal square machine, not just its restriction to legal inputs.
No separate coefficient bound is assumed; large coefficients or ill-conditioned
preparation must be reflected in K. A coefficient bound alone is not a K bound.

There is an explicit potential Phi and a native jump

    Delta_Q = Phi(M_after_native) - Phi(M_before_native)

such that, for total coordinate-ADD volume S,

    8 K S + Re(Delta_Q) >= lambda f V = fV/2.                  (2)

More precisely, if K_t is the maximum of the condition numbers immediately
before and after arithmetic primitive t, then

    8 sum_t K_t + Re(Delta_Q) >= fV/2.                         (3)

For a native call performed on the target payload before ANY arithmetic,
with only payload-preserving monomial maps before it, Delta_Q=0. Consequently

    S >= fV/(16K).                                           (4)

After that call, arbitrary sparse feedback, mixtures, cross-coordinate
monomial maps and any number of restored auxiliaries remain allowed. Neither
(2) nor(4) claims an fV bound for unrestricted conditioning or unrestricted
native interleaving. The native jump is not silently assigned zero in(2).

## 2. A preconditioner that detects the triangular correction

Embed J in the full machine with sole nonzero block

    J_xy = C^{-1} B = A^{-1}.                                 (5)

All auxiliary blocks are zero. Therefore ||J||_2=1. This matrix is a fixed
ANALYTICAL preconditioner; the algorithm is not given an implementation of J
or allowed to apply it for free. Define

    N = M^{-*} J,
    p_ij = M_ij conjugate(N_ij),
    h(z) = -z log2|z| (z!=0), h(0)=0,
    Phi(M) = sum_ij h(p_ij).                                  (6)

Phi can be complex. We bound absolute changes and take real parts only in the
final inequality. This avoids assuming quasi-probabilities are nonnegative.
At M=I, each diagonal entry of J is zero, so every p_ij is zero and Phi(I)=0.

Ignoring auxiliaries first, direct multiplication gives

    F^{-*} J = [[0,B],[0,-lambda I]].                          (7)

The only nonzero p entries are lambda|B_ij|^2 in the xy block and -lambda
on the V diagonal yy entries. Each B row contains2^f entries of weight2^-f.
Thus the xy contribution is lambda V(f-log2 lambda), the yy contribution
is lambda V log2 lambda, and

    Phi(F)=lambda fV.                                        (8)

Restored dirty auxiliaries add an identity block and zero p entries.
Clean auxiliaries need not have a prescribed nonzero-input behavior. Group
independent primary/dirty variables as w and clean variables as z. Correctness
and clean restoration on z=0 force the final full matrix to be

    M_final = [[T,R],[0,D]],     T=F direct-sum I_dirty,

where D is invertible and R is unrestricted. Embed J as diag(J_w,0). Then

    M_final^{-*}J = [[T^{-*}J_w,0],[-D^{-*}R* T^{-*}J_w,0]].

In the original-w columns, bottom rows of M_final vanish; in clean-input
columns, N vanishes. Every auxiliary-associated p therefore vanishes, and
(8) still holds. This argument uses restoration on every independent legal w;
it does not assume correctness when clean inputs are nonzero.

Ordinary, unpreconditioned quasi-entropy misses the new correction:
for F, its off-diagonal block pairs with zeros of F^{-*}, leaving exactly
the same potential as diag(C,I). Its determinant is also unchanged. This is
why4009's pass lower bound or an ordinary Fourier entropy bound cannot simply
be read as the present volume theorem.

## 3. Dimension-free cost of a single coordinate update

For any complex p,q, let L=|p|+|q|. If L=0 the following is immediate.
Otherwise normalize by L. Homogeneity cancels the log L term in the defect.
Writing a=|p|/L and b=|q|/L, a+b=1, gives

    |h(p)+h(q)-h(p+q)|
      <= L [ -a log2 a - b log2 b
              + r log2(1/r) ] < 2L,                         (9)

where r=|p+q|/L in[0,1], and continuous zero conventions apply. We used
binary entropy<=1 and r log2(1/r)<=1/(e ln2)<1. The non-strict bound<=2L
will suffice. This calculation also covers exact cancellation p+q=0.

A shear G=I+c e_t e_s^T changes row t of M and row s of N, since
`N' = G^{-*}N`. For each column j, the pair satisfies

    p'_tj + p'_sj = p_tj + p_sj.                              (10)

Indeed the added c M_sj conjugate(N_tj) cancels the corresponding inverse-dual
term. Other p entries are unchanged. Applying(9) to the old and new pairs
around their common sum yields

    |Delta Phi| <= 2 sum_j (|p_tj|+|p_sj|+|p'_tj|+|p'_sj|).

For ANY row i at a prefix M, Cauchy-Schwarz and spectral norm bounds give

    sum_j |M_ij| |N_ij|
      <= ||row_i M||_2 ||row_i N||_2
      <= ||M||_2 ||M^{-1}||_2 ||J||_2
      = cond_2(M).                                          (11)

There are two rows at each of two endpoints, so

    |Delta Phi| <= 8 K_t.                                   (12)

The constant8 is a convenient rigorous upper bound, not claimed sharp.
There is no dimension factor, coefficient bound, entrywise positivity or
bounded fanout premise hidden in(12).

For an invertible monomial row map, the corresponding rows of M and N
are permuted together and their nonzero scale factors cancel in p.
Hence Phi is exactly unchanged, even for nonunit scales. Treating such maps
as free only makes the necessary condition more generous. A physically
implemented permutation is not declared costless by this theorem.

## 4. The native cut and what it does not settle

Telescope from I to M_final. Monomial jumps vanish, the sole native jump is
Delta_Q, and every arithmetic jump is at most8K_t in real part. Equations
(8),(12) prove(2),(3).

If before the native call there are only payload-preserving monomial maps,
M is block diagonal on target, donor and auxiliary payloads. The product
M^{-*}J remains supported in the target-row/donor-column block. This block
of M is zero. Applying the native call on the TARGET payload preserves that
support disjointness, so both potentials are zero. This proves Delta_Q=0
and(4). Arbitrary monomial permutations across the target/donor split before
the call are NOT included in this zero-jump argument.

For a general interleaved call, Delta_Q must be evaluated or bounded from
its actual input matrix. If S=o(fV) and K=O(1), (2) requires

    Re(Delta_Q) >= fV/2-o(fV).

Thus a sparse interleaved proposal must arrange for its one native call to
supply almost all of this specifically selected coupling potential. This is
a necessary condition, not a construction or a bound on achievable Delta_Q.
The theorem leaves that route open. Likewise, (4) permits smaller volume
if K grows. It quantifies the price in conditioning; it does not itself
translate K into a bit-precision or numerical-stability invoice.

## 5. Relation to the selected budget

For the pinned selected exponent0<alpha<1,4009's ideal recursive saving has
the form A0 V delta f^(1-alpha), with A0>0 fixed and
`delta=2-2^(1-alpha)>0`. For the child-first class with K bounded independently
of f, (4) is Omega(fV); crediting the original V-coordinate ADD does not
change that asymptotic conclusion. Hence such a uniformly well-conditioned
sparse adapter cannot fit that rank-only saving for all f.

More generally, a necessary child-first improvement condition is

    f/(16K) - 1 < A0 delta f^(1-alpha).                       (13)

In particular, asymptotic sub-fV designs must give up a uniform K bound or
move to the nonzero-native-jump case, or change another stated model premise.
No finite threshold or new kappa follows without actual constants and the
complete routing/precision/hosting invoice. The general sparse-coordinate
family is not closed by this theorem.

## 6. Provenance and verification scope

The potential method is an adaptation of Nir Ailon's well-conditioned
Fourier lower bounds and Ailon--Gal Yehuda's preconditioned quasi-entropy,
not a newly invented lower-bound technique. Primary sources:

- Ailon, arXiv:1403.1307, https://arxiv.org/abs/1403.1307.
- Ailon and Yehuda, arXiv:1604.02557v4, Section1.1 and Lemma1.1,
  https://arxiv.org/abs/1604.02557.

Here the new scoped contribution is the nilpotent block preconditioner(5),
its exact coupling value lambda fV, the explicit native-cut debit, and the
complex coordinate-shear/returned-clean-auxiliary argument. The proof above
is self-contained; finite checks do not prove the quantified entropy theorem.
PR4009 at89a358aac11d11e0539eb95c27600e7677be7ce4 supplies the selected
boundary. PR3989 and Gonzalo Mier's3975 supply its prior physical-binding
lineage. All remain distinct from supplier admission.
