# Four-term transport syzygies for two-sided address twists

## Model and question

Use the setting of JoyboyBrian's PR5490 (`research/bit-three-term-twist-rigidity/PROOF.md`),
which inherits the second-order quotient of Krzysztof Wójt's PR5003. Here
V = M_m(F2), m >= 2, and Sym^2(V) is the degree-two part of the
polynomial ring F2[V], with squares retained. A *two-sided transport* is a
map U(z) = L z R with L, R in GL_m(F2). Over F2 the pair (L, R) is
determined by U, because U corresponds to the rank-one tensor L ⊗ R^T and
the only nonzero scalar is 1.

For an off-diagonal block (r, s), PR5490 Section 3 derives two necessary
conditions on the calls j contributing to that block. With a_j the role-r
frame reduction and U_j the induced relative transport, they are

    sum_j a_j = 0,    sum_j a_j · (U_j z) = 0 in Sym^2(V) for all z.      (1)

The role-s frames are b_j = U_j^-1 a_j. Write

    beta = sum_j U_j^-1 a_j

for the *role-s residue*. PR5490 shows that three contributions force
beta = 0. The residue then cancels from the diagonal block (s, s), which
is how its eight-call pattern is excluded. Its Open next question 1 asks
whether four or more contributions can survive this condition. This file
answers the four-contribution case.

## Theorem

Let a_1, ..., a_4 in V and two-sided transports U_1, ..., U_4 satisfy (1).

1. **m = 2.** beta = 0 for all frames, not only rank-one frames.
2. **m >= 3.** If beta ≠ 0, then a_1 = a_2 = a_3 = a_4 = x ≠ 0 and
   U_1 + U_2 + U_3 + U_4 = 0 as linear maps of V. Moreover
   rank(beta) <= 2 rank(x). So rank(beta) <= 2 for rank-one frames.
3. **Sharpness.** For every m >= 3 there are four pairwise distinct
   two-sided transports and a rank-one x with a_j = x for all j. They
   satisfy (1), and rank(beta) = 2.

So four contributions *can* survive the dirty degree-one condition once
m >= 3. The three-term rigidity does not extend. The escape is narrow: all
four role-r frames must agree modulo two, the transports must satisfy a
four-term relation, and the surviving residue has rank at most two.

## Proof of parts 1 and 2

**Normalization.** Replacing z by U_4^-1 z turns (1) into the same
condition for U_j U_4^-1. The new residue is U_4 beta, which has the same
rank. Part 1 is therefore a finite statement over 36^3 transport triples
with U_4 = id. For each triple, (1) is a linear system in (a_1, a_2, a_3),
with a_4 = a_1 + a_2 + a_3. The verifier computes a kernel basis and checks
beta = 0 on every basis vector. This is enough because beta is linear in the
frames. It checks all 46,656 triples.

**Part 2.** Assume m >= 3. Two facts are used:

- **Rank distance.** PR5490 Section 1 proves that two distinct two-sided
  transports differ by a map of rank at least m.
- **Linear syzygies.** If l_1, ..., l_d are linearly independent linear forms
  and sum_i l_i f_i = 0 with each f_i linear, then f_i lies in the span of
  {l_j : j ≠ i}. This is because l_1, ..., l_d form a regular sequence in the
  polynomial ring, so the degree-one syzygies are spanned by the Koszul
  relations.

If some a_j = 0, at most three terms remain and PR5490's three-term lemma
gives beta = 0. So assume all four frames are nonzero. Since their sum is
zero, their span W has dimension 1, 2 or 3.

*dim W = 3.* The frames are x, y, w, x+y+w with x, y, w independent.
Then (1) becomes

    x·((U_1+U_4)z) + y·((U_2+U_4)z) + w·((U_3+U_4)z) = 0.

By the syzygy fact, each U_j + U_4 maps V into a span of two of x, y, w,
so it has rank at most 2 < m. Rank distance forces U_1 = U_2 = U_3 = U_4 = U.
Then beta = U^-1(sum a_j) = 0.

*dim W = 2.* Every frame lies in {x, y, x+y}. The multiplicities
(n_x, n_y, n_(x+y)) sum to 4 with n_x + n_(x+y) and n_y + n_(x+y) even, and at
least two values occur. Up to renaming the three nonzero values, the
frames are x, x, y, y. Then (1) reads x·((U_1+U_2)z) + y·((U_3+U_4)z) = 0.
The syzygy fact gives rank(U_1+U_2) <= 1 and rank(U_3+U_4) <= 1. So
U_1 = U_2 and U_3 = U_4, and the two pairs cancel in beta.

