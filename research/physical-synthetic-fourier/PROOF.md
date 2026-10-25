# Complete normalized synthetic Fourier execution

I prove a conditional implementation theorem for the polynomial Fourier
maps in source06. I use PR3627's complete arbitrary-support normalized H
interface and PR3619's complete sparse-support router. I retain their native,
hosting, height, refinement and all-size premises. I do not infer scientific
admission from their finite replays.

## 1. Boundary and conclusion

Fix a positive axis count D, ell >= 2, precision p >= 2 and outer-row count C.
The caller supplies D flags in axis order, most-significant axis first.
Flag i determines a_i = ell-1+flag_i. Put

    A = sum_i a_i, M = 2^A, r = 2^ell, P = p+A.

The caller supplies exactly C M r Gaussian dyadics on the p grid, each in
the closed complex unit disk. Within each outer row, addresses increase
from 0 to M-1. Each address owns coefficients 0 through r-1 of a polynomial
modulo y^r+1. Each coefficient owns a signed real word followed by a signed
imaginary word, each p+2 bits, least-significant bit first. The caller encodes
numerical parameters as canonical Count tapes and flags as a raw binary tape.

For natural multi-indices j and k, define

    W±[j,k] = y^(± sum_i 2^(ell+1-a_i) j_i k_i),
    F± = W±/M.

On successful legal calls, `Fourier.run` returns exactly Q_p(F±x), where
Q_p truncates both components of each coefficient toward zero. I preserve
borrowed data and descriptors, consume intermediate child returns, and restore
owned scratch bodies and heads. The caller must consume the protected output
before another invocation. I make no rollback claim after an interrupted or
failed inherited callee.

Each returned coefficient has error strictly below sqrt(2) 2^-p relative to
the ideal endpoint, and remains in the unit disk. If that ideal endpoint
already lies on the p grid, I return it exactly. Both maps divide by M:

    F+ F- = F- F+ = I/M.

A convolution caller must retain its final M scale. I do not call these two
normalized maps unscaled inverses.

For fixed 0<epsilon<1 and fixed positive shape constants, assume

    D = Theta(p^epsilon), ell = Theta(p^(1-epsilon)), A = Theta(p).

Let alpha=99827101/100000000, tau=332353/332929,
b=2^floor((997/1000)floor(log2 P)), m=min(D,b), and V=2(p+2) C M r.
Under the named callee premises, I obtain

    O(V [A m^(alpha-1) log p
         + A m^(tau-1) (log p)^(1+tau) + ell])

time and O(V)+F_q space. I include input/output copies, signed diagonals,
all top and common rounds, support preparation, endpoint bit reversal,
precision conversion and cleanup. In particular, with
s=min(epsilon,997/1000), I obtain

    O(V p^(1-s(1-alpha)) log p).

For epsilon >= 997/1000 the saving in this synthetic-transform bound is
172380303/100000000000 = .00172380303. I claim no integer-multiplication
exponent from this theorem. Constants depend on the fixed shape constants,
epsilon and the inherited suppliers; I claim no uniform limit as epsilon
approaches one and no practical cutoff.

## 2. Natural-axis arithmetic

For each axis set o_i=sum_(j>i) a_j. The address bit o_i+v represents named
bit v of axis i. In round h, let

    S_h = {o_i+h : h<a_i},
    E±(x,h) = ±2^(ell-h) sum_(i:h<a_i)
                    bit(x,o_i+h) ((x div 2^o_i) mod 2^h)  (mod 2r).

The forward procedure visits h=ell-1,...,0 and applies H0 on S_h followed
by multiplication by y^E-. The opposite procedure visits h=0,...,ell-1
and applies y^E+ before H0 on S_h. H0 denotes the tensor product of
normalized two-point butterflies [[1,1],[1,-1]]/2. At h=ell-1 only long
axes participate; at h=0 the diagonal exponent is zero. An empty top
round performs the identity.

The source06 author proves the unnormalized one-axis formula by following
processed branch bits and untouched lower bits. Tensoring axes and dividing
by the product of all butterfly factors gives

    U- = B W-/M, U+ = W+ B^-1/M,

where B reverses bits within each named axis. The retained
`synthetic-allsize-identity/PROOF.md`, sections 2-4, gives the same all-size
identity. I therefore apply B after the forward rounds and before the
opposite rounds. Since B=B^-1, both endpoints have natural frequency order.

I do not use the older L layout. PR3627 accepts the actual selected positions
and restores the incoming frame after each H call. `natural_axes` visits
axes from right to left, so the emitted positions increase. Consequently the
following diagonal reads the same named bits. The internal actual-g spacing
of the H callee does not change this interface. I do not pass old Kd-spaced
headers to a Kg-spaced root.

I split S_h into consecutive groups of at most b positions. Disjoint H0
factors commute, so executing these groups in order gives the entire H0_S_h.
I place the diagonal after the complete forward round, or before the complete
opposite round. I never interleave J with an incomplete H round.

