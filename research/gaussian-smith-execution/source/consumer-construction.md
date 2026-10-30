# Exact integral delivery for the actual Gaussian tensor

This note gives an explicit all-output program for the matrix defined by GaussianTensorExecution. It accepts arbitrary Gaussian-integer inputs; no exceptional Walsh cache, parity promise or clean public field is assumed. Its complete precision schedule is charged. It does not claim a new numerical κ.

## C1. Actual source and consumer contract

The inspected source defines C = [[i, 1], [1, i]], π = 1 + i, and the normalized tensor A_n = π^(−n) C^⊗n on N = 2^n coordinates. Every Gaussian-integer cube is admitted. GaussianScalarCircuits explicitly supports heterogeneous denominator tags and arbitrary scratch before owned initialization. These source proofs establish arithmetic composition and grids; they do not establish physical tape cost.

The inspected P104 helper-subspace and asynchronous-helper proofs require arbitrary independent public inputs, every full helper output and all main endpoints. Therefore a residual rank bound or presumed input symmetry does not suffice. The construction below computes all of A_n x and neither discards exceptional outputs nor treats a retained helper as a free measurement.

## C2. Integral Smith coordinates

Put

    L = [[−i, 0], [i, 1]],       R = [[1, i], [0, 1]],
    S = L^−1 = [[i, 0], [1, 1]],
    T = R^−1 = [[1, −i], [0, 1]].

**Theorem C2.** These are invertible over Z[i], and

    L C R = diag(1, π²),       C = S diag(1, π²) T.

**Proof.** Adding i times C's first row to its second gives [[i, 1], [0, 2i]]. Multiplying its first row by −i gives [[1, −i], [0, 2i]]. Right multiplication by R clears the upper-right entry. Now 2i = π². Direct multiplication gives the displayed inverses. Their determinants are Gaussian units. No division by 2 or π occurs in a coordinate change. ∎

T is the literal word a ← a − i b. S is b ← b + a followed by a ← i a. Multiplication by i is a signed exchange of real and imaginary components. These are ordinary integral operations, not Gaussian queries.

**Corollary C3.** Writing S_n = S^⊗n and T_n = T^⊗n,

    A_n = S_n diag_u(π^(2|u| − n)) T_n.

**Proof.** Tensor C2 in all axes and extract π^(−n). A diagonal tensor entry selects |u| factors π². ∎

Both changes of coordinates are integral and unimodular. Thus, unlike Walsh projectors, they introduce no further denominator.

## C4. Complete finite-precision response

Residues here are classes in Q(i)/π^p Z[i], so A_n x need not be integral. Let x be integral, p ≥ 1, P = p + n, and z = T_n x. Define q_u = max(P − 2|u|, 0).

**Theorem C4.** The entire response A_n x modulo π^p is determined by z_u modulo π^q_u for every q_u > 0. A channel with q_u = 0 may be replaced by zero. To deliver the answer, assign z_u denominator tag e_u = n − 2|u| and execute the integral S_n circuit with C6's tag-alignment rule.

**Proof.** Changing z_u by π^q_u times an integer changes π^(2|u|−n) z_u by a multiple of π^p. If q_u = 0, its coefficient is already divisible by π^p. Multiplication by S_n, whose entries are integral, preserves this congruence in every output. Apply C3. ∎

A negative tag is an integral scale, not an exact division. It can be represented by signed metadata or realized by an integral power of π. Final tags will all equal n.

**Corollary C5.** If J is binomial with parameters n and 1/2, the diagonal bank's required π-residue digits satisfy

    Q_diag = N E[(p + n − 2J)_+] ≤ N(p + √n/2).

**Proof.** Let Y = n − 2J. Its mean is zero, variance n, and law symmetric. Then (p + Y)_+ ≤ p + Y_+, while E Y_+ = E|Y|/2 ≤ √n/2. ∎

This is the diagonal storage bill, not the whole transform's work bill.

## C6. Both ordinary passes and all propagated moduli

Use an owned copy of x and retain x unchanged.

After k T axes, a coordinate whose processed prefix is u stores its integer value modulo π^max(P−2|u|,0). At the next axis a pair a, b has the same current precision Q. Execute

    a ← a − i b modulo π^Q;
    b ← b modulo π^max(Q−2,0).

The addition precedes b's truncation. Zero-precision branches can be discarded under the charged owned-storage rule.

**Proof.** Every completion of prefix u has final weight at least |u|, so it needs at most P − 2|u| digits. T sends (a,b) to (a−ib,b). The first child keeps the old bound and the second has one additional 1 bit. Induct over axes. This truncates owned work only, never an original public input. ∎

For the S pass, a pair has tags e and e−2, represented values π^(−e)a and π^(−e)π²b, and corresponding precisions (p+e)_+ and (p+e−2)_+. Execute

    b ← a + π² b modulo π^max(p+e,0);
    a ← i a modulo π^max(p+e,0);
    assign tag e to both outputs.

