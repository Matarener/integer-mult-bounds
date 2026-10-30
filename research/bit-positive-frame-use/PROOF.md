# Which positive rank-one additions can occur at all?

Proof by **apoursh**, with substantial OpenAI Codex assistance. Apache-2.0.

This proof is self-contained in the established formal register model. It imports no theorem, executable, certificate or pending Git object from PR6079. The determinant method is credited to Nick Petalas's PR2910; the target, model, support and first-order methods retain the PR2085/2112/6032 attribution.

## Statement

Put

$$
 A=\begin{pmatrix}1&0\\0&0\end{pmatrix},\quad
 B=\begin{pmatrix}0&0\\0&1\end{pmatrix},\quad
 P=\frac12\begin{pmatrix}1&1\\1&1\end{pmatrix},\quad
 Q=\frac12\begin{pmatrix}1&-1\\-1&1\end{pmatrix}.
$$

Thus $A+B=P+Q=I_2$, and each of these four addresses has trace one. Fix a **nonzero positive semidefinite symmetric rational matrix $R$ of rank one**. Let $\Lambda=\mathbb ZA+\mathbb ZB+\mathbb ZP+\mathbb ZR$, an additive subgroup of $\operatorname{Sym}_2(\mathbb Q)$. Work in the commutative formal group algebra $K=\mathbb F_2[\Lambda]$, where $[F][G]=[F+G]$. Distinct rational addresses index distinct basis monomials; the exponents are not reduced modulo two or identified through a finite representation.

For every finite $w\ge4$, allow paid calls

$$
 D_N(F)=I_w+([F]-1)N,
 \qquad F\in\{A,B,P,Q,R\},\quad
 N\in M_w(\mathbb F_2),\quad N^2=N,\quad\operatorname{rank}N=1.
$$

Arbitrary address-independent matrices in $\operatorname{GL}_w(\mathbb F_2)$ may be interspersed at zero cost. Require exact equality of the whole register matrix with

$$
 T_w=\operatorname{diag}([A+P],[A+Q],[B+P],[B+Q],1,\ldots,1).
$$

All roles start arbitrary. The extra $w-4$ roles are dirty workspace and must be restored exactly; they need not stay unchanged during the word. Inverse labels, address-dependent free matrices, clean-only initialization, and discarded roles are not included.

Call $R$ **usable** if some such finite exact word contains at least one call labelled $R$. There is no length bound in this definition.

**Theorem.** For every finite $w\ge4$:

1. $R$ is usable if and only if $R=F/m$ for an address $F\in\{A,B,P,Q\}$ and a positive integer $m$.
2. For $R=F/m$, the complete set of attainable total call counts among exact words required to use $R$ is exactly $\{m+7,2m+6\}$. In particular, the minimum is $m+7$. The two counts coincide when $m=1$.
3. Every exact word using $R=F/m$ has one of the three necessary multiplicity profiles below, in order $(F,F^\perp,G,H,R)$, where $F^\perp$ is its mate in the old orthogonal pair and $G,H$ are the other pair:

$$
 (1,2,2,2,m),\qquad
 (0,2,2,2,2m),\qquad
 (0,1,3,3,m).                                             \tag{P}
$$

The first two profiles are attained by explicit subdivision words. The third is only a necessary candidate; its realizability for $m\ge2$ is **not asserted**. Accordingly, (P) is a complete necessary list, not a claimed classification of attainable count profiles.

When $m=1$, $R$ duplicates an old address. One may distinguish the name of the extra label for the required-use statement; the operation and its cost are unchanged. Ignoring $R$ always gives the ordinary eight-call construction. For $m>1$, requiring use of the extra frame strictly raises the optimum.

## 1. Determinants and removal of free mixing

A rank-one binary idempotent has the form $N=xy^T$, with $y^Tx=1$. The matrix determinant lemma over the commutative ring $K$ gives

$$
 \det D_N(F)=1+([F]-1)y^Tx=[F].
$$

Every invertible binary matrix has determinant one. Thus, if $a,b,p,q,r$ count calls at $A,B,P,Q,R$, exact endpoint equality implies

$$
 aA+bB+pP+qQ+rR=4I_2.                                    \tag{1}
$$

This is exact rational-matrix equality, because it follows from equality of formal basis monomials. It is the determinant invariant already used in PR2910, not a new general identity.

For the remaining arguments, move free binary matrices through paid factors by conjugation. Rank-one idempotence and the address label are preserved. The word becomes a product of paid factors followed by one free binary matrix $G$. Under augmentation $[F]\mapsto1$, every paid factor and the target become identity, so $G=I_w$. Consequently the support and first-order arguments may assume only paid factors, without restricting the permitted free mixing.

In particular these arguments retain the full $w$-dimensional projectors. They do not incorrectly replace a projector by its compression to the first four roles.

