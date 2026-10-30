# Fine-prime Gaussian assembly audit

Written all-size argument, 2026-10-19; PROOF.md supplies final integration.
This is not a formal proof-assistant certification.
Retained sources are PR1673's capped Gaussian papers and PR1758/1786's
shifted Toeplitz, sparse-union and fine-prime constructions. Their original
conditional labels are not treated as proofs of their interface premises.

## One fixed reference matrix and uniform conditioning

Use theta=t/s-1 in [1/(4p^2),1/p^2], rho=1+theta and
alpha=ceil(sqrt((4/pi)log(16p))). Write a=pi alpha^2 and b=pi/(alpha^2 rho^2).
Eventually 4log(16p)<=a<=5log(16p). Source primes, alpha and all cutoffs are
computed from p. The prime-interval argument in the pinned fine-prime proof
uses Trudgian's explicit unconditional prime-counting bound; its main term
t/(4p^2 log t) dominates its error because log t=Theta(p^(1-epsilon)).
There are eventually more than d distinct primes in the required intervals.
Trial division costs 2^O(p^(1-epsilon))*poly(p)=2^o(p). The capacity ratio
T/S<2 follows from sum theta_i=O(d/p^2). No unproved short-interval premise
is used; small failed parameter checks invoke the elementary multiplier.

Let N be the normalized narrow Gaussian matrix. The exact nearest-neighbor
pair estimate and Gaussian tail give
||N-I||_infinity <= exp(-2a theta)+5exp(-2a).
Thus its row gap exceeds 1/(8p^2) eventually. Remove its tiny diagonal
aliases, truncate at physical bandwidth W=O(sqrt(p)polylog(p))<p, and
round at sufficiently high fixed precision so the reference H has diagonal1,
row gap delta>=1/(16p^2) and row norm<2. Augment target holes by identity.
This gives Haug permutation-similar to H direct_sum I, with bandwidth<p.

All principal restrictions retain the row gap. INVERSE-CONDITIONING.md
proves, for I-E with bandwidth w and ||E||_infinity<=1-delta,
||H^-1||_infinity<=delta^-1 and
||H^-1||_1<=delta^-1+2w(1-delta)delta^-2.
The proof sums E^k; a column has at most2kw+1 possible entries, each bounded
by the row-sum bound. This works on periodic axes and finite sections and
does not assume that a row norm bounds a column norm. In particular both
||Haug||_2 and ||Haug^-1||_2, and the corresponding principal-section
norms, are less than p^10 eventually, uniformly in the global side length.

For the broad forward reference M, retain each selected Gaussian column
and an identity column at each target hole. Gaussian row and column sums
are bounded, so ||M||_2<3 eventually. Only its capped interior blocks are
inverted in the forward factorization. Their inverse bound follows directly
from the shifted-symbol argument below; a finite or bilateral LDU inverse
theorem is unnecessary for this construction.

Indeed xi<1 at the specified parameters. Thus theta B^2 log(p)=o(1).
In the exact broad identity of vendor/GAUGEFREE-INTERIORS.md, Section 2,
anchor x,y at the block center and put gamma=pi/(alpha^2 rho) and
s=-delta(1-theta), |delta|<=1/2. The two diagonal factors, after taking
out the scalar alpha^-1, and their inverses have bounded norms: their
logarithmic ranges are O(log(p) theta B^2)=o(1), and their constant
terms are bounded. The normalized Toeplitz symbol has accretivity

    mu >= (1-exp(-gamma theta)) exp(-pi^2/(3gamma)) > p^-5

eventually. To check the last inequality, gamma=Theta(1/log p),
theta>=1/(4p^2), and pi^2/(3gamma)=a rho/3 <=2 log p eventually.
Use 1-exp(-gamma theta)>=gamma theta/2. Therefore every capped broad
interior K has ||K^-1||_2<O(alpha p^5)<p^6. Truncation and rounding
perturb this by less than a factor two. The conservative p^10 allowance
is ample. No arbitrary principal inverse theorem for M is used.

Narrow weights may be exp(-Theta(p^2 log p)). Generate the common
reference weights at P_setup=Cp+64p^2ceil(log2 p) bits, not Cp bits.
They remain positive with relative error<2^-Cp. Reference entries and
their structure-preserving ratios are rational and polynomial-size in p.
Every local page is derived from this one reference; windows are not
independently rerounded before defining their overlap.

## Interior circuit and actual precision

Carve each constant-phase run into separated dyadic interiors of length
at most B=2^floor(xi log2 p). Include holes, original period cuts, core
edges, endpoint strips and dyadic tails in the boundary. Phase-run length
is Theta(p^2); W<<B<p^2. The enlarged boundary set E has density
O(W/B polylog(p)). Interior neighbors are separated by W, so eliminating
interiors leaves a Schur matrix of bandwidth O(W) in boundary order.

