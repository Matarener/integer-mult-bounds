# A smaller joint interval envelope from protected boundaries

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof. The proof uses the cited prefix-entry and
squarefree-interval lemmas as premises. It does not audit those predecessors.

## Contract and theorem

Use Chafik Boukhalfa's PR628 balanced dirty word on n>=1 factors, a protected
source x, an unread target y and h=ceil(log2 n) arbitrary dirty scratch registers.
The scratch register for each depth is reused by sibling calls. All cuts are
complete ideal-leaf boundaries. Let P_t be any prefix of either word orientation.
The full state has the maximum of the individual register norms.

Put

```text
K(0)=2,
K(h)=h^2+2h+3 for h>=1.
```

For every ordered pair of cuts s,t, the free noncommutative coefficient
absolute row sum of P_t P_s^-1 is at most K(h). Consequently:

1. For arbitrary contractive operator factors, without commutation,
   ||P_t P_s^-1|| <= K(h).
2. If the factors commute and every subset product, including the empty one,
   has norm at most G>=1, then ||P_t P_s^-1|| <= K(h) G.

For h>=1 the coefficient envelope improves the squared-prefix bound by
exactly (h+2)^2-K(h)=2h+1. It is not claimed sharp. Arham Tahir's PR1374
lower bound floor(h^2/2)+h+2 remains compatible with it. This does not change
the exact destination-only result of philippeVV's PR2177.

## Predecessor inputs

Hanson Sun's PR1085 proves that every entry of P_t and P_s^-1 is zero or
one signed monomial, and that the source row and target column are identity.
Its retained text is at
`research/single-register-interval-transport/vendor/PR1085-PROOF.md`.
We consume those assertions without replaying or re-proving them.

Charles Bethin's PR1278 proves that every surviving interval monomial uses
each factor at most once, including both cut orders, both orientations and
shared deeper scratch. This is needed only for conclusion 2. Its retained
text is `research/commuting-interval-audit/PROOF.md`.

## New block inequality

Order registers as source, the h scratch registers, target. The protected
source and unread target force the following shape for P=P_t and Q=P_s^-1:

```text
P = [ 1  0  0 ]       Q = [ 1  0  0 ]
    [ a  B  0 ]           [ c  D  0 ]
    [ b  e  1 ]           [ d  f  1 ].

P Q = [ 1        0       0 ]
      [ a+B c    B D     0 ]
      [ b+e c+d  e D+f   1 ].
```

Here a,c are h-by-1, B,D are h-by-h, e,f are 1-by-h, and b,d are scalars
in the free algebra. Every displayed entry of P and Q has coefficient mass
at most one. Coefficient mass is subadditive and submultiplicative because
concatenation multiplies words and cancellation can only reduce mass.

A scratch row of Q has at most h+1 occupied entries, since its target entry
vanishes. Its source row has mass one. Therefore any scratch row of P Q has
mass at most

```text
1 + h(h+1) = h^2+h+1.
```

The target row of Q has mass at most h+2. The target row of P Q is the sum
of b times Q's source row, h terms e_j times Q's scratch rows, and Q's target
row. Its mass is at most

```text
1 + h(h+1) + (h+2) = h^2+2h+3.
```

The protected source row still has mass one. Taking the largest row gives
the theorem for h>=1. This argument uses both boundary restrictions; it
does not multiply the global row bound h+2 by itself. It does not assume
fresh scratch, commuting coefficients, or an ordering of s and t.

When h=0, n=1 and there is one leaf. Every interval is identity or that
leaf shear in either sign. Its coefficient row sum is at most two, proving
the separate K(0)=2 case.

For conclusion 1, every formal word evaluates to an operator of norm at
most one, by submultiplicativity of the contractive factor norms. Summing
the row coefficient masses gives K(h). For conclusion 2, use PR1278's
squarefree conclusion before substitution. Commutation turns each surviving
word into a subset product with norm at most G. The same coefficient bound
gives K(h)G. Individual factor bounds by G alone would not justify this step.

## What the computation checks

The verifier multiplies generic protected-boundary matrices with independent
formal entries. It obtains the exact abstract row counts above for h=1..8.
These matrices are not asserted to be prefixes of a common word, so equality
in that calculation is not a sharpness claim for actual dirty intervals.
The strict-gain identity is checked with exact integers at h=1..10000.

A separately written iterative emitter expands the balanced word for six
factor counts, with both signs and the same physical scratch at each depth.
It propagates every nonempty interval directly over the free noncommutative
algebra and checks the new inequality. It also checks the full arbitrary-dirty
endpoint and literal inverse order. It imports no predecessor implementation.
No predecessor extremal census or scalar sign witness is a deliverable here.

Abstract controls remove each protected boundary or the entry-size premise
and require failure of the new bound. Invalid argument controls check the
finite executable capacities. These are not claimed to be realizable dirty
word counterexamples. A separate check keeps the bound labelled nonsharp.

## Limits and next implication

The all-size statement rests on the written block proof and the cited
lemmas. Computation only corroborates its fixed finite fixtures. No formal
proof-kernel or independent human review is claimed. Internal rounded leaf
operations, nonlinear errors, negative-leaf preimages, preparation, physical
movement, stock, precision and a complete caller invoice are not supplied.
The five selected framework assumptions remain. No new kappa follows.

The original sharp-constant question remains open between the cited lower
family and this smaller upper bound. A further improvement must exploit
relations between the two actual prefixes, beyond these protected boundaries.
