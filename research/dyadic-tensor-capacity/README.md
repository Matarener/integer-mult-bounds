# Product cuts retain their full dyadic channel module under tensoring

A pure product of saturated dyadic helper cuts has exactly the tensor product
of their eligible prefix and suffix modules. This includes arbitrary linear
combinations across tensor coordinates: it is not a simple-tensor restriction.
Consequently, tensoring cannot recover hidden channels beyond the primewise
capacity already proved in [Nick Petalas](https://github.com/petalas)'s
[PR #5882](https://github.com/CrocSwap/integer-mult-bounds/pull/5882).

A second consequence concerns a fixed finite catalogue: if each of its cuts
loses a positive fraction of rational channels at some odd prime, **every
arbitrarily mixed long product retains at most an exponentially vanishing
fraction of its rational channel count**. Complementary primes can still improve finite tensor
capacity, exactly as #5882 shows. Changing the cut/support or catalogue is a
real reopening condition; repeating the same defective catalogue is not.

This is a scoped module theorem with source-relative causal examples. It does
not construct selected P104 physical tensor carriers or a new supplier or κ.
The numerical tensor-capacity formula and its sharp bounds are predecessor
results, not new claims here.

## 1. Full eligible-module theorem

Let $D=\mathbb{Z}[1/2]$, with fraction field $\mathbb{Q}$. For each factor $i$, take a finite free ambient module $V_i$, an invertible dyadic prefix $A_i$, and coordinate summands $F_i$ (the cut) and $G_i$ (allowed helper input support). In row convention, define

$$
L_i = F_i \cap \bigl(G_i A_i^{-1}\bigr).
$$

For the pure tensor prefix, cut and allowed support, write

$$
A=\bigotimes_i A_i,
\qquad F=\bigotimes_i F_i,
\qquad G=\bigotimes_i G_i.
$$

Let $L$ consist of all vectors $v$ in $F$ satisfying $vA\in G$. Then the **entire** eligible row module is

$$
\boxed{\displaystyle
L=\bigotimes_i L_i.
}
\tag{1}
$$

The column version gives the same identity for suffix-eligible modules $R_i$. With full module bases $L_{0,i}$ and $R_{0,i}$, their full tensor bases therefore pair by

$$
K=\bigotimes_i\bigl(L_{0,i}R_{0,i}\bigr).
$$

No additional eligible vector is omitted by using those bases. Basis changes are algebraic coordinates, with no free physical implementation or channel credit inferred.

**Proof.** A submodule is saturated when $dv$ belonging to it, for nonzero $d\in D$, implies that $v$ belongs to it. Coordinate summands are saturated, as are their images under an invertible dyadic map. Intersections of saturated submodules are saturated. Since $D$ is a PID, a saturated submodule of a finite free module is a direct summand: its finitely generated torsion-free quotient is free, and a basis of the quotient lifts to a splitting. Thus every $L_i$ is a direct summand.

Over $\mathbb{Q}$, for any subspaces $U_i,W_i\subseteq V_i$,

$$
\left(\bigotimes_i U_i\right)\cap
\left(\bigotimes_i W_i\right)
=\bigotimes_i(U_i\cap W_i).
$$

To see this, in each factor choose a basis of $U_i\cap W_i$, extend it separately to $U_i$ and $W_i$, and then to the ambient space. The tensor basis vectors common to both tensor subspaces use an intersection vector in every factor. This proves the identity for arbitrary, including nondecomposable, vectors. Rationalization commutes with these intersections: clearing finitely many denominators proves the reverse inclusion.

The two sides of (1) have this same rational span. The left side is saturated as an intersection of direct summands. The right side is a direct summand by tensoring splittings of the $L_i$, so is saturated too. A saturated submodule $H\subseteq V$ of a free $D$-module satisfies

$$
H=(\mathbb{Q}H)\cap V.
$$

Clear a denominator and apply saturation. Hence the two sides are equal over $D$. The column argument is identical. Multiplication of tensor row/column bases gives the pairing identity. ∎

Invertibility here is **over $D$**, not merely over $\mathbb{Q}$. The supports $F$ and $G$ are the exact product supports. A larger cut, cross-factor support not of this form, live owned fields, or a prefix not factoring as $A$ changes the hypotheses. Equation (1) alone does not prove timing, common physical charts or native realization.

## 2. Fixed finite catalogues cannot tensor away their losses

Use [Ali Romman](https://github.com/aliromman)'s [PR #5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615) single-cut criterion and [PR #5882](https://github.com/CrocSwap/integer-mult-bounds/pull/5882)'s tensor theorem as cited premises. Let a catalogue contain $q\geq1$ matrices $K_j$ with positive rational ranks $r_j$ and unit capacities $c_j<r_j$. Put

$$
\theta=\max_{1\leq j\leq q}\frac{c_j}{r_j},
\qquad 0\leq\theta<1.
$$

For every sequence of length $n$ $j_1,\ldots,j_n$ of catalogue members, with repetitions and arbitrary ordering,

$$
\boxed{\displaystyle
\frac{c\left(\bigotimes_{\ell=1}^{n}K_{j_\ell}\right)}
     {\prod_{\ell=1}^{n}r_{j_\ell}}
\leq\theta^{\lceil n/q\rceil}.
}
\tag{2}
$$

**Proof.** Some type $j$ occurs $m_j\geq\lceil n/q\rceil$ times. Choose an odd prime attaining its capacity, so its rank fraction there is $c_j/r_j$. Every other factor has rank fraction at most one at that same prime. The primewise tensor formula therefore bounds the whole fraction by

$$
\left(\frac{c_j}{r_j}\right)^{m_j}
\leq\theta^{\lceil n/q\rceil}.
$$

If $\theta=0$, any nonempty tensor has zero capacity by the predecessor's zero-capacity case. ∎

This is uniform over switching schedules, not only repeated equal factors. It assumes a **fixed finite** defective catalogue. Adding new cuts as $n$ grows, a full-capacity type, nonproduct supports or changed endpoints is outside it. It concerns unit-channel capacity, not the entire productive signed invoice: one must not turn it into a universal $\kappa$ ceiling.

Let $K_3$ and $K_5$ be the predecessor's diagonal matrices with entries $(1,3)$ and $(1,5)$. Take $a$ copies of the first and $b$ of the second. Then

$$
\begin{aligned}
c\left(K_3^{\otimes a}
\otimesK_5^{\otimes b}\right)
&=2^{\min(a,b)},\\
r\left(K_3^{\otimes a}
\otimesK_5^{\otimes b}\right)
&=2^{a+b}.
\end{aligned}
$$

Bound (2) is attained by balanced counts. The one-of-each capacity two exceeds the product of individual capacities one; its relative loss nevertheless persists under every long word from this fixed catalogue.

## 3. Causal scalar cuts with full saturated bases

Here is an explicit reversible scalar realization of those pairing types. For odd $p\geq3$, take one untouched free coordinate $f$, $p$ coordinates $x$, and $p-1$ coordinates $z$, all arbitrary dirty. Let $V$ have columns $e_j-e_{j+1}$, and apply

$$
A:\quad
\begin{aligned}
x&\leftarrow x+Vz,\\
z&\leftarrow z+V^Tx.
\end{aligned}
$$

The suffix $B$ reverses those two operations. Each half consists of $4(p-1)$ signed scalar ADDs; the complete identity word costs **$8(p-1)$ ADDs**, uses $2p$ arbitrary coordinates and restores all of them. There is no clean storage, erasure or free basis conversion. Every intermediate event is replayed exactly.

At the cut choose $F=G$ to be the coordinate module generated by $f$ and $x$, with the original $z$-support excluded. The row and column eligibility equations are

$$
v_xV=0,
\qquad V^Tu_x=0.
$$

Both full $D$-modules have basis $\bigl(f,\sum_jx_j\bigr)$, because all adjacent coordinate differences must vanish. Their pairing is the diagonal matrix with entries $(1,p)$.

Thus $p=3$ and $p=5$ yield explicit causal algebraic cuts with complementary prime losses. They are calibration circuits, not source-bound P104 helpers: the required strict chart nesting, native targets, tensor carriers, delivery and complete caller bill are still absent. In particular their coefficient-basis channels are not automatically independent productive Gaussian targets.

The verifier also tensors the actual three-coordinate $K=[5]$ causal fixture from [PR #5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615) through depth four. Full independently recomputed row/column kernels have the complete tensor module, pairing $[5^d]$, and zero unit capacity. Scalar restoration at the base is checked; no exponentially large physical word is claimed or materialized.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/dyadic-tensor-capacity
python3.12 -B scripts/check_research_commit.py --package research/dyadic-tensor-capacity
```

The replay authenticates all live inputs. It reuses the pinned #5615 saturated
kernel routine, with a separate Fraction elimination to check ranks and
bidirectional module-basis coordinate changes. Every coordinate change must
be dyadic. It reconstructs the p=3,5 scalar words, their inverse and full cut
modules, checks mixed product cuts and the K=[5] fixture, and tests all binary
catalogue schedules through length 12. Corrupted supports, nonsaturated bases,
wrong capacities and a false nondefective-catalogue inference are rejected.
Normal and optimized modes use no dependencies and write no package files.
The uniform theorem is the written proof; the bounded checks do not replace it.

Base main was refreshed on 2026-10-28 UTC at
721c03822c421b7f7fcbb2598993b947c4d88419, priority 8. The navigation-only
repair from [PR #6050](https://github.com/CrocSwap/integer-mult-bounds/pull/6050)
is included. No selected cold replay was run. The optional full-history check
is unavailable in this shallow repository; declared source pins use its
reachable main-base descendant. No full-history pass is claimed.

## Significance for researchers

This fills the full-module premise of tensor capacity for exactly factored
causal cuts. Searching more general vectors inside the same product support
cannot evade the prime obstruction. A fixed finite collection of defective
cuts also cannot maintain a positive fraction of rational channels at arbitrary
tensor depth. New support, charts or caller boundaries remain legitimate
escape directions, with their implementation costs payable.

## Open next questions

Does an actual selected or pending native word admit a legal product cut with
these exact saturated supports and common physical timing? First extract one
prefix/suffix and its cut-field list, then verify the full module and price
its tensor carrier. The scalar calibration circuits do not discharge native
or productive-target obligations.

Can a controlled nonproduct cut enlarge the eligible module enough to fund its
extra fields and delivery? Begin with one added coordinate outside $F\otimes F$;
state the changed support and full signed bill before expanding a search.

## Credit

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
[Ali Romman](https://github.com/aliromman) supplies #5615's single-cut criterion,
causal K=[5] fixture and saturated-kernel code, retained unchanged.
[Nick Petalas](https://github.com/petalas) supplies #5882's tensor formula,
sharp bounds and complementary-prime examples. Those are credited premises.
Saturation over a PID, tensor basis arguments and pigeonhole counting are
classical; the contribution is the full eligible-module implication, fixed
catalogue bound and explicit causal-cut calibration here. No independent human
or proof-assistant review is claimed. Apache-2.0.