The exact fractional-shift identities in GAUGEFREE-INTERIORS replace the
linear part of each Gaussian diagonal gauge by a shift of its Toeplitz
symbol. For the narrow block, k(h)=exp(-a rho h^2-2a beta0 h), with
|beta0/rho|<1/2 and gap>=theta/2. For the broad block choose the shrunken
shift s=-delta(1-theta), whose gap>=theta. The remaining diagonal range
on a capped block is O(a theta B^2+a theta B), not O(aB).

For the normalized shifted Gaussian symbol, Jacobi's product and the
interlaced phase bound prove

    Re phi >= (1-exp(-gamma(1-2|s|))) exp(-pi^2/(3gamma)),
    ||phi|| <= 3+sqrt(2pi/gamma).

Both bounds are polynomial in p for gamma=Theta(log p) or Theta(1/log p).
Every finite Toeplitz section is therefore accretive with polynomial
norm and inverse norm. Every recursive Schur descendant has inverse norm
at most mu^-1 and norm at most Lambda+Lambda^2/mu. In bounding its
shears use this enlarged bound; Lambda/mu alone is not required.

vendor/SHALLOW-TOEPLITZ.md gives an explicit no-ancilla circuit. Its Schur
displacement rank grows by at most one per level; a rank-r Stein
displacement gives T=sum L(g_j)U(h_j). With bounded orthonormal generators,
use P=I+U(h)/gamma0, gamma0>=2||h||_1, and
Px; y+=gamma0 L(g)x; P^-1x; y-=gamma0 L(g)x.
This is a dirty shear with restored source. The triangular parity split
runs its two children on disjoint coordinates. These identities give
depth O(log^4 B) and logarithmic prefix norm O(log B log poly(p)).
Partial generator shears add; their norms are not multiplied as though
they were unrelated dense matrices. Ancestor factors contribute only
O(log B) polynomial factors along a recursive path.

Exact rational Schur matrices and normalized rational Gram-Schmidt give
a polynomial-time coefficient generator. Offline rational numbers may
have poly(p) bits. Final data-gate coefficients and all relevant prefix
norms need only O(log^2 p) guard bits per axis. The shifted circuit may
approximate the fixed reference interior, rather than share identical
rounded coefficients: its entry error is poly(p)2^-Cp, and
X^-1-Y^-1=X^-1(Y-X)Y^-1 bounds the inverse error as well.

For g=p^beta axes the total uncompleted log amplification is

    O(g a B^2/p^2 + g polylog(p)).

The exact ledger checks beta+2xi-2<1 and beta<1. Thus this is o(p).
The complex supplier's own common-grid guard is O(g)=o(p). One fixed
Cp+o(p) online precision suffices for the complete tensor circuit.

## The five factors, boundary arithmetic and current-value union schedule

Write Q=[[A,B1],[C1,D1]], with F=D1-C1 A^-1 B1. Execute

 Q^-1=diag(A^-1,I) E_-B1 diag(A,F^-1) E_-C1 diag(A^-1,I),
 Q=diag(A,I) E_C1 diag(A^-1,F) E_B1 diag(A,I),

in right-to-left matrix order. Here E_B1 and E_C1 are the corresponding
upper/lower shears with ORIGINAL banded couplings. There are three dense
interior stages and two sparse windows. Dense stages require scattering
the prior sparse union and gathering a new one afterwards.

For the narrow inverse, strict row diagonal dominance survives every
elimination with at least the original row gap and bounded row sum.
Every principal inverse is polynomially bounded. This bounds every pivot,
Schur matrix and partial block right-hand side in a no-pivot boundary solve.
For the broad forward map, F is APPLIED, never inverted; its norm is
bounded by ||D1||+||C1|| ||A^-1|| ||B1||. It is banded after the carve.

Batch right-hand sides in dyadic width between W and2W. Dense block updates
use Strassen's seven-product identity. Its recursive additions have
polynomial growth in W; 7^16<2^45 gives exponent tau=45/16. Rounding after
each block update creates residual poly(p)2^-Cp. A core has polynomial
length and its inverse and partial solve norms are polynomial, so the
total local residual remains poly(p)2^-Cp. All pages, copied headers,
transposes, erasures and rewinds are charged. The global boundary cost is

    O(V d W^(tau-1)/B polylog(p)).

Use the per-visit schedule in vendor/UNION-SCHEDULE.md, not the older g scans of
the whole union. Each record carries F(x)={i:xi in Ei}. These flags are
invariant under every sparse factor. Round r tags a current record by
the r-th member of F(x), stably distributes by that axis, transposes the
polynomial row field and applies the axis factor on complete Ei-lines.
The tag restriction depends only on the other coordinates along such a
line. Undo the transpose and distribution before deleting finished records.
Later rounds use the updated values. Stored split masks reconstruct the
original order on return. The number of visits is exactly
sum_x |F(x)|=sum_i |Ui|<=g mu V in record units.

