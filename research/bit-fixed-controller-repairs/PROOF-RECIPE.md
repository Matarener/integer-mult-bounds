# Exact repair count for the fixed routed involution recipe

This is a written all-parameter proof, with finite executable certificates.
It is not a formal-kernel proof or an admission theorem for a physical supplier.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.

## Model and theorem

Let \(B\geq1\), \(n=2B\), and work over \(\mathbb F_2\). Every bank contains an
arbitrary, independently chosen vector in a common vector space. Fix a
nonidentity linear involution \(N\), and put \(\epsilon=N+I\). Thus
\(\epsilon^2=0\), and \(I,\epsilon\) are linearly independent over
\(\mathbb F_2\): a nonzero scalar multiple of \(I\) cannot be nonzero and square
to zero. Consequently the dual-number algebra embeds in this representation.
The argument therefore covers every nonidentity involution, not just a
particular small matrix representation.

Use exactly the event word returned by the pinned `global_k.py:recipe(B)`,
with its bridge order, bank pairing and terminal pair exchange unchanged.
Replace its two local interfaces by

\[
 F(x,y)=(x,x+Ny),\qquad H(x,y)=(Nx+y,y).
\]

A bridge from pair \(s\) into pair \(d\) sends
\(x_d\leftarrow x_d+x_s\) and \(y_s\leftarrow y_s+y_d\).
Its source coefficient \(+1\) or \(-1\) has the same value in this field.

An allowed additional paid repair is a scalar-GL-conjugated application of
\(N\) to one bank:
\[
 Q_P=I+\epsilon P,\qquad
 P=uv^T,\quad v^Tu=1.
\]
Scalar mixing means matrices over \(\mathbb F_2\) on the bank index, tensored
with the identity on the bank contents. These scalar changes of basis and
their inverses are free only in the formal call-count model.

The target is \(N I_n\) on the original banks. For any finite number \(d\)
of extra independently dirty banks, their target is literal identity.
The fixed recipe acts as identity on these spectators.

**Theorem.** The minimum number of such additional repair calls is
\[
 k(B)=
 \begin{cases}
 2B+1,&B\text{ odd},\\
 2B-1,&B\text{ even}.
 \end{cases}
\]
The same minimum holds with any finite number of restored dirty spectators,
even if each additional repair mixes original and spectator banks.
Repairs can be placed after the fixed word. The lower bound also permits
inserting these complete constant-identity repair gates between its events.

This theorem does not allow changing the existing scalar topology, pairing,
local alphabet, or observation boundary. In particular it does not obstruct
the changed seeded-star topology or the separate closed hybrid controller.

## Endpoint derivation for every B

Write the original bank inputs as \(X_j,Y_j\), \(0\leq j<B\).
Immediately before the reverse local call on pair \(j\), write its current
second bank as \(t_j\). The first bank is still \(X_j\). The initial forward
call and each bridged pair of local calls give
\[
 t_0=X_0+NY_0,\qquad
 t_{j+1}=X_{j+1}+Y_{j+1}+N(X_j+t_j).
\]
For \(j<B-1\), the pair after its two local calls and its bridge/unbridge is
\[
 p_j=NX_j+t_j,\qquad q_j=NX_j+\epsilon t_j+X_{j+1}.
\]
For the last pair, the same formulas hold with \(X_B=0\).
These identities follow by substituting the four operations; they make no
clean-input assumption.

Set \(S_j=\sum_{k=0}^jY_k\). The recurrence gives
\[
 t_j=X_j+S_j+\epsilon b_j,\quad
 b_0=Y_0,\quad b_{j+1}=b_j+S_j.
\]
The descending terminal bridges send \(p_0\) to itself,
\(p_j\) to \(p_j+p_{j-1}\) for \(j\geq1\), and \(q_j\) to
\(\sum_{\ell=j}^{B-1}q_\ell\). The final exchange therefore gives
\[
\begin{aligned}
 x'_j&=X_j+\epsilon\sum_{\ell=j}^{B-1}S_\ell,\\
 y'_0&=Y_0+\epsilon(X_0+Y_0),\\
 y'_j&=Y_j+\epsilon(X_j+X_{j-1}+S_{j-1})\quad(j\geq1).
\end{aligned}
\]
This is a direct induction and telescoping calculation, valid for every B.

In grouped coordinate order \(x_0,\ldots,x_{B-1},y_0,\ldots,y_{B-1}\), the
endpoint is \(R_B=I+\epsilon A_B\), where
\[
 A_B=\begin{pmatrix}0&C\\D&E\end{pmatrix},\quad
 C_{jk}=(B-\max(j,k))\bmod2,
\]
\[
 D_{jk}=[k=j]+[j>0,\ k=j-1],\qquad
 E_{00}=1,\quad E_{jk}=[k<j]\ (j\geq1).
\]
All unspecified entries of E are zero. If \(L_{jk}=[k\leq j]\), then
\(C=L^TL\), so C and D are invertible. Thus A has rank \(2B\).

## Defect rank and trace

