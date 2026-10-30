# Least borrowing at the actual body depth

Fix integers q>=2, w>=1, m>r>=1, b>=1 and Q>=1. The atom width w is fixed
before borrowing. Define

```
D(n)=0                              for 0<=n<m,
D(n)=1+D(r floor(n/m))              for n>=m,
S_0=1,   S_d=Q b^d                 for d>=1,
L_d=min{j>=0 : q^j>=S_d}.
```

These statements concern this prescribed reserve and the current NODE guard
contract. They do not assert a minimum for arbitrary implementations. A
consumer requiring the older simultaneous full depth-d formats retains its
stronger divisor.

Optimality below retains the selector's explicit covering constraint
q^k>=S_D(n). It does not optimize over alternative padding/volume budgets.
For example, R<S can sometimes still give R'=S<2R. Such a relaxation is
outside the stated predicate and is not ruled out by this result.

## 1. The exact admissibility predicate

For positive original width e and borrowed width k, put

```
n(k)=floor((e-k)/w),   ell(k)=(e-k) mod w,
U=min(floor((e-1)/2), e-mw).
```

A fitted plan in this guard model exists exactly when some integer k in
[0,U] satisfies

```
k >= F(k),   F(k)=L_D(n(k)).                         (1)
```

Indeed, k<=floor((e-1)/2) is precisely strict fit 2k<e. The condition
k<=e-mw is precisely n(k)>=m. The reserve condition q^k>=S_D(n(k)) is
equivalent to (1) by the definition of L. These are the three conditions
being optimized. Complete physical execution has additional premises below.

The child map is nondecreasing and strictly contracts positive internal
widths. Thus D is finite and nondecreasing. The latter also follows by strong
induction: for m<=x<=y, compare the two smaller child widths; if x<m its
depth is zero. S_d and L_d are nondecreasing, including d=0, since b,Q>=1.
As k increases, n(k), D(n(k)) and F(k) are nonincreasing. Therefore (1) is
a monotone predicate on [0,U].

If U<0 or U<F(U), there is no fitted plan. Otherwise bisection between the
false sentinel -1 and true endpoint U returns the least k satisfying (1).
Every tested midpoint is nonnegative; the sentinel is never passed to F.
The integer interval length at least halves, rounded up, at each step.
Thus ceil(log2(U+2)) steps suffice. The implementation allows
e.bit_length()+1 steps. The theorem has no finite e cap; replay declares one.

This is an inequality problem. The least k need not equal F(k). Replacing
the predicate by k=F(k) can discard the optimum or fail to terminate, as
section 4 demonstrates within the selected parameter domain.

## 2. An independent inverse-depth formula

The least n of depth at least d has thresholds

```
a_1=m,   a_(d+1)=m ceil(a_d/r).
```

Direct inversion of r floor(n/m)>=a_d proves this recurrence. Hence D(n)=d
exactly when a_d<=n<a_(d+1), for d>=1. At a proposed depth d, the three
admissibility conditions are equivalent to

```
max(0,L_d,e-w*a_(d+1)+1) <= k
                         <= min(floor((e-1)/2),e-w*a_d).
```

Take the lower endpoint whenever this interval is nonempty, then minimize it
over 1<=d<=D(floor(e/w)). This is a second exact characterization of the
same optimum. It uses inverse thresholds and finitely many depth slabs,
rather than the forward recurrence and bisection. independent.py implements
this formula without importing the primary implementation or its receipt.

## 3. Bind the result to the existing consumer

David Arias's PR2753 source supplies m=64, r=42 and the completed recursive
caller boundary. Jose Manuel's PR2899 encoded selector fixes
w=ceil(e^(17/10000)) before borrowing and uses D(e) to choose stock.
Tekalign's PR3264 opt-in selector retains that depth and substitutes Nick
Petalas's PR3246 one-factor reserve. Its proof explicitly leaves actual-body
depth and optimal borrowing open. These exact source files are inputs in
SOURCES.json; their bytes and attribution remain unchanged.

For the selected guard reserve, at fixed source-admissible prime q>2^80,

```
N=|GL_64(F_q)|,   H=q^(4096(w-1)),
b=28416*N*H,      Q=9475.
```

