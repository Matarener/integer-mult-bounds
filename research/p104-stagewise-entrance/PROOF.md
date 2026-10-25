# Chronological partial sums classify the exact producer entrance

Clear1nsight, with substantial OpenAI assistance. This note supplies the
mathematical derivation and an abstract reversible arithmetic schedule. Source
authentication, the actual path invoice, and replay evidence belong to the
package verifier. The inherited word and native recipes are unchanged.

## 1. The classified contract

Write $R=\mathbb Z[i]$, $\pi=1+i$,

$$
E_r=\begin{pmatrix}1&0\\1&\pi\end{pmatrix}^{\otimes r},
\qquad B_r=E_rR^{2^r}.
$$

Address bit zero is the first tensor coordinate. The actual source uses $r=9$.
The formulas below hold at every rank at which the named gate exists; the
finite reference accepts ranks at most nine.

The target is the fixed 257-event backward cone ending immediately before word
event 2025, with five targets D31, D30, D29, D28, D27 and Q7. Its 58 initial
banks are those six banks and 52 Y banks. All initial banks are required to be
in $B_9$. The D and Q values may be arbitrary dirty values in that domain.

We classify exactly the following conjunction:

1. Every quarter-ADD in this cone has a Gaussian-integral increment.
2. At every native pair in this cone, literal signed-floor execution equals the
   stated ideal complex-linear gate.
3. All six target arrays at the cut belong to $B_9$.

This is a necessary-and-sufficient description within the stated initial
domain. It is not a classification of genuinely rounded paths whose later
errors happen to cancel. It is also not a universal execution theorem for the
omitted events of the full 2025-event prefix: some of these Y banks feed other
D banks outside the cone. It neither admits the later external recipients nor
prices a physical caller.

The native covariance, including global phase, is inherited from PR #3416.
The $B_r$-automorphisms and the literal pair criterion are inherited from
PR #3382; the relevant pair calculation is recalled below. PR #3426 supplies
the five terminal group-sum condition and explicitly leaves these stagewise
conditions open. The new step is to separate those conditions into independent
chronological partial-sum coordinates and solve every actual interval.

## 2. Why the source correlations separate

The source parser binds all selected ADDs and transports to the frozen WORD
and NATIVE bytes. It checks that the five groups have sizes $3,7,7,11,24$,
that each of the 52 Y sources occurs in exactly one group and once in that
group, and that all of these ADDs have coefficient $+1/4$. There are also
five coefficient $-1$ ADDs from the initial dirty Ds into Q7, before any
Y quarter is added to those Ds.

For a group of size $m$, let $y_1,\ldots,y_m\in B_9$ be its initial Y
values in their actual read order and put

$$
p_t=\sum_{u=1}^t y_u,\qquad p_0=0.
$$

The change between $y$ and $p$ is triangular and unimodular over $R$:

$$
y_1=p_1,\qquad y_t=p_t-p_{t-1}\quad(t>1).
$$

It therefore maps $B_9^m$ bijectively to itself. The 52 partial-sum banks
are independent coordinates, not 52 simultaneous constraints on one bank.

Let $A_H$ be the actual ideal native map from the initial empty frame to the
frame of a read, with its authenticated phase. Covariance gives the physical
D value immediately after that read as

$$
A_H\left(d+\frac{p_t}{4}\right),
$$

where $d\in B_9$ is the initial dirty D value. The same expression, with the
actual composed map in place of $A_H$, holds after each subsequent complete
stage until the next read. Every transformed dirty term is Gaussian integral,
so subtracting it leaves an integrality condition on $p_t/4$ alone.

The interval includes the array immediately after the current quarter, every
literal pair stage of an intervening native, and the array immediately before
the next quarter. These endpoint requirements are necessary. They are also
sufficient for exact quarter increments: at a common read frame, subtracting
the old and new integral D states gives precisely $A_Hy_t/4$. For the first
read the old partial sum is zero. Thus no additional coupling between
successive partial-sum coordinates has been discarded.

The exact source has 47 nonterminal intervals: **32 have no D transport and
15 have exactly one rank-one D transport**. That native is its actual right
monomial wrapper, then $C_0$, then its actual left monomial wrapper. No
paired-inverse substitute or frame-name-only identification is used. The five
terminal intervals are dealt with by the final-cut condition.

## 3. Two local diagonal profiles

### 3.1 No intervening transport

Put

$$
L_0=B_r\cap4R^{2^r}.
$$

For $q=E_rc$, its unweighted Boolean Newton coefficient indexed by a subset
$S$ is $\pi^{|S|}c_S$. Boolean Möbius inversion and its inverse both have
integer entries. Consequently $q\in4R^{2^r}$ if and only if all those
Newton coefficients are divisible by $4$, equivalently by $\pi^4$.
Thus

