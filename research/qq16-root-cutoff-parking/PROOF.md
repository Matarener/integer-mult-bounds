# A global-root cutoff in the QQ16 parking recurrence

## Domain and inherited premises

Fix the historical original selected-C backend retained by QQ16 #4166,
as identified in [#4753](../qq16-nonterminal-c8-tree/README.md). Its dimension
is 73. Write **d for the positive integer global root-width descriptor**;
this is not the fixed dimension. At each selected-C node of integer width w,
the source tests `w < 73 or w**1000 < d` before stripping a remainder.
Only widths `0 <= w <= d` have a source interpretation. The recurrence below
also makes sense outside that range, without claiming source admission.

The inherited histogram and full-bank relation are

| r | 1 | 2 | 3 | 4 | 5 | 7 | 8 | 48 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| n_r | 349604 | 60192 | 62585 | 20448 | 11808 | 7 | 1152 | 4866 |

Put `N = sum n_r = 510662`, `F = 14336 Gamma`, `c_r = n_r/14336`, and
`C = sum c_r = 255331/7168`. Gamma is the same positive integer owner
multiplier throughout this fixed backend. A nonterminal node has `n_r Gamma`
children of width `r floor(w/73)`. Each child's incoming rows and complete
bank volume are the parent's divided by F. Calls are sequential; their row
quotients are reused, not consumed additively. These are cited source premises,
not a new full literal-word census or physical correctness proof.

The only priced subtrace is one current-bank volume per selected-child
park/restore pair. Ordinary/native internals, remainder leaves, other parked
roles, restore actions and candidate work are outside that quantity. In
particular the source-action floor `(2,5,5)` per parked bank bit is inherited
from #4753, not a complete park/restore invoice proved here.

## Exact cutoff and recurrence

For every integer d >= 1 define

\[
T_d=\max(73,\lceil d^{1/1000}\rceil),\qquad
H_d(w)=\begin{cases}
0,&w<T_d,\\
1+\sum_r c_r H_d(r\lfloor w/73\rfloor),&w\ge T_d.
\end{cases}
\]

For integer w, `w**1000 < d` is equivalent to
`w < ceil(d**(1/1000))`, including when d is a perfect 1000th power.
The strict inequality matters at equality. If w=73q+delta is nonterminal,
the source reaches its selected program at 73q without repeating the test.
Thus the recurrence tests the original w, and recurses on rq. Every edge
contracts by at most rho=48/73, so the recurrence is well defined.

The actual `Machine.node` computes columns=q and unused rows=R/F.
The actual `prepare_child` sets width=rq, rows=R/F, and
`after'=after+(73-r)q*spacing`; it forwards root_width unchanged. The preceding
remainder step replaces `before` by `before+delta*spacing`. Hence

\[
b=3\,\mathrm{compact\_bits}+\mathrm{front}+\mathrm{before}
  +w\,\mathrm{spacing}+\mathrm{after}+\mathrm{back}
\]

is preserved by both steps. All prefix/component/coefficient descriptors are
also preserved. Consequently the bank volume, including spectators, is
divided by F, not by a width ratio. These source statements explain the
recurrence's weights. `source_probe.py` executes these two unchanged methods
over an exact descriptor-integer interpreter; it does not execute records,
native payloads, Count arithmetic algorithms or their costs.

If the incoming bank has complete volume v, summing current-bank volume over
all selected-child parking pairs gives

\[
P_d(w,v)=N\Gamma v H_d(w).
\]

Indeed a depth-j rank path has multiplicity
`Gamma**j product(n_r)` and volume `v/F**j`. Their Gamma factors cancel
inside the path weight, but the `N Gamma` child invocations at that node
remain. For sixteen removed C8 calls per outer cover, the corresponding
quantity is `16 N Gamma**2 v H_d(8 lambda)`, when `8 lambda <= d` and all
other source premises hold. It is already part of the removed complete C8
bodies; it cannot be added a second time to a matched invoice.

## Uniform envelope

Let s be the unique number in (0,1) satisfying

\[
M(s)=\sum_r c_r(r/73)^s=1.
\]

Existence and uniqueness follow from strict decrease and
`M(0)=255331/7168 > 1`, `M(1)=1041408/1046528 < 1`.
This is exactly #4865's existing exponent, not a new root search. Its
published bracket is `0.9983245373 < s < 0.9983245374`; the present proof
needs only the defining equation and `0<s<1`.

Set `a = 3456/25` and `q_T = floor(T_d/73) >= 1`. For every w >= T_d,

\[
\boxed{\quad
\frac{((w+a)/(T_d-1+a))^s-1}{C-1}
\le H_d(w)\le
\frac{(w/q_T)^s-1}{C-1}.
\quad}
\]

The proof uses Nick Petalas's #4865 weighted-leaf argument with the cutoff
kept as a parameter. To make the extension's dependence explicit, let L be
the total terminal-leaf weight in the finite rank tree. Replacing one
frontier vertex by its children multiplies that vertex's weight by C.
Telescoping gives `L=1+(C-1)H_d(w)`. Every terminal leaf below a nonterminal
root has width in `[floor(T_d/73), T_d-1]`.

For phi(x)=x^s, at an internal width w=73q+delta,
`sum c_r phi(rq)=(73q)^s <= phi(w)`. Telescoping implies
`q_T^s L <= w^s`, giving the upper bound. For psi(x)=(x+a)^s,

\[
a\ge\max_{r,0\le\delta\le72}\frac{r\delta}{73-r}
 =\frac{48\cdot72}{25},\qquad
rq+a\ge(r/73)(w+a).
\]

Thus `sum c_r psi(rq) >= psi(w)`. Terminal widths are at most T_d-1,
so `(T_d-1+a)^s L >= (w+a)^s`, giving the lower bound. The potential
functions and sharp per-edge affine shift are predecessor work; retaining
the moving cutoff and applying the result to changing d is the new scope.

The constants can also be made uniform simultaneously in both parameters.
Put `A=1+a/73=5281/1825` and `X=(w/T_d)^s`. Since
`T_d-1+a <= A*T_d` and `floor(T_d/73) >= T_d/146`, the envelope and H>=1 give

\[
\frac{X}{C A^s}\le H_d(w)\le\frac{146^s}{C-1}X
\quad (w\ge T_d).
\]

For the lower bound combine `H>=1` with
`H>=(X/A^s-1)/(C-1)`: the first suffices when X<=C A^s and the second when
X>=C A^s. Thus `H_d(w)=Theta((w/T_d)^s)` uniformly over the whole nonterminal
domain, with constants independent of d and w. There is no positive estimate
of this form for terminal widths, where H=0.

## The diagonal recurrence and a growing root descriptor

At w=d, let t=d^(1/1000). For t>=a, `T_d=ceil(t)`,
`T_d-1+a <= 2t`, and `floor(T_d/73) >= T_d/146 >= t/146`.
The latter inequality follows from `floor(x)>=x/2` for x>=1. Therefore

\[
\frac{(d^{999/1000}/2)^s-1}{C-1}
\le H_d(d)\le
\frac{(146d^{999/1000})^s-1}{C-1},
\qquad H_d(d)=\Theta(d^{999s/1000}).
\]

The implicit constants are independent of d. The same exponent applies
conditionally to any family with `epsilon*d <= w(d) <= d`, for fixed
epsilon>0. For other width families use the explicit envelope. Multiplying
the predecessor's bracket by 999/1000 gives the inherited numerical interval
`0.9973262127627 < 999s/1000 < 0.9973262128626`; it is not newly certified
numerical root information.

This is a diagonal statement about a two-parameter recurrence. It neither
constructs an admitted RootPlan with w=d nor treats physical volume v as
constant while d grows. The full physical term has the extra factor
`N Gamma v(d)`. It does not follow that total runtime has this exponent.
The earlier fixed-cutoff `Theta(w^s)` remains correct on its stated domain.

## Exact selected-C row-division depth

Define

\[
D_d(w)=0\ (w<T_d),\qquad
D_d(w)=1+D_d(48\lfloor w/73\rfloor)\ (w\ge T_d).
\]

This is the exact maximum number of nonterminal selected-C nodes on a path,
including the incoming node if nonterminal. Strong induction shows that D
is nondecreasing in w: the threshold case is immediate and the child map is
nondecreasing with argument strictly below w. Hence among all ranks the
maximum descendant depth is attained by rank 48, which has positive
multiplicity. This proves the recurrence from the complete tree.

An equivalent inverse characterization checks the depth without expanding
any tree. Let `B_1=T_d` and

\[
B_{j+1}=73\left\lceil B_j/48\right\rceil.
\]

Then `D_d(w)>=j` if and only if `w>=B_j`. The base case is the source cutoff.
Inductively, another internal level requires
`48 floor(w/73)>=B_j`, exactly equivalent to the displayed ceiling threshold.
These thresholds increase strictly. The source's pre-remainder test is why
`B_1` is T_d, not the next multiple of 73. For T_d=356, the first three
thresholds are 356, 584 and 949. The verifier checks this inverse oracle
against all finite DP depths and the giant historical maximum path.

For a positive integer incoming row count R, every selected-C row division
in this reached tree is positive and exact **if and only if**

\[
F^{D_d(w)}\mid R.
\]

Sufficiency follows since a depth-j node receives R/F^j and no path has more
than D internal nodes. Necessity follows on an attained longest path: its D
successive exact divisions imply divisibility by F^D. In particular the
smallest positive row count for this arithmetic contract is F^D. This is
not a minimum for all supplier stock or native/Ordinary internals. Sequential
sibling invocations reuse the same quotient; the total child count does not
create an additional stock power.

There are explicit depth estimates. With rho=48/73 and a=3456/25, for w>=T_d,

\[
\left\lceil\frac{\log((w+a)/(T_d-1+a))}{\log(73/48)}\right\rceil
\le D_d(w)\le
1+\left\lfloor\frac{\log(w/T_d)}{\log(73/48)}\right\rfloor.
\]

Along the maximum path, `w_j <= rho^j w` and
`w_j+a >= rho^j(w+a)`. The first terminal width is at most T_d-1;
the last internal width is at least T_d. Substituting these two facts gives
the displayed inequalities, with the strict threshold explaining the upper
`1+floor`. The checker verifies their integral equivalents, using powers
of 48 and 73, without floating-point logs.

Consequently

\[
D_d(d)=\frac{999}{1000}\frac{\log d}{\log(73/48)}+O(1).
\]

For fixed F, the arithmetic row minimum therefore satisfies
`F**D_d(d) = Theta_F(d**((999/1000)*log(F)/log(73/48)))`.
For variable F use the exact power; the constants in `Theta_F` are not
asserted uniform in F. This is a row-divisibility statement, not an installed
storage improvement.

In #4753's historical descriptor `d=isqrt(2**16949)`, exact integer iteration
gives T_d=356 and D_d(d)=13997, ending at width 240. The cutoff-free
recurrence with T=73 gives 13999, ending at 48. The original conservative
RootPlan and its stock remain unchanged. Replacing its depth needs its own
root-layout, padding, all-caller and admission argument.

## Boundary of the result

No matched D* versus B* sign is established. All retained later calls,
candidate-only nonchild/shell/control work and the exact return credits must
still appear in that comparison. Lower bounds on both sides do not compare
their difference. No new recursive invoice is proposed, so the signed
invoice preflight is not an admission substitute or a claimed improvement.

Source histogram/physical correctness, actual RootPlan admissibility, stock
construction, numerical precision, restoration, native/Ordinary implementations
and the selected framework assumptions remain inherited or unchecked. The
finite checker corroborates the written proof and its source descriptor
boundary; it is not a proof-assistant derivation or production execution.
