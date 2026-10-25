# Incoming height at the mixed-provider Gaussian call

I audit the exact-grid implication in Cinna Davis's PR4100,
`337d04939571a637aeab54a0f58f54fde811663a`, against the four PR4088
providers at `72d7efc181edb21806a878f174847c96dd410ab0`.
I retain the sources through main
`12fa8c5c844be21bfefb38a19503fbd867a11244`.
I use AAAmirinu's earlier primitive-prefix and exact-shift analysis of
PR2287, including its credit to Gareth Davidson's Horner analysis.

## 1. The quantified interface

In `unconditional-batched-crt/COMPLEX.md:153–167`, the author calls an
incoming array height \(t\) if its entries belong to
\(2^{-(P+t)}\mathbb Z[i]\) and have modulus at most \(2^t\).
The author defines \(A(h)\) as **additional** internal height. At line169
the author allocates \(P+\lceil Ch\rceil\) fractional bits and
\(\lceil Ch\rceil+O(1)\) integer/sign bits, without an incoming-height term.
That allocation suffices under a root-height-zero restriction. I find
no such restriction or per-call normalization at the Gaussian interface.

For any integers \(P\ge0,h\ge1,k\ge0\), set \(t_0=k+1\) and
\[
 x_j=2^{-(P+t_0)}\quad(0\le j<2^h).
\]
These entries meet the height-\(t_0\) contract. For
\[
 C=\tfrac12\begin{pmatrix}1+i&1-i\\1-i&1+i\end{pmatrix},
\]
both row sums equal one. Thus \(C^{\otimes h}x=x\), and the inverse
has the same constant-vector property. Multiplying an input or output
entry by \(2^{P+k}\) gives \(1/2\). No exact representation on that
stated grid exists. Take \(k=Bh\) for any proposed fixed integer reserve
constant \(B\). Even with \(h=\lfloor p^\beta\rfloor\), \(\beta<1\),
the witness has \(t_0=o(p)\).

For integer headroom, fix any proposed additive constant \(b\). A constant
input \(2^{Bh+b}\) meets its own incoming-height contract and exceeds
the positive range of a signed \(Bh+b\)-bit integer field. The same
constant-vector argument preserves that value at the endpoint.

These are examples at the stated supplier interface. I have not exhibited
them along an actual Gaussian execution. They establish a missing
incoming-height restriction or term, and do not disprove the proposed
multiplication exponent.

## 2. Primitive reserve and completed children

For the rest of this proof use \(B\) for a reserve constant and retain
\(C\) for the matrix. Assume integral \(P,t\ge0\). For a reduced real
dyadic \(q=n/2^d\), put
\[
 k(q)=d+\lceil\log_2(1+|n|)\rceil
     =d+\operatorname{bitlength}(|n|).
\]
Implement a scalar product by signed Horner additions, and a scalar ADD
by forming \(2^d x+n y\), followed by exact division by \(2^d\).
The Horner prefixes have magnitude at most \(|n|2^t\).
The ADD numerator has magnitude at most
\[
 (2^d+|n|)2^t\le 2^{t+k(q)}.
\]
Its partial sums obey the same bound. Both endpoints have denominators
dividing \(2^{P+t+d}\), hence height at most \(t+k(q)\).
I use this conservative charge for both operations. I assign zero
additional height to COPY and CLEAR.

For one elementary \(C\) or inverse-\(C\) pair, the numerator
\((1+i)a+(1-i)b\), or its conjugate-sign counterpart, has modulus at most
\(2\sqrt2\,2^t<2^{t+2}\). Each completed output has modulus at most
\(\sqrt2\,2^t<2^{t+1}\) and needs at most one more denominator bit.
Executing \(e\) coordinate pairs in sequence therefore needs at most
\(e+1\) additional prefix height; each completed endpoint needs at most
\(e\). AAAmirinu proved the corresponding actual signed-word prefix
conditions in `complex-grid-prefix-audit/PROOF.md`.

The same endpoint bound applies to a completed \(C^{\otimes u}\) child.
Reset its *mathematical* height allowance to at most the entry height
plus \(u\) only after it returns. Retain its full internal reserve while
it runs. This use of completed-child cancellation changes divisibility
information, not the stored grid or numerical value.

