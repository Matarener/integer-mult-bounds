# Stock-capped comparison and exact final borrowing

Fix compiled integers q>=2, m>r>=1, W>=1 and Q>=1, and a rational width
exponent alpha=A/C with C>0 and 0<=A<=C. Let e>=1 be the original width and
w=ceil(e^alpha). Keep w fixed during this invocation. Define

```
N = product_(i=0)^(m-1) (q^m-q^i),
b = W N q^(m^2(w-1)),
D(n) = 0                         for n<m,
D(n) = 1+D(r floor(n/m))          for n>=m,
S_0 = 1, S_d = Q b^d             for d>=1,
n(k) = floor((e-k)/w),
U = min(floor((e-1)/2), e-mw).
```

For prime q, N is the GL_m(F_q) order. The arithmetic refinement only needs
integer q>=2; it does not authorize a composite radix for a finite-field caller.
The covering-constrained plan requires 0<=k<=U and q^k>=S_D(n(k)).
This is the PR3486/3502 contract, separate from PR3503's strict-volume rule.

Hiroki Kumazaki's PR3502 implements the same minimum with full powers in
all trials. Its unchanged proof and selector are retained in comparison/,
with exact public head and SHA256 receipts in SOURCES.json. They supply a
before/after comparison, not a foreign ancestry pin or a runtime dependency.
The arguments below independently establish the capped refinement and bill.

## 1. Positive saturation is exact

For positive integers a,b and c>=1,

```
min(c, min(c,a) min(c,b)) = min(c,ab).                 (1)
```

If either factor is at least c, positivity makes each side c. Otherwise both
factors are unchanged. The positive-factor hypothesis matters; the shortcut
would fail for a zero factor paired with a saturated factor.

In power(base,exponent,cap), the scanned MSB prefix p has accumulator
min(cap,base^p). Equation (1) proves the update for the next exponent bit:
square the accumulator, then multiply by the positive base for a one bit.
The new accumulator is min(cap,base^(2p+bit)). Initially p=0 and the
accumulator is one, including when cap=1. The zero exponent also returns one.
The uncapped variant has the usual base^p invariant.

The implementation compares factors with the cap before multiplication.
If either is already at least the cap, it copies the cap. Otherwise the raw
product is less than cap^2 and is reduced immediately when needed. Thus a
cap of L bits permits at most 2L-bit product values, plus fixed tape markers.
The exponent is scanned and restored, and no input-dependent number is
decoded to a host integer. The public helper rejects an exponent aliased with
its base or cap, since borrowed-head preservation would otherwise be false.

## 2. The exact stock comparison and least plan

A trial computes its body, remainder, depth and stock exactly. It computes

```
trial_rows = min(q^k, S_D(n(k))).
```

The equality trial_rows=S_D(n(k)) holds exactly when q^k>=S_D(n(k)). This
also handles equality and unit stock. Rejected trials never construct q^k.

The child map is nondecreasing and strictly contracts each internal width.
Strong induction proves that D(n) is finite and nondecreasing. Consequently
n(k) and S_D(n(k)) are nonincreasing in k, while q^k is increasing. The
covering predicate is monotone on [0,U]. The definitions of U express exactly
strict fit 2k<e and at least m body atoms.

When e<mw, no legal interval exists. Otherwise the selector tests zero and U.
A passing zero is minimal, and a failing U proves no fit. In the remaining
case, bisection maintains a false lower and true upper endpoint. A midpoint
reduces the nonnegative integer gap by at least half, rounded up. Adjacent
endpoints therefore identify the least passing k after O(log(e+1)) trials.
The capped comparison gives exactly the same decisions as full arithmetic.

After that minimum is identified, one fresh trial recomputes every dependent
field. Only its rows field is replaced by exact q^k. Seven owned Counts and
the fit flag leave the selector. The no-fit sentinel keeps the true width,
zero depth/borrowed/body/remainder, and unit stock/rows; it describes no call.
The caller must release the seven Counts with close_plan after use.

## 3. Why final exact materialization is small

Let Sinit=S_D(floor(e/w)) and T=min{j>=0:q^j>=Sinit}. If a plan fits, its
least borrowing k satisfies

```
k <= T,                     q^k < q Sinit.           (2)
```

If U<T, any legal k is smaller than T. If U>=T, then T belongs to the legal
interval, and S_D(n(T))<=Sinit<=q^T. Thus T is feasible and minimality gives
k<=T. Finally, if T>0, minimality of T gives q^(T-1)<Sinit. If T=0, q^k=1
and q Sinit>=2. Both cases prove the strict inequality in (2).

This argument is required before claiming reduced storage. Capping the
trials alone would not bound an arbitrary final candidate's exact power.
The returned rows are the genuine radix power, even when q^k>S_D(n(k));
returning the saturated stock instead would violate the high-field contract.

## 4. Complete conditional setup invoice

