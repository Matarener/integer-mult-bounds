# Deleting one lower-only phase

This contribution was produced by Nick Petalas. Apache-2.0.

## Exact model and statement

Fix a field k, a positive width m and a finite number R of scalar registers.
Write

\[
 u_A=\begin{pmatrix}I&A\\0&I\end{pmatrix},\qquad
 v_K=\begin{pmatrix}I&0\\K&I\end{pmatrix},\qquad
 U=\{u_A:A\in M_m(k)\},\quad V=\{v_K:K\in M_m(k)\}.
\]

Let C be any commutative coefficient ring. The application here is k=Q and
C=F2, with rational or dyadic address matrices and free binary register
mixing. Brackets denote *formal group-algebra labels*, not evaluation of
an address matrix in characteristic two.

Consider a state matrix

\[
 X=LFB,\qquad L,B\in M_R(C[U]),\qquad F\in M_R(C[V]).
\]

Let epsilon:C[V]->C be augmentation, sending every [v_K] to 1.
For any chosen set of matrix entries J, assume X_ij belongs to C[U] for
every (i,j) in J. Then

\[
 \boxed{X_{ij}=(L\,\epsilon(F)\,B)_{ij}\quad((i,j)\in J).}
\]

Thus the lower-only phase can be replaced by its scalar augmentation
without changing any required upper-supported entry. No condition is
imposed on other entries. With clean auxiliaries initially zero, J can be
just the data-to-data block and auxiliary outputs can be garbage. With
arbitrary dirty auxiliaries, J must also include each required data-from-
auxiliary zero entry. Any required restoration entries must likewise be
included. If every entry is upper-supported, the entire formal endpoint
is unchanged.

For a circuit, L and B consist of upper-shear paid calls and scalar mixing.
F consists of any finite sequence of lower-left updates on individual
registers and scalar mixing, with no intervening upper call. Its
augmentation is precisely the product of the scalar mixing matrices in
that phase. Every lower update augments to identity. If those mixing
matrices are invertible, their product is an allowed free mixing map.
Deleting the lower updates preserves every paid call and its rational rank.

This is a scoped reduction. Internal register-dependent Levi maps,
additional alternating lower phases and endpoints with non-upper labels
are not covered. General full-Borel words remain open.

## The label lemma

Direct multiplication over k gives

\[
 u_Av_Ku_D=
 \begin{pmatrix}
 I+AK&A+D+AKD\\K&I+KD
 \end{pmatrix}.                                      \tag{1}
\]

Suppose u_A v_K u_D = u_(A') v_(K') u_(D'). The lower-left
block gives K=K'. The two diagonal blocks give AK=A'K and KD=KD'.
Consequently

\[
 AKD=A'KD=A'KD',
\]

and comparison of the upper-right blocks gives A+D=A'+D'.
No inverse of K, integrality condition or rank assumption was used.
This includes K=0, when the label is simply u_(A+D).

Therefore the following map on the *set of distinct group labels* is
well-defined:

\[
 f:UVU\longrightarrow U,\qquad f(u_Av_Ku_D)=u_{A+D}.   \tag{2}
\]

It is identity on U. For all E,H it satisfies

\[
 f(u_E g u_H)=u_E f(g)u_H.                            \tag{3}
\]

Indeed prefixing and suffixing just replace A,D by E+A,D+H.
The additive identity u_E u_A=u_(E+A) proves (3).

Extend f C-linearly to the free C-module spanned by UVU, calling the map
P. Equal labels have equal images by the lemma, so cancellations in the
formal group algebra are respected. Equation (3) makes P a C[U]-bimodule
map, and P fixes C[U]. It is not asserted to be a ring homomorphism or to
extend to the entire group algebra.

## Circuit reduction

Every entry of LFB lies in the span of UVU. Expand its finite sums and
apply (2) term by term. For upper labels a,b and a lower label v,

\[
 P([a][v][b])=[a][b].
\]

Linearity and matrix multiplication therefore give

\[
 P(LFB)=L\,\epsilon(F)\,B.                           \tag{4}
\]

At each required entry, the upper-support assumption gives P(X_ij)=X_ij.
Equation (4) proves the statement. This works over every C, in particular
the binary superposition algebra, without reducing rational addresses
modulo two. Arbitrarily many registers do not change the argument.

A contiguous phase in an ordinary left-multiplication circuit has the
required factorization. The analogous right-multiplication circuit also
does. If a model allows both left and right moves, the assertion requires
the displayed *final factorization*, not just contiguity in wall-clock
order. A phase acting on both sides of an existing upper word can leave
two lower factors separated by that word. No reduction for that broader
bidirectional case is asserted.

## What changes for the source question

Sagar Thakrar's [PR2613](https://github.com/CrocSwap/integer-mult-bounds/pull/2613)
asks whether inserting D+=K H can escape the upper-shear superposition
obstruction, beginning with one such update. The theorem above removes
*every* contiguous lower-only phase under the explicit upper-supported
endpoint and alphabet conditions. It covers singular K and even
denominators, which a mod-two natural-representation argument cannot
automatically cover.

Any obstruction already established for the remaining upper-only word
therefore transfers without changing its paid profile. The existing
width-two abelian floor, when its full target hypotheses are supplied, is
a predecessor premise from eumemic's PR288 as cited by PR2613. No new
derivation or replay of that floor is claimed here. In particular, this
package's new theorem is not a new census of three-call words or a claim
about every full-Borel word. dcharb78's PR3183 separately reports a finite
width-two block-Borel screen; it is not used in this proof.

## Why the hypotheses matter

If a required entry may retain a lower label, deletion need not preserve
it: the one-register word v_1 differs from identity.

Allowing an additional internal Levi factor also breaks naive deletion.
In one dimension let d=diag(2,1). Then

\[
 u_1\,d\,u_{-1/2}\,d^{-1}=I,
\]

but deleting d and d^-1 leaves u_(1/2). This is a control on enlarging the
middle alphabet, not a counterexample to the lower-unipotent theorem.

Nor may one apply P as an unrestricted multiplicative map across many
alternating lower phases. In one address dimension,

\[
 u_1v_1u_1v_{-1/3}u_{-3}v_{-1/3}=I,                 \tag{5}
\]

whereas deleting the three separated lower factors leaves u_-1.
Equation (5) follows by direct 2-by-2 multiplication. It supplies no
profitable paid word and no physical construction; it rejects a false
unrestricted deletion rule.

## Evidence boundary

The universal result is the algebraic proof above. The standalone verifier
checks literal matrix products, complete small finite-field collision
classes, singular rational fixtures, and full formal superposition words.
It imports no predecessor executable and supplies no finite-to-universal
inference. Physical legality, native realization, chronological compiler,
restoration outside the declared endpoint, precision/tape/stock and the
complete signed invoice remain separate. No new kappa is claimed.
