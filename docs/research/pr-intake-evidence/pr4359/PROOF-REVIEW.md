# PR #4359: review of the changed proof interfaces

Source: zxv's PR #4359 at `da637c87c89482bc4c86be36bd0071b3d400dbed`.
Canonical main checked at `12fa8c5c844be21bfefb38a19503fbd867a11244`.
Prepared by Douglas Colkitt's OpenAI assistant; substantial AI assistance.
Apache-2.0. This is a mathematical review, not a Lean certificate or an
independent human review. The earlier replay and its limitations are retained
in `REVIEW.md` and `VALIDATION.json`.

## Verdict

**The changed construction passes this conditional proof audit at
κ = 23/10000.** The three admission questions left by the initial review have
been checked below. No additional unsupported primitive or uncharged
productive input was found in these changes. The conclusion retains the
upstream/native and outer hypotheses identified at the end of this note.
It does not establish an unconditional integer multiplication theorem.

The next task is integration: retain the exact source closure and attribution,
install a selected-result record that describes this new supplier class and
its conditional proof boundary, and reconcile the public statement and
reproduction entry point. This review does not itself change the selection,
merge or close the PR. The PR's unrelated later H-branch research is outside
this positive verdict.

## 1. Integer compiler: why the moment has an actual circuit behind it

Write m for the largest productive rank, k0 for the smallest, and r0 for the
largest paid rank. In the two applications these are (57,6,5) and (50,8,7).
The strict separation r0 < k0 is essential.

For a target multi-index a, the unit multiplicity
u(a) = multinomial(|a|;a) product W_k^a_k obeys
u(b) = sum_k W_k u(b-e_k). This is an identity of integer slot counts.
At a parent round of rank r, a slot with parent column rho*c(b) matches a
child target k at column rho*r*c(b-e_k), since both jobs have rank
rho*r*c(b). The child fits whenever its parent fits, because r/k < 1.
Thus no paid parent demand is dropped by the geometric cutoff.

The root degree is G = floor(log_(k0)(n/m)). A root source has rank at least
k0^(G+1) > n/m. In later classes, a missing parent of a target of rank s
would have ambient requirement m*s/r; hence it too implies s > nr/m >= n/m.
All sources have s <= n. At the deepest generation, each exit rank is at
most r0^(G+1) <= r0*(n/m)^theta, theta = log(r0)/log(k0) < 1.
These observations justify the source and exit bounds, rather than merely
assuming that a finite enumerated flow represents every n.

Classes retain the entire ordered parent-round path. A parent issues one job
per unit in the current round and resumes only after its child class returns.
At the root, different units have disjoint physical inputs and owned centers.
Inductively, inputs arriving in a child class are distinct fields; missing
slots receive distinct new sources. That preserves distinctness within each
unit. A parent's copied center can be a child input: arbitrary-input linear
correctness does not require statistically independent current values. It
must still be a distinct physical field. There is no extra output credit for
that center, and simultaneously suspended centers have separate allocations.

For each n, replicate the finite flow by a common multiple of all smaller
supplier widths used in its exit and complement batches. This gives integer
batches without fractional arrays or discarded jobs. Each top source receives
its n-s complementary transform first, followed by its s-job. Only completed
endpoints must fix spectators; intermediate operations need not commute with
the complement. The completed product is the full n-job on every counted
source. Adapters and role routes are undone before resuming a parent.

Consequently the actual per-source leaf count satisfies
L(n) = sum_s w_s L(n-s) + sum_e x_e L(e), with sum_s w_s = 1.
At the exact mixed root, exit and source tau-potentials are equal. At the
strict tested superpotential used in the explicit bounds, the exit potential
is smaller, which suffices. For tau < z0 < z < 1 and delta = z0-tau,

    sum_e x_e e^z0 <= (m E(n)/n)^delta sum_s w_s s^z0.

Meanwhile, for t=s/n >= 1/m,

    1-(1-t)^z0 >= z0*t >= z0*m^(z0-1)*t^z0.

The first coefficient tends to zero, while the second is positive. Strong
induction on strictly smaller ranks gives L(n) <= A n^z0 and eventually
L(N) < N^z. Positive rank-one surplus also supplies L(n) <= n for the explicit
finite base bound. This proves existence of a finite supplier, independently
of a RAM running-time estimate or a materialized huge instruction list.

The explicit H0/H1 argument uses these same inequalities with conservative
constants. The exact-source replay verified the two specified ranks and
strict inequalities. PR #4404 supplies additional, narrower arithmetic/flow
evidence; this review does not use it to certify the native interfaces.

