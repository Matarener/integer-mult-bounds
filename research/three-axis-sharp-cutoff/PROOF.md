# The three-axis native monomial tensor cutoff is exactly seven

Joseph Anglada (@fluorine), with substantial OpenAI Codex assistance.
Apache-2.0. This is a scoped computer-assisted algebraic proof, not an
improved multiplication exponent, physical supplier or full theorem audit.

## 1. Statement and exact grammar

Use the input-phase grammar of Ali Romman's PR5369 and PR5529. Let
X = F_2^3, with addresses 0..7 and bit j the coefficient of e_j. Put

    U(g,q)e_x = i^{q(x)} e_{g(x)},
    q(x) = c + sum_j a_j x_j + 2 sum_{j<k} b_jk x_j x_k (mod 4),

where g is in AGL(3,2), c,a_j are in Z/4, and b_jk are in Z/2.
Let G be this finite monomial group and k = Q(i) or C. Its diagonal
subgroup D has 2048 elements; each gD_q is a unique normal form. Work in
k[G] with rho_f([U]) = U^{tensor f}, extended linearly. External scalar
coefficients are fixed outside the tensor power. Set z=[iI] and
I_r=(z-i^r[1]), for r=0,1,2,3. These are two-sided central ideals.

**Theorem.** For every positive f with residue r modulo four,

    ker rho_f = I_r  if and only if  f >= L_r,
    (L_0,L_1,L_2,L_3) = (8,9,10,7).

The least F for which the equality holds for every f>=F is therefore
seven. A set T of positive tensor widths decides every fixed k[G] identity
at all positive widths exactly when, for each r, T contains a width
f>=L_r congruent to r. In particular 7,8,9,10 suffice, four residue tests
are necessary, and no complete test set can have maximum width below ten.

The upper bound and its exact full-span census are PR5529's result. The
addition here is necessity for the **complete representation**, using the
explicit cancellation witness below. Full-span minima alone do not prove it.

## 2. A 168-term cancellation certificate

Embed H=GL(3,2) in the affine subgroup by fixing the zero address. For h in H
define a(h) by its order:

    order       1    2    3    4    7
    a(h)        6   -2    0    2   -1.

Put A=sum_h a(h)[h]. This is nonzero: its identity coefficient is six.
For any two-dimensional linear plane V in X, let K_V be its pointwise
stabilizer in H. It has four elements. The exact finite certificate is

    sum_{h in g K_V} a(h) = 0       for every g in H and every V.       (1)

Here is a small checkable description of the whole certificate. Take the
standard plane V={0,1,2,3}. Its stabilizer consists of the matrices with
first two columns e_1,e_2 and third column e_3+v, v in V. Right cosets are
indexed by the 42 ordered independent image pairs (h(e_1),h(e_2)). The
multisets of element orders and their multiplicities are exactly:

    (1,2,2,2): 1; (2,2,4,4): 3; (2,3,3,4): 12;
    (3,3,3,3): 2; (3,4,7,7): 24.

Every displayed multiset has coefficient sum zero. Conjugation sends the
standard plane to any linear plane and preserves orders, proving (1)
from this finite table. The executables independently reconstruct all
168 maps and the table: one enumerates independent binary matrix columns,
the other enumerates all 5040 permutations of the seven nonzero addresses
and retains exactly the XOR-preserving maps. The separate audit also
recovers the coefficient vector by rationally solving the coset equations
with a(1)=6. No character table or floating-point rank is an input.

As redundant corroboration, direct group-algebra multiplication gives
A^2=56 A. This idempotent relation is not needed for the proof.

If a tuple x uses addresses lying in a proper linear subspace, choose a
linear plane V containing it. For each output tuple y, the set
{h:h x=y} is empty or a coset of the tuple's pointwise stabilizer, hence a
disjoint union of right cosets of K_V. Equation (1) gives

    A^{(f)} e_x := sum_h a(h) h^{tensor f} e_x = 0.                  (2)

This defines a linear combination of tensor powers, not the tensor power
of the sum A. That distinction is essential.

## 3. A coding-theory obstruction below width seven

Say a tuple x_1,...,x_f has zero nonconstant phase character if

    sum_t x_tj = 0 (mod 4),
    sum_t x_tj x_tk = 0 (mod 2)  for j<k.                          (3)

Let the three binary row words of this tuple be R_1,R_2,R_3 in F_2^f.
Their weights are divisible by four and their pairwise dot products are
zero. Every word in their binary linear span has weight divisible by
four: wt(u+v)=wt(u)+wt(v)-2|supp(u) intersect supp(v)|, and the whole
span is self-orthogonal. This is a doubly even binary code.

If the rows were independent, the seven nonzero codewords would each
have weight at least four, so their total weight would be at least 28.
But every nonzero address column contributes to exactly four of those
seven words. Thus that total is 4 times the number of nonzero columns,
at most 4f. For f<=6 this is at most 24, a contradiction. Therefore the
row rank, and equivalently the linear span of the address columns, is
at most two. Equation (2) now annihilates every tuple satisfying (3)
at every positive width below seven.

