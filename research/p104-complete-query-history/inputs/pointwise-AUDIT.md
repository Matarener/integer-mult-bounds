# Independent audit of the pointwise Clifford tensor bound

Prepared for DLamdata with substantial OpenAI Codex assistance. Apache-2.0.
This is a written mathematical audit with exact finite corroboration, not a
formal-kernel proof or independent human review.

## Verdict and source boundary

No substantive gap was found in Sections 2–5 of Ali Romman's
[PR5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526), at
`45f7de73b168721cdf7ec8c1769b1b594493716a`. The immutable
[source proof](source/PR5526-PROOF.md) has SHA256
`45483e4b5f604a5e70602c5caaa4394d4a0d0d1a6d0b6e8a93b836d50b23f764`.
The theorem, constants and constructions remain the predecessor's work.

The audited statements are the stabilizer overlap count, the first Clifford
overlap count and general upper bound, the uniform rational Gram estimates,
and the exact central-phase/four-width implication. The source's later
paid-repair theorem, cost invoice, actual passive-caller binding, native frontend
implementation and selected multiplication construction are **not audited here**.
In particular, this result alone does not accept PR5526's 104-return conclusion.

One verifier agent derived the symplectic and phase implications before seeing
any lead checker or result; a second reviewer derived the proof audit before
verdict comparison. The lead separately implemented literal Gaussian matrices.
These are independent AI-assisted approaches, with shared classical assumptions
and Python integer/rational arithmetic. They are not independent human reviews.
The lead read the source's census code to distinguish its coverage; the independent
binary-matrix checker imported and read no predecessor executable. The source
already has a projective Choi orbit and signed-Pauli census. Our literal matrix
orbit is related finite corroboration, not a new census theorem. The independent
exhaustive binary-matrix path, residual-form checks, full central extension and
written audit are the added review evidence.

## 1. The exact phase group really has four elements

Let R=Z[i,1/2]. If alpha I is unitary and has entries in R, write
alpha=(a+ib)/2^k. Then a^2+b^2=4^k. For k>0, reduction modulo four makes both
integers even; descent leaves alpha in {1,i,-1,-i}. If U and V in the group are
projectively equal, their scalar ratio belongs to R because UV* does. Thus the
argument does not rely on dividing an arbitrary matrix entry in R.

The ordinary Hadamard is not itself in R. This does not remove projective
Cliffords: H'=(1+i)/2 [[1,1],[1,-1]] is unitary in R and induces the same Pauli
label action. H', S=diag(1,i) and CNOT supply the usual projective generators.
The classical Clifford-to-symplectic surjection and its Pauli kernel therefore
apply to these Gaussian-dyadic representatives. For the first-overlap equality
one can directly realize every transvection: for a nonidentity Hermitian Pauli
P_a, V_a=(1+i)(I-iP_a)/2 is Gaussian-dyadic, unitary, and induces the
transvection at a. This makes explicit an implicit lift step in the source;
no change to its theorem is needed.

