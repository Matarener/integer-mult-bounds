# One-way coupled corank-one requests

## Contract

Let K be a finite field of order q and m>=2. Let U,V be rank-one
idempotents on K^m with UV nonzero and VU=0. Put P=I-U and Q=I-V.
A header G in GL_m(K) passes R when every leading principal minor of
GRG^-1 of orders 1 through rank(R) is nonzero. Headers have equal weight.
Both requests have rank m-1 and use the same complete header.

The claim is a scoped counting proof. It extends the partial-Gram method
of Nick Petalas's #4261 from orthogonal kernels to one-way coupled kernels.
The noncommuting requests are outside its hypotheses and outside #4259's
laminar-family theorem. No physical implementation or new kappa follows.

## All-field transfer theorem

Write B=[[1,1],[0,1]]. Define, for 2 by 2 matrices A,

```text
w(A) = 2q^2-1 if A=0;
       q-1    if rank(A)=1;
       0      if rank(A)=2.
S = {A : A_11 != 1 and A_22 != 1}.
f_0(A) = 1 if A=0, otherwise 0.
f_(j+1)(A) = sum_(T in S) f_j(T) w(A-T), for A in S.
C(q,m) = sum_(A in S) f_(m-1)(A) w(B-A).
D(q,m) = (q^m-1)(q^m-q) q^(2m-4).
```

**Theorem.** The joint passing fraction is C(q,m)/D(q,m). There are
C(q,m)|GL_(m-2)(K)| passing headers, with |GL_0(K)|=1. The transfer has
q^2(q-1)^2 states and applies to every finite field.

**Proof.** Write U=u a and V=v b with a(u)=b(v)=1. The assumptions give
b(u)=0 and a(v)!=0. Rescale v and b inversely so that a(v)=1. Then
X_0=(u,v) and Y_0=(a;b) satisfy Y_0 X_0=B. Both have rank two since B
is invertible. Choose an ordered basis of ker(Y_0) after u,v. In this
basis U=e_1(e_1^T+e_2^T), V=e_2 e_2^T and Y_0=[B 0]. This change of
fixed basis permutes the header domain, preserving the fraction.

For a header G, put X=G X_0 and Y=Y_0 G^-1. Then YX=B and the
conjugated kernels are the first column of X times the first row of Y,
and the second column times the second row. Conversely, given X,Y with
YX=B, choose the remaining columns of G as any ordered basis of ker(Y).
This gives an invertible G and YG=[B 0]=Y_0. The fiber has exactly
|GL_(m-2)(K)| elements. There are (q^m-1)(q^m-q) full-rank X, and each
of the two rows of Y has q^(m-2) solutions to its two equations. Thus
there are D(q,m) pairs, with equal fibers.

For a column x and row y, multilinearity of the determinant gives

```text
det((I-xy)[1..j,1..j]) = 1 - sum_(i=1)^j y_i x_i.
```

Terms choosing the rank-one part from two columns vanish. This is the
corank-one guard reduction of #4227. If x_i is row i of X and y_i is
column i of Y, the two diagonal entries of A_j=sum_(i<=j) y_i x_i are
exactly the two guard prefix sums. Hence A_j must lie in S for 1<=j<m,
while A_m=B. The guards impose no condition at order m.

Each coordinate increment y_i x_i has w(A) ordered factorizations.
For A=0, either factor is zero, giving 2q^2-1 choices. Every nonzero
rank-one A has q-1 factorizations by reciprocal rescaling; rank two has
none. Summing independent coordinate choices gives the transfer above.
Invertibility of B already forces X,Y to have rank two, so no further
rank or independence filter is missing. Equal fibers prove the claim.

## Binary closed form

Put n=m-1. For every m>=2,

```text
C(2,m) = (9^n - 5^n)/4,
Pr(P and Q pass) = (9^(m-1)-5^(m-1))
                  / [4(2^m-1)(2^m-2)2^(2m-4)].
```

**Proof.** Safe states over F2 have zero diagonal and are indexed by their
two off-diagonal bits. Safe increments are zero with weight seven, E_12
with weight one and E_21 with weight one. The final increment B-A has
both diagonal entries one. Its determinant vanishes exactly when
(1+A_12)A_21=1, so only A_12=0,A_21=1 contributes, with weight one.

The length-n walk on F2^2 therefore ends at (0,1). The four character
eigenvalues of its transition operator are 9,7,7,5. Character inversion
at (0,1) gives (9^n+7^n-7^n-5^n)/4. This proves the formula, including
integrality. A walk with one E_21 and n-1 zero increments proves positivity
for every m>=2. For m=2,3,4,5,6 the fractions are respectively
1/6, 1/12, 151/3360, 371/14880 and 451/32256.

## Comparison and correlation

The orthogonal-kernel count in #4261 is
C_orth=(9^n-2*7^n+5^n)/4. The new one-way count exceeds it by
(7^n-5^n)/2>0 for every m>=2, with the same denominator D(2,m).
Thus one-way coupling creates passing headers even at m=2, where the
orthogonal pair has none. This is a count improvement, without a priced
caller or a primitive-saving claim.

The two passing events remain strictly negatively correlated. The marginal
law from #4227 is s_m=3^n/[(2^m-1)2^n]. Directly, each of the first n
coordinate products must be zero, with three choices each; the last must
be one. The normalized rank-one denominator is (2^m-1)2^n. Therefore

```text
joint / s_m^2 = (2^(n+1)-1)/(2^(n+1)-2) * [1-(5/9)^n] < 1.
```

The inequality is equivalent to (2^(n+1)-1)5^n>9^n. It holds at n=1;
the left-to-right ratio increases at each step since
5(2^(n+2)-1)>9(2^(n+1)-1). The joint density is asymptotic to
(1/4)(9/16)^n and its ratio to s_m^2 tends to one from below. These
conclusions use the complete equally weighted header domain.

## Scope

The theorem covers one-way coupled rank-one kernels over finite fields.
Pairs with both UV and VU nonzero, coincident images or covectors, restricted
header subsets, and finite local rings are outside scope. The all-field
result is a recurrence; only F2 has a closed form here. Written mathematics
is the universal evidence. The executable census covers only its declared
finite domains. Binary guards extend beyond the retained normalizer's
odd-prime executable domain. Even for odd fields, a request producer,
header selection/emission, dispatch, dirty return, stock and full physical
invoice remain unknown. No multiplication theorem or supplier is admitted.