## 2. Complex native hypothesis and arbitrary column multiplicity

The native evaluator at
`research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py`
represents a row by rational coefficients on (input role, reduced operator
word). Its warp reduction only cancels adjacent inverse symbols. Paid moves
change the reference frame, and scalar operations require identical current
frames. The complete word was replayed against all arbitrary persistent input
columns, with owned centers cleared. `native_extensions.literal_replay` gives
a second literal evaluator; the already completed replay includes both.

This is stronger than testing one numerical matrix: evaluation of the free
word algebra into any physical operator representation preserves the identity.
For f columns, substitute each lifted warp for its generator. Scalar
coefficients do not change. The separate exact physical factorizations of
paid moves and whole-helper endpoints lift by tensoring products; no step
requires tensor power to distribute over a sum. Absolute monomial phase
must become a*f + sum q(x_j), as specified, rather than retaining a single a.
The p3 physical boundary audit includes signs/translations before that lift.

The controller's scalar identity and its physical endpoint normalization are
separate checked layers. All 2,856 local helper occurrences have owners. Each
invocation has 408 distinct helper fields, disjoint from its live main fields.
Idle-main uses occur in the recorded inactive windows; residual idle axes are
paid. Only the 1,570 fresh helper owners enlarge the productive source census.
For example, G0:371's rank-five transform receives its paid rank-one top-up
before it is counted as rank six. The complete target-minus-paid rank mass
is 224, not the gross helper rank sum.

After the whole local invocation, each helper endpoint is autonomous.
Whole-field pre/post monomials therefore normalize it without reassigning
frames at internal scalar gates. Canonical positive tensor jobs admit disjoint
splitting and fixed coordinate matchers. Finite compositions retain the
arbitrary-input/spectator contract. One owned center per compiled unit instance
is a safe allocation; the older one-center-per-depth shortcut is not used.

## 3. BIT: the adapter exists without a free dense address map

For an idempotent P and atom reversal C, let

    D_P = [[I-P, PC], [CP, I-CPC]],
    Q_S = diag(S, CSC).

Block multiplication gives D_P D_(I-P) = D_I and
Q_S D_Q Q_S^-1 = D_(SQS^-1). Both identities permit nonsymmetric projectors.
Same-rank rational idempotents have a rational matcher S by choosing image
and kernel bases. This algebra alone would not make Q_S a cheap operation.

The actual adapter instead maps a complete role fiber x_g to y_(gS)=x_g,
runs the child's complete word, then restores its fiber. A child endpoint
D_(h Q h^-1) becomes D_(g S Q S^-1 g^-1) = D_(g P g^-1).
Different target roles may have different matchers: each fiber map is a
bijection, the child is correct on arbitrary simultaneous input arrays, and
its completed endpoint has no cross-role contamination. Owned child storage
is separate. This also explains why slot independence survives the routing.

The final compiled program embeds every projector and routing symbol in one
common ambient N. Its internal per-port routes are retained, including those
already present in the p3 word. The global cover is applied to this entire
finite program. Equal-rank jobs are not first lowered to incompatible
role-specific weighted interchanges.

One common external weight A is independent of the fresh cover coordinate.
It consequently commutes with role routing and pointwise scalar/COPY gates.
Final rank-one leaves can then be lowered by the inherited normal form;
their pivot weights depend on parent cover data, which are ancestors of the
child's new role fields. This meets the existing weighted-child contract.
Allowing A to depend on the current cover coordinate would invalidate this
argument and is expressly excluded.

All template matrices and matchers are fixed before choosing the odd prime.
A prime can avoid the finite denominator/determinant/rank-witness list.
For g=g0+qG1, right multiplication is a fixed low-type permutation and an
affine map of the complete high-matrix field with its carry. The retained
`notes/three-stage-cover-bit.tex` prices such rational routes using old atom
interchanges and ordered shifts. Applying it here changes fixed dimensions,
operation counts and constants, not its w exponent or tape uniformity.
All high matrices are streamed in batches; there is no tape per cover row.

With compiler saving C0=.00276 and covered saving C1=.00275, d=C0-C1=10^-5.
For N>=2, N^d >= 1+d/2. Choosing q>256 N^5/d bounds the fallback multiplier
by 1+d/4, so the full moment is strictly below 400001/400002. This pays the
bad classes individually; no assumption of independent bad events is needed.

