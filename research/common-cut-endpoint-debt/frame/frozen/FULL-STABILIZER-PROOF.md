# Every unary current-cut insertion retains a Y endpoint deficit

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This is a local written all-parameter obstruction, with exact finite operator
checks. It establishes no new conditional κ and is not a formal-kernel proof.

The result replaces a failed extension of the earlier common-corner argument.
It does **not** assume that leakage into a completed fresh block is absorbing.
Legal dressed swaps really can move that leakage into future support. The
invariant below is the maximum row support of the exact factored operator.

## 1. Model and exact representatives

Fix an integer `L>=1` and split the binary address space orthogonally as

    C ⊕ F_0 ⊕ ... ⊕ F_(L-1),   dim C=2, dim F_s=5,
    m=2+5L.

Write `C=span(p,q)` in the canonical chart, with p and q orthogonal norm-one
directions. The third D4 orbit root is the characteristic vector of the
five-dimensional fresh complement; it is not a single fresh coordinate.

All operators act on the entire array of arbitrary Gaussian dyadic values.
For one address bit in direction v use the actual positive Gaussian Clifford

    C_v=((1+i)I+(1-i)X_v)/2,  C_v^2=X_v,  C_v^-1=C_v X_v.

Let `F_s` be the product of the five positive coordinate C gates on `F_s`,
and `F_<=s=F_s ... F_0`. These products commute, and their actual adjoints
are retained. Let `R=C_p C_q^-1`. A local normalized source pre-operator
is `pre_s`, a monomial on `C⊕F_s`, and put `P_s=pre_s^-1`.
It is identity on every other fresh block. Different P_s need not commute.

The pinned OPEN alphabet admits the forward shear F(A_s) and backward shear
B(A_s^-1), with `A_s=C_p^-1 pre_s C_p`. It has the zero-helper profile
`H_1=8,H_2=40,H_3=16`, native rank mass136 per invocation. Both orientations
use the same pre-X/post-Y corrections. The frozen ordered B1 identity gives

    E=A_2^-1 Z A_1^-1 H A_0^-1

on both arbitrary input columns after the signed exchange. It imposes no
commutation or involution premise on A_s,H,Z. `verify_free_word()` independently
checks this two-column identity in the free integer group algebra. The generic
L expression below is an operator theorem whenever a caller produces that
ordered relay expression; the present free-word check specifically certifies
the two-bank B1 word, L=3. It is not a new L-stage scalar caller construction.

At cut s the nominal physical fronts are

    D_X,s=C_p F_<=s,   D_Y,s=C_q F_<=s.

A legal common logical unary insertion H_s has physical X pullback

    M_s=D_X,s H_s D_X,s^-1,

which must be a monomial. Its simultaneous Y pullback must also be monomial.
The theorem only uses the X condition, so it covers the complete simultaneous
stabilizer without needing a finite generating set or a classification of it.
In fact M_s may be **any** invertible monomial, with arbitrary permutation and
nonzero diagonal phases. It need not be affine, quadratic, Clifford, local in
the fresh blocks, or a tensor product. Its actual address/phase work is paid.

Conjugating the logical insertion into the source-normalizer chart gives

    J_s=C_p H_s C_p^-1=F_<=s^-1 M_s F_<=s.

Thus, with no dropped phase or replacement of an adjoint by a positive gate,

    Q=P_(L-1) J_(L-2) P_(L-2) ... J_0 P_0.

For the canonical representatives used in the frozen endpoint producer,
the isolated original input operators after the terminal signed exchange are

    X_out=F_global X_p Q,
    Y_out=F_<=L-1 Q R.

The actual Pauli decorations of native representatives are monomials.
They can be retained in the corresponding end factors or M_s. Conjugating
a Pauli through a Clifford yields a Pauli; no row-support bound changes.
The proof does not infer equality of actual operators merely from their
binary tableaus. The displayed factorization is an exact operator identity.

## 2. Telescoping, with all phases retained

For `s>=1`, P_s acts only on C and F_s, while F_<=s-1 acts only on earlier
fresh blocks. They therefore commute as actual tensor-factor operators.
Consequently

    F_<=s P_s F_<=s-1^-1=F_s P_s.

