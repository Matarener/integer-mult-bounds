# A tiny conditional endpoint refinement

Let D be Jeremy Diviney's PR3148 construction on dcharb78's PR3133 words.
The entire finite construction, owner allocation, and charged profile remain D.
This proof changes only the rational lower endpoint and outer free parameters.
It is conditional on all of D's inherited physical and asymptotic obligations.

The paid histogram is
`{1:16376940,2:4821840,3:1567431,4:679320,5:147075,8:53280,48:282569}`,
with m=73, W=896*740 and rank mass 65088*740. The moment is

    M(b) = sum_r n_r*r*(73/r)^b / (73*W).

Every charged rank is positive and below m; hence M is strictly increasing.
The new rational endpoint is

    C = 0.001729777494678597011886903656817803609.

Three engines certify M(C)<1<M(C+10^-40). Two are the unchanged retained
engines. The separately implemented `binomial.py` imports neither of them
and evaluates no logarithm or exponential.

Positive-binomial enclosures already appear in earlier repository audits; see
the README credits. Independence here refers to this implementation versus
the retained endpoint engines, not a novel numerical method.

## Independent positive-binomial enclosure

Reduce x=73/r as x=2^k*y, 1<=y<=2. For z=1-1/y, 0<=z<=1/2 and 0<=b<1,

    y^b = (1-z)^(-b) = sum_{j>=0} t_j,
    t_0=1, t_{j+1}=t_j*z*(b+j)/(j+1).

All terms are nonnegative. Every successive ratio is at most z, so after
the term t_N the remaining tail is at most t_{N+1}/(1-z).
Use N=256 and scale S=2^256. At each multiplication, round the lower term
down and the upper term up to multiples of 1/S. Induction preserves the
term intervals. Sum their endpoints exactly as integers; add the upward
rounded tail to the upper sum. Multiply the intervals for y^b and k copies
of 2^b with outward rounding. Positive integer histogram weights preserve
the enclosure. The final normalized endpoints are exact Fractions.

The certificate retains both endpoints of each decisive interval. All 72
ratios at b=1/2 are additionally checked by squaring the interval endpoints,
at four truncation lengths. This uses exact rational ordering against x,
independently of either transcendental implementation. Removing the tail
fails the small-N algebraic control. Zero powers, invalid domains, the
next 10^-40 endpoint, and unpaid rank-one/rank-48 children are also checked.

## Outer transfer

Reconstruct the exact PR3148 admitted `outer/check_ledger.py` from its pinned
source and its recorded replica-width substitution; require the original
post-substitution digest. No inequality or rejection predicate is changed.
Supply endpoint_digits=40 as a new input. The checker's existing formulas give

    r0=10^-120, delta=(1025/1024)*r0,
    epsilon=1-delta, beta=1-3*delta,
    b=C-r0, q=C-2*r0,
    FLOOR=10^86, BACKOFF=10^-62.

All 63 strict rows and all 17 original rejecting controls pass. The unchanged
independent outer checker agrees. Since C*FLOOR is an integer and
0<C-epsilon*q<1/FLOOR, the derived saving is exactly

    K = C - 10^-62 - 10^-86.

The retained 12-stage carried-constant bootstrap is rerun at C, with its
conservative predecessor precision settings: all 47 strict rows and four
controls pass. That older balanced-transfer point is not substituted for K.
The modern transfer still requires the credited fine-prime padding,
gauge-free interior, explicit Strassen boundary and union schedule arguments.
The structured-boundary alternative is not invoked.

The pinned comparator is dataisfire's PR3361 at
`f9de2024916a347d939ed256a7a2e9e68d633684`:

    K_old = 0.0017297774946785970118869036568178 - 10^-57 - 10^-81.
    K-K_old = 3.609e-36 + 10^-57 - 10^-62 + 10^-81 - 10^-86 > 0.

This is only an arithmetic rounding-slack improvement. The endpoint was
already contained in PR3361's stored 40-digit bracket; the new contribution
is a separate binomial certificate and the finer outer release, not discovery
of a cheaper circuit or independent verification of all inherited assumptions.

## Reuse and conditional boundary

All source bytes and baseline receipt checks are bound through SOURCES.json.
PR3148's full stored-release checker and ten receipt/invoice corruption controls
run unchanged. This authenticates recorded evidence, not a new native replay.
The complete finite stock is 663,549, including 91 private zero buffers; the
required prefix is 1,479 within the paid 2,048-bit reserve. No operation,
child, frame, owner, copy, restoration, scalar coefficient or finite invoice
changes. Thus these fixed finite checks are unaffected by changing the proof
endpoint. Their source-bound admission premise is explicitly reused.

The session's separate fresh cold reproduction is documented in VALIDATION.json
when available; it is not silently inferred from a stored receipt. All-size
compiler, common-label/mutable-source realization, whole-call hosting,
precision/tape, exact recovery, analytic transfer and BIT H1-H5 remain conditional.
In particular, finite replay does not establish uniform compiler coefficient
and stock bounds, the retained bootstrap time constant, physical rational
SCALAR/COPY/CLEAR contracts, or zero-allocation contracts. PR3342 records the
uniform-coefficient gap without claiming a counterexample to the modern release.
Finite success is not a formal proof of the full multiplication theorem, and
the saving is not measured runtime. No maintainer acceptance is claimed.

Prepared by SovereignSteak with substantial OpenAI Codex assistance. Apache-2.0.
