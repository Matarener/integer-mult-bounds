# Exact diagonal minimum for F2-valued right vectors

Let \(R\) be any algebra over \(\mathbb F_2\), not necessarily commutative, finite, or local. Fix a register count \(n\ge 0\). A paid factor is a matrix
\[
F=I+uy^T,\qquad u\in R^n,\quad y\in\mathbb F_2^n.
\]
No other operation is free. There is no idempotence hypothesis on \(uy^T\) and no restriction that \(u\) be a scalar times a binary vector. Write \(t(d)\) for the number of coordinates of a tuple \(d\in R^n\) with \(d_i\ne 1\).

**Column expansion.** Let \(P\) be a product of \(L\) paid factors, multiplied on the right, and write \(P_0=I\) and \(P_j=P_{j-1}(I+u_j y_j^T)\). Then
\[
P-I=\sum_{j=1}^L c_j y_j^T,\qquad c_j=P_{j-1}u_j\in R^n.
\]
Each right vector \(y_j\) has coordinates in \(\mathbb F_2\). Evaluating on the standard basis of \(\mathbb F_2^n\) therefore gives
\[
(P-I)e_i=\sum_{j=1}^L (y_j)_i\, c_j,
\]
an \(\mathbb F_2\)-linear combination of the \(L\) columns \(c_j\). The image of this map \(\mathbb F_2^n\to R^n\) has dimension at most \(L\).

**Diagonal count.** If \(P=\operatorname{diag}(d_1,\ldots,d_n)\), then \((P-I)e_i=(d_i-1)e_i\). Suppose \(\sum_i \varepsilon_i(d_i-1)e_i=0\) with \(\varepsilon_i\in\mathbb F_2\). The \(i\)th coordinate of that vector is \(\varepsilon_i(d_i-1)\), so \(\varepsilon_i=0\) whenever \(d_i\ne 1\). The \(t(d)\) vectors \((d_i-1)e_i\) are linearly independent over \(\mathbb F_2\). Hence \(t(d)\le L\).

**Matching construction.** For each \(i\) with \(d_i\ne 1\), the factor \(I+(d_i-1)e_ie_i^T\) is paid: its right vector is the binary standard basis vector \(e_i\). Increments supported on distinct matrix units multiply to zero, so these \(t(d)\) factors, in any order, equal \(\operatorname{diag}(d)\). The empty product is \(I\). The exact minimum is therefore \(t(d)\), for every finite \(n\) and every tuple in \(R^n\).

**Group-label corollary.** Let \(G\) be any finite group and let \(R=\mathbb F_2[G]\). Restrict the paid alphabet to factors \(I+(g-1)xy^T\) with \(g\in G\setminus\{1\}\) and binary \(x,y\) satisfying \(y^Tx=1\). This is a subset of the alphabet above, so the lower bound \(L\ge t\) remains. For a target \(\operatorname{diag}(h_1,\ldots,h_n)\) with \(h_i\in G\), each non-identity entry is attained by the legal coordinate factor \(I+(h_i-1)e_ie_i^T\). Identity coordinates are restored dirty roles and contribute nothing to \(t\). The exact paid-call minimum is the number of non-identity diagonal entries. Commutativity is not used. Elements of \(1+\mathfrak m^2\) are included: the vectors \((h_i-1)e_i\) stay independent in \(R^n\) whenever \(h_i\ne 1\), even if \(h_i-1\) lies in a higher power of the augmentation ideal.

**Why the chain-ring theorem does not imply this.** The product theorem in `research/bit-cyclic-root-barrier/PROOF.md` allows both \(u_j\) and \(v_j\) to have entries in \(R=\mathbb F_2[z]/(z^q)\), and it uses that principal ideals in a chain ring have one-dimensional socles. That hypothesis is false for a general \(\mathbb F_2\)-algebra. The same note records that the column lemma is not asserted for arbitrary group algebras, and that in \(\mathbb F_2[x,y]/(x^2,y^2)\) the one-column matrix \((x,y)^T\) has two-dimensional socle. The argument above never uses socles. It uses that the right vectors are \(\mathbb F_2\)-valued, which the chain-ring product theorem does not assume.

**Sharpness of the right-vector hypothesis.** Over \(R=\mathbb F_2[z_1,z_2]/(z_1^2,z_2^2)\), the single outer product
\[
\begin{pmatrix}z_1\\ z_2\end{pmatrix}
\begin{pmatrix}z_2& z_1\end{pmatrix}
=
\operatorname{diag}(z_1z_2,z_1z_2)
\]
has zero off-diagonal entries because \(z_1^2=z_2^2=0\). The matrix \(I\) plus this product is \(\operatorname{diag}(1+z_1z_2,1+z_1z_2)\). Both diagonal entries differ from \(1\), so \(t=2\), but only one factor was used, and its right vector \((z_2,z_1)\) is not \(\mathbb F_2\)-valued. Thus the exact count does not survive if right vectors may have entries in \(R\). This witness is an algebra diagonal, not a recomputation of a cyclic root-lift census.

**What is not claimed.** Free changes of basis in \(\mathrm{GL}_n(\mathbb F_2)\) are not part of the alphabet. The bound does not price native frames, hosting, or precision, and it does not change the selected multiplication exponent. A specialization to a torsion-free rational frame algebra is a different model; the one-relation lemma in `research/bit-one-relation-any-registers/PROOF.md` concerns that formal algebra and explicitly declines finite torsion specializations as evidence for its premise.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
