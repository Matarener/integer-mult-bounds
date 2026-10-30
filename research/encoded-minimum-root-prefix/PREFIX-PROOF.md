# Minimum row-reservation prefix at the actual root core

This is a conditional root-interface theorem and an exact reference compiler.
It concerns the original 73-dimensional physical backend retained by QQ16.
It does not install a production Count frontend or prove a new kappa.

## 1. Source contract and changed parameter

The retained RootPlan has precision p>=2, global width
`d=floor(p^(997/1000))`, spacing `K=floor(d^(1/500))`, selected width n<=d,
`G=4 ceil(log2 p)+6`, and H=dG. Keep these fields and

```text
qF=ceil(2H/K),  qB=ceil(H/K),  M=n-qF-qB,
F=14336 Gamma,  Gamma=2^1296 product_(j=1..36)(2^(2j)-1).
```

The selected-C backend has ranks {1,2,3,4,5,7,8,48}. It tests w<73 or
w^1000<d before its remainder step. PR5515 supplies the exact depth

```text
T=max(73,ceil(d^(1/1000))),
D(w)=0 for w<T; otherwise D(w)=1+D(48 floor(w/73)).
```

D is nondecreasing. All reached selected-C row divisions are positive and
exact if and only if F^D(w) divides the incoming rows. This is inherited
from PR5515; it is not a new depth theorem. Native/Ordinary internals retain
the source's complete endpoint and admission contracts.

The old plan uses `q0=2642 D0(d)`, where D0 ignores the height cutoff and
2642=ceil(log2 F). It then creates **2^(K q0)** original rows. Thus q0 is
an axis count, not a bit count. Every reserved axis already supplies K row
bits. A shorter depth alone does not use this large difference.

If M<=0, use the direct root leaf. Assume M>0 below. For a proposed integer
q with 0<=q<M, the remaining core has width M-q. Define

```text
S(q)=F^D(M-q),       R(q)=2^(Kq),
P(q)=ceil(R(q)/S(q)) S(q).
```

P is the padded row count. We retain the original strict volume promise
`P(q)<2 R(q)`, complete prefixes, complete zero padding, and exact division
by S(q). This is the format in which the minimum below is proved.

## 2. Exact feasibility and minimum

For positive integers S,R,

```text
ceil(R/S) S < 2R    if and only if    S < 2R.
```

If S>R, the left side is just S<2R. If S<=R, then
`ceil(R/S) S < R+S <=2R`, including equality R=S in the second inequality.
Thus the equivalence holds. For R=2^(Kq), it becomes

```text
floor(log2 S(q)) <= Kq.                                      (1)
```

This includes powers of two with the correct strict boundary. The source
condition R>=S is sufficient but stronger: a stock between R and 2R also
fits. The reference compiler uses `(S.bit_length()-1)`, with S=1 allowed.

The left side of (1) is nonincreasing in q, and the right side is increasing.
There is a unique least feasible q. The value q=M-1 is feasible because its
core has width one and S=1. A smaller known upper bound is

```text
U=min(M-1, ceil(2642 D(M)/K)).
```

If the second branch applies, K U>=2642 D(M)>=log2 S(U). The first branch
was already proved feasible. Binary search between the failed sentinel -1
and U gives the exact minimum q*. Its certificate is the exact power-bit
comparison at q* and the failed comparison at q*-1, unless q*=0.
This proves the compiler for all inputs in the stated format; a finite
width scan is not used as its proof.

No smaller prefix in this same complete-row format can keep the strict
factor-two volume bound. A different row encoding, a different permitted
volume factor or a different supplier can have a different minimum.

## 3. Bind the complete root interface

Set the plan's q0=q*, depth=D(M-q*), and stock=S(q*). Recompute all dependent
fields with the source formulas. Keep qF,qB and all global precision fields.
The actual consumers are recorded in CONSUMER-INVENTORY.json. Both a lexical
pass and an AST literal pass cover all 32 Python files in the retained
physical-complex-controller directory. Tests are distinguished from production.
The package pins all those files; it does not rely on their moving checkout.

The production use chain is complete within this source module:

1. RootPlan.compute derives Q0, original_rows, stock, padded_rows, core_width
   and row_bits. No independent downstream depth consumer exists there.
2. RootLayer.reserved_leaves uses q0+qF at the high selected end and qB at
   the low end. These leave exactly M-q0 core axes.
3. RootLayer.fast_core passes both row counts to RowPadding and passes
   padded_rows as Machine's rows. It passes global d unchanged.
4. RowPadding copies every genuine row under every prefix, appends zero
   rows, and checks every removed padding bit on return. Machine divides
   its incoming rows by F at each nonterminal selected-C node.

The following identities hold for any admissible q0, not only the old choice:

```text
core_front=qF K-2H,     core_back=qB K-H+right,
core_front+3H+(n-q0-qF-qB)K+core_back=(n-q0)K+right,
prefixes=outer_rows*2^left,
original_rows*2^((n-q0)K+right)=2^(nK+right).
```

