# Observed coupled bills and a sharp divergence window

Let A be an n by n nonnegative rational matrix and let b,c be nonnegative
rational column vectors. Define

\[
 a_k=c^T A^k b,\qquad S_N=\sum_{k=0}^{N-1}a_k,\qquad S_0=0.
\]

The graph convention is j -> i when A_ij>0. A path of length zero is allowed.
Let H be the intersection of the vertices reachable from supp(b) and the
vertices that can reach supp(c). Put r=|H|, B=A[H,H], beta=b[H], gamma=c[H].
All statements below concern this declared nonnegative linear model. They
do not establish that a proposed matrix bounds any actual supplier.

## Theorem

If H is empty, every a_k is zero. Otherwise exactly one of the following holds.

1. There are positive rational p and rational 0<=q<1 with Bp<=qp. The bill is
   finite. Its exact value is gamma^T u, where u is the unique solution of
   u=Bu+beta. Moreover, for every integer K>=0,

   \[
   \sum_{k=K}^{\infty}a_k=\gamma^T B^K u
   \le \alpha q^K\gamma^T p,
   \qquad \alpha=\max_i u_i/p_i.
   \]

2. There is a nonzero rational v>=0 with Bv>=v and gamma^T v>0. Define

   \[
   z=\sum_{t=0}^{r-1}B^t\beta,\qquad
   \delta=\min_{i:v_i>0}z_i/v_i,\qquad h=\delta\gamma^T v.
   \]

   Then z>0, delta>0, h>0, and for every integer N>=0,

   \[
   \boxed{S_N\ge\lfloor N/r\rfloor h.}
   \]

Both alternatives have rational certificates checked by graph closure and
matrix-vector arithmetic. No eigenvalue approximation is needed. The window
r in the second alternative is the smallest universal dimension-only window
for a positive bound of this form without an additive delay. In fact the
stated bound can be an equality for every N.

## Path reduction

Expand c^T A^k b as the sum of the weights of all length-k paths from a vertex
with b_j>0 to a vertex with c_i>0. The weight includes both endpoint weights.
Every vertex on every contributing path is in H. Conversely, restricting to
H removes no contributing path. Thus

\[
a_k=\gamma^T B^k\beta\quad\hbox{for every }k\ge0.
\]

For every vertex in H there is an input-to-vertex path entirely in H and a
vertex-to-output path entirely in H. Choose simple paths, each of length at
most r-1. Therefore z>0. The analogous row vector

\[
w^T=\sum_{t=0}^{r-1}\gamma^T B^t
\]

is strictly positive as well. These assertions concern all vertices in H,
including ones with beta_i=0 or gamma_i=0.

## The classical alternative used here

For completeness, the following argument states the classical nonsingular
M-matrix alternative used by Ali Romman's #5785. Its mathematical priority
is not claimed here.

Set M=I-B. Its off-diagonal entries are nonpositive. Eliminate columns in
order, without row swaps, as long as the diagonal pivot is positive.
Every remaining Schur complement has nonpositive off-diagonal entries.

If all pivots are positive, forward and backward substitution on Mp=1
give p>0. Substitution preserves nonnegativity because the relevant
off-diagonal entries are nonpositive. Thus Bp=p-1<p. In particular
q=max_i (Bp)_i/p_i is rational and belongs to [0,1). The same substitutions
give u>=0 from Mu=beta.

If the first nonpositive pivot is at k, set v_k=1 and v_i=0 for i>k, then
back-substitute the first k homogeneous equations. All v_i are nonnegative.
The first k rows of Mv are zero. The remaining rows of Mv are nonpositive.
To see the latter in the original rows, every earlier elimination step only
added a multiple of a row whose value on v is zero. In the reduced rows,
row k has its nonpositive pivot and every later row has a nonpositive
coefficient in column k. Hence Mv<=0, so Bv>=v.

The alternatives are exclusive. If p>0 and Bp<p while v>=0 is nonzero and
Bv>=v, take t=max_i v_i/p_i>0. At an index attaining the maximum,
(Bv)_i<=t(Bp)_i<t p_i=v_i, a contradiction.

The small-matrix verification uses a separate principal-minor criterion.
All principal minors of I-B are positive exactly in the positive alternative.
In one direction, positive leading minors give positive Gaussian pivots.
In the other, any principal submatrix inherits strict contraction weights
by restriction. Its negative alternative is impossible by the same maximum
ratio argument, so all its pivots and its determinant are positive. Computing
these minors by permutation expansion is independent of the producer's
elimination implementation. Cramer's rule then independently computes each
finite observed total.

## Finite bill and exact tail

The weighted maximum norm with weights p contracts under B by q<1.
Consequently sum B^k beta converges and equals the unique solution u of
u=Bu+beta. The identity for the tail follows by factoring out B^K.
Since 0<=u<=alpha p, monotonicity gives
B^K u<=alpha B^K p<=alpha q^K p, proving the tail bound.

This proof also covers q=0, using q^0=1.

## Observable divergence certificate

Suppose the classical alternative gives v>=0, v!=0 and Bv>=v, possibly
with gamma^T v=0. The sequence B^j v is coordinatewise nondecreasing.
Since w>0 and v is nonzero, gamma^T B^s v>0 for some 0<=s<=r-1.
Replace v by B^(r-1)v. This preserves nonnegativity and Bv>=v, and makes
gamma^T v>0. All entries remain rational.

Because z>0, the defined delta is positive and z>=delta v. For each integer
m>=0,

\[
\begin{aligned}
\sum_{t=0}^{r-1}a_{mr+t}
 &=\gamma^T B^{mr}z\\
 &\ge\delta\gamma^T B^{mr}v\\
 &\ge\delta\gamma^T v=h.
\end{aligned}
\]

There are floor(N/r) disjoint complete windows in the first N terms.
All remaining terms are nonnegative. Summing gives the stated lower bound,
and therefore divergence. This proves necessity of the positive alternative
for finiteness as well as sufficiency.

## Sharpness

For every r>=1 take the directed r-cycle, with unit edge weights. In matrix
notation B e_j=e_((j+1) mod r). Set beta=e_0 and gamma=e_(r-1). Then

\[
a_k=1\ \Longleftrightarrow\ k\equiv r-1\pmod r,
\qquad S_N=\lfloor N/r\rfloor.
\]

The certificate v=1 has z=1, delta=1 and h=1. The lower bound is an equality
at every N. For any integer window L<r, S_L=0, so no bound
S_N>=floor(N/L)h' with h'>0 can hold for this example at every N.

## What the extension changes

The #5785 whole-matrix alternative certifies or excludes a global strict
contraction. It explicitly warns that zero or unreachable forcing can miss
a bad component. Here the exact object being decided is the specified
scalar input/output bill. The path intersection is sufficient and necessary;
an unstable component outside it may be both forced and harmless to that
particular output. The new quantitative witness converts an applicable
noncontraction alternative into an observable divergent bill, with a sharp
universal depth window.

Classical nonnegative matrix, path expansion and M-matrix theory underlie
the proof. The contribution is this explicit output-specific contract and
its finite-depth certificate in the repository's budget setting. It is not
a claim of new general Perron-Frobenius theory.

If A is only a componentwise upper bound for actual costs, the finite
alternative supplies a sufficient upper bound. The divergent alternative
does not disprove the actual caller in that case. A negative conclusion
needs an exact recurrence or a justified componentwise lower bound, together
with compatible forcing and observed-cost inequalities. An omitted real
adapter or restoration cost cannot be assigned c_i=0 merely to pass this test.