I calculate b from an encoded logarithm, multiplication by the fixed 997 and
division by the fixed 1000. Thus P^(.997)/4 < b <= P^(.997), so b remains
within the inherited exact-root admission cap and has the same asymptotic
power. I avoid a large integer-root calculation in the new schedule planner.

## 3. One exact grid for the complete transform

`execute` inserts A zero low bits into each input word. The represented value
does not change; its precision becomes P=p+A and its word width becomes P+2.

Count a normalized one-coordinate butterfly as one factor. Across all rounds,

    sum_h |S_h| = sum_i a_i = A.

After t factors, every ideal coefficient lies in 2^(-(p+t)) Z[i]. Each J
and B only permutes coefficients and changes their signs, so it preserves
that grid. For t<=A, this grid is a subgrid of the P grid. This statement
also holds after each support batch inside a round.

PR3627 returns Q_P of the complete ideal H batch, including its own paid
literal fallback when necessary. The divisibility argument makes Q_P exact
at each such return. Thus no intermediate callee truncation changes a value.
I truncate once, from P to p, after the entire Fourier procedure.

For two disk-valued inputs z,w, both (z+w)/2 and (z-w)/2 remain in the disk.
Signed polynomial rotations and B preserve the disk coefficientwise. The
P+2-bit signed words therefore retain headroom; in particular a negated
coefficient cannot be the most-negative representable word. Componentwise
truncation toward zero preserves the disk and gives the stated endpoint error.

This argument uses the complete rounded endpoint contract of PR3627, not an
error estimate alone. A merely approximate root with error less than one ulp
would not establish exact intermediate grid values. The failure suite executes
a physical per-round p-grid truncation mutant and distinguishes its output
from the complete-transform endpoint.

## 4. Encoded all-size diagonal

`FourierPlan` computes offsets and lengths on Count tapes. It has a fixed
dictionary of numerical roles; it does not decode an address or dimension
into a Python integer. `flag_at` scans the borrowed flag stream from its
origin. `natural_axes` retains one offset, length and reverse ordinal.

For one actual address and round, `exponent` sums the selected lower h-bit
windows, reduces that sum modulo 2^(h+1), then shifts it by ell-h bits.
This equals E+ modulo 2r. For the forward direction it negates that canonical
residue modulo 2r. All values have O(P) bits; I retain only a fixed number
of them at once. The runtime has no ell<=32 or D<=16 admission cap.

Write E=epsilon_sign*r+s with 0<=s<r and epsilon_sign in {0,1}. For the
input polynomial sum_j z_j y^j, multiplication by y^E sends z_j to position
(j+s) mod r with sign (-1)^(epsilon_sign+floor((j+s)/r)). I therefore split
one record before coefficient r-s and emit

    its s-coefficient suffix with sign (-1)^(epsilon_sign+1),
    then its (r-s)-coefficient prefix with sign (-1)^epsilon_sign.

`diagonal` performs those exact sequential copies and emissions. It keeps
one prefix buffer, one suffix buffer and one signed-component buffer across
records. It copies real and imaginary components in order, without exchanging
them. The signed complement-plus-carry loop implements exact two's-complement
negation. I adapted that loop from the retained `signed_phase.py`; the
polynomial split is the same identity used by Sagar Thakrar's PR3617 consumer.
Empty suffixes, E=0, E=r and negative exponents reduced modulo 2r use the same
rule. No coefficient oracle or random-access array enters the runtime.

Per record, I traverse O(r(P+2)) payload cells, including component buffers,
rewinds and clearing. I conservatively allow O(P^8) additional bit operations
for exponent and descriptor arithmetic. To justify that allowance, D<=A<P
and ell<=A+1<P; axis and flag loops have at most P iterations each. Every
window scan visits at most O(P) digits, and each retained Count addition,
copy, reduction, shift or product uses at most a quadratic bit-arithmetic
allowance on O(P)-bit operands. Even charging that quadratic allowance to
each iteration of three nested P-bounded metadata loops stays below P^8.
The binary counters use amortized linear increments/decrements over a scan.

Outer-row C may be arbitrary. Its countdown has amortized O(C) traffic;
I do not scan its full binary representation per coefficient. I pay the
one-time polynomial arithmetic on log C in setup. Since C dominates every
fixed power of log(C+1), and M is exponential in A, I can absorb that setup
in the final bound uniformly in positive C.

Thus one J round costs O(C M [rP+P^8]) plus polynomial setup, including its
complete output and consumed input. For fixed epsilon<1, ell grows as a
positive power of p, so r=2^ell eventually exceeds every fixed power of P.
The total diagonal cost is O(V ell). At bounded earlier p the same literal
code remains correct and costs a fixed constant per outer row; I enlarge
the asymptotic constant rather than remove those inputs.

## 5. Physical endpoint order

