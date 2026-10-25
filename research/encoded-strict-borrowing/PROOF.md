# Exact encoded strict-volume borrowing

Fix compiled integers q>=2, m>r>=1, W>=1 and Q>=1. Fix a rational width
exponent alpha=A/C with C>0 and 0<=A<=C. For original width e>=1, put

```text
w = ceil(e^alpha),
N = product_(i=0)^(m-1) (q^m-q^i),
b = W N q^(m^2(w-1)),
D(n) = 0 for n<m, otherwise 1+D(r floor(n/m)),
S_0 = 1, S_d = Q b^d for d>=1,
n(k) = floor((e-k)/w),
U = min(floor((e-1)/2), e-mw).
```

The atom width w stays fixed throughout the invocation. Prime q gives the
usual GL_m(F_q) interpretation of N. The arithmetic works for every integer
q>=2, without admitting composite q to a finite-field caller.

Nick Petalas's PR3503 proves that the least compatible padded row count
Rprime=ceil(R/S)S satisfies Rprime<2R exactly when S<2R. Its complete proof
is retained in PR3503-PROOF.md as a mathematical dependency, with its
consumer premises. The present contribution implements the complete least
borrowing selector for that changed predicate. Hiroki Kumazaki's PR3502
supplies the Count-selector lineage. PR3518 supplies positive saturation,
encoded arithmetic and its conditional setup proof. Its exact committed
export is retained in pr3518.tar, including all runtime and proof inputs.
PREDECESSOR.json gives the origin commit, path, Git blob, SHA256 and size of
each retained source. Scientific replay needs neither foreign Git objects nor
network access. None of these inherited results is relabelled as a comparison.

## 1. Integer strictness determines the cap

For positive stock S and nonnegative k, define H(S)=floor(S/2)+1. Then

```text
2 q^k > S  iff  q^k >= H(S)
          iff  min(q^k,H(S)) = H(S).                       (1)
```

The first equivalence is exact integer arithmetic, including even S. For
S=2R, the candidate R is rejected. For odd S=2R-1, R is accepted. Unit
stock gives H(1)=1 and therefore admits k=0 arithmetically. A consumer that
requires a nonempty high field must separately require k>0, as in PR3503.

strict_threshold copies the borrowed stock Count, divides by the compiled
constant two and increments. Both the original stock and canonical head
remain unchanged. A trial computes body, remainder, depth and stock exactly,
then uses H(S) as the positive cap for the inherited power routine.

For positive x,y,c, min(c,min(c,x)min(c,y))=min(c,xy). The retained PR3518
proof gives the MSB-prefix invariant min(c,q^p) for scanned exponent prefix p.
It also bounds a raw product by c^2 whenever neither factor is already capped.
Thus the trial rows are precisely min(q^k,H(S)), with no host decoding and
without constructing rejected q^k. The exact stock S remains available for
the returned plan and for a later padding adapter. Returning H(S) as stock
would be wrong.

## 2. Monotone bisection finds the least admitted plan

The child map n -> r floor(n/m) is nondecreasing and contracts by the fixed
factor r/m<1 whenever n>=m. Strong induction proves that D is finite and
nondecreasing. Since b>=1 and Q>=1, S_d, including d=0, is nondecreasing.
As k increases, n(k), S_D(n(k)) and H(S_D(n(k))) are nonincreasing, while
q^k is increasing. Equation (1) therefore defines a monotone predicate on
the legal interval [0,U]. This interval expresses exactly 2k<e and n(k)>=m.

If e<mw, the legal interval is empty. Otherwise test zero and U. A passing
zero is minimal; a failing U excludes every legal plan. In the remaining
case, bisection keeps a false lower and a true upper endpoint. Each midpoint
halves their positive integer gap, rounded up. Adjacent endpoints determine
the least passing k after O(log(e+1)) trials. The finite bound follows from
an initial gap at most e, rather than an assumed search convergence.

A fresh final trial recomputes all dependent values. Its capped rows are
replaced by exact q^k, and the exact comparison against H(S) is checked.
The result contains the same seven mathematical Count fields as the earlier
covering selector: width, depth, borrowed, body, remainder, stock and rows,
plus the Boolean fits flag. Its minimum can differ because the predicate
changed. The no-fit sentinel retains the computed width, zero depth,
borrowed/body/remainder and unit stock/rows; it describes no invocation.
The caller owns all seven returned Counts and releases them with close_plan.

PR3503 already proves that this minimum saves at most one radix digit when
both strict and covering plans fit, and can admit a previously rejected fit.
The new Count implementation realizes that theorem. These comparison facts
are inherited, not new mathematical claims.

## 3. Bound the exact final power before materializing it

Let Sinit=S_D(floor(e/w)) and t=min{j>=0:2q^j>Sinit}. If a plan fits, its
least k satisfies

```text
k <= t,                    2 q^k <= q Sinit.             (2)
```

