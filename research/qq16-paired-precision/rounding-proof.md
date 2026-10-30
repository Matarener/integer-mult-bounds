# Rounding on the changed query DAG

This audit consumes the frozen literal PR4015 and PR4106 words and the latter's
construction data. It executes no predecessor code. The endpoint semantics and
source authenticity are established by the central package and prior paid-word
replays. This note supplies numerical implications, not a caller admission.

## Exact common grid

The independent range induction gives both words the sufficient format

```
t=lambda-1,  q=h 2^(-9-3t),  W=P+28+6t.
```

Its premise is entry real and imaginary components in h Z, of magnitude strictly
below 2^P h, uniformly over all owners and payload coordinates. This includes
all quarter divisions and the pair-first Gaussian reference interiors. Every
stored intermediate is a q-integer, each division has the required divisibility,
and all numerators fit signed W bits. Consequently **both numerical references
have zero arithmetic rounding error**. No extra relative width is required by
the paired query. This conclusion does not choose the implementation or tariff
of a recursive H1 child.

## Relative fixed-point identity with approximate normalizers

There is also a narrower implication that does not require exact normalization.
Suppose both words use the same common component lattice q Z; all unit additions
are exact and do not overflow; covers/sign changes are exact; and each captured
normalizer is an isolated deterministic function of its input, returning q-grid
components. Its internal state must be restored or otherwise have the same
specified entry state at every call. The same corrected W input reaches each
port's same normalizer, so both words receive identical normalized arrays v_p.
Changing the order of independent normalizations has no effect under this premise.

For an equal-sign row of a pair, integer associativity gives

```
(Q + s v_p) + s v_q = Q + s(v_p+v_q),   s in {-1,1}.
```

For differing-sign rows the two deposits are unchanged. Reordering independent
source deposits likewise preserves their integer sum. Thus all eight query arrays
are bit-identical for arbitrary normalized q-integers, including approximate
ones. The response, quarter operations and suffix are unchanged, receive identical
inputs and therefore have identical results if their primitives are deterministic.
This is a relative statement: common existing rounding defects or failures of
private cleanup remain common; it does not prove they meet a caller tolerance.
It also does not allow the new pair sum to overflow. The exact-grid range theorem
supplies nonoverflow only in its stated exact-reference domain; an approximate
native contract must supply adequate range margins separately.

The checker runs the actual query scalar subsequences on 104 one-source integer
basis inputs, an 80-bit alternating cancellation input, and another mixed integer
input. These 106 regressions support the word binding; associativity proves the
statement for all lattice inputs. No floating-point associativity is assumed.

## Rounded primitive envelope

For a separate abstract rounded model, let epsilon bound each borrowed entry
component error, eta the absolute residual of each complete scalar ADD implementation relative to ideal `dst+c*src`, and nu the absolute output residual of each complete signed rank-one tensor-native call. The ideal coefficient c is exact. Eta includes all product/division, addition and storage errors together; scaling within the implementation need not be exact. Identifying eta with one rounding step requires a separate implementation proof. CLEAR, signed monomials and covers are exact. Neither
eta nor nu is silently identified with a chosen mantissa width. Native interiors,
overflow and private cleanup remain separate contracts.

Put x=2^lambda. A rank-one tensor Gaussian line has component-infinity operator
norm at most x: each coordinate layer has bound2, and there are lambda layers.
The proof uses this factor, never the invalid componentwise factor1 inferred from
unitarity. At each logical cut propagate a polynomial with nonnegative rational
coefficients in x, linear in epsilon, eta and nu:

```
CLEAR: E <- 0
ADD c: E_dst <- E_dst + |c| E_src + eta
signed native: E_dst <- x E_dst + nu
cover / signed monomial: unchanged
```

Triangle inequalities prove this enclosure for all lambda>=1, including fully
correlated rounding errors. The independent interpreter runs both complete words.
Their 224 endpoint polynomials are equal coefficient by coefficient (six distinct
classes, all fields explicitly listed in ROUNDING.json). Their whole-word logical
cut coefficient envelopes are also equal:

```
entry:  (445 + 14115 x + 2964 x^2 + 17784 x^3) epsilon
scalar: (16380 + 14451 x + 19104 x^2 + 17784 x^3) eta
native: (14121 + 2964 x + 17784 x^2) nu.
```

This envelope takes the maximum of each coefficient across all visited logical
writes; it need not be simultaneously attained and is not an optimal norm. It
excludes approximate native interiors, whose contract is supplied separately.
Each query row has52 source coefficients. An equal-sign pair injects one shared
sum residual and one deposit residual, giving2eta, exactly the conservative bound
for its two original deposits. Differing rows still have two deposits. Therefore
each channel's query-accumulation bound remains52eta. A shared residual is present
in several channels; no independence or square-root aggregation is used.

The endpoint envelope does not establish exact private-helper restoration in a
rounded execution. The exact-grid path has no such scalar arithmetic defect;
otherwise restoration and actual native guarantees must be checked separately.

## Actual changed-site floating counterexample

A distinct model rounds every scalar query addition to a binary significand of
precision2, nearest with ties to even, with unbounded exponent. Supply exact
normalizer outputs at one observed real component as

```
v_76=4, v_87=1, v_92=1; all other v_p=0.
```

The checker executes the literal query scalar events, replacing each paid
normalization output by that supplied value. In PR4015's source order Q0 receives
4,1,1 separately. RN(4+1)=4 at a tie, twice, so Q0=4. PR4106's pair(87,92) forms
RN(1+1)=2 at event1729 and adds it to Q0 at event1730, giving RN(4+2)=6. The full
query vectors are respectively `(4,3,4,-2,0,0,0,0)` and `(6,3,4,-2,0,0,0,0)`.
The precision2 rounder is exact rational code, including ties-to-even.

This is a counterexample to automatic bitwise transfer of the query arithmetic
under floating rounding. It is intentionally a query-cut example with supplied
normalization outputs, not a full rounded recursive-caller counterexample. The
invertibility of exact normalizers explains the algebraic availability of these
arrays, but does not establish their reachability under a particular rounded
prefix or recursive native implementation. It is compatible with the equal
conservative error envelopes and with the exact fixed-point result above.
