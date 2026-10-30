# Full retained boxes for rational Gram factorizations

Copyright 2026 Sagar Thakrar. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

This proves a sufficient case of the retained three-total rational anchor-box
problem. It uses the existing directed, ordered sub-anchor definition, not an
unordered orthogonal-label condition. The argument is elementary and written;
it is not a proof-assistant certificate or a theorem about a complete
multiplication algorithm.

## 1. Canonical factors and the box definition

Let $P,Q\in\mathbb Q^{n\times3}$, $n\ge1$, and $M=PQ^T$, with
$M_{ii}\ne0$ for every $i$. Write $\nu$ for the 2-adic valuation, with
$\nu(0)=+\infty$. A product column for which either entire factor column
is zero contributes nothing to $M$. Delete that column before taking its
valuation minima; in all binary labels below restore it as a zero coordinate.
This avoids assigning a finite minimum to an identically zero column.

For each remaining column put

\[
 m_j=\min_i\nu(P_{ij}),\qquad n_j=\min_i\nu(Q_{ij}),\qquad
 \gamma=\min_j(m_j+n_j),
\]
\[
 p_{ij}=2^{-m_j}P_{ij},\qquad
 q_{ij}=2^{m_j-\gamma}Q_{ij}.
\]

Every entry of $p,q$ lies in $\mathbb Z_{(2)}$, the rational numbers with
odd denominator, and $pq^T=2^{-\gamma}M$. Let $A_i,B_i$ be the supports
of $p_i,q_i$ modulo two, let $T_i=A_i\cap B_i$, and let
$\tau_i=|T_i|$. These are the original canonical anchors for the complete
instance. No subset chosen later is renormalized.

A box witness consists of a kept subset $K$, an order on $K$, and binary
labels $a_i\subseteq A_i$, $b_i\subseteq B_i$ such that
$a_i\cdot b_i=1$ over $\mathbb F_2$ for every $i\in K$. Its only
off-diagonal conditions are

\[
 i\text{ before }j,\quad M_{ij}=0
 \quad\Longrightarrow\quad a_i\cdot b_j=0.
\]

The maximum size of such a set is the retained $\operatorname{box}$
quantity for this factorization and its anchors. In particular a full
witness proves $\operatorname{box}=n$, since there are only $n$ rows.

Reduction modulo two gives the inherited scalar-to-anchor implication

\[
 M_{ij}=0\quad\Longrightarrow\quad A_i\cdot B_j=0.
 \tag{SG}
\]

For an element of $\mathbb Z_{(2)}$, reduction modulo four means reducing
its numerator and multiplying by the inverse of its odd denominator. All
congruences below therefore include negative entries and rational entries
with odd denominators; they are not restricted to nonnegative integers.

## 2. A modulo-four coloring lemma

Suppose $u_i,v_i\in\mathbb Z_{(2)}^3$ have the same two-coordinate
odd support $S_i=\{s_i,t_i\}$, and
$\nu(u_i\cdot v_i)=1$. Define

\[
 \chi_i=u_{i,s_i}u_{i,t_i}\pmod4\in\{1,-1\}.
\]

The product at the unsupported coordinate is zero modulo four. The two
supported products $x=u_{i,s_i}v_{i,s_i}$ and
$y=u_{i,t_i}v_{i,t_i}$ are odd, and $x+y\equiv2\pmod4$.
Thus $x\equiv y\pmod4$ and $xy\equiv1\pmod4$. Consequently

\[
 u_{i,s_i}u_{i,t_i}\equiv v_{i,s_i}v_{i,t_i}\pmod4.
 \tag{1}
\]

If $S_i\ne S_j$, the two supports intersect in exactly one coordinate.
Hence $u_i\cdot v_j$ is odd and cannot be zero. This is where the
three-coordinate domain is used.

If $S_i=S_j=\{s,t\}$ and $u_i\cdot v_j=0$, the unsupported product
again vanishes modulo four. The two odd supported products now sum to zero,
so their product is $-1$ modulo four. By (1),

\[
 -1\equiv(u_{i,s}u_{i,t})(v_{j,s}v_{j,t})
       =\chi_i\chi_j\pmod4.
\]

Every directed zero therefore joins opposite colors with the same support.
In particular, both color classes have no zero entry between distinct rows
in either direction. This conclusion concerns actual rational zeros; it
does not replace them by every even entry.

Changing the sign of an entire factor row multiplies its color product by
$(-1)^2=1$. There is no hidden positivity or row-sign assumption.

## 3. Two nonzero blocks with all odd-tied rows in the middle

