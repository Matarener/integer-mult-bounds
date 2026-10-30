# A representation rank cut for diagonal group-label targets

Nick Petalas. Apache-2.0.

## 1. Model

Use the model of Ali Romman's `research/group-subproduct-cover` (PR #5394),
section 1, unchanged. K is any field and G any group with identity e. A
circuit has finitely many registers. Free operations are fixed scalar
matrices over K. They may be rectangular or singular, and they may copy,
clear or discard registers. A paid gate on R registers is

    D(N,g) = (I_R - N)[e] + N[g],      N in M_R(K).

The rank-charged cost of a word is sum_j rank(N_j). The rank-one count is
the number of gates when every N_j has rank at most one. The idempotent
condition is allowed but not used. The target is the data block
diag([t_1],...,[t_d]). Repeated entries are allowed. For the lower bound,
workspace may change arbitrarily, with clean or dirty initial values.

## 2. The cut

For a matrix representation rho: G -> GL_m(K') over an extension field
K' of K, put

    r_rho(g) = rank_{K'}(rho(g) - I_m).

**Theorem 1.** Let C_0 D(N_1,g_1) C_1 ... D(N_k,g_k) C_k realize the
data block diag([t_1],...,[t_d]). Then

    sum_i r_rho(t_i)  <=  sum_j rank(N_j) * r_rho(g_j).

*Proof.* Extend rho linearly to an algebra homomorphism K[G] -> M_m(K').
Apply it entrywise to a matrix over K[G]. This map is multiplicative on
block matrices and commutes with taking the data-row/data-column submatrix.
A scalar matrix C becomes C (x) I_m. The gate becomes

    I (x) I_m + N_j (x) (rho(g_j) - I_m).

Its second term has rank rank(N_j) * r_rho(g_j). Write A_j for the image of
C_j and B_j for that second term. Then the image of the circuit is
A_0 (I + B_1) A_1 ... (I + B_k) A_k. Expand it one gate at a time,
replacing (I + B_j) by I from the left:

    image - A_0 A_1 ... A_k = sum_j A_0 ... A_{j-1} B_j A_j (I+B_{j+1}) ... A_k,

where gates 1..j-1 have already been replaced by I. Each summand has rank
at most rank(B_j). Rank is subadditive, so the left side has rank at most
sum_j rank(N_j) r_rho(g_j).

Apply the augmentation map [g] -> 1 entrywise. Every gate maps to I, so the
circuit maps to C_0 C_1 ... C_k. The target maps to I_d. Its data block is
therefore I_d, and the data block of A_0 ... A_k is I_d (x) I_m. The data
block of the image is diag(rho(t_1),...,rho(t_d)). The data block of the
difference has rank sum_i r_rho(t_i). A submatrix has rank at most the
rank of the whole matrix. QED.

The telescoping step is not new. This account's PR #5202
(`research/order21-normal-tariff`) used it for one F2 representation of
the order-21 group, and `research/cut58-separable-query-floor` uses a
character twist. Theorem 1 states it for an arbitrary representation, an
arbitrary field and projectors of any rank.

## 3. The regular representation over K itself

Let G be finite and let rho be the left regular permutation representation
over K. A permutation matrix P has (P - I)v = 0 exactly when v is constant
on every cycle. In every characteristic the kernel has dimension equal to
the number of cycles. Left multiplication by g has |G|/ord(g) cycles, each
of length ord(g). Hence

    r_reg(g) = |G| (1 - 1/ord(g))      over every field.

**Corollary 2.** Over every field, for every finite group and alphabet,

    sum_i (1 - 1/ord(t_i))  <=  sum_j rank(N_j) (1 - 1/ord(g_j)).

In particular, the rank-charged cost is at least
sum_i (1 - 1/ord(t_i)) / (1 - 1/M), where M is the largest order of a paid
label.

## 4. Prime exponent

**Corollary 3.** Let G have prime exponent p: every nonidentity element
has order p. G may be nonabelian. Let K be any field and take any
finite clean or dirty scalar workspace. Any diagonal target with d
nonidentity entries, repetitions allowed and identity entries ignored,
has

    rank-charged cost >= d,      rank-one count >= d.

If every target label is allowed, d direct rank-one coordinate gates attain
both bounds. The exact rank-one count and the exact rank-charged cost are
then both d.

*Proof.* Identity entries and identity labels contribute zero to both sides
of Corollary 2. Every other term is 1 - 1/p. Divide by 1 - 1/p. The direct
word puts N = E_ii with label t_i on data role i and touches nothing else. QED.

**Answer for these groups.** By Ali Romman's cover theorem, the
arbitrary-rank unit-cost count is the cover cost c_L(T). In a group of prime
exponent, with every target label allowed, the rank-one count is d.
Thus the rank-one count exceeds the relaxed cover cost exactly when
c_L(T) < d. The gap can be exponential. Take G = (C_p)^n and all
p^n - 1 nonidentity targets. Any word of length k has at most 2^k ordered
subproducts. Words covering all of G exist, for example each basis
vector repeated p-1 times, so c(T) <= n(p-1). For p = 2 the cover cost is
exactly n and the rank-one count is 2^n - 1. The verifier computes the
exact cover costs 2, 3 and 4 for (C2)^2, (C2)^3 and (C3)^2, with rank-one
counts 3, 7 and 8. It also realizes the length-four basis cover of all 15
nonidentity labels of (C2)^4 over F2.

The nonabelian Heisenberg group of order p^3 (p odd) has exponent p, so
Corollary 3 applies to it over every field. The verifier checks the order-27
case.

## 5. Relation to predecessors

Wentao Li's `research/elementary-abelian-diagonal-minimum` proves the exact
rank-one count t for F2[(C2)^k], using a graded image in m/m^2. Corollary 3
contains that statement. It also adds every field, every prime p,
nonabelian groups of prime exponent, repeated and rank-charged projectors,
rectangular or singular free maps, and arbitrary workspace changes. Ali
Romman's corollary for three distinct labels holds in every group. Corollary
3 recovers it only for groups of prime exponent. Its two-call rank argument
is not reused here.

## 6. Scope limits

Corollary 2 is the regular cut only. It is weaker when the labels have mixed
orders. For three copies of a^2 in C4 it gives only 2 < 3; a different
argument is needed there. In Q8, targets {i,j,k,-1} still get the bound 4.
Other representations can do better. A faithful character of C_m over an
extension of K with char K not dividing m gives r = 1 at every nonidentity
element. Theorem 1 then gives rank-charged cost >= d for cyclic groups in
those characteristics. That remark is proved by the same theorem but has no
separate finite check here.

The proved bill is an abstract gate count in the relaxed model. Physical
group gates, scalar maps, source reads, precision, recursive children,
hosting and cleanup are not priced. No complete kappa calculation changes.
