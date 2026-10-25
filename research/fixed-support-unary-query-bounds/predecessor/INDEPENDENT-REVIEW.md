# Independent review of the fixed-support unary tariff

Review date: 2026-10-19 UTC. Outcome: **the sharp 2n theorem is valid under
the stated model, including every finite number of arbitrary restored dirty
banks. No material mathematical gap found.** The native balanced-spectrum
premise also follows from the displayed literal chirp formula, as proved below.

This review credits the theorem and initial proof to the frozen
`kappa-changed-endpoints-20261019T0153Z/fixed-support-audit/PROOF.md` and
`witness.py`. The adjacent scalar quartic theorem and primitive-scan
counterexample are credited to that round's `coded-quadratic-caller` sources;
their native formulas are credited to its `stabilizer-escape` sources. This
review supplies a separate derivation and an independent exact checker. It
does not relabel these prior findings as new constructions. All work here is
AI-assisted local mathematical review; no publication or upstream acceptance
is asserted. Frozen producer bytes and their hashes are recorded in
`INPUT-MANIFEST.json`, including scientific pin
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` where recorded by those sources.

## Exact theorem being accepted

Let K be a characteristic-zero field containing i. Let f>=1 be an integer,
d=4^f, and X be a d-dimensional K-space. Let N^2=-I and suppose its +i and
-i eigenspaces both have dimension r=d/2. On Y=X tensor X put

    S(x tensor y)=y tensor x,   A=(N tensor I)S,   B=iA.

For finite integers m>=n>=1 consider m banks in Y with independent arbitrary
inputs. Free bridges are exactly GL_m(R), where R=K[S]/(S^2-1) acts by the
displayed internal swap. One paid call is A or A^-1 on one bank. The required
operator endpoint is

    T=diag(A^2 I_n,I_(m-n)).

All non-output banks must be restored on every input. The optimum is exactly
2n paid calls. The n=0 case is trivially zero. The bound includes all bridge
coefficients in K, all query signs, all circuit lengths, and every finite m;
no bound on helper count or clean-state assumption is used.

If this particular native carrier is assigned arity 2f per A/A^-1 call,
its total paid native arity is at least 4nf. Native arity pricing is a
separate carrier premise. No precision, physical execution, recursive moment
or kappa conclusion is part of this theorem.

## Literal balanced spectrum

The source carrier specifies

    C=alpha I+beta X,  C^-1=beta I+alpha X,
    alpha=(1+i)/2, beta=(1-i)/2,
    N1=i (Z C^-1) tensor (Z C),
    N_f=i^(1-f) N1^(tensor f),

up to the harmless permutation that groups equal chunk positions. Here X is
the bit flip and Z=diag(1,-1), so ZX=-XZ. Direct multiplication gives

    (Z C^-1)^2=(beta^2-alpha^2)I=-iI,
    (Z C)^2=(alpha^2-beta^2)I=iI.

Both ZC and ZC^-1 have trace zero. Consequently N1^2=-I and tr(N1)=0.
For every f>=1,

    N_f^2=i^(2-2f)(-1)^f I=-I,
    tr(N_f)=i^(1-f)(tr N1)^f=0.

The minimal polynomial divides t^2+1, which has distinct roots over K.
Thus N_f is diagonalizable with eigenvalues in {i,-i}; trace zero in
characteristic zero forces both eigenspaces to have dimension 4^f/2.
This proves the actual displayed carrier's balanced spectrum for every f.
The phase i^(1-f) is essential: it cannot be replaced by a single i
normalization independent of tensor convention.

This derivation checks the mathematical operator formula. It does not
independently re-audit the producer's full native lowering, primitive access,
or physical head-return implementation. Those remain outside this review.

## Actual D8 constituents, with phase retained

Since A^2=N tensor N, one has B^4=I and S^2=I. Moreover

    SBS=i(I tensor N)S=B^-1.

The factor i is necessary: SAS=A^-1 is false for this A. On X_+ tensor X_+
the operator B is -S; on X_- tensor X_- it is S. Therefore the four actual
one-dimensional constituents are

| B | S | Subspace | Multiplicity |
|---|---|---|---|
| -1 | +1 | Sym^2(X_+) | r(r+1)/2 |
| +1 | -1 | exterior^2(X_+) | r(r-1)/2 |
| +1 | +1 | Sym^2(X_-) | r(r+1)/2 |
| -1 | -1 | exterior^2(X_-) | r(r-1)/2 |

Every multiplicity is positive because f>=1 gives r>=2. This last condition
matters: a different carrier with r=1 does not furnish all four characters
used in the argument.

For x in X_+, y in X_-, write p=x tensor y and q=y tensor x. Then

    Bp=q, Bq=-p, Sp=q, Sq=p.

In the basis (p-iq,q-ip), whose change-of-basis determinant is 2,

    rho(B)=diag(i,-i),    rho(S)=[[0,1],[1,0]].

This constituent occurs r^2 times. Its dimension contribution 2r^2 plus
the four one-dimensional multiplicities is 4r^2=d^2, as required. These
evaluations are restrictions to native invariant subspaces; no equality in
a small quotient is used to infer equality on the full native space.

## Bridge extraction and the order of factors

Replace each bank query A^epsilon by B^epsilon and absorb its bank scalar
i^(-epsilon) into an adjacent free bridge. Consider the resulting circuit

    C=H_k Q_k H_(k-1) ... Q_1 H_0.

Set P_j=H_(j-1)...H_0, H=H_k...H_0. Direct telescoping gives

    C=H (P_k^-1 Q_k P_k) ... (P_1^-1 Q_1 P_1)=H W.

For a query on bank b_j, write

    u_j=P_j^-1 e_(b_j),    v_j=e_(b_j)^T P_j,
    d_j=B^epsilon_j-I,     F_j=I+u_j d_j v_j,
    W=F_k...F_1.

Then u_j and v_j have coefficients in R and v_j u_j=1. This extraction
does not commute B past an R coefficient.

At each actual character (B,S)=(1,+1),(1,-1), every F_j evaluates to I,
while the required endpoint evaluates to J=diag(-I_n,I_(m-n)). Hence
H(+1)=H(-1)=J. Since R is isomorphic to K x K by the two S evaluations,
this forces H=J entrywise. Thus the exact normalized endpoint is

    W=J T=diag(B^2 I_n,I_(m-n)).

This argument retains the arbitrary total bridge; it does not assume that
bridge away.

Define U=[u_1 ... u_k], let V have rows v_j, put D=diag(d_j), and let
L_ab=v_a u_b for a>b, with all other entries zero. Expansion of the ordered
product gives the finite identity

    W-I=U G V,
    G=D sum_(t=0)^(k-1)(L D)^t=D(I-LD)^-1.

Indeed, the term with indices a_t>...>a_0 is exactly

    u_(a_t) d_(a_t) (v_(a_t)u_(a_(t-1))) d_(a_(t-1)) ... d_(a_0) v_(a_0).

Strict lower triangularity makes the series finite even in a
noncommutative operator ring. Equivalently G=(I-DL)^-1 D. The expression
(I-LD)^-1 D is generally wrong. When every represented d_j is invertible,

    G^-1=D^-1-L.

No inverse of B-I in the full group algebra is needed or claimed.

## Rank argument with all dirty helpers present

For s in {+1,-1}, let U_s,V_s be evaluation of the R entries at S=s, and
write a_s=rank(U_s), b_s=rank(V_s). In the two-dimensional constituent,
diagonalize S and regroup the bank and query coordinates. This identifies
rho(U) with U_+ direct-sum U_- and rho(V) with V_+ direct-sum V_-.

Because rho(B^2)=-I_2, the exact normalized endpoint has
rank(rho(W-I))=2n, including its zero blocks on every restored helper. The
factorization therefore yields

    a_++a_- >= 2n,       b_++b_- >= 2n.

At either actual character (B,S)=(-1,s), every query sign has d_j=-2.
Consequently G_s^-1=-I_k/2-L_s is lower triangular and invertible. The
endpoint has W-I=0 there, so

    U_s G_s V_s=0.

The image of G_s V_s has dimension b_s and is contained in ker(U_s), of
dimension k-a_s. Thus k>=a_s+b_s for each s. Summing gives

    2k >= (a_++a_-)+(b_++b_-) >= 4n.

Therefore k>=2n. This proves the all-m result. Individual U_s or V_s ranks
need not be inferred separately from the two-dimensional component when
m>n; the summed argument is what closes that issue. Applying A twice to
each output bank, while touching no helper, attains 2n.

## Independent exact evidence

`independent_check.py` imports no producer modules. It uses two explicitly
different models:

* Full Q(i)[D8], represented on all eight group basis elements with exact
  Gaussian rational coefficients. For three banks and five fixed, distinct
  R-valued bridge conjugations, it checks all 32 query-sign patterns, direct
  products, split rank-one factors, and chronological resolvents. Every
  pattern detects the deliberately reversed resolvent ordering.
* Rational realification of literal chirp matrices. It checks the actual
  N1 spectrum, normalized f=2 spectrum, and actual f=1 D8 character
  projector ranks 3,1,3,1 with four copies of the two-dimensional
  constituent. Removing the B=iA phase is detected.

It also independently checks the quartic opposite-character scalar identity
in the full rational regular representation of Q[z]/(z^4+1), for both query
signs, and the zero-helper per-bit identity and inverse on both independent
public inputs. The per-bit word is additionally checked after its optional
forward-orientation correction.

`validate_review.py` authenticates the prior proof/witness/validation hashes
and the relevant native-source receipts. It makes byte-identical copies of
the producer witnesses inside `source-replay/`, runs those copies and the
new checker in normal and optimized Python, compares outputs, reproduces
the saved fixed-support witness receipt exactly, and tests explicit failure
controls in both modes. It verifies all frozen input hashes again afterward.
Current results are in `VALIDATION.json` and `INPUT-MANIFEST.json`.

Reproduce from this directory with:

    python3 -B validate_review.py

These are finite exact identity checks, not exhaustive searches over words
or bridge matrices. The quantified theorem is supported by the written
proof above. There is no formal-kernel proof in this package.

## Limits and unresolved implications

The theorem does not include other ADDRESS or Pauli controllers outside
K[S], changing support, other native paid operators, approximate equality,
nonlinear/noninvertible bridges, or weakened restoration endpoints. The
same proof is not automatically transferable to an A^4=-I carrier.
The separate quartic scalar-bridge argument is reviewed in
`GROUPED-SCOPE.md`; it must retain its narrower bridge alphabet.

The zero-helper counterexample uses explicit ADDRESS-valued shears and an
unbounded-in-f scan count, so it is compatible with both fixed-alphabet
query theorems. It rules out an unrestricted native-query-mass floor under
that broader primitive model. It does not supply a constant-scan algorithm
or a cost-aware lower bound.

Upstream overlap and publication permission are intentionally unresolved
here and belong to the parent's publication ledger. No new conditional
kappa, global native impossibility, chronological hosting, compatible joint
supplier, precision or physical-execution result follows from this review.
