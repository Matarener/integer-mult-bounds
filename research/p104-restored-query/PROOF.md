# A restored coefficient caller factors through one Newton query

Clear1nsight, with substantial OpenAI assistance. This is a scoped written
proof with a bounded finite replay, not a formal proof-kernel certificate.
The original word, recipes, stagewise domain, and their credit are preserved.

## 1. Statement and exact boundary

Let \(R=\mathbb Z[i]\), \(\pi=1+i\), \(N=512\), and

\[
E_r=\begin{pmatrix}1&0\\1&\pi\end{pmatrix}^{\otimes r},
\qquad B_r=E_rR^{2^r},\qquad B=B_9.
\]

The inputs are 52 separately owned Gaussian coefficient banks
\(a_0,\ldots,a_{51}\in R^N\), five distinct dirty banks
\(d_{31},d_{30},d_{29},d_{28},d_{27}\in B\), and a separate dirty query
\(q\in B\). All public frames are initially empty. The coefficient meanings
are those of PR #3467's encoder \(K:R^{52N}\to L\), recalled below. They
are not arbitrary pre-existing raw Y values.

Consider this **new closed program**:

1. Apply \(K\), obtaining the 52 prepared Y banks.
2. Execute the actual 257-event producer dependency cone before event 2025.
3. Execute the actual first collector, events 2025 through 2039.
4. Traverse the selected producer events in reverse, applying their inverses
   except for the five Q compensation ADDs at 908, 910, 912, 914, and 916.
5. Apply \(K^{-1}\) to the returned Y banks.

Then every coefficient bank and every dirty D bank is returned exactly, every
public frame is empty, private C is erased at zero, and

\[
q_{\rm out}=q+E_9(a_2+a_9+a_{16}+a_{27}+a_{51}).                 \tag{1}
\]

The literal core in steps 2--4 has 524 events. Its return is appended by this
construction; it is not asserted to occur in the original 5,398-event word.
The source cone excludes 1,768 events of the full 2,025-event prefix. The
theorem does not execute or admit those omitted recipient histories or the
675 external ports. The distinct full-prefix result in PR #3466 and the
omitted adapters in PR #3469 are not replaced by this theorem.

## 2. Inherited entrance theorem and coefficient meanings

The retained [PR3467 proof](inputs/PR3467_PROOF.md) classifies \(L\subset B^{52}\):
the maximal module in that stated initial domain for which all cone quarter
increments are integral, every completed literal native pair equals its ideal
Gaussian gate, and all six cut banks lie in \(B\). It does not classify genuinely
rounded paths whose later errors cancel.

In the actual read order of each D group, write
\(p_t=y_1+\cdots+y_t\), with \(p_0=0\). The change from the Y values to these
partial sums is unimodular. PR #3467 separately parameterizes 32 intervals
without a D transport, 15 intervals with one actual rank-one D transport, and
five terminal intervals. Nonterminal profiles use respectively

\[
E_9\operatorname{diag}(\pi^{\max(4-|S|,0)}),\qquad
E_9\operatorname{diag}(\pi^{\max(4-|S\setminus\{0\}|,0)}),
\]

followed, where required, by the inverse right wrapper, then by the specified
actual inverse path. Each terminal partial sum is exactly \(4E_9a_t\), with positive
4; replacing it by \(\pi^4=-4\) would change the coefficient map. Finally,
successive partial sums are differenced into the Y banks.

We inherit that \(K\) is an \(R\)-module isomorphism onto \(L\), and that

\[
S=(4B)^{52}\subset L\subset B^{52},\qquad
[B^{52}:L]=2^{20424},\quad [B^{52}:S]=2^{106496}.               \tag{2}
\]

These are predecessor results, not new lattice classifications here.
The [PR3382 proof](inputs/PR3382_PROOF.md) supplies the Newton invariance and
literal-pair criterion; the [PR3416 proof](inputs/PR3416_PROOF.md) supplies
the actual native covariance including global phase. The
[PR3426 proof](inputs/PR3426_PROOF.md) supplies the ideal five-group condition.
The primary implementation reuses authenticated predecessor code. The second
literal implementation derives its Y paths and arithmetic separately and
imports no predecessor executable, while retaining those written dependencies.

## 3. The actual producer and collector

Both implementations derive the dependency cone and the group order from the
frozen WORD and bind every used native occurrence to its old frame, new frame,
rank, and exact recipe. The resulting terminal coordinates are:

