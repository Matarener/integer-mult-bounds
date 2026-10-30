# Every intermediate Schur rank attains the dimension lower bound

Prepared for SHIN09-git with substantial OpenAI Codex assistance.
Apache-2.0. This is a scoped algebraic proof, not a physical supplier theorem.

Final overlap refresh found apoursh's concurrent PR6053, opened during this
session, proving the same dimension law and a closed minimum-rank formula.
This coordinate-minor derivation is retained as a separate argument for the
source-bound audit in AUDIT.md. No novel-theorem or priority claim is retained.
The exact reviewed PR6053 proof is included as reference6053.md.

## Statement and exact dependence

Let K be any field, d >= 1, A,B invertible d by d matrices, and H arbitrary.
We seek commuting idempotents P,Q of dimension n, with leading blocks
P11=A, Q11=B, (PQ)11=H. Let S,Z be their Schur complements at those
invertible leading blocks, and let rho=rank(SZ-ZS).

Put T00=I-A-B+H, T10=A-H, T01=B-H, T11=H and
nu=sum nullity(Tj), with j=10,01,11. Define

    n0   = rank(T00) + 3d - nu,
    nmax = rank(T00) + 3d + nu.

Let G,G' be the ordered maps below and T=diag(T10,T01,T11).
Put rho0=rank(T G G' T). Then for every integer rho in [rho0,2d],

    n_min(rho) = max(n0 + rho - rho0, nmax - 2(2d-rho)).          (1)

No smaller rank is feasible. At any fixed n >= n0 the feasible ranks are
exactly the integers from rho0 to

    min(2d, rho0+n-n0, floor((n-nmax+4d)/2)).                    (2)

There is no pair at n<n0. Formula (1) answers Open next question 1 of
Nick Petalas's PR6031 over every field and dimension, under its stated
invertible-pivot/common-deletion hypotheses.

The sector reduction and lower bounds are Petalas #6031, using Krzysztof
Wojt #5128 and the ordered-factor lineage. Their unchanged proofs are
retained as reference6031.md and reference5128.md. The distinct step here is the
block-admissible attainment construction in Sections 3–4. No priority
claim is made for the elementary nonsingular-minor fact.

## 1. Sector reduction and cost

For each j=00,10,01,11 choose a vector space Vj and Xj:Vj -> K^d,
Yj:K^d -> Vj with Xj Yj=Tj. Concatenating the X maps as pi and the Y
maps as i gives pi i=I. The diagonal sector projections P0,Q0 commute
and are idempotent. In a basis [i,ker pi], their conjugates have the
prescribed leading blocks. Conversely the joint eigenspaces of any
commuting idempotents give exactly these factorizations; characteristic
two causes no difficulty since 0 and 1 remain distinct.

In the three active sectors set Ij=im Xj and Nj=ker Yj.
They satisfy im Tj subset Ij and Nj subset ker Tj. For these subspaces,

    min dim Vj = dim Ij + d - dim Nj - rank Tj.                 (3)

The rank inequality gives the lower bound. For attainment choose a
basis sigma of im Tj, write Tj=sigma phi, let psi read the coordinates
of a complement of Nj in ker Tj, and extend sigma to a basis of Ij
by tau. Then Xj=[sigma,0,tau], Yj=[phi;psi;0] give (3), the prescribed
image and kernel, and XjYj=Tj. The 00 sector is a rank factorization.

Write a=sum codim Ij, b=sum dim Nj over active sectors. The exact
least total dimension for these choices is therefore

    n = nmax-a-b.                                             (4)

Padding only the 00 sector attains every larger n with the same rho.

The ordered maps on U=K^d are

    G(x,y) = (A^-1 y, -B^-1(Hx+y),
              (I-B^-1 H)x + (A^-1-B^-1)y),
    G'(v10,v01,v11) =
       (A^-1 v10 - B^-1 v01 + (A^-1-B^-1)v11,
        H B^-1 v01 + (H B^-1-I)v11).

With X=diag(X10,X01,X11), Y=diag(Y10,Y01,Y11), the
Schur-commutator rank equals rank(Y G G' X). These are the ordered
#5128/#6031 maps; H is not commuted with either inverse.

## 2. Defect pairing

For each active j fix a basis of the left kernel of Tj and a basis
of its right kernel. Lift a left-kernel row w to a covector on U^2
and a right-kernel column z to a vector on U^2 as follows:

| sector | left lift e(w) | right lift k(z) |
|---|---|---|
| 10 | (wA,w) | (-z,Az) |
| 01 | (0,w) | (-z,0) |
| 11 | (0,-w) | (z,0) |

Direct multiplication gives e(w)G' equal to the pure j-sector
covector w, and Gk(z) equal to the pure j-sector vector z.
These identities use, respectively, wTj=0 and Tj z=0.
G is injective: G(x,y)=0 first forces y=0, then Hx=0, then x=0.
G' is onto: a row (u,v) annihilating it has u=0 from its first
component, then vHB^-1=0 and v(HB^-1-I)=0, hence v=0.
Thus all nu left lifts are independent,
as are all nu right lifts; in particular nu<=2d.

Let E be the nu by 2d matrix of left lifts, K the 2d by nu matrix
of right lifts, and C=E K. Changing either within-sector basis
changes C by invertible block row/column factors, so its rank is
well defined. Let r=rank C.

Choose any subset R of the original left basis indices and any subset
J of the original right basis indices. In each sector define Ij to be
the common annihilator of its retained left basis vectors, and Nj
to be the span of its retained right basis vectors. These choices
are admissible. No vector has been mixed across different sectors.

For this choice a=|R| and b=|J|. The annihilator of im(G'X) is
exactly the span of the selected left lifts, and ker(YG) is exactly
the span of the selected right lifts. To see exactness, any row
annihilating G'X maps under the injective map e -> eG' into the
block annihilator of I; every such block covector already has its
unique listed lift. The analogous assertion uses the injectivity of
G and the pure-sector lifts of N.

Consequently, using the restriction of E_R to span(K_J),

    rho = 2d-a-b+rank C[R,J].                                 (5)

Indeed im(G'X)=ker E_R has dimension 2d-a and its intersection
with ker(YG)=im K_J has dimension b-rank C[R,J].

At R=J=all indices, the cost is n0 and the rank is forced to rho0,
so (5) also gives

    rho0 = 2d-2nu+r.                                         (6)

This agrees with rank(T G G' T): the latter uses the same images
im Tj and kernels ker Tj in the rank formula of #6031 Section 1.

## 3. A coordinate-minor chain

Every rank-r matrix C contains a nonsingular r by r coordinate
submatrix C[R*,J*]; the empty minor is used when r=0.
Begin with every row and column retained.

First delete, one at a time, the nu-r rows outside R*, followed by
the nu-r columns outside J*. Each retained matrix contains the same
rank-r minor and is a submatrix of C, so its rank remains r.
After t deletions, 0<=t<=2(nu-r), equations (4)–(6) give

    rho=rho0+t,   n=n0+t=n0+rho-rho0.

At the end the retained matrix is a nonsingular r by r minor,
a=b=r and rho=2d-r.

Now an invertible s by s matrix, s>=1, has a nonzero cofactor:
its adjugate is det(C) C^-1 and is nonzero. Delete the row and
column of one such cofactor. The retained (s-1) by (s-1) matrix is
nonsingular. Repeat until the empty minor. At retained size s,

    a=b=s,   rho=2d-s,   n=nmax-2s=nmax-2(2d-rho).

Thus every integer rank from rho0 through 2d occurs. The construction
uses only deletion of original basis vectors. Even for a finite field,
it never asks for a generic vector, a nonempty Zariski-open set, or an
arbitrary transversal subject to a sector constraint.

## 4. Match the lower bound

The two branches of (1) are equal at rho=2d-r, by (6) and
nmax-n0=2nu. Below this crossover the slope-one branch is larger;
above it the slope-two branch is larger. Section 3 attains exactly
the larger branch in both phases. With #6031's lower bounds, (1)
follows. Padding the 00 sector and solving the two inequalities in
(1) for rho proves (2).

The edge cases are included: r=0 has only the first phase; r=nu has
only the second phase; nu=0 gives the unique rank 2d already at n0.
The empty Schur complement at n=d has rank zero.

## 5. What the evidence can and cannot establish

For the complete d=2 ternary check, simultaneous conjugation by
W in GL_d(K) sends (A,B,H) to (WAW^-1,WBW^-1,WHW^-1).
Conjugate a witness P,Q by diag(W,I_(n-d)); this changes precisely
those leading blocks and leaves the two Schur complements unchanged.
The inverse transformation proves invariance of every feasible rank
and least dimension. The exact finite group partition therefore lets
8,136 representatives cover all 186,624 ternary input triples.
The action table, disjoint coverage and Burnside orbit count are
checked separately. Literal witnesses are built for representatives,
not separately for all 186,624 raw triples.

The executable constructor uses exact prime-field arithmetic or rational
fractions. Independent finite subspace enumeration and literal full-matrix
checks corroborate the construction on declared finite domains. They do
not replace Sections 1–4, prove every field by testing, or certify a
physical header. The theorem inherits the common deletion, invertible
pivot and commuting-idempotent setting. Singular pivots, coefficient rings,
multiple deletions, native realization, ownership/restoration, precision,
stock and outer costs are outside its claim. No new kappa follows.

Full independent human or formal-kernel review is not claimed.