Tag extraction and headers have O(g log L)=o(p) bits and fit the cost of
each visited coefficient. Two-tape stable radix passes and level-by-level
lockstep transposes use a fixed number of tapes. Payload records deleted
at different rounds are disjoint; all indicator stacks together have at
most g V bits, which fits O(Vp) bits because g<p. This addresses space
as well as head movement. Total union cost over d/g groups is
O(V d W/B polylog(p)). Temporary padding of the one exposed polynomial
row field is removed before the next axis and never accumulates as2^g.

## Core locality and explicit enumeration of corrections

Use the conservative polynomial locality witness in HALO:
P=p^-20 sum_{j<ceil(p^42)}(I-p^-20 H*H)^j H*, bandwidth<p^45 and
error<=p^10 exp(-p^2). Its row agrees with the section polynomial whenever
it is A=ceil(p^48) from a section edge. Choose core side
L=2^ceil(400log2 p). Every global target side is eventually divisible by L.
The broad forward direction uses only its actual bandwidth W locality.

Apply the full section tensor on each complete L^g core and keep the
interior outputs. Partition discarded outputs by their FIRST boundary
axis and side. The corresponding 2g disjoint rectangles, enlarged by A,
have total volume O(gA/L) times the core volume, since gA/L=o(1).
Apply the actual position-dependent polynomial rows on these rectangles,
paying O(A^2) word operations per output per axis. No convolution or
translation invariance of those coefficients is assumed.

Here is a sequential source-driven enumeration for the input copies.
For each source address scan its g local coordinates once. Store the
possible neighboring core index choices (at most two per coordinate),
its membership in each expanded interior interval, and its membership
in each expanded lower/upper face. Prefix AND flags determine in O(g)
additional short operations which first-face choices are permitted.
For each permitted face, enumerate the Cartesian product of the allowed
later core choices with an encoded depth-first odometer. Earlier choices
are unique because the expanded interior intervals are disjoint when
the polynomial bandwidth is <A. Emit a complete value and destination
rectangle/coordinate key per leaf. Internal enumeration nodes number at
most g times the emitted leaves. Charge O(p) work per emitted copy; the
initial coordinate scan costs O(g log L) plus original-coordinate arithmetic
O(g ell^2 polylog p)=o(p), using beta+2(1-epsilon)<1.

Thus there is one dense scan, and further work is charged to actual copies,
even if a rare address belongs to exponentially many enlarged rectangles.
Stable full-key radix passes sort only these sparse copies. The return
outputs have unique keys because the first-face partition is disjoint.
Merge them into the discarded holes in one dense scan. These scans cost
O(V) per group. Sparse copying, keys, sorting and axis exposure are covered
by the generous extra p^2 polylog(p) factor on copied volume.

All local row-polynomial and core factor pages are polynomial-size in p
and computed once per rectangle or core. A rectangle has g-1 long axes,
so its complete payload absorbs every fixed polynomial setup cost as
g tends to infinity. Coefficient generation is not repeated at every scalar
record. Intermediate polynomial applications amplify by exp(O(g log p));
the error exp(-p^2) remains below2^-Cp even after global norm conversions.
Rounding the polynomial coefficients and products has the same o(p)
log-amplification budget. The total conservative halo cost is

    O(V [d/g + d g A^3/L + d A p^2/L] polylog(p)).

## Complete-array calls and q-image layout

For a group the maps j->floor(tj/s+1/2) are increasing injections. Their
tensor product preserves lexicographic order. A target coordinate k has
candidate j=max(0,ceil(s(2k-1)/(2t))); membership is exactly j<s and
2tj<s(2k+1). One target scan inserts zero holes or consumes the next source
value. Extraction is the inverse increasing scan. Arithmetic for all group
coordinates fits one p-bit record by beta+2(1-epsilon)<1.

Gather the O(g log L) low microbox bits once by the support router,
retain every coarse coordinate as a complete spectator, then undo that
same gather before extraction. The tensor compiler's common six-H word
and Beneš layers invoke the complex supplier globally across complete
coarse ranges. Circuit coefficients may depend on coarse origin, but the
H layers do not. No supplier call is made on a masked set of coarse labels.
Polynomial factor-page setup is amortized by complete L^g microboxes.
Cached prefix products of per-axis diagonal coefficients update on odometer
carries, giving O(1) word products per record on average, with charged
sequential table scans and rewinds. There is no g full-input-pass cost.

Divide each completed per-axis map by a sufficient dyadic p^100 bound.
Combine the normalizers within group diagonals, with one scan per group.
Their total compensating shift is O(d log p)=o(p). This makes completed
maps contractions on arbitrary errors, including nonzero hole coordinates.
All local, tensor and global residuals at a sufficiently large fixed Cp
working precision are therefore 2^{-(C-O(1))p}; constants can be chosen
before n is known. PROOF.md proves the final transform identity, CRT
composition and exact integer recovery.

## Outer integration

PROOF.md combines these costs with CRT.md and the complete synthetic
convolution. Its cached-table construction removes the upstream per-record
d-axis chirp scan, and its global scalar/error calculation proves correct
integer rounding. The exact ledger checks the strict exponent inequalities;
it does not replace the construction or recovery proof.
