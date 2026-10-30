# Rank-batched Gaussian boundaries with exact dual tariffs

Dugongue, with substantial OpenAI Codex assistance. Informal mathematics only. The purpose is to apply a whole ordinary boundary matrix at its actual Gaussian correction rank, instead of paying independently for every crossed ADD in one scalar program. No numerical search, executable proof check, web search or Lean verification is used.

## Source context and scope

The local `HETEROGENEOUS-CONTROLLER.md` and `FREE-ENDPOINT-GAUGES.md` distinguish an actually diagonalized supplier from a coupled local B/C port. They give the exact physical boundary G_out M G_in^(-1), where M is an ordinary scalar program and G consists of central Gaussian row gauges. The present note constructs that complete boundary directly. It applies to those scalar boundaries, not to an arbitrary Clifford word whose coefficients are themselves address operators.

The shared library's fixed-circuit and support principles motivate preserving one actual all-input map. `Mathproof/SymplecticTITOCIBalancedCoevaluation20260901.lean` supplies the primal/reciprocal-dual viewpoint, and `Mathproof/LinearAlgebra/SchurBlockElimination.lean` records exact elimination rather than an assumed inverse. The rank factorizations and nullity identity proved below are classical finite-dimensional linear algebra. No historical or exhaustive project novelty is claimed.

Credit the retained native controller, quotient and restriction work of Cinna Davis, DaysSky, Cao Yifan, Dugongue, Nick Petalas, Ryanson Jonathan, zxv, Jacob Alan Sussman and their compiler predecessors. The new contribution here is the explicit boundary construction, owned storage, dual-price equality and profile substitution interface.

## Definitions

Let K be a field and V a finite-dimensional K-vector space. A role field is an arbitrary vector of V. Fix an invertible Gaussian operator Q on V. Ordinary operations in this note are K-linear combinations between role fields and explicitly supplied ordinary address monomials. Scalar role matrices commute with Q. A Q or Q^(-1) application to one arbitrary role field is one charged rank-one Gaussian job. In the actual lifted setting Q is the central-axis Gaussian over all its digit columns; its inverse differs by its known even-power monomial and has the same Gaussian rank.

There are n independent input fields. Let M be an invertible n by n scalar matrix over K. Give each input role j a gauge bit a_j and each output role i a gauge bit b_i. Put

    G_a = diag_j(Q^(a_j)),    G_b = diag_i(Q^(b_i)),
    F = G_b M G_a^(-1).

Define input groups A_0,A_1 and output groups B_0,B_1 by their gauge bits. Write M_uv for the block with rows B_u and columns A_v. Empty blocks have rank zero. Let m_0=|A_0| and n_0=|B_0|. All ranks below are over K.

## B1. Exact whole-boundary decomposition

**Theorem.** The physical boundary F has the block form

    [ M_00          M_01 Q^(-1) ]
    [ M_10 Q        M_11        ].

It can be applied using exactly

    r = rank(M_01) + rank(M_10)

charged Gaussian jobs in the construction below, plus ordinary linear work. This is a sufficient tariff, not a lower-bound assertion against all possible uses of the concrete Q.

**Proof.** A block with output gauge u and input gauge v has coefficient Q^u M_uv Q^(-v). Scalars commute with Q, giving the displayed form.

Choose rank factorizations M_01=U_01 V_01 and M_10=U_10 V_10, where the inner dimensions equal their respective ranks. Such factorizations exist constructively: choose independent columns as U, express every column in that basis, and place the coordinates into V. Form V_01 x_1 in r_01 temporary fields and apply Q^(-1) separately to each. Ordinary multiplication by U_01 then produces M_01 Q^(-1)x_1. Independently form V_10 x_0, apply Q separately to its r_10 fields, and spread by U_10. Add the ordinary direct terms M_00 x_0 and M_11 x_1. This gives every physical output exactly, on arbitrary mutually independent inputs. No Q is declared free and no temporary linear combination is mistaken for an independent productive target. ∎

For a fixed finite boundary template this uses O(n²) ordinary scalar operations per address, plus its explicitly counted Gaussian jobs. A low-rank boundary may have a substantially smaller Gaussian tariff than a long sequence of individually priced ADDs.

## B2. A complete owned-buffer realization

**Theorem.** B1 can be realized with O(n) owned field buffers, all zero on exit, without overwriting a source before its last read. It preserves every unrelated main or helper field. The net map on the n main fields is exactly the invertible boundary F.

