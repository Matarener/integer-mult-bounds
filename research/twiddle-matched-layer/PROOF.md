# A matched chunk layout for the actual-width T74 synthetic caller

## Result and boundary

This is a source-relative, changed outer-layout proposal and an independent
interface audit. It does not implement the diagonal pass claimed by Sagar
Thakrar in Discussion 2612 comment 19015185, execute a production T74 object,
or certify a new multiplication exponent.

There is a concrete mismatch between the conservative outer caller and the
new actual-width root. The caller chooses

\[
d=\lfloor p^{1/40}\rfloor,\qquad K_d=\lfloor d^{1/500}\rfloor,
\]

and each common synthetic round selects exactly \(g=d-1\) bits. PR3599's
literal planner instead chooses \(K_g=\lfloor g^{1/500}\rfloor\).
These widths disagree at every \(d=k^{500}\), \(k\ge2\). The unchanged
outer wrapper also requires a different planner constructor. A substitution
based only on the normalized tensor endpoint is therefore insufficient.

Replace the outer named-slot layout's chunk width by \(K=K_g\), retain its
explicit positional permutation and inverse, and use a wrapper whose
admission is the actual-width root's admission. This makes every common
round a complete, correctly positioned PR3599 input. It requires no new
arbitrary-support router. The source layout bounds and their exponents
survive. The source's long records satisfy the newer root's record condition;
the disk-grid invariant guarantees every signed negation required by PR3611.

Conditional on a complete paid diagonal/caller adapter with the lifecycle
specified below, the resulting forward/opposite transform has the same
normalization, error and asymptotic outer routing bottleneck. The public
single-record producer/consumer results alone do not establish that lifecycle.

## 1. Exact sources and inherited premises