## 2. At every word length, a usable positive direction must be old

Suppose $r\ge1$. Set

$$
 n=a+b+p+q,\qquad d=a-b,\qquad e=p-q.
$$

Since $\operatorname{tr}R>0$, the trace of (1) gives $n<8$, independently of the total number $n+r$ of calls. Subtracting the old frames entry by entry yields

$$
 2rR=
 \begin{pmatrix}8-n-d&-e\\-e&8-n+d\end{pmatrix}.
$$

The rank-one condition and nonnegative old counts imply

$$
 d^2+e^2=(8-n)^2,\qquad |d|+|e|\le n.                    \tag{2}
$$

Because $8-n>0$,

$$
 8-n=\sqrt{d^2+e^2}\le |d|+|e|\le n,
$$

so $4\le n\le7$. The only possible circle radii are therefore $8-n\in\{1,2,3,4\}$. These four integer circles have only axial integer points. Substitution shows

$$
 rR=(8-n)F\quad\text{for some }F\in\{A,B,P,Q\}.           \tag{3}
$$

Therefore every usable positive frame has the form $R=cF$, $c>0$. This already excludes every positive direction outside the four old directions at every finite word length and workspace width.

The small-circle assertion can be checked by listing squares up to sixteen. It is the entire uniform reduction, not a bounded search in rational slopes or word lengths.

## 3. Exact symmetries reduce to $R=cA$

The rational similarity maps induced by

$$
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
 H=\begin{pmatrix}1&1\\1&-1\end{pmatrix},\quad H^{-1}=H/2,
$$

preserve the four old frames. Conjugation by $J$ swaps $A,B$ and fixes $P,Q$; conjugation by $H$ swaps $A,P$ and swaps $B,Q$. They act transitively on the four addresses. In target order $(A+P,A+Q,B+P,B+Q)$, the induced permutations are respectively $(1\ 3)(2\ 4)$ and $(2\ 3)$, using one-based positions.

Applying either address isomorphism to every formal monomial and then the corresponding active-role permutation takes exact admissible words to exact admissible words, preserving counts and restored dirty roles. This is a proof isomorphism between cases, not a free address-transformation operation being added to the model. We may therefore prove the remaining assertions for $R=cA$, with $c>0$.

## 4. A denominator-independent character leaves three count patterns

Equation (1), now with $R=cA$, gives

$$
 p=q=s,\qquad b=4-s,\qquad a+rc=b.                       \tag{4}
$$

Since $r,c>0$, $0\le a<b$; hence $0\le s\le3$.

Let $\phi(F)$ be twice the off-diagonal matrix entry of $F$. On the generators of $\Lambda$,

$$
 \phi(A)=\phi(B)=\phi(R)=0,\qquad \phi(P)=1,\quad\phi(Q)=-1.
$$

Therefore $\phi$ is integer-valued on $\Lambda$, even when $c$ has arbitrary rational denominators. Reduction modulo two gives an additive character $\chi:\Lambda\to\mathbb F_2$. The assignment

$$
 [F]\longmapsto1+\epsilon\chi(F)
$$

is a ring homomorphism to $\mathbb F_2[\epsilon]/(\epsilon^2)$. The image of the paid word is

$$
 I_w+\epsilon(S_P+S_Q),
$$

where $S_P,S_Q$ sum the corresponding binary call projectors. Every active target frame has character value one and every restored identity exponent has character zero. Thus exact equality forces

$$
 S_P+S_Q=D_w:=\operatorname{diag}(1,1,1,1,0,\ldots,0).
$$

The right side has rank four. The left is a sum of $p+q=2s$ rank-one matrices, so $s\ge2$. Together with (4), this leaves precisely

$$
 (a,b,p,q)=(1,2,2,2),\quad(0,2,2,2),\quad(0,1,3,3).        \tag{5}
$$

No enumeration of binary projectors or workspace widths is used.

For an optional finite check, before this character filter the determinant equations have ten old-count profiles per direction: for $R=cA$, choose $s\in\{0,1,2,3\}$ and $a\in\{0,\ldots,3-s\}$, and put $b=4-s,p=q=s$. Across all four directions there are forty old-count profiles. These forty old profiles are not the same census domain as the forty short-word determinant candidates in PR6079.

## 5. Support forces reciprocal-integer scaling

Each paid factor expands as

$$
 D_N(F)=(I_w-N)+[F]N.
$$

Every exponent appearing in any coefficient of the full product is consequently a subset sum of the paid labels. Matrix cancellation may remove terms but cannot introduce an exponent. Since the first target diagonal entry contains $[A+P]$ with nonzero coefficient, there is a representation of $A+P$ as a nonnegative integer sum of available labels.

In the independent basis $A,B,P$, a symmetric matrix with entries $\begin{pmatrix}x&z\\z&y\end{pmatrix}$ has coordinates $(x-z,y-z,2z)$. If $u_A,u_B,u_P,u_Q,u_R$ are the counts in such a target representation, then