**Proof.** Clear n owned output buffers and at most r temporary buffers. Read the immutable main input bank to accumulate both direct output blocks and the rank-factor combinations. Once a combination is complete, apply its charged Q or Q^(-1) job and accumulate its U multiple into the output bank. A temporary is cleared after its last use and may be reused. No further input source is read after the two output blocks are complete. Swap the main and owned output banks, then clear the old input bank, which now occupies the owned bank. The operation is the same all-input invertible main map F; no independent input is lost from that main endpoint. Every other field was untouched. ∎

The model here permits clearing owned buffers, as in the retained native recoders. This theorem does not claim a reversible computation with no erasure, nor does it borrow an uninitialized helper as though it were a zero input. Gaussian-child workspace and cleanup retain the child service's own charged contract.

## B3. A strict sharing example for a dense boundary

**Theorem.** Let u and v be nonzero scalar vectors and take

    M = [ I    u v^T ]
        [ 0      I   ],

with the first output/input group carrying gauge 0 and the second group gauge 1. The complete physical boundary needs one charged Q^(-1) job in B1. If all entries of u and v are nonzero, the literal coordinate-ADD expansion of the upper-right block contains |u||v| crossed terms; implementing each as a separate fresh query uses that many jobs.

**Proof.** The upper-right block has rank one. Its action is u times Q^(-1)(v^T x_1). Compute the scalar combination v^T x_1 once in one owned temporary, query Q^(-1) once, and add its u multiples to the first group. The literal expansion has one nonzero coefficient u_i v_j for each pair (i,j); its stated separate-query implementation therefore makes one query per pair. The theorem compares these two explicit constructions, not every possible caching strategy. ∎

The sharing is across one fixed input snapshot. There is no reuse of a stale query after one of its source fields has changed. This is why the matrix-level construction is safe even when a chronological ADD program would change its intermediate inputs repeatedly.

## B4. An elementary inverse-block nullity identity

**Theorem.** Let M:U→W be an isomorphism of n-dimensional spaces with coordinate bases. For any row-index subset I and column-index subset J of M^(-1),

    rank((M^(-1))_(J,I))
      = rank(M_(I^c,J^c)) + |I| + |J| − n.

Here I refers to coordinates of W and J to coordinates of U; the subscripts keep those two spaces distinct.

**Proof.** Restrict M^(-1) to the coordinate space W_I and then project to U_J. Its kernel consists exactly of y in W_I with M^(-1)y in U_(J^c). Thus its kernel is W_I intersect M(U_(J^c)). The map obtained by applying M to U_(J^c) and projecting to W_(I^c) has rank rank(M_(I^c,J^c)) and domain dimension n−|J|. Its kernel has dimension n−|J|−rank(M_(I^c,J^c)); this equals the intersection dimension just identified. Subtract that dimension from |I| to obtain the claimed rank. ∎

The formula also covers empty groups. Its right side is nonnegative because it equals an actual rank.

## B5. Forward and reciprocal-dual boundaries have equal tariffs

**Theorem.** Use the reciprocal-dual Gaussian Q_d=Q^(-T) for the inverse-transpose boundary. Its two crossed-block ranks satisfy

    rank((M^(-T))_01) = rank(M_10)+n_0−m_0,
    rank((M^(-T))_10) = rank(M_01)+m_0−n_0.

Consequently the B1 tariff for the forward boundary and for its actual inverse transpose is identical:

    rank((M^(-T))_01)+rank((M^(-T))_10)
      = rank(M_01)+rank(M_10).

**Proof.** Transposing the inverse changes its block 01 into the inverse block with rows A_1 and columns B_0. Apply B4 with I=B_0 and J=A_1; their complementary M block is M_10, and |B_0|+|A_1|−n=n_0−m_0. The other equality follows with I=B_1,J=A_0. Sum them.

For the actual operator, direct inversion and transposition gives

    F^(-T) = G_b^(-T) M^(-T) G_a^T.

This has the same binary in/out gauge partitions with Q replaced by Q_d, since G_b^(-T)=diag(Q_d^(b_i)) and G_a^T=diag(Q_d^(-a_j)). Apply B1. The actual symmetric central Gaussian has Q_d=Q^(-1), whose charged rank is the same; all even-power monomials remain explicit. ∎

This is a useful compatibility statement for mirrored suppliers: the cost improvement is not obtained by silently ignoring the backward orientation.

## B6. Coefficients, guards and preparation are finite mathematical data

