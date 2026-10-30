# A native tariff obstruction that permits changed paid inputs

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

This is a necessary condition for a declared class of complete linear native
programs. It is not a lower bound on integer multiplication. The general
off-diagonal rank inequality is classical and already used in the repository.
The contribution here is an invariant cut for the full columnwise monomial
alphabet, its exact Clifford price, and the resulting all-width tariff test.

## 1. Contract and result

Fix n>=1 and f>=1. A field has space V=(C^(2^n))^(tensor f). All fields have
this capacity. Independent original inputs, dirty helper inputs and owned
scratch fields are separate registers. A finite linear word may use:

- Scalar linear combinations of fields, COPY, CLEAR and field permutations.
- Any linear combination of maps M^(tensor f), where M is a one-column
  monomial matrix. In particular this includes every monomial Clifford map,
  affine address change and quadratic diagonal phase on the n axes.
- A paid application of U^(tensor f) to one field, or a paid update
  y <- y + c U^(tensor f) x. Here U is a unitary Clifford matrix and c is
  a scalar. Count each field output of a multi-output primitive separately.

The Fourier rank r(U) is n minus the dimension of the intersection of the
diagonal Pauli space Z with U Z U^*. Equivalently, it is the binary rank of
the X part of the images of the n diagonal Pauli generators. A native
rank-r Gaussian, with monomial changes of frame, has Fourier rank r.

Require independent final jobs T_j^(tensor f), each on its own original
field. Monomial changes of frame and permutations are allowed. The initial
state contains original fields and zero or independent dirty scratch. Every
nonordinary initial observation must instead be accounted for in section 5.
No larger-field packing or operation between different tensor columns is
granted. More generally, a proposed free map is allowed for a cut exactly
when it preserves that cut and its complement.

Let P_r and T_r count paid calls and required jobs of Fourier rank r. Then
for every integer k with 1<=2k<=f,

    sum_r P_r (1-2^(-kr)) >= sum_r T_r (1-2^(-kr)).       (1)

If the profiles are fixed and the word works at arbitrarily large widths,
(1) holds for every positive integer k. The word, order, paid inputs,
coefficients, feedback and number of ordinary steps may change with f.
No paid input is frozen. A proof of (1) therefore rejects every word with
the declared profiles and alphabet, including active feedback into paid gates.

For example, one rank-one and one rank-three call cannot supply two
independent rank-two jobs. Their counts and rank masses agree, but at k=1
the paid side is 11/8 and the target side is 3/2. This is an obstruction to
the complete native word, not a comparison of quoted upper cost estimates.

## 2. The equality cut

Put D=2^n. In each field, let E_k project onto basis strings for which
columns 1 and 2 are equal, columns 3 and 4 are equal, and so on through
columns 2k-1 and 2k. The other columns are unrestricted. Then

    a_k = rank(E_k) = D^(f-k).

A one-column monomial matrix applies the same bijection to both members
of each pair. It preserves equality and inequality. Its phases are diagonal
and do not change support. Thus M^(tensor f) commutes with E_k. Every
allowed ordinary field operation also commutes with the direct sum of E_k
over the registers. This includes arbitrary ordinary codes across registers.

For a map A between register banks, define

    rho_k(A) = rank((I-E_out) A E_in).

The projectors are the direct sums for the relevant input and output banks.
For composable, possibly rectangular maps,

    (AB)_-+ = A_-- B_-+ + A_-+ B_++,
    rho_k(AB) <= rho_k(A) + rho_k(B).                   (2)

This uses only rank subadditivity and rank(AB)<=rank(B). Invertibility,
unitarity and a tree topology are not required. COPY, CLEAR, arbitrary
feedback and overwrites therefore do not invalidate (2).

## 3. The exact native price

For one pair of columns write E=E_1. Its range is spanned by |x,x> and
is the common +1 eigenspace of the n commuting Pauli operators

    Z_j tensor Z_j.