Substitute the exact J_s expression into Y_out and apply this identity from
left to right. All adjacent past-frame factors cancel with their **actual
inverses**, giving

    Y_out=(F_(L-1) P_(L-1)) M_(L-2)
             ... (F_1 P_1) M_0 (F_0 P_0 R).                (1)

For B1 specifically,

    F_2 F_1 F_0 P_2 (F_1 F_0)^-1 M_1 F_1 F_0
      P_1 F_0^-1 M_0 F_0 P_0 R
      = (F_2 P_2) M_1 (F_1 P_1) M_0 (F_0 P_0 R).

No M_s is moved through a fresh Fourier operator. In particular M_s may
freely mix completed and future fresh directions. This is why the failed
absorption premise is unnecessary.

## 3. The rank and row-support bounds

For a Clifford U on n address bits define its native rank by `rank B(U)`,
where B is the upper-right binary symplectic block. A rank-r Clifford has
exactly `2^r` nonzero entries in every matrix row. Equivalently, its exact
native lowering consists of one r-coordinate child between monomials.
In particular `F_s P_s` has native rank5, since P_s is monomial.

The first factor is special. The actual OPEN source geometry and normalization
give, for every source pre-normalizer in the declared common-F family,

    rank(F_0 P_0 R)=3  on each of the four C ports,
    rank(F_0 P_0 R)=5  on each of the eight A/B ports.        (2)

One source-bound derivation is `post S pre=T`: both post and pre are
monomial and `T=F_0` up to a retained Pauli. Hence `S R=post^-1 T P R`.
The pinned actual source operators have native ranks3/5 for S R, so (2)
holds for every admitted normalizer, not merely the saved winners.
`ENDPOINT-GAUGE.md` gives the independent split-Lagrangian derivation.
The new verifier reconstructs all12 actual winners and checks their rank3/5
literal lowerings, including global phase with an independent sparse Gaussian
evaluator. The universal assertion uses the source identity; these12 checks
alone are not an exhaustive covering of normalizers.

Let `s(U)` be the largest number of nonzero entries in a row of U. For any
matrices of compatible dimensions,

    s(U V) <= s(U) s(V).

Every invertible monomial has s=1. Applying this inequality to (1) gives

    s(Y_out) <= 2^(5(L-1)+3) = 2^(m-4)   on C,
    s(Y_out) <= 2^(5(L-1)+5) = 2^(m-2)   on A/B.            (3)

If the insertions are Clifford, (3) implies the exact native-rank bounds

    rank(Y_out) <= m-4  on C,
    rank(Y_out) <= m-2  on A/B.                            (4)

The same conclusion follows directly from Bruhat-rank subadditivity:
`B(UV)=A(U)B(V)+B(U)D(V)`, so native rank(UV) is at most the sum of
native ranks. The support proof is stronger because the inserted monomials
need not be Clifford and Y_out itself need not be Clifford. Any native
full-rank endpoint, even with arbitrary monomial adapters, has `2^m` nonzero
entries per row. Equation (3) therefore excludes it in either case.

The inequality does not depend on X_out. Requiring X_out to have full rank
cannot remove Y's deficit. The identity insertions attain (4) for the saved
charts for every L: their inverse-pre common corners are diag(1,0) on A/B
and0 on C, and disjoint support makes their products the same corners.
Thus extra unary current-cut insertions cannot improve the best Y rank of
that frozen relay, although they can lower it or change X.

## 4. All chunk sizes, arbitrary inputs and a cost consequence

For a tensor-column chunk parameter `f>=1`, each F_s acts on5f coordinate
bits. The first factor in (2) acts on3f or5f native bits. Every P_s and
every admitted physical M_s remains monomial. Thus (3) becomes

    s(Y_out) <= 2^((m-4)f)  on C,
    s(Y_out) <= 2^((m-2)f)  on A/B,

whereas a full native m-coordinate endpoint has row support `2^(mf)`.
This is an operator obstruction on arbitrary input arrays; it uses no clean
target promise, dirty-helper promise, one-hot fitting, finite-character
expansion, or approximation of the phases. The normalized OPEN local boxes
have no ordinary helper or private field to restore.