Thus the root address partition and row serialization remain those proved
by Jose Manuel and independently refined by Sagar Thakrar. There is no
truncated high field, changed original payload or free private row. The
three selected-axis regions are disjoint and cover all n axes. At the
completed rowwise linear recursive endpoint, each added zero row is again
zero, even if intermediate operations mix rows. The unchanged removal test
therefore remains valid under that inherited endpoint premise.

Since P is a positive multiple of F^depth, PR5515's exact-depth contract
supplies every reached row quotient. Sequential children reuse it. No
additional factor is lost at a sibling. Complete spectators stay in the
source rectangle. This is a source-relative proof; it does not reprove the
native, Ordinary, Compact or numerical endpoint.

The compact guard also remains valid. Fast entry requires n>q0+qF+qB and
n<=d, hence K>3G. The source's sufficient inequality
`K>=3G+1>G+4 ceil(log2 p)+10` follows unchanged. Front/back residues lie in
[0,K). The changed q0 is at most the old 2642D0(d). Its reserved-leaf count
and descriptor extents therefore do not exceed that source allowance. The
recursive core stays at most d; padded volume remains strictly below twice
the original volume. The original exponent estimate can retain its former
upper bounds. No improved total exponent follows from this finite reduction.

For source inputs that were direct only because of the old q0, the new plan
may choose a fast branch. The same guard and full endpoint argument apply;
this does not grant a zero cost to the new core or the reserved leaves.

## 4. One axis suffices eventually

Fix the source divisor F. For every integer p>=2^14000 and every source
selected width with M>0, the minimum is

```text
q*=0 if M<T; otherwise q*=1.                                (2)
```

Here is an explicit integer proof. Put u=floor(log2 p),
`v=floor(997u/500000)`. Then K>=2^v and v>=27. Two maximum child steps
contract by less than one half, since `2*48^2<73^2`. Hence

```text
D0(d)<=2 ceil(log2 d),
2642 D0(d)<=5284(u+1).
```

For v>=27, `u+1 <= ceil(500000(v+1)/997)+1`. At v=27,

```text
2^27 = 134217728 > 74208496
      = 5284(ceil(500000*28/997)+1).
```

Each increase in v raises the right side by at most 5284*502=2652568.
The right side at 27 already exceeds this increment. Doubling the left
side therefore preserves the strict inequality by induction. It follows
that K>2642D0(d). For q=1 this is more than the required stock bit count
at any core width at most d. If M>=T, q=0 has S>=F>1 and fails (1); q=1
has a positive core and succeeds. If M<T, q=0 has S=1 and succeeds. This
proves (2), with no floating logarithm and no unstated eventual constant.

## 5. Exact source geometry at p=2^8500

Use d=isqrt(2^16949), K=126519, T=356 and G=34006. The old coarse depth is
13999 and its prefix is 36985358 axes.

For n=d, the exact minimum is **293 axes**, with reached depth13993. The
stock floor logarithm is36959276. The chosen row address has37070067 bits;
292 axes have too few bits. Independent inverse thresholds from PR5515
confirm the reached depth. No giant payload or row-count array is built.

For the same selected input widths used by the old lambda45 and lambda72
QQ16 band fixtures, the new minimum is **one axis**. The new cores have
widths36988642 and36990613, both with depth28 and stock floor logarithm73955.
This changes their internal core: the old one-generation C8 interpretation
must not be carried over. These are root-plan witnesses, not a new matched
QQ16 caller bill or the old call program with work silently removed.

## 6. Construction cost and execution limits

The reference compiler uses exact host integers. It is not a physical Count
implementation. A direct encoded construction is as follows. Use the source
fixed-degree integer-root routines to compute T. Store the endpoints and
midpoint of the bounded binary search as Counts. For each candidate, subtract
q from M, iterate the fixed maximum child map until below T, multiply a
Count initially one by the fixed F once per level, scan its binary length,
and compare that length minus one with Kq. Close each temporary before the
next candidate. Save the final q and depth. Then use the existing source
formulas to form stock, original_rows and padded_rows.

With B=ceil(log2(p+2)) and fixed F, the depth is O(B), the search interval
is O_F(B), and each trial stores O_F(B)-bit values. The T computation uses
O(B) binary-search trials and fixed-degree integer products. A direct tape
implementation can charge O_F(B^5) read/write/move actions and O_F(B^2)
visited scratch bits, using scans for every indexed arithmetic access.
These loose positive bounds include counters, copies, comparisons, returns
and clearing. They require no random-access oracle or free host arithmetic.
They are constructive planning bounds, not measurements of the retained
Count routines. Integration must use actual Count primitives and meter it.

The final original_rows descriptor can have O_F(B+K) bits: the known upper
bound gives Kq*<=2642D0(d)+K. Its construction is separately charged by the
source's output-bit scans; it is not hidden in the O(B)-bit trial workspace.
The former bound was O_F(KB). All payload, parking, leaf and native costs
remain paid. This package does not install a production frontend or execute
production O73/GL64 payloads.

The checker independently enumerates20000 minima using actual padded integer
row counts, checks10245 all-child depth entries, and tests21 complete finite
layout/tensor endpoints on dirty data. Those reduced layouts are declared
address controls, not production p-geometries. Exact production descriptors
and both sides of each claimed minimum are checked separately. The written
proof supplies the all-parameter result. No proof-kernel or independent human
acceptance is claimed.