The b update precedes the a phase. Multiplication by π² = 2i is an ordinary binary shift and phase. It supplies exactly the two valuation units missing from b's former precision.

**Proof.** Substitution shows that these represent precisely (i a_value, a_value+b_value), which is S on the represented pair. After k S axes the tag is n minus twice the number of 1 bits in the unprocessed suffix. Each stage removes the next bit from this suffix, so the rule gives exactly the required new tag. At completion every tag is n. Every propagated error remains divisible by π^p. ∎

This explicitly delivers the former exceptional part as well as the bulk. It uses neither a rank-to-grade inference nor termwise division of Walsh projectors.

## C7. A small arbitrary-input example

For n = 2 and bit-order input (a,b,c,d), the T transform is

    z_00 = a − i b − i c − d,
    z_01 = b − i d,
    z_10 = c − i d,
    z_11 = d.

Put w_00 = π^(−2)z_00, w_01 = z_01, w_10 = z_10, w_11 = π²z_11. The outputs are

    y_00 = −w_00,
    y_01 = i(w_00+w_01),
    y_10 = i(w_00+w_10),
    y_11 = w_00+w_01+w_10+w_11.

These equal A_2 x by C3. At p = 1 the needed z precisions are 3,1,1,0. The last channel contributes zero in the required quotient for every a,b,c,d. No input parity has been assumed.

## C8. Full ordinary-work and storage invoice

Define

    B_m(P) = Σ_(j=0)^m binom(m,j) (P−2j)_+.

Weight an addition at precision Q by Q. This is a precise addition-operand mass, not a wall-clock prediction. T stage k has 2^(n−k) B_(k−1)(P) mass. The S masses are the same list in reverse order because S precision depends on the unprocessed suffix. Thus

    Q_add = 2 Σ_(m=0)^(n−1) 2^(n−m−1) B_m(P).

Before pruning there are nN additions: nN/2 in each triangular pass. Phases, shifts, modular reductions, copies and clears require additional comparable visits. Under linear-time bit addition, phase and truncation, the complete arithmetic upper bound is

    O(Q_add + NP + Nn) = O(N n(p+n)).

Neither O(N(p+√n)) total work nor a κ improvement follows from the diagonal-bank bound. Input and conventional output storage can each contain NP bits.

When P ≥ 2(n−1), binomial first moments give the exact identity

    Q_add = N[nP − n(n−1)/2].

Indeed B_m(P)=2^m(P−m), and summing m=0,...,n−1 gives the formula. A literal raw C tensor computes two output additions per pair at common precision P, with addition mass nNP. The new program has strictly smaller addition-operand mass when n>1, at the same unpruned addition count. It remains the same order of bit complexity. Representation, routing and erasure can affect actual runtime and must be compared separately.

A π^Q residue has Q bits of information and can be stored with O(Q) binary bits. At even Q its two Gaussian coordinates are taken modulo 2^(Q/2); odd Q also requires the parity lattice condition or constant-factor redundant rectangular storage. Pay the actual representation conversion. The shift π²=2i is explicit in either representation.

The work array is in-place, with a constant number of extra scalar cells for each routed pair. To add into an arbitrary dirty destination, deliver the complete tagged result by an ADD at the required grid, and only then clear owned work. Every tensor-axis scan, layout permutation, normalization, source read, allocation and clear is charged. If a host lacks the inherited owned-erasure rule, retaining rounding information and a charged modular uncompute are required. No reversible implementation may silently discard intermediate bits.

## C9. Exact precision/size recursion

A raw C tensor modulo π^P also has this literal recursive word:

    h_0 = x_0 − i x_1 modulo π^P;
    h_1 = x_1 modulo π^max(P−2,0);
    u_0 = C^⊗(n−1) h_0 modulo π^P;
    u_1 = C^⊗(n−1) h_1 modulo π^max(P−2,0);
    y_0 = i u_0;
    y_1 = u_0 + π² u_1 modulo π^P.

**Theorem C9.** This word is exactly C^⊗n. With all surrounding ordinary work charged, its recurrence is

    F(n,P) ≤ F(n−1,P) + F(n−1,(P−2)_+) + c 2^n(P+1).

A zero-precision branch needs no response. The full-grid pair is obtained by an invertible triangular input map. In this implementation both recursive calls are paid work; they do not by themselves create extra external productive targets. A different productive target split requires its own exact input/output ABI, precision domains and complete encoder/decoder bill.

**Proof.** Tensor C2 in one axis. The middle diagonal is diag(C^⊗(n−1), π² C^⊗(n−1)). Expanding its surrounding T and S gives the stated word. Its second child needs two fewer residue digits because its output is multiplied by π². Count copies and arithmetic around the children. The displayed constant assumes the declared direct-access or streaming layout; a larger physical routing cost is an additional explicit term, not absorbed without a layout proof. ∎

