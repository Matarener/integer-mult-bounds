# Exact operator admission and the cost of repairing the moved axes

This note concerns the declared eight-stream complex controller. It proves its
global operator from its local endpoint interface, rejects the former axis
overlay, constructs an exact correction, and identifies why that correction
does not retain the proposed saving. The uniform native tape, precision,
recurrence and local invocation interfaces remain conditional assumptions.

## 1. Exact phase convention

The retained construction uses

\[
X_v f(x)=f(x+v),\qquad
C_v=\frac{(1+i)I+(1-i)X_v}{2}.
\]

On Fourier character \(z\), \(C_v\) has multiplier
\(i^{\chi_v(z)}\), where \(\chi_v(z)=v\cdot z\bmod2\). A translation
has multiplier \(i^{2\chi_v(z)}\). No global phase is discarded.

As a function of Boolean coordinates, its exponent has the exact normal form

\[
\chi_v(z)=\sum_jv_jz_j-2\sum_{j<k}v_jv_kz_jz_k\pmod4.
\]

The program stores all 73 linear coefficients modulo four and all quadratic
coefficients divided by two modulo two. It compares these forms exactly. Such
a comparison is a proof for every character; it is not a test of selected
characters. Equality also survives tensoring: the exponents of the separate
tensor factors add modulo four.

## 2. Gauge normalization, including the signs

For a port \(q\), write

\[
D_{-1,X}=C_q,\quad D_{-1,Y}=I,\quad
D_{s,X}=C_{[0,9+8s)},\quad D_{s,Y}=D_{s,X}C_q^{-1}.
\]

There are four pairs. Let \(D_{\rm initial}\) be the eight-stream diagonal
operator with entries \((C_q,I)\) on each pair. The canonical forward local
call is

\[
\operatorname{diag}(D_{s,X},D_{s,Y})
\begin{pmatrix}1&0\\1&1\end{pmatrix}
\operatorname{diag}(D_{s-1,X},D_{s-1,Y})^{-1},
\]

and the reverse local call has scalar matrix
\(\left(\begin{smallmatrix}1&-1\\0&1\end{smallmatrix}\right)\).
This is the retained local endpoint contract, including the reverse sign.

The checker maintains the identity

\[
P_t=D_tM_tD_{\rm initial}^{-1}
\]

through every declared event. Here \(D_t\) is a diagonal matrix of exact phase
forms, and \(M_t\) is an ordinary signed integer matrix. At a local call, its
two entrance phases are checked and removed before the scalar transvection,
then the two declared exit phases are installed. Every idle child is added
with its actual translation, and its exit phase is checked against its
declared clock. Every bridge is permitted only after the two phases that it
mixes agree exactly.

The bridge updates are \(X_d\mathrel{+}=cX_s\) and
\(Y_s\mathrel{-}=cY_d\). At the end, each Y stream receives the literal
\(X_q\) translation. The signed exchange is
\((X,Y)\leftarrow(Y,-X)\). The resulting integer scalar matrix is exactly
the identity. The final gauge is exactly
\(D_{\rm final}=C_{\rm all}D_{\rm initial}\). Consequently

\[
P_{\rm final}=C_{\rm all}I_8.
\]

`full_operator.py` and `t360_admission.py` check 10,416 exact phase identities
across all 112 actual ports. The omission controls for an idle translation and
the final Y translation both fail. Independently written dense Gaussian
matrix composition agrees with the normalized formula on 19 complete physical
characters, including mixed characters. This last comparison is a check on
the implementation and sign conventions; the polynomial argument provides
the all-character proof.

For a common cover map \(g\), conjugate the whole identity by \(P_g\). The
retained all-live translation identity converts
\(P_gC_{\rm all}P_g^{-1}\) to \(C_{\rm all}\), including its exact phase.
The present proof does not replace that inherited cover/physical routing
interface.

## 3. Binding the positive statement to the actual T360 supplier

The positive receipt uses PR3945's literal `ORDER.json`, `DISPATCH.json` and
`FILL.json.gz`, and the newly composed base and extra words. The substitution
is explicit: the dispatch tag `gauge44` selects the composed base word and
`extra` selects the composed extra word. Both inputs are matched to their
completed five-stage native receipts. The current native frames determine
the widths; the old report's descriptive profile is not used to derive them.

The order contains each of the 3,240 calls exactly once and orders each
replica's nine stages correctly. For each of 360 owners and each of twenty
idle slots, the checker records the stream's preceding scalar observation and
the idle endpoint. Every one of the 1,321,920 helper rows lies strictly inside
its own interval. Its actual width fits its assigned original child axes, and
the assigned cells are disjoint. Every helper occurrence is assigned once.

