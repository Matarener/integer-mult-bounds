# Sharp error for every real rank-seven Gram approximation

## Statement and scope

Let the rows of R be one representative of squared norm 2 from each of
the 56 D8 lines e_i +/- e_j in R^8, together with any proper subset of
the 64 half-spin lines of one parity. Write m for the number of rows and
K=RR^T/2. Then

    min { max_ij |K_ij-C_ij| : C in R^(m x m), rank C <= 7 } = 1/4.

There is no assumption on C's symmetry, sign, spectrum, or row and column
spaces. In particular C need not have the form RDR^T/2. This strengthens
Nick Petalas's PR6183 theorem for symmetric positive contractive carrier
filters, answering its first open question and the larger unrestricted
real-matrix question. Its attaining projection is retained with credit.

The theorem uses the full coefficient matrix, real scalars, and the fixed
Gram target. It is not a statement about masked entries, complex matrices,
nonlinear consumers, a changed total target, or physical implementation cost.

## Eight columns detect every deficient-rank candidate

Choose the eight retained column labels J corresponding to

    e_1+e_2, e_1-e_2, e_3+e_4, e_3-e_4,
    e_5+e_6, e_5-e_6, e_7+e_8, e_7-e_8.

Let U=R[J,:]. Stored representatives may differ by row signs. These roots
are mutually orthogonal with squared norm 2, so UU^T=U^TU=2I.

For arbitrary C of rank at most seven, the m-by-8 submatrix C[:,J] has
a nonzero real null vector a. Put z=U^T a. Then z is nonzero,
a=Uz/2, and K[:,J]a=Rz/2. For real s,t,

    (|s+t|+|s-t|)/2 = max(|s|,|t|).

Consequently, writing b_1>=...>=b_8 for the sorted absolute coordinates
of z and h=b_1+b_2>0,

    ||a||_1 = sum_(four coordinate pairs) max(|z_i|,|z_j|)
            <= b_1+b_2+b_3+b_4 <= 2h.

The first inequality holds because the four maxima select four distinct
coordinates; the second uses b_3<=b_1 and b_4<=b_2. Row sign choices in
U do not change its left-hand side. The retained D8 roots include a signed
root joining the two largest absolute coordinates of z. Hence

    ||Rz||_infinity >= h.

The extra half-spin rows may make this inequality strict. If
epsilon=max_ij |K_ij-C_ij|, coefficientwise triangle inequality gives

    h/2 <= ||K[:,J]a||_infinity
         = ||(K-C)[:,J]a||_infinity
         <= epsilon ||a||_1 <= 2 epsilon h.

Divide by h to obtain epsilon>=1/4. This is an all-real-matrix proof,
not an inference from the finite verifier. It uses only the D8 rows and
eight D8 columns; no projection back to the carrier spaces is needed.

Equivalently, an approximation with entry error strictly below 1/4 must
have eight independent columns at J, and therefore rank at least eight.
The norm ratio is sharp: take z with one nonzero coordinate in each of
the four pairs, all of the same magnitude. Then ||a||_1=2h.

## Attainment (PR6183's construction)

Choose an omitted half-spin root q. It has squared norm 2. Set

    D = I-qq^T/2,
    C = RDR^T/2 = K-(Rq)(Rq)^T/4.

D is a rank-seven orthogonal projector. R has column rank eight because
it contains U. Therefore C has rank seven: a left inverse of R shows
rank D<=rank(RDR^T), and the opposite inequality is immediate.

For every D8 root r, r dot q belongs to {-1,0,1}. For two distinct lines
in the same half-spin parity shell, their sign patterns differ in an
even number of coordinates, and the inner product also belongs to
{-1,0,1}. The line of q is absent, so

    |K_ij-C_ij| = |(r_i dot q)(r_j dot q)|/4 <= 1/4.

A D8 root has inner product of magnitude one with q; its diagonal error
is 1/4. This proves attainment, including when the half-spin subset is
empty. No optimality or invention of this projection is attributed here.

## P104 binding, precision consequence, and limits

Matarener's PR6166 at 096938513138868f0ed27639061f1a5054900f96 identifies
the relevant P104 configuration with all 56 D8 lines plus 48 half-spin
lines in orthonormal coordinates. This identification remains a cited
premise, as it was in PR6183; it is not independently audited here.
The source-pinned MISSING.json from PR6183 records its sixteen omitted
lines. The verifier constructs and checks the resulting mathematical
root set and the sixteen attaining matrices. That is distinct from
checking the physical selected ports' coordinate identification.

PR6183 at eaf77790466f34b86ce72080e3ec690e26dfacab supplies the preceding
question, Gram convention and attaining projection. Rohan Arun's PR1972,
Chafik Boukhalfa's PR1991 and their retained lineage supply the earlier
Gram channel. Their native/operator theorems are not replayed or adopted
as new results here.

For any real rank-seven C, some entry (i,j) of K-C has magnitude at least
1/4. On input B e_j the i-th output bias is at least |B|/4. Unlike the
positive-error predecessor, this argument need not locate a diagonal
entry. The maximum-entry norm here equals the induced l1-to-l_infinity
norm; the theorem does not assert an l2 operator-norm optimum.
Increasing arithmetic precision cannot make this fixed approximation
bias vanish. Any changed side correction or consumer must account for it.

This closes arbitrary real linear rank-seven replacement of this whole
Gram block. It does not price corrections, transport, restoration,
native calls, compiler operations, precision/tape work or the completed
supplier. No selected framework assumption is discharged and no kappa
improvement follows. General literature priority, independent human
review and formal proof-kernel acceptance are unclaimed.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