The following retained labeling construction makes the graph implication
explicit. Suppose disjoint sets $F,L$ have no forward zero entries in their
chosen internal orders, and every row of $F\cup L$ has a nonempty tied set.
Let $O$ be any additional set of rows with odd $\tau_i$. For each
$i\in F\cup L$, choose $c_i\in T_i$. Use

\[
 (a_i,b_i)=
 \begin{cases}
 (A_i,e_{c_i}),&i\in F,\\
 (A_i,B_i),&i\in O,\\
 (e_{c_i},B_i),&i\in L.
 \end{cases}
\]

Order $F$ first, then $O$, then $L$; the middle order is arbitrary.
Every label is a sub-anchor. A diagonal dot is one for $F,L$ because
$c_i\in T_i$, and for $O$ because $\tau_i$ is odd.

Every forward-zero condition is covered:

* Within $F$ or within $L$, there is no forward zero to check.
* Within $O$, the dot is $A_i\cdot B_j$ and (SG) applies.
* Across $F\to O$, $F\to L$, or $O\to L$, the dot is again
  $A_i\cdot B_j$ and (SG) applies.

There is no constraint from a later block to an earlier one. Empty blocks
cause no difficulty. This construction retains all of $F\cup O\cup L$.
It does not require the rows in a block to share one tied coordinate.

## 4. Sufficient rows in a general rational factorization

For the canonical factors in section 1 define

\[
 O=\{i:\tau_i\text{ is odd}\},
 \qquad
 E=\{i:A_i=B_i,\ |A_i|=2,\ \nu(M_{ii})=\gamma+1\}.
\]

For $i\in E$ the last condition is exactly
$\nu(p_i\cdot q_i)=1$. Apply the modulo-four lemma to $u_i=p_i$,
$v_i=q_i$ on these rows. Let $F,L$ be its two color classes. They have
no internal zero entries in either direction, so any internal orders work.
Section 3 gives

\[
 \operatorname{box}\ge |O|+|E|.
 \tag{2}
\]

In particular, if every row is odd-tied or lies in $E$, the box is full.
All anchors, valuations and labels in (2) are retained from the complete
original instance. The condition is on the normalized diagonal: raw
$\nu(M_{ii})=1$ alone is not the same condition when $\gamma\ne0$.

## 5. Main theorem: arbitrary rational Gram factorizations

**Theorem.** Let $P\in\mathbb Q^{n\times3}$ and $M=PP^T$. If every
canonical tied set is nonempty, then $\operatorname{box}=n$ for this
factorization and its original canonical anchors.

Only columns that are identically zero are inactive in this case. For the
active columns write $m=\min_j m_j$ and $d_j=m_j-m\ge0$. Since $P=Q$,
$n_j=m_j$ and $\gamma=2m$. Put $R=2^{-m}P$. Every entry of $R$ lies in
$\mathbb Z_{(2)}$, and

\[
 p_{ij}=2^{-d_j}R_{ij},\qquad q_{ij}=2^{d_j}R_{ij}.
\]

If $d_j>0$, every entry in column $j$ of $R$ is even, and every entry in
column $j$ of $q$ is even. If $d_j=0$, both normalized columns equal the
corresponding column of $R$. Therefore

\[
 B_i=\operatorname{supp}(R_i\bmod2)\subseteq A_i,
 \qquad T_i=B_i.
 \tag{3}
\]

The hypothesis makes every row of $R$ primitive: it has at least one odd
coordinate. Odd $\tau_i$ rows belong to the middle block $O$. Every other
row has exactly two odd coordinates. For such a row, odd rational squares
are one modulo four and the even square is zero, so

\[
 R_i\cdot R_i\equiv2\pmod4.
\]

Apply section 2 to these even-tied rows with $u_i=v_i=R_i$. Their two color
classes have no internal zero of $RR^T=2^{-2m}M$. They therefore have no
internal zero of $M$. These supports are the tied sets in (3), although
the original canonical anchors $A_i,B_i$ need not be equal.

Now use section 3 with the **original** $A_i,B_i$, not newly normalized
anchors for the even subset. Every row is in $F$, $O$ or $L$, so the
result is a full witness. This proves the theorem.

The statement is about a rational Gram factorization $P=Q$, not merely a
symmetric matrix $M$. It does not claim that every rational positive
semidefinite rank-three matrix has a rational factorization of this form.