This seven-column threshold is the elementary binary simplex-code
weight-counting bound. It is classical coding theory, not a new coding
bound. Its use here supplies the missing stabilizer-kernel witness.

## 4. Four explicit fixed residuals

Define the finite phase projector and residual

    E_r = (1/2048) sum_{c,a,b} i^{-r c} [D_q],
    P_r = A E_r.                                                 (4)

The phase acts first, in the predecessor's input-phase convention.
Finite Fourier orthogonality says rho_f(E_r) projects onto tuples
satisfying (3) when f=r modulo four, and is zero at all other residues.
For a matching residue at f<L_r, the positive f is at most six.
Sections 2 and 3 prove rho_f(P_r)=0. At a wrong residue this is already
forced by E_r. Thus P_r vanishes at **every** positive f<L_r.

At width L_r, take each of the seven nonzero addresses once and add
L_r-7 zero addresses. Each coordinate then occurs four times and each
coordinate pair twice, so E_r acts as identity. Only the identity
linear map fixes this tuple. Its diagonal matrix entry under rho_f(P_r)
is exactly six. The same construction with additional groups of four
zeros works for every larger width of that residue.

Each P_r is nonzero as a formal group-algebra element: in the expansion
hD_q the normal forms are distinct and the identity-h coefficient is a
nonzero Gaussian multiple of 6/2048. Moreover z P_r=i^r P_r, so P_r is
not in I_r (evaluation at width L_r also proves this). It follows that
ker rho_f properly contains I_r at every matching f<L_r. In particular
P_2 is zero at widths 1..9 but has diagonal entry six at width ten.
This is the missing necessity statement, not an inference from an absent
full-span tuple or a rank modulo one prime.

## 5. Upper bound and all-width completeness

For completeness the PR5529 upper bound is checked in two separate finite
ways. For a multiplicity vector m on the eight addresses define its phase
statistics (r,u,v) by (3), retaining the actual coordinate residues u in
(Z/4)^3, pair parities v in (Z/2)^3 and r=sum m mod four. There are
4*4^3*2^3=2048 characters.

The first checker exhausts all 43758 nonnegative multiplicity vectors
with total at most ten and records the least total with full affine span
for each character. Every character occurs; the largest minima in the
four residues are (8,9,10,7). The second checks all 65536 vectors
a in {0,1,2,3}^8 using PR5529's exact formula

    shortest full-span length for this a = sum a + 4(3-d(a)),

where d(a) is the affine dimension of its positive support, with -1 for
empty support. Indeed every new support address costs at least four
copies and adds at most one affine dimension; conversely exactly 3-d
new addresses extend that support to full affine span. Taking minima
over a gives the same result. Thus this finite certificate is exhaustive,
not a sample of widths. Four-copy zero padding preserves a character
and full affine span at all later widths of the same residue.

Write an arbitrary group-algebra residual as a sum over unique affine
buckets and phases. After imposing the residue relation, a nonzero
residual has a nonzero Fourier coefficient in some bucket g. At
f>=L_r, choose a full-affine-span tuple realizing that character and
output g times the tuple. No other affine map gives that same output,
so the corresponding matrix entry is the nonzero Fourier coefficient.
Hence ker rho_f=I_r. This is the predecessor Fourier-separation argument.

The four central ideals have zero intersection by Fourier inversion in
the constant phase. Upper bounds therefore prove sufficiency of any
test set reaching all four thresholds. If a test set misses the threshold
in residue r, the fixed nonzero residual P_r vanishes at every test in
that set and fails at L_r. This proves necessity even for infinite T.

## 6. Scope and evidence

The theorem applies entrywise to complete fixed register-program endpoint
matrices over k[G], with every independent dirty input and specified
return retained. It excludes Hadamard/nonmonomial gates, width-dependent
external coefficients or program families, and undeclared aliases.
It does not provide efficient expansion of a circuit into group algebra.
No physical cost, ownership budget, compiler, precision, stock, tape,
analytic reduction or multiplication exponent changes.

The integer coset table is computer-assisted finite evidence. The
all-width statement follows from the written Fourier, code-weight and
padding arguments. Same-agent separate implementations are corroboration,
not independent human review or formal proof-kernel acceptance.

Credit Ali Romman for PR5369's grammar/Fourier theorem and PR5529's
improved sufficient bound and explicit open question; Hiroki KUMAZAKI for
PR5522's two-axis sharpness and warning about the representation-kernel
gap; Mihir Srivastava for PR5521's one-axis/general audit; Jose Manuel,
ywz65, Chris R and the retained native/phase/compiler lineage. The
GL(3,2), finite Fourier and doubly-even/simplex-code tools are classical.
No general literature-priority claim is made.