If U<t, every legal k is smaller than t. If U>=t, t is legal and
S_D(n(t))<=Sinit<2q^t. Hence t passes and minimality gives k<=t.
For t>0, minimality of t gives 2q^(t-1)<=Sinit, so
2q^k<=2q^t<=q Sinit. For t=0, k=0 and 2<=q Sinit. This proves (2) in
both cases, including an optimum at U and strict equality in the preceding
failed threshold. The nonstrict final bound is intentional.

The bound is sharp for general positive stock: at q=2 and Sinit=2^j,
t=j and 2q^t=q Sinit. This sharpness statement concerns the threshold
identity, not an assertion that every such stock is a GL-derived profile.
Replacing the strict predicate by >=, or claiming a strict final bound,
would fail these equality cases.

This final-size proof is needed even though every rejected trial is capped.
A cap alone does not bound an arbitrary uncapped returned candidate. Also,
returning H(S) instead of exact q^k would corrupt the genuine high-field range.

## 4. Complete conditional setup bill

Put h=1+ceil(log2(e+1)) and L=wh. Constants may depend on the compiled
q,m,r,W,Q,A,C, with a separate fixed initialization cost. The exact arithmetic
and tape refinement premises are retained from PR2899 and PR3518.

The contracting child recurrence gives D=O(h). The level b has O(w) bits,
so exact stock has O(wh)=O(L) bits. H(S) has no more bits than S, and
forming it needs O(L) operations and one owned Count. Geometric Counts have
O(h) bits. Equation (2) puts the final exact rows in O(L) bits too.

The retained arithmetic charges O(length) for scans, copy, comparison,
normalization, clearing and fixed-small arithmetic, and O(length^2) for
schoolbook product and long division. A t-bit exponent scan with length-L
products, comparisons and cleanup costs O(t L^2). Each raw capped product
uses at most twice its cap's bit length. The exact final power's prefixes
are bounded by its final value, which is covered by (2).

The full bill includes all these stages:

- Original atom-width bisection with fixed-denominator powers costs O(h^3).
- Bounds and construction of b cost O(h+h w^2).
- Each trial's division, remainder and contracting depth scans cost O(h^2).
- Its exact stock power costs O((1+log(h+1))L^2).
- The strict threshold costs O(L), and the capped radix power costs O(h L^2).
- O(h) endpoint/bisection/final trials cost O(h^2 L^2) in total.
- Final exact radix materialization and all remaining disposal cost O(h L^2).

Consequently the complete setup bound remains

```text
T_setup = O(h^3 + w^2 h^4) tape operations,
S_setup = O(wh) binary cells on a fixed role inventory.    (3)
```

This extends PR3518's reduced setup bound to a different admission predicate;
it does not claim a second asymptotic improvement over that predecessor.
One extra threshold Count is live in a trial. The old conservative 24-role
allowance increases by at most one for that retained threshold, plus one
conservative spare role, giving 26 including the borrowed input. This remains
within the inherited conditional 64-role setup inventory. The literal census
observes a peak of 21 roles, but that measurement is not the all-domain proof.

Managed Python allocation and source-loader buffers are checker machinery,
not a fixed-role production microtransition table. ENGINEERING.md records
bounded deviations and limits. Successful execution, invalid public inputs,
and failure after a completed trial are checked. Arbitrary interruption or
allocation failure inside inherited arithmetic is not claimed transactional.

## 5. Evidence, decision and consumer limits

The direct integer census and independent inverse-depth slabs agree on 2880
cases. The literal runtime executes 990 complete plans with no_decode active,
checks all seven fields, input bytes/head and erasure. Of its fitted cases,
125 have q^k<S and therefore exercise the changed domain. The threshold
check covers all 4096 pairs S,R in [1,64], including 32 rejected equalities and 192 final-bound checks with 14 sharp equalities.

For e=1000000, q=2, m=2, r=1, W=Q=1 and alpha=0, actual Count execution
returns k=49, depth 19, rows 562949953421312 and stock 609359740010496.
The retained covering implementation returns k=50 in its earlier evidence.
The current strict selector observes at most 63 cells per runtime Count tape,
including markers. The uncapped upper trial would have a 500000-bit power by
arithmetic; it was not executed or timed. Neither statement is a runtime
speed factor, Python-heap measurement or selected GL64 payload experiment.

The decision is to finish this one encoded-selector handoff. No downstream
implementation expansion is justified by (3) alone. The two padded payload
returns, genuine other high field, immediate restrictions, pointwise row and
spectator restoration, completed recursive leaves, source access, fresh
fields, all children, frame/routing changes, private buffers, cleanup and
output disposal retain their full separate costs and proof obligations.
The old padding planner rejects q^k<S. A later caller must explicitly compose
the strict-volume padding adapter and its completed-callee premises; passing
this plan alone through the old ordinary factory is insufficient.

The complete selected stock coefficient, physical C0/source refinement,
full-cover, precision/tape, outer transfer and full multiplication theorem
remain open. There is no new supplier, cutoff, kappa or selected-frontier
change. Independent human and formal proof-kernel review are unclaimed.
