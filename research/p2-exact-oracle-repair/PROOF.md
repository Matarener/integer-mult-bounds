# Exactly 240 returns in the frozen p2 oracle model

The minimum is 240 new returns, for every width f >= 72, in the enlarged
linear-oracle model of PR5587. Keep its 39 observed bank fields, original paid
input expressions, capacities, ordinary algebra and target credit fixed.
New returns may be arbitrary linear fields and may use earlier new returns.
This is a scoped negative result. It does not construct 240 native calls.
It does not change complete kappa or the selected result.

## Credited premises

Use the source proof at commit 49811a9a37cc1b71bcbe851dd20da3cbf479ff35:
[PR #5587](https://github.com/CrocSwap/integer-mult-bounds/pull/5587),
[proof](https://github.com/aliromman/integer-mult-bounds/blob/49811a9a37cc1b71bcbe851dd20da3cbf479ff35/research/p2-full-history-deficit/PROOF.md).
At f >= 72 the ordinary algebra A is the twisted group algebra of the full
projective monomial Clifford group H on 17 axes. Write h = |H|.
The pointwise faithfulness premise is credited to
[PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526).
Sections 4 and 5 of the source proof give these two results:

* The required target module has deficit at least 224h + r, where r is the
  complex rank of right multiplication by L = I - C3 C1 on A^112.
* A linear oracle can supply the targets with 240 returns. The construction
  uses 224 negative targets and 16 factored repair rows.

Each new same-capacity return adds at most h dimensions, including with
feedback. We retain these source results as premises. The new proof bounds
r/h strongly enough to close the integer gap from 225 through 240.

## 1. Two rank-eight defects

Let C be the pinned scalar matrix F^T. The checker verifies C^2 = I and
tr(C) = 96. Thus P = (I-C)/2 has rank eight. Write P = UV with U of size
112 by 8 and V of size 8 by 112. Set D_s = diag(K_s), where the K_s are the
pinned signed monomial normalizers in the two fresh blocks. Then

    P_s = D_s^-1 P D_s = U_s V_s,
    L = 2P1 + 2P3 - 4P3 P1
      = [U1 U3] [[2I, 0], [-4 V3 U1, 2I]] [V1; V3].

Use the regular representation of A. Its group basis is orthonormal and its
signed monomials are unitary, for every phase cocycle. Left and right regular
matrix ranks agree: the conjugate-linear map x -> x* converts right
multiplication to left multiplication by the adjoint, which has the same rank.
The middle block above is invertible. Let delta_c be the dimension of the
intersection of the two column spaces and delta_r the corresponding row-space
intersection. The rank inequality for a product gives

    r >= 16h - delta_c - delta_r.                      (1)

## 2. One projector bounds both intersections

The scalar orthogonal projector R onto im(P) has rank eight, is real symmetric,
and has every diagonal entry equal to d = 1/14. The checker derives R from
eight independent columns with an exact Gram inverse. It verifies all entries
of R^2 = R, RP = P and the constant diagonal using integers after scaling by 28.

Let W have entry -1/11 at the eight positions where C_ii = 12 and entry 1
elsewhere. The checker verifies R W P^T = W P^T. Both spaces have rank eight,
so W im(P^T) = im(P). Since W is invertible and commutes with both D_s,
it maps both row spaces to the corresponding column spaces. In particular,
delta_r = delta_c. Division by 11 is only an invertible change of metric in
a rank proof. It is not a proposed ordinary operation or an unpaid map.

The two orthogonal projectors onto the column spaces are
R_s = D_s^-1 R D_s. For two orthogonal projections E,F, their common space has
eigenvalue one in EFE; the other eigenvalues are nonnegative. Therefore

    delta_c/h <= Tr((R1 R3)^2)/h.                     (2)

Here Tr is the ordinary trace on the 112h-dimensional regular space.

## 3. Exact second moment

Set J_i = K_(1,i) K_(3,i)^-1. The checker proves that all 112*111 ordered
products J_i J_j^-1 with i != j have different binary linear parts. None has
the identity linear part. The 112 diagonal products are exactly identity,
including phase. Thus these are 12433 distinct classes in H. This test uses
all 17 axes. A separate chronological action checks each signed product on
all 17 basis addresses. The phase functions are linear, so these basis tests
check the full signed maps.

In a twisted regular group algebra, the normalized trace of a nonidentity
group element is zero. Expand the trace in (2) and group ordered pairs by
J_i J_j^-1. Every off-diagonal class has one pair. The identity class has the
112 diagonal pairs. The coefficient in each surviving term is positive phase
one: a group word is followed by its exact inverse. Thus

    tau = Tr((R1 R3)^2)/h
        = d^2 sum_(i,k) R_ik^2 + d^2 sum_(i != j) R_ij^2
        = 2*8*d^2 - 112*d^4
        = 27/343.                                    (3)

The verifier also sums the grouped expression directly, without this reduction:
for each pair class, sum R_ij R_kl R_ik R_jl over its pairs (i,j),(k,l).
The first moment is 4/7; it would not close the integer gap. The second moment
does so. No computation of an irreducible decomposition or exact r is needed.

## 4. Integer optimum

Equations (1)--(3) give

    r/h >= 16 - 54/343 = 5434/343,
    q >= (224h+r)/h >= 82266/343 > 239.

The number q of returns is an integer, so q >= 240. The credited 240-return
construction attains this bound in the same enlarged oracle model. This proves
the exact minimum. The full right-multiplication rank may still exceed this
lower bound; its exact value cannot improve the minimum return count.

## Verification and limits

The registered normal and optimized Python checks use exact arithmetic only.
They verify the source hashes, involution, full projector identities, balanced
row spaces, all ordered signed products, and both forms of the second moment.
Four controls reject repeated normalizers, a wrong scalar diagonal, a singular
normalizer and a false 239-return capacity. The committed receipt is compared
with a fresh result. The package uses the standard library.

We did not replay all 39 source observations, the full Clifford faithfulness
proof, a native compiler, a physical caller, the selected cold replay, or the
complete kappa calculation. Those source statements remain credited premises.
The earlier 225-return tariff obstruction already excludes this frozen caller;
this proof settles its exact oracle repair optimum. A productive next caller
must change a frozen input, observation, ordinary alphabet, capacity or target.

## Attribution

Dugongue supplies [PR #4948](https://github.com/CrocSwap/integer-mult-bounds/pull/4948)
and its native source. Chris R / Clear1nsight supplies
[PR #4978](https://github.com/CrocSwap/integer-mult-bounds/pull/4978), the D-left
audit and the fixed-alphabet and owned-reset clarifications. Ali Romman supplies
the consumed PR5587 deficit and oracle construction, PR5526 faithfulness and
[PR #5449](https://github.com/CrocSwap/integer-mult-bounds/pull/5449) history model.
josecarlosgonzalezroque-design supplies the
[PR #5570](https://github.com/CrocSwap/integer-mult-bounds/pull/5570) bridge audit.
Retain Cao Yifan, Cinna Davis, DLamdata, zxv and their native, controller,
Clifford and interval lineage, as recorded in the source proof.
Projection moments and the product rank inequality are classical. The balanced
projector, exact pair-class certificate and sharp 240-return conclusion here
are by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
