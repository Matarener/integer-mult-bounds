# A cost obstruction for separated native lifts

This result rejects one implementation of the odd E8 family. It does not
reject the geometry, all native producers, or all integer-multiplication
algorithms. The positive geometry result in PROOF.md remains unchanged.

The cost model below fails at exponent 151/50000 = 0.00302 for every odd
factor count k>=3 and every odd stage count N>=3. It also fails at every
larger exponent below one. Thus this model cannot reach the selected
0.003027288235 checkpoint. This is a scoped obstruction, not a new kappa.

## 1. The implementation class

Let E be the 112-dimensional space of base port values over C. Let C be
the rank-eight fitting matrix in PROOF.md, and let B be its block-diagonal
restriction to the 14 sign cubes. Put

```
K = I-B
H = B-C.
```

For odd k=2s+1, form F_k as in PROOF.md. Form F_block,k with B in place of C.
The side map to be produced is H_k=F_block,k-F_k.

A separated implementation writes

```
H_k = sum_(i=1)^k H_i tensor D_i,
```

where D_i is any linear operator on the other k-1 port factors. It need
not be diagonal, symmetric, a scalar polynomial, or a member of a fixed
dictionary. Every rank-one factor of D_i uses one channel of the fixed
base H module. All coefficient maps are granted for free. A decomposition
with several terms for one i cannot use fewer channels than rank(D_i)
after those terms are added.

Each channel retains one complete native helper bank from the pinned base
word. Its helper paid and productive profiles are counted in section 5.
We grant extraction of H from the base coded transfer, all other main-role
work outside the stated paths, and all coefficient acquisition for free.
These grants favor this implementation. They do not describe an emitted
native program.

The declared main and caller inventory is specified in section 6. There
are no additional productive main-role targets in this inventory. A joint
producer, a shared helper protocol that changes the paid word, a different
base module, conjugated modules that replace H, or a caller with changed
targets, main paths or idle cap is outside the claim. Address-dependent
operator coefficients are also outside this port-space model.

## 2. The base spectral split

The literal normalizers give

```
B^2=2B; C^2=14C; BC=CB=2C.
rank(B)=56; rank(C)=8.
```

Thus E=Z direct-sum U, with both spaces of dimension 56. On Z, B=C=H=0
and K=I. On U, B=2I and K=-I. The operator H on U is invertible: it has
eigenvalue 2 with multiplicity 48 and eigenvalue -12 with multiplicity 8.
The checker verifies the two projection identities and the source covariance
over exact integers. The dimensions follow from their traces.

## 3. A channel bound for every odd k

Put t=(k+1)/2. Choose a set S of t factors and restrict H_k to U on S and
Z on the other factors. On this space,

```
H_k = 2I - 2*7^t P,
```

where P is the product of the rank-eight projections on the active factors.
This operator is invertible. The restricted space has dimension 56^k.
Only terms H_i tensor D_i with i in S remain. If D_i[S] denotes the
corresponding principal restriction to the other factors, rank subadditivity
therefore gives

```
sum_(i in S) rank(D_i[S]) >= 56^(k-1).
```

Fix i. Let J be a set of s of the other 2s factors. Consider the two spaces
with U on J and Z on its complement, and with these choices reversed.
The two off-diagonal blocks of D_i between these spaces are zero. To prove
this, restrict the full operator identity to U on factor i and to either
of these off-diagonal blocks. Every other factor changes between U and Z.
Each H_j for j!=i has a zero block between these two spaces. The right side
H_k also has zero such blocks. Since H_i is invertible on U, the block of
D_i is zero.

Consequently rank(D_i) is at least the sum of its two principal block ranks.
Average this inequality over the binomial(2s,s) choices of J. Sum over i,
and then use the preceding inequality for all sets S. The result is

```
sum_i rank(D_i) >= (2k/t)*56^(k-1).
```