*dim W = 1.* All a_j = x ≠ 0. Then (1) is x·((sum_j U_j) z) = 0 for all z. The
polynomial ring has no zero divisors, so sum_j U_j = 0. Write
U_j(z) = L_j z R_j. The relation is the tensor identity
sum_j L_j ⊗ R_j^T = 0 with all factors invertible. Let d be the dimension of
span{L_j}.

- d = 1: all L_j = L, and beta = L^-1 x (sum_j R_j^-1). Its rank is at most rank(x).
- d = 3: if some L_j were outside the span of the other three, its lone
  coefficient R_j^T would vanish, which is impossible. So the one linear
  dependency among the L_j has full support, and the values are
  A, B, C, A+B+C. Comparing coefficients gives R_1 = R_2 = R_3 = R_4 = R, and
  beta = (sum_j L_j^-1) x R^-1. Its rank is at most rank(x).
- d = 2: the values lie in {D, E, D+E}. If the multiplicities are 2, 2, 0,
  then comparing coefficients gives equal R inside each pair. So the
  transports cancel in pairs and beta = 0. Multiplicities 3, 1, 0 force a
  lone coefficient R^T = 0, which is impossible. The remaining shape, up to
  renaming, is L = (D, E, D+E, D+E). Coefficient comparison gives
  R = (P, P, Q, Q+P). Then
  beta = (D^-1 + E^-1) x P^-1 + (D+E)^-1 x (Q^-1 + (Q+P)^-1). Each summand has
  rank at most rank(x).
- d = 4 is impossible, because then every coefficient would have to vanish.

In every case rank(beta) <= 2 rank(x). This proves part 2.

## Proof of part 3

Identify F2^m with the field F = F_(2^m), and let M_c be the matrix of
multiplication by c. Then c ↦ M_c is F2-linear and injective, and
M_c M_d = M_(cd). Take a = 1 and choose b in F outside F_4, which exists
because m >= 3. Set q = 1, q' = b and p = q + q'. Then a, b, a+b, p, q, q' are
all nonzero. Let

    L = (M_a, M_b, M_(a+b), M_(a+b)),   R = (M_p, M_p, M_q, M_(q')),

with U_j(z) = L_j z R_j and a_j = x = u v^T of rank one. Then
sum U_j(z) = M_(a+b) z M_p + M_(a+b) z M_(q+q') = 0. So (1) holds, and the
four transports are pairwise distinct. The residue is

    beta = M_(c1) x M_(d1) + M_(c2) x M_(d2),
    c1 = a^-1 + b^-1,  c2 = (a+b)^-1,  d1 = p^-1,  d2 = q^-1 + q'^-1.

It has rank 2 exactly when M_(c1) u and M_(c2) u are independent and
M_(d1)^T v and M_(d2)^T v are independent. Since the M_c are injective and
linear in c, this holds when c1 ≠ c2 and d1 ≠ d2. In a field,
c1 = c2 is equivalent to (a+b)^2 = ab, that is, a^2 + ab + b^2 = 0. Then a/b
would be a primitive cube root of unity and would lie in F_4. With a = 1
this would put b in F_4. The same argument applies to q, q' with q'/q = b.
Hence rank(beta) = 2.

For m = 2 the same family uses F_4 itself. There c1 = c2 and d1 = d2, so
beta = 0, in agreement with part 1.

The verifier checks the explicit witness for m = 3, 4, 5, 6 with the
moduli x^3+x+1, x^4+x+1, x^5+x^2+1 and x^6+x+1, taking b = x. It evaluates
(1) directly as polynomial products in Sym^2(V), independently of the
relation shortcut. It also checks pairwise rank distance, the transport
relation and rank(beta) = 2, plus a negative control.

## Scope

This is a statement about the necessary degree-one conditions (1) in a single
off-diagonal block. It does not synthesize a word or realize I_m diagonal
targets. It checks no other block, the PR5003 cross terms, native prices or
the five-or-more contribution case. Lifting the F2 frames and transports to
odd-denominator rank-one frames and GL_m(Z_(2)) twists, as in PR5490's model,
is routine, but this package does not check a complete group-ring word.
No kappa, supplier or multiplication-theorem claim is made.