## 3. The actual eight emitted programs

I reconstruct the construction fields of each canonical word from its
original THREE/FOUR, base/extra input using the authenticated construction
prefix of `bw_transport.run`. I compare those fields with the retained
canonical artifact. The three later fields `local_profile`, `edges` and
`warp_edges` remain separate: I bind the first to the original report and
check the emitted climb/center profile; I do not rerun the source's full
free-algebra or native-edge checks.

I execute seven unchanged definitions from the authenticated `bw_emit.py`:
`basis`, `reg`, `dual`, `scalar`, `lregs`, `expand`, `emit`. I exclude its
top-level CLI and output writes. I compile the extracted definitions with
assertions enabled in both ordinary and optimized audit runs. For each
canonical word I emit forward and backward programs, compare the complete
program digest and event counts with the retained receipts, then sum
\(k(q)\) over **all** scalar ADD/SCALE events.

| Provider, both base/extra | Forward height sum | Backward height sum | Events per direction |
|---|---:|---:|---:|
| THREE | 30,341 | 30,349 | 22,807 |
| FOUR | 30,333 | 30,341 | 22,808 |

The backward program replaces eight center COPY operations with eight
coefficient-\(-1\) flush ADDs. The sum includes zero-frame correction
expansion, preconditions, compensation, A/B phases, restoration tail and
full-frame cleanup. Negative stored denominators undergo fraction
reduction before classification. The maximum division shift is three.
I use \(L=30{,}349\) as a common bound across all eight programs.

The native sources serialize a monomial wrapper as a binary affine
permutation and a Gaussian-unit phase, with denominator exponent zero:
`clifford_exact.monomial`, `bw_gauss.apply_mono` and the recipe serializer
give the explicit convention. Its tensor lift acts as
\[
 |x_1,\ldots,x_f\rangle\longmapsto
 i^{fa+\sum_j q(x_j)}
 |Gx_1+b,\ldots,Gx_f+b\rangle .
\]
It preserves magnitude and the dyadic grid. Inverse and dual wrappers
have the same property. A fused native transition consists of its right
monomial, one \(C^{\otimes rf}\) child and its left monomial.

I condition this arithmetic argument on the claimed native factorizations
and lifted endpoints, including residual adapters. I read and pin their
source contracts; this census does not reprove their column identities,
free-algebra cancellations, or physical realization.

## 4. A complete conservative recurrence

Use the author's
\[
 \Gamma=2^{1296}\prod_{i=1}^{36}(2^{2i}-1),\qquad W=322{,}560.
\]
From the complete retained histogram, the sum of child ranks is
\[
 \sum_r rH_r=23{,}431{,}680=65{,}088\cdot360.
\]
The actual schedule has 3,240 local calls. It also has nine bridge
instructions per replica/port, each implemented by two signed unit ADDs
in `full_operator.normalize`. Across 360 replicas and 112 ports this
gives \(9\cdot2\cdot360\cdot112=725{,}760\) ADDs per cover.
Each unit ADD has \(k(1)=k(-1)=1\).
I count the whole cover in the height reserve:
\[
 S=23{,}431{,}680\Gamma,\qquad
 E=(3240L+725{,}760)\Gamma+73
   =99{,}056{,}520\Gamma+73.
\]
I do not divide these height bounds by \(W\Gamma\), the payload factor
in the separate time recurrence. Overcounting disjoint rows still gives
a valid global maximum-height reserve.

For the remainder \(r=e-73\lfloor e/73\rfloor<73\), choose the elementary
coordinate schedule from section2. Its prefix height is at most
\(r+1\le73\) when \(r>0\), and zero for \(r=0\). This operation covers
the complete array; it does not add another factor \(W\) or \(\Gamma\).