$$
L_0=E_r\operatorname{diag}
   \left(\pi^{\max(4-|S|,0)}\right)R^{2^r}.
\tag{1}
$$

For an actual zero-transport gap at frame $H$, the allowed initial partial
sum is exactly $A_H^{-1}L_0$. This includes both interval endpoints, which
are at the same frame and have the same D value.

### 3.2 One actual rank-one transport

Let its right wrapper be $M_R$ and put $P=M_RA_H$. Monomial wrappers and
their inverses preserve $4R^{2^r}$. They also preserve $B_r$ by the
inherited source-bound theorem. The interval condition is therefore exactly

$$
q=Pp_t\in4R^{2^r},\qquad C_0q\in4R^{2^r}.
\tag{2}
$$

Split the bit-zero pairs of $q\in B_r$ as

$$
q(x,0)=f(x),\qquad q(x,1)=f(x)+\pi g(x),
\qquad f,g\in B_{r-1}.
$$

The source's ideal gate is

$$
C=\frac1\pi\begin{pmatrix}i&1\\1&i\end{pmatrix},
\qquad C(f,f+\pi g)=(f+g,f+i g).
$$

Conditions (2) are equivalent to $f,g\in4R^{2^{r-1}}$: necessity follows
by subtracting $q(x,0)=f(x)$ from $(C_0q)(x,0)=f(x)+g(x)$; sufficiency
follows directly from all four displayed values. Applying (1) separately to
the two coefficient blocks gives

$$
L_1=E_r\operatorname{diag}
 \left(\pi^{\max(4-|S\setminus\{0\}|,0)}\right)R^{2^r}.
\tag{3}
$$

The allowed initial partial sum is exactly $P^{-1}L_1$. The left wrapper
adds no further divisibility condition because it is an integral monomial
automorphism, but its endpoint and its charged execution remain in the source
word. This is why testing the quarter output alone would give a larger,
incorrect domain.

### 3.3 Terminal intervals and the literal pair

At the cut the five Ds have the actual frame
$O=[256,136,64,40,16,4,2,1]$. A D has value
$A_O(d+p_m/4)$. Since $A_O$ is a bijection on
$B_r$ and $d\in B_r$, its membership in $B_r$ is equivalent to
$p_m\in4B_r$. That condition also keeps every remaining stage of this D in
$B_r$. Q7 remains in $B_r$, since it only combines the initially admitted
dirty D/Q values before its last transport. Thus each terminal coordinate has
the profile $4E_rR^{2^r}$, independently of its final read frame.

For clarity, equality with the signed-floor pair does **not** require each
internal floor half to be an exact division. If the pair difference is
$(u,v)\in\mathbb Z^2$, ideal outputs are Gaussian integral exactly when
$u\equiv v\pmod2$. In that case

$$
\lfloor u/2\rfloor-\lfloor-v/2\rfloor=(u+v)/2,
\quad
\lfloor v/2\rfloor-\lfloor u/2\rfloor=(v-u)/2.
$$

These identities hold for positive and negative integers. They give the
literal output exactly, including the odd/odd case. If the parities differ,
the ideal pair is nonintegral and cannot equal an integer literal output.
This proves the necessity and sufficiency used above; the inverse pair has
the corresponding calculation with $i$ replaced by $-i$.

## 4. The resulting exact module

At rank nine the canonical diagonal exponents are:

| Interval | Number | Multiplicities of exponents $0,1,2,3,4$ | Index exponent |
|---|---:|---|---:|
| No transport | 32 | $382,84,36,9,1$ | 187 |
| One rank-one transport | 15 | $326,112,56,16,2$ | 280 |
| Terminal $4B_9$ | 5 | $0,0,0,0,512$ | 2048 |

Here the index is $2^e$ when the index exponent is $e$, because
$|R/(\pi^k)|=2^k$. The actual frame pullbacks are automorphisms of $B_9$,
and the partial-sum bank change is unimodular. Therefore they do not alter the
quotient type. The complete Y entrance is explicitly isomorphic, in these
coordinates, to the product of the 52 displayed diagonal modules. Its
quotient inside $B_9^{52}$ is

$$
(R/(\pi))^{4368}\oplus
(R/(\pi^2))^{1992}\oplus
(R/(\pi^3))^{528}\oplus
(R/(\pi^4))^{2622}.
$$

There are also 17,114 unrestricted Gaussian coefficient coordinates. The
total index exponent is

$$
32\cdot187+15\cdot280+5\cdot2048=20424.
$$