For k=5 this is (10/3)*56^4 channels. Relative to 112^4 channels, the
bound is 5/24. A fractional lower bound is sufficient for the cost test;
an actual channel count is an integer.

## 4. A stronger three-factor bound

For k=3, fix the third factor in Z. On U tensor U tensor Z the required
operator is

```
(H tensor I + I tensor H - H tensor H/2) tensor I_Z.
```

Let X and Y be the principal blocks of D_1 and D_2 that occur here. Every
solution of the two-factor identity has the form

```
X = I - H/4 + H tensor S
Y = I - H/4 - H tensor S,
```

with identity factors on Z understood, and with an arbitrary operator S
on Z. To see completeness, subtract the displayed particular solution.
The homogeneous equation is H tensor DeltaX + DeltaY tensor H=0. Passing
to the quotient of either matrix space by the line spanned by H forces
DeltaX=H tensor S and DeltaY=-H tensor S. This argument does not assume
that S is diagonalizable.

Use the two eigenspaces of H on U. Then

```
rank(X)+rank(Y)
 = 48*(rank(I/2+2S)+rank(I/2-2S))
   + 8*(rank(4I-12S)+rank(4I+12S)).
```

The four kernels are eigenspaces of S at the distinct values
-1/4, 1/4, 1/3 and -1/3. Their direct sum has dimension at most 56.
The largest coefficient in the weighted kernel sum is 48. It follows that

```
rank(X)+rank(Y) >= (2*48+2*8-48)*56 = 3584.
```

Apply this result with each factor in Z. For each D_i the two blocks used
in this sum are on U tensor Z and Z tensor U. Their off-diagonal blocks
are zero by section 3. Their ranks therefore add inside a principal
restriction of D_i. Summing the three face bounds gives

```
sum_i rank(D_i) >= 3*3584 = 10752.
```

This is 6/7 of 112^2. No claim that this lower bound is attained is needed.
The finite checker also tests the two-factor identity with diagonal,
nondiagonalizable and nonreal-spectrum choices of S. These checks support
the written argument; they do not replace its universal quantifiers.

## 5. The retained helper cost

The authenticated native source gives the following profiles on its 408
original helper roles, in both orientations:

```
paid:    {1:1513, 2:201, 3:432, 4:50, 5:12}
targets: {4:28, 7:7, 8:47, 9:326}.
```

Both have rank mass 3471. For each individual helper, the checker verifies
that its positive paid widths sum to its requested width. Owned center
copies and all main-role calls are excluded from these profiles. Removing
the center copies does not remove these helper paths.

At sigma=1-a, write beta(a) for the paid moment minus the target moment of
one helper bank. The per-helper width partitions imply beta(a)>=0 for
0<=a<1 by concavity. Thus the three-factor side map costs at least
10752*beta(a) per local invocation. For five factors the lower bound is
(10/3)*56^4*beta(a). The coefficient maps and every further cost remain free
in this lower bound.

The source is Cao Yifan's retained native word, used by Dugongue's center-free
code and Dillon's normalized caller. Their attribution and source notices
remain in the pinned files. This result counts their existing helper paths;
it does not re-prove their native operator identities.

## 6. The declared relaxed invoice

For a fixed odd k>=3 and odd N>=3, put v=112^k and m=8kN+1. Grant these
main paths per local invocation and per port:

```
source children: [3k-1, 5k, 1]
target children: [5k, 1 repeated 3k times].
```

There are N local invocations and (N-1)*v productive main jobs of rank m.
Grant the pairing-rank COPY profile from PROOF.md. The k=3 check also tests
the larger source-dimension profile. The declared idle rank mass is
8k*N*(N-3)*v. Grant fractional packing of that mass at the largest width

```
c = floor(sqrt((m^2-1)/2)).
```

This is a stated caller model, not a proof that a native caller realizes it.
For N=3 it reduces to the inventory already used in PROOF.md. The bounds
for larger N apply to this declared idle cap; a changed cap is outside scope.

