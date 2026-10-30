# Four agreement layers at quadratic degree

All ranks and polynomials in this note are over the rationals. The same ranks
hold over the reals and complexes. Let n=4m, where m is an integer at least 4.
For Boolean n-vectors x and y, write t=sum_i x_i y_i and let H_n(x,y)=(-1)^t.
This is the 2^n by 2^n Walsh-Hadamard matrix.

Define

```
P_m(t) = (-1)^m (2(t-m)^2 - 5)/3,
A_m(x,y) = P_m(sum_i x_i y_i).
```

The construction agrees with H_n at exactly the four overlap weights
m-2, m-1, m+1 and m+2. Both A_m and every polynomial interpolant of parity
on three consecutive overlap weights have exact rank

```
d_n = 1 + n + binom(n,2).
```

Among all such consecutive triples, the unique best one is m-1,m,m+1.
A_m agrees on strictly more entries for every m>=4. This compares two explicit
families. It does not assert an optimum over all rank-d_n matrices or all
quadratic polynomials.

## Equality set

Put u=t-m. At u=+-1, P_m=-(-1)^m; at u=+-2, P_m=(-1)^m.
These equal (-1)^t. At u=0 its absolute value is 5/3. At every integer
|u|>=3 its absolute value is at least 13/3. Thus there are no other equalities.
All four weights lie between 0 and n under the stated hypotheses.

## Exact rank

Let z_i=x_i y_i. Since z_i^2=z_i on Boolean inputs, the multilinear expansion is

```
3P_m(sum_i z_i) = c0 + c1 sum_i z_i + c2 sum_(i<j) z_i z_j,
c0 = (-1)^m (2m^2-5),
c1 = (-1)^m (2-4m),
c2 = (-1)^m 4.
```

Let Z have rows indexed by Boolean vectors and columns indexed by subsets S
of size at most two, with Z[x,S]=prod_(i in S) x_i. Then 3A_m=Z D Z^T, where D
is diagonal with the corresponding c0,c1,c2 entries. Each is nonzero.
Restrict the rows of Z to characteristic vectors of subsets T of size at most
two, ordered by cardinality. The resulting square matrix has entry 1 exactly
when S is a subset of T. It is lower triangular with diagonal 1, hence invertible.
Therefore Z is injective, Z^T is surjective, and Z D Z^T has rank d_n.

For a consecutive triple h-1,h,h+1, the unique degree-at-most-two interpolant is

```
Q_h(t) = (-1)^h (1 - 2(t-h)^2).
```

Its equality set with parity is exactly that triple: equality with either 1 or
-1 requires t-h to be 0 or +-1. Its multilinear coefficients, grouped as above,
are (-1)^h times 1-2h^2, 4h-2 and -4. They are nonzero for every integer h.
The same factorization therefore gives exact rank d_n for every admissible
triple, including triples next to the endpoints.

The monomial-to-rank method is classical. See Alman and Williams,
[Probabilistic Rank and Matrix Rigidity, Section 3](https://arxiv.org/html/1611.05558#S3).
The new comparison here uses a different four-layer quadratic, without changing
the degree or the number of nonzero features.

## Exact entry counts and the best consecutive triple

An ordered pair (x,y) has t common one-coordinates in

```
w_t = binom(4m,t) 3^(4m-t)
```

ways. Choose those coordinates; each other coordinate has three allowable
ordered bit pairs. Thus the normalized distribution is Bin(4m,1/4).
The sequence w_t is strictly increasing through t=m and strictly decreasing
after t=m, by w_(t+1)/w_t=(4m-t)/(3(t+1)).

For a triple starting at s, shifting it one place right changes its mass by
w_(s+3)-w_s. This is positive for s<=m-3 and negative for s>=m. The remaining
two comparisons are strict as well:

```
w_(m+1)/w_(m-2) = (3m+1)(3m+2) / (9(m^2-1)) > 1,
w_(m+2)/w_(m-1) = (9m^2-1) / (9(m+1)(m+2)) < 1.
```

Consequently the unique best triple starts at m-1 and has mass
B_m=w_(m-1)+w_m+w_(m+1).

The four-layer mass F_m=w_(m-2)+w_(m-1)+w_(m+1)+w_(m+2) has gain

```
F_m-B_m = w_(m-2)+w_(m+2)-w_m
        = w_m N(m) / D(m),
N(m) = 27m^4 - 36m^3 - 171m^2 - 128m - 12,
D(m) = 3(m+1)(m+2)(3m+1)(3m+2).
```

This follows by substituting

```
w_(m-2)/w_m = 9m(m-1)/((3m+1)(3m+2)),
w_(m+2)/w_m = m(3m-1)/(3(m+1)(m+2)).
```

For k=m-4>=0, direct expansion gives

```
N(k+4) = 27k^4 + 396k^3 + 1989k^2 + 3688k + 1348 > 0.
```

Both denominator and w_m are positive. This proves the strict improvement for
every m>=4. At n=16, d_n=137, F_4=2713419648, B_4=2633821596 and the gain is
79598052 entries, out of 4^16=4294967296 ordered pairs.

## Limits

The comparison is about exact entry agreement, not operator norm, per-row
error, rounded execution or a complete transform algorithm. The counts include
every row, without filtering by its Hamming weight. No claimed asymptotic
non-rigidity exponent or multiplication saving follows.

The four-layer choice loses to the best consecutive triple at n=8 and n=12.
It is also not globally best among low-rank matrices. For example, at n=40 the
rank-one constant matrix 1 agrees on more entries. Its agreement count is
sum_(t even) w_t. The verifier checks that limitation explicitly. Higher degree,
row corrections, coefficient preparation, a physical consumer, and the full
paid/target invoice are separate obligations.