This adds 10,184 stagewise divisibility bits to PR #3426's terminal-only
algebraic index exponent 10,240. These are algebraic quotient counts, not a
physical storage bill or an operation lower bound. In particular, they do not
remove any ownership, precision, routing, or restoration obligation.

## 5. An explicit typed preparation and inverse

The in-place entry contract is 52 owned coefficient banks containing
independent arbitrary arrays $a_t\in R^{512}$, together with six separately
admitted dirty D/Q banks in $B_9$. The encoder touches the 52 owned banks;
it leaves those six dirty banks and all other roles unchanged. For each
partial-sum slot, form the appropriate profile:

$$
p_t=\begin{cases}
A_H^{-1}E_9D_0a_t,&\text{no transport},\\
A_H^{-1}M_R^{-1}E_9D_1a_t,&\text{one rank-one transport},\\
4E_9a_t,&\text{terminal}.
\end{cases}
$$

The terminal convention is **positive $4$**, whereas $\pi^4=-4$; the two
images agree but their coefficient fixtures have different signs. Use the
actual inverse path in reverse chronological order, not merely a matrix
having the same frame label. Then recover all Y banks by the groupwise
differences $y_t=p_t-p_{t-1}$. The five D and Q inputs retain their separate
$B_9$ contract.

Every step is bijective between its stated domains. To invert, compute the
chronological partial sums, apply the actual forward path and (for a rank-one
gap) its right wrapper, apply $E_9^{-1}$, and perform the profile's exact
Gaussian divisions. Terminal decoding divides the Newton coefficients by
positive $4$. An unavailable division rejects. It never rounds an input
into the domain.

The parameters range over the entire product $R^{512\cdot52}$, so this is
an arbitrary-parameter module construction. It is not restricted to Gaussian
multiples of the paired Y27/Y26 family in PR #3426. That family remains a
credited regression example inside the classified domain.

`classifier.py` implements the diagonal maps and the bank-coordinate change
without importing a native implementation. Its outputs are exact Python
integers and it does not mutate its inputs. The source layer separately
performs the authenticated frame maps. The functional arrays allocated by
these references are not presented as a measured in-place physical layout.

## 6. Constructive arithmetic invoice and width

One in-place $E_r$ schedule uses $r2^{r-1}$ Gaussian additions and the
same number of multiplications by $\pi$. Its inverse uses Gaussian
subtractions and exact divisions by $\pi$. Applying the diagonal one
$\pi$-step at a time costs the sum of its exponents. A terminal multiplication
by positive $4$ is implemented as two Gaussian doublings per entry.

At rank nine, preparation of all 52 profiles, before their actual frame
pullbacks, costs:

| Operation | Constructive count |
|---|---:|
| Gaussian additions in the 52 Newton encoders | 119,808 |
| Gaussian multiplications by $\pi$, including the diagonal profiles | 129,992 |
| Gaussian doublings for the five terminal profiles | 5,120 |
| Field subtractions to recover the 52 Y banks | 47 |
| Gaussian subtractions represented by those field subtractions | 24,064 |

The 47 field differences can be performed in place from the last bank to the
first within each group. Their inverse runs forward. The full preparation
also includes **all 47 nonterminal actual inverse frame paths and all 15
extra inverse right wrappers**. The source audit finds 158 native occurrences
with total rank 281 in those paths: 71,936 pair gates and 316 native wrappers,
plus the 15 extra wrappers, for 331 wrappers in total. Actual wrapper cycles,
phases, and scratch are recorded in the source-bound invoice. They are not
zero and are not included in the table.

The literal signed-floor backend uses eight real additions/subtractions and
four real floor-halves per pair, with unit phases separately counted. Counting
one Gaussian addition or $\pi$ multiplication as two real additions gives the
following complete arithmetic sum for preparation, with all frame paths:

$$
8\cdot71936+2\cdot119808+2\cdot129992
+2\cdot5120+2\cdot24064=1,133,456
$$

real additions/subtractions, together with 287,744 real floor-halves. Wrapper
movement and phase costs remain distinct invoice entries. Undo executes the
reversed paths and the exact profile inverses: its real-addition count is
1,123,216, since the 10,240 real terminal doublings become exact halvings.
It additionally has 259,984 real exact halves from Gaussian $\pi$ divisions
and 10,240 real terminal exact halves, as well as the same 287,744 native
floor-halves. These are constructive schedules, with no minimality claim.

For a finite-width interpretation, let every real and imaginary component of
every supplied coefficient have absolute value at most $H$. The exact
coefficient-to-profile component gains at rank nine are 3456, 3828, and
13,452 for the three rows of the profile table. For example, the first is

$$
\sum_{d=0}^9 {9\choose d}
  2^{\lceil\max(4,d)/2\rceil}=3456.
$$

The rank-one gain is

