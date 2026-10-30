# A scalar relation across the cut58 ADDRESS adapter

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped mathematical proof with exact finite corroboration.

## Operators and scope

Use the literal monomials supplied by unpaidmoon in PR #4149, following
Ross Richardson's cut58 source in #4082 and separable floor in #4086.
Those operator definitions are premises, not an audit target. We do not
replay either predecessor's group census, endpoint or 22f calculation.

Write the active bits as three ordered pairs
`a=(x0,x1)`, `b=(x2,x3)`, `c=(x10,x11)`.
Bits 4 through 9 are spectators. For bit pairs, a bar complements both bits,
and `a.b=a0*b0+a1*b1` is an integer dot product.
The one-coordinate maps send a basis vector at `(a,b,c)` to the stated
address, multiplied by `i^q`:

```text
       output address       q modulo 4
k      (bar(a),b,c)         3(a0+a1+b0+b1)+2 a.b+3
w      (b,a,c)              2a1+3(b0+b1)+2 a.b+3
t      (a,b,bar(c))         3c0+c1
p      (c,b,a)              0
```

The actual families are `K_f=i k^(tensor f)`, `W_f=w^(tensor f)`,
`T_f=i t^(tensor f)` and `P_f=p^(tensor f)` for every positive integer f.
Both displayed factors i are outside the tensor powers. Optional identity
spectators do not change any statement below. Products act right to left.

## New exact relation

For every positive integer f,

```text
P_f W_f K_f P_f W_f = -T_f W_f K_f P_f K_f.                 (1)
```

Here is a direct symbolic proof, without closing the generated group.
The left one-coordinate word `p w k p w` sends

```text
(a,b,c) -> (b,a,c) -> (c,a,b) -> (bar(c),a,b)
          -> (a,bar(c),b) -> (b,bar(c),a).
```

The right one-coordinate word `t w k p k` sends

```text
(a,b,c) -> (bar(a),b,c) -> (c,b,bar(a))
          -> (bar(c),b,bar(a)) -> (b,bar(c),bar(a))
          -> (b,bar(c),a).
```

Substitute the phases from the table at the input of each successive map.
On both sides their sum modulo four reduces to the same multilinear polynomial

```text
q = 3+2a1+3(b0+b1)+3c0+c1+2(a0*b0+a1*b1).                 (2)
```

For example, the left sum is `q_w(a,b)+q_k(c,a)+q_w(bar(c),a)`.
The right sum is `q_k(a,b)+q_k(c,b)+q_w(bar(c),b)+q_t(bar(a))`.
Expanding each complemented bit as `1-x` proves (2) over Z/4Z.
Thus the one-coordinate operators are exactly equal, including their phase.
The actual left word has outer factor i from its single K. The right word
has outer factor `i^3=-i` from its two K factors and one T. Tensoring the
one-coordinate equality and retaining these outer factors proves (1).
The minus sign is independent of f, including even f.

## Consequence for the tariff characters

Let chi be a homomorphism from the actual generated operator group to
`{+1,-1}` that fixes scalar operators. This requirement also holds for a
scalar-linear represented-algebra sign twist. Put

```text
chi(K)=(-1)^A, chi(W)=(-1)^B, chi(T)=(-1)^C, chi(P)=(-1)^D.
```

Apply chi to (1). Its left side has sign `chi(K)` because W and P each
occur twice. Its right side has sign `chi(T) chi(W) chi(P)` because K
occurs twice and chi fixes the scalar -I. Necessarily

```text
A+B+C+D = 0 modulo 2.                                    (3)
```

In particular, if the rank-zero ADDRESS adapter is required to have sign
`chi(P)=+1`, then `A+B+C=0`. The predecessor's three tests restrict to

```text
chi_W:   (A,B,C)=(0,1,0)       impossible with chi(P)=+1
chi_KW:  (A,B,C)=(1,1,0)       not excluded by this relation
chi_T:   (A,B,C)=(0,0,1)       impossible with chi(P)=+1.
```

Indeed, every scalar-fixing extension of either chi_W or chi_T, if an
extension exists at all, must give `chi(P)=-1`. This is the obstruction
needed for native tariff counting. A one-bank P response is free in polar
rank. A twist odd on P gives a nonzero full-bank gate defect at zero native
rank, so its odd-response count cannot retain the predecessor's positive
native-charge inequality. P's separate scalar or physical costs are not
claimed zero by this argument.

Equation (3) is necessary, not a presentation or a sufficiency theorem.
It leaves four of the eight sign assignments with D=0 unexcluded.
No extension of chi_KW or any other surviving assignment is constructed.
We do not claim that the full generated group has four such characters.

## Research consequence and limits

The separable 22f theorem of #4086 remains a cited result in its own
alphabet. A per-response tariff for the one-P sandwiches, proved in #4149,
does not extend its character count to arbitrary words in the enlarged
alphabet. Relation (1) proves a specific failure of that attempted route:
two of its three sign tests cannot keep the new free adapter even.

This supplies neither a cheaper six-bank word nor a counterexample to any
published lower bound. Other characters, invariants, changed tariffs or
explicit synthesis could still settle the enlarged problem. There is no
new supplier, native admission, kappa or selected-frontier change. Native,
compiler, ownership, precision/tape, BIT and analytic obligations remain.
Independent human and formal proof-kernel review are unclaimed.

## Executable evidence

The new verifier derives both word phases as Boolean multilinear
polynomials over Z/4Z, compares their coefficients with (2), and independently
applies the ten literal primitive occurrences to every one of the 4,096
twelve-bit basis addresses. It enumerates all 16 sign assignments and checks
(3). These are new relation checks, not a replay of the old response census.

Controls distinguish unsigned equality from (1), omitted P, discarded
global phases, moving those phases inside even tensor powers, and the
change that permits P to have a negative sign. Normal and optimized Python
use explicit exceptions. The all-f result follows from the proof above;
the finite basis check establishes the exact one-coordinate identity.