Let \(A(e)\) bound additional height over arbitrary correlated input
entries, including borrowed dirty values. Suppose a nonleaf call uses
\(f=\lfloor e/73\rfloor\) and children of widths \(rf\), \(1\le r\le48\).
At a prefix, charge all scalar work by \(E\), all completed child widths
by \(Sf\), and the one unfinished child's internal reserve separately.
Then
\[
 A(e)\le\max_{1\le r\le48}A(rf)+Sf+E.
\]
Choose
\[
 B=\max\!\left(2,\left\lceil\frac{S+E}{25}\right\rceil\right).
\]
For a leaf of any positive width, the elementary schedule gives
\(A(e)\le e+1\le2e\le Be\). This includes the author's growing
\(h^\eta\) stopping threshold. For an internal node every child width
is smaller than \(e\), and strong induction gives
\[
 A(e)\le48Bf+Sf+E
       \le(48B+S+E)f
       \le73Bf\le Be,
\]
using \(f\ge1\). No monotonicity assumption on \(A\) is needed.
Define \(A(0)=0\).

The checker computes this explicit \(B\), an integer of 2,650 bits.
I use its existence and value for a uniform asymptotic reserve; I do
not claim a practical working-precision constant.

## 5. Corrected grid, exact shifts and the raw-H caller

At root width \(h\) and incoming height \(t_0\), allocate once
\[
 F=P+t_0+Bh,\qquad I=t_0+Bh+2,
\]
where \(F\) counts fractional bits and \(I\) includes sign/headroom.
Represent real and imaginary components as signed \(F+I\)-bit integers
at scale \(2^{-F}\). The preceding bounds cover their values and
numerator temporaries. Every descendant uses this same representation;
adding its incoming height to the root allocation again would double-count.

For each division by \(2^j\), prove both that the integer numerator is
divisible by \(2^j\) and that \(0\le j<F+I\). The invariant proves the
first condition, while the instruction descriptor proves the second.
Zero values still require the extent check. Here scalar \(j\le3\);
elementary coordinate divisions use \(j=1\). The computed reserve covers
these shifts at positive root width. At width zero, execute the identity.

For \(H_0=H/2\) and \(D=\operatorname{diag}(1,i)\), use
\[
 H_0=\frac{1-i}{2}DCD.
\]
For \(h=2k\) the tensor scalar equals \((-i)^k2^{-k}\); for \(h=2k+1\)
it equals \((-i)^k(1-i)2^{-(k+1)}\). Execute one phase, at most one
sum/difference operation, and one exact shift. An additional \(h+1\)
height reserve suffices. The caller in `vendor/TENSOR-COMPILER.md:154–156`
restores raw \(H^{\otimes h}\) by multiplying by \(2^h\); reserve another
\(h\). Thus \((B+4)h\) covers the whole raw-H call for \(h\ge1\).
Its shifts have extent at most \(h<F+I\) under the correspondingly
enlarged allocation. Retain the headroom check for left shifts too.

## 6. What the Gaussian caller must supply

In `GAUSSIAN.md:120–126`, the author allows uncompleted logarithmic
amplification
\(O(g\,aB_{\rm block}^2/p^2+g\,\operatorname{polylog}p)=o(p)\).
The author normalizes completed maps elsewhere. Completed normalization
alone does not specify the height at each internal raw-H entrance.

For this repair, the caller must bind its actual entries to an explicit
base grid and a common \(t_*(p)\) that dominates their magnitudes and any
additional denominator bits at those entrances. If
\(P=O(p)\), \(t_*(p)=o(p)\), and all call widths satisfy
\(h\le g_{\max}=O(p^\beta)\), \(\beta<1\), allocate
\[
 F=P+t_*+(B+4)g_{\max},\qquad
 I=t_*+(B+4)g_{\max}+2.
\]
This is \(O(p)\) space per component and makes the internal supplier
arithmetic exact under the stated endpoint hypotheses. It does not add
a precision exponent to the proposed asymptotic bill.

Alternatively the caller may normalize every entrance to height zero,
but it must specify the precision adjustment and restoration scale.
For \(y=2^{-t_0}x\), a height-zero description uses base precision
\(P+2t_0\); scaling without that adjustment does not prove exactness.

In [CALLER.md](CALLER.md), I now bind an explicit rounded protocol to the
actual tensor compiler. I include cached coefficient error, completed
F-grid returns, raw-H scaling and transient product widths. That argument
permits O(p) incoming height under the stated Gaussian norm hypotheses.
I leave the universal coefficient/conditioning and boundary-prefix
estimates, native/free-algebra endpoints, tape/stock implementation and
complete multiplication theorem to separate audits. I retain the selected
frontier.