$$
\sum_{d=0}^8{8\choose d}
[2^{\lceil\max(4,d)/2\rceil}
+2^{\lceil(\max(4,d)+1)/2\rceil}]=3828.
$$

These are absolute row sums in real coordinates and bound intermediate
Newton-encoder states as well.

Every ideal native stage and monomial wrapper is unitary. A 512-entry array
with component bound $M$ has Euclidean norm at most $32M$, so every stage
of a frame pullback has component bound at most $32M$. Thus a nonterminal
partial sum has component bound at most $32\cdot3828H=122,496H$. Terminal
partial sums have bound $13,452H$. The bank-difference schedule has bound
$244,992H$. Separately, allowing a conservative factor five on the native
stage bound for the literal pair's difference, middle, and restore temporaries
gives the encoder-work bound $5\cdot122,496H=612,480H$.
Constant arithmetic work space and diagonal/Newton scratch also
fit this bound. This is less than $2^{20}H$.

Conversely, if an admitted prepared Y input has component bound $J$, a
partial sum has bound $24J$. Its forward path has bound $768J$, the
Newton decoder has component gain at most 32, and exact profile divisions
do not increase the component bound. A conservative decoder stored bound is
$24,576J$, with temporary bound $98,304J<2^{17}J$. A signed storage
implementation needs a sign bit in addition to these magnitude bounds.
Widths must be reserved explicitly; the Python reference supplies no fixed
width physical implementation. These are codec bounds, not admission or
width statements about an omitted caller or external recipient.

## 7. What this preparation does and does not pay for

The preparation is a bijection **from arbitrary coefficient banks to admitted
native-domain Y banks**. It does not preserve the original interpretation of
an arbitrary pre-existing Y input. A caller must supply and prove the
appropriate input/output intertwining for this changed coordinate contract.

If raw coefficient sources must remain borrowed and unchanged, one explicit
abstract schedule uses 52 owned zero banks, 52 copy ADDs, the preparation,
its inverse after the caller has returned the prepared banks, and 52 cleanup
subtractions against the unchanged sources. That final return is an input
condition to this schedule; it is not proved by a producer-only analysis.
Producing the six dirty D/Q banks from raw coefficients would separately
require six Newton encoders and their ownership/restoration contract. Allowing
arbitrary initially admitted dirty D/Q values does not declare them zero.

Actual tape routes, copy tariffs, bounded-width gate implementation, supplier
and consumer interfaces, return frames, scratch ownership and liveness, and
any displaced-work credit remain explicit obligations. This result makes a
correlated stagewise producer entrance constructive and reviewable. It does
not reopen the frozen 599/584 profile screen or certify a fully paid caller.

## 8. Lineage and limits of the new result

The frozen word is ywz65's PR #2586 word, with its existing native archive and
collector lineage. The source-bound Newton domain and gate intertwiners are
from Clear1nsight's PR #3382; the literal actual-interface analysis is from
Clear1nsight's PR #3423; exact native covariance with phase is from PR #3416.
Nick Petalas / petalas's PR #3426 establishes the ideal correlated terminal
module and a nontrivial exact literal family, and names the stagewise
classification answered here. The wider lattice and collector predecessors
retain their credit in the package source manifest.

The new universal statement is the explicit product of the two interval
profiles and five terminal profiles, transported by the actual histories and
the unimodular partial-sum change. Finite replay checks its application to
the frozen word; it is not substituted for the algebraic necessity proof.
No predecessor source, selected frontier, full-word claim, or external-port
scope is changed.

## Concurrent sharp calibration

At the submission checkpoint, Nick Petalas's independently developed
[PR #3449](https://github.com/CrocSwap/integer-mult-bounds/pull/3449),
head `5cb2ff187a27de1cbd1a37933f7228b35b15702b`, was public. It proves the
sharp $2^{280}$ module for the named $Y27=y$, $Y26=-y$ family across
events 1090, 1092, and 1129, with other sources in $4B_9$. Its Newton
exponent $\max(|S|,4+1_{0\in S})$ equals equation (3) after subtracting
$|S|$ to pass to weighted coefficient coordinates. That supplies a matching
independent calibration of the rank-one formula. Its proof was read at the
checkpoint, after this package's full module and dense receipt had been
constructed. No code, certificate, or provisional claim from it is imported.

The contribution here is the complete 58-bank entrance, all 47 independently
parameterised intermediate partial sums and five terminal sums, the actual-path
encoder/inverse, and their direct cost/width obligations. No priority over the
concurrent local result is claimed. See [COSTS.md](COSTS.md) for the explicitly
stated component-overwrite model behind the optional SWAP/phase lowering; it
is not an assertion about the repository's stricter ADD tariff.
