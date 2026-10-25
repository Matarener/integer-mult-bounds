# Independent review: arbitrary-support skew rank tariff

The proposed rank inequality is correct under its stated fixed topology,
two-sided isolation and complete inventory premises. It does not require J
to commute with any fresh N_s, to have two-plane support, or to have even
native rank. This review leaves all earlier review/source directories frozen.

The primary reviewed inputs are `../root-joint/arbitrary_skew_gate.py`,
`ARBITRARY-SKEW-GATE.json` and `ARBITRARY-SKEW-GATE-PROOF.md` in that same
directory. The initial receipt has 36 exact wider-support fixtures at q=2,3.
Source hashes are retained separately in this review.

## Exact transport and phase identities

For arbitrary actual skew J let `J_s=F_s J F_s^-1` and
`B_s=P_s N_0^-1 J`. The crucial one-step identity is

    F_(2t)^-1 P_(2t) J_(2t-1) N_(2t-1)
      = B_(2t) F_(2t-2)^-1.

Substitute the definition of J_(2t-1) first. P_(2t) commutes with
F_(2t-1), while `N_(2t)^-1 P_(2t)=P_(2t)N_0^-1`.
The fresh factor at the right cancels in
`F_(2t-1)^-1 N_(2t-1)=F_(2t-2)^-1`. No interchange of J with a fresh
factor occurs. The base is `F_4^-1 T_2=B_4 F_3^-1`. Thus, with the even
indices explicitly retained,

    F_(2q)^-1 T_q=(B_(2q) B_(2q-2)...B_4) F_3^-1.

Using `Du=(B_(2q) B_(2q-2)...B_4)B_3J` yields

    L=F_(2q) J^-1 B_3^-1 F_3^-1 P_3
     =-N_(2q) N_(2q-1)...N_3.

The sign follows from `J^-2=-I`, not a tableau-only argument. Similarly,

    Q=J^-1 B_1 J=J P_1 N_0^-1,
    (F Q^-1 F^-1)(FJ)=F N_0 P_1.

The latter has full native rank m because F N_0 is the disjoint product
on all planes and P_1 is physical monomial. These are whole-field operator
identities, including phase. An incorrect skew square or discarded global
unit would invalidate these equalities even if some binary ranks matched.

The scalar topology must still supply the indicated transported direction
and inverse dual row, isolated in one current bank, and the deletion defect
`C=F_(2q)Du^-1F_(2q)^-1`. These are explicit hypotheses in the all-q
tariff. The independent finite audit reconstructs every q2/q3 original
column, both literal inverse orders, the complete actual column/inverse-row
transport, and the current n-by-n deletion defect after pulling it back
through the literal prefix. Thus these hypotheses are source-bound for the
36 retained finite fixtures. They are not inferred at all q from sampling.

## Inventory cancellation, including negative d

At f=1 put `r=nu(FJ)`, `d=r-2k`, `a_s=nu(J_s)` and
`w=nu(FQ^-1F^-1)`. At general f use actual ranks and replace every constant
arity c by cf, or divide all ranks by f pointwise. No uniform tensor or
parity premise is needed for the written inequality.

The exact factorization

    FJ=(F F_s^-1) J_s F_s

implies `a_s>=d` for every s. This remains a valid weaker lower bound if
d<0. The full Q-target product above gives `w>=m-r=2-d`.

Let `S=sum_(t=2..q) a_(2t-1)`. From the actual transport product,
`rho=nu(T_q)<=S+2(q-2)`. Since `ell=nu(L)=4q-4`, the two separately charged
replacement sites satisfy

    nu(U)+nu(V)>=abs(ell-rho)>=2q-S.

This form does not require U to be monomial: if U is a charged Clifford,
the same triangle inequality includes its native charge. It does require
the native costs of U and V to be counted at these separate sites; a new
cross-cut fusion, additional coupled sites or changed scalar word is not
covered by that inventory.

The N-only bill is `A=n(2k-1)`. There are two J_0 calls, one of each
J_2,J_4,...,J_(2q), and two of each J_3,J_5,...,J_k. Thus the complete J
inventory has `3q+2` occurrences. Subtracting one paid occurrence at each
selected index3,5,...,2q-1 leaves `2q+3=n+1` occurrences. Hence

    M >= A+2q+sum_remaining a_s+w
      >= A+2q+(n+1)d+w
      >= n*r.