Atom power .003 then gives ordinary saving
(1-.003)*.00275 + .003*.0000384599 = .0027418653797 > .0027.
The linear adapter and borrowed-stock inequalities are strict. The two-call
ordinary wrapper restores rows and pays its three additions. Cover, source
batch and old-leaf stock have logarithm O(w log e); fresh roles are carved
only from unused stock. Enormous N, B and q are fixed constants here.

## 4. Precision, storage and the outer call boundary

The new complex word cannot inherit the old numerical scalar cap. The PR
recounts the dyadic coefficients and replaces it with G=1494376*U, where U
counts compiled mixed-unit instances. Owned fields are excluded from productive
W, but included in Z=W+O, with O<=U. Its proposed E dominates
2GZ^2+8P+4Z+4+32N, so remainder kernels and local scalar growth are covered.
Fixed address permutations and unit phases contribute no coefficient height;
their actual implementation costs are separately paid.

A completed rank-f canonical child increases magnitude/denominator exponents
by at most f, regardless of the size of its internal temporaries. Parents
wait for completion, and no rounding occurs on return. Thus

    A(e) <= A(floor(e/N)) + P floor(e/N) + E.

With B=P+E, N>=2 and f>=1,
2Bf+Pf+E <= 2BNf <= 2Be. The ordinary leaf bound handles f=0 and stopped
leaves. This establishes the substituted linear semantic guard, with the
new C0=32NB^2. Every such constant is fixed before p varies; epsilon<1
absorbs it at an effective threshold. This is the same completed-child
argument as the retained semantic precision theorem, with its inputs replaced.

The changed BIT reserve requires more than the older O(log h) claim. The
PR explicitly retains a conservative product-stock bound

    q0(h,p) <= C*(log h + h^.003*(log p)^3 + 1).

For h above a sufficiently large fixed polylogarithmic threshold this is
at most h/64. Together with the 3h/128 control chunks and bounded rounding,
the deferred width is at most h/16. Smaller h is a polylogarithmic tail.
Thus the geometric phase sum still has the claimed selected-width exponent.
No selected bit in a reserved chunk is prematurely transformed.

This uses the global support-local wrapper, not a call inside a fixed
coarse-label microbox. Complete neighborhoods, controls, spectators and row
ranges remain present. Row padding is removed at every completed phase
before inverse exposure or the next coarse-dependent diagonal. The unchanged
suffix exclusion and K=128G finite guard are necessary and retained.
For group width p^beta, beta=.99997<epsilon=.99999<1, all new reservoir
sizes are o(p) and each original axis eventually fits its O(log p) neighborhood.
The one-axis length need not hold the entire control reservoir.

The exact outer calculation has nine cost rows, all strictly above .0023;
the limiting saving is .00230197698. The spare powers for precision, record
preparation, source axes and group support are positive. Fixed-template
complexity can alter the eventual threshold, but cannot be treated as a
parameter that grows with p. Under that order of choices the substitution
introduces no new exponent in these rows.

## 5. What this verdict does and does not accept

Accepted scope: the supplied productive-helper p3 words, their finite
uniformization, delayed BIT interface, replacement constants and the stated
outer parameter point, conditional on the retained native and outer contracts.
The earlier 23-stage replay supports the exact finite data used in this review.
It is not substituted for the arguments above.

Inherited assumptions remain: the underlying native producer/normal-form
implementations, ordered affine and compact movement/repair primitives,
fixed-tape execution contracts, fine-prime padding, analytic decomposition,
gauge-free interiors and exact recovery from the retained outer framework.
This pass did not re-prove that entire historical stack or the OpenAI manuscript.
It found the changed suppliers compatible with those interfaces as stated.

The uniform winning words have ranks 2^276540184361 (complex) and
2^6552928412 (BIT before covering). They are effectively specified finite
programs, not materialized or practical constructions. Their small rank-57
and rank-50 checks are ownership/completion examples, not witnesses achieving
the limiting saving. No practical speedup follows from this review.

Credit: zxv for this proposed construction and binding; Jacob Alan Sussman
for Theorem 1G / PR #4268; the retained native-word, cover, semantic-precision,
support-local and outer-framework contributors credited in the pinned source
closure. PR #4404's separate audit has its own narrower scope and attribution.

## Next action and invalidation

Integrate the exact reviewed closure and prepare conditional selected-result
metadata. Do not turn this review into approval of unrelated H-branch claims.
No new critical replay is required for unchanged source bytes; a packaging
change needs integrity/source-binding checks, and any mathematical change
needs review and replay of the affected dependency chain.

A new head, changed native endpoint, compiler rule, matcher/weight contract,
precision/stock formula or inherited implementation invalidates the affected
part of this verdict. The main and PR head were rechecked during this pass.
