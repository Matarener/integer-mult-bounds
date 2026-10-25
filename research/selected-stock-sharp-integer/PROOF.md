# The least integer coefficient is 6741

Fix any prime `q > 2^80` and integers `e,w >= 1`. Write

```
N = |GL_64(F_q)|,
H = q^(4096(w-1)),
b = 28416 N H,
Q = 9475,
K = Q b = 269241600 N H.

D(e) = 0                         for e < 64,
D(e) = 1 + D(42 floor(e/64))      for e >= 64.
```

The two reserves under consideration are

```
S_old(e,w) = K^D(e),
S_guard(e,w) = 1                  if D(e)=0,
S_guard(e,w) = Q b^D(e)           otherwise.
```

These are the unchanged original complete-format stock and PR3246's current
NODE-guard stock. Their source contracts remain different. For either one,

```
log_q S(e,w) <= 6741 w log2(e).
```

The inequality is strict when `D(e)>0`. Moreover, 6741 is the least **integer**
coefficient valid at every stated width. No optimal real coefficient is asserted.
The statement concerns these prescribed reserves, not every possible reserve
or implementation. It is also valid with `1+log2(e)` on the right, with the
same least integer coefficient, as shown below.

## Source and implementation boundary

David Arias's PR2753 proof gives `K`, the floor-child rule, terminal width 64
and complete-row restoration premise. Its `node.py` computes the fresh
quotient and retains the 9475 compatibility check. Nick Petalas's PR3246
proves the smaller current-guard divisor and distinguishes the stronger
dual full-depth format. jwr's PR2888 bounds the original `K^D` reserve by
`6748 w (1+log2(e))`, using PR2120's 28/17 depth certificate. All four source
texts and the selected assembly are exact main-branch live inputs in
SOURCES.json. No predecessor executable is imported or changed.

The new result tightens that numerical envelope and proves integer sharpness.
It supplies no new endpoint, compiler, stock selector, time bound, consumer,
bootstrap cutoff or supplier admission. In particular, it does not prove a
complex `m=73` reserve coefficient or discharge the ordinary leaf's completed
contract. Existing source attribution and notices remain unchanged.

## 1. A rational depth bound

The exact integer inequality

```
2^2631 > 21^599
```

is equivalent to `(32/21)^599 > 2^364`. Consequently

```
c = 599/364 > 1/log2(32/21).
```

Strong induction on integer e proves `D(e) <= c log2(e)`. For `1<=e<64`,
the left side is zero. For an internal width, its maximum child
`f=42 floor(e/64)` is positive and strictly smaller than e. It satisfies
`f <= (21/32)e`. Thus

```
D(e) = 1+D(f)
     <= 1+c log2(f)
     <= c log2(e)+1-c log2(32/21)
      < c log2(e).
```

The floor recurrence is an explicit source premise; a finite census is not
its proof. Paid children of smaller rank cannot increase the maximum depth.

## 2. The complete stock logarithm

Counting independent columns of an invertible matrix gives

```
N = product_(i=0)^63 (q^64-q^i) < q^4096.
```

The actual lcm multiplier obeys `269241600 < 2^29`, while `q > 2^80`, so

```
log_q K < 4096w + 29/80
        <= (4096+29/80)w.
```

Every factor remains charged. This does not replace the actual divisor K by
a rounded q-power in the caller. Combining with the depth bound gives

```
log_q S_old < [599*327709/(364*80)] w log2(e)
              = [6741-229/29120] w log2(e)
              < 6741 w log2(e)                         when D(e)>0.
```

When `D(e)=0`, both reserves are one and the non-strict statement holds,
including e=1. For positive depth, `Q b^D <= (Qb)^D` because `Q>=1` and
`D>=1`. The same upper bound therefore covers `S_guard`. This comparison
does not identify their separate physical-format contracts.

The stronger logarithm `log2(e)` also implies the conventional
`1+log2(e)` envelope. Existing fit lemmas can use the smaller coefficient,
but `ceil(log2(8*6741))=16` is unchanged. No new fit cutoff follows here.

## 3. Exact depth thresholds

Let `a_d` be the smallest width with depth at least d. Direct inversion of
the child inequality gives

```
a_1=64,
a_(d+1)=64 ceil(a_d/42).
```

Indeed `42 floor(e/64)>=a_d` holds exactly when
`e>=64 ceil(a_d/42)`. The thresholds strictly increase because `64/42>1`.
Induction proves both directions, and hence `D(a_d)=d` and
`D(a_d-1)=d-1`. This is an all-depth proof.

The replay generates `a_262144` exactly. It has 159307 bits. Its minimal
unsigned big-endian byte representation has SHA256

```
4244143f5dcb47d33ad69a8dcce2e75057f8856543bc923b7ba1c9d6dddf9839
```

This compact recurrence is the exact witness specification; a decimal string
or a materialized stock of astronomic size is unnecessary. An independent
implementation uses `a_d=64 t_d` and
`t_(d+1)=t_d+ceil(11t_d/21)`, then reconstructs the forward depth.

## 4. Coefficient 6740 fails for every admissible prime

For q>=3, let `P(q)=product_(i=1)^64 (1-q^-i)`. Expanding successively,
or inducting on the number of factors, proves

```
P(q) >= 1-sum_(i=1)^64 q^-i > 1-1/(q-1) >= 1/2.
```

Since `N=q^4096 P(q)` and `28416>2`, at atom width w=1 we have
`b=28416 N > q^4096`. For e=`a_262144`, both reserves therefore satisfy

```
log_q S > 4096*262144 = 1073741824.
6740 log2(e) < 6740*159307 = 1073729180.
```

The strict certified separation is greater than 12644. It holds for **every**
prime q>2^80, without a primality computation or floating-point logarithm.
For the conventional envelope the same witness still fails:

```
6740*(1+log2(e)) < 6740*159308 = 1073735920 < 1073741824.
```

Thus coefficient 6740, and every smaller integer, fails. Together with the
upper bound this establishes 6741 as the least integer coefficient for both
logarithmic conventions and both prescribed stocks over the stated domain.
This is not a claim of real-coefficient optimality, practical sharpness at
bootstrap widths or minimal borrowing. Here e and w are independent; the
explicit w=1 witness does not satisfy a positive bootstrap relation
`w=ceil(e^s)`. No optimal coefficient for that restricted relation is claimed.

## Evidence and limits

The primary verifies exact contraction and coefficient inequalities, all
child ranks 1 through 42 at widths 0 through 131072, 32 inverse-depth
boundaries, and the exact large-width witness. The separate implementation
imports neither the primary nor its receipt. It reconstructs both integer
certificates and the witness with different integer expressions and a
forward pass. These checks support the written proof; they are not formal
proof-kernel verification or an execution of the selected GL64 payload.

The two reserves inherit the source's constant atom width, full-cover,
fresh-field, completed leaf, pointwise restoration and all-size caller
premises. Physical compilation, routing, precision/tape, complete costs and
outer transfer remain separate. No selected frontier or kappa changes.