Indeed, Aaron Wang's retained PR2978 three-row core has
$P=((-1,-3,0),(1,-1,-2),(3,3,3))$ and
$Q=((1,-3,2),(3,-1,-2),(3,-1,2))$. Its matrix is the symmetric positive
definite $\operatorname{diag}(8,8,12)$, but its supplied factors have
$A=(3,3,7)$, $B=(3,3,3)$ and box two, as retained in PR3393. All target
labels lie in a common two-coordinate space, so retaining the three
mutually zero rows would again require an impossible rank-three triangular
pairing matrix. Two rows can be retained with different unit labels.
Thus even positive definiteness of $M$ cannot replace the hypothesis on
the supplied rational factors and their canonical anchors.

## 6. Boundary examples and necessity controls

### Equal raw factors need not have equal canonical anchors

Take

\[
 P=Q=\begin{pmatrix}1&1&2\\1&-1&0\end{pmatrix}.
\]

The column minima are $(0,0,1)$ and $\gamma=0$. Thus

\[
 p=\begin{pmatrix}1&1&1\\1&-1&0\end{pmatrix},\qquad
 q=\begin{pmatrix}1&1&4\\1&-1&0\end{pmatrix}.
\]

Using coordinate masks $1,2,4$, the anchors are $A=(7,3)$ and $B=(3,3)$.
The matrix is $\operatorname{diag}(6,2)$. The rows have opposite colors,
and the theorem retains both. This is why the Gram proof uses the common
global scaling $R$ and then the original anchors, rather than asserting
that canonical normalization preserves equality of the two factors.

### Matched anchors alone do not imply a full box

For $t=0,1,2$ put $P(t)=(1,1+4t^2,2t)$. If $\{a,b\}$ are the other
two elements of $\{0,1,2\}$, pair this row with
$Q(a,b)=(1-4ab,-1,2(a+b))$. Then

\[
 P(t)\cdot Q(a,b)=-4(t-a)(t-b).
\]

Append a fourth row $(1,0,1)$ to both factors. Explicitly,

\[
 P=\begin{pmatrix}1&1&0\\1&5&2\\1&17&4\\1&0&1\end{pmatrix},
 \qquad
 Q=\begin{pmatrix}-7&-1&6\\1&-1&4\\1&-1&2\\1&0&1\end{pmatrix}.
\]

All column minima and $\gamma$ are zero, and
$A=B=(3,3,3,5)$. The appended row is important: it makes the third column
minimum zero in both factors. The actual matrix is

\[
 M=\begin{pmatrix}
 -8&0&0&1\\0&4&0&3\\0&0&-8&5\\-1&5&3&2
 \end{pmatrix}.
\]

It has rank three. Its first three diagonal valuations are $3,2,3$, so
those rows violate the valuation-one condition in section 4.

No full witness exists. If all four rows were retained, restrict its order
and labels to the first three. Every off-diagonal entry of that principal
matrix is zero, so the ordered binary pairing matrix is triangular with
unit diagonal and has rank three. But all source and target labels of these
three rows lie in the same two-coordinate space, giving rank at most two.
This contradiction is independent of the fourth row's placement.

Rows $0,1,3$ are retained by unit labels $1,2,1$ in that order: their only
same-label cross entries are nonzero. Hence the box is exactly three.
This is an asymmetric-factor necessity example, not a counterexample to
the Gram theorem.

### Nonempty canonical ties are essential even for Gram factors

Take $P=Q$ with rows $(1,0,0)$ and $(2,0,0)$. Then $\gamma=0$ and
$A=B=(1,0)$. The second row has a nonzero diagonal but no available
nonzero sub-anchor label. The box is one, not two. Scaling a single row can
therefore remove its canonical tie; nonzero Gram diagonal alone is not the
theorem's hypothesis.

## 7. Attribution and scope

The canonical root-unit/anchor-decoder framework, valuation scope and directed
box engine are retained from Aaron Wang/navinor's PR2869, PR2914 and PR3031,
with the broader F-star and certificate lineage of DreamingOfClouds through
PR1590 and PR2111. The asymmetric two-block transfer is the existing
PR3409/PR3420 construction; the insertion of odd-tied rows is already used
in PR3445. PR3454 retains the Yu--Oh thirteen-ray Gram example and its full
box witness, crediting Sixia Yu and C. H. Oh for that known construction.
The present statement generalizes that type of full-box conclusion to the
specified arbitrary-size rational Gram class. It does not claim a new
general routing or tensor identity, a new known ray construction, or first
use of a modulo-four parity argument.

Finite residue checks, rational fixtures and definition-level witness replay
support this written proof. They do not constitute independent human
acceptance, a formal kernel proof, an unrestricted asymmetric F-star result,
native supplier admission, or a new multiplication exponent. No selected
frontier is changed.
