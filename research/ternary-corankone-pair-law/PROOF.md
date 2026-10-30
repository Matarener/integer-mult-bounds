# Ternary corank-one pair law

This scoped counting proof was produced by Nick Petalas. Apache-2.0.

## Statement

Let U,V be rank-one idempotents on F_3^m, with UV=VU=0 and m>=2.
Set P=I-U and Q=I-V. A complete header G in GL_m(F_3) passes a request
R if every leading principal minor of GRG^-1, of orders 1 through rank(R),
is nonzero. Give every complete header equal weight. Write n=m-1.

The joint passing fraction is

```text
                 4(49^n - 2*25^n + 19^n)
J_m = ------------------------------------------------- .
       9(3^m-1)(3^m-3)3^(2m-4)
```

In particular J_2=1/6. A common passing header exists for every m>=2.
The two passing events are strictly negatively correlated, and

```text
J_m ~ (4/9)(49/81)^(m-1).
```

The all-field partial-Gram transfer is due to Nick Petalas's
[#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261), head
`4728fc766b3084f3ab2f5c8543a5e74e4a12b126`. The new result is its ternary
four-class reduction and closed form. The transfer reduction is restated below
so the proof does not require fetching that pending package.

## Transfer and equal header fibers

Choose a fixed basis with U=e_1 e_1^T and V=e_2 e_2^T. This change of basis
permutes the complete header domain. Let X=(u,v) be the first two columns
of G, and Y=(a;b) the first two rows of G^-1. Then YX=I_2. Conversely every
normalized pair X,Y has exactly |GL_(m-2)(F_3)| header completions, obtained
by choosing an ordered basis of ker(Y) for the remaining columns. Here
|GL_0|=1. The number of normalized pairs is

```text
D_m = (3^m-1)(3^m-3)3^(2m-4).
```

Indeed X has two independent columns, and each dual row has 3^(m-2)
solutions to its two prescribed scalar products.

The rank-one determinant identity makes the two guards at order j equivalent
to sum_(i<=j) a_i u_i != 1 and sum_(i<=j) b_i v_i != 1. With row
x_i=(u_i,v_i) and column y_i=(a_i,b_i)^T, put A_j=sum_(i<=j) y_i x_i.
All A_j for 1<=j<m must lie in

```text
S = { [[a,b],[c,d]] : a,d in {0,2}, b,c in F_3 }.
```

The endpoints are A_0=0 and A_m=I_2. For a fixed increment H, its number
of factorizations H=yx is w(0)=17, w(H)=2 for nonzero rank-one H, and
w(H)=0 for rank two. Zero has 9+9-1 factorizations. A nonzero rank-one
matrix has two factorizations, related by nonzero scalar rescaling.

Let T_(A,B)=w(B-A) for A,B in S, and h(A)=w(I_2-A). The normalized
passing-pair numerator is C_m=(T^n h)(0). Dividing by D_m also gives the
header fraction, since every normalized pair has the same header fiber.

## Four classes

Partition A=[[a,b],[c,d]] in S as follows.

| Class | Condition | Size | Representative A |
|---|---|---:|---|
| Z | b=c=0 | 4 | [[0,0],[0,0]] |
| L | exactly one of b,c is zero | 16 | [[0,1],[0,0]] |
| R | bc=(1-a)(1-d) | 8 | [[0,1],[1,0]] |
| N | b,c nonzero and bc!=(1-a)(1-d) | 8 | [[0,1],[2,0]] |

The right side in the R condition is nonzero. Thus these are disjoint and
exhaust S. To see that the partition is equitable, put B=I_2-A. Its two
diagonal entries are nonzero. Independent invertible diagonal row and column
scalings of B preserve this domain and preserve rank differences, hence
preserve every transfer weight. They normalize the diagonal to 1,1.
Residual scaling and transposition have exactly four orbits: no nonzero
off-diagonal entries, one, two with product 1, and two with product 2.
These are precisely Z,L,R,N. Therefore the weighted number of transitions
to each class is constant on every source class.

For the representatives in the table, count target states with nonzero
rank-one difference. In class order Z,L,R,N, these counts are

```text
    2  12  2  0
    3   6  3  4
    1   6  5  4
    0   8  4  4
```

Each count is the sum over target a,d in {0,2}, b,c in F_3, excluding
the source itself, of the condition det(target-source)=0 and the target
class condition above. This is a 36-term calculation for each row.
Multiplying by two and adding 17 on the diagonal gives the quotient

```text
      21  24   4   0
M =    6  29   6   8 .
       2  12  27   8
       0  16   8  25
```

The terminal weight is two precisely on class R, so h=(0,0,2,0)^T in the
quotient. Starting from 0 means C_m=e_Z^T M^n h. Class sizes do not enter
again: each row of M already sums the individual target-state weights.

## Closed form

The following exact integer-vector identities prove the needed recurrence.

```text
M h                           = (8,12,54,16)^T
(M-19I) h                     = (8,12,16,16)^T
(M-25I)(M-19I) h              = 320(1,1,1,1)^T
M(1,1,1,1)^T                  = 49(1,1,1,1)^T
```

Consequently (M-49I)(M-25I)(M-19I)h=0. The scalar sequence c_n=e_Z^T M^n h
satisfies

```text
c_(n+3) = 93*c_(n+2) - 2631*c_(n+1) + 23275*c_n,
c_0=0, c_1=8, c_2=672.
```

The sequence (4/9)(49^n-2*25^n+19^n) satisfies this recurrence and the
same three initial values. Induction proves equality for every n>=0,
which proves the stated header fraction for all m>=2. This is an all-m
written proof, rather than an extrapolation from the finite replay.

Positivity follows from M_(Z,R)=4, h_R=2 and M_(Z,Z)=21: for every n>=1,
the n-step term that stays in Z for n-1 steps and then enters R is positive.
Dividing numerator and denominator by 81^n gives the stated asymptotic.

## Correlation

The single corank-one fraction is s_m=2*7^n/((3^m-1)3^n), as in #4227.
It also follows directly: a safe scalar partial product has two states
0,2, transition matrix [[5,2],[2,5]], and terminal vector (2,2)^T.
Thus

```text
J_m/s_m^2 = (3^(n+1)-1)/(3^(n+1)-3)
            * [1 - 2(25/49)^n + (19/49)^n].
```

For n>=1,

```text
(3^(n+1)-1)(2*25^n-19^n)
    > 2*3^n*25^n
    = 2*75^n
    > 2*49^n.
```

This is exactly the strict inequality J_m/s_m^2<1 after rearranging.
The same ratio tends to one. This concerns complete headers with uniform
weight; it does not imply anything about a producer's restricted header set.

## Limits

Only F_3, two orthogonal rank-one kernels and their two corank-one requests
are covered by the new closed form. P,Q have overlapping images for m>2.
No new claim is made for other fields, nonorthogonal kernels or three kernels.
The four-class table is independently enumerated in the replay on every
one of its 36 source states. The proof is not checked by a formal kernel.
No header producer, selection or emission algorithm, dispatch, dirty return,
stock bound, physical caller or supplier admission is supplied.