**Theorem.** Suppose M has rational entries, and a common scaling makes their integer numerators have magnitude at most 2^H, with the scaling denominator explicitly supplied. The rank factorizations in B1 can be chosen with coefficient numerator and denominator bit lengths O(n(H+log(n+1))) plus the supplied common denominator length. They can therefore be prepared by exact finite elimination, independently of data.

**Proof.** Choose independent columns and an invertible square minor of their full rank r. The coordinates of any other column in that basis are given by solving the r by r minor system. Cramer's rule expresses each coordinate as a ratio of r by r determinants. The determinant expansion has at most r! terms and each product has magnitude at most 2^(rH). Thus the determinant numerators have at most rH+log2(r!)+O(1) bits, bounded by O(r(H+log(r+1))). Common denominator factors cancel or contribute their explicitly supplied lengths. The independent columns give U and these coordinates give V. This is a finite construction, not an oracle for a smallest circuit. ∎

For a fixed finite provider template, n and these coefficient sizes are fixed before the external input length grows. Their ordinary work is an actual finite multiple of the field volume, and their coefficient/partial-sum bounds give a fixed extra guard. If the template itself grows, these costs and guards must be charged as functions of n and H; the theorem does not turn growing matrices into constant-time instructions.

## B7. Safe substitution into an already completed provider

**Theorem.** Consider a completed all-input independent-output supplier, with both orientations supplied, whose chronological word includes an ordinary scalar boundary M implemented under the stated in/out gauges. Replace that boundary by B1–B2 and perform the corresponding B5 replacement in the inverse transpose. Then the exact endpoints, independent main/helper inputs and Gaussian target ranks are unchanged. If the replaced implementation used c charged rank-one jobs and B1 uses r<c, the paid Gaussian count drops by c−r in that orientation. Every target-minus-paid concave moment increases by exactly c−r.

**Proof.** B1 proves equality of the full boundary operator, rather than equality of selected test outputs or a local parity mask. B2 supplies actual cleanup and preserves every outside field. Composing an equal operator inside the unchanged chronological word therefore gives the same all-input endpoint and same independent targets. B5 supplies the actual dual operator with its equal crossed-rank tariff. All other Gaussian calls are unchanged. The decrease in the paid sum at exponent t is (c−r)1^t=c−r, for every real t. ∎

The theorem states the exact contribution a completed boundary replacement would make. It does not assert that the currently selected supplier has c>r, nor that a changed B/C local word has already been completed. Its additional finite ordinary work and finite guard belong to the subsequent uniform-compiler cost bound. An exact positive moment is one input to that compiler, not by itself a proof of an improved multiplication exponent.

## B8. Multi-axis boundary blocks and complete rank tariffs

**Theorem.** Let Q_1,...,Q_s be commuting invertible Gaussians on disjoint address axes. Give each input and output a binary gauge vector. Partition input roles by a in {0,1}^s and output roles by b. For each scalar block M_ba choose a rank factorization of inner dimension r_ba. Then the whole boundary can be applied with, for each a≠b,

    r_ba jobs of the explicit product Q^(b−a),

plus ordinary work. Each such product has charged Gaussian rank |supp(b−a)|, with inverse orientations normalized by their actual even-power monomials.

**Proof.** The physical block is Q^b M_ba Q^(−a)=M_ba Q^(b−a). Apply the rank-factor construction of B1 to that whole block. The commuting product is a tensor Gaussian on precisely the axes whose gauge entries differ; inverse factors differ from forward ones by the supplied even-power monomials. Treat the a=b blocks ordinarily. Distribute and sum the explicitly specified output blocks. ∎

Here the safe tariff is the sum over displayed blocks. No equality of forward/backward weighted tariffs is inferred for arbitrary multi-axis rank weights; B5 proved that equality only for the single-axis count. Nor is a whole rank-r product replaced by r separate rank-one jobs when its actual service permits one rank-r call.

## Mathematical contribution and remaining κ task

These results construct a cheaper boundary whenever its crossed scalar blocks have low rank relative to the literal query expansion. They include arbitrary independent fields, cleanup, both orientations and actual coefficient data. They are applicable to a complete already proved caller and do not use an unproved Gaussian gadget.

To obtain a higher κ one must instantiate B7 in a specific complete profitable provider, or complete a new provider whose actual boundaries satisfy this tariff and whose whole paid moment is stronger. The present note supplies neither that missing particular instance nor a numerical κ. The companion inverse and consumer notes develop independent positive mechanisms that can be joined only through their exact stated interfaces.