| D group | Number of Y reads | Terminal coefficient slot | Last Y source | Last read event |
|---|---:|---:|---|---:|
| D31 | 3 | 2 | Y99 | 1231 |
| D30 | 7 | 9 | Y100 | 1393 |
| D29 | 7 | 16 | Y66 | 1459 |
| D28 | 11 | 27 | Y72 | 1641 |
| D27 | 24 | 51 | Y80 | 1831 |

Write \(p_j\) for the terminal partial sum of group \(j\).
The six cut values, with the exact phase conventions of the source, are

\[
D_j=A_O(d_j+p_j/4),\qquad
Q7=A_P\left(q-\sum_jd_j\right),                               \tag{3}
\]

where

\[
O=[256,136,64,40,16,4,2,1],\qquad P=[364].
\]

The Q path consists of native event 972. The five negative unit ADDs
into Q occur at 908, 910, 912, 914, and 916, before any Y quarter
enters the respective D. They therefore compensate the initial dirty values.

The first collector allocates \(C=0\) at O, adds the five D banks into C,
uses the authentic rank-seven O-to-P native at 2031, adds C into Q7
with coefficient \(+1\) at 2032, uses the authentic reverse native at 2033,
subtracts the five unchanged D banks in reverse order, and erases zero C
at 2039. From (3), after the query ADD its Q value is

\[
A_P\left(q-\sum_jd_j+\sum_j(d_j+p_j/4)\right)
=A_P\left(q+\sum_jp_j/4\right).                              \tag{4}
\]

The Ds and Ys are untouched by the collector, and all its inputs are in B.
Inherited native invariance and covariance therefore apply. Every literal
completed pair is exact on this domain; an individual internal signed-floor
half is allowed to round. The proof never replaces that criterion by the
stronger and generally false demand that each internal half divide exactly.

## 4. Why the selective return works

During the reverse traversal, every D and Y operation sees the same states it
saw in the forward producer, in reverse order. In particular, each inverse
quarter increment is integral. Its donor is restored before that donor is
used again. Each inverse native on D or Y retraces an admitted exact path.

Q differs from its original producer state only by (4). Its single inverse
native, event 972, maps (4) to \(q+\sum_jp_j/4\). This value lies in B because
each \(p_j/4=E_9a_{t_j}\) lies in B. Thus the changed Q input to that inverse
is also admitted. No further Q operation is executed: the five inverse
compensation ADDs are deliberately absent. The return restores every
prepared Y and every dirty D, and all 58 public frames are empty.

Applying \(K^{-1}\) now returns every original coefficient bank. Substituting
the five terminal partial sums into (4) gives (1), proving the closed caller.

Full producer reversal would instead perform the five positive dirty
compensation ADDs at the end. Its exact output is

\[
q_{\rm wrong}=q+\sum_jd_j+E_9\sum_{t\in T}a_t,\qquad
T=(2,9,16,27,51).                                           \tag{5}
\]

This is a concrete failed cleanup when the dirty sum is nonzero, not a generic
interface warning. Both literal implementations check (5) on every coordinate
of the signed dense fixture. Other controls remove inverse 972, alter the
collector phase, change the query sign, or change a return-quarter sign.

## 5. The enlargement adds no five-readout range

Define the normalized five-readout map on L by

\[
\rho_5(y)=\left(\frac14\sum_{Y\in G_j}y_Y\right)_{j=1}^5
\in B^5.                                                    \tag{6}
\]

Define \(\sigma:B^5\to S\) by placing \(4b_j\) in the final Y bank of group j
and zero in every other Y bank. The groups are disjoint, and
\(\rho_5\sigma=\operatorname{id}_{B^5}\). In particular,

\[
\rho_5(L)=\rho_5(S)=B^5.                                    \tag{7}
\]

Let \(K_5=\ker(\rho_5|_L)\). For any \(y\in L\),
\(y-\sigma\rho_5(y)\in K_5\); if \(y\in S\), the same difference lies in S.
The shared section gives

\[
L=K_5\oplus\sigma(B^5),\qquad
S=(S\cap K_5)\oplus\sigma(B^5).
\]

Consequently the inclusion of \(K_5\) into L induces an isomorphism

\[
L/S\ \cong\ K_5/(S\cap K_5),\qquad |L/S|=2^{86072}.           \tag{8}
\]

This is the precise sense in which the entire relative enlargement has
readout-kernel representatives. **The map \(\rho_5\) does not descend to
L/S:** S itself has nonzero, indeed surjective, readouts. Equation (8) does
not identify a quotient with a literal subset of L.

For a fixed dirty input, (7) means the larger domain does not enlarge the
range of the five normalized D increments. The five-active section reproduces
all five cut D values and Q's cut value, not merely the final summed query.
It need not reproduce intermediate Y/D values or any omitted external readout.