For the normalized tensor, the child output precisions are p+1 and p−1: each child has n−1 normalization units. A nonpositive child output precision is interpreted on its specified fractional grid. In particular p−1 = 0 does not allow dropping that child: its raw modulus p+n−2 can still be positive. Only a zero raw precision removes the branch. This exact two-parameter contract is supplied for a recursive compiler, without claiming that its full paid moment beats the selected inventory.

## C10. Exact recovery and source-bound application

If both components of each input coordinate have absolute value below 2^b, each integer component of C^⊗n x is below 2^(b+n) in absolute value: it is a sum of N unit-phase input components. Compute the final common numerator modulo π^(2q), q ≥ b+n+2. The modulus is a unit times 2^q, so signed integer representative recovery is unique. The final tag n then gives A_n x exactly. This explicitly pays recovery precision rather than equating a modular class with an exact rational output.

To install this word at a current native site, identify its actual tensor-axis basis and absolute phase, preserve spectators, deliver every requested output, and charge the physical charts and movement. A numerical rank does not establish that response identity. GaussianTensorExecution provides precisely the finite C tensor. Current P104 native recipes retain separate all-width and physical implementation obligations.

This closes the algebraic all-output response without assuming a cheap exceptional cache. It supplies a whole precision-scheduled triangular word and a two-parameter recursive word. A κ increase still requires their actual complete recursive invoice and target matching. The package must not call the diagonal storage estimate a funded exponent improvement.

## C11. Exact current native matching and the scope of a shared gauge

The current inspected clifford_exact and native_verify sources resolve the normalization match directly. Their C gate is

    ((1+i)/2) I + ((1−i)/2) X
      = [[i,1],[1,i]] / π = A_1.

Their fourier(rank) is the product of these gates on the selected coordinate axes. Their lower_child recipe is the literal circuit

    monomial(right), then fourier(rank), then monomial(left),

including signed permutations, quadratic phases, translations and the recorded global phase. Consequently the Smith word substitutes for that central fourier primitive after the actual recipe's matchers. At lifted width f, the central active factor is A_(rf); untouched axes remain spectators. This statement retains the source's all-column and every-width implementation premise. It does not infer physical cost from the grade r alone. Inverse primitives use the conjugate factorization and the same valuation/precision schedule.

A proposed single global Walsh gauge for every chart would require more. It is false for these actual chart definitions. Here is an exact source-bound reason, not a numerical test.

For a singleton chart U = [q], let h be q's highest set-bit index. The source's basis_extend first takes q, then the standard basis vectors in increasing order. It omits e_h and takes all other units. Hence the first dual vector is e_h. In the source formula Q = I + G^(−T)G^(−1), the conjugated quarter-turn generator has Pauli displacement

    P_q = unit phase times X_q Z_(q+e_h).

Indeed G e_0 = q and Q q = q + G^(−T)e_0 = q+e_h. The circuit order conjugates the axis generator by the actual chart K; the unit phase does not change Pauli commutation.

**Theorem C11.** For singleton charts q,r with highest indices h,k, their Pauli generators commute exactly when

    q_k + r_h = 0 in F_2.

In particular, every family with one fixed highest index is commuting. The actual source singleton charts [11] and [41] do not commute.

**Proof.** The symplectic pairing is

    q·(r+e_k) + (q+e_h)·r = q_k + r_h.

Paulis commute exactly when this pairing is zero. At equal highest indices both bits equal one. For q=11=8+2+1 and r=41=32+8+1, the Z displacements are 3 and 9. Their pairing is parity(11 and 9) + parity(3 and 41) = 0+1. Their nontrivial quarter-turns therefore have nonzero commutator as well: the product of their nonzero Pauli coefficients multiplies the nonzero Pauli commutator. Both singleton frame records occur literally in the retained PR 5786 WORD. ∎

This rules out silently treating all native chart changes as translations in one fixed Walsh basis. It does not obstruct C2–C10, which replace the central primitive inside each actual matched recipe. A commuting subfamily may support one shared diagonal gauge, but a source-bound chronological patch must still pay its entry/exit charts, each crossing role, every target change, ordinary scalar operations and physical restoration. No favorable whole-patch invoice is assumed here.

## Attribution and evidence

Inspected modules: Mathproof.External.IntegerMultBounds20261008.Matrix.GaussianTensorExecution, GaussianScalarCircuits, GaussianLattice and CommunityPrecisionProfile. Source-only retrieval is not fresh kernel checking. The prior Gaussian spectral bridge is credited for identifying the normalized C tensor and exposing the exceptional-correction obligation. OpenAI's pinned preprint motivated valuation-filtered replacement; no global preprint complexity conclusion is assumed here.

Smith factorization, tensor products and binomial moments are classical. The explicit source-specific full-response word and propagated precision schedule are proved above; no worldwide novelty is asserted. P104 predecessors receive their retained credit: Cinna Davis's controller, Ali Romman's all-forward/asynchronous/accumulated words, Pierre-Loïc Doulcet's local improvements, and Dugongue's source-bound compositions. New text is Apache-2.0 with substantial OpenAI Codex assistance.


