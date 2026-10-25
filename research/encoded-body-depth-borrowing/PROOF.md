# Count-tape refinement of actual-body borrowing

This result refines Nick Petalas's [PR3486](https://github.com/CrocSwap/integer-mult-bounds/pull/3486)
at `991861d40a1ebdbbf35be9adc1726e6af5b71e49`. Its byte-pinned proof is
retained in `predecessor/PR3486-PROOF.md`. The new contribution is the
`selector.py` implementation, its setup and ownership invoice, and bounded
checks against independent integer specifications. The monotonicity and
inverse-depth arguments remain PR3486's work.

The execution vocabulary is Jose Manuel's PR2899 Count selector and its
retained PR2809/PR2753 source closure. The consumer contract is Tekalign's
PR3264 ordinary one-factor adapter, using Nick Petalas's PR3246 NODE-guard
reserve. Source access, completed children, pointwise fresh-row restoration,
physical refinement and uniform caller costs remain inherited premises.

## 1. Contract and arithmetic refinement

Fix compiled integers `q>=2`, `m>r>=1`, `W>=1`, `Q>=1` and a fixed rational
width exponent `alpha=A/C`, with `C>0` and `0<=A<=C`. The zero exponent is
useful for reduced fixtures; the selected exponent is `17/10000`. For a
positive canonical input Count `e`, define

```
w = ceil(e^alpha),
N = product_(i=0)^(m-1) (q^m-q^i),
b = W*N*q^(m*m*(w-1)),
D(n) = 0                         if n<m,
D(n) = 1+D(r*floor(n/m))          otherwise,
S_0 = 1,  S_d = Q*b^d            for d>=1.
```

For a source-admissible prime `q`, `N=|GL_m(F_q)|`. Validation of the
arithmetic selector only requires integer `q>=2`; this does not admit a
composite radix to the selected finite-field construction.

The retained `encoded.atom_width` computes the stated ceiling using exact
integer powers and bisection. All subsequent values depending on `e` are
Counts. The host expressions for `N`, `q^(m*m)`, `W*N`, and the profile are
compiled source constants. Neither `e`, `w`, `k`, `D(n)` nor a stock value is
decoded to a Python integer by the selector.

The new `_power(base, exponent)` scans the canonical exponent from most
significant bit to least significant bit. If the scanned prefix has value
`p`, its invariant is `value=base^p`. Squaring and then multiplying by the
base exactly when the next bit is one changes the exponent to `2p+bit`.
The initial value is one, so this also handles zero. Count products copy
their inputs, and the exponent is rewound on return. The two inputs retain
their contents and origin positions. No recursion or list of exponent bits
is required.

For a trial `0<=k<=e`, `encoded.divide(e-k,w)` returns its exact quotient
and remainder. Repeated small division by `m` followed by multiplication by
`r` computes `D(n)`; this terminates because the child is strictly smaller
than each positive internal width. `_power` then constructs the exact
`stock=S_D(n)` and `rows=q^k`. At positive depth, `Q` is multiplied once.
At depth zero, stock is one. Every trial's body, remainder, depth, stock and
rows are recomputed from its own borrowing Count.

## 2. Least feasible borrowing

Let

```
n(k)=floor((e-k)/w),
U=min(floor((e-1)/2), e-m*w).
```

Exactly the integers `k` in `[0,U]` satisfy both `2k<e` and `n(k)>=m`.
PR3486 proves that, on this interval,

```
P(k): q^k >= S_D(n(k))
```

is monotone: `D` is nondecreasing, `n(k)` is nonincreasing, and the stock
sequence is nondecreasing. This selector implements that same predicate by
comparing its two exact Count values, without approximating logarithms.

If `e<m*w`, it returns no fit. Otherwise it constructs the nonnegative `U`,
tests zero, and then tests `U`. A successful zero is minimal. A failed `U`
rules out every candidate. In the remaining case the maintained endpoints
satisfy `0<=lower<upper<=U`, with `P(lower)` false and `P(upper)` true.
Their integer midpoint is strictly between them when the gap exceeds one.
Replacing the appropriate endpoint preserves the invariant and at least
halves the gap, rounded up. Thus the loop takes `O(log(e+1))` trials and
terminates at adjacent endpoints. Its upper endpoint is the least feasible
borrowing. This nonnegative formulation needs no encoded negative sentinel.