Because \(\epsilon^2=0\), the required repair relative to \(NI_n\) is
\[
 (NI_n)R_B^{-1}=I+\epsilon M_B,\qquad M_B=A_B+I_n.
\]
The upper-left block of M is identity. Block row elimination reduces its
rank to
\[
 \operatorname{rank}M_B=B+\operatorname{rank}(E+I_B+DC).
\]
For \(j\geq1\), row j of DC is row j of C plus row \(j-1\) of C.
Its k-entry is one precisely when \(k<j\), so this row equals row j of E.
Row zero of DC is row zero of C. As \(E_{00}=1\), the Schur block has
first row \(C_{0,*}\) and all subsequent rows \(e_j^T\).
Its first entry is \(B\bmod2\). Hence
\[
 \operatorname{rank}M_B=
 \begin{cases}2B,&B\text{ odd},\\2B-1,&B\text{ even}.\end{cases}
\]
The only nonzero diagonal entry of A is its y0 entry, so
\(\operatorname{tr}M_B=1\). Equivalently, every diagonal entry of M is one
except its y0 entry, which is zero.

When B is even, the kernel is generated by
\[
 z=e_{y_0}+\sum_{\substack{0\leq j<B\\j\text{ odd}}}e_{x_j}.
\]
Indeed the Schur block kills \(e_0\), and the upper block forces
\(x=Ce_0\), whose j-entry is \(j\bmod2\).
The rank calculation proves that this is the entire kernel.

## Lower bound, including arbitrary restored spectators

A rank-one operator \(P=uv^T\) is a nonzero idempotent precisely when
\(v^Tu=1\). It then has rank one and trace one. Conversely every such P is
scalar-conjugate to a coordinate projector: choose a basis consisting of u
followed by any basis of \(\ker v^T\).

Products of allowed repairs satisfy
\[
 \prod_{i=1}^k(I+\epsilon P_i)=I+\epsilon\sum_{i=1}^kP_i.
\]
For d dirty spectators the required coefficient is \(M_B\oplus0_d\).
Injectivity of the dual-number representation forces
\(\sum_iP_i=M_B\oplus0_d\), including every spectator row and column.
Rank subadditivity and the trace identity imply
\[
 k\geq\operatorname{rank}M_B,\qquad k\equiv1\pmod2.
\]
Thus k is at least \(2B+1\) for odd B and \(2B-1\) for even B,
independently of d. No reduction to a clean spectator is made.

For a repair inserted inside the fixed word, push it to the final cut.
Every fixed suffix is invertible over the dual numbers. If such a suffix
is \(S+\epsilon T\), its constant matrix S is invertible, and conjugation
sends \(I+\epsilon P\) to \(I+\epsilon SPS^{-1}\).
Its rank and trace are unchanged. This extends the same bound to inserted
constant-identity repair gates. It does not extend to changing the original
scalar gates or adding scalar changes that do not cancel within a repair.

## Explicit attaining words

Let \(m_j=M_Be_j\) be a column of M.

For odd B, take \(m_je_j^T\) for every \(j\ne y_0\), together with
\[
 (m_{y_0}+e_{y_0})e_{y_0}^T,\qquad e_{y_0}e_{y_0}^T.
\]
Each of these \(2B+1\) outer products has dual/image pairing one.
Their sum is M, because the two added copies of
\(e_{y_0}e_{y_0}^T\) cancel.

For even B, use the kernel relation
\(m_{y_0}=\sum_{j\ {\rm odd}}m_{x_j}\). Take
\[
 m_{x_j}(e_{x_j}^T+[j\text{ odd}]e_{y_0}^T)
 \quad(0\leq j<B),
\]
and \(m_{y_k}e_{y_k}^T\) for \(1\leq k<B\).
These \(2B-1\) outer products sum to M. Their dual/image pairings are one:
the y0 row of the x-column block is \(e_0^T\), and j=0 is even.
The remaining y-column diagonal entries are all one.

For every listed pair u,v, choose the scalar basis
\(S=[u,\text{ a basis of }\ker v^T]\).
The concrete repair word is, in chronological order, \(S^{-1}\), one
coordinate-bank N call, then S. Concatenating these words in any order
attains the required endpoint, since the epsilon coefficients add.
Extend every S by identity on spectators to attain the same count for
arbitrary dirty spectator inputs.

At B=4 this gives exactly seven formal N calls. If a separately admitted
111-port implementation costs 111 rank-one children per N call, this is
777 rank-one children for these repairs. The theorem supplies neither that
implementation nor its scalar-access and frame costs, and makes no comparison
with a differently normalized planning allowance.

## Evidence and remaining obligations

The checker replays the authenticated recipe independently in dual-number
arithmetic for B=1 through 12, reproduces every field of the historical six
finite cases, verifies every projector and explicit scalar conjugator, and
replays 72 full arbitrary-input binary instantiations. Those instantiations
use B=1 through 8, three nonidentity involutions of widths two or four, and
zero, one or three independently dirty spectator banks. Twelve controls alter
actual words, repairs or hypotheses and require their intended rejection.

The all-B conclusion follows from the preceding written formulas and proof,
not from extending that finite list. There is no formal-kernel proof.
This work does not supply native interfaces, helper ownership, fresh-stage
commutation/frame admission, integer or rounded lifts, scalar-access costs,
complete recursive moments, a physical controller, or a kappa improvement.

The historical B=1,...,6 observation and B4 rank/parity lower screen are
from `bit_nilpotent_recipe.py` at scientific pin
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
The retained upstream recipe credits DreamingOfClouds with Claude Opus
assistance, chafreaky with OpenAI Codex assistance, and the earlier
PR386/436/439 contributors. Their notices must accompany the frozen source.
The all-B closed form, rank proof and attaining decomposition above are this
review's extension. Published rank-one idempotent counts and trace-zero
commutator floors use different targets and are not invoked as proofs here.