Put h=1+ceil(log2(e+1)) and L=wh. Constants may depend on the compiled
q,m,r,W,Q,A,C; there is an additional fixed compilation/initialization cost.
For fixed r/m<1, D(n)=O(h), since every child is at most (r/m)n. The level b
has O(w) bits. Every exact trial stock has O(wh)=O(L) bits. Geometric fields
have O(h) bits. Equation (2) puts final exact rows in O(L) bits too.

A comparison, copy, normalization, clear, increment, subtraction or fixed
small multiplication/division scans O(length) cells. Retained Count.product
and long division cost O(length^2). An exponentiation with a t-bit exponent
costs O(t length^2), including the temporary raw products, comparisons and
cleanup. Count arithmetic and atom-width selection follow the exact PR2899
functions in the pinned encoded.py. count_math.py only omits physical source
activation and the unrelated old selector.

| Stage | Charged tape operations |
| --- | --- |
| Exact atom-width selection | O(h^3) |
| Bounds and level construction | O(h + h w^2) |
| One trial's geometry and contracting depth recurrence | O(h^2) |
| One exact stock power and Q multiplication | O((1+log(h+1)) L^2) |
| One stock-capped radix power | O(h L^2) |
| Endpoint tests, bisection and fresh final trial | O(h^2 L^2) total |
| Final exact rows and all remaining disposal | O(h L^2) |

Width selection has a fixed-power target of O(h) bits and O(h) bisection
steps. Its fixed-denominator powers already saturate at that target. The
level exponent w-1 has O(h) bits; its intermediate values have O(w) bits.
In every trial, k has O(h) bits and the positive cap is the exact stock.
There are O(h) trials, each closed before the next. The final exact power
is charged independently using (2), rather than assuming it remains capped.
Therefore

```
T_setup = O(h^3 + w^2 h^4),
S_setup = O(wh) binary cells on a fixed role inventory.               (3)
```

PR3502's compared bound is O(h^3+h^2(e+wh)^2) operations and O(e+wh) cells,
including its full rejected-trial powers. For fixed alpha<1, w=O(e^alpha),
so (3) removes that rejected-trial e term. For alpha=1, these conservative
asymptotic bounds agree. This is an analytic setup improvement, not a
measured elapsed-time speedup, numerical compiler constant or new exponent.
With the inherited e=O_q(log V), the new setup still adds a polynomial in
log V to the complete payload bill; that payload bill is not removed.

## 5. Role ownership and scope of resource evidence

Each Owned scope has a fixed finite vocabulary. It never accumulates a list
of trials or exponent bits. The main scope has at most eight Counts. A trial
has at most five retained Counts, and a power needs at most five additional
temporary roles beyond its borrowed inputs, including Count.literal's
construction tape. The no-fit path can temporarily overlap the main scope,
five completed-trial Counts, six sentinel Counts and one literal-construction
tape. Including the borrowed original, 24 roles conservatively cover every
phase, including inherited width selection and final uncapped materialization.
This remains within the predecessor's conditional 64-role setup inventory.

The observer watches both counts.Tape and cardinality.Tape, because literal
creation and Natural copies use different module bindings. It verifies blank
closed tape bodies and canonical heads. The actual finite plan suite peaks
at 20 roles. Its first incomplete observer watched only the former binding;
that failed diagnostic was retained and supplies no resource evidence.

For e=1000000, q=2, m=2, r=1, W=Q=1, alpha=0, the literal full selector
returns k=50, depth=19, exact rows 1125899906842624 and stock 609359740010496.
The largest observed runtime Count tape has 63 cells, including its markers.
The old upper-end trial would request q^499999, a 500000-bit integer by exact
arithmetic. That old request was not executed or timed. The observation
concerns runtime Count tapes, not Python object overhead, bytecode caches or
the host-integer checking oracle. RESULT.json records the separate direct
power and full-selector experiments.

Managed Python allocation, inherited arithmetic exception behavior and the
host source loader are not a proof of a production fixed-role transition
table. Successful returns, invalid public inputs and one injected failure
after a completed trial are checked. Arbitrary allocation failure or interruption
inside inherited arithmetic remains unclaimed. ENGINEERING.md records these
limits and all ten Power of Ten inspections.

## 6. Consumer boundary and remaining theorem obligations

The plan's mathematical fields equal the full-power selector's fields. Under
the existing completed-callee and cost premises it may be passed through the
ordinary execute_plan hook. No callback is installed and no Boolean payload
is run here. The two padded returns, genuine other high field, immediate
restrictions, source access, private buffers, pointwise row/spectator
restoration, every recursive child, routing, cleanup and output disposal
retain their complete separate bills and proof obligations.

The pinned PR2899 proof and the immutable PR2786/2753/earlier source closure
retain those authors' contracts and notices. The actual producer's selected
GL64 payload, uniform physical refinement, stock coefficients, full-cover,
completed leaves, precision/tape, outer transfer and complete multiplication
theorem are not supplied by (3). There is no new supplier, cutoff, kappa or
selected-frontier change. Independent human and formal proof-kernel review
are unclaimed.
