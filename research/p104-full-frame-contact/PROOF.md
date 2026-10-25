# One full-frame contact in the productive P104 caller

This package changes one contact in the exact word of
[PR5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544), at
`e2a6cce2f9db5a2c5f9714f4b9e5292dd3a10581`. The new conditional endpoint is
`kappa = 304117/100000000 = .00304117`. The gain over PR5544 is
`3/5000000 = .00000060`. The selected record stays unchanged.

The five source assumptions remain: native all-column implementation,
owned erasure, the uniform compiler, precision and tape costs, and analytic
recovery. The ideal operator proof and the complete conditional price are
given below. The enormous uniform word and the rounded integer multiplier
are not materialized.

## Exact source change

Let `A=span(30,70,429)`, `B=span(13,19,70,416)`, and `D=F_2^9`.
These are source frames 739, 240 and 127, with `A < B < D` and dimensions
3, 4 and 9. The zero-based source events are:

| Event | Source instruction |
| --- | --- |
| 16798 | Move register 345 from A to B |
| 16799 | `341 -= 345`, in B |
| 16800 | `341 *= -1`, in B |
| 17061 | Move register 341 from B to D |
| 17067 | Move register 345 from B to D |

Register 341 is already in B at event 16798. It has no other read or write
before event 17061. Register 345 has no other read or write between events
16798 and 17067. The constructor checks the complete intervening event lists,
including source operands. Other registers can retain their original order.

Replace event 16798 by moves `341: B -> D` and `345: A -> D`. Run events
16799 and 16800 in D. Remove events 17061 and 17067. Keep all other events
byte-equivalent as JSON records. The scalar coefficients, scalar order,
public boundaries, independent inputs and owned lifetimes stay the same.
The word has 25,310 events, one fewer than the source.

## Uniform operator identity

Use the source chart Phi_V at frame V. Put
`T_VU = Phi_V Phi_U^(-1)`. On logical values x and y, the old two-register
fragment ends with

```text
register 341: Phi_D (y - x)
register 345: Phi_D y.
```

The new fragment first places both values in chart D, then performs the same
subtraction and sign. It has exactly these outputs. Equivalently, a common
linear transport on both operands commutes with a scalar ADD and SCALE.
The checked read intervals permit this equality inside the complete word.
The next reads of each register use D in both words.

For every positive digit-column count, replace each chart by its prescribed
tensor power. The common-chart identity is still valid. Scalar coefficients
remain outside tensor powers. No sum of operators is tensor-powered.
The source native compiler lowers every candidate MOVE and helper boundary.
Its separate Gaussian interpreter checks signed Pauli images and absolute
phase. In particular, the new `A -> D` child has rank six, with its actual
monomial adapters. It is not an uncharged change of coordinates.

The sparse rational interpreter checks all 743 endpoint rows. The independent
reverse interpreter uses dense integer columns and binary denominators. Both
cover all 552,049 public and owned coefficients. All 735 public inputs remain
arbitrary. The eight owned lifetimes still start and return at the declared
zero states, with peak occupancy one.

## Complete cost and transfer

The old fragment pays H1 + 2H5. The replacement pays H5 + H6. Thus

```text
local paid delta:    -H1 - H5 + H6
complete paid delta: -18H1 - 18H5 + 18H6
target delta:        zero at every rank.
```

For `0 < t < 1`, strict subadditivity gives `6^t < 1 + 5^t`. Therefore the
complete signed recursive moment is strictly smaller at every such power.
Rank mass is unchanged. The standard signed-invoice comparator gives the
same conclusion for the actual complete histograms. This comparison uses
all helper targets and all thin and idle jobs, not a local cost alone.

The new local profile is

```text
{1:2428, 2:557, 3:389, 4:112, 5:107, 6:17, 7:13, 9:1}.
```

All 527 helper targets keep their source ranks
`{4:51, 5:36, 7:24, 8:122, 9:294}`. The 104-port caller, both orientations,
its 18 forward source invocations, 15 thin queries, 15 whole idles and
32 main banks are unchanged. The source's signed exchanges and central-square
translations still supply all backward interfaces. The full bill has 69,912
paid calls and 12,814 productive fields, with rank surplus 760. The unused
helper 711 keeps both its paid H9 and its productive H9.

