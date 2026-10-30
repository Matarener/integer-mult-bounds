# The optimal boundary fraction under bare Pascal iteration

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped mathematical proof with an exact finite numerical certificate.
Independent human and formal proof-kernel review are unclaimed.

## 1. Declared model and predecessor boundary

Yiyang / Lyy-iiis's PR #5037, retained in
`research/bounded-lane-border-core/core/PROOF.md`, Section 7, gives the formal
population recurrence

```text
d'_h = d_h + d_(h-1),   0 <= h <= H,   d_(-1) = 0.
```

The term above grade H is omitted. The source already observes eventual
top-grade domination. We take that recurrence and its published local invoice
as premises. We do not establish a native implementation of the recurrence or
recount the source word. The new result optimizes the boundary fraction over
every starting population and certifies an exact failure depth.

Let d be any nonzero vector in R_(>=0)^(H+1), let K=I+S where S shifts grades
up by one and truncates above H, and put d^(e)=K^e d for an integer e>=0.
Let D_e be the sum of its entries and z_e its grade-H entry.

We declare the homogeneous local-ledger extension explicitly. Each unit of
population receives the same complete local target and paid profiles T and P;
each top-grade unit loses 112 rank-17 productive targets. At exponent t the
signed surplus is therefore

```text
A(t) = sum_k T_k k^t - sum_r P_r r^t,
B(t) = 112 * 17^t,
M_e(d) = A(t) D_e - B(t) z_e.
```

This is a scalar accounting relaxation of a potential recursive caller.
The source does not prove that actual graded main/helper inventories realize
this homogeneous extension. The theorem below concerns this declared ledger,
not arbitrary implementations of the border core. Extra costs can only worsen
this ledger when its productive contract is held fixed. Changed profiles,
new productive outputs or paid grade-reset mechanisms require a new analysis.

## 2. Sharp population theorem

Use binom(e,k)=0 for k>e. For every H,e>=0 and every permitted d,

```text
z_e / D_e >= q_H(e),
q_H(e) = binom(e,H) / sum_(k=0)^H binom(e,k).
```

Equality is attained simultaneously at every depth by d=(1,0,...,0).
If e>=H>=1, equality holds exactly when all initial grades above zero vanish.
For fixed H>=1, q_H(e) is zero for e<H, strictly increases for e>=H,
and tends to one as e tends to infinity.

**Proof.** Since S^(H+1)=0, the binomial theorem gives

```text
d^(e)_h = sum_(j=0)^h binom(e,h-j) d_j.
```

Write a_l=binom(e,l) and s_l=sum_(k=0)^l a_k. The contribution of initial
grade j to z_e is a_(H-j) d_j and its contribution to D_e is s_(H-j) d_j.
Consequently z_e/D_e is a weighted average of the ratios a_l/s_l, with
nonnegative weights s_(H-j)d_j.

If e<H, the claimed lower bound is zero and the pure lowest grade attains it.
Suppose e>=H. For 0<=l<=e,

```text
s_l/a_l = sum_(j=0)^l product_(a=0)^(j-1) (l-a)/(e-l+1+a).
```

For l<e, replacing l by l+1 increases every nonempty product already present and
adds one positive term. Thus s_l/a_l strictly increases with l, so a_l/s_l
strictly decreases. The weighted average is minimized at l=H, which
corresponds to initial grade zero. Strictness gives the equality case.

For e>=H, the same expression with l=H shows that 1/q_H(e) strictly
decreases with e when H>=1: every nonempty product decreases. These products
tend to zero, so q_H(e) tends to one. The transition from e=H-1 to e=H
is from zero to a positive fraction. This proves every assertion. For H=0,
q_0(e)=1 and the population ratio is identically one. QED.

## 3. Exact local-ledger depth limit

Suppose B>0. The largest possible surplus per unit final population is exactly

```text
max_(d != 0, d >= 0) M_e(d)/D_e = A - B q_H(e).
```

The pure lowest-grade vector attains it. Thus a positive local surplus is
possible exactly when q_H(e)<A/B. In particular, if 0<A/B<1, every fixed
height eventually fails, even after optimizing the initial populations.
This sharpens the source's qualitative domination observation to an exact
decision criterion at each depth.

For the cited PR5037 invoice, take

```text
T = {4:56, 7:14, 8:94, 9:652, 17:224},
P = {1:4656, 2:920, 3:1386},
t = 4983/5000,   H = 65.
```

The integer-only certificate in `verify.py` proves

```text
0.015196119 < A/B < 0.015196120,
q_65(110) < A/B < q_65(111).
```

Therefore the first impossible depth is **111 bare Pascal steps**. Through
depth 110 the algebraic ledger has an attainer with strictly positive
surplus; this is not an attained native construction. At every depth at
least 111, every nonzero nonnegative initial population fails strictly.
Depth here counts applications of K to the initial population, not actual
recursive calls or the logarithmic depth of a multiplication algorithm.

For the source's equal-population start d=(1,...,1) with 66 entries, the
initial population has D_0=66 and z_0=1. Its first successor is
(1,2,...,2), with D_1=131 and z_1=2. Exact enclosures give

```text
  5.551472 < 66 A - B     <   5.551475,
-17.553092 < 131 A - 2 B < -17.553089.
```

Thus the equal-population one-shot bill already fails on the first bare
reuse. Enlarging the initial populations can delay failure, but cannot
pass depth 111 in this height-65 ledger. This says nothing against a
changed matching, replenishment, filtration height or local invoice.

## 4. Exact numerical certificate and finite checks

No floating-point transcendental value is trusted. Rank one is exact. For
each of the other seven distinct ranks in T and P, the checker bounds
r^(4983/5000) between L/s and U/s, where s=10^12. It finds adjacent integers
L,U by at most 48 bisections and directly verifies

```text
L^5000 <= r^4983 * s^5000 <= U^5000.
```

Monotonicity of the positive 5000th power proves the enclosure. Signed
interval addition gives bounds on A and B. Exact rational comparisons with
the binomial fractions certify the two depth signs and the equal-start
failure. The printed intervals are rounded outward to denominator 10^9.

The separate finite population engine applies the recurrence literally and
compares it with the binomial formula, its optimal ratio and equality case
for all nonzero vectors in {0,1,2}^(H+1), H=0,...,4, e=0,...,12.
Pure-grade attainers and monotonicity through depth 256 are also checked.
Invalid inputs and four false extrapolations have explicit rejection
controls. These finite checks corroborate the proof; the universal
quantifiers come from Sections 2 and 3.

Every run prints a generated JSON receipt binding all six package files
and the two cited inputs by SHA256. The receipt is stdout, so replay writes
nothing into the checkout. The source numerical/operator verifiers are
never imported or executed. Their mathematical premises retain Yiyang's
and the underlying native/compiler contributors' credit.