Equivalently, the last difference is exactly `d+w-2>=0`. This derivation
does not need to assume `2q-S` positive. A negative replacement lower
bound is harmless; the selected paid J charges were subtracted from both
sides consistently. It also does not replace a negative d by zero while
silently keeping the same equality calculation.

The extra grid includes `J=F^-1` at q=2..8. Then FJ=I, `d=-2k`, and the
same rank inequalities remain valid at the most negative possible d. These
are rank-degeneracy controls, not recursive targets. The grid also includes
`J=N_0`, for which r=m, d=2, w=0 and the optimistic mass inequality is an
equality. The retained wider-support kernels include odd native ranks.

The rank result is unweighted. The moment consequence for
`sum(a_i/r)^sigma`, `0<sigma<=1`, follows from
`(a_i/r)^sigma>=a_i/r` only when all positive children have `a_i<r` and
the complete caller uses the stipulated equal-volume full-bank child
normalization. It is not a statement about arbitrary heterogeneous-volume
moments, unpaid monomial/scalar scans, or a new multiplication bound.

## Optional support-length strengthening

For an arbitrary finite-dimensional unitary G define

    lambda(G)=log2 max(maximum row support, maximum column support).

It is invariant under unitary monomial left/right factors and under inverse
because the adjoint exchanges row and column supports. Matrix multiplication
gives each product row support at most the product of the two maximum row
supports; the analogous column argument is identical. Therefore
`lambda(AB)<=lambda(A)+lambda(B)`, with arbitrary cancellation allowed.

Every displayed operator identity, support-independent transport argument,
triangle inequality and inventory cancellation above therefore remains valid
with lambda in place of native Clifford rank. Native rank-a Fourier/chirp
blocks have row and column support `2^a`, while physical address/phase
monomials have lambda zero. F, L and F N_0 P_1 have respectively support
lengths2k,4q-4,m. This proves the same conditional inequality
`M>=n*lambda(FJ)` for arbitrary unitary skew J, if each separately charged
unary site's implementation cost is at least its lambda. No Clifford,
two-plane, tensor or parity premise is used in this algebraic extension.

That implementation premise is essential. It holds for unary compositions
of native blocks and physical monomial scans, by subadditivity. It is not
automatically justified for a coupled-bank implementation with helper
fields and scalar ADD path sums whose additions are omitted from the
charge. Treating a bank ADD as rank-free in that larger implementation can
increase matrix support. Such implementations need their own paid support
or scan argument; this review does not import one silently. In particular,
the extension is not a global lower bound for arbitrary nonlinear/coupled
suppliers. For a recursive stock interpretation, FJ must still be an admitted
native/flat target of the corresponding arity, not merely an operator with
some logarithmic support value. `lambda_controls.py` supplies exact small
orthogonal/monomial examples and a non-Clifford skew example iH, including
strict support cancellation. These corroborate, rather than prove, the
arbitrary-dimensional union-bound argument.

## Evidence domain and remaining obligations

The independent producer does not execute the parent's kernel builder.
It reads the saved J data, reconstructs N/P/J_s and the semantic event
operators, lowers their exact X-character actions to physical Gaussian
circuits using the previously frozen independent checker, and replays the
complete actual default source words and inverses. The saved two-site bill
is separately recomputed from the full literal default inventory, deletion
rank and isolated rank-distance attainment; no new selected-child recipe
is admitted by that invoice check. The 36 finite q2/q3 cases and
the 14 extreme-rank tests pass in normal and optimized Python. All-f phases
are represented by literal tensor circuits plus the exact four Gaussian
residue coefficients; they are not extrapolated from f=1 equality.

The supplementary caller proof in
`../trajectory-pairing-search/arbitrary-skew-review/PROOF.md` supplies an
explicit all-parameter column/dual-row induction for the pinned repeating
suffix. Its base table, nonfinal encoder table, even-query cancellation and
paid occurrence count agree with the actual update rules. This establishes
the isolation/inventory premise for that specified suffix independently of
J's support. It does not construct a new all-q start-to-finish selected-native
compiler. Its initial executable pin referred to an earlier root proof;
the source-bound final-pin derivative is identified in this review's handoff.
The moment
normalization, selected-child recipes, ADDRESS/COPY/source costs, precision,
owner stock, tape/storage and outer transfer remain distinct. No global
caller optimality, formal-kernel certificate, BIT result or new kappa is
claimed. No frozen predecessor file was modified.