Within axis i, B consists of the disjoint transpositions

    (o_i+v, o_i+a_i-1-v), 0<=v<floor(a_i/2).

I place at most b complete edges in each batch. For each edge I emit both
directed rows, then use the retained physical stable radix sort to order
the rows by source position. Every batch has at most 2b listed positions,
within PR3619's domain. Its equal source/image sets and unique images follow
from disjoint transpositions; the router also validates that descriptor.
The router moves opaque records of 2(P+2)r bits, so it leaves coefficient
order and signed component order intact. All batches commute and their
product is B. I pay each complete materialized router return.

Put b'=min(A,b). There are O(A/b'+1) nonempty batches, and each costs at
most O(V (b'+1)^tau (log P)^(1+tau)). Hence the total B cost is
O(V A (b')^(tau-1) (log P)^(1+tau)). Since m<=b' and tau<1, this is at
most the routing term in section 1. I do not invoke the sparse-support
rate once on a Theta(p)-support permutation.

## 6. Fixed ownership and reusable lifecycle

Before reading input, `production_fourier` constructs one authenticated
`ComposedRoot`, its two fresh native instances and its existing owners,
one additional GridBoundary, 256 outer scratch tapes and one protected
Fourier output. I authenticate the whole PR3627 official export, including
its nested source archives and their unchanged notices. Its opener supplies
one Count/Tape cohort; I do not open a second native namespace.

I install the outer allocation scope only while doing outer work. Before a
root, router or grid call I suspend that scope, pass borrowed views, then
copy the returned packet into an outer lease. I clear and erase the child's
output marker before another call. The diagonal consumes the old outer
lease and returns its new outer lease directly. I close its three buffers
before continuing. `idle` checks the complete inherited child baselines.

I keep no list of payload rows, axes, rounds or batches. Each generator uses
a fixed tuple of Count roles. The dictionaries contain a fixed compiled set
of fields or diagnostic counters. The Python simulator may retain blank
backing arrays; after reuse I bound each role by its largest preceding
extent, without claiming that a smaller call shrinks it.

A conservative outer inventory has 16 persistent numerical roles, current
and descriptor/output leases, at most 24 loop/exponent roles, at most 32
temporary arithmetic roles and at most 16 sorting/component roles. This
totals fewer than 128 of the 256 compiled scratch tapes. Child scopes use
their own retained inventories; they do not borrow free outer roles.
Each packet buffer has O(V) bits and each numerical/descriptor buffer has
O(P+log C) or polynomial-in-P extent, which the complete packet pays in the
stated shape bands. I therefore retain O(V)+F_q total space. I include
returns to origins, dynamic-body erasure and marker restoration in time.

The constructor and port guards reject an unconsumed output. The finite
failure checks also cover malformed flag/packet extents and reuse after
those pre-callee failures. I retain the source distinction between successful
restoration and rollback after an interrupted inherited macro.

## 7. Complete time sum and scope of the exponent

Each H support batch has q<=b actual selected coordinates. Since A=Theta(p),
P=Theta(p), and log r=O(P), PR3627 applies to the entire addressed packet.
It supplies

    O(V [q^alpha log P + (q+1)^tau (log P)^(1+tau)]).

Across ell rounds I use at most O(ell D/m)=O(A/m) batches, each of size at
most m. This includes the top round and a final short batch. The exact
complete counts obey A>=D(ell-1) and ell>=2. I obtain the two H terms in
section 1. I add section 5's B bound, section 4's diagonal bill, O(V)
precision/input/output copies and polynomial metadata setup. The complete
packet absorbs the latter in the same fixed shape domain. I retain both
H terms until substituting that domain.

There m=Theta(p^s), s=min(epsilon,.997)>0. The root power is
1-s(1-alpha), while the routing power is 1-s(1-tau). Since alpha>tau,
their positive difference s(alpha-tau) absorbs the extra routing logarithm.
Also 1-epsilon < 1-s(1-alpha), so the ell term is smaller. At the cap,

    .997(1-alpha) = .00172380303,
    .997(1-tau) = 71784/41616125 > .00172380303.

The code remains defined for all admitted finite descriptors; the uniform
rate uses the fixed shape bands and the inherited explicit root/router
cutoffs. Any finite prefix below their maximum has a constant-size address
and coefficient geometry and a linear-in-C literal execution, so it does
not create an exceptional-input gap.

I have completed this synthetic interface. I have not physically joined it
to Gaussian production, CRT exposure, packed products, exact recovery or
both selected suppliers. The conservative PR2298 Gaussian dimension cannot
be retuned to .997 under its unchanged assumptions. Later bulk and fine-prime
interfaces change those assumptions. A future contributor must bind one
actual caller, its online precision and complete movement/normalization bill
before using this bound in an integer theorem.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including source-analysis agents. Apache-2.0. I claim no independent human
or formal-kernel verification.