`pricing.py` adapts the pinned PR5544 price engine. Its only mathematical
changes are the new paid-call count, claimed and tested endpoints, and the
comparison endpoint. It recomputes both complete histograms by two counts,
the raw crossing with rational intervals, and a second independent moment
enclosure. The tested saving is `.003041171`. Cutoff 17, floor 18, tail offset
1/5, reserve `10^-10`, power 1024 and logarithm power 1000 remain fixed.
All completion, splitting, capacity, compiler-grid, BIT-stock and 58 outer
predicates must pass. `RESULT.json` records their exact rational values.
The fixed-invoice crossing and its remaining headroom are reported there;
no global optimum or exclusion of other words is claimed.

The new crossing is in `(.00304117181649, .00304117181650)`. Its increase
over the source crossing is in `(.00000059374018, .00000059374020)`.
The claimed endpoint is below the new crossing by between
`.00000000181649` and `.00000000181650`. The strict compiler gap is
`1/7000000000`; its independently checked integer height is
`H=337848000000000`, with test exponent 48264. The previous grid point fails.
The stated endpoint gain `.00000060` also reflects the different safety
margins below the two crossings; it is not the exact raw-root difference.

This mixed-target caller is outside the historical fixed-rank packing model
in `research/complex-local-word-ceiling/ceiling.py`. It retains independent
productive helpers and targets of unequal ranks, rather than one target rank
and the old hosted coverage law. The replacement bound is the exact crossing
of this complete fixed invoice. The endpoint attains between
99.9999402697% and 99.9999402701% of that crossing.

For this invoice the crossing is unique for `0 < kappa < 1`. To see this,
put `t=1-kappa` and divide its signed moment by `6^t`. The signed coefficients
at ranks 1 through 6 are negative; those at ranks 7 through 9 are positive.
Each of these normalized terms increases with t, except the constant rank-six
term. The other terms are 416 copies of `((r+1)/6)^t-(r/6)^t` for
`r=16,24,...,64`, 208 copies at r=72, and `208*(145/6)^t`.
They also increase for `t >= 0`: the derivative of each difference is positive
because `x^t*log(x)` increases for `x > 1`. The full normalized moment is
strictly increasing. Its values at t=0 and t=1 have opposite signs, since
the count difference is -57,098 and the rank surplus is 760. Thus the upper
crossing endpoint bounds the saving allowed by this fixed invoice. It does
not bound a changed word, caller, target contract or invoice.

The local scalar program is unchanged. There is one fewer native call and
no new owned field. Native ranks stay at most nine locally; complete maximum
target and child ranks stay 145 and 72. The source's finite bound of fewer
than 26,000 events, scalar growth factor below `2^16` per event and total
local Gaussian rank 5,894 still applies. These bounds fund the reordered
prefix as well as the old prefix. All caller routes, private COPY paths,
returns, normalizers and matching remain in the complete ordinary allowance.
No precision or machine-operation cost is set to zero.

## Controls and limits

The checker rejects a one-operand retiming, a changed subtraction sign, an
intervening source read and an omitted paid charge. It also reruns the source
caller controls, exact phase control and adverse compiler/outer controls.
The dependency hashes are checked before the source modules are imported.

These are author-side exact checks. They are not independent human review or
a proof-kernel verification. The source interpreters and mathematical
framework remain credited dependencies. No merge or selected-frontier update
is part of this contribution.

Credit Ali Romman's PR5544 for the productive caller; Gareth Davidson's
PR2305, David Arias's PR2152 and Cinna Davis's PR2219 for the composed word.
The P104 shared-chart and dual-ADD retiming packages already use the standard
two-operand identity. The new result is this literal contact and its complete
conditional endpoint. Retain Jacob Alan Sussman's productive recursion,
Cinna Davis's controller, zxv's compiler and outer machinery, Cao Yifan's
pricing lineage, and all geometry, native, COPY and analytic source notices.
Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
