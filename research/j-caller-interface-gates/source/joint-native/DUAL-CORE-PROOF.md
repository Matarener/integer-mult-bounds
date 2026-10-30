# Changed dual source retractions and the remaining charged gap

This calculation changes the base core. The preceding fixed-core gate
does not imply it. The changed dual core does save four units in one
inverse coefficient, but its literal early continuation costs two. Its
best complete equal-volume native mass is consequently still at least
two units above stock in the separately charged architecture below.

Take `q>=2`, `n=2q+2`, `k=2q+1`, `m=4q+4`, `f>=1`. Keep the actual
response `J^2=-I`, old fresh prefix `F_s=N_s...N_1`, and declared public
target **F_k J**. All original fields and additional dirty fields are
arbitrary. A changed public/owner endpoint is outside this statement.
The current physical phase is the frozen
`J_f=i^(f+1) Z U`, not the incorrect constant-i normalization.

The first two owner functionals are `r1=(J,0)`, `r2=(-I,I)`. Choose

    w1=(-J,lambda*J)^T,   w2=(mu,1+mu)^T.

Both are normalized: `r_i w_i=I`. In the fixed initial beta/c chart their
transported query directions are exactly

    u1=e_a+e_b1+(lambda+1)J sum_r e_cr,
    u2=e_t+sum_r e_cr+(mu+1)J e_b1.

The stated literal compiler therefore has one extra source J
continuation when `lambda!=-1`, and one when `mu!=-1`. These are separate
query sites. Let their indicators be c1,c2. If B1,B2 are the old retarded
source codes, the new ones are

    P1tilde=J^c1 B1,  P2tilde=J^c2 B2,
    Q1=J^-1 P1tilde J.

The source conjugation and each continuation retain the physical
fresh-prefix chart. An outgoing source code is not replaced by a raw
ADDRESS operator.

The owner-plane updates are

    T1=[[Q1,0],[-lambda*(Q1-I),I]],
    T2=I+(mu,1+mu)^T (P2tilde-I) (-I,I).

They are invertible over the full noncommutative operator ring. For
`K=T2 T1`, direct multiplication gives

    (K^-1)_row1 =
      [Q1^-1((1+mu)I-mu*P2tilde^-1),
       mu*Q1^-1(P2tilde^-1-I)].                    (1)

The producer verifies this as a polynomial identity in the central
variables lambda,mu with free noncommuting Q1,P2tilde coefficients.
No numerical parameter screen proves (1).

At the dual choice `lambda=-1,mu=0`, the cross pairings both vanish:
`r1 w2=r2 w1=0`. Thus the two rank-one updates commute and

    K=[[Q1,0],[Q1-P2tilde,P2tilde]]
      =L diag(Q1,P2tilde) L^-1,  L=[[I,0],[I,I]],

    K^-1=[[Q1^-1,0],
           [Q1^-1-P2tilde^-1,P2tilde^-1]].         (2)

Assume the later retained interface has homogeneous pivots

    (U,V)=(Du*K_row2,Dv*K_row1),
    Dv=D_k(-D_(k-2))...(-D5),   D_s=B_s J.

Arbitrary public coupling L is retained. The unique joint inverse from
all original independent columns then has physical original-t/current-V
coefficient

    C_tV=(1+mu) A-mu B,
    A=F J Q1^-1 Dv^-1 F^-1,
    B=F J Q1^-1 P2tilde^-1 Dv^-1 F^-1.             (3)

Public-reader fusion cannot alter (3). No prior diagonal factory
cleanup is assumed. A different retired owner or a changed public row
does alter this required coefficient and is not covered.

For the dual choice, (3) is the single operator
`C=F B1^-1 J Dv^-1 F^-1`; P2tilde disappears exactly. This admits a
support proof for arbitrary physical monomial source posts S_s. They
need not commute any old or future Fourier frame. The literal stage has

    B_s=F_s^-1 S_s F_(s-1) J,
    D_s=-F_s^-1 S_s F_(s-1),
    Dv=-F^-1 S_k N_(k-1) S_(k-2)...S5 F4.

Put `R=-F Dv J^-1 F1^-1 S1`. Then **C R=F J** exactly. With
`K2=F1 J F1^-1`, the complement telescopes to

    R=S_k N_(k-1) S_(k-2)...S5 N4 N3 N2 K2^-1 S1. (4)

