# Six is the exact directed-cycle price

Let R=Z/4, w>=1 and take arbitrary independent a,b,c,p in R^w. The dirty
rows start at a,b,c. The disjoint source p cannot be written. The gate
E_ij(alpha) adds alpha A_j into A_i, for distinct dirty rows i,j; P_i(beta)
adds beta p into A_i. Every nonzero coefficient is allowed. The gate types
E_10, E_21, E_02 and P_0 cost one; the remaining five types cost 100.
Prices are stationary and coefficient-independent. No other operations,
workspace, observations or free basis changes are available. Words are fixed,
finite and may have arbitrary repetitions and interleavings. The required
endpoint is (a+2p,b+p,c+p,p) on every input.

## Attainment

Execute chronologically

```text
E_21(-1), E_10(-1), P_0(1), E_10(1), P_0(1), E_21(1).
```

The first two gates leave (a,b-a,c-b). After the first insertion and next
ADD they are (a+p,b+p,c-b). The last insertion and ADD give
(a+2p,b+p,c+p). Every gate costs one; the complete price is six. The source
never changes. The identities hold coordinatewise at every positive width,
retaining all original dirt.

## No word can cost less

Track the three-by-three matrix M of original dirt coefficients. Every
prefix is invertible, because each ADD has its negated-coefficient inverse
and insertions leave M unchanged. The endpoint requires M=I.

Recall the incoming-row return argument of #5045/#5163. A row cannot receive
exactly one nonzero ADD. Before its unique incoming ADD its dirt row is e_i.
If that gate is E_ij(alpha), restoration with no later incoming ADD requires
alpha m_j=0, where m_j is row j of the invertible prefix M. Right multiplication
by M inverse gives alpha e_j=0, hence alpha=0, a contradiction. This counts
total arrivals at a row, not individual directed edges.

Suppose a word costs less than six. It uses only price-one gates, so every
source insertion is into row zero. Let t be the number of insertions. Rows
one and two each have a nonzero final source coefficient and no insertion
of their own. Each must receive an ADD, hence at least two by the return
argument.

If t=0, every source coefficient remains zero, which is impossible. If
t>=2, its price is at least t+2+2>=6, a contradiction.

For t=1, write beta for the inserted coefficient. The final source column
is beta v, since every subsequent gate is R-linear. Its row-one coefficient
is 1, so beta is a unit. If row zero receives no ADD, its final source
coefficient is beta, which cannot equal the required nonunit 2. Row zero
therefore receives at least one ADD, and hence at least two. The price is
at least 1+2+2+2=7, again a contradiction. This exhausts t and proves the
minimum six. The proof requires no width bound or special dirty input.

## Separate finite certificate

Represent rows by a three-by-four matrix of coefficients of (a,b,c,p).
The start is [I|0] and the target is [I|(2,1,1)]. The twelve cheap generators
include all three nonzero coefficients on each cheap gate type, so the
alphabet is closed under inversion.

The verifier enumerates the complete radius-two ball about the start and
radius-three ball about the target. They contain 99 and 613 matrices and
have empty intersection. A word of length at most five has a split with
prefix length at most two and suffix length at most three. Its split matrix
would lie in both balls. Price-100 gates cannot occur in a cheaper word.
The six-gate word supplies the matching upper certificate.

This finite computation independently corroborates the written lower bound
after the coefficient-matrix reduction. The result is an abstract tariff,
not a physical implementation, supplier or multiplication theorem.