The frozen canonical base is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` (priority revision 6).

| Source | Exact head or canonical path | Used implication |
|---|---|---|
| Jose Manuel, PR2298 | canonical `research/selected-conservative-outer/PROOF.md` | Outer dimension/record bands, exact-K positional caller, analytic and cost premises |
| Nick Petalas, PR3493 | `c0ee30f63a89c3bd0eabb3ea7eaa7786d5ad707f` | Actual MSB/LSB wrapper, complete cardinality, consumed-output gate, smaller-dimension caller |
| Jose Manuel, PR3599 | `72df81b8cee17ffd990fc18b2d54024f65971556` | Actual selected-width plan, complete normalized root, retained physical premises and cost |
| Nick Petalas, PR3593 | `46c04613a19a5b7bd50d98e50bbc8ea8dc6275b0` | Encoded named-slot exponent, descriptor and declared tape-action tariff |
| Sagar Thakrar, PR3611 | `c21172062a2d907804538aa5a74012a2a4cc144e` | One encoded header to one exact signed Gaussian packet |
| Retained transform source | canonical `upstream/build/sections/06-transforms.tex` | Named slots, positional layout, grouped rounds, frequency order, one truncation per round |

PR3576 at `1630afea0fc1083717b5b2799b8de7a819a6ea02` retunes the
older root and stopping rule but explicitly retains the older dimension law.
PR3553 at `d5ea38a0a613e721d828ef072379d7101d770cd6` is a logical
ordinary-selector composition, not a replacement physical synthetic caller.
Neither removes the present literal layout/constructor mismatch.

The normalized T74 theorem remains conditional on the cited native,
ordinary/C0, common-label, hosting, coefficient-height and physical-refinement
premises. This audit does not replay the 2,394,506-child certificate or upgrade
any source's review status. The original transform and analytic arguments
remain credited to their sources, including Douglas Colkitt, Nussbaumer and
Quandalle, Harvey and van der Hoeven, Philipp, and the retained contributor
lineage. PR3599 also credits Hiroki Kumazaki's PR3576. The new result is the
specific joined contract, its floor-boundary obstruction and matched repair.

## 2. The floor obstruction is literal

For integer \(k\ge2\), if \(d=k^{500}\), then

\[
\lfloor d^{1/500}\rfloor=k,
\qquad
\lfloor(d-1)^{1/500}\rfloor=k-1.
\]

Conversely, for integer \(d\ge2\), the two floors differ only at such
perfect powers. Indeed the integers between consecutive 500th powers share
the same floor, and subtracting one crosses a boundary only at a power.
Thus this is an infinite family of actual caller parameters, not a numerical
rounding accident.

For arbitrary integer precision, the old threshold \(K_d\ge k\) is exactly \(p\ge k^{20000}\).
The repaired threshold \(K_g\ge k\) is exactly

\[
p\ge(k^{500}+1)^{40}.
\]

For \(k=2\), these are respectively \(2^{20000}\) and
\((2^{500}+1)^{40}\). The actual PR2298 choice p=6b further restricts
p to multiples of six: replace either threshold X by \(6\lceil X/6\rceil\).
For k=2 these are \(2^{20000}+2\) and \((2^{500}+1)^{40}+5\).
Each perfect-power dimension interval contains such admitted multiples,
so this restriction does not remove the mismatch family.
A huge threshold is not a refutation of an
asymptotic theorem. It matters here because the API computes these floors;
one cannot equate them by asymptotic notation.

In PR3599 `active_plan.py`, `d` is copied from the selected count and `K`
is computed from that value. Its full Gaussian count is

\[
\text{outer_rows}\;2^{\text{left}+gK+\text{right}}r.
\]

Passing the old left/right fields with a smaller internally computed K
changes the complete expected payload extent by a factor
\(2^{g(K_d-K_g)}\). Enlarging the left field to conceal the extent mismatch
does not repair the endpoint: at offset zero and right field zero the
selected bit sets become \(\{0,K_d,\ldots,(g-1)K_d\}\) and
\(\{0,K_g,\ldots,(g-1)K_g\}\). Their Walsh tensors differ.

A small exact calibration replaces the fixed exponent 1/500 by 1/2:
\(d=4,g=3,K_d=2,K_g=1\). A delta input at address zero has an output
at address two under the latter tensor and none under the former. This
scaled-exponent fixture checks the structural failure; it is not a finite
execution at the enormous production floor boundary. The checker separately
validates the exact production integer-power inequalities.

## 3. Matched layout and all round cases

Assume the outer caller's nontrivial range \(d\ge2\), and put
\(g=d-1\). There are g polynomial-record axes. Each is long, with
\(\ell\) named bits, or short, with \(\ell-1\) named bits. Let a be
the number of long axes and let A be their total number of record bits.
The number of complete polynomial records is \(M=2^A\), and
\(T=rM\), \(r=2^\ell\). No coefficient suffix or spectator is omitted.

Set \(K=\lfloor g^{1/500}\rfloor\),
\(b=(\ell-1)\bmod K\), and \(q=\lfloor(\ell-1)/K\rfloor\).
Use the source's positional construction with this K:

1. Move the long top slots to a prefix in axis order.
2. Append each of the low named planes \(b-1,\ldots,0\), in that order
   and in axis order within a plane.
3. Transpose the remaining equal K-bit chunks from axis-major to chunk-major
   order, preserving the bit order inside every chunk.

Call this permutation L. It preserves the complete polynomial suffix. It
has the same explicit inverse as the retained construction, with its own
recorded positions; do not reuse an old-K inverse descriptor.

For each common round \(\ell-2\ge h\ge b\), set

\[
j=\left\lfloor\frac{\ell-2-h}{K}\right\rfloor,
\quad \rho=(h-b)\bmod K,
\quad n_P=a+gb+jgK,
\quad n_S=(q-j-1)gK.
\]

The selected named bits occupy exactly
\(n_S+\rho+tK\), \(0\le t<g\), numbered from the right. All record
addresses occur, and

\[
n_P+gK+n_S=A,\qquad 2^{n_P}\,2^{gK}\,2^{n_S}=M.
\]

The actual root descriptors are `selected=g`, `left=n_P`, `right=n_S`,
`coefficients=r`, `outer_rows=1`, `residue=rho`, and `precision=p`.
The left/right descriptors count bits; passing the cardinalities
\(P=2^{n_P}\), \(S=2^{n_S}\) in those fields would be another error.
The root selects all g current axes at the intended offset and fixes every
unselected bit, preceding/following field, row and coefficient index.

There are exactly \(qK=\ell-1-b\) common calls. The top round exists
only if \(a>0\) and acts on a axes. The b bottom rounds act on g axes.
Keep the source's elementary prefix implementation for these rounds;
do not invoke a smaller actual-width root against a g-chunk header.
They require \(a+gb\) individual butterfly sweeps. There are
\(R=\ell-1+\mathbf1_{a>0}\) complete rounds in total. At h=0 the
twiddle is the identity. Counting a diagonal there is a harmless charged
upper bound; this audit claims no implementation that removes it.

The cases \(a=0\), \(a=1\), and \(a=g\) respectively include no top
round, a singleton top round, and a fully participating top round. If g=1,
K=1 and every common root is the source's singleton/fallback case. If d=1,
there are no record axes: use the outer finite-range/identity case instead
of evaluating \(\lfloor0^{1/500}\rfloor\) as a legal chunk width. The
opposite transform uses exactly the reversed round order and the inverse
twiddle before each butterfly. These rules cover both ends of the schedule.

## 4. Parameter and budget compatibility

For \(d\ge2\), \(g\ge d/2\). Since \(\lfloor x\rfloor\ge x/2\)
for \(x\ge1\),

\[
2^{-1-1/500}d^{1/500}\le K\le d^{1/500}.
\]

Thus K retains the required growth and logarithmic absorption. The outer
source's bands include

\[
\frac{p}{12d}\le\ell\le\frac{p}{3d},\qquad
d\ell\le p/3,\qquad p\ge2^{40}.
\]

They imply \(K\le\ell-1\): \(K\le d\), while
\(\ell\ge d^{39}/12\ge d+1\) for \(d\ge2\).
In particular K is also smaller than r. The full address and descriptor
length bounds remain O(p); changing the computed chunk positions adds no
advice tape or unbounded number of roles.

The active width satisfies \(1\le g\le\lfloor p^{.997}\rfloor\).
The older source long-record band implies PR3599's newer condition with
fixed constants b=B=1:

\[
\log_2r=\ell\ge\frac{p^{39/40}}{12}
\ge(\log_2p)^2,\qquad \log_2r\le p.
\]

For the middle inequality put \(t=\lfloor\log_2p\rfloor\ge40\).
It suffices that \(2^{39t/40}\ge12(t+1)^2\). At t=40,
\(2^{39}>12\cdot41^2\). Raising consecutive-step comparisons to the
40th power proves monotonicity because
\(2^{39}>((t+2)/(t+1))^{80}\) for t>=40. All comparisons can be
checked with integers. This proof uses actual complete coefficient records;
it does not replace record count by a label or a declaration.

The prefix and movement costs are still charged. At most \(g(b+1)\)
single-bit moves and \(gq-1\) chunk exchanges give

\[
O\bigl(V[gK+pK^{\tau-1}]\bigr),
\qquad \tau=99830289/10^8,
\]

including the inverse layout when needed. In the negative power term the
*lower* bound on K is essential:

\[
K^{\tau-1}\le
2^{(1+1/500)(1-\tau)}d^{(\tau-1)/500}.
\]

The prefactor is fixed. This audit retains the old outer ordinary
interchange contract; PR3599's internal ordinary retuning is not silently
substituted into the independent outer movement term.

With \(\alpha=99827101/10^8\), the common roots cost
\(O(V(\ell-1-b)g^\alpha\log p)\). Their MSB/LSB conversions add
O(V) per common call under the retained bridge theorem. The complete
conditional transform cost, once the paid diagonal/caller condition in
Section 6 holds, is therefore

\[
O\left(Tp\left[dK+pK^{\tau-1}+\ell g^\alpha\log p\right]\right).
\]

The logarithm stays explicit until compared against an outer power gap.
The new common-round power saving is
\((1-\alpha)/40=172899/4000000000\). The exact-K movement saving
remains \(169711/2000000000000\), much smaller. Changing only the
root and this layout therefore does not improve that inherited bottleneck
or establish a new integer exponent.

## 5. Complete-round numerical admission and formats

At a legal caller entrance each Gaussian coefficient is in the closed
unit disk and each real/imaginary part is on the p-grid. Its integer
numerators lie in \([-2^p,2^p]\). The source width is w=p+2, so the
sole signed value whose negative is unrepresentable is \(-2^{p+1}\),
strictly outside that set. Every sign change requested by PR3611 is
therefore admitted. PR3611 already states the one-packet w=p+2 implication;
the added implication here is its preservation through every complete
actual-root, prefix and opposite round. It is not a claim based on the
tested packets or a new local signed-negation result.

Every completed \(H_0^{\otimes g}\) is a contraction in maximum
coefficient norm; truncating each component toward zero preserves the
disk and returns the p-grid. A monomial \(J_E\) is an exact signed
coefficient permutation, so it preserves the disk, grid and width. It
commutes with Q_p because truncation toward zero is odd. Consequently

\[
J_EQ_p(\mathcal H z)=Q_p(J_E\mathcal H z),
\qquad
Q_p(\mathcal H J_E^{-1}z)
\]

are the forward and opposite completed rounds. For prefix rounds, all
elementary factors are evaluated exactly before that single Q_p; applying
Q_p immediately before J_E gives the same output and allows the diagonal
to use w=p+2 rather than the temporary p+s grid. There is no truncation
between the individual prefix factors. Intermediate root or pair-update
values need their retained guard; they are not declared disk values.

Induction proves signed-negation admission, disk/grid return and one error
increment below \(\sqrt2\,2^{-p}\) at every complete round. After R
rounds the error is below \(\sqrt2 R2^{-p}\le\sqrt2\ell2^{-p}\).
The exact forward and opposite operators are respectively
\(LB F^-\) and \(F^+B^{-1}L^{-1}\). The bit-reversed frequency order
B remains part of the endpoint. Using the same new L for both operands
allows their pointwise product in that order; the opposite consumes it.

PR3599 returns LSB-first components; PR3611 consumes framed MSB-first
components. Nick Petalas's complete WordOrderBridge proves value-preserving
linear-cost conversion, but his `OuterLayer.__init__` requires
`root.plan.dimension_exponent == (1,40)`. The active-width plan derives its
dimension from the selected count. A new wrapper must validate that actual
contract and use its computed complete cardinality. Calling the old wrapper
unchanged is not established. Framing a full cube into packet records and
returning it to the root's sentinel/descriptor vocabulary is also a physical
adapter obligation, not an algebraic consequence of equal word widths.

## 6. A positive paid-join criterion and remaining bill

Let Q be the complete extra tariff for address enumeration, packet framing,
cube extraction/assembly, descriptor updates between rounds, output
consumption/clearing, role reuse and all head returns. It is unknown for the
joined published artifacts, and is not assigned zero. The new active claim
19015185 covers a fixed-h diagonal pass; its result and any later caller
interface must be checked before treating Q as paid.

For one shape, define
\(M_0=A+\ell+1\) and
\(N_h=\ell+K+h+g+6\). The source's declared tape read/write/move and
data-gate producer tariff is bounded by
\(5000M_0^2(N_h+4)\). It is not a precise count of every finite-control
transition; a fixed transition-lowering factor must be retained separately.
The complete packet consumer tariff is bounded by
\(256(2rw+\ell+w+1)\).

Invoking both modules once per record per complete round therefore has
the constructive declared-tariff bound

\[
\begin{aligned}
T_{\rm pc}\le {}&5000M M_0^2
\left[R(\ell+K+g+10)
+\frac{(\ell-2)(\ell-1)}2
+\mathbf1_{a>0}(\ell-1)\right]\\
&+256MR(2rw+\ell+w+1).
\end{aligned}
\]

This counts even the identity h=0 call; it does not charge the producer a
second time after shared header/descriptor accesses by the consumer. Source
volume and all complete-record calls are explicit. The outer caller has
\(A+\ell=\log_2T\le p/6\); thus M_0=O(p), N_h=O(p), and
\(T_{\rm pc}=O(MR(p^3+rp))\). With the proved long-record inequality,
\(p^2/r\le1\) for p>=2^40, so this is O(MRrp)=O(RV).
An exact bound for a proposed finite constant allowance B per rp record is
obtained by retaining the displayed tariffs, the finite-control factor and
the actual Q, rather than dropping any of them.

A sufficient full caller condition is a fixed finite-tape diagonal
implementation, uniform over the round descriptors, with

\[
Q\le C\,MR(rw+A+p^3)+\operatorname{poly}(p)
\]

for a fixed C, complete same-order disk-grid output, preserved borrowed
input and descriptors, and canonical returned heads. It must clear or
consume each previous owned output before reuse, restore its private roles,
and retain only a fixed number of complete cube buffers across rounds.
Under this condition the same long records pay Q, including its arbitrary
fixed-degree polynomial setup term: \(r\ge2^{(\log_2p)^2}\) dominates
every fixed power of p. The complete transform bound in Section 4 follows.
This is a positive conditional composition
criterion, not a claim that the unpublished diagonal or active-root wrapper
already satisfies it.

| Item | Status in this audit |
|---|---|
| Exact chunk floor, extent and selected-bit mismatch | Proved; bounded controls |
| Matched complete-address layout and all round cases | Proved; bounded complete-cube arithmetic checks |
| Root dimension and long-record admission | Proved implication from the retained outer bands |
| Signed packet admission and completed-round error | Proved from source disk-grid contracts |
| New-root asymptotic tariff and native/hosting/height | Inherited source-relative theorem; no production replay |
| Component-order conversion | Retained constructive O(V) bridge; active-wrapper integration unimplemented |
| One-record encoded producer/consumer tariff | Retained written bounds; limited actual-interface corroboration |
| Owned full-array diagonal, framing, reuse and all-round control | Required positive criterion; not established by this audit |
| Precise combined tape count, arbitrary dirty private entry and production widths | Unestablished; no zero charge or practical cutoff claim |
| Full analytic/packing/multiplier adoption and selected improvement | Outside this result |

## 7. Finite evidence and stopping decision

The checker uses exact integers/rationals, directly reconstructs the named
layout, and compares complete small Gaussian cubes for every common/prefix
round, both directions and singleton/all-short/mixed/all-long cases. Its
normalized butterfly is an arithmetic oracle, not a physical T74 execution.
It checks the production floor thresholds with exact large
integers. A scaled-c case exposes both the extent failure and the wrong
selected-bit endpoint if the extent is concealed. Other controls reject a
changed offset, old inverse layout, wrong inverse-round order, floor rounding
in place of truncation toward zero, and an undersized signed format.

The ten geometries produce 50 complete-round comparisons. Two additional
calls execute the unchanged PR3593 and PR3611 modules on a nonzero packet
returned by the repaired layout's arithmetic H oracle. The actual address
36 in the three-short-axis ell=3 example emits residues 12 and 4 with K=1;
interpreting those same physical bits under old K=2 emits zero instead.
The opposite packet returns exactly. Success tariffs independently reconcile
against all actual tape counters without double-counting shared header work.
The unchanged consumer rejects a second call with `one-shot consumer`, even
after its successful private cleanup. Both source ell=33 admission controls
reject before large allocation. These checks do not execute a full-array
diagonal pass, a physical root, or a new rearming implementation.

The PR3593/3611 executables cap ell at 32. In the actual nontrivial PR2298
domain, the source bands imply
\(\ell\ge2^{39}/12\), hence integer ell>=45,812,984,491.
Thus their small replay fixtures do not execute a legal nontrivial outer
instance. They test interfaces; the unbounded statements remain written,
source-relative arguments. This incompatibility of finite caps is not a
counterexample to those arguments and is not repaired by omitting a guard.

Continue the bounded layer interface audit and hand the matched descriptor,
wrapper and paid lifecycle criterion to the diagonal author. Do not duplicate
that pass, execute an enormous root, or optimize header counts before the
required full-array result is available. The route is mathematically
compatible and closes concrete admission implications, but production
integration remains conditional and the inherited exact-K outer bottleneck
still controls the exponent. A new full caller implementation, a paid
different movement law, or independently admitted production sources is the
appropriate reopening evidence.
