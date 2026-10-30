# Independent audit of the native equality-cut tariff and its caller contract

Prepared for Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex
assistance in derivation, checking, and writing. New work is Apache-2.0.

**Finding:** the signed Clifford tariff and the complete-word, initial-cache,
and approximation implications in Sections 3–5 of Ali Romman's
[PR #5588 proof](https://github.com/aliromman/integer-mult-bounds/blob/97db3fb45cd93a350e300781d75440d14e6a1f73/research/native-equality-cut/PROOF.md)
hold under their stated hypotheses. No mathematical defect was found in
that scope. The derivation below uses a trace expansion to verify the
signed intersection, then treats all register banks as typed rectangular
maps. It does not infer correctness of a particular physical caller or
admit a new multiplication bound.

The reviewed source head is
`97db3fb45cd93a350e300781d75440d14e6a1f73`. The unchanged proof and README
are authenticated inputs in [SOURCES.json](SOURCES.json); the repository
base is `df0137efd35e11b4445734bf612bdd4c7ebc330c`.

## 1. Quantified statement and the equality projector

Let \(n\ge1\), \(D=2^n\), and \(f\ge1\) be integers. A field is
\(V_f=(\mathbb C^D)^{\otimes f}\). For an integer
\(1\le k\le\lfloor f/2\rfloor\), let \(E_k\) be the orthogonal
projector onto basis strings with equal addresses in each of the pairs
\((1,2),(3,4),\ldots,(2k-1,2k)\). Set

\[
 a_k=\operatorname{rank}E_k=D^{f-k}.
\]

For a bank of \(m\) fields the cut projector is
\(E_k^{[m]}=\bigoplus_{j=1}^m E_k\). For a map \(A\) from one bank
to another, define

\[
 c_k(A)=\operatorname{rank}\bigl((I-E_{\rm out})A E_{\rm in}\bigr).
 \tag{1}
\]

Input and output projectors in (1) are those of the actual banks, which
may have different numbers of fields. All ranks are over \(\mathbb C\).

For an \(n\)-qubit unitary Clifford operator \(U\), let \(Z\) denote
the diagonal binary Pauli label space and set

\[
 r(U)=n-\dim_{\mathbb F_2}(Z\cap UZU^*).
 \tag{2}
\]

Here the intersection in (2) is of Pauli labels, ignoring signs. If
\(U Z_j U^*\) has binary \(X\)-label \(x_j\), then
\(r(U)=\operatorname{rank}_{\mathbb F_2}[x_1\ \cdots\ x_n]\): the
kernel consists exactly of diagonal images. The first result to audit is

\[
 c_k(U^{\otimes f})=a_k(1-2^{-kr(U)}),                 \tag{3}
\]

with every nonzero singular value of this cut block equal to one.
When \(r=0\) the cut block is zero. At width \(f=1\) there is no
admissible positive \(k\), so this family supplies no inequality.

## 2. Signed intersection from a trace calculation

First consider one pair. For \(v\in\mathbb F_2^n\), write
\(Z_v e_x=(-1)^{v\cdot x}e_x\). Its equality projector is

\[
 E=\frac1D\sum_v Z_v\otimes Z_v.
 \tag{4}
\]

Indeed its diagonal entry at \((x,y)\) is
\(D^{-1}\sum_v(-1)^{v\cdot(x+y)}\), which is one exactly when
\(x=y\). Put \(W_w=UZ_wU^*\), \(R=U\otimes U\), and

\[
 F=RER^*=\frac1D\sum_w W_w\otimes W_w.
\]

Each \(W_w\) is a Hermitian Pauli, and the map \(w\mapsto W_w\)
is injective and multiplicative, including its signs. For each \(v,w\)
the one-column Paulis commute or anticommute. Their two tensor copies
therefore commute: the commutation factor is \((\pm1)^2=1\).
Consequently \(E\) and \(F\) commute and \(EF\) is the orthogonal
projector onto their intersection.

Expand its trace directly:

\[
 \operatorname{Tr}(EF)
   =\frac1{D^2}\sum_{v,w}
        \operatorname{Tr}(Z_v W_w)^2.                \tag{5}
\]

This is the square of the trace, not an assumed absolute-value square.
Pauli trace orthogonality makes it zero unless \(W_w=\pm Z_v\).
In that case the trace is \(\pm D\), so its contribution to (5) is
exactly one. Hermiticity rules out \(W_w=\pm iZ_v\). For precisely
\(2^{n-r(U)}\) choices of \(w\), its image has a diagonal label;
there is one \(v\) for each. Thus

\[
 \operatorname{rank}(EF)=\operatorname{Tr}(EF)
   =2^{n-r(U)}=D\,2^{-r(U)}.                         \tag{6}
\]

This calculation explicitly handles negative diagonal images and
images containing \(Y\) factors. Discarding Clifford signs before
forming the tensor-pair stabilizers would not by itself justify (6).

For comparison with the source's stabilizer-group proof, let
\(S_E=\{Z_v\otimes Z_v\}\) and \(S_F=\{W_w\otimes W_w\}\).
Each is a group of order \(2^n\), and their intersection has order
\(2^{n-r}\), by the same diagonal-image test. There is no negative
identity in their generated joint group. Otherwise, because the groups
commute, some \(Z_v\otimes Z_v=-(W_w\otimes W_w)\) would hold.
Equality of their Pauli labels first forces \(W_w=\pm Z_v\); its
tensor square then gives equality with a **positive** sign, a
contradiction. Hence the joint group has \(2^{n+r}\) elements and
contains no sign conflict. This verifies the specific premise needed
by the source's alternative stabilizer dimension count.

## 3. From the intersection to the exact tariff

Let \(C=(I-E)RE\). Its range before projecting by \(I-E\) is
\(\operatorname{ran}F\), and \(R\) maps \(\operatorname{ran}E\)
unitarily onto that space. More explicitly,

\[
 CC^*=(I-E)F(I-E)=(I-E)F,
\]

which is a projector because \(E\) and \(F\) commute. Thus the
nonzero singular values of \(C\) are all one, and

\[
 \operatorname{rank}C
  =\operatorname{rank}F-\operatorname{rank}(EF)
  =D(1-2^{-r}).
\]

For \(k\) pairs and \(f-2k\) remaining columns, the cut and its
conjugate are tensor products of these pair projectors and an identity.
They still commute. Their intersection has rank

\[
 (D2^{-r})^k D^{f-2k}=a_k2^{-kr},
\]

whereas each cut has rank \(a_k\). The same projector calculation
proves (3) and its singular-value statement for every allowed
\(n,f,k\). Both terms are integers: in particular
\(a_k2^{-kr}=2^{n(f-k)-kr}\), with exponent at least
\(n(f-2k)\ge0\).

Multiplying \(U\) by a global scalar phase does not alter its
conjugation action or any rank or singular value here. Also
\(r(U^{-1})=r(U)\), since conjugation by \(U\) identifies
\(Z\cap U^{-1}ZU\) with \(UZU^{-1}\cap Z\). Thus inverse calls
have the same tariff. Nonzero scalar multiples of a cut block have
the same rank, but their nonzero singular values are scaled by the
absolute value of that scalar; only the rank is needed for paid query
updates.

Two literal boundary examples distinguish the premises from their
unsigned rank consequences. On one qubit, take

\[
 C=\frac12\begin{pmatrix}1+i&1-i\\1-i&1+i\end{pmatrix},
 \qquad CZC^*=-Y.
\]

For \(C\otimes C\), the intersection of the equality subspace with
its image is the line spanned by
\((|00\rangle-|11\rangle)/\sqrt2\). Replacing the second factor by
\(\overline C\) changes that line to
\((|00\rangle+|11\rangle)/\sqrt2\). Both intersection ranks are
one, so a rank-only comparison misses this orientation error. The
source requires identical tensor factors; it does not identify these
two projectors. The exact projector numerators are checked by
`stabilizers.signed_matrix_controls`.

For a different boundary, left-compose \(C\otimes C\) with CNOT
whose control is the first tensor column and whose target is the
second. This CNOT is a unitary monomial map of the complete field, but
it does not preserve the equality cut. In the equality input basis
\((|00\rangle,|11\rangle)\), the resulting cut block has Gram
matrix \(I_2/2\), also checked by `signed_matrix_controls`. Its
nonzero singular values are \(1/\sqrt2\), not one. This is not a
counterexample to the theorem: such inter-column routing is already
excluded from its ordinary alphabet. It shows why unitary endpoint
frames must also preserve the cut.

## 4. Rectangular composition and all dirty directions

For composable maps \(B:H_0\to H_1\) and \(A:H_1\to H_2\), with
the respective bank projectors, insert
\(I=E_1+(I-E_1)\) to obtain

\[
 (AB)_{-+}=A_{--}B_{-+}+A_{-+}B_{++},\qquad
 c_k(AB)\le c_k(A)+c_k(B).                            \tag{7}
\]

Rank subadditivity and the two elementary product-rank inequalities
prove (7). No inverse, square shape, unitary assumption, fixed choice
of paid input, or absence of feedback is used.

A rectangular ordinary map satisfies
\(E_{\rm out}A=A E_{\rm in}\), so both of its cross blocks vanish.
A one-column monomial map uses the same address permutation in every
tensor column; it preserves equality and inequality in each pair, and
its diagonal weights do not change support. Its tensor lift therefore
commutes with \(E_k\), as does any linear combination of such lifts.
Scalar mixing between fields, register permutations, COPY, CLEAR,
zero-field insertion, and field selection intertwine the bank cuts.
They consequently have zero charge in (7).

An application of \(U^{\otimes f}\) on one field has the rank (3)
in its sole potentially nonzero bank cut block. For an update
\(y\leftarrow y+cU^{\otimes f}x\), that block is
\(c(I-E_k)U^{\otimes f}E_k\). It has the same rank for \(c\ne0\),
and rank zero for \(c=0\). This remains the rank calculation if the
alphabet permits a self update: the identity part contributes no cross
block. Overcharging a zero update is harmless to the upper bound.
If a primitive returns several fields, each output must be included
in a valid rank budget; the single-output tariff is not a multi-output
credit.

Represent the input as the direct sum of **every independent original
and dirty helper field**. Owned fields that actually start at zero
are inserted by a separate rectangular map. A chronological word is a
product of its complete state maps, so induction in (7) gives an upper
bound by the sum of all its paid cut ranks. COPY may increase bank
size, CLEAR may destroy information, and later paid arguments may
depend on all earlier responses. These facts do not change the matrix
identity (7).

Required output selection is a cut-intertwining map and cannot increase
the endpoint cut rank. This does not authorize ignoring required dirty
returns: they remain in the specified endpoint and are required for
correctness. To obtain a necessary condition one may project that
complete endpoint onto the disjoint target-job blocks. Independent
targets \(T_j^{\otimes f}\), each on its own independent input and
output field, then have additive cut ranks. With \(P_r\) paid calls
and \(T_r\) such target jobs of Fourier rank \(r\), the result is

\[
 a_k\sum_r T_r(1-2^{-kr})
 \le a_k\sum_r P_r(1-2^{-kr}).                        \tag{8}
\]

Repeated credit for the same input/output block would not satisfy this
independence premise. Since \(a_k>0\), it may be canceled in (8).
If fixed profiles are realizable at arbitrarily large widths, each
fixed positive \(k\) is covered by some such \(f\ge2k\). The same
inequality then holds for every \(k\), even if the program, feedback,
coefficients, and storage vary with \(f\).

## 5. A cached boundary has one joint initial rank

Let \(J:H_{\rm original}\to H_{\rm available}\) map all independent
inputs to the complete rows available at a chosen caller boundary.
It must specify the actual row versions and their dependence on those
inputs, including independent dirty helper fields. If \(W\) is the
subsequent word and \(S\) selects the required outputs, (7) gives

\[
 c_k(SWJ)\le c_k(J)+\sum_{\text{subsequent paid calls}}c_k(\text{call}).
 \tag{9}
\]

An exact target endpoint \(T\) therefore requires
\(c_k(T)\) to be at most the right side. In the ordinary initial
state, \(J\) consists of identities and zero insertions and has
\(c_k(J)=0\), recovering (8). At a cached boundary, the entire
cross matrix of \(J\) must be ranked jointly.

For example, let \(R\) be any one-field map with cut block \(C\).
The availability map \(J=(I,R,R)^\mathsf T\) on one independent
original has cut block \((0,C,C)^\mathsf T\), of rank
\(\operatorname{rank}C\), not twice that rank. Two copies of the
same response do not become two independent inputs. Conversely, rows
depending on separate independent originals can have disjoint domain
blocks and contribute additive rank. A nominal cache count cannot
distinguish these cases.

Omitting a nonordinary cache is also unsound: a free copy of an already
available \(Rx\) realizes that target with no new paid call, but it
uses the initial cross rank in \(J\). Equation (9) is a relative
boundary statement. It does not make producing those initial cached
rows free in a full physical invoice. A full-word accounting can start
before their production and charge those calls there instead.

## 6. Endpoint codes and approximation constants

Let \(L\) and \(R\) be invertible ordinary output and input codes,
respectively, intertwining the same bank cuts. Their restrictions to
the plus and minus subspaces are invertible, and

\[
 (LAR)_{-+}=L_{--}A_{-+}R_{++}.
\]

Thus these codes preserve cut rank exactly. This proves the exact
rank obstruction also for nonunitary invertible ordinary endpoint
codes, including invertible monomial frames. It does not preserve
singular values unless the relevant restrictions are unitary.

For the source's approximation statement, use independent unitary
target jobs and unitary cut-preserving endpoint frames. Their target
cut block \(B\) is a partial isometry with

\[
 q=\operatorname{rank}B=a_k\sum_r T_r(1-2^{-kr})
\]

unit nonzero singular values. Let the program cut block be \(A\),
with rank at most an integer paid budget \(b\). On the \(q\)-dimensional
initial singular subspace of \(B\), the kernel of \(A\) has
dimension at least \(q-b\). If \(q>b\), choose an orthonormal set
of \(q-b\) vectors there. For each such vector \(v\),
\((A-B)v=-Bv\) has norm one. Hence

\[
 \|A-B\|_{\rm op}\ge1,\qquad
 \|A-B\|_{\rm HS}^2\ge q-b.                         \tag{10}
\]

Projecting the full endpoint error onto its cut block cannot increase
either norm. In the zero-initial-rank case, take
\(b=a_k\sum_rP_r(1-2^{-kr})\); (10) is precisely the source's
unit operator-error floor and squared Hilbert–Schmidt floor
\(a_k\delta_k\). The same reasoning with caches uses
\(b=c_k(J)+a_k\sum_rP_r(1-2^{-kr})\), when a positive deficit
remains. These are bounds for words assembled from the exact ideal
paid maps. Approximation errors inside a query are not extra
unpriced linear operations in this model.

The unitary-frame restriction is necessary for the stated constants.
Multiplying the whole output by \(\varepsilon I\), with
\(0<\varepsilon<1\), is an invertible ordinary code and preserves
every cut rank. But it scales the error between a zero endpoint and
a unitary target to operator norm \(\varepsilon\), and its squared
Hilbert–Schmidt error by \(\varepsilon^2\). Thus the exact rank
obstruction survives while the numerical lower bounds with constant
one do not. The source explicitly states this limitation.

## 7. Audit disposition and boundaries

| Source assertion at the pinned head | Disposition in this review | Retained premise |
|---|---|---|
| Section 3: signed stabilizer intersection and no negative identity | Established by (5)–(6) and the explicit joint-group check | Unitary Clifford conjugation; the same operator on both tensor columns |
| Section 3, equation (4): exact tariff and unit singular values | Established in Section 3 for every admissible \(n,f,k\), including rank zero | Disjoint equality pairs and unchanged field capacity |
| Section 4: chronological paid-rank upper bound | Established by rectangular identity (7) | Every free map preserves the stated cut; every nonordinary call is charged |
| Section 4: independent targets and dirty inputs/returns | Established as the necessary condition (8) | Separate input/output job blocks and a complete specified endpoint |
| Section 4: invertible ordinary endpoint codes | Exact-rank invariance established in Section 6 | Both cut blocks are preserved and the codes are invertible |
| Section 4, equation (5): approximation floors | Established by the explicit kernel subspace in (10) | Independent unitary target blocks, unitary cut-preserving endpoint frames, exact paid gates |
| Section 5, equation (6): retained observations | Established by (9) and the duplicate-cache example | The complete actual availability matrix \(J\), not nominal rows |
| Sections 6–7: profile decision algorithm and semisimple row-return discussion | Outside this audit | No acceptance of those separate claims is inferred |
| A particular P104/G20 caller, physical execution, or multiplication theorem | Outside this audit | Actual source bindings, availability ledger, paid invoice, compiler, precision, and outer assumptions remain separate |

An operation acting on only one member of an equality pair need not
preserve the cut. Nor need arbitrary inter-column routing or a nonlinear
operation. Such changes are outside the declared free alphabet. With
different field capacities, (7) can still be formulated using correctly
typed projectors, but the common factor \(a_k\) in (8) cannot simply
be canceled across unlike fields.

The package's executable receipts provide finite exact corroboration
and controls for these implications. This note makes no claim about
their case counts; the counts and executed commands belong to the
receipt and verification documentation. The general result rests on
the quantified arguments above, not extrapolation from a finite
Clifford sample. This is a separate agent-assisted review, not
independent human acceptance or proof-kernel verification.

Ali Romman retains credit for the equality-cut invariant, Clifford
tariff, full-word extension, explicit cached-boundary contract, and
source theorem in PR #5588. The classical product-rank inequality,
Pauli/stabilizer theory, trace orthogonality, and rank-deficit
approximation principle are not new results. The source's credited
fused-block/dirty-host work, an664 and its reviewers, Adam Gall, Ross
Richardson, Chris R/Clear1nsight, and the P104/native/controller/compiler
lineage retain their attribution. This contribution checks the stated
proof obligation through a separate trace calculation and explicit
caller-domain accounting; it does not change the selected frontier.