Any **separate unary** native completion on an isolated Y output must have
total positive native rank at least4f on a C port and2f on an A/B port:
subadditivity would otherwise keep the completed endpoint below mf. Across
the12-port Y bank this is at least `4*4+8*2=32` native arity units before
tensoring. This is a lower bound, not an optimal completion recipe, child
histogram, primitive count, or recursive moment. Multi-field cleanup is a
different model and must be analyzed on its actual coupled operator.

The inherited local profile136 remains a valid zero-helper local resource.
All normalizer, insertion, permutation, sign and phase scans remain paid.
The theorem does not provide a favorable complete recursive bill or κ.

## 5. Exact evidence and limits

`full_stabilizer_bound.py --write` produces `FULL-STABILIZER-BOUND.json`.
Ordinary replay omits `--write`; optimized replay uses `python3 -O -B`.
The verifier checks12 ports at L=1,3,5,9 with prescribed dense simultaneous
stabilizers, not a random search. Independent packed binary arithmetic checks
global products. Complete sparse Gaussian columns at actual B1 arity17 for
an A and a C port fix the exact factorization phase after signed-tableau
equality. Four named controls detect an undressed swap, an omitted common
chirp, an adjoint/positive past-frame error, and an undetected i global phase.

The full operator theorem is (1)-(3), not an inference from these48 cases.
No claim of formal-kernel proof, optimal recursive exponent, full precision
contract, owner stock, physical tape realization, hosted CI or multiplication
theorem verification is made.

This theorem fixes the unary insertion topology, the common2/own-fresh5 local
support, the raw OPEN boundary, and the canonical relay endpoint expression.
It does not cover a changed scalar word with retained bank-dependent codes,
new local source/target interfaces, or arbitrary bank mixing. A nonlocal
multi-bank linear operation is not a monomial on one isolated input array:
after transport through differently coded banks, its isolated Y coefficient
can be a sum of multiple operator paths. Equation (1) would then be replaced
by a sum, and its single-product row-support bound would need a new proof.
Simply adding more scalar bank additions without changing those paths does
not by itself certify an escape or a favorable cost.

## Source pins and attribution

All predecessor files remain read only under
`/Users/ross/git/math/.research-automation/runs/kappa-major-20261018T1330Z`.

| Frozen source | SHA256 |
| --- | --- |
| shared-helper-algebra/SOURCE-COMMON-FRAME-INVERSE-SEARCH.json | bc45cf6f3ab114c565fd330d01174092bf4a32d94d3e3e2c49f80ccaa602bb99 |
| shared-helper-algebra/SOURCE-D4-BUS-INPUT.json | 93716ba2a0297c4b468ca7344a9b744fcdaee4013f490443a58ddc7a6610eedd |
| shared-helper-algebra/canonical_endpoints.py | 0bbd62dd84f7f7172a57b04abcccd62831042cc417c491970ede42d257cb41a6 |
| shared-helper-algebra/noncommon_b1.py | 4badaf9158a945da34dd4497508d36483da52a87968b24d0553ef18d858e8c49 |
| shared-helper-algebra/NONCOMMON-B1.json | 7e59465f98810f3daa73a14a15d434ddced3a09ce3fb931eeb81f34721e25cff |
| complex-boundary/paired-pivot/ENDPOINT-GAUGE.md | 52237c3b663221a74d68a18efb7946569342c200446cf7a181860c25718b8618 |
| complex-boundary/paired-pivot/INSERTION-SUPPLEMENT.md | f01718e0987aef7c06198630be1a80824de45970f929073f48e1f2c09208fa50 |
| primary pinned Clifford compiler | 2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962 |

The predecessor complex lane and root supply the source-carrier OPEN boxes,
normalizers and corrected inverse alphabet; the predecessor algebra lane
supplies the noncommuting B1 identity and canonical relay expression; the
complex lane supplies the insertion counterexample and endpoint-gauge review.
This lane supplies the exact telescoping proof and arbitrary-monomial support
obstruction, with independent binary products and Gaussian phase evaluation.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