After bisection, a fresh final trial materializes all five dependent fields.
Together with `width` and `borrowed`, the seven returned Counts describe
exactly the accepted plan. They belong to the caller. A no-fit result has the
true width, zero depth/borrowed/body/remainder, and unit stock/rows. Those
sentinel fields describe no admitted recursive call. They cannot be reused
as stale fields from a rejected trial. `close_plan` releases all seven Counts.

Optimality is for this fixed width and the explicit covering constraint
`q^k>=S_D(n)`. It does not optimize width or all possible padding budgets.
In particular, the optimum need not satisfy `k=ceil(log_q S_D(n(k)))`;
PR3486's discontinuous-depth example explains why fixed-point iteration
would be incorrect.

## 3. Complete setup invoice

This invoice counts the retained sequential binary-tape operations, subject
to their existing physical refinement. Constants below may depend on the
fixed profile and radix. Put

```
h = 1+ceil(log_2(e+1)),
B = e+w*h.
```

Since `w<=e` and `r/m<1`, trial depths are `O(h)`. The bitlengths of the
input, geometric endpoints, body, remainder and depth are `O(h)`; the level
`b` has `O(w)` bits; and a trial stock has `O(w*h)` bits. The full `q^k`
may have `Theta(e)` bits even for a rejected trial with small `w`. It is
therefore included in `B`. The bound does not charge only the final stock
threshold or silently replace full radix powers by saturated comparisons.

A copy, comparison, small fixed multiplication/division, increment,
subtraction, normalization or clear costs `O(L)` at word length `L`.
Retained binary long division and `Count.product` cost `O(L^2)` when all
operands and results have `O(L)` bits. In the product, at most `O(L)` scanned
multiplier bits each cause an `O(L)` shift/add scan. An MSB exponentiation
with a `t`-bit exponent consequently costs `O(t*L^2)`. All intermediate
exponents are prefixes of the final exponent, including the doubled prefix
before a conditional multiply. Bases here are at least one, so no
intermediate product exceeds its final power.

The charges are as follows; they include the scans that rewind, normalize,
copy and clear each temporary.

| Stage | Bound in retained tape operations |
| --- | --- |
| Atom-width selection | `O(h^3)` |
| Geometric bounds and endpoint setup | `O(h)` |
| Construct `b` from the compiled `q^(m*m)` and Count exponent `w-1` | `O(h*w^2)` |
| One trial's quotient/remainder and depth recurrence | `O(h^2)` |
| One trial's stock power and one compatibility multiplication | `O((1+log(h+1))*(w*h)^2)` |
| One trial's full radix power `q^k` | `O(h*e^2)` |
| Endpoint tests, `O(h)` bisection trials and one final materialization | `O(h^2*B^2)` in total |
| Final returned-plan disposal and other remaining cleanup | `O(B)` |

For the first row, the fixed numerator gives an `O(h)`-bit target `e^A`.
Width bisection has `O(h)` iterations. The fixed-denominator powers saturate
at that target: an unsaturated product has at most twice its bitlength.
There are a fixed number of products per fixed-exponent power, each costing
`O(h^2)`. For the level row, there are at most `O(h)` exponent bits and
`O(w)`-bit intermediate values. For the stock row, `D(n)=O(h)` has only
`O(1+log(h+1))` bits. The conservative total also includes zero and upper
endpoint trials, discarded plans and the final complete recomputation.

The resulting bound is

```
T_setup = O(h^3 + h^2*(e+w*h)^2),
S_setup = O(e+w*h) binary cells on a fixed number of roles.
```