Its conjugate F=(U tensor U) E (U tensor U)^* is the common +1 eigenspace
of (U Z_j U^*) tensor (U Z_j U^*). Every generator of E commutes with every
generator of F: the two Pauli commutation signs cancel. Thus E and F commute.

The two stabilizer groups each have n independent generators. Their common
subgroup has dimension n-r(U). There is no sign conflict on this subgroup.
If U Z^v U^*=+/- Z^w, its tensor square is Z^w tensor Z^w. Hence their joint
group has n+r(U) independent generators and contains no negative identity.
It follows that

    rank(E F) = 2^(2n-(n+r(U))) = D 2^(-r(U)).         (3)

For clarity, the stabilizer dimension formula follows by expanding the
projector as the average of its commuting group. Only identity has nonzero
trace. A group with s independent signed Pauli generators and no negative
identity therefore has projector rank 2^(2n-s).

Since E and F are commuting projections, (I-E)(U tensor U)E has only zero
and unit singular values. Its rank is rank(F)-rank(E F). For k disjoint
pairs, the projections and intersections tensor together. The remaining
columns contribute an identity factor. Consequently

    rho_k(U^(tensor f)) = a_k (1-2^(-k r(U))).          (4)

The nonzero singular values of this cut block are all one. Global phases
of U do not change (3) or (4). Inverse calls have the same rank.

## 4. Complete words and approximation

A paid call on one field has cut rank (4). A nonzero scalar query update
has the same cut rank; a zero update has rank zero and may be overcharged.
All ordinary steps have cut rank zero. Apply (2) along the actual word.
This gives the paid side of (1), multiplied by a_k, as an upper bound.

The independent target jobs occupy disjoint input and output blocks. Their
cut ranks add and give the target side of (1), multiplied by a_k. This
proves (1). Zero scratch insertion and required output selection commute
with the cut. They cannot increase its rank. Arbitrary extra storage does
not invalidate the bound. Invertible ordinary input/output codes also
preserve the cut rank, so the exact obstruction permits those codes.

There is an approximation consequence for the original independent target
maps and unitary monomial endpoint frames. Let

    delta_k = sum_r (T_r-P_r)(1-2^(-kr)) > 0.

The target cut block has a_k sum_r T_r(1-2^(-kr)) unit singular values.
The program's cut block has rank at most a_k sum_r P_r(1-2^(-kr)). A rank
deficit leaves a unit vector in the target's initial singular subspace that
the program cut block kills. Thus

    ||program-target||_op >= 1,
    ||program-target||_HS^2 >= a_k delta_k.             (5)

Projection onto a cut is a contraction, so the complete endpoint has at
least this error. General invertible ordinary endpoint codes retain the
exact rank obstruction, but can rescale singular values; the constant one
in (5) is not asserted after arbitrary ill-conditioned codes. The paid
maps in this argument are the exact ideal maps. Numerical error inside a
query is not a new free operation in this model.

## 5. Prior observations and changes of model

At a caller boundary, let J map the independent original inputs to all
initially available rows, including the actual versions of cached rows.
Use the same input cut and the direct sum cut on the available fields.
The necessary condition becomes

    rho_k(target) <= rho_k(J) + sum_calls rho_k(call).  (6)

This follows from (2) and does not charge a cached response twice. Compute
rho_k(J) on its complete matrix. Do not replace it by nominal row counts:
duplicates and dependent observations can have smaller joint rank. The
identity rows contribute zero. The CLI checks the zero-initial-cross-rank
case (1); it does not claim to extract J from an arbitrary caller.

The theorem still applies when a later paid input changes, provided the
new word meets this contract. An extra free map that crosses the cut must
be charged by its actual cut rank. Inter-column permutations or payload
maps need not preserve E_k. Different field capacities require typed cuts
and their separate rank factors; canceling a common a_k is then invalid.
Nonlinear or data-dependent operations are outside this linear theorem.

## 6. A finite exact test for the infinite tariff family

For fixed finite profiles define the integer polynomial

    C(x) = sum_r (P_r-T_r)(1-x^r).

