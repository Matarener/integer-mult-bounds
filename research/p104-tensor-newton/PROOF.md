# All-depth Newton entrance for the P104 payload lift

Let `R=Z[i]`, `pi=1+i`, and

```text
E = [[1,0],[1,pi]],     B_n = E^tensor-n R^(2^n).
```

Fix the exact PR2586 WORD and NATIVE inputs in SOURCES.json. Let `lambda` be
any positive integer and put `n=9 lambda`. A public bank is an arbitrary
array on `lambda` ordered nine-bit blocks. It need not be a simple tensor.

## The payload lift, and what is inherited

Keep all 5,398 role events, scalar ADD coefficients, signs, allocations and
erasures unchanged. Replace each native recipe `U` by `U^tensor-lambda`.
Implement it as its right wrapper independently on every block, its actual
coordinate butterflies on every block, then its left wrapper on every block.
The block order within the butterfly portion is arbitrary. This defines the
explicit scalar reference being proved. A fast recursive implementation is
not supplied.

For a wrapper `M|x>=i^p(x)|Ax+b>`, the lifted address map is block diagonal
with `lambda` copies of `A` and `b`. Its phase is `sum_h p(x_h)` modulo four.
In particular the constant phase is `lambda*p(0)`, not `p(0)`. The operation
is the tensor power of the complete phase-sensitive wrapper.

We inherit the source-specific equality

```text
U_(H,K) = Delta_K Delta_H^-1
```

for all 1,245 archived native classes from PR3416, exact
`f1112560883a5e81b1a29c37c81a79a20be31fe3`. Its proof is retained unchanged
in inputs/PR3416_PROOF.md. This package rechecks every occurrence's frame and
rank, but does not rerun that predecessor's full covariance certificate.
Tensor functoriality gives, for every positive lambda,

```text
U_(H,K)^tensor-lambda
  = Delta_K^tensor-lambda (Delta_H^tensor-lambda)^-1.
```

ADD coefficients remain `q`, including `1/4`. They do not become `q^lambda`.
Tensor-powering the complete register program would be a different operation
with different role dimensions and coefficients.

## The theorem

Choose an exponent `k_s>=0` independently for each of the 358 initial public
roles and allow every physical initial array in `pi^k_s B_n`. Private C is
owned exact zero at each allocation. The following property holds if and only if

```text
k_Y >= 4  for each of 104 Y banks,
k_N >= 2  for each of  78 N banks,
k_s >= 0  for the other 176 banks.
```

The property is exact realization of the declared scalar/native maps with
membership in `B_n` at every event boundary, after every complete block
wrapper, and after every coordinate stage of the stated native implementation.
Every scalar division and signed-floor butterfly is exact. All eight private
erasures are literal zero. In the declared
terminal charts, non-X public banks restore their initial logical arrays and
the X banks realize the unchanged scalar Y shear.

The exponents are independent of lambda. A common scale `2^-f` may multiply
the entire contract, with floor arithmetic measured in those grid units.
This theorem is about the stated payload lift, not arbitrary tensor callers
or a complete multiplication algorithm.

## Tensor lattices and arbitrary arrays

Reordering the tensor factors by nine-bit blocks gives

```text
B_n = B_9 tensor_R ... tensor_R B_9
```

as free embedded R-modules. This equality concerns the full R-span of simple
tensors. It imposes no separability condition on an individual array.
If `T` and `T^-1` preserve `B_9`, applying T on one block and identity on all
others preserves `B_n`, with an integral inverse in E_n coordinates.

The required one-block automorphisms are the Newton theorem of
Clear1nsight/PR3382 and its source-bound use in PR3406. For completeness, the
coordinate butterfly obeys `E^-1 C E=[[1,1],[0,i]]`. Bit flips, coordinate
permutations and CNOT preserve the weighted multilinear divisibility
`pi^|S|` and have integral inverses. A linear phase contributes a factor
`1+(i^a-1)x_j`, whose nonconstant coefficient is divisible by pi. A quadratic
sign contributes `1-2x_j x_k`, divisible by pi squared in degree two.
These generate the actual affine-address/quadratic-phase wrapper alphabet.
The pinned wrappers' dimensions, numeric ranges and bijections are checked.
Their complete blockwise actions and each coordinate stage therefore preserve
every `pi^k B_n`. The canonical Delta charts and their inverses do as well.

