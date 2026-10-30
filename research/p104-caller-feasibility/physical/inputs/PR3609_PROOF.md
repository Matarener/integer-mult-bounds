# An in-place completion at the actual P104 entrance

Clear1nsight, with substantial OpenAI assistance. New material is Apache-2.0;
predecessor authorship and notices remain in force.

## Statement and source boundary

The supplied program replaces the omitted part of the pinned 5,398-event P104
word by a 1,238-operation entrance program, followed by the unchanged
4,027-event projection. It has the same complete physical endpoint map,
including arbitrary admitted dirty offsets and all 358 final frames. The
result closes a chronological, common-frame access obligation. It does not
establish a complete physical supplier or a new multiplication exponent.

The projection is credited to [PR #3446](https://github.com/CrocSwap/integer-mult-bounds/pull/3446),
Hiroki Kumazaki; the rank-eight residual and integer factorization to
[PR #3462](https://github.com/CrocSwap/integer-mult-bounds/pull/3462), Nick Petalas;
and the endpoint-adapter construction to
[PR #3469](https://github.com/CrocSwap/integer-mult-bounds/pull/3469), Nick Petalas.
Their exact retained sources, the original WORD/native lineage, and executable
dependencies are bound in [SOURCES.json](SOURCES.json).

The method of using dirty outputs as accumulators while restoring modified
inputs is general: see Jean-Guillaume Dumas and Bruno Grenet,
[In-place accumulation of fast multiplication formulae](https://arxiv.org/abs/2307.12712),
ISSAC 2024. The contribution here is its source-bound P104 realization and bill,
not that general accumulation principle or the predecessor factorization.

## 1. Why the correction can move to the entrance

Let $J_f$ denote the retained Delta chart of frame $f$. Work first with
chart-normalized public fields: the physical value of normalized $z$ in frame
$f$ is $J_fz$. Let $W$ be the original normalized endpoint operator and $S$
the normalized operator of the projection. The source reconstruction proves

$$
W=S+K,\qquad K_{X,Y}=\frac12 CA,
$$

where $A$ has eight rows and 104 Y columns, and $C$ has 52 X rows and eight
columns. Every other block of $K$ is zero.

The dependency reconstruction retains exactly the predecessor's event-index
digest. Every retained event neither reads nor writes any of the 93 omitted
public banks. Consequently $S$ acts identically on them and has no dependence
on their initial values in its other outputs. It also preserves every
normalized Y field. Since the image of $K$ lies in the omitted X banks and
$K$ reads only Y,

$$
SK=KS=K,\qquad K^2=0,\qquad W=S(I+K)=(I+K)S.
$$

These equalities concern the normalized operators. Physical frames are still
owed. At the actual entrance all Y banks are in the empty frame. The new
prefix computes $I+K$ there and delivers all 93 omitted banks in their required
full frame

$$F=[256,128,64,32,16,8,4,2,1].$$

It restores every retained public field to its identical entrance value and
frame. Thus the original retained trace executes from exactly its original
state, including its eight private lifetimes. Its disjointness makes the
already completed omitted banks irrelevant to that trace.

## 2. Dirty-output accumulation and source return

Use the following ordered eight pivot X banks:

```text
X0, X33, X101, X102, X11, X12, X15, X24.
```

The actual rows of $C$ on these banks are $I_8$. Write their values as $x_P$,
and the other 44 X values as $x_T$. First move all 52 X banks from their
actual singleton entrance frames to the empty frame. Then perform

$$
x_T\leftarrow x_T-C_Tx_P,\qquad
x_P\leftarrow x_P+\frac12 AY,\qquad
x_T\leftarrow x_T+C_Tx_P.
$$

The entire first stage precedes every gather. The last stage uses the updated
pivots, so its result is
$x_T-C_Tx_P+C_T(x_P+AY/2)=x_T+C_TAY/2$.
The pivots themselves have their required updates because $C_P=I_8$.
No dirty value is assumed zero or discarded.

For each active Y column, halve that bank once, execute its signed unit ADDs
into the eight pivots, then double it immediately. This realizes coefficients
of magnitude two by repeated unit ADDs and returns the source before advancing
to the next column. Exactly 103 columns are active. Y1 is unused by this
correction but remains live and is used by the retained projection.

Finally move all 52 X and the other 41 omitted banks from empty to $F$.
The latter are 38 N banks and G2, G3, G9; they retain their normalized dirty
values. Sources and outputs have distinct physical roles. The prefix needs
temporarily writable, restored Y access and no additional Gaussian bank.
Arithmetic registers, monomial workspace, routing and controllers still need
their own implementations.

## 3. The new native maps include their phases

There are 52 actual singleton-to-empty maps of rank one and a shared
empty-to-full map of rank nine, used 93 times. Each requested map is
$J_{\rm new}J_{\rm old}^{-1}$. The pinned compiler synthesizes its affine
quadratic-phase monomials and positive native child.

The separately written PR #3416 checker compares each of the 53 distinct
recipes with the direct canonical-chart expression. It checks all 18 signed
Pauli actions and a complete 512-entry exact Gaussian-dyadic anchor. Equality
of the signed actions makes the ratio commute with all binary X and Z:
commutation with Z makes it diagonal, and commutation with X makes it scalar.
The nonzero anchor fixes that scalar to one. This covers global phase as well
as address action. An extra-$i$ control specifically fails the anchor check.

An additional elimination computes the requested B-block rank, and separately
enumerated monomial maps agree with the checker's maps. These are 53 new-map
certificates; the historical 1,245-class native census is inherited, not
reexecuted. The common rank-nine recipe also matches PR #3469's retained
certificate. Total new native work is 145 calls, rank mass 889, and 227,584
Gaussian pairs in the fixed 512-coordinate model.

## 4. Exactness domains and the universal implication

Put $R=\mathbb Z[i]$, $\pi=1+i$, and

$$B_9=E_9R^{512},\qquad
E_9=\begin{pmatrix}1&0\\1&\pi\end{pmatrix}^{\otimes9}.$$

The pinned [PR #3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382)
module lemmas and [PR #3416](https://github.com/CrocSwap/integer-mult-bounds/pull/3416)
covariance theorem supply the chart/native interpretation. Their admitted
monomials and native coordinate factors preserve $B_9$; on this domain the
literal signed-floor pairs equal their integral ideal pairs.

Locally, all 93 physical dirty inputs may lie in $B_9$, and all 104 Y inputs
must lie in $4B_9$. Inverse entrance charts preserve the dirty domain.
Temporary Y halves lie in $2B_9$; integer ADDs preserve $B_9$; subsequent
charts therefore have exact literal executions. The halves are exact also
for negative components.

For a common sufficient domain of the complete old and new programs, require
all 104 Y banks in $4B_9$, all 78 N banks in $2B_9$, and the other 176 public
banks in $B_9$. This stronger domain is not claimed minimal. Assign one
independent $B_9$ symbol to each normalized entrance bank, with weights
respectively four, two and one. The exact rational row interpreter checks
that every fractional ADD increment and every resulting state has integer
symbol coefficients, throughout both programs. Every private erasure has
the zero symbolic row. This induction, together with the pinned native
lemmas, proves universal literal admission and equality. It checks 128,164
final matrix entries and all 358 final frames. Weakening N100 alone fails the
increment condition at original event 312.

## 5. Finite evidence, costs and limits

The independent physical engine imports no candidate or predecessor executable.
It reconstructs charts directly, executes the serialized 1,238-operation
prefix on one dense signed fixture, checks all 227,584 completed floor pairs,
and compares all 93 dirty outputs and 104 returned Y arrays. This finite
fixture complements the universal symbolic and native arguments; it does not
replace them.

The prefix has 887 unit Gaussian ADD/SUBs, 103 field halves and 103 field
doublings. Its local native tariff is $52+93\,9^s$. For $0\le s\le1$,
concavity gives

$$r^s\ge1+(r-1)(9^s-1)/8\quad(1\le r\le9).$$

The original omitted 473 calls have rank mass 889, hence tariff at least
$421+52\,9^s$. The local improvement is therefore at least
$41(9-9^s)>0$ for $0\le s<1$, with equal mass at $s=1$.
The changed full profile nevertheless misses the selected target under the
explicit favorable complete-consumer screen in [COSTS.md](COSTS.md).

The finite engine caps input magnitude at 8,192 bits and stored work at
8,224 bits. Observed peaks concern fields after complete program operations,
not native-pair temporaries. Let $H_X$ bound X components after entering the
empty frame and $H_Y$ bound the actual unhalved Y components. The scalar-row
envelope, derived and checked in COSTS, is

$$\max\{8H_X+95H_Y,\;11H_X+64H_Y,\;12H_X+49H_Y,\;14H_X\}.$$

It is at most $103H$ for $H=\max(H_X,H_Y)$. Adapter and temporary headroom
are separate obligations. Python verification allocations do not establish
physical workspace, precision, access, all-size recursion or a fully paid bill.
Stop at this exact local interface and retain the stated consumer obstruction.