The required signs are C(2^(-k))>=0 for k=1,2,... . Rank-zero jobs make
no contribution. If C=0 the test is complete. Otherwise write

    C(x) = x^j (a + sum_(r>j) c_r x^(r-j)),
    L = sum_(r>j) |c_r|,  a!=0.

Choose K>=1 with |a| 2^K > L. For k>=K, the absolute remainder in
parentheses is at most L 2^(-k)<|a|. Thus the sign is the sign of a.
Check the finitely many k=1,...,K exactly. A negative leading coefficient
has a failure by K; a positive one certifies the entire remaining tail.
For a fixed width check only k<=floor(f/2). No floating-point roots or
sampled extrapolation is used. Passing this test proves only necessary
inequalities, not a circuit, recursion, compiler result or kappa saving.

No fixed finite prefix of the hierarchy is sufficient for all profiles.
For any K>=1, put m=2^(K+1), P_1=3, P_3=m and T_2=m+3. Then

    C(x) = x (m x-3) (1-x).

This is positive at x=2^(-k) for k<K and negative at k=K. The two job
counts agree. The paid rank mass exceeds the target mass by m-3. Thus
even a test of the count, the rank mass and an arbitrarily long fixed
prefix can miss an obstruction. The adaptive tail proof above is needed.

There are also profiles that pass a strict recursive power-moment test
and still first fail at an arbitrarily late cut. For the same m=2^(K+1),
take

    P_1=9, P_3=7m+12, T_2=3m+21, T_4=4m.
    C(x) = x (m x-3) (3-4x) (1-x).                   (7)

At every tested dyadic x<=1/2, the extra factor 3-4x is positive. The
first failing cut is again exactly K. Both job counts are 7m+21, while
the paid and target rank masses are 21m+45 and 22m+42. In particular the
target has a positive rank-mass surplus m-3.

The raw moment is favorable for every saving parameter 0<=c<=1/256:

    sum_r T_r r^(1-c) > sum_r P_r r^(1-c).            (8)

Indeed, all target ranks are at most four, so the left side is at least
(22m+42) 4^(-c). The right side is at most 21m+45. For m>=4,

    (21m+45)/(22m+42) <= 129/130 < 2^(-1/128).

The last strict inequality is equivalent to the integer comparison
130^128 > 2*129^128. Since 4^(-c)>=2^(-1/128), (8) follows. Thus even a
favorable raw saving of 1/256 and any fixed number of these native cut
tests can miss an impossible word. This is not a kappa construction:
the cut proves that no word in the stated model realizes these profiles.
No outer or compiler claim is inferred from the favorable raw moment.

## 7. Relation to the initial module question

This investigation began with the semisimple question left by PR5449.
For A=direct_sum_s M_(d_s)(K), let the target module modulo retained history
have simple multiplicities m_s. The exact number of arbitrary linear row
returns in the enlarged multi-input oracle model is

    max_s ceil(m_s/d_s).

One return is cyclic and contributes at most d_s copies of simple s.
Conversely, matrix units pack up to d_s copies from each simple into one
row, at the same time. This is a direct use of classical semisimple module
theory, not a new theorem in that subject.

That upper construction need not be one physical single-input query. For
example let A be all diagonal maps on K^3. Start with independent fields
x and y. Require rows e_1 x_3 and e_2 y_3. The output-module formula gives
one arbitrary row return, which can pack the two answers. But one physical
query on one field cannot obtain both independent source values. Before
the query its third coordinate is one scalar combination of x_3 and y_3.
The cut from coordinate 3 to coordinates 1 and 2 has target rank two and
one-call rank at most one. Two calls suffice and are necessary.

This input bottleneck led to (2). The equality cut makes that principle
work with the full columnwise monomial alphabet, where a coordinate cut
does not. The package therefore develops the native cut obstruction. It
does not publish the unrestricted row-packing formula as a physical
query compiler. The earlier frozen 104-return result remains unchanged.
