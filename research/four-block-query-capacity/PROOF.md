# Exact capacity of four bounded-rank binary query shears

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let K be any field of characteristic two and let
A = K[Q]/(Q²−1). There are n independent input coordinates and no additional
workspace. Free operations are arbitrary constant matrices in GL_n(K).
A paid operation has the form I_n + Q N, where N is a constant n-by-n
matrix, N²=0, and rank N≤r. Different calls may use different N.
All input coordinates must receive Q, so the exact desired endpoint is Q I_n.

**Theorem.** For positive integers n,r, an endpoint Q I_n is possible with at
most four paid operations if and only if n is even and

    n ≤ 2 floor(4r/3).

Equivalently, the least possible maximum paid rank is ceil(3n/8) for even n.
Every successful four-call word has total paid rank at least 3n/2. The
construction below attains this total rank as well as the optimal maximum.
Zero-rank padding represents an unused call, not a separately charged job.

This is an abstract interface theorem. A native operation realizing an arbitrary
rank-r query, its helpers, physical scalar maps and complete recursive invoice
are not supplied. In particular, treating constant bases as free is an explicit
hypothesis, not a statement about the selected multiplier.

## 1. Normalize the exact endpoint

Put ε=Q+1, so ε²=0. For a paid factor,

    I+Q N = (I+N)(I+εN),       (I+N)⁻¹=I+N.

Move all constant factors to one end by conjugation. Conjugation preserves
rank and the square-zero property. Since the desired endpoint at ε=0 is I_n,
the combined constant factor is I_n. The remaining four factors have the form
I+εR_i, with R_i²=0 and rank R_i=r_i≤r. Their product is

    I+ε sum_i R_i = Q I_n = I+εI_n.

Thus sum_i R_i=I_n. Taking traces shows n=0 in K, since a square-zero matrix
has trace zero. Therefore n is even. This reduction allows arbitrary free
constant bases between calls; it does not assume separate ports or a common
coordinate support for the R_i.

## 2. Factor the query Gram projector and its complement

Choose full-rank factorizations R_i=U_i V_i, with U_i having r_i columns and
V_i having r_i rows. Square-zero gives V_i U_i=0: multiply
U_i(V_i U_i)V_i=0 by a left inverse of U_i and a right inverse of V_i.
This also covers r_i=0 by empty blocks.

Write S=sum_i r_i, concatenate the U_i into U and stack the V_i into V.
Then UV=I_n. Consequently G=VU is an idempotent of rank n in dimension S,
and its four diagonal blocks are zero. Its complementary idempotent
C=I_S−G has rank c=S−n and diagonal blocks I_(r_i).

Factor C=AB with A of full column rank c and B of full row rank c. From
C²=C, left and right inverses give BA=I_c. Partition A into row blocks A_i
and B into column blocks B_i. The diagonal blocks say A_i B_i=I_(r_i).
Hence E_i=B_i A_i is an idempotent of rank r_i on K^c, and

    sum_i E_i = BA = I_c.

The complements F_i=I_c−E_i have rank c−r_i. There are exactly four blocks,
and characteristic two gives

    sum_i F_i = 4I_c − sum_i E_i = I_c.

Subadditivity of rank now implies

    c ≤ sum_i rank F_i = 4c−S,
    S ≤ 3c = 3(S−n),
    3n ≤ 2S ≤ 8r.

Since n is even, this proves n≤2 floor(4r/3). The inequality S≥3n/2 is the
additional rank cost missed by the simpler n≤3r complement-dimension bound.
For example, four rank-two queries cannot twist six independent coordinates;
four rank-three queries can twist eight, but cannot twist nine or ten.

The use of the four complementary idempotents is the new step beyond the
minimum-query and block-simplex arguments credited below.

## 3. Attain the bound by balancing omitted calls

Write n=2p. On one coordinate pair, let

    A = [[0,1],[0,0]],        B = [[0,0],[1,0]].

Both matrices are square-zero of rank one. The three-query identity is

    (I+Q A)(I+Q B)(I+Q A) = Q [[0,1],[1,0]],

using Q²=1. A final constant swap makes this Q I_2.

For each of the p disjoint coordinate pairs, omit one of four call positions
and place these three factors, in order, in the remaining positions. Assign
omitted positions cyclically 0,1,2,3,0,1,2,3,... . At each position, direct-sum
its active rank-one matrices. This produces one square-zero paid matrix whose
rank is the number of pairs active there. A final direct sum of swaps produces
Q I_n on every original input.

Every call is omitted by at least floor(p/4) pairs, so the maximum rank is

    p − floor(p/4) = ceil(3p/4) = ceil(3n/8).

The sum of the four ranks is exactly 3p. The required cap is therefore
ceil(3p/4)≤r, equivalent to p≤floor(4r/3). This proves the converse and both
sharpness claims. It works over F2, and therefore over every field K in the
contract. No search result is used to infer the unbounded construction.

For r=3, take four pairs and omit a different call on each pair. Every query
then has rank three, there are eight independent outputs, and the total rank
is twelve. This is a concrete packing witness for the abstract changed model.

## 4. Relation to predecessors

Cinna Davis / 1337isnot1337's
`research/productive-controller-basis-search/GLOBAL-PROOF.md` supplies the
rank-one minimum-query simplex and its use in caller obstructions. Ali Romman's
PR #5617, `research/shortest-controller-stage-capacity/PROOF.md`, Section 9,
extends the Gram-complement method to coupled rank-q ports at the shortest
count. It derives the block simplex and its parity requirement there.

Matarener's PR #6114, Open next question 1, asks about higher-rank or multi-bank
paid operations beyond its rank-one Laurent income bound. This package gives
a sharp abstract binary specialization of that question. It does not extend
#6114's rational Laurent theorem to physical multi-bank calls. None of those
predecessors' verifiers or reported numbers are rechecked here. The three-query
exchange identity and elementary rank factorization are standard tools;
worldwide priority for those tools is unclaimed.

## 5. Verification boundary

`verify.py` constructs every feasible even dimension for caps 1 through 24,
up to dimension 64. It checks exact matrices in F2[Q]/(Q²−1) and independently
checks their action on every original coefficient bit using a lifted binary
interpreter. Small witnesses also check the factored Gram complement and all
four complementary idempotents. Four conjugated witnesses mix coordinate pairs.

The independent finite feasibility control enumerates every binary matrix in
dimensions two, three and four, retains every square-zero matrix, and uses all
pair sums to decide whether four such matrices sum to I at each rank cap.
This exhausts the normalized necessary condition in those finite domains.
It is not an enumeration of words in larger dimensions or a formal proof kernel.
Ten rejection controls exercise input bounds, a missing paid layer, a nonnilpotent
matrix and a rank-cap violation. Every check remains active with Python -O.