Thus the hosted phase factors of a child can be moved to its idle endpoint
without crossing a scalar observation of that physical stream. These factors
and the literal complementary residual multiply to the original full child.
This commutation argument uses completed local endpoint operators and permits
arbitrary correlated dirty inputs. It does not require clean helper streams.

The independent scan obtains hosted width mass 10,704,960 and residual rank
mass 6,713,280, summing to the original 17,418,240 axes. Its residual profile is

\[
\{3:23328,\;5:4320,\;48:137952\}.
\]

That profile is compared exactly to the independently generated complete
owner invoice. The actual nine-stage graph normalizes to the proved graph.
There are no axis transfers. Old T37 stock, bank-padding counts, local
programs, replica counts and price metadata in the inherited template are
not used as the T360 supplier. Native realization of the declared axis-cell
embedding and common cover routing remains an explicit source-bound interface.

## 4. Exhaustive phase-support admission

Let \(\delta_c(z)\) be a candidate's changed phase at slot \(c\). Removing the
proved baseline gauges leaves the constant scalar controller and the diagonal
factors \(i^{\delta_c(z)}\). Its complete normalized operator is denoted
\(E(z)\). The candidate is correct only if \(E(z)=I_8\).

If the moved axes span a \(k\)-dimensional space of linear forms, every binary
phase assignment is realized by some Fourier character. Enumerating the
\(2^k\) assignments therefore decides every one of the \(2^{73}\) characters.
The source owner-0/port-0 group has five independent moved axes and six moves.
Exactly 31 of its 32 binary assignments give a nonidentity operator.

**Positive tensor admission requires a stronger check.** A binary phase
\(C_v\) has eigenvalues \(1,i\), whereas \(C_v^{\otimes f}\) can have all
four fourth roots. An identity such as
\((C-I)(C-iI)=0\) is true on one factor and false at the tensor eigenvalue
\(-1\), where its value is \(2+2i\).

For the distinct active axes \(a_1,\ldots,a_J\), let \(H\) be the subgroup
of \((\mathbb Z/4)^J\) generated by all binary vectors
\((\chi_{a_j}(z))_j\). This subgroup is exactly the set attainable at some
positive tensor multiplicity. A nonnegative sum describes tensor factors;
conversely, every inverse of a generator is three copies of that generator.
The zero vector is also realized by a zero-character factor. Checking every
element of \(H\) proves the declared phase/scalar identity for every tensor
multiplicity. The checker fails closed when a configured state cap would
leave this enumeration incomplete.

For the actual five independent axes, \(|H|=4^5=1024\). Exactly 1,008 states
give a nonidentity operator. Baseline admission uses the exact gauge proof and
also passes this stronger predicate. This is uniform operator correctness of
the declared network, not admission of an all-size runtime or tariff.

## 5. A literal exact correction and a rank-five obstruction

Let \(M_c\) be the signed scalar prefix at slot \(c\), and \(E_s\) the
coordinate projector onto its physical stream. Set

\[
K_c=M_c^{-1}E_sM_c,\qquad
Q_c(z)=I+(i^{\delta_c(z)}-1)K_c.
\]

Each \(K_c\) is an exact rank-one idempotent. The normalized discrepancy is
the chronologically composed product of these factors. Reversing their order
and phase signs supplies its exact inverse. The physical correction is

\[
R(z)=D_{\rm initial}(z)E(z)^{-1}D_{\rm initial}(z)^{-1}.
\]

`correction.py` constructs the five affected projectors independently of its
reverse-event inverse and checks their agreement on all 1,024 tensor phase
states. Omitting any one factor fails on 768 states; changing all inverse
signs fails on 896. It also writes the actual finite physical correction as
66 nonzero matrix/translation terms with Gaussian-dyadic coefficients, and
checks its complete 64-character inverse Walsh reconstruction.

There is a sharp insertion-count witness within the declared caller-level
character-block interface. At the binary character \(e_{52}+e_{72}\), the
normalized defect \(E-I\) has rank five. Its rows and columns
\(\{1,2,3,6,7\}\) form a diagonal minor with entries

\[
-1-i,\;-1-i,\;-1-i,\;-2,\;-1+i,
\]

whose determinant is \(-8i\). A completed single-stream phase insertion
changes a fixed-character operator by rank at most one, even after invertible
prefix and suffix maps within that character block. Telescoping a sequence
of insertions shows that at least five such children are necessary. This
does not cover adapters that mix distinct Fourier characters or edits inside
an opaque recursive child's implementation.