There is an additional fixed compilation/initialization constant for the
chosen `q,m,r,W,Q,A,C`; this is not uniform in these source parameters. For
the selected fixed exponent `0<alpha<1`, `w*h=O(e)`, so setup is
`O(e^2*h^2+h^3)` and uses `O(e)` cells. More generally `alpha<=1` gives the
still polynomial bound `O(e^2*h^4+h^3)`. With the inherited relation
`e=O_q(log V)`, either is a fixed polynomial in `1+log V`. Setup is charged
in addition to the consumer's full payload bill. This proof supplies no
numerical machine-step constant or new asymptotic multiplication exponent.

## 4. Fixed roles and successful-return ownership

Each `_Owned` dictionary has a fixed finite set of literal names; loop
iterations replace existing slots. A trial is closed before the next one,
and `_power` uses one replacement accumulator. Thus the Python bookkeeping
does not encode an unbounded table or a growing recursion stack.

The count includes the temporary tape used by `Count.literal`, not merely
the returned Counts. A Count product has at most four simultaneous internal
tapes: factor, scan, result, and either the result literal's temporary or the
copy used by addition. A power retains one old accumulator while that
product is constructed, so it needs at most five additional roles beyond
its borrowed inputs.

| Phase | Conservative simultaneous roles, excluding the borrowed input |
| --- | --- |
| Inherited width helper, before other selector fields exist | 10 |
| Main scope plus active trial and power temporaries | 17 |
| No-fit sentinel construction while the upper trial is still live | 19 |

For the second row, the main scope has at most eight live Counts, including
the midpoint. The trial retains at most four other Counts while creating
its rows power, which adds at most five. Its division path uses fewer roles.
For the last row there are seven main Counts, five completed trial Counts,
six sentinel Counts and one literal-construction temporary. Including the
borrowed input still leaves a conservative allowance of 24 roles. Width
selection has already returned before the later main/trial scopes overlap.

Under the retained fixed-role allocator these requests fit within the
predecessor's 64 setup-role allowance. This is an analytic upper bound on
successful well-formed executions, not an inference from a finite observed
peak. The input Count is preserved and rewound. Every other result is either
transferred once to the returned plan or closed by its scope; replacement
closes the old value after the new value is computed. The caller closes the
plan after use. This preserves the inherited successful-return marker and
lease convention. It does not promise transactional recovery from arbitrary
exceptions inside predecessor arithmetic or supply a new universal physical
compiler proof.

## 5. Conditional consumer implication and limits

For an admitted plan let `d=D(n)`, `R=q^k` and
`R'=ceil(R/S_d)*S_d`. The predicate proves `R>=S_d`, hence
`R<=R'<2R`. PR3486 and PR3264 then give the same NODE-guard implication:
the whole fresh quotient passes to children, completed siblings reuse it,
and compatibility `Q` is not charged again at each ancestor. Both padded
ordinary calls use this same reserve. The genuine other high field stays
`R`, and each padded return is immediately restricted to its genuine rows.
These implications retain the completed-callee, exact source, pointwise
restoration, restriction and ownership hypotheses of those predecessors.

No callback or default backend is changed here, and the verifier does not
run a selected-parameter Boolean payload. The setup implementation can be
passed to the existing plan hook only with its inherited consumer contracts.
The older simultaneous full-depth-format contract remains a distinct,
stronger requirement.

If PR3264's old `D(e)` selector fits, its borrowing is feasible here because
`D(n)<=D(e)` and the guard stock is nondecreasing. The new least borrowing
is no greater. The existing sufficient fallback cutoff therefore remains
sufficient, conditional on the same source contracts. This says neither that
all inputs fit nor that a smaller borrowing is a runtime speed factor.

Independent integer specifications and reduced literal Count replays are
finite evidence for this refinement. They do not discharge full-cover,
completed-leaf, source-access, uniform physical-cost, routing, precision,
outer-transfer or complete multiplication-theorem obligations. All children,
helpers, padding, restriction, output copies and cleanup remain charged in
the inherited consumer recurrence. No selected-frontier change is claimed.

Prepared by Hiroki Kumazaki with substantial OpenAI Codex assistance.
Predecessor attribution above is retained. Apache-2.0.
