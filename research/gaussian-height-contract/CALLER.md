# Rounded diagonal stages and exact raw-H entrances

I bind an explicit rounded execution to the retained six-H/Beneš compiler.
I credit Vlado Vojdanovski's compiler and ywz65's
`simultaneous-gate-rounding` analysis. The latter already proves a generic
simultaneous-error theorem. My scope is the emitted caller, cached
coefficient products, temporary words and raw-H entrance/export contract.

## Protocol and hypotheses

Use \(|z|_1=|\Re z|+|\Im z|\) and its coordinate maximum for vectors.
This norm is submultiplicative and dominates complex modulus. Let \(R_F\)
truncate both signed components toward zero on the \(2^{-F}\) grid.
Each rounding has error at most \(u=2^{1-F}\); take \(F\ge1\).

The compiler has \(g\ge1\) axes of side \(N=2^m\ge2\) and \(M\ge1\)
diagonal/H stages. Require a common H signature across coarse labels and
an explicit bound \(|d_a(i;c)|_1\le B\), \(B\ge1\), on all exact reference
table entries. Enlarge a complex-modulus bound by two if necessary.

For each diagonal stage and coarse label:

1. Produce F-grid coefficient tables with error at most \(u\).
   Generate inverse coefficients from their exact references and round
   separately. Do not invert a rounded table entry.
2. Initialize a fresh suffix cache and enumerate with axis0 fastest.
   On a carry to axis \(k\), recompute suffixes \(P_k,\ldots,P_1\) from
   the unchanged higher suffix. Round each coefficient multiplication.
3. Multiply the current data entry by its rounded tensor coefficient,
   then round the complete product to the F-grid.

Reset the cache on every stage, coarse-label or table change. Use no
division by an old entry; zeros require no special update. Padded identity
diagonals follow the same protocol. Between diagonals, execute raw H
exactly: restore its full \(2^g\) scale before exporting the endpoint.
Remove only guard bits whose zero value follows from that exact endpoint.

## Cached-product bounds

Put \(b=B+1\ge2\). For a suffix of \(k\le g\) factors, induction gives
\[
 |\widehat P_k-P_k|_1\le2ku\,b^{k-1}.
\]
At a new factor, multiply the old error by at most \(b\), add at most
\(uB^{k-1}\) from coefficient approximation and at most \(u\) from
product rounding. This proves the displayed induction.

Prove magnitude separately. With \(q_0=1\),
\[
 q_k\le bq_{k-1}+u
 \ \Longrightarrow\
 q_k\le b^k+u(b^k-1)/(b-1)\le2b^k .
\]
The carry rule restores the same nested rounded expression as a fresh
evaluation at the current address. Repeated reads add no error. The
bound depends on suffix length, not the number of records already scanned.

## Trajectory, precision and incoming height

Take \(M_0\ge\max(1,\|x_0\|_\infty)\), and set
\[
 R=4b^g,\qquad K=\lceil\log_2R\rceil .
\]
A rounded diagonal maps a bound \(X\ge1\) to
\(2b^gX+u\le RX\). A raw \(g\)-axis H layer has norm \(2^g\le b^g\).
Thus \(\|\widehat x_s\|_\infty\le M_0R^s\). Exact stages also have norm
at most \(R\).

At a diagonal stage \(s\), the coefficient and arithmetic residual is
at most
\[
 2gu\,b^{g-1}M_0R^{s-1}+u\le(2g+1)uM_0R^s .
\]
Propagate each residual through the exact remaining stages and sum:
\[
 \|\widehat x_M-x_M\|_\infty\le M(2g+1)uM_0R^M.       \tag{1}
\]
I use neither cancellation nor independence of rounding errors.

For target error \(2^{-P_{\rm out}}\), choose
\[
 t_*=\lceil\log_2M_0\rceil+MK,\qquad
 F=P_{\rm out}+1+\lceil\log_2(M(2g+1))\rceil+t_* .
\]
Equation(1) gives the target. Every raw-H entrance lies on the F-grid
with magnitude at most \(2^{t_*}\).

Use [PROOF.md](PROOF.md) with base precision \(P=F-t_*\ge0\).
For its mixed-provider reserve \(B_{\rm res}\), allocate
\[
 \text{fractional}=F+(B_{\rm res}+4)g,\qquad
 \text{integer/sign}=t_*+(B_{\rm res}+4)g+2 .
\]
Since \(H^{\otimes g}\) has integer entries, its exact endpoint returns
to the F-grid. Removing the extra fractional zeros after raw-H restoration
adds no error. Rounding the H0 intermediate before restoration would
require a different error budget.

## Temporary words and complete scan cost