Five grouped inverse phase children also suffice algebraically: their axis
ranks are \(3,3,4,1,1\). Insert them adjacent to the affected residual
factors to restore each original phase exactly, or use the conjugated inverse
above. Inverse phases need one child of the same rank plus the explicit
translation, because \(C_v^{-1}=C_vX_v\).

## 6. The correction cannot retain the gain in the additive interface

The following comparison retains the old local calls, hosted profile, stock
and total residual rank mass. New repair children are extra to that mass.
Grant all movement, gauge conjugation, restoration and adapters for free.
Write \(a=349/200000=0.001745\), \(p=1-a\). A rank-\(r\) child has raw
moment cost \(r^p\); multiplying every term by the same normalization does
not change the price sign.

PR3220's allowance argument applies to at most twenty old residual slots with
rank at most 51. Repacking them at fixed mass, even with real ranks and real
multiplicities, can save no more than

\[
\sum_r(r^{1-a}-r51^{-a})
\le20a\frac{51}{e}
<20a51\frac38
=\frac{53397}{80000}.
\]

Here \(e>8/3\), and \(x\log(51/x)\le51/e\) is the one-variable maximum.
Every positive integer-rank repair child costs at least one. Consequently
even one extra child loses by more than \(26603/80000\) raw units; five lose
by more than \(346603/80000\). The literal five-factor bill is actually

\[
2+2\,3^{1-a}+4^{1-a}\approx11.97884390772367.
\]

The finite 66-term translation expression does not supply a constant uniform
native bill. PR3989 gives a closely related exact two-term Pauli transfer
whose direct monomial expansion needs \(2^f\) channels at tensor multiplicity
\(f\). A fixed finite cube computation cannot erase this volume obligation.
The present package does not claim a universal lower bound against different
coupled native macros. It supplies no such macro with a profitable complete
bill.

## 7. Constant Gaussian bridge coefficients do not repair these slots

There is a useful extension beyond signed-integer bridge coefficients. Work
in the local Gaussian-integer ring at \(\pi=1-i\). Permit arbitrary constant
scalar coefficients integral at \(\pi\), including \(\pm i\), provided every
normalized scalar prefix reduces to the same prefix modulo \(\pi\), the
same twenty phase slots remain, and the full zero-character scalar matrix is
exactly identity. The coefficient sizes are unbounded. Additional normalized
scalar factors congruent to identity modulo \(\pi\) are included.

For the candidate prefixes, \(K'_c=M_c'^{-1}E_sM'_c\) has the same reduction
as \(K_c\). The retained twenty reduced projectors have a left inverse.
The new program independently reconstructs all twenty from signed prefixes
and checks all 400 entries of that left-inverse identity. It does not rerun
the old fixed-slot search.

Fix any Fourier character. Modulo \(\pi^2\), the identity of the product

\[
\prod_c[I+(i^{\delta_c}-1)K'_c]
\]

forces each \(\delta_c\) to be even, because the twenty first-order columns
are independent. Every perturbation now starts at \(\pi^2\). Modulo
\(\pi^3\), cross products vanish and each \(K'_c\) can be replaced by its
reduction modulo \(\pi\). The same left inverse forces
\(\delta_c/2\equiv0\pmod2\). Thus \(\delta_c\equiv0\pmod4\) at every
slot and every character.

If arbitrary linear translations are also allowed, equality of the phase
forms fixes the off-diagonal entries of \(\sum_a aa^T\). Their linear
coefficients modulo two fix its diagonal. An orthonormal frame therefore
has the same orthogonal projector and the same rank in every slot.

This rules out constant Gaussian bridge dressing on the retained normalized
graph as a repair of a nonzero rank transfer. It does not cover denominators
divisible by \(\pi\), including \(1/2\); a changed topology modulo \(\pi\);
new phase slots; changed local endpoints; or coordinate-dependent coupled
operator coefficients. Those changes alter an actual hypothesis of the
proof and remain appropriate places to seek a new construction.

## Attribution and status

The local, native, controller and cover lineage is retained from Rohan Arun,
Jeremy Diviney and the credited predecessor packages. Nick Petalas/PR3187
supplied the authenticated physical-stream objection and source projection;
PR4046 and the independent dense audit bound it to the disputed literal
MOVES. Ross Richardson/PR3220 supplied the additive repair allowance.
Clear1nsight/PR3989 supplied the selected Pauli-transfer/tensor-cost result.
PR3945 supplied the T360 terminal refits and literal allocation used by the
new composed supplier. The present symbolic normalization, tensor subgroup
gate, literal multi-axis rank-five correction analysis, and Gaussian
coefficient extension were developed with substantial OpenAI assistance.
No independent human review or formal proof-kernel verification is claimed.
New material is Apache-2.0. All predecessor sources remain unchanged.
