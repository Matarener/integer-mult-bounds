# Unequal three-helper closure

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and inherited contract

Fix either final gauge vector of Philipp / mightyOil's
[PR1322](https://github.com/CrocSwap/integer-mult-bounds/pull/1322), retained
in `research/k8-coherent-triples/CERTIFICATE.json`. Fix its 237 eligible
helpers and its original scalar ADD stream. Let k be that vector, with zero
at all other registers. For an ADD with coefficient of absolute value
p 2^e, where p is positive odd, put u=1 when p=1 and u=0 otherwise. Define

```text
f_u(z) = |z| - u [z=0]
F(k) = 2 sum_h |k_h| + sum_ADD f_u(e + k_target - k_source).
```

The complete scalar tariff in PR1322 differs from F only by a constant.
In particular the first term pays both boundary scales. This tariff and
the eligibility/conjugation contract are cited premises, not new results.
The original macro stream, coefficients, boundary contract and lowering
alphabet remain fixed.

**Theorem.** For every integer vector d supported on at most three of these
helpers, in either orientation,

```text
F(k+d) - F(k) >= 8 sum_h max(0, |d_h|-3) >= 0.
```

Consequently every improving constant integer gauge move needs at least
four changed helpers. This is a scoped computer-assisted negative proof,
with an exact finite certificate, not a failed bounded search or a global
optimum theorem. PR1322 previously established common-shift triple closure
and explicitly left independently chosen shifts open. It did not assert
arbitrary pair stationarity at its final vector.

## A finite clipping certificate for an infinite domain

An incident ADD at helper h has signed change +d_h at its target or -d_h
at its source. At the fixed vector k record it as (u,E,sigma), where
E=e+k_target-k_source and sigma is +1 or -1. Multiplicities are retained.
Let I_h be this multiset, and let I_hb contain just the ADDs joining h and
another eligible helper b. Define the outward unit difference

```text
V(J,x,s) = sum_(u,E,sigma in J)
             [ f_u(E+sigma*x) - f_u(E+sigma*(x-s)) ],   s in {-1,+1}.

D_h(x,s) = 2(|k_h+x|-|k_h+x-s|) + V(I_h,x,s).
m_hb(s) = min_(z in Z) V(I_hb,z,s).
loss_hb(x,s) = max(0, V(I_hb,x,s)-m_hb(s)).
L_h(x,s) = D_h(x,s) - sum of the two largest loss_hb(x,s).
```

A missing largest loss is zero. Suppose d_h=x and at most two other
helpers change. If such a neighbor b has displacement y, its actual pair
contribution to the outward difference is V(I_hb,x-y,s), hence is at least
m_hb(s). Unchanged neighbors contribute their baseline difference exactly.
Subtracting the two largest nonnegative losses therefore gives a valid
lower bound on the complete outward difference. It does not assume the
two independently minimized pair contributions can be attained together.

All minima and all tail inequalities above have finite exact checks. Set

```text
B_h = max(3, |k_h|, max_(u,E,sigma in I_h) |E|) + 2.
```

For fixed s, each V(I_hb,z,s) is constant on each integer tail outside
[-B_h,B_h]. Both arguments of every f then stay strictly on one side of
zero. Thus its minimum over all integers is attained in that finite
interval. The same fact applies to D_h(x,s), every loss, and L_h(x,s) on
the outward tail x=s*t, t>=B_h. The boundary absolute value also has
constant difference there. Checking t=4,...,B_h covers every outward
integer displacement beyond three.

In each orientation the verifier checks all 1,540 resulting (h,s,t)
rows. The least L_h is exactly 8. These are exact integer inequalities,
including the point discount at exponent zero. Replacing that tariff by
plain absolute value would be a different problem.

Reduce each coordinate outside [-3,3] one step toward that interval.
The support size never increases, and each step reduces F by at least
8. After sum_h max(0,|d_h|-3) steps the resulting displacement d' is in
[-3,3] and has support at most three. This proves

```text
F(k+d) - F(k+d') >= 8 sum_h max(0,|d_h|-3).
```

The remaining obligation is the bounded claim F(k+d')>=F(k).

## Exact bounded decomposition and complete coverage

Let S_h(a)=F(k+a e_h)-F(k). For every helper pair a<b, sum over its
shared ADDs the correction

```text
C_ab(x,y) = sum [ f_u(E+sigma*(x-y))
                 - f_u(E+sigma*x) - f_u(E-sigma*y) + f_u(E) ],
```

where sigma is +1 when a is the ADD target and -1 otherwise. Direct
expansion gives, for every displacement on a set T,

```text
F(k+d)-F(k) = sum_(h in T) S_h(d_h)
              + sum_(a<b in T) C_ab(d_a,d_b).
```

Boundary scales occur only in the singleton term. Shared ADDs are
counted once after the correction. No source-independence assumption is
needed for this identity of scalar costs.

The undirected interaction graph joins helpers that share any ADD.
There are 2,414 edges. Every connected triple has a length-two path, so
generating every pair of neighbors of every vertex and deduplicating
enumerates exactly its 49,898 connected triples. A separate enumeration
classifies every three-helper subset by its three possible graph edges and
confirms complete connected-triple coverage. The verifier visits
all seven singleton values, all 49 independent pair values, and all 343
independent values of each connected triple. In each orientation every
singleton, pair and connected triple has minimum zero.

The two-sided pair search covers all 27,966 pairs, including nonedges.
A disconnected triple has components of size at most two. There is no
shared ADD between components, so its cost difference is the sum of their
nonnegative singleton/pair differences, even when their shifts differ.
This covers all 2,190,670 three-helper subsets. Disconnected triples are
counted by the separate graph enumeration; their shift assignments are
discharged by the component argument rather than individual triple searches.

The bounded minimum is therefore zero. Combining it with clipping proves
the theorem. The zero displacement attains the lower bound zero; no
uniqueness or strict local minimum is claimed.

## Evidence and limits

`verify.py` extracts the signed valuation graph directly from the retained
archive and reads the final gauge vector as input. It imports no predecessor
executable and runs no predecessor census, invoice or endpoint replay. SHA256
pins authenticate both inputs. Its generated stdout receipt binds the package
files, exact input hashes, clipping rows and ordered minimum streams.

The finite certificate uses the Python standard library and exact integers.
Forty synthetic graphs independently compare the decomposition with literal
objective differences at all 343 displacement triples. Separate controls
exercise the zero-exponent discount and both paid boundary scales. These
tests corroborate the algebra; an unjustified-clipping fixture is rejected,
and 32 actual-objective controls include displacements of magnitude 2^32.
The clipping and disconnected-component arguments above justify the
quantified domain.

The theorem changes no circuit or recursive child. Four or more simultaneous
changes, temporal gauges, a changed graph, new coefficients, a changed
lowerer, native/owner integration, global precision, stock and tape costs
are outside scope. The historical source is not the selected P104 supplier.
No kappa improvement, supplier admission, complete multiplication theorem,
independent human review or formal proof-kernel acceptance is claimed.
