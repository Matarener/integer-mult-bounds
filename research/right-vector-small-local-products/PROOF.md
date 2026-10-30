# Common scalar pivot flags in small local products

Let K be a finite field of cardinality q. Let

    R = R_1 x ... x R_k,     1 <= k <= q,

where each R_i is an associative unital central K-algebra whose nonunits
form a proper two-sided ideal J_i. Thus D_i=R_i/J_i is a division algebra.
No commutativity, finite dimension, nilpotence, or equality D_i=K is assumed.
Fix n>=1 and an invertible M in M_n(R).

A paid factor is I+u y^T, with u in R^n and y in K^n. Arbitrary common
GL_n(K) maps are free anywhere in a word. In particular the free maps and
right vectors cannot be chosen separately in the product components.
Let pi:R^n -> (R/K)^n use the diagonal central copy of K. The theorem is

    cost_R(M) = delta_R(M) = rank_K(pi M|_{K^n}) <= n,
    delta_R(M) = min_{T in GL_n(K)} dim_K((MT-I)K^n).

The column lower bound cost>=delta is cited from #4243/#4099. The new
step extends #4787's local arbitrary-role upper bound to these products.
#4601 and ToikY #4334 already give the two-role small-product case.

## Avoiding the component kernels

A union of k<=q proper K-linear subspaces of K^d cannot equal K^d, for
every d>=1. Each subspace has at most q^(d-1) elements and contains zero.
Their union therefore has size at most

    1 + k(q^(d-1)-1) <= q^d-q+1 < q^d.

We use only this elementary finite-vector-space count.

For any invertible A in M_d(R), its reduction Abar_i is invertible over
D_i. The K-linear map

    L_i : K^d -> D_i,     phi -> phi Abar_i e_1

is nonzero, since otherwise every entry in the first column of Abar_i
would vanish. Thus ker L_i is a proper scalar subspace. Choose one phi
outside their union. Then every phi A_i e_1 is a unit in R_i, since its
residue is nonzero. Hence a=phi A e_1 is a unit in R. This argument uses
one common scalar row phi, including when the division residues differ.

## A common full pivot flag

We prove by induction on d that some Q in GL_d(K) makes every leading
square corner of QA invertible over R. The d=0 statement is vacuous.
For d>=1 choose phi as above, and extend it to the first row of a scalar
basis matrix Q_0. Write

    Q_0 A = [[a,b],[c,F]],     S=F-c a^(-1)b.

Here a is a unit in R. Block triangular elimination makes diag(a,S),
so S is invertible. Apply the induction hypothesis to S, obtaining
P in GL_(d-1)(K), and set Q=diag(1,P)Q_0. Each leading corner of size
j>=2 in QA has pivot a and Schur complement the leading corner of PS
of size j-1. Both are invertible, so that corner is invertible. The
size-one corner is a. All ring products retain the displayed order;
no commutativity of R_i or D_i has been used.

This proves existence of one common scalar pivot flag. The finite
constructor in verify.py searches scalar rows at each step and performs
this induction iteratively on its fixed bounded examples.

## The exact number of active columns

The following chart reduction is the cited #4787 argument, included to
connect the new flag to the precise cost. Put

    E={v in K^n : Mv belongs to K^n},
    s=dim_K E,     d=n-s=rank_K(pi M|_{K^n}).

Invertibility makes M:E -> M(E) injective. Choose a scalar basis of E,
extend it to a basis H of K^n, and extend its images to a basis B of K^n.
Then N=B^(-1)MH has its first s columns equal to those of I, so

    N=[[I_s,C],[0,A]],

with A invertible. For any scalar T, pi(MT-I)=pi MT has rank d, giving
delta>=d. Conversely T=HB^(-1) gives

    MT-I=B(N-I)B^(-1),

whose scalar column rank is at most d. Therefore delta=d. This reduction
needs invertibility but does not need the local-product hypothesis.

Apply the common-flag lemma to A and left-multiply N by diag(I_s,Q).
This is free and preserves the first s fixed columns. Call the resulting
matrix N again. Its active leading corners are all invertible.

For j=0,...,d let A_j consist of the first s+j columns of N and the
remaining columns of I. All A_j are invertible by the corner property.
A_0=I and A_d=N. Set h=s+j for j=1,...,d and

    u_j=A_(j-1)^(-1)(N e_h-e_h),     F_j=I+u_j e_h^T.

The h-th column of A_(j-1) is still e_h. Right multiplication by F_j
therefore replaces exactly that column, giving A_(j-1)F_j=A_j. Hence

    N=F_1 ... F_d.

Every right vector e_h is scalar and common to all components. Undoing
the free charts gives a legal word for M with at most d paid factors.
Together with the cited lower bound, its cost is exactly d. If d=0,
M itself is a common free map and no paid factor is needed. There is no
auxiliary role or componentwise free operation in this construction.

## Coverage of the separate binary metric

The finite oracle treats invertible pairs (A,B) over F_2. A free common
left map sends this pair to (I,C), where C=A^(-1)B. Common free right
multiplication by T sends C to T^(-1)CT. A paid factor has components
P_0=I+u_0 y^T and P_1=I+u_1 y^T. Applied at the normalized representative,
it sends C to P_0^(-1)P_1 C. At an arbitrary representative, conjugating
the paid factor by A gives the same alphabet with a changed scalar y.
Thus all normalized paid transitions are exactly the generators enumerated
by the bit-matrix oracle. Both P_i must be invertible on any path to an
invertible endpoint, since singular matrices cannot regain rank over a field.

BFS gives attaining paid paths. The verifier also checks every paid edge
against the distance labels and checks that every free conjugation leaves
its label unchanged. These inequalities prove the lower bound for every
word with arbitrary interleaved free maps. Hence the independent finite
metric is exact, without using the common-pivot theorem to prune its words.

## What is new and what remains open

The new statement is the arbitrary-role small-product theorem, in particular
all invertible targets over two local F_2-algebras at every role count.
The finite-subspace avoidance argument and Gaussian elimination are
classical. Their use to choose a complete common scalar pivot flag closes
the product gap left in #4787 while preserving the exact column bound.
The k<=q condition is necessary for a theorem covering every role count:
ToikY #4334 and #4601 already give two-role cost-three examples with
k=q+1 and delta=2. Their examples are cited, not replayed as this result.
No claim is made that k<=q is necessary for an individual target.

Singular endpoints, products with more than q components at n>=3, matrix
blocks in a semilocal quotient, and a complete physical supplier are not
classified. Native coefficient preparation, routing, frames, restoration,
precision, stock and the full recursive bill remain unknown. This is a
scoped algebraic proof, not a complete multiplication theorem or new kappa.
Independent human and formal proof-kernel review are unclaimed.

This contribution was produced by Nick Petalas. Credit Nick Petalas #4787
for the local arbitrary-role theorem, active-column chart and open product
question; #4601 for the local-product two-role theorem; ToikY #4334 for
the field-product threshold; and Nick Petalas #4243 and Wentao Li #4099,
following #2513, for the alphabet, normal form and column lower bound.
Predecessor files and attribution are unchanged. Apache-2.0.
