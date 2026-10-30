# One extra cut coordinate can restore two dyadic helper channels

In the fixed-prefix dyadic helper interface of
[Ali Romman](https://github.com/aliromman)'s
[PR #5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615), enlarging
the eligible cut by $d$ scalar coordinates changes its unit-channel capacity by
at most $2d$. The bound is sharp for every positive integer $d$.
One added coordinate can therefore unlock **two** channels, not just one.

The attaining example is source-relative: the exact three-coordinate causal
fixture already present in #5615 has capacity zero on its restricted two-coordinate
cut and capacity two when its third coordinate becomes eligible. No prefix,
suffix or helper target is changed. Its complete arbitrary-dirty identity word
costs 12 signed scalar ADDs. Repeating independent blocks attains the $2d$ gain
with $d$ extra eligible coordinates and a full cost of $12d$ ADDs.

This is a scoped cut-module theorem and calibration construction, not a native
P104 realization, productive-target split, selected-frontier change or new κ.
Eligibility is a changed contract; permitting the third coordinate at a physical
common chart and delivering its channels remain separate obligations.

## Fixed contract and sharp bound

Let $D=\mathbb{Z}[1/2]$. Keep the prefix $A$, suffix $B$, helper input/output
support $G$, and complete endpoint fixed. Let $E$ be the dyadic row module
whose prefix image has support in $G$, and let $H$ be the corresponding suffix
column module. For eligible coordinate supports $F\subseteq F'$, define

$$
L=F\cap E,\qquad L'=F'\cap E,
\qquad R=F\cap H,\qquad R'=F'\cap H.
$$

The row/column copies of a coordinate module are identified in this notation.
Suppose $F'/F$ has rank $d$. With full dyadic bases, form the old and new
pairings $K$ and $K'$. Let $c(K)$ be the largest $t$ for which dyadic matrices
$X,Y$ satisfy $XKY=I_t$. Then

$$
\boxed{0\leq c(K')-c(K)\leq2d.}
$$

**Proof.** The quotient $L'/L$ injects into $F'/F$: its kernel consists precisely
of those eligible rows already in $F$. It is therefore a free $D$-module of rank
$a\leq d$. The short exact sequence splits, so every full basis of $L$ extends
to one of $L'$. Likewise a full basis of $R$ extends by $b\leq d$ columns.
Thus compatible choices of full bases put $K$ in the upper-left block of $K'$.

Padding old $X,Y$ with zeros shows $c(K')\geq c(K)$. By #5615's single-cut
criterion, some odd prime $p$ attains $c(K)$ as the rank of $K$ modulo $p$.
Adding $a$ rows and $b$ columns can raise rank by at most $a+b$. Consequently

$$
c(K')\leq r_p(K')\leq r_p(K)+a+b\leq c(K)+2d,
$$

where $r_p$ denotes rank modulo $p$. This proves the bound. The argument does
not require the added channels to be simple tensors or to use coordinate bases
inside the eligible modules. ∎

The proof requires a **fixed** prefix, suffix, helper support and embedding of
the old cut into the new one. A different program or helper endpoint need not
contain the old pairing block. The theorem then supplies no capacity bound.

## Exact source fixture: zero becomes two

The retained fixture has prefix and inverse suffix

$$
A=\begin{pmatrix}1&0&1\\0&1&2\\1&2&6\end{pmatrix},
\qquad
B=\begin{pmatrix}2&2&-1\\2&5&-2\\-1&-2&1\end{pmatrix}.
$$

Take helper support $G$ on the first two original coordinates. On the old cut
$F$, also supported on the first two physical coordinates, the full eligible
row and column bases are both $(-2,1)$. Their pairing is $[5]$, with rational
rank one but zero dyadic unit capacity: reduction modulo five has rank zero.

Now allow the third physical coordinate, so $F'$ is the whole ambient space.
Full eligible bases are the first two rows of $B$ and the first two columns
of $A$. Their pairing is $I_2$, since $BA=I_3$. The new capacity is exactly two.
These are full module bases: invertibility over $D$ identifies them with all
helper-supported rows and columns. No clean-input assumption is used. In bases
that extend the old ones, the enlarged pairing is

$$
K'=\begin{pmatrix}5&-2\\-2&1\end{pmatrix},
\qquad 5\cdot1-(-2)^2=1.
$$

Its old upper-left block is still $[5]$, while the whole block is a unit.

The exact prefix, in current-value semantics, is

```text
x0 += z
x1 += z
x1 += z
z  += x0
z  += x1
z  += x1
```

The suffix executes these instructions in reverse order with minus signs.
All three independent dirty inputs are restored. The complete word has 12
signed ADDs and uses the same three coordinates before and after changing the
eligible support. No allocation or basis conversion is silently added to this
calibration word. Realizing the changed eligibility and channel delivery in a
native supplier is not provided or priced as zero.

For $d$ independent blocks, the old pairing is $5I_d$ and the enlarged pairing
is $I_{2d}$. Adding all $d$ third coordinates therefore attains the bound $2d$.
If only $s$ third coordinates become eligible, the exact capacity is $2s$.
This also gives every intermediate even gain in the family.

## A necessary size for a nonproduct rescue

[Nick Petalas](https://github.com/petalas)'s
[PR #5882](https://github.com/CrocSwap/integer-mult-bounds/pull/5882) proves that
an algebraic repeated pairing $K$ has tensor capacity $c(K)^f$ and rational
rank $r(K)^f$. Suppose an actual product cut has this exact pairing. Any
fixed-prefix enlargement that raises its capacity to at least $r(K)^f$ must add

$$
d\geq\left\lceil\frac{r(K)^f-c(K)^f}{2}\right\rceil
$$

eligible scalar coordinates. This follows by applying the sharp bound to the
whole tensor cut. It does not assume that the enlarged cut itself factors.
This is a coordinate-availability requirement, not a paid-job or storage tariff:
newly eligible coordinates may already exist. Their native charts, timing and
delivery still require a separate source-bound bill.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/dyadic-cut-enlargement
python3.12 -B scripts/check_research_commit.py --package research/dyadic-cut-enlargement
```

The verifier authenticates the unchanged #5615 kernel/capacity source and the
#5882 proof. It reconstructs every ADD of the scalar words, solves the complete row/column eligibility constraints with the retained kernel
routine, and checks all partial support
enlargements of one through six independent blocks. It verifies literal full
unit-block witnesses and modular upper bounds, including odd and dyadic-scaled
coefficient controls. A separate small bordered-matrix census corroborates the
rank bound. Wrong cut supports, a nonsaturated basis, false one-channel gain
bounds and a changed prefix are rejected. Normal and optimized replays use
explicit checks and write no package files.

Canonical main was refreshed on 2026-10-28 UTC at
721c03822c421b7f7fcbb2598993b947c4d88419, priority 8. The navigation repair
from [PR #6050](https://github.com/CrocSwap/integer-mult-bounds/pull/6050) is
included; frozen packages and the selected record are unchanged. No selected
cold replay ran. The optional full-history preflight is unavailable in this
shallow checkout; all declared pins use its reachable base.

## Significance for researchers

A zero-capacity restricted cut need not remain useless after one legal support
change. Conversely, each extra eligible coordinate can recover at most two
channels while the program is fixed. This supplies a sharp optimistic resource
screen for nonproduct support changes beyond
[PR #6054](https://github.com/CrocSwap/integer-mult-bounds/pull/6054)'s product-cut
obstruction. It does not grant the physical common-chart or consumer contract.

## Open next questions

Can one actual native helper cut make an outside coordinate eligible at a paid
cost that its additional channels can fund? First extract the fixed prefix,
suffix and complete support embedding, then prove legal chart/timing and delivery.
The scalar fixture alone does not supply those conditions.

Can changed prefixes or helper endpoints beat the fixed-program two-per-coordinate
bound at a favorable complete invoice? First name the changed map and preserve
all independent dirty inputs. Such changes lie outside this theorem.

## Credit

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
[Ali Romman](https://github.com/aliromman) supplies the single-cut theorem,
source fixture and unchanged saturated-kernel code in #5615.
[Nick Petalas](https://github.com/petalas) supplies #5882's tensor formula.
Their methods and prior attribution remain intact. Module splitting over a PID
and bordered-matrix rank bounds are classical. The contribution is their sharp
fixed-cut enlargement implication and the source-relative attaining family.
No independent human or proof-assistant review is claimed. Apache-2.0.
