# Conservative local corrections for the Gaussian route

Auxiliary argument, 2026-10-19. This avoids assuming a quasilinear
position-dependent halo implementation. GAUSSIAN.md binds the norm,
core-circuit and enumeration hypotheses below to the actual rounded
matrices; PROOF.md composes the resulting maps into multiplication.

Let H_i be periodic matrices on axes of dyadic length S_i. Suppose H_i and
every contiguous principal section have 2-norm at most p^10 and inverse
2-norm at most p^10, and H_i has physical bandwidth W<p. The bounds refer
to one fixed rounded/truncated matrix, not independently rerounded windows.
They apply to the narrow augmented matrix. The broad direction applies a
forward banded matrix M, and does NOT need an inverse-locality theorem.
For that direction, a core row at distance W from its edge agrees exactly
with the global row; sparse corrections apply M itself. Only the broad
phase-interior blocks need the finite inverse bounds used in their LDU
factorization. In particular, this argument does not assume that arbitrary
principal subsets of the broad matrix have uniformly bounded inverses.

Put Q_i=I-p^-20 H_i^* H_i and J=ceil(p^42). The polynomial

    P_i=p^-20 sum_(j=0)^(J-1) Q_i^j H_i^*

has physical bandwidth <=(2J+1)W<p^45 eventually, and

    ||P_i-H_i^-1||_2 <= p^10 exp(-p^2).

The same holds for a principal section. These facts follow from the spectral
interval [p^-20,p^20] for H_i^*H_i, the geometric-series identity and
(1-p^-40)^J<=exp(-p^2). For any row at distance A=ceil(p^48) from a section
boundary, all paths in this polynomial stay inside the section; its row is
therefore EXACTLY the corresponding row of the global P_i. The polynomial
is only a locality witness and an offline coefficient generator. It is not
iterated J times on the dense data.

## Complete core tensor and sparse correction volume

Choose dyadic core side L=2^ceil(400 log2 p). Eventually L divides every
dyadic target axis, L>4A and gA/L=o(1) for every g<=p. On each L^g core box
apply the tensor product of the section inverses by the independently
required capped Toeplitz/boundary construction. Keep outputs at distance A
from every face. Their difference from the full inverse tensor is at most

    g p^(10g) exp(-p^2),

before changes between induced norms. Even a global dimension factor
exp(O(p)) leaves this below 2^-Cp for every fixed C eventually, provided
g log p=o(p). Scalar normalizations can only improve this error bound.

Partition discarded outputs by their first boundary axis and its lower or
upper face. These 2g sets are disjoint rectangles. Enlarge their input
intervals by A on each side. Since gA/L=o(1), the product enlargement factor
(1+2A/L)^g is bounded. Their total copied input/output volume is
O(gA/L) times the complete core volume. Periodic wrap is encoded in the
coordinate keys; no global axis is padded independently.

For these rectangles apply the FULL polynomial tensor product of the P_i,
using the actual position-dependent coefficient rows. Coefficients depend
on the absolute axis coordinate and are not treated as a translation-
invariant convolution. Each P_i has bandwidth <=A. A direct sequential
banded application suffices: expose one axis, scan each required input window
against its coefficient row, accumulate its output and advance. Even paying
O(A^2) record operations per output is an ample bound. Keep the source until
the complete output is produced, then erase the source and work. For each
record operation use the established classical quasilinear p-bit arithmetic,
independent of the improved multiplier being constructed.

All rectangle side lengths and local coefficient pages are fixed powers
of p. Their setup can recompute the local polynomial from band entries by
ordinary polynomial-time matrix arithmetic. It uses no global inverse
oracle. Setup is polynomial in p, including the absolute-coordinate words;
each rectangle has at least g-1 long L-O(A) axes. For balanced groups with
g tending to infinity, their payload absorbs every such fixed polynomial.
Alternatively retain that explicit setup term until the eventual threshold.

Axis exposure uses equal-width exchanges and elementary short-field moves
at widths O(log p). Repeated exposure for g axes is charged to the sparse
rectangle volume, never to the full array. Copies, full O(p)-bit keys, radix
passes and sparse counters cost at most that volume times p^2 polylog p.
Gathering and final reinsertion also make a full O(V) scan per group; this
belongs to the outer group-scan row. Use source-driven enumeration with
one O(p)-bit coordinate scan per record and further work charged to emitted
copies. A separate full scan for each face would cost gV and is not admitted.
Address arithmetic and row setup are included; no random table lookup is free.
GAUSSIAN.md, "Core locality and explicit enumeration of corrections",
gives that source-driven enumeration and proves its per-copy bound.

Thus a deliberately loose bound per group is

    O(V [1 + (gA/L) (g A^2 + p^2)] polylog p),

plus the absorbed local setup. Over O(d/g) balanced groups this is at most

    O(V [d/g + d g A^3/L + d A p^2/L] polylog p).

For A=p^48, L>=p^400, d=p^epsilon and g=p^beta with epsilon,beta<1, the
two sparse powers are epsilon+beta+144-400 and epsilon+48+2-400, both negative.
This leaves ample room to use a simple polynomial local algorithm rather
than the stronger halo tariff in the inherited ledger.

## Discharge at the Gaussian call site

1. INVERSE-CONDITIONING.md and GAUSSIAN.md prove the p^10 narrow bounds
   for the same rounded matrix and its sections. The capped broad blocks
   use the shifted-symbol argument directly, with bounded diagonal gauges.
2. GAUSSIAN.md supplies the complete core application, capped interiors,
   Strassen boundary costs, prefix bounds and common online precision.
3. Its source-driven enumeration and increasing q-image scan handle holes,
   period cuts and the immutable coefficient pages of one reference matrix.
4. PROOF.md combines the normalizers and proves exact integer recovery.

For the broad block factorization, apply the boundary Schur complement
S=D-C A^-1 B; do not solve with S^-1. Only the narrow inverse direction
requires a boundary solve. Its strict row dominance supplies invertibility
for every principal elimination set. Importing that fact to the broad
matrix without proof would create an unnecessary additional hypothesis.

The polynomial locality identity and sparse-volume count are auxiliary
lemmas; the complete multiplication theorem is asserted only in PROOF.md.