$$
 (u_A+cu_R+u_Q,\;u_B+u_Q,\;u_P-u_Q)=(1,0,1).
$$

All counts are nonnegative and $c>0$. Therefore

$$
 u_B=u_Q=0,\qquad u_P=1,\qquad u_A+cu_R=1.               \tag{6}
$$

If $a=0$ globally, then $u_A=0$; (6) gives $c=1/u_R$, where $u_R$ is a positive integer. If $a>0$, (5) forces $(a,b,p,q)=(1,2,2,2)$, and (4) gives $rc=1$, again $c=1/r$. In every case

$$
 c=1/m\quad\text{for a positive integer }m.
$$

Substituting into (4) and (5) gives exactly the necessary profiles (P): respectively $r=m,2m,m$. Their lengths are $m+7,2m+6,m+7$. Thus every exact word using $R$ has total length in $\{m+7,2m+6\}$, and since $m\ge1$, every such word has at least $m+7$ calls.

For $m=1$, the third profile is impossible. In the canonical case $R=A$, the old-lattice character with values $\chi(A)=\chi(B)=1$ and $\chi(P)=\chi(Q)=0$ sends every target to one. That profile has only one $R$ call and one $B$ call detected by this character, so its first-order coefficient has rank at most two, whereas $D_w$ has rank four. The other directions follow by the exact symmetries. The remaining count-profile question starts at $m=2$.

## 6. Sharp construction, valid at every width

The ordinary eight-call construction uses coordinate-projector label pairs $(A,P),(A,Q),(B,P),(B,Q)$ on the four active roles. All other roles remain identity. For any idempotent $E$,

$$
 D_E(U)D_E(V)=D_E(U+V),
$$

because the complementary summands $E$ and $I-E$ multiply orthogonally. Hence for $R=F/m$,

$$
 D_E(R)^m=D_E(mR)=D_E(F).
$$

Replace one of the two $F$-labelled coordinate calls in the direct construction by $m$ consecutive $R$ calls. The new exact word has $7+m$ calls and uses the extra label. Replacing both such calls realizes profile $(0,2,2,2,2m)$ at length $6+2m$. These words work for every finite $w\ge4$, with all workspace unchanged. Both lengths in the necessary spectrum are therefore attained. This proves usability, the exact spectrum $\{m+7,2m+6\}$, and the required-use minimum. For $m=1$, the distinction between calls named $F$ and calls named $R$ is retained when counting profiles; both constructions use eight operations and the spectrum is the singleton $\{8\}$.

The result does not say that every admissible word is literally a subdivided direct word. It classifies the additional addresses that may occur, proves their exact possible total call counts and optimal required-use cost, and supplies a necessary count-profile list. No realization is asserted for the third profile in (P) when $m\ge2$; $m=1$ was excluded above.

## Scope, boundaries and contribution beyond PR6079

PR6079 excludes words of at most seven calls for one arbitrary signed rational rank-one addition. That minimum-eight result does not decide which positive additions can appear in longer exact words. The present proof answers that all-length question: the only usable positive additions are reciprocal-integer subdivisions of the four original directions, and the exact possible total call counts are $\{m+7,2m+6\}$, with optimum $m+7$. The proof here reconstructs all needed invariants directly from the canonical predecessor model and needs no PR6079 code or result as an input.

The positivity and single-added-frame hypotheses are substantive. The zero frame gives an identity call and is excluded from the classification. A negative frame such as $-A$ can appear by appending an $A,-A$ cancellation pair to the direct word, so the positive classification must not be asserted for signed frames. Two or more positive added frames change the determinant rank-one reduction; no conclusion is made for that model. Clean ancillas, disposal, address-dependent free mixing, finite evaluated representations, changed endpoints, and native/consumer pricing remain outside scope.

This is a scoped formal-model theorem, not a new native supplier, kappa improvement, all-size multiplication theorem, formal-kernel verification or independent human review. Finite checks should corroborate the forty determinant-compatible old-count profiles, exact source/target symmetries, the denominator-independent character, the three symbolic multiplicity families and the attaining subdivision words. A bounded integer-m grid cannot itself prove the all-length or all-workspace statements; those follow from the argument above.

Credit Cinna Davis's PR2085/2112 for the model and endpoint; Nick Petalas's PR2910 for the earlier fixed-frame determinant obstruction and arbitrary dirty-workspace treatment, and PR6032 for its support/first-order approach and open alphabet question; Philippe Van Velzen's earlier fixed-frame exact-eight finding as retained in PR2910; and the retained BIT predecessor lineage. The standard determinant, support expansion and character/rank arguments are inherited techniques. The new conclusion is the all-length positive-frame classification, exact total-length spectrum and sharp required-use tariff.