At the optimum choose R=q^k and pad to
R'=ceil(R/S_D(n))*S_D(n). Equation (1) gives R>=S_D(n), so R<=R'<2R.
The callee receives n and all R' fresh rows. Its actual maximum child depth
is D(n), so PR3246's unchanged guard induction supplies every quotient and
Q check. The entire fresh quotient passes to children; completed siblings
reuse it.

PR3264's consumer argument then applies with d=D(n) in both padded calls,
conditional on its existing completed-callee, source access, fresh-field,
pointwise row/spectator restoration, restriction and ownership premises.
The genuine other high field remains R rather than R'. Both restrictions
occur immediately after their padded call. Sequential calls do not multiply
stock. No child, helper, routing or cleanup charge disappears.

If the existing D(e) selector fits, its k is a feasible candidate for (1),
because D(n(k))<=D(e). The new optimum is no larger. It need not be smaller,
and smaller k is not a measured runtime gain. This implication does not
install a Count-tape selector or prove its setup cost. The artifact is a
bounded exact host-integer selector and a source-bound conditional interface
theorem. No default backend or selected frontier changes.

## 4. Exact selected examples without enormous stocks

Take q=2^127-1, a prime greater than 2^80. The replay checks primality of
127 and the 125-step Lucas-Lehmer residue zero for q. The
[GIMPS prime record](https://www.mersenne.org/primes/) also identifies this
classical prime. This explanatory reference is not a network replay input.

Put P(q)=product_(i=1)^64 (1-q^-i). Independent-column counting gives
N=q^4096 P(q). The elementary product and Bernoulli inequalities give

```
1 > P(q) > 1-1/(q-1),
P(q)^d > 1-d/(q-1)                         for d>=1.
```

Let C_d=9475*28416^d and h_d=min{j:q^j>=C_d}. Whenever

```
C_d*(q-1-d) > q^(h_d-1)*(q-1),                     (2)
```

the exact stock lies strictly between q^(4096wd+h_d-1) and
q^(4096wd+h_d). Thus L_d=4096wd+h_d. Both implementations check (2)
independently at every consumed depth. No floating logarithm, rounded group
order or materialized GL64 reserve enters acceptance. The larger group and
reserve retain their exact defining formulae.

For e=250000, the exact inequality 1<e^17<=2^10000 certifies
w=ceil(e^(17/10000))=2. The D(e)=18 choice has k=147459 and fails 2k<e.
Even D(floor(e/w))=17 requires k=139267 and fails. The actual-body optimum is

```
k=122882, n=63559, ell=0, D(n)=15, L_15=122882,
2k=245764<250000.
```

Feedback therefore supplies a fitted plan in the stated guard model where
both coarser depths select fallback. This is selected-parameter arithmetic,
not an execution of its immense Boolean payload or a changed asymptotic
bootstrap cutoff.

For e=970370, the same exact ceiling gives w=2, and

```
F(155651)=163843,   F(163843)=155651.
```

Both k values meet the geometric fit conditions. The exact threshold a_20
is 405312. At k=159746 the body is 405312 of depth 20 and requires 163843
digits. At k=159747 the body is 405311 of depth 19 and requires 155651.
The least feasible k is therefore 159747, strictly greater than its own
required digit count. Monotonicity proves minimality and shows no fixed point
exists: below this k the predicate fails; at or above it,
F(k)<=155651<159747<=k. Substitution can cycle between 155651 and 163843.
It is not a valid general selection algorithm.

## 5. Evidence and limits

The primary and independent depth-slab implementations agree on 8192 bounded
cases and five selected examples. A separate exhaustive scan over every
geometrically legal k in those cases checks the least result and each
accepted padded quotient/Q guard. The written proof supplies the universal
claim; finite agreement does not replace it. The actual optimized CLI accepts
its Git-free source closure and rejects seven malformed source, receipt and
arithmetic producers. Contracts remain active under -O.

The result optimizes k at fixed w for the prescribed guard stock. It does not
optimize w, prove a smaller universal reserve, supply encoded tapes, execute
the selected GL64 payload, discharge universal C0/physical refinement or
uniform costs, or solve the complex m=73 reserve. Full-cover, completed
leaves, fresh fields, pointwise restoration, routing, precision/tape and outer
transfer obligations remain. No new kappa, supplier admission or complete
multiplication theorem is asserted.
