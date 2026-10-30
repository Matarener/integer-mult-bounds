# Optimal axis order for heterogeneous Smith tensors

This contribution was produced by Nick Petalas. New material is Apache-2.0.
Credit Dugongue / David Ganz, PR [#5815](https://github.com/CrocSwap/integer-mult-bounds/pull/5815)
at `f0fcda576df410dc15cd5b8183d4f74d284eba2b`, for the Gaussian integral
Smith word and its complete two-pass addition-precision accounting, especially
consumer-construction.md C2–C8. Tensor products, valuation arithmetic and
adjacent-exchange proofs are classical. No literature-wide priority is claimed.

## 1. Changed premise and exact tariff

Put pi=1+i, and fix n>=1 nonnegative integers a_1,...,a_n. Define

```text
S = [[i,0],[1,1]],       T = [[1,-i],[0,1]],
C_a = S diag(1,pi^a) T = [[i,1],[1,pi^a-i]],
F_a = tensor_j C_(a_j),  N=2^n.
```

The Gaussian factor in #5815 is C_2. We allow unequal gaps a_j. This changes
the tensor being computed; we do not claim an order improvement for its
identical C_2 axes. Input coordinates are arbitrary Gaussian integers. The
endpoint is every coordinate of F_a x modulo pi^P, for an integer P>=0.
Normalization by pi^-B instead gives the same calculation with raw modulus
P=p+B, whenever this raw modulus is nonnegative.

We permit independent axis permutations sigma for the T gather and tau for
the S delivery, at fixed coordinate indices. There are no axis swaps of the
data. Each scalar ADD performed at q residue digits costs exactly q in this
tariff, including q=0. The theorem minimizes the sum of this mass over **both**
passes. It does not minimize shifts, phases, routing, allocation, truncation,
cleanup, bit time, or all implementations of F_a.

## 2. A legal modular word for every pair of orders

Work in an owned copy of the input, initially reduced modulo pi^P. After
gathering a set A of axes, a coordinate u has precision

```text
q(u,A) = (P - sum_(j in A) a_j u_j)_+.
```

For the next axis j, a low/high pair differs only at bit j and has common
current precision q. Execute

```text
low  <- low - i*high mod pi^q
high <- high mod pi^(q-a_j)_+
```

The subtraction precedes truncation. Later T axes do not change the already
processed bits. Therefore each discarded error, on reaching the diagonal
tensor factor, receives at least the valuation sum that paid for its loss.
If that sum is >=P, the entire coordinate may be replaced by zero. This
proves the gather invariant and correctness of truncation by induction.

After all T axes, a coordinate represents pi^e z, where
e=sum_j a_j u_j and z is known modulo pi^(P-e)_+. We need not physically
multiply all diagonal entries into a common-precision array.

During delivery let B be the remaining axes. A pair at axis j in B has tags
e and e+a_j, where e=sum_(h in B minus {j}) a_h u_h. Its represented values
are pi^e z_0 and pi^(e+a_j) z_1. With q=(P-e)_+, execute

```text
z_1 <- z_0 + pi^a_j * z_1 mod pi^q
z_0 <- i*z_0 mod pi^q
give both coordinates tag e and precision q.
```

These are precisely S applied to the represented pair. The old z_1 needs
only (q-a_j)_+ digits. When q-a_j<0, its missing contribution is already
zero modulo pi^q. The new z_0 phase follows the addition. At the end all
tags are zero and all precisions are P. Thus this word computes every
required output for arbitrary inputs, for every sigma and tau. Original
inputs are preserved. This ordinary modular word uses the declared owned
truncation/erasure contract; it is not a reversible implementation.

## 3. Exact mass formula

For a set A of axes define the rational average

```text
H(A) = 2^(-|A|) sum_(U subset A) (P - sum_(j in U) a_j)_+.
```

For a gather order sigma, let A_m contain its first m axes, including A_0
empty. Among its N/2 pairs at the next stage, each processed bit pattern
occurs equally often, so

```text
M_T(sigma) = (N/2) sum_(m=0)^(n-1) H(A_m).
```

For delivery order tau, the ADD at a stage depends only on axes remaining
after that stage. Their sets, read backwards, are the prefixes of reverse(tau).
The same counting gives the exact identity

```text
M_S(tau) = M_T(reverse(tau)).
```

All actual stage masses are integers: a stage uses at most n-1 averaging
bits, which are paid by the factor N/2. The formula counts every scalar pair
of both passes, rather than only the diagonal bank or one pass.

## 4. Adjacent exchange and all equality cases

Take adjacent gather axes with gaps a,b after an arbitrary prefix A. Let
X=sum_(j in A) a_j U_j, where U_j are independent uniform binary bits, and
write f(t)=max(t,0). The first stage cost is unchanged by the exchange;
every later stage has the same prefix set. The difference of the two
normalized gather sums is exactly

```text
D(a,b | A) = (1/2) E[ f(P-X-a) - f(P-X-b) ].
```

If a>=b, every summand is <=0. If a>b and P>b, the event with all prefix
bits zero has positive probability and gives a strictly negative summand.
If P<=b, both summands vanish for every X>=0. Hence for a>b the exchange
is strict exactly when P>b.

Define clipped gaps b_j=min(a_j,P). An order has minimum gather mass **if
and only if** its clipped gaps are nonincreasing. Sufficiency follows by
sorting all adjacent inversions; swaps within a clipped tie have zero cost.
For necessity, any sequence that is not nonincreasing has an adjacent
increase in its clipped gaps. Swapping that pair strictly decreases cost,
by the preceding calculation. This includes P=0 and arbitrary zero gaps.

The exact delivery minimizers are the orders with clipped gaps
nondecreasing, by Section 3. The two order choices are independent, so
these conditions characterize every minimizing pair (sigma,tau).

In particular, sort the actual gaps descending for gather and ascending
for delivery. If a_[1]>=...>=a_[n] is that sorted list, the exact optimum is

```text
M_min = N sum_(m=0)^(n-1)
          2^(-m) sum_(U subset {1,...,m}) (P-sum_(j in U) a_[j])_+.
```

Once the orders are chosen, this is an explicit finite formula, with no
search over permutations. The written theorem has no executable size limit.

## 5. First strict improvement

For gaps (1,4) and P=3, use the same fixed four-coordinate target throughout.

```text
gather gaps (1,4), delivery gaps (4,1): 11+11 = 22
gather gaps (4,1), delivery gaps (1,4):  9+ 9 = 18
```

Both words have eight nominal scalar ADD positions; a zero-precision ADD
contributes zero mass. The optimized word saves four residue-digit ADD
units. Its literal modular execution and independent dense tensor outputs
agree. This is an exact component-work comparison, not a runtime speedup.

Equal gaps make every order tie. More generally, gaps >=P are all tied even
if their actual values differ. Ordering heterogeneous physical axes can
change movement costs, which this theorem does not absorb into its tariff.

## 6. Evidence boundary

The verifier exhausts its declared small profiles and orders, separately
enumerates actual stage pairs, checks the exchange identity and all equality
cases, and compares the new heterogeneous modular word with direct dense
tensor multiplication. Odd moduli are checked through their Gaussian parity
lattice. These checks corroborate this written proof. No predecessor result
or verifier is replayed or audited. No selected source, supplier admission,
five framework assumption, or complete multiplication theorem is changed.