The matrix checker retains these phases during generation: (H')^2=iI.
It obtains 96 and 46,080 exact matrices on one and two axes, with exactly four
lifts in each of 24 and 11,520 projective classes. Unitarity is checked on every
projective representative; scalar-unit invariance covers its other three lifts.
Completeness uses the classical group order and generator theorem, not merely
the absence of a new element during enumeration.

## 2. Stabilizer overlaps and the basis-counting issue

Fix one coordinate basis for each k-dimensional binary support W. A stabilizer
ray supported on W with its amplitude at zero positive has phase polynomial

    q(t) = sum_j a_j t_j + 2 sum_(j<l) b_jl t_j t_l (mod 4),

with a_j in Z/4 and b_jl in F2. Its coefficients are recovered uniquely from
values at e_j and e_j+e_l. There is no extra factor for choices of basis: one
basis on each W is fixed. There are 4^k 2^(k(k-1)/2) such phases.

Conversely the finite difference in direction e_j is

    q(t+e_j)-q(t) = a_j + 2(a_j mod 2)t_j
                    + 2 sum_(l!=j) b_jl t_l (mod 4).

The associated translation Paulis commute by symmetry of the cross coefficients.
Their X parts are independent. Together with the N-k diagonal annihilators of
W they give N independent stabilizers. This proves that the phase count describes
the family exactly, rather than assuming every quadratic phase is admissible.
Affine supports not containing zero have zero overlap with |0^N>. Those containing
zero are linear subspaces. Therefore the number of rays at squared overlap 2^-k is

    A_(N,k) = [N choose k]_2 2^(k(k+3)/2).

The k=0 term is the reference ray and is excluded from the off-diagonal sum.
Other singleton supports have zero overlap. Clifford transitivity follows by
removing the support offset, choosing coordinate axes, undoing the quadratic
phase and applying Hadamards. This also proves that every Gram row has the same
absolute-overlap distribution. N=0 has one ray and an empty off-diagonal sum.

This all-N statement is audited in writing. Our finite checker does not claim a
new exhaustive stabilizer-state census; its 528 bounded checks test the resulting
subspace-term inequality for 1<=N<=32. The predecessor retains its own state census.

## 3. Why fixed Pauli signs are a character

Use Hermitian Paulis P_v indexed by V=F2^(2n), with alternating form omega.
For a Clifford lift U of S in Sp(V), let L=ker(S-I). On fixed labels write
UP_v U*=epsilon(v)P_v. In P_v P_w=zeta(v,w)P_(v+w), conjugation preserves the
same zeta on both sides, so epsilon(v+w)=epsilon(v)epsilon(w). This remains true
when v and w anticommute; L need not be isotropic.

The trace of conjugation on the Pauli basis is sum_(v in L) epsilon(v), while
on the full matrix space it is |tr U|^2. Character orthogonality makes this
zero or 2^dim(L). Multiplication of the lift by P_p changes its sign character
by (-1)^omega(p,v). Restriction V -> L* is onto and has kernel L-perp. Thus,
when rank(S-I)=k, exactly 2^k of the 2^(2n) projective Pauli lifts have nonzero
trace, and their normalized trace magnitude is 2^(-k/2).

For rank-one displacement, write (S-I)x=ell(x)a. Symplecticity forces the two
nonzero linear forms ell and omega(-,a) to agree over F2. Conversely each
nonzero a defines a transvection x -> x+omega(x,a)a. There are 2^(2n)-1 such
maps and two nonzero-trace lifts each. Hence B_(n,1)=2(2^(2n)-1), half of
A_(2n,1). This factor is essential to the advertised uniform row budget.

The independent checker tries **all** 16 binary 2x2 matrices and 65,536 binary
4x4 matrices, accepting only literal preservers of omega. It enumerates actual
fixed-space character sums without gate/tableau generation. At n=2 it finds
720 symplectic matrices with displacement counts

    k:                  0   1    2     3     4
    symplectic maps:    1  15  100   300   304
    nonzero lifts:      1  30  400  2400  4864.

The lead's literal trace calculation independently gives the latter distribution
and 3,825 zero-overlap projective classes. The checker relies on the written
identification between these abstract characters and actual Clifford lifts;
the direct matrix calculation corroborates that identification in these two
small dimensions. Neither finite path supplies the universal quantifier.

## 4. Residual forms: an injection, not a claimed classification

Put W=im(S-I). Symplecticity gives W-perp=ker(S-I). Therefore

    B((S-I)x,w)=omega(x,w)

is well defined. If its left argument pairs to zero with W, its preimage lies
in W-perp and the left argument is zero; the right-kernel argument uses
nondegeneracy of omega. Substitution verifies B(u,v)+B(v,u)=omega(u,v).
For each fixed W of dimension k there are 2^(k(k+1)/2) bilinear forms with
this symmetrization, including singular forms. A nonsingular one determines
(S-I)x by its pairings with all w. Consequently S -> (W,B) is injective.
No converse realizing every counted form is needed for the upper bound.

Counting W and the nonzero-trace lifts gives A_(2n,k) as an upper bound for
Clifford overlaps. The separate rank-one equality improves its first term.
The independent finite checker explicitly tests every preimage choice for B,
its kernel, symmetrization, and uniqueness of (W,B) across the enumerated maps.
These checks target potential failures hidden by simply comparing group totals.

## 5. The entire tail, including odd widths

Write d_k=product_(j=1..k)(2^j-1). At f=2N+4 the exact kth stabilizer row term is

    A_(N,k) 2^(-kf/2)
      = product_(j=0..k-1)(1-2^(-(N-j))) / d_k <= 1/d_k.

For Clifford Choi states N=2n, the first term is strictly below 1/2. Retain
terms through k=4; the k=5 tail has successive ratio at most 1/63. At the
extra even-width shift 2s, multiply the kth term by 2^(-sk), so the tail ratio
is at most 1/(63*2^s). The exact independently calculated majorants are:

| Family/shift | Complete majorant | Required strict upper bound |
|---|---:|---:|
| Clifford s=0 | 53534/60543 | 8/9 |
| Stabilizer at f=2N+6 | 719543/1220625 | 3/5 |
| Clifford s=2 | 359294/2451015 | 3/20 |
| Clifford s=6 | 162912909217/20637399121920 | 1/126 |

Terms beyond the actual dimension only enlarge the upper bound. Every overlap
has modulus at most one, so increasing f decreases the absolute row sum; this
covers intervening odd widths without a floating-point square root.
For Hermitian Gram diagonal one and row sum at most s, the elementary inequality
2|b_i b_j|<=|b_i|^2+|b_j|^2 gives spectral bounds 1-s and 1+s. It applies to every
subset. Thus the predecessor's Clifford bounds [1/9,17/9] at f>=4n+4 and
stabilizer bounds [2/5,8/5] at f>=2N+6 follow. Vectorization transfers the latter
to rectangular stabilizer maps with the stated norm weights. These are sufficient
bounds, not sharp thresholds or a physical implementation theorem.

## 6. Four tests have a fixed-program premise

Write each exact Clifford as i^j U_g for a chosen projective representative.
At width f the coefficient for that projective class is

    beta_(g,f mod 4) = sum_(j=0..3) c_(g,j) i^(jf).

Pointwise positive Gram bounds identify the kernel exactly after this phase
combination. Four consecutive sufficiently large widths include all four
residues; Fourier inversion forces all **fixed** coefficients c_(g,j) to vanish.
Parseval gives sum_(g,r)|beta_(g,r)|^2=4M, where M=sum_(g,j)|c_(g,j)|^2.
Averaging the four separately normalized squared residual norms gives at least
M/9, hence at least one attains that bound. No common D^-f normalization across
different widths is assumed. For n=0 the same Fourier argument uses widths1..4.

The necessity witness for residue r is sum_j i^(-rj)[i^j I]. It vanishes in the
other three residues and equals4I in residue r. Keeping U and iU as separate
pointwise columns instead makes a singular Gram matrix. Both failure modes are
checked with exact Gaussian arithmetic.

Two stronger exclusions are explicit controls in the new matrix checker:

* Width-dependent formal coefficients c_0(f)=1, c_1(f)=-i^(-f) give a nonzero
  formal vector but the zero operator at every width. The pointwise theorem
  allows this phase cancellation; it is not a fixed-coefficient certificate.
* For arbitrary nonunitary scalar maps, take
  P(x)=product_(j=0..3)(x-2^(8+j))=sum_k c_k x^k. The nonzero residual
  sum_k c_k[2^k I] vanishes at widths8..11 and not12. Each scalar map is a
  stabilizer map, but the four-test implication does not extend to these scales.

The source correctly makes these quantifier distinctions. We retain them rather
than promoting its pointwise stabilizer-map statement into a uniform program test.

## Coverage and remaining obligations

The independent checks and written arguments support only the scoped core theorem.
They share classical Pauli/Clifford/stabilizer structure, Fourier orthogonality,
and exact arithmetic; no formalization of those foundations was undertaken.
The full predecessor replay was not run: it includes frontend and caller claims
outside this audit. Actual costs, source versions, observation histories, routing,
precision, ownership and admission must be verified at each application. The
selected record and all frozen predecessors remain unchanged.

This audit answers the independent core-proof portion of the handoff in
[Discussion1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19174354).
Its requested passive-contract implication remains a separate review task.
PR5531's application and PR5526's later paid-repair extension also remain outside
coverage. A reviewed universal algebraic implication is useful evidence, not
scientific approval of every downstream claim.