## 6. One final increment, with all source information returned

In the independent coefficient coordinates,

\[
\rho_5K(a)=(E_9a_2,E_9a_9,E_9a_{16},E_9a_{27},E_9a_{51}).
\]

Thus \(\ker(\rho_5K)\) has Gaussian rank \(47N\). Summing the five readouts
gives the increment map

\[
\Phi(a)=E_9\sum_{t\in T}a_t,\qquad
\operatorname{rank}_R\Phi=N,\quad
\operatorname{rank}_R\ker\Phi=51N.                           \tag{9}
\]

Indeed E is injective, a single terminal coordinate provides a section onto B,
and the terminal sum has four independent difference coordinates in addition
to the 47 nonterminal banks. This specializes the already credited rank-one
port-map observation in PR #3423 to an actual admitted, returned caller; it
does not claim a new general rank-one phenomenon.

The **complete** map sends \((a,d,q)\) to \((a,d,q+\Phi(a))\). It is reversible:
its inverse subtracts \(\Phi(a)\) from Q. Its coefficient outputs do not
disappear. Kernel rank in (9), and the finite index in (8), are not erased
information, released storage, compressed inputs, or saved physical bits.

Three source-bound fixtures make the distinctions concrete:

- Set only \(a_{44}=\delta_{15}\). This slot is Y91 at 1817, followed by
  Y90 at 1819, in a zero-transport gap of D27. Its profile exponent is zero,
  and its prepared pair is \(p,-p\), where \(A_Op=E_9\delta_{15}\).
  At the first quarter read the D increment is \(-1\) on exactly 32 addresses;
  the next read cancels it. Since the Newton coefficient \(\delta_{15}\)
  is not divisible by 4 and \(A_O\) preserves 4B, \(p\notin4B\).
  This is a nonzero class in (8) with zero five-readout and Q increments.
- Set \(a_2=\delta_0,\ a_9=-\delta_0\). The first two readouts are nonzero
  opposites, while Q's increment is zero. This fixture already belongs to S
  and distinguishes terminal differences from the nonterminal kernel.
- Combine the nonterminal fixture with five distinct signed terminal
  coefficient impulses. Compare K(a) with \(\sigma\rho_5K(a)\).
  Both have the same five readouts and final increment. The original
  nonterminal coefficient remains required in the complete returned output.

The fixture module checks actual preparation, decoding, source paths, readout
arrays, and both direct schedules. It does not present those formula checks
as additional full literal-core replays.

## 7. Two direct schedules for exactly this interface

For a caller lending all coefficients read-only, supply a distinct owned zero
Gaussian bank Z. Gather the five terminal banks into Z, apply E, add Z to Q,
apply the exact inverse E, ungather the five terminals in reverse order, and
erase zero Z. All coefficients remain unchanged throughout.

For a caller permitting temporary mutation of the first terminal coefficient
bank \(a_2\), gather the other four into that bank, encode it, add it to Q,
decode it, and subtract the other four in reverse order. This restores the
original possibly nonzero \(a_2\) and needs no extra Gaussian bank. The other
51 coefficient banks are read-only. In both modes the five dirty Ds are
untouched, so they can be carried through as unchanged outputs.

Each direct schedule also uses one separate real zero scratch word. The
strict real-register programs for multiplication and exact division by
\(\pi\), their zero restoration, arithmetic counts, and finite signed-width
proof appear in [COSTS.md](COSTS.md). All inverse divisions are on the actual
image of the preceding encoding, which the Q read leaves unchanged.

These schedules prove a logical caller equivalence and constructive arithmetic
upper bounds. They do not supply physical addressing, layout, zero generation,
or a fast recursive realization. The larger P104 supplier still needs its
other consumers and complete bill. The inherited 599/584 unchanged-profile
stop and the selected result remain unchanged.

## 8. What the finite evidence establishes

The registered verifier authenticates exact inputs and retained proof bytes,
compiles captured source bytes, independently constructs the two literal
executions, and compares full prepared, cut, returned-coefficient, returned-D,
returned-Y, and Q arrays before hashing them. Each dense core executes
524 events and compares 184,832 completed literal pairs with ideal values.
The direct strict-register executions match the same returned arrays and Q.

The dense fixture is evidence for the implementation and exact source
composition. The universal statements above rely on the written algebra and
the explicitly inherited theorems; they are not inferred by testing one
fixture. Adversarial arithmetic, dirty-state, phase, frame, ownership, source,
and typed-receipt controls are separate from that positive evidence.
No independent human mathematical review is claimed.