The sign in (4) is plus. There are q+1 rank-2f fresh N factors and one
already admitted rank-2f source K2 inverse. Thus R has maximum row
support at most `2^((2q+4)f)`. Since every row of full target FJ has
`2^(mf)` nonzeros, **every row of C has at least `2^(2qf)` nonzeros**.
This argument uses no Clifford assumption on the source posts or on J,
apart from the declared support/arity of K2 and the full target.

For the frozen actual J and whole-plane swaps, the exact Clifford ranks
of all strata are sharper and simple. Let `O=sum_(odd s=5..k) E_s` on
one p or q half. Each of the two halves has the same binary polar
matrix. The core blocks on planes0,1,2 are:

| c1,c2 | Gamma(A)-O | Gamma(B)-O |
| --- | --- | --- |
| 0,0 | diag(0,1,0) | [[1,1,0],[1,0,0],[0,0,1]] |
| 0,1 | diag(0,1,0) | [[0,1,1],[1,0,0],[1,0,0]] |
| 1,0 | [[1,1,0],[1,0,0],[0,0,0]] | diag(0,1,1) |
| 1,1 | [[1,1,0],[1,0,0],[0,0,0]] | [[1,0,1],[0,1,0],[1,0,0]] |

This is an all-q calculation. In binary phase/permutation form,
`(Gamma,pi)(Delta,rho)=(Gamma+pi*Delta*pi^T,pi*rho)`.
The incoming core acts only on0,1,2. The permutation of Dv is the cycle
`0->5->7->...->k->0`, and its polar is O. Applying the composition rule
to `F X Dv^-1 F^-1`, where X is either entrance core in (3), leaves
the fixed core block `Gamma(X)+E0+E_(pi_X(0))` and the disjoint O.
Multiplying the fixed three-plane core gives the displayed table.
Therefore, for every q,f,

    rank(A)/f=2q+2c1,
    rank(B)/f=2q+4 if c1=c2, else2q+2.             (5)

The actual all-f operator is retained, not inferred from f1 tableaus:

    A_f=i^((6-3q-c1)(1-f)) A_1^tensor(f),
    B_f=i^((6-3q-c1-c2)(1-f)) B_1^tensor(f),

after bit regrouping. The producer checks these literal phase families
in all four f residues. Tensoring A+B is never used.

If `mu=0`, only A survives. If `mu=-1`, only B survives. Otherwise c2=1
and B has two more native units than A. For every row, subtracting the
lower-support ray can remove at most `2^(rank(A))` entries of the
nonzero B ray. Thus the mixed case still has at least
`2^(rank(B))-2^(rank(A))` surviving entries, even for f-dependent nonzero
Gaussian scalar coefficients. No coefficient-size or Gram assumption is
needed here.

The exact resulting support exponents and separately charged cost gaps
are:

| lambda | mu | Extra J queries | Cleanup exponent/f | Complete mass minus stock |
| --- | --- | ---: | ---: | ---: |
| -1 | -1 | 0 | 2q+4 | at least4 |
| other | -1 | 1 | 2q+2 | at least4 |
| -1 | 0 | 1 | 2q | at least2 |
| other | 0 | 2 | 2q+2 | at least6 |
| -1 | other than-1,0 | 1 | 2q+2 | at least4 |
| other | other than-1,0 | 2 | 2q+4 | at least8 |

The support statements are unweighted bank/address circuit results:
total actual native arity plus the literal binary-ADD count is at least
the listed exponent times f, up to an absolute additive constant in the
two-ray cases. Arbitrary extra independent dirty banks and exact
restoration do not change the required original-column coefficient.

The final mass column additionally assumes **equal-volume full-bank
native child normalization**, the parent's stated full-scan transfer
premises, and separately charged source/query/continuation sites. The
prefix has native mass `nm-2q+2(c1+c2)` in this compiler. Positive fixed
relative helper volumes alone do not justify this unweighted mass
comparison. Partial/local scans, an altered transfer or a query fused
across these sites require a new bill.

The caller owns the source-bound literal changed prefix and all-column
binding. The algebra above applies to every q satisfying that interface;
finite physical fixtures do not by themselves establish its all-q
implementation. A chronological owner-retirement interface, a changed
retained continuation, source/continuation fusion, another retraction
family or a coupled endpoint remains outside this gate. No improved
kappa or completed supplier is claimed.