Let g_k(a) be the per-port, per-local paid moment from the main paths,
the copied decoder, and the lower bound on separated helper banks. The
remaining moment per port per local invocation is at most

```
((N-1)/N)*m^(1-a) - 8k*(N-3)*c^(-a) - g_k(a).
```

At a=151/50000 every case below is strictly negative. The checker uses
rational logarithm and exponential bounds. It does not use floating-point
sign tests. To enclose log(r), first divide r by a power of two. For
z=(y-1)/(y+1), with 1<=y<2, use the first 24 terms of
`2*sum z^(2j+1)/(2j+1)`. The remainder is between zero and
`2*z^49/(49*(1-z^2))`. The same formula at z=1/3 encloses log(2).
Round the resulting bounds outward to a grid of 10^(-30). For
`x=a*log(r)`, use the exponential sum through degree 18. Its tail is at
most `(x^19/19!)/(1-x/20)`, since 0<=x<1. Invert these positive bounds
to enclose r^(1-a). Stored final intervals are rounded outward again.

- For k=3, check all odd N from 3 through 61. For N>=63, even parent-width
  idle packing gives the upper bound `49*1513^(-a)-g_3(a)`, which is negative.
  Indeed the pre-main moment is at most `(49-1/N)*(24N+1)^(-a)`.
- For k=5, check N=3 and N=5 with the stated cap. For N>=7, parent-width
  packing at N=7 already fails. The parent-width upper bound decreases with
  N in this range. The rational derivative test is included in the checker.
- For all k>=7, grant every copy and helper for free. Main paths alone fail.
  It is enough to check k=7,N=3 and the parent-width bound at k=7,N=5.
  The monotonicity argument below covers the infinite ranges.

For the last two tail arguments, the parent-width pre-main expression is

```
G(k,N) = (16k+1-1/N)*(8kN+1)^(-a).
```

For fixed k its derivative in N is negative when

```
1/N + 1/(8kN^2) < a*(16k+1-1/N).
```

The left side decreases with N and the right side increases. The checker
proves the inequality at k=5,N=5 and k=7,N=5.

For the all-k tail subtract the main-path cost
`(3k-1)^(1-a)+2*(5k)^(1-a)+3k+1` from G(k,N). Its derivative in k is at most

```
[3*(1-a)-8*a*(N-3)/(8kN+1)]*(8kN+1)^(-a) - 3 < 0.
```

This follows because `3k-1` and `5k` are smaller than `8kN+1`. Thus the
two k=7 checks cover every larger odd k, with all copies and helpers free.

## 7. Why failure persists at larger exponents

Normalize each invoice by m^(1-a). The main target count is then constant.
Each normalized main, copy and idle paid term increases with a, since its
width is below m. The normalized helper-bank excess also cannot decrease.

For one helper let its paid widths be d_j and its target width be r, with
sum d_j=r<m. The derivative in a of its normalized excess is

```
sum_j (d_j/m)^(1-a)*log(m/d_j)
      - (r/m)^(1-a)*log(m/r).
```

The function `x^(-a)*log(m/x)` decreases on 0<x<m for a>=0. Divide each
summand by its width and use sum d_j=r. The displayed derivative is
nonnegative. Hence a failed invoice at 0.00302 stays failed for every
a in [0.00302,1). This uses the checked per-helper partitions, not only
equality of the two aggregate rank masses.

## 8. Consequence and limits

Do not implement a larger separated lift with the same full helper-bank
contract and declared invoice. Even the free coefficient maps and favorable
packing do not make it fit. A useful next construction must change the joint
producer, native helper word, main paths or caller inventory, and must price
the resulting state and restoration work.

The odd direct-sum fitting family and its vanishing pairing tariff remain
valid. No theorem here excludes a direct joint producer or a better interface.
No native program, independent human review, formal-kernel check or new
integer-multiplication bound is claimed.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