For a pair `(a,b)` drawn from such an array, its difference is divisible by
pi. Its real and imaginary differences have equal parity. In the literal
signed-floor butterfly the two half-unit errors cancel after the Gaussian
rotation, so its output equals C exactly, also for negative integers. This
is a pair identity; the global module invariant supplies its parity premise
at every new pair. Intermediate permutation-cycle states need only be
Gaussian integers, since wrappers contain no division. We do not require
the global Newton module at individual permutation-cycle intermediates.

Checking each block's slices separately would be insufficient. On two selected
bits from distinct blocks, let `g=pi*x_0*x_9`, constant on the unused bits.
Every one-block slice is zero or a degree-one Newton element. But the mixed
degree-two coefficient is only pi, so g is outside B_n. After C on each of
these two bits its value at their joint zero address is `(1-i)/2`, which is
not Gaussian integral. The separate slice tests therefore do not supply the
global invariant used in the theorem. algebra_controls checks this failure.

## The same scalar trace controls every depth

Let `c_(j,t,s)` be the rational coefficient of initial logical role s in
role t at cut j. Its recurrence depends only on the fixed role program.
Transport changes no coefficient, ADD adds `q` times its source row, a sign
negates a row and private allocation creates a zero row. Thus c is independent
of lambda. Covariance gives the physical value

```text
sum_s c_(j,t,s) Delta_(j,t)^tensor-lambda
                      (Delta_(0,s)^tensor-lambda)^-1 f_s.
```

Every displayed chart factor is a `B_n` automorphism. Consequently the sharp
independent-product criterion is

```text
k_s >= max(0, max_(j,t) -v_pi(c_(j,t,s))).
```

The new exact forward trace computes that maximum through all 5,398 events.
It records every source exponent and every attaining positive bound. A
separate reverse covector trace checks all 182 witness coefficients.
The result is four for every Y, two for every N and zero otherwise, matching
the credited nine-bit result of PR3406. All eight erased rows are zero and
the final scalar rows have precisely the restoration/shear form stated above.
No finite depth extrapolation is used in this deduction.

Sufficiency now follows term by term and from closure under addition, then
from the native prefix automorphisms. Each pre-ADD target and post-ADD target
is in B_n, so their difference, the scaled source increment, is in B_n too.
Thus fractional ADD products are integral before accumulation. For necessity, choose one attaining
coefficient q and set every other source to zero. Take `f_s=pi^k E_n e_0`.
It is a primitive column times pi^k. An integral lattice automorphism with an
integral inverse preserves primitivity. Therefore its image multiplied by q
belongs to B_n if and only if `v_pi(q)+k>=0`. Lowering that source exponent
even by one pi violates membership at the attaining cut. If literal arithmetic
deviates earlier, the required exact-prefix property has already failed.
This proves sharpness at each positive lambda, independently of input size.

## A literal nonseparable depth-two check

The standalone checker executes the actual 2031 and 2033 recipes at depth two,
on all 262,144 Gaussian coordinates of

```text
f(x)=1+pi^2*x_0*x_9.
```

This belongs to B_18. Its two-block 2-by-2 value minor is
`[[1,1],[1,1+2i]]`, with nonzero determinant `2i`, so it is not a simple
tensor across the blocks. Every literal signed-floor pair is compared with
the independently evaluated exact Gaussian matrix formula. The returned
array equals f at every address. Reversing the block-stage order gives the
same forward array. This fixture supports the universal written argument;
it is not execution of the complete 5,398-event depth-two word.

## Domain size and the remaining price

The constant source exponents do not mean constant precision or free input
admission. The Gaussian index of B_n in `R^(2^n)` is
`2^(n*2^(n-1))`, because `det(E_n)=pi^(n*2^(n-1))` and `Norm(pi)=2`.
The complete public entrance has index

```text
2^((179*n+572)*2^n)
```

in the unrestricted Gaussian public array module. Here `572=104*4+78*2`.
This exact index measures a restriction on inputs, not a physical resource
bill. Admission, representation intertwiners, numerical heights, ownership,
routing, recursive realization, complete costs and all-size supplier transfer
remain open. The unfavorable unchanged-profile stop from PR3423 is retained.

Nick Petalas. Apache-2.0. Credit Clear1nsight/PR3382 and PR3423, ywz65/PR2586,
Tekalign/PR3025 and PR3218, Ross Richardson, Arham Tahir, Alejandro Zarzuelo
Urdiales, Jose Manuel and the retained Clifford, geometry, compiler and
precision lineage. Classical Barnes-Wall provenance remains with Nebe,
Rains and Sloane. Frozen predecessor bytes and notices are unchanged.