Two F-grid operands produce a \(2F\)-grid exact product. Coefficient
magnitude is at most \(2b^g\), and data magnitude at most \(2^{t_*}\).
Therefore
\[
 2F+t_*+\lceil g\log_2b\rceil+O(1)
\]
bits per signed component cover product temporaries and complex-component
sums. Round only after forming the complete product. An unrounded chain
of cached multiplications would need a different denominator argument.

Cache initialization costs \(g-1\) products. A depth-k carry causes at
most k recomputations and occurs at most \(V/N^k\) times, \(V=N^g\).
Including one output coefficient per record,
\[
 g-1+V+\sum_{k\ge1}kV/N^k\le4V .
\]
A carry visits and rewinds \(O(kN)\) table records. The same geometric
sum gives O(V) record moves, including normal axis0 rewinds. Cache and
table storage use O(g) and O(gN) records, both O(V). Retain the author's
separate generation/loading charge for each coarse-label table.

Rounding and raw-H export add a bounded number of scans per record per
stage. Under the retained pointwise arithmetic kernel, O(p)-bit products
cost \(O(p\operatorname{polylog}p)\). The protocol therefore preserves
the original diagonal allowance \(O(V_{\rm bits}\operatorname{polylog}p)\).
I do not assign zero cost to setup, carry updates or return scans.

## Gaussian substitution and remaining analytic premises

The source has \(M=O(D\log N)=\operatorname{polylog}p\), \(g=p^\beta\),
\(\beta<1\), and the per-axis coefficient/gauge envelope
\[
 \log b=O(\operatorname{polylog}p+aB_{\rm cap}^2/p^2).
\]
Its \(\beta+2\xi-2<1\), \(B_{\rm cap}=O(p^\xi)\), imply \(MK=o(p)\).
If \(P_{\rm out}=O(p)\) and \(\log M_0=O(p)\), the fields above and the
product temporaries are O(p). An o(p) incoming height is sufficient but
unnecessary for this conclusion.

The author allows a full-array conversion with \(T=2^{\Theta(p)}\).
Under the stated completed-map contraction and accumulated-error bounds,
the data 2-norm is at most \(2\sqrt T\). A boundary/dense prefix of norm
at most \(2^{A(p)}\) therefore permits
\[
 M_0=4\sqrt T\,2^{A(p)},\qquad
 \log_2M_0=2+\tfrac12\log_2T+A(p).
\]
The factor two covers conversion to complex \(\ell_1\). The claimed
\(A(p)=o(p)\), or an explicit O(p) substitute, suffices. This states
the actual norm obligation instead of assuming normalized entries at
each raw-H entrance. I retain the coefficient-generation, conditioning
and rounded boundary-prefix estimates in `GAUSSIAN.md:112–152` as
hypotheses; this diagonal protocol does not prove their analytic validity.

For J circuit invocations, final scale \(2^\gamma\) and outer suffix
amplification \(\Lambda_{\rm out}\), choose
\[
 P_{\rm out}\ge4p+\gamma+
 \lceil\log_2(J\Lambda_{\rm out})\rceil+3 .
\]
These circuit errors then consume at most \(2^{-4p}/8\) after restoration.
Keep separate budgets for reference approximation, boundary arithmetic
and other transforms. Polynomial J, \(\gamma=o(p)\) and
\(\log\Lambda_{\rm out}=O(p)\) preserve O(p) precision.

## Executed caller and limits

I authenticate the original import-safe compiler in
`capped-phase-fusion/evidence/inplace_algebra_ultra/check_tensor_compiler.py`.
I preserve its assertions under optimized audit execution and call its
actual `gateword` and `local_layer`, enforcing the shear B hypothesis.
I use two coarse labels with distinct matchings/tables, zero and nonzero
shears, swaps, identity and complex FFT phases.

I execute all sixteen basis inputs and one dense complex input per label:
34 trajectories, each with eighteen raw-H calls and nineteen diagonals.
I compare the exact emitted endpoint with separately constructed
original-gate endpoints, then bound the rounded outputs. The actual
coefficient bound is \(B=3\); \(M_0=2,R=64,K=6,t_*=223,F=256\) suffice
for a 24-bit target. Equation(1) gives \(185/2^{32}\).
I observe nonzero rounding error, incoming height eight and temporary
fractional width 511.

Fresh-cache cases include zeros and carries through four axes. Controls
reject a stale carry and incompatible coarse-label H signatures. Exact
witnesses detect omitted product rounding and omitted H0 restoration.

I use an exact C/H0 interface model, not the physical mixed-provider
recursion. I do not execute the astronomical cover, complete Gaussian
circuit or integer recovery, or certify the source's universal analytic
bounds. The result is an explicit rounded caller contract, an actual
emitted-table replay and a conditional O(p)-word consequence.
