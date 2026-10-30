# Exactly which budgets attain the hidden-window bound

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Model and predecessor

Fix integers h>=1 and N>=1. On ranks 2^j for 0<=j<=2h+2, let A_j,B_j
be nonnegative integer call multiplicities, at most N calls per profile.
Set Q(x)=sum_j(B_j-A_j)x^j and F(p)=Q(2^p). Require endpoint zeros of
multiplicity at least h at p=0,1 and two distinct interior zeros alpha<beta,
with F positive between them. Write w=beta-alpha.

Karnaugh33's [PR6139 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/3b9de03623e8bf05af49f9f9c5fc7a426cbde9e5/research/fixed-budget-hidden-windows/PROOF.md)
supplies this reduction and bound:

```text
S=6^h/2,  L=floor(N/S),  Z=floor((L-1)/2),
Q(x)=(-1)^(h+1)(x-1)^h(x-2)^h R(x),
R(x)=a x^2-z x+c=a(x-r)(x-s),
a,z,c positive integers,  1<r<s<2,
Delta=z^2-4ac positive integer,
D=a+z+c,  W=SD<=N,
w >= log_2((Z+1)/(Z-1)).
```

W counts calls on each side after cancelling common calls. It is not the
combined count. Eligible profiles have Z>1. The source supplies the bound,
one infinite attaining family and one further example. Its Open next
question 1 asks for the complete attainment classification. Our result
answers that question; no source executable or census is replayed.

## Classification

The bound is attainable at budget N if and only if L belongs to

```text
{4n^2-1, 4n^2 : n>=3} union {2n(n+1) : n>=4}.
```

All attaining residuals are as follows, with the positive leading coefficient
convention above. Include both when both tests hold.

```text
L=4n^2-1 or 4n^2, n>=3:
  (a,z,c)=(n(n-1), 2n^2-1, n(n+1)),  D=4n^2-1;

L=2n(n+1), n>=4:
  (a,z,c)=(n(n-1)/2, n^2+n-1, (n+1)(n+2)/2),  D=L.
```

This is an existence statement at a budget. Other profiles at that budget
may have strictly wider windows. Elsewhere the bound is unattainable; this
does not identify the true optimum or imply that no eligible profile exists.

## Necessity

The quadratic formula gives s/r=(z+sqrt(Delta))/(z-sqrt(Delta)). Its
denominator is positive since c>0. Put k=R(1)=a+c-z. Strict interior
roots imply that k is a positive integer. Since D=2z+k<=L, we have 0<z<=Z.
Thus sqrt(Delta)/z>=1/Z. Strict monotonicity of (1+t)/(1-t) on 0<t<1
shows that equality in the bound is equivalent to Z^2 Delta=z^2.
Because Delta>=1 and 0<z<=Z, this means exactly Delta=1 and z=Z.
No irrational-root residual or integer scaling greater than one can attain it.

Now L is 2z+1 or 2z+2, so D=2z+k<=L forces k in {1,2}. Also
c/a=rs>1, hence u=c-a is a positive integer. Using a+c=z+k yields

```text
u^2=(a+c)^2-4ac=2kz+k^2+1.
```

For k=1, u^2=2z+2 is even. Write u=2n, n>=1. Then

```text
z=2n^2-1,  a=n(n-1),  c=n(n+1),  D=4n^2-1.
r=(n+1)/n,  s=n/(n-1).
```

Positivity and s<2 force n>=3. From z=Z and D<=L, exactly
L=4n^2-1 and L=4n^2 remain.

For k=2, u^2=4z+5 is odd. Write u=2n+1, n>=0. Then

```text
z=n^2+n-1,  a=n(n-1)/2,  c=(n+1)(n+2)/2,
D=2n(n+1)=2z+2,  r=(n+2)/n,  s=(n+1)/(n-1).
```

Positivity and s<2 force n>=4. Now D<=L leaves only L=2n(n+1).
These cases exhaust k and prove necessity.

## Sufficiency and every profile realization

Each listed triple has positive integer coefficients, Delta=1, strict
interior roots, z=Z and SD<=N. Form Q using the endpoint factors above.
All its roots are positive, so its coefficients alternate strictly in sign.
Let A be its negative coefficient part and B its positive coefficient part.
Then Q(1)=Q(2)=0 gives equal counts and rank masses, and

```text
sum A_j = sum B_j = |Q(-1)|/2 = S(a+z+c) = SD.
```

The orientation makes Q positive on (r,s) and negative on (1,r) and (s,2).
Thus these profiles satisfy the premises and attain the bound.

Every profile pair giving this Q is obtained by adding the same nonnegative
integer vector H to both disjoint coefficient parts. It is permitted exactly
when sum H_j<=N-SD. Writing N=SL+rho with 0<=rho<S, the maximum common
count is rho at L=4n^2-1, S+rho at L=4n^2, and rho for the second family.
Padding changes neither Q nor R and creates no other residuals.

An even L can belong to both families. At L=144 the two residuals are
(30,71,42) and (28,71,45). A construction must return both. Classifying
all overlap indices is unnecessary for the theorem.

## Credit and limits

The reduction, bound, first family at L=4n^2-1 and second family's n=4
example belong to Karnaugh33. The new part is the exhaustive equality
classification, adjacent normalized budgets 4n^2, the full second family
and explicit padding allowances. zxv's [PR6049](https://github.com/CrocSwap/integer-mult-bounds/pull/6049)
supplies the hidden-window/minimal-support framework and credits Nick
Petalas's PR5174 and Ali Romman's rank-budget lineage. The quadratic formula,
integer discriminants and positive-root coefficient signs are classical.

The proof is uniform in h,N. Finite checks corroborate it; no formal
proof-kernel certification is claimed. Arithmetic call profiles do not
establish legal native realization, source compatibility, independent targets,
dirty restoration, compiler, stock, precision/tape or the complete caller.
No new kappa or complete multiplication theorem follows.
